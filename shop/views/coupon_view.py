from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponseNotFound
from django.views import View
from constants.enums import Role
from shop.models import Coupon
from shop.services import coupon_service
from user.services import enduser_service
from decorators import customer_required,login_admin_required_with_user,inject_authenticated_user
from django.contrib.auth import get_user_model



# Coupon list view
class CouponListView(View):
    @login_admin_required_with_user
    def get(self, request):
        coupons = coupon_service.get_all_coupons()
        customers = enduser_service.get_all_customers()
        return render(request, 'coupon/coupon_list.html', {
            'coupons': coupons,
            'customers': customers
        })


# Coupon creation view 
class CouponCreateView(View):
    @login_admin_required_with_user
    def get(self, request):
        return render(request, 'coupon/coupon_create.html')

    @login_admin_required_with_user
    def post(self, request):
        code = request.POST.get('code')
        discount_percent = request.POST.get('discount_percent')
        valid_from = request.POST.get('valid_from')
        valid_to = request.POST.get('valid_to')
        usage_limit = request.POST.get('usage_limit')
        try:
            coupon_service.create_coupon(
                code, discount_percent, valid_from, valid_to, usage_limit, created_by=request.user
            )
            messages.success(request, "Coupon created successfully.")
            return redirect('coupon_list')
        except Exception as e:
            messages.error(request, f"Failed to create coupon: {e}")
            return render(request, 'coupon/coupon_create.html')


# Coupon update view 
class CouponUpdateView(View):
    @login_admin_required_with_user
    def get(self, request, coupon_id):
        try:
            coupon = Coupon.objects.get(id=coupon_id)
            return render(request, 'coupon/coupon_update.html', {'coupon': coupon})
        except Coupon.DoesNotExist:
            return HttpResponseNotFound("Coupon not found.")

    @login_admin_required_with_user
    def post(self, request, coupon_id):
        code = request.POST.get('code')
        discount_percent = request.POST.get('discount_percent')
        valid_from = request.POST.get('valid_from')
        valid_to = request.POST.get('valid_to')
        usage_limit = request.POST.get('usage_limit')
        try:
            coupon_service.update_coupon(coupon_id, code, discount_percent, valid_from, valid_to, usage_limit)
            messages.success(request, "Coupon updated successfully.")
            return redirect('coupon_list')
        except Exception as e:
            messages.error(request, f"Failed to update coupon: {e}")
            return redirect('coupon_update', coupon_id=coupon_id)


# Coupon Delete View 
class CouponDeleteView(View):
    @login_admin_required_with_user
    def get(self, request, coupon_id):
        try:
            coupon = Coupon.objects.get(id=coupon_id)
            return render(request, 'coupon/coupon_delete.html', {'coupon': coupon})
        except Coupon.DoesNotExist:
            messages.error(request, "Coupon not found.")
            return redirect('coupon_list')

    @login_admin_required_with_user
    def post(self, request, coupon_id):
        try:
            coupon_service.delete_coupon(coupon_id)
            messages.success(request, "Coupon deleted successfully.")
            return redirect('coupon_list')
        except Exception as e:
            messages.error(request, f"Failed to delete coupon: {e}")
            return redirect('coupon_list')


# Assign coupon to user view 
class AssignCouponToUserView(View):
    @login_admin_required_with_user
    def post(self, request, coupon_id):
        user_id = request.POST.get('user_id')
        try:
            coupon = Coupon.objects.get(id=coupon_id)
            User = get_user_model()
            user = User.objects.get(id=user_id)
            if user.role != Role.ENDUSER_CUSTOMER:
                messages.error(request, "Only customers can be assigned coupons.")
                return redirect('coupon_list')
            coupon_service.assign_coupon_to_user(coupon=coupon,user=user)
            messages.success(request,f"Coupon assigned to {user.email}.")
        except Exception as e:
            messages.error(request, f"Error assigning coupon: {e}")
        return redirect('coupon_list')


# Customer coupon list view
class CustomerCouponListView(View):
    @inject_authenticated_user
    @customer_required
    def get(self, request):
        user = request.user
        coupons = coupon_service.get_coupons_assigned_to_user(user)
        return render(request, 'coupon/customer_coupon_list.html', {'coupons': coupons})

'''
# Coupon Apply View 
class CouponApplyView(View):
    @inject_authenticated_user
    @customer_required
    def post(self, request, coupon_id):
        try:
            coupon = coupon_service.apply_coupon_by_id(
                user=request.user,
                coupon_id=coupon_id
            )
            # Store coupon in session
            request.session["applied_coupon"] = {
                "id": coupon.id,
                "code": coupon.code,
                "discount_percent": str(coupon.discount_percent),
            }
            return render(request, "partials/coupon_message.html", {
                "type": "success",
                "message": "🎉 Coupon applied successfully!",
                "coupon": coupon,
            })
        except ValueError as e:
            msg = str(e).lower()
            if "expired" in msg:
                alert_type = "danger"
                message = "⏰ This coupon has expired."
            elif "already used" in msg:
                alert_type = "warning"
                message = "ℹ️ You already used this coupon."
            elif "usage limit" in msg:
                alert_type = "warning"
                message = "❌ Coupon usage limit reached."
            else:
                alert_type = "danger"
                message = str(e)
            return render(request, "partials/coupon_message.html", {
                "type": alert_type,
                "message": message,
                "coupon_id": coupon_id
            }, status=400)
'''

from django.views import View
from django.shortcuts import render
from shop.services import coupon_service
from shop.services.coupon_service import CouponValidationError


class CouponApplyView(View):
    @inject_authenticated_user
    @customer_required
    def post(self, request, coupon_id):
        try:
            # 1️⃣ Validate coupon
            coupon = coupon_service.apply_coupon_by_id(
                user=request.user,
                coupon_id=coupon_id
            )

            # 2️⃣ Mark coupon as USED immediately
            coupon_service.mark_coupon_used(
                request.user,
                coupon
            )

            # 3️⃣ Flush session immediately
            coupon_service.remove_coupon_from_session(request)

            return render(request, "partials/coupon_message.html", {
                "type": "success",
                "message": "🎉 Coupon applied successfully!",
                "coupon": coupon,
            })

        except CouponValidationError as e:
            coupon_service.remove_coupon_from_session(request)

            msg = str(e).lower()

            if "expired" in msg:
                alert_type = "danger"
                message = "⏰ This coupon has expired."
            elif "already used" in msg:
                alert_type = "warning"
                message = "ℹ️ You already used this coupon."
            elif "usage limit" in msg:
                alert_type = "warning"
                message = "❌ Coupon usage limit reached."
            elif "assigned" in msg:
                alert_type = "danger"
                message = "🚫 This coupon is not assigned to you."
            else:
                alert_type = "danger"
                message = str(e)

            return render(request, "partials/coupon_message.html", {
                "type": alert_type,
                "message": message,
                "coupon_id": coupon_id
            }, status=400)
