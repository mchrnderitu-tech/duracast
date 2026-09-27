"""Dashboard URLs — mounted at settings.COMPANY_DASHBOARD_URL.

All paths here are relative, so changing COMPANY_DASHBOARD_URL (or sourcing it
from an env var) instantly relocates the whole dashboard with no other edits.
"""

from django.urls import path

from . import views

app_name = "dashboard"

urlpatterns = [
    path("login/", views.DashboardLoginView.as_view(), name="login"),
    path("logout/", views.DashboardLogoutView.as_view(), name="logout"),
    path("", views.dashboard_home, name="home"),

    # Leads
    path("leads/", views.LeadListView.as_view(), name="lead-list"),
    path("leads/<int:pk>/", views.lead_detail, name="lead-detail"),
    path("leads/<int:pk>/toggle-contacted/", views.lead_toggle_contacted, name="lead-toggle"),
    path("leads/<int:pk>/delete/", views.LeadDeleteView.as_view(), name="lead-delete"),

    # Projects
    path("projects/", views.ProjectListView.as_view(), name="project-list"),
    path("projects/new/", views.ProjectCreateView.as_view(), name="project-create"),
    path("projects/<int:pk>/edit/", views.ProjectUpdateView.as_view(), name="project-update"),
    path("projects/<int:pk>/delete/", views.ProjectDeleteView.as_view(), name="project-delete"),

    # Services
    path("services/", views.ServiceListView.as_view(), name="service-list"),
    path("services/new/", views.ServiceCreateView.as_view(), name="service-create"),
    path("services/<int:pk>/edit/", views.ServiceUpdateView.as_view(), name="service-update"),
    path("services/<int:pk>/delete/", views.ServiceDeleteView.as_view(), name="service-delete"),

    # FAQs
    path("faqs/", views.FAQListView.as_view(), name="faq-list"),
    path("faqs/new/", views.FAQCreateView.as_view(), name="faq-create"),
    path("faqs/<int:pk>/edit/", views.FAQUpdateView.as_view(), name="faq-update"),
    path("faqs/<int:pk>/delete/", views.FAQDeleteView.as_view(), name="faq-delete"),

    # Site content
    path("content/", views.SiteContentUpdateView.as_view(), name="content-edit"),
]