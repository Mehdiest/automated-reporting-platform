"""
AI Insights Service
====================
Generates natural-language insights from a KPI dictionary.

If OPENAI_API_KEY is set, insights are produced by an OpenAI chat model.
Otherwise the service falls back to a deterministic, rule-based generator
so the feature remains fully functional (and testable) without any
external API access.
"""

import os
import logging
from typing import Any

logger = logging.getLogger(__name__)

_DEFAULT_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


def _fmt(value: Any) -> str:
    try:
        return f"{float(value):,.2f}"
    except (TypeError, ValueError):
        return str(value)


def _rule_based_insights(kpis: dict) -> dict:
    """Deterministic insights derived directly from KPI values."""
    points = []

    if kpis.get("total_revenue") is not None:
        points.append(f"Total revenue across the dataset is {_fmt(kpis['total_revenue'])}.")
    if kpis.get("average_order_value") is not None:
        points.append(f"The average order value is {_fmt(kpis['average_order_value'])}.")
    if kpis.get("top_product"):
        extra = (
            f" generating {_fmt(kpis['top_product_revenue'])} in revenue"
            if kpis.get("top_product_revenue") is not None else ""
        )
        points.append(f"'{kpis['top_product']}' is the top-performing product{extra}.")
    cat = kpis.get("revenue_by_category")
    if isinstance(cat, dict) and cat:
        leader = max(cat, key=cat.get)
        points.append(f"'{leader}' is the strongest category by revenue ({_fmt(cat[leader])}).")
    if kpis.get("total_customers"):
        points.append(f"The dataset covers {kpis['total_customers']} unique customers.")
    if kpis.get("total_orders"):
        points.append(f"A total of {kpis['total_orders']} orders were analysed.")

    if not points:
        points.append(
            "No revenue-related KPIs were detected; insights are limited to basic row and column counts."
        )

    return {
        "summary": " ".join(points),
        "insights": points,
        "source": "rule_based",
    }


def generate_insights(kpis: dict, model: str = _DEFAULT_MODEL) -> dict:
    """
    Produce insights for a KPI dictionary.

    Returns a dict: {"summary": str, "insights": list[str], "source": str}.
    Never raises — falls back to rule-based insights on any AI error.
    """
    api_key = os.getenv("OPENAI_API_KEY", "").strip()

    if not api_key:
        logger.info("OPENAI_API_KEY not set — using rule-based insight generator.")
        return _rule_based_insights(kpis)

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        prompt = (
            "You are a data analyst. Given the following KPI data from a sales "
            "dataset, write 3-5 concise, business-focused insights as short bullet "
            "points, then a one-sentence executive summary.\n\n"
            f"KPIs:\n{kpis}"
        )
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a concise business data analyst."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.4,
        )
        text = response.choices[0].message.content.strip()
        bullets = [line.strip("-• ").strip() for line in text.splitlines() if line.strip()]
        return {"summary": text, "insights": bullets, "source": model}

    except Exception as exc:  # network error, invalid key, quota, etc.
        logger.warning("AI insight generation failed (%s) — falling back to rule-based.", exc)
        result = _rule_based_insights(kpis)
        result["source"] = "rule_based_fallback"
        return result
