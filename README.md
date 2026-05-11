# Finance AI Agent 💹

> **Autonomous 4-agent investment analysis system.** Bull, Bear, Risk Analyst, and CIO Decision Maker debate a stock — then produce a professional PDF investment report with human-in-loop approval.

![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-1C3C3C?style=flat&logoColor=white)
![Groq](https://img.shields.io/badge/Groq_LLM-F55036?style=flat&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat&logo=streamlit&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=flat)

---

## What It Does

Enter a stock ticker. The system launches 4 AI analysts in parallel who debate the investment thesis, assess risk across 5 dimensions, and deliver a structured verdict — all without human intervention until the final approval gate.

---

## Agent Architecture

```
                    Stock Ticker Input
                          │
              ┌───────────┴───────────┐
              ▼                       ▼
        ┌──────────┐           ┌──────────┐
        │  Bull    │           │  Bear    │
        │  Agent   │           │  Agent   │
        │          │           │          │
        │ Bullish  │           │ Bearish  │
        │ signals  │           │ signals  │
        └────┬─────┘           └─────┬────┘
             │                       │
             └──────────┬────────────┘
                        ▼
               ┌─────────────────┐
               │  Risk Analyst   │
               │     Agent       │
               │                 │
               │ 5-dim risk      │
               │ assessment      │
               └────────┬────────┘
                        │
                        ▼
               ┌─────────────────┐
               │  CIO Decision   │
               │   Maker Agent   │
               │                 │
               │ Final verdict + │
               │ confidence      │
               └────────┬────────┘
                        │
                        ▼
               Human Approval Gate
                        │
                        ▼
               PDF Investment Report
```

---

## Features

- **4-Agent Debate** — Bull and Bear agents argue from opposing positions using real market data
- **Real-time Data** — Yahoo Finance price/fundamentals + SEC EDGAR XBRL filings
- **5-Dimension Risk** — Market, liquidity, regulatory, operational, macro risk scoring
- **Human-in-Loop** — CIO verdict staged for human approval before PDF generation
- **Backtesting** — `evals/` module for historical verdict accuracy testing
- **PDF Reports** — Professional investment reports generated with ReportLab
- **Streamlit UI** — Clean web interface for stock input and report viewing
- **Parallel Execution** — Bull and Bear agents run concurrently via LangGraph

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Agent Orchestration | LangGraph (StateGraph, parallel nodes) |
| Primary LLM | Groq — Llama 3.3 70B |
| Fallback LLM | OpenAI GPT-4o |
| Financial Data | yfinance, SEC EDGAR XBRL API |
| Web Search | Tavily Search API |
| UI | Streamlit |
| PDF Generation | ReportLab |
| Language | Python |

---

## Quick Start

```bash
git clone https://github.com/iampriyabrat14/finance-ai-agent.git
cd finance-ai-agent
pip install -r requirements.txt

# Set environment variables
export GROQ_API_KEY=your_groq_key
export OPENAI_API_KEY=your_openai_key      # optional fallback
export TAVILY_API_KEY=your_tavily_key

# Run the Streamlit app
streamlit run ui/app.py
```

---

## Project Structure

```
finance-ai-agent/
├── agents/           # Bull, Bear, Risk, CIO agent implementations
├── graph/            # LangGraph workflow (StateGraph definition)
├── prompts/          # System prompts per agent role
├── tools/            # yfinance, SEC, Tavily, PDF generation tools
├── evals/            # Backtesting + verdict evaluation
├── ui/               # Streamlit frontend
└── requirements.txt
```

---

## Example Output

The system produces a PDF report containing:
- Executive summary with investment verdict
- Bull case: top 5 bullish signals with data
- Bear case: top 5 risk factors with data
- 5-dimension risk scorecard
- Historical XBRL financial snapshots
- Final CIO recommendation with confidence score

---

## License

MIT © 2026 Priyabrat Dalbehera
