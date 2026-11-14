
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from store.models import Category, Product
from .models import Cart, CartItem
from .services import (
    get_current_cart,
    add_product_to_cart,
    merge_guest_cart,
    get_cart_totals,
)

User = get_user_model()


class CartTestDataMixin:
    def setUp(self):
        self.user = User.objects.create_user(
            username="cart_customer",
            email="cart@example.com",
            password="StrongPass!234",
        )

        self.category = Category.objects.create(
            name="Cart Gadgets",
        )

        self.product = Product.objects.create(
            name="Mini Desk Vacuum",
            sku="CART-001",
            category=self.category,
            description="A compact desk vacuum.",
            price=Decimal("499.00"),
            stock=10,
            is_active=True,
        )

        self.second_product = Product.objects.create(
            name="LED Desk Lamp",
            sku="CART-002",
            category=self.category,
            description="A desk lamp.",
            price=Decimal("899.00"),
            stock=5,
            is_active=True,
        )

    def create_user_cart(self):
        return Cart.objects.get_or_create(user=self.user)[0]

    def create_guest_cart(self, session_key="guest-test-session"):
        return Cart.objects.create(session_key=session_key)


class CartServiceTests(CartTestDataMixin, TestCase):

    def test_authenticated_user_gets_personal_cart(self):
        request = self.client.request().wsgi_request
        request.user = self.user

        cart = get_current_cart(request)

        self.assertEqual(cart.user, self.user)

    def test_guest_gets_session_cart(self):
        response = self.client.get(reverse("cart:detail"))

        self.assertEqual(response.status_code, 200)

        session_key = self.client.session.session_key

        self.assertTrue(
            Cart.objects.filter(
                session_key=session_key,
                user__isnull=True,
            ).exists()
        )

    def test_add_product_creates_cart_item(self):
        cart = self.create_user_cart()

        self.client.force_login(self.user)
        request = self.client.post(reverse("cart:detail")).wsgi_request
        request.user = self.user

        item = add_product_to_cart(request, self.product, 2)

        self.assertEqual(item.cart, cart)
        self.assertEqual(item.quantity, 2)

    def test_adding_same_product_increases_quantity(self):
        cart = self.create_user_cart()
        CartItem.objects.create(
            cart=cart,
            product=self.product,
            quantity=2,
        )

        self.client.force_login(self.user)
        request = self.client.get(reverse("cart:detail")).wsgi_request
        request.user = self.user

        item = add_product_to_cart(request, self.product, 3)

        self.assertEqual(item.quantity, 5)

    def test_add_product_rejects_quantity_below_one(self):
        self.client.force_login(self.user)
        request = self.client.get(reverse("cart:detail")).wsgi_request
        request.user = self.user

        with self.assertRaises(ValueError):
            add_product_to_cart(request, self.product, 0)

    def test_add_product_rejects_quantity_above_stock(self):
        self.client.force_login(self.user)
        request = self.client.get(reverse("cart:detail")).wsgi_request
        request.user = self.user

        with self.assertRaises(ValueError):
            add_product_to_cart(request, self.product, 11)

    def test_add_product_rejects_inactive_product(self):
        self.product.is_active = False
        self.product.save()

        self.client.force_login(self.user)
        request = self.client.get(reverse("cart:detail")).wsgi_request
        request.user = self.user

        with self.assertRaises(Exception):
            add_product_to_cart(request, self.product, 1)

    def test_add_product_rejects_inactive_category(self):
        self.category.is_active = False
        self.category.save()

        self.client.force_login(self.user)
        request = self.client.get(reverse("cart:detail")).wsgi_request
        request.user = self.user

        with self.assertRaises(Exception):
            add_product_to_cart(request, self.product, 1)

    def test_guest_cart_merges_into_user_cart(self):
        guest_cart = self.create_guest_cart()
        CartItem.objects.create(
            cart=guest_cart,
            product=self.product,
            quantity=2,
        )

        merge_guest_cart(self.user, guest_cart.session_key)

        user_cart = Cart.objects.get(user=self.user)

        self.assertEqual(
            user_cart.items.get(product=self.product).quantity,
            2,
        )
        self.assertFalse(
            Cart.objects.filter(pk=guest_cart.pk).exists()
        )

    def test_guest_cart_merge_combines_existing_quantity(self):
        user_cart = self.create_user_cart()
        CartItem.objects.create(
            cart=user_cart,
            product=self.product,
            quantity=2,
        )

        guest_cart = self.create_guest_cart()
        CartItem.objects.create(
            cart=guest_cart,
            product=self.product,
            quantity=3,
        )

        merge_guest_cart(self.user, guest_cart.session_key)

        item = user_cart.items.get(product=self.product)

        self.assertEqual(item.quantity, 5)

    def test_guest_cart_merge_does_not_exceed_stock(self):
        user_cart = self.create_user_cart()
        CartItem.objects.create(
            cart=user_cart,
            product=self.product,
            quantity=8,
        )

        guest_cart = self.create_guest_cart()
        CartItem.objects.create(
            cart=guest_cart,
            product=self.product,
            quantity=8,
        )

        merge_guest_cart(self.user, guest_cart.session_key)

        item = user_cart.items.get(product=self.product)

        self.assertEqual(item.quantity, self.product.stock)

    def test_cart_totals_are_calculated_correctly(self):
        cart = self.create_user_cart()

        CartItem.objects.create(
            cart=cart,
            product=self.product,
            quantity=2,
        )
        CartItem.objects.create(
            cart=cart,
            product=self.second_product,
            quantity=1,
        )

        totals = get_cart_totals(cart)

        self.assertEqual(totals["subtotal"], Decimal("1897.00"))
        self.assertEqual(totals["total_quantity"], 3)
        self.assertEqual(len(totals["items"]), 2)


