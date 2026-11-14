
from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from cart.models import Cart, CartItem
from orders.models import Order, OrderItem
from orders.services import place_order
from store.models import Category, Product


User = get_user_model()


class CheckoutServiceTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="checkoutuser",
            email="checkout@example.com",
            password="TestPassword123!",
        )

        self.category = Category.objects.create(
            name="Test Category",
            slug="test-category",
            is_active=True,
        )

        self.product = Product.objects.create(
            name="Test Product",
            sku="TEST-001",
            category=self.category,
            price=Decimal("500.00"),
            stock=10,
            is_active=True,
        )

        self.cart = Cart.objects.create(user=self.user)

        self.cart_item = CartItem.objects.create(
            cart=self.cart,
            product=self.product,
            quantity=2,
        )

        self.customer_data = {
            "full_name": "Test Customer",
            "email": "customer@example.com",
            "phone": "9876543210",
            "address_line_1": "Test Street",
            "address_line_2": "",
            "city": "Delhi",
            "state": "Delhi",
            "postal_code": "110001",
            "country": "India",
            "customer_note": "",
        }

    def test_successful_order_creation(self):
        order = place_order(
            self.user,
            self.cart,
            self.customer_data,
        )

        self.product.refresh_from_db()

        self.assertEqual(Order.objects.count(), 1)
        self.assertEqual(OrderItem.objects.count(), 1)
        self.assertEqual(order.subtotal, Decimal("1000.00"))
        self.assertEqual(order.shipping_fee, Decimal("0.00"))
        self.assertEqual(order.total, Decimal("1000.00"))
        self.assertEqual(self.product.stock, 8)
        self.assertEqual(self.cart.items.count(), 0)

    def test_standard_shipping_below_threshold(self):
        self.cart_item.quantity = 1
        self.cart_item.save()

        order = place_order(
            self.user,
            self.cart,
            self.customer_data,
        )

        self.assertEqual(order.subtotal, Decimal("500.00"))
        self.assertEqual(order.shipping_fee, Decimal("79.00"))
        self.assertEqual(order.total, Decimal("579.00"))

    def test_insufficient_stock_rejects_order(self):
        self.cart_item.quantity = 20
        self.cart_item.save()

        with self.assertRaises(ValidationError):
            place_order(
                self.user,
                self.cart,
                self.customer_data,
            )

        self.product.refresh_from_db()

        self.assertEqual(Order.objects.count(), 0)
        self.assertEqual(self.product.stock, 10)
        self.assertEqual(self.cart.items.count(), 1)

    def test_inactive_product_rejects_order(self):
        self.product.is_active = False
        self.product.save()

        with self.assertRaises(ValidationError):
            place_order(
                self.user,
                self.cart,
                self.customer_data,
            )

        self.product.refresh_from_db()

        self.assertEqual(Order.objects.count(), 0)
        self.assertEqual(self.product.stock, 10)
        self.assertEqual(self.cart.items.count(), 1)

    def test_inactive_category_rejects_order(self):
        self.category.is_active = False
        self.category.save()

        with self.assertRaises(ValidationError):
            place_order(
                self.user,
                self.cart,
                self.customer_data,
            )

        self.product.refresh_from_db()

        self.assertEqual(Order.objects.count(), 0)
        self.assertEqual(self.product.stock, 10)
        self.assertEqual(self.cart.items.count(), 1)

    def test_transaction_rolls_back_on_order_item_failure(self):
        with patch(
            "orders.services.OrderItem.objects.create",
            side_effect=RuntimeError("Simulated database failure"),
        ):
            with self.assertRaises(RuntimeError):
                place_order(
                    self.user,
                    self.cart,
                    self.customer_data,
                )

        self.product.refresh_from_db()

        self.assertEqual(Order.objects.count(), 0)
        self.assertEqual(OrderItem.objects.count(), 0)
        self.assertEqual(self.product.stock, 10)
        self.assertEqual(self.cart.items.count(), 1)
