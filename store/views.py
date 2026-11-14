from django.shortcuts import render, get_object_or_404
from django.db.models import Q

from .models import Product, Category


def home(request):
    products = Product.objects.filter(
        is_active=True,
        category__is_active=True
    ).select_related("category")

    categories = Category.objects.filter(is_active=True)

    search_query = request.GET.get("q", "").strip()
    category_slug = request.GET.get("category", "").strip()
    sort_by = request.GET.get("sort", "newest")

    selected_category = None

    if search_query:
        products = products.filter(
            Q(name__icontains=search_query)
            | Q(description__icontains=search_query)
            | Q(sku__icontains=search_query)
            | Q(category__name__icontains=search_query)
        )

    if category_slug:
        selected_category = get_object_or_404(
            Category,
            slug=category_slug,
            is_active=True
        )
        products = products.filter(category=selected_category)

    if sort_by == "price_low":
        products = products.order_by("price")
    elif sort_by == "price_high":
        products = products.order_by("-price")
    elif sort_by == "name":
        products = products.order_by("name")
    else:
        products = products.order_by("-created_at")

    featured_products = Product.objects.filter(
        is_active=True,
        is_featured=True,
        category__is_active=True
    ).select_related("category")[:4]

    context = {
        "products": products,
        "categories": categories,
        "featured_products": featured_products,
        "search_query": search_query,
        "selected_category": selected_category,
        "sort_by": sort_by,
        "product_count": products.count(),
    }

    return render(request, "store/home.html", context)


def product_detail(request, slug):
    product = get_object_or_404(
        Product.objects.select_related("category"),
        slug=slug,
        is_active=True,
        category__is_active=True
    )

    related_products = Product.objects.filter(
        category=product.category,
        is_active=True,
        category__is_active=True
    ).exclude(pk=product.pk).select_related("category")[:4]

    context = {
        "product": product,
        "related_products": related_products,
    }

    return render(request, "store/product_detail.html", context)