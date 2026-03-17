"""
yfinance tool — deep financial data extraction.

Pulls beyond basic info:
  - Price & valuation
  - Quarterly income statement (revenue, net income, EPS)
  - Balance sheet highlights
  - Analyst recommendation trend (last 4 quarters)
  - Top 5 institutional holders
  - Recent news headlines
  - Options put/call ratio (sentiment proxy)
"""
import yfinance as yf
from datetime import datetime, timedelta


def get_stock_financials(ticker: str) -> dict:
    """Fetch comprehensive real financial data for a stock ticker."""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        # ── Price history ──────────────────────────────────────
        hist_1m = stock.history(period="1mo")
        hist_3m = stock.history(period="3mo")
        hist_1y = stock.history(period="1y")

        price_change_30d = 0
        price_change_3m = 0
        price_change_1y = 0

        if not hist_1m.empty:
            price_change_30d = round(
                (hist_1m['Close'].iloc[-1] - hist_1m['Close'].iloc[0]) / hist_1m['Close'].iloc[0] * 100, 2
            )
        if not hist_3m.empty:
            price_change_3m = round(
                (hist_3m['Close'].iloc[-1] - hist_3m['Close'].iloc[0]) / hist_3m['Close'].iloc[0] * 100, 2
            )
        if not hist_1y.empty:
            price_change_1y = round(
                (hist_1y['Close'].iloc[-1] - hist_1y['Close'].iloc[0]) / hist_1y['Close'].iloc[0] * 100, 2
            )

        # ── Quarterly financials ───────────────────────────────
        quarterly_revenue = []
        quarterly_net_income = []
        try:
            qfin = stock.quarterly_financials
            if not qfin.empty:
                for col in qfin.columns[:6]:  # last 6 quarters
                    date_str = col.strftime("%Y-Q%q") if hasattr(col, 'strftime') else str(col)[:7]
                    rev_row = "Total Revenue" if "Total Revenue" in qfin.index else None
                    ni_row = "Net Income" if "Net Income" in qfin.index else None
                    quarterly_revenue.append({
                        "period": str(col)[:7],
                        "value": int(qfin[col].get("Total Revenue", 0) or 0) if rev_row else 0,
                    })
                    quarterly_net_income.append({
                        "period": str(col)[:7],
                        "value": int(qfin[col].get("Net Income", 0) or 0) if ni_row else 0,
                    })
        except Exception:
            pass

        # ── Analyst recommendations trend ──────────────────────
        rec_trend = []
        try:
            recs = stock.recommendations
            if recs is not None and not recs.empty:
                for _, row in recs.tail(8).iterrows():
                    rec_trend.append({
                        "date": str(row.name)[:10] if hasattr(row.name, 'strftime') else str(row.name)[:10],
                        "firm": row.get("Firm", ""),
                        "grade": row.get("To Grade", row.get("toGrade", "")),
                        "action": row.get("Action", row.get("action", "")),
                    })
                rec_trend = list(reversed(rec_trend))  # newest first
        except Exception:
            pass

        # ── Top institutional holders ──────────────────────────
        top_holders = []
        try:
            inst = stock.institutional_holders
            if inst is not None and not inst.empty:
                for _, row in inst.head(5).iterrows():
                    top_holders.append({
                        "holder": row.get("Holder", ""),
                        "shares": int(row.get("Shares", 0) or 0),
                        "pct_held": round(float(row.get("% Out", 0) or 0) * 100, 2),
                    })
        except Exception:
            pass

        # ── Recent news ────────────────────────────────────────
        recent_news = []
        try:
            news = stock.news or []
            for item in news[:6]:
                recent_news.append({
                    "title": item.get("title", ""),
                    "publisher": item.get("publisher", ""),
                    "published": datetime.fromtimestamp(item.get("providerPublishTime", 0)).strftime("%Y-%m-%d"),
                })
        except Exception:
            pass

        # ── Options put/call ratio (sentiment proxy) ───────────
        put_call_ratio = None
        try:
            expirations = stock.options
            if expirations:
                chain = stock.option_chain(expirations[0])
                total_put_vol = chain.puts["volume"].sum()
                total_call_vol = chain.calls["volume"].sum()
                if total_call_vol > 0:
                    put_call_ratio = round(total_put_vol / total_call_vol, 2)
        except Exception:
            pass

        # ── Core data dict ─────────────────────────────────────
        data = {
            "ticker": ticker.upper(),
            "company_name": info.get("longName", ticker),
            "sector": info.get("sector", "N/A"),
            "industry": info.get("industry", "N/A"),
            "current_price": info.get("currentPrice") or info.get("regularMarketPrice", 0),
            "market_cap": info.get("marketCap", 0),
            "pe_ratio": info.get("trailingPE", "N/A"),
            "forward_pe": info.get("forwardPE", "N/A"),
            "peg_ratio": info.get("pegRatio", "N/A"),
            "price_to_book": info.get("priceToBook", "N/A"),
            "price_to_sales": info.get("priceToSalesTrailing12Months", "N/A"),
            "eps": info.get("trailingEps", "N/A"),
            "eps_forward": info.get("forwardEps", "N/A"),
            "revenue_growth": info.get("revenueGrowth", "N/A"),
            "earnings_growth": info.get("earningsGrowth", "N/A"),
            "profit_margin": info.get("profitMargins", "N/A"),
            "gross_margin": info.get("grossMargins", "N/A"),
            "operating_margin": info.get("operatingMargins", "N/A"),
            "ebitda_margin": round(
                info.get("ebitda", 0) / info.get("totalRevenue", 1), 4
            ) if info.get("ebitda") and info.get("totalRevenue") else "N/A",
            "debt_to_equity": info.get("debtToEquity", "N/A"),
            "current_ratio": info.get("currentRatio", "N/A"),
            "quick_ratio": info.get("quickRatio", "N/A"),
            "free_cash_flow": info.get("freeCashflow", "N/A"),
            "operating_cash_flow": info.get("operatingCashflow", "N/A"),
            "total_cash": info.get("totalCash", "N/A"),
            "total_debt": info.get("totalDebt", "N/A"),
            "52w_high": info.get("fiftyTwoWeekHigh", "N/A"),
            "52w_low": info.get("fiftyTwoWeekLow", "N/A"),
            "50d_avg": info.get("fiftyDayAverage", "N/A"),
            "200d_avg": info.get("twoHundredDayAverage", "N/A"),
            "analyst_target": info.get("targetMeanPrice", "N/A"),
            "analyst_target_high": info.get("targetHighPrice", "N/A"),
            "analyst_target_low": info.get("targetLowPrice", "N/A"),
            "analyst_recommendation": info.get("recommendationKey", "N/A"),
            "analyst_count": info.get("numberOfAnalystOpinions", "N/A"),
            "price_change_30d": price_change_30d,
            "price_change_3m": price_change_3m,
            "price_change_1y": price_change_1y,
            "dividend_yield": info.get("dividendYield", 0),
            "dividend_rate": info.get("dividendRate", "N/A"),
            "payout_ratio": info.get("payoutRatio", "N/A"),
            "beta": info.get("beta", "N/A"),
            "short_ratio": info.get("shortRatio", "N/A"),
            "short_percent_float": info.get("shortPercentOfFloat", "N/A"),
            "shares_outstanding": info.get("sharesOutstanding", "N/A"),
            "float_shares": info.get("floatShares", "N/A"),
            "insider_ownership": info.get("heldPercentInsiders", "N/A"),
            "institutional_ownership": info.get("heldPercentInstitutions", "N/A"),
            "description": info.get("longBusinessSummary", "")[:600],
            "quarterly_revenue": quarterly_revenue,
            "quarterly_net_income": quarterly_net_income,
            "analyst_rec_trend": rec_trend,
            "top_holders": top_holders,
            "recent_news": recent_news,
            "put_call_ratio": put_call_ratio,
        }

        # Format market cap
        mc = data["market_cap"]
        if mc:
            if mc >= 1e12:
                data["market_cap_fmt"] = f"${mc/1e12:.2f}T"
            elif mc >= 1e9:
                data["market_cap_fmt"] = f"${mc/1e9:.2f}B"
            else:
                data["market_cap_fmt"] = f"${mc/1e6:.2f}M"
        else:
            data["market_cap_fmt"] = "N/A"

        return data

    except Exception as e:
        return {"error": str(e), "ticker": ticker}


