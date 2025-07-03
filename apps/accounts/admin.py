from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from django.utils.html import format_html
from .models import User, UserProfile


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
        'email', 'username', 'user_type', 'is_verified', 
        'is_active', 'profile_completion', 'date_joined'
    )
    list_filter = (
        'user_type', 'is_verified', 'is_active', 'is_staff', 'date_joined'
    )
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    
    fieldsets = DefaultUserAdmin.fieldsets + (
        ('Custom Fields', {
            'fields': ('user_type', 'is_verified'),
        }),
    )
    
    add_fieldsets = DefaultUserAdmin.add_fieldsets + (
        ('Custom Fields', {
            'fields': ('email', 'user_type'),
        }),
    )
    
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


# Customize admin site headers
admin.site.site_header = "Video Platform Admin"
admin.site.site_title = "Video Platform Admin Portal"
admin.site.index_title = "Welcome to Video Platform Administration"
