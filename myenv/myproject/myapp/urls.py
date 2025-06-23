"""myproject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.urls import path,include
from . import views

urlpatterns = [
    path('index/', views.index, name='index'),
    path('dindex/', views.dindex, name='dindex'),
    path('about/', views.about, name='about'),
    path('dabout/', views.dabout, name='dabout'),
    path('blog/', views.blog, name='blog'),
    path('contact/', views.contact, name='contact'),
    path('service/', views.service, name='service'),
    path('team/', views.team, name='team'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('cpass/', views.cpass, name='cpass'),
    path('fpass/', views.fpass, name='fpass'),
    path('otp/', views.otp, name='otp'),
    path('signup/', views.signup, name='signup'),
    path('appointment/', views.appointment, name='appointment'),

    path('adddoc/', views.adddoc, name='adddoc'),
    path('view/', views.view, name='view'),
    path('payment/<int:appointment_id>/', views.payment, name='payment'),
    path('process_payment/<int:appointment_id>/', views.process_payment, name='process_payment'),
    path('appointment_success/<int:appointment_id>/', views.appointment_success, name='appointment_success'),
    path('delete_doctor/<int:id>/', views.delete_doctor, name='delete_doctor'),
    path('update/<int:id>/', views.update, name='update'),
    path('patient-details/', views.patient_details, name='patient_details'),
    path('appointment-details/<int:appointment_id>/', views.appointment_details, name='appointment_details'),
    path('cancel-appointment/<int:appointment_id>/', views.cancel_appointment, name='cancel_appointment'),
    path('print-appointments/', views.print_appointments, name='print_appointments'),
    path('appointment-print/', views.appointment_print, name='appointment_print'),
    path('print/', views.print, name='print'),
]
