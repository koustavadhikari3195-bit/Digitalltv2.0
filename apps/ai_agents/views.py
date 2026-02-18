import json
from datetime import timedelta

from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_protect
from django.http import JsonResponse, HttpResponse
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.core.cache import cache
from django.utils import timezone
from django.conf import settings
from groq import Groq

from .models import RoastRequest
from .utils.scraper import scrape_website
from .utils.gpt_client import roast_website
from .utils.logger import log_failure


# ──────────────────────────────────────────────
# Helper
# ──────────────────────────────────────────────
def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


# ──────────────────────────────────────────────
# FEATURE 2 — AI Sales Director (Chatbot)
# ──────────────────────────────────────────────
SALES_SYSTEM_PROMPT = """
You are the AI Sales Director for DIGITALLY, a premium digital agency.
You are professional, direct, and sales-driven — but never pushy or fake.

YOUR SERVICES (be specific, never invent):
1. Website Management — Hosting, daily backups, uptime monitoring, SSL management, speed optimization. Retainer: from ₹8,000/month.
2. Social Media — 15–20 posts/month, platform strategy, copywriting, scheduling. Platforms: Instagram, LinkedIn, Twitter/X. From ₹12,000/month.
3. SEO — On-page optimization, Google My Business (GMB) management, monthly ranking reports, backlink outreach. From ₹10,000/month.
4. Content Marketing — 4 blog posts/month, email newsletter (biweekly), content calendar. From ₹15,000/month.
5. Graphic Design — Brand identity, social templates, pitch decks, marketing collateral. From ₹5,000/project.

RULES:
- If someone asks about pricing, give the starting range and note that exact pricing depends on scope.
- If they seem interested or ask what to do next, always close with: "Want to book a free 15-minute discovery call? Just say the word and I'll get you a link."
- Never discuss competitors by name.
- Never make promises about specific results (e.g., "we'll get you to #1 on Google").
- Keep replies under 80 words unless the question genuinely requires detail.
- Sound like a sharp human, not a bot.
""".strip()

_groq_client = None


def _get_groq_client():
    global _groq_client
    if _groq_client is None:
        _groq_client = Groq(api_key=settings.GROQ_API_KEY)
    return _groq_client


@csrf_protect
@require_POST
def chat_view(request):
    """AI Chatbot endpoint — rate-limited, CSRF-protected. Powered by Groq."""
    ip = get_client_ip(request)

    # Rate limit: 20 messages/IP/hour
    rate_key = f"chat_rate_{ip}"
    count = cache.get(rate_key, 0)
    if count >= 20:
        return JsonResponse(
            {"error": "You've reached the chat limit. Email us at hello@digitally.in."},
            status=429,
        )
    cache.set(rate_key, count + 1, timeout=3600)

    try:
        body = json.loads(request.body)
        user_message = body.get("message", "").strip()[:500]
        raw_history = body.get("history", [])

        if not user_message:
            return JsonResponse({"error": "Empty message."}, status=400)

        # Sanitize history — only allow role/content keys, valid roles
        safe_history = [
            {"role": m["role"], "content": str(m["content"])[:1000]}
            for m in raw_history[-8:]
            if m.get("role") in ("user", "assistant") and m.get("content")
        ]

        messages = [
            {"role": "system", "content": SALES_SYSTEM_PROMPT},
            *safe_history,
            {"role": "user", "content": user_message},
        ]

        client = _get_groq_client()
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            max_tokens=200,
            temperature=0.7,
        )
        reply = response.choices[0].message.content
        return JsonResponse({"reply": reply})

    except Exception as e:
        log_failure("chat_view", str(e), {"ip": ip}, exc=e)
        return JsonResponse(
            {"error": "The assistant is temporarily unavailable."},
            status=500,
        )


# ──────────────────────────────────────────────
# FEATURE 3 — "Roast My Site" Tool
# ──────────────────────────────────────────────
@csrf_protect
@require_POST
def roast_view(request):
    """Website roast endpoint — rate-limited, CSRF-protected, SSRF-safe."""
    url = request.POST.get("url", "").strip()
    ip = get_client_ip(request)

    # Rate limit: 3 roasts/IP/hour (DB-tracked for audit)
    one_hour_ago = timezone.now() - timedelta(hours=1)
    recent_count = RoastRequest.objects.filter(
        ip_address=ip, created_at__gte=one_hour_ago
    ).count()
    if recent_count >= 3:
        return HttpResponse(
            '<p class="text-[#FF6B00] text-sm">You\'ve used 3 roasts this hour. '
            "Come back later — or just email us.</p>"
        )

    validator = URLValidator(schemes=["http", "https"])
    try:
        validator(url)
    except ValidationError:
        return HttpResponse(
            '<p class="text-red-400 text-sm">Enter a valid URL (include https://).</p>'
        )

    roast_obj = RoastRequest.objects.create(url=url, ip_address=ip)
    try:
        scraped = scrape_website(url)
        critique_html = roast_website(scraped)
        roast_obj.was_successful = True
        roast_obj.result_preview = critique_html[:200]
        roast_obj.save(update_fields=["was_successful", "result_preview"])

        return HttpResponse(
            f'<div class="bg-[#0A0A0A] border border-white/10 rounded-2xl p-8 text-sm '
            f'text-[#E0E0E0] leading-relaxed roast-output">'
            f'<div class="overflow-x-auto">{critique_html}</div>'
            f'</div>'
        )
    except Exception as e:
        log_failure("roast_view", str(e), {"url": url, "ip": ip}, exc=e)
        return HttpResponse(
            '<p class="text-red-400 text-sm">We couldn\'t reach that site — it may be blocking scrapers. '
            'Try another URL or <a href="#contact" class="text-[#FF6B00] underline">contact us directly</a>.</p>'
        )
