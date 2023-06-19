from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404, redirect
from rest_framework.authentication import TokenAuthentication, SessionAuthentication, BasicAuthentication
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from django.conf import settings
import os
from django.db.models import Q
from .serializers import AttendanceSerializers, fetchAttendanceSerializers, AuthenticateSerializers
from .models import AttendanceRecord, Employee
from .knn_detector import predict, show_prediction_labels_on_image
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from django.http import JsonResponse
from django.db.models import Count
from datetime import datetime, timedelta
from rest_framework import viewsets


class AttendanceEntryViewset(ModelViewSet):
    queryset = AttendanceRecord.objects.all()
    serializer_class = AttendanceSerializers
    permission_classes = [IsAuthenticated]
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    KNN_MODEL = os.path.join(BASE_DIR, 'api/trained_knn_model.clf')

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        filename = request.data['snapshot']
        time = request.data['time']

        if serializer.is_valid():
            save_directory = os.path.join(settings.MEDIA_ROOT, 'snapshots')
            save_path = os.path.join(save_directory, str(filename))

            with open(save_path, 'wb') as file:
                file.write(request.data['snapshot'].read())

            path_name = os.path.abspath(save_path)
            snap_full_path = path_name
            predictions = predict(snap_full_path, model_path=self.KNN_MODEL)
            for name, (top, right, bottom, left) in predictions:
                print("- Found {} at ({}, {})".format(name, left, top))
            predicted_face = show_prediction_labels_on_image(snap_full_path, predictions)
            now = datetime.now()
            date = now.strftime("%Y-%m-%d")
            current_time = now.strftime("%H:%M:%S")
            employee = get_object_or_404(Employee, name=name)
            attendance = AttendanceRecord.objects.filter(Q(date=date, employee__name=employee.name))

            a_status = "success"
            shift_val = "Present"
            _id = attendance.values('id')

            if attendance.exists():
                print("exists")
                if current_time < "12:00:00" and not attendance.filter(morning_in__isnull=False).exists():
                    attendance.update(morning_in=current_time, is_present=True)
                    shift_val = "Morning"
                    if current_time > "08:30:00" and current_time < "09:00:00":
                        attendance.update(is_late=True)

                elif "12:00:00" <= current_time < "13:00:00" and not attendance.filter(lunch_out__isnull=False).exists():
                    attendance.update(lunch_out=current_time)
                    shift_val = "Lunch Out"
                    if attendance.filter(morning_in__isnull=True):
                        attendance.update(is_present=False, is_halfday=True)

                elif "13:00:00" <= current_time < "14:00:00" and not attendance.filter(lunch_in__isnull=False).exists():
                    attendance.update(lunch_in=current_time)
                    shift_val = "Lunch In"

                elif current_time >= "14:00:00" and not attendance.filter(afternoon_out__isnull=False).exists():
                    attendance.update(afternoon_out=current_time, is_present=True)
                    attendance.update(is_verified=True)
                    shift_val = "Afternoon Out"

                else:
                    a_status = "duplicate_entry"

                attendance.update(status=shift_val)

                # analysis.save()
            else:
                print("not exists")
                instance = serializer.save()
                if current_time < "12:00:00" and not attendance.filter(morning_in__isnull=False).exists():
                    instance.morning_in = current_time
                    shift_val = "Morning"
                elif "12:00:00" <= current_time < "13:00:00" and not attendance.filter(lunch_out__isnull=False).exists():
                    instance.lunch_out = current_time
                    shift_val = "Lunch Out"
                elif "13:00:00" <= current_time < "14:00:00" and not attendance.filter(lunch_in__isnull=False).exists():
                    instance.lunch_in = current_time
                    shift_val = "Lunch In"
                elif current_time >= "14:00:00" and not attendance.filter(afternoon_out__isnull=False).exists():
                    instance.afternoon_out = current_time
                    shift_val = "Afternoon Out"
                else:
                    a_status = "duplicate_entry"
                instance.status = shift_val
                instance.employee = employee
                _id = instance.id
                instance.save()

            return Response({
                '_id': _id,
                'status': a_status,
                'message': 'Face Detected',
                'name': employee.name,
                'id': employee.emp_id,
                'dept': employee.department,
                'dtime': now.strftime("%Y-%m-%d %H:%M:%S %p"),
                'shift': shift_val,
                'predicted_face': settings.MEDIA_URL + 'labeled/' + predicted_face
            }, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class fetchAttendanceViewset(ModelViewSet):
    queryset = AttendanceRecord.objects.all()
    serializer_class = fetchAttendanceSerializers
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        date = request.query_params.get('date', None)
        if date is not None:
            queryset = queryset.filter(date=date)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)




class AuthenticateStaffViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = AuthenticateSerializers
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        username = request.user.username  # Get the username from the request
        password = request.data["password"]  # Get the password from the request body
        print(username)
        print(password)
        # Authenticate the user with the provided username and password
        user = authenticate(username=username, password=password)

        if user is not None and user.is_staff:
            # User is authenticated and is a staff member
            queryset = queryset.filter(id=user.id)
            serializer = self.get_serializer(queryset, many=True)
            return Response({
                'status': 'auth_ok',
                'message': 'Authentication successful'
            }, status=status.HTTP_200_OK)

        # Return an appropriate response if authentication fails or user is not a staff member
        return Response({'error': 'Authentication failed or user is not a staff member'}, status=status.HTTP_401_UNAUTHORIZED)


class WeeklyAttendanceAPI(View):
    def get(self, request, *args, **kwargs):
        # Define the days of the week
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

        # Get the start and end dates for the current week
        today = datetime.now().date()
        start_date = today - timedelta(days=today.weekday())
        end_date = start_date + timedelta(days=6)
        print(start_date)
        print(end_date)
        # Query the database for the number of present users for each day
        attendance_counts = AttendanceRecord.objects.filter(date__range=[start_date, end_date]) \
            .values('date__week_day') \
            .annotate(count=Count('id'))

        # Create a dictionary to store the attendance counts for each day
        attendance_data = {day: 0 for day in days}

        # Update the dictionary with the actual attendance counts
        for entry in attendance_counts:
            day_index = entry['date__week_day'] - 2
            attendance_data[days[day_index]] = entry['count']
        data = {
            'data': attendance_data,
            'start_date': start_date,
            'end_date': end_date
        }
        return JsonResponse(data, status=200)


class MonthlyAttendanceAPI(View):

    def get(self, request, *args, **kwargs):
        # Define the months of the year
        months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September',
                  'October', 'November', 'December']
        
        # Get the current year
        current_year = datetime.now().year
        
        # Query the attendance records and count for each month
        monthly_counts = AttendanceRecord.objects.filter(date__year=current_year).values('date__month').annotate(count=Count('id'))
        
        # Create a dictionary to store the attendance count for each month
        attendance_data = {month: 0 for month in months}
        
        # Update the attendance count in the dictionary
        for monthly_count in monthly_counts:
            month = months[monthly_count['date__month'] - 1]
            attendance_data[month] = monthly_count['count']
        
        # Return the attendance data as JSON response
        return JsonResponse(attendance_data)




class fetchDatasetViewset(View):
    
    def get(self, request, *args, **kwargs):
        PATH_DIR = os.path.dirname(os.path.abspath(__file__))
        TRAIN_DIR = os.path.join(PATH_DIR, "train_dir/")
        #get all the folders in the train_dir
        folders = os.listdir(TRAIN_DIR)
        #create a dictionary to store the data
        data = {}
        #loop through the folders
        for folder in folders:
            if folder == '.DS_Store':
                continue
            #get the path of the folder
            folder_path = os.path.join(TRAIN_DIR, folder)
            #get the images in the folder
            images = os.listdir(folder_path)
            #create a list to store the images
            image_list = []
            #loop through the images
            for image in images:
                #get the path of the image
                image_path = os.path.join(folder_path, image)
                #append the image path to the list
                image_list.append(image_path)
            #add the image list to the dictionary
            data[folder] = image_list
            img_count = len(image_list)
            print(folder, img_count)
        return JsonResponse(data, status=200)


class AttendanceAPI(View):
    def get(self, request, *args, **kwargs):
        employee_name = request.GET.get('employee_name', '')
        
        attendance_data = []
        
        # Retrieve the attendance records for the specified employee name
        records = AttendanceRecord.objects.filter(employee__name=employee_name)
        
        # Loop through the records and calculate the counts
        for record in records:
            attendance_data.append({
                'title': self.get_attendance_status(record),
                'start_date': record.date.strftime('%Y-%m-%d'),
            })
        
        return JsonResponse(attendance_data, safe=False)
    
    def get_attendance_status(self, record):
        if record.is_present:
            return 'Present'
        elif record.is_late:
            return 'Late'
        elif record.is_absent:
            return 'Absent'
        else:
            return 'Unknown'

class ConfirmAttendanceViewset(ModelViewSet):
    queryset = AttendanceRecord.objects.all()
    serializer_class = AttendanceSerializers
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        record_id = kwargs.get('pk')
        try:
            record = self.get_object()
            record.is_verified = True
            record.save()
            return Response({'message': 'Attendance record verified'}, status=status.HTTP_200_OK)
        except AttendanceRecord.DoesNotExist:
            return Response({'error': 'Attendance record not found'}, status=status.HTTP_404_NOT_FOUND)


class CancelAttendanceViewSet(ModelViewSet):    
    
    def destroy(self, request, *args,**kwargs):
        record_id = kwargs.get('pk')
        try:
            record = AttendanceRecord.objects.get(id=record_id)
            record.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except AttendanceRecord.DoesNotExist:
            return Response({"detail": "Attendance record not found."}, status=status.HTTP_404_NOT_FOUND)
