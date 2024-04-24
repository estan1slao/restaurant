from datetime import datetime

from django.contrib.auth.password_validation import validate_password
from django.shortcuts import render
from rest_framework import viewsets, mixins, status, generics
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework.permissions import IsAdminUser, AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.views import TokenObtainPairView

from backend_drf.Models.administrator.models import ModerationSettings
from backend_drf.models import Account
from backend_drf.serializers.administrators.serializers import ModerationResponseSerializer
from backend_drf.serializers.registation.serializers import MyTokenObtainPairSerializer, RegisterSerializer, \
    ProfileSerializer
from backend_drf.Models.booking_service.models import *
from backend_drf.serializers.booking.serializers import *
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.db.models import Q
from datetime import datetime, timedelta
from django.utils.timezone import make_aware


# Profile/Registration
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class RegisterView(generics.CreateAPIView):
    queryset = Account.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getProfile(request):
    user = request.user
    serializer = ProfileSerializer(user, many=False)
    return Response(serializer.data)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateProfile(request):
    user = request.user
    if "password" in request.data:
        return Response({"message": "Чтобы поменять пароль обратитесь по адресу: /update-password/"}, status=status.HTTP_400_BAD_REQUEST)
    serializerAccount = ProfileSerializer(user, data=request.data, partial=True)
    if serializerAccount.is_valid():
        serializerAccount.update(user, serializerAccount.validated_data)
        return Response({"message": "Информация успешно обновлена."}, status=status.HTTP_200_OK)
    return Response(serializerAccount.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updatePassword(request):
    user = request.user
    current_password = request.data.get('current_password')
    new_password = request.data.get('password')

    if not user.check_password(current_password):
        return Response({"error": "Неверный текущий пароль."}, status=status.HTTP_400_BAD_REQUEST)

    try:
        validate_password(new_password, user=user)
    except:
        return Response({"error": "Пароль не соответствует требованиям безопасности"}, status=status.HTTP_400_BAD_REQUEST)

    user.set_password(new_password)
    user.save()

    return Response({"message": "Пароль успешно обновлен."}, status=status.HTTP_200_OK)


# Get table cards
class TablesView(generics.ListAPIView,
                 generics.GenericAPIView):
    queryset = Table.objects.all()
    permission_classes = (AllowAny, )
    serializer_class = TableSerializer


class CreateBookingView(mixins.CreateModelMixin,
                        GenericViewSet):
    queryset = Booking.objects.all()
    permission_classes = (IsAuthenticated, )
    serializer_class = BookingSerializer

    def create(self, request, *args, **kwargs):
        data = request.data

        if 'start_datetime' not in data or 'end_datetime' not in data:
            return Response({"error": "Необходимые поля start_datetime и end_datetime не найдены"},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            start_datetime = datetime.strptime(data['start_datetime'], '%Y-%m-%dT%H:%M:%S')
            end_datetime = datetime.strptime(data['end_datetime'], '%Y-%m-%dT%H:%M:%S')
        except ValueError:
            return Response({"error": "Неверный формат даты/времени. Используйте формат YYYY-MM-DDTHH:MM:SS"},
                            status=status.HTTP_400_BAD_REQUEST)

        start_datetime = start_datetime.replace(minute=0, second=0)
        end_datetime = end_datetime.replace(minute=0, second=0)
        request.data['start_datetime'] = start_datetime
        request.data['end_datetime'] = end_datetime

        if start_datetime <= datetime.now() or end_datetime <= datetime.now():
            return Response({"error": "Даты должны быть только в будущем времени"},
                            status=status.HTTP_400_BAD_REQUEST)

        if start_datetime >= end_datetime:
            return Response({"error": "Дата начала бронирования должна быть перед датой окончания"},
                            status=status.HTTP_400_BAD_REQUEST)

        return super().create(request, *args, **kwargs)


class ModerationView(APIView):
    def get(self, request, *args, **kwargs):
        moderation_settings = ModerationSettings.objects.first()
        if not moderation_settings:
            moderation_settings = ModerationSettings.objects.create()
        serializer = ModerationResponseSerializer(moderation_settings)
        return Response(serializer.data)

class ManualModerationView(APIView):
    def post(self, request, *args, **kwargs):
        moderation_settings, created = ModerationSettings.objects.get_or_create()
        moderation_settings.moderation_type = 'manual'
        moderation_settings.save()
        return Response(status=status.HTTP_200_OK)

class AutoModerationView(APIView):
    def post(self, request, *args, **kwargs):
        moderation_settings, created = ModerationSettings.objects.get_or_create()
        moderation_settings.moderation_type = 'auto'
        moderation_settings.save()
        return Response(status=status.HTTP_200_OK)



def get_table_info(request, table_id, date):
    # Получаем информацию о столике
    table = get_object_or_404(Table, pk=table_id)

    # Парсим дату
    try:
        date = datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        return JsonResponse({'error': 'Invalid date format. Please use YYYY-MM-DD.'}, status=400)

    # Создаем расписание на весь день с промежутками по часу
    schedule = []
    current_time = make_aware(date.replace(hour=0, minute=0, second=0))
    while current_time < make_aware(date.replace(hour=23, minute=59, second=59)):
        schedule.append({
            'start_time': current_time,
            'end_time': current_time + timedelta(hours=1),
            'free_seats': table.available_seats
        })
        current_time += timedelta(hours=1)

    # Получаем все бронирования для этого столика на заданный день
    bookings = Booking.objects.filter(
        tableID=table,
        start_datetime__date=date,
        status= 'PAID'
    )

    # Обновляем расписание на основе бронирований
    for booking in bookings:
        for slot in schedule:
            if slot['start_time'] < booking.end_datetime and slot['end_time'] > booking.start_datetime:
                slot['free_seats'] -= booking.occupied_seats
                if slot['free_seats'] <= 0:
                    schedule.remove(slot)


    # Формируем ответ
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

