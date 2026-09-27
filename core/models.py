"""Content models shared by the public site and the staff dashboard."""

from django.db import models
from django.urls import reverse
from django.utils.text import slugify

from .placeholders import placeholder


class TimeStampedModel(models.Model):
    """Abstract base adding audit timestamps to every content model."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class SiteContent(TimeStampedModel):
    """Singleton (pk=1) holding every editable block of marketing copy.

    Exposed globally via core.context_processors.site_context, so any template
    can read {{ site.hero_headline }} etc.
    """

    # Branding
    company_name = models.CharField(max_length=80, default="BuildCorp")
    tagline = models.CharField(max_length=160, default="Building the Future, Restoring the Past.")

    # Hero
    hero_eyebrow = models.CharField(max_length=120, default="Licensed & insured · Design-build since 2005")
    hero_headline = models.CharField(max_length=200, default="Building the Future, Restoring the Past.")
    hero_subheadline = models.TextField(default=(
        "Your trusted partner for residential and commercial construction. "
        "From concept to completion, we deliver excellence with integrity."
    ))
    hero_spline_url = models.URLField(blank=True, help_text="Spline scene .splinecode URL.")
    hero_video_url = models.URLField(blank=True, help_text="Optional looping MP4 fallback.")
    hero_video_poster = models.ImageField(upload_to="site/", blank=True, null=True)
    hero_primary_cta_label = models.CharField(max_length=60, default="Request a Consultation")
    hero_secondary_cta_label = models.CharField(max_length=60, default="View Our Work")

    # About
    about_heading = models.CharField(max_length=160, default="Who We Are")
    about_body = models.TextField(default=(
        "Founded in 2005, BuildCorp has been at the forefront of innovative construction, "
        "delivering more than 480 residential and commercial projects across the region. "
        "Our in-house architects, engineers and site teams work as one unit, which means "
        "fewer hand-offs, tighter schedules and a single point of accountability for you."
    ))
    about_body_secondary = models.TextField(blank=True, default=(
        "We are licensed, bonded and fully insured, and we hold our crews to a safety "
        "standard that goes well beyond the minimum. Every project is led by a dedicated "
        "project manager who reports to you weekly with photos, budgets and next steps."
    ))
    about_image_primary = models.ImageField(upload_to="site/", blank=True, null=True)
    about_image_secondary = models.ImageField(upload_to="site/", blank=True, null=True)
    about_image_tertiary = models.ImageField(upload_to="site/", blank=True, null=True)

    # Trust stats
    years_experience = models.PositiveIntegerField(default=21)
    projects_completed = models.PositiveIntegerField(default=480)
    team_members = models.PositiveIntegerField(default=65)
    on_time_rate = models.PositiveIntegerField(default=98, help_text="Percentage on time.")

    # Contact & footer
    contact_email = models.EmailField(default="hello@buildcorp.example")
    contact_phone = models.CharField(max_length=40, default="+1 (555) 010-2030")
    contact_address = models.CharField(max_length=200, default="1200 Ironworks Avenue, Suite 400, Denver, CO 80216")
    office_hours = models.CharField(max_length=120, default="Mon – Fri · 7:30am – 6:00pm")
    footer_tagline = models.CharField(max_length=220, default=(
        "Design-build construction delivered with integrity, transparency and craftsmanship."
    ))
    footer_copyright = models.CharField(max_length=120, default="Duracast")
    facebook_url = models.URLField(blank=True, default="https://facebook.com")
    linkedin_url = models.URLField(blank=True, default="https://linkedin.com")
    instagram_url = models.URLField(blank=True, default="https://instagram.com")

    class Meta:
        verbose_name = "site content"
        verbose_name_plural = "site content"

    def __str__(self):
        return "Site content"

    def save(self, *args, **kwargs):
        self.pk = 1  # enforce the singleton
        super().save(*args, **kwargs)

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    # Template-friendly image accessors with placeholder fallbacks
    @property
    def about_image_primary_url(self):
        return self.about_image_primary.url if self.about_image_primary else placeholder("buildcorp-team", 900, 1100)

    @property
    def about_image_secondary_url(self):
        return self.about_image_secondary.url if self.about_image_secondary else placeholder("buildcorp-blueprint", 900, 700)

    @property
    def about_image_tertiary_url(self):
        return self.about_image_tertiary.url if self.about_image_tertiary else placeholder("buildcorp-site", 900, 700)

    @property
    def hero_poster_url(self):
        return self.hero_video_poster.url if self.hero_video_poster else placeholder("buildcorp-hero", 1920, 1080)


class Service(TimeStampedModel):
    """A card in the public “Services” grid."""

    title = models.CharField(max_length=120)
    icon = models.CharField(max_length=80, default="fa-solid fa-helmet-safety",
                            help_text="Font Awesome class, e.g. fa-solid fa-building")
    description = models.TextField()
    order = models.PositiveSmallIntegerField(default=0, help_text="Lower numbers appear first.")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("order", "title")
        verbose_name = "service"
        verbose_name_plural = "services"

    def __str__(self):
        return self.title


class Project(TimeStampedModel):
    """A gallery item — also the CRUD target of the staff dashboard."""

    class Category(models.TextChoices):
        RESIDENTIAL = "residential", "Residential"
        COMMERCIAL = "commercial", "Commercial"
        RENOVATION = "renovation", "Renovation & Remodeling"
        INFRASTRUCTURE = "infrastructure", "Infrastructure"

    title = models.CharField(max_length=160)
    slug = models.SlugField(max_length=180, unique=True, blank=True)
    category = models.CharField(max_length=20, choices=Category.choices, default=Category.RESIDENTIAL)
    description = models.TextField(help_text="Short summary shown in the gallery modal.")
    image = models.ImageField(upload_to="projects/", blank=True, null=True)
    image_url = models.URLField(blank=True, help_text="External image URL when no upload exists.")
    client = models.CharField(max_length=140, blank=True)
    location = models.CharField(max_length=140, blank=True)
    completed_on = models.DateField(blank=True, null=True)
    is_featured = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ("order", "-completed_on", "-created_at")
        verbose_name = "project"
        verbose_name_plural = "projects"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)[:170] or "project"
            slug, counter = base, 2
            while Project.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return f"{reverse('core:landing')}#projects"

    @property
    def display_image(self):
        """Upload first, then external URL, then deterministic placeholder."""
        if self.image:
            return self.image.url
        if self.image_url:
            return self.image_url
        return placeholder(f"project-{self.slug or self.pk or 'new'}", 1400, 1000)

    @property
    def year(self):
        return self.completed_on.year if self.completed_on else None

    def as_dict(self):
        """Payload consumed by the Alpine gallery component."""
        return {
            "id": self.pk,
            "title": self.title,
            "category": self.category,
            "categoryLabel": self.get_category_display(),
            "description": self.description,
            "client": self.client,
            "location": self.location,
            "year": self.year,
            "image": self.display_image,
            "featured": self.is_featured,
        }


class FAQ(TimeStampedModel):
    """Accordion item on the landing page and /faq/ page."""

    question = models.CharField(max_length=220)
    answer = models.TextField()
    order = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("order", "question")
        verbose_name = "FAQ"
        verbose_name_plural = "FAQs"

    def __str__(self):
        return self.question


class Lead(TimeStampedModel):
    """A quote request captured from the public site."""

    class ProjectType(models.TextChoices):
        RESIDENTIAL = "residential", "Residential"
        COMMERCIAL = "commercial", "Commercial"
        OTHER = "other", "Other"

    class Source(models.TextChoices):
        LANDING = "landing", "Landing page form"
        SIGNUP = "signup", "Sign-up page"
        PHONE = "phone", "Phone call"
        REFERRAL = "referral", "Referral"

    full_name = models.CharField(max_length=140)
    email = models.EmailField()
    phone = models.CharField(max_length=40, blank=True)
    project_type = models.CharField(max_length=20, choices=ProjectType.choices, default=ProjectType.RESIDENTIAL)
    details = models.TextField(verbose_name="Project details")
    source = models.CharField(max_length=20, choices=Source.choices, default=Source.LANDING)
    is_contacted = models.BooleanField(default=False)
    internal_notes = models.TextField(blank=True)

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "lead"
        verbose_name_plural = "leads"

    def __str__(self):
        return f"{self.full_name} · {self.get_project_type_display()}"