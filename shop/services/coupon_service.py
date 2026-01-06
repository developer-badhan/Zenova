import re
from datetime import datetime
from django.utils import timezone
from django.db import transaction
from decimal import Decimal
from shop.models import Coupon,CouponUsage,CouponAssignment



# Coupone Sanitization Input
def _normalize_date_str(s: str) -> str:
    if s is None:
        raise ValueError("Date string is required.")
    s = s.strip()
    s = re.sub(r'\s+', ' ', s)
    s = re.sub(r'\bA\.?M\.?\b', 'AM', s, flags=re.IGNORECASE)
    s = re.sub(r'\bP\.?M\.?\b', 'PM', s, flags=re.IGNORECASE)
    s = s.upper()
    s = re.sub(r'(?<!\s)(AM|PM)\b', r' \1', s)
    return s


# Coupon Time Checkup
def parse_datetime_with_fallback(date_str):
    s = _normalize_date_str(date_str)
    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d %I:%M:%S %p",
        "%Y-%m-%d %I:%M %p",
        "%Y-%m-%d %I%p",
        "%Y-%m-%d %I %p",
    ]
    for fmt in formats:
        try:
            dt = datetime.strptime(s, fmt)
            return timezone.make_aware(dt)
        except ValueError:
            continue
    raise ValueError(
        "Invalid date/time format. Use "
        "'YYYY-MM-DD HH:MM' or 'YYYY-MM-DD h:MM AM/PM'."
    )


# Coupon List
def get_all_coupons():
    return Coupon.objects.all()


# Coupon Creation
def create_coupon(code, discount_percent, valid_from, valid_to, usage_limit, created_by):
    if not code:
        raise ValueError("Coupon code is required.")
    if discount_percent in (None, ''):
        raise ValueError("Discount percent is required.")
    if not valid_from or not valid_to:
        raise ValueError("Validity dates are required.")
    if Coupon.objects.filter(code__iexact=code).exists():
        raise ValueError("Coupon code already exists.")
    coupon = Coupon.objects.create(
        code=code,
        # discount_percent=float(discount_percent),
        discount_percent=Decimal(discount_percent),
        valid_from=parse_datetime_with_fallback(valid_from),
        valid_to=parse_datetime_with_fallback(valid_to),
        usage_limit=usage_limit,
        created_by=created_by,
    )
    return coupon


# Coupon Update
def update_coupon(coupon_id, code, discount_percent, valid_from, valid_to, usage_limit):
    try:
        coupon = Coupon.objects.get(id=coupon_id)
    except Coupon.DoesNotExist:
        raise ValueError("Coupon not found.")
    coupon.code = code
    coupon.discount_percent = Decimal(discount_percent)
    coupon.valid_from = parse_datetime_with_fallback(valid_from)
    coupon.valid_to = parse_datetime_with_fallback(valid_to)
    coupon.usage_limit = usage_limit
    coupon.save()
    return coupon


# Coupon Deletion
def delete_coupon(coupon_id):
    deleted, _ = Coupon.objects.filter(id=coupon_id).delete()
    if not deleted:
        raise ValueError("Coupon not found.")


# Assign Coupon to User
def assign_coupon_to_user(coupon, user):
    assignment, created = CouponAssignment.objects.get_or_create(
        coupon=coupon,
        user=user
    )
    return assignment


# Get Coupons Assigned to User
def get_coupons_assigned_to_user(user):
    return Coupon.objects.filter(
        couponassignment__user=user,
        active=True
    ).distinct()


# Class for error validation
class CouponValidationError(Exception):
    pass


# Validate Coupon for User
def validate_coupon_for_user(user, coupon: Coupon):
    if not coupon.active:
        raise CouponValidationError("Coupon is inactive.")
    now = timezone.now()
    if coupon.valid_from > now or coupon.valid_to < now:
        raise CouponValidationError("Coupon expired.")
    if coupon.used_count >= coupon.usage_limit:
        raise CouponValidationError("Coupon usage limit reached.")
    if not CouponAssignment.objects.filter(coupon=coupon,user=user).exists():
        raise CouponValidationError("Coupon not assigned to user.")
    if CouponUsage.objects.filter(coupon=coupon,user=user).exists():
        raise CouponValidationError("Coupon already used.")
    return coupon


# Apply Coupon by ID
def apply_coupon_by_id(user, coupon_id):
    try:
        coupon = Coupon.objects.get(id=coupon_id,active=True)
    except Coupon.DoesNotExist:
        raise CouponValidationError("Invalid coupon.")
    return validate_coupon_for_user(user, coupon)


# Coupon store in the session
def store_coupon_in_session(request, coupon: Coupon):
    request.session["applied_coupon"] = {
        "coupon_id": coupon.id,
        "applied_at": timezone.now().isoformat(),
    }
    request.session.modified = True


# Remove the coupon from the session
def remove_coupon_from_session(request):
    if "applied_coupon" in request.session:
        del request.session["applied_coupon"]
        request.session.modified = True


# Mark as Coupon was used or not
def mark_coupon_used(user, coupon):
    with transaction.atomic():
        if CouponUsage.objects.select_for_update().filter(coupon=coupon,user=user).exists():
            return
        CouponUsage.objects.create(coupon=coupon,user=user)
        coupon.used_count = CouponUsage.objects.filter(coupon=coupon).count()
        coupon.save(update_fields=["used_count"])

