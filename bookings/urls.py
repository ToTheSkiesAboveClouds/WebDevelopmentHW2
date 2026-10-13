from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("rooms", views.RoomViewSet)
router.register("bookings", views.BookingViewSet)

urlpatterns = [
    path("health/", views.health),
    path("api/", include(router.urls)),
]
