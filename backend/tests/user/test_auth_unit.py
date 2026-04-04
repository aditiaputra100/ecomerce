import pytest
from app.user import utils

def test_password_hashing():
    password = "secret_password"
    hashed = utils.get_password_hash(password)
    assert hashed != password
    assert utils.verify_password(password, hashed) is True

def test_create_access_token():
    data = {"sub": "user@example.com"}
    token = utils.create_access_token(data)
    assert isinstance(token, str)
    assert len(token) > 0
