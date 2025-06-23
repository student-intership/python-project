from django.shortcuts import render,redirect,get_object_or_404
from .models import *
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from datetime import datetime
import random
import os
from myapp.models import Appointment, Add 
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import get_user_model
import razorpay
from django.conf import settings
import json
from django.http import JsonResponse

# Create your views here.

def home(request):
    return render(request,'home')

def index(request):
    return render(request,'index.html')

def about(request):
    return render(request,'about.html')

def appointment(request):
    # Check if user is logged in
    if 'email' not in request.session:
        messages.error(request, "Please login to book an appointment!")
        return redirect('login')
    
    if request.method == "POST":
        try:
            doctor_id = request.POST.get('doctor')
            if not doctor_id:
                raise ValueError("Please select a doctor")
                
            doctor = Add.objects.get(id=doctor_id)
            
            # Get logged in user
            user = User.objects.get(email=request.session['email'])
            
            # Create the appointment with doctor and user
            appointment = Appointment.objects.create(
                doctor=doctor,
                user=user,  # Link appointment to logged in user
                name=request.POST.get('name'),
                email=request.POST.get('email'),
                phone=request.POST.get('phone'),
                age=request.POST.get('age'),
                date_of_birth=request.POST.get('date_of_birth'),
                address=request.POST.get('address'),
                date=request.POST.get('date'),
                time=request.POST.get('time'),
                status='Pending'
            )

            messages.success(request, "Appointment booked successfully!")
            return redirect('payment', appointment_id=appointment.id)

        except Add.DoesNotExist:
            messages.error(request, "Selected doctor not found!")
            return redirect('appointment')
        except ValueError as e:
            messages.error(request, str(e))
            return redirect('appointment')
        except Exception as e:
            messages.error(request, f"Error booking appointment: {str(e)}")
            return redirect('appointment')

    # Get all doctors for the dropdown
    try:
        doctors = Add.objects.all()
        # Get user information for pre-filling the form
        user = User.objects.get(email=request.session['email'])
        context = {
            'doctors': doctors,
            'user': user
        }
        return render(request, 'appointment.html', context)
    except Exception as e:
        messages.error(request, f"Error loading doctors: {str(e)}")
        return redirect('index')

def payment(request, appointment_id):
    # Check if user is logged in
    if 'email' not in request.session:
        messages.error(request, "Please login to access payment!")
        return redirect('login')
    
    try:
        appointment = Appointment.objects.get(id=appointment_id)
        
        # Check if the appointment belongs to the logged-in user
        user = User.objects.get(email=request.session['email'])
        if appointment.user != user:
            messages.error(request, "You can only access your own appointments!")
            return redirect('index')
        
        # Initialize Razorpay client
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        
        # Create Razorpay order
        amount_in_paise = int(appointment.doctor.consultation_fee * 100)  # Convert to paise
        
        order_data = {
            'amount': amount_in_paise,
            'currency': 'INR',
            'receipt': f'appointment_{appointment.id}',
            'notes': {
                'appointment_id': str(appointment.id),
                'doctor_name': appointment.doctor.dname,
                'patient_name': appointment.name
            }
        }
        
        order = client.order.create(data=order_data)
        
        context = {
            'appointment': appointment,
            'razorpay_key': settings.RAZORPAY_KEY_ID,
            'order_id': order['id'],
            'amount': amount_in_paise,
            'title': 'Payment'
        }
        return render(request, 'payment.html', context)
    except Appointment.DoesNotExist:
        messages.error(request, "Appointment not found!")
        return redirect('index')
    except Exception as e:
        messages.error(request, f"Error loading payment page: {str(e)}")
        return redirect('index')

