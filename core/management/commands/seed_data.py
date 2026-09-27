"""Seed realistic demo content.

    python manage.py seed_data            # idempotent
    python manage.py seed_data --flush    # delete existing content first
"""

from datetime import date

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify

from core.models import FAQ, Project, Service, SiteContent
from core.placeholders import placeholder

SERVICES = [
    ("Residential Construction", "fa-solid fa-house-chimney-window",
     "Custom homes, multi-family builds and estates delivered turnkey — from site preparation "
     "and framing to the final inspection walkthrough."),
    ("Commercial Projects", "fa-solid fa-building",
     "Offices, retail, hospitality and light industrial builds engineered for operational "
     "efficiency, code compliance and leasing timelines."),
    ("Renovation & Remodeling", "fa-solid fa-hammer",
     "Structural retrofits, interior fit-outs and heritage restorations that respect the "
     "original build while modernising performance."),
    ("Project Management", "fa-solid fa-diagram-project",
     "Pre-construction planning, cost modelling, trade coordination and weekly reporting — "
     "one accountable team from concept to closeout."),
]

PROJECTS = [
    ("Meridian Ridge Residence", "residential", "Denver, CO", "Northgate Family Trust", date(2025, 8, 12),
     "A 5,400 sq ft hillside home with a glulam frame, geothermal loop and a fully daylit "
     "lower level. Delivered two weeks ahead of schedule.", True),
    ("Harbour Point Offices", "commercial", "Portland, OR", "Harbour Point Holdings", date(2025, 5, 30),
     "A six-storey, 92,000 sq ft mass-timber office block targeting LEED Gold, completed while "
     "the adjacent plaza stayed open to the public.", True),
    ("Ironside Loft Conversion", "renovation", "Seattle, WA", "Private client", date(2024, 11, 4),
     "A 1920s warehouse loft converted into four code-compliant residences with exposed steel, "
     "restored brickwork and a new structural mezzanine.", False),
    ("Cedarline Retail Pavilion", "commercial", "Boulder, CO", "Cedarline Retail Group", date(2024, 9, 19),
     "A 14,000 sq ft retail pavilion with cross-laminated timber roofing and a full stormwater "
     "reclamation system integrated into the landscape design.", False),
    ("Aspen Court Restoration", "renovation", "Aspen, CO", "Aspen Court Association", date(2024, 6, 7),
     "Heritage façade restoration on a 1908 civic building paired with a complete seismic "
     "upgrade and interior accessibility retrofit.", True),
    ("Kestrel Logistics Hub", "infrastructure", "Aurora, IL", "Kestrel Freight", date(2023, 10, 22),
     "A 210,000 sq ft distribution facility delivered design-build, including yard paving, dock "
     "equipment and a 2 MW rooftop solar array.", False),
    ("Larkspur Terrace Homes", "residential", "Fort Collins, CO", "Larkspur Development", date(2023, 7, 15),
     "Eighteen energy-positive townhomes built to Passive House standards with a shared courtyard "
     "and on-site water retention.", False),
    ("Vantage Bridge Deck Renewal", "infrastructure", "Tacoma, WA", "State Transport Authority", date(2023, 3, 28),
     "Night-shift deck replacement across a 340 m span, maintaining one open lane of traffic for "
     "the full duration of the works.", False),
]

FAQS = [
    ("What types of projects do you handle?",
     "We handle residential construction (custom homes, multi-family and estates), commercial "
     "builds (offices, retail, hospitality and light industrial), renovation and remodeling, and "
     "infrastructure packages such as logistics hubs and bridge renewal. Project values typically "
     "range from $250k to $40m."),
    ("Are you licensed and insured?",
     "Yes. We hold a general contractor licence in every state we operate in, carry $5m general "
     "liability plus workers' compensation cover, and are fully bonded. Certificates of insurance "
     "are issued to clients before mobilisation."),
    ("How do you estimate project costs?",
     "Every estimate starts with a site visit and a scope workshop. You receive a line-item cost "
     "plan built from live trade pricing, separated into hard costs, soft costs, contingency and "
     "allowances — so there are no hidden line items later."),
    ("How long will my project take?",
     "After the scope workshop we publish a milestone schedule with dates for design sign-off, "
     "permits, mobilisation, key trades and closeout. We report progress weekly, and 98% of our "
     "projects over the last three years finished on or before the agreed date."),
    ("Do you provide a warranty?",
     "Yes. All workmanship carries a 24-month warranty, manufacturer warranties are registered in "
     "your name at handover, and structural elements are covered for the full statutory period. "
     "Our closeout pack includes as-built drawings and O&M manuals."),
    ("Can I make changes once construction has started?",
     "Absolutely — changes are managed through a written variation order showing the cost and "
     "schedule impact before any work proceeds. Nothing is actioned until you approve it in writing."),
]


class Command(BaseCommand):
    help = "Populate the database with demo services, projects, FAQs and site content."

    def add_arguments(self, parser):
        parser.add_argument("--flush", action="store_true", help="Delete existing content first.")

    @transaction.atomic
    def handle(self, *args, **options):
        if options["flush"]:
            Project.objects.all().delete()
            Service.objects.all().delete()
            FAQ.objects.all().delete()
            self.stdout.write(self.style.WARNING("Existing content deleted."))

        SiteContent.get_solo().save()
        self.stdout.write("Site content ready.")

        for index, (title, icon, description) in enumerate(SERVICES, start=1):
            Service.objects.update_or_create(title=title, defaults={
                "icon": icon, "description": description, "order": index, "is_active": True})

        for index, (title, category, location, client, completed, description, featured) in enumerate(PROJECTS, start=1):
            Project.objects.update_or_create(slug=slugify(title), defaults={
                "title": title, "category": category, "location": location, "client": client,
                "completed_on": completed, "description": description, "is_featured": featured,
                "is_published": True, "order": index,
                "image_url": placeholder(f"project-{slugify(title)}", 1400, 1000),
            })

        for index, (question, answer) in enumerate(FAQS, start=1):
            FAQ.objects.update_or_create(question=question, defaults={
                "answer": answer, "order": index, "is_active": True})

        self.stdout.write(self.style.SUCCESS(
            f"Seeded {len(SERVICES)} services, {len(PROJECTS)} projects, {len(FAQS)} FAQs."))