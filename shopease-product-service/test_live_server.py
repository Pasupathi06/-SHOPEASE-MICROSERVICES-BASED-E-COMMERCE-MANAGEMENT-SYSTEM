"""
Live Server Integration Test for ShopEase Product Service.
Spawns Uvicorn server on port 8003, executes HTTP requests against all endpoints,
and validates end-to-end functionality.
"""

import time
import json
import urllib.request
import urllib.error
import threading
import uvicorn
from app.main import app
from app.services.product_service import product_service

BASE_URL = "http://127.0.0.1:8003"


class ServerThread(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        config = uvicorn.Config(app=app, host="127.0.0.1", port=8003, log_level="warning")
        self.server = uvicorn.Server(config)

    def run(self):
        self.server.run()

    def stop(self):
        self.server.should_exit = True


def make_request(method, path, body=None):
    """Helper to perform HTTP requests using standard urllib."""
    url = f"{BASE_URL}{path}"
    data = json.dumps(body).encode("utf-8") if body is not None else None
    headers = {"Content-Type": "application/json"} if body is not None else {}
    req = urllib.request.Request(url, data=data, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            status_code = response.getcode()
            resp_body = response.read().decode("utf-8")
            data = json.loads(resp_body) if resp_body else None
            return status_code, data
    except urllib.error.HTTPError as e:
        status_code = e.code
        err_body = e.read().decode("utf-8")
        try:
            data = json.loads(err_body)
        except Exception:
            data = err_body
        return status_code, data


def main():
    print("=" * 70)
    print("STARTING SHOPEASE LIVE SERVER ON PORT 8003...")
    print("=" * 70)

    server = ServerThread()
    server.start()

    # Wait for server to become responsive
    max_retries = 20
    ready = False
    for _ in range(max_retries):
        try:
            status, data = make_request("GET", "/health")
            if status == 200 and data.get("status") == "healthy":
                ready = True
                print("Server is UP and HEALTHY on http://127.0.0.1:8003!\n")
                break
        except Exception:
            time.sleep(0.3)

    if not ready:
        print("ERROR: Server failed to start in time.")
        server.stop()
        return

    try:
        # Reset storage
        product_service.clear()

        # 1. Root & Swagger Docs check
        status, data = make_request("GET", "/")
        print(f"[Check 1] GET / -> HTTP {status}: {data['service']} (version {data['version']})")
        assert status == 200

        # 2. POST /api/products/ (Valid product)
        payload = {
            "product_name": "Ultra HD 4K Smart TV",
            "product_description": "55-inch OLED HDR display",
            "product_price": 699.99,
            "stock_quantity": 18,
            "product_category": "Electronics",
            "product_status": "Active"
        }
        status, data = make_request("POST", "/api/products/", payload)
        print(f"[Check 2] POST /api/products/ -> HTTP {status}: Created {data['product_id']} ({data['product_name']})")
        assert status == 201
        prod_id = data["product_id"]

        # 3. POST /api/products/ (Empty name validation)
        bad_payload = {
            "product_name": "   ",
            "product_price": 50.0,
            "stock_quantity": 10,
            "product_category": "Electronics"
        }
        status, data = make_request("POST", "/api/products/", bad_payload)
        print(f"[Check 3] POST /api/products/ (empty name) -> HTTP {status} (Expected 422)")
        assert status == 422

        # 4. POST /api/products/ (Negative price validation)
        bad_price = {
            "product_name": "Headphones",
            "product_price": -25.0,
            "stock_quantity": 10,
            "product_category": "Electronics"
        }
        status, data = make_request("POST", "/api/products/", bad_price)
        print(f"[Check 4] POST /api/products/ (negative price) -> HTTP {status} (Expected 422)")
        assert status == 422

        # 5. POST /api/products/ (Negative stock validation)
        bad_stock = {
            "product_name": "Headphones",
            "product_price": 25.0,
            "stock_quantity": -10,
            "product_category": "Electronics"
        }
        status, data = make_request("POST", "/api/products/", bad_stock)
        print(f"[Check 5] POST /api/products/ (negative stock) -> HTTP {status} (Expected 422)")
        assert status == 422

        # 6. GET /api/products/ (Retrieve all products)
        status, data = make_request("GET", "/api/products/")
        print(f"[Check 6] GET /api/products/ -> HTTP {status}: Retrieved {len(data)} product(s)")
        assert status == 200
        assert len(data) >= 1

        # 7. GET /api/products/{product_id} (Retrieve by valid ID)
        status, data = make_request("GET", f"/api/products/{prod_id}")
        print(f"[Check 7] GET /api/products/{prod_id} -> HTTP {status}: {data['product_name']}")
        assert status == 200
        assert data["product_id"] == prod_id

        # 8. GET /api/products/{product_id} (Invalid ID 404)
        status, data = make_request("GET", "/api/products/PROD-INVALID")
        print(f"[Check 8] GET /api/products/PROD-INVALID -> HTTP {status} (Expected 404: {data['detail']})")
        assert status == 404

        # 9. PUT /api/products/{product_id} (Update product)
        update_body = {
            "product_name": "Ultra HD 4K Smart TV Series X",
            "product_price": 649.99,
            "stock_quantity": 25,
            "product_status": "Active"
        }
        status, data = make_request("PUT", f"/api/products/{prod_id}", update_body)
        print(f"[Check 9] PUT /api/products/{prod_id} -> HTTP {status}: Price updated to ${data['product_price']}")
        assert status == 200
        assert data["product_price"] == 649.99

        # Seed more items for category filtering and pagination
        make_request("POST", "/api/products/", {
            "product_name": "Wireless Soundbar",
            "product_price": 149.99,
            "stock_quantity": 30,
            "product_category": "Electronics",
            "product_status": "Active"
        })
        make_request("POST", "/api/products/", {
            "product_name": "Denim Jacket",
            "product_price": 89.99,
            "stock_quantity": 40,
            "product_category": "Apparel",
            "product_status": "Active"
        })
        make_request("POST", "/api/products/", {
            "product_name": "Cotton Polo Shirt",
            "product_price": 29.99,
            "stock_quantity": 60,
            "product_category": "Apparel",
            "product_status": "Active"
        })

        # 10. GET /api/products/?category=Apparel
        status, data = make_request("GET", "/api/products/?category=Apparel")
        print(f"[Check 10] GET /api/products/?category=Apparel -> HTTP {status}: Found {len(data)} items")
        assert status == 200
        assert len(data) == 2

        # 11. GET /api/products/?skip=1&limit=2 (Pagination)
        status, data = make_request("GET", "/api/products/?skip=1&limit=2")
        print(f"[Check 11] GET /api/products/?skip=1&limit=2 -> HTTP {status}: Got page of {len(data)} items")
        assert status == 200
        assert len(data) == 2

        # 12. DELETE /api/products/{product_id}
        status, data = make_request("DELETE", f"/api/products/{prod_id}")
        print(f"[Check 12] DELETE /api/products/{prod_id} -> HTTP {status}: {data['message']}")
        assert status == 200

        # 13. GET /api/products/{product_id} (Verify deleted is 404)
        status, data = make_request("GET", f"/api/products/{prod_id}")
        print(f"[Check 13] GET deleted /api/products/{prod_id} -> HTTP {status} (Expected 404)")
        assert status == 404

        print("\n" + "=" * 70)
        print("ALL END-TO-END REST APIS TESTED SUCCESSFULLY ON PORT 8003!")
        print("=" * 70)

    finally:
        server.stop()
        print("Uvicorn test server stopped cleanly.")


if __name__ == "__main__":
    main()
