# ShopEase – Product Catalog Microservice

[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-009688.svg?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-D71F00.svg?style=flat&logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0-4479A1.svg?style=flat&logo=mysql&logoColor=white)](https://www.mysql.com/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg?style=flat&logo=docker&logoColor=white)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

An enterprise-ready, containerized **Product Catalog Microservice** built with **FastAPI**, **SQLAlchemy 2.0**, and **MySQL 8.0** for the **ShopEase Microservices-Based E-Commerce Platform**. 

This microservice provides comprehensive category management, rich product catalog indexing (search, multi-criteria filtering, sorting, pagination), real-time inventory management (ACID stock-in, stock-out with negative prevention, low-stock threshold alerting), and full audit history logging, guarded by **JWT Role-Based Access Control (RBAC)**.

---

## 🌟 Key Features

1. **Category Management:**
   - Full CRUD operations with unique naming enforcement.
   - Guard against accidental deletion of categories that have active products assigned.
2. **Product Catalog & Lifecycle:**
   - Product creation with unique SKU validation, category relationship integrity, and positive price rules.
   - Multi-criteria filtering by category, brand, price range (`min_price`, `max_price`), and stock availability (`in_stock_only`).
   - Case-insensitive search across product title and SKU.
   - Flexible pagination (`page`, `page_size`) and sorting by price, name, stock quantity, or date.
   - Soft-delete capability (`is_active = false`) for seamless order history preservation.
3. **Inventory Management & Audit Trail:**
   - **Stock-In:** Increment inventory upon supply arrival, recording transaction type `IN`.
   - **Stock-Out:** Decrement inventory upon order dispatch, recording transaction type `OUT`.
   - **Negative Stock Prevention:** Rejects any stock deduction that exceeds current available inventory with HTTP 400.
   - **Audit Trail:** Chronological immutable transaction history recording `product_id`, `transaction_type`, `quantity`, `previous_stock`, `updated_stock`, `remarks`, and timestamps.
   - **Low-Stock Alerting:** Instant visibility into products whose stock is at or below the warning threshold (default: 10 units).
4. **Security & JWT Role-Based Access Control (RBAC):**
   - **Customers:** Public read access to active products, categories, search, filtering, and stock availability checks.
   - **Administrators:** Strict `role == "admin"` RBAC verification for category mutations, product additions/modifications/deletions, and all inventory operations.
   - Seamless interoperability with the **ShopEase Authentication Service** sharing the same secret key and algorithm (`HS256`).
5. **Production Ready & Resilient:**
   - Configured for MySQL 8 with automatic fallback to local SQLite for instant standalone development.
   - Docker and Docker Compose definitions for one-command containerization.
   - Alembic database migration support.

---

## 🏗️ Architecture & Project Structure

```
shopease-product-catalog-service/
│
├── app/
│   ├── main.py                    # FastAPI application initialization & lifespan
│   │
│   ├── routers/                   # API Route Controllers
│   │   ├── __init__.py
│   │   ├── category_routes.py     # /api/categories endpoints
│   │   ├── product_routes.py      # /api/products endpoints
│   │   └── inventory_routes.py    # /api/inventory endpoints
│   │
│   ├── models/                    # SQLAlchemy ORM Database Models
│   │   ├── __init__.py
│   │   ├── category_model.py      # categories table definition
│   │   ├── product_model.py       # products table definition
│   │   └── inventory_model.py     # inventory_transactions table definition
│   │
│   ├── schemas/                   # Pydantic Request/Response Models
│   │   ├── __init__.py
│   │   ├── category_schema.py     # Category schemas
│   │   ├── product_schema.py      # Product schemas & pagination
│   │   └── inventory_schema.py    # Stock adjustment & transaction schemas
│   │
│   ├── services/                  # Business Logic Layer
│   │   ├── __init__.py
│   │   ├── category_service.py    # Category CRUD & integrity logic
│   │   ├── product_service.py     # Product search, filter, paginate & CRUD
│   │   └── inventory_service.py   # ACID inventory stock-in/out & auditing
│   │
│   ├── core/                      # Application Settings & Security
│   │   ├── config.py              # Environment variable loading
│   │   └── security.py            # JWT decoding & Admin RBAC dependencies
│   │
│   └── database/                  # Database Connection & Lifecycle
│       └── connection.py          # SQLAlchemy 2.0 Engine, Sessions & SQLite fallback
│
├── alembic/                       # Alembic Database Migrations
│   ├── versions/
│   │   └── 001_initial_catalog_tables.py
│   ├── env.py
│   └── script.py.mako
│
├── alembic.ini                    # Alembic migration configuration
├── Dockerfile                     # Multi-stage Python 3.11 Docker container
├── docker-compose.yml             # Service & MySQL 8.0 orchestration
├── requirements.txt               # Locked Python dependencies
├── .env                           # Environment configuration variables
├── .dockerignore                  # Docker build exclusions
├── .gitignore                     # Git tracking exclusions
├── run_server.bat                 # Windows one-click local server launcher
├── test_catalog_service.py        # 20-scenario automated verification suite
├── test_live_catalog_server.py    # Live HTTP endpoint probe script
└── README.md                      # Comprehensive documentation
```

---

## 🗄️ Database Schema & Relationships

### 1. Categories Table (`categories`)
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | Integer | Primary Key, Auto Increment | Unique Category ID |
| `name` | String(100) | Unique, Not Null, Indexed | Category Name |
| `description` | Text | Nullable | Detailed Category Description |
| `is_active` | Boolean | Default: True | Active Availability Flag |
| `created_at` | DateTime | Not Null, Default: Current | Creation Timestamp |
| `updated_at` | DateTime | Not Null, Auto Update | Modification Timestamp |

### 2. Products Table (`products`)
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | Integer | Primary Key, Auto Increment | Unique Product ID |
| `category_id` | Integer | Foreign Key (`categories.id`), Indexed | Associated Category |
| `name` | String(150) | Not Null, Indexed | Product Title |
| `description` | Text | Nullable | Product Description / Specs |
| `sku` | String(50) | Unique, Not Null, Indexed | Stock Keeping Unit |
| `price` | Numeric(10,2) | Not Null, Price > 0 | Regular Price |
| `discount_price` | Numeric(10,2) | Nullable, Discount < Price | Discounted Sale Price |
| `stock_quantity` | Integer | Not Null, Default: 0, Stock >= 0 | On-hand Inventory Count |
| `image_url` | String(500) | Nullable | Primary Product Image URL |
| `brand` | String(100) | Nullable, Indexed | Manufacturer / Brand |
| `is_active` | Boolean | Default: True | Active Catalog Status |
| `created_at` | DateTime | Not Null, Default: Current | Creation Timestamp |
| `updated_at` | DateTime | Not Null, Auto Update | Modification Timestamp |

### 3. Inventory Transactions Table (`inventory_transactions`)
| Column | Type | Constraints | Description |
|---|---|---|---|
| `id` | Integer | Primary Key, Auto Increment | Unique Transaction ID |
| `product_id` | Integer | Foreign Key (`products.id`), Indexed | Referenced Product |
| `transaction_type` | String(20) | Not Null (`IN` or `OUT`) | Movement Type |
| `quantity` | Integer | Not Null, Quantity > 0 | Quantity Altered |
| `previous_stock` | Integer | Not Null | Stock Prior to Movement |
| `updated_stock` | Integer | Not Null | Stock After Movement |
| `remarks` | String(255) | Nullable | Reason / PO Number / Memo |
| `created_at` | DateTime | Not Null, Default: Current | Audit Timestamp |

---

## 🚀 API Endpoints Reference

### Category Endpoints (`/api/categories`)
| Method | Endpoint | Access | Description |
|---|---|---|---|
| `POST` | `/api/categories` | Admin Only | Create a new product category |
| `GET` | `/api/categories` | Public | List all categories (active only for customers) |
| `GET` | `/api/categories/{id}` | Public | Retrieve a specific category |
| `PUT` | `/api/categories/{id}` | Admin Only | Update category name/description |
| `DELETE` | `/api/categories/{id}` | Admin Only | Delete category (blocked if products present) |

### Product Endpoints (`/api/products`)
| Method | Endpoint | Access | Description |
|---|---|---|---|
| `POST` | `/api/products` | Admin Only | Create a new product & log initial inventory |
| `GET` | `/api/products` | Public | Search, filter, sort & paginate products |
| `GET` | `/api/products/{id}` | Public | Get single product details |
| `PUT` | `/api/products/{id}` | Admin Only | Full product update |
| `PATCH` | `/api/products/{id}` | Admin Only | Partial product update |
| `DELETE` | `/api/products/{id}` | Admin Only | Soft-delete / deactivate product |

#### Query Parameters for `GET /api/products`:
- `search`: Keyword matching product title or SKU (e.g. `?search=iPhone`).
- `category_id`: Filter by specific category ID (e.g. `?category_id=1`).
- `min_price`: Minimum price filter (e.g. `?min_price=100.00`).
- `max_price`: Maximum price filter (e.g. `?max_price=1000.00`).
- `brand`: Filter by brand name (e.g. `?brand=Apple`).
- `in_stock_only`: If true, returns only products where `stock_quantity > 0`.
- `page`: Page index (default: `1`).
- `page_size`: Number of items per page (default: `10`, max: `100`).
- `sort_by`: Field to sort on (`price`, `name`, `stock_quantity`, `created_at`).
- `sort_order`: Sorting direction (`asc` or `desc`).

### Inventory Endpoints (`/api/inventory`)
| Method | Endpoint | Access | Description |
|---|---|---|---|
| `GET` | `/api/inventory/low-stock` | Admin Only | List products where stock <= threshold |
| `GET` | `/api/inventory/{id}` | Public | Real-time stock status & alert flag |
| `POST` | `/api/inventory/{id}/stock-in` | Admin Only | Increase stock and record IN transaction |
| `POST` | `/api/inventory/{id}/stock-out` | Admin Only | Decrease stock (with negative prevention) |
| `GET` | `/api/inventory/{id}/history` | Admin Only | Chronological immutable audit history |

### System & Health Endpoints
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | Microservice metadata and route sitemap |
| `GET` | `/health` | Microservice and MySQL database status check |
| `GET` | `/docs` | Interactive Swagger UI API documentation |
| `GET` | `/redoc` | OpenAPI ReDoc documentation |

---

## 🔐 Authentication & Role-Based Access Control

The Product Catalog Service validates JWT Bearer tokens issued by the ShopEase Authentication Service (`/api/auth/login`).

Include the token in the `Authorization` header:
```http
Authorization: Bearer <JWT_ACCESS_TOKEN>
```

### Role Matrix:
| Action | Customer Role | Admin Role | Unauthenticated |
|---|:---:|:---:|:---:|
| Browse & Search Products | ✅ | ✅ | ✅ |
| View Active Categories | ✅ | ✅ | ✅ |
| Check Stock Availability | ✅ | ✅ | ✅ |
| Create / Update Categories | ❌ (403) | ✅ | ❌ (401) |
| Create / Update / Delete Products | ❌ (403) | ✅ | ❌ (401) |
| Stock-In / Stock-Out Operations | ❌ (403) | ✅ | ❌ (401) |
| View Low Stock Alerts | ❌ (403) | ✅ | ❌ (401) |
| View Stock Audit Trail | ❌ (403) | ✅ | ❌ (401) |

---

## ⚙️ Configuration & Environment Variables

Variables in `.env`:
```ini
# Application
PROJECT_NAME="ShopEase Product Catalog Service"
PROJECT_VERSION="1.0.0"
HOST=0.0.0.0
PORT=8004

# MySQL Database
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DATABASE=shopease_product_catalog_db
MYSQL_USER=pasu
MYSQL_PASSWORD=pasupathi@123
DATABASE_URL=mysql+pymysql://pasu:pasupathi%40123@localhost:3306/shopease_product_catalog_db

# JWT Security (Must match Auth Service)
JWT_SECRET_KEY=shopease_jwt_super_secret_key_pasupathi_2026_secure_hash_key_123
JWT_ALGORITHM=HS256

# Inventory Defaults
DEFAULT_LOW_STOCK_THRESHOLD=10
```

---

## 🛠️ Installation & Running Locally

### 1. Prerequisites
- Python 3.10+ installed
- MySQL 8.0 server running (or the app will automatically use SQLite for local standalone development)

### 2. Setup Virtual Environment & Install Dependencies
```bash
cd shopease-product-catalog-service
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

### 3. Run Database Migrations (Optional / Automated)
```bash
alembic upgrade head
```

### 4. Start the Application Server
```bash
# Using uvicorn:
python -m uvicorn app.main:app --host 0.0.0.0 --port 8004 --reload

# Or on Windows, double-click:
run_server.bat
```

Access Swagger UI at: **`http://localhost:8004/docs`**

---

## 🐳 Docker & Docker Compose Deployment

### Start Service with Docker Compose:
```bash
docker compose up -d --build
```
This starts:
1. `shopease-catalog-db`: MySQL 8.0 container on port `3309:3306`.
2. `shopease-product-catalog-service`: FastAPI container on port `8004:8004`.

### Stop Containers:
```bash
docker compose down
```

---

## 🧪 Automated Test Suite (20 Scenarios)

The service includes an automated test suite verifying all 20 business, security, and edge-case requirements:

```bash
python test_catalog_service.py
```

### Verification Checklist:
- [x] 1. Category Creation with Valid Data
- [x] 2. Duplicate Category Prevention (HTTP 400)
- [x] 3. Product Creation with Valid Data & Initial Stock Logging
- [x] 4. Product Creation with Non-Existent Category (HTTP 404)
- [x] 5. Duplicate SKU Prevention (HTTP 400)
- [x] 6. Negative / Zero Price Validation (Pydantic ValidationError)
- [x] 7. Stock-In Operation (Quantity increment & IN transaction logged)
- [x] 8. Stock-Out Operation (Quantity decrement & OUT transaction logged)
- [x] 9. Stock-Out Exceeding Available Stock (Negative prevention HTTP 400)
- [x] 10. Product Search by Name / Keyword
- [x] 11. Product Filtering by Category
- [x] 12. Product Filtering by Price Range
- [x] 13. Product Pagination (`page`, `page_size`, `total_pages`)
- [x] 14. Category Deletion Guard when Associated Products Exist (HTTP 400)
- [x] 15. Low Stock Alert Retrieval (`stock_quantity <= threshold`)
- [x] 16. RBAC Enforcement (Customer blocked from Admin endpoints with HTTP 403)
- [x] 17. Invalid / Expired Token Rejection (HTTP 401)
- [x] 18. Category Deletion Allowed when Empty
- [x] 19. Product Partial Update / Patch
- [x] 20. Stock Audit History Retrieval in Chronological Order

**Pass Rate: 20/20 (100%)**
