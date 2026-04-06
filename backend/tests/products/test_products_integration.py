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


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


def _create_category(client, token, name="Test Category"):
    resp = client.post("/categories/", headers=_auth(token), json={"name": name})
    assert resp.status_code == 201
    return resp.json()["data"]["id"]


def _create_product(client, token, category_id, name="Test Product", price=100.0, stock=10):
    return client.post(
        "/products/",
        headers=_auth(token),
        data={
            "name": name, "description": "Test description",
            "price": price, "stock": stock,
            "is_publish": True, "category_id": category_id,
        },
        files={"image": ("test.jpg", io.BytesIO(b"\xff\xd8\xff\xe0"), "image/jpeg")},
    )


class TestCreateProduct:
    """Test pembuatan produk melalui endpoint POST /products/."""

    def test_success(self, client):
        token = _setup_shopowner(client)
        cat_id = _create_category(client, token)

        resp = _create_product(client, token, cat_id, name="Mechanical Keyboard")

        assert resp.status_code == 201
        body = resp.json()
        data = body["data"]
        assert data["name"] == "Mechanical Keyboard"
        assert data["id"] is not None
        assert data["image_url"] is not None
        assert data["owner"]["username"] == "seller"

    def test_empty_name(self, client):
        token = _setup_shopowner(client)
        cat_id = _create_category(client, token)

        resp = client.post("/products/", headers=_auth(token),
            data={"name": "  ", "description": "d", "price": 100, "stock": 10,
                  "is_publish": True, "category_id": cat_id},
            files={"image": ("test.jpg", io.BytesIO(b"\xff\xd8"), "image/jpeg")},
        )
        assert resp.status_code == 400
        body = resp.json()
        assert body["success"] is False
        assert "Name cannot be empty" in body["message"]

    def test_invalid_price(self, client):
        token = _setup_shopowner(client)
        cat_id = _create_category(client, token)

        resp = client.post("/products/", headers=_auth(token),
            data={"name": "Product", "description": "d", "price": 0, "stock": 10,
                  "is_publish": True, "category_id": cat_id},
            files={"image": ("test.jpg", io.BytesIO(b"\xff\xd8"), "image/jpeg")},
        )
        assert resp.status_code == 400
        assert resp.json()["success"] is False

    def test_invalid_category(self, client):
        token = _setup_shopowner(client)

        resp = client.post("/products/", headers=_auth(token),
            data={"name": "Product", "description": "d", "price": 100, "stock": 10,
                  "is_publish": True, "category_id": 9999},
            files={"image": ("test.jpg", io.BytesIO(b"\xff\xd8"), "image/jpeg")},
        )
        assert resp.status_code == 400
        assert resp.json()["success"] is False

    def test_missing_image(self, client):
        token = _setup_shopowner(client)
        cat_id = _create_category(client, token)

        resp = client.post("/products/", headers=_auth(token),
            data={"name": "Product", "description": "d", "price": 100, "stock": 10,
                  "is_publish": True, "category_id": cat_id},
        )
        assert resp.status_code == 400
        assert resp.json()["success"] is False


class TestReadProduct:
    """Test endpoint GET /products/ dan GET /products/{id}."""

    def test_list_products(self, client):
        token = _setup_shopowner(client)
        cat_id = _create_category(client, token)

        _create_product(client, token, cat_id, name="Product A")
        _create_product(client, token, cat_id, name="Product B")

        resp = client.get("/products/")
        assert resp.status_code == 200
        body = resp.json()
        products = body["data"]
        assert len(products) == 2

    def test_get_product(self, client):
        token = _setup_shopowner(client)
        cat_id = _create_category(client, token)

        create_resp = _create_product(client, token, cat_id, name="Single Product")
        product_id = create_resp.json()["data"]["id"]

        resp = client.get(f"/products/{product_id}")
        assert resp.status_code == 200
        body = resp.json()
        assert body["data"]["name"] == "Single Product"

    def test_get_product_not_found(self, client):
        resp = client.get("/products/9999")
        assert resp.status_code == 404
        assert resp.json()["success"] is False


class TestUpdateProduct:
    """Test endpoint PUT /products/{id}."""

    def test_success(self, client):
        token = _setup_shopowner(client)
        cat_id = _create_category(client, token)

        create_resp = _create_product(client, token, cat_id, name="Old Name", price=100.0)
        product_id = create_resp.json()["data"]["id"]

        resp = client.put(f"/products/{product_id}", headers=_auth(token),
            data={"name": "New Name", "description": "Updated desc",
                  "price": 250.0, "stock": 20, "is_publish": True},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["data"]["name"] == "New Name"
        assert body["data"]["price"] == 250.0


class TestDeleteProduct:
    """Test endpoint DELETE /products/{id}."""

    def test_success(self, client):
        token = _setup_shopowner(client)
        cat_id = _create_category(client, token)

        create_resp = _create_product(client, token, cat_id, name="To Delete")
        product_id = create_resp.json()["data"]["id"]

        resp = client.delete(f"/products/{product_id}", headers=_auth(token))
        assert resp.status_code == 200
        body = resp.json()
        assert body["message"] == "Product deleted successfully"

    def test_deleted_product_not_accessible(self, client):
        token = _setup_shopowner(client)
        cat_id = _create_category(client, token)

        create_resp = _create_product(client, token, cat_id, name="To Delete")
        product_id = create_resp.json()["data"]["id"]

        client.delete(f"/products/{product_id}", headers=_auth(token))

        resp = client.get(f"/products/{product_id}")
        assert resp.status_code == 404
        assert resp.json()["success"] is False


class TestPublishProduct:
    """Test endpoint PATCH /products/{id}/publish."""

    def test_toggle_publish(self, client):
        token = _setup_shopowner(client)
        cat_id = _create_category(client, token)

        create_resp = _create_product(client, token, cat_id)
        product_id = create_resp.json()["data"]["id"]

        # Toggle: published → not published
        resp = client.patch(f"/products/{product_id}/publish", headers=_auth(token))
        assert resp.status_code == 200
        body = resp.json()
        assert body["message"] == "Product not published"

        # Toggle kembali: not published → published
        resp = client.patch(f"/products/{product_id}/publish", headers=_auth(token))
        assert resp.status_code == 200
        body = resp.json()
        assert body["message"] == "Product published"


class TestProductAuthorization:
    """Test otorisasi pada endpoint produk."""

    def test_unauthorized_create(self, client):
        resp = client.post("/products/",
            data={"name": "X", "description": "X", "price": 100, "stock": 10},
        )
        assert resp.status_code == 401

    def test_unauthorized_update(self, client):
        resp = client.put("/products/1",
            data={"name": "X", "description": "X", "price": 100, "stock": 10},
        )
        assert resp.status_code == 401

    def test_unauthorized_delete(self, client):
        resp = client.delete("/products/1")
        assert resp.status_code == 401

    def test_forbidden_delete_other_owner(self, client):
        token_a = _setup_shopowner(client, username="ownerA", email="a@test.com")
        token_b = _setup_shopowner(client, username="ownerB", email="b@test.com")
        cat_id = _create_category(client, token_a)

        create_resp = _create_product(client, token_a, cat_id, name="Owner A Product")
        product_id = create_resp.json()["data"]["id"]

        resp = client.delete(f"/products/{product_id}", headers=_auth(token_b))
        assert resp.status_code == 403
        assert resp.json()["success"] is False
