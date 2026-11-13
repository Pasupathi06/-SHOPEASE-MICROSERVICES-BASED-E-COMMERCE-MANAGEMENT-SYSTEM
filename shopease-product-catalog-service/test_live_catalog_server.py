"""
Live API HTTP Endpoint Verification Script for ShopEase Product Catalog Service.
Spins up a lightweight background server or queries port 8004.
"""

import urllib.request
import json

base_url = "http://127.0.0.1:8004"

def test_endpoint(url: str, description: str):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "ShopEase-Test-Client"})
        with urllib.request.urlopen(req, timeout=5) as response:
            status_code = response.getcode()
            body = response.read().decode("utf-8")
            print(f"[OK] {description}: Status {status_code}")
            return json.loads(body) if "json" in response.headers.get("Content-Type", "") else body
    except Exception as e:
        print(f"[ERROR] {description} ({url}): {e}")
        return None

if __name__ == "__main__":
    print("Testing live endpoints...")
    test_endpoint(f"{base_url}/", "Root Endpoint")
    test_endpoint(f"{base_url}/health", "Health Check Endpoint")
    test_endpoint(f"{base_url}/docs", "Swagger UI Docs")
    test_endpoint(f"{base_url}/api/categories", "Categories Listing")
    test_endpoint(f"{base_url}/api/products", "Products Listing")
