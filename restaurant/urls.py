from django.contrib import admin
from rest_framework import routers
from rest_framework_simplejwt.views import TokenRefreshView

from django.urls import path, include
from backend_drf.Views.Auth.views import *
from backend_drf.Views.Booking.views import *
from backend_drf.Views.Table.views import *
from backend_drf.Views.Admin.views import *

router = routers.DefaultRouter()
router.register(r'bookings', CreateBookingView)

urlpatterns = [
    path('admin/', admin.site.urls),

    # Authentication
    path('api/v1/token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/v1/registration/', RegisterView.as_view(), name='auth_register'),

    # Profile
    path('api/v1/me/profile/', getProfile, name='profile'),
    path('api/v1/me/profile/update/', updateProfile, name='update-profile'),
    path('api/v1/me/profile/update-password/', updatePassword, name='update-password'),

    # Table
    path('api/v1/tables/', TablesView.as_view(), name='get-tables'),
    path('api/v1/tables/<int:table_id>/<str:date>/', get_table_info, name='get_table_info'),

    # Booking
    path('api/v1/', include(router.urls)),
    path('api/v1/me/bookings/', GetBookingView.as_view(), name='get_booking'),
    path('api/v1/me/bookings/<int:booking_id>/', CancelBookingView.as_view(), name='cancel-booking'),

    # Administrator
    path('api/v1/moderation/', ModerationView.as_view(), name='moderation'),
    path('api/v1/admin/manual-moderation/', ManualModerationView.as_view(), name='manual_moderation'),
    path('api/v1/admin/auto-moderation/', AutoModerationView.as_view(), name='auto_moderation'),

    path('api/v1/admin/bookings/<int:booking_id>/', CancelBookingView.as_view(), name='cancel-booking'),
    path('api/v1/admin/bookings/<int:booking_id>/confirm/', ConfirmBookingView.as_view(), name='confirm-booking'),

    path('api/v1/admin/bookings/all/', AllBookingsView.as_view(), name='all-bookings'),
    path('api/v1/admin/bookings/all/<str:date>/', AllBookingsByDateView.as_view(), name='all-bookings-by-date'),
    path('api/v1/admin/bookings/verification/', VerificationBookingsView.as_view(), name='verification-bookings'),
    path('api/v1/admin/bookings/verification/<str:date>/', VerificationBookingsByDateView.as_view(),
         name='verification-bookings-by-date'),
]
