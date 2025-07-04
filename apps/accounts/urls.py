from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
   # Authentication
   path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
   path('logout/', views.LogoutView.as_view(), name='logout'),
   path('signup/', views.SignUpView.as_view(), name='signup'),
   
   # Email Verification
   path('verification-sent/', views.EmailVerificationSentView.as_view(), name='verification_sent'),
   path('verify/<uidb64>/<token>/', views.EmailVerificationView.as_view(), name='verify_email'),
   path('resend-verification/', views.ResendVerificationView.as_view(), name='resend_verification'),
   
   # Judge Approval
   path('pending-approval/', views.PendingApprovalView.as_view(), name='pending_approval'),
   
   # Profile Management
   path('profile/', views.ProfileView.as_view(), name='profile'),
   path('profile/edit/', views.ProfileEditView.as_view(), name='profile_edit'),
   path('settings/', views.AccountSettingsView.as_view(), name='account_settings'),
   path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
   
   # Security
   path('change-password/', views.ChangePasswordView.as_view(), name='change_password'),
   
   # Account Deactivation
   path('deactivate/', views.AccountDeactivationView.as_view(), name='deactivate_account'),
   
   
   # AJAX
   path('ajax/upload-image/', views.ProfileImageUploadView.as_view(), name='upload_image'),
   
   # Password Reset
   path('password-reset/', views.CustomPasswordResetView.as_view(), name='password_reset'),
   path('password-reset/done/', views.CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
   path('password-reset/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
   path('password-reset/complete/', views.CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
