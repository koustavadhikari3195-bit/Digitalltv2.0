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
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    is_contacted = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} <{self.email}>"
