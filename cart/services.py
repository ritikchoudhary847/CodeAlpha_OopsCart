from django.db import transaction
from django.shortcuts import get_object_or_404

from .models import Cart, CartItem
from store.models import Product


def get_current_cart(request):
    """Return the authenticated or session-based cart."""

    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        return cart

    if not request.session.session_key:
        request.session.create()

    cart, _ = Cart.objects.get_or_create(
        session_key=request.session.session_key,
        defaults={"user": None},
    )

    return cart



@transaction.atomic
def add_product_to_cart(request, product, quantity=1):
    if quantity < 1:
        raise ValueError("Quantity must be at least 1.")

    product = get_object_or_404(
        Product.objects.select_for_update(),
        pk=product.pk,
        is_active=True,
        category__is_active=True,
    )

    if product.stock < 1:
        raise ValueError("This product is currently out of stock.")

    if quantity > product.stock:
        raise ValueError(
            f"Only {product.stock} units are currently available."
        )

    cart = get_current_cart(request)

    item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={"quantity": quantity},
    )

    if not created:
        new_quantity = item.quantity + quantity

        if new_quantity > product.stock:
            raise ValueError(
                f"Only {product.stock} units are currently available."
            )

        item.quantity = new_quantity
        item.save(update_fields=["quantity"])

    return item

@transaction.atomic
def merge_guest_cart(user, guest_session_key):
    """Merge guest cart into the customer's existing cart."""

    if not guest_session_key:
        return

    guest_cart = Cart.objects.filter(
        session_key=guest_session_key,
        user__isnull=True,
    ).first()

    if not guest_cart:
        return

    customer_cart, _ = Cart.objects.get_or_create(user=user)

    guest_items = CartItem.objects.select_for_update().filter(
        cart=guest_cart
    ).select_related("product")

    for guest_item in guest_items:
        product = guest_item.product

        if not product.is_active or product.stock < 1:
            continue

        existing_item = CartItem.objects.filter(
            cart=customer_cart,
            product=product,
        ).first()

        if existing_item:
            existing_item.quantity = min(
                existing_item.quantity + guest_item.quantity,
                product.stock,
            )

            existing_item.save(update_fields=["quantity"])

        else:
            CartItem.objects.create(
                cart=customer_cart,
                product=product,
                quantity=min(guest_item.quantity, product.stock),
            )

    guest_cart.delete()


def get_cart_totals(cart):
    items = list(
        cart.items.select_related(
            "product",
            "product__category",
        )
    )

    subtotal = sum(
        (item.product.price * item.quantity for item in items),
        start=0,
    )

    return {
        "items": items,
        "subtotal": subtotal,
        "total_quantity": sum(item.quantity for item in items),
    }