from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from functools import wraps


def role_required(*roles):
    """
    Decorator to require specific user roles.
    Usage: @role_required('admin', 'moderator')
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                from django.contrib.auth.views import redirect_to_login
                from django.urls import reverse
                return redirect_to_login(request.get_full_path(), reverse('login'))
            
            if not request.user.has_role(*roles):
                raise PermissionDenied("You don't have permission to access this page.")
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator


def admin_required(view_func):
    """Decorator to require admin role."""
    return role_required('admin')(view_func)


def moderator_required(view_func):
    """Decorator to require moderator or admin role."""
    return role_required('admin', 'moderator')(view_func)


def expert_required(view_func):
    """Decorator to require verified expert role."""
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            from django.contrib.auth.views import redirect_to_login
            from django.urls import reverse
            return redirect_to_login(request.get_full_path(), reverse('login'))
        
        if not request.user.is_expert:
            raise PermissionDenied("You must be a verified expert to access this page.")
        
        return view_func(request, *args, **kwargs)
    return wraps(view_func)(_wrapped_view)


def moderator_or_expert_required(view_func):
    """Decorator to require moderator or expert role."""
    return role_required('admin', 'moderator', 'expert')(view_func)


class RoleRequiredMixin(UserPassesTestMixin):
    """
    Mixin for class-based views to require specific roles.
    Usage: class MyView(RoleRequiredMixin, ...):
              required_roles = ['admin', 'moderator']
    """
    required_roles = None

    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        
        if self.required_roles is None:
            return True
        
        return self.request.user.has_role(*self.required_roles)

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            from django.contrib.auth.views import redirect_to_login
            from django.urls import reverse
            return redirect_to_login(self.request.get_full_path(), reverse('login'))
        
        raise PermissionDenied("You don't have permission to access this page.")


class AdminRequiredMixin(RoleRequiredMixin):
    """Mixin to require admin role."""
    required_roles = ['admin']


class ModeratorRequiredMixin(RoleRequiredMixin):
    """Mixin to require moderator or admin role."""
    required_roles = ['admin', 'moderator']


class ExpertRequiredMixin(UserPassesTestMixin):
    """Mixin to require verified expert role."""
    
    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_expert

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            from django.contrib.auth.views import redirect_to_login
            from django.urls import reverse
            return redirect_to_login(self.request.get_full_path(), reverse('login'))
        
        raise PermissionDenied("You must be a verified expert to access this page.")


def check_high_risk_user(user):
    """Check if user is marked as high risk."""
    return user.is_authenticated and user.is_high_risk


class HighRiskRequiredMixin(UserPassesTestMixin):
    """Mixin to restrict access for high-risk users."""
    
    def test_func(self):
        if not self.request.user.is_authenticated:
            return True  # Anonymous users are not restricted
        
        return not self.request.user.is_high_risk

    def handle_no_permission(self):
        from django.shortcuts import render
        return render(self.request, 'users/high_risk_restriction.html', status=403)
