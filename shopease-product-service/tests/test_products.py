"""
Automated Integration and Unit Tests for ShopEase Product Service.
Covers all 12 required test scenarios using FastAPI TestClient and pytest.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services.product_service import product_service


@pytest.fixture(autouse=True)
def reset_service():
    """Reset product store before each test for clean test isolation."""
    product_service.clear()
    yield
    product_service.clear()


@pytest.fixture
def client():
    """Create a FastAPI test client."""
    return TestClient(app)


# --------------------------------------------------------------------------
# Scenario 1: Create valid product
# --------------------------------------------------------------------------
def test_create_valid_product(client: TestClient):
    payload = {
        "product_name": "Mechanical Keyboard",
        "product_description": "RGB backlit mechanical gaming keyboard",
        "product_price": 79.99,
        "stock_quantity": 25,
        "product_category": "Electronics",
        "product_status": "Active",
    }
    response = client.post("/api/products/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["product_id"].startswith("PROD-")
    assert data["product_name"] == "Mechanical Keyboard"
    assert data["product_price"] == 79.99
    assert data["stock_quantity"] == 25
    assert data["product_category"] == "Electronics"
    assert data["product_status"] == "Active"
    assert "created_date" in data


# --------------------------------------------------------------------------
# Scenario 2: Create product with empty name (Reject with 422)
# --------------------------------------------------------------------------
def test_create_product_empty_name(client: TestClient):
    payload = {
        "product_name": "   ",  # whitespace only
        "product_description": "Valid description",
        "product_price": 49.99,
        "stock_quantity": 10,
        "product_category": "Electronics",
        "product_status": "Active",
    }
    response = client.post("/api/products/", json=payload)
    assert response.status_code == 422


# --------------------------------------------------------------------------
# Scenario 3: Create product with negative price (Reject with 422)
# --------------------------------------------------------------------------
def test_create_product_negative_price(client: TestClient):
    payload = {
        "product_name": "USB-C Cable",
        "product_description": "Fast charging cable",
        "product_price": -15.00,
        "stock_quantity": 100,
        "product_category": "Accessories",
        "product_status": "Active",
    }
    response = client.post("/api/products/", json=payload)
    assert response.status_code == 422


def test_create_product_zero_price(client: TestClient):
    payload = {
        "product_name": "Free Sample",
        "product_description": "Zero price sample",
        "product_price": 0.00,
        "stock_quantity": 10,
        "product_category": "Accessories",
        "product_status": "Active",
    }
    response = client.post("/api/products/", json=payload)
    assert response.status_code == 422


# --------------------------------------------------------------------------
# Scenario 4: Create product with negative stock (Reject with 422)
# --------------------------------------------------------------------------
def test_create_product_negative_stock(client: TestClient):
    payload = {
        "product_name": "Wireless Mouse",
        "product_description": "Ergonomic Bluetooth mouse",
        "product_price": 29.99,
        "stock_quantity": -5,
        "product_category": "Electronics",
        "product_status": "Active",
    }
    response = client.post("/api/products/", json=payload)
    assert response.status_code == 422


# --------------------------------------------------------------------------
# Scenario 5: Retrieve all products
# --------------------------------------------------------------------------
def test_retrieve_all_products(client: TestClient):
    # Empty case
    res_empty = client.get("/api/products/")
    assert res_empty.status_code == 200
    assert res_empty.json() == []

    # Insert two items
    client.post("/api/products/", json={
        "product_name": "Item 1",
        "product_price": 10.0,
        "stock_quantity": 5,
        "product_category": "Books",
        "product_status": "Active",
    })
    client.post("/api/products/", json={
        "product_name": "Item 2",
        "product_price": 20.0,
        "stock_quantity": 15,
        "product_category": "Clothing",
        "product_status": "Active",
    })

    res = client.get("/api/products/")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 2


# --------------------------------------------------------------------------
# Scenario 6: Retrieve product by valid ID
# --------------------------------------------------------------------------
def test_retrieve_product_by_valid_id(client: TestClient):
    create_res = client.post("/api/products/", json={
        "product_name": "Gaming Monitor",
        "product_description": "144Hz 27-inch IPS panel",
        "product_price": 299.99,
        "stock_quantity": 12,
        "product_category": "Electronics",
        "product_status": "Active",
    })
    prod_id = create_res.json()["product_id"]

    get_res = client.get(f"/api/products/{prod_id}")
    assert get_res.status_code == 200
    data = get_res.json()
    assert data["product_id"] == prod_id
    assert data["product_name"] == "Gaming Monitor"


# --------------------------------------------------------------------------
# Scenario 7: Retrieve product by invalid ID (404)
# --------------------------------------------------------------------------
def test_retrieve_product_by_invalid_id(client: TestClient):
    response = client.get("/api/products/PROD-99999")
    assert response.status_code == 404
    data = response.json()
    assert "not found" in data["detail"].lower()


# --------------------------------------------------------------------------
# Scenario 8: Update product
# --------------------------------------------------------------------------
def test_update_product(client: TestClient):
    create_res = client.post("/api/products/", json={
        "product_name": "Laptop Stand",
        "product_price": 35.00,
        "stock_quantity": 20,
        "product_category": "Accessories",
        "product_status": "Active",
    })
    prod_id = create_res.json()["product_id"]

    update_payload = {
        "product_name": "Aluminum Laptop Stand",
        "product_price": 39.99,
        "stock_quantity": 15,
        "product_status": "Inactive",
    }
    update_res = client.put(f"/api/products/{prod_id}", json=update_payload)
    assert update_res.status_code == 200
    data = update_res.json()
    assert data["product_name"] == "Aluminum Laptop Stand"
    assert data["product_price"] == 39.99
    assert data["stock_quantity"] == 15
    assert data["product_status"] == "Inactive"
    assert data["product_category"] == "Accessories"  # Unchanged


def test_update_nonexistent_product(client: TestClient):
    res = client.put("/api/products/PROD-NONEXISTENT", json={"product_price": 19.99})
    assert res.status_code == 404


# --------------------------------------------------------------------------
# Scenario 9: Delete product
# --------------------------------------------------------------------------
def test_delete_product(client: TestClient):
    create_res = client.post("/api/products/", json={
        "product_name": "Desk Mat",
        "product_price": 18.50,
        "stock_quantity": 40,
        "product_category": "Accessories",
        "product_status": "Active",
    })
    prod_id = create_res.json()["product_id"]

    del_res = client.delete(f"/api/products/{prod_id}")
    assert del_res.status_code == 200
    del_data = del_res.json()
    assert del_data["product_id"] == prod_id
    assert "deleted successfully" in del_data["message"].lower()


def test_delete_nonexistent_product(client: TestClient):
    res = client.delete("/api/products/PROD-99999")
    assert res.status_code == 404


# --------------------------------------------------------------------------
# Scenario 10: Retrieve deleted product (404)
# --------------------------------------------------------------------------
def test_retrieve_deleted_product(client: TestClient):
    create_res = client.post("/api/products/", json={
        "product_name": "Temporary Item",
        "product_price": 5.00,
        "stock_quantity": 1,
        "product_category": "Test",
        "product_status": "Active",
    })
    prod_id = create_res.json()["product_id"]

    client.delete(f"/api/products/{prod_id}")

    get_res = client.get(f"/api/products/{prod_id}")
    assert get_res.status_code == 404


# --------------------------------------------------------------------------
# Scenario 11: Category filtering
# --------------------------------------------------------------------------
def test_category_filtering(client: TestClient):
    client.post("/api/products/", json={
        "product_name": "Laptop",
        "product_price": 999.00,
        "stock_quantity": 10,
        "product_category": "Electronics",
        "product_status": "Active",
    })
    client.post("/api/products/", json={
        "product_name": "Smartphone",
        "product_price": 699.00,
        "stock_quantity": 15,
        "product_category": "Electronics",
        "product_status": "Active",
    })
    client.post("/api/products/", json={
        "product_name": "T-Shirt",
        "product_price": 19.99,
        "stock_quantity": 50,
        "product_category": "Clothing",
        "product_status": "Active",
    })

    # Filter Electronics
    res_elec = client.get("/api/products/?category=Electronics")
    assert res_elec.status_code == 200
    elec_items = res_elec.json()
    assert len(elec_items) == 2
    for item in elec_items:
        assert item["product_category"] == "Electronics"

    # Filter Clothing (case-insensitive test)
    res_cloth = client.get("/api/products/?category=clothing")
    assert res_cloth.status_code == 200
    cloth_items = res_cloth.json()
    assert len(cloth_items) == 1
    assert cloth_items[0]["product_name"] == "T-Shirt"

    # Filter Non-existent category
    res_none = client.get("/api/products/?category=Automotive")
    assert res_none.status_code == 200
    assert res_none.json() == []


# --------------------------------------------------------------------------
# Scenario 12: Pagination (skip and limit)
# --------------------------------------------------------------------------
def test_pagination(client: TestClient):
    for i in range(1, 11):
        client.post("/api/products/", json={
            "product_name": f"Product {i}",
            "product_price": float(i * 10),
            "stock_quantity": i * 2,
            "product_category": "General",
            "product_status": "Active",
        })

    # First page: skip=0, limit=3
    page1 = client.get("/api/products/?skip=0&limit=3")
    assert page1.status_code == 200
    data1 = page1.json()
    assert len(data1) == 3
    assert data1[0]["product_name"] == "Product 1"
    assert data1[2]["product_name"] == "Product 3"

    # Second page: skip=3, limit=3
    page2 = client.get("/api/products/?skip=3&limit=3")
    assert page2.status_code == 200
    data2 = page2.json()
    assert len(data2) == 3
    assert data2[0]["product_name"] == "Product 4"
    assert data2[2]["product_name"] == "Product 6"

    # Third page: skip=8, limit=5 (only 2 left)
    page3 = client.get("/api/products/?skip=8&limit=5")
    assert page3.status_code == 200
    data3 = page3.json()
    assert len(data3) == 2


# --------------------------------------------------------------------------
# System Health and Root Tests
# --------------------------------------------------------------------------
def test_root_and_health(client: TestClient):
    r_root = client.get("/")
    assert r_root.status_code == 200
    assert r_root.json()["status"] == "online"

    r_health = client.get("/health")
    assert r_health.status_code == 200
    assert r_health.json()["status"] == "healthy"
