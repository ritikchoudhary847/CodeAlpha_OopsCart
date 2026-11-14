
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.db import transaction
from django.utils.http import url_has_allowed_host_and_scheme

from store.models import Product
from .models import CartItem
from .services import (
    get_current_cart,
    add_product_to_cart,
    get_cart_totals,
)


@require_POST
def add_to_cart(request, product_id):
    try:
        quantity = int(request.POST.get("quantity", 1))

        if quantity < 1:
            raise ValueError("Quantity must be at least 1.")

        product = get_object_or_404(
            Product,
            pk=product_id,
            is_active=True,
            category__is_active=True,
        )

        add_product_to_cart(request, product, quantity)

        messages.success(
            request,
            f"{product.name} added to your cart."
        )

    except (ValueError, TypeError) as error:
        messages.error(request, str(error))

    next_url = request.POST.get("next", "")

    if next_url and url_has_allowed_host_and_scheme(
        next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return redirect(next_url)

    return redirect("cart:detail")


def cart_detail(request):
    cart = get_current_cart(request)
    context = get_cart_totals(cart)

    return render(request, "cart/detail.html", context)


@require_POST
def update_cart_item(request, item_id):
    cart = get_current_cart(request)

    item = get_object_or_404(
        CartItem.objects.select_related(
            "product",
            "product__category",
        ),
        pk=item_id,
        cart=cart,
    )

    try:
        quantity = int(request.POST.get("quantity", 1))

        if quantity < 1:
            raise ValueError("Quantity must be at least 1.")

        with transaction.atomic():
            product = (
                Product.objects
                .select_for_update()
                .select_related("category")
                .get(pk=item.product_id)
            )

            if (
                not product.is_active
                or not product.category.is_active
                or product.stock < 1
            ):
                raise ValueError(
                    "This product is no longer available."
                )

            if quantity > product.stock:
                raise ValueError(
                    f"Only {product.stock} units are available."
                )

            item.quantity = quantity
            item.save(update_fields=["quantity"])

        messages.success(request, "Cart updated.")

    except (ValueError, TypeError, Product.DoesNotExist) as error:
        messages.error(request, str(error))

    return redirect("cart:detail")


@require_POST
def remove_cart_item(request, item_id):
    cart = get_current_cart(request)

    item = get_object_or_404(
        CartItem,
        pk=item_id,
        cart=cart,
    )

    item.delete()

    messages.info(request, "Item removed from your cart.")

    return redirect("cart:detail")
