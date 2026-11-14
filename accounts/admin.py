from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        "username", "email", "first_name",
        "last_name", "is_staff", "is_active"
    )

    search_fields = ("username", "email", "phone_number")

    fieldsets = UserAdmin.fieldsets + (
        ("Customer Information", {
            "fields": ("phone_number", "avatar", "created_at")
        }),
    )

    readonly_fields = ("created_at",)