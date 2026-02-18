"""
DIGITALLY — Root URL Configuration
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("apps.website.urls")),
    path("ai/", include("apps.ai_agents.urls")),
    path("widgets/", include("apps.widgets.urls")),
]
