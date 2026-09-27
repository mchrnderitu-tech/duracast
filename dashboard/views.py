"""Staff dashboard views. Every view is gated behind StaffRequiredMixin/staff_required."""

from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.views import LoginView, LogoutView
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from core.models import FAQ, Lead, Project, Service, SiteContent

from .forms import (FAQForm, LeadUpdateForm, ProjectForm, ServiceForm,
                    SiteContentForm, StaffAuthenticationForm)
from .mixins import StaffRequiredMixin, staff_required


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------
class DashboardLoginView(LoginView):
    """Minimal login page at <dashboard-prefix>/login/."""

    template_name = "dashboard/login.html"
    authentication_form = StaffAuthenticationForm
    redirect_authenticated_user = True

    def get_success_url(self):
        return self.get_redirect_url() or reverse("dashboard:home")


class DashboardLogoutView(LogoutView):
    next_page = "dashboard:login"


# ---------------------------------------------------------------------------
# Home
# ---------------------------------------------------------------------------
@staff_required
def dashboard_home(request):
    """Overview: KPIs plus the five most recent leads."""
    today = timezone.now()
    context = {
        "total_leads": Lead.objects.count(),
        "new_leads_7d": Lead.objects.filter(created_at__gte=today - timedelta(days=7)).count(),
        "uncontacted_leads": Lead.objects.filter(is_contacted=False).count(),
        "project_count": Project.objects.count(),
        "published_project_count": Project.objects.filter(is_published=True).count(),
        "faq_count": FAQ.objects.filter(is_active=True).count(),
        "service_count": Service.objects.filter(is_active=True).count(),
        "recent_leads": Lead.objects.all()[:5],
        "leads_by_type": Lead.objects.values("project_type").annotate(total=Count("id")).order_by("-total"),
    }
    return render(request, "dashboard/dashboard_home.html", context)


# ---------------------------------------------------------------------------
# Reusable CRUD base classes — keeps the dashboard DRY
# ---------------------------------------------------------------------------
class StaffCrudMixin(StaffRequiredMixin):
    """Shared context for the dashboard create/update/delete templates."""

    object_type = ""
    cancel_url_name = ""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["object_type"] = self.object_type
        context["cancel_url"] = reverse(self.cancel_url_name)
        if isinstance(self, (CreateView, UpdateView)):
            obj = getattr(self, "object", None)
            label = str(obj) if obj else None
            context["form_title"] = f"Edit “{label}”" if label else f"Add {self.object_type}"
        else:
            context["object_label"] = str(self.object)
            context["cancel_url"] = reverse(self.cancel_url_name)
        return context

    def form_valid(self, form):
        messages.success(self.request, f"{self.object_type.capitalize()} saved.")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Please correct the errors below.")
        return super().form_invalid(form)


class StaffDeleteMixin(StaffRequiredMixin):
    template_name = "dashboard/confirm_delete.html"
    object_type = ""
    cancel_url_name = ""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "object_label": str(self.object),
            "object_type": self.object_type,
            "cancel_url": reverse(self.cancel_url_name),
        })
        return context

    def form_valid(self, form):
        messages.success(self.request, f"{self.object_type.capitalize()} deleted.")
        return super().form_valid(form)


# ---------------------------------------------------------------------------
# Leads
# ---------------------------------------------------------------------------
class LeadListView(StaffRequiredMixin, ListView):
    model = Lead
    template_name = "dashboard/leads_list.html"
    context_object_name = "leads"
    paginate_by = 20

    def get_queryset(self):
        queryset = Lead.objects.all()
        status = self.request.GET.get("status")
        project_type = self.request.GET.get("type")
        query = self.request.GET.get("q")
        if status == "new":
            queryset = queryset.filter(is_contacted=False)
        elif status == "contacted":
            queryset = queryset.filter(is_contacted=True)
        if project_type in dict(Lead.ProjectType.choices):
            queryset = queryset.filter(project_type=project_type)
        if query:
            queryset = queryset.filter(Q(full_name__icontains=query) | Q(email__icontains=query)
                                       | Q(details__icontains=query))
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            "project_types": Lead.ProjectType.choices,
            "current_status": self.request.GET.get("status", ""),
            "current_type": self.request.GET.get("type", ""),
            "query": self.request.GET.get("q", ""),
        })
        return context


@staff_required
def lead_detail(request, pk):
    """Read a lead and record follow-up notes."""
    lead = get_object_or_404(Lead, pk=pk)
    if request.method == "POST":
        form = LeadUpdateForm(request.POST, instance=lead)
        if form.is_valid():
            form.save()
            messages.success(request, "Lead updated.")
            return redirect("dashboard:lead-detail", pk=lead.pk)
    else:
        form = LeadUpdateForm(instance=lead)
    return render(request, "dashboard/lead_detail.html", {"lead": lead, "form": form})


