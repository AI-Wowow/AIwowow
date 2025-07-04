from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
import logging

logger = logging.getLogger(__name__)


def send_verification_email(user, request):
    """Send email verification email to user"""
    try:
        # Generate verification link
        verification_link = user.get_verification_link(request)
        
        # Render email template
        subject = 'Verify your Video Platform account'
        html_message = render_to_string('emails/verification_email.html', {
            'user': user,
            'verification_link': verification_link,
            'site_name': 'Video Platform',
            'site_domain': get_current_site(request).domain,
        })
        plain_message = strip_tags(html_message)
        
        # Send email
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Verification email sent to {user.email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send verification email to {user.email}: {str(e)}")
        return False


def send_welcome_email(user):
    """Send welcome email to verified user"""
    try:
        subject = 'Welcome to Video Platform!'
        html_message = render_to_string('emails/welcome_email.html', {
            'user': user,
            'site_name': 'Video Platform',
        })
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=True,
        )
        
        logger.info(f"Welcome email sent to {user.email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send welcome email to {user.email}: {str(e)}")
        return False


def send_judge_approval_notification(user):
    """Send notification when judge is approved"""
    try:
        subject = 'Your judge application has been approved!'
        html_message = render_to_string('emails/judge_approval_email.html', {
            'user': user,
            'site_name': 'Video Platform',
        })
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=True,
        )
        
        logger.info(f"Judge approval email sent to {user.email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send judge approval email to {user.email}: {str(e)}")
        return False


def notify_admin_new_judge(user):
    """Notify admin when new judge registers"""
    try:
        admin_emails = [admin[1] for admin in settings.ADMINS]
        if not admin_emails:
            return False
            
        subject = f'New judge registration: {user.email}'
        html_message = render_to_string('emails/admin_new_judge.html', {
            'user': user,
            'site_name': 'Video Platform',
        })
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=admin_emails,
            html_message=html_message,
            fail_silently=True,
        )
        
        logger.info(f"Admin notification sent for new judge: {user.email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send admin notification for judge {user.email}: {str(e)}")
        return False


def send_deactivation_email(user, deactivation):
    """Send account deactivation confirmation email"""
    try:
        subject = 'Account Deactivated - Video Platform'
        html_message = render_to_string('emails/deactivation_email.html', {
            'user': user,
            'deactivation': deactivation,
            'site_name': 'Video Platform',
        })
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=True,
        )
        
        logger.info(f"Deactivation email sent to {user.email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send deactivation email to {user.email}: {str(e)}")
        return False


def notify_admin_reactivation_request(email, message):
    """Notify admin of reactivation request"""
    try:
        admin_emails = [admin[1] for admin in settings.ADMINS]
        if not admin_emails:
            return False
            
        subject = f'Account Reactivation Request: {email}'
        html_message = render_to_string('emails/admin_reactivation_request.html', {
            'email': email,
            'message': message,
            'site_name': 'Video Platform',
        })
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=admin_emails,
            html_message=html_message,
            fail_silently=True,
        )
        
        logger.info(f"Admin notification sent for reactivation request: {email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send admin notification for reactivation {email}: {str(e)}")
        return False


def send_deactivation_email(user, deactivation):
    """Send account deactivation confirmation email"""
    try:
        subject = 'Account Deactivated - Video Platform'
        html_message = render_to_string('emails/deactivation_email.html', {
            'user': user,
            'deactivation': deactivation,
            'site_name': 'Video Platform',
        })
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=True,
        )
        
        logger.info(f"Deactivation email sent to {user.email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send deactivation email to {user.email}: {str(e)}")
        return False


def notify_admin_reactivation_request(email, message):
    """Notify admin of reactivation request"""
    try:
        admin_emails = [admin[1] for admin in settings.ADMINS]
        if not admin_emails:
            return False
            
        subject = f'Account Reactivation Request: {email}'
        html_message = render_to_string('emails/admin_reactivation_request.html', {
            'email': email,
            'message': message,
            'site_name': 'Video Platform',
        })
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=admin_emails,
            html_message=html_message,
            fail_silently=True,
        )
        
        logger.info(f"Admin notification sent for reactivation request: {email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send admin notification for reactivation {email}: {str(e)}")
        return False


def send_reactivation_approval_email(user):
    """Send email when account reactivation is approved"""
    try:
        subject = 'Account Reactivated - Video Platform'
        html_message = render_to_string('emails/reactivation_approval_email.html', {
            'user': user,
            'site_name': 'Video Platform',
        })
        plain_message = strip_tags(html_message)
        
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=True,
        )
        
        logger.info(f"Reactivation approval email sent to {user.email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send reactivation approval email to {user.email}: {str(e)}")
        return False
