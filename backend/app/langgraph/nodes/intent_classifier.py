import json
import logging

from app.config import get_openai_client, get_settings

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """You are an intent classifier for an AI data analyst system.

Classify the user's question into exactly one category:

1. "database_query" – Questions about data that require querying a database
   (analytics, reports, statistics, counts, aggregations, trends, comparisons,
   salary data, employee counts, sales figures, etc.)
2. "rag_query" – Questions about company policies, procedures, uploaded
   documents, HR knowledge, onboarding guides, or any document-specific
   information.
3. "general_question" – General greetings, help requests, capability questions,
   or anything not clearly about data or documents.

Respond with ONLY a JSON object: {"intent": "<category>"}"""

_VALID_INTENTS = {"database_query", "rag_query", "general_question"}


def classify_intent(state: dict) -> dict:
    """Classify the user's question into database_query / rag_query / general_question."""
    question = state["question"]
    logger.info("Classifying intent for: %s", question[:100])

    try:
        client = get_openai_client()
        settings = get_settings()

        response = client.chat.completions.create(
            model=settings.model_name,
            temperature=0.0,
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
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