class CartViewTests(CartTestDataMixin, TestCase):

    def setUp(self):
        super().setUp()
        self.cart_url = reverse("cart:detail")

    def test_cart_page_loads(self):
        response = self.client.get(self.cart_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "cart/detail.html")

    def test_add_to_cart_requires_post(self):
        response = self.client.get(
            reverse("cart:add", args=[self.product.pk])
        )

        self.assertEqual(response.status_code, 405)

    def test_add_to_cart_view_adds_product(self):
        response = self.client.post(
            reverse("cart:add", args=[self.product.pk]),
            {"quantity": "2"},
        )

        self.assertRedirects(response, self.cart_url)

        cart = Cart.objects.get(
            session_key=self.client.session.session_key
        )

        self.assertEqual(
            cart.items.get(product=self.product).quantity,
            2,
        )

    def test_update_cart_item_changes_quantity(self):
        self.client.force_login(self.user)

        cart = self.create_user_cart()
        item = CartItem.objects.create(
            cart=cart,
            product=self.product,
            quantity=1,
        )

        response = self.client.post(
            reverse("cart:update", args=[item.pk]),
            {"quantity": "4"},
        )

        self.assertRedirects(response, self.cart_url)

        item.refresh_from_db()
        self.assertEqual(item.quantity, 4)

    def test_update_cart_item_rejects_excess_stock(self):
        self.client.force_login(self.user)

        cart = self.create_user_cart()
        item = CartItem.objects.create(
            cart=cart,
            product=self.product,
            quantity=1,
        )

        self.client.post(
            reverse("cart:update", args=[item.pk]),
            {"quantity": "11"},
        )

        item.refresh_from_db()
        self.assertEqual(item.quantity, 1)

    def test_user_cannot_update_another_users_cart_item(self):
        other_user = User.objects.create_user(
            username="other_customer",
            email="other@example.com",
            password="StrongPass!234",
        )

        other_cart = Cart.objects.create(user=other_user)
        item = CartItem.objects.create(
            cart=other_cart,
            product=self.product,
            quantity=2,
        )

        self.client.force_login(self.user)

        response = self.client.post(
            reverse("cart:update", args=[item.pk]),
            {"quantity": "5"},
        )

        self.assertEqual(response.status_code, 404)

        item.refresh_from_db()
        self.assertEqual(item.quantity, 2)

    def test_remove_cart_item(self):
        self.client.force_login(self.user)

        cart = self.create_user_cart()
        item = CartItem.objects.create(
            cart=cart,
            product=self.product,
            quantity=1,
        )

        response = self.client.post(
            reverse("cart:remove", args=[item.pk])
        )

        self.assertRedirects(response, self.cart_url)
        self.assertFalse(CartItem.objects.filter(pk=item.pk).exists())

    def test_user_cannot_remove_another_users_cart_item(self):
        other_user = User.objects.create_user(
            username="other_remove",
            email="remove@example.com",
            password="StrongPass!234",
        )

        other_cart = Cart.objects.create(user=other_user)
        item = CartItem.objects.create(
            cart=other_cart,
            product=self.product,
            quantity=1,
        )

        self.client.force_login(self.user)

        response = self.client.post(
            reverse("cart:remove", args=[item.pk])
        )

        self.assertEqual(response.status_code, 404)
        self.assertTrue(CartItem.objects.filter(pk=item.pk).exists())
