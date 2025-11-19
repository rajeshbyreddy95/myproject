from datetime import timedelta
from io import BytesIO
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.core.mail import send_mail
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from datetime import datetime

from xhtml2pdf import pisa

from .constants import  ROLE_CHOICES
from .forms import (
    IndividualUserCreationForm,
    OfficialUserRegistrationForm,
    LandRequestForm,
    ForgotPasswordForm,
    ResetPasswordForm,
)
from .models import CustomUser, LandRequest, LandRequestHistory
from .utils import (
    generate_otp,
    get_next_official,
    send_otp,
    verify_otp_pass,
)

# Get the custom user model
User = get_user_model()



def home(request):
    context = {
        "role_choices": ROLE_CHOICES
    }
    return render(request, 'index.html', context)

def registration(request):
    if request.method == 'POST':
        form = IndividualUserCreationForm(request.POST)
        if form.is_valid():
            # Create a copy of cleaned data
            reg_data = form.cleaned_data.copy()
            # Convert the date field to an ISO formatted string, if it exists
            if 'dob' in reg_data and reg_data['dob']:
                reg_data['dob'] = reg_data['dob'].isoformat()

            otp = generate_otp()
            request.session['registration_data'] = reg_data
            request.session['registration_otp'] = otp
            request.session['otp_timestamp'] = datetime.now().isoformat()

            # Send the OTP via email
            send_mail(
                subject='Your OTP for Registration',
                message=f'Your OTP is: {otp}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[reg_data['email']],
                fail_silently=False,
            )
            return redirect('verify_otp')
        else:
            print("Form errors:", form.errors)
    else:
        form = IndividualUserCreationForm()
    return render(request, 'register.html', {'form': form})

from datetime import datetime, timedelta

def verify_otp(request):
    can_resend = False
    resend_delay = 60  # seconds

    # Check resend eligibility
    otp_timestamp_str = request.session.get('otp_timestamp')
    if otp_timestamp_str:
        otp_time = datetime.fromisoformat(otp_timestamp_str)
        now = datetime.now()
        if (now - otp_time).total_seconds() >= resend_delay:
            can_resend = True

    if request.method == 'POST':
        if 'resend_otp' in request.POST:
            if can_resend:
                otp = generate_otp()
                request.session['registration_otp'] = otp
                request.session['otp_timestamp'] = datetime.now().isoformat()
                can_resend = False  # 🔥 Force it false so the page shows countdown again

                reg_data = request.session.get('registration_data')
                if reg_data:
                    send_mail(
                        subject='Your New OTP for Registration',
                        message=f'Your new OTP is: {otp}',
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[reg_data['email']],
                        fail_silently=False,
                    )
                    messages.add_message(
                        request,
                        messages.SUCCESS,
                        "A new OTP has been sent to your email.",
                        extra_tags='success'
                    )
                else:
                    messages.add_message(
                        request,
                        messages.ERROR,
                        "Registration data not found. Please restart registration.",
                        extra_tags='danger'
                    )
            else:
                messages.add_message(
                    request,
                    messages.WARNING,
                    f"Please wait {resend_delay} seconds before resending the OTP.",
                    extra_tags='warning'
                )
        else:
            # Normal OTP verification
            entered_otp = request.POST.get('otp')
            session_otp = request.session.get('registration_otp')
            if entered_otp == session_otp:
                reg_data = request.session.get('registration_data')
                if reg_data:
                    user = User.objects.create_user(
                        username=reg_data['username'],
                        password=reg_data['password1'],
                        first_name=reg_data['first_name'],
                        middle_name=reg_data.get('middle_name', ''),
                        last_name=reg_data['last_name'],
                        email=reg_data['email'],
                        phone=reg_data['phone'],
                        dob=reg_data['dob'],
                        gender=reg_data['gender'],
                        aadhar=reg_data['aadhar'],
                        address=reg_data['address'],
                        user_type='individual'
                    )
                    del request.session['registration_data']
                    del request.session['registration_otp']
                    del request.session['otp_timestamp']
                    # Inside your successful OTP verification block:
                    messages.success(request, "Registration successful! Welcome.")
                    return redirect('home')  # Or another page after registration
                else:
                    messages.add_message(
                        request,
                        messages.ERROR,
                        "Registration data not found. Please try again.",
                        extra_tags='danger'
                    )
            else:
                messages.add_message(
                    request,
                    messages.ERROR,
                    "Invalid OTP. Please try again.",
                    extra_tags='danger'
                )

    return render(request, 'verify_otp.html', {
    'can_resend': can_resend,
    'resend_label': 'Resend OTP',
    'otp_title': 'Individual OTP Verification'  # or 'Official OTP Verification'
})


