from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.handlers.modwsgi import check_password
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers, status
from rest_framework.generics import UpdateAPIView
from rest_framework.response import Response
from rest_framework.serializers import raise_errors_on_nested_writes
from rest_framework.utils import model_meta
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from backend_drf.models import Account


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['username'] = user.username
        token['email'] = user.email
        #token['phone_number'] = user.phone_number
        # ...

        return token


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=Account.objects.all())]
    )
    name = serializers.CharField(write_only=True, required=True, max_length=20)
    surname = serializers.CharField(write_only=True, required=True, max_length=20)

    class Meta:
        model = Account
        fields = ('username', 'email', 'password', 'password2', 'name', 'surname', 'phone_number')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."})

        return attrs

    def create(self, validated_data):
        user = Account.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['name'],
            last_name=validated_data['surname'],
            phone_number=validated_data['phone_number']
        )

        user.set_password(validated_data['password'])
        user.save()

        return user


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'phone_number')

    def update(self, instance, validated_data):
        if "password" in validated_data:
            raise serializers.ValidationError("Чтобы поменять пароль обратитесь по адресу: /update-password/")

        if "username" in validated_data:
            raise serializers.ValidationError("Невозможно поменять username у пользователя.")

        if "email" in validated_data:
            raise serializers.ValidationError("Невозможно поменять email у пользователя.")

        if "phone_number" in validated_data:
            raise serializers.ValidationError("Невозможно поменять номер телефона у пользователя.")

        validated_data.pop('username', None)
        validated_data.pop('email', None)
        validated_data.pop('password', None)
        validated_data.pop('phone_number', None)

        return super(ProfileSerializer, self).update(instance, validated_data)