from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Profile

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    pass

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'follower_count', 'following_count', 'created_at')
    search_fields = ('user__username', 'bio')
