"""Public-facing forms."""

from django import forms

from .models import Lead, Project


class LeadForm(forms.ModelForm):
    """Quote request form. Includes a honeypot ('website') field invisible to
    humans — bots that autofill it are rejected without a CAPTCHA."""

    website = forms.CharField(required=False, widget=forms.HiddenInput, label="")

    class Meta:
        model = Lead
        fields = ["full_name", "email", "phone", "project_type", "details"]
        widgets = {
            "full_name": forms.TextInput(attrs={"placeholder": "Jane Doe", "autocomplete": "name",
                                                "x-model": "fields.full_name", "@blur": "touch('full_name')"}),
            "email": forms.EmailInput(attrs={"placeholder": "jane@company.com", "autocomplete": "email",
                                             "x-model": "fields.email", "@blur": "touch('email')"}),
            "phone": forms.TextInput(attrs={"placeholder": "+1 (555) 010-2030", "autocomplete": "tel",
                                            "x-model": "fields.phone"}),
            "project_type": forms.Select(attrs={"x-model": "fields.project_type", "@change": "touch('project_type')"}),
            "details": forms.Textarea(attrs={"rows": 5, "x-model": "fields.details", "@blur": "touch('details')",
                                             "placeholder": "Tell us about the site, the scope, your budget range and timeline…"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["phone"].required = False
        self.fields["project_type"].empty_label = "Select a project type"
        self.fields["project_type"].required = True

    def clean_website(self):
        if self.cleaned_data.get("website"):
            raise forms.ValidationError("Submission rejected.")
        return ""

    def clean_details(self):
        details = (self.cleaned_data.get("details") or "").strip()
        if len(details) < 10:
            raise forms.ValidationError("Please give us at least a sentence about your project.")
        return details


class ProjectFilterForm(forms.Form):
    """Optional server-side filter for the gallery (progressive enhancement)."""

    category = forms.ChoiceField(required=False,
                                 choices=[("", "All projects")] + list(Project.Category.choices))