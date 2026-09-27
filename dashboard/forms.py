"""Forms used exclusively by the staff dashboard."""

from django import forms
from django.contrib.auth.forms import AuthenticationForm

from core.models import FAQ, Lead, Project, Service, SiteContent


class StaffAuthenticationForm(AuthenticationForm):
    """Login form that rejects valid-but-non-staff credentials outright."""

    def confirm_login_allowed(self, user):
        super().confirm_login_allowed(user)
        if not user.is_staff:
            raise forms.ValidationError("This account does not have dashboard access.", code="not_staff")


class ProjectForm(forms.ModelForm):
    """Create/update a gallery project."""

    class Meta:
        model = Project
        fields = ["title", "category", "description", "image", "image_url", "client",
                  "location", "completed_on", "is_featured", "is_published", "order"]
        widgets = {"description": forms.Textarea(attrs={"rows": 4}),
                   "completed_on": forms.DateInput(attrs={"type": "date"})}
        help_texts = {
            "image": "Upload a photo (preferred). Max ~4 MB, landscape orientation.",
            "image_url": "Or paste an external image URL — used only when no upload exists.",
        }

    def clean_image(self):
        image = self.cleaned_data.get("image")
        if image and getattr(image, "size", 0) > 5 * 1024 * 1024:
            raise forms.ValidationError("Images must be smaller than 5 MB.")
        return image


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ["title", "icon", "description", "order", "is_active"]
        widgets = {"description": forms.Textarea(attrs={"rows": 3})}
        help_texts = {"icon": "Any Font Awesome class, e.g. fa-solid fa-building"}


class FAQForm(forms.ModelForm):
    class Meta:
        model = FAQ
        fields = ["question", "answer", "order", "is_active"]
        widgets = {"answer": forms.Textarea(attrs={"rows": 4})}


class LeadUpdateForm(forms.ModelForm):
    """Staff-only fields on a captured lead."""

    class Meta:
        model = Lead
        fields = ["is_contacted", "internal_notes"]
        widgets = {"internal_notes": forms.Textarea(attrs={"rows": 4})}


class SiteContentForm(forms.ModelForm):
    """Edit the copy blocks exposed on the public site."""

    class Meta:
        model = SiteContent
        fields = ["company_name", "tagline", "hero_eyebrow", "hero_headline", "hero_subheadline",
                  "hero_spline_url", "hero_video_url", "hero_video_poster", "hero_primary_cta_label",
                  "hero_secondary_cta_label", "about_heading", "about_body", "about_body_secondary",
                  "about_image_primary", "about_image_secondary", "about_image_tertiary",
                  "years_experience", "projects_completed", "team_members", "on_time_rate",
                  "contact_email", "contact_phone", "contact_address", "office_hours",
                  "footer_tagline", "footer_copyright", "facebook_url", "linkedin_url", "instagram_url"]
        widgets = {
            "hero_subheadline": forms.Textarea(attrs={"rows": 3}),
            "about_body": forms.Textarea(attrs={"rows": 5}),
            "about_body_secondary": forms.Textarea(attrs={"rows": 4}),
        }