# Healthcare Backend (Django + DRF + PostgreSQL)

## Overview
- Django REST backend for a simple healthcare system.
- Supports user registration/login with JWT, and CRUD for Patients, Doctors, and Patient–Doctor mappings.
- Uses PostgreSQL as the database and environment variables for sensitive settings.

## Tech Stack
- `Django` (project: `healthcare_backend`, app: `api`)
- `Django REST Framework`
- `djangorestframework-simplejwt` for JWT auth
- `django-filter` for query filtering on mappings
- `psycopg2-binary` for PostgreSQL
- `python-dotenv` to load `.env`

## Configuration
Create a `.env` file in the project root:


`healthcare_backend/settings.py` loads this file with `load_dotenv()` and uses these values for `SECRET_KEY`, `DEBUG`, and `DATABASES`.

## Database (PostgreSQL via Docker)
Example setup used during development:

```bash
docker run --name healthcare-db -e POSTGRES_PASSWORD=test123 -p 5432:5432 -d postgres
# Inside container, once:
docker exec -it healthcare-db psql -U postgres -c "CREATE DATABASE healthcare_db;"
```

## Setup & Run
From the project root:

```bash
python -m venv venv
venv\Scripts\activate  # on Windows
pip install django djangorestframework djangorestframework-simplejwt django-filter python-dotenv psycopg2-binary
python manage.py migrate
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/`.

## Seeding Demo Data
A management command seeds demo users, doctors, patients, and appointments:

```bash
python manage.py seed_data
```

This creates:
- User: `demo` / `password123`
- 3 doctors
- 2 patients (owned by `demo`)
- Several appointment mappings

## Authentication Flow
1. **Register**
   - `POST /api/auth/register/`
   - Body: `{ "username": "demo", "email": "demo@example.com", "password": "password123" }`
2. **Login**
   - `POST /api/auth/login/`
   - Returns `{ access, refresh }` JWT tokens.
3. Use `Authorization: Bearer <access>` for all protected endpoints below.

## Main Endpoints

### Patients (authenticated)
- `POST /api/patients/` – create patient (scoped to current user)
- `GET /api/patients/` – list patients created by current user
- `GET /api/patients/<id>/` – retrieve patient
- `PUT /api/patients/<id>/` – update patient
- `DELETE /api/patients/<id>/` – delete patient

### Doctors (authenticated)
- `POST /api/doctors/` – create doctor
- `GET /api/doctors/` – list all doctors
- `GET /api/doctors/<id>/` – retrieve doctor
- `PUT /api/doctors/<id>/` – update doctor
- `DELETE /api/doctors/<id>/` – delete doctor

### Patient–Doctor Mappings (authenticated)
- `POST /api/mappings/` – assign doctor to patient
- `GET /api/mappings/` – list all mappings
- `GET /api/mappings/?patient=<patient_id>` – list mappings (doctors) for a specific patient
- `DELETE /api/mappings/<id>/` – remove a mapping

Mappings include extra read-only fields `patient_name` and `doctor_name` for convenience.

## Tests
Automated tests are in `api/tests.py` and cover:
- Auth registration and login (JWT tokens)
- Patients: create/list/get/update/delete with user scoping
- Doctors: create/list/get/update/delete
- Mappings: create/list/filter-by-patient/delete
- `seed_data` command: verifies demo data is created

Run tests with:

```bash
python manage.py test api
```

## Postman Collection
A ready-made Postman collection is included:
- File: `healthcare_backend_postman_collection.json`

Import it into Postman (Import → File) and set the `token` variable to your JWT access token after logging in.
