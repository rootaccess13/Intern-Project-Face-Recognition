from django.contrib import admin
from . models import *
# Register your models here.
from django.contrib.auth.models import User

@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    list_display = ['employee', 'date', 'day', 'time', 'status', 'morning_in', 'lunch_out', 'lunch_in', 'afternoon_out', 'is_verified', 'is_present', 'is_late', 'is_absent', 'is_halfday']
    list_filter = ['is_verified', 'is_present', 'is_late', 'is_absent', 'is_halfday']
    search_fields = ['employee__name', 'date', 'day', 'time', 'status', 'morning_in', 'lunch_out', 'lunch_in', 'afternoon_out', 'is_verified', 'is_present', 'is_late', 'is_absent', 'is_halfday']


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['name', 'emp_id', 'position', 'department', 'is_verified', 'is_active']
    list_filter = ['is_verified', 'is_active']
    search_fields = ['name', 'emp_id', 'position', 'department']



admin.site.site_header = 'Earist - SARRMS Administration Panel'



admin.site.index_template = 'admin/index.html'