from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .serializers import RegistrationSerializer, LoginSerializer, PasswordResetSerializer, PasswordConfirmSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
import django_rq
from django_rq import enqueue
from .services import activate_user_account, create_jwt_tokens, clear_auth_cookies, set_auth_cookies, blacklist_refresh_token,create_access_token_from_refresh, get_refresh_token_from_cookies, create_password_reset, confirm_password_reset
from .tasks import send_verification_email, send_password_reset_email
from rest_framework import views
from django.conf import settings
from django.contrib.auth.models import User

class RegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)

        if serializer.is_valid():
            instance = serializer.save()
            
            queue = django_rq.get_queue('high', autocommit=True)
            queue.enqueue(
                send_verification_email, instance.email, instance.usermodel.token, instance.usermodel.uidb64)
            
            return Response({
                "user": {
                         "id": instance.id,
                         "email": instance.email,
                         }, 
                "token": instance.usermodel.token,                            
                             }, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

class ActivationView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, uidb64: str, token: str):
        try:
            activate_user_account(uidb64, token)
            return Response({"message": "Account activated successfully!"}, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class LoginView(TokenObtainPairView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        access_token, refresh_token = create_jwt_tokens(user)

        res = Response({
            "message": "Login successful",
            "user": {
                "id": user.id,
                "username": user.email,
            }}, status=status.HTTP_200_OK)
        set_auth_cookies(res, access_token, refresh_token)
        return res
    

class LogoutView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_cookie = getattr(settings, 'REFRESH_TOKEN_COOKIE_NAME', 'refresh_token')
        refresh_token = request.COOKIES.get(refresh_cookie)

        if not refresh_token:
            return Response({"detail": "Refresh token not found in cookies"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            blacklist_refresh_token(refresh_token)
        except Exception:
            return Response({"detail": "Invalid refresh token"}, status=status.HTTP_400_BAD_REQUEST)
        
        res = Response({"message": "Logout successful"}, status=status.HTTP_200_OK)
        clear_auth_cookies(res)
        return res

class CookieRefreshView(views.APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        refresh_cookie = getattr(settings, 'REFRESH_TOKEN_COOKIE_NAME', 'refresh_token')
        refresh_token = request.COOKIES.get(refresh_cookie)

        if not refresh_token :
            return Response({"error": "Refresh token not found in cookies"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            new_access_token = create_access_token_from_refresh(refresh_token)
        except Exception:
            return Response({"error": "Invalid refresh token"}, status=status.HTTP_401_UNAUTHORIZED)
        
        response = Response(
            {
            "detail": "Token refreshed", 
             "access": new_access_token}, 
             status=status.HTTP_200_OK)
        
        get_refresh_token_from_cookies(response, new_access_token)
        return response


class PasswordResetView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        
        try:
            user = User.objects.get(email=email)
            uidb64, token = create_password_reset(user)
            
            queue = django_rq.get_queue('high', autocommit=True)
            queue.enqueue(send_password_reset_email, email, token, uidb64)
            
        except User.DoesNotExist:
            pass
        
        return Response(
            {"detail": "An email has been sent to reset your password."},
            status=status.HTTP_200_OK
        )


class PasswordConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, uidb64, token):
        serializer = PasswordConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        new_password = serializer.validated_data['new_password']
        
        try:
            confirm_password_reset(uidb64, token, new_password)
        except Exception:        
            return Response(
            {"error": "Invalid password reset link."},
            status=status.HTTP_400_BAD_REQUEST
        )
        
        return Response(
                {"detail": "Password has been successfully reset."},
                status=status.HTTP_200_OK
            )
            

    
