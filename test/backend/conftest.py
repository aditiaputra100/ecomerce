from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[2]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from app.database import Base, get_db
from app.main import app

# Import models to register them with Base.metadata
from app.user import models as user_models
from app.products import models as product_models
from app.orders import models as order_models
from app.categories import models as category_models
from app.campaign import models as campaign_models


class ApiPrefixedClient:
    def __init__(self, client: TestClient):
        self._client = client

    def _prefix(self, path: str) -> str:
        return path if path.startswith("/api") else f"/api{path}"

    def get(self, path: str, *args, **kwargs):
        return self._client.get(self._prefix(path), *args, **kwargs)

    def post(self, path: str, *args, **kwargs):
        return self._client.post(self._prefix(path), *args, **kwargs)

    def put(self, path: str, *args, **kwargs):
        return self._client.put(self._prefix(path), *args, **kwargs)

    def patch(self, path: str, *args, **kwargs):
        return self._client.patch(self._prefix(path), *args, **kwargs)

    def delete(self, path: str, *args, **kwargs):
        return self._client.delete(self._prefix(path), *args, **kwargs)

    def __getattr__(self, name):
        return getattr(self._client, name)


# Use an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    """
    Creates a fresh database session for a test.
    """
    # Create the database tables
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        # Drop the tables after the test is done
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    """
    Creates a TestClient instance that uses the test database session.
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass # Session is closed in the db_session fixture

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield ApiPrefixedClient(c)
    app.dependency_overrides.clear()
