from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login, logout
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.http import JsonResponse
from django.views import View
from .models import User, UserProfile
from .forms import CustomUserCreationForm, UserProfileForm, UserAccountForm


class SignUpView(CreateView):
    model = User
    form_class = CustomUserCreationForm
    template_name = 'accounts/signup.html'
    success_url = reverse_lazy('accounts:profile_edit')
    
    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        messages.success(
            self.request, 
            'Account created successfully! Please complete your profile.'
        )
        return redirect(self.success_url)


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
        messages.success(self.request, 'Account settings updated successfully!')
        return super().form_valid(form)


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        
        # Basic stats for dashboard
        context['profile_completion'] = user.profile.profile_completion_percentage
        context['is_profile_complete'] = context['profile_completion'] >= 80
        
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
