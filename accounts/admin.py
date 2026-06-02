from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import CustomUser, CodeVerify


class CodeVerifyInline(admin.TabularInline):
    model = CodeVerify
    extra = 0
    readonly_fields = ['code', 'verify_type', 'is_used', 'expiration_time', 'created_at']
    can_delete = False


@admin.register(CustomUser)
class CustomUserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'phone_number', 'user_role', 'auth_type', 'auth_status', 'is_staff', 'is_active']
    list_filter = ['user_role', 'auth_type', 'auth_status', 'is_active', 'is_staff']
    search_fields = ['username', 'email', 'phone_number']
    ordering = ['-date_joined']
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Shaxsiy ma’lumotlar', {'fields': ('first_name', 'last_name', 'email', 'phone_number', 'photo')}),
        ('Ruxsatlar', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Muhim sanalar', {'fields': ('last_login', 'date_joined')}),
        ('Maxsus maydonlar', {'fields': ('user_role', 'auth_type', 'auth_status')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'phone_number', 'password1', 'password2', 'user_role', 'auth_type', 'auth_status'),
        }),
    )
    
    inlines = [CodeVerifyInline]


@admin.register(CodeVerify)
class CodeVerifyAdmin(admin.ModelAdmin):
    list_display = ['user', 'code', 'verify_type', 'is_used', 'expiration_time', 'created_at']
    list_filter = ['verify_type', 'is_used']
    search_fields = ['user__username', 'user__email', 'code']
    readonly_fields = ['code', 'verify_type', 'is_used', 'expiration_time']