from django.urls import path
from . import views

app_name = "widgets"

urlpatterns = [
    path("live/", views.live_widgets, name="live"),
]
