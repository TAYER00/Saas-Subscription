from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Subscription, Notification

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'is_active', 'date_joined')
    list_filter = ('role', 'is_active')
    search_fields = ('username', 'email')
    ordering = ('-date_joined',)
    
    fieldsets = UserAdmin.fieldsets + (
        ('Informations supplémentaires', {'fields': ('role',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Informations supplémentaires', {'fields': ('role',)}),
    )

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active',)
    search_fields = ('user__username', 'user__email')
    ordering = ('-created_at',)

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'is_read', 'created_at')
    list_filter = ('is_read',)
    search_fields = ('user__username', 'title', 'message')
    ordering = ('-created_at',)
