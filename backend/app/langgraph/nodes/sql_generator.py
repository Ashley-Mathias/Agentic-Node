import json
import logging

from app.config import get_openai_client, get_settings
from app.database.schema_loader import get_schema, format_schema_for_llm

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """You are a PostgreSQL SQL expert. Generate a single SQL query to
answer the user's question.

STRICT RULES:
- Generate ONLY a SELECT query. Never INSERT, UPDATE, DELETE, DROP, or any DDL.
- Use ONLY tables and columns from the provided schema.
- Use proper PostgreSQL syntax and standard SQL.
- Include appropriate JOINs when data spans multiple tables.
- Use clear aliases for readability.
- Add LIMIT 500 unless the user explicitly requests all rows.
- For aggregations, always include GROUP BY.
- Order results meaningfully (e.g. DESC for top-N, chronological for time series).

Respond with ONLY a JSON object:
{{"sql": "<your SQL query>", "explanation": "<one-line explanation>"}}

DATABASE SCHEMA:
{schema}"""


def generate_sql(state: dict) -> dict:
    """Generate a PostgreSQL SELECT query from the user's natural-language question.

    Uses only the database schema -- never actual row data -- in accordance
    with the security rule.
    """
    question = state["question"]
    schema = state.get("db_schema") or get_schema()
    schema_text = format_schema_for_llm(schema)

    logger.info("Generating SQL for: %s", question[:100])

    try:
        client = get_openai_client()
        settings = get_settings()

        response = client.chat.completions.create(
            model=settings.model_name,
            temperature=0.0,
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT.format(schema=schema_text)},
                {"role": "user", "content": question},
            ],
            response_format={"type": "json_object"},
        )

        result = json.loads(response.choices[0].message.content)
        sql_query = result.get("sql", "").strip()
        explanation = result.get("explanation", "")

        if not sql_query:
            return {"error": "LLM returned an empty SQL query"}

        logger.info("Generated SQL: %s", sql_query[:150])
        return {"sql_query": sql_query, "sql_explanation": explanation}

    except Exception as e:
        logger.exception("SQL generation failed")
        return {"error": f"SQL generation failed: {e}"}
