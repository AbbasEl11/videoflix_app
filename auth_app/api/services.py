import secrets
from django.conf import settings
from auth_app.models import UserModel
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User

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


def create_jwt_tokens(user):
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token), str(refresh)

def set_auth_cookies(response, access_token: str, refresh_token: str):
    access_cookie = getattr(settings, 'ACCESS_TOKEN_COOKIE_NAME', 'access_token')
    refresh_cookie = getattr(settings, 'REFRESH_TOKEN_COOKIE_NAME', 'refresh_token')

    secure = bool(getattr(settings, 'AUTH_COOKIE_SECURE', False))
    samesite = getattr(settings, 'AUTH_COOKIE_SAMESITE', 'Lax')

    access_cookie_max_age = int(getattr(settings, 'ACCESS_TOKEN_COOKIE_AGE', 60 * 15))  
    refresh_cookie_max_age = int(getattr(settings, 'REFRESH_TOKEN_COOKIE_AGE', 60 * 15 * 24 * 7))

    response.set_cookie(
        access_cookie,
        access_token,
        max_age=access_cookie_max_age,
        secure=secure,
        httponly=True,
        samesite=samesite,
        path='/'
    )

    response.set_cookie(
        refresh_cookie,
        refresh_token,
        max_age=refresh_cookie_max_age,
        secure=secure,
        httponly=True,
        samesite=samesite,
        path='/'
    )

    return response

def clear_auth_cookies(response):
    access_cookie = getattr(settings, 'ACCESS_TOKEN_COOKIE_NAME', 'access_token')
    refresh_cookie = getattr(settings, 'REFRESH_TOKEN_COOKIE_NAME', 'refresh_token')

    samesite = getattr(settings, 'AUTH_COOKIE_SAMESITE', 'Lax')

    response.delete_cookie(
        access_cookie,
        path = '/',
        samesite=samesite,
    )

    response.delete_cookie(
        refresh_cookie,
        path = '/',
        samesite=samesite,
    )

    return response

def blacklist_refresh_token(refresh_token: str):
    token = RefreshToken(refresh_token)
    token.blacklist()

def create_access_token_from_refresh(refresh_token: str):
    token = RefreshToken(refresh_token)
    new_access_token = token.access_token
    return str(new_access_token)

def get_refresh_token_from_cookies(response, access_token: str):
    access_cookie = getattr(settings, 'ACCESS_TOKEN_COOKIE_NAME', 'access_token')

    secure = bool(getattr(settings, 'AUTH_COOKIE_SECURE', False))
    samesite = getattr(settings, 'AUTH_COOKIE_SAMESITE', 'Lax')

    access_max_age = int(getattr(settings, 'ACCESS_TOKEN_COOKIE_AGE', 60 * 15))

    response.set_cookie(
        access_cookie,
        access_token,
        max_age=access_max_age,
        secure=secure,
        httponly=True,
        samesite=samesite,
        path='/'
    )

    return response


def create_password_reset(user: User):
    token = secrets.token_urlsafe(20)

    obj, created = UserModel.objects.get_or_create(user=user)
    obj.token = token
    obj.save()

    uidb64 = str(obj.uidb64)
    
    return uidb64, token


def confirm_password_reset(uidb64: str, token: str, new_password: str):
    try:
        user_model = UserModel.objects.select_related('user').get(uidb64=uidb64, token=token)
    except UserModel.DoesNotExist:
        raise ValueError("Invalid password reset link")

    user = user_model.user
    user.set_password(new_password)
    user.save(update_fields=['password'])
    
    user_model.delete()

    