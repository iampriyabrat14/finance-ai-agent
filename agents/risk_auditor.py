from tools.llm import call_llm
from prompts.agent_prompts import RISK_AUDITOR_PROMPT


def run(state: dict) -> dict:
    # Risk auditor gets all data sources — regulatory/insider news is especially relevant
    context = "\n".join(filter(None, [
        state["financial_summary"],
        state.get("edgar_summary", ""),
        state.get("web_summary", ""),
    ]))
    content = call_llm(
        messages=[
            {"role": "system", "content": RISK_AUDITOR_PROMPT},
            {"role": "user", "content": f"Audit risk for {state['ticker']}\n\n{context}"},
        ],
        temperature=0.2,
    )
    return {"risk_audit": content, "status": "risk_done"}
