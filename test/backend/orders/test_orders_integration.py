import pytest
import io
from unittest.mock import patch


# ── Mock image I/O untuk semua test ──

@pytest.fixture(autouse=True)
def mock_image_ops():
    with patch("app.products.service.save_image", return_value="/static/uploads/products/test.jpg"):
        with patch("app.products.service.delete_image", return_value=True):
            yield


# === Helpers ===

def _auth(token):
    return {"Authorization": f"Bearer {token}"}


def _setup_shopowner(client, username="seller", email="seller@test.com"):
    """Register → login → create shop → re-login untuk dapat scope shopowner."""
    client.post("/register", json={
        "username": username, "email": email,
        "password": "password123", "disable": False,
    })
    login = client.post("/token", data={"username": username, "password": "password123"})
    token = login.json()["data"]["access_token"]

    client.post("/shops/", headers=_auth(token), data={
        "name": f"{username} Shop", "description": "Test shop",
    })

    login = client.post("/token", data={"username": username, "password": "password123"})
    return login.json()["data"]["access_token"]


def _setup_customer(client, username="buyer", email="buyer@test.com"):
    """Register → login → return token customer."""
    client.post("/register", json={
        "username": username, "email": email,
        "password": "password123", "disable": False,
    })
    login = client.post("/token", data={"username": username, "password": "password123"})
    return login.json()["data"]["access_token"]


def _create_category(client, token, name="Test Category"):
    """Create a product category."""
    resp = client.post("/categories/", headers=_auth(token), json={"name": name})
    assert resp.status_code == 201, resp.text
    return resp.json()["data"]["id"]


def _create_product(client, token, name="Test Product", price=100.0, stock=10):
    """Create a product with image mocked."""
    cat_id = _create_category(client, token, name=f"{name} Category")
    return client.post(
        "/products/",
        headers=_auth(token),
        data={
            "name": name, "description": "Test description",
            "price": price, "stock": stock, "is_publish": True, "category_id": cat_id,
        },
        files={"image": ("test.jpg", io.BytesIO(b"\xff\xd8\xff\xe0"), "image/jpeg")},
    )


# === Test Classes ===

class TestCreateOrder:
    """Test pembuatan order."""

    def test_create_order_success(self, client):
        # Setup seller & product
        seller_token = _setup_shopowner(client, username="seller1", email="seller1@test.com")
        prod_resp = _create_product(client, seller_token, name="Keyboard", price=100.0, stock=5)
        assert prod_resp.status_code == 201, prod_resp.text
        product_id = prod_resp.json()["data"]["id"]

        # Setup buyer
        buyer_token = _setup_customer(client, username="buyer1", email="buyer1@test.com")

        # Create order
        order_resp = client.post("/orders/", headers=_auth(buyer_token), json={
            "items": [{"product_id": product_id, "quantity": 3}]
        })
        assert order_resp.status_code == 201, order_resp.text
        body = order_resp.json()
        order = body["data"]
        assert order["total_price"] == 300.0
        assert order["status"] == "pending"

    def test_create_order_product_not_found(self, client):
        buyer_token = _setup_customer(client, username="buyer2", email="buyer2@test.com")

        order_resp = client.post("/orders/", headers=_auth(buyer_token), json={
            "items": [{"product_id": 9999, "quantity": 1}]
        })
        assert order_resp.status_code == 400
        body = order_resp.json()
        assert body["success"] is False
        assert "not found" in body["message"].lower()

    def test_create_order_insufficient_stock(self, client):
        # Setup seller & product
        seller_token = _setup_shopowner(client, username="seller2", email="seller2@test.com")
        prod_resp = _create_product(client, seller_token, name="Mouse", price=50.0, stock=2)
        assert prod_resp.status_code == 201
        product_id = prod_resp.json()["data"]["id"]

        # Setup buyer
        buyer_token = _setup_customer(client, username="buyer3", email="buyer3@test.com")

        # Try to order more than available
        order_resp = client.post("/orders/", headers=_auth(buyer_token), json={
            "items": [{"product_id": product_id, "quantity": 5}]
        })
        assert order_resp.status_code == 400
        body = order_resp.json()
        assert body["success"] is False
        assert "insufficient stock" in body["message"].lower()

    def test_prevent_self_purchase(self, client):
        seller_token = _setup_shopowner(client, username="seller3", email="seller3@test.com")
        prod_resp = _create_product(client, seller_token, name="Monitor", price=200.0, stock=10)
        assert prod_resp.status_code == 201
        product_id = prod_resp.json()["data"]["id"]

        # Seller tries to buy own product
        order_resp = client.post("/orders/", headers=_auth(seller_token), json={
            "items": [{"product_id": product_id, "quantity": 1}]
        })
        assert order_resp.status_code == 400
        body = order_resp.json()
        assert body["success"] is False
        assert "cannot buy your own product" in body["message"].lower()

    def test_allow_duplicate_orders(self, client):
        """After removal of duplicate check, user can order same products multiple times."""
        seller_token = _setup_shopowner(client, username="seller4", email="seller4@test.com")
        prod_resp = _create_product(client, seller_token, name="Headset", price=80.0, stock=20)
        assert prod_resp.status_code == 201
        product_id = prod_resp.json()["data"]["id"]

        buyer_token = _setup_customer(client, username="buyer4", email="buyer4@test.com")

        # First order
        order1 = client.post("/orders/", headers=_auth(buyer_token), json={
            "items": [{"product_id": product_id, "quantity": 2}]
        })
        assert order1.status_code == 201

        # Second order (same product, should succeed now)
        order2 = client.post("/orders/", headers=_auth(buyer_token), json={
            "items": [{"product_id": product_id, "quantity": 2}]
        })
        assert order2.status_code == 201, order2.text


