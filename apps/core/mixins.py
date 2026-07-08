from django.contrib.auth.mixins import UserPassesTestMixin


class StaffRequiredMixin(UserPassesTestMixin):
    """Restrict a class-based view to staff/admin accounts.

    Used across announcements, events, and resources — any app where
    content is authored by admins but read by all students.
    """

    raise_exception = False

    def test_func(self):
        return self.request.user.is_authenticated and self.request.user.is_staff

    def handle_no_permission(self):
        from django.contrib import messages

        messages.error(self.request, "You need administrator access to do that.")
        from django.shortcuts import redirect

        return redirect("dashboard:home")


class OwnerRequiredMixin(UserPassesTestMixin):
    """Restrict object access to its owner (or staff)."""

    owner_field = "owner"

    def test_func(self):
        obj = self.get_object()
        user = self.request.user
        return user.is_staff or getattr(obj, self.owner_field, None) == user

    def handle_no_permission(self):
        from django.contrib import messages

        messages.error(self.request, "You don't have permission to do that.")
        from django.shortcuts import redirect

        return redirect("dashboard:home")
