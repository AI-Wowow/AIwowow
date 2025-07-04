from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, UserProfile


class CustomUserCreationForm(UserCreationForm):
    """Enhanced user registration form"""
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address'
        })
    )
    
    user_type = forms.ChoiceField(
        choices=User.USER_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = User
        fields = ('email', 'username', 'user_type', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Choose a username'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter your password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm your password'
        })
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class UserProfileForm(forms.ModelForm):
    """Form for editing user profile information"""
    
    class Meta:
        model = UserProfile
        fields = [
            'first_name', 'last_name', 'bio', 'profile_image',
            'phone_number', 'date_of_birth', 'school_organization',
            'grade_level', 'expertise_area', 'years_experience'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'First Name'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Last Name'
            }),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Tell us about yourself...',
                'maxlength': 500
            }),
            'profile_image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+1 (555) 123-4567'
            }),
            'date_of_birth': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'school_organization': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'School or Organization Name'
            }),
            'grade_level': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Grade Level or Year'
            }),
            'expertise_area': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Area of Expertise'
            }),
            'years_experience': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'max': 50
            }),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Hide fields based on user type
        if user:
            if user.is_student:
                self.fields.pop('expertise_area', None)
                self.fields.pop('years_experience', None)
            elif user.is_judge:
                self.fields.pop('school_organization', None)
                self.fields.pop('grade_level', None)
    
    def clean_profile_image(self):
        image = self.cleaned_data.get('profile_image')
        if image:
            # Check file size (max 5MB)
            if image.size > 5 * 1024 * 1024:
                raise forms.ValidationError('Image file too large ( > 5MB )')
            
            # Check file type
            if not image.content_type.startswith('image/'):
                raise forms.ValidationError('File is not an image')
        
        return image


class UserAccountForm(forms.ModelForm):
    """Form for editing basic user account information"""
    
    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Username'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email Address'
            }),
        }
    
    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('Email address already in use.')
        return email


class AccountDeactivationForm(forms.Form):
    """Form for account deactivation confirmation."""
    confirm = forms.BooleanField(
        label='I understand that my account will be permanently deleted.',
        required=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    )
    feedback = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Please provide any feedback before you go (optional).',
        }),
        label='Feedback (optional)',
        max_length=500,
    )
