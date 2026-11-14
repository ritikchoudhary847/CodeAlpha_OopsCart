
from django import forms


class CheckoutForm(forms.Form):
    full_name = forms.CharField(
        max_length=150,
        label="Full name",
        widget=forms.TextInput(attrs={
            "class": "checkout-input",
            "placeholder": "Your full name",
        }),
    )

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            "class": "checkout-input",
            "placeholder": "you@example.com",
        }),
    )

    phone = forms.CharField(
        max_length=15,
        label="Phone number",
        widget=forms.TextInput(attrs={
            "class": "checkout-input",
            "placeholder": "10-digit mobile number",
        }),
    )

    address_line_1 = forms.CharField(
        max_length=255,
        label="Address",
        widget=forms.TextInput(attrs={
            "class": "checkout-input",
            "placeholder": "House no., street, area",
        }),
    )

    address_line_2 = forms.CharField(
        max_length=255,
        required=False,
        label="Apartment / Landmark",
        widget=forms.TextInput(attrs={
            "class": "checkout-input",
            "placeholder": "Apartment, landmark (optional)",
        }),
    )

    city = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            "class": "checkout-input",
            "placeholder": "City",
        }),
    )

    state = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            "class": "checkout-input",
            "placeholder": "State",
        }),
    )

    postal_code = forms.CharField(
        max_length=10,
        label="PIN code",
        widget=forms.TextInput(attrs={
            "class": "checkout-input",
            "placeholder": "6-digit PIN code",
        }),
    )

    country = forms.ChoiceField(
        choices=[("India", "India")],
        initial="India",
        widget=forms.Select(attrs={
            "class": "checkout-input",
        }),
    )

    customer_note = forms.CharField(
        required=False,
        label="Order note",
        widget=forms.Textarea(attrs={
            "class": "checkout-input",
            "rows": 3,
            "placeholder": "Any delivery instructions? (optional)",
        }),
    )

    def clean_phone(self):
        phone = self.cleaned_data["phone"].strip()

        allowed_characters = set("0123456789+()- ")

        if any(char not in allowed_characters for char in phone):
            raise forms.ValidationError(
                "Enter a valid phone number."
            )

        if phone.count("+") > 1 or (
            "+" in phone and not phone.startswith("+")
        ):
            raise forms.ValidationError(
                "Enter a valid phone number."
            )

        digits = "".join(
            char for char in phone if char.isdigit()
        )

        if not 10 <= len(digits) <= 15:
            raise forms.ValidationError(
                "Enter a valid phone number."
            )

        return phone

    def clean_postal_code(self):
        postal_code = self.cleaned_data["postal_code"].strip()

        if not postal_code.isdigit() or len(postal_code) != 6:
            raise forms.ValidationError(
                "Enter a valid 6-digit Indian PIN code."
            )

        return postal_code
