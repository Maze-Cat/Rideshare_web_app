from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.admin import widgets
from django.forms import ModelForm
from . import models

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    class Meta:
        model = User
        fields = ('username',
                'first_name',
                'last_name',
                'email',
                'password1',
                'password2'
                )
        def save(self, commit=True):
            user = super(RegistrationForm, self).save(commit=False)
            user.first_name =  cleaned_data['first_name']
            user.last_name = cleaned_data['last_name']
            user.email = cleaned_data['email']
            if commit:
                user.save()
            return user

class EditProfileForm(UserChangeForm):
    class Meta:
        model = User
        fields = (
                'email',
                'first_name',
                'last_name'
                )
        pass
    pass

class DriverRegistrationForm(ModelForm):

    class Meta:
        model = models.Driver
        fields = [
                'vehicle_type',
                'license_number',
                'num_passengers',
                'special_info',
                ]


class RideRequestingForm(ModelForm):
    class Meta:
        model = models.Trip
        fields = [
                'address',
                'arrival_time',
                'number_riders',
                'vehicle_type',
                'free_text',
                'is_share',
                ]
        widgets = {
                'arrival_time': forms.DateTimeInput(attrs={'class': 'datetime-input'})
                }
        def clean_is_share(self):
            share = self.cleaned_data['is_share']
            if not (share < 0 or share > 1):
                raise forms.ValidationError("is_share can only be 0 or 1")
            return share



class ShareRequestingForm(ModelForm):
    class Meta:
        model = models.ShareTrip
        fields = [
                'address',
                'number_riders',
                'earliest_time',
                'latest_time',
                ]
