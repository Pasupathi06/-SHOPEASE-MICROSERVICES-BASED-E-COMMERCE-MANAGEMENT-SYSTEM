# ShopEase – User Management Microservice

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-4479A1.svg?style=flat&logo=mysql&logoColor=white)](https://www.mysql.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?style=flat&logo=docker&logoColor=white)](https://www.docker.com/)
[![JWT](https://img.shields.io/badge/JWT-Protected-000000.svg?style=flat&logo=jsonwebtokens&logoColor=white)](https://jwt.io/)

An independent, production-grade **User Management Microservice** for the **ShopEase Microservices-Based E-Commerce Management System**. Built with **FastAPI**, **SQLAlchemy ORM**, **Alembic**, and **Docker Compose**, this service manages customer profiles, contact info, and multiple delivery addresses with strict JWT authorization and a single default address constraint.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Objective](#objective)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Database Schema](#database-schema)
  - [1. User Profiles Table (`user_profiles`)](#1-user-profiles-table-user_profiles)
  - [2. User Addresses Table (`user_addresses`)](#2-user-addresses-table-user_addresses)
- [Authentication Service Integration](#authentication-service-integration)
- [REST API Endpoints Specification](#rest-api-endpoints-specification)
  - [Profile APIs](#user-profile-apis-apiusersprofile)
  - [Address APIs](#delivery-address-apis-apiusersaddresses)
- [Local Setup & Execution](#local-setup--execution)
- [Alembic Migrations](#alembic-migrations)
- [Docker & Docker Compose](#docker--docker-compose)
- [Automated Testing Results (16/16 Passed)](#automated-testing-results)

---

## Project Overview

In the ShopEase architecture, User Management is cleanly separated from Authentication:
- **Authentication Service (Port 8001):** Manages user credentials, password hashing, and issues JWT access tokens.
- **User Service (Port 8002):** Validates incoming JWT tokens, extracts the authenticated `auth_user_id`, and manages rich profile attributes and delivery addresses.

Users can **never** view, modify, or delete another customer's profile or delivery address.

---

## Technology Stack

| Layer | Technology | Purpose |
| :--- | :--- | :--- |
| **Framework** | FastAPI | High-performance asynchronous REST API framework |
| **Language** | Python 3.11+ | Modern Python runtime |
| **Database** | MySQL 8.0 / SQLite | Relational database (with SQLite local fallback) |
| **ORM** | SQLAlchemy 2.0 | Object-Relational Mapping & session management |
| **Migrations** | Alembic | Database schema version control & migrations |
| **Auth** | PyJWT | Stateless verification of JWT Bearer tokens |
| **Validation** | Pydantic v2 | Strict request validation & serialization |
| **Container** | Docker & Compose | Multi-container orchestration (App + MySQL 8) |

---

## Project Structure

```text
shopease-user-service/
│
├── app/
│   ├── main.py                     # Application entry point, routers & database lifecycle
│   ├── core/
│   │   ├── config.py               # Environment configuration settings
│   │   └── security.py             # JWT token verification & identity extraction
│   ├── database/
│   │   └── connection.py           # SQLAlchemy session management & connection pooling
│   ├── models/
│   │   ├── user_model.py           # SQLAlchemy UserProfile model (user_profiles table)
│   │   └── address_model.py        # SQLAlchemy Address model (user_addresses table)
│   ├── routers/
│   │   ├── user_routes.py          # Profile CRUD REST API endpoints (/api/users/profile)
│   │   └── address_routes.py       # Address CRUD REST API endpoints (/api/users/addresses)
│   ├── schemas/
│   │   ├── user_schema.py          # Pydantic profile validation schemas
│   │   └── address_schema.py       # Pydantic address validation schemas
│   └── services/
│       ├── user_service.py         # Business logic for profile operations
│       └── address_service.py      # Business logic for addresses & default flag logic
│
├── alembic/
│   ├── env.py                      # Alembic migration environment
│   ├── script.py.mako              # Migration template
│   └── versions/
│       └── 001_initial_user_tables.py  # Initial migration script
│
├── tests/
│   └── test_user.py                # Automated Pytest suite
│
├── alembic.ini                     # Alembic configuration
├── Dockerfile                      # Microservice Docker build definition (python:3.11-slim)
├── docker-compose.yml              # Multi-container setup (User Service + MySQL 8.0)
├── requirements.txt                # Dependencies (FastAPI, SQLAlchemy, PyJWT, etc.)
├── .env                            # Environment variables (configured with pasu / pasupathi@123)
├── .dockerignore                   # Build context exclusions
├── .gitignore                      # Git repository exclusions
├── run_server.bat                  # 1-Click Windows execution script
├── test_user_service.py            # 16/16 automated test suite runner
├── test_live_user_server.py        # Live server runner on Port 8002
└── README.md                       # Comprehensive documentation
```

---

## Database Schema

### 1. User Profiles Table (`user_profiles`)

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | Primary Key, Auto-increment | Unique profile identifier |
| `auth_user_id` | `INTEGER` | UNIQUE, NOT NULL, INDEX | Foreign reference to Auth Service user ID |
| `full_name` | `VARCHAR(100)` | NOT NULL | Customer name |
| `phone_number` | `VARCHAR(20)` | NULLABLE | Contact telephone |
| `date_of_birth`| `DATE` | NULLABLE | Birthdate |
| `gender` | `VARCHAR(20)` | NULLABLE | Gender |
| `profile_image`| `VARCHAR(255)` | NULLABLE | Avatar URL |
| `is_active` | `BOOLEAN` | NOT NULL, DEFAULT TRUE | Active account status |
| `created_at` | `DATETIME` | NOT NULL, DEFAULT NOW() | Profile creation timestamp |
| `updated_at` | `DATETIME` | NOT NULL, DEFAULT NOW() | Last update timestamp |

### 2. User Addresses Table (`user_addresses`)

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | Primary Key, Auto-increment | Unique address identifier |
| `user_id` | `INTEGER` | Foreign Key (`user_profiles.id`), INDEX | Reference to user profile |
| `address_type` | `VARCHAR(20)` | NOT NULL, DEFAULT 'Home' | Categorization (`Home`, `Office`, etc.) |
| `full_name` | `VARCHAR(100)` | NOT NULL | Delivery recipient name |
| `phone_number` | `VARCHAR(20)` | NOT NULL | Recipient phone number |
| `address_line_1`| `VARCHAR(255)`| NOT NULL | Address street / building |
| `address_line_2`| `VARCHAR(255)`| NULLABLE | Landmark or suite |
| `city` | `VARCHAR(100)` | NOT NULL | City |
| `state` | `VARCHAR(100)` | NOT NULL | State |
| `country` | `VARCHAR(100)` | NOT NULL, DEFAULT 'India' | Country |
| `postal_code` | `VARCHAR(20)` | NOT NULL | Postal PIN code |
| `is_default` | `BOOLEAN` | NOT NULL, DEFAULT FALSE | Default delivery address indicator |
| `created_at` | `DATETIME` | NOT NULL, DEFAULT NOW() | Address creation timestamp |

---

## Authentication Service Integration

- Every request to `/api/users/*` must supply a valid JWT access token:
  ```http
  Authorization: Bearer <jwt_access_token>
  ```
- The service decodes the token using the shared `JWT_SECRET_KEY` and extracts the subject claim `sub` as `auth_user_id`.
- Clients **cannot** supply a different user ID in the request body to access or manipulate records.
- Missing or expired tokens automatically return **HTTP 401 Unauthorized**.
- Attempts to query or update addresses belonging to another customer return **HTTP 403 Forbidden**.

---

## REST API Endpoints Specification

Base URL: `http://localhost:8002/api/users`

### User Profile APIs (`/api/users/profile`)

| HTTP Method | Endpoint | Description | Auth Required | Status Code |
| :--- | :--- | :--- | :---: | :--- |
| `POST` | `/api/users/profile` | Create customer profile | Yes | `201 Created` / `400` |
| `GET` | `/api/users/profile` | Get authenticated user profile | Yes | `200 OK` / `404` |
| `PUT` | `/api/users/profile` | Fully update profile | Yes | `200 OK` |
| `PATCH` | `/api/users/profile` | Partially update profile | Yes | `200 OK` |
| `DELETE` | `/api/users/profile` | Deactivate profile | Yes | `200 OK` |

### Delivery Address APIs (`/api/users/addresses`)

| HTTP Method | Endpoint | Description | Auth Required | Status Code |
| :--- | :--- | :--- | :---: | :--- |
| `POST` | `/api/users/addresses` | Add new delivery address | Yes | `201 Created` |
| `GET` | `/api/users/addresses` | List all saved addresses | Yes | `200 OK` |
| `GET` | `/api/users/addresses/{id}` | Get specific address by ID | Yes | `200 OK` / `403` / `404` |
| `PUT` | `/api/users/addresses/{id}` | Update address by ID | Yes | `200 OK` / `403` / `404` |
| `DELETE` | `/api/users/addresses/{id}` | Delete address by ID | Yes | `200 OK` / `403` / `404` |
| `PATCH` | `/api/users/addresses/{id}/default` | Set address as default | Yes | `200 OK` / `403` / `404` |

---

## Local Setup & Execution

```bash
cd shopease-user-service

# Create virtual environment & install dependencies
python -m venv venv
venv\Scripts\activate       # Windows
# source venv/bin/activate  # Linux / macOS

pip install -r requirements.txt

# Start User Service
python -m uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
```

Interactive Documentation:
- **Swagger UI:** [http://localhost:8002/docs](http://localhost:8002/docs)
- **ReDoc:** [http://localhost:8002/redoc](http://localhost:8002/redoc)

---

## Docker & Docker Compose

```bash
# Build and launch User Service + MySQL 8.0
docker-compose up -d --build

# View logs
docker-compose logs -f user-service

# Stop services
docker-compose down
```

---

## Automated Testing Results

Run the full automated test suite verifying all 16 scenarios:
```bash
python test_user_service.py
```

| # | Test Scenario | Status |
| :-: | :--- | :---: |
| 1 | Access profile API without token | ✅ Passed (401) |
| 2 | Access profile API using invalid token | ✅ Passed (401) |
| 3 | Create profile using valid token | ✅ Passed (201) |
| 4 | Create duplicate profile for same user | ✅ Passed (400) |
| 5 | Retrieve authenticated user's profile | ✅ Passed (200) |
| 6 | Update profile information | ✅ Passed (200) |
| 7 | Partially update profile information | ✅ Passed (200) |
| 8 | Add multiple delivery addresses | ✅ Passed (201) |
| 9 | Retrieve all saved addresses | ✅ Passed (200) |
| 10 | Update existing address | ✅ Passed (200) |
| 11 | Set a default address | ✅ Passed (200) |
| 12 | Verify single default address constraint | ✅ Passed (1 default) |
| 13 | Delete an address | ✅ Passed (200) |
| 14 | Attempt to access another user's profile | ✅ Passed (404) |
| 15 | Attempt to access another user's address | ✅ Passed (403 Forbidden) |
| 16 | Deactivate user profile | ✅ Passed (200) |
