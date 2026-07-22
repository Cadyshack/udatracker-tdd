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
    pass

@app.route('/api/orders/<string:order_id>/status', methods=['PUT'])
def update_order_status_api(order_id):
    pass

@app.route('/api/orders', methods=['GET'])
def list_orders_api():
    pass

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8000, debug=True)
