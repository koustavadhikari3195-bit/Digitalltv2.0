from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
from django.http import HttpResponse
from django.shortcuts import render
from .models import Lead
from .forms import LeadCaptureForm


def get_client_ip(request):
    """Extract client IP, respecting X-Forwarded-For for reverse proxies."""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


def index(request):
    """Landing page — hero, roast section, services, contact."""
    return render(request, "website/index.html")


def services_page(request):
    """Dedicated services page."""
    return render(request, "website/services.html")


@csrf_protect
@require_POST
def capture_lead(request):
    """HTMX endpoint for Gatekeeper modal lead capture."""
    form = LeadCaptureForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        lead, created = Lead.objects.get_or_create(
            email=cd["email"],
            defaults={
                "name": cd["name"],
                "website": cd.get("website", ""),
                "ip_address": get_client_ip(request),
                "source": "gatekeeper_modal",
            },
        )
        if not created:
            # Update name if they came back with a new submission
            lead.name = cd["name"]
            lead.save(update_fields=["name"])

        return HttpResponse(
            '<p class="text-green-400 font-medium flex items-center gap-2">'
            '<svg class="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">'
            '<polyline points="20,6 9,17 4,12"/></svg>'
            "We'll send your audit within 24 hours."
            "</p>"
        )
    errors = " ".join([e for errs in form.errors.values() for e in errs])
    return HttpResponse(f'<p class="text-red-400 text-xs">{errors}</p>', status=400)
