from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
from .constants import ROLE_CHOICES,DESIGNATIONS

class IndividualUserCreationForm(UserCreationForm):
    dob = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    class Meta:
        model = CustomUser
        fields = (
            'username',
            'first_name',
            'middle_name',
            'last_name',
            'email',
            'phone',
            'dob',
            'gender', 
            'aadhar',
            'address',
            'password1',
            'password2',

        )

# # Define choices matching the options in your HTML
# DESIGNATION_CHOICES = (
#     ('ministry_welfare', 'Ministry of Welfare'),
#     ('district_collector', 'District Collector'),
#     ('joint_collector', 'Joint Collector'),
#     ('revenue_dept_officer', 'Revenue Department Officer'),
#     ('project_officer', 'Project Officer'),
#     ('mro', 'MRO (Mandal Revenue Officer)'),
#     ('surveyor', 'Surveyor'),
#     ('revenue_inspector', 'Revenue Inspector'),
#     ('vro', 'VRO (Village Revenue Officer)'),
#     ('superitendent', 'superitendent'),
#     ('clerk', 'Clerk'),
# )

DEPARTMENT_CHOICES = (
    ('revenue', 'Revenue Department'),
    ('welfare', 'Welfare Department'),
    ('survey', 'Survey Department'),
    ('collector_office', 'Collector Office'),
    ('mandal_office', 'Mandal Office'),
    ('village_office', 'Village Office'),
)

class OfficialUserRegistrationForm(UserCreationForm):
    # These fields are rendered from the model
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    designation = forms.ChoiceField(choices=ROLE_CHOICES, label="Select Role")
    department = forms.ChoiceField(choices=DEPARTMENT_CHOICES, required=True)
    email = forms.EmailField(required=True)
    phone = forms.CharField(required=True, max_length=10)
    office_id = forms.CharField(required=True, label="Office ID")
    
    # Extra fields that are not stored in the user model
    # otp = forms.CharField(max_length=6, required=True, label="Enter OTP")
    terms = forms.BooleanField(required=True, label="I agree to the Terms and Conditions and Privacy Policy")
    
    class Meta:
        model = CustomUser
        fields = (
            'first_name',
            'last_name',
            'designation',
            'department',
            'email',
            'phone',
            'office_id',
            'username',
            'password1',
            'password2',
        )



from django import forms
from .models import LandRequest

class LandRequestForm(forms.ModelForm):
    class Meta:
        model = LandRequest
        fields = [
            'nature', 'full_name', 'email', 'phone_number', 'aadhar_number', 'dob',
            'owner_name', 'survey_number', 'area', 'address', 'state', 'city', 'pincode', 'document'
        ]



class ForgotPasswordForm(forms.Form):
    username = forms.CharField(max_length=150, required=True)

class ResetPasswordForm(forms.Form):
    otp = forms.CharField(max_length=6, required=True)
    new_password = forms.CharField(widget=forms.PasswordInput, required=True)
    confirm_password = forms.CharField(widget=forms.PasswordInput, required=True)