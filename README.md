# Medicalka

A blog-style API (posts, comments, likes, authentication) built with **FastAPI + Celery**, using **PostgreSQL** as the database, **Redis** as the broker, and a **Vue 3 (Vite)** frontend.

## Running locally

Only Docker is required. All environment variables are already defined in `docker-compose.yml`, so no `.env` file is needed.

```bash
docker compose up -d --build
```

On the first start the tests (`pytest`) run first, and only then the API comes up. Once running:

| Service         | URL / port                       |
|-----------------|----------------------------------|
| Frontend        | http://localhost:5173            |
| API             | http://localhost:8000            |
| **Swagger UI**  | http://localhost:8000/docs       |
| OpenAPI JSON    | http://localhost:8000/openapi.json |
| PostgreSQL      | localhost:15432                  |
| Redis           | localhost:16379                  |

Stop: `docker compose down` (to also wipe the database: `docker compose down -v`).

## API — endpoints

Full reference and an interactive playground are available in Swagger: **http://localhost:8000/docs**

| Method | Path                                   | Access           |
|--------|----------------------------------------|------------------|
| POST   | `/auth/register`                       | public           |
| GET    | `/auth/verify-email?token=...`         | public           |
| POST   | `/auth/login`                          | public           |
| POST   | `/auth/refresh`                        | public           |
| GET    | `/auth/me`                             | authenticated    |
| PATCH  | `/users/me`                            | authenticated    |
| GET    | `/posts`                               | public           |
| POST   | `/posts`                               | verified user    |
| GET    | `/posts/{id}`                          | public           |
| PATCH  | `/posts/{id}`                          | author           |
| DELETE | `/posts/{id}`                          | author           |
| GET    | `/posts/{id}/comments`                 | public           |
| POST   | `/posts/{id}/comments`                 | verified user    |
| DELETE | `/posts/{id}/comments/{comment_id}`    | author           |
| POST   | `/posts/{id}/like`                     | authenticated    |
| DELETE | `/posts/{id}/like`                     | authenticated    |

### Example requests

**1. Register** (the response contains a `verification_token` — the email verification link):

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","username":"user1","full_name":"John Doe","password":"secret123"}'
```

**2. Verify email** — open the `verification_token` link from the response (a GET request).

**3. Log in** → returns `access_token` and `refresh_token`:

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username_or_email":"user1","password":"secret123"}'
```

**4. Create a post** (requires `access_token`):

```bash
curl -X POST http://localhost:8000/posts \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"title":"First post","content":"Post body"}'
```

**5. List posts** (public, with pagination and search):

```bash
curl "http://localhost:8000/posts?page=1&page_size=20&search=post"
```

## Project structure

```
.
├── docker-compose.yml        # all services: API, worker, beat, DB, redis, frontend
├── backend/                  # FastAPI + Celery
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app/
│   │   ├── main.py           # FastAPI entry point, router registration
│   │   ├── config.py         # config loaded from environment variables
│   │   ├── celery_app.py     # Celery setup
│   │   ├── tasks.py          # background tasks (worker/beat)
│   │   ├── routers/          # HTTP endpoints (auth, posts, comments, likes)
│   │   ├── services/         # business logic
│   │   ├── repositories/     # database access
│   │   ├── models/           # SQLAlchemy models
│   │   ├── schemas/          # Pydantic schemas (request/response validation)
│   │   ├── db/               # database connection
│   │   └── alembic/          # migrations
│   └── tests/                # tests (pytest)
└── frontend/                 # Vue 3 + Vite, served via nginx
    ├── Dockerfile
    └── src/                  # views, components, stores, router, api
```

**Background services:** `medicalka_worker` (Celery worker) and `medicalka_beat` (scheduler) — they periodically clean up unverified users.
