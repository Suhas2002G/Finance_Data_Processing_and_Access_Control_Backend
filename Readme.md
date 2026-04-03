# Finance Data Processing and Access Control

Backend assignment submission for a finance dashboard system with role-based access control, financial record management, and summary analytics.

## Overview

This project is built with FastAPI and SQLite. It focuses on:

- user creation and authentication
- role-based access control for `viewer`, `analyst`, and `admin`
- financial transaction CRUD with filtering and pagination
- dashboard summary APIs for totals, recent activity, category totals, and monthly trends
- admin user management for role assignment and active/inactive status
- input validation, consistent API responses, and rate limiting

## Tech Stack

- Python 3.12
- FastAPI
- SQLAlchemy
- SQLite
- Pydantic
- JWT via `python-jose`
- Passlib + bcrypt
- SlowAPI for rate limiting
- Loguru for application logging

## Project Structure

```text
Finance Data Processing/
├── core/                  # configuration, database setup, dependencies
├── docs/                  # assignment reference material
├── models/                # SQLAlchemy models and Pydantic schemas
├── routes/                # auth, users, finance, dashboard endpoints
├── services/              # security and rate limiting helpers
├── utils/                 # roles, logging, response helpers
├── .env.example
├── finance.db             # SQLite database file
├── main.py                # FastAPI application entry point
├── pyproject.toml
├── requirements.txt
└── Readme.md
```

## Role Model

- `viewer`
  Can read dashboard summaries only.
- `analyst`
  Can read financial records and dashboard summaries.
- `admin`
  Can manage users and perform full transaction CRUD in addition to read access.

Permission checks are enforced in `core/deps.py` using dependency-based guards.

## Authentication

Authentication uses access and refresh JWT tokens stored in HTTP-only cookies.

Available endpoints:

- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/refresh`
- `POST /auth/logout`

Notes:

- public registration creates an `analyst` user by default
- inactive users cannot log in
- local development cookie settings use `secure=False`

## User Management APIs

Base path: `/users`

- `GET /users/me`
  Returns the currently authenticated user.
- `GET /users`
  Admin only. Supports `role`, `is_active`, `skip`, and `limit`.
- `GET /users/{user_id}`
  Admin only.
- `POST /users`
  Admin only. Create a user with explicit role and active status.
- `PATCH /users/{user_id}`
  Admin only. Update name, role, password, and active status.

Guardrails:

- admins cannot deactivate themselves
- admins cannot remove their own admin role

## Financial Record APIs

Base path: `/finance`

- `GET /finance/transactions`
- `GET /finance/transactions/{transaction_id}`
- `POST /finance/transactions`
- `PUT /finance/transactions/{transaction_id}`
- `DELETE /finance/transactions/{transaction_id}`

Supported filters on `GET /finance/transactions`:

- `category`
- `transaction_type`
- `start_date`
- `end_date`
- `skip`
- `limit`

Transaction fields:

- `amount`
- `type` (`income` or `expense`)
- `category`
- `note`
- `date`

## Dashboard API

Base path: `/dashboard`

- `GET /dashboard/`

Supported filters:

- `start_date`
- `end_date`

Returned summary data includes:

- total income
- total expenses
- net balance
- category-wise totals
- recent activity
- monthly trends

## Data Model

### User

- `id`
- `name`
- `email`
- `password_hash`
- `role`
- `is_active`
- `created_at`

### Transaction

- `id`
- `user_id`
- `amount`
- `type`
- `category`
- `note`
- `date`
- `created_at`

## Setup

1. Create and activate a virtual environment.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

2. Install dependencies.

```powershell
pip install -r requirements.txt
```

3. Create `.env` from `.env.example`.

Example:

```env
SECRET_KEY=your_access_secret
REFRESH_SECRET_KEY=your_refresh_secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
FRONTEND_URL=http://localhost:5173
```

4. Start the server.

```powershell
uvicorn main:app --reload
```

5. Open Swagger UI.

```text
http://127.0.0.1:8000/docs
```

## Example Workflow

1. Register a user with `POST /auth/register`.
2. Promote that user to `admin` using `PATCH /users/{user_id}` or by updating the seeded database once for local demo.
3. Log in with `POST /auth/login`.
4. Create users or update their roles/status through `/users`.
5. Create transactions through `/finance/transactions`.
6. Review filtered records through `GET /finance/transactions`.
7. Inspect aggregated metrics through `GET /dashboard/`.

## Validation and Error Handling

The backend demonstrates:

- schema validation through Pydantic
- permission enforcement through FastAPI dependencies
- role validation through enums
- `401`, `403`, `404`, `422`, and `429` responses where applicable
- rollback on database write failures in mutating endpoints

## Persistence

SQLite is used for persistence to keep local setup simple and fast for evaluation. Tables are created from SQLAlchemy metadata when the application starts.

Database file:

- `finance.db`

## Assumptions and Tradeoffs

- This is an assessment-focused backend, not a production deployment.
- SQLite was chosen for simplicity over multi-user production concerns.
- Authentication is cookie-based because it is easy to demo with Swagger and browser clients.
- Public registration defaults to `analyst`; admin-level user creation is available separately.
- There is no separate migration tool in this submission; schema creation is metadata-driven.

## Possible Extensions

- automated tests with `pytest` and FastAPI `TestClient`
- token revocation / blacklist support
- soft delete for transactions
- search support across notes and categories
- richer audit logging
