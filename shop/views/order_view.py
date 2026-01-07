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
        try:
            cart = request.user.cart
        except Cart.DoesNotExist:
            messages.error(request, "Cart not found.")
            return redirect("cart_detail")
        if not cart.items.exists():
            messages.warning(request, "Your cart is empty.")
            return redirect("cart_detail")
        cart_totals = cart_service.calculate_cart_total(cart, request)
        context = {
            "cart": cart,
            "cart_totals": cart_totals,
        }
        return render(request, "order/order_detail.html", context)


# Order Creation
class OrderCreateView(View):
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
            return redirect(
                "choose_method",
                order_id=order.id
            )
        except order_service.OrderCreationError as e:
            messages.error(request, str(e))
        except Exception:
            messages.error(request, "Unable to create order.")
        context = {
            "cart": cart,
            "cart_totals": cart_totals,
        }
        return render(request, "order/order_create.html", context)


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








































'''
from django.views import View
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponseNotFound
from shop.services import order_service
from decorators import signin_required,customer_required,inject_authenticated_user



# View for listing orders
class OrderListView(View):
    @signin_required
    @customer_required
    @inject_authenticated_user
    def get(self, request):
        try:
            orders = order_service.get_all_orders(user=request.user)
            return render(request, 'order/order_list.html', {'orders': orders})
        except Exception as e:
            print(f"[OrderListView] Error: {e}")
            messages.error(request, "Failed to load orders.")
            return render(request, 'order/order_list.html', {'orders': []})


# View for displaying order details
class OrderDetailView(View):
    @signin_required
    @customer_required
    @inject_authenticated_user
    def get(self, request, order_id):
        order = order_service.get_order_by_id(order_id)
        if order:
            return render(request, 'order/order_detail.html', {'order': order})
        return HttpResponseNotFound("Order not found.")


# View for creating a new order
class OrderCreateView(View):
    @signin_required
    @customer_required
    @inject_authenticated_user
    def get(self, request):
        return render(request, 'order/order_create.html')

    @signin_required
    @customer_required
    @inject_authenticated_user
    def post(self, request):
        try:
            items = []
            count = int(request.POST.get('item_count', 0))
            for i in range(1, count + 1):
                product_id = request.POST.get(f'product_id_{i}')
                quantity = request.POST.get(f'quantity_{i}')
                if product_id and quantity:
                    items.append({
                        'product_id': product_id,
                        'quantity': int(quantity)
                    })
            coupon_code = request.POST.get('coupon_code')
            order = order_service.create_order(user=request.user, items=items, coupon_code=coupon_code)
            if order:
                messages.success(request, "Order placed successfully.")
                return redirect('order_detail', order_id=order.id)
        except Exception as e:
            print(f"[OrderCreateView] Error: {e}")
            messages.error(request, "Failed to place order.")
        return redirect('order_create')


# View for deleting an existing order
class OrderDeleteView(View):
    @signin_required
    @customer_required
    @inject_authenticated_user
    def post(self, request, order_id):
        try:
            success = order_service.delete_order(order_id)
            if success:
                messages.success(request, "Order deleted.")
            else:
                messages.error(request, "Failed to delete order.")
        except Exception as e:
            print(f"[OrderDeleteView] Error: {e}")
            messages.error(request, "An error occurred while deleting the order.")
        return redirect('order_list')


# Proceed to Payment
class OrderCreateFromCartView(View):
    @signin_required
    @customer_required
    @inject_authenticated_user
    def get(self, request):
        try:
            # fetch cart items
            from shop.services.cart_service import get_cart_items  # adjust import path if needed
            cart_items = get_cart_items(request.user)

            if not cart_items:
                messages.error(request, "Your cart is empty.")
                return redirect('cart')  # cart url name

            items = [
                {"product_id": item.product.id, "quantity": item.quantity}
                for item in cart_items
            ]

            # create order
            order = order_service.create_order(
                user=request.user,
                items=items,
                coupon_code=None  # apply later if needed
            )

            if order:
                messages.success(request, "Order created. Complete payment to place order.")
                return redirect('order_detail', order_id=order.id)

        except Exception as e:
            print(f"[OrderCreateFromCartView] Error: {e}")
            messages.error(request, "Unable to create order. Try again.")

        return redirect('cart')

'''