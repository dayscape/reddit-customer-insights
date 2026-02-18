import sys
import time
from datetime import datetime
from typing import List, Optional, Union

import requests

from .config import (
    TARGET_SUBREDDITS,
    SEARCH_QUERIES,
    MAX_THREADS_PER_QUERY,
    MAX_COMMENTS_PER_THREAD,
    TIME_FILTER,
    SORT_BY,
)

# Rate limiting: 1 request per 3 seconds base delay
REQUEST_DELAY = 3.0
MAX_RETRIES = 3

HEADERS = {
    "User-Agent": "CustomerInsightsBot/1.0 (Educational research tool)"
}


class RedditScraper:
    def __init__(self, fetch_comments: bool = False):
        """Initialize scraper. Set fetch_comments=True to fetch comments (slower, more rate limits)."""
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.last_request_time = 0
        self.fetch_comments = fetch_comments

    def _rate_limit(self, extra_delay: float = 0):
        """Enforce rate limiting between requests."""
        delay = REQUEST_DELAY + extra_delay
        elapsed = time.time() - self.last_request_time
        if elapsed < delay:
            time.sleep(delay - elapsed)
        self.last_request_time = time.time()

    def _make_request(self, url: str, retry_count: int = 0) -> Optional[Union[dict, list]]:
        """Make a rate-limited request to Reddit's JSON API with exponential backoff."""
        # Exponential backoff on retries
        extra_delay = (2 ** retry_count - 1) * 2 if retry_count > 0 else 0
        self._rate_limit(extra_delay)

        try:
            response = self.session.get(url, timeout=15)

            # Handle rate limiting with retry
            if response.status_code == 429:
                if retry_count < MAX_RETRIES:
                    wait_time = (2 ** (retry_count + 1)) * 2
                    print(f"Rate limited, waiting {wait_time}s before retry...", file=sys.stderr)
                    time.sleep(wait_time)
                    return self._make_request(url, retry_count + 1)
                else:
                    print(f"Max retries exceeded for: {url}", file=sys.stderr)
                    return None

            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Request error: {e}", file=sys.stderr)
            return None

    def search_subreddit(self, subreddit_name: str, query: str, limit: int = MAX_THREADS_PER_QUERY) -> List[dict]:
        """Search a single subreddit for threads matching the query."""
        threads = []

        # Build search URL
        encoded_query = requests.utils.quote(query)
        url = (
            f"https://www.reddit.com/r/{subreddit_name}/search.json"
            f"?q={encoded_query}&sort={SORT_BY}&t={TIME_FILTER}&limit={limit}&restrict_sr=1"
        )

        data = self._make_request(url)
        if not data or not isinstance(data, dict):
            return threads

        try:
            posts = data.get("data", {}).get("children", [])
            for post in posts:
                post_data = post.get("data", {})
                thread_data = self.extract_thread_data(post_data)
                if thread_data:
                    threads.append(thread_data)
        except Exception as e:
            print(f"Error parsing r/{subreddit_name} for '{query}': {e}", file=sys.stderr)

        return threads

    def extract_thread_data(self, post_data: dict) -> Optional[dict]:
        """Extract relevant data from a Reddit post."""
        selftext = post_data.get("selftext", "")
        if selftext in ("[removed]", "[deleted]"):
            return None

        permalink = post_data.get("permalink", "")
        created_utc = post_data.get("created_utc", 0)

        # Only fetch comments if enabled (reduces API calls significantly)
        comments = []
        if self.fetch_comments:
            comments = self._fetch_comments(permalink)

        return {
            "id": post_data.get("id", ""),
            "title": post_data.get("title", ""),
            "body": selftext,
            "subreddit": post_data.get("subreddit", ""),
            "url": f"https://reddit.com{permalink}",
            "upvotes": post_data.get("score", 0),
            "created_utc": datetime.utcfromtimestamp(created_utc).isoformat() if created_utc else "",
            "num_comments": post_data.get("num_comments", 0),
            "comments": comments,
        }

    def _fetch_comments(self, permalink: str) -> List[str]:
        """Fetch top comments for a thread."""
        if not permalink:
            return []

        url = f"https://www.reddit.com{permalink}.json?limit={MAX_COMMENTS_PER_THREAD}&sort=best"
        data = self._make_request(url)

        if not data or not isinstance(data, list) or len(data) < 2:
            return []

        comments = []
        try:
            comment_listing = data[1].get("data", {}).get("children", [])
            for comment in comment_listing[:MAX_COMMENTS_PER_THREAD]:
                if comment.get("kind") != "t1":
                    continue
                body = comment.get("data", {}).get("body", "")
                if body and body not in ("[removed]", "[deleted]"):
                    comments.append(body)
        except Exception as e:
            print(f"Error fetching comments: {e}", file=sys.stderr)

        return comments

    def search_all(self, limit_per_query: int = MAX_THREADS_PER_QUERY) -> List[dict]:
        """Search all configured subreddits with all queries, deduplicating by thread ID."""
        seen_ids = set()
        all_threads = []
        total_searches = len(TARGET_SUBREDDITS) * len(SEARCH_QUERIES)
        current = 0

        for subreddit in TARGET_SUBREDDITS:
            for query in SEARCH_QUERIES:
                current += 1
                print(f"[{current}/{total_searches}] Searching r/{subreddit} for '{query}'...", file=sys.stderr)
                threads = self.search_subreddit(subreddit, query, limit_per_query)

                for thread in threads:
                    if thread["id"] not in seen_ids:
                        seen_ids.add(thread["id"])
                        all_threads.append(thread)

        print(f"Found {len(all_threads)} unique threads", file=sys.stderr)
        return all_threads
