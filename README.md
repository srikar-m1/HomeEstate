# HomeEstate

HomeEstate is a Django REST Framework property marketplace with account verification, searchable listings, favorites, buyer inquiries, background email delivery, API documentation, and production-ready configuration.

## Highlights

- Property CRUD with owner-only editing
- Search and filters for city, listing type, property type, and price range
- Favorites and inquiry workflows
- Celery background email with Redis support
- PostgreSQL in production and SQLite for local tests
- OpenAPI schema and Swagger UI
- Docker Compose services for Django, PostgreSQL, Redis, and Celery
- GitHub Actions checks for migrations, Django validation, and tests

## Local setup

```bash
cp .env.example .env
docker compose up --build
```

The application is available at `http://localhost:8000` and API documentation at `http://localhost:8000/api/docs/`.

For a lightweight local run without Docker:

```bash
cd HomeEstate
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Main endpoints

- `GET/POST /api/properties/`
- `GET/PATCH/DELETE /api/properties/<id>/`
- `GET /api/favorites/`
- `POST/DELETE /api/favorites/<property_id>/`
- `GET/POST /api/inquiries/`
- `GET /api/schema/`
- `GET /api/docs/`

Create an account through `/accounts/api/register/`, verify the email, and sign in through `/accounts/api/login/` to receive a Knox token for authenticated API requests.
