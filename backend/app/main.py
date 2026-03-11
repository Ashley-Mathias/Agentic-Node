import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes_query import router as query_router
from app.api.routes_upload import router as upload_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: pre-load schema and compile the LangGraph pipeline."""
    logger.info("Application starting up …")

    try:
        from app.database.schema_loader import get_schema
        schema = get_schema()
        logger.info("Database schema loaded: %s", list(schema.keys()))
    except Exception as e:
        logger.warning("Could not load database schema on startup: %s", e)
        logger.warning("Schema will be loaded lazily on first query")

    try:
        from app.langgraph.graph_builder import get_graph
        get_graph()
        logger.info("LangGraph pipeline compiled")
    except Exception as e:
        logger.warning("Could not compile LangGraph pipeline on startup: %s", e)

    yield

    logger.info("Application shutting down …")


app = FastAPI(
    title="AI Data Analyst & HR Knowledge Assistant",
    description=(
        "LangGraph-powered REST API for natural-language database queries, "
        "automated charting, and document-based Q&A (RAG)."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(query_router, prefix="/api")
app.include_router(upload_router, prefix="/api")


@app.get("/health")
async def health_check():
    """Liveness probe."""
    return {"status": "healthy", "service": "ai-analyst-backend"}
