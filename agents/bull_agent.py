from tools.llm import call_llm
from prompts.agent_prompts import BULL_PROMPT


def run(state: dict) -> dict:
    context = "\n".join(filter(None, [
        state["financial_summary"],
        state.get("edgar_summary", ""),
        state.get("web_summary", ""),
        f"Research focus:\n{state['planner_output']}",
    ]))
    content = call_llm(
        messages=[
            {"role": "system", "content": BULL_PROMPT},
            {"role": "user", "content": f"Build the bull case for {state['ticker']}\n\n{context}"},
        ],
        temperature=0.7,
    )
    return {"bull_analysis": content, "status": "bull_done"}
