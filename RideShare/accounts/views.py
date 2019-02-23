from django.shortcuts import render, redirect
from accounts.forms import RegistrationForm, EditProfileForm, DriverRegistrationForm, RideRequestingForm, ShareRequestingForm
from django.contrib.auth.forms import UserChangeForm, PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from accounts.models import Driver, Trip, ShareTrip, UserProfile
from django.http import HttpResponse
from django.db.models import Q
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings

def isValidDriver(request):
    related_drivers = Driver.objects.filter(user=request.user)
    return related_drivers.count() == 1


def home(request):

    return render(request, 'accounts/home.html')

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            send_mail('Hello from Rideshare','Your account has been set up!',settings.EMAIL_HOST_USER,[form.cleaned_data['email']])
            return redirect('/account/login')
        else:
            return render(request, 'accounts/error.html', {'error':'Form is invalid...'})

    else:
        form = RegistrationForm()
        args = {'form':form}
        return render(request, 'accounts/reg_form.html', args)


@login_required
def view_profile(request):
    drivers = Driver.objects.filter(user=request.user)
    if(drivers.count()):
        driver = Driver.objects.get(user=request.user)
        args = {'user': request.user, 'driver':driver}
        return render(request, 'accounts/profile_driver.html', args)
    else:
        args = {'user': request.user}
        return render(request, 'accounts/profile.html', args)


@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=request.user)

        if form.is_valid():
            form.save()
            return redirect('/account/profile')
    else:
        form = EditProfileForm(instance=request.user)
        args = {'form': form}
        return render(request, 'accounts/edit_profile.html', args)

@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(data=request.POST, user=request.user)

        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            return redirect('/account/profile')
        else:
            return redirect('/account/change_password')
    else:
        form = PasswordChangeForm(user=request.user)
        args = {'form': form}
        return render(request, 'accounts/change_password.html', args)

@login_required
def driver_registration(request):

    related_drivers = Driver.objects.filter(user=request.user)
    if not related_drivers.count() == 0:
        return render(request, 'accounts/error.html', {'error': 'You can only register as a driver once!'})

    if request.method == 'POST':
        form = DriverRegistrationForm(request.POST)
        if not form.is_valid():
            return render(request, "accounts/error.html", {'error': 'Form is not valid!'})
        mydriver = form.save(commit=False)
        mydriver.user = request.user
        mydriver.save()
        return redirect('/account/driver/dashboard')

    form = DriverRegistrationForm()
    args = {'form':form}
    return render(request, 'accounts/driver_registration.html', args)

@login_required
def role_selection(request):
    return render(request, 'accounts/role_selection.html')

@login_required
def driver_dashboard(request):
    if not isValidDriver(request):
        return redirect('/account/driver/registration')
    return render(request, "accounts/driver_dashboard.html")

@login_required
def user_dashboard(request):
    return render(request, "accounts/user_dashboard.html")

@login_required
def user_ride_selection(request):

    related_ride = Trip.objects.filter(
            Q( rider=request.user) &
            Q(state__lte=1) &
            Q(arrival_time__gte=timezone.now()))
    related_share = ShareTrip.objects.filter(
            Q(sharer=request.user) &
            Q(trip__state__lte = 1) &
            Q(trip__arrival_time__gte=timezone.now())
            )
    args = {
            'related_ride':related_ride,
            'related_share': related_share
            }
    return render(request, 'accounts/user_cur_trips.html', args)

@login_required
def ride_requesting_editing_owner(request, trip_id):
    mytrip = Trip.objects.get(id=trip_id)
    if not mytrip.rider.id == request.user.id:
        return render(request, 'accounts/error.html', {'error': 'You do not own this trip.'})
    if request.method == 'POST':
        form = RideRequestingForm(request.POST, instance=mytrip)
        if (form.is_valid() and
                mytrip.state == 0
                and mytrip.num_current_rider == mytrip.number_riders): # ensure current trip has no sharers
            form.num_current_rider = form.cleaned_data['number_riders']
            form.save()
            return redirect('/account/user/ride') #Success
        else:
            return render(request,'accounts/error.html', {'error': 'form is not valid or this trip cannot be edited'}) #form error
    else:
        form = RideRequestingForm(instance=mytrip)
        return render(request, 'accounts/general_form.html', {'form':form, 'topic':'Edit user requset form'}) ## GET FORM

#@login_required
#def ride_requesting_editing_sharer(request, share_trip_id):
#    share_trip = ShareTrip.objects.get(id=share_trip_id)
#    if not share_trip.sharer.id == request.user.id:
#        return render(request, 'accounts/error.html', {'error': 'This share trip does not belong to you!'})
#    prev_number = share_trip.number_riders
#    if request.method == 'POST':
#        form = ShareRequestingForm(request.POST, instance=share_trip)
#        if form.is_valid():
#            if share_trip.trip:
#                share_trip.trip.num_current_rider -= prev_number #if joined open trip, then remove from that
#                share_trip.trip = None
#            new_share_trip = form.save(commit=False)
#            new_share_trip.trip = None
#            new_share_trip.save()
#            return render(request,'', args) ##TODO SUCCESS
#        else:
#            return render(request,'',args) ##TODO invalid form
#    else:
#        return render(request, '', args) ##TODO GET form



