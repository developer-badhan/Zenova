from decimal import Decimal
from django.db import transaction
from shop.models import Order, OrderItem, Cart
from django.db.models import Prefetch



# Error Handling on Orders
class OrderCreationError(Exception):
    pass


# Order creation from Cart
def create_order_from_cart(*, user, cart: Cart, cart_totals: dict):
    if not cart.items.exists():
        raise OrderCreationError("Cart is empty.")
    if cart_totals["grand_total"] <= Decimal("0.00"):
        raise OrderCreationError("Invalid order amount.")
    with transaction.atomic():
        order = Order.objects.create(
            user=user,
            total_amount=cart_totals["grand_total"],
            coupon=cart_totals.get("coupon"),
            payment_status="pending",
            is_paid=False,
        )
        OrderItem.objects.bulk_create([
            OrderItem(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price,
            )
            for item in cart.items.select_related("product")
        ])
        return order


# Fetch all order for admin
def get_all_orders_for_admin():
    return (
        Order.objects
        .select_related("user", "coupon")
        .prefetch_related(
            Prefetch(
                "items",
                queryset=OrderItem.objects.select_related("product")
            )
        )
        .order_by("-created_at")
    )



'''
from shop.models import Order, OrderItem, Coupon, Product
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction


# Get all orders for a specific user
def get_all_orders(user=None):
    try:
        if user and not user.is_staff:
            return Order.objects.filter(user=user).order_by('-created_at')
        return Order.objects.all().order_by('-created_at')
    except Exception as e:
        print(f"Error fetching orders: {e}")
        return []


# Get a specific order by its ID
def get_order_by_id(order_id):
    try:
        return Order.objects.get(id=order_id)
    except ObjectDoesNotExist:
        print(f"Order with ID {order_id} not found.")
        return None
    except Exception as e:
        print(f"Error retrieving order: {e}")
        return None


# Create a new order
@transaction.atomic
def create_order(user, items, coupon_code=None):
    try:
        coupon = None
        discount_percent = 0
        if coupon_code:
            try:
                coupon = Coupon.objects.get(code=coupon_code, active=True)
                discount_percent = float(coupon.discount_percent)
            except Coupon.DoesNotExist:
                print(f"Invalid or inactive coupon code: {coupon_code}")
        order = Order.objects.create(user=user, coupon=coupon)
        total = 0
        for item in items:
            product_id = item.get('product_id')
            quantity = item.get('quantity', 1)
            product = Product.objects.get(id=product_id)
            price = float(product.price) * int(quantity)
            total += price
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=product.price
            )
        if discount_percent > 0:
            total = total - (total * discount_percent / 100)
        order.total_amount = total
        order.save()
        return order
    except Exception as e:
        print(f"Error creating order: {e}")
        return None


# Update the payment status of an order
def update_payment_status(order_id, payment_id, status):
    try:
        order = Order.objects.get(id=order_id)
        order.is_paid = status.lower() == 'paid'
        order.payment_status = status
        order.payment_id = payment_id
        order.save()
        return order
    except ObjectDoesNotExist:
        print(f"Order with ID {order_id} not found.")
        return None
    except Exception as e:
        print(f"Error updating payment status: {e}")
        return None


# Delete an existing order
def delete_order(order_id):
    try:
        order = Order.objects.get(id=order_id)
        order.delete()
        return True
    except ObjectDoesNotExist:
        print(f"Order with ID {order_id} not found.")
        return False
    except Exception as e:
        print(f"Error deleting order: {e}")
        return False
    
'''