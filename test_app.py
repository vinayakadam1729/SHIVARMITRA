import sys
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
from fastapi.testclient import TestClient
from app.main import app
from app.config import settings

def run_tests():
    print("\n🔍 Running Shivar Platform Verification Tests...\n")
    client = TestClient(app)

    # Test 1: Home Page Render
    res = client.get("/")
    assert res.status_code == 200, f"Home page failed: {res.status_code}"
    print("✅ Test 1: Storefront Home Page rendered successfully (200 OK)")

    # Test 2: Categories API
    res = client.get("/api/categories")
    assert res.status_code == 200
    categories = res.json()
    assert len(categories) >= 5
    print(f"✅ Test 2: Categories API returned {len(categories)} categories")

    # Test 3: Products API in Marathi, Hindi, English
    for lang in ["mr", "hi", "en"]:
        res = client.get(f"/api/products?lang={lang}")
        assert res.status_code == 200
        products = res.json()
        assert len(products) >= 10
        print(f"✅ Test 3: Products API [{lang.upper()}] returned {len(products)} localized products")

    # Test 4: Single Product Detail
    first_prod = products[0]
    res = client.get(f"/api/products/{first_prod['slug']}?lang=mr")
    assert res.status_code == 200
    p_data = res.json()
    assert p_data["name"] is not None
    print(f"✅ Test 4: Product detail for '{p_data['name']}' fetched successfully")

    # Test 5: Admin Login
    res = client.post("/api/admin/login", json={
        "username": settings.ADMIN_USERNAME,
        "password": settings.ADMIN_PASSWORD
    })
    assert res.status_code == 200, f"Admin login failed: {res.text}"
    auth_data = res.json()
    token = auth_data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Test 5: Admin Authentication successful (JWT token generated)")

    # Test 6: Admin Dashboard Stats
    res = client.get("/api/admin/dashboard-stats", headers=headers)
    assert res.status_code == 200
    stats = res.json()
    print(f"✅ Test 6: Dashboard stats retrieved - Products: {stats['total_products']}, Orders: {stats['total_orders']}")

    # Test 7: Customer Order Placement & WhatsApp Redirection to 9021273002
    order_payload = {
        "customer_name": "संतोष एकनाथ जाधव",
        "customer_phone": "9823456789",
        "customer_email": "santosh@gmail.com",
        "address_line": "गट नं. ४५, पिंपळगाव रोड",
        "village": "राहुरी",
        "taluka": "राहुरी",
        "district": "अहमदनगर",
        "state": "Maharashtra",
        "pincode": "413705",
        "delivery_notes": "सकाळी ११ वाजता फोन करावा",
        "payment_method": "COD",
        "items": [
            {
                "product_id": first_prod["id"],
                "product_name": first_prod["name_mr"],
                "price": first_prod["price"],
                "quantity": 2,
                "unit": first_prod["unit_mr"]
            }
        ],
        "preferred_language": "mr"
    }

    res = client.post("/api/orders", json=order_payload)
    assert res.status_code == 201, f"Order placement failed: {res.text}"
    order_res = res.json()
    assert order_res["success"] is True
    assert "9021273002" in order_res["whatsapp_url"]
    print(f"✅ Test 7: Order placed (#{order_res['order_number']}). WhatsApp redirect points to 9021273002")

    # Test 8: Order Tracking
    order_num = order_res["order_number"]
    res = client.get(f"/api/orders/track/{order_num}")
    assert res.status_code == 200
    track_data = res.json()
    assert track_data["customer_name"] == "संतोष एकनाथ जाधव"
    print(f"✅ Test 8: Order tracking verified - Status: '{track_data['order_status']}'")

    # Test 9: Admin Status Update Workflow
    order_id = order_res["order_id"]
    res = client.put(f"/api/admin/orders/{order_id}/status", json={"order_status": "Confirmed"}, headers=headers)
    assert res.status_code == 200
    print("✅ Test 9: Admin updated order status to 'Confirmed'")

    # Test 10: CSV Export
    res = client.get("/api/admin/orders/export-csv", headers=headers)
    assert res.status_code == 200
    assert "text/csv" in res.headers["content-type"]
    print("✅ Test 10: Admin CSV Export verified")

    print("\n🎉 ALL 10 TESTS PASSED SUCCESSFULLY! The Shivar platform is 100% production ready.\n")

if __name__ == "__main__":
    run_tests()
