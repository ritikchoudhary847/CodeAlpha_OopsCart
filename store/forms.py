
import warnings

from django import forms
from django.core.files.uploadedfile import UploadedFile
from PIL import Image, UnidentifiedImageError

from .models import Product


MAX_PRODUCT_IMAGE_SIZE = 5 * 1024 * 1024  # 5 MB
MAX_IMAGE_DIMENSION = 6000
MAX_IMAGE_PIXELS = 25_000_000

ALLOWED_IMAGE_FORMATS = {"JPEG", "PNG", "WEBP"}


class ProductAdminForm(forms.ModelForm):

    class Meta:
        model = Product
        fields = "__all__"

    def clean_image(self):
        image_file = self.cleaned_data.get("image")

        # Validate only newly uploaded files.
        # Existing stored product images remain untouched.
        if not isinstance(image_file, UploadedFile):
            return image_file

        if image_file.size > MAX_PRODUCT_IMAGE_SIZE:
            raise forms.ValidationError(
                "Product image must not exceed 5 MB."
            )

        if image_file.size == 0:
            raise forms.ValidationError(
                "Uploaded image cannot be empty."
            )

        try:
            image_file.seek(0)

            with warnings.catch_warnings():
                warnings.simplefilter(
                    "error",
                    Image.DecompressionBombWarning
                )

                with Image.open(image_file) as img:

                    if img.format not in ALLOWED_IMAGE_FORMATS:
                        raise forms.ValidationError(
                            "Only JPG, PNG and WEBP images are allowed."
                        )

                    if (
                        img.width > MAX_IMAGE_DIMENSION
                        or img.height > MAX_IMAGE_DIMENSION
                        or img.width * img.height > MAX_IMAGE_PIXELS
                    ):
                        raise forms.ValidationError(
                            "Image dimensions or resolution are too large."
                        )

                    img.verify()

            image_file.seek(0)

        except forms.ValidationError:
            raise

        except (
            UnidentifiedImageError,
            OSError,
            ValueError,
            Image.DecompressionBombError,
            Image.DecompressionBombWarning,
        ):
            raise forms.ValidationError(
                "Please upload a valid, non-corrupted image."
            )

        return image_file
