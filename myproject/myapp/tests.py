# myapp/tests/test_views.py

from django.test import TestCase, RequestFactory
from django.contrib.sessions.middleware import SessionMiddleware
from django.urls import reverse
from myapp.views import verify_otp
from myapp.models import CustomUser

class OTPVerificationTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        # A dummy function required by SessionMiddleware
        self.middleware = SessionMiddleware(lambda req: None)
        self.dummy_registration_data = {
            'username': 'testuser',
            'first_name': 'Test',
            'middle_name': '',
            'last_name': 'User',
            'email': 'test@example.com',
            'phone': '1234567890',
            'dob': '1990-01-01',
            'gender': 'male',
            'aadhar': '123412341234',
            'address': '123 Test Street',
            'password1': 'testpassword',
        }
        self.otp = '123456'

    def attach_session(self, request):
        """Helper function to attach a session to a request."""
        self.middleware.process_request(request)
        request.session.save()
        return request

    def test_verify_otp_success(self):
        """Test that a valid OTP leads to successful user creation and redirect."""
        # Create a POST request with the correct OTP
        url = reverse('verify_otp')
        request = self.factory.post(url, {'otp': self.otp})
        self.attach_session(request)
        request.session['registration_data'] = self.dummy_registration_data
        request.session['registration_otp'] = self.otp
        request.session.save()

        response = verify_otp(request)
        
        # Expect a redirect (status code 302)
        self.assertEqual(response.status_code, 302)
        # Verify that it redirects to 'home' (adjust as needed)
        self.assertEqual(response.url, reverse('home'))

        # Verify that the user was created in the database
        self.assertTrue(CustomUser.objects.filter(username='testuser').exists())

    def test_verify_otp_failure(self):
        """Test that an incorrect OTP returns an error message."""
        # Create a POST request with an incorrect OTP
        url = reverse('verify_otp')
        request = self.factory.post(url, {'otp': '000000'})
        self.attach_session(request)
        request.session['registration_data'] = self.dummy_registration_data
        request.session['registration_otp'] = self.otp
        request.session.save()

        response = verify_otp(request)
        # Expect the page to render again with status 200 (no redirect)
        self.assertEqual(response.status_code, 200)
        # Verify that the error message is included in the response
        self.assertIn(b"Invalid OTP", response.content)
