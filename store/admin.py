from django.contrib import admin
from .models import Category, Product
from .forms import ProductAdminForm

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    form = ProductAdminForm
    list_display = (
        "name", "sku", "category", "price",
        "stock", "is_active", "is_featured"
    )
    list_filter = ("category", "is_active", "is_featured")
    search_fields = ("name", "sku")
    list_editable = ("price", "stock", "is_active", "is_featured")
    prepopulated_fields = {"slug": ("name",)}
   