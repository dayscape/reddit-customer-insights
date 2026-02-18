# Reddit Customer Insights Tool

96% of B2B website visitors leave without converting. They browse your pricing page, read case studies, and disappear forever. What if you could understand what these buyers are actually thinking?

Reddit is where your potential customers discuss their real pain points, evaluate tools like yours, and share unfiltered opinions about competitors. This tool scrapes those conversations and uses Claude AI to extract actionable insights for B2B SaaS companies in the website visitor identification space.

## What It Does

- **Scrapes targeted subreddits** (r/sales, r/b2bmarketing, r/SaaS, etc.) for discussions about visitor identification, intent data, and lead enrichment
- **Analyzes threads with Claude** to extract structured insights
- **Generates markdown reports** with:
  - Buying signals (people actively looking for solutions)
  - Pain points (grouped by theme)
  - Content ideas (questions that could become blog posts)
  - Competitor sentiment analysis
  - Emerging industry themes

## Quick Start

1. **Clone and install dependencies**
   ```bash
   cd reddit-customer-insights
   pip install -r requirements.txt
   ```

2. **Configure API credentials**
   ```bash
   cp .env.example .env
   ```

   Edit `.env` with your Anthropic API key:
   ```
   ANTHROPIC_API_KEY=your_key_here
   ```

   Get your key from https://console.anthropic.com

3. **Run the tool**
   ```bash
   python main.py --output report.md --limit 5
   ```

## Configuration

### CLI Options

| Option | Default | Description |
|--------|---------|-------------|
| `--output`, `-o` | `insights_report.md` | Output file path |
| `--limit`, `-l` | `10` | Max threads per subreddit/query combo |
| `--with-comments` | disabled | Fetch comments for each thread (slower) |

### Customizing Searches

Edit `reddit_insights/config.py` to modify:
- `TARGET_SUBREDDITS`: Which subreddits to search
- `SEARCH_QUERIES`: What terms to search for
- `TIME_FILTER`: How far back to search (hour, day, week, month, year, all)

## Sample Output

See [sample_output.md](sample_output.md) for an example of what the generated report looks like.

## How It Works

1. **Scraping**: Uses Reddit's public JSON API to search configured subreddits with relevant queries. Includes rate limiting (3s between requests) with exponential backoff for reliability. Deduplicates threads that match multiple queries.

2. **Analysis**: Sends all thread content to Claude in a single batch request. Claude extracts structured insights following a detailed prompt template.

3. **Reporting**: Transforms Claude's JSON response into a readable markdown report with proper formatting, links, and tables.

## Requirements

- Python 3.9+
- Anthropic API key (usage-based pricing)

No Reddit API credentials required - uses Reddit's public JSON endpoints.

## Cost Estimate

A typical run analyzing ~300 threads uses approximately 30-50K input tokens and 3-5K output tokens with Claude Sonnet, costing roughly $0.10-0.20 per run.
