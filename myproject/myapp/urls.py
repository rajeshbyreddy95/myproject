"""
URL configuration for myproject project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from myapp.views import home, official_registration, registration, user_login, official_login, verify_otp, verify_official_otp
from myapp import views

urlpatterns = [
    path('', home, name='home'),  # Add this line
    path('officialregistration', official_registration, name='officialregistraion'),  # Add this line
    path('registration', registration, name='registration'),  # Add this line
    path('verify_otp/', verify_otp, name='verify_otp'),
    path('official/verify_otp/', verify_official_otp, name='verify_official_otp'),
    path('userlogin', user_login, name='userlogin'),
    path('logout/', views.user_logout, name='logout'),
    path('officiallogin', official_login, name='officiallogin'),
    path('userdashboard', views.userdashboard, name='userdashboard'),  # Add this line
    path('receipt_create', views.receipt_create, name='receipt_create'),  # Add this line
    path('receipt/<int:pk>/', views.receipt, name='receipt'),
    path('receipt_inbox', views.receipt_inbox, name='receipt_inbox'),
    path('receipt_sent', views.receipt_sent, name='receipt_sent'),
    path('submit_receipt/<int:pk>/', views.submit_receipt_to_official, name='submit_receipt'),


    path('forgot-password/', views.forgot_password, name='forgotPassword'),
    path('reset-password/<str:username>/', views.reset_password, name='resetPassword'),


    # path('official/dashboard/', views.official_dashboard_redirect, name='official_dashboard'),

    path('official/official_dashboard', views.official_dashboard, name='official_dashboard'),
    path('official/dashboard/official_eLand/', views.official_eLand, name='official_eLand'),
    # path('official/dashboard/clerk_file_create/', views.clerk_file_create, name='clerk_file_create'),
    path('official/dashboard/official_receipt_sent/', views.official_receipt_sent, name='official_receipt_sent'),
    path('official/dashboard/official_receipt_inbox/', views.official_receipt_inbox, name='official_receipt_inbox'),


    path('api/get_file_details/<int:file_id>/', views.get_file_details, name='get_file_details'),


    path("file-create/", views.handle_file_action, name="file_create"),





]

