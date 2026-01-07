'''


from shop.models import OrderItem, Product
from django.core.exceptions import ObjectDoesNotExist


# Get all items for a specific order
def get_items_by_order(order_id):
    try:
        return OrderItem.objects.filter(order__id=order_id)
    except Exception as e:
        print(f"Error fetching order items for order {order_id}: {e}")
        return []


# Get a specific order item by its ID
def get_item_by_id(item_id):
    try:
        return OrderItem.objects.get(id=item_id)
    except ObjectDoesNotExist:
        print(f"Order item with ID {item_id} not found.")
        return None
    except Exception as e:
        print(f"Error retrieving order item with ID {item_id}: {e}")
        return None


# Create a new order item
def create_order_item(order, product_id, quantity, price=None):
    try:
        product = Product.objects.get(id=product_id)
        order_item = OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity,
            price=price or product.price
        )
        return order_item
    except Product.DoesNotExist:
        print(f"Product with ID {product_id} not found.")
        return None
    except Exception as e:
        print(f"Error creating order item: {e}")
        return None


# Update an existing order item
def update_order_item(item_id, quantity=None, price=None):
    try:
        item = OrderItem.objects.get(id=item_id)

        if quantity is not None:
            item.quantity = quantity
        if price is not None:
            item.price = price
        item.save()
        return item
    except OrderItem.DoesNotExist:
        print(f"Order item with ID {item_id} not found.")
        return None
    except Exception as e:
        print(f"Error updating order item with ID {item_id}: {e}")
        return None


# Delete an existing order item
def delete_order_item(item_id):
    try:
        item = OrderItem.objects.get(id=item_id)
        item.delete()
        return True
    except OrderItem.DoesNotExist:
        print(f"Order item with ID {item_id} not found.")
        return False
    except Exception as e:
        print(f"Error deleting order item with ID {item_id}: {e}")
        return False
'''