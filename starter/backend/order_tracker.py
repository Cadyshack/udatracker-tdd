# This module contains the OrderTracker class, which encapsulates the core
# business logic for managing orders.

class OrderTracker:
    """
    Manages customer orders, providing functionalities to add, update,
    and retrieve order information.
    """
    def __init__(self, storage):
        required_methods = ['save_order', 'get_order', 'get_all_orders']
        for method in required_methods:
            if not hasattr(storage, method) or not callable(getattr(storage, method)):
                raise TypeError(f"Storage object must implement a callable '{method}' method.")
        self.storage = storage
        self.valid_status = ["pending", "processing", "shipped", "delivered", "cancelled"]

    def add_order(self, order_id: str, item_name: str, quantity: int, customer_id: str, status: str = "pending"):
        """Create and store a new order, raising ValueError on duplicate ID, missing fields, or invalid status."""
        if self.storage.get_order(order_id):
            raise ValueError(f"Order with ID '{order_id}' already exists.")
        
        required_fields = {
            "order_id": order_id,
            "item_name": item_name,
            "quantity": quantity,
            "customer_id": customer_id
        }
        missing_fields = [name for name, value in required_fields.items() if value is None]
        if missing_fields:
            raise ValueError(f"Missing required field(s): {', '.join(missing_fields)}")

        if status not in self.valid_status:
            raise ValueError(f"Invalid status '{status}'. Must be one of: {', '.join(self.valid_status)}")

        order = {
            "order_id": order_id,
            "item_name": item_name,
            "quantity": quantity,
            "customer_id": customer_id,
            "status": status
        }
        self.storage.save_order(order_id, order)

    def get_order_by_id(self, order_id: str) -> dict | None:
        """Return the order for order_id, or None if it doesn't exist."""
        if not isinstance(order_id, str) or not order_id:
            raise ValueError("order_id must be a non-empty string.")
        
        return self.storage.get_order(order_id) # returns None when absent

    def update_order_status(self, order_id: str, new_status: str) -> None:
        """Set an existing order's status, raising ValueError on invalid status or unknown order_id."""
        if new_status not in self.valid_status:
            raise ValueError(f"Invalid status '{new_status}'. Must be one of: {', '.join(self.valid_status)}")

        if not isinstance(order_id, str) or not order_id:
            raise ValueError("order_id must be a non-empty string.")
        
        order = self.storage.get_order(order_id)
        if order is None:
            raise ValueError(f"Order with ID '{order_id}' not found.")
        
        order["status"] = new_status
        self.storage.save_order(order_id, order)


    def list_all_orders(self) -> dict:
        """Return every order, keyed by order_id."""
        return self.storage.get_all_orders()

    def list_orders_by_status(self, status: str) -> dict:
        """Return orders matching status, raising ValueError on empty or invalid status."""
        if not isinstance(status, str) or not status.strip():
             raise ValueError("Cannot use an empty string as status argument.")
        elif status not in self.valid_status:
            raise ValueError(f"Invalid status '{status}'. Must be one of: {', '.join(self.valid_status)}")
        
        all_orders = self.storage.get_all_orders()
        filtered_orders = {k: v.copy() for k, v in all_orders.items() if v["status"] == status}
        return filtered_orders
