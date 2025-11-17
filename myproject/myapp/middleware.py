# myapp/middleware.py
from django.conf import settings

class DisableXFrameOptionsForMediaMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        # Check if the request is for media files
        if request.path.startswith(settings.MEDIA_URL):
            if 'X-Frame-Options' in response:
                del response['X-Frame-Options']
        #Optionally, if you need to remove it for the entire site (development only), uncomment:
        if settings.DEBUG:
            if 'X-Frame-Options' in response:
                del response['X-Frame-Options']
        return response
