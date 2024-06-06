from rest_framework import mixins, status
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from backend_drf.serializers.administrators.serializers import BookingSerializerForAdmin
from backend_drf.serializers.booking.serializers import *
from django.shortcuts import get_object_or_404
from datetime import datetime
from backend_drf.permissions import IsAdminUserOrOwner
from django.utils import timezone


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


class GetBookingView(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request, *args, **kwargs):
        me_booking = Booking.objects.filter(
            userID=request.user
        )
        serializer = BookingSerializer(me_booking, many=True)
        return Response(serializer.data)


class CancelBookingView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUserOrOwner]

    def delete(self, request, booking_id):
        booking = get_object_or_404(Booking, id=booking_id)

        if request.user == booking.userID or request.user.is_staff:
            if booking.status == 'VERIFY' or request.user.is_staff or booking.start_datetime > timezone.now():
                booking.status = 'CANCEL'
                booking.save()
                return Response({'detail': 'Booking cancelled successfully.'}, status=status.HTTP_200_OK)
            else:
                return Response({'detail': 'Booking cannot be cancelled.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'detail': 'You do not have permission to cancel this booking.'},
                            status=status.HTTP_403_FORBIDDEN)


class AllBookingsView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        bookings = Booking.objects.all()
        serializer = BookingSerializerForAdmin(bookings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class VerificationBookingsView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        bookings = Booking.objects.filter(status='VERIFY')
        serializer = BookingSerializerForAdmin(bookings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AllBookingsByDateView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, date):
        try:
            date_obj = datetime.strptime(date, '%Y-%m-%d')
            bookings = Booking.objects.filter(start_datetime__date=date_obj)
            serializer = BookingSerializerForAdmin(bookings, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ValueError:
            return Response({'detail': 'Invalid date format. Please use YYYY-MM-DD.'},
                            status=status.HTTP_400_BAD_REQUEST)


class VerificationBookingsByDateView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, date):
        try:
            date_obj = datetime.strptime(date, '%Y-%m-%d')
            bookings = Booking.objects.filter(status='VERIFY', start_datetime__date=date_obj)
            serializer = BookingSerializerForAdmin(bookings, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ValueError:
            return Response({'detail': 'Invalid date format. Please use YYYY-MM-DD.'},
                            status=status.HTTP_400_BAD_REQUEST)


class ConfirmBookingView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUserOrOwner]

    def put(self, request, booking_id):
        booking = get_object_or_404(Booking, id=booking_id)
        table = get_object_or_404(Table, id=booking.tableID.id)

        if request.user == booking.userID or request.user.is_staff:
            if booking.status == 'VERIFY':
                intersecting_bookings = Booking.objects.filter(
                    tableID=table.id,
                    status='PAID',
                    start_datetime__lte=booking.end_datetime,
                    end_datetime__gt=booking.start_datetime
                )

                total_taken_seats = intersecting_bookings.aggregate(
                    total_taken_seats=Sum('occupied_seats')
                )['total_taken_seats']
                total_taken_seats = total_taken_seats or 0

                available_seats = table.available_seats - total_taken_seats

                if available_seats >= booking.occupied_seats:
                    booking.status = 'PAID'
                    booking.save()
                    return Response({'detail': 'Booking confirmed successfully.'}, status=status.HTTP_200_OK)
                else:
                    return Response({'detail': 'Not enough available seats.'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'detail': 'Booking cannot be confirmed.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'detail': 'You do not have permission to confirm this booking.'},
                            status=status.HTTP_403_FORBIDDEN)
