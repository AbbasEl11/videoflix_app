from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from auth_app.models import UserModel
import secrets


class RegistrationSerializer(serializers.ModelSerializer):
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
        password = self.initial_data.get('password')
        if password and value and password != value:
            raise serializers.ValidationError('Passwords do not match')
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('Email already exists')
        return value

    def save(self):
        pw = self.validated_data['password']

        account = User(email=self.validated_data['email'], username=self.validated_data['email'])
        account.is_active = False
        account.set_password(pw)
        account.save()

        user_data = UserModel(user=account, token= secrets.token_urlsafe(20))
        user_data.save()
        return account


class ActivationSerializer(serializers.Serializer):
    message = serializers.CharField()
    

class LoginSerializer(serializers.Serializer):
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


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordConfirmSerializer(serializers.Serializer):
    new_password = serializers.CharField()
    confirm_password = serializers.CharField()

    def validate(self, attrs):
        new_password = attrs.get('new_password')
        confirm_password = attrs.get('confirm_password')

        if new_password != confirm_password:
            raise serializers.ValidationError('Passwords do not match')
        
        return attrs