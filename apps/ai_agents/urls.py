from django.urls import path
from . import views

app_name = "ai_agents"

urlpatterns = [
    path("chat/", views.chat_view, name="chat"),
    path("roast/", views.roast_view, name="roast"),
]
