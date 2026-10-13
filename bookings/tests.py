from rest_framework.test import APITestCase

from .models import Room


class BookingApiTests(APITestCase):
    def setUp(self):
        self.room = Room.objects.create(name="Test Room", capacity=4)

    def book(self, start, end, room=None, who="alice"):
        return self.client.post(
            "/api/bookings/",
            {
                "room": (room or self.room).id,
                "booked_by": who,
                "title": "Meeting",
                "start": start,
                "end": end,
            },
            format="json",
        )

    def test_create_and_read_back(self):
        r = self.book("2026-10-20T10:00:00+05:00", "2026-10-20T11:00:00+05:00")
        self.assertEqual(r.status_code, 201)
        r = self.client.get("/api/bookings/")
        self.assertEqual(r.json()["count"], 1)

    def test_overlap_rejected(self):
        self.book("2026-10-20T10:00:00+05:00", "2026-10-20T11:00:00+05:00")
        for start, end in [
            ("2026-10-20T10:30:00+05:00", "2026-10-20T11:30:00+05:00"),  # хвост
            ("2026-10-20T09:30:00+05:00", "2026-10-20T10:30:00+05:00"),  # голова
            ("2026-10-20T10:15:00+05:00", "2026-10-20T10:45:00+05:00"),  # внутри
            ("2026-10-20T09:00:00+05:00", "2026-10-20T12:00:00+05:00"),  # накрывает
        ]:
            self.assertEqual(self.book(start, end, who="bob").status_code, 400, (start, end))

    def test_back_to_back_allowed(self):
        self.book("2026-10-20T10:00:00+05:00", "2026-10-20T11:00:00+05:00")
        r = self.book("2026-10-20T11:00:00+05:00", "2026-10-20T12:00:00+05:00", who="bob")
        self.assertEqual(r.status_code, 201)

    def test_other_room_allowed(self):
        other = Room.objects.create(name="Other", capacity=2)
        self.book("2026-10-20T10:00:00+05:00", "2026-10-20T11:00:00+05:00")
        r = self.book("2026-10-20T10:00:00+05:00", "2026-10-20T11:00:00+05:00", room=other)
        self.assertEqual(r.status_code, 201)

    def test_end_before_start_rejected(self):
        r = self.book("2026-10-20T11:00:00+05:00", "2026-10-20T10:00:00+05:00")
        self.assertEqual(r.status_code, 400)

    def test_availability(self):
        self.book("2026-10-20T10:00:00+05:00", "2026-10-20T11:00:00+05:00")
        r = self.client.get(f"/api/rooms/{self.room.id}/availability/?date=2026-10-20")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.json()["busy"]), 1)
        self.assertEqual(len(r.json()["free"]), 2)

    def test_health(self):
        self.assertEqual(self.client.get("/health/").json()["status"], "ok")
