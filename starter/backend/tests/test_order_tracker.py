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

# add_order tests
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

# get_order_by_id tests
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