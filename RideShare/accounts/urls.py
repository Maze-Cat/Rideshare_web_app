from django.urls import path, re_path
from . import views
from django.contrib.auth import views as auth_views

app_name='accounts'
urlpatterns = [
path('', views.home),
        path('home/', views.home),
        path('login/', auth_views.LoginView.as_view(template_name = 'accounts/login.html')),
        path('logout/', auth_views.LogoutView.as_view(template_name = 'accounts/logout.html')),
        path('register/', views.register,name='register' ),
        path('profile/', views.view_profile, name='view_profile'),
        path('profile/edit/', views.edit_profile, name = 'edit_profile'),
        path('change_password/', views.change_password, name='change_password'),
        path('reset_password/', auth_views.PasswordResetView.as_view(), name='password_reset'),
        path('reset_password/done', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done' ),
        re_path(r'^reset_password/confirm/(?P<uidb64>[0-9A-Za-z]+)-(?P<token>.+)/$', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm' ),
        path('reset_password/complete', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
        path('driver/registration/', views.driver_registration, name='driver_registration'),
        path('driver/request/view1/', views.ride_status_viewing_driver1, name='ride_status_viewing_driver1'),
        path('user/ride/', views.user_ride_selection, name='user_ride_selection'),
        path('ride/request/edit/<int:trip_id>', views.ride_requesting_editing_owner, name='ride_requesting_editing_owner'),
        #path('ride/request/view/owner/<int:trip_id>', views.ride_status_viewing_owner, name='ride_status_viewing_owner'),
        #path('ride/request/view/sharer/<int:share_trip_id>', views.ride_status_viewing_sharer, name='ride_status_viewing_sharer'),
        path('ride/request/cancel/owner/<int:trip_id>', views.ride_request_cancel_user, name='ride_request_cancel_user'),
        path('ride/request/cancel/sharer/<int:share_trip_id>', views.ride_request_cancel_sharer, name='ride_request_cancel_sharer'),
        #path('ride/request/edit/share/<int:share_trip_id>', views.ride_requesting_editing_sharer, name='ride_requesting_editing_sharer'),
        path('ride/request/user/', views.ride_requesting_user, name='ride_requesting_user'),
        path('ride/request/sharer/<int:trip_id>/<int:share_trip_id>', views.ride_requesting_sharer, name='ride_requesting_sharer'),
        path('ride/search/sharer/', views.ride_searching_sharer, name='ride_searching_sharer'),
        path('driver/search1/', views.ride_searching_driver1, name='ride_searching_driver1'),
        path('driver/confirm/<int:trip_id>/', views.ride_confirm_driver, name='ride_confirm_driver'),
        path('driver/dashboard/', views.driver_dashboard, name='driver_dashboard'),
        path('user/dashboard/', views.user_dashboard, name='user_dashboard'),
        path('role/', views.role_selection, name='role_selection'),
        path('driver/complete/<int:trip_id>/', views.driver_complete, name='driver_complete')

]
