"""
FRED (Federal Reserve Economic Data) tool — macro indicators for risk context.
Requires: FRED_API_KEY env var (free at https://fred.stlouisfed.org/docs/api/api_key.html)
"""
import os
import requests

FRED_BASE_URL = "https://api.stlouisfed.org/fred/series/observations"

# Common macro series useful for equity analysis
MACRO_SERIES = {
    "fed_funds_rate": "FEDFUNDS",
    "cpi_inflation": "CPIAUCSL",
    "unemployment": "UNRATE",
    "gdp_growth": "A191RL1Q225SBEA",
    "10y_treasury": "GS10",
    "vix": "VIXCLS",
}


def get_macro_indicator(series_id: str, limit: int = 6) -> list[dict]:
    """
    Fetch recent observations for a FRED series.

    Args:
        series_id: FRED series ID e.g. 'FEDFUNDS'
        limit: Number of most recent observations

    Returns:
        List of {date, value} dicts
    """
    api_key = os.environ.get("FRED_API_KEY", "")
    if not api_key:
        return [{"error": "FRED_API_KEY not set — skipping macro data"}]

    try:
        resp = requests.get(
            FRED_BASE_URL,
            params={
                "series_id": series_id,
                "api_key": api_key,
                "file_type": "json",
                "limit": limit,
                "sort_order": "desc",
            },
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json().get("observations", [])
    except Exception as e:
        return [{"error": str(e)}]


def get_macro_snapshot() -> str:
    """Return a formatted macro environment summary for agents."""
    lines = ["MACRO ENVIRONMENT (FRED):"]
    for label, series_id in MACRO_SERIES.items():
        obs = get_macro_indicator(series_id, limit=1)
        if obs and "error" not in obs[0]:
            lines.append(f"  {label.replace('_', ' ').title()}: {obs[0].get('value', 'N/A')} ({obs[0].get('date', '')})")
        else:
            lines.append(f"  {label.replace('_', ' ').title()}: N/A (FRED_API_KEY not set)")
    return "\n".join(lines)
