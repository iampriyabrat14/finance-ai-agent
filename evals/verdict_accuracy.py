"""
Custom evaluation suite for AI Hedge Fund Intern.

Measures: Did the agent verdict align with actual 30-day price performance?
This is what separates serious GenAI projects from demos.
"""

import yfinance as yf
from datetime import datetime, timedelta
import argparse


VERDICT_BULLISH = {"STRONG BUY", "BUY"}
VERDICT_BEARISH = {"SELL", "AVOID", "SHORT"}
VERDICT_NEUTRAL = {"HOLD"}


def get_price_return(ticker: str, from_date: str, days: int = 30) -> float:
    """Get actual price return from a given date."""
    start = datetime.strptime(from_date, "%Y-%m-%d")
    end = start + timedelta(days=days)

    stock = yf.Ticker(ticker)
    hist = stock.history(start=start.strftime("%Y-%m-%d"), end=end.strftime("%Y-%m-%d"))

    if hist.empty or len(hist) < 2:
        return None

    return_pct = ((hist['Close'].iloc[-1] - hist['Close'].iloc[0]) / hist['Close'].iloc[0]) * 100
    return round(return_pct, 2)


def score_verdict(verdict: str, actual_return: float) -> dict:
    """Score whether the verdict was correct given actual return."""
    verdict_upper = verdict.upper()

    is_bullish = any(v in verdict_upper for v in VERDICT_BULLISH)
    is_bearish = any(v in verdict_upper for v in VERDICT_BEARISH)

    if is_bullish and actual_return > 2:
        result, score = "CORRECT", 1.0
    elif is_bearish and actual_return < -2:
        result, score = "CORRECT", 1.0
    elif is_bullish and actual_return < -5:
        result, score = "WRONG", 0.0
    elif is_bearish and actual_return > 5:
        result, score = "WRONG", 0.0
    else:
        result, score = "PARTIAL", 0.5

    return {
        "verdict": verdict,
        "is_bullish": is_bullish,
        "is_bearish": is_bearish,
        "actual_30d_return": actual_return,
        "result": result,
        "score": score,
    }


def run_backtest(verdicts: list) -> dict:
    """
    Run backtest on a list of past verdicts.

    verdicts format:
    [
        {"ticker": "NVDA", "verdict": "STRONG BUY", "date": "2024-01-15"},
        {"ticker": "TSLA", "verdict": "AVOID", "date": "2024-02-01"},
    ]
    """
    results = []
    correct = 0
    total = 0

    for item in verdicts:
        actual = get_price_return(item["ticker"], item["date"])
        if actual is None:
            continue

        scored = score_verdict(item["verdict"], actual)
        scored["ticker"] = item["ticker"]
        scored["date"] = item["date"]
        results.append(scored)

        correct += scored["score"]
        total += 1

    accuracy = (correct / total * 100) if total > 0 else 0

    return {
        "total_verdicts": total,
        "accuracy_pct": round(accuracy, 1),
        "correct": int(correct),
        "results": results,
    }


def evaluate_single(ticker: str, verdict: str, lookback_days: int = 30) -> dict:
    """Evaluate a single verdict against recent price action."""
    end = datetime.now()
    start = end - timedelta(days=lookback_days)

    actual = get_price_return(ticker, start.strftime("%Y-%m-%d"), lookback_days)
    if actual is None:
        return {"error": f"Could not fetch price data for {ticker}"}

    result = score_verdict(verdict, actual)
    result["ticker"] = ticker
    result["lookback_days"] = lookback_days

    print(f"\n{'='*50}")
    print(f"EVALUATION: {ticker}")
    print(f"Verdict: {verdict}")
    print(f"Actual {lookback_days}d return: {actual}%")
    print(f"Result: {result['result']}")
    print(f"Score: {result['score']}")
    print(f"{'='*50}\n")

    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate AI Hedge Fund Intern verdicts")
    parser.add_argument("--ticker", required=True, help="Stock ticker e.g. NVDA")
    parser.add_argument("--verdict", default="BUY", help="Verdict from agent e.g. 'STRONG BUY'")
    parser.add_argument("--lookback", type=int, default=30, help="Days to look back")

    args = parser.parse_args()
    evaluate_single(args.ticker, args.verdict, args.lookback)
