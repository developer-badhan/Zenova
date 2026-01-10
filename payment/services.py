
'''
# payment/services.py
from decimal import Decimal
from django.apps import apps
from django.db import transaction
from django.utils import timezone
from .models import Payment, PaymentMethod, PaymentStatus, generate_txn_id

def calculate_order_total_from_cart(cart):
    """Return Decimal total computed from cart items (reads product price)."""
    total = Decimal('0.00')
    for item in cart.items.select_related('product').all():
        price = Decimal(str(item.product.price))
        qty = int(item.quantity)
        total += price * qty
    return total.quantize(Decimal("0.01"))

@transaction.atomic
def create_order_from_cart(user, cart, coupon=None):
    """Create an Order and OrderItems from the user's cart.
    Returns (order, total_amount)
    """
    Order = apps.get_model('shop', 'Order')
    OrderItem = apps.get_model('shop', 'OrderItem')
    Product = apps.get_model('shop', 'Product')
    Coupon = apps.get_model('shop', 'Coupon')

    total_amount = calculate_order_total_from_cart(cart)

    # apply coupon discount if provided & valid
    coupon_obj = None
    if coupon:
        try:
            coupon_obj = Coupon.objects.get(id=coupon.id, active=True)
            discount = (total_amount * (coupon_obj.discount_percent / Decimal('100.0')))
            total_amount -= discount
        except Coupon.DoesNotExist:
            coupon_obj = None

    order = Order.objects.create(
        user=user,
        total_amount=total_amount,
        coupon=coupon_obj,
        is_paid=False,
        payment_status='pending'
    )

    # create OrderItems
    for item in cart.items.select_related('product').all():
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price=item.product.price
        )

    return order, total_amount

@transaction.atomic
def create_payment_record(user, order, method=PaymentMethod.ZPAY.value, amount=None, meta=None):
    """Create a Payment row and optionally link it to the order (order.payment will be set later)."""
    if amount is None:
        amount = getattr(order, 'total_amount', None) or Decimal('0.00')
    txn = generate_txn_id()
    payment = Payment.objects.create(
        user=user,
        order_id=order.id,
        amount=amount,
        method=method,
        status=PaymentStatus.INITIATED.value,
        transaction_id=txn,
        meta=meta or {}
    )
    return payment

@transaction.atomic
def complete_payment(payment: Payment, gateway_txn_id=None, gateway_meta=None):
    """Mark payment as successful, update order.is_paid and link payment to order,
    then clear user's cart and optionally create shipment."""
    Order = apps.get_model('shop', 'Order')
    Cart = apps.get_model('shop', 'Cart')
    CartItem = apps.get_model('shop', 'CartItem')
    shipment_service = None
    try:
        shipment_service = apps.get_app_config('shop').module.services.shipment_service
    except Exception:
        # fallback import if structure differs
        try:
            from shop.services import shipment_service as shipment_service
        except Exception:
            shipment_service = None

    # mark payment success
    txn = gateway_txn_id or generate_txn_id()
    payment.mark_success(txn_id=txn, meta=gateway_meta or {})
    if order.coupon:
        coupon = order.coupon
        coupon.used_count += 1
        coupon.used_by.add(order.user)
        coupon.save(update_fields=['used_count'])


    order = Order.objects.select_for_update().get(id=payment.order_id)

    # mark order as paid; do not change shipment status here
    order.is_paid = True
    order.payment_status = 'paid'
    order.payment = payment  # set relation (Order.payment FK)
    order.save(update_fields=['is_paid', 'payment_status', 'payment', 'total_amount'])

    # clear user's cart
    try:
        cart = Cart.objects.get(user=payment.user)
        CartItem.objects.filter(cart=cart).delete()
    except Cart.DoesNotExist:
        pass

    # Optionally: create Shipment automatically (if your workflow requires),
    # here we create with order address if available
    try:
        if shipment_service:
            # Try to pick an address from order if available: order may have an address field in future
            address = getattr(order, 'shipping_address', None) or getattr(order, 'address', None) or ''
            shipment_service.create_shipment(order_id=order.id, address=address)
    except Exception:
        # swallow errors from shipment creation to avoid breaking payment completion
        pass

    return payment, order

@transaction.atomic
def fail_payment(payment: Payment, gateway_txn_id=None, gateway_meta=None):
    payment.mark_failed(txn_id=gateway_txn_id, meta=gateway_meta or {})
    # update order payment status if linked
    Order = apps.get_model('shop', 'Order')
    try:
        order = Order.objects.get(id=payment.order_id)
        order.payment_status = 'failed'
        order.save(update_fields=['payment_status'])
    except Exception:
        pass
    return payment
'''

# payment/services.py
from decimal import Decimal
from django.apps import apps
from .models import Payment, PaymentMethod, PaymentStatus
from .utils import (
    simulate_gateway_delay,
    simulate_payment_result,
    generate_txn_id,
    build_transaction_meta,
)

class PaymentError(Exception):
    pass


def create_payment(*, user, order):
    payment, created = Payment.objects.get_or_create(
        order_id=order.id,
        defaults={
            "user": user,
            "amount": order.total_amount,
            "method": PaymentMethod.ZPAY.value,
            "status": PaymentStatus.INITIATED.value,
        }
    )
    return payment


def process_zpay_payment(*, payment, order):
    simulate_gateway_delay()
    result = simulate_payment_result()
    txn_id = generate_txn_id()
    meta = build_transaction_meta(order.id, "ZPAY")

    if result == "success":
        payment.mark_success(txn_id=txn_id, meta=meta)
        order.is_paid = True
        order.payment_status = "paid"
        order.save(update_fields=["is_paid", "payment_status"])
        return True

    payment.mark_failed(txn_id=txn_id, meta=meta)
    return False
