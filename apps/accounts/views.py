from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (
    LoginView,
    LogoutView,
    PasswordChangeView as BasePasswordChangeView,
)
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, TemplateView, View
from django.shortcuts import redirect, render

from core.models import ActivityLog, ActivityVerb

from .forms import LoginForm, PasswordChangeForm, ProfileUpdateForm, RegisterForm, UserUpdateForm


class RegisterView(CreateView):
    form_class = RegisterForm
    template_name = "accounts/register.html"
    success_url = reverse_lazy("dashboard:home")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("dashboard:home")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        messages.success(
            self.request,
            f"Welcome to NUM Connect, {self.object.first_name}! Your account is ready.",
        )
        return response


class UserLoginView(LoginView):
    form_class = LoginForm
    template_name = "accounts/login.html"
    redirect_authenticated_user = True

    def form_valid(self, form):
        messages.success(self.request, f"Welcome back, {form.get_user().first_name or form.get_user().username}!")
        return super().form_valid(form)


class UserLogoutView(LogoutView):
    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        messages.info(request, "You've been logged out. See you soon!")
        return response


class ProfileDetailView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/profile.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["profile"] = self.request.user.profile
        return context


class ProfileEditView(LoginRequiredMixin, View):
    template_name = "accounts/profile_edit.html"

    def get(self, request):
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)
        return render(request, self.template_name, {"user_form": user_form, "profile_form": profile_form})

    def post(self, request):
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, "Your profile has been updated.")
            ActivityLog.log(
                request.user,
                ActivityVerb.PROFILE_UPDATED,
                "Updated their profile",
                icon="bi-person-gear",
                url=reverse("accounts:profile"),
            )
            return redirect("accounts:profile")

        messages.error(request, "Please correct the errors below.")
        return render(request, self.template_name, {"user_form": user_form, "profile_form": profile_form})


class PasswordChangeView(LoginRequiredMixin, BasePasswordChangeView):
    form_class = PasswordChangeForm
    template_name = "accounts/password_change.html"
    success_url = reverse_lazy("accounts:profile")

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Your password has been changed successfully.")
        return response
