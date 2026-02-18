from django.contrib import admin
from .models import Lead


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "source", "is_contacted", "created_at")
    list_filter = ("source", "is_contacted", "created_at")
    search_fields = ("name", "email", "website")
    readonly_fields = ("id", "created_at", "ip_address")
    ordering = ("-created_at",)
