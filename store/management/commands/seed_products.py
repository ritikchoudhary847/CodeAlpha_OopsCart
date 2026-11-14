
from io import BytesIO
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction

from PIL import Image, UnidentifiedImageError

from store.models import Category, Product


IMAGE_BASE = "https://images.unsplash.com/"

IMAGE_PARAMS = "?fit=crop&w=1000&q=85&fm=jpg"


CATALOGUE = [
    {
        "category": "Tech & Gadgets",
        "description": "Smart technology and everyday electronic essentials.",
        "products": [
            {
                "name": "Studio Wireless Headphones",
                "sku": "OOPS-TECH-001",
                "price": "2499.00",
                "compare_at_price": "3299.00",
                "stock": 24,
                "featured": True,
                "image": "photo-1505740420928-5e560c06d30e",
                "description": "Enjoy immersive sound, comfortable ear cushions and a clean wireless listening experience. Designed for work, travel and everyday entertainment.",
            },
            {
                "name": "Minimal Smart Watch",
                "sku": "OOPS-TECH-002",
                "price": "3299.00",
                "compare_at_price": "4299.00",
                "stock": 18,
                "featured": True,
                "image": "photo-1523275335684-37898b6baf30",
                "description": "A contemporary smartwatch-inspired design for everyday style. A versatile accessory for casual and professional outfits.",
            },
            {
                "name": "Portable Bluetooth Speaker",
                "sku": "OOPS-TECH-003",
                "price": "1799.00",
                "compare_at_price": "2299.00",
                "stock": 30,
                "featured": True,
                "image": "photo-1608043152269-423dbba4e7e1",
                "description": "A compact speaker concept with a modern design. An ideal companion for desks, bedrooms and relaxed weekends.",
            },
            {
                "name": "Digital Creator Camera",
                "sku": "OOPS-TECH-004",
                "price": "8999.00",
                "compare_at_price": "10999.00",
                "stock": 8,
                "featured": False,
                "image": "photo-1516035069371-29a1b244cc32",
                "description": "A camera for photography enthusiasts and content creators who love capturing everyday moments.",
            },
            {
                "name": "Aluminium Laptop Stand",
                "sku": "OOPS-TECH-005",
                "price": "1299.00",
                "compare_at_price": "1699.00",
                "stock": 35,
                "featured": False,
                "image": "photo-1525547719571-a2d4ac8945e2",
                "description": "Give your workspace a cleaner look with a minimalist laptop setup accessory designed for a more organized desk.",
            },
        ],
    },
    {
        "category": "Desk Essentials",
        "description": "Thoughtfully selected accessories for productive workspaces.",
        "products": [
            {
                "name": "Mechanical Keyboard",
                "sku": "OOPS-DESK-001",
                "price": "2199.00",
                "compare_at_price": "2799.00",
                "stock": 20,
                "featured": True,
                "image": "photo-1587829741301-dc798b83add3",
                "description": "A clean mechanical keyboard aesthetic for people who appreciate a comfortable and organized desk setup.",
            },
            {
                "name": "Precision Wireless Mouse",
                "sku": "OOPS-DESK-002",
                "price": "899.00",
                "compare_at_price": "1199.00",
                "stock": 40,
                "featured": False,
                "image": "photo-1527814050087-3793815479db",
                "description": "A minimal wireless mouse designed to complement modern workstations and everyday productivity.",
            },
            {
                "name": "Ambient LED Desk Lamp",
                "sku": "OOPS-DESK-003",
                "price": "1499.00",
                "compare_at_price": "1999.00",
                "stock": 22,
                "featured": True,
                "image": "photo-1507473885765-e6ed057f782c",
                "description": "Bring a warm, focused atmosphere to your workspace with a contemporary desk lighting design.",
            },
            {
                "name": "Urban Laptop Backpack",
                "sku": "OOPS-DESK-004",
                "price": "1899.00",
                "compare_at_price": "2499.00",
                "stock": 16,
                "featured": False,
                "image": "photo-1553062407-98eeb64c6a62",
                "description": "A versatile everyday backpack concept for carrying work essentials, accessories and personal belongings.",
            },
            {
                "name": "Insulated Steel Bottle",
                "sku": "OOPS-DESK-005",
                "price": "699.00",
                "compare_at_price": "999.00",
                "stock": 45,
                "featured": False,
                "image": "photo-1602143407151-7111542de6e8",
                "description": "A reusable bottle with a simple, timeless design for your desk, commute and everyday routine.",
            },
        ],
    },
    {
        "category": "Home & Living",
        "description": "Modern lifestyle pieces for comfortable, beautiful spaces.",
        "products": [
            {
                "name": "Artisan Ceramic Mug",
                "sku": "OOPS-HOME-001",
                "price": "499.00",
                "compare_at_price": "699.00",
                "stock": 50,
                "featured": True,
                "image": "photo-1514228742587-6b1558fcca3d",
                "description": "A timeless ceramic mug for your morning coffee, evening tea and slow weekend moments.",
            },
            {
                "name": "Indoor Table Planter",
                "sku": "OOPS-HOME-002",
                "price": "599.00",
                "compare_at_price": "799.00",
                "stock": 28,
                "featured": False,
                "image": "photo-1485955900006-10f4d324d411",
                "description": "Add a refreshing natural touch to your desk, shelf or living space with a minimal plant-inspired accent.",
            },
            {
                "name": "Soft Neutral Cushion Cover",
                "sku": "OOPS-HOME-003",
                "price": "449.00",
                "compare_at_price": "649.00",
                "stock": 32,
                "featured": False,
                "image": "photo-1584100936595-c0654b55a2e2",
                "description": "A subtle home accent designed to bring texture and warmth to your favourite corner.",
            },
            {
                "name": "Minimal Table Clock",
                "sku": "OOPS-HOME-004",
                "price": "799.00",
                "compare_at_price": "1099.00",
                "stock": 19,
                "featured": False,
                "image": "photo-1501139083538-0139583c060f",
                "description": "A decorative timepiece concept that adds a clean, understated detail to your room or workspace.",
            },
            {
                "name": "Aroma Diffuser",
                "sku": "OOPS-HOME-005",
                "price": "1199.00",
                "compare_at_price": "1599.00",
                "stock": 15,
                "featured": True,
                "image": "photo-1608571423902-eed4a5ad8108",
                "description": "Create a relaxing atmosphere with a contemporary diffuser-inspired addition to your home.",
            },
        ],
    },
    {
        "category": "Fashion Accessories",
        "description": "Everyday fashion essentials with a modern, understated look.",
        "products": [
            {
                "name": "Classic Aviator Sunglasses",
                "sku": "OOPS-FASH-001",
                "price": "999.00",
                "compare_at_price": "1399.00",
                "stock": 26,
                "featured": True,
                "image": "photo-1511499767150-a48a237f0083",
                "description": "A classic eyewear silhouette that pairs effortlessly with casual and smart-casual outfits.",
            },
            {
                "name": "Urban Street Sneakers",
                "sku": "OOPS-FASH-002",
                "price": "2799.00",
                "compare_at_price": "3499.00",
                "stock": 14,
                "featured": True,
                "image": "photo-1542291026-7eec264c27ff",
                "description": "A bold everyday sneaker look designed to add a sporty edge to your casual wardrobe.",
            },
            {
                "name": "Classic Leather Wallet",
                "sku": "OOPS-FASH-003",
                "price": "899.00",
                "compare_at_price": "1199.00",
                "stock": 30,
                "featured": False,
                "image": "photo-1627123424574-724758594e93",
                "description": "A compact wallet concept with a timeless appearance for carrying your everyday essentials.",
            },
            {
                "name": "Everyday Crossbody Bag",
                "sku": "OOPS-FASH-004",
                "price": "1599.00",
                "compare_at_price": "2199.00",
                "stock": 17,
                "featured": False,
                "image": "photo-1548036328-c9fa89d128fa",
                "description": "A versatile bag silhouette that balances everyday practicality with a polished look.",
            },
            {
                "name": "Timeless Analog Watch",
                "sku": "OOPS-FASH-005",
                "price": "1999.00",
                "compare_at_price": "2699.00",
                "stock": 12,
                "featured": True,
                "image": "photo-1524592094714-0f0654e20314",
                "description": "A refined analog watch aesthetic for people who prefer classic accessories and simple styling.",
            },
        ],
    },
    {
        "category": "Lifestyle",
        "description": "Useful everyday companions for travel, fitness and beyond.",
        "products": [
            {
                "name": "Travel Essentials Organizer",
                "sku": "OOPS-LIFE-001",
                "price": "749.00",
                "compare_at_price": "999.00",
                "stock": 25,
                "featured": False,
                "image": "photo-1553062407-98eeb64c6a62",
                "description": "Keep everyday travel essentials organized with a practical accessory for short trips and daily commutes.",
            },
            {
                "name": "Premium Tumbler",
                "sku": "OOPS-LIFE-002",
                "price": "899.00",
                "compare_at_price": "1199.00",
                "stock": 30,
                "featured": True,
                "image": "photo-1577937927133-66ef06acdf18",
                "description": "A reusable tumbler concept for coffee, cold drinks and busy days on the move.",
            },
            {
                "name": "Everyday Fitness Yoga Mat",
                "sku": "OOPS-LIFE-003",
                "price": "1199.00",
                "compare_at_price": "1599.00",
                "stock": 18,
                "featured": False,
                "image": "photo-1544367567-0f2fcb009e0b",
                "description": "A fitness essential for stretching, yoga and building a consistent home workout routine.",
            },
            {
                "name": "Compact Power Bank",
                "sku": "OOPS-LIFE-004",
                "price": "1399.00",
                "compare_at_price": "1799.00",
                "stock": 21,
                "featured": True,
                "image": "photo-1609592806596-b43bada2f8a9",
                "description": "A portable charging accessory concept for keeping your devices ready throughout the day.",
            },
            {
                "name": "Compact Everyday Umbrella",
                "sku": "OOPS-LIFE-005",
                "price": "599.00",
                "compare_at_price": "799.00",
                "stock": 35,
                "featured": False,
                "image": "photo-1534274988757-a28bf1a57c17",
                "description": "A practical everyday accessory for unpredictable weather and convenient travel.",
            },
        ],
    },
]


