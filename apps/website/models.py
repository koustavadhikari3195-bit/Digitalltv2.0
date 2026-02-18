import uuid
from django.db import models
from django.utils import timezone


class Lead(models.Model):
    """Captured lead from the Gatekeeper modal or other sources."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True, db_index=True)
    website = models.URLField(max_length=2000, blank=True)
    source = models.CharField(max_length=50, default="gatekeeper_modal")
    ip_address = models.CharField(max_length=64, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    is_contacted = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]


class Inquiry(models.Model):
    """
    Full project inquiry. 3-step form submission.
    Auto-links to Lead record on matching email.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # Step 1 — Identity
    name = models.CharField(max_length=100)
    email = models.EmailField(db_index=True)
    company = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    website = models.URLField(max_length=2000, blank=True)
    role = models.CharField(max_length=50, blank=True)
    # Step 2 — Goals
    services = models.JSONField(default=list)  # list of service slugs
    goals = models.TextField(max_length=1000)
    # Step 3 — Scope
    budget = models.CharField(max_length=30, blank=True)
    timeline = models.CharField(max_length=30, blank=True)
    source_channel = models.CharField(max_length=40, blank=True)
    notes = models.TextField(max_length=2000, blank=True)
    # Meta
    ip_address = models.CharField(max_length=64, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(
        max_length=20,
        default="new",
        choices=[
            ("new", "New"),
            ("contacted", "Contacted"),
            ("converted", "Converted"),
            ("lost", "Lost"),
        ],
    )
    lead = models.ForeignKey(
        "Lead",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="inquiries",
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Inquiries"

    def __str__(self):
        return f"{self.name} | {self.budget} | {self.status}"
