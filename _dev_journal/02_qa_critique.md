# 02 — QA & Argumentation Log

This is where the developer argues with themselves about decisions made under pressure.
It's honest. It's messy. That's the point.

---

## [Entry 1] — Gatekeeper Modal Timing
**Date:** 2026-02-18
**Decision:** Set popup delay to 4000ms instead of 2000ms.
**Why:** At 2 seconds, it fires before the hero headline finishes loading. Users instinctively close things
that interrupt initial scan. 4 seconds gives them one full read of the headline.
**Regret level:** 2/10. Could A/B test it. Won't for MVP.

---

## [Entry 2] — Chatbot History: Last 8 Turns Only
**Date:** 2026-02-18
**Decision:** Only pass the last 8 conversation turns to GPT-4o.
**Why:** Token cost. 20-turn context at GPT-4o rates adds up fast. 8 turns is enough for
most sales conversations — if someone has been chatting for 10+ turns they're already sold or gone.
**Risk:** If a user references something from turn 1 in turn 12, the bot may seem forgetful.
**Deferred fix:** Summarize old turns instead of truncating. See 03_deferred_fixes.md.

---

## [Entry 3] — Yahoo Finance for Market Data
**Date:** 2026-02-18
**Decision:** Using Yahoo Finance's unofficial API endpoint for Nifty 50 / NASDAQ data.
**Why:** NSE's official API requires registration and has rate limits. Yahoo works now.
**Risk:** Yahoo can break this endpoint without notice. It has broken it before.
**Deferred fix:** Subscribe to a proper financial data provider (Alpha Vantage, Polygon.io). Budget: ~$30/month.

---

## [Entry 4] — Supabase Connection Security
**Date:** 2026-02-18
**ssl_require=True** is set. TLS enforced. Good.
**conn_max_age=600** — fine for MVP, but under traffic spikes, Supabase's default 100-connection limit
will be exhausted. Mitigation: enable Supabase's PgBouncer session-mode pooler. Not done yet.
**Deferred fix:** Switch DATABASE_URL to the pooler endpoint before any marketing push.

---

## [Entry 5] — Widget Strip Performance Impact
**Date:** 2026-02-18
**Decision:** Keeping the Command Center strip despite it adding ~200–350ms server latency.
**Why:** The client asked for "live data." Also: it genuinely proves real-time integration capability.
**Mitigation implemented:** 5-minute cache on weather data, 3-minute cache on market data.
**Residual cost:** Cold cache = ~350ms extra TTFB. Acceptable given async HTMX load.
**I hate it a little.** But I respect the requirement.
