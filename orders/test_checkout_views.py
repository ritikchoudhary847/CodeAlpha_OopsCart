
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from cart.models import Cart
from orders.models import Order


User = get_user_model()


class CheckoutViewIntegrityTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="checkout_customer",
            email="customer@example.com",
            password="SecureTestPass123!",
        )

        self.other_user = User.objects.create_user(
            username="another_customer",
            email="another@example.com",
            password="SecureTestPass123!",
        )

        self.cart = Cart.objects.create(user=self.user)

        self.order = Order.objects.create(
            user=self.user,
            full_name="Checkout Customer",
            email="customer@example.com",
            phone="9876543210",
            address_line_1="123 Test Street",
            city="Lucknow",
            state="Uttar Pradesh",
            postal_code="226001",
            country="India",
            subtotal=Decimal("500.00"),
            shipping_fee=Decimal("79.00"),
            discount=Decimal("0.00"),
            total=Decimal("579.00"),
        )

    def test_empty_cart_redirects_to_cart(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse("orders:checkout")
        )

        self.assertRedirects(
            response,
            reverse("cart:detail"),
        )

    def test_anonymous_user_cannot_access_checkout(self):
        response = self.client.get(
            reverse("orders:checkout")
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn(
            reverse("accounts:login"),
            response.url,
        )

    def test_order_owner_can_view_confirmation(self):
        self.client.force_login(self.user)

        response = self.client.get(
            reverse(
                "orders:confirmation",
                kwargs={"order_number": self.order.order_number},
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["order"].pk,
            self.order.pk,
        )

    def test_another_user_cannot_view_order_confirmation(self):
        self.client.force_login(self.other_user)

        response = self.client.get(
            reverse(
                "orders:confirmation",
                kwargs={"order_number": self.order.order_number},
            )
        )

        self.assertEqual(response.status_code, 404)

    def test_anonymous_user_cannot_view_order_confirmation(self):
        response = self.client.get(
            reverse(
                "orders:confirmation",
                kwargs={"order_number": self.order.order_number},
            )
        )

        self.assertEqual(response.status_code, 302)
        self.assertIn(
            reverse("accounts:login"),
            response.url,
        )
