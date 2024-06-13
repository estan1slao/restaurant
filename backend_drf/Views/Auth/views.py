from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import status, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from backend_drf.models import Account
from backend_drf.serializers.registation.serializers import MyTokenObtainPairSerializer, RegisterSerializer, \
    ProfileSerializer


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
        return Response({"message": "Чтобы поменять пароль обратитесь по адресу: /update-password/"},
                        status=status.HTTP_400_BAD_REQUEST)
    serializer_account = ProfileSerializer(user, data=request.data, partial=True)
    if serializer_account.is_valid():
        serializer_account.update(user, serializer_account.validated_data)
        return Response({"message": "Информация успешно обновлена."}, status=status.HTTP_200_OK)
    return Response(serializer_account.errors, status=status.HTTP_400_BAD_REQUEST)


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
    except ValueError:
        return Response({"error": "Пароль не соответствует требованиям безопасности"},
                        status=status.HTTP_400_BAD_REQUEST)
    except ValidationError:
        return Response({"error": "Пароль не соответствует требованиям безопасности"},
                        status=status.HTTP_400_BAD_REQUEST)

    user.set_password(new_password)
    user.save()

    return Response({"message": "Пароль успешно обновлен."}, status=status.HTTP_200_OK)

