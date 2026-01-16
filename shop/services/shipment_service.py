import random
import string
from django.db import transaction
from django.utils import timezone
from user.models import User
from shop.models import Shipment, ShipmentStatus
from constants import Role
from django.core.exceptions import ValidationError



# Fetch all shipment details for customer
def get_shipment():
    try:
        return Shipment.objects.all()
    except ValueError:
        print("Shipment was invalid")


# Auto created shipment after payment
def create_shipment_after_payment(*, order, address):
    if not order.is_paid:
        raise ValidationError("Shipment cannot be created for unpaid order")
    if hasattr(order, "shipment"):
        return order.shipment 
    shipment = Shipment.objects.create(
        order=order,
        customer=order.user,
        address_snapshot=str(address),
        status=ShipmentStatus.PENDING_ASSIGNMENT
    )
    return shipment


# Retrieve data from staff 
def get_all_staff_users():
    return User.objects.filter(role=Role.ENDUSER_STAFF, is_active=True)


# Auto created tracking number
def generate_unique_tracking_number():
    while True:
        tracking = "ZNV-" + "".join(
            random.choices(string.ascii_uppercase + string.digits, k=10)
        )
        if not Shipment.objects.filter(tracking_number=tracking).exists():
            return tracking


# Assignment staff for shipment via admin
@transaction.atomic
def assign_staff_to_shipment(*, shipment: Shipment, staff_user):
    if staff_user.role != Role.ENDUSER_STAFF:
        raise ValueError("Only staff users can be assigned.")
    if shipment.assigned_staff:
        raise ValueError("Shipment already assigned.")
    shipment.assigned_staff = staff_user
    shipment.tracking_number = generate_unique_tracking_number()
    shipment.status = ShipmentStatus.ASSIGNED
    shipment.shipped_at = timezone.now()
    shipment.save()
    return shipment


# Fetch shipment data for staff
def get_required_data():
    shipments = Shipment.objects.select_related('customer', 'order').filter(
        status__in=[
            ShipmentStatus.PENDING_ASSIGNMENT.value,
            ShipmentStatus.ASSIGNED.value,
            ShipmentStatus.SHIPPED.value,
        ]
    )

    data = []
    for shipment in shipments:
        data.append({
            'id': shipment.id,
            'customer_first_name': shipment.customer.first_name,
            'customer_last_name': shipment.customer.last_name,
            'customer_email': shipment.customer.email,
            'address': shipment.address_snapshot,
            'tracking_number': shipment.tracking_number or 'N/A',
            'order_created_at': shipment.order.created_at,
            'status': ShipmentStatus(shipment.status).name.replace("_", " ").title(),
        })
    return data


# Staff: mark shipment as shipped
@transaction.atomic
def mark_shipment_as_shipped(*, shipment: Shipment, staff_user):
    if shipment.assigned_staff != staff_user:
        raise PermissionError("You are not assigned to this shipment.")
    if shipment.status != ShipmentStatus.ASSIGNED:
        raise ValueError("Shipment cannot be marked as shipped.")
    shipment.status = ShipmentStatus.SHIPPED
    shipment.shipped_at = timezone.now()
    shipment.save()
    return shipment


# Staff: mark shipment as delivered
@transaction.atomic
def mark_shipment_as_delivered(*, shipment: Shipment, staff_user):
    if shipment.assigned_staff != staff_user:
        raise PermissionError("You are not assigned to this shipment.")
    if shipment.status != ShipmentStatus.SHIPPED:
        raise ValueError("Shipment cannot be marked as delivered.")
    shipment.status = ShipmentStatus.DELIVERED
    shipment.delivered_at = timezone.now()
    shipment.save()
    return shipment




# def mark_shipment_shipped(*, shipment, staff_user):
#     if shipment.assigned_staff != staff_user:
#         raise ValidationError("You are not assigned to this shipment")

#     if shipment.status != ShipmentStatus.ASSIGNED:
#         raise ValidationError("Shipment must be assigned before shipping")

#     shipment.status = ShipmentStatus.SHIPPED
#     shipment.shipped_at = timezone.now()
#     shipment.save(update_fields=["status", "shipped_at", "updated_at"])


# def mark_shipment_delivered(*, shipment, staff_user):
#     if shipment.assigned_staff != staff_user:
#         raise ValidationError("You are not assigned to this shipment")

#     if shipment.status != ShipmentStatus.SHIPPED:
#         raise ValidationError("Shipment must be shipped before delivery")

#     shipment.status = ShipmentStatus.DELIVERED
#     shipment.delivered_at = timezone.now()
#     shipment.save(update_fields=["status", "delivered_at", "updated_at"])

