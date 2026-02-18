from django.urls import path
from . import views

app_name = "website"

urlpatterns = [
    path("", views.index, name="index"),
    path("services/", views.services_page, name="services"),
    path("leads/capture/", views.capture_lead, name="capture_lead"),
    path("leads/full-inquiry/", views.full_inquiry, name="full_inquiry"),
]
