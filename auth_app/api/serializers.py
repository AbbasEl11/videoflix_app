from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from auth_app.models import UserModel
import secrets


class RegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    
    Handles user creation with password confirmation and email uniqueness validation.
    Passwords are hashed before saving to database.
    """
    confirmed_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'password', 'confirmed_password']
        extra_kwargs = {
            'password': {
                'write_only': True
            },
            'email': {
                'required': True
            }
        }

    def validate_confirmed_password(self, value):
        """
        Validate that password and confirmed_password match.
        
        Args:
            value: Confirmed password value
            
        Returns:
            str: Validated password
            
        Raises:
            ValidationError: If passwords don't match
        """
        password = self.initial_data.get('password')
        if password and value and password != value:
            raise serializers.ValidationError('Passwords do not match')
        return value

    def validate_email(self, value):
        """
        Validate that email is unique.
        
        Args:
            value: Email address
            
        Returns:
            str: Validated email
            
        Raises:
            ValidationError: If email already exists
        """
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email already exists')
        return value

    def save(self):
        """
        Create and save new user with hashed password.
        
        Returns:
            User: Newly created user instance
        """
        pw = self.validated_data['password']

        account = User(email=self.validated_data['email'], username=self.validated_data['email'])
        account.is_active = False
        account.set_password(pw)
        account.save()

        user_data = UserModel(user=account, token= secrets.token_urlsafe(20))
        user_data.save()
        return account


class ActivationSerializer(serializers.Serializer):
    """
    Serializer for account activation.
    
    Validates the activation token and user ID.
    """
    message = serializers.CharField()
    

class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login.
    
    Validates email and password for authentication.
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        user = authenticate(username=email, password=password)
        
        if not user:
            raise serializers.ValidationError('Invalid email or password')
        
        if not user.is_active:
            raise serializers.ValidationError('Account is not activated')
        
        attrs['user'] = user
        return attrs