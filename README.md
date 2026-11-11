# ShopEase – Microservices-Based E-Commerce Management System

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?style=flat&logo=docker&logoColor=white)](https://www.docker.com/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-4479A1.svg?style=flat&logo=mysql&logoColor=white)](https://www.mysql.com/)
[![JWT](https://img.shields.io/badge/JWT-Secure_Tokens-000000.svg?style=flat&logo=jsonwebtokens&logoColor=white)](https://jwt.io/)

Welcome to the **ShopEase Microservices-Based E-Commerce Management System** repository. This platform consists of independent, containerized backend microservices built with Python and FastAPI following Clean Architecture, strict Pydantic validation, and modern DevOps container standards.

---

## Architecture Overview

```text
                               ┌────────────────────────────────────────────────────────┐
                               │                  API Gateway / Client                  │
                               └───────────────────────────┬────────────────────────────┘
                                                           │
                    ┌──────────────────────────────────────┼──────────────────────────────────────┐
                    │                                      │                                      │
                    ▼ (Port 8001)                          ▼ (Port 8002)                          ▼ (Port 8003)
 ┌─────────────────────────────────────┐┌─────────────────────────────────────┐┌─────────────────────────────────────┐
 │     shopease-auth-service           ││     shopease-user-service           ││     shopease-product-service        │
 │  (JWT Authentication & Security)    ││  (User Profiles & Delivery Addr)    ││      (Product Catalog & CRUD)       │
 ├─────────────────────────────────────┤├─────────────────────────────────────┤├─────────────────────────────────────┤
 │ • FastAPI + PyJWT + Bcrypt          ││ • FastAPI + SQLAlchemy ORM          ││ • FastAPI + Pydantic v2             │
 │ • MySQL 8.0 (shopease_auth_db)      ││ • MySQL 8.0 (shopease_user_db)      ││ • In-Memory Thread-Safe Store       │
 │ • User Registration & Login         ││ • Profile CRUD (/api/users/profile) ││ • Complete CRUD REST APIs           │
 │ • Bearer Token Issuance             ││ • Address Management (Single Def.)  ││ • Category Filtering & Pagination   │
 │ • Token Validation Endpoint         ││ • Ownership Protection via JWT      ││ • Port 8003                         │
 │ • Port 8001                         ││ • Port 8002                         ││ • Docker Container                  │
 └──────────────────┬──────────────────┘└──────────────────┬──────────────────┘└─────────────────────────────────────┘
                    │                                      │
                    ▼                                      ▼
 ┌─────────────────────────────────────┐┌─────────────────────────────────────┐
 │        MySQL 8.0 Auth DB            ││        MySQL 8.0 User DB            │
 │          (auth-db:3306)             ││          (user-db:3306)             │
 └─────────────────────────────────────┘└─────────────────────────────────────┘
```

---

## Repository Structure

```text
SHOPEASE-MICROSERVICES-BASED-E-COMMERCE-MANAGEMENT-SYSTEM/
│
├── shopease-auth-service/          # Microservice 1: JWT Authentication & User Credentials (Port 8001)
│   ├── app/                        # Routers, Core, Database, Models, Schemas, Services
│   ├── alembic/                    # Database Migration Scripts
│   ├── Dockerfile                  # Container build instructions
│   ├── docker-compose.yml          # Multi-container orchestration (Auth Service + MySQL 8.0)
│   ├── requirements.txt            # Python dependencies
│   ├── test_auth_service.py        # 14-scenario automated test runner
│   ├── run_server.bat              # 1-Click Windows execution script
│   └── README.md                   # Dedicated Authentication Service Documentation
│
├── shopease-user-service/          # Microservice 2: User Profiles & Delivery Addresses (Port 8002)
│   ├── app/                        # Routers (Profile & Address), Models, Schemas, Services
│   ├── alembic/                    # Database Migration Scripts
│   ├── Dockerfile                  # Container build instructions
│   ├── docker-compose.yml          # Multi-container orchestration (User Service + MySQL 8.0)
│   ├── requirements.txt            # Python dependencies
│   ├── test_user_service.py        # 16-scenario automated test runner
│   ├── run_server.bat              # 1-Click Windows execution script
│   └── README.md                   # Dedicated User Management Service Documentation
│
├── shopease-product-service/       # Microservice 3: Product Catalog Management (Port 8003)
│   ├── app/                        # Routers, Models, Schemas, Services
│   ├── Dockerfile                  # Container build instructions
│   ├── requirements.txt            # Python dependencies
│   ├── test_live_server.py         # Live HTTP server test runner
│   └── README.md                   # Dedicated Product Service Documentation
│
└── README.md                       # Master Repository Overview
```

---

## Microservices Breakdown

### 1. [ShopEase Authentication Service (`shopease-auth-service`)](./shopease-auth-service/README.md)
* **Port:** `8001`
* **Technologies:** Python 3.11+, FastAPI, MySQL 8.0, SQLAlchemy ORM, Alembic, PyJWT, Bcrypt, Docker Compose.
* **Responsibilities:**
  * User Registration (`POST /api/auth/register`) with Bcrypt password hashing.
  * User Authentication (`POST /api/auth/login`) with signed JWT token issuance.
  * Protected Current User Profile (`GET /api/auth/me`).
  * Token Verification (`POST /api/auth/verify-token`).
  * Password Change (`POST /api/auth/change-password`).
  * Default Pre-Seeded Credentials: `pasu@shopease.com` / `pasupathi@123`.
* **Interactive Docs:** [http://localhost:8001/docs](http://localhost:8001/docs)

---

### 2. [ShopEase User Management Service (`shopease-user-service`)](./shopease-user-service/README.md)
* **Port:** `8002`
* **Technologies:** Python 3.11+, FastAPI, MySQL 8.0, SQLAlchemy ORM, Alembic, PyJWT, Docker Compose.
* **Responsibilities:**
  * Customer Profile CRUD (`/api/users/profile`) linked to `auth_user_id`.
  * Delivery Address CRUD (`/api/users/addresses`) with strict ownership authorization.
  * Single default shipping address enforcement.
  * Stateless token verification using shared JWT secret.
* **Interactive Docs:** [http://localhost:8002/docs](http://localhost:8002/docs)

---

### 3. [ShopEase Product Service (`shopease-product-service`)](./shopease-product-service/README.md)
* **Port:** `8003`
* **Technologies:** Python 3.11+, FastAPI, Pydantic v2, Uvicorn, Docker.
* **Responsibilities:**
  * Full Product CRUD (`POST`, `GET`, `GET by ID`, `PUT`, `DELETE`).
  * Sequential unique product IDs (`PROD-1001`).
  * In-memory thread-safe dictionary store.
  * Category filtering (`?category=...`) and skip/limit pagination (`?skip=0&limit=10`).
* **Interactive Docs:** [http://localhost:8003/docs](http://localhost:8003/docs)

---

## Quick Execution Commands

### 1. Run User Service (Port 8002)
```bash
cd shopease-user-service

# Run directly:
python -m uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload

# Or with Docker Compose:
docker-compose up -d --build
```

### 2. Run Authentication Service (Port 8001)
```bash
cd shopease-auth-service
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

### 3. Run Product Service (Port 8003)
```bash
cd shopease-product-service
python -m uvicorn app.main:app --host 0.0.0.0 --port 8003 --reload
```

---

## Automated Verification Status

| Service | Test Runner | Scenarios Covered | Status |
| :--- | :--- | :---: | :---: |
| **User Service** | `python shopease-user-service/test_user_service.py` | 16 Scenarios | ✅ **100% Passed** |
| **Auth Service** | `python shopease-auth-service/test_auth_service.py` | 14 Scenarios | ✅ **100% Passed** |
| **Product Service**| `python shopease-product-service/test_live_server.py` | 12 Scenarios | ✅ **100% Passed** |
