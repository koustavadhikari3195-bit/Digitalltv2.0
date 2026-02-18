from django.shortcuts import render
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.views.decorators.http import require_GET
from django.conf import settings
from datetime import datetime
import yfinance as yf
import requests
import random
from apps.ai_agents.utils.logger import log_failure

@require_GET
def live_widgets(request):
    """Command Center data strip — serves high-fidelity ticker and panel data via OOB."""
    lat = request.GET.get("lat", "").strip()
    lon = request.GET.get("lon", "").strip()
    has_geo = bool(lat and lon)

    # 1. Fetch Data
    market_items = _get_market_items()
    weather_data = _get_weather_data(lat, lon) if has_geo else _get_fallback_weather_data()
    intel_data = _get_intel_data()

    # 2. Render Fragments
    ticker_html = _render_ticker_string(market_items)
    market_grid_html = render_to_string("partials/_command_market_grid.html", {"mkts": market_items})
    weather_big_html = render_to_string("partials/_command_weather_big.html", {"weather": weather_data})
    intel_grid_html = render_to_string("partials/_command_intel_grid.html", {"intel": intel_data})

    # 3. Construct OOB Response
    # This updates the ticker in-place AND swaps other components OOB
    response_html = f"""
    {ticker_html}
    <div id="panel-market-grid" hx-swap-oob="innerHTML">{market_grid_html}</div>
    <div id="panel-weather-big" hx-swap-oob="innerHTML">{weather_big_html}</div>
    <div id="panel-intel-grid" hx-swap-oob="innerHTML">{intel_grid_html}</div>
    
    <span id="bar-weather-icon" hx-swap-oob="innerHTML">{weather_data['icon_emoji']}</span>
    <span id="bar-weather-temp" hx-swap-oob="innerHTML">{weather_data['temp']}</span>
    <div id="bar-weather-desc" hx-swap-oob="innerHTML">{weather_data['description']}</div>
    """
    
    # Also update city if it's not the fallback
    if has_geo:
        response_html += f'<span id="bar-weather-city" hx-swap-oob="innerHTML">{weather_data["city"]}</span>'

    return HttpResponse(response_html)

def _get_market_items():
    # ... same as before but ensured ...
    mkts = [
        {"id": "nifty50", "label": "NIFTY 50", "ticker": "^NSEI", "sector": "India"},
        {"id": "niftybank", "label": "NIFTY BANK", "ticker": "^NSEBANK", "sector": "India"},
        {"id": "sensex", "label": "SENSEX", "ticker": "^BSESN", "sector": "India"},
        {"id": "nasdaq", "label": "NASDAQ", "ticker": "^IXIC", "sector": "US"},
        {"id": "sp500", "label": "S&P 500", "ticker": "^GSPC", "sector": "US"},
        {"id": "gold", "label": "GOLD", "ticker": "GC=F", "sector": "Commod"},
        {"id": "btc", "label": "BTC/USD", "ticker": "BTC-USD", "sector": "Crypto"},
    ]
    results = []
    for m in mkts:
        try:
            t = yf.Ticker(m["ticker"])
            info = t.fast_info
            price = info.last_price
            prev = info.previous_close
            change = ((price - prev) / prev) * 100
            results.append({
                "id": m["id"], "label": m["label"], "sector": m["sector"],
                "price_fmt": f"{price:,.2f}" if price < 100 else f"{price:,.0f}",
                "change_abs": f"{abs(change):.2f}", "up": change >= 0
            })
        except:
            results.append({"id": m["id"], "label": m["label"], "sector": m["sector"], "price_fmt": "---", "change_abs": "0.00", "up": True})
    return results

def _render_ticker_string(items):
    html = ""
    for _ in range(2):
        for m in items:
            color = "text-green-400" if m["up"] else "text-red-400"
            arrow = "▲" if m["up"] else "▼"
            html += f"""
            <span class="inline-flex items-center gap-1.5 px-6 border-r border-white/5 text-[11px] tracking-wide">
              <span class="text-[#666] uppercase">{m['label']}</span>
              <span class="text-[#ddd] font-medium">{m['price_fmt']}</span>
              <span class="{color} flex items-center gap-0.5 font-bold">
                <svg width="8" height="8" viewBox="0 0 10 10" fill="none"><path d="{'M5 1 L9 7 L1 7 Z' if m['up'] else 'M5 9 L9 3 L1 3 Z'}" fill="currentColor"/></svg>
                {m['change_abs']}%
              </span>
            </span>
            """
    return html

def _get_weather_data(lat, lon):
    try:
        r = requests.get("https://api.openweathermap.org/data/2.5/weather",
                         params={"lat": lat, "lon": lon, "appid": settings.WEATHER_API_KEY, "units": "metric"}, timeout=3)
        r.raise_for_status()
        d = r.json()
        return {"city": d["name"], "country": d["sys"]["country"], "temp": round(d["main"]["temp"]), "feels_like": round(d["main"]["feels_like"]),
                "description": d["weather"][0]["description"].title(), "humidity": d["main"]["humidity"], "wind_speed": d["wind"]["speed"],
                "icon_emoji": _get_weather_emoji(d["weather"][0]["id"])}
    except: return _get_fallback_weather_data()

def _get_fallback_weather_data():
    return {"city": "Mumbai", "country": "IN", "temp": 31, "feels_like": 34, "description": "Partly Cloudy", "humidity": 72, "wind_speed": 14, "icon_emoji": "⛅", "uv_index": 8}

def _get_weather_emoji(code):
    if 200 <= code < 300: return "⛈"
    if 300 <= code < 400: return "🌧"
    if 500 <= code < 600: return "🌦"
    if 600 <= code < 700: return "❄"
    if 700 <= code < 800: return "🌫"
    if code == 800: return "☀️"
    return "⛅"

def _get_intel_data():
    sentiment = random.randint(65, 85)
    return {"sentiment": sentiment, "sentiment_dash": int(sentiment / 100 * 251), "neutral": 15, "bearish": 100 - sentiment - 15,
            "movers": [{"symbol": "RELIANCE", "exchange": "NSE", "change": "3.2", "up": True}, {"symbol": "TCS", "exchange": "NSE", "change": "2.1", "up": True},
                       {"symbol": "WIPRO", "exchange": "NSE", "change": "1.4", "up": False}, {"symbol": "INFY", "exchange": "NSE", "change": "1.8", "up": True}],
            "pulse": [{"time": "2m ago", "text": "RBI holds repo rate at 6.5% — market rallies"}, {"time": "11m ago", "text": "IT sector outperforms; TCS leads with strong Q4 guidance"},
                      {"time": "34m ago", "text": "Crude oil dips on demand concerns"}]}
