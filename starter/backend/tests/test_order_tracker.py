import pytest
from unittest.mock import Mock
from ..order_tracker import OrderTracker

# --- Fixtures for Unit Tests ---

@pytest.fixture
def mock_storage():
    """
    Provides a mock storage object for tests.
    This mock will be configured to simulate various storage behaviors.
    """
    mock = Mock()
    # By default, mock get_order to return None (no order found)
    mock.get_order.return_value = None
    # By default, mock get_all_orders to return an empty dict
    mock.get_all_orders.return_value = {}
    return mock

@pytest.fixture
def order_tracker(mock_storage):
    """
    Provides an OrderTracker instance initialized with the mock_storage.
    """
    return OrderTracker(mock_storage)


# --- Unit Tests Below ---

# ------ add_order tests ------
def test_add_order_successfully(order_tracker, mock_storage):
    """Tests adding a new order with default 'pending' status."""
    order_tracker.add_order("ORD001", "Laptop", 1, "CUST001")

    # We expect save_order to be called once
    mock_storage.save_order.assert_called_once()

def test_add_order_raises_error_if_exists(order_tracker, mock_storage):
    """Tests that adding an order with a duplicate ID raises a ValueError."""
    # Simulate that the storage finds an existing order
    mock_storage.get_order.return_value = {"order_id": "ORD_EXISTING"}

    with pytest.raises(ValueError, match="Order with ID 'ORD_EXISTING' already exists."):
        order_tracker.add_order("ORD_EXISTING", "New Item", 1, "CUST001")

@pytest.mark.parametrize(
        "field_name",
        ["order_id", "item_name", "quantity", "customer_id"]
)
def test_add_order_raises_error_if_missing_field(order_tracker, mock_storage, field_name):
    """Tests that all required fields are present or raise """

    order_data = {
        "order_id": "ORD002",
        "item_name": "Mobile Phone",
        "quantity": 1,
        "customer_id": "CUST001"
    }
    order_data[field_name] = None
    
    with pytest.raises(ValueError, match="Missing required field"):
        order_tracker.add_order(**order_data)
    
    mock_storage.save_order.assert_not_called()

# ------ get_order_by_id tests ------
def test_get_order_by_id_successfully(order_tracker, mock_storage):
    """Happy path test that getting an order that exists returns the proper order information"""
    #Arrange
    order_data = {
        "order_id": "ORD003",
        "item_name": "Table",
        "quantity": 3,
        "customer_id": "CUST002",
        "status": "shipped"
    }
    mock_storage.get_order.return_value = order_data

    #Act
    retrieved_order = order_tracker.get_order_by_id("ORD003")

    #Assert
    assert retrieved_order == order_data
    mock_storage.get_order.assert_called_once_with("ORD003")

def test_get_order_by_id_returns_none_if_not_found(order_tracker, mock_storage):
    """Sad path test that returns None when trying to retrieve an order by an id that doesn't exist in the storage"""
    #Arrange
    mock_storage.get_order.return_value = None

    #Act
    retrieved_order = order_tracker.get_order_by_id("ORD009")

    #Assert
    assert retrieved_order is None
    mock_storage.get_order.assert_called_once_with("ORD009")

@pytest.mark.parametrize(
        "order_id",
        ["", 123456, ["ORD001", "ORD002"], {"order_id": "ORD001"}]
)
def test_get_order_by_id_raises_error_if_wrong_or_empty_id_field(order_tracker, order_id):
    """Test that ValueErrror is raised when getting order with empty string or wrong type used for order_id argument"""
    with pytest.raises(ValueError, match=r"order_id must be a non-empty string\."):
        order_tracker.get_order_by_id(order_id)

# ------ update_order_status tests ------
def test_update_order_status_successfully(order_tracker, mock_storage):
    """Test update order status successfully updates the status"""
    #Arrange
    order_data_before_update = {
        "order_id": "ORD004",
        "item_name": "Pillow",
        "quantity": 2,
        "customer_id": "CUST003",
        "status": "pending"
    }
    mock_storage.get_order.return_value = order_data_before_update

    order_data_after_update = {**order_data_before_update, "status": "processing"}

    #Act
    order_tracker.update_order_status("ORD004", "processing")

    #Assert
    mock_storage.get_order.assert_called_once_with("ORD004")
    mock_storage.save_order.assert_called_once_with("ORD004", order_data_after_update)

def test_update_order_status_raises_error_if_invalid_status_used(order_tracker):
    """Test that ValueError is raised when an invalid status is used for updating order status"""
    with pytest.raises(ValueError, match=r"Invalid status 'invalid_status'\. Must be one of: .*"):
        order_tracker.update_order_status("ORD004", "invalid_status")

def test_update_order_status_raises_error_if_order_does_not_exist(order_tracker, mock_storage):
    """Test that ValueError is raised when trying to update the status of an order that doesn't exist in storage"""
    #Arrange
    mock_storage.get_order.return_value = None

    #Act/Assert
    with pytest.raises(ValueError, match=r"Order with ID 'ORD004' not found\."):
        order_tracker.update_order_status("ORD004", "shipped")

def test_update_order_status_raises_error_using_empty_string(order_tracker, mock_storage):
    """Test that ValueError is raised when an empty string is used for order_id"""
    with pytest.raises(ValueError, match=r"order_id must be a non-empty string\."):
        order_tracker.update_order_status("", "shipped")

# ------ list_all_orders tests ------
@pytest.mark.parametrize(
        "order_data",
        [
            {
                "ORD005": {"order_id": "ORD005", "item_name": "Chair", "quantity": 4, "customer_id": "CUST004", "status": "pending"},
                "ORD006": {"order_id": "ORD006", "item_name": "Desk", "quantity": 1, "customer_id": "CUST005", "status": "shipped"}
            },
            {}
        ]
)
def test_list_all_orders_returns_all_orders(order_tracker, mock_storage, order_data):
    """Test that all orders are returned as a dict mapping order_id --> order dict, or an empty dict if no orders in storage"""
    #Arrange
    mock_storage.get_all_orders.return_value = order_data

    #Act
    all_orders = order_tracker.list_all_orders()

    #Assert
    assert all_orders == order_data
    mock_storage.get_all_orders.assert_called_once()