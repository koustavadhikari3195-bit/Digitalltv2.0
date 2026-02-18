from groq import Groq
from django.conf import settings

client = Groq(api_key=settings.GROQ_API_KEY)

ROAST_PROMPT = """
You are a brutally honest but witty digital strategist.
You've been given scraped data from a website. Your job: roast it.

Output FORMAT (strict HTML, no markdown):
<div class="roast-critique">
  <h3>The Verdict: [One punchy sentence summary]</h3>
  <ul>
    <li><strong>SEO:</strong> [Your critique]</li>
    <li><strong>Messaging:</strong> [Your critique]</li>
    <li><strong>Design Signals:</strong> [What the HTML structure implies about design quality]</li>
    <li><strong>CTA Effectiveness:</strong> [Critique]</li>
    <li><strong>First Impression:</strong> [What a visitor thinks in 3 seconds]</li>
  </ul>
</div>
<div class="roast-pivot">
  <p>Here's how we'd fix this:</p>
  <ul>
    <li>[Service 1 that solves a specific problem you just identified]</li>
    <li>[Service 2]</li>
    <li>[Service 3]</li>
  </ul>
</div>

Be specific. Reference actual content from the scrape. Be funny but professional.
Available services to cite: Website Management, Social Media, SEO, Content Marketing, Graphic Design.
Max 250 words total.
""".strip()


def roast_website(scraped_data: dict) -> str:
    """Send scraped website data to Groq (Llama) for a roast critique."""
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": ROAST_PROMPT},
            {"role": "user", "content": str(scraped_data)},
        ],
        max_tokens=500,
        temperature=0.85,
    )
    return response.choices[0].message.content
