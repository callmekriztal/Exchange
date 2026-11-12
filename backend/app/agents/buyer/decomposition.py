import json
from typing import Any, Dict, List
from pydantic import BaseModel, Field
from app.core.config import settings


class DecomposedTask(BaseModel):
    title: str
    description: str
    service_type: str  # 'research', 'analysis', 'report'
    allocated_budget_usd: float
    sequence_order: int
    input_payload: Dict[str, Any] = {}


class GoalDecompositionPlan(BaseModel):
    tasks: List[DecomposedTask] = Field(..., min_items=1, max_items=5)


async def decompose_goal_llm(
    title: str,
    description: str,
    max_budget_usd: float,
) -> List[Dict[str, Any]]:
    """Decomposes an objective into structured subtasks within the allocated budget."""
    # If a live OpenAI API key is configured and not mock, invoke OpenAI
    if settings.OPENAI_API_KEY and not settings.OPENAI_API_KEY.startswith("mock"):
        try:
            from openai import AsyncOpenAI
            client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

            system_prompt = (
                "You are the Apex Buyer Agent in an autonomous agent marketplace. "
                "Decompose the user's objective into three sequential subtasks: "
                "1. 'research' (Web research, data gathering) "
                "2. 'analysis' (Quantitative calculation, trends) "
                "3. 'report' (Executive brief compilation) "
                f"Ensure the sum of allocated_budget_usd across all tasks is strictly <= {max_budget_usd:.2f}."
            )

            user_prompt = f"Objective Title: {title}\nObjective Description: {description}\nMax Budget: ${max_budget_usd:.2f}"

            completion = await client.beta.chat.completions.parse(
                model=settings.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                response_format=GoalDecompositionPlan,
            )
            parsed: GoalDecompositionPlan = completion.choices[0].message.parsed
            return [task.model_dump() for task in parsed.tasks]
        except Exception as e:
            print(f"[BuyerAgent] OpenAI decomposition call failed: {e}. Falling back to deterministic decomposition.")

    # High-precision deterministic decomposition fallback
    # Divides the budget roughly 30% research, 30% analysis, 40% report
    r_budget = round(max_budget_usd * 0.30, 2)
    a_budget = round(max_budget_usd * 0.30, 2)
    rep_budget = round(max_budget_usd - (r_budget + a_budget), 2)

    return [
        {
            "title": f"Market & Domain Intelligence: {title}",
            "description": f"Gather primary sources, industry data, and key metrics regarding {description[:100]}...",
            "service_type": "research",
            "allocated_budget_usd": r_budget,
            "sequence_order": 1,
            "input_payload": {"topic": title, "query": f"{title} trends and statistics", "depth": "thorough"},
        },
        {
            "title": f"Quantitative Metrics & Trend Analysis: {title}",
            "description": f"Perform statistical calculations, growth CAGR, and quantitative projections based on research findings.",
            "service_type": "analysis",
            "allocated_budget_usd": a_budget,
            "sequence_order": 2,
            "input_payload": {"metrics": ["cagr", "growth_rate", "variance"], "time_horizon": "5_year"},
        },
        {
            "title": f"Executive Synthesis & Strategic Report: {title}",
            "description": f"Synthesize research findings and statistical insights into a publication-ready executive summary and report.",
            "service_type": "report",
            "allocated_budget_usd": rep_budget,
            "sequence_order": 3,
            "input_payload": {"format": "markdown", "include_executive_summary": True},
        },
    ]