@login_required
def ride_requesting_user(request):
    if request.method == 'POST':
        form = RideRequestingForm(request.POST)
        if(form.is_valid() and ( 0 <= form.cleaned_data['is_share'] <= 1 ) and form.cleaned_data['arrival_time'] >= timezone.now() ):
            trip = form.save(commit=False)
            trip.state = 0
            trip.driver = None
            trip.rider = request.user
            trip.num_current_rider = form.cleaned_data['number_riders']
            form.save()
            return redirect('/account/user/ride/') # success
        else:
            return render(request, 'accounts/error.html', {'error':'Invalid user requesting form.'})
    else:
        form = RideRequestingForm()
        return render(request, 'accounts/general_form.html', {'form':form, 'topic':'User request form'}) # GET form

@login_required
def ride_requesting_sharer(request, trip_id, share_trip_id):
    trip = Trip.objects.get(id=trip_id)
    share_trip = ShareTrip.objects.get(id=share_trip_id)
    if not trip.state == 0:
        return render(request, 'accounts/error.html', {'error': 'Trip is already confirmed by a driver.'}) ##trip is already confirmed by driver
    if not trip.address == share_trip.address:
        return render(request,'accounts/error.html', {'error': 'Address doesn not match'}) ## address not match(modified by owner)
    if not share_trip.sharer.id == request.user.id:
        return render(request, 'accounts/error.html', {'error': 'You have no right to access this share trip.'})
    if trip.arrival_time < share_trip.earliest_time or trip.arrival_time > share_trip.latest_time:
        return render(request, 'accounts/error.html', {'error': 'Your time does not fit this open trip.'})
    trip.num_current_rider += share_trip.number_riders
    trip.sharers.add(request.user)
    share_trip.trip = trip
    share_trip.save()
    trip.save()
    return redirect( '/account/user/ride/')





@login_required
def ride_searching_sharer(request):

    if(request.method == 'POST'):
        form = ShareRequestingForm(request.POST)
        if form.is_valid():
            share_trip = form.save(commit=False)
            share_trip.trip = None
            share_trip.sharer = request.user
            number_riders = share_trip.number_riders
            #driver_s_trips = request.user.mysharer.all()
            ########################################
            ########################################
            rider_trips = request.user.myrider.all()
            sharer_trips = request.user.share_trips.all() #sharer_trips_fd = sharer_trips__trip

            open_trips = Trip.objects.filter(Q(state=0) &
                    Q(is_share=1) &
                    Q(arrival_time__gte=share_trip.earliest_time) &
                    Q(arrival_time__lte=share_trip.latest_time) &
                    Q(address=share_trip.address)).exclude(
                    Q(driver__user = request.user) |
                    Q(pk__in=rider_trips) |
                    Q(pk__in=sharer_trips)
                    )

            

            if not open_trips.count() == 0:
                share_trip.save()
            return render(request, 'accounts/sharer_open_trips.html', {'num_trips':str(open_trips.count()),'trips':open_trips, 'myshare':str(share_trip.id)})
        else:
            return render(request, 'accounts/error.html', {'error':'Form is invalid real form!'})
    else:
        form = ShareRequestingForm()
        return render(request, 'accounts/general_form.html', {'form':form, 'topic':'Share searching'})


#@login_required
#def ride_status_viewing_owner(request, trip_id):
#    current_profile = UserProfile.objects.get(user=request.user)
#    mytrip = Trip.objects.get(id=trip_id)
#    if mytrip.rider.id == current_profile.id:
#        if mytrip.state < 2:
#            return render(request, '', args) #TODO request success
#        else:
#            return render(request, '', args) #TODO status error
#    else:
#        return render(request, '', args) #TODO trip->user error
#
#@login_required
#def ride_status_viewing_sharer(request, share_trip_id):
#    current_profile = UserProfile.objects.get(user=request.user)
#    sharetrip = ShareTrip.objects.get(id=share_trip_id)
#    if sharetrip.sharer.id == current_profile.id:
#        if sharetrip.state < 2:
#            return render(request, '', args) #TODO: request success
#        else:
#            return render(request, '', args) #TODO: request error
#    else:
#        return render(request, '', args) #TODO:trip->user error
#
@login_required
def ride_status_viewing_driver1(request):
    if not isValidDriver(request):
        return render(request, "accounts/error.html", {'error':'You have not registered as a Driver!'})
    cur_driver = Driver.objects.get(user=request.user)
    rides = Trip.objects.filter(
            Q(driver=cur_driver) &
            Q(state__lte=1)
            )
    return render(request, 'accounts/driver_cur_trips.html', {'trips':rides, 'driver:':cur_driver})