@csrf_exempt
def process_payment(request, appointment_id):
    # Check if user is logged in
    if 'email' not in request.session:
        messages.error(request, "Please login to process payment!")
        return redirect('login')
    
    if request.method == "POST":
        try:
            appointment = Appointment.objects.get(id=appointment_id)
            
            # Check if the appointment belongs to the logged-in user
            user = User.objects.get(email=request.session['email'])
            if appointment.user != user:
                messages.error(request, "You can only process payments for your own appointments!")
                return redirect('index')
            
            # Get payment data from Razorpay
            payment_id = request.POST.get('razorpay_payment_id')
            order_id = request.POST.get('razorpay_order_id')
            signature = request.POST.get('razorpay_signature')
            
            # Verify payment signature
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
            
            try:
                client.utility.verify_payment_signature({
                    'razorpay_order_id': order_id,
                    'razorpay_payment_id': payment_id,
                    'razorpay_signature': signature
                })
                
                # Payment verification successful
                payment = Payment.objects.create(
                    appointment=appointment,
                    amount=appointment.doctor.consultation_fee,
                    payment_method='razorpay',
                    status='Completed',
                    transaction_id=payment_id
                )
                
                # Update appointment status
                appointment.status = 'Confirmed'
                appointment.save()
                
                messages.success(request, "Payment successful! Your appointment is confirmed.")
                return redirect('appointment_success', appointment_id=appointment.id)
                
            except Exception as e:
                # Payment verification failed
                payment = Payment.objects.create(
                    appointment=appointment,
                    amount=appointment.doctor.consultation_fee,
                    payment_method='razorpay',
                    status='Failed',
                    transaction_id=payment_id
                )
                
                messages.error(request, f"Payment verification failed: {str(e)}")
                return redirect('payment', appointment_id=appointment_id)
                
        except Appointment.DoesNotExist:
            messages.error(request, "Appointment not found!")
            return redirect('index')
        except Exception as e:
            messages.error(request, f"Error processing payment: {str(e)}")
            return redirect('payment', appointment_id=appointment_id)
    
    return redirect('index')

def appointment_success(request, appointment_id):
    try:
        appointment = Appointment.objects.get(id=appointment_id)
        context = {
            'appointment': appointment,
            'title': 'Appointment Confirmed'
        }
        return render(request, 'appointment_success.html', context)
    except Appointment.DoesNotExist:
        messages.error(request, "Appointment not found!")
        return redirect('index')

def blog(request):
    return render(request,'blog.html')

def contact(request):
    return render(request,'contact.html')

def service(request):
    return render(request,'service.html')

def team(request):
    return render(request,'team.html')

@csrf_exempt
def login(request):
    if request.method == "POST":
        try:
            user = User.objects.get(email=request.POST['email'])
            
            if user.password == request.POST['password']:
                request.session['email'] = user.email

                if user.usertype == "patient":
                    return redirect('index')
                else:
                    return redirect('dindex')
            else:
                msg = "Invalid Password!!"
                return render(request,'login.html',{'msg':msg})
        except User.DoesNotExist:
            msg = "Invalid Email!!"
            return render(request,'login.html',{'msg':msg})
    else:
        return render(request,'login.html')

def signup(request):
    if request.method == "POST":
        try:
            user = User.objects.get(email = request.POST['email'])
            msg = "Email Already Exits!!"
            return render(request,'signup.html',{'msg': msg})
        except User.DoesNotExist:
            if request.POST['password'] == request.POST['cpassword']:
                User.objects.create(
                    name=request.POST['name'],
                    email=request.POST['email'],
                    mobile=request.POST['mobile'],
                    password=request.POST['password'],
                    usertype=request.POST['usertype']

                )
                msg = "Signup Successfully!!"
                return render(request,'login.html',{'msg':msg})
            else:
                msg = "Pssword & Confirm Password Does Not Match!!"
                return render(request,'signup.html',{'msg':msg})
    else:
        return render(request,'signup.html')
    
def logout(request):
    request.session.pop('email',None)
    request.session.pop('profile',None)
    return redirect('login')
    

