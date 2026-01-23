from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def send_verification_email(to_email: str, token: str, uidb64: str):
    subject = 'Welcome to Videoflix!'
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None) or getattr(settings, 'EMAIL_HOST_USER', None)

    frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:5500')   
    verify_url = f"{frontend_url}/pages/auth/activate.html?uid={uidb64}&token={token}"

    html = render_to_string(
        "verify_email.html",
        {
            "subject": subject,
            "preheader": "Please verify your email address to activate your account.",
            "app_name": getattr(settings, "APP_NAME", None) or "Videoflix",
            "logo_url": getattr(settings, "EMAIL_LOGO_URL", None),
            "verify_url": verify_url,
            "year": getattr(settings, "EMAIL_YEAR", None),
        },
    )

    text = strip_tags(html)

    send_mail(
        subject=subject,
        message=text,
        from_email=from_email,
        recipient_list=[to_email],
        html_message=html,
        fail_silently=False,
    )


def send_password_reset_email(to_email: str, token: str, uidb64: str):
    print( uidb64, token )
    subject = 'Reset your Videoflix password'
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', None) or getattr(settings, 'EMAIL_HOST_USER', None)

    frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:5500')
    reset_url = f"{frontend_url}/pages/auth/password-reset.html?uid={uidb64}&token={token}"

    html = render_to_string(
        "password_reset_email.html",
        {
            "subject": subject,
            "preheader": "You requested to reset your password. Click the link to reset it.",
            "app_name": getattr(settings, "APP_NAME", None) or "Videoflix",
            "logo_url": getattr(settings, "EMAIL_LOGO_URL", None),
            "reset_url": reset_url,
            "year": getattr(settings, "EMAIL_YEAR", None),
        },
    )

    text = strip_tags(html)

    send_mail(
        subject=subject,
        message=text,
        from_email=from_email,
        recipient_list=[to_email],
        html_message=html,
        fail_silently=False,
    )
