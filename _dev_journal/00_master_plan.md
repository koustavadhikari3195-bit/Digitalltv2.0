# 00 — Master Plan

## DIGITALLY v2 — Production Build Plan

### Project Vision
Premium digital agency website with integrated AI tools (chatbot, website roaster),
live data dashboard, and smart lead capture — all built as a single Django monolith.

### Architecture
- **Framework:** Django 4.2 with split settings (base/dev/prod)
- **Frontend:** HTMX for reactive partials, Tailwind CSS for styling, self-hosted fonts (Syne + DM Sans)
- **AI:** OpenAI GPT-4o for chatbot and website roaster
- **Data:** PostgreSQL (Supabase) for production, SQLite for dev
- **Caching:** Django LocMemCache (dev), Redis (prod)

### Apps
1. `apps/website` — Landing page, lead capture, portfolio
2. `apps/ai_agents` — Roaster + Chatbot AI endpoints  
3. `apps/widgets` — Command Center live data strip

### Features (8 total)
1. Gatekeeper Modal — Skippable lead popup, fires once after 4s
2. AI Sales Director — Floating chatbot with service catalog knowledge
3. Roast My Site — URL → scrape → GPT critique → service pivot
4. Command Center — Live weather/market data strip
5. Service Portfolio — 5 service pillars with pricing
6. Error Log — Auto-logging failures to dev journal
7. QA Critique Log — Decision documentation
8. Tech Debt Tracker — Deferred fixes with priority/effort

### Build Order
Follow the execution checklist in the master prompt — scaffold first, then models,
then templates, then views, then polish.

---

*Written before any code. This document is the source of truth for project direction.*
