"""Sign-up form that creates a User *and* a Lead in one step."""

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

from core.models import Lead


class SignupForm(UserCreationForm):
    """Extended registration form — destination of “Get a Free Quote”."""

    full_name = forms.CharField(max_length=140, label="Full name")
    email = forms.EmailField(label="Email address")
    phone = forms.CharField(max_length=40, required=False, label="Phone number")
    project_type = forms.ChoiceField(choices=Lead.ProjectType.choices, label="Project type")
    project_details = forms.CharField(
        label="Project details",
        widget=forms.Textarea(attrs={"rows": 4, "placeholder": "Site, scope, budget range, timeline…"}),
    )

    class Meta:
        model = User
        fields = ["full_name", "email", "phone", "project_type", "project_details"]

    field_order = ["full_name", "email", "phone", "project_type", "project_details"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["password1"].label = "Password"
        self.fields["password2"].label = "Confirm password"
        self.order_fields(["full_name", "email", "phone", "project_type",
                           "project_details", "password1", "password2"])

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email, username__iexact=email).exists():
            raise forms.ValidationError("An account with this email already exists. Please log in instead.")
        return email

    def clean_project_details(self):
        details = (self.cleaned_data.get("project_details") or "").strip()
        if len(details) < 10:
            raise forms.ValidationError("Please give us at least a sentence about your project.")
        return details

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.username = self.cleaned_data["email"]  # email is the login identifier
        full_name = self.cleaned_data["full_name"].strip()
        parts = full_name.split(" ")
        user.first_name = parts[0][:150]
        user.last_name = " ".join(parts[1:])[:150]
        if commit:
            user.save()
            Lead.objects.create(
                full_name=full_name,
                email=user.email,
                phone=self.cleaned_data.get("phone", ""),
                project_type=self.cleaned_data["project_type"],
                details=self.cleaned_data["project_details"],
                source=Lead.Source.SIGNUP,
            )
        return user


class ClientLoginForm(AuthenticationForm):
    """Standard auth form with client-friendly labels."""

    username = forms.EmailField(label="Email address")
    password = forms.CharField(label="Password", strip=False, widget=forms.PasswordInput)