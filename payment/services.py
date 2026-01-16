from payment.models import Payment, PaymentMethod, PaymentStatus
from payment import utils
from shop.services import coupon_service
from shop.services import shipment_service
from django.core.exceptions import ValidationError



# Payment Error Handle
class PaymentError(Exception):
    pass


# Payment Create Service
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


# Z-Payment Processing Service
def process_zpay_payment(*, payment, order, request):
    utils.simulate_gateway_delay()
    result = utils.simulate_payment_result()
    txn_id = utils.generate_txn_id()
    meta = utils.build_transaction_meta(order.id, "ZPAY")
    if result == "success":
        payment.mark_success(txn_id=txn_id,meta=meta)
        if order.coupon:
            coupon_service.mark_coupon_used(order.user,order.coupon)
            coupon_service.flush_coupon_session(request)
        order.is_paid = True
        order.payment_status = "paid"
        order.payment = payment
        order.save(update_fields=[
            "is_paid",
            "payment_status",
            "payment"
        ])
        address = order.user.addresses.filter(
            is_default=True
        ).first()
        if not address:
            raise ValidationError(
                "Default address not found. Cannot create shipment."
            )
        shipment_service.create_shipment_after_payment(
            order=order,
            address=address
        )
        return True
    payment.mark_failed(txn_id=txn_id,meta=meta)
    coupon_service.flush_coupon_session(request)
    return False
