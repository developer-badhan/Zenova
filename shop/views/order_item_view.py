'''


from django.views import View
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponseNotFound
from decorators.auth_decorators import signin_required,customer_required, inject_authenticated_user
from shop.services import order_item_service
from shop.models import Order



# View for listing order items
class OrderItemListView(View):
    @signin_required
    @customer_required
    @inject_authenticated_user
    def get(self, request, order_id):
        try:
            items = order_item_service.get_items_by_order(order_id)
            order = Order.objects.get(id=order_id)
            return render(request, 'order/order_item_list.html', {'items': items, 'order': order})
        except Order.DoesNotExist:
            return HttpResponseNotFound("Order not found.")
        except Exception as e:
            print(f"[OrderItemListView] Error: {e}")
            messages.error(request, "Failed to load order items.")
            return redirect('order_list')


# View for creating a new order item
class OrderItemCreateView(View):
    @signin_required
    @customer_required
    @inject_authenticated_user
    def get(self, request, order_id):
        return render(request, 'order/order_item_create.html', {'order_id': order_id})

    @signin_required
    @customer_required
    @inject_authenticated_user
    def post(self, request, order_id):
        try:
            product_id = request.POST.get('product_id')
            quantity = request.POST.get('quantity')
            price = request.POST.get('price')

            item = order_item_service.create_order_item(
                order=Order.objects.get(id=order_id),
                product_id=product_id,
                quantity=int(quantity),
                price=float(price) if price else None
            )
            if item:
                messages.success(request, "Order item added.")
                return redirect('order_item_list', order_id=order_id)
        except Order.DoesNotExist:
            messages.error(request, "Order not found.")
        except Exception as e:
            print(f"[OrderItemCreateView] Error: {e}")
            messages.error(request, "Failed to add order item.")
        return redirect('order_item_create', order_id=order_id)


# View for updating an existing order item
class OrderItemUpdateView(View):
    @signin_required
    @customer_required
    @inject_authenticated_user
    def get(self, request, item_id):
        item = order_item_service.get_item_by_id(item_id)
        if item:
            return render(request, 'order/order_item_update.html', {'item': item})
        return HttpResponseNotFound("Order item not found.")

    @signin_required
    @customer_required
    @inject_authenticated_user
    def post(self, request, item_id):
        try:
            quantity = request.POST.get('quantity')
            price = request.POST.get('price')
            item = order_item_service.update_order_item(
                item_id=item_id,
                quantity=int(quantity) if quantity else None,
                price=float(price) if price else None
            )
            if item:
                messages.success(request, "Order item updated.")
                return redirect('order_item_list', order_id=item.order.id)
        except Exception as e:
            print(f"[OrderItemUpdateView] Error: {e}")
            messages.error(request, "Failed to update order item.")
        return redirect('order_item_update', item_id=item_id)
    

# View for deleting an existing order item
class OrderItemDeleteView(View):
    @signin_required
    @customer_required
    @inject_authenticated_user
    def post(self, request, item_id):
        item = order_item_service.get_item_by_id(item_id)
        if not item:
            messages.error(request, "Order item not found.")
            return redirect('order_list')
        order_id = item.order.id
        try:
            success = order_item_service.delete_order_item(item_id)
            if success:
                messages.success(request, "Order item deleted.")
            else:
                messages.error(request, "Failed to delete order item.")
        except Exception as e:
            print(f"[OrderItemDeleteView] Error: {e}")
            messages.error(request, "An error occurred while deleting the item.")
        return redirect('order_item_list', order_id=order_id)
'''