def official_registration(request):
    if request.method == 'POST':
        form = OfficialUserRegistrationForm(request.POST)
        if form.is_valid():
            # Generate OTP
            otp = generate_otp()
            # Copy the cleaned data
            reg_data = form.cleaned_data.copy()
            # Convert any non-serializable objects (if needed) here
            
            # Store the data and OTP in session with keys specific for officials
            request.session['official_registration_data'] = reg_data
            request.session['official_registration_otp'] = otp
            request.session['official_otp_timestamp'] = datetime.now().isoformat()

            # Send OTP via email
            send_mail(
                subject='Your OTP for Official Registration',
                message=f'Your OTP is: {otp}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[reg_data['email']],
                fail_silently=False,
            )
            return redirect('verify_official_otp')
        else:
            print("Form errors:", form.errors)
    else:
        form = OfficialUserRegistrationForm()
    return render(request, 'officialregistration.html', {'form': form})

def verify_official_otp(request):
    can_resend = False
    resend_delay = 60  # seconds

    # Check resend eligibility
    otp_timestamp_str = request.session.get('official_otp_timestamp')
    if otp_timestamp_str:
        otp_time = datetime.fromisoformat(otp_timestamp_str)
        now = datetime.now()
        if (now - otp_time).total_seconds() >= resend_delay:
            can_resend = True

    if request.method == 'POST':
        if 'resend_otp' in request.POST:
            if can_resend:
                otp = generate_otp()
                request.session['official_registration_otp'] = otp
                request.session['official_otp_timestamp'] = datetime.now().isoformat()
                can_resend = False  # 🔥 Force it false so the page shows countdown again

                reg_data = request.session.get('official_registration_data')
                if reg_data:
                    send_mail(
                        subject='Your New OTP for Official Registration',
                        message=f'Your new OTP is: {otp}',
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[reg_data['email']],
                        fail_silently=False,
                    )
                    messages.add_message(
                        request,
                        messages.SUCCESS,
                        "A new OTP has been sent to your email.",
                        extra_tags='success'
                    )
                else:
                    messages.add_message(
                        request,
                        messages.ERROR,
                        "Registration data not found. Please restart registration.",
                        extra_tags='danger'
                    )
            else:
                messages.add_message(
                    request,
                    messages.WARNING,
                    f"Please wait {resend_delay} seconds before resending the OTP.",
                    extra_tags='warning'
                )
        else:
            entered_otp = request.POST.get('otp')
            session_otp = request.session.get('official_registration_otp')
            if entered_otp == session_otp:
                reg_data = request.session.get('official_registration_data')
                if reg_data:
                    user = User.objects.create_user(
                        username=reg_data['username'],
                        password=reg_data['password1'],
                        first_name=reg_data['first_name'],
                        last_name=reg_data['last_name'],
                        email=reg_data['email'],
                        phone=reg_data.get('phone', ''),
                        designation=reg_data.get('designation', ''),
                        department=reg_data.get('department', ''),
                        office_id=reg_data.get('office_id', ''),
                        user_type='official',
                    )
                    user.save()
                    del request.session['official_registration_data']
                    del request.session['official_registration_otp']
                    del request.session['official_otp_timestamp']
                    messages.success(request, "Registration successful. Welcome!", extra_tags='success')
                    return redirect('home')
                else:
                    messages.add_message(
                        request,
                        messages.ERROR,
                        "Registration data not found. Please try again.",
                        extra_tags='danger'
                    )
            else:
                messages.add_message(
                    request,
                    messages.ERROR,
                    "Invalid OTP. Please try again.",
                    extra_tags='danger'
                )

    return render(request, 'verify_otp.html', {
    'can_resend': can_resend,
    'resend_label': 'Resend OTP',
    'otp_title': 'Individual OTP Verification'  # or 'Official OTP Verification'
})


