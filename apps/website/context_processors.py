"""
Service portfolio data — injected into every template via context processor.
"""

SERVICES = [
    {
        "slug": "website-management",
        "title": "Website Management",
        "tagline": "Your site, always running.",
        "description": (
            "Daily backups, uptime monitoring, SSL management, security patches, "
            "and monthly speed optimization. We own the headache so you don't have to."
        ),
        "deliverables": [
            "Hosting management",
            "Daily automated backups",
            "SSL renewal",
            "Performance audits",
            "Emergency support (24h response)",
        ],
        "starting_from": "₹8,000/month",
        "icon": "server",
    },
    {
        "slug": "social-media",
        "title": "Social Media",
        "tagline": "15–20 posts/month. Zero effort from you.",
        "description": (
            "Content strategy, copywriting, graphic creation, scheduling, and analytics "
            "across Instagram, LinkedIn, and Twitter/X. Consistent brand voice, always on."
        ),
        "deliverables": [
            "15–20 original posts/month",
            "Platform-native copywriting",
            "Branded graphics",
            "Scheduling & posting",
            "Monthly analytics report",
        ],
        "starting_from": "₹12,000/month",
        "icon": "social",
    },
    {
        "slug": "seo",
        "title": "SEO",
        "tagline": "Rank. Be found. Grow.",
        "description": (
            "Technical SEO audits, on-page optimization, Google My Business management, "
            "and backlink outreach — all reported monthly with plain-English results."
        ),
        "deliverables": [
            "Technical SEO audit",
            "On-page optimization",
            "GMB management",
            "Backlink outreach",
            "Monthly rank tracking report",
        ],
        "starting_from": "₹10,000/month",
        "icon": "search",
    },
    {
        "slug": "content-marketing",
        "title": "Content Marketing",
        "tagline": "Words that work while you sleep.",
        "description": (
            "4 SEO-optimized blog posts/month, biweekly email newsletters, and a "
            "full content calendar so you're never scrambling for ideas."
        ),
        "deliverables": [
            "4 blog posts/month",
            "Biweekly email newsletter",
            "Content calendar",
            "Topic research",
            "Internal linking strategy",
        ],
        "starting_from": "₹15,000/month",
        "icon": "document",
    },
    {
        "slug": "graphic-design",
        "title": "Graphic Design",
        "tagline": "Brand identity that stops the scroll.",
        "description": (
            "Logos, brand guidelines, social templates, pitch decks, and marketing "
            "collateral. One designer. Your brand. Total consistency."
        ),
        "deliverables": [
            "Logo & brand identity",
            "Social media templates",
            "Pitch deck design",
            "Marketing collateral",
            "Brand guidelines doc",
        ],
        "starting_from": "₹5,000/project",
        "icon": "design",
    },
]


def services_context(request):
    """Inject the service catalog into every template context."""

def contact_form_context(request):
    """Provides metadata for the 3-step project inquiry form."""
    return {
        "step_labels": [(1, "About You"), (2, "Your Goals"), (3, "Scope & Budget")],
        "service_options": [
            ("website_management", "🖥", "Website Management"),
            ("social_media", "📣", "Social Media"),
            ("seo", "🔍", "SEO"),
            ("content_marketing", "✍️", "Content Marketing"),
            ("graphic_design", "🎨", "Graphic Design"),
            ("full_package", "⭐", "Full Package"),
        ],
        "contact_alternates": [
            ("📧", "Email Us", "hello@digitally.in", "mailto:hello@digitally.in"),
            ("💬", "WhatsApp", "Quick conversations", "https://wa.me/919999999999"),
            ("📅", "Book a Call", "15-min discovery call", "https://cal.com/digitally"),
        ],
    }
