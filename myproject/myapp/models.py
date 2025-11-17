from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid
from django.contrib.auth import get_user_model
from django.conf import settings

from .constants import NATURE_CHOICES, STATUS_CHOICES


class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('individual', 'Individual'),
        ('official', 'Official'),
    )
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='individual')
    
    # Fields for individual users
    middle_name = models.CharField(max_length=150, blank=True)
    dob = models.DateField(null=True, blank=True)
    GENDER_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other'),
    )
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True)
    phone = models.CharField(max_length=15, blank=True)
    aadhar = models.CharField(max_length=12, unique=True, null=True, blank=True)
    address = models.TextField(blank=True)
    
    # Extra fields for official users
    designation = models.CharField(max_length=50, blank=True, null=True)
    department = models.CharField(max_length=50, blank=True, null=True)
    office_id = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.username} - {self.office_id}"
    


def generate_application_id():
    return uuid.uuid4().hex[:8].upper()

def generate_transfer_id():
    return uuid.uuid4().hex[:8].upper()



User = get_user_model()

class LandRequest(models.Model):
    
    
    txn_id = models.CharField(max_length=100, blank=True, null=True)
    print(txn_id)
    # Nature Details
    nature = models.CharField(max_length=10, choices=NATURE_CHOICES, default='electronic')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="created_requests")

    # Personal Details
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    aadhar_number = models.CharField(max_length=20)
    dob = models.DateField()

    # Land Registration Details
    owner_name = models.CharField(max_length=200)
    survey_number = models.CharField(max_length=100)
    area = models.CharField(max_length=50)
    address = models.CharField(max_length=300)
    state = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)

    # Document Uploads
    document = models.FileField(upload_to='documents/', blank=True, null=True)
    receipt = models.FileField(upload_to='receipts/', blank=True, null=True)
    patta = models.FileField(upload_to='pattas/', blank=True, null=True)
    ipfs_hash = models.CharField(max_length=255, blank=True, null=True)
    print(ipfs_hash)
    # Unique random receipt number for searching
    receipt_number = models.CharField(max_length=20, unique=True, blank=True, null=True)

    # Workflow status and assignment
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='submitted')
    currently_with = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='current_requests')

    created_at = models.DateTimeField(auto_now_add=True)

    comp_no = models.CharField(max_length=50, blank=True, null=True)
    file_no = models.CharField(max_length=50, blank=True, null=True)
    subject = models.CharField(max_length=200, blank=True, null=True)
    sent_to = models.CharField(max_length=200, blank=True, null=True)
    # who the request is forwarded to can be maintained in currently_with field
    due_on = models.DateField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.receipt_number:
            # Generate a random receipt number (e.g. first 10 characters of a UUID, uppercase)
            self.receipt_number = uuid.uuid4().hex[:10].upper()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.full_name} - {self.survey_number}"


class LandRequestHistory(models.Model):
    land_request = models.ForeignKey(LandRequest, on_delete=models.CASCADE, related_name='history')
    timestamp = models.DateTimeField(auto_now_add=True)
    from_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='sent_requests')
    to_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='received_requests')
    action = models.CharField(max_length=50)  # e.g., 'forwarded', 'rejected'
    remarks = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.land_request} - {self.action} by {self.from_user} to {self.to_user}"

