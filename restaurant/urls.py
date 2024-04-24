"""
URL configuration for restaurant project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from rest_framework import routers
from rest_framework_simplejwt.views import TokenRefreshView

from backend_drf import views
from backend_drf.views import CreateBookingView, ModerationView, ManualModerationView, AutoModerationView, \
    get_table_info
from django.urls import path, include

router = routers.DefaultRouter()
router.register(r'bookings', CreateBookingView)

urlpatterns = [
    path('admin/', admin.site.urls),

    #Authentication
    path('api/v1/token/', views.MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/v1/registration/', views.RegisterView.as_view(), name='auth_register'),

    # Profile
    path('api/v1/me/profile/', views.getProfile, name='profile'),
    path('api/v1/me/profile/update/', views.updateProfile, name='update-profile'),
    path('api/v1/me/profile/update-password/', views.updatePassword, name='update-password'),

    # Table
    path('api/v1/tables/', views.TablesView.as_view(), name='get-tables'),
    path('api/v1/tables/<int:table_id>/<str:date>/', get_table_info, name='get_table_info'),

    # Booking
    path('api/v1/', include(router.urls)),

    # Administator
    path('api/v1/moderation/', ModerationView.as_view(), name='moderation'),
    path('api/v1/admin/manual-moderation/', ManualModerationView.as_view(), name='manual_moderation'),
    path('api/v1/admin/auto-moderation/', AutoModerationView.as_view(), name='auto_moderation'),
]