def user_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.user_type != 'individual':
                messages.error(request, "Please use the official login form.", extra_tags='danger')
                return redirect('home')
            login(request, user)
            messages.success(request, "Login successful. Welcome!", extra_tags='success')
            return redirect('userdashboard')
        else:
            messages.error(request, "Invalid username or password.", extra_tags='danger')
            return redirect('home')
    
    return render(request, 'index.html')


def user_logout(request):
    logout(request)  # Logs out the user
    messages.success(request, "You have successfully logged out.", extra_tags="success")
    return redirect('home')  # Redirect to your desired page, e.g., homepag

@login_required  # Ensures only logged-in users can access the dashboard
def userdashboard(request):
    user = request.user  # This retrieves the currently authenticated user
    context = {
        'user': user,
    }
    return render(request, 'eLand.html', context)


def get_official_by_role(role):
    """
    Returns the first official (User) matching the role (designation).
    Adjust the query as needed based on your CustomUser model.
    """
    return User.objects.filter(designation__iexact=role, user_type='official').first()

from weasyprint import HTML
import json
import base64
try:
    import qrcode
except Exception:
    qrcode = None

def generate_receipt_pdf(land_request):
    html_string = render_to_string('receipt_pdf.html', {'land_request': land_request})
    pdf_file = BytesIO()
    HTML(string=html_string).write_pdf(target=pdf_file)
    return pdf_file.getvalue()



from django.utils.timezone import now
from .blockchain_api import upload_file_to_pinata 
from django.core.files.base import ContentFile
import os
 # import your new function
from django.conf import settings
from django.utils.timezone import now
from datetime import timedelta
@login_required
def receipt_create(request):
    """
    Create a LandRequest, generate its receipt PDF,
    and forward it to the Clerk while maintaining a workflow history.
    """
    if request.method == 'POST':
        form = LandRequestForm(request.POST, request.FILES)
        if form.is_valid():
            # Save the form but do not commit to DB yet
            land_request = form.save(commit=False)
            land_request.created_by = request.user  # Assign creator
            land_request.status = 'clerk_review'  # Set initial status
            land_request.created_at = now()  # Ensure timestamp consistency
            land_request.file_no = land_request.survey_number
            land_request.subject = "Land Record Management"
            
            # Assign the request to the Clerk
            clerk = get_official_by_role('Clerk')
            if clerk:
                land_request.currently_with = clerk
            else:
                messages.error(request, "No Clerk found to assign request.")
                return redirect('receipt_create')  # Redirect back to form
            
            # Set workflow details
            land_request.due_on = land_request.created_at + timedelta(days=30)
            land_request.comp_no = land_request.receipt_number or f"LR-{land_request.pk}"
            land_request.save()  # Save now to generate primary key
            
            # Generate and attach receipt PDF
            pdf_content = generate_receipt_pdf(land_request)
            if pdf_content:
                filename = f"receipt_{land_request.pk}.pdf"
                land_request.receipt.save(filename, ContentFile(pdf_content))
                land_request.save()
                
                
                # Save the PDF temporarily on disk for uploading to Pinata
                temp_pdf_path = os.path.join(settings.MEDIA_ROOT, f"receipt_{land_request.pk}.pdf")
                with open(temp_pdf_path, 'wb') as temp_pdf_file:
                    temp_pdf_file.write(pdf_content)

                try:
                    # Upload to Pinata IPFS and get hash
                    ipfs_hash = upload_file_to_pinata(temp_pdf_path, file_name=filename)
                    print("✅ Uploaded to IPFS. Hash:", ipfs_hash)

                    # Save IPFS hash in model
                    land_request.ipfs_hash = ipfs_hash
                    land_request.save()

                except Exception as e:
                    print(f"❌ Pinata upload failed: {e}")
            
            # **Create Workflow History Entry**
            LandRequestHistory.objects.create(
                land_request=land_request,
                from_user=request.user,
                to_user=clerk,
                action="submitted",
                remarks="Request submitted and forwarded to Clerk."
            )

            messages.success(request, "Request successfully created and sent to the Clerk.")
            return redirect('receipt', pk=land_request.pk)

    else:
        form = LandRequestForm()
    
    return render(request, 'receipt_create.html', {'form': form})

