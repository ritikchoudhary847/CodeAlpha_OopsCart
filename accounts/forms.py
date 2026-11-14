import re

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from .models import User
from PIL import Image, UnidentifiedImageError

PHONE_PATTERN = re.compile(r"^(?:\+91[\s-]?)?[6-9]\d{9}$")
MAX_AVATAR_SIZE = 3 * 1024 * 1024


class RegisterForm(UserCreationForm):
    email = forms.EmailField()
    phone_number = forms.CharField(max_length=15, required=False)

    class Meta:
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "phone_number",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control"})

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()

        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(
                "An account with this email already exists."
            )

        return email

    def clean_phone_number(self):
        phone = self.cleaned_data.get("phone_number", "").strip()

        if phone and not PHONE_PATTERN.fullmatch(phone):
            raise forms.ValidationError(
                "Enter a valid Indian mobile number."
            )

        return phone


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Your username",
            "autocomplete": "username",
        })
    )

    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Your password",
            "autocomplete": "current-password",
        })
    )


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "avatar",
        )

        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "phone_number": forms.TextInput(attrs={"class": "form-control"}),
        }

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()

        if User.objects.filter(email__iexact=email).exclude(
            pk=self.instance.pk
        ).exists():
            raise forms.ValidationError(
                "This email is already being used."
            )

        return email

    def clean_phone_number(self):
        phone = self.cleaned_data.get("phone_number", "").strip()

        if phone and not PHONE_PATTERN.fullmatch(phone):
            raise forms.ValidationError(
                "Enter a valid Indian mobile number."
            )

        return phone

        def clean_avatar(self):
          avatar = self.cleaned_data.get("avatar")

        if not avatar or not hasattr(avatar, "read"):
            return avatar

        if avatar.size > MAX_AVATAR_SIZE:
            raise forms.ValidationError(
                "Avatar image must not exceed 3 MB."
            )

        try:
            avatar.seek(0)

            with Image.open(avatar) as image:
                if image.format not in ("JPEG", "PNG", "WEBP"):
                    raise forms.ValidationError(
                        "Only JPG, PNG and WEBP images are allowed."
                    )

                if image.width > 6000 or image.height > 6000:
                    raise forms.ValidationError(
                        "Image dimensions must not exceed 6000 × 6000 pixels."
                    )

                image.verify()

            avatar.seek(0)

        except forms.ValidationError:
            raise
        except (
            UnidentifiedImageError,
            OSError,
            ValueError,
            Image.DecompressionBombError,
        ):
            raise forms.ValidationError(
                "Please upload a valid, non-corrupted image."
            )

        return avatar