def cpass(request):
    if request.method=="POST":
        user = User.objects.get(email=request.session['email'])

        if user.password == request.POST['opassword']:
            if request.POST['npassword']==request.POST['cnpassword']:
                user.password = request.POST['npassword']
                user.save()

                return redirect('logout')


            else:
                msg = "New password & confirm new password does not match!!"
                return render(request,'cpass.html',{'msg':msg})

        else:
            msg = "Old password does not match!!"
            return render(request,'cpass.html',{'msg':msg})
    
    else:
        return render(request,'cpass.html')
    
def dindex(request):
    return render(request,'dindex.html')

def fpass(request):
    if request.method == "POST":
        mobile = request.POST.get('mobile')

        if not mobile or not mobile.isdigit():
            msg = "Please enter a valid mobile number!"
            return render(request, 'fpass.html', {'msg': msg})

        try:
            user = User.objects.get(mobile=int(mobile))  # Cast to int for safety
            otp = random.randint(1000, 9999)

            request.session['otp'] = otp
            request.session['reset_user_id'] = user.id  # Optional: store user to reset password later
            return render(request, 'otp.html')

        except User.DoesNotExist:
            msg = "Mobile number not found!"
            return render(request, 'fpass.html', {'msg': msg})

    return render(request, 'fpass.html')

def otp(request):
    if request.method == "POST":
        entered_otp = request.POST.get('otp')
        session_otp = request.session.get('otp')

        if str(entered_otp) == str(session_otp):
            # OTP is correct – now allow password reset
            return redirect('cpass')  # Create a URL and view for this
        else:
            msg = "Invalid OTP. Please try again."
            return render(request, 'otp.html', {'msg': msg})
    else:
        return render(request, 'otp.html')
    
def dabout(request):
    return render(request,'dabout.html')

def adddoc(request):
    if request.method == "POST":
        try:
            user = User.objects.get(email=request.session.get('email'))
            
            # Create doctor record
            doctor = Add.objects.create(
                user=user,
                dname=request.POST.get('dname'),
                dmobile=request.POST.get('dmobile'),
                dexperience=request.POST.get('dexperience'),
                department=request.POST.get('department'),
                consultation_fee=request.POST.get('consultation_fee'),
                follow_up_fee=request.POST.get('follow_up_fee'),
                emergency_fee=request.POST.get('emergency_fee'),
                description=request.POST.get('description'),
            )

            # Handle profile image upload
            if 'dprofile' in request.FILES:
                doctor.dprofile = request.FILES['dprofile']
                doctor.save()

            messages.success(request, f"Doctor {doctor.dname} added successfully!")
            return redirect('view')

        except User.DoesNotExist:
            messages.error(request, "User not found! Please log in again.")
            return redirect('login')
        except Exception as e:
            messages.error(request, f"Error adding doctor: {str(e)}")
            return render(request, 'adddoc.html')
    else:
        return render(request, 'adddoc.html')

def view(request):
    try:
        # Check session
        if 'email' not in request.session:
            messages.error(request, "Please login first!")
            return redirect('login')

        # Get current user
        user = User.objects.get(email=request.session.get('email'))

        # Role-based query
        if user.usertype == "Doctor":
            # For doctors, show only their own profile
            adds = Add.objects.filter(user=user)
        else:
            # For patients, show all doctors
            adds = Add.objects.all().order_by('dname')

        context = {
            'adds': adds,
            'user': user  # Pass user object to template
        }
        return render(request, 'view.html', context)

    except User.DoesNotExist:
        messages.error(request, "User not found. Please login again.")
        return redirect('login')
    except Exception as e:
        messages.error(request, f"An unexpected error occurred: {str(e)}")
        return redirect('login')


