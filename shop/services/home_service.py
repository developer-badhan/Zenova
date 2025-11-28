from shop.models.product_model import Product
from shop.models.category_model import Category

def get_homepage_context(user=None):
    """
    Build homepage context for both guests and logged-in users.
    """
    context = {
        "products": [],
        "categories": [],
        "wishlist_count": 0,
        "user_logged_in": False,
    }

    try:
        # Latest 6 active products
        context["products"] = Product.objects.filter(is_active=True).order_by("-created_at")[:6]

        # All categories
        context["categories"] = Category.objects.all().order_by("name")

        # If logged-in, show wishlist count
        if user and user.is_authenticated:
            context["user_logged_in"] = True
            context["wishlist_count"] = user.wishlists.count()

    except Exception as e:
        print(f"[HomeService] Error fetching homepage data: {e}")

    return context
