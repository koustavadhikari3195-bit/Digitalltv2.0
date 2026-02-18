import socket
import ipaddress
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

PRIVATE_RANGES = [
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("169.254.0.0/16"),  # AWS metadata
    ipaddress.ip_network("::1/128"),
]


def _is_private_ip(hostname: str) -> bool:
    """DNS-resolve hostname and check if it resolves to a private range. Prevents DNS rebinding SSRF."""
    try:
        resolved = socket.getaddrinfo(hostname, None)[0][4][0]
        ip = ipaddress.ip_address(resolved)
        return any(ip in net for net in PRIVATE_RANGES)
    except Exception:
        return True  # Fail closed — if we can't resolve, block it


def scrape_website(url: str) -> dict:
    """Scrape a website and return structured data for the roast engine."""
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise ValueError("Only HTTP/HTTPS URLs are allowed.")
    if _is_private_ip(parsed.hostname):
        raise ValueError("Private/internal URLs are not allowed.")

    resp = requests.get(
        url,
        timeout=8,
        headers={"User-Agent": "DIGITALLY-Roaster/1.0 (+https://digitally.in/roast)"},
        allow_redirects=True,
    )
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    # Remove nav, footer, scripts — get body copy only
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()

    return {
        "title": (soup.title.string or "").strip()[:200] if soup.title else "",
        "meta_desc": (soup.find("meta", attrs={"name": "description"}) or {}).get("content", "")[:300],
        "h1_tags": [h.get_text(strip=True) for h in soup.find_all("h1")[:3]],
        "h2_tags": [h.get_text(strip=True) for h in soup.find_all("h2")[:5]],
        "body_text": soup.get_text(separator=" ", strip=True)[:2000],
        "has_cta": bool(soup.find("button") or soup.find("a", class_=lambda c: c and "cta" in c.lower())),
    }
