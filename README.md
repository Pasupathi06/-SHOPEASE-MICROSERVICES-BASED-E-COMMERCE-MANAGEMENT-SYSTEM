# ShopEase – Microservices-Based E-Commerce Management System

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?style=flat&logo=docker&logoColor=white)](https://www.docker.com/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-4479A1.svg?style=flat&logo=mysql&logoColor=white)](https://www.mysql.com/)
[![JWT](https://img.shields.io/badge/JWT-Secure_Tokens-000000.svg?style=flat&logo=jsonwebtokens&logoColor=white)](https://jwt.io/)

Welcome to the **ShopEase Microservices-Based E-Commerce Management System** repository. This enterprise-grade platform consists of independent, containerized backend microservices built with Python and FastAPI following Clean Architecture, SQLAlchemy ORM, strict Pydantic validation, and modern DevOps container standards.

---

## Architecture Overview

```text
                               ┌────────────────────────────────────────────────────────┐
                               │                  API Gateway / Client                  │
                               └───────────────────────────┬────────────────────────────┘
                                                           │
        ┌───────────────────────────┬──────────────────────┴─────┬───────────────────────────┐
        │                           │                            │                           │
        ▼ (Port 8001)               ▼ (Port 8002)                ▼ (Port 8003)               ▼ (Port 8004)
 ┌─────────────────────────┐ ┌─────────────────────────┐ ┌─────────────────────────┐ ┌─────────────────────────┐
 │  shopease-auth-service  │ │  shopease-user-service  │ │ shopease-product-service│ │shopease-product-catalog │
 │  (JWT Auth & Security)  │ │ (Profiles & Addresses)  │ │(Fast In-Memory Catalog) │ │ (MySQL Catalog & Stock) │
 ├─────────────────────────┤ ├─────────────────────────┤ ├─────────────────────────┤ ├─────────────────────────┤
 │• FastAPI + PyJWT+Bcrypt │ │• FastAPI+SQLAlchemy ORM │ │• FastAPI + Pydantic v2  │ │• FastAPI+SQLAlchemy 2.0 │
 │• MySQL (shopease_auth)  │ │• MySQL (shopease_user)  │ │• Thread-safe In-Memory  │ │• MySQL(shopease_catalog)│
 │• Register & Login APIs  │ │• Profile CRUD           │ │• Fast Mock CRUD REST    │ │• Categories & Products  │
 │• Bearer Token Issuance  │ │• Address Mgmt (Def Addr)│ │• Category Filtering     │ │• Stock IN/OUT & Auditing│
 │• Token Verification     │ │• Ownership JWT Guard    │ │• Port 8003              │ │• Admin RBAC & Search    │
 │• Port 8001              │ │• Port 8002              │ │• Docker Container       │ │• Port 8004              │
 └───────────┬─────────────┘ └───────────┬─────────────┘ └─────────────────────────┘ └───────────┬─────────────┘
             │                           │                                                       │
             ▼                           ▼                                                       ▼
 ┌─────────────────────────┐ ┌─────────────────────────┐                             ┌─────────────────────────┐
 │   MySQL 8.0 Auth DB     │ │   MySQL 8.0 User DB     │                             │  MySQL 8.0 Catalog DB   │
 │     (auth-db:3306)      │ │     (user-db:3306)      │                             │   (catalog-db:3309)     │
 └─────────────────────────┘ └─────────────────────────┘                             └─────────────────────────┘
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
├── shopease-product-service/       # Microservice 3: Product In-Memory CRUD Mock (Port 8003)
│   ├── app/                        # Routers, Models, Schemas, Services
│   ├── Dockerfile                  # Container build instructions
│   ├── requirements.txt            # Python dependencies
│   ├── test_live_server.py         # Live HTTP server test runner
│   └── README.md                   # Dedicated Product Service Documentation
│
├── shopease-product-catalog-service/ # Microservice 4: Production Catalog & Inventory (Port 8004)
│   ├── app/                        # Routers (Category, Product, Inventory), Models, Schemas, Services
│   ├── alembic/                    # Alembic Database Migrations
│   ├── Dockerfile                  # Container build instructions
│   ├── docker-compose.yml          # Multi-container orchestration (Catalog + MySQL 8.0 Port 3309)
│   ├── requirements.txt            # Python dependencies
│   ├── test_catalog_service.py     # 20-scenario automated verification suite
│   ├── run_server.bat              # 1-Click Windows execution script
│   └── README.md                   # Dedicated Product Catalog Service Documentation
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

### 4. [ShopEase Product Catalog Service (`shopease-product-catalog-service`)](./shopease-product-catalog-service/README.md)
* **Port:** `8004`
* **Technologies:** Python 3.11+, FastAPI, MySQL 8.0, SQLAlchemy 2.0, Alembic, PyJWT, Docker Compose.
* **Responsibilities:**
  * **Categories Management:** CRUD operations, duplicate name prevention, deletion guard if products exist.
  * **Products Management:** Unique SKU enforcement, category validation, multi-criteria filtering (category, price range, brand, in-stock), full-text search, pagination, and sorting.
  * **Inventory Management:** ACID Stock-In and Stock-Out operations with strict negative stock prevention.
  * **Audit History:** Chronological audit trail of all inventory transactions.
  * **Low-Stock Alerts:** Real-time query for products with stock below threshold (default: 10 units).
  * **Security & RBAC:** Admin-only access for mutations and inventory management; Customer access for browsing and searching.
* **Interactive Docs:** [http://localhost:8004/docs](http://localhost:8004/docs)

---

## Quick Execution Commands

### 1. Run Product Catalog Service (Port 8004)
```bash
cd shopease-product-catalog-service

# Run directly with uvicorn:
python -m uvicorn app.main:app --host 0.0.0.0 --port 8004 --reload

# Or with Docker Compose (Service + MySQL 8.0 on Port 3309):
docker compose up -d --build
```

### 2. Run User Service (Port 8002)
```bash
cd shopease-user-service
python -m uvicorn app.main:app --host 0.0.0.0 --port 8002 --reload
```

### 3. Run Authentication Service (Port 8001)
```bash
cd shopease-auth-service
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

### 4. Run Product Service (Port 8003)
```bash
cd shopease-product-service
python -m uvicorn app.main:app --host 0.0.0.0 --port 8003 --reload
```

---

## Automated Verification Status

| Microservice | Port | Test Runner | Scenarios Covered | Status |
| :--- | :---: | :--- | :---: | :---: |
| **Product Catalog Service** | `8004` | `python shopease-product-catalog-service/test_catalog_service.py` | 20 Scenarios | ✅ **100% Passed** |
| **User Management Service** | `8002` | `python shopease-user-service/test_user_service.py` | 16 Scenarios | ✅ **100% Passed** |
| **Authentication Service** | `8001` | `python shopease-auth-service/test_auth_service.py` | 14 Scenarios | ✅ **100% Passed** |
| **Product Service (Mock)** | `8003` | `python shopease-product-service/test_live_server.py` | 12 Scenarios | ✅ **100% Passed** |
