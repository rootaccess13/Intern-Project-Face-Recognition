from django.shortcuts import render
from django.contrib.auth.decorators import login_required as lr
from api.models import *
from django.db.models import Q
import datetime
from django.db.models import Count

# Create your views here.
@lr(login_url='/auth/l/')
def index(request):
    list = AttendanceRecord.objects.all().filter(Q(date=datetime.date.today()))
    context = {
        'list': list
    }
    return render(request, 'index/index.html', context)


def gathers(request):
    return render(request, 'index/gather.html')



def settings(request):
    employees = Employee.objects.all()
    records = AttendanceRecord.objects.all().filter()
    
    # Count the occurrences of is_present, is_late, and is_absent for each employee
    employee_counts = records.values('employee').annotate(
        present_count=Count('employee', filter=Q(is_present=True)),
        late_count=Count('employee', filter=Q(is_late=True)),
        absent_count=Count('employee', filter=Q(is_absent=True))
    )
    
    # Retrieve the Employee objects based on the employee IDs
    for employee_count in employee_counts:
        employee_count['employee'] = employees.get(pk=employee_count['employee'])
    
    context = {
        'employees': employees,
        'employee_counts': employee_counts,
    }
    
    return render(request, 'setting/setting.html', context)


def reqdtr(request):
    context = {
        'list_employee': Employee.objects.all()
    }
    return render(request, 'setting/reqdtr.html', context)