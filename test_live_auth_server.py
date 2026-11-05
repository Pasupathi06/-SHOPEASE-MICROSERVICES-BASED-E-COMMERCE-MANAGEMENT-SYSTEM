"""
Live Server Integration Test for ShopEase Auth Service on Port 8001.
Spawns Uvicorn server, executes HTTP requests against all endpoints, and verifies JWT flow.
"""

import time
import json
import urllib.request
import urllib.error
import threading
import uvicorn
from app.main import app

BASE_URL = "http://127.0.0.1:8001"


class ServerThread(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        config = uvicorn.Config(app=app, host="127.0.0.1", port=8001, log_level="warning")
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
    print("STARTING SHOPEASE AUTH LIVE SERVER ON PORT 8001...")
    print("=" * 70)

    server = ServerThread()
    server.start()

    ready = False
    for _ in range(25):
        try:
            status, data = make_request("GET", "/health")
            if status == 200 and data.get("status") == "healthy":
                ready = True
                print("Auth Server is UP and HEALTHY on http://127.0.0.1:8001!\n")
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

        # 2. Login with default credentials (pasu / pasupathi@123)
        status, data = make_request("POST", "/api/auth/login", {
            "email": "pasu@shopease.com",
            "password": "pasupathi@123"
        })
        print(f"[Check 2] POST /api/auth/login -> HTTP {status}: Token generated for {data['user']['email']}")
        assert status == 200
        jwt_token = data["access_token"]

        # 3. Access /api/auth/me with Bearer token
        status, data = make_request("GET", "/api/auth/me", token=jwt_token)
        print(f"[Check 3] GET /api/auth/me (with token) -> HTTP {status}: Hello {data['full_name']} ({data['role']})")
        assert status == 200
        assert data["email"] == "pasu@shopease.com"

        # 4. Access /api/auth/me without token (expect 401)
        status, data = make_request("GET", "/api/auth/me")
        print(f"[Check 4] GET /api/auth/me (no token) -> HTTP {status} (Expected 401)")
        assert status == 401

        # 5. Verify token endpoint
        status, data = make_request("POST", "/api/auth/verify-token", {"token": jwt_token})
        print(f"[Check 5] POST /api/auth/verify-token -> HTTP {status}: valid={data['valid']}")
        assert status == 200
        assert data["valid"] is True

        # 6. Register a new user
        import random
        rand_email = f"customer_{random.randint(1000, 9999)}@example.com"
        status, data = make_request("POST", "/api/auth/register", {
            "full_name": "New Customer",
            "email": rand_email,
            "password": "pasupathi@123",
            "confirm_password": "pasupathi@123"
        })
        print(f"[Check 6] POST /api/auth/register -> HTTP {status}: Registered {rand_email}")
        assert status == 201

        print("\n" + "=" * 70)
        print("ALL AUTHENTICATION LIVE ENDPOINTS TESTED AND VERIFIED ON PORT 8001!")
        print("=" * 70)

    finally:
        server.stop()
        print("Auth test server stopped cleanly.")


if __name__ == "__main__":
    main()
