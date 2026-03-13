import json
import logging

from app.config import get_openai_client, get_settings

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """You are an intent classifier for an AI data analyst system.

You will receive the recent conversation history (if any) followed by the user's latest question.
Use the conversation context to understand follow-up questions.

Classify the user's LATEST question into exactly one category:

1. "database_query" – Questions about data that require querying a database
   (analytics, reports, statistics, counts, aggregations, trends, comparisons,
   salary data, employee counts, sales figures, etc.)
2. "rag_query" – Questions about company policies, procedures, uploaded
   documents, HR knowledge, onboarding guides, or any document-specific
   information.
3. "greeting" – ONLY simple greetings and small talk: "hello", "hi", "hey",
   "how are you", "good morning/afternoon/evening", "what's up", "howdy".
   Nothing else. If the user asks for help or capabilities, that is NOT greeting.
4. "general_question" – Anything that is not database_query, rag_query, or greeting.
   This includes: "what is X", "explain Y", help requests, capability questions,
   or any question that would require general knowledge. The assistant will
   politely decline and direct the user to ask about data or documents only.

Respond with ONLY a JSON object: {"intent": "<category>"}"""

_MAX_CONTEXT_FOR_INTENT = 6
_VALID_INTENTS = {"database_query", "rag_query", "greeting", "general_question"}


def classify_intent(state: dict) -> dict:
    """Classify the user's question into database_query / rag_query / general_question."""
    question = state["question"]
    logger.info("Classifying intent for: %s", question[:100])

    history = state.get("conversation_history") or []
    context_msgs = [
        {"role": m.get("role"), "content": m.get("content", "")}
        for m in history[-_MAX_CONTEXT_FOR_INTENT:]
        if m.get("role") and m.get("content")
    ]
    logger.info("Intent classifier received %d context messages", len(context_msgs))

    try:
        client = get_openai_client()
        settings = get_settings()

        response = client.chat.completions.create(
            model=settings.model_name,
            temperature=0.0,
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                *context_msgs,
                {"role": "user", "content": question},
            ],
            response_format={"type": "json_object"},
        )

        result = json.loads(response.choices[0].message.content)
        intent = result.get("intent", "general_question")

        if intent not in _VALID_INTENTS:
            logger.warning("LLM returned unknown intent '%s', defaulting to general_question", intent)
            intent = "general_question"

        logger.info("Intent classified as: %s", intent)
        return {"intent": intent}

    except Exception as e:
        logger.exception("Intent classification failed")
        return {"intent": "general_question", "error": str(e)}
