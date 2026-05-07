from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'role', 'is_verified_expert', 'is_active', 'created_at']
    list_filter = ['role', 'is_verified_expert', 'is_active', 'created_at']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['-created_at']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('role', 'phone', 'date_of_birth', 'bio', 'profile_picture', 'is_verified_expert')}),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('email', 'role', 'phone', 'date_of_birth')}),
    )


admin.site.register(User, UserAdmin)
