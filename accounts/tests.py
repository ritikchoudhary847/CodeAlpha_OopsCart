from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .forms import RegisterForm, ProfileForm

User = get_user_model()


class RegistrationTests(TestCase):

    def test_registration_form_accepts_valid_data(self):
        form = RegisterForm(data={
            "username": "ritik_test",
            "first_name": "Ritik",
            "last_name": "Test",
            "email": "Ritik@example.com",
            "phone_number": "9876543210",
            "password1": "StrongPass!234",
            "password2": "StrongPass!234",
        })

        self.assertTrue(form.is_valid(), form.errors)

        user = form.save()

        self.assertEqual(user.email, "ritik@example.com")
        self.assertEqual(user.phone_number, "9876543210")
        self.assertTrue(user.check_password("StrongPass!234"))

    def test_registration_rejects_duplicate_email_case_insensitively(self):
        User.objects.create_user(
            username="existing",
            email="user@example.com",
            password="StrongPass!234",
        )

        form = RegisterForm(data={
            "username": "new_user",
            "email": "USER@example.com",
            "phone_number": "9876543210",
            "password1": "StrongPass!234",
            "password2": "StrongPass!234",
        })

        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_registration_rejects_invalid_phone(self):
        form = RegisterForm(data={
            "username": "invalid_phone",
            "email": "phone@example.com",
            "phone_number": "12345",
            "password1": "StrongPass!234",
            "password2": "StrongPass!234",
        })

        self.assertFalse(form.is_valid())
        self.assertIn("phone_number", form.errors)

    def test_registration_view_creates_account_and_logs_user_in(self):
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "new_customer",
                "first_name": "New",
                "last_name": "Customer",
                "email": "new@example.com",
                "phone_number": "9876543210",
                "password1": "StrongPass!234",
                "password2": "StrongPass!234",
            },
        )

        self.assertRedirects(response, reverse("store:home"))
        self.assertTrue(
            User.objects.filter(username="new_customer").exists()
        )
        self.assertTrue(response.wsgi_request.user.is_authenticated)


class ProfileTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="profile_user",
            email="profile@example.com",
            password="StrongPass!234",
        )
        self.client.force_login(self.user)

    def test_profile_form_normalizes_email(self):
        form = ProfileForm(
            data={
                "first_name": "Ritik",
                "last_name": "Choudhary",
                "email": "PROFILE@EXAMPLE.COM",
                "phone_number": "9876543210",
            },
            instance=self.user,
        )

        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(
            form.cleaned_data["email"],
            "profile@example.com",
        )

    def test_profile_rejects_another_users_email(self):
        User.objects.create_user(
            username="another_user",
            email="another@example.com",
            password="StrongPass!234",
        )

        form = ProfileForm(
            data={
                "first_name": "Ritik",
                "last_name": "Test",
                "email": "ANOTHER@example.com",
                "phone_number": "",
            },
            instance=self.user,
        )

        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_profile_view_requires_authentication(self):
        self.client.logout()

        response = self.client.get(reverse("accounts:profile"))

        self.assertEqual(response.status_code, 302)
        self.assertIn(
            reverse("accounts:login"),
            response.url,
        )