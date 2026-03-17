"""
SEC EDGAR tool — real filing data and XBRL financial history.
No API key required. Uses public SEC REST APIs.

APIs used:
  - https://www.sec.gov/files/company_tickers.json     (ticker → CIK lookup)
  - https://data.sec.gov/submissions/CIK{cik}.json     (recent filings list)
  - https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json  (XBRL financials)
"""
import requests
import time

HEADERS = {
    "User-Agent": "hedge-fund-intern research@example.com",
    "Accept-Encoding": "gzip, deflate",
}
TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
SUBMISSIONS_URL = "https://data.sec.gov/submissions/CIK{cik}.json"
COMPANY_FACTS_URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"

_cik_cache: dict = {}


# ── CIK Lookup ─────────────────────────────────────────────────

def _get_cik(ticker: str) -> str | None:
    """Map a ticker symbol to its zero-padded 10-digit SEC CIK."""
    key = ticker.upper()
    if key in _cik_cache:
        return _cik_cache[key]

    try:
        resp = requests.get(TICKERS_URL, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        for entry in resp.json().values():
            if entry.get("ticker", "").upper() == key:
                cik = str(entry["cik_str"]).zfill(10)
                _cik_cache[key] = cik
                return cik
    except Exception:
        pass
    return None


# ── XBRL Financial History ─────────────────────────────────────

def _extract_xbrl_series(facts: dict, concept: str, form: str = "10-K") -> list[dict]:
    """
    Extract annual or quarterly values for a US-GAAP concept from XBRL company facts.
    Returns list of {date, value} sorted newest-first, deduplicated by fiscal period end.
    """
    try:
        units = facts["facts"]["us-gaap"][concept]["units"]
        unit_key = "USD" if "USD" in units else ("shares" if "shares" in units else list(units.keys())[0])
        entries = [e for e in units[unit_key] if e.get("form") == form and e.get("val") is not None]
        seen, result = set(), []
        for e in sorted(entries, key=lambda x: x.get("end", ""), reverse=True):
            end = e.get("end")
            if end not in seen:
                seen.add(end)
                result.append({"date": end, "value": e["val"], "filed": e.get("filed", "")})
        return result[:5]
    except (KeyError, IndexError, TypeError):
        return []


def get_financial_history(ticker: str) -> dict:
    """
    Fetch SEC XBRL financial history: revenue, net income, EPS, operating income, R&D.
    Uses 10-K (annual) filings — verified source of truth, not estimated.
    """
    cik = _get_cik(ticker)
    if not cik:
        return {"error": f"Could not find SEC CIK for ticker '{ticker}'"}

    try:
        resp = requests.get(COMPANY_FACTS_URL.format(cik=cik), headers=HEADERS, timeout=20)
        resp.raise_for_status()
        facts = resp.json()
    except Exception as e:
        return {"error": f"XBRL fetch failed: {e}"}

    # Revenue — try multiple GAAP labels (different companies use different ones)
    revenue = (
        _extract_xbrl_series(facts, "Revenues") or
        _extract_xbrl_series(facts, "RevenueFromContractWithCustomerExcludingAssessedTax") or
        _extract_xbrl_series(facts, "SalesRevenueNet") or
        _extract_xbrl_series(facts, "RevenueFromContractWithCustomerIncludingAssessedTax")
    )
    net_income = _extract_xbrl_series(facts, "NetIncomeLoss")
    eps = (
        _extract_xbrl_series(facts, "EarningsPerShareBasic") or
        _extract_xbrl_series(facts, "EarningsPerShareDiluted")
    )
    operating_income = _extract_xbrl_series(facts, "OperatingIncomeLoss")
    gross_profit = _extract_xbrl_series(facts, "GrossProfit")
    rd_expense = _extract_xbrl_series(facts, "ResearchAndDevelopmentExpense")
    total_assets = _extract_xbrl_series(facts, "Assets")
    total_debt = (
        _extract_xbrl_series(facts, "LongTermDebt") or
        _extract_xbrl_series(facts, "LongTermDebtNoncurrent")
    )

    return {
        "ticker": ticker.upper(),
        "cik": cik,
        "revenue": revenue,
        "net_income": net_income,
        "eps": eps,
        "operating_income": operating_income,
        "gross_profit": gross_profit,
        "rd_expense": rd_expense,
        "total_assets": total_assets,
        "total_debt": total_debt,
    }


# ── Recent Filings ─────────────────────────────────────────────

def get_recent_filings(ticker: str, form_types: list[str] | None = None, limit: int = 12) -> list[dict]:
    """
    Fetch recent SEC filings metadata from EDGAR submissions API.
    Returns filings with type, date, and description (what the 8-K is about, etc.)
    """
    if form_types is None:
        form_types = ["8-K", "10-K", "10-Q"]

    cik = _get_cik(ticker)
    if not cik:
        return [{"error": f"Could not find SEC CIK for ticker '{ticker}'"}]

    try:
        resp = requests.get(SUBMISSIONS_URL.format(cik=cik), headers=HEADERS, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        return [{"error": f"Submissions fetch failed: {e}"}]

    recent = data.get("filings", {}).get("recent", {})
    forms = recent.get("form", [])
    dates = recent.get("filingDate", [])
    descriptions = recent.get("primaryDocDescription", [])
    accessions = recent.get("accessionNumber", [])
    items = recent.get("items", [])  # 8-K item codes e.g. "2.02" = earnings results

    results = []
    for i, form in enumerate(forms):
        if form in form_types:
            desc = descriptions[i] if i < len(descriptions) else ""
            item_code = items[i] if i < len(items) else ""
            # Map 8-K item codes to human labels
            item_label = _8k_item_label(item_code) if form == "8-K" else ""
            results.append({
                "form": form,
                "date": dates[i] if i < len(dates) else "N/A",
                "description": desc,
                "item_code": item_code,
                "item_label": item_label,
                "accession": accessions[i] if i < len(accessions) else "",
            })
        if len(results) >= limit:
            break

    return results


def _8k_item_label(item_code: str) -> str:
    """Map SEC 8-K item codes to readable event descriptions."""
    labels = {
        "1.01": "Entry into material agreement",
        "1.02": "Termination of material agreement",
        "1.03": "Bankruptcy or receivership",
        "2.01": "Completion of acquisition/disposition",
        "2.02": "Results of operations (Earnings)",
        "2.05": "Departure of directors or officers",
        "2.06": "Material impairment",
        "3.01": "Delisting notice",
        "4.01": "Auditor change",
        "5.01": "Change in control",
        "5.02": "Executive departure/appointment",
        "5.03": "Amendment to articles",
        "7.01": "Regulation FD disclosure",
        "8.01": "Other events",
        "9.01": "Financial statements",
    }
    for code, label in labels.items():
        if code in str(item_code):
            return label
    return item_code


# ── Aggregated Agent-Ready Output ─────────────────────────────

def format_edgar_for_agent(ticker: str) -> str:
    """
    Pull all SEC EDGAR data and return a structured string for agents.
    Includes verified annual financial history + recent filing events.
    """
    history = get_financial_history(ticker)
    filings = get_recent_filings(ticker, form_types=["8-K", "10-K", "10-Q"], limit=10)

    lines = [f"\nSEC EDGAR — {ticker.upper()} (Verified Filing Data)"]

    def fmt(val: float) -> str:
        if abs(val) >= 1e12:
            return f"${val/1e12:.2f}T"
        if abs(val) >= 1e9:
            return f"${val/1e9:.2f}B"
        if abs(val) >= 1e6:
            return f"${val/1e6:.1f}M"
        return f"${val:,.0f}"

    if "error" not in history:
        if history["revenue"]:
            lines.append("\nANNUAL REVENUE (10-K XBRL):")
            for r in history["revenue"][:4]:
                lines.append(f"  {r['date'][:4]}: {fmt(r['value'])}")

        if history["net_income"]:
            lines.append("\nNET INCOME (10-K XBRL):")
            for r in history["net_income"][:4]:
                sign = "+" if r["value"] >= 0 else ""
                lines.append(f"  {r['date'][:4]}: {sign}{fmt(r['value'])}")

        if history["operating_income"]:
            lines.append("\nOPERATING INCOME (10-K XBRL):")
            for r in history["operating_income"][:4]:
                sign = "+" if r["value"] >= 0 else ""
                lines.append(f"  {r['date'][:4]}: {sign}{fmt(r['value'])}")

        if history["eps"]:
            lines.append("\nEPS HISTORY (10-K XBRL):")
            for r in history["eps"][:4]:
                lines.append(f"  {r['date'][:4]}: ${r['value']:.2f}")

        if history["gross_profit"]:
            lines.append("\nGROSS PROFIT (10-K XBRL):")
            for r in history["gross_profit"][:4]:
                lines.append(f"  {r['date'][:4]}: {fmt(r['value'])}")

        if history["rd_expense"]:
            lines.append("\nR&D EXPENSE (10-K XBRL):")
            for r in history["rd_expense"][:4]:
                lines.append(f"  {r['date'][:4]}: {fmt(r['value'])}")

        if history["total_assets"]:
            lines.append("\nTOTAL ASSETS (10-K XBRL):")
            for r in history["total_assets"][:3]:
                lines.append(f"  {r['date'][:4]}: {fmt(r['value'])}")

        if history["total_debt"]:
            lines.append("\nLONG-TERM DEBT (10-K XBRL):")
            for r in history["total_debt"][:3]:
                lines.append(f"  {r['date'][:4]}: {fmt(r['value'])}")
    else:
        lines.append(f"\n[XBRL Error]: {history['error']}")

    # Recent filings
    if filings and "error" not in filings[0]:
        lines.append("\nRECENT MATERIAL FILINGS:")
        for f in filings:
            label = f" — {f['item_label']}" if f["item_label"] else (f" — {f['description']}" if f["description"] else "")
            lines.append(f"  [{f['form']}] {f['date']}{label}")

    return "\n".join(lines)
