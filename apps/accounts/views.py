from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login, logout
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.http import JsonResponse, HttpResponseRedirect
from django.views import View
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.core.exceptions import ValidationError
from .models import User, UserProfile, EmailVerification
from .forms import CustomUserCreationForm, UserProfileForm, UserAccountForm
from .utils import send_verification_email, send_welcome_email, send_judge_approval_notification, notify_admin_new_judge
import logging

logger = logging.getLogger(__name__)


class SignUpView(CreateView):
    model = User
    form_class = CustomUserCreationForm
    template_name = 'accounts/signup.html'
    success_url = reverse_lazy('accounts:verification_sent')
    
    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_verified = False  # Require email verification
        
        # Judges require approval
        if user.user_type == 'judge':
            user.is_approved = False
        
        user.save()
        
        # Send verification email
        if send_verification_email(user, self.request):
            messages.success(
                self.request, 
                f'Account created! Please check your email ({user.email}) to verify your account.'
            )
            
            # Notify admin if judge
            if user.user_type == 'judge':
                notify_admin_new_judge(user)
                
        else:
            messages.error(
                self.request,
                'Account created but verification email failed to send. Please contact support.'
            )
        
        return redirect(self.success_url)


class EmailVerificationSentView(TemplateView):
    template_name = 'accounts/verification_sent.html'


class EmailVerificationView(View):
    """Handle email verification from link"""
    
    def get(self, request, uidb64, token):
        try:
            # Decode user ID
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
            
            # Check token validity
            if default_token_generator.check_token(user, token):
                if not user.is_verified:
                    user.is_verified = True
                    user.save()
                    
                    # Send welcome email
                    send_welcome_email(user)
                    
                    messages.success(
                        request,
                        'Email verified successfully! Your account is now active.'
                    )
                    
                    # Auto-login the user
                    login(request, user)
                    
                    # Redirect based on user type and approval status
                    if user.is_judge and not user.is_approved:
                        return redirect('accounts:pending_approval')
                    else:
                        return redirect('accounts:dashboard')
                else:
                    messages.info(request, 'Email already verified.')
                    return redirect('accounts:login')
            else:
                messages.error(request, 'Invalid or expired verification link.')
                return redirect('accounts:resend_verification')
                
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            messages.error(request, 'Invalid verification link.')
            return redirect('accounts:resend_verification')


class ResendVerificationView(TemplateView):
    template_name = 'accounts/resend_verification.html'
    
    def post(self, request):
        email = request.POST.get('email')
        if email:
            try:
                user = User.objects.get(email=email)
                if not user.is_verified:
                    if send_verification_email(user, request):
                        messages.success(request, 'Verification email sent!')
                    else:
                        messages.error(request, 'Failed to send email. Please try again.')
                else:
                    messages.info(request, 'Email already verified.')
            except User.DoesNotExist:
                messages.error(request, 'No account found with that email address.')
        
        return redirect('accounts:resend_verification')


class PendingApprovalView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/pending_approval.html'
    
    def dispatch(self, request, *args, **kwargs):
        # Only allow judges who are verified but not approved
        if not request.user.is_judge or not request.user.is_verified or request.user.is_approved:
            return redirect('accounts:dashboard')
        return super().dispatch(request, *args, **kwargs)


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.request.user.profile
        context['completion_percentage'] = self.request.user.profile.profile_completion_percentage
        return context


class ProfileEditView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    form_class = UserProfileForm
    template_name = 'accounts/profile_edit.html'
    success_url = reverse_lazy('accounts:profile')
    
    def get_object(self):
        return self.request.user.profile
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs
    
    def form_valid(self, form):
        messages.success(self.request, 'Profile updated successfully!')
        return super().form_valid(form)


