from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END


# ── State Schema ──────────────────────────────────────────────
class HedgeFundState(TypedDict):
    ticker: str
    company_name: str
    financial_data: dict
    financial_summary: str   # yfinance formatted text
    edgar_summary: str       # SEC EDGAR verified financials
    web_summary: str         # Tavily real-time intelligence
    planner_output: str
    bull_analysis: str
    bear_analysis: str
    debate_round: str
    risk_audit: str
    judge_verdict: str
    report: str
    human_approved: bool
    iteration: int
    status: str
    error: Optional[str]


# ── Node Functions ─────────────────────────────────────────────
def planner_node(state: HedgeFundState) -> dict:
    from tools.yfinance_tool import get_stock_financials, format_financials_for_agent
    from tools.sec_edgar_tool import format_edgar_for_agent
    from tools.tavily_tool import format_tavily_for_agent
    from tools.llm import call_llm
    from prompts.agent_prompts import PLANNER_PROMPT

    ticker = state["ticker"]

    # Pull all three real data sources
    fin_data = get_stock_financials(ticker)
    fin_summary = format_financials_for_agent(fin_data)
    edgar_summary = format_edgar_for_agent(ticker)
    web_summary = format_tavily_for_agent(ticker, fin_data.get("company_name", ticker))

    full_context = f"{fin_summary}\n{edgar_summary}\n{web_summary}"

    planner_output = call_llm(
        messages=[
            {"role": "system", "content": PLANNER_PROMPT},
            {"role": "user", "content": f"Create research plan for {ticker}\n\n{full_context}"},
        ],
        temperature=0.3,
    )
    return {
        "financial_data": fin_data,
        "financial_summary": fin_summary,
        "edgar_summary": edgar_summary,
        "web_summary": web_summary,
        "planner_output": planner_output,
        "status": "planner_done",
        "company_name": fin_data.get("company_name", ticker),
    }


def bull_node(state: HedgeFundState) -> dict:
    from agents.bull_agent import run
    return run(state)


def bear_node(state: HedgeFundState) -> dict:
    from agents.bear_agent import run
    return run(state)


def debate_node(state: HedgeFundState) -> dict:
    from tools.llm import call_llm
    from prompts.agent_prompts import DEBATE_PROMPT

    context = f"""TICKER: {state['ticker']}

BULL CASE:
{state['bull_analysis']}

BEAR CASE:
{state['bear_analysis']}"""

    return {
        "debate_round": call_llm(
            messages=[
                {"role": "system", "content": DEBATE_PROMPT},
                {"role": "user", "content": context},
            ],
            temperature=0.8,
        ),
        "status": "debate_done",
    }


def risk_auditor_node(state: HedgeFundState) -> dict:
    from agents.risk_auditor import run
    return run(state)


def judge_node(state: HedgeFundState) -> dict:
    from agents.judge_agent import run
    return run(state)


def report_node(state: HedgeFundState) -> dict:
    from agents.report_agent import run
    return run(state)


def human_checkpoint_node(state: HedgeFundState) -> dict:
    """Pause point — UI handles approval, just mark status."""
    return {"status": "awaiting_human"}


# ── Build Graph ────────────────────────────────────────────────
def build_graph():
    graph = StateGraph(HedgeFundState)

    graph.add_node("planner", planner_node)
    graph.add_node("bull", bull_node)
    graph.add_node("bear", bear_node)
    graph.add_node("debate", debate_node)
    graph.add_node("risk_auditor", risk_auditor_node)
    graph.add_node("judge", judge_node)
    graph.add_node("report", report_node)
    graph.add_node("human_checkpoint", human_checkpoint_node)

    graph.set_entry_point("planner")
    graph.add_edge("planner", "bull")
    graph.add_edge("planner", "bear")   # parallel fan-out
    graph.add_edge("bull", "debate")
    graph.add_edge("bear", "debate")
    graph.add_edge("debate", "risk_auditor")
    graph.add_edge("risk_auditor", "judge")
    graph.add_edge("judge", "report")
    graph.add_edge("report", "human_checkpoint")
    graph.add_edge("human_checkpoint", END)

    return graph.compile()


workflow = build_graph()
