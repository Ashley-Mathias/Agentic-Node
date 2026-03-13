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

# Max number of prior messages to send as context (avoid token overflow).
_MAX_CONTEXT_MESSAGES = 10


def _context_messages(state: dict) -> list:
    """Build list of prior conversation messages for LLM context (last N only)."""
    history = state.get("conversation_history") or []
    if not history:
        logger.debug("No conversation history in state")
        return []
    msgs = [{"role": m.get("role"), "content": m.get("content", "")} for m in history[-_MAX_CONTEXT_MESSAGES:] if m.get("role") and m.get("content")]
    logger.info("Response generator injecting %d context messages into LLM", len(msgs))
    return msgs


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
        if intent == "greeting":
            return _greeting_response(state)
        return _general_question_decline(state)

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
    messages = [
        {"role": "system", "content": "Generate a concise data summary."},
        *_context_messages(state),
        {
            "role": "user",
            "content": _SUMMARY_PROMPT.format(
                question=state["question"],
                columns=query_columns,
                preview=preview,
                total_rows=len(query_result),
            ),
        },
    ]
    llm_resp = client.chat.completions.create(
        model=settings.model_name,
        temperature=0.3,
        messages=messages,
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

    messages = [
        {"role": "system", "content": _RAG_PROMPT.format(context=context)},
        *_context_messages(state),
        {"role": "user", "content": state["question"]},
    ]
    llm_resp = client.chat.completions.create(
        model=settings.model_name,
        temperature=0.2,
        messages=messages,
    )
    answer = llm_resp.choices[0].message.content.strip()

    return {"final_response": {"type": "rag", "summary": answer}}


def _greeting_response(state: dict) -> dict:
    """Short friendly reply for greetings only. No LLM call."""
    summary = (
        "Hello! I'm here to help with questions about your data and uploaded documents. "
        "You can ask for analytics (e.g. salary by department) or ask about policies and docs you've uploaded."
    )
    return {"final_response": {"type": "text", "summary": summary}}


def _general_question_decline(state: dict) -> dict:
    """Politely decline general knowledge questions; only RAG and database queries allowed."""
    summary = (
        "I can only answer questions about your data (e.g. reports, analytics, trends) "
        "and your uploaded documents (e.g. policies, HR guides). "
        "Try something like: \"Show employee salary by department\" or \"What is our vacation policy?\""
    )
    return {"final_response": {"type": "text", "summary": summary}}
