"""Authentication views for clients (public users)."""

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from .forms import ClientLoginForm, SignupForm


@require_http_methods(["GET", "POST"])
def signup(request):
    """Register a client, create their Lead, and log them in."""
    if request.user.is_authenticated:
        return redirect("dashboard:home" if request.user.is_staff else "core:landing")

    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Welcome to BuildCorp! Your project request has been logged.")
            return redirect(reverse("core:thank_you") + "?source=signup")
    else:
        form = SignupForm()

    return render(request, "accounts/signup.html", {
        "form": form,
        "meta_title": "Get a Free Quote — BuildCorp",
        "meta_description": "Tell us about your project and get a free, no-obligation cost consultation.",
    })


class ClientLoginView(LoginView):
    """Public login. Staff are forwarded to the hidden dashboard."""

    template_name = "accounts/login.html"
    authentication_form = ClientLoginForm
    redirect_authenticated_user = True

    def get_success_url(self):
        if self.request.user.is_staff:
            return reverse("dashboard:home")
        return self.get_redirect_url() or reverse("core:landing")

    def form_valid(self, form):
        messages.success(self.request, "Signed in successfully.")
        return super().form_valid(form)


class ClientLogoutView(LogoutView):
    """POST-only logout (CSRF protected)."""

    next_page = "core:landing"