def delete_doctor(request, id):
    try:
        if 'email' not in request.session:
            msg = "Please Login First!"
            return render(request, 'login.html', {'msg': msg})
        
        user = User.objects.get(email=request.session['email'])
        if user.usertype != "Doctor":
            msg = "Access Denied! Only doctors can delete their profiles."
            return render(request, 'login.html', {'msg': msg})
            
        doctor = Add.objects.get(id=id, user=user)
        doctor.delete()
        messages.success(request, "Doctor profile deleted successfully!")
        return redirect('view')
    except Add.DoesNotExist:
        messages.error(request, "Doctor profile not found!")
        return redirect('view')
    except Exception as e:
        messages.error(request, f"Error deleting doctor profile: {str(e)}")
        return redirect('view')

def update(request, id):
    add = None
    try:
        # First check if user is logged in
        if 'email' not in request.session:
            messages.error(request, "Please login first!")
            return redirect('login')

        # Get the current user
        user = User.objects.get(email=request.session.get('email'))
        
        # Try to get the doctor profile
        try:
            add = Add.objects.get(id=id)
        except Add.DoesNotExist:
            messages.error(request, "Doctor profile not found!")
            return redirect('view')
        
        # Check if user has permission to update this profile
        if user.email != add.user.email:
            messages.error(request, "You don't have permission to update this profile!")
            return redirect('view')
            
        if request.method == 'POST':
            # Update fields
            add.dname = request.POST.get('dname')
            add.dmobile = request.POST.get('dmobile')    
            add.department = request.POST.get('department') 
            add.consultation_fee = request.POST.get('consultation_fee')
            add.follow_up_fee = request.POST.get('follow_up_fee')
            add.emergency_fee = request.POST.get('emergency_fee')
            add.description = request.POST.get('description')
            add.dexperience = request.POST.get('dexperience')
            
            # Handle profile image upload
            if 'dprofile' in request.FILES:
                add.dprofile = request.FILES['dprofile']
            
            # Basic validation
            if not add.dname:
                raise ValueError("Doctor name is required!")
            if not add.consultation_fee:
                raise ValueError("Consultation fee is required!")
                
            add.save()
            messages.success(request, f"Doctor {add.dname}'s profile updated successfully!")
            return redirect('view')
            
    except User.DoesNotExist:
        messages.error(request, "User not found! Please login again.")
        return redirect('login')
    except ValueError as e:
        messages.error(request, str(e))
    except Exception as e:
        messages.error(request, f"An error occurred while updating the profile: {str(e)}")
        return redirect('view')
        
    return render(request, 'update.html', {'add': add})
    
def patient_details(request):
    try:
        if 'email' not in request.session:
            messages.error(request, "Please login first!")
            return redirect('login')

        # Get current user
        user = User.objects.get(email=request.session.get('email'))
        
        # Get filter parameter
        status_filter = request.GET.get('status', '')
        
        if user.usertype == "Doctor":
            # For doctors: show all appointments assigned to this doctor
            try:
                # Get all doctor profiles for this user
                doctor_profiles = Add.objects.filter(user=user)
                if doctor_profiles.exists():
                    # Get all appointments for all doctor profiles of this user
                    appointments = Appointment.objects.filter(doctor__in=doctor_profiles).select_related('doctor')
                else:
                    messages.error(request, "Doctor profile not found!")
                    return redirect('view')
            except Exception as e:
                messages.error(request, f"Error loading doctor profiles: {str(e)}")
                return redirect('view')
        else:
            # For patients: show their own appointments
            appointments = Appointment.objects.filter(email=user.email).select_related('doctor')
        
        # Apply status filter if provided
        if status_filter:
            appointments = appointments.filter(status=status_filter)
        
        # Get user's details
        patient_details = {
            'name': user.name,
            'email': user.email,
            'mobile': user.mobile,
        }
        
        # Get available statuses for filter dropdown
        available_statuses = ['Pending', 'Confirmed', 'Cancelled', 'Completed', 'Denied']
        
        context = {
            'user': user,
            'appointments': appointments,
            'patient': patient_details,
            'title': 'Patient Details',
            'status_filter': status_filter,
            'available_statuses': available_statuses
        }
        return render(request, 'patient_details.html', context)
    except User.DoesNotExist:
        messages.error(request, "User not found!")
        return redirect('login')
    except Exception as e:
        messages.error(request, f"Error loading patient details: {str(e)}")
        return redirect('index')

