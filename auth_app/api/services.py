from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from auth_app.models import UserModel
from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str


def send_email(to_email: str, token: str, uidb64: str,):
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

def activate_user_account(uidb64: str, token: str):
    if not uidb64 or not token:
        raise ValueError("UID and token must be provided")
    
    try:
        user_model = UserModel.objects.select_related('user').get(uidb64=uidb64, token=token)
    except UserModel.DoesNotExist:
        raise ValueError("Account is already activated or invalid activation link")
    
    user = user_model.user

    if user_model.token != token:
        raise ValueError("Invalid activation token")
    
    user.is_active = True
    user.save(update_fields=['is_active'])

    user_model.token = ''
    user_model.save(update_fields=['token'])

    UserModel.delete(user_model)

    return "Account activated successfully"