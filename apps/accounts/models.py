from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
import os


def user_profile_image_path(instance, filename):
    """Generate file path for user profile images"""
    ext = filename.split('.')[-1]
    filename = f"user_{instance.user.id}_profile.{ext}"
    return os.path.join('profiles', filename)


class User(AbstractUser):
    """Custom user model with email as username field"""
    
    USER_TYPE_CHOICES = [
        ('student', _('Student')),
        ('judge', _('Judge')),
        ('admin', _('Admin')),
    ]
    
    email = models.EmailField(_('email address'), unique=True)
    user_type = models.CharField(
        max_length=10,
        choices=USER_TYPE_CHOICES,
        default='student',
        help_text=_('Select your role in the platform')
    )
    is_verified = models.BooleanField(
        default=False,
        help_text=_('Email verification status')
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        db_table = 'accounts_user'
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ['-created_at']
    
    def __str__(self):
        return self.email
    
    @property
    def is_student(self):
        return self.user_type == 'student'
    
    @property
    def is_judge(self):
        return self.user_type == 'judge'
    
    def get_absolute_url(self):
        return reverse('accounts:profile')


class UserProfile(models.Model):
    """Extended user profile information"""
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    first_name = models.CharField(
        max_length=100, 
        blank=True,
        help_text=_('Your first name')
    )
    last_name = models.CharField(
        max_length=100, 
        blank=True,
        help_text=_('Your last name')
    )
    bio = models.TextField(
        blank=True,
        max_length=500,
        help_text=_('Tell us about yourself (max 500 characters)')
    )
    profile_image = models.ImageField(
        upload_to=user_profile_image_path,
        blank=True,
        null=True,
        help_text=_('Upload a profile picture')
    )
    phone_number = models.CharField(
        max_length=20, 
        blank=True,
        help_text=_('Your contact phone number')
    )
    date_of_birth = models.DateField(
        blank=True, 
        null=True,
        help_text=_('Your date of birth')
    )
    
    # Student-specific fields
    school_organization = models.CharField(
        max_length=200,
        blank=True,
        help_text=_('School or organization name')
    )
    grade_level = models.CharField(
        max_length=50,
        blank=True,
        help_text=_('Grade level or year')
    )
    
    # Judge-specific fields
    expertise_area = models.CharField(
        max_length=200,
        blank=True,
        help_text=_('Area of expertise for judges')
    )
    years_experience = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text=_('Years of relevant experience')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'accounts_userprofile'
        verbose_name = _('User Profile')
        verbose_name_plural = _('User Profiles')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email}'s profile"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    @property
    def display_name(self):
        return self.full_name or self.user.username or self.user.email
    
    @property
    def profile_completion_percentage(self):
        """Calculate profile completion percentage"""
        fields = ['first_name', 'last_name', 'bio', 'phone_number']
        if self.user.is_student:
            fields.extend(['school_organization', 'grade_level'])
        elif self.user.is_judge:
            fields.extend(['expertise_area', 'years_experience'])
        
        completed = sum(1 for field in fields if getattr(self, field))
        if self.profile_image:
            completed += 1
            fields.append('profile_image')
        
        return int((completed / len(fields)) * 100)


# Signal to create profile when user is created
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a UserProfile when a User is created"""
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save the UserProfile when the User is saved"""
    if hasattr(instance, 'profile'):
        instance.profile.save()
    else:
        UserProfile.objects.create(user=instance)