def appointment_details(request, appointment_id):
    """
    View to display detailed information about a specific appointment
    """
    try:
        # Check if user is logged in
        if 'email' not in request.session:
            messages.error(request, "Please login first!")
            return redirect('login')

        # Get current user
        user = User.objects.get(email=request.session.get('email'))
        
        # Get the appointment
        appointment = get_object_or_404(Appointment, id=appointment_id)
        
        # Check permissions based on user type
        if user.usertype == "Doctor":
            # Doctors can only see appointments assigned to them
            doctor_profiles = Add.objects.filter(user=user)
            if not doctor_profiles.filter(id=appointment.doctor.id).exists():
                messages.error(request, "You don't have permission to view this appointment!")
                return redirect('patient_details')
        else:
            # Patients can only see their own appointments
            if appointment.email != user.email:
                messages.error(request, "You don't have permission to view this appointment!")
                return redirect('patient_details')
        
        context = {
            'appointment': appointment,
            'user': user,
            'title': f'Appointment #{appointment.id} Details'
        }
        return render(request, 'appointment_details.html', context)
        
    except User.DoesNotExist:
        messages.error(request, "User not found!")
        return redirect('login')
    except Exception as e:
        messages.error(request, f"Error loading appointment details: {str(e)}")
        return redirect('patient_details')

def cancel_appointment(request, appointment_id):
    """
    View to handle appointment cancellation
    """
    try:
        # Check if user is logged in
        if 'email' not in request.session:
            messages.error(request, "Please login first!")
            return redirect('login')

        # Get current user
        user = User.objects.get(email=request.session.get('email'))
        
        # Get the appointment
        appointment = get_object_or_404(Appointment, id=appointment_id)
        
        # Check permissions based on user type
        if user.usertype == "Doctor":
            # Doctors can only cancel appointments assigned to them
            doctor_profiles = Add.objects.filter(user=user)
            if not doctor_profiles.filter(id=appointment.doctor.id).exists():
                messages.error(request, "You don't have permission to cancel this appointment!")
                return redirect('patient_details')
        else:
            # Patients can only cancel their own appointments
            if appointment.email != user.email:
                messages.error(request, "You don't have permission to cancel this appointment!")
                return redirect('patient_details')
        
        # Check if appointment can be canceled
        if appointment.status in ['Cancelled', 'Completed']:
            messages.error(request, "This appointment cannot be canceled as it's already cancelled or completed.")
            return redirect('patient_details')
        
        if request.method == "POST":
            # Process cancellation
            cancel_reason = request.POST.get('cancel_reason')
            cancel_type = request.POST.get('cancel_type')
            notify_patient = request.POST.get('notify_patient') == 'on'
            
            if not cancel_reason or not cancel_type:
                messages.error(request, "Please provide both reason and type for cancellation.")
                return render(request, 'cancel.html', {'appointment': appointment, 'user': user})
            
            # Update appointment status
            appointment.status = 'Cancelled'
            appointment.save()
            
            # Here you could save cancellation details to a separate model if needed
            # For now, we'll just update the status
            
            # Show success message
            if user.usertype == "Doctor":
                messages.success(request, f"Appointment #{appointment.id} has been cancelled successfully.")
            else:
                messages.success(request, "Your appointment has been cancelled successfully.")
            
            return redirect('patient_details')
        
        # GET request - show cancellation form
        context = {
            'appointment': appointment,
            'user': user,
            'title': f'Cancel Appointment #{appointment.id}'
        }
        return render(request, 'cancel.html', context)
        
    except User.DoesNotExist:
        messages.error(request, "User not found!")
        return redirect('login')
    except Exception as e:
        messages.error(request, f"Error processing cancellation: {str(e)}")
        return redirect('patient_details')

