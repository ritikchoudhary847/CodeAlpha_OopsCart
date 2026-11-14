from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.views.decorators.http import require_POST

from .forms import RegisterForm, LoginForm, ProfileForm
from cart.services import merge_guest_cart


def register_view(request):
    if request.user.is_authenticated:
        return redirect("store:home")

    guest_session_key = request.session.session_key

    if request.method == "POST":
        form = RegisterForm(request.POST)

        if form.is_valid():
            user = form.save()

            login(
                request,
                user,
                backend="django.contrib.auth.backends.ModelBackend",
            )

            merge_guest_cart(user, guest_session_key)

            messages.success(
                request,
                "Welcome to OopsCart! Your account is ready."
            )

            return redirect("store:home")

    else:
        form = RegisterForm()

    return render(request, "accounts/register.html", {"form": form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("store:home")

    guest_session_key = request.session.session_key

    if request.method == "POST":
        form = LoginForm(request, data=request.POST)

        if form.is_valid():
            user = form.get_user()

            login(request, user)
            merge_guest_cart(user, guest_session_key)

            messages.success(request, "Welcome back!")

            return redirect("store:home")

    else:
        form = LoginForm(request)

    return render(request, "accounts/login.html", {"form": form})


@require_POST
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("store:home")


@login_required
def profile_view(request):
    if request.method == "POST":
        form = ProfileForm(
            request.POST,
            request.FILES,
            instance=request.user,
        )

        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated.")
            return redirect("accounts:profile")

    else:
        form = ProfileForm(instance=request.user)

    return render(request, "accounts/profile.html", {"form": form})