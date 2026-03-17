"""
Tavily web search tool — real-time intelligence across 5 research dimensions.

Runs targeted searches for:
  1. Analyst upgrades / downgrades / price target changes
  2. Earnings surprises, guidance revisions, revenue beats/misses
  3. Insider buying/selling (SEC Form 4)
  4. Regulatory, legal, and macro risk headlines
  5. Competitive landscape and industry trends

Requires: pip install tavily-python
Set env var: TAVILY_API_KEY
"""
import os
from datetime import datetime


def _client():
    api_key = os.environ.get("TAVILY_API_KEY", "")
    if not api_key:
        return None
    try:
        from tavily import TavilyClient
        return TavilyClient(api_key=api_key)
    except ImportError:
        return None


def _search(client, query: str, max_results: int = 4) -> list[dict]:
    """Run a single Tavily search, return cleaned result list."""
    try:
        raw = client.search(
            query,
            max_results=max_results,
            search_depth="advanced",   # deeper extraction
            include_answer=False,
        )
        results = []
        for r in raw.get("results", []):
            results.append({
                "title": r.get("title", "").strip(),
                "url": r.get("url", ""),
                "content": r.get("content", "")[:400].strip(),
                "published": (r.get("published_date") or "")[:10],
                "score": round(r.get("score", 0), 3),
            })
        # Sort by relevance score descending
        return sorted(results, key=lambda x: x["score"], reverse=True)
    except Exception:
        return []


def get_stock_intelligence(ticker: str, company_name: str = "") -> dict:
    """
    Run 5 targeted searches and return structured intelligence dict.

    Keys: analyst, earnings, insider, risk, competitive
    Each value: list of {title, url, content, published, score}
    """
    client = _client()
    if not client:
        return {"error": "TAVILY_API_KEY not set or tavily-python not installed"}

    name = company_name or ticker
    year = datetime.now().year

    queries = {
        "analyst": (
            f"{ticker} {name} analyst upgrade downgrade price target raised lowered {year}",
            4,
        ),
        "earnings": (
            f"{ticker} earnings revenue beat miss guidance EPS quarter {year}",
            4,
        ),
        "insider": (
            f"{ticker} insider buying selling SEC Form 4 executive shares {year}",
            3,
        ),
        "risk": (
            f"{ticker} {name} lawsuit regulatory investigation SEC CFTC antitrust risk",
            4,
        ),
        "competitive": (
            f"{name} market share competitor industry headwinds tailwinds {year}",
            4,
        ),
    }

    results = {}
    for key, (query, max_r) in queries.items():
        results[key] = _search(client, query, max_results=max_r)

    return results


def search_web(query: str, max_results: int = 5) -> list[dict]:
    """Generic web search. Returns list of result dicts."""
    client = _client()
    if not client:
        return [{"error": "TAVILY_API_KEY not set"}]
    return _search(client, query, max_results=max_results)


def format_tavily_for_agent(ticker: str, company_name: str = "") -> str:
    """
    Run all 5 targeted searches and return agent-readable text.
    Gracefully degrades if Tavily key is missing.
    """
    intel = get_stock_intelligence(ticker, company_name)

    if "error" in intel:
        return f"\n[WEB INTELLIGENCE]: {intel['error']} — set TAVILY_API_KEY to enable real-time web search."

    section_labels = {
        "analyst":     "ANALYST UPGRADES / DOWNGRADES / PRICE TARGETS",
        "earnings":    "EARNINGS SURPRISES & GUIDANCE REVISIONS",
        "insider":     "INSIDER ACTIVITY (SEC FORM 4)",
        "risk":        "REGULATORY, LEGAL & MACRO RISKS",
        "competitive": "COMPETITIVE LANDSCAPE & INDUSTRY TRENDS",
    }

    lines = [f"\nWEB INTELLIGENCE — {ticker.upper()} (via Tavily real-time search)"]

    for key, label in section_labels.items():
        items = intel.get(key, [])
        if not items:
            lines.append(f"\n{label}:\n  No results found.")
            continue

        lines.append(f"\n{label}:")
        for item in items:
            date_str = f" [{item['published']}]" if item.get("published") else ""
            lines.append(f"  • {item['title']}{date_str}")
            if item["content"]:
                # Truncate and clean content
                content = item["content"].replace("\n", " ").strip()
                lines.append(f"    {content[:250]}")

    return "\n".join(lines)
