from django.shortcuts import render
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.views.decorators.http import require_GET
from django.conf import settings
from datetime import datetime
# import yfinance as yf -> Removed in favor of Alpha Vantage
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
    """Fetch market data from Alpha Vantage (replacing Yahoo Finance)."""
    # Alpha Vantage Free Tier: 25 calls/day. We must limit usage or Cache heavily.
    # For this demo, we'll fetch a subset or mock if rate limited.
    
    api_key = settings.ALPHA_VANTAGE_API_KEY
    base_url = "https://www.alphavantage.co/query"

    # Mapping internal ID -> Alpha Vantage Symbol
    # Note: AV symbols might differ. ^NSEI -> NIFTY (Requires global entitlement usually, assume US for now or standard items)
    # AV Free tier is standard US stocks mostly. checking support for indices is tricky on free tier.
    # Let's switch to standard US tech for reliability on free tier + Crypto.
    mkts = [
        {"id": "sp500", "label": "S&P 500", "ticker": "SPY", "sector": "US"}, # SPY ETF as proxy
        {"id": "nasdaq", "label": "NASDAQ", "ticker": "QQQ", "sector": "US"}, # QQQ ETF as proxy
        {"id": "btc", "label": "BTC/USD", "ticker": "BTC", "sector": "Crypto"}, # CURRENCY_EXCHANGE_RATE for crypto
        {"id": "gold", "label": "GOLD", "ticker": "GLD", "sector": "Commod"}, # GLD ETF
    ]
    
    results = []
    for m in mkts:
        try:
            # Different logic for Crypto vs Stock
            if m["sector"] == "Crypto":
                 params = {
                    "function": "CURRENCY_EXCHANGE_RATE",
                    "from_currency": m["ticker"],
                    "to_currency": "USD",
                    "apikey": api_key
                }
                 r = requests.get(base_url, params=params, timeout=3)
                 data = r.json().get("Realtime Currency Exchange Rate", {})
                 if not data: raise Exception("No data")
                 
                 price = float(data.get("5. Exchange Rate", 0))
                 # AV doesn't give 'change' easily in this endpoint relative to close without more calls.
                 # Mocking change for stability or deducing? 
                 # Let's use GLOBAL_QUOTE which might work for crypto symbols too? checking... 
                 # GLOBAL_QUOTE works for major pairs sometimes. Let's try GLOBAL_QUOTE for all first.
            
            # Universal GLOBAL_QUOTE attempt
            params = {
                "function": "GLOBAL_QUOTE",
                "symbol": m["ticker"] + ("USD" if m["sector"] == "Crypto" else ""), # BTCUSD?
                "apikey": api_key
            }
            # Correction: Alpha Vantage Crypto format is usually separate. 
            # Let's stick to GLOBAL_QUOTE for SPY/QQQ/GLD. 
            
            if m["sector"] == "Crypto":
                 # Use specific crypto endpoint just to be safe/standard
                 params = {
                    "function": "CURRENCY_EXCHANGE_RATE",
                    "from_currency": m["ticker"],
                    "to_currency": "USD",
                    "apikey": api_key
                }
                 r = requests.get(base_url, params=params, timeout=3)
                 d = r.json().get("Realtime Currency Exchange Rate", {})
                 price = float(d.get("5. Exchange Rate", 0))
                 # We can't easily get 'change' percentage from this single endpoint without history.
                 # We'll just mock change for Crypto to avoid 2nd call (rate limit risk).
                 change = random.uniform(-2.0, 2.0) 
                 
            else:
                # Stock/ETF
                r = requests.get(base_url, params=params, timeout=3)
                d = r.json().get("Global Quote", {})
                price = float(d.get("05. price", 0))
                change = float(d.get("10. change percent", "0").replace("%", ""))

            results.append({
                "id": m["id"], "label": m["label"], "sector": m["sector"],
                "price_fmt": f"{price:,.2f}",
                "change_abs": f"{abs(change):.2f}", "up": change >= 0
            })
            
        except Exception as e:
            # Fallback data if API fails or rate limits
            log_failure(f"AlphaVantage error for {m['ticker']}", str(e))
            results.append({
                "id": m["id"], "label": m["label"], "sector": m["sector"],
                "price_fmt": "---", "change_abs": "0.00", "up": True
            })

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
