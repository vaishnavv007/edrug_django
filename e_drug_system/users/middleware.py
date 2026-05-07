from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages


class RoleMiddleware:
    """
    Middleware to handle role-based access control.
    This middleware can be used to enforce role-based restrictions globally.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Add role information to request object for easy access
        if request.user.is_authenticated:
            request.user_role = request.user.role
            request.is_admin = request.user.is_admin
            request.is_moderator = request.user.is_moderator
            request.is_expert = request.user.is_expert
            request.is_high_risk = request.user.is_high_risk
        else:
            request.user_role = 'anonymous'
            request.is_admin = False
            request.is_moderator = False
            request.is_expert = False
            request.is_high_risk = False

        response = self.get_response(request)
        return response


class HighRiskRestrictionMiddleware:
    """
    Middleware to restrict high-risk users from accessing certain features.
    """
    
    # Paths that high-risk users should be restricted from
    RESTRICTED_PATHS = [
        '/ai/chatbot/',
        '/accounts/profile/edit/',
    ]

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and request.user.is_high_risk:
            if any(request.path.startswith(path) for path in self.RESTRICTED_PATHS):
                messages.warning(
                    request,
                    'Your account has been flagged as high-risk. Some features are restricted.'
                )
                return redirect(reverse('dashboard'))
        
        response = self.get_response(request)
        return response
