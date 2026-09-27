"""Access control for every dashboard view.

Two independent gates are enforced:
  1. login_required                          → anonymous users hit the dashboard login page.
  2. user_passes_test(lambda u: u.is_staff)  → logged-in non-staff users get a 403.
"""

from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect


def is_staff_user(user):
    return bool(user.is_authenticated and user.is_active and user.is_staff)


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Class-based view mixin enforcing staff access."""

    login_url = "dashboard:login"
    raise_exception = False

    def test_func(self):
        return is_staff_user(self.request.user)

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            # Logged in but not staff → hard 403 (renders templates/403.html).
            raise PermissionDenied("You do not have access to the staff dashboard.")
        return redirect(self.login_url)


def staff_required(view_func):
    """Function-based view decorator combining login + staff checks."""

    @login_required(login_url="dashboard:login")
    @user_passes_test(is_staff_user, login_url="dashboard:login")
    def wrapper(request, *args, **kwargs):
        return view_func(request, *args, **kwargs)

    return wrapper