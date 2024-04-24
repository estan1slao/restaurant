from django.contrib.auth.handlers.modwsgi import check_password
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers, status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import UpdateAPIView
from rest_framework.response import Response
from rest_framework.serializers import raise_errors_on_nested_writes
from rest_framework.utils import model_meta
from rest_framework.validators import UniqueValidator
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from backend_drf.Models.administrator.models import ModerationSettings
from backend_drf.Models.booking_service.models import *
from django.db.models import Q, Sum


class TableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Table
        fields = '__all__'


class BookingSerializer(serializers.ModelSerializer):
    #tableID = serializers.PrimaryKeyRelatedField(queryset=Table.objects.all(), source='id')

    class Meta:
        model = Booking
        fields = ('tableID', 'start_datetime', 'end_datetime', 'occupied_seats')

    def create(self, validated_data):
        moderation_settings, created = ModerationSettings.objects.get_or_create()
        if moderation_settings.moderation_type == 'auto':
            STATUS = 'PAID'
        else:
            STATUS = 'VERIFY'

        taken_seats = validated_data['occupied_seats']
        table_id = validated_data['tableID'].id
        intersecting_bookings = Booking.objects.filter(
            tableID = table_id,
            status = 'PAID',
            start_datetime__lte=validated_data['end_datetime'],
            end_datetime__gt=validated_data['start_datetime']
        )

        total_taken_seats = intersecting_bookings.aggregate(total_taken_seats=Sum('occupied_seats'))[
            'total_taken_seats']
        table = Table.objects.get(id=table_id)
        available_seats = table.available_seats - (total_taken_seats or 0)
        if available_seats >= taken_seats:
            user = self.context['request'].user
            booking = Booking.objects.create(
                userID = user,
                status = STATUS,
                tableID = table,

                start_datetime = validated_data['start_datetime'],
                end_datetime = validated_data['end_datetime'],

                occupied_seats = taken_seats,
            )
            booking.save()
            return booking
        else:
            raise ValidationError("Для этого бронирования недостаточно свободных мест")

