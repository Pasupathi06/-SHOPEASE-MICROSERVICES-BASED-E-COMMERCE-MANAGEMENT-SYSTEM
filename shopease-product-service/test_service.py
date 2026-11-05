"""
Unit Tests for ProductService and Pydantic Schemas.
Tests in-memory CRUD operations, unique IDs, category filtering, pagination, and data validations.
"""

import pytest
from pydantic import ValidationError
from app.services.product_service import (
    product_service,
    ProductNotFoundException,
)
from app.schemas.product_schema import (
    ProductCreate,
    ProductUpdate,
    ProductStatus,
)


def test_product_crud_service():
    product_service.clear()

    # 1. Test Create Product
    prod_in = ProductCreate(
        product_name="Wireless Keyboard",
        product_description="Bluetooth ergonomic keyboard",
        product_price=59.99,
        stock_quantity=30,
        product_category="Electronics",
        product_status=ProductStatus.ACTIVE,
    )
    created = product_service.create_product(prod_in)
    assert created.product_id == "PROD-1001"
    assert created.product_name == "Wireless Keyboard"
    assert created.product_price == 59.99
    assert created.stock_quantity == 30
    assert created.product_category == "Electronics"
    assert created.product_status == "Active"
    assert created.created_date is not None
    print("Test 1 Passed: create_product")

    # 2. Test Get By ID
    retrieved = product_service.get_product_by_id("PROD-1001")
    assert retrieved.product_name == "Wireless Keyboard"
    print("Test 2 Passed: get_product_by_id")

    # 3. Test Get Non-Existent ID
    try:
        product_service.get_product_by_id("PROD-9999")
        assert False, "Should have raised ProductNotFoundException"
    except ProductNotFoundException:
        print("Test 3 Passed: ProductNotFoundException on get")

    # 4. Test Update Product
    update_in = ProductUpdate(
        product_name="Wireless Keyboard v2",
        product_price=64.99,
        stock_quantity=25,
        product_status=ProductStatus.INACTIVE,
    )
    updated = product_service.update_product("PROD-1001", update_in)
    assert updated.product_name == "Wireless Keyboard v2"
    assert updated.product_price == 64.99
    assert updated.stock_quantity == 25
    assert updated.product_status == "Inactive"
    assert updated.product_category == "Electronics"  # preserved
    print("Test 4 Passed: update_product")

    # 5. Test Filter and Pagination
    product_service.create_product(ProductCreate(
        product_name="Gaming Mouse",
        product_price=49.99,
        stock_quantity=15,
        product_category="Electronics",
        product_status=ProductStatus.ACTIVE,
    ))
    product_service.create_product(ProductCreate(
        product_name="Cotton T-Shirt",
        product_price=19.99,
        stock_quantity=50,
        product_category="Clothing",
        product_status=ProductStatus.ACTIVE,
    ))

    # All products
    all_prods = product_service.get_all_products(skip=0, limit=10)
    assert len(all_prods) == 3
    print("Test 5 Passed: get_all_products count = 3")

    # Category filter
    elec_prods = product_service.get_all_products(category="electronics", skip=0, limit=10)
    assert len(elec_prods) == 2
    cloth_prods = product_service.get_all_products(category="Clothing", skip=0, limit=10)
    assert len(cloth_prods) == 1
    print("Test 6 Passed: category filtering")

    # Pagination
    paged = product_service.get_all_products(skip=1, limit=1)
    assert len(paged) == 1
    assert paged[0].product_id == "PROD-1002"
    print("Test 7 Passed: pagination (skip=1, limit=1)")

    # 6. Test Delete Product
    del_result = product_service.delete_product("PROD-1001")
    assert del_result is True
    assert len(product_service.get_all_products()) == 2
    try:
        product_service.get_product_by_id("PROD-1001")
        assert False, "Should have raised ProductNotFoundException"
    except ProductNotFoundException:
        print("Test 8 Passed: delete_product and 404 verification")

    # 7. Test Schema Validations
    # Empty name
    try:
        ProductCreate(
            product_name="   ",
            product_price=10.0,
            stock_quantity=5,
            product_category="Test",
        )
        assert False, "Should fail on whitespace name"
    except ValidationError:
        print("Test 9 Passed: reject whitespace name")

    # Negative price
    try:
        ProductCreate(
            product_name="Negative Price",
            product_price=-10.0,
            stock_quantity=5,
            product_category="Test",
        )
        assert False, "Should fail on negative price"
    except ValidationError:
        print("Test 10 Passed: reject negative price")

    # Zero price
    try:
        ProductCreate(
            product_name="Zero Price",
            product_price=0.0,
            stock_quantity=5,
            product_category="Test",
        )
        assert False, "Should fail on zero price"
    except ValidationError:
        print("Test 11 Passed: reject zero price")

    # Negative stock
    try:
        ProductCreate(
            product_name="Negative Stock",
            product_price=10.0,
            stock_quantity=-1,
            product_category="Test",
        )
        assert False, "Should fail on negative stock"
    except ValidationError:
        print("Test 12 Passed: reject negative stock")

    print("\nALL SERVICE AND SCHEMA UNIT TESTS PASSED PERFECTLY!")


if __name__ == "__main__":
    test_product_crud_service()
