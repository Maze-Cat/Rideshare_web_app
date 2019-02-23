from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.utils import timezone
from django.utils.html import mark_safe
VEHICLE_TYPES = (
        ('EC','Economic'),
        ('RG','Regular'),
        ('LX','Luxury'),
        )

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    description = models.CharField(max_length=100, default='')

    def __str__(self):
        return self.user.username

def create_profile(sender, **kwargs):
    if kwargs['created']:
        user_profile = UserProfile.objects.create(user=kwargs['instance'])


class Driver(models.Model):
    vehicle_type = models.CharField(max_length=2, choices=VEHICLE_TYPES, default='RG')
    license_number = models.CharField(max_length=30)
    num_passengers = models.IntegerField()
    special_info = models.CharField(max_length=30, blank=True, null=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True) #user account related with this driver
    def __str__(self):
        return self.__unicode__()
    def __unicode__():
        return ("V_Type:{} License_No.:{} Passengers_Limit:{} Special_Info:{} Driver_Name:{} {}".format(
                self.vehicle_type,
                self.license_number,
                self.num_passengers,
                self.special_info,
                self.user.first_name,
                self.user.second_name) )

class Trip(models.Model):
    address = models.CharField(max_length = 30)
    arrival_time = models.DateTimeField()
    number_riders = models.IntegerField()
    vehicle_type = models.CharField(max_length=2, choices=VEHICLE_TYPES, default='RG')
    free_text = models.CharField(max_length=30, blank=True, null=True)
    is_share = models.IntegerField()
    state = models.IntegerField()
    num_current_rider = models.IntegerField()
    sharers = models.ManyToManyField(User, related_name="share_trips", blank=True)
    driver = models.ForeignKey(Driver, null=True, blank=True, on_delete=models.SET_NULL, related_name="mydriver")
    rider = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL , related_name="myrider")
    def __str__(self):
        return self.__unicode__()
    def __unicode__(self):
        return ('Addr:{} Arv_Time:{} Num_of_Riders:{} V_Type:{} Free_Text:{} State:{} Num_of_Cur:{} Shareable:{}'.format(
                self.address,
                self.arrival_time,
                str(self.number_riders),
                self.vehicle_type,
                self.free_text,
                str(self.state),
                self.num_current_rider,
                str(self.is_share)
                ))
    def isExpired(self):
        return timezone.now() <= self.arrival_time
    def isOpen(self):
        return (not self.isExpired()) and self.state == 0
    def canEdit(self):
        return  self.isOpen() and self.number_riders == self.num_current_rider


class ShareTrip(models.Model):
    trip = models.ForeignKey(Trip, null=True, blank=True, on_delete=models.SET_NULL)
    sharer = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="mysharer")
    address = models.CharField(max_length=30)
    number_riders = models.IntegerField()
    earliest_time = models.DateTimeField()
    latest_time = models.DateTimeField()
    def __str__(self):
        return self.__unicode__()
    def __unicode__(self):
        return ('Addr:{} Num_of_Riders:{} Earliest_Time:{} Latest_Time:{}'.format(
                self.address,
                str(self.number_riders),
                self.earliest_time,
                self.latest_time
                )
                )



post_save.connect(create_profile, sender = User)
