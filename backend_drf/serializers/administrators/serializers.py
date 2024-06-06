from rest_framework import serializers
from backend_drf.Models.administrator.models import *
from backend_drf.Models.booking_service.models import *


class ModerationResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModerationSettings
        fields = ['moderation_type']


class BookingSerializerForAdmin(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = '__all__'