def receipt(request, pk):
    """
    Render the receipt view for a specific LandRequest.
    """
    land_request = get_object_or_404(LandRequest, pk=pk)
    return render(request, 'receipt.html', {'land_request': land_request})

def submit_receipt_to_official(request, pk):
    """
    Generic view to forward the LandRequest to an official based on role.
    For example, to send to a Clerk or Superintendent without duplicating code.
    """
    land_request = get_object_or_404(LandRequest, pk=pk)
    role = request.POST.get('role')
    official = get_official_by_role(role)
    if official:
        land_request.currently_with = official
        # Update status based on role (customize as needed)
        if role.lower() == 'clerk':
            land_request.status = 'clerk_review'
        elif role.lower() == 'superintendent':
            land_request.status = 'superintendent_review'
        else:
            land_request.status = 'submitted'
        land_request.save()
    return redirect('receipt_sent')

@login_required
def receipt_inbox(request):
    """
    Inbox for officials: show all requests that the user has interacted with (sent or received).
    """
    messages_list = LandRequest.objects.filter(
        history__from_user=request.user  # ✅ User sent it
    ) | LandRequest.objects.filter(
        history__to_user=request.user  # ✅ User received it
    )

    messages_list = messages_list.distinct()  # ✅ Remove duplicates

    return render(request, "inbox.html", {"messages_list": messages_list})

@login_required
def receipt_sent(request):
    """
    Display all LandRequests that are currently with the logged-in official.
    This view is generic and will show requests assigned to any official.
    """
    receipts = LandRequest.objects.all()
    return render(request, 'receipt_sent.html', {'receipts': receipts})









###########################################################################################################3
#############################################################################################################





# officials
def official_login(request):
    print("DEBUG: Entered official_login view")
    if request.method == "POST":
        print("DEBUG: Received POST request for official login")
        official_id = request.POST.get('officialId')
        role = request.POST.get('role')
        
        password = request.POST.get('password')
        print("DEBUG: Official ID:", official_id)
        print("DEBUG: Role:", role)
        print("DEBUG: Password received")

        # Attempt to retrieve the official user
        try:
            user = CustomUser.objects.get(office_id=official_id, user_type='official')
            print("DEBUG: Found user with username:", user.username)
        except CustomUser.DoesNotExist:
            print("DEBUG: No official user found with office_id:", official_id)
            messages.error(request, "Official user not found.")
            return redirect('home')

        # Check if the provided role matches the user's designation
        if user.designation.lower() != role.lower():
            print("DEBUG: Role mismatch. User designation:", user.designation, "provided role:", role)
            messages.error(request, "Role does not match our records.")
            return redirect('home')

        # Authenticate the user using the username and provided password.
        user_auth = authenticate(request, username=user.username, password=password)
        if user_auth is not None:


            print("DEBUG: Authentication successful for user:", user.username)
            login(request, user_auth)
            messages.success(request, "Official login successful.")
            return redirect('official_dashboard')  # Adjust to your desired official dashboard URL
        else:
            print("DEBUG: Authentication failed for user:", user.username)
            messages.error(request, "Invalid password.")
            return redirect('officiallogin')
    print("DEBUG: Rendering official login page (GET request)")
    return render(request, 'index.html')

# @login_required
# def official_dashboard_redirect(request):
#     role = request.user.designation.lower()

#     if role in DASHBOARD_URLS:
#         return redirect(DASHBOARD_URLS[role])
#     else:
#         messages.error(request, "Your role does not have a dashboard assigned.")
#         return redirect('home')
    
