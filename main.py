#!/usr/bin/env python3
"""Reddit Customer Insights Tool - Extract B2B insights from Reddit discussions."""

import argparse
import sys

from dotenv import load_dotenv

from reddit_insights import RedditScraper, InsightsAnalyzer, ReportGenerator


def main():
    parser = argparse.ArgumentParser(
        description="Scrape Reddit for B2B customer insights and generate analysis reports."
    )
    parser.add_argument(
        "--output", "-o",
        default="insights_report.md",
        help="Output file path for the markdown report (default: insights_report.md)",
    )
    parser.add_argument(
        "--limit", "-l",
        type=int,
        default=10,
        help="Maximum threads to fetch per subreddit/query combination (default: 10)",
    )
    parser.add_argument(
        "--with-comments",
        action="store_true",
        help="Fetch comments for each thread (slower, more API calls)",
    )
    args = parser.parse_args()

    load_dotenv()

    print("Starting Reddit Customer Insights extraction...", file=sys.stderr)

    # Scrape Reddit
    scraper = RedditScraper(fetch_comments=args.with_comments)
    threads = scraper.search_all(limit_per_query=args.limit)

    if not threads:
        print("No threads found. Check your search queries and API credentials.", file=sys.stderr)
        sys.exit(1)

    # Analyze with Claude
    analyzer = InsightsAnalyzer()
    analysis = analyzer.analyze_threads(threads)

    # Generate report
    generator = ReportGenerator()
    report = generator.generate(analysis, len(threads))
    generator.save(report, args.output)

    print(f"Report saved to: {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
