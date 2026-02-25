import pytest
from app.products import service, models
from app.user.models import User

def test_create_product_service(db_session):
    # Create a user first
    user = User(username="testuser", email="test@example.com", hashed_password="hashedpassword")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    product_data = {
        "name": "Headphone Sony",
        "description": "Premium audio",
        "price": 250.0,
        "stock": 50,
        "user_id": user.id,
        "is_publish": True
    }
    product = service.create_product(db_session, product_data)
    assert product.id is not None
    assert product.name == "Headphone Sony"
    assert product.user_id == user.id
    
    # Verify in DB
    db_product = service.get_product_by_id(db_session, product.id)
    assert db_product.price == 250.0
