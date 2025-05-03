from django.shortcuts import redirect
from django.conf import settings
from django.urls import reverse

class AuthRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # List of URL paths that require authentication
        protected_paths = ['/accounts/dashboard/']
        
        # Check if the current path requires authentication
        if any(request.path.startswith(path) for path in protected_paths):
            # If user is not authenticated, redirect to login
            if not request.user.is_authenticated:
                return redirect(settings.LOGIN_URL)
        
        response = self.get_response(request)
        return response