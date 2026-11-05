"""
Standalone Verification Script for ShopEase Product Service APIs.
Runs all CRUD scenarios and validates status codes, response shapes, and business logic.
"""

import sys
from fastapi.testclient import TestClient
from app.main import app
from app.services.product_service import product_service


def run_all_tests():
    print("=" * 60)
    print("SHOPEASE PRODUCT SERVICE - API VERIFICATION")
    print("=" * 60)

    client = TestClient(app)
    passed = 0
    total = 12

    # Reset in-memory store
    product_service.clear()

    # Scenario 1: Create Valid Product
    print("\n[Scenario 1] Testing: Create valid product (POST /api/products/)")
    payload1 = {
        "product_name": "Mechanical Keyboard",
        "product_description": "RGB backlit mechanical keyboard",
        "product_price": 79.99,
        "stock_quantity": 25,
        "product_category": "Electronics",
        "product_status": "Active",
    }
    r = client.post("/api/products/", json=payload1)
    assert r.status_code == 201, f"Expected 201, got {r.status_code}"
    prod1 = r.json()
    assert prod1["product_id"].startswith("PROD-")
    assert prod1["product_name"] == "Mechanical Keyboard"
    prod1_id = prod1["product_id"]
    print(f"  --> PASSED (Created {prod1_id}: HTTP 201)")
    passed += 1

    # Scenario 2: Create product with empty name
    print("\n[Scenario 2] Testing: Reject empty name (POST /api/products/)")
    r = client.post("/api/products/", json={
        "product_name": "   ",
        "product_price": 49.99,
        "stock_quantity": 10,
        "product_category": "Electronics",
        "product_status": "Active",
    })
    assert r.status_code == 422, f"Expected 422, got {r.status_code}"
    print("  --> PASSED (Rejected empty name: HTTP 422)")
    passed += 1

    # Scenario 3: Create product with negative price
    print("\n[Scenario 3] Testing: Reject negative/zero price (POST /api/products/)")
    r = client.post("/api/products/", json={
        "product_name": "USB-C Cable",
        "product_price": -15.00,
        "stock_quantity": 100,
        "product_category": "Accessories",
        "product_status": "Active",
    })
    assert r.status_code == 422, f"Expected 422, got {r.status_code}"
    print("  --> PASSED (Rejected negative price: HTTP 422)")
    passed += 1

    # Scenario 4: Create product with negative stock
    print("\n[Scenario 4] Testing: Reject negative stock (POST /api/products/)")
    r = client.post("/api/products/", json={
        "product_name": "Wireless Mouse",
        "product_price": 29.99,
        "stock_quantity": -5,
        "product_category": "Electronics",
        "product_status": "Active",
    })
    assert r.status_code == 422, f"Expected 422, got {r.status_code}"
    print("  --> PASSED (Rejected negative stock: HTTP 422)")
    passed += 1

    # Scenario 5: Retrieve all products
    print("\n[Scenario 5] Testing: Retrieve all products (GET /api/products/)")
    r = client.get("/api/products/")
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    items = r.json()
    assert len(items) >= 1
    print(f"  --> PASSED (Retrieved {len(items)} products: HTTP 200)")
    passed += 1

    # Scenario 6: Retrieve product by valid ID
    print(f"\n[Scenario 6] Testing: Retrieve product by valid ID (GET /api/products/{prod1_id})")
    r = client.get(f"/api/products/{prod1_id}")
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    assert r.json()["product_id"] == prod1_id
    print(f"  --> PASSED (Found product {prod1_id}: HTTP 200)")
    passed += 1

    # Scenario 7: Retrieve product by invalid ID
    print("\n[Scenario 7] Testing: Retrieve product by invalid ID (GET /api/products/PROD-99999)")
    r = client.get("/api/products/PROD-99999")
    assert r.status_code == 404, f"Expected 404, got {r.status_code}"
    print("  --> PASSED (Handled missing product: HTTP 404)")
    passed += 1

    # Scenario 8: Update product
    print(f"\n[Scenario 8] Testing: Update product (PUT /api/products/{prod1_id})")
    update_data = {
        "product_name": "Mechanical Gaming Keyboard RGB v2",
        "product_price": 89.99,
        "stock_quantity": 30,
        "product_status": "Active"
    }
    r = client.put(f"/api/products/{prod1_id}", json=update_data)
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    updated = r.json()
    assert updated["product_name"] == "Mechanical Gaming Keyboard RGB v2"
    assert updated["product_price"] == 89.99
    print(f"  --> PASSED (Updated product {prod1_id}: HTTP 200)")
    passed += 1

    # Scenario 9: Delete product
    print(f"\n[Scenario 9] Testing: Delete product (DELETE /api/products/{prod1_id})")
    r = client.delete(f"/api/products/{prod1_id}")
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    assert "deleted successfully" in r.json()["message"].lower()
    print(f"  --> PASSED (Deleted product {prod1_id}: HTTP 200)")
    passed += 1

    # Scenario 10: Retrieve deleted product (expect 404)
    print(f"\n[Scenario 10] Testing: Retrieve deleted product (GET /api/products/{prod1_id})")
    r = client.get(f"/api/products/{prod1_id}")
    assert r.status_code == 404, f"Expected 404, got {r.status_code}"
    print(f"  --> PASSED (Deleted product correctly returns HTTP 404)")
    passed += 1

    # Seed data for category and pagination tests
    product_service.clear()
    client.post("/api/products/", json={
        "product_name": "Laptop",
        "product_price": 1200.0,
        "stock_quantity": 10,
        "product_category": "Electronics",
        "product_status": "Active",
    })
    client.post("/api/products/", json={
        "product_name": "Smartphone",
        "product_price": 800.0,
        "stock_quantity": 15,
        "product_category": "Electronics",
        "product_status": "Active",
    })
    client.post("/api/products/", json={
        "product_name": "Cotton Hoodie",
        "product_price": 45.0,
        "stock_quantity": 50,
        "product_category": "Clothing",
        "product_status": "Active",
    })
    client.post("/api/products/", json={
        "product_name": "Running Shoes",
        "product_price": 75.0,
        "stock_quantity": 30,
        "product_category": "Footwear",
        "product_status": "Active",
    })

    # Scenario 11: Category filtering
    print("\n[Scenario 11] Testing: Category filtering (GET /api/products/?category=Electronics)")
    r = client.get("/api/products/?category=Electronics")
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    cat_items = r.json()
    assert len(cat_items) == 2
    assert all(i["product_category"] == "Electronics" for i in cat_items)
    print(f"  --> PASSED (Filtered {len(cat_items)} electronics items: HTTP 200)")
    passed += 1

    # Scenario 12: Pagination
    print("\n[Scenario 12] Testing: Pagination (GET /api/products/?skip=1&limit=2)")
    r = client.get("/api/products/?skip=1&limit=2")
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    paginated = r.json()
    assert len(paginated) == 2
    print(f"  --> PASSED (Pagination returned {len(paginated)} items: HTTP 200)")
    passed += 1

    print("\n" + "=" * 60)
    print(f"ALL {passed}/{total} API TEST SCENARIOS PASSED SUCCESSFULLY!")
    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()
