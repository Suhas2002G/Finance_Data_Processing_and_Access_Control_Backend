# Finance Data Processing and Access Control

Backend-focused assignment project for a finance dashboard system with role-based access control, transaction management, and summary analytics.

## Overview

This project implements the backend for a finance dashboard where different users interact with financial data based on role.

The system currently provides:

- User registration and login
- Cookie-based JWT authentication
- Role-based access control for `viewer`, `analyst`, and `admin`
- Financial transaction CRUD APIs
- Transaction filtering and pagination
- Dashboard summary APIs for totals, category breakdown, recent activity, and monthly trends
- SQLite-based persistence using SQLAlchemy
- Rate limiting on API endpoints

The frontend folder is present as a Vite + React scaffold, but this submission is primarily backend-focused.

## Tech Stack

- Backend: FastAPI
- Database: SQLite
- ORM: SQLAlchemy
- Auth: JWT access and refresh tokens stored in HTTP-only cookies
- Validation: Pydantic
- Rate limiting: SlowAPI
- Logging: Loguru
- Frontend scaffold: React + Vite

## Project Structure

```text
Finance Data Processing/
├── backend/
│   ├── core/                 # app config, DB session, dependencies
│   ├── models/               # SQLAlchemy models and Pydantic schemas
│   ├── routes/               # auth, users, finance, dashboard routes
│   ├── services/             # security and rate limiting
│   ├── utils/                # roles, response helpers, logger
│   ├── main.py               # FastAPI app entry point
│   └── finance.db            # SQLite database
├── frontend/                 # React/Vite scaffold
├── docs/
└── Readme.md
```

## Role Model

The project uses three roles:

- `viewer`: can view dashboard summary data only
- `analyst`: can view transactions and dashboard summary data
- `admin`: full access to transactions and user-management related actions

Permission mapping is defined in [roles.py](/F:/Finance%20Data%20Processing/backend/utils/roles.py).

## Features

### Authentication

- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/refresh`
- `POST /auth/logout`

Authentication uses JWT tokens stored in cookies:

- `access_token`
- `refresh_token`

### Transaction APIs

Base path: `/finance`

- `GET /finance/transactions`
- `GET /finance/transactions/{transaction_id}`
- `POST /finance/transactions`
- `PUT /finance/transactions/{transaction_id}`
- `DELETE /finance/transactions/{transaction_id}`

Supported filters for `GET /finance/transactions`:

- `category`
- `type`
- `start_date`
- `end_date`
- `skip`
- `limit`

### Dashboard API

Base path: `/dashboard`

- `GET /dashboard/`

The dashboard summary includes:

- total income
- total expenses
- net balance
- category-wise totals
- recent activity
- monthly trends

Optional filters:

- `start_date`
- `end_date`

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
- `type` (`income` or `expense`)
- `category`
- `note`
- `date`
- `created_at`

## Setup Instructions

## Prerequisites

- Python 3.12+
- Node.js 18+ if you want to run the frontend scaffold

## Backend Setup

1. Move into the backend folder.

```powershell
cd backend
```

2. Create and activate a virtual environment.

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

3. Install dependencies.

```powershell
pip install -r requirements.txt
```

4. Create a `.env` file in `backend/`.

Example:

```env
SECRET_KEY=your_access_secret
REFRESH_SECRET_KEY=your_refresh_secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
FRONTEND_URL=http://localhost:5173
```

5. Start the backend server.

```powershell
uvicorn main:app --reload
```

Backend will run at:

```text
http://127.0.0.1:8000
```

Swagger docs:

```text
http://127.0.0.1:8000/docs
```

## Frontend Setup

The frontend is currently a scaffold and not the primary focus of this assignment, but it can still be started.

1. Move into the frontend folder.

```powershell
cd frontend
```

2. Install dependencies.

```powershell
npm install
```

3. Start the development server.

```powershell
npm run dev
```

## Validation and Error Handling

The backend includes:

- Pydantic validation for auth and transaction payloads
- permission checks at the dependency layer
- consistent success/error response wrappers
- HTTP status codes for invalid authentication, missing records, forbidden actions, and server errors

## Persistence

The project uses SQLite for simplicity. Tables are created automatically on application startup through SQLAlchemy metadata.

Database file:

- `backend/finance.db`

## Current Status

Implemented:

- auth flow
- role model and permission checks
- transaction CRUD with filters
- dashboard analytics
- SQLite persistence
- rate limiting

Still minimal or pending:

- user management endpoints are placeholder-level
- frontend app is still a scaffold
- automated tests are not yet included
- deployment configuration is not included

## Assumptions

- This project is intended for assessment and local development, not production deployment.
- Cookie settings currently use `secure=False` for local development.
- SQLite is used to keep setup simple and fast for evaluation.
- Role enforcement is done at the backend level using dependency-based permission checks.

## Suggested Demo Flow

1. Register a user through `POST /auth/register`.
2. Update that user in the database to an `admin` role for full access.
3. Log in through `POST /auth/login`.
4. Create several transactions through `POST /finance/transactions`.
5. Fetch filtered records through `GET /finance/transactions`.
6. Open `GET /dashboard/` to inspect summary metrics.

## Notes

- The root assignment was backend-oriented, so the backend is the main deliverable.
- The frontend directory is included for completeness but is not yet connected to the APIs.
