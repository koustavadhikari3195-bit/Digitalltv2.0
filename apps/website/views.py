from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
from django.http import HttpResponse
from django.shortcuts import render
from .models import Lead
from .forms import LeadCaptureForm


import hashlib

def get_client_ip(request):
    """Extract client IP, respecting X-Forwarded-For for reverse proxies."""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")

def get_hashed_ip(request):
    """Return SHA-256 hash of the client IP for GDPR compliance."""
    ip = get_client_ip(request)
    if ip:
        return hashlib.sha256(ip.encode()).hexdigest()
    return None


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
                "ip_address": get_hashed_ip(request),
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

@csrf_protect
@require_POST
def full_inquiry(request):
    """3-step project inquiry handler via HTMX. Creates/Links a Lead and an Inquiry."""
    from .forms import InquiryForm
    from .models import Lead

    form = InquiryForm(request.POST)

    if not form.is_valid():
        error_lines = [
            f'<strong>{f.replace("_"," ").title()}:</strong> {errs[0]}'
            for f, errs in form.errors.items()
        ]
        return HttpResponse(
            '<div style="background:rgba(239,68,68,.1);border:1px solid rgba(239,68,68,.3);'
            'border-radius:10px;padding:16px;color:#f87171;font-size:13px;line-height:1.8;">'
            + "<br>".join(error_lines)
            + "</div>",
            status=400,
        )

    inquiry = form.save(commit=False)
    inquiry.ip_address = get_hashed_ip(request)

    try:
        inquiry.lead = Lead.objects.get(email=inquiry.email)
    except Lead.DoesNotExist:
        inquiry.lead = Lead.objects.create(
            name=inquiry.name,
            email=inquiry.email,
            website=inquiry.website,
            ip_address=inquiry.ip_address, # Already hashed above
            source="full_inquiry_form",
        )
    inquiry.save()

    # Log the win to the journal
    log_entry = (
        f"\n---\n### ✅ New Inquiry — {inquiry.name}\n"
        f"**Email:** {inquiry.email}  \n"
        f"**Budget:** {inquiry.budget}  \n"
        f"**Services:** {', '.join(inquiry.services)}  \n"
        f"**Created:** {inquiry.created_at.isoformat()}\n"
    )
    _append_journal("_dev_journal/01_error_log.md", log_entry)

    return HttpResponse(
        '<div style="background:rgba(22,163,74,.08);border:1px solid rgba(22,163,74,.2);'
        'border-radius:16px;padding:44px;text-align:center;">'
        '<div style="width:54px;height:54px;background:rgba(22,163,74,.15);border-radius:50%;'
        'display:flex;align-items:center;justify-content:center;margin:0 auto 18px;">'
        '<svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="#4ade80"'
        ' stroke-width="2.5" style="stroke-dasharray:100;stroke-dashoffset:100;'
        'animation:checkDraw .5s ease .15s forwards;">'
        '<polyline points="20 6 9 17 4 12"/></svg></div>'
        '<p style="font-family:\'Syne\',sans-serif;font-weight:900;font-size:22px;'
        'color:#fff;margin-bottom:10px;">We got it.</p>'
        '<p style="font-size:14px;color:#A0A0A0;line-height:1.75;max-width:380px;margin:0 auto;">'
        "Expect a tailored response within 24 hours. "
        "Urgent? WhatsApp us directly — link below.</p></div>"
    )


def _append_journal(path, entry):
    """Internal utility to log project events to markdown files."""
    try:
        from pathlib import Path

        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        with open(p, "a", encoding="utf-8") as f:
            f.write(entry)
    except Exception:
        pass
