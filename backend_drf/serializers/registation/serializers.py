from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from backend_drf.models import Account


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['username'] = user.username
        token['email'] = user.email
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
        fields = ('id', 'username', 'first_name', 'last_name', 'email', 'phone_number', 'is_staff')

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


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['first_name', 'last_name', 'email', 'phone_number']
