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

            if attendance.exists():
                print("exists")
                if current_time < "12:00:00" and not attendance.filter(morning_in__isnull=False).exists():
                    attendance.update(morning_in=current_time)
                    shift_val = "Morning"
                elif "12:00:00" <= current_time < "13:00:00" and not attendance.filter(lunch_out__isnull=False).exists():
                    attendance.update(lunch_out=current_time)
                    shift_val = "Lunch Out"
                elif "13:00:00" <= current_time < "14:00:00" and not attendance.filter(lunch_in__isnull=False).exists():
                    attendance.update(lunch_in=current_time)
                    shift_val = "Lunch In"
                elif current_time >= "14:00:00" and not attendance.filter(afternoon_out__isnull=False).exists():
                    attendance.update(afternoon_out=current_time)
                    shift_val = "Afternoon Out"
                else:
                    a_status = "duplicate_entry"
                attendance.update(status=shift_val)
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
                instance.save()

            return Response({
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