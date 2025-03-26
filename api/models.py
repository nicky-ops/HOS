from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Driver(models.Model):
    '''
    This class represents the driver model
    '''
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    licence_number = models.CharField(max_length=50)
    cycle_type = models.CharField(max_length=10, choices=[('70/8', '70-hour/8-day'), ('60/7', '60-hour/7-day')])
    current_cycle_used = models.DecimalField(max_digits=5, decimal_places=2, default=0)


class Trip(models.Model):
    '''
    This class represents the trip model
    '''
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE)
    start_location = model.CharField(max_length=255)
    pickup_location = model.CharField(max_length=255)
    dropoff_location = model.CharField(max_length=255)
    start_time = models.DateTimeField()
    distance_miles = models.DecimalField(max_digits=5, decimal_places=2)
    estimated_duration_hours = models.DecimalField(max_digits=5, decimal_places=2)


class DutyStatus(models.Model):
    '''
    This class represents the duty status model
    '''
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE)
    status = models.CharFiels(max_length=20, choices=[
        ('OFF_DUTY', 'Off Duty'),
        ('SLEEPER', 'Sleeper Berth'),
        ('DRIVING', 'Driving'),
        ('ON_DUTY', 'On Duty (Not Driving)')
    ])
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    location = models.CharField(max_length=255)


class DailyLog(models.Model):
    '''
    This class represents the daily log model
    '''
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE)
    date = models.DateField()
    total_miles = models.DecimalField(max_digits=5, decimal_places=2)
    vehicle_number = models.CharField(max_length=50)
    remarks = models.TextField(blank=True)