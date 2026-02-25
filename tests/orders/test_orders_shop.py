from fastapi.testclient import TestClient
import pytest

def test_prevent_self_purchase(client: TestClient):
    # 1. Register Seller (ShopOwner)
    client.post("/register", json={"username": "seller", "email": "seller@test.com", "password": "password123", "disable": False})
    
    # 2. Login Seller
    login_res = client.post("/token", data={"username": "seller", "password": "password123", "scope": "shopowner"})
    assert login_res.status_code == 200, login_res.text
    token = login_res.json()["access_token"]
    
    # 3. Create Product
    prod_res = client.post("/products/", headers={"Authorization": f"Bearer {token}"}, data={
        "name": "Self Product",
        "description": "Test",
        "price": 50.0,
        "stock": 10,
        "is_publish": True
    })
    assert prod_res.status_code == 200, prod_res.text
    product_id = prod_res.json()["id"]
    
    # 4. Attempt to buy own product
    order_res = client.post("/orders/", headers={"Authorization": f"Bearer {token}"}, json={
        "items": [{"product_id": product_id, "quantity": 1}]
    })
    
    assert order_res.status_code == 400
    assert order_res.json()["detail"] == "You cannot buy your own product"

def test_shop_orders_and_status(client: TestClient):
    # 1. Register Seller
    client.post("/register", json={"username": "seller2", "email": "seller2@test.com", "password": "password123", "disable": False})
    seller_login = client.post("/token", data={"username": "seller2", "password": "password123", "scope": "shopowner"})
    assert seller_login.status_code == 200
    seller_token = seller_login.json()["access_token"]
    
    # 2. Register Buyer
    client.post("/register", json={"username": "buyer2", "email": "buyer2@test.com", "password": "password123", "disable": False})
    buyer_login = client.post("/token", data={"username": "buyer2", "password": "password123", "scope": ""})
    assert buyer_login.status_code == 200
    buyer_token = buyer_login.json()["access_token"]
    
    # 3. Seller creates product
    prod_res = client.post("/products/", headers={"Authorization": f"Bearer {seller_token}"}, data={
        "name": "My Product",
        "description": "Test",
        "price": 100.0,
        "stock": 10,
        "is_publish": True
    })
    assert prod_res.status_code == 200
    product_id = prod_res.json()["id"]
    
    # 4. Buyer places order
    order_res = client.post("/orders/", headers={"Authorization": f"Bearer {buyer_token}"}, json={
        "items": [{"product_id": product_id, "quantity": 2}]
    })
    assert order_res.status_code == 200
    order_id = order_res.json()["id"]
    
    # 5. Seller views shop orders
    shop_orders = client.get("/orders/shop", headers={"Authorization": f"Bearer {seller_token}"})
    assert shop_orders.status_code == 200
    orders = shop_orders.json()
    assert len(orders) == 1
    assert orders[0]["id"] == order_id
    assert orders[0]["owner"]["username"] == "buyer2"
    
    # 6. Status Update: Seller sets to processing -> shipped
    status_res = client.patch(f"/orders/{order_id}/status", headers={"Authorization": f"Bearer {seller_token}"}, json={"status": "processing"})
    assert status_res.status_code == 200
    assert status_res.json()["status"] == "processing"
    
    status_res = client.patch(f"/orders/{order_id}/status", headers={"Authorization": f"Bearer {seller_token}"}, json={"status": "shipped"})
    assert status_res.status_code == 200
    assert status_res.json()["status"] == "shipped"
    
    # 7. Status Update: Buyer tries to set to shipped (should fail)
    fail_res = client.patch(f"/orders/{order_id}/status", headers={"Authorization": f"Bearer {buyer_token}"}, json={"status": "shipped"})
    assert fail_res.status_code == 403
    
    # 8. Status Update: Buyer sets to completed
    complete_res = client.patch(f"/orders/{order_id}/status", headers={"Authorization": f"Bearer {buyer_token}"}, json={"status": "completed"})
    assert complete_res.status_code == 200
    assert complete_res.json()["status"] == "completed"
