"""Django-admin fallback mirroring the custom dashboard."""

from django.contrib import admin

from .models import FAQ, Lead, Project, Service, SiteContent


@admin.register(SiteContent)
class SiteContentAdmin(admin.ModelAdmin):
    list_display = ("company_name", "hero_headline", "updated_at")
    fieldsets = (
        ("Branding", {"fields": ("company_name", "tagline")}),
        ("Hero", {"fields": ("hero_eyebrow", "hero_headline", "hero_subheadline", "hero_spline_url",
                             "hero_video_url", "hero_video_poster", "hero_primary_cta_label",
                             "hero_secondary_cta_label")}),
        ("About", {"fields": ("about_heading", "about_body", "about_body_secondary",
                              "about_image_primary", "about_image_secondary", "about_image_tertiary",
                              "years_experience", "projects_completed", "team_members", "on_time_rate")}),
        ("Contact & footer", {"fields": ("contact_email", "contact_phone", "contact_address",
                                         "office_hours", "footer_tagline", "footer_copyright",
                                         "facebook_url", "linkedin_url", "instagram_url")}),
    )

    def has_add_permission(self, request):
        # Singleton: editable, but a second row can never be added.
        return not SiteContent.objects.exists()


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("title", "order", "is_active")
    list_editable = ("order", "is_active")
    list_filter = ("is_active",)
    search_fields = ("title", "description")


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "location", "completed_on", "is_featured", "is_published")
    list_editable = ("is_featured", "is_published")
    list_filter = ("category", "is_featured", "is_published")
    search_fields = ("title", "description", "client", "location")
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "created_at"


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ("question", "order", "is_active")
    list_editable = ("order", "is_active")
    search_fields = ("question", "answer")


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "project_type", "source", "is_contacted", "created_at")
    list_filter = ("project_type", "source", "is_contacted")
    search_fields = ("full_name", "email", "phone", "details")
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "created_at"