
from io import BytesIO
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from PIL import Image, UnidentifiedImageError

from store.models import Product


IMAGE_BASE = "https://images.unsplash.com/"

IMAGE_MAP = {
    "Compact Power Bank": "photo-1601898532138-9f145a2ad69e",
    "Portable Mini Fan": "photo-1564510182791-29645da7fac4",
    "Led desk lamp": "photo-1507473885765-e6ed057f782c",
    "Mini Desk Vacuum": "photo-1669255344189-fc6a34d42f3a",
}


def download_and_validate(photo_id):
    url = (
        f"{IMAGE_BASE}{photo_id}"
        "?fit=crop&w=1000&q=85&fm=jpg"
    )

    request = Request(
        url,
        headers={"User-Agent": "OopsCart-ImageRepair/1.0"},
    )

    with urlopen(request, timeout=30) as response:
        image_data = response.read(8 * 1024 * 1024 + 1)

    if not image_data or len(image_data) > 8 * 1024 * 1024:
        raise ValueError("Image is empty or exceeds 8 MB.")

    try:
        with Image.open(BytesIO(image_data)) as image:
            image.verify()
    except (UnidentifiedImageError, OSError) as exc:
        raise ValueError("Downloaded file is not a valid image.") from exc

    return image_data


class Command(BaseCommand):
    help = "Repair missing OopsCart product images."

    def handle(self, *args, **options):
        repaired = 0
        skipped = 0
        failures = []

        for product_name, photo_id in IMAGE_MAP.items():
            product = Product.objects.filter(
                name__iexact=product_name
            ).first()

            if not product:
                self.stderr.write(
                    self.style.WARNING(
                        f"Product not found: {product_name}"
                    )
                )
                failures.append(product_name)
                continue

            if product.image:
                try:
                    if Path(product.image.path).is_file():
                        self.stdout.write(
                            f"Already has image: {product.name}"
                        )
                        skipped += 1
                        continue
                except (ValueError, OSError):
                    pass

            try:
                image_data = download_and_validate(photo_id)

                filename = f"{product.sku.lower()}-image.jpg"

                product.image.save(
                    filename,
                    ContentFile(image_data),
                    save=True,
                )

                repaired += 1

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Image repaired: {product.name}"
                    )
                )

            except (
                HTTPError,
                URLError,
                TimeoutError,
                ValueError,
                OSError,
            ) as exc:
                failures.append(product.name)

                self.stderr.write(
                    self.style.ERROR(
                        f"Failed: {product.name} - {exc}"
                    )
                )

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("IMAGE REPAIR REPORT"))
        self.stdout.write(f"Repaired: {repaired}")
        self.stdout.write(f"Already available: {skipped}")
        self.stdout.write(f"Failures: {len(failures)}")

        if failures:
            self.stdout.write(
                self.style.WARNING(
                    "Failed products: " + ", ".join(failures)
                )
            )
