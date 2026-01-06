from shop.models import Cart, CartItem, Product
from django.core.exceptions import ObjectDoesNotExist
from decimal import Decimal


# User Validation
def is_valid_user(user):
    return user and hasattr(user, 'id') and isinstance(user.id, int)


# User ID Validation
def is_valid_id(value):
    try:
        return int(value) > 0
    except (TypeError, ValueError):
        return False


# Quantity Validation
def is_valid_quantity(value):
    try:
        return int(value) > 0
    except (TypeError, ValueError):
        return False


# Get Cart
def get_cart(user):
    if not is_valid_user(user):
        print("Invalid user object.")
        return None
    try:
        cart, _ = Cart.objects.get_or_create(user=user)
        return cart
    except Exception as e:
        print(f"Error fetching cart: {e}")
        return None


# Get Cart Items
def get_cart_items(user):
    cart = get_cart(user)
    if not cart:
        return []
    try:
        return cart.items.select_related('product').all()
    except Exception as e:
        print(f"Error fetching cart items: {e}")
        return []


# Add Item to Cart
def add_item(user, product_id, quantity=1):
    if not is_valid_user(user) or not is_valid_id(product_id) or not is_valid_quantity(quantity):
        print("Invalid input for adding item.")
        return None
    try:
        cart = get_cart(user)
        product = Product.objects.get(id=int(product_id))

        item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        item.quantity = item.quantity + int(quantity) if not created else int(quantity)
        item.save()
        return item
    except ObjectDoesNotExist:
        print(f"Product with ID {product_id} not found.")
        return None
    except Exception as e:
        print(f"Error adding item to cart: {e}")
        return None


# SKU Validation
def is_valid_sku(sku):
    if not sku:
        return False
    if not isinstance(sku, str):
        return False
    return bool(sku.strip())


# Check_Avaliabilty
def check_avaliabilty(value):
    if not is_valid_sku(value):
        print(f"check_avaliabilty: Invalid SKU provided: {value!r}")
        return False
    sku = value.strip()
    try:
        product = Product.objects.get(sku=sku, is_active=True)
    except Product.DoesNotExist:
        print(f"check_avaliabilty: Product not found for SKU: {sku}")
        return False
    except Exception as e:
        print(f"check_avaliabilty: Unexpected error fetching product for SKU {sku}: {e}")
        return False
    stock = product.stock
    if stock is None:
        print(f"check_avaliabilty: SKU {sku} => stock = unlimited (None)")
        return None
    try:
        stock_int = int(stock)
    except (TypeError, ValueError):
        print(f"check_avaliabilty: SKU {sku} => invalid stock value: {stock!r}")
        return False
    print(f"check_avaliabilty: SKU {sku} => stock = {stock_int}")
    return stock_int


# Update  Item to the Cart 
def update_item(user, product_sku, quantity, expected_sku=None):
    if not is_valid_user(user):
        print("update_item: Invalid user.")
        return None
    if not is_valid_sku(product_sku):
        print(f"update_item: Invalid product_sku provided: {product_sku!r}")
        return None
    if not is_valid_quantity(quantity):
        print(f"update_item: Invalid quantity provided: {quantity!r}")
        return None
    if expected_sku:
        if not is_valid_sku(expected_sku):
            print("update_item: Invalid expected_sku provided.")
            return None
        if product_sku.strip().lower() != expected_sku.strip().lower():
            print(f"update_item: SKU mismatch between expected ({expected_sku}) and provided ({product_sku}).")
            return None
    sku = product_sku.strip()
    try:
        qty_int = int(quantity)
        if qty_int <= 0:
            print(f"update_item: Quantity must be positive. Provided: {qty_int}")
            return None
    except (TypeError, ValueError):
        print(f"update_item: Quantity is not an integer: {quantity!r}")
        return None
    try:
        cart = get_cart(user)
        if not cart:
            print("update_item: Could not fetch cart for user.")
            return None
        try:
            product = Product.objects.get(sku=sku, is_active=True)
        except Product.DoesNotExist:
            print(f"update_item: Product not found for SKU: {sku}")
            return None
        stock_info = check_avaliabilty(sku)
        if stock_info is False:
            print(f"update_item: check_avaliabilty failed for SKU {sku}")
            return None
        if stock_info is not None:
            if qty_int > stock_info:
                print(f"update_item: Requested qty {qty_int} exceeds available stock {stock_info} for SKU {sku}")
                return None
        try:
            item = CartItem.objects.get(cart=cart, product=product)
        except CartItem.DoesNotExist:
            print(f"update_item: Cart item not found for product SKU: {sku}")
            return None
        item.quantity = qty_int
        item.save()
        print(f"update_item: Updated SKU {sku} to quantity {qty_int} for user_id={user.id}")
        return item
    except Exception as e:
        print(f"update_item: Unexpected error updating cart item: {e}")
        return None


# Remove Item from the Cart
def remove_item(user, product_sku, expected_sku=None):
    if not is_valid_user(user) or not is_valid_sku(product_sku):
        print("Invalid input for removing item.")
        return False
    if expected_sku:
        if not is_valid_sku(expected_sku):
            print("Invalid expected_sku provided.")
            return False
        if product_sku.strip().lower() != expected_sku.strip().lower():
            print("SKU mismatch between expected and provided SKU.")
            return False
    sku = product_sku.strip()
    try:
        cart = get_cart(user)
        if not cart:
            print("Could not fetch cart for user.")
            return False
        try:
            product = Product.objects.get(sku=sku, is_active=True)
        except Product.DoesNotExist:
            print(f"Product not found for SKU: {sku}")
            return False
        try:
            item = CartItem.objects.get(cart=cart, product=product)
        except CartItem.DoesNotExist:
            print(f"Cart item not found for product SKU: {sku}")
            return False
        item.delete()
        return True
    except Exception as e:
        print(f"Error removing item from cart: {e}")
        return False


# Clear Cart
def clear_cart(user):
    if not is_valid_user(user):
        print("Invalid user for clearing cart.")
        return False
    try:
        cart = get_cart(user)
        cart.items.all().delete()
        return True
    except Exception as e:
        print(f"Error clearing cart: {e}")
        return False


# Calculate the total price in Grand Cart
def calculate_cart_total(cart, request=None):
    items = cart.items.select_related("product")
    subtotal = sum(
        item.product.price * item.quantity
        for item in items
    )
    discount_amount = Decimal("0.00")
    coupon = None
    if request:
        coupon_data = request.session.get("applied_coupon")
        if coupon_data:
            coupon = coupon_data
            discount_percent = Decimal(coupon_data["discount_percent"])
            discount_amount = (subtotal * discount_percent) / Decimal("100")
    grand_total = subtotal - discount_amount
    return {
        "subtotal": subtotal,
        "discount": discount_amount,
        "grand_total": grand_total,
        "coupon": coupon,
    }