def print_appointments(request):
    """
    View to handle appointment printing with various filter options
    """
    try:
        # Check if user is logged in
        if 'email' not in request.session:
            messages.error(request, "Please login first!")
            return redirect('login')

        # Get current user
        user = User.objects.get(email=request.session.get('email'))
        
        # Get filter parameters
        status_filter = request.GET.get('status', '')
        appointment_id = request.GET.get('appointment_id', '')
        print_type = request.GET.get('type', 'all')  # all, upcoming, single
        
        if user.usertype == "Doctor":
            # For doctors: show all appointments assigned to this doctor
            try:
                # Get all doctor profiles for this user
                doctor_profiles = Add.objects.filter(user=user)
                if doctor_profiles.exists():
                    # Get all appointments for all doctor profiles of this user
                    appointments = Appointment.objects.filter(doctor__in=doctor_profiles).select_related('doctor')
                else:
                    messages.error(request, "Doctor profile not found!")
                    return redirect('view')
            except Exception as e:
                messages.error(request, f"Error loading doctor profiles: {str(e)}")
                return redirect('view')
        else:
            # For patients: show their own appointments
            appointments = Appointment.objects.filter(email=user.email).select_related('doctor')
        
        # Apply filters based on print type
        if print_type == 'upcoming':
            appointments = appointments.filter(status='Confirmed')
        elif print_type == 'single' and appointment_id:
            appointments = appointments.filter(id=appointment_id)
        elif status_filter:
            appointments = appointments.filter(status=status_filter)
        
        # Get current date
        current_date = datetime.now().strftime('%B %d, %Y')
        
        # Prepare context
        context = {
            'user': user,
            'appointments': appointments,
            'current_date': current_date,
            'status_filter': status_filter,
            'print_type': print_type,
            'title': f'Appointment Report - {print_type.title()}'
        }
        
        # If single appointment, add it to context
        if print_type == 'single' and appointment_id:
            try:
                single_appointment = appointments.first()
                context['appointment'] = single_appointment
                context['title'] = f'Appointment #{appointment_id} Details'
            except:
                pass
        
        return render(request, 'print.html', context)
        
    except User.DoesNotExist:
        messages.error(request, "User not found!")
        return redirect('login')
    except Exception as e:
        messages.error(request, f"Error generating print report: {str(e)}")
        return redirect('patient_details')

def appointment_print(request):
    """
    View to handle appointment print from navigation menu
    """
    try:
        # Check if user is logged in
        if 'email' not in request.session:
            messages.error(request, "Please login first!")
            return redirect('login')

        # Get current user
        user = User.objects.get(email=request.session.get('email'))
        
        # Get filter parameters
        status_filter = request.GET.get('status', '')
        print_type = request.GET.get('type', 'all')  # all, upcoming, confirmed, pending
        
        if user.usertype == "Doctor":
            # For doctors: show all appointments assigned to this doctor
            try:
                # Get all doctor profiles for this user
                doctor_profiles = Add.objects.filter(user=user)
                if doctor_profiles.exists():
                    # Get all appointments for all doctor profiles of this user
                    appointments = Appointment.objects.filter(doctor__in=doctor_profiles).select_related('doctor')
                else:
                    messages.error(request, "Doctor profile not found!")
                    return redirect('view')
            except Exception as e:
                messages.error(request, f"Error loading doctor profiles: {str(e)}")
                return redirect('view')
        else:
            # For patients: show their own appointments
            appointments = Appointment.objects.filter(email=user.email).select_related('doctor')
        
        # Apply filters based on print type
        if print_type == 'upcoming':
            appointments = appointments.filter(status='Confirmed')
        elif print_type == 'confirmed':
            appointments = appointments.filter(status='Confirmed')
        elif print_type == 'pending':
            appointments = appointments.filter(status='Pending')
        elif status_filter:
            appointments = appointments.filter(status=status_filter)
        
        # Get current date
        current_date = datetime.now().strftime('%B %d, %Y')
        
        # Get available statuses for filter dropdown
        available_statuses = ['Pending', 'Confirmed', 'Cancelled', 'Completed', 'Denied']
        
        # Prepare context
        context = {
            'user': user,
            'appointments': appointments,
            'current_date': current_date,
            'status_filter': status_filter,
            'print_type': print_type,
            'available_statuses': available_statuses,
            'title': f'Appointment Print - {print_type.title()}'
        }
        
        return render(request, 'appointment_print.html', context)
        
    except User.DoesNotExist:
        messages.error(request, "User not found!")
        return redirect('login')
    except Exception as e:
        messages.error(request, f"Error loading appointment print page: {str(e)}")
        return redirect('patient_details')

