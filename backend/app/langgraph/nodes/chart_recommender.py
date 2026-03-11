import json
import logging

from app.config import get_openai_client, get_settings

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """You are a data-visualization expert. Given the user's question and a
preview of the query result, recommend the single best visualization.

Options:
- "bar"   : comparing discrete categories (departments, products, regions …)
- "line"  : time-series or sequential trend data
- "pie"   : proportions / percentages of a whole (best with ≤ 8 slices)
- "table" : detailed multi-column data, lists, or when no chart adds value
- "text"  : single scalar value, simple count, or yes/no answer

Also identify which columns to use for the axes / labels.

Respond with ONLY a JSON object:
{{"chart_type": "<type>",
  "x_column": "<column or null>",
  "y_column": "<column or null>",
  "label_column": "<column or null>"}}"""

_VALID_CHART_TYPES = {"bar", "line", "pie", "table", "text"}


def recommend_chart(state: dict) -> dict:
    """Determine the best visualization type for the query results."""
    if state.get("error"):
        return {}

    question = state["question"]
    query_result = state.get("query_result", [])
    query_columns = state.get("query_columns", [])

    if not query_result:
        return {"chart_type": "text"}

    if len(query_result) == 1 and len(query_columns) <= 2:
        return {
            "chart_type": "text",
            "x_column": None,
            "y_column": None,
            "label_column": None,
        }

    result_preview = {
        "columns": query_columns,
        "row_count": len(query_result),
        "sample_rows": query_result[:5],
    }

    try:
        client = get_openai_client()
        settings = get_settings()

        response = client.chat.completions.create(
            model=settings.model_name,
            temperature=0.0,
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": (
                        f"Question: {question}\n\n"
                        f"Result structure: {json.dumps(result_preview, default=str)}"
                    ),
                },
            ],
            response_format={"type": "json_object"},
        )

        result = json.loads(response.choices[0].message.content)
        chart_type = result.get("chart_type", "table")

        if chart_type not in _VALID_CHART_TYPES:
            chart_type = "table"

        logger.info("Recommended chart type: %s", chart_type)
        return {
            "chart_type": chart_type,
            "x_column": result.get("x_column"),
            "y_column": result.get("y_column"),
            "label_column": result.get("label_column"),
        }

    except Exception as e:
        logger.exception("Chart recommendation failed")
        return {"chart_type": "table"}
