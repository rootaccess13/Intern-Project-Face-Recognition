from rest_framework import serializers
from django.contrib.auth.models import User
from . models import *

class AttendanceSerializers(serializers.ModelSerializer):
    class Meta:
        model = AttendanceRecord
        fields = '__all__'

class fetchAttendanceSerializers(serializers.ModelSerializer):
    employee = serializers.CharField(source='employee.name')

    class Meta:
        model = AttendanceRecord
        fields = '__all__'

class AuthenticateSerializers(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password']