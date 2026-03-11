import asyncio
import logging

from fastapi import APIRouter, HTTPException

from app.models.request_models import QueryRequest
from app.models.response_models import QueryResponse
from app.langgraph.graph_builder import get_graph
from app.database.schema_loader import get_schema

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Query"])


def _run_pipeline(question: str) -> dict:
    """Invoke the LangGraph pipeline synchronously (called via thread-pool)."""
    graph = get_graph()

    initial_state = {
        "question": question,
        "intent": "",
        "db_schema": get_schema(),
        "sql_query": "",
        "sql_explanation": "",
        "query_result": [],
        "query_columns": [],
        "chart_type": "",
        "chart_data": {},
        "chart_image": "",
        "x_column": "",
        "y_column": "",
        "label_column": "",
        "text_summary": "",
        "rag_context": "",
        "final_response": {},
        "error": "",
    }

    return graph.invoke(initial_state)


@router.post("/query", response_model=QueryResponse)
async def query_endpoint(request: QueryRequest):
    """Process a natural-language query through the AI analysis pipeline."""
    logger.info("Received query: %s", request.question[:100])

    try:
        result = await asyncio.to_thread(_run_pipeline, request.question)
        resp = result.get("final_response", {})

        return QueryResponse(
            type=resp.get("type", "text"),
            chart_type=resp.get("chart_type"),
            chart_data=resp.get("chart_data"),
            chart_image=resp.get("chart_image"),
            table=resp.get("table"),
            summary=resp.get("summary", "No response generated"),
            sql_query=resp.get("sql_query"),
            error=resp.get("error"),
        )

    except Exception as e:
        logger.exception("Query processing failed")
        raise HTTPException(status_code=500, detail=str(e))