class TestCancelOrder:
    """Test pembatalan order."""

    def test_cancel_pending_order(self, client):
        # Setup seller & product
        seller_token = _setup_shopowner(client, username="seller5", email="seller5@test.com")
        prod_resp = _create_product(client, seller_token, name="Keyboard", price=100.0, stock=10)
        assert prod_resp.status_code == 201
        product_id = prod_resp.json()["data"]["id"]

        # Setup buyer
        buyer_token = _setup_customer(client, username="buyer5", email="buyer5@test.com")

        # Create order
        order_resp = client.post("/orders/", headers=_auth(buyer_token), json={
            "items": [{"product_id": product_id, "quantity": 3}]
        })
        assert order_resp.status_code == 201
        order_id = order_resp.json()["data"]["id"]

        # Cancel order
        cancel_resp = client.delete(f"/orders/{order_id}", headers=_auth(buyer_token))
        assert cancel_resp.status_code == 200
        body = cancel_resp.json()
        assert "Success delete order" in body["message"]

        # Verify order status is deleted
        orders_resp = client.get("/orders/", headers=_auth(buyer_token))
        orders = orders_resp.json()["data"]
        order = next(o for o in orders if o["id"] == order_id)
        assert order["status"] == "deleted"

        # Verify stock is restored
        prod_list = client.get("/products/")
        product = next(p for p in prod_list.json()["data"] if p["id"] == product_id)
        assert product["stock"] == 10  # 10 - 3 + 3 = 10

    def test_cancel_non_pending_order(self, client):
        # Setup seller & product
        seller_token = _setup_shopowner(client, username="seller6", email="seller6@test.com")
        prod_resp = _create_product(client, seller_token, name="Mouse", price=50.0, stock=10)
        assert prod_resp.status_code == 201
        product_id = prod_resp.json()["data"]["id"]

        # Setup buyer
        buyer_token = _setup_customer(client, username="buyer6", email="buyer6@test.com")

        # Create order
        order_resp = client.post("/orders/", headers=_auth(buyer_token), json={
            "items": [{"product_id": product_id, "quantity": 2}]
        })
        assert order_resp.status_code == 201
        order_id = order_resp.json()["data"]["id"]

        # Change status to processing
        status_resp = client.patch(
            f"/orders/{order_id}/status",
            headers=_auth(seller_token),
            json={"status": "processing"}
        )
        assert status_resp.status_code == 200

        # Try to cancel non-pending order
        cancel_resp = client.delete(f"/orders/{order_id}", headers=_auth(buyer_token))
        assert cancel_resp.status_code == 400
        body = cancel_resp.json()
        assert body["success"] is False
        assert "only pending" in body["message"].lower()

    def test_cancel_order_not_found(self, client):
        buyer_token = _setup_customer(client, username="buyer7", email="buyer7@test.com")

        cancel_resp = client.delete(f"/orders/9999", headers=_auth(buyer_token))
        assert cancel_resp.status_code == 400
        body = cancel_resp.json()
        assert body["success"] is False
        assert "not found" in body["message"].lower()

    def test_cancel_other_user_order(self, client):
        # Setup seller & product
        seller_token = _setup_shopowner(client, username="seller7", email="seller7@test.com")
        prod_resp = _create_product(client, seller_token, name="Monitor", price=200.0, stock=10)
        assert prod_resp.status_code == 201
        product_id = prod_resp.json()["data"]["id"]

        # Setup buyer A
        buyer_a_token = _setup_customer(client, username="buyerA", email="buyerA@test.com")

        # Setup buyer B
        buyer_b_token = _setup_customer(client, username="buyerB", email="buyerB@test.com")

        # Buyer A creates order
        order_resp = client.post("/orders/", headers=_auth(buyer_a_token), json={
            "items": [{"product_id": product_id, "quantity": 1}]
        })
        assert order_resp.status_code == 201
        order_id = order_resp.json()["data"]["id"]

        # Buyer B tries to cancel buyer A's order
        cancel_resp = client.delete(f"/orders/{order_id}", headers=_auth(buyer_b_token))
        assert cancel_resp.status_code == 403
        body = cancel_resp.json()
        assert body["success"] is False
        assert "not allowed" in body["message"].lower()


