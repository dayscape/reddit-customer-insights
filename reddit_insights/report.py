from datetime import datetime


class ReportGenerator:
    def generate(self, analysis: dict, threads_count: int) -> str:
        """Generate a markdown report from the analysis data."""
        sections = [
            self._header(threads_count),
            self._buying_signals(analysis.get("buying_signals", [])),
            self._pain_points(analysis.get("pain_points", {})),
            self._content_ideas(analysis.get("content_ideas", [])),
            self._competitor_mentions(analysis.get("competitor_mentions", {})),
            self._emerging_themes(analysis.get("emerging_themes", [])),
        ]
        return "\n\n".join(sections)

    def _header(self, threads_count: int) -> str:
        date = datetime.now().strftime("%Y-%m-%d")
        return f"""# Reddit Customer Insights Report
*Generated: {date} | Threads Analyzed: {threads_count}*"""

    def _buying_signals(self, signals: list) -> str:
        lines = ["## 🔥 Buying Signals"]
        if not signals:
            lines.append("*No buying signals detected in this batch.*")
        else:
            for signal in signals:
                title = signal.get("title", "Untitled")
                url = signal.get("url", "#")
                subreddit = signal.get("subreddit", "unknown").removeprefix("r/")
                quote = signal.get("quote", "")
                lines.append(f'- [{title}]({url}) - r/{subreddit} - "{quote}"')
        return "\n".join(lines)

    def _pain_points(self, pain_points: dict) -> str:
        lines = ["## 😤 Pain Points"]
        if not pain_points:
            lines.append("*No specific pain points identified.*")
        else:
            for theme, items in pain_points.items():
                lines.append(f"### {theme}")
                for item in items:
                    title = item.get("title", "Thread")
                    url = item.get("url", "#")
                    quote = item.get("quote", "")
                    lines.append(f'- [{title}]({url}) - "{quote}"')
        return "\n".join(lines)

    def _content_ideas(self, ideas: list) -> str:
        lines = ["## 💡 Content Ideas"]
        if not ideas:
            lines.append("*No content ideas extracted.*")
        else:
            for idea in ideas:
                question = idea.get("question", "")
                potential_title = idea.get("potential_title", "")
                source_url = idea.get("source_url", "#")
                if potential_title:
                    lines.append(f'- **{potential_title}**: "{question}" ([source]({source_url}))')
                else:
                    lines.append(f'- "{question}" ([source]({source_url}))')
        return "\n".join(lines)

    def _competitor_mentions(self, competitors: dict) -> str:
        lines = ["## 🗣️ Competitor Mentions"]
        if not competitors:
            lines.append("*No competitor mentions found.*")
            return "\n".join(lines)

        lines.append("| Tool | Positive | Negative | Neutral |")
        lines.append("|------|----------|----------|---------|")

        for tool, data in competitors.items():
            positive = data.get("positive", 0)
            negative = data.get("negative", 0)
            neutral = data.get("neutral", 0)
            lines.append(f"| {tool} | {positive} | {negative} | {neutral} |")

        lines.append("")
        lines.append("### Notable Quotes")
        for tool, data in competitors.items():
            quotes = data.get("notable_quotes", [])
            if quotes:
                lines.append(f"**{tool}:**")
                for quote in quotes[:3]:
                    lines.append(f'- "{quote}"')

        return "\n".join(lines)

    def _emerging_themes(self, themes: list) -> str:
        lines = ["## 📊 Emerging Themes"]
        if not themes:
            lines.append("*No emerging themes identified.*")
        else:
            for theme in themes:
                name = theme.get("theme", "Unknown")
                description = theme.get("description", "")
                count = theme.get("thread_count", 0)
                lines.append(f"- **{name}** ({count} threads): {description}")
        return "\n".join(lines)

    def save(self, content: str, filepath: str) -> None:
        """Save the report content to a file."""
        with open(filepath, "w") as f:
            f.write(content)