@staff_required
@require_POST
def lead_toggle_contacted(request, pk):
    lead = get_object_or_404(Lead, pk=pk)
    lead.is_contacted = not lead.is_contacted
    lead.save(update_fields=["is_contacted", "updated_at"])
    messages.success(request, f"{lead.full_name} marked as "
                              f"{'contacted' if lead.is_contacted else 'not contacted'}.")
    return redirect(request.META.get("HTTP_REFERER") or reverse("dashboard:lead-list"))


class LeadDeleteView(StaffDeleteMixin, DeleteView):
    model = Lead
    object_type = "lead"
    cancel_url_name = "dashboard:lead-list"
    success_url = reverse_lazy("dashboard:lead-list")


# ---------------------------------------------------------------------------
# Projects
# ---------------------------------------------------------------------------
class ProjectListView(StaffRequiredMixin, ListView):
    model = Project
    template_name = "dashboard/project_list.html"
    context_object_name = "projects"
    paginate_by = 20


class ProjectCreateView(StaffCrudMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = "dashboard/project_form.html"
    object_type = "project"
    cancel_url_name = "dashboard:project-list"
    success_url = reverse_lazy("dashboard:project-list")


class ProjectUpdateView(StaffCrudMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = "dashboard/project_form.html"
    object_type = "project"
    cancel_url_name = "dashboard:project-list"
    success_url = reverse_lazy("dashboard:project-list")


class ProjectDeleteView(StaffDeleteMixin, DeleteView):
    model = Project
    object_type = "project"
    cancel_url_name = "dashboard:project-list"
    success_url = reverse_lazy("dashboard:project-list")


# ---------------------------------------------------------------------------
# Services
# ---------------------------------------------------------------------------
class ServiceListView(StaffRequiredMixin, ListView):
    model = Service
    template_name = "dashboard/service_list.html"
    context_object_name = "services"


class ServiceCreateView(StaffCrudMixin, CreateView):
    model = Service
    form_class = ServiceForm
    template_name = "dashboard/service_form.html"
    object_type = "service"
    cancel_url_name = "dashboard:service-list"
    success_url = reverse_lazy("dashboard:service-list")


class ServiceUpdateView(StaffCrudMixin, UpdateView):
    model = Service
    form_class = ServiceForm
    template_name = "dashboard/service_form.html"
    object_type = "service"
    cancel_url_name = "dashboard:service-list"
    success_url = reverse_lazy("dashboard:service-list")


class ServiceDeleteView(StaffDeleteMixin, DeleteView):
    model = Service
    object_type = "service"
    cancel_url_name = "dashboard:service-list"
    success_url = reverse_lazy("dashboard:service-list")


# ---------------------------------------------------------------------------
# FAQs
# ---------------------------------------------------------------------------
class FAQListView(StaffRequiredMixin, ListView):
    model = FAQ
    template_name = "dashboard/faq_list.html"
    context_object_name = "faqs"


class FAQCreateView(StaffCrudMixin, CreateView):
    model = FAQ
    form_class = FAQForm
    template_name = "dashboard/faq_form.html"
    object_type = "FAQ"
    cancel_url_name = "dashboard:faq-list"
    success_url = reverse_lazy("dashboard:faq-list")


class FAQUpdateView(StaffCrudMixin, UpdateView):
    model = FAQ
    form_class = FAQForm
    template_name = "dashboard/faq_form.html"
    object_type = "FAQ"
    cancel_url_name = "dashboard:faq-list"
    success_url = reverse_lazy("dashboard:faq-list")


class FAQDeleteView(StaffDeleteMixin, DeleteView):
    model = FAQ
    object_type = "FAQ"
    cancel_url_name = "dashboard:faq-list"
    success_url = reverse_lazy("dashboard:faq-list")


# ---------------------------------------------------------------------------
# Site content (singleton)
# ---------------------------------------------------------------------------
class SiteContentUpdateView(StaffRequiredMixin, UpdateView):
    """Edits the hero headline, about copy, contact details and footer text."""

    form_class = SiteContentForm
    template_name = "dashboard/content_form.html"
    success_url = reverse_lazy("dashboard:content-edit")

    def get_object(self, queryset=None):
        return SiteContent.get_solo()

    def form_valid(self, form):
        messages.success(self.request, "Site content saved — refresh the public site to see it.")
        return super().form_valid(form)