# ◈ AI Hedge Fund Intern
### Multi-Agent Stock Due Diligence System

> An autonomous AI investment committee powered by **LangGraph + Groq (Llama 3.3)** that debates stocks like real analysts — Bull vs Bear vs Risk Auditor — backed by **three live data sources** (yfinance, SEC EDGAR, Tavily), with a CIO judge making the final call and **human-in-the-loop approval** before a professional PDF report is generated.

---

## Architecture

```
Ticker Input
      │
      ▼
┌─────────────────────────────────────────────┐
│              DATA PIPELINE                  │
│  yfinance ──► SEC EDGAR ──► Tavily Search   │
│  (fundamentals) (XBRL history) (live news)  │
└────────────────────┬────────────────────────┘
                     │
                     ▼
            ┌────────────────┐
            │  Planner Agent │  Structures bull/bear/risk focus areas
            └───────┬────────┘
                    │
           ┌────────┴────────┐
           ▼                 ▼
     ┌──────────┐      ┌──────────┐
     │   Bull   │      │   Bear   │  ← Parallel execution
     │  Analyst │      │  Analyst │
     └────┬─────┘      └─────┬────┘
          └────────┬──────────┘
                   ▼
          ┌─────────────────┐
          │  Debate Round   │  Cross-examination & rebuttals
          └────────┬────────┘
                   ▼
          ┌─────────────────┐
          │  Risk Auditor   │  Scores 5 dimensions (1–10)
          └────────┬────────┘
                   ▼
          ┌─────────────────┐
          │   CIO Judge     │  Final verdict + confidence %
          └────────┬────────┘
                   ▼
        ⏸  HUMAN-IN-THE-LOOP
        Approve · Re-run · Reject
                   │
                   ▼
        ↓ PDF + Markdown Export
```

---

## What Makes This Different

| Feature | Detail |
|---|---|
| **Groq primary / OpenAI fallback** | Llama 3.3 70B by default — fast, free tier available. Falls back to GPT-4o automatically |
| **Three real data sources** | yfinance (price + fundamentals + options), SEC EDGAR XBRL (verified annual filings, no key), Tavily (live analyst news + insider activity) |
| **Adversarial debate pattern** | Agents argue *against* each other — not just summarize. Bull must respond to bear's strongest point |
| **LangGraph state machine** | True non-linear workflow with typed state, not a simple chain |
| **Tabbed premium UI** | Research / Bull / Bear / Debate / Risk / Verdict — each in its own tab with live pipeline stepper |
| **PDF report generation** | Professional multi-page PDF with cover page, metrics table, color-coded sections, disclaimer |
| **Human-in-the-loop** | Hard approval gate before any report is finalized |
| **Custom eval suite** | Verdict accuracy scored against actual 30-day price performance |

---

## Tech Stack

| Layer | Technology |
|---|---|
| LLM (primary) | Groq — `llama-3.3-70b-versatile` |
| LLM (fallback) | OpenAI — `gpt-4o` |
| Orchestration | LangGraph |
| Data — Price & Fundamentals | yfinance |
| Data — Filing History | SEC EDGAR XBRL REST API |
| Data — Live News | Tavily Search API |
| UI | Streamlit (wide layout, sidebar, tabs) |
| PDF Export | ReportLab |
| Eval | Custom backtest vs. 30-day price return |

---

## Project Structure

```
financecode/
├── agents/
│   ├── bull_agent.py          ← run(state) → bull_analysis
│   ├── bear_agent.py          ← run(state) → bear_analysis
│   ├── risk_auditor.py        ← run(state) → risk_audit
│   ├── judge_agent.py         ← run(state) → judge_verdict
│   └── report_agent.py        ← run(state) → compiled markdown report
│
├── graph/
│   └── workflow.py            ← LangGraph state machine (HedgeFundState)
│
├── tools/
│   ├── llm.py                 ← call_llm() — Groq primary, OpenAI fallback
│   ├── yfinance_tool.py       ← Price, fundamentals, options, holders, news
│   ├── sec_edgar_tool.py      ← XBRL financial history + 8-K/10-K filings
│   ├── tavily_tool.py         ← 5 targeted searches (analyst, earnings, insider, risk, competitive)
│   └── pdf_report.py          ← ReportLab PDF generator
│
├── prompts/
│   └── agent_prompts.py       ← All system prompts (versioned, structured)
│
├── evals/
│   └── verdict_accuracy.py    ← Backtest verdicts vs actual price movement
│
├── ui/
│   └── app.py                 ← Streamlit UI (sidebar config, tabs, HITL, download)
│
├── requirements.txt
└── README.md
```

---

## Quick Start

### 1. Clone & install

```bash
git clone https://github.com/yourusername/hedge-fund-intern
cd hedge-fund-intern/financecode
pip install -r requirements.txt
```

### 2. API Keys

