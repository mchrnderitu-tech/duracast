from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("", views.landing, name="landing"),
    path("about/", views.about, name="about"),
    path("faq/", views.faq, name="faq"),
    path("thank-you/", views.thank_you, name="thank_you"),
    path("robots.txt", views.robots_txt, name="robots"),
]