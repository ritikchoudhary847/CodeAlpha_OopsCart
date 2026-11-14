from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from .models import Category, Product


class StoreTestDataMixin:
    def setUp(self):
        self.category = Category.objects.create(
            name="Desk Gadgets",
            description="Useful desk accessories.",
        )

        self.product = Product.objects.create(
            name="Mini Desk Vacuum",
            sku="TEST-GAD-001",
            category=self.category,
            description="A compact desk cleaning gadget.",
            price=Decimal("499.00"),
            compare_at_price=Decimal("599.00"),
            stock=10,
            is_active=True,
            is_featured=True,
        )

        self.second_product = Product.objects.create(
            name="LED Desk Lamp",
            sku="TEST-GAD-002",
            category=self.category,
            description="A modern desk lamp.",
            price=Decimal("899.00"),
            stock=5,
            is_active=True,
        )


class ProductModelTests(StoreTestDataMixin, TestCase):

    def test_product_slug_is_generated(self):
        self.assertTrue(self.product.slug)
        self.assertEqual(
            self.product.slug,
            "mini-desk-vacuum",
        )

    def test_discount_percentage(self):
        self.assertEqual(self.product.discount_percentage, 17)

    def test_product_stock_property(self):
        self.assertTrue(self.product.is_in_stock)

        self.product.stock = 0

        self.assertFalse(self.product.is_in_stock)

    def test_category_slug_is_generated(self):
        self.assertTrue(self.category.slug)
        self.assertEqual(self.category.slug, "desk-gadgets")


class StoreViewTests(StoreTestDataMixin, TestCase):

    def test_home_page_loads(self):
        response = self.client.get(reverse("store:home"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "store/home.html")

    def test_home_page_displays_active_products(self):
        inactive_product = Product.objects.create(
            name="Hidden Product",
            sku="TEST-HIDDEN-001",
            category=self.category,
            description="This product should not appear.",
            price=Decimal("100.00"),
            stock=2,
            is_active=False,
        )

        response = self.client.get(reverse("store:home"))
        products = list(response.context["products"])

        self.assertIn(self.product, products)
        self.assertNotIn(inactive_product, products)

    def test_product_search(self):
        response = self.client.get(
            reverse("store:home"),
            {"q": "Mini Desk Vacuum"},
        )

        products = list(response.context["products"])

        self.assertIn(self.product, products)
        self.assertNotIn(self.second_product, products)

    def test_category_filter(self):
        response = self.client.get(
            reverse("store:home"),
            {"category": self.category.slug},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["selected_category"],
            self.category,
        )

    def test_price_low_sorting(self):
        response = self.client.get(
            reverse("store:home"),
            {"sort": "price_low"},
        )

        products = list(response.context["products"])

        self.assertEqual(products[0], self.product)
        self.assertEqual(products[1], self.second_product)

    def test_product_detail_loads(self):
        response = self.client.get(
            reverse(
                "store:product_detail",
                kwargs={"slug": self.product.slug},
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["product"], self.product)

    def test_inactive_product_detail_returns_404(self):
        self.product.is_active = False
        self.product.save()

        response = self.client.get(
            reverse(
                "store:product_detail",
                kwargs={"slug": self.product.slug},
            )
        )

        self.assertEqual(response.status_code, 404)