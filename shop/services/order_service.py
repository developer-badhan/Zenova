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

