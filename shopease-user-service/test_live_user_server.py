"""
Live Server Integration Test for ShopEase User Service on Port 8002.
Spawns Uvicorn server, executes HTTP requests against Profile & Address endpoints,
and validates JWT authentication and responses.
"""

import time
import json
import urllib.request
import urllib.error
import threading
import uvicorn
import jwt
from app.main import app
from app.core.config import settings

BASE_URL = "http://127.0.0.1:8002"


def generate_token(user_id: int = 1, email: str = "pasu@shopease.com"):
    return jwt.encode(
        {"sub": str(user_id), "email": email, "role": "customer"},
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )


class ServerThread(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        config = uvicorn.Config(app=app, host="127.0.0.1", port=8002, log_level="warning")
        self.server = uvicorn.Server(config)

    def run(self):
        self.server.run()

    def stop(self):
        self.server.should_exit = True


def make_request(method, path, body=None, token=None):
    url = f"{BASE_URL}{path}"
    data = json.dumps(body).encode("utf-8") if body is not None else None
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
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
    print("STARTING SHOPEASE USER SERVICE LIVE ON PORT 8002...")
    print("=" * 70)

    server = ServerThread()
    server.start()

    ready = False
    for _ in range(25):
        try:
            status, data = make_request("GET", "/health")
            if status == 200 and data.get("status") == "healthy":
                ready = True
                print("User Service is UP and HEALTHY on http://127.0.0.1:8002!\n")
                break
        except Exception:
            time.sleep(0.3)

    if not ready:
        print("ERROR: Server failed to start.")
        server.stop()
        return

    try:
        # 1. Health check
        status, data = make_request("GET", "/health")
        print(f"[Check 1] GET /health -> HTTP {status}: {data}")
        assert status == 200

        # Token for test user 201
        test_token = generate_token(201, "pasu_user201@shopease.com")

        # 2. Access profile without token (expect 401)
        status, data = make_request("GET", "/api/users/profile")
        print(f"[Check 2] GET /api/users/profile (no token) -> HTTP {status} (Expected 401)")
        assert status == 401

        # 3. Create profile
        prof_payload = {
            "full_name": "Pasupathi User",
            "phone_number": "+919876543210",
            "date_of_birth": "1998-05-15",
            "gender": "Male",
            "profile_image": "https://cdn.shopease.com/pasu.png"
        }
        status, data = make_request("POST", "/api/users/profile", prof_payload, token=test_token)
        print(f"[Check 3] POST /api/users/profile -> HTTP {status}: Created profile for {data['full_name']}")
        assert status == 201

        # 4. Get profile
        status, data = make_request("GET", "/api/users/profile", token=test_token)
        print(f"[Check 4] GET /api/users/profile -> HTTP {status}: Phone: {data['phone_number']}")
        assert status == 200
        assert data["full_name"] == "Pasupathi User"

        # 5. Add Address
        addr_payload = {
            "address_type": "Home",
            "full_name": "Pasupathi",
            "phone_number": "+919876543210",
            "address_line_1": "100 IT Expressway",
            "city": "Chennai",
            "state": "Tamil Nadu",
            "country": "India",
            "postal_code": "600096",
            "is_default": True
        }
        status, data = make_request("POST", "/api/users/addresses", addr_payload, token=test_token)
        print(f"[Check 5] POST /api/users/addresses -> HTTP {status}: Created Address ID {data['id']}")
        assert status == 201
        addr_id = data["id"]

        # 6. List Addresses
        status, data = make_request("GET", "/api/users/addresses", token=test_token)
        print(f"[Check 6] GET /api/users/addresses -> HTTP {status}: {len(data)} address(es) listed")
        assert status == 200
        assert len(data) >= 1

        # 7. Get Address by ID
        status, data = make_request("GET", f"/api/users/addresses/{addr_id}", token=test_token)
        print(f"[Check 7] GET /api/users/addresses/{addr_id} -> HTTP {status}: {data['city']}, {data['state']}")
        assert status == 200

        print("\n" + "=" * 70)
        print("ALL USER SERVICE LIVE ENDPOINTS TESTED AND VERIFIED ON PORT 8002!")
        print("=" * 70)

    finally:
        server.stop()
        print("User test server stopped cleanly.")


if __name__ == "__main__":
    main()
