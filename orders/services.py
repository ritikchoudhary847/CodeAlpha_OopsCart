
from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction

from cart.models import Cart
from orders.models import Order, OrderItem
from store.models import Product


FREE_SHIPPING_THRESHOLD = Decimal("999.00")
STANDARD_SHIPPING_FEE = Decimal("79.00")


@transaction.atomic
def place_order(user, cart, customer_data):
    locked_cart = Cart.objects.select_for_update().get(
        pk=cart.pk
    )

    cart_items = list(
        locked_cart.items.select_for_update().select_related(
            "product",
            "product__category",
        )
    )

    if not cart_items:
        raise ValidationError("Your cart is empty.")

    validated_items = []
    subtotal = Decimal("0.00")

    # Validate every product before creating the order or changing stock.
    for cart_item in cart_items:
        try:
            product = (
                Product.objects
                .select_for_update()
                .select_related("category")
                .get(pk=cart_item.product_id)
            )
        except Product.DoesNotExist:
            raise ValidationError(
                "A product in your cart is no longer available."
            )

        if not product.is_active or not product.category.is_active:
            raise ValidationError(
                f"{product.name} is currently unavailable."
            )

        if cart_item.quantity < 1:
            raise ValidationError("Invalid product quantity.")

        if product.stock < cart_item.quantity:
            raise ValidationError(
                f"Only {product.stock} units of "
                f"{product.name} are available."
            )

        line_total = product.price * cart_item.quantity
        subtotal += line_total

        validated_items.append({
            "product": product,
            "quantity": cart_item.quantity,
            "unit_price": product.price,
            "line_total": line_total,
        })

    # Calculate order charges.
    shipping_fee = (
        Decimal("0.00")
        if subtotal >= FREE_SHIPPING_THRESHOLD
        else STANDARD_SHIPPING_FEE
    )

    discount = Decimal("0.00")
    total = subtotal + shipping_fee - discount

    # Create the order.
    order = Order.objects.create(
        user=user,
        full_name=customer_data["full_name"],
        email=customer_data["email"],
        phone=customer_data["phone"],
        address_line_1=customer_data["address_line_1"],
        address_line_2=customer_data.get("address_line_2", ""),
        city=customer_data["city"],
        state=customer_data["state"],
        postal_code=customer_data["postal_code"],
        country=customer_data.get("country", "India"),
        customer_note=customer_data.get("customer_note", ""),
        subtotal=subtotal,
        shipping_fee=shipping_fee,
        discount=discount,
        total=total,
        payment_method=Order.PaymentMethod.COD,
    )

    # Deduct stock and create order-item snapshots.
    for item in validated_items:
        product = item["product"]

        product.stock -= item["quantity"]
        product.save(update_fields=["stock"])

        OrderItem.objects.create(
            order=order,
            product=product,
            product_name=product.name,
            product_sku=product.sku,
            unit_price=item["unit_price"],
            quantity=item["quantity"],
            line_total=item["line_total"],
        )

    # Clear the cart only after successful order creation.
    locked_cart.items.all().delete()

    return order
