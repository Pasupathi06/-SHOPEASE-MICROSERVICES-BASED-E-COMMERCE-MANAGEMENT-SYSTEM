# ShopEase – Microservices-Based E-Commerce Management System

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?style=flat&logo=docker&logoColor=white)](https://www.docker.com/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-4479A1.svg?style=flat&logo=mysql&logoColor=white)](https://www.mysql.com/)
[![JWT](https://img.shields.io/badge/JWT-Secure_Tokens-000000.svg?style=flat&logo=jsonwebtokens&logoColor=white)](https://jwt.io/)

Welcome to the **ShopEase Microservices-Based E-Commerce Management System** repository. This repository houses independently developed, containerized microservices built with Python and FastAPI, following Clean Architecture, strict Pydantic validation, and modern DevOps container standards.

---

## Architecture Overview

```text
                               ┌────────────────────────────────────────┐
                               │           API Gateway / Client         │
                               └───────────────────┬────────────────────┘
                                                   │
                         ┌─────────────────────────┴─────────────────────────┐
                         │                                                   │
                         ▼ (Port 8001)                                       ▼ (Port 8003)
      ┌─────────────────────────────────────┐             ┌─────────────────────────────────────┐
      │     shopease-auth-service           │             │     shopease-product-service        │
      │  (JWT Authentication & Security)    │             │      (Product Catalog & CRUD)       │
      ├─────────────────────────────────────┤             ├─────────────────────────────────────┤
      │ • FastAPI + PyJWT + Bcrypt          │             │ • FastAPI + Pydantic v2             │
      │ • MySQL 8.0 + SQLAlchemy + Alembic  │             │ • In-Memory Thread-Safe Store       │
      │ • User Registration & Login         │             │ • Complete CRUD REST APIs           │
      │ • Protected Profile (/api/auth/me)  │             │ • Category Filtering & Pagination   │
      │ • Docker Compose Multi-Container    │             │ • Dockerfile (python:3.11-slim)     │
      └──────────────────┬──────────────────┘             └─────────────────────────────────────┘
                         │
                         ▼
      ┌─────────────────────────────────────┐
      │          MySQL 8.0 Database         │
      │           (auth-db:3306)            │
      └─────────────────────────────────────┘
```

---

## Repository Structure

```text
SHOPEASE-MICROSERVICES-BASED-E-COMMERCE-MANAGEMENT-SYSTEM/
│
├── shopease-auth-service/          # Microservice 1: JWT Authentication & User Management
│   ├── app/                        # Application Source (Routers, Core, Database, Models, Schemas, Services)
│   ├── alembic/                    # Alembic Database Migration Scripts
│   ├── tests/                      # Automated Test Suite
│   ├── Dockerfile                  # Container build instructions
│   ├── docker-compose.yml          # Multi-container orchestration (Auth Service + MySQL 8.0)
│   ├── requirements.txt            # Python dependencies
│   ├── .env                        # Environment configurations
│   ├── test_auth_service.py        # 14-scenario automated test runner
│   ├── run_server.bat              # 1-Click Windows execution script
│   └── README.md                   # Dedicated Authentication Service Documentation
│
├── shopease-product-service/       # Microservice 2: Product Catalog Management
│   ├── app/                        # Application Source (Routers, Config, Models, Schemas, Services)
│   ├── tests/                      # Automated Pytest Suite
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

### 2. [ShopEase Product Service (`shopease-product-service`)](./shopease-product-service/README.md)
* **Port:** `8003`
* **Technologies:** Python 3.11+, FastAPI, Pydantic v2, Uvicorn, Docker.
* **Responsibilities:**
  * Full Product CRUD (`POST`, `GET`, `GET by ID`, `PUT`, `DELETE`).
  * Unique sequential product ID generation (`PROD-1001`).
  * In-memory thread-safe dictionary storage.
  * Category filtering (`?category=...`) and skip/limit pagination (`?skip=0&limit=10`).
  * Strict validation (Price > 0, Stock >= 0, Non-blank names, Status enums).
* **Interactive Docs:** [http://localhost:8003/docs](http://localhost:8003/docs)

---

## Quick Start Guide

### Running Authentication Service (Port 8001)
```bash
cd shopease-auth-service

# Option A: Run directly with Python
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload

# Option B: Run with Docker Compose (Auth Service + MySQL 8.0)
docker-compose up -d --build
```

### Running Product Service (Port 8003)
```bash
cd shopease-product-service

# Option A: Run directly with Python
python -m uvicorn app.main:app --host 0.0.0.0 --port 8003 --reload

# Option B: Run with Docker
docker build -t shopease-product-service .
docker run -d -p 8003:8003 shopease-product-service
```

---

## Automated Verification

Each microservice includes comprehensive test suites:
- **Auth Service:** `python shopease-auth-service/test_auth_service.py` (14/14 Scenarios Passed)
- **Product Service:** `python shopease-product-service/test_live_server.py` (12/12 Scenarios Passed)
