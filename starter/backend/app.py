from flask import Flask, request, jsonify, send_from_directory
from backend.order_tracker import OrderTracker
from backend.in_memory_storage import InMemoryStorage

app = Flask(__name__, static_folder='../frontend')
in_memory_storage = InMemoryStorage()
order_tracker = OrderTracker(in_memory_storage)

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)

@app.route('/api/orders', methods=['POST'])
def add_order_api():
    """Add a new order to the system."""
    data = request.get_json()
    #  --- 400 Bad Request: validate input first ---
    if not data or not all(k in data for k in ("order_id", "item_name", "quantity", "customer_id")):
        return jsonify({"error": "order_id, item_name, quantity, and customer_id are required"}), 400

    # --- 409 Conflict: duplicate order_id ---
    try:
        order_tracker.add_order(
            order_id=data["order_id"],
            item_name=data["item_name"],
            quantity=data["quantity"],
            customer_id=data["customer_id"],
            status=data.get("status", "pending"),
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 409

    # --- happy path: 201 Created ---
    created_order = order_tracker.get_order_by_id(data["order_id"])
    return jsonify(created_order), 201

@app.route('/api/orders/<string:order_id>', methods=['GET'])
def get_order_api(order_id):
    """Retrieve an order by its ID."""
    order = order_tracker.get_order_by_id(order_id)
    # --- 404 Not Found: order doesn't exist ---
    if order is None:
        return jsonify({"error": f"{order_id} does not exist."}), 404
    # --- happy path: 200 OK response ---
    return jsonify(order), 200

@app.route('/api/orders/<string:order_id>/status', methods=['PUT'])
def update_order_status_api(order_id):
    """Update the status of an existing order."""
    data = request.get_json()
    # Check if missing request body or request body doesn't have "new_status" key
    if not data or "new_status" not in data:
        return jsonify({"error": "new_status is required"}), 400
    
    new_status = data["new_status"]

    try:
        order_tracker.update_order_status(order_id, new_status)
    except ValueError as e:
        if "Invalid status" in str(e):
            return jsonify({"error": str(e)}), 400
        else:
            return jsonify({"error": str(e)}), 404

    updated_order = order_tracker.get_order_by_id(order_id)
    return jsonify(updated_order), 200    

@app.route('/api/orders', methods=['GET'])
def list_orders_api():
    """Return list of all orders, or those matching stuatus query parameter"""
    status = request.args.get("status")
    try:
        if status:
            orders = list(order_tracker.list_orders_by_status(status).values())
        else:
            orders = list(order_tracker.list_all_orders().values())
    except ValueError as e:
        return jsonify({"error": str(e)}), 400

    return jsonify(orders), 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000, debug=True)
