"""Globally available template context (branding, navigation, site content)."""

from django.db.utils import OperationalError, ProgrammingError

from .models import Service, SiteContent

NAV_LINKS = [
    {"label": "Home", "url_name": "core:landing", "anchor": "top"},
    {"label": "About Us", "url_name": "core:about", "anchor": ""},
    {"label": "Services", "url_name": "core:landing", "anchor": "services"},
    {"label": "Projects", "url_name": "core:landing", "anchor": "projects"},
    {"label": "FAQ", "url_name": "core:faq", "anchor": ""},
    {"label": "Contact", "url_name": "core:landing", "anchor": "contact"},
]


def site_context(request):
    """Expose `site_content`, nav links and services to every template."""
    try:
        site = SiteContent.get_solo()
        services = list(Service.objects.filter(is_active=True).order_by("order", "title"))
    except (OperationalError, ProgrammingError):
        site, services = SiteContent(), []

    return {"site_content": site, "nav_links": NAV_LINKS, "services": services}