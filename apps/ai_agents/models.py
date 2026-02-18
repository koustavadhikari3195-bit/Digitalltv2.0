import uuid
from django.db import models
from django.utils import timezone


class RoastRequest(models.Model):
    """Tracks website roast requests for rate-limiting and audit."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    url = models.URLField(max_length=2000)
    ip_address = models.GenericIPAddressField()
    created_at = models.DateTimeField(default=timezone.now)
    was_successful = models.BooleanField(default=False)
    result_preview = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Roast: {self.url} ({self.created_at:%Y-%m-%d %H:%M})"
