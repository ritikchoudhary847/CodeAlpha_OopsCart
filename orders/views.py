
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import render, redirect, get_object_or_404

from cart.services import get_current_cart, get_cart_totals
from orders.forms import CheckoutForm
from orders.models import Order
from orders.services import (
    place_order,
    FREE_SHIPPING_THRESHOLD,
    STANDARD_SHIPPING_FEE,
)


@login_required
def checkout(request):
    cart = get_current_cart(request)
    cart_data = get_cart_totals(cart)

    if not cart_data["items"]:
        messages.warning(request, "Your cart is empty.")
        return redirect("cart:detail")

    if request.method == "POST":
        form = CheckoutForm(request.POST)

        if form.is_valid():
            try:
                order = place_order(
                    request.user,
                    cart,
                    form.cleaned_data,
                )

                messages.success(
                    request,
                    "Your order has been placed successfully!"
                )

                return redirect(
                    "orders:confirmation",
                    order_number=order.order_number,
                )

            except ValidationError as error:
                for error_message in error.messages:
                    messages.error(request, error_message)

    else:
        form = CheckoutForm(
            initial={
                "full_name": request.user.get_full_name(),
                "email": request.user.email,
                "phone": request.user.phone_number,
                "country": "India",
            }
        )

    subtotal = cart_data["subtotal"]

    shipping_fee = (
        Decimal("0.00")
        if subtotal >= FREE_SHIPPING_THRESHOLD
        else STANDARD_SHIPPING_FEE
    )

    remaining_for_free_shipping = max(
        Decimal("0.00"),
        FREE_SHIPPING_THRESHOLD - subtotal,
    )

    total = subtotal + shipping_fee

    context = {
        "form": form,
        "cart": cart,
        "cart_items": cart_data["items"],
        "subtotal": subtotal,
        "shipping_fee": shipping_fee,
        "remaining_for_free_shipping": remaining_for_free_shipping,
        "total": total,
    }

    return render(request, "orders/checkout.html", context)


@login_required
def order_confirmation(request, order_number):
    order = get_object_or_404(
        Order,
        order_number=order_number,
        user=request.user,
    )

    return render(
        request,
        "orders/confirmation.html",
        {"order": order},
    )


@login_required
def order_history(request):
    orders = (
        Order.objects
        .filter(user=request.user)
        .prefetch_related("items")
        .order_by("-created_at")
    )

    return render(
        request,
        "orders/history.html",
        {"orders": orders},
    )
