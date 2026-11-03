# ShopEase – Product Management Microservice

[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688.svg?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg?style=flat&logo=docker&logoColor=white)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An independent, production-grade microservice for the **ShopEase Microservices-Based E-Commerce Management System**. Built with **FastAPI**, **Pydantic v2**, and **Docker**, this service manages the product lifecycle (Create, Read, Update, Delete) with in-memory thread-safe data storage, robust validation, category filtering, pagination, and Swagger UI interactive documentation.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Project Objective](#project-objective)
- [Technology Stack](#technology-stack)
- [Architecture & Layer Separation](#architecture--layer-separation)
- [Project Structure](#project-structure)
- [Product Data Model & Validation Rules](#product-data-model--validation-rules)
- [REST API Endpoints Specification](#rest-api-endpoints-specification)
  - [Example Request & Response Payloads](#example-request--response-payloads)
- [Local Setup & Execution](#local-setup--execution)
- [Docker Build & Containerization](#docker-build--containerization)
- [Automated & Manual API Testing](#automated--manual-api-testing)
- [Git & Repository Best Practices](#git--repository-best-practices)

---

## Project Overview

In a modern e-commerce platform, decoupling services into isolated, independently deployable microservices ensures scalability, resilience, and maintainability. The **ShopEase Product Service** is responsible for managing the catalog of products available on the platform, providing high-performance REST APIs consumed by frontend web apps, mobile clients, and upstream ordering/checkout microservices.

---

## Project Objective

- Develop an independent **Product Management Microservice** using **Python 3.11+** and **FastAPI**.
- Implement complete **CRUD** (Create, Read, Update, Delete) REST APIs with HTTP status codes (`200 OK`, `201 Created`, `400 Bad Request`, `404 Not Found`, `422 Unprocessable Entity`).
- Use **in-memory thread-safe dictionary storage** (no external database dependencies).
- Enforce strict input validation using **Pydantic v2** models.
- Support **query-based category filtering** and **skip/limit pagination**.
- Containerize the microservice with **Docker** and verify execution on port `8003`.
- Provide automated verification suites and interactive **Swagger UI** documentation.

---

## Technology Stack

| Layer / Tool | Technology | Purpose |
| :--- | :--- | :--- |
| **Framework** | FastAPI | High-performance asynchronous REST API framework |
| **Language** | Python 3.11+ | Modern Python runtime |
| **Server** | Uvicorn | Lightning-fast ASGI web server |
| **Validation** | Pydantic v2 | Data parsing, type checking, and schema validation |
| **Container** | Docker | Containerization & isolated deployment |
| **Testing** | Pytest, HTTPX, urllib | Automated integration, unit, and live server testing |
| **Documentation**| OpenAPI & Swagger UI | Auto-generated interactive API docs (`/docs`) |
| **Config** | python-dotenv | 12-factor application configuration |

---

## Architecture & Layer Separation

The service strictly adheres to **Clean Architecture** and separation of concerns:

```
           ┌─────────────────────────────┐
           │      HTTP Client / UI       │
           └──────────────┬──────────────┘
                          │ (HTTP Requests on Port 8003)
                          ▼
           ┌─────────────────────────────┐
           │       app/main.py           │ ◄─── Exception Handlers, CORS, Health
           └──────────────┬──────────────┘
                          │
                          ▼
           ┌─────────────────────────────┐
           │  app/routers/product_routes │ ◄─── REST Endpoints & Status Codes
           └──────────────┬──────────────┘
                          │
            ┌─────────────┴─────────────┐
            ▼                           ▼
┌───────────────────────┐   ┌───────────────────────────┐
│ app/schemas/product   │   │ app/services/product      │
│ (Pydantic Validation) │   │ (Business Logic & Memory) │
└───────────────────────┘   └─────────────┬─────────────┘
                                          │
                                          ▼
                            ┌───────────────────────────┐
                            │    app/models/product     │
                            │   (In-Memory Dict Data)   │
                            └───────────────────────────┘
```

1. **`app/main.py`**: Initializes the FastAPI app, registers routes, configures CORS, handles global and domain exceptions, and provides `/health` monitoring endpoints.
2. **`app/routers/product_routes.py`**: Declares API routes, path parameters, query parameters, and maps HTTP methods to service calls.
3. **`app/schemas/product_schema.py`**: Pydantic models validating payloads, preventing whitespace-only strings, enforcing price > 0, stock >= 0, and status enums.
4. **`app/services/product_service.py`**: Contains all business logic, unique ID generation (`PROD-1001`), thread-safe locking, filtering, and CRUD operations.
5. **`app/models/product_model.py`**: Internal product data entity structure.
6. **`app/config/settings.py`**: Application settings loaded from environment variables (`.env`).

---

## Project Structure

```text
shopease-product-service/
│
├── app/
│   ├── main.py                     # Application entry point & router registration
│   ├── config/
│   │   └── settings.py             # Environment configurations
│   ├── models/
│   │   └── product_model.py        # In-memory data entity model
│   ├── routers/
│   │   └── product_routes.py       # REST API endpoints (/api/products)
│   ├── schemas/
│   │   └── product_schema.py       # Pydantic request & response validation
│   └── services/
│       └── product_service.py      # Core business logic & storage
│
├── tests/
│   └── test_products.py            # Automated Pytest suite
│
├── Dockerfile                      # Production Docker container build definition
├── .dockerignore                   # Build context exclusions
├── requirements.txt                # Python package dependencies
├── .env                            # Local environment configuration
├── .gitignore                      # Git tracking exclusions
├── verify_apis.py                  # Standalone API verification runner
├── test_service.py                 # Pure unit tests for schemas and service
├── test_live_server.py             # Live HTTP server test suite on port 8003
└── README.md                       # Comprehensive documentation
```

---

## Product Data Model & Validation Rules

### Data Fields

| Field Name | Type | Description | Rules / Constraints |
| :--- | :--- | :--- | :--- |
| `product_id` | `str` | Unique Identifier | System generated (`PROD-1001`, `PROD-1002`, etc.) |
| `product_name` | `str` | Product Title | Required, non-empty, trimmed, 1-100 characters |
| `product_description` | `str` | Detailed Description | Optional, max 500 characters |
| `product_price` | `float`| Unit Price | Required, must be strictly greater than 0 (`gt=0.0`) |
| `stock_quantity` | `int` | Stock Units | Required, non-negative integer (`ge=0`) |
| `product_category` | `str` | Category Name | Required, non-empty, trimmed, 2-50 characters |
| `product_status` | `str` | Lifecycle Status | Allowed: `"Active"` or `"Inactive"` |
| `created_date` | `str` | Timestamp | ISO 8601 UTC timestamp generated on creation |

---

## REST API Endpoints Specification

Base Path: `http://localhost:8003/api/products`

| HTTP Method | Endpoint | Description | Status Code |
| :--- | :--- | :--- | :--- |
| `GET` | `/` | Service root welcome info & status | `200 OK` |
| `GET` | `/health` | Microservice health check probe | `200 OK` |
| `POST` | `/api/products/` | Create a new product | `201 Created` / `422 Unprocessable` |
| `GET` | `/api/products/` | Retrieve all products (supports filtering & pagination) | `200 OK` |
| `GET` | `/api/products/{id}` | Retrieve single product by unique ID | `200 OK` / `404 Not Found` |
| `PUT` | `/api/products/{id}` | Update existing product fields | `200 OK` / `404 Not Found` / `422` |
| `DELETE` | `/api/products/{id}` | Delete product by unique ID | `200 OK` / `404 Not Found` |

---

### Example Request & Response Payloads

#### 1. Create Product (`POST /api/products/`)

**Request Body:**
```json
{
  "product_name": "Wireless Noise-Canceling Headphones",
  "product_description": "Over-ear Bluetooth headphones with active noise cancellation and 30-hour battery life.",
  "product_price": 149.99,
  "stock_quantity": 45,
  "product_category": "Electronics",
  "product_status": "Active"
}
```

**Response (`201 Created`):**
```json
{
  "product_id": "PROD-1001",
  "product_name": "Wireless Noise-Canceling Headphones",
  "product_description": "Over-ear Bluetooth headphones with active noise cancellation and 30-hour battery life.",
  "product_price": 149.99,
  "stock_quantity": 45,
  "product_category": "Electronics",
  "product_status": "Active",
  "created_date": "2026-11-03T04:26:00.123456+00:00"
}
```

#### 2. Retrieve All Products with Category Filter (`GET /api/products/?category=Electronics`)

**Response (`200 OK`):**
```json
[
  {
    "product_id": "PROD-1001",
    "product_name": "Wireless Noise-Canceling Headphones",
    "product_description": "Over-ear Bluetooth headphones with active noise cancellation and 30-hour battery life.",
    "product_price": 149.99,
    "stock_quantity": 45,
    "product_category": "Electronics",
    "product_status": "Active",
    "created_date": "2026-11-03T04:26:00.123456+00:00"
  }
]
```

#### 3. Pagination Query (`GET /api/products/?skip=0&limit=10`)

- `skip`: Number of records to skip (default `0`, minimum `0`).
- `limit`: Maximum records to return (default `10`, range `1` to `100`).

#### 4. Update Product (`PUT /api/products/PROD-1001`)

**Request Body:**
```json
{
  "product_price": 129.99,
  "stock_quantity": 40
}
```

**Response (`200 OK`):**
```json
{
  "product_id": "PROD-1001",
  "product_name": "Wireless Noise-Canceling Headphones",
  "product_description": "Over-ear Bluetooth headphones with active noise cancellation and 30-hour battery life.",
  "product_price": 129.99,
  "stock_quantity": 40,
  "product_category": "Electronics",
  "product_status": "Active",
  "created_date": "2026-11-03T04:26:00.123456+00:00"
}
```

#### 5. Delete Product (`DELETE /api/products/PROD-1001`)

**Response (`200 OK`):**
```json
{
  "message": "Product deleted successfully.",
  "product_id": "PROD-1001"
}
```

#### 6. Missing Product Error (`GET /api/products/PROD-9999`)

**Response (`404 Not Found`):**
```json
{
  "detail": "Product with ID 'PROD-9999' was not found."
}
```

---

## Local Setup & Execution

### Prerequisites
- Python 3.11 or higher
- Git

### 1. Clone or Open the Repository
```bash
cd shopease-product-service
```

### 2. Create and Activate Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8003 --reload
```

### 5. Access Interactive Swagger Documentation
Open your browser and navigate to:
- **Swagger UI**: [http://localhost:8003/docs](http://localhost:8003/docs)
- **ReDoc UI**: [http://localhost:8003/redoc](http://localhost:8003/redoc)
- **OpenAPI Schema**: [http://localhost:8003/openapi.json](http://localhost:8003/openapi.json)

---

## Docker Build & Containerization

The microservice includes a lightweight `Dockerfile` based on `python:3.11-slim`.

### 1. Build the Docker Image
```bash
docker build -t shopease-product-service .
```

### 2. Verify Docker Image Creation
```bash
docker images
```

### 3. Run the Container
```bash
docker run -d --name shopease-product-container -p 8003:8003 shopease-product-service
```

### 4. Inspect Container Status & Logs
```bash
# Check running containers
docker ps

# Inspect real-time logs
docker logs -f shopease-product-container
```

### 5. Manage Container Lifecycle
```bash
# Stop container
docker stop shopease-product-container

# Start container
docker start shopease-product-container

# Remove container
docker rm -f shopease-product-container
```

---

## Automated & Manual API Testing

### Automated Test Suites

The project includes test runners covering all 12 evaluation criteria:

#### 1. Pure Unit & Schema Tests:
```bash
python test_service.py
```
*Validates in-memory CRUD operations, ID counters, category filtering, pagination, and Pydantic validation rules.*

#### 2. Live HTTP Server Test on Port 8003:
```bash
python test_live_server.py
```
*Spawns Uvicorn on port 8003, runs end-to-end HTTP requests, and verifies status codes (200, 201, 404, 422).*

### Test Scenarios Matrix

| # | Test Scenario | Expected Outcome | Verified |
| :-: | :--- | :--- | :-: |
| 1 | Create product with valid data | HTTP `201 Created` with unique `PROD-xxxx` ID | ✅ Passed |
| 2 | Create product with empty/whitespace name | HTTP `422 Unprocessable Entity` | ✅ Passed |
| 3 | Create product with negative or zero price | HTTP `422 Unprocessable Entity` | ✅ Passed |
| 4 | Create product with negative stock | HTTP `422 Unprocessable Entity` | ✅ Passed |
| 5 | Retrieve all products (empty & populated) | HTTP `200 OK` returning JSON array | ✅ Passed |
| 6 | Retrieve product by valid ID | HTTP `200 OK` returning matching product | ✅ Passed |
| 7 | Retrieve product by invalid ID | HTTP `404 Not Found` with clear detail | ✅ Passed |
| 8 | Update product attributes | HTTP `200 OK` with updated values preserved | ✅ Passed |
| 9 | Delete existing product | HTTP `200 OK` with deletion confirmation | ✅ Passed |
| 10 | Retrieve deleted product | HTTP `404 Not Found` | ✅ Passed |
| 11 | Filter products by category | HTTP `200 OK` returning matching category | ✅ Passed |
| 12 | Paginate products with skip and limit | HTTP `200 OK` returning slice of records | ✅ Passed |

---

## Git & Repository Best Practices

- `.gitignore` ensures `venv/`, `.env`, `__pycache__/`, `.pytest_cache/`, and temporary files are excluded.
- `.dockerignore` prevents unnecessary files from bloating the Docker build context.
- Sensitive environment configurations are kept out of source control.

---

## Project Status

- **Architecture:** Complete (Clean separation of Routes, Schemas, Models, Services, Config)
- **CRUD REST APIs:** 100% Implemented & Tested
- **Docker Support:** Fully Containerized (`Dockerfile`, `.dockerignore`, port 8003)
- **Automated Tests:** 12/12 Scenarios Passed
- **Documentation:** Complete
