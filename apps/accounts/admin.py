from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from django.utils.html import format_html
from django.utils import timezone
from django.urls import reverse
from django.shortcuts import redirect
from django.contrib import messages
from .models import User, UserProfile, EmailVerification
from .utils import send_verification_email, send_judge_approval_notification


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile Information'
    fields = (
        'first_name', 'last_name', 'bio', 'profile_image',
        'phone_number', 'date_of_birth', 'school_organization',
        'grade_level', 'expertise_area', 'years_experience'
    )


@admin.register(User)
class UserAdmin(DefaultUserAdmin):
    inlines = (UserProfileInline,)
    list_display = (
        'email', 'username', 'user_type', 'verification_status', 
        'approval_status', 'is_active', 'profile_completion', 'date_joined'
    )
    list_filter = (
        'user_type', 'is_verified', 'is_approved', 'is_active', 'is_staff', 'date_joined'
    )
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    actions = ['approve_judges', 'send_verification_emails', 'deactivate_users', 'reactivate_users']
    
    fieldsets = DefaultUserAdmin.fieldsets + (
        ('Custom Fields', {
            'fields': ('user_type', 'is_verified', 'is_approved'),
        }),
        ('Important Dates', {
            'fields': ('created_at', 'updated_at'),
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    add_fieldsets = DefaultUserAdmin.add_fieldsets + (
        ('Custom Fields', {
            'fields': ('email', 'user_type'),
        }),
    )
    
    def verification_status(self, obj):
        """Display verification status with color coding"""
        if getattr(obj, 'is_verified', True):
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ Verified</span>'
            )
        else:
            return format_html(
                '<span style="color: red; font-weight: bold;">✗ Unverified</span>'
            )
    verification_status.short_description = 'Email Status'
    
    def approval_status(self, obj):
        """Display approval status for judges"""
        if obj.user_type != 'judge':
            return format_html('<span style="color: gray;">N/A</span>')
        
        if getattr(obj, 'is_approved', True):
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ Approved</span>'
            )
        else:
            return format_html(
                '<span style="color: orange; font-weight: bold;">⏳ Pending</span>'
            )
    approval_status.short_description = 'Judge Status'
    
    def profile_completion(self, obj):
        """Display profile completion percentage"""
        if hasattr(obj, 'profile'):
            completion = obj.profile.profile_completion_percentage
            color = 'green' if completion >= 80 else 'orange' if completion >= 50 else 'red'
            return format_html(
                '<span style="color: {};">{:.0f}%</span>',
                color, completion
            )
        return 'No Profile'
    profile_completion.short_description = 'Profile Complete'
    
    def approve_judges(self, request, queryset):
        """Bulk approve judges"""
        judge_users = queryset.filter(user_type='judge', is_approved=False)
        approved_count = 0
        
        for user in judge_users:
            user.is_approved = True
            user.save()
            
            # Send approval email
            if send_judge_approval_notification(user):
                approved_count += 1
        
        self.message_user(
            request,
            f'{approved_count} judges approved and notified.',
            messages.SUCCESS
        )
    approve_judges.short_description = "Approve selected judges"
    
    def send_verification_emails(self, request, queryset):
        """Resend verification emails"""
        unverified_users = queryset.filter(is_verified=False)
        sent_count = 0
        
        for user in unverified_users:
            if send_verification_email(user, request):
                sent_count += 1
        
        self.message_user(
            request,
            f'Verification emails sent to {sent_count} users.',
            messages.SUCCESS
        )
    send_verification_emails.short_description = "Send verification emails"
    
    def deactivate_users(self, request, queryset):
        """Deactivate selected users"""
        queryset.update(is_active=False)
        self.message_user(
            request,
            f'{queryset.count()} users deactivated.',
            messages.SUCCESS
        )
    deactivate_users.short_description = "Deactivate selected users"
    
    def reactivate_users(self, request, queryset):
        """Reactivate selected users"""
        queryset.update(is_active=True)
        self.message_user(
            request,
            f'{queryset.count()} users reactivated.',
            messages.SUCCESS
        )
    reactivate_users.short_description = "Reactivate selected users"


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'full_name', 'user_type', 'profile_completion_display',
        'created_at'
    )
    list_filter = ('user__user_type', 'created_at')
    search_fields = (
        'user__email', 'user__username', 'first_name', 
        'last_name', 'school_organization', 'expertise_area'
    )
    readonly_fields = ('created_at', 'updated_at', 'profile_completion_percentage')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'first_name', 'last_name', 'bio', 'profile_image')
        }),
        ('Contact Information', {
            'fields': ('phone_number', 'date_of_birth')
        }),
        ('Student Information', {
            'fields': ('school_organization', 'grade_level'),
            'classes': ('collapse',)
        }),
        ('Judge Information', {
            'fields': ('expertise_area', 'years_experience'),
            'classes': ('collapse',)
        }),
        ('System Information', {
            'fields': ('profile_completion_percentage', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def user_type(self, obj):
        return obj.user.get_user_type_display()
    user_type.short_description = 'User Type'
    
    def profile_completion_display(self, obj):
        completion = obj.profile_completion_percentage
        color = 'green' if completion >= 80 else 'orange' if completion >= 50 else 'red'
        return format_html(
            '<span style="color: {};">{:.0f}%</span>',
            color, completion
        )
    profile_completion_display.short_description = 'Completion'


@admin.register(EmailVerification)
class EmailVerificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'email', 'created_at', 'expires_at', 'is_used', 'status')
    list_filter = ('is_used', 'created_at', 'expires_at')
    search_fields = ('user__email', 'email')
    readonly_fields = ('token', 'created_at', 'status')
    
    def status(self, obj):
        if obj.is_used:
            return format_html('<span style="color: green;">✓ Used</span>')
        elif obj.is_expired:
            return format_html('<span style="color: red;">✗ Expired</span>')
        else:
            return format_html('<span style="color: orange;">⏳ Valid</span>')
    status.short_description = 'Status'





# Customize admin site headers
admin.site.site_header = "Video Platform Admin"
admin.site.site_title = "Video Platform Admin Portal"
admin.site.index_title = "Welcome to Video Platform Administration"

# Add admin settings for better email configuration
admin.site.site_url = "/"
