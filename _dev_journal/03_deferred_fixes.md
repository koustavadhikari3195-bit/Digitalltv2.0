# 03 — Deferred Fixes (Technical Debt Tracker)

Items intentionally skipped during the build sprint. Each has a PRIORITY and ESTIMATED EFFORT.

---

| # | Item | Why Deferred | Priority | Est. Effort |
|---|------|-------------|----------|-------------|
| 1 | Supabase PgBouncer pooler | Fine for MVP traffic. Must fix before launch. | 🔴 HIGH | 30min |
| 2 | Tailwind CSS purge/minify pipeline | Dev builds are ~3MB. Must add `npx tailwindcss --minify` to deploy script. | 🔴 HIGH | 1hr |
| 3 | Chatbot history summarization | Currently truncates at 8 turns. Should summarize instead. | 🟡 MED | 3hr |
| 4 | Mobile responsiveness: Roast result table | Overflow on screens <375px. Add horizontal scroll wrapper. | 🟡 MED | 30min |
| 5 | DNS rebinding SSRF mitigation | Scraper resolves hostname before request — good. But doesn't handle slow DNS rebinding attacks. Add socket-level IP check post-resolve. | 🟡 MED | 2hr |
| 6 | Replace Yahoo Finance with real API | Yahoo endpoint is unofficial and fragile. Subscribe to Alpha Vantage or Polygon.io. | 🟡 MED | 2hr |
| 7 | GDPR-compliant IP storage | IPs stored on Lead model. Need privacy policy disclosure and opt-out or hash IPs at rest. | 🟠 MED-HIGH | 1hr |
| 8 | Email verification on lead capture | Currently stores any email that passes format check. Add double opt-in or at least MX lookup validation. | 🟡 MED | 3hr |
| 9 | Service Worker + offline fallback | Hero section should render offline. Currently blank on no-connection. | 🟢 LOW | 4hr |
| 10 | Admin rate-limit dashboard | django-axes protects the site but there's no UI to review lockouts. Build a simple admin view. | 🟢 LOW | 2hr |

---

**Ground rule:** Nothing gets removed from this list without either a fix commit or a conscious decision to accept the risk.
