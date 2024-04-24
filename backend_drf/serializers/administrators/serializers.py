from rest_framework import serializers
from backend_drf.Models.administrator.models import *


class ModerationResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = ModerationSettings
        fields = ['moderation_type']