class TestListOrders:
    """Test daftar order."""

    def test_list_user_orders(self, client):
        seller_token = _setup_shopowner(client, username="seller8", email="seller8@test.com")
        prod_resp = _create_product(client, seller_token, name="Keyboard", price=100.0, stock=10)
        assert prod_resp.status_code == 201
        product_id = prod_resp.json()["data"]["id"]

        buyer_token = _setup_customer(client, username="buyer8", email="buyer8@test.com")

        # Create 2 orders
        order1 = client.post("/orders/", headers=_auth(buyer_token), json={
            "items": [{"product_id": product_id, "quantity": 1}]
        })
        assert order1.status_code == 201

        order2 = client.post("/orders/", headers=_auth(buyer_token), json={
            "items": [{"product_id": product_id, "quantity": 2}]
        })
        assert order2.status_code == 201

        # List orders
        list_resp = client.get("/orders/", headers=_auth(buyer_token))
        assert list_resp.status_code == 200
        body = list_resp.json()
        orders = body["data"]
        assert len(orders) == 2

    def test_list_shop_orders(self, client):
        seller_token = _setup_shopowner(client, username="seller9", email="seller9@test.com")
        prod_resp = _create_product(client, seller_token, name="Mouse", price=50.0, stock=10)
        assert prod_resp.status_code == 201
        product_id = prod_resp.json()["data"]["id"]

        buyer_token = _setup_customer(client, username="buyer9", email="buyer9@test.com")

        # Create order
        order_resp = client.post("/orders/", headers=_auth(buyer_token), json={
            "items": [{"product_id": product_id, "quantity": 2}]
        })
        assert order_resp.status_code == 201
        order_id = order_resp.json()["data"]["id"]

        # Seller lists shop orders
        shop_orders = client.get("/orders/shop", headers=_auth(seller_token))
        assert shop_orders.status_code == 200
        body = shop_orders.json()
        orders = body["data"]
        assert len(orders) == 1
        assert orders[0]["id"] == order_id
        assert orders[0]["owner"]["username"] == "buyer9"


