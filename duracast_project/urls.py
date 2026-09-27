from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path(settings.DJANGO_ADMIN_URL, admin.site.urls),
    # Hidden staff dashboard — prefix configurable in settings/.env
    path(settings.COMPANY_DASHBOARD_URL, include("dashboard.urls")),
    path("accounts/", include("accounts.urls")),
    path("", include("core.urls")),  # owns "/", keep last
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)