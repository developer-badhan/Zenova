from shop.models import Shipment, Order
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone


def get_all_shipment():
    try:
        return Shipment.objects.all()
    except Exception as e:
        print(f"Error no shipment found: {e}")
        return None

def create_shipment(order_id, address, tracking_number=None, carrier=None):
    try:
        order = Order.objects.get(id=order_id)
        if hasattr(order, 'shipment'):
            print("Shipment already exists for this order.")
            return None
        shipment = Shipment.objects.create(
            order=order,
            address=address,
            tracking_number=tracking_number,
            carrier=carrier
        )
        return shipment
    except Order.DoesNotExist:
        print(f"Order with ID {order_id} not found.")
        return None
    except Exception as e:
        print(f"Error creating shipment: {e}")
        return None

def get_shipment_by_order(order_id):
    try:
        return Shipment.objects.get(order_id=order_id)
    except Shipment.DoesNotExist:
        return None
    except Exception as e:
        print(f"Error fetching shipment: {e}")
        return None

def update_tracking(order_id, tracking_number=None, carrier=None):
    try:
        shipment = Shipment.objects.get(order_id=order_id)
        if tracking_number:
            shipment.tracking_number = tracking_number
        if carrier:
            shipment.carrier = carrier
        shipment.save()
        return shipment
    except Shipment.DoesNotExist:
        print(f"No shipment found for order {order_id}")
        return None
    except Exception as e:
        print(f"Error updating shipment: {e}")
        return None

def mark_as_shipped(order_id):
    try:
        shipment = Shipment.objects.get(order_id=order_id)
        shipment.shipped_at = timezone.now()
        shipment.save()
        return shipment
    except Shipment.DoesNotExist:
        print(f"No shipment found for order {order_id}")
        return None
    except Exception as e:
        print(f"Error marking shipment as shipped: {e}")
        return None

def mark_as_delivered(order_id):
    try:
        shipment = Shipment.objects.get(order_id=order_id)
        shipment.delivered_at = timezone.now()
        shipment.save()
        return shipment
    except Shipment.DoesNotExist:
        print(f"No shipment found for order {order_id}")
        return None
    except Exception as e:
        print(f"Error marking shipment as delivered: {e}")
        return None