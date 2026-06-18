from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy
from django.contrib import messages
from .forms import CustomUserCreationForm, UserProfileForm
from .models import User


class CustomLoginView(LoginView):
    form_class = AuthenticationForm
    template_name = 'users/login.html'
    redirect_authenticated_user = True

    def form_valid(self, form):
        user = form.get_user()
        
        # Check if user is approved
        if not user.is_approved:
            messages.error(self.request, 'Your account is awaiting administrator approval.')
            return redirect('login')
        
        return super().form_valid(form)

    def get_success_url(self):
        if self.request.user.is_superuser:
            return '/admin/'
        return super().get_success_url()


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('home')


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Only auto-login if user role (already approved)
            if user.role == 'user':
                login(request, user)
                messages.success(request, 'Registration successful! Welcome to E-Drug System.')
                return redirect('dashboard')
            else:
                # For Expert, Moderator, Admin roles - pending approval
                messages.info(request, f'Your account has been created with role "{user.get_role_display()}" and is awaiting administrator approval. You will be able to login once approved.')
                return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})


@login_required
def profile(request):
    return render(request, 'users/profile.html', {'user': request.user})


@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, 'users/edit_profile.html', {'form': form})
