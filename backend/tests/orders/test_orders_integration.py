import pytest

def test_complete_checkout_flow(client):
    # 1. Setup Admin & Produk (Domain Auth & Products)
    # Register needs username and password >= 8 chars
    client.post("/register", json={"username": "admin", "email": "admin@test.com", "password": "password123", "disable": False})
    
    # Login needs scope="shopowner" to create products
    login = client.post("/token", data={"username": "admin", "password": "password123"})
    assert login.status_code == 200, login.text
    token = login.json()["access_token"]

    shop_resp = client.post(
        "/shops/",
        headers={"Authorization": f"Bearer {token}"},
        data={"name": "Admin Shop", "description": "Admin official store"}
    )
    assert shop_resp.status_code == 201, shop_resp.text

    login = client.post("/token", data={"username": "admin", "password": "password123"})
    assert login.status_code == 200, login.text
    token = login.json()["access_token"]
    
    # Create Product (needs image URL or similar? Service allows None, Router might require it? Router has image: UploadFile = File(None))
    # Router uses Form(...) for fields.
    prod_resp = client.post("/products/", headers={"Authorization": f"Bearer {token}"}, data={
        "name": "Mechanical Keyboard", 
        "description": "RGB", 
        "price": 100.0, 
        "stock": 5,
        "is_publish": True
    })
    assert prod_resp.status_code == 200, prod_resp.text
    product_id = prod_resp.json()["id"]

    # 2. Setup Customer & Order (Domain Auth & Orders)
    client.post("/register", json={"username": "buyer", "email": "buyer@test.com", "password": "password123", "disable": False})
    login_cust = client.post("/token", data={"username": "buyer", "password": "password123"})
    assert login_cust.status_code == 200, login_cust.text
    cust_token = login_cust.json()["access_token"]
    
    # Place Order
    order_resp = client.post("/orders/", headers={"Authorization": f"Bearer {cust_token}"}, json={
        "items": [{"product_id": product_id, "quantity": 3}]
    })
    
    assert order_resp.status_code == 200, order_resp.text
    assert order_resp.json()["total_price"] == 300.0

    # 3. Verify Product Stock Deduction (Domain Products)
    prod_list = client.get("/products/")
    product = next(p for p in prod_list.json() if p["id"] == product_id)
    assert product["stock"] == 2 # 5 - 3 = 2


def test_duplicate_order_rejected(client):
    client.post("/register", json={"username": "sellerdup", "email": "sellerdup@test.com", "password": "password123", "disable": False})

    seller_login = client.post("/token", data={"username": "sellerdup", "password": "password123"})
    assert seller_login.status_code == 200
    seller_token = seller_login.json()["access_token"]

    shop_resp = client.post(
        "/shops/",
        headers={"Authorization": f"Bearer {seller_token}"},
        data={"name": "Seller Dup Shop", "description": "Shop for duplicate test"}
    )
    assert shop_resp.status_code == 201, shop_resp.text

    seller_login = client.post("/token", data={"username": "sellerdup", "password": "password123"})
    assert seller_login.status_code == 200
    seller_token = seller_login.json()["access_token"]

    prod_resp = client.post("/products/", headers={"Authorization": f"Bearer {seller_token}"}, data={
        "name": "Unique Keyboard",
        "description": "RGB",
        "price": 150.0,
        "stock": 10,
        "is_publish": True
    })
    assert prod_resp.status_code == 200, prod_resp.text
    product_id = prod_resp.json()["id"]

    client.post("/register", json={"username": "buyerdup", "email": "buyerdup@test.com", "password": "password123", "disable": False})
    buyer_login = client.post("/token", data={"username": "buyerdup", "password": "password123"})
    assert buyer_login.status_code == 200
    buyer_token = buyer_login.json()["access_token"]

    first_order = client.post("/orders/", headers={"Authorization": f"Bearer {buyer_token}"}, json={
        "items": [{"product_id": product_id, "quantity": 2}]
    })
    assert first_order.status_code == 200, first_order.text

    dup_order = client.post("/orders/", headers={"Authorization": f"Bearer {buyer_token}"}, json={
        "items": [{"product_id": product_id, "quantity": 2}]
    })
    assert dup_order.status_code == 400
    assert dup_order.json()["detail"] == "You already placed this order. Complete or cancel the previous one before retrying."