@login_required
def official_dashboard(request):
    """
    Dashboard for Clerk: show requests assigned to the logged-in clerk.
    """
    receipts = LandRequest.objects.filter(currently_with=request.user)
    context = {
        'user': request.user,
        'receipts': receipts,
    }
    return render(request, 'official_home.html', context)

def official_eLand(request):
    context = {
        'user' : request.user,
    }
    return render(request, "official_eLand.html", context)

@require_GET
def get_file_details(request, file_id):
    land_request = get_object_or_404(LandRequest, pk=file_id)
    data = {
        "survey_number": land_request.survey_number,
        "area": land_request.area,
        "address":land_request.address
    }
    return JsonResponse(data)

@login_required
def official_receipt_inbox(request):
    """
    Inbox for officials: show all requests that the user has interacted with (sent or received).
    """
    messages_list = LandRequest.objects.filter(
        history__from_user=request.user  # ✅ User sent it
    ) | LandRequest.objects.filter(
        history__to_user=request.user  # ✅ User received it
    )

    messages_list = messages_list.distinct()  # ✅ Remove duplicates

    return render(request, "official_receipt_inbox.html", {"messages_list": messages_list})

@login_required
def official_receipt_sent(request):
    """
    Show all requests that have been forwarded by the logged-in user.
    """
    role = request.user.designation
    nextofficialrole = get_next_official(role)
    nextofficial = get_official_by_role(nextofficialrole)  # Get the next official user
    
    # ✅ Correct query using the `history` related name
    receipts = LandRequest.objects.filter(
        history__from_user=request.user,  # Ensure logged-in user sent it
        history__to_user=nextofficial,  # Ensure it was sent to next official
        history__action="forwarded"  # Only show forwarded requests
    ).distinct()

    return render(request, "official_receipt_sent.html", {"receipts": receipts})



def generate_patta_pdf(land_request):
    # Build a flat context matching the template variable names
    certificate_number = getattr(land_request, 'receipt_number', None) or f"PATTA-{land_request.pk}"
    full_name = getattr(land_request, 'full_name', '')
    father_name = getattr(land_request, 'owner_name', '')
    aadhaar = getattr(land_request, 'aadhar_number', '')
    mobile = getattr(land_request, 'phone_number', '')
    district = getattr(land_request, 'state', '')
    mandal = getattr(land_request, 'city', '')
    village = getattr(land_request, 'address', '')
    survey_number = getattr(land_request, 'survey_number', '')
    patta_number = certificate_number
    land_area = getattr(land_request, 'area', '')
    # land_type is not a field on the model; fallback to nature
    land_type = getattr(land_request, 'land_type', None) or getattr(land_request, 'nature', '')
    issued_date = now().strftime('%d-%m-%Y')

    # Prepare QR payload
    qr_payload = {
        'certificate_number': certificate_number,
        'full_name': full_name,
        'father_name': father_name,
        'aadhaar': aadhaar,
        'mobile': mobile,
        'district': district,
        'mandal': mandal,
        'village': village,
        'survey_number': survey_number,
        'patta_number': patta_number,
        'land_area': land_area,
        'land_type': land_type,
        'issued_date': issued_date,
    }

    qr_code_data_url = ''
    if qrcode is not None:
        try:
            qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=4, border=2)
            qr.add_data(json.dumps(qr_payload, ensure_ascii=False))
            qr.make(fit=True)
            img = qr.make_image(fill_color='black', back_color='white')
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)
            qr_code_data_url = 'data:image/png;base64,' + base64.b64encode(buffer.read()).decode()
        except Exception:
            qr_code_data_url = ''

    context = {
        'certificate_number': certificate_number,
        'full_name': full_name,
        'father_name': father_name,
        'aadhaar': aadhaar,
        'mobile': mobile,
        'district': district,
        'mandal': mandal,
        'village': village,
        'survey_number': survey_number,
        'patta_number': patta_number,
        'land_area': land_area,
        'land_type': land_type,
        'issued_date': issued_date,
        'qr_code_data_url': qr_code_data_url,
    }

    html_string = render_to_string('patta_pdf.html', context)
    pdf_file = BytesIO()
    HTML(string=html_string).write_pdf(target=pdf_file)
    return pdf_file.getvalue()

    

