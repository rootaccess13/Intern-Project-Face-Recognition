from django.urls import path
from . views import *


urlpatterns = [
    path('r/', AttendanceEntryViewset.as_view({'post': 'create'})),
    path('r/fetch/', fetchAttendanceViewset.as_view({'get': 'list'})),
    path('r/authenticate/', AuthenticateStaffViewSet.as_view({'post': 'post'})),
    path('r/weekly/', WeeklyAttendanceAPI.as_view(), name='weekly-attendance-api'),
    path('r/monthly/', MonthlyAttendanceAPI.as_view(), name='weekly-attendance-api'),
    path('r/dataset/', fetchDatasetViewset.as_view(), name='dataset-attendance-api'),
    path('r/attendance/', AttendanceAPI.as_view(), name='attendance-api'),
    path('r/attendance/<int:pk>/confirm/', ConfirmAttendanceViewset.as_view({'put': 'update'}), name='confirm_attendance'),
    path('r/attendance/cancel/<int:pk>/', CancelAttendanceViewSet.as_view({'delete': 'destroy'}), name='cancel-attendance-delete'),
    path('r/employee/all/', FetchAllEmployessViewset.as_view({'get': 'retrieve'}), name='employee-all'),
    path('r/employee/<slug:slug>/', EmployeeDetailsViewset.as_view({'get': 'retrieve'}), name='employee-detail'),
]