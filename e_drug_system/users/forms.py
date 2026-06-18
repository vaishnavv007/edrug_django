from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    REGISTRATION_ROLE_CHOICES = [
        ('user', 'User'),
        ('expert', 'Expert'),
        ('moderator', 'Moderator'),
        ('admin', 'Admin'),
    ]
    
    role = forms.ChoiceField(choices=REGISTRATION_ROLE_CHOICES, required=True, label='Select Role')
    is_verified_expert = forms.BooleanField(required=False, label='Verified Expert')

    class Meta:
        model = User
        fields = ('username', 'email', 'role', 'is_verified_expert', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.role = self.cleaned_data['role']
        
        # Auto-approve User role, others require approval
        if user.role == 'user':
            user.is_approved = True
        else:
            user.is_approved = False
        
        # Auto-verify expert role
        if user.role == 'expert':
            user.is_verified_expert = True
        else:
            user.is_verified_expert = False
            
        if commit:
            user.save()
        return user


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'role', 'phone', 'date_of_birth', 'bio', 'profile_picture')


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone', 'date_of_birth', 'bio', 'profile_picture')
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'bio': forms.Textarea(attrs={'rows': 4}),
        }


class AdminUserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)
    
    # Only allow admin, moderator, expert roles (not user or anonymous)
    ADMIN_ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('moderator', 'Moderator'),
        ('expert', 'Expert'),
    ]
    
    role = forms.ChoiceField(choices=ADMIN_ROLE_CHOICES, required=True)
    is_verified_expert = forms.BooleanField(required=False, label='Verify Expert (only for Expert role)')
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'role', 'phone', 'is_verified_expert')
    
    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2
    
    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        is_verified_expert = cleaned_data.get('is_verified_expert')
        
        if role != 'expert' and is_verified_expert:
            raise forms.ValidationError("is_verified_expert can only be set for Expert role")
        
        return cleaned_data
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user
