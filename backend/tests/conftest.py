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
        yield c
    app.dependency_overrides.clear()
