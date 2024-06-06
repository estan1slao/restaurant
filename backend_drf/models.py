from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField
from django.conf import settings


User = settings.AUTH_USER_MODEL


class Account(AbstractUser):
    phone_number = PhoneNumberField(region="RU")
    REQUIRED_FIELDS = ["email", "first_name", "phone_number"]