class TestOrderStatus:
    """Test perubahan status order."""

    def test_seller_update_status(self, client):
        seller_token = _setup_shopowner(client, username="seller10", email="seller10@test.com")
        prod_resp = _create_product(client, seller_token, name="Keyboard", price=100.0, stock=10)
        assert prod_resp.status_code == 201
        product_id = prod_resp.json()["data"]["id"]

        buyer_token = _setup_customer(client, username="buyer10", email="buyer10@test.com")

        # Create order
        order_resp = client.post("/orders/", headers=_auth(buyer_token), json={
            "items": [{"product_id": product_id, "quantity": 1}]
        })
        assert order_resp.status_code == 201
        order_id = order_resp.json()["data"]["id"]

        # Seller updates to processing
        status_resp = client.patch(
            f"/orders/{order_id}/status",
            headers=_auth(seller_token),
            json={"status": "processing"}
        )
        assert status_resp.status_code == 200
        body = status_resp.json()
        assert body["data"]["status"] == "processing"

        # Seller updates to shipped
        status_resp = client.patch(
            f"/orders/{order_id}/status",
            headers=_auth(seller_token),
            json={"status": "shipped"}
        )
        assert status_resp.status_code == 200
        body = status_resp.json()
        assert body["data"]["status"] == "shipped"

    def test_buyer_complete_order(self, client):
        seller_token = _setup_shopowner(client, username="seller11", email="seller11@test.com")
        prod_resp = _create_product(client, seller_token, name="Mouse", price=50.0, stock=10)
        assert prod_resp.status_code == 201
        product_id = prod_resp.json()["data"]["id"]

        buyer_token = _setup_customer(client, username="buyer11", email="buyer11@test.com")

        # Create order
        order_resp = client.post("/orders/", headers=_auth(buyer_token), json={
            "items": [{"product_id": product_id, "quantity": 1}]
        })
        assert order_resp.status_code == 201
        order_id = order_resp.json()["data"]["id"]

        # Seller sets to shipped
        client.patch(
            f"/orders/{order_id}/status",
            headers=_auth(seller_token),
            json={"status": "processing"}
        )
        client.patch(
            f"/orders/{order_id}/status",
            headers=_auth(seller_token),
            json={"status": "shipped"}
        )

        # Buyer completes order
        complete_resp = client.patch(
            f"/orders/{order_id}/status",
            headers=_auth(buyer_token),
            json={"status": "completed"}
        )
        assert complete_resp.status_code == 200
        body = complete_resp.json()
        assert body["data"]["status"] == "completed"

    def test_buyer_cannot_set_shipped(self, client):
        seller_token = _setup_shopowner(client, username="seller12", email="seller12@test.com")
        prod_resp = _create_product(client, seller_token, name="Monitor", price=200.0, stock=10)
        assert prod_resp.status_code == 201
        product_id = prod_resp.json()["data"]["id"]

        buyer_token = _setup_customer(client, username="buyer12", email="buyer12@test.com")

        # Create order
        order_resp = client.post("/orders/", headers=_auth(buyer_token), json={
            "items": [{"product_id": product_id, "quantity": 1}]
        })
        assert order_resp.status_code == 201
        order_id = order_resp.json()["data"]["id"]

        # Buyer tries to set to shipped (should fail)
        fail_resp = client.patch(
            f"/orders/{order_id}/status",
            headers=_auth(buyer_token),
            json={"status": "shipped"}
        )
        assert fail_resp.status_code == 403
        assert fail_resp.json()["success"] is False


class TestOrderAuthorization:
    """Test otentikasi & otorisasi."""

    def test_create_order_without_token(self, client):
        order_resp = client.post("/orders/", json={
            "items": [{"product_id": 1, "quantity": 1}]
        })
        assert order_resp.status_code == 401

    def test_list_orders_without_token(self, client):
        list_resp = client.get("/orders/")
        assert list_resp.status_code == 401