@login_required
def handle_file_action(request):
    """
    Generic function for handling file actions (forward or reject) for all officers.
    """
    role = request.user.designation
    if request.method == "POST":
        file_id = request.POST.get("fileNo")
        action = request.POST.get("action")
        remarks = request.POST.get("remarks", "")
        
        print(role)

        # Ensure the file is assigned to the current user and is not rejected
        land_request = get_object_or_404(
            LandRequest.objects.exclude(status="rejected"),
            pk=file_id,
            currently_with=request.user
        )

        if action == "accept":
            next_official_role = get_next_official(role)

            if next_official_role:
                next_official = get_official_by_role(next_official_role)

                if next_official:
                    # Forward to next role
                    land_request.currently_with = next_official
                    land_request.status = f"{next_official_role}_review"
                    land_request.save()

                    LandRequestHistory.objects.create(
                        land_request=land_request,
                        from_user=request.user,
                        to_user=next_official,
                        action="forwarded",
                        remarks=remarks
                    )

                    messages.success(request, f"File forwarded to {next_official_role}.", extra_tags="success")
                else:
                    # Role exists in flow, but no user assigned — invalid setup
                    messages.error(
                        request,
                        f"No active user found for role: {next_official_role}. Please contact admin.",
                        extra_tags="danger"
                    )
            else:
                # No next role — you're the final approver
                land_request.status = "approved"
                land_request.currently_with = None
                land_request.save()

                LandRequestHistory.objects.create(
                    land_request=land_request,
                    from_user=request.user,
                    to_user=None,
                    action="approved",
                    remarks=remarks
                )

                # ✅ Add this step: generate and attach patta PDF
                pdf_bytes = generate_patta_pdf(land_request)
                if pdf_bytes:
                    filename = f"patta_{land_request.pk}.pdf"
                    land_request.patta.save(filename, ContentFile(pdf_bytes))
                    land_request.save()


                messages.success(request, "File has been approved and marked complete.", extra_tags="success")


        elif action == "reject":
            land_request.status = "rejected"
            land_request.save()

            # Notify all past handlers
            previous_users = LandRequestHistory.objects.filter(
                land_request=land_request
            ).values_list("from_user", flat=True).distinct()

            for user_id in previous_users:
                if user_id:
                    LandRequestHistory.objects.create(
                        land_request=land_request,
                        from_user=request.user,
                        to_user_id=user_id,
                        action="rejected",
                        remarks=remarks
                    )

            messages.success(request, "File has been rejected, and all predecessors have been notified.", extra_tags="danger")

        else:
            messages.error(request, "Invalid action.", extra_tags="danger")

        return redirect("official_eLand")

    else:
        file_numbers = LandRequest.objects.filter(currently_with=request.user)\
                    .exclude(file_no__isnull=True)\
                    .exclude(file_no__exact="")\
                    .exclude(status="rejected")\
                    .distinct()

    return render(request, "official_file_create.html", {"file_numbers": file_numbers, "role": role})

def forgot_password(request):
    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            try:
                user = User.objects.get(username=username)
                send_otp(user)  # sending OTP via existing function
                messages.success(request, 'OTP sent successfully!')
                return redirect(reverse('resetPassword', args=[username]))
            except User.DoesNotExist:
                messages.error(request, 'Username does not exist.')
    else:
        form = ForgotPasswordForm()
    return render(request, 'forgot_password.html', {'form': form})

def reset_password(request, username):
    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            otp = form.cleaned_data['otp']
            new_password = form.cleaned_data['new_password']
            confirm_password = form.cleaned_data['confirm_password']

            if new_password != confirm_password:
                messages.error(request, 'Passwords do not match.')
            elif verify_otp_pass(username, otp):  # existing OTP verification
                user = User.objects.get(username=username)
                user.set_password(new_password)
                user.save()
                messages.success(request, 'Password reset successfully.')
                return redirect('userlogin')
            else:
                messages.error(request, 'Invalid OTP.')
    else:
        form = ResetPasswordForm()
    return render(request, 'reset_password.html', {'form': form, 'username': username})



