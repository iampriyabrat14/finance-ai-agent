from tools.llm import call_llm
from prompts.agent_prompts import JUDGE_PROMPT


def run(state: dict) -> dict:
    full_context = f"""STOCK: {state['ticker']} — {state['company_name']}

FINANCIAL DATA:
{state['financial_summary']}

BULL ANALYST CASE:
{state['bull_analysis']}

BEAR ANALYST CASE:
{state['bear_analysis']}

DEBATE REBUTTALS:
{state['debate_round']}

RISK AUDIT:
{state['risk_audit']}"""

    content = call_llm(
        messages=[
            {"role": "system", "content": JUDGE_PROMPT},
            {"role": "user", "content": full_context},
        ],
        temperature=0.4,
    )
    return {"judge_verdict": content, "status": "judge_done"}
