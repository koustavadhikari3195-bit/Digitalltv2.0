import yfinance as yf
from django.core.cache import cache
from django.http import HttpResponse
from django.views.decorators.http import require_GET
from django.conf import settings
from datetime import datetime
from apps.ai_agents.utils.logger import log_failure

import requests


@require_GET
def live_widgets(request):
    """Command Center data strip — serves weather, time, and market data."""
    if request.headers.get("X-Widget-Client") != "1":
        return HttpResponse(status=403)

    lat = request.GET.get("lat", "").strip()
    lon = request.GET.get("lon", "").strip()
    has_geo = bool(lat and lon)

    parts = [_get_time(), _get_weather(lat, lon) if has_geo else _get_fallback_weather()]

    if not has_geo:
        parts.append(_get_nifty())
        parts.append(_get_nasdaq())

    html = " &nbsp;·&nbsp; ".join(p for p in parts if p)
    return HttpResponse(f'<div class="flex items-center gap-0 whitespace-nowrap">{html}</div>')


def _get_time():
    now = datetime.utcnow()
    return f'<span>🕐 UTC {now.strftime("%H:%M")}</span>'


def _get_weather(lat, lon):
    cache_key = f"weather_{float(lat):.2f}_{float(lon):.2f}"
    cached = cache.get(cache_key)
    if cached:
        return cached
    try:
        r = requests.get(
            "https://api.openweathermap.org/data/2.5/weather",
            params={"lat": lat, "lon": lon, "appid": settings.WEATHER_API_KEY, "units": "metric"},
            timeout=3,
        )
        r.raise_for_status()
        d = r.json()
        result = (
            f'<span>🌡 {d["main"]["temp"]:.0f}°C &nbsp; '
            f'{d["weather"][0]["description"].title()} — {d["name"]}</span>'
        )
        cache.set(cache_key, result, 300)  # 5 min cache
        return result
    except Exception as e:
        log_failure("widget_weather", str(e), {"lat": lat, "lon": lon})
        return ""


def _get_fallback_weather():
    return '<span>🌍 Global Mode — location not shared</span>'


def _get_nifty():
    """Fetch Nifty Bank data using yfinance library."""
    cache_key = "nifty_50"
    cached = cache.get(cache_key)
    if cached:
        return cached
    try:
        ticker = yf.Ticker("^NSEBANK")
        info = ticker.fast_info
        price = info.last_price
        prev = info.previous_close
        change = ((price - prev) / prev) * 100
        color = "text-green-400" if change >= 0 else "text-red-400"
        arrow = "▲" if change >= 0 else "▼"
        result = (
            f'<span>NIFTY BANK: <span class="{color}">'
            f'{price:,.0f} {arrow} {abs(change):.2f}%</span></span>'
        )
        cache.set(cache_key, result, 180)
        return result
    except Exception as e:
        log_failure("widget_nifty", str(e), {})
        return '<span>NIFTY BANK: <span class="text-[#A0A0A0]">—</span></span>'


def _get_nasdaq():
    """Fetch NASDAQ Composite data using yfinance library."""
    cache_key = "nasdaq_comp"
    cached = cache.get(cache_key)
    if cached:
        return cached
    try:
        ticker = yf.Ticker("^IXIC")
        info = ticker.fast_info
        price = info.last_price
        prev = info.previous_close
        change = ((price - prev) / prev) * 100
        color = "text-green-400" if change >= 0 else "text-red-400"
        arrow = "▲" if change >= 0 else "▼"
        result = (
            f'<span>NASDAQ: <span class="{color}">'
            f'{price:,.0f} {arrow} {abs(change):.2f}%</span></span>'
        )
        cache.set(cache_key, result, 180)
        return result
    except Exception as e:
        log_failure("widget_nasdaq", str(e), {})
        return ""
