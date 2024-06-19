from django.core.mail import send_mail
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from backend_drf.Models.administrator.models import ModerationSettings
from backend_drf.Models.booking_service.models import *
from django.db.models import Sum
from restaurant.settings import SERVER_EMAIL


class TableSerializer(serializers.ModelSerializer):
    class Meta:
        model = Table
        fields = '__all__'


class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ('id', 'tableID', 'start_datetime', 'end_datetime', 'occupied_seats', 'status')
        extra_kwargs = {
            'status': {'required': False},
        }

    def create(self, validated_data):
        moderation_settings, created = ModerationSettings.objects.get_or_create()
        if moderation_settings.moderation_type == 'auto':
            status = 'PAID'
        else:
            status = 'VERIFY'

        try:
            taken_seats = validated_data['occupied_seats']
        except KeyError:
            raise ValidationError("Укажите количество занимаемых мест в поле occupied_seats")

        if taken_seats <= 0:
            raise ValidationError("Укажите корректное (<= 0) количество занимаемых мест в поле occupied_seats")

        table_id = validated_data['tableID'].id
        intersecting_bookings = Booking.objects.filter(
            tableID=table_id,
            status='PAID',
            start_datetime__lt=validated_data['end_datetime'],
            end_datetime__gt=validated_data['start_datetime']
        )

        total_taken_seats = intersecting_bookings.aggregate(total_taken_seats=Sum('occupied_seats'))[
            'total_taken_seats']
        table = Table.objects.get(id=table_id)
        available_seats = table.available_seats - (total_taken_seats or 0)
        if available_seats >= taken_seats:
            user = self.context['request'].user
            booking = Booking.objects.create(
                userID=user,
                status=status,
                tableID=table,

                start_datetime=validated_data['start_datetime'],
                end_datetime=validated_data['end_datetime'],

                occupied_seats=taken_seats,
            )
            booking.save()

            send_mail(
                "Новое бронирование в «Ресторан-и-Точка»",
                f"Вы совершили бронирование на дату {booking.start_datetime.strftime('%d.%m.%Y')} с {booking.start_datetime.strftime('%H:%M')} по {booking.end_datetime.strftime('%H:%M')}.\n"
                f"Статус бронирования: {'Оплачено' if booking.status == 'PAID' else 'На проверке' if booking.status=='VERIFY' else 'Отменено'}.\n"
                f"Забронированные места: {booking.occupied_seats}",
                SERVER_EMAIL,
                [user.email],
                fail_silently=False,
            )

            return booking
        else:
            raise ValidationError("Для этого бронирования недостаточно свободных мест")

