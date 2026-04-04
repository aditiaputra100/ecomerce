import pytest


# === Helpers ===

def _setup_shopowner(client, username="seller", email="seller@test.com"):
    """Register → login → create shop → re-login untuk dapat scope shopowner."""
    client.post("/register", json={
        "username": username, "email": email,
        "password": "password123", "disable": False,
    })
    login = client.post("/token", data={"username": username, "password": "password123"})
    token = login.json()["access_token"]

    client.post("/shops/", headers=_auth(token), data={
        "name": f"{username} Shop", "description": "Test shop",
    })

    login = client.post("/token", data={"username": username, "password": "password123"})
    return login.json()["access_token"]


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


class TestCreateCategory:
    """Test pembuatan kategori melalui endpoint POST /categories/."""

    def test_success(self, client):
        token = _setup_shopowner(client)

        resp = client.post("/categories/", headers=_auth(token), json={
            "name": "Elektronik", "description": "Semua barang elektronik",
        })

        assert resp.status_code == 201
        data = resp.json()
        assert data["id"] is not None
        assert data["name"] == "Elektronik"
        assert data["description"] == "Semua barang elektronik"

    def test_duplicate_name(self, client):
        token = _setup_shopowner(client)

        client.post("/categories/", headers=_auth(token), json={"name": "Pakaian"})

        resp = client.post("/categories/", headers=_auth(token), json={"name": "Pakaian"})
        assert resp.status_code == 409

    def test_empty_name(self, client):
        token = _setup_shopowner(client)

        resp = client.post("/categories/", headers=_auth(token), json={"name": "  "})
        assert resp.status_code == 400


class TestReadCategory:
    """Test endpoint GET /categories/ dan GET /categories/{id}."""

    def test_list_categories(self, client):
        token = _setup_shopowner(client)

        client.post("/categories/", headers=_auth(token), json={"name": "B-Olahraga"})
        client.post("/categories/", headers=_auth(token), json={"name": "A-Elektronik"})

        resp = client.get("/categories/")
        assert resp.status_code == 200
        categories = resp.json()
        assert len(categories) == 2
        assert categories[0]["name"] == "A-Elektronik"
        assert categories[1]["name"] == "B-Olahraga"

    def test_get_category(self, client):
        token = _setup_shopowner(client)

        create_resp = client.post("/categories/", headers=_auth(token), json={"name": "Makanan"})
        cat_id = create_resp.json()["id"]

        resp = client.get(f"/categories/{cat_id}")
        assert resp.status_code == 200
        assert resp.json()["name"] == "Makanan"

    def test_get_category_not_found(self, client):
        resp = client.get("/categories/9999")
        assert resp.status_code == 404


class TestUpdateCategory:
    """Test endpoint PUT /categories/{id}."""

    def test_success(self, client):
        token = _setup_shopowner(client)

        create_resp = client.post("/categories/", headers=_auth(token), json={
            "name": "Old Name", "description": "Old desc",
        })
        cat_id = create_resp.json()["id"]

        resp = client.put(f"/categories/{cat_id}", headers=_auth(token), json={
            "name": "New Name", "description": "Updated desc",
        })

        assert resp.status_code == 200
        assert resp.json()["name"] == "New Name"
        assert resp.json()["description"] == "Updated desc"

    def test_not_found(self, client):
        token = _setup_shopowner(client)

        resp = client.put("/categories/9999", headers=_auth(token), json={"name": "X"})
        assert resp.status_code == 404

    def test_duplicate_name(self, client):
        token = _setup_shopowner(client)

        client.post("/categories/", headers=_auth(token), json={"name": "Existing"})
        create_resp = client.post("/categories/", headers=_auth(token), json={"name": "ToUpdate"})
        cat_id = create_resp.json()["id"]

        resp = client.put(f"/categories/{cat_id}", headers=_auth(token), json={"name": "Existing"})
        assert resp.status_code == 409


class TestDeleteCategory:
    """Test endpoint DELETE /categories/{id}."""

    def test_success(self, client):
        token = _setup_shopowner(client)

        create_resp = client.post("/categories/", headers=_auth(token), json={"name": "To Delete"})
        cat_id = create_resp.json()["id"]

        resp = client.delete(f"/categories/{cat_id}", headers=_auth(token))
        assert resp.status_code == 204

    def test_deleted_category_not_accessible(self, client):
        token = _setup_shopowner(client)

        create_resp = client.post("/categories/", headers=_auth(token), json={"name": "To Delete"})
        cat_id = create_resp.json()["id"]

        client.delete(f"/categories/{cat_id}", headers=_auth(token))

        resp = client.get(f"/categories/{cat_id}")
        assert resp.status_code == 404

    def test_not_found(self, client):
        token = _setup_shopowner(client)

        resp = client.delete("/categories/9999", headers=_auth(token))
        assert resp.status_code == 404


class TestCategoryAuthorization:
    """Test otorisasi pada endpoint kategori."""

    def test_unauthorized_create(self, client):
        resp = client.post("/categories/", json={"name": "X"})
        assert resp.status_code == 401

    def test_unauthorized_update(self, client):
        resp = client.put("/categories/1", json={"name": "X"})
        assert resp.status_code == 401

    def test_unauthorized_delete(self, client):
        resp = client.delete("/categories/1")
        assert resp.status_code == 401

    def test_public_list_without_auth(self, client):
        resp = client.get("/categories/")
        assert resp.status_code == 200
