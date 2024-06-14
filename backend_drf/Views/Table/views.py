import pytz
from rest_framework import generics
from rest_framework.permissions import AllowAny

from backend_drf.serializers.booking.serializers import *
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from datetime import datetime, timedelta
from django.utils.timezone import make_aware, get_current_timezone


class TablesView(generics.ListAPIView,
                 generics.GenericAPIView):
    queryset = Table.objects.all()
    permission_classes = (AllowAny, )
    serializer_class = TableSerializer


def get_table_info(request, table_id, date):
    table = get_object_or_404(Table, pk=table_id)

    try:
        date = datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        return JsonResponse({'error': 'Invalid date format. Please use YYYY-MM-DD.'}, status=400)

    def round_up_to_nearest_hour(dt):
        if dt.minute != 0 or dt.second != 0 or dt.microsecond != 0:
            dt += timedelta(hours=1)
            dt = dt.replace(minute=0, second=0, microsecond=0)
        return dt

    local_tz = pytz.timezone('Asia/Yekaterinburg')
    now = datetime.now(local_tz)

    booking_date = make_aware(date, get_current_timezone())

    if booking_date.date() < now.date():
        schedule = []
    elif booking_date.date() == now.date():
        current_time = round_up_to_nearest_hour(now)
        end_of_day = now.replace(hour=23, minute=59, second=59, microsecond=0)
        schedule = []
        while current_time < end_of_day:
            schedule.append({
                'start_time': current_time,
                'end_time': current_time + timedelta(hours=1),
                'free_seats': table.available_seats
            })
            current_time += timedelta(hours=1)
    else:
        start_of_day = booking_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = booking_date.replace(hour=23, minute=59, second=59, microsecond=0)
        schedule = []
        current_time = start_of_day
        while current_time < end_of_day:
            schedule.append({
                'start_time': current_time,
                'end_time': current_time + timedelta(hours=1),
                'free_seats': table.available_seats
            })
            current_time += timedelta(hours=1)

    bookings = Booking.objects.filter(
        tableID=table,
        start_datetime__date=date,
        status='PAID'
    )

    for booking in bookings:
        for slot in schedule:
            if slot['start_time'] < booking.end_datetime and slot['end_time'] > booking.start_datetime:
                slot['free_seats'] -= booking.occupied_seats
                if slot['free_seats'] <= 0:
                    schedule.remove(slot)

    response = {
        'table_id': table.id,
        'title': table.title,
        'description': table.description,
        'price': table.price,
        'date': date.strftime('%Y-%m-%d'),
        'schedule': [{
            'start_time': slot['start_time'].strftime('%H:%M'),
            'end_time': slot['end_time'].strftime('%H:%M'),
            'free_seats': slot['free_seats']
        } for slot in schedule]
    }

    return JsonResponse(response)
