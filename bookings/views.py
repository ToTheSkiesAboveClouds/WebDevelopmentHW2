from datetime import datetime, time, timedelta

from django.db import connection
from django.http import JsonResponse
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Booking, Room
from .serializers import BookingSerializer, RoomSerializer


def health(request):
    """Проверка, что бэкенд жив и видит базу."""
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
    return JsonResponse({"status": "ok", "rooms": Room.objects.count(), "bookings": Booking.objects.count()})


class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer

    @action(detail=True, methods=["get"])
    def availability(self, request, pk=None):
        """GET /api/rooms/<id>/availability/?date=YYYY-MM-DD
        Возвращает занятые и свободные слоты комнаты на день (рабочие часы 09:00-18:00)."""
        room = self.get_object()
        date_str = request.query_params.get("date")
        try:
            day = datetime.strptime(date_str, "%Y-%m-%d").date() if date_str else timezone.localdate()
        except ValueError:
            return Response({"detail": "date must be YYYY-MM-DD"}, status=400)

        tz = timezone.get_current_timezone()
        day_start = timezone.make_aware(datetime.combine(day, time(9, 0)), tz)
        day_end = timezone.make_aware(datetime.combine(day, time(18, 0)), tz)

        bookings = room.bookings.filter(start__lt=day_end, end__gt=day_start).order_by("start")
        busy = [
            {"start": b.start.astimezone(tz).isoformat(), "end": b.end.astimezone(tz).isoformat(), "title": b.title}
            for b in bookings
        ]

        free, cursor = [], day_start
        for b in bookings:
            if b.start > cursor:
                free.append({"start": cursor.isoformat(), "end": b.start.astimezone(tz).isoformat()})
            cursor = max(cursor, b.end.astimezone(tz))
        if cursor < day_end:
            free.append({"start": cursor.isoformat(), "end": day_end.isoformat()})

        return Response({"room": room.name, "date": day.isoformat(), "busy": busy, "free": free})


class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.select_related("room").all()
    serializer_class = BookingSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        room = self.request.query_params.get("room")
        booked_by = self.request.query_params.get("booked_by")
        if room:
            qs = qs.filter(room_id=room)
        if booked_by:
            qs = qs.filter(booked_by__iexact=booked_by)
        return qs
