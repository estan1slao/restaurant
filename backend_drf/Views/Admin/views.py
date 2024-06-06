from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from backend_drf.serializers.administrators.serializers import ModerationResponseSerializer, BookingSerializerForAdmin
from backend_drf.serializers.booking.serializers import *


class ModerationView(APIView):
    def get(self, request, *args, **kwargs):
        moderation_settings = ModerationSettings.objects.first()
        if not moderation_settings:
            moderation_settings = ModerationSettings.objects.create()
        serializer = ModerationResponseSerializer(moderation_settings)
        return Response(serializer.data)


class ManualModerationView(APIView):
    permission_classes = (IsAdminUser,)

    def post(self, request, *args, **kwargs):
        moderation_settings, created = ModerationSettings.objects.get_or_create()
        moderation_settings.moderation_type = 'manual'
        moderation_settings.save()
        return Response(status=status.HTTP_200_OK)


class AutoModerationView(APIView):
    permission_classes = (IsAdminUser,)

    def post(self, request, *args, **kwargs):
        moderation_settings, created = ModerationSettings.objects.get_or_create()
        moderation_settings.moderation_type = 'auto'
        moderation_settings.save()
        return Response(status=status.HTTP_200_OK)
