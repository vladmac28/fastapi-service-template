# fastapi-service-template

Production-style каркас: FastAPI + Postgres + Redis + Alembic + Docker Compose.

## Запуск
1) Создай `.env` из примера:
```bash
cp .env.example .env
```

2) Подними сервисы:
```bash
make up
```

Открой:
- API: http://localhost:8000
- Swagger: http://localhost:8000/docs
- Health: http://localhost:8000/api/v1/health

## Быстрая проверка auth
```bash
# register
curl -s -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'

# login -> token
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}' | python -c "import sys,json;print(json.load(sys.stdin)['access_token'])")

# me
curl -s http://localhost:8000/api/v1/auth/me -H "Authorization: Bearer $TOKEN"
```

## Команды
```bash
make up       # поднять
make down     # остановить
make logs     # логи приложения
make psql     # psql внутрь базы
```

## Что есть
- Асинхронный SQLAlchemy engine + сессии
- Alembic миграции (создаёт таблицу users)
- JWT auth: register/login/me
- Redis rate limiting (fixed window per IP)
- request-id middleware (X-Request-ID)
- Единый формат ошибок: `{"error": {...}, "request_id": "..."}`
