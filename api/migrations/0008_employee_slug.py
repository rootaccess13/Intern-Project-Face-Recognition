# Generated by Django 4.1.2 on 2023-06-20 12:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_attendancerecord_is_halfday'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='slug',
            field=models.SlugField(blank=True, max_length=255, null=True),
        ),
    ]
