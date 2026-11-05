# ShopEase – Authentication Microservice

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-4479A1.svg?style=flat&logo=mysql&logoColor=white)](https://www.mysql.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?style=flat&logo=docker&logoColor=white)](https://www.docker.com/)
[![JWT](https://img.shields.io/badge/JWT-Secure_Tokens-000000.svg?style=flat&logo=jsonwebtokens&logoColor=white)](https://jwt.io/)

An independent, production-grade **Authentication Microservice** for the **ShopEase Microservices-Based E-Commerce Management System**. Built with **FastAPI**, **SQLAlchemy ORM**, **Alembic**, **PyJWT**, **Bcrypt**, and **Docker Compose**, this service provides user registration, login, JWT token issuance & verification, password hashing, and role-based profile management.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Objective](#objective)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Database Schema (`users` Table)](#database-schema-users-table)
- [REST API Endpoints Specification](#rest-api-endpoints-specification)
  - [Example Request & Response Payloads](#example-request--response-payloads)
- [Default Seed Credentials](#default-seed-credentials)
- [Local Setup & Execution](#local-setup--execution)
- [Alembic Database Migrations](#alembic-database-migrations)
- [Docker & Docker Compose Deployment](#docker--docker-compose-deployment)
- [Automated API Testing (14/14 Scenarios)](#automated-api-testing-1414-scenarios)

---

## Project Overview

In a microservices architecture, user authentication must be centralized and decentralized in validation. The **ShopEase Auth Service** issues tamper-proof, cryptographically signed JSON Web Tokens (JWT) containing user claims (User ID, Email, Role) that allow other microservices (Product Service, Order Service, Cart Service) to verify authenticated users statelessly without querying the database for every request.

---

## Objective

- Provide user registration with email uniqueness, format validation, and password confirmation.
- Store passwords strictly as salted **Bcrypt** hashes.
- Authenticate credentials and issue standard **Bearer JWT access tokens**.
- Provide protected profile retrieval (`/api/auth/me`) and token verification (`/api/auth/verify-token`).
- Allow authenticated users to change passwords securely.
- Deploy via **Docker Compose** alongside an isolated **MySQL 8.0** container with health checks and persistent volume storage.

---

## Technology Stack

| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **Framework** | FastAPI | High-performance asynchronous REST API framework |
| **Language** | Python 3.11+ | Modern Python runtime |
| **Database** | MySQL 8.0 / SQLite | Relational database (with SQLite local fallback) |
| **ORM** | SQLAlchemy 2.0 | Object-Relational Mapping & session management |
| **Migrations** | Alembic | Database schema version control & migrations |
| **Tokens** | PyJWT | Cryptographic JWT access token signing & decoding |
| **Hashing** | Bcrypt / Passlib | Industrial-strength 12-round salted password hashing |
| **Validation** | Pydantic v2 | Strict request validation & serialization |
| **Container** | Docker & Compose | Multi-container orchestration & networking |

---

## Project Structure

```text
shopease-auth-service/
│
├── app/
│   ├── main.py                     # FastAPI application entry point & lifecycle
│   ├── core/
│   │   ├── config.py               # Environment configuration settings
│   │   └── security.py             # Bcrypt hashing & PyJWT token utilities
│   ├── database/
│   │   └── connection.py           # SQLAlchemy engine & session dependency
│   ├── models/
│   │   └── user_model.py           # SQLAlchemy User model (users table)
│   ├── routers/
│   │   └── auth_routes.py          # Auth REST API endpoints (/api/auth)
│   ├── schemas/
│   │   └── auth_schema.py          # Pydantic request & response validation schemas
│   └── services/
│       └── auth_service.py         # Business logic for registration & auth
│
├── alembic/
│   ├── env.py                      # Alembic migration environment
│   ├── script.py.mako              # Migration script template
│   └── versions/
│       └── 001_initial_auth_tables.py  # Initial migration for users table
│
├── tests/
│   └── test_auth.py                # Pytest integration tests
│
├── alembic.ini                     # Alembic configuration
├── Dockerfile                      # Microservice Docker build definition
├── docker-compose.yml              # Multi-container orchestration (Auth + MySQL 8)
├── requirements.txt                # Python package dependencies
├── .env                            # Environment variables (configured with pasu/pasupathi@123)
├── .dockerignore                   # Docker build context exclusions
├── .gitignore                      # Git repository exclusions
├── test_auth_service.py            # Automated 14-scenario test suite
├── test_live_auth_server.py        # Live server runner and endpoint tester
└── README.md                       # Comprehensive documentation
```

---

## Database Schema (`users` Table)

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | Primary Key, Auto-increment | Unique user identifier |
| `full_name` | `VARCHAR(100)` | NOT NULL | User's full name |
| `email` | `VARCHAR(150)` | UNIQUE, NOT NULL, INDEX | Unique login email address |
| `password_hash`| `VARCHAR(255)` | NOT NULL | 12-round salted Bcrypt hash |
| `role` | `VARCHAR(50)` | NOT NULL, DEFAULT 'customer' | Authorization role (`customer`, `admin`) |
| `is_active` | `BOOLEAN` | NOT NULL, DEFAULT TRUE | Account active/disabled status |
| `created_at` | `DATETIME` | NOT NULL, DEFAULT NOW() | Account creation timestamp |
| `updated_at` | `DATETIME` | NOT NULL, DEFAULT NOW() | Last update timestamp |

---

## REST API Endpoints Specification

Base URL: `http://localhost:8001/api/auth`

| HTTP Method | Endpoint | Description | Auth Required | Status Code |
| :--- | :--- | :--- | :---: | :--- |
| `POST` | `/api/auth/register` | Register a new user | No | `201 Created` / `400` / `422` |
| `POST` | `/api/auth/login` | Authenticate user & issue JWT | No | `200 OK` / `401` / `403` |
| `GET` | `/api/auth/me` | Retrieve authenticated user profile | **Yes (Bearer)** | `200 OK` / `401` / `403` |
| `POST` | `/api/auth/verify-token` | Validate JWT token & inspect claims | No | `200 OK` |
| `POST` | `/api/auth/change-password`| Change current user password | **Yes (Bearer)** | `200 OK` / `400` / `401` |
| `GET` | `/health` | Microservice health check | No | `200 OK` |

---

### Example Request & Response Payloads

#### 1. User Registration (`POST /api/auth/register`)
**Request:**
```json
{
  "full_name": "Pasupathi",
  "email": "pasu@shopease.com",
  "password": "pasupathi@123",
  "confirm_password": "pasupathi@123"
}
```

**Response (`201 Created`):**
```json
{
  "message": "User registered successfully.",
  "user": {
    "id": 1,
    "full_name": "Pasupathi",
    "email": "pasu@shopease.com",
    "role": "customer",
    "is_active": true,
    "created_at": "2026-11-05T10:25:00.123456"
  }
}
```

#### 2. User Login (`POST /api/auth/login`)
**Request:**
```json
{
  "email": "pasu@shopease.com",
  "password": "pasupathi@123"
}
```

**Response (`200 OK`):**
```json
{
  "message": "Authentication successful.",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "full_name": "pasu",
    "email": "pasu@shopease.com",
    "role": "admin",
    "is_active": true,
    "created_at": "2026-11-05T10:25:00.123456"
  }
}
```

#### 3. Current User Profile (`GET /api/auth/me`)
**Header:**
```http
Authorization: Bearer <your_jwt_access_token>
```

**Response (`200 OK`):**
```json
{
  "id": 1,
  "full_name": "pasu",
  "email": "pasu@shopease.com",
  "role": "admin",
  "is_active": true,
  "created_at": "2026-11-05T10:25:00.123456"
}
```

---

## Default Seed Credentials

For evaluation and rapid testing, default credentials are automatically configured on startup:
- **Username / Full Name:** `pasu`
- **Email:** `pasu@shopease.com`
- **Password:** `pasupathi@123`
- **Role:** `admin`

---

## Local Setup & Execution

### 1. Navigate to Project
```bash
cd shopease-auth-service
```

### 2. Create Virtual Environment & Install Dependencies
```bash
python -m venv venv
venv\Scripts\activate       # Windows
# source venv/bin/activate  # Linux / macOS

pip install -r requirements.txt
```

### 3. Start the Authentication Service
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

### 4. Interactive API Documentation
- **Swagger UI:** [http://localhost:8001/docs](http://localhost:8001/docs)
- **ReDoc:** [http://localhost:8001/redoc](http://localhost:8001/redoc)

---

## Alembic Database Migrations

Apply database schema migrations using Alembic:
```bash
# Check current migration revision
alembic current

# Run migrations to latest revision
alembic upgrade head

# Rollback one migration if needed
alembic downgrade -1
```

---

## Docker & Docker Compose Deployment

Run the complete multi-container setup (FastAPI Auth Service + MySQL 8.0):

```bash
# Build and start all services in detached mode
docker-compose up -d --build

# Inspect container status
docker-compose ps

# View live service logs
docker-compose logs -f auth-service

# Stop services
docker-compose down
```

---

## Automated API Testing (14/14 Scenarios)

Execute the comprehensive automated test suite verifying all 14 mandatory scenarios:

```bash
python test_auth_service.py
```

### Test Scenarios Verification Matrix

| # | Test Scenario | Expected Result | Status |
| :-: | :--- | :--- | :-: |
| 1 | Register new user with valid details | HTTP `201 Created` with hashed password | ✅ Passed |
| 2 | Register with already existing email | HTTP `400 Bad Request` duplicate error | ✅ Passed |
| 3 | Register with invalid email format | HTTP `422 Unprocessable Entity` | ✅ Passed |
| 4 | Register with mismatched passwords | HTTP `422 Unprocessable Entity` | ✅ Passed |
| 5 | Login using valid credentials | HTTP `200 OK` with valid signed JWT | ✅ Passed |
| 6 | Login using incorrect password | HTTP `401 Unauthorized` | ✅ Passed |
| 7 | Login using an inactive account | HTTP `403 Forbidden` | ✅ Passed |
| 8 | Access `/api/auth/me` with valid token | HTTP `200 OK` returning profile | ✅ Passed |
| 9 | Access protected endpoint without token | HTTP `401 Unauthorized` | ✅ Passed |
| 10 | Access protected endpoint with invalid token | HTTP `401 Unauthorized` invalid signature | ✅ Passed |
| 11 | Access protected endpoint with expired token | HTTP `401 Unauthorized` token expired | ✅ Passed |
| 12 | Change password using correct current password | HTTP `200 OK` password updated | ✅ Passed |
| 13 | Change password using incorrect current password| HTTP `400 Bad Request` | ✅ Passed |
| 14 | Verify new password works for subsequent login | HTTP `200 OK` successful login | ✅ Passed |