def _pct(val) -> str:
    if val == "N/A" or val is None:
        return "N/A"
    try:
        return f"{float(val)*100:.1f}%"
    except Exception:
        return str(val)


def _fmt_large(val) -> str:
    if val == "N/A" or val is None:
        return "N/A"
    try:
        v = float(val)
        if abs(v) >= 1e12:
            return f"${v/1e12:.2f}T"
        if abs(v) >= 1e9:
            return f"${v/1e9:.2f}B"
        if abs(v) >= 1e6:
            return f"${v/1e6:.1f}M"
        return f"${v:,.0f}"
    except Exception:
        return str(val)


def format_financials_for_agent(data: dict) -> str:
    """Format financial data as rich, agent-readable text."""
    if "error" in data:
        return f"Error fetching data for {data['ticker']}: {data['error']}"

    d = data
    sign = lambda x: f"+{x}%" if isinstance(x, (int, float)) and x >= 0 else f"{x}%"

    # Quarterly revenue table
    q_rev_lines = ""
    if d["quarterly_revenue"]:
        rows = [f"  {r['period']}: {_fmt_large(r['value'])}" for r in d["quarterly_revenue"] if r["value"]]
        q_rev_lines = "\nQUARTERLY REVENUE:\n" + "\n".join(rows)

    # Quarterly net income table
    q_ni_lines = ""
    if d["quarterly_net_income"]:
        rows = [f"  {r['period']}: {_fmt_large(r['value'])}" for r in d["quarterly_net_income"] if r["value"]]
        q_ni_lines = "\nQUARTERLY NET INCOME:\n" + "\n".join(rows)

    # Analyst rec trend
    rec_lines = ""
    if d["analyst_rec_trend"]:
        rows = [
            f"  {r['date']} | {r['firm']:<30} | {r['action']:<10} → {r['grade']}"
            for r in d["analyst_rec_trend"][:6]
        ]
        rec_lines = "\nANALYST RATING CHANGES (recent):\n" + "\n".join(rows)

    # Top holders
    holder_lines = ""
    if d["top_holders"]:
        rows = [f"  {h['holder']}: {h['pct_held']:.2f}% ({h['shares']:,} shares)" for h in d["top_holders"]]
        holder_lines = "\nTOP INSTITUTIONAL HOLDERS:\n" + "\n".join(rows)

    # News
    news_lines = ""
    if d["recent_news"]:
        rows = [f"  [{n['published']}] {n['publisher']}: {n['title']}" for n in d["recent_news"]]
        news_lines = "\nRECENT NEWS:\n" + "\n".join(rows)

    # Put/call
    pcr_line = f"- Options Put/Call Ratio: {d['put_call_ratio']} ({'bearish' if d['put_call_ratio'] and d['put_call_ratio'] > 1 else 'bullish'} sentiment)" if d["put_call_ratio"] else ""

    return f"""
STOCK: {d['ticker']} — {d['company_name']}
Sector: {d['sector']} | Industry: {d['industry']}

PRICE & PERFORMANCE:
- Current Price: ${d['current_price']}
- 30D Change: {sign(d['price_change_30d'])} | 3M: {sign(d['price_change_3m'])} | 1Y: {sign(d['price_change_1y'])}
- 52W Range: ${d['52w_low']} — ${d['52w_high']}
- 50D MA: ${d['50d_avg']} | 200D MA: ${d['200d_avg']}

VALUATION:
- Market Cap: {d['market_cap_fmt']}
- P/E (TTM): {d['pe_ratio']} | Forward P/E: {d['forward_pe']} | PEG: {d['peg_ratio']}
- P/B: {d['price_to_book']} | P/S: {d['price_to_sales']}
- EPS (TTM): ${d['eps']} | Forward EPS: ${d['eps_forward']}

GROWTH & PROFITABILITY:
- Revenue Growth (YoY): {_pct(d['revenue_growth'])}
- Earnings Growth: {_pct(d['earnings_growth'])}
- Gross Margin: {_pct(d['gross_margin'])}
- Operating Margin: {_pct(d['operating_margin'])}
- Profit Margin: {_pct(d['profit_margin'])}
- EBITDA Margin: {_pct(d['ebitda_margin'])}
{q_rev_lines}
{q_ni_lines}

BALANCE SHEET & CASH:
- Free Cash Flow: {_fmt_large(d['free_cash_flow'])}
- Operating Cash Flow: {_fmt_large(d['operating_cash_flow'])}
- Total Cash: {_fmt_large(d['total_cash'])}
- Total Debt: {_fmt_large(d['total_debt'])}
- Debt/Equity: {d['debt_to_equity']}
- Current Ratio: {d['current_ratio']} | Quick Ratio: {d['quick_ratio']}

SHORT INTEREST & SENTIMENT:
- Short % of Float: {_pct(d['short_percent_float'])}
- Short Ratio (days to cover): {d['short_ratio']}
{pcr_line}
- Beta: {d['beta']}

OWNERSHIP:
- Insider Ownership: {_pct(d['insider_ownership'])}
- Institutional Ownership: {_pct(d['institutional_ownership'])}
{holder_lines}

ANALYST CONSENSUS ({d['analyst_count']} analysts):
- Recommendation: {d['analyst_recommendation'].upper() if isinstance(d['analyst_recommendation'], str) else d['analyst_recommendation']}
- Price Target: ${d['analyst_target']} (Low: ${d['analyst_target_low']} / High: ${d['analyst_target_high']})
{rec_lines}

DIVIDEND:
- Yield: {_pct(d['dividend_yield'])} | Annual Rate: ${d['dividend_rate']} | Payout Ratio: {_pct(d['payout_ratio'])}
{news_lines}

BUSINESS: {d['description']}
"""
