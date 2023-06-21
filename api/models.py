import base64
from django.core.files.base import ContentFile
from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.urls import reverse

class Employee(models.Model):
    verified_by = models.ForeignKey(User, on_delete=models.CASCADE)
    emp_id = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    department = models.CharField(max_length=255, blank=True, null=True)
    position = models.CharField(max_length=255, blank=True, null=True)
    date_added = models.DateField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    slug = models.SlugField(max_length=255, blank=True, null=True)


    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if self.emp_id and self.name and self.department and self.position:
            self.slug = slugify(self.emp_id + '-' + self.name + '-' + self.department + '-' + self.position)
        super(Employee, self).save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('employee-detail', kwargs={'slug': self.slug})


class AttendanceRecord(models.Model):
    DAY_CHOICES = (
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, blank=True, null=True)
    snapshot = models.ImageField(upload_to='snapshots/', blank=True, null=True)
    date = models.DateField(auto_now_add=True)
    day = models.CharField(max_length=10, choices=DAY_CHOICES, default="")
    time = models.TimeField(auto_now_add=True)
    status = models.CharField(max_length=10, default='Present')
    morning_in = models.TimeField(blank=True, null=True)
    lunch_out = models.TimeField(blank=True, null=True)
    lunch_in = models.TimeField(blank=True, null=True)
    afternoon_out = models.TimeField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    is_present = models.BooleanField(default=False)
    is_late = models.BooleanField(default=False)
    is_absent = models.BooleanField(default=False)
    is_halfday = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.employee} - {self.date}'
    
    def count_all_late(self):
        return AttendanceRecord.objects.filter(is_late=True).count()
    
    def count_all_absent(self):
        return AttendanceRecord.objects.filter(is_absent=True).count()
    
    def count_all_halfday(self):
        return AttendanceRecord.objects.filter(is_halfday=True).count()
    
    def count_all_present(self):
        return AttendanceRecord.objects.filter(is_present=True).count()

