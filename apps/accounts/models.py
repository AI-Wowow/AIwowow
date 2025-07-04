from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
import os
import uuid
from datetime import timedelta


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
    is_approved = models.BooleanField(
        default=True,
        help_text=_('Admin approval status (judges require approval)')
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
    
    @property
    def can_access_platform(self):
        """Check if user can access platform features"""
        return self.is_verified and self.is_approved
    
    def get_absolute_url(self):
        return reverse('accounts:profile')
    
    def generate_verification_token(self):
        """Generate email verification token"""
        return default_token_generator.make_token(self)
    
    def get_verification_link(self, request):
        """Generate email verification link"""
        from django.utils.encoding import force_bytes
        from django.utils.http import urlsafe_base64_encode
        
        uid = urlsafe_base64_encode(force_bytes(self.pk))
        token = self.generate_verification_token()
        
        return request.build_absolute_uri(
            reverse('accounts:verify_email', kwargs={'uidb64': uid, 'token': token})
        )


class EmailVerification(models.Model):
    """Track email verification attempts"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    email = models.EmailField()
    token = models.CharField(max_length=100, unique=True, default=uuid.uuid4)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'accounts_emailverification'
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=24)
        super().save(*args, **kwargs)
    
    @property
    def is_expired(self):
        return timezone.now() > self.expires_at
    
    @property
    def is_valid(self):
        return not self.is_used and not self.is_expired


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
        
        # Set judge approval status
        if instance.user_type == 'judge':
            instance.is_approved = False
            instance.save()

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save the UserProfile when the User is saved"""
    if hasattr(instance, 'profile'):
        instance.profile.save()
    else:
        UserProfile.objects.create(user=instance)



