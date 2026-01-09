from django.views import View
from django.shortcuts import redirect, render
from django.contrib import messages
from decorators import signin_required,customer_required,inject_authenticated_user,login_admin_required
from shop.models import Cart,Order
from shop.services import cart_service, order_service



# Order Preview before Creation
class OrderPreviewView(View):
    @signin_required
    @customer_required
    @inject_authenticated_user
    def get(self, request):
        cart = request.user.cart
        if not cart.items.exists():
            messages.warning(request, "Your cart is empty.")
            return redirect("cart_detail")
        cart_totals = cart_service.calculate_cart_total(cart, request)
        return render(request,"order/order_detail.html",{"cart": cart, "cart_totals": cart_totals})

    @signin_required
    @customer_required
    @inject_authenticated_user
    def post(self, request):
        return redirect("order_create")


# Order Creation
class OrderCreateView(View):
    @signin_required
    @customer_required
    @inject_authenticated_user
    def get(self, request):
        cart = request.user.cart
        if not cart.items.exists():
            messages.error(request, "Cart is empty.")
            return redirect("cart_detail")
        cart_totals = cart_service.calculate_cart_total(cart, request)
        return render(request,"order/order_create.html",{"cart": cart, "cart_totals": cart_totals})

    @signin_required
    @customer_required
    @inject_authenticated_user
    def post(self, request):
        try:
            cart = request.user.cart
            cart_totals = cart_service.calculate_cart_total(cart, request)
            order = order_service.create_order_from_cart(
                user=request.user,
                cart=cart,
                cart_totals=cart_totals,
            )
            messages.success(request, "Order created successfully.")
            return redirect("payment:choose_method", order_id=order.id)
        except order_service.OrderCreationError as e:
            messages.error(request, str(e))
        except Exception as e:
            print("ORDER CREATE ERROR:", e)
            messages.error(request, "Unable to create order.")
        return redirect("order_preview")


# Order List 
class OrderListAdminView(View):
    @login_admin_required
    def get(self, request):
        try:
            orders = order_service.get_all_orders_for_admin()
            return render(
                request,
                "order/order_listadmin.html",
                {"orders": orders}
            )
        except Exception as e:
            print(f"[OrderListAdminView] Error: {e}")
            messages.error(request, "Failed to load orders.")
            return redirect("admin_dashboard")


# Order Cancelation
class OrderCancelView(View):
    @signin_required
    @customer_required
    @inject_authenticated_user
    def post(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id, user=request.user)
            order_service.cancel_order(order=order, request=request)
            messages.success(request,"Order cancelled successfully. Coupon has been removed.")
            return redirect("cart_detail")
        except Order.DoesNotExist:
            messages.error(request, "Order not found.")
        except order_service.OrderCancelError as e:
            messages.error(request, str(e))
        except Exception:
            messages.error(request, "Unable to cancel order.")
        return redirect("order_preview")


# Order Listing for User
class OrderListCustomerView(View):
    @signin_required
    @customer_required
    @inject_authenticated_user
    def get(self, request):
        try:
            orders = order_service.get_orders_for_user(user=request.user)
            return render(
                request,
                "order/order_list.html",
                {"orders": orders}
            )
        except Exception as e:
            print(f"[OrderListCustomerView] Error: {e}")
            messages.error(request, "Unable to load your orders.")
            return redirect("home")
