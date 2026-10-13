# Room Booking API

Сервис бронирования переговорок: Django REST Framework + PostgreSQL, всё запускается через Docker Compose.
Главная фишка: API не даёт забронировать комнату на пересекающееся время и умеет показывать свободные слоты на день.

## Запуск

```bash
cp .env.example .env     # впиши свои SECRET_KEY и POSTGRES_PASSWORD
docker compose up --build
```

API: http://localhost:8000/api/ (в браузере открывается DRF browsable API).
При старте backend сам применяет миграции и создаёт 4 тестовые переговорки.

## Эндпоинты

| Метод | URL | Описание |
|---|---|---|
| GET | `/health/` | проверка бэкенда и БД |
| GET/POST | `/api/rooms/` | список / создание комнат |
| GET | `/api/rooms/<id>/availability/?date=YYYY-MM-DD` | занятые и свободные слоты (09:00-18:00) |
| GET/POST | `/api/bookings/` | список (фильтры `?room=`, `?booked_by=`) / создание брони |
| GET/PUT/PATCH/DELETE | `/api/bookings/<id>/` | одна бронь |

Пример:

```bash
curl -X POST localhost:8000/api/bookings/ -H "Content-Type: application/json" \
  -d '{"room":2,"booked_by":"damir","title":"Sprint","start":"2026-10-20T10:00:00+05:00","end":"2026-10-20T11:00:00+05:00"}'
```

Повторная бронь на пересекающееся время вернёт `400`. Бронь «встык» (одна кончается в 11:00, другая начинается в 11:00) разрешена.

## Проверка сохранности данных

```bash
docker compose down      # контейнеры удалены, том pgdata остался
docker compose up        # данные на месте: GET /api/bookings/
docker compose down -v   # а вот так том удаляется вместе с данными
```

## Структура Docker

- `db`: `postgres:16-alpine`, данные в named volume `pgdata`, healthcheck через `pg_isready`.
- `backend`: собирается из `Dockerfile`, стартует только когда БД healthy (`depends_on: condition: service_healthy`).
- Общая сеть `backend-net`, бэкенд обращается к БД по имени сервиса `db`.
- Порт БД наружу не публикуется, наружу открыт только бэкенд (`APP_PORT`).
- Секреты только в `.env` (в `.gitignore`), шаблон в `.env.example`.

## Тесты

```bash
SECRET_KEY=x DB_ENGINE=django.db.backends.sqlite3 POSTGRES_DB=test.sqlite3 python manage.py test
```