| Key | Where to Get | Required? |
|---|---|---|
| `GROQ_API_KEY` | [console.groq.com](https://console.groq.com) | **Yes** (primary LLM) |
| `OPENAI_API_KEY` | [platform.openai.com](https://platform.openai.com) | Optional (fallback) |
| `TAVILY_API_KEY` | [tavily.com](https://tavily.com) | Optional (live news) |

You can set them in a `.env` file:

```env
GROQ_API_KEY=gsk_...
OPENAI_API_KEY=sk-...        # optional
TAVILY_API_KEY=tvly-...      # optional
```

Or enter them directly in the sidebar when the app is running.

### 3. Run

```bash
streamlit run ui/app.py
```

Opens at **http://localhost:8501**

---

## Data Sources — What Each Pulls

### yfinance (no API key needed)
- Current price, 30D / 3M / 1Y performance
- P/E, Forward P/E, PEG, P/B, P/S ratios
- Gross / operating / EBITDA / net margins
- Quarterly revenue & net income (last 6 quarters)
- Free cash flow, operating cash flow, total debt
- Short interest %, put/call ratio (options sentiment)
- Top 5 institutional holders with % held
- Analyst recommendation trend (firm-by-firm)
- Recent news headlines

### SEC EDGAR XBRL (no API key needed)
- Ticker → CIK lookup
- Annual revenue history (last 4 years, verified 10-K)
- Net income, operating income, EPS, gross profit history
- R&D expense history
- Total assets, long-term debt
- Recent 8-K events with item codes (earnings, exec changes, acquisitions)

### Tavily Search (optional, `TAVILY_API_KEY`)
- Analyst upgrades / downgrades / price target changes
- Earnings beat/miss & guidance revisions
- Insider buying/selling (SEC Form 4)
- Regulatory / legal / investigation headlines
- Competitive landscape & industry trends

---

## Agent Roles

| Agent | Prompt Role | Temperature | Output |
|---|---|---|---|
| **Planner** | Senior research director | 0.3 | JSON research focus plan |
| **Bull Analyst** | Optimistic, data-driven | 0.7 | 4–5 numbered buy arguments + price target |
| **Bear Analyst** | Skeptical, forensic | 0.7 | 4–5 numbered short arguments + downside target |
| **Debate** | Investment committee | 0.8 | Bull rebuttal + Bear rebuttal |
| **Risk Auditor** | Quantitative, objective | 0.2 | 5 risk scores (1–10) + overall rating |
| **CIO Judge** | Decisive, experienced | 0.4 | Final verdict + confidence % + position size |
| **Report Agent** | Compiler | — | Structured markdown report |

---

## PDF Report Structure

The generated PDF includes:

1. **Cover page** — Ticker, company, verdict badge (color-coded), confidence %, date
2. **Financial snapshot** — 16-metric table (price, valuation, margins, debt, ownership)
3. **SEC EDGAR data** — Verified XBRL annual financial history
4. **Web intelligence** — Tavily news digest (if configured)
5. **Research plan** — Planner agent output
6. **Bull case** — Green-accented section
7. **Bear case** — Red-accented section
8. **Debate** — Cross-examination section
9. **Risk audit** — Scored risk dimensions
10. **CIO verdict** — Hero card with verdict KPIs + full rationale
11. **Legal disclaimer**

---

## Sample Output

```
TICKER: NVDA

▲ BULL VERDICT: STRONG BUY — $1,400 target
1. Data center revenue +427% YoY; H100/H200 backlogged through 2026
2. Gross margins at 78.4% — highest in semiconductor history
3. CUDA ecosystem moat makes switching costs prohibitive for hyperscalers
4. Sovereign AI wave (UAE, Japan, France) opening entirely new TAM

▽ BEAR VERDICT: AVOID — $480 downside scenario
1. Forward P/S of 35x prices in perfection — zero room for execution miss
2. AMD MI300X closing performance gap faster than consensus expects
3. China export controls cut 20% of total addressable market
4. Customer concentration: 3 hyperscalers = 40% of revenue

◉ OVERALL RISK SCORE: 7.2/10 — HIGH RISK
  Valuation Risk: 9/10 | Regulatory: 8/10 | Macro Sensitivity: 6/10

⊕ CIO FINAL VERDICT: BUY
  Confidence: 72% | Position: Medium (3–5% of portfolio)
  Bull argument stronger on structural AI demand. Bear's valuation
  concern valid but doesn't override the multi-year thesis. Size accordingly.
```

---

## Evaluation

```bash
# Score a single past verdict
python evals/verdict_accuracy.py --ticker NVDA --verdict "STRONG BUY" --lookback 30

# Output
EVALUATION: NVDA
Verdict: STRONG BUY
Actual 30d return: +18.4%
Result: CORRECT
Score: 1.0
```

The eval suite (`evals/verdict_accuracy.py`) compares agent verdicts against actual 30-day price returns to track accuracy over time. Use `run_backtest()` for bulk scoring.

---

## Environment Variables

| Variable | Description | Default |
|---|---|---|
| `GROQ_API_KEY` | Groq API key | — |
| `OPENAI_API_KEY` | OpenAI API key (fallback) | — |
| `TAVILY_API_KEY` | Tavily search API key | — |
| `FRED_API_KEY` | FRED macro data (optional) | — |

---

## Roadmap

- [x] Groq primary LLM with OpenAI fallback
- [x] SEC EDGAR XBRL verified financial history
- [x] Tavily real-time web intelligence (5 targeted search types)
- [x] Options put/call ratio sentiment
- [x] Institutional holders + analyst rec trend
- [x] Premium tabbed UI with pipeline stepper
- [x] PDF report generation (ReportLab)
- [ ] Multi-stock portfolio screener (rank 10 tickers by conviction)
- [ ] Backtesting dashboard (visualize verdict accuracy over time)
- [ ] Slack / email notification on verdict
- [ ] FRED macro overlay (interest rates, CPI, VIX)
- [ ] Fine-tuned judge model on historical analyst reports

---

*Built to demonstrate production-grade multi-agent LangGraph patterns — real data, real debate, real accountability.*
