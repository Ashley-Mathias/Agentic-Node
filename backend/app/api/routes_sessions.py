"""
REST API for chat sessions: list, create, get, delete.
All session/message memory lives in PostgreSQL; no browser storage.
"""
import asyncio
import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.database.chat_sessions import (
    list_sessions as db_list_sessions,
    create_session as db_create_session,
    get_session_with_messages as db_get_session,
    delete_session as db_delete_session,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Sessions"])


def _run_sync(sync_fn, *args, **kwargs):
    """Run sync DB calls in a thread pool so the event loop is not blocked."""
    return asyncio.to_thread(sync_fn, *args, **kwargs)


@router.get("/sessions")
async def get_sessions():
    """List all chat sessions for the sidebar, newest first."""
    try:
        sessions = await _run_sync(db_list_sessions)
        return {"sessions": sessions}
    except Exception as e:
        logger.exception("List sessions failed")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sessions")
async def create_session(title: Optional[str] = Query(default="New chat", description="Session title")):
    """Create a new chat session. Returns the new session (id, title, created_at, updated_at)."""
    try:
        session = await _run_sync(db_create_session, title=title or "New chat")
        return session
    except Exception as e:
        logger.exception("Create session failed")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sessions/{session_id}")
async def get_session(session_id: str):
    """Get one session with all messages (for loading into the chat view)."""
    try:
        session = await _run_sync(db_get_session, session_id)
        if session is None:
            raise HTTPException(status_code=404, detail="Session not found")
        return session
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Get session failed")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a session and all its messages from the database (sync)."""
    try:
        deleted = await _run_sync(db_delete_session, session_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Session not found")
        return {"ok": True}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Delete session failed")
        raise HTTPException(status_code=500, detail=str(e))
