from app.config import Settings, settings


def _auth(token: str):
    return {"Authorization": f"Bearer {token}"}


def _register(client, username="milda", email="milda@example.com"):
    response = client.post(
        "/register",
        json={
            "username": username,
            "email": email,
            "password": "password123",
            "disable": False,
        },
    )
    assert response.status_code == 201, response.text
    return response


def _login(client, username="milda", password="password123"):
    response = client.post("/token", data={"username": username, "password": password})
    assert response.status_code == 200, response.text
    return response


class TestRegister:
    def test_register_sets_refresh_cookie_and_returns_session(self, client):
        response = _register(client)

        body = response.json()
        assert body["message"] == "User created successfully"
        assert body["data"]["access_token"]
        assert body["data"]["user"]["username"] == "milda"

        set_cookie = response.headers.get("set-cookie", "")
        assert settings.REFRESH_TOKEN_COOKIE_NAME in set_cookie
        assert "HttpOnly" in set_cookie
        assert f"Path={settings.REFRESH_TOKEN_COOKIE_PATH}" in set_cookie
        assert ("Secure" in set_cookie) is settings.REFRESH_TOKEN_COOKIE_SECURE
        assert f"SameSite={settings.REFRESH_TOKEN_COOKIE_SAMESITE}" in set_cookie

    def test_register_auto_login_allows_me_endpoint(self, client):
        response = _register(client)
        access_token = response.json()["data"]["access_token"]

        me_response = client.get("/user/me", headers=_auth(access_token))

        assert me_response.status_code == 200
        assert me_response.json()["data"]["username"] == "milda"

    def test_duplicate_register_rejected(self, client):
        _register(client)

        response = client.post(
            "/register",
            json={
                "username": "milda",
                "email": "milda2@example.com",
                "password": "password123",
                "disable": False,
            },
        )

        assert response.status_code == 409
        assert response.json()["success"] is False


class TestToken:
    def test_login_sets_cookie_and_returns_session(self, client):
        _register(client)
        response = _login(client)

        body = response.json()
        assert body["data"]["access_token"]
        assert body["data"]["user"]["username"] == "milda"

        set_cookie = response.headers.get("set-cookie", "")
        assert settings.REFRESH_TOKEN_COOKIE_NAME in set_cookie
        assert "HttpOnly" in set_cookie
        assert f"Path={settings.REFRESH_TOKEN_COOKIE_PATH}" in set_cookie
        assert ("Secure" in set_cookie) is settings.REFRESH_TOKEN_COOKIE_SECURE
        assert f"SameSite={settings.REFRESH_TOKEN_COOKIE_SAMESITE}" in set_cookie


class TestCookiePolicy:
    def test_development_defaults_to_http_safe_cookie_policy(self):
        test_settings = Settings(
            APP_ENV="development",
            SECRET_KEY="dev-secret",
            ALGORITHM="HS256",
            ACCESS_TOKEN_EXPIRE_MINUTES=15,
            MIDTRANS_SERVER_KEY="midtrans-server",
            MIDTRANS_CLIENT_KEY="midtrans-client",
        )

        assert test_settings.REFRESH_TOKEN_COOKIE_SECURE is False
        assert test_settings.REFRESH_TOKEN_COOKIE_SAMESITE == "lax"

    def test_production_forces_secure_cookie_policy(self):
        test_settings = Settings(
            APP_ENV="production",
            SECRET_KEY="prod-secret",
            ALGORITHM="HS256",
            ACCESS_TOKEN_EXPIRE_MINUTES=15,
            MIDTRANS_SERVER_KEY="midtrans-server",
            MIDTRANS_CLIENT_KEY="midtrans-client",
            REFRESH_TOKEN_COOKIE_SECURE=False,
            REFRESH_TOKEN_COOKIE_SAMESITE="lax",
        )

        assert test_settings.REFRESH_TOKEN_COOKIE_SECURE is True
        assert test_settings.REFRESH_TOKEN_COOKIE_SAMESITE == "strict"

    def test_login_wrong_password(self, client):
        _register(client)

        response = client.post("/token", data={"username": "milda", "password": "wrong"})

        assert response.status_code == 401
        assert response.json()["success"] is False


class TestRefresh:
    def test_refresh_rotates_cookie_and_returns_new_access_token(self, client):
        register_response = _register(client)
        first_access_token = register_response.json()["data"]["access_token"]

        response = client.post("/token/refresh")

        assert response.status_code == 200, response.text
        body = response.json()
        assert body["data"]["access_token"]
        assert body["data"]["access_token"] != first_access_token
        assert settings.REFRESH_TOKEN_COOKIE_NAME in response.headers.get("set-cookie", "")

    def test_refresh_without_cookie_rejected(self, client):
        client.cookies.clear()

        response = client.post("/token/refresh")

        assert response.status_code == 401
        assert response.json()["success"] is False


class TestLogout:
    def test_logout_clears_cookie(self, client):
        _register(client)

        response = client.post("/logout")

        assert response.status_code == 200
        assert response.json()["message"] == "Logged out successfully"
        assert settings.REFRESH_TOKEN_COOKIE_NAME in response.headers.get("set-cookie", "")
        assert client.cookies.get(settings.REFRESH_TOKEN_COOKIE_NAME) is None

    def test_logout_prevents_refresh(self, client):
        _register(client)
        client.post("/logout")

        response = client.post("/token/refresh")

        assert response.status_code == 401