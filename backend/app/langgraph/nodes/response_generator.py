import json
import logging

from app.config import get_openai_client, get_settings

logger = logging.getLogger(__name__)

_SUMMARY_PROMPT = """You are a data analyst assistant. Write a clear, concise natural
language summary of the query results.

Guidelines:
- 2-3 sentences highlighting key findings.
- Mention concrete numbers, trends, or outliers.
- Professional tone; no SQL or technical jargon.

Question: {question}
Columns: {columns}
Result preview (first rows): {preview}
Total rows: {total_rows}"""

_RAG_PROMPT = """Answer the user's question using ONLY the provided document context.

Context:
{context}

Guidelines:
- Base your answer strictly on the context.
- If the context is insufficient, say so explicitly.
- Be specific and cite relevant details.
- Keep the answer concise but complete."""

_GENERAL_PROMPT = """You are a helpful AI assistant for a data analytics and HR knowledge
system. You can help with:
1. Querying databases using natural language
2. Answering questions from uploaded documents
3. General assistance

Respond helpfully to the user's question."""


def generate_response(state: dict) -> dict:
    """Compile all upstream outputs into a final JSON response."""
    intent = state.get("intent", "general_question")
    error = state.get("error")

    if error:
        return {
            "final_response": {
                "type": "error",
                "summary": f"An error occurred while processing your request: {error}",
                "error": error,
            }
        }

    try:
        client = get_openai_client()
        settings = get_settings()

        if intent == "database_query":
            return _database_response(state, client, settings)
        if intent == "rag_query":
            return _rag_response(state, client, settings)
        return _general_response(state, client, settings)

    except Exception as e:
        logger.exception("Response generation failed")
        return {
            "final_response": {
                "type": "error",
                "summary": f"Failed to generate response: {e}",
                "error": str(e),
            }
        }


# ---------------------------------------------------------------------------
# Private builders
# ---------------------------------------------------------------------------

def _database_response(state: dict, client, settings) -> dict:
    query_result = state.get("query_result", [])
    query_columns = state.get("query_columns", [])
    chart_type = state.get("chart_type", "table")

    preview = json.dumps(query_result[:10], default=str)
    llm_resp = client.chat.completions.create(
        model=settings.model_name,
        temperature=0.3,
        messages=[
            {"role": "system", "content": "Generate a concise data summary."},
            {
                "role": "user",
                "content": _SUMMARY_PROMPT.format(
                    question=state["question"],
                    columns=query_columns,
                    preview=preview,
                    total_rows=len(query_result),
                ),
            },
        ],
    )
    summary = llm_resp.choices[0].message.content.strip()

    resp: dict = {
        "type": "chart" if chart_type in ("bar", "line", "pie") else chart_type,
        "chart_type": chart_type,
        "summary": summary,
        "table": query_result,
        "sql_query": state.get("sql_query", ""),
    }

    if state.get("chart_data"):
        resp["chart_data"] = state["chart_data"]
    if state.get("chart_image"):
        resp["chart_image"] = state["chart_image"]

    return {"final_response": resp}


def _rag_response(state: dict, client, settings) -> dict:
    context = state.get("rag_context", "")

    llm_resp = client.chat.completions.create(
        model=settings.model_name,
        temperature=0.2,
        messages=[
            {"role": "system", "content": _RAG_PROMPT.format(context=context)},
            {"role": "user", "content": state["question"]},
        ],
    )
    answer = llm_resp.choices[0].message.content.strip()

    return {"final_response": {"type": "rag", "summary": answer}}


def _general_response(state: dict, client, settings) -> dict:
    llm_resp = client.chat.completions.create(
        model=settings.model_name,
        temperature=0.5,
        messages=[
            {"role": "system", "content": _GENERAL_PROMPT},
            {"role": "user", "content": state["question"]},
        ],
    )
    answer = llm_resp.choices[0].message.content.strip()

    return {"final_response": {"type": "text", "summary": answer}}
