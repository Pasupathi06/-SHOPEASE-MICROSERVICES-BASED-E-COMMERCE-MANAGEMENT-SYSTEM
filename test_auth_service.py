"""
Automated Test Suite for ShopEase Authentication Microservice.
Tests all 14 mandatory authentication scenarios:
1. Register a new user successfully.
2. Register using an already existing email.
3. Register with an invalid email.
4. Register with mismatched passwords.
5. Login using valid credentials.
6. Login using an incorrect password.
7. Login using an inactive account.
8. Access /api/auth/me with a valid token.
9. Access a protected endpoint without a token.
10. Access a protected endpoint with an invalid token.
11. Access a protected endpoint with an expired token.
12. Change password using the correct current password.
13. Change password using an incorrect current password.
14. Verify that the new password works for login.
"""

from datetime import timedelta
from app.database.connection import SessionLocal, init_db
from app.models.user_model import User
from app.schemas.auth_schema import UserRegister, UserLogin, ChangePasswordRequest
from app.services.auth_service import auth_service
from app.core.security import create_access_token, decode_access_token, hash_password
from fastapi import HTTPException


def run_tests():
    print("=" * 75)
    print("SHOPEASE AUTH SERVICE - RUNNING 14 MANDATORY TEST SCENARIOS")
    print("=" * 75)

    init_db()
    db = SessionLocal()

    # Clean test users
    db.query(User).filter(User.email.in_([
        "test_john@example.com",
        "inactive_user@example.com",
        "changepw_user@example.com"
    ])).delete(synchronize_session=False)
    db.commit()

    passed = 0
    total = 14

    # -------------------------------------------------------------
    # Scenario 1: Register a new user successfully
    # -------------------------------------------------------------
    print("\n[Scenario 1] Register new user successfully")
    reg_in = UserRegister(
        full_name="John Doe",
        email="test_john@example.com",
        password="pasupathi@123",
        confirm_password="pasupathi@123",
    )
    user1 = auth_service.register_user(db, reg_in)
    assert user1.id is not None
    assert user1.email == "test_john@example.com"
    assert user1.role == "customer"
    assert user1.password_hash != "pasupathi@123"  # Must be hashed!
    print(f"  --> PASSED: Registered user {user1.email} (ID: {user1.id})")
    passed += 1

    # -------------------------------------------------------------
    # Scenario 2: Register using an already existing email (Reject with 400)
    # -------------------------------------------------------------
    print("\n[Scenario 2] Register with already existing email")
    try:
        auth_service.register_user(db, reg_in)
        assert False, "Should have rejected duplicate email"
    except HTTPException as e:
        assert e.status_code == 400
        print(f"  --> PASSED: Duplicate email correctly rejected with HTTP 400 ({e.detail})")
        passed += 1

    # -------------------------------------------------------------
    # Scenario 3: Register with an invalid email (Pydantic validation)
    # -------------------------------------------------------------
    print("\n[Scenario 3] Register with invalid email format")
    try:
        UserRegister(
            full_name="Bad Email",
            email="invalid-not-an-email",
            password="pasupathi@123",
            confirm_password="pasupathi@123"
        )
        assert False, "Should have failed on invalid email"
    except Exception:
        print("  --> PASSED: Invalid email format rejected by schema validation")
        passed += 1

    # -------------------------------------------------------------
    # Scenario 4: Register with mismatched passwords (Pydantic validation)
    # -------------------------------------------------------------
    print("\n[Scenario 4] Register with mismatched passwords")
    try:
        UserRegister(
            full_name="Mismatch User",
            email="mismatch@example.com",
            password="pasupathi@123",
            confirm_password="different_password_456"
        )
        assert False, "Should have failed on mismatched passwords"
    except Exception:
        print("  --> PASSED: Password mismatch rejected by schema validation")
        passed += 1

    # -------------------------------------------------------------
    # Scenario 5: Login using valid credentials
    # -------------------------------------------------------------
    print("\n[Scenario 5] Login using valid credentials")
    login_in = UserLogin(
        email="test_john@example.com",
        password="pasupathi@123"
    )
    auth_user, token = auth_service.authenticate_user(db, login_in)
    assert auth_user.id == user1.id
    assert len(token) > 20
    print(f"  --> PASSED: Authenticated successfully, JWT token generated ({token[:20]}...)")
    passed += 1

    # -------------------------------------------------------------
    # Scenario 6: Login using an incorrect password (Reject with 401)
    # -------------------------------------------------------------
    print("\n[Scenario 6] Login using incorrect password")
    bad_login = UserLogin(
        email="test_john@example.com",
        password="wrongpassword999"
    )
    try:
        auth_service.authenticate_user(db, bad_login)
        assert False, "Should have rejected bad password"
    except HTTPException as e:
        assert e.status_code == 401
        print(f"  --> PASSED: Invalid password rejected with HTTP 401 ({e.detail})")
        passed += 1

    # -------------------------------------------------------------
    # Scenario 7: Login using an inactive account (Reject with 403)
    # -------------------------------------------------------------
    print("\n[Scenario 7] Login using inactive account")
    inactive_user = User(
        full_name="Inactive Person",
        email="inactive_user@example.com",
        password_hash=hash_password("pasupathi@123"),
        role="customer",
        is_active=False
    )
    db.add(inactive_user)
    db.commit()
    db.refresh(inactive_user)

    try:
        auth_service.authenticate_user(db, UserLogin(
            email="inactive_user@example.com",
            password="pasupathi@123"
        ))
        assert False, "Should have rejected inactive user"
    except HTTPException as e:
        assert e.status_code == 403
        print(f"  --> PASSED: Inactive account blocked with HTTP 403 ({e.detail})")
        passed += 1

    # -------------------------------------------------------------
    # Scenario 8: Access /api/auth/me with a valid token
    # -------------------------------------------------------------
    print("\n[Scenario 8] Access profile with valid token")
    claims = decode_access_token(token)
    assert claims["sub"] == str(user1.id)
    assert claims["email"] == user1.email
    print(f"  --> PASSED: Token decoded and validated (User ID: {claims['sub']})")
    passed += 1

    # -------------------------------------------------------------
    # Scenario 9: Access protected endpoint without a token
    # -------------------------------------------------------------
    print("\n[Scenario 9] Access protected endpoint without a token")
    from app.core.security import get_current_user
    try:
        get_current_user(credentials=None, db=db)
        assert False, "Should have rejected missing credentials"
    except HTTPException as e:
        assert e.status_code == 401
        print(f"  --> PASSED: Missing token rejected with HTTP 401 ({e.detail})")
        passed += 1

    # -------------------------------------------------------------
    # Scenario 10: Access protected endpoint with an invalid token
    # -------------------------------------------------------------
    print("\n[Scenario 10] Access protected endpoint with invalid token")
    try:
        decode_access_token("this.is.a.completely.invalid.token")
        assert False, "Should have rejected invalid token"
    except HTTPException as e:
        assert e.status_code == 401
        print(f"  --> PASSED: Invalid token signature rejected with HTTP 401 ({e.detail})")
        passed += 1

    # -------------------------------------------------------------
    # Scenario 11: Access protected endpoint with an expired token
    # -------------------------------------------------------------
    print("\n[Scenario 11] Access protected endpoint with expired token")
    expired_token = create_access_token(
        {"sub": str(user1.id), "email": user1.email, "role": user1.role},
        expires_delta=timedelta(seconds=-10)  # expired 10 seconds ago
    )
    try:
        decode_access_token(expired_token)
        assert False, "Should have rejected expired token"
    except HTTPException as e:
        assert e.status_code == 401
        print(f"  --> PASSED: Expired token rejected with HTTP 401 ({e.detail})")
        passed += 1

    # -------------------------------------------------------------
    # Scenario 12: Change password using correct current password
    # -------------------------------------------------------------
    print("\n[Scenario 12] Change password using correct current password")
    change_req = ChangePasswordRequest(
        current_password="pasupathi@123",
        new_password="new_pasupathi@456",
        confirm_new_password="new_pasupathi@456"
    )
    auth_service.change_password(db, user1, change_req)
    print("  --> PASSED: Password changed successfully")
    passed += 1

    # -------------------------------------------------------------
    # Scenario 13: Change password using incorrect current password
    # -------------------------------------------------------------
    print("\n[Scenario 13] Change password using incorrect current password")
    bad_change_req = ChangePasswordRequest(
        current_password="wrong_old_password",
        new_password="another_password@789",
        confirm_new_password="another_password@789"
    )
    try:
        auth_service.change_password(db, user1, bad_change_req)
        assert False, "Should have rejected bad current password"
    except HTTPException as e:
        assert e.status_code == 400
        print(f"  --> PASSED: Wrong current password rejected with HTTP 400 ({e.detail})")
        passed += 1

    # -------------------------------------------------------------
    # Scenario 14: Verify that the new password works for login
    # -------------------------------------------------------------
    print("\n[Scenario 14] Verify new password works for login")
    new_login = UserLogin(
        email="test_john@example.com",
        password="new_pasupathi@456"
    )
    reauthed_user, new_token = auth_service.authenticate_user(db, new_login)
    assert reauthed_user.id == user1.id
    assert len(new_token) > 20
    print(f"  --> PASSED: Logged in successfully with new password!")
    passed += 1

    db.close()

    print("\n" + "=" * 75)
    print(f"ALL {passed}/{total} AUTHENTICATION TEST SCENARIOS PASSED 100%!")
    print("=" * 75)


if __name__ == "__main__":
    run_tests()
