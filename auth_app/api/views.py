from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .serializers import RegistrationSerializer, LoginSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
import django_rq
from django_rq import enqueue
from .services import send_email, activate_user_account, create_jwt_tokens, clear_auth_cookies, set_auth_cookies, blacklist_refresh_token,create_access_token_from_refresh, get_refresh_token_from_cookies
from rest_framework import views
from django.conf import settings

class RegistrationView(APIView):
    """
    API view for user registration.
    
    POST: Creates a new user account with username, email, and password.
          Returns success message on successful registration.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Register a new user.
        
        Args:
            request: HTTP request with username, email, password, confirmed_password
            
        Returns:
            Response: Success message (201) or validation errors (400)
        """
        serializer = RegistrationSerializer(data=request.data)

        if serializer.is_valid():
            instance = serializer.save()
            
            queue = django_rq.get_queue('high', autocommit=True)
            queue.enqueue(
                send_email, instance.email, instance.usermodel.token, instance.usermodel.uidb64)
            
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
    """
    API view for user account activation.
    
    GET: Activates user account using uidb64 and token from activation link.
          Returns success message on successful activation.
    """
    permission_classes = [AllowAny]

    def get(self, request, uidb64: str, token: str):
        """
        Activate user account.
        
        Args:
            request: HTTP request
            uidb64: Base64 encoded user ID
            token: Activation token
            
        Returns:
            Response: Success message (200) or error message (400)
        """
        try:
            activate_user_account(uidb64, token)
            return Response({"message": "Account activated successfully!"}, status=status.HTTP_200_OK)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class LoginView(TokenObtainPairView):
    """
    API view for user login with JWT tokens stored in HTTP-only cookies.
    
    POST: Authenticates user and returns access/refresh tokens in secure cookies.
          Also returns user information (id, username, email) in response body.
    """
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
    """
    API view for user logout with token blacklisting.
    
    POST: Blacklists the refresh token and deletes both access and refresh cookies.
          Requires authentication via access token.
    """
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
    """
    API view for refreshing JWT access token using refresh token from cookies.
    
    POST: Validates refresh token from cookie and issues new access token.
          Updates access_token cookie with new token.
    """
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