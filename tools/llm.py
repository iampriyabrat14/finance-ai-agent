"""
Shared LLM helper — Groq (primary) with OpenAI (fallback).
All agents import call_llm from here.
"""
import os


def call_llm(messages: list[dict], temperature: float = 0.5) -> str:
    groq_key = os.environ.get("GROQ_API_KEY", "")
    oai_key = os.environ.get("OPENAI_API_KEY", "")

    if groq_key:
        try:
            from groq import Groq
            client = Groq(api_key=groq_key)
            resp = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                temperature=min(temperature, 1.0),
            )
            return resp.choices[0].message.content
        except Exception as e:
            if not oai_key:
                raise RuntimeError(f"Groq failed and no OpenAI fallback: {e}")

    import openai
    client = openai.OpenAI(api_key=oai_key)
    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=temperature,
    )
    return resp.choices[0].message.content
