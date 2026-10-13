from django.db import migrations

ROOMS = [
    ("Alatau", 4, 1, False),
    ("Medeu", 8, 2, True),
    ("Charyn", 12, 2, True),
    ("Kok-Tobe", 20, 3, True),
]


def seed(apps, schema_editor):
    Room = apps.get_model("bookings", "Room")
    for name, capacity, floor, projector in ROOMS:
        Room.objects.get_or_create(
            name=name, defaults={"capacity": capacity, "floor": floor, "has_projector": projector}
        )


def unseed(apps, schema_editor):
    apps.get_model("bookings", "Room").objects.filter(name__in=[r[0] for r in ROOMS]).delete()


class Migration(migrations.Migration):
    dependencies = [("bookings", "0001_initial")]
    operations = [migrations.RunPython(seed, unseed)]
