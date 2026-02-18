from django.contrib import admin
from .models import RoastRequest


@admin.register(RoastRequest)
class RoastRequestAdmin(admin.ModelAdmin):
    list_display = ("url", "ip_address", "was_successful", "created_at")
    list_filter = ("was_successful", "created_at")
    search_fields = ("url", "ip_address")
    readonly_fields = ("id", "created_at")
    ordering = ("-created_at",)
