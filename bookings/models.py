from django.db import models


class Room(models.Model):
    name = models.CharField(max_length=100, unique=True)
    capacity = models.PositiveIntegerField()
    floor = models.PositiveIntegerField(default=1)
    has_projector = models.BooleanField(default=False)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name} (capacity {self.capacity})"


class Booking(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="bookings")
    booked_by = models.CharField(max_length=100)
    title = models.CharField(max_length=200)
    start = models.DateTimeField()
    end = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["start"]
        indexes = [models.Index(fields=["room", "start", "end"])]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(end__gt=models.F("start")),
                name="booking_end_after_start",
            )
        ]

    def __str__(self):
        return f"{self.room.name}: {self.title} ({self.start:%Y-%m-%d %H:%M}-{self.end:%H:%M})"
