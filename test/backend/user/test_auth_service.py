import pytest
from jose import jwt

from app.config import settings
from app.user import models, service


def _make_user(db_session, username="milda", email="milda@example.com", password="password123"):
    return service.create_user(
        username=username,
        email=email,
        password=password,
        disable=False,
        db=db_session,
    )


class TestAuthenticateUser:
    def test_authenticate_success(self, db_session):
        _make_user(db_session)

        user = service.authenticate_user("milda", "password123", db_session)

        assert user.username == "milda"

    def test_authenticate_wrong_password_raises(self, db_session):
        _make_user(db_session)

        with pytest.raises(Exception) as exc_info:
            service.authenticate_user("milda", "wrong-password", db_session)

        assert getattr(exc_info.value, "status_code", None) == 401


class TestIssueSession:
    def test_issue_session_creates_refresh_record_and_access_token(self, db_session):
        user = _make_user(db_session)

        result = service.issue_session(user, db_session)

        assert result.access_token
        assert result.refresh_token
        assert result.user.id == user.id
        assert db_session.query(models.RefreshSession).count() == 1

        payload = jwt.decode(result.access_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        assert payload["sub"] == "milda"
        assert "customer" in payload["scopes"]


class TestRotateSession:
    def test_rotate_session_replaces_token_hash(self, db_session):
        user = _make_user(db_session)
        issued = service.issue_session(user, db_session)
        old_session = db_session.query(models.RefreshSession).first()
        old_hash = old_session.token_hash

        rotated = service.rotate_session(issued.refresh_token, db_session)

        assert rotated.refresh_token != issued.refresh_token
        assert rotated.access_token != issued.access_token
        assert db_session.query(models.RefreshSession).count() == 1
        refreshed_session = db_session.query(models.RefreshSession).first()
        assert refreshed_session.token_hash != old_hash

    def test_rotate_invalid_token_raises(self, db_session):
        _make_user(db_session)

        with pytest.raises(Exception) as exc_info:
            service.rotate_session("invalid-token", db_session)

        assert getattr(exc_info.value, "status_code", None) == 401


class TestRevokeSession:
    def test_revoke_session_marks_session_revoked(self, db_session):
        user = _make_user(db_session)
        issued = service.issue_session(user, db_session)

        result = service.revoke_session(issued.refresh_token, db_session)

        assert result is True
        session = db_session.query(models.RefreshSession).first()
        assert session.revoked_at is not None

    def test_revoke_unknown_token_returns_false(self, db_session):
        _make_user(db_session)

        result = service.revoke_session("missing-token", db_session)

        assert result is False