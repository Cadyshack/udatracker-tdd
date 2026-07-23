import pytest
from backend.app import app, in_memory_storage

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['DEBUG'] = False
    in_memory_storage.clear()
    with app.test_client() as client:
        yield client

def test_add_order_api_success(client):
    order_data = {
        "order_id": "API001", "item_name": "API Laptop", "quantity": 1, "customer_id": "APICUST001"
    }
    response = client.post('/api/orders', json=order_data)
    assert response.status_code == 201
    assert response.json['order_id'] == "API001"

def test_get_order_api_success(client):
    client.post('/api/orders', json={
        "order_id": "GET001", "item_name": "Test Item", "quantity": 1, "customer_id": "C1"
    })
    response = client.get('/api/orders/GET001')
    assert response.status_code == 200
    assert response.json['order_id'] == "GET001"

def test_get_order_api_not_found(client):
    response = client.get('/api/orders/NONEXISTENT')
    assert response.status_code == 404

def test_update_order_status_api_success(client):
    client.post('/api/orders', json={
        "order_id": "UPDATE001", "item_name": "Test Item", "quantity": 1, "customer_id": "C1"
    })
    response = client.put('/api/orders/UPDATE001/status', json={"new_status": "shipped"})
    assert response.status_code == 200
    assert response.json['status'] == "shipped"

def test_list_all_orders_api_with_data(client):
    client.post('/api/orders', json={"order_id": "LST001", "item_name": "Item A", "quantity": 1, "customer_id": "C1"})
    client.post('/api/orders', json={"order_id": "LST002", "item_name": "Item B", "quantity": 2, "customer_id": "C2"})
    response = client.get('/api/orders')
    assert response.status_code == 200
    assert len(response.json) == 2

def test_list_orders_by_status_api_matching(client):
    client.post('/api/orders', json={"order_id": "S001", "item_name": "A", "quantity": 1, "customer_id": "C1", "status": "pending"})
    client.post('/api/orders', json={"order_id": "S002", "item_name": "B", "quantity": 2, "customer_id": "C2", "status": "shipped"})
    response = client.get('/api/orders?status=pending')
    assert response.status_code == 200
    assert len(response.json) == 1
    assert response.json[0]['order_id'] == "S001"

def test_add_order_api_bad_quantity(client):
    order_data = {
         "order_id": "API002", "item_name": "API Table", "quantity": -1, "customer_id": "APICUST001"
    }
    response = client.post('/api/orders', json=order_data)
    assert response.status_code == 400

def test_add_order_api_duplicate_conflict(client):
    order_data = {
        "order_id": "DUP001", "item_name": "API Laptop", "quantity": 1, "customer_id": "APICUST001"
    }
    client.post('/api/orders', json=order_data)
    response = client.post('/api/orders', json=order_data)
    assert response.status_code == 409

def test_add_order_api_missing_field(client):
    order_data = {
        "order_id": "API003", "item_name": "API Chair", "customer_id": "APICUST001"
    }
    response = client.post('/api/orders', json=order_data)
    assert response.status_code == 400

def test_add_order_api_blank_field(client):
    order_data = {
        "order_id": "API004", "item_name": "   ", "quantity": 1, "customer_id": "APICUST001"
    }
    response = client.post('/api/orders', json=order_data)
    assert response.status_code == 400

def test_add_order_api_invalid_status(client):
    order_data = {
        "order_id": "API005", "item_name": "API Desk", "quantity": 1, "customer_id": "APICUST001", "status": "brunch"
    }
    response = client.post('/api/orders', json=order_data)
    assert response.status_code == 400

def test_update_order_status_api_missing_body(client):
    client.post('/api/orders', json={
        "order_id": "UPD002", "item_name": "Test Item", "quantity": 1, "customer_id": "C1"
    })
    response = client.put('/api/orders/UPD002/status', json={})
    assert response.status_code == 400

def test_update_order_status_api_invalid_status(client):
    client.post('/api/orders', json={
        "order_id": "UPD003", "item_name": "Test Item", "quantity": 1, "customer_id": "C1"
    })
    response = client.put('/api/orders/UPD003/status', json={"new_status": "banana"})
    assert response.status_code == 400

def test_update_order_status_api_not_found(client):
    response = client.put('/api/orders/NONEXISTENT/status', json={"new_status": "shipped"})
    assert response.status_code == 404

def test_list_orders_by_status_api_invalid_status(client):
    response = client.get('/api/orders?status=banana')
    assert response.status_code == 400