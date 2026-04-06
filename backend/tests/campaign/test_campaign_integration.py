import pytest
from datetime import datetime, timedelta


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


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


def _today():
    return datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)


class TestCreateCampaign:
    def test_create_success(self, client):
        token = _setup_shopowner(client)

        start = _today().isoformat()
        end = (_today() + timedelta(days=3)).isoformat()

        resp = client.post("/campaign/", headers=_auth(token), json={
            "name": "Year End Sale",
            "start_time": start,
            "end_time": end,
        })

        assert resp.status_code == 201
        body = resp.json()
        assert body["message"] == "Campaign created successfully"
        assert body["data"]["name"] == "Year End Sale"
        assert body["data"]["is_active"] is True
        assert body["data"]["id"] is not None

    def test_create_empty_name(self, client):
        token = _setup_shopowner(client)

        resp = client.post("/campaign/", headers=_auth(token), json={
            "name": "   ",
            "start_time": _today().isoformat(),
            "end_time": (_today() + timedelta(days=3)).isoformat(),
        })

        assert resp.status_code == 400
        assert "message" in resp.json()

    def test_create_start_time_in_past(self, client):
        token = _setup_shopowner(client)

        resp = client.post("/campaign/", headers=_auth(token), json={
            "name": "Sale",
            "start_time": (_today() - timedelta(days=1)).isoformat(),
            "end_time": (_today() + timedelta(days=3)).isoformat(),
        })

        assert resp.status_code == 400

    def test_create_end_time_before_start(self, client):
        token = _setup_shopowner(client)

        resp = client.post("/campaign/", headers=_auth(token), json={
            "name": "Sale",
            "start_time": (_today() + timedelta(days=5)).isoformat(),
            "end_time": _today().isoformat(),
        })

        assert resp.status_code == 400

    def test_create_overlapping(self, client):
        token = _setup_shopowner(client)

        start = _today().isoformat()
        end = (_today() + timedelta(days=5)).isoformat()

        # Create first campaign
        resp1 = client.post("/campaign/", headers=_auth(token), json={
            "name": "First Sale",
            "start_time": start,
            "end_time": end,
        })
        assert resp1.status_code == 201

        # Try overlapping campaign
        resp2 = client.post("/campaign/", headers=_auth(token), json={
            "name": "Second Sale",
            "start_time": (_today() + timedelta(days=1)).isoformat(),
            "end_time": (_today() + timedelta(days=3)).isoformat(),
        })
        assert resp2.status_code == 400


class TestGetActiveCampaign:
    def test_get_active_success(self, client):
        token = _setup_shopowner(client)

        # Create campaign
        client.post("/campaign/", headers=_auth(token), json={
            "name": "Active Sale",
            "start_time": _today().isoformat(),
            "end_time": (_today() + timedelta(days=3)).isoformat(),
        })

        resp = client.get("/campaign/active")
        assert resp.status_code == 200
        body = resp.json()
        assert "data" in body
        assert isinstance(body["data"], list)

    def test_get_active_empty(self, client):
        # Tidak ada campaign aktif
        resp = client.get("/campaign/active")
        assert resp.status_code == 200
        body = resp.json()
        assert body["data"] == []


class TestUpdateCampaign:
    def test_update_success(self, client):
        token = _setup_shopowner(client)

        # Create campaign
        create_resp = client.post("/campaign/", headers=_auth(token), json={
            "name": "Old Name",
            "start_time": _today().isoformat(),
            "end_time": (_today() + timedelta(days=3)).isoformat(),
        })
        campaign_id = create_resp.json()["data"]["id"]

        # Update campaign
        new_end = (_today() + timedelta(days=5)).isoformat()
        resp = client.put(f"/campaign/{campaign_id}", headers=_auth(token), json={
            "name": "New Name",
            "start_time": _today().isoformat(),
            "end_time": new_end,
        })

        assert resp.status_code == 200
        body = resp.json()
        assert body["message"] == "Campaign updated successfully"
        assert body["data"]["name"] == "New Name"

    def test_update_not_found(self, client):
        token = _setup_shopowner(client)

        resp = client.put("/campaign/9999", headers=_auth(token), json={
            "name": "Name",
            "start_time": _today().isoformat(),
            "end_time": (_today() + timedelta(days=3)).isoformat(),
        })

        assert resp.status_code == 404

    def test_update_empty_name(self, client):
        token = _setup_shopowner(client)

        create_resp = client.post("/campaign/", headers=_auth(token), json={
            "name": "Campaign",
            "start_time": _today().isoformat(),
            "end_time": (_today() + timedelta(days=3)).isoformat(),
        })
        campaign_id = create_resp.json()["data"]["id"]

        resp = client.put(f"/campaign/{campaign_id}", headers=_auth(token), json={
            "name": "  ",
            "start_time": _today().isoformat(),
            "end_time": (_today() + timedelta(days=3)).isoformat(),
        })

        assert resp.status_code == 400


class TestToggleCampaignActive:
    def test_toggle_active_to_inactive(self, client):
        token = _setup_shopowner(client)

        create_resp = client.post("/campaign/", headers=_auth(token), json={
            "name": "Campaign",
            "start_time": _today().isoformat(),
            "end_time": (_today() + timedelta(days=3)).isoformat(),
            "is_active": True,
        })
        campaign_id = create_resp.json()["data"]["id"]

        resp = client.patch(f"/campaign/{campaign_id}/active", headers=_auth(token))

        assert resp.status_code == 200
        body = resp.json()
        assert body["message"] == "Campaign deactivated successfully"
        assert body["data"]["is_active"] is False

    def test_toggle_inactive_to_active(self, client):
        token = _setup_shopowner(client)

        create_resp = client.post("/campaign/", headers=_auth(token), json={
            "name": "Campaign",
            "start_time": _today().isoformat(),
            "end_time": (_today() + timedelta(days=3)).isoformat(),
            "is_active": False,
        })
        campaign_id = create_resp.json()["data"]["id"]

        resp = client.patch(f"/campaign/{campaign_id}/active", headers=_auth(token))
        assert resp.status_code == 200

    def test_toggle_not_found(self, client):
        token = _setup_shopowner(client)

        resp = client.patch("/campaign/9999/active", headers=_auth(token))
        assert resp.status_code == 404


class TestCampaignAuthorization:
    def test_create_without_token(self, client):
        resp = client.post("/campaign/", json={
            "name": "Sale",
            "start_time": _today().isoformat(),
            "end_time": (_today() + timedelta(days=3)).isoformat(),
        })
        assert resp.status_code == 401

    def test_update_without_token(self, client):
        resp = client.put("/campaign/1", json={
            "name": "Sale",
            "start_time": _today().isoformat(),
            "end_time": (_today() + timedelta(days=3)).isoformat(),
        })
        assert resp.status_code == 401

    def test_toggle_without_token(self, client):
        resp = client.patch("/campaign/1/active")
        assert resp.status_code == 401

    def test_get_active_without_token(self, client):
        # GET active campaign harus bisa diakses tanpa login (publik)
        resp = client.get("/campaign/active")
        assert resp.status_code == 200
