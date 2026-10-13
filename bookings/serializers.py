from django.utils import timezone
from rest_framework import serializers

from .models import Booking, Room


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ["id", "name", "capacity", "floor", "has_projector"]


class BookingSerializer(serializers.ModelSerializer):
    room_name = serializers.CharField(source="room.name", read_only=True)

    class Meta:
        model = Booking
        fields = ["id", "room", "room_name", "booked_by", "title", "start", "end", "created_at"]
        read_only_fields = ["created_at"]

    def validate(self, attrs):
        start = attrs.get("start", getattr(self.instance, "start", None))
        end = attrs.get("end", getattr(self.instance, "end", None))
        room = attrs.get("room", getattr(self.instance, "room", None))

        if start and end and end <= start:
            raise serializers.ValidationError({"end": "End must be after start."})

        if start and end and room:
            # Два интервала пересекаются, если start1 < end2 И end1 > start2.
            # Бронь "встык" (одна кончается, когда другая начинается) допустима.
            conflicts = Booking.objects.filter(room=room, start__lt=end, end__gt=start)
            if self.instance:
                conflicts = conflicts.exclude(pk=self.instance.pk)
            clash = conflicts.first()
            if clash:
                raise serializers.ValidationError(
                    {
                        "detail": (
                            f"Room '{room.name}' is already booked from "
                            f"{timezone.localtime(clash.start).isoformat()} to "
                            f"{timezone.localtime(clash.end).isoformat()} "
                            f"by {clash.booked_by}."
                        )
                    }
                )
        return attrs
