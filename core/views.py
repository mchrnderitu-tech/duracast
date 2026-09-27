"""Public-facing views: landing page, about, FAQ, thank-you, robots."""

from django.contrib import messages
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_http_methods

from .forms import LeadForm
from .models import FAQ, Project, Service


def _published_projects():
    return list(Project.objects.filter(is_published=True).order_by("order", "-created_at"))


@require_http_methods(["GET", "POST"])
def landing(request):
    """Landing page plus inline quote-request handling."""
    if request.method == "POST":
        form = LeadForm(request.POST)
        if form.is_valid():
            lead = form.save(commit=False)
            lead.source = lead.Source.LANDING
            lead.save()
            messages.success(request,
                "Thanks! Your request is in — a project manager will call you within one business day.")
            return redirect(reverse("core:thank_you") + f"?ref={lead.pk}")
        messages.error(request, "Please correct the highlighted fields and try again.")
    else:
        form = LeadForm()

    projects = _published_projects()
    context = {
        "form": form,
        "projects": projects,
        "projects_json": [p.as_dict() for p in projects],
        "services": Service.objects.filter(is_active=True).order_by("order", "title"),
        "faqs": FAQ.objects.filter(is_active=True).order_by("order", "question"),
        "categories": Project.Category.choices,
        "meta_title": "BuildCorp — Construction, Design-Build & Renovation",
        "meta_description": ("BuildCorp delivers residential and commercial construction from concept "
                             "to completion. Licensed, insured and on schedule."),
    }
    return render(request, "core/landing_page.html", context)


def about(request):
    projects = _published_projects()
    context = {
        "services": Service.objects.filter(is_active=True).order_by("order", "title"),
        "featured_projects": [p for p in projects if p.is_featured][:3] or projects[:3],
        "meta_title": "About BuildCorp — Our Story, Team & Values",
        "meta_description": ("Founded in 2005, BuildCorp has delivered 480+ projects with in-house "
                             "architects, engineers and site crews."),
    }
    return render(request, "core/about.html", context)


def faq(request):
    context = {
        "faqs": FAQ.objects.filter(is_active=True).order_by("order", "question"),
        "meta_title": "Frequently Asked Questions — BuildCorp",
        "meta_description": "Licensing, insurance, estimates, timelines and warranty — answered.",
    }
    return render(request, "core/faq.html", context)


def thank_you(request):
    return render(request, "core/thank_you.html", {
        "reference": request.GET.get("ref", ""),
        "meta_title": "Thank you — BuildCorp",
        "meta_description": "Your project request has been received.",
    })


def robots_txt(request):
    """Disallow crawling of the hidden dashboard and admin area."""
    from django.conf import settings

    lines = [
        "User-agent: *",
        "Disallow: /accounts/",
        f"Disallow: /{settings.COMPANY_DASHBOARD_URL}",
        f"Disallow: /{settings.DJANGO_ADMIN_URL}",
        f"Sitemap: {settings.SITE_BASE_URL.rstrip('/')}/sitemap.xml",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")