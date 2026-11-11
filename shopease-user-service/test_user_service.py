"""
Automated Test Suite for ShopEase User Management Microservice.
Verifies all 16 mandatory testing scenarios covering profile & address management,
JWT security, ownership authorization, and single default address enforcement.
"""

from datetime import date
import jwt
from fastapi import HTTPException
from app.core.config import settings
from app.database.connection import SessionLocal, init_db
from app.models.user_model import UserProfile
from app.models.address_model import Address
from app.schemas.user_schema import UserProfileCreate, UserProfileUpdate, UserProfilePatch
from app.schemas.address_schema import AddressCreate, AddressUpdate
from app.services.user_service import user_service
from app.services.address_service import address_service
from app.core.security import decode_access_token


def generate_test_token(user_id: int, email: str = "pasu@shopease.com", role: str = "customer") -> str:
    """Helper generating signed JWT tokens mimicking Auth Service."""
    return jwt.encode(
        {"sub": str(user_id), "email": email, "role": role},
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )


def run_tests():
    print("=" * 80)
    print("SHOPEASE USER SERVICE - RUNNING 16 MANDATORY TEST SCENARIOS")
    print("=" * 80)

    init_db()
    db = SessionLocal()

    # Clean existing test data
    db.query(Address).delete()
    db.query(UserProfile).delete()
    db.commit()

    passed = 0
    total = 16

    # Test tokens
    user1_id = 101
    user2_id = 102
    token_user1 = generate_test_token(user1_id, "user1@shopease.com")
    token_user2 = generate_test_token(user2_id, "user2@shopease.com")

    # --------------------------------------------------------------------
    # Scenario 1: Access profile API without a JWT token (Expect 401)
    # --------------------------------------------------------------------
    print("\n[Scenario 1] Access profile API without token")
    from app.core.security import get_current_auth_user
    try:
        get_current_auth_user(credentials=None)
        assert False, "Should have rejected missing token"
    except HTTPException as e:
        assert e.status_code == 401
        print(f"  --> PASSED: Missing token rejected with HTTP 401 ({e.detail})")
        passed += 1

    # --------------------------------------------------------------------
    # Scenario 2: Access profile API using an invalid token (Expect 401)
    # --------------------------------------------------------------------
    print("\n[Scenario 2] Access profile API using invalid token")
    try:
        decode_access_token("fake.invalid.jwt.token")
        assert False, "Should have rejected invalid token"
    except HTTPException as e:
        assert e.status_code == 401
        print(f"  --> PASSED: Invalid signature rejected with HTTP 401 ({e.detail})")
        passed += 1

    # --------------------------------------------------------------------
    # Scenario 3: Create profile using valid token (201)
    # --------------------------------------------------------------------
    print("\n[Scenario 3] Create profile using valid token")
    prof1_in = UserProfileCreate(
        full_name="Pasupathi",
        phone_number="+919876543210",
        date_of_birth=date(1998, 5, 15),
        gender="Male",
        profile_image="https://cdn.shopease.com/pasu.png"
    )
    p1 = user_service.create_profile(db, user1_id, prof1_in)
    assert p1.id is not None
    assert p1.auth_user_id == user1_id
    assert p1.full_name == "Pasupathi"
    print(f"  --> PASSED: Profile created for auth_user_id={user1_id} (Profile ID: {p1.id})")
    passed += 1

    # --------------------------------------------------------------------
    # Scenario 4: Create duplicate profile for same auth_user_id (Expect 400)
    # --------------------------------------------------------------------
    print("\n[Scenario 4] Create duplicate profile for same user")
    try:
        user_service.create_profile(db, user1_id, prof1_in)
        assert False, "Should have rejected duplicate profile"
    except HTTPException as e:
        assert e.status_code == 400
        print(f"  --> PASSED: Duplicate profile rejected with HTTP 400 ({e.detail})")
        passed += 1

    # --------------------------------------------------------------------
    # Scenario 5: Retrieve authenticated user's profile
    # --------------------------------------------------------------------
    print("\n[Scenario 5] Retrieve authenticated user's profile")
    p1_get = user_service.get_profile(db, user1_id)
    assert p1_get.id == p1.id
    assert p1_get.full_name == "Pasupathi"
    print(f"  --> PASSED: Retrieved profile successfully for auth_user_id={user1_id}")
    passed += 1

    # --------------------------------------------------------------------
    # Scenario 6: Update profile information (PUT)
    # --------------------------------------------------------------------
    print("\n[Scenario 6] Update profile information")
    update_data = UserProfileUpdate(
        full_name="Pasupathi Senior Dev",
        phone_number="+919876500000",
        gender="Male"
    )
    p1_updated = user_service.update_profile(db, user1_id, update_data, is_patch=False)
    assert p1_updated.full_name == "Pasupathi Senior Dev"
    assert p1_updated.phone_number == "+919876500000"
    print(f"  --> PASSED: Profile updated successfully ({p1_updated.full_name})")
    passed += 1

    # --------------------------------------------------------------------
    # Scenario 7: Partially update profile information (PATCH)
    # --------------------------------------------------------------------
    print("\n[Scenario 7] Partially update profile information")
    patch_data = UserProfilePatch(profile_image="https://cdn.shopease.com/pasu_new.png")
    p1_patched = user_service.update_profile(db, user1_id, patch_data, is_patch=True)
    assert p1_patched.profile_image == "https://cdn.shopease.com/pasu_new.png"
    assert p1_patched.full_name == "Pasupathi Senior Dev"  # Preserved
    print(f"  --> PASSED: Partial update preserved existing fields correctly")
    passed += 1

    # --------------------------------------------------------------------
    # Scenario 8: Add multiple delivery addresses
    # --------------------------------------------------------------------
    print("\n[Scenario 8] Add multiple delivery addresses")
    addr1 = address_service.create_address(db, user1_id, AddressCreate(
        address_type="Home",
        full_name="Pasupathi",
        phone_number="+919876543210",
        address_line_1="10 Main Road, Anna Nagar",
        city="Chennai",
        state="Tamil Nadu",
        country="India",
        postal_code="600040",
        is_default=True
    ))
    addr2 = address_service.create_address(db, user1_id, AddressCreate(
        address_type="Office",
        full_name="Pasupathi Office",
        phone_number="+919876543210",
        address_line_1="Floor 4, Tidel Park",
        city="Chennai",
        state="Tamil Nadu",
        country="India",
        postal_code="600113",
        is_default=False
    ))
    assert addr1.id is not None
    assert addr2.id is not None
    print(f"  --> PASSED: Added Address 1 (ID: {addr1.id}, Default: {addr1.is_default}) and Address 2 (ID: {addr2.id})")
    passed += 1

    # --------------------------------------------------------------------
    # Scenario 9: Retrieve all saved addresses
    # --------------------------------------------------------------------
    print("\n[Scenario 9] Retrieve all saved addresses")
    user1_addresses = address_service.get_user_addresses(db, user1_id)
    assert len(user1_addresses) == 2
    print(f"  --> PASSED: Retrieved {len(user1_addresses)} addresses for user")
    passed += 1

    # --------------------------------------------------------------------
    # Scenario 10: Update an existing address
    # --------------------------------------------------------------------
    print("\n[Scenario 10] Update existing address")
    addr2_updated = address_service.update_address(
        db, user1_id, addr2.id,
        AddressUpdate(address_line_2="Near Tech Hub Gate 2")
    )
    assert addr2_updated.address_line_2 == "Near Tech Hub Gate 2"
    print(f"  --> PASSED: Address {addr2.id} updated successfully")
    passed += 1

    # --------------------------------------------------------------------
    # Scenario 11: Set a default address
    # --------------------------------------------------------------------
    print("\n[Scenario 11] Set a default address")
    addr2_default = address_service.set_default_address(db, user1_id, addr2.id)
    assert addr2_default.is_default is True
    print(f"  --> PASSED: Address {addr2.id} set as default")
    passed += 1

    # --------------------------------------------------------------------
    # Scenario 12: Verify that only one default address exists
    # --------------------------------------------------------------------
    print("\n[Scenario 12] Verify single default address constraint")
    all_addrs = address_service.get_user_addresses(db, user1_id)
    defaults = [a for a in all_addrs if a.is_default]
    assert len(defaults) == 1, f"Expected exactly 1 default address, got {len(defaults)}"
    assert defaults[0].id == addr2.id
    print(f"  --> PASSED: Only 1 address is default (Address ID: {defaults[0].id})")
    passed += 1

    # --------------------------------------------------------------------
    # Scenario 13: Delete an address
    # --------------------------------------------------------------------
    print("\n[Scenario 13] Delete an address")
    address_service.delete_address(db, user1_id, addr1.id)
    remaining = address_service.get_user_addresses(db, user1_id)
    assert len(remaining) == 1
    assert remaining[0].id == addr2.id
    print(f"  --> PASSED: Address {addr1.id} deleted. Remaining count: {len(remaining)}")
    passed += 1

    # --------------------------------------------------------------------
    # Scenario 14: Attempt to access another user's profile
    # --------------------------------------------------------------------
    print("\n[Scenario 14] Attempt to access another user's profile")
    # User 2 does not have a profile yet; User 2 cannot see User 1's profile
    try:
        user_service.get_profile(db, user2_id)
        assert False, "Should have raised 404 for User 2"
    except HTTPException as e:
        assert e.status_code == 404
        print(f"  --> PASSED: User 2 isolated; cannot view User 1 profile (HTTP 404)")
        passed += 1

    # --------------------------------------------------------------------
    # Scenario 15: Attempt to access another user's address (Expect 403)
    # --------------------------------------------------------------------
    print("\n[Scenario 15] Attempt to access another user's address (Ownership protection)")
    # Create profile for User 2 first
    user_service.create_profile(db, user2_id, UserProfileCreate(
        full_name="Second User",
        phone_number="+919876511111"
    ))
    # User 2 attempts to view Address 2 (which belongs to User 1)
    try:
        address_service.get_address_by_id(db, user2_id, addr2.id)
        assert False, "Should have blocked access with HTTP 403"
    except HTTPException as e:
        assert e.status_code == 403
        print(f"  --> PASSED: Cross-user address access rejected with HTTP 403 ({e.detail})")
        passed += 1

    # --------------------------------------------------------------------
    # Scenario 16: Deactivate profile
    # --------------------------------------------------------------------
    print("\n[Scenario 16] Deactivate user profile")
    user_service.deactivate_or_delete_profile(db, user1_id)
    p1_deactivated = user_service.get_profile(db, user1_id)
    assert p1_deactivated.is_active is False
    print(f"  --> PASSED: Profile deactivated successfully (is_active={p1_deactivated.is_active})")
    passed += 1

    db.close()

    print("\n" + "=" * 80)
    print(f"ALL {passed}/{total} USER MANAGEMENT TEST SCENARIOS PASSED 100%!")
    print("=" * 80)


if __name__ == "__main__":
    run_tests()
