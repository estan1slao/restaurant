from rest_framework import serializers
from backend_drf.Models.administrator.models import *
from backend_drf.Models.booking_service.models import *
from backend_drf.serializers.booking.serializers import TableSerializer
from backend_drf.serializers.registation.serializers import AccountSerializer


class ModerationResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModerationSettings
        fields = ['moderation_type']


class BookingSerializerForAdmin(serializers.ModelSerializer):
    user = AccountSerializer(source='userID', read_only=True)
    table = TableSerializer(source='tableID', read_only=True)

    class Meta:
        model = Booking
        fields = '__all__'
