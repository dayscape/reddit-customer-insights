import json
import os
import sys
from typing import List

import anthropic


ANALYSIS_PROMPT = """You are analyzing Reddit threads to extract B2B customer insights for a company in the website visitor identification space (similar to RB2B, Clearbit Reveal, 6sense, Demandbase).

Analyze the following Reddit threads and extract insights in these categories:

1. **buying_signals**: Threads where someone is actively looking to buy, evaluate, or switch visitor identification/intent data tools. Include the thread title, URL, subreddit, and a key quote showing buying intent.

2. **pain_points**: Complaints, frustrations, or problems people mention about existing tools or the general challenge of identifying website visitors. Group by theme (e.g., "Data Accuracy Issues", "Pricing Concerns", "Integration Problems").

3. **content_ideas**: Questions people are asking that could be turned into blog posts, guides, or marketing content. These are educational opportunities.

4. **competitor_mentions**: Track mentions of competitors (RB2B, Clearbit, 6sense, Demandbase, ZoomInfo, Leadfeeder, etc.) with sentiment analysis. For each competitor, count positive, negative, and neutral mentions.

5. **emerging_themes**: Broader trends or patterns you notice across multiple threads - what topics keep coming up? What's the general sentiment about visitor identification tools?

Return your analysis as valid JSON with this structure:
{
  "buying_signals": [
    {"title": "...", "url": "...", "subreddit": "...", "quote": "..."}
  ],
  "pain_points": {
    "Theme Name": [
      {"title": "...", "url": "...", "quote": "..."}
    ]
  },
  "content_ideas": [
    {"question": "...", "source_url": "...", "potential_title": "..."}
  ],
  "competitor_mentions": {
    "Competitor Name": {"positive": 0, "negative": 0, "neutral": 0, "notable_quotes": ["..."]}
  },
  "emerging_themes": [
    {"theme": "...", "description": "...", "thread_count": 0}
  ]
}

Here are the threads to analyze:

"""


class InsightsAnalyzer:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    def analyze_threads(self, threads: List[dict]) -> dict:
        """Analyze threads using Claude and return structured insights."""
        if not threads:
            return self._empty_analysis()

        print(f"Analyzing {len(threads)} threads with Claude...", file=sys.stderr)

        threads_text = self._format_threads_for_analysis(threads)
        prompt = ANALYSIS_PROMPT + threads_text

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4096,
                messages=[{"role": "user", "content": prompt}],
            )

            response_text = response.content[0].text
            analysis = self._parse_response(response_text)
            return analysis

        except Exception as e:
            print(f"Error during Claude analysis: {e}", file=sys.stderr)
            return self._empty_analysis()

    def _format_threads_for_analysis(self, threads: List[dict]) -> str:
        """Format threads into a readable text block for Claude."""
        formatted = []
        for i, thread in enumerate(threads, 1):
            comments_text = "\n".join(f"  - {c[:500]}..." if len(c) > 500 else f"  - {c}" for c in thread["comments"][:5])
            formatted.append(f"""
--- Thread {i} ---
Title: {thread['title']}
Subreddit: r/{thread['subreddit']}
URL: {thread['url']}
Upvotes: {thread['upvotes']}
Date: {thread['created_utc']}

Body:
{thread['body'][:2000]}{'...' if len(thread['body']) > 2000 else ''}

Top Comments:
{comments_text}
""")
        return "\n".join(formatted)

    def _parse_response(self, response_text: str) -> dict:
        """Parse Claude's JSON response."""
        try:
            start = response_text.find("{")
            end = response_text.rfind("}") + 1
            if start != -1 and end > start:
                json_str = response_text[start:end]
                return json.loads(json_str)
        except json.JSONDecodeError as e:
            print(f"Failed to parse Claude response as JSON: {e}", file=sys.stderr)

        return self._empty_analysis()

    def _empty_analysis(self) -> dict:
        """Return an empty analysis structure."""
        return {
            "buying_signals": [],
            "pain_points": {},
            "content_ideas": [],
            "competitor_mentions": {},
            "emerging_themes": [],
        }