class AccountSettingsView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserAccountForm
    template_name = 'accounts/account_settings.html'
    success_url = reverse_lazy('accounts:profile')
    
    def get_object(self):
        return self.request.user
    
    def form_valid(self, form):
        # If email changed, require re-verification
        if 'email' in form.changed_data:
            user = form.save(commit=False)
            user.is_verified = False
            user.save()
            
            # Send new verification email
            if send_verification_email(user, self.request):
                messages.warning(
                    self.request,
                    'Email updated! Please check your new email address for verification.'
                )
                logout(self.request)
                return redirect('accounts:verification_sent')
            else:
                messages.error(self.request, 'Failed to send verification email.')
        
        messages.success(self.request, 'Account settings updated successfully!')
        return super().form_valid(form)


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Ensure user has verification status (for backwards compatibility)
        if not hasattr(user, 'is_verified'):
            user.is_verified = True
            user.save()
        
        if not hasattr(user, 'is_approved'):
            user.is_approved = True
            user.save()
        
        # Basic stats for dashboard
        context['profile_completion'] = user.profile.profile_completion_percentage
        context['is_profile_complete'] = context['profile_completion'] >= 80
        context['verification_status'] = {
            'is_verified': getattr(user, 'is_verified', True),
            'is_approved': getattr(user, 'is_approved', True),
            'can_access': getattr(user, 'can_access_platform', True)
        }
        
        # Student-specific context
        if user.is_student:
            context['total_videos'] = 0  # Will implement in Week 2
            context['pending_evaluations'] = 0  # Will implement in Week 3
        
        # Judge-specific context
        elif user.is_judge:
            context['videos_to_review'] = 0  # Will implement in Week 3
            context['completed_reviews'] = 0  # Will implement in Week 3
        
        return context


class LogoutView(View):
    """Custom logout view"""
    def get(self, request):
        logout(request)
        messages.success(request, 'You have been successfully logged out.')
        return redirect('core:home')
    
    def post(self, request):
        logout(request)
        messages.success(request, 'You have been successfully logged out.')
        return redirect('core:home')


class ProfileImageUploadView(LoginRequiredMixin, View):
    """AJAX view for profile image upload"""
    
    def post(self, request):
        if 'profile_image' in request.FILES:
            image = request.FILES['profile_image']
            
            # Basic validation
            if image.size > 5 * 1024 * 1024:  # 5MB limit
                return JsonResponse({
                    'success': False, 
                    'error': 'Image too large (max 5MB)'
                })
            
            # Save image to profile
            profile = request.user.profile
            profile.profile_image = image
            profile.save()
            
            return JsonResponse({
                'success': True,
                'image_url': profile.profile_image.url
            })
        
        return JsonResponse({
            'success': False, 
            'error': 'No image provided'
        })


# Password Reset Views (using Django's built-in views with custom templates)
from django.contrib.auth.views import (
    PasswordResetView, PasswordResetDoneView, 
    PasswordResetConfirmView, PasswordResetCompleteView
)

class CustomPasswordResetView(PasswordResetView):
    template_name = 'accounts/password_reset.html'
    email_template_name = 'emails/password_reset_email.html'
    html_email_template_name = 'emails/password_reset_email.html'
    success_url = reverse_lazy('accounts:password_reset_done')


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'accounts/password_reset_done.html'


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'accounts/password_reset_confirm.html'
    success_url = reverse_lazy('accounts:password_reset_complete')


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'accounts/password_reset_complete.html'


from .forms import AccountDeactivationForm


class AccountDeactivationView(LoginRequiredMixin, View):
    
    def get(self, request):
        form = AccountDeactivationForm()
        return render(request, 'accounts/deactivate_account.html', {'form': form})

    def post(self, request):
        form = AccountDeactivationForm(data=request.POST)
        # The form is not strictly necessary for deletion, 
        # but we can keep it for collecting feedback if we want.
        # For now, we'll just delete the user.
        
        user = request.user
        
        # Log the user out before deleting
        logout(request)
        
        # Permanently delete the user
        user.delete()
        
        messages.success(
            request,
            'Your account has been permanently deleted. We are sorry to see you go.'
        )
        return redirect('core:home')





class ChangePasswordView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/change_password.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from django.contrib.auth.forms import PasswordChangeForm
        context['form'] = PasswordChangeForm(user=self.request.user)
        return context
    
    def post(self, request):
        from django.contrib.auth.forms import PasswordChangeForm
        from django.contrib.auth import update_session_auth_hash
        
        form = PasswordChangeForm(user=request.user, data=request.POST)
        
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Keep user logged in
            messages.success(request, 'Your password was successfully updated!')
            return redirect('accounts:account_settings')
        
        return render(request, self.template_name, {'form': form})