def download_image(photo_id):
    url = f"{IMAGE_BASE}{photo_id}{IMAGE_PARAMS}"

    request = Request(
        url,
        headers={
            "User-Agent": "OopsCart-Django-ProductSeeder/1.0",
        },
    )

    with urlopen(request, timeout=30) as response:
        image_data = response.read(8 * 1024 * 1024 + 1)

    if len(image_data) > 8 * 1024 * 1024:
        raise ValueError("Image exceeds the 8 MB limit.")

    if not image_data:
        raise ValueError("Downloaded image is empty.")

    try:
        with Image.open(BytesIO(image_data)) as image:
            image.verify()
    except (UnidentifiedImageError, OSError) as exc:
        raise ValueError("Downloaded file is not a valid image.") from exc

    return image_data


class Command(BaseCommand):
    help = "Create the OopsCart demo catalogue with product images."

    def add_arguments(self, parser):
        parser.add_argument(
            "--skip-images",
            action="store_true",
            help="Create products without downloading images.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        skip_images = options["skip_images"]

        created_categories = 0
        created_products = 0
        added_images = 0
        image_failures = []

        for category_data in CATALOGUE:
            category, category_created = Category.objects.get_or_create(
                name=category_data["category"],
                defaults={
                    "description": category_data["description"],
                    "is_active": True,
                },
            )

            if category_created:
                created_categories += 1
            elif not category.is_active:
                category.is_active = True
                category.save(update_fields=["is_active"])

            for item in category_data["products"]:
                product, product_created = Product.objects.get_or_create(
                    sku=item["sku"],
                    defaults={
                        "name": item["name"],
                        "category": category,
                        "description": item["description"],
                        "price": item["price"],
                        "compare_at_price": item["compare_at_price"],
                        "stock": item["stock"],
                        "is_active": True,
                        "is_featured": item["featured"],
                    },
                )

                if product_created:
                    created_products += 1
                    self.stdout.write(
                        self.style.SUCCESS(f"Created: {product.name}")
                    )

                if skip_images or product.image:
                    continue

                try:
                    image_data = download_image(item["image"])

                    product.image.save(
                        f"{item['sku'].lower()}.jpg",
                        ContentFile(image_data),
                        save=True,
                    )

                    added_images += 1
                    self.stdout.write(
                        self.style.SUCCESS(f"Image saved: {product.name}")
                    )

                except (HTTPError, URLError, TimeoutError, ValueError, OSError) as exc:
                    image_failures.append((product.name, str(exc)))
                    self.stderr.write(
                        self.style.WARNING(
                            f"Image skipped for {product.name}: {exc}"
                        )
                    )

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("OopsCart catalogue seeding finished."))
        self.stdout.write(f"New categories: {created_categories}")
        self.stdout.write(f"New products: {created_products}")
        self.stdout.write(f"New images: {added_images}")
        self.stdout.write(f"Image failures: {len(image_failures)}")

        if image_failures:
            self.stdout.write(
                self.style.WARNING(
                    "Run the same command again to retry missing images."
                )
            )
            for name, error in image_failures:
                self.stdout.write(f"- {name}: {error}")
