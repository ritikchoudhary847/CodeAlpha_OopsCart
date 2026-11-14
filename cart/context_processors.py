from .models import Cart


def cart_summary(request):
    cart = None

    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()

    elif request.session.session_key:
        cart = Cart.objects.filter(
            session_key=request.session.session_key,
            user__isnull=True,
        ).first()

    cart_count = 0

    if cart:
        cart_count = sum(
            cart.items.values_list("quantity", flat=True)
        )

    return {"cart_count": cart_count}