import random
import string
from .constants import ROLE_HIERARCHY
def generate_otp(length=6):
    return ''.join(random.choices(string.digits, k=length))



import random
from django.core.cache import cache
from django.core.mail import send_mail

def send_otp(user):
    otp = random.randint(100000, 999999)
    cache.set(user.username, otp, 300)  # OTP valid for 5 minutes
    send_mail(
        'Your OTP Code',
        f'Your OTP is: {otp}',
        'your_email@example.com',
        [user.email],
        fail_silently=False,
    )

def verify_otp_pass(username, otp):
    stored_otp = cache.get(username)
    return stored_otp and str(stored_otp) == otp



def get_next_official(current_role):
    """
    Determines the next official in the hierarchy.
    """
    return ROLE_HIERARCHY.get(current_role, None)  # Returns None if no next role
