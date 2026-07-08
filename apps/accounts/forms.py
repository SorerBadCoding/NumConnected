from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm as BasePasswordChangeForm, UserCreationForm

from core.forms import BootstrapFormMixin

from .models import AcademicYear, Profile, User


class LoginForm(BootstrapFormMixin, AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={"autofocus": True, "placeholder": "Username"})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"placeholder": "Password"})
    )


class RegisterForm(BootstrapFormMixin, UserCreationForm):
    """Creates the User and, in the same submission, fills in the required
    Profile fields (student ID, major, academic year). A Profile row already
    exists by this point thanks to accounts.signals.ensure_profile_exists —
    this form just populates it with real data instead of the placeholder."""

    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={"placeholder": "you@university.edu"}))
    first_name = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={"placeholder": "First name"}))
    last_name = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={"placeholder": "Last name"}))
    student_id = forms.CharField(max_length=20, required=True, widget=forms.TextInput(attrs={"placeholder": "e.g. 2024-00123"}))
    major = forms.CharField(max_length=120, required=True, widget=forms.TextInput(attrs={"placeholder": "e.g. Computer Science"}))
    academic_year = forms.ChoiceField(choices=AcademicYear.choices)

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "password1", "password2")
        widgets = {
            "username": forms.TextInput(attrs={"placeholder": "Choose a username"}),
        }

    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def clean_student_id(self):
        student_id = self.cleaned_data["student_id"].strip()
        if Profile.objects.filter(student_id__iexact=student_id).exists():
            raise forms.ValidationError("This student ID is already registered.")
        return student_id

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            profile = user.profile
            profile.student_id = self.cleaned_data["student_id"]
            profile.major = self.cleaned_data["major"]
            profile.academic_year = self.cleaned_data["academic_year"]
            profile.save()
        return user


class UserUpdateForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = ("first_name", "last_name", "email")

    def clean_email(self):
        email = self.cleaned_data["email"]
        if User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email


class ProfileUpdateForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Profile
        fields = ("profile_picture", "student_id", "major", "academic_year", "bio")
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 4, "placeholder": "Tell classmates a bit about yourself..."}),
        }

    def clean_student_id(self):
        student_id = self.cleaned_data["student_id"].strip()
        if Profile.objects.filter(student_id__iexact=student_id).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("This student ID is already registered.")
        return student_id


class PasswordChangeForm(BootstrapFormMixin, BasePasswordChangeForm):
    pass