def print(request):
    """
    View to handle the print.html template for printing appointments
    """
    try:
        # Check if user is logged in
        if 'email' not in request.session:
            messages.error(request, "Please login first!")
            return redirect('login')

        # Get current user
        user = User.objects.get(email=request.session.get('email'))
        
        # Get parameters
        appointment_id = request.GET.get('appointment_id', '')
        print_type = request.GET.get('type', 'all')
        status_filter = request.GET.get('status', '')
        date_from = request.GET.get('date_from', '')
        date_to = request.GET.get('date_to', '')
        
        if user.usertype == "Doctor":
            # For doctors: show all appointments assigned to this doctor
            try:
                # Get all doctor profiles for this user
                doctor_profiles = Add.objects.filter(user=user)
                if doctor_profiles.exists():
                    # Get all appointments for all doctor profiles of this user
                    appointments = Appointment.objects.filter(doctor__in=doctor_profiles).select_related('doctor')
                else:
                    messages.error(request, "Doctor profile not found!")
                    return redirect('view')
            except Exception as e:
                messages.error(request, f"Error loading doctor profiles: {str(e)}")
                return redirect('view')
        else:
            # For patients: show their own appointments
            appointments = Appointment.objects.filter(email=user.email).select_related('doctor')
        
        # Apply filters
        if appointment_id:
            # Single appointment
            appointments = appointments.filter(id=appointment_id)
            single_appointment = appointments.first() if appointments.exists() else None
        else:
            # Multiple appointments with filters
            if print_type == 'upcoming':
                appointments = appointments.filter(status='Confirmed')
            elif print_type == 'pending':
                appointments = appointments.filter(status='Pending')
            elif print_type == 'confirmed':
                appointments = appointments.filter(status='Confirmed')
            
            if status_filter:
                appointments = appointments.filter(status=status_filter)
            
            if date_from:
                appointments = appointments.filter(date__gte=date_from)
            
            if date_to:
                appointments = appointments.filter(date__lte=date_to)
            
            single_appointment = None
        
        # Get current date
        current_date = datetime.now().strftime('%B %d, %Y')
        
        # Prepare title based on print type
        if appointment_id:
            title = f"Appointment #{appointment_id} Details"
        elif print_type == 'upcoming':
            title = "Upcoming Appointments"
        elif print_type == 'pending':
            title = "Pending Appointments"
        elif print_type == 'confirmed':
            title = "Confirmed Appointments"
        elif status_filter:
            title = f"{status_filter} Appointments"
        else:
            title = "All Appointments"
        
        context = {
            'user': user,
            'appointments': appointments,
            'appointment': single_appointment,
            'current_date': current_date,
            'status_filter': status_filter,
            'print_type': print_type,
            'title': title
        }
        
        return render(request, 'print.html', context)
        
    except User.DoesNotExist:
        messages.error(request, "User not found!")
        return redirect('login')
    except Exception as e:
        messages.error(request, f"Error generating print view: {str(e)}")
        return redirect('patient_details')


