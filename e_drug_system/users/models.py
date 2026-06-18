from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = [
        ('anonymous', 'Anonymous'),
        ('user', 'User'),
        ('admin', 'Admin'),
        ('moderator', 'Moderator'),
        ('expert', 'Expert'),
    ]

    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    is_approved = models.BooleanField(default=True, help_text="Whether the account has been approved by an administrator")
    is_high_risk = models.BooleanField(default=False)
    phone = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    bio = models.TextField(blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True)
    is_verified_expert = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_moderator(self):
        return self.role in ['admin', 'moderator']

    @property
    def is_expert(self):
        return self.role == 'expert' and self.is_verified_expert

    @property
    def is_regular_user(self):
        return self.role == 'user'

    def has_role(self, *roles):
        return self.role in roles