@login_required
def ride_searching_driver1(request):
    if not isValidDriver(request):
        return render(request, "accounts/error.html", {'error':'You have not registered as a Driver!'})
    driver = Driver.objects.get(user=request.user)
    driver_trips = driver.mydriver.all()
    rider_trips = request.user.myrider.all()
    share_trips = request.user.share_trips.all() ## ShareTrip type
    trips = Trip.objects.filter(
            Q(driver__isnull=True) &
            Q(state=0) &
            Q(num_current_rider__lte=driver.num_passengers)&
            (Q(vehicle_type__isnull=True) | Q(vehicle_type=driver.vehicle_type)) &
            (Q(free_text__isnull=True) |Q(free_text=driver.special_info) ) &
            Q(arrival_time__gte = timezone.now())
            ).exclude(
            Q(driver__user = request.user) |
            Q(pk__in=rider_trips) |
            Q(pk__in=share_trips)
                    ) ## exclude all sharer trip and owner trip this driver request

    return render(request, 'accounts/driver_trips.html', {'trips':trips, 'driver':driver})


@login_required
def ride_confirm_driver(request ,trip_id):
    if not isValidDriver(request):
        return render(request, "accounts/error.html", {'error':'You have not registered as a Driver!'})

    driver = Driver.objects.get(user=request.user)
    trip = Trip.objects.get(id=trip_id)

    if(trip.driver is None and
            trip.state == 0 and
            timezone.now() <  trip.arrival_time and
            trip.num_current_rider <= driver.num_passengers and
            (trip.free_text is None) or (trip.free_text == driver.special_info)):
        trip.state = 1
        trip.driver = driver
        trip.save()
        #TODO SEND EMAIL
        content_rider =  'Your trip '+str(trip_id)+' has been confirmed!'
        content_sharer =  'Your shared trip '+str(trip_id)+' has been confirmed!'
        to_sharer = []
        for share in trip.sharers.all():
            to_sharer.append(share.email)

        send_mail('Trip confirmed from Rideshare',content_rider,settings.EMAIL_HOST_USER,[trip.rider.email])
        send_mail('Trip confirmed from Rideshare',content_sharer,settings.EMAIL_HOST_USER,to_sharer, fail_silently = False)
        return redirect('/account/driver/request/view1')
    else:
        return render(request, 'accounts/error.html', {'error': 'This trip is no longer valid'})

#@login_required
#def ride_status_viewing_owner(request, trip_id):
#    mytrip = Trip.onjects.get(trip_id)
#    if mytrip.user.id != request.user.id:
#        return render(request, 'accounts/error.html', {'error':'This trip does not belong to you!'})
#    related_share = ShareTrip.objects.filter(trip=mytrip)
#    return render(request, 'accounts/user_one_trip_view.html', {'trip':mytrip, 'shares':related_share})

@login_required
def ride_request_cancel_user(request, trip_id):
    trip = Trip.objects.get(id=trip_id)
    if not trip.rider.id == request.user.id:
        return render(request, 'accounts/error.html', {'error': 'You do not own this trip.'})
    if not trip.state == 0:
        return render(request, 'accounts/error.html', {'error': 'You do not own this trip.'})
    content = 'Your trip '+ str(trip_id)+ ' has been cancelled!'
    send_mail('Your Cancelled Trip from Rideshare',content,settings.EMAIL_HOST_USER,[trip.rider.email])
    trip.state = 3
    trip.save()
    trip.delete()
    return redirect('/account/user/ride')

@login_required
def ride_request_cancel_sharer(request, share_trip_id):
    share_trip = ShareTrip.objects.get(id=share_trip_id)
    if not share_trip.sharer.id == request.user.id:
        return render(request, 'accounts/error.html', {'error': 'This share trip does not belong to you.'})
    if not share_trip.trip.state == 0:
        return render(request, 'accounts/error.html', {'error': 'You do not join this share trip'})
    content = 'Your trip '+ str(share_trip_id)+ ' has been cancelled!'
    send_mail('Your Cancelled Trip from Rideshare',content,settings.EMAIL_HOST_USER,[share_trip.sharer.email])
    share_trip.trip.sharers.remove(request.user)
    share_trip.trip.save()
    share_trip.delete()
    return redirect('/account/user/ride')
@login_required
def driver_complete(request, trip_id):
    trip = Trip.objects.get(id=trip_id)
    if not trip.driver.user.id == request.user.id:
        return render(request, 'accounts/error.html', {'error': 'This trip belongs to another driver.'})
    to_sharer = []
    for share in trip.sharers.all():
        to_sharer.append(share.email)
    send_mail('Your Complete Trip from Rideshare','Your trip '+str(trip_id)+' as rider has been completed!',settings.EMAIL_HOST_USER,[trip.rider.email])
    send_mail('Your Complete Trip from Rideshare','Your trip '+str(trip_id)+' as sharer has been completed!',settings.EMAIL_HOST_USER,to_sharer)
    send_mail('Your Complete Trip from Rideshare','Your trip '+str(trip_id)+' as driver has been completed!',settings.EMAIL_HOST_USER,[trip.driver.user.email])
    trip.state = 2
    trip.save()
    return redirect('/account/driver/request/view1')
