"""
Chat session and message persistence in PostgreSQL.
No browser memory: all sessions and messages stored in DB.
"""
import json
import logging
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import text

from app.database.connection import get_session

logger = logging.getLogger(__name__)


def _json_serial(obj):
    """Convert non-JSON-serializable types (e.g. Decimal, datetime) for json.dumps."""
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


def _ensure_tables(session):
    """Create chat_sessions and chat_messages tables if they do not exist."""
    session.execute(text("""
        CREATE TABLE IF NOT EXISTS chat_sessions (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            title VARCHAR(500) NOT NULL DEFAULT 'New chat',
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
    """))
    session.execute(text("""
        CREATE TABLE IF NOT EXISTS chat_messages (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            session_id UUID NOT NULL REFERENCES chat_sessions(id) ON DELETE CASCADE,
            role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
            content TEXT NOT NULL,
            payload JSONB,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        )
    """))
    session.execute(text("""
        CREATE INDEX IF NOT EXISTS idx_chat_messages_session_id ON chat_messages(session_id)
    """))
    session.execute(text("""
        CREATE INDEX IF NOT EXISTS idx_chat_sessions_updated_at ON chat_sessions(updated_at DESC)
    """))
    session.commit()


def list_sessions():
    """Return all chat sessions ordered by updated_at descending."""
    session = get_session()
    try:
        _ensure_tables(session)
        result = session.execute(text("""
            SELECT id, title, created_at, updated_at
            FROM chat_sessions
            ORDER BY updated_at DESC
        """))
        rows = result.fetchall()
        return [
            {
                "id": str(row[0]),
                "title": row[1],
                "created_at": row[2].isoformat() if row[2] else None,
                "updated_at": row[3].isoformat() if row[3] else None,
            }
            for row in rows
        ]
    finally:
        session.close()


def create_session(title: str = "New chat") -> dict:
    """Create a new chat session and return it."""
    session = get_session()
    try:
        _ensure_tables(session)
        result = session.execute(
            text("""
                INSERT INTO chat_sessions (title)
                VALUES (:title)
                RETURNING id, title, created_at, updated_at
            """),
            {"title": title},
        )
        row = result.fetchone()
        session.commit()
        return {
            "id": str(row[0]),
            "title": row[1],
            "created_at": row[2].isoformat() if row[2] else None,
            "updated_at": row[3].isoformat() if row[3] else None,
        }
    finally:
        session.close()


def get_session_with_messages(session_id: str) -> dict | None:
    """Get a session and its messages, or None if not found."""
    session = get_session()
    try:
        _ensure_tables(session)
        row = session.execute(
            text("""
                SELECT id, title, created_at, updated_at
                FROM chat_sessions WHERE id = :id
            """),
            {"id": session_id},
        ).fetchone()
        if not row:
            return None
        messages_result = session.execute(
            text("""
                SELECT id, role, content, payload, created_at
                FROM chat_messages
                WHERE session_id = :session_id
                ORDER BY created_at ASC
            """),
            {"session_id": session_id},
        )
        messages = []
        for m in messages_result.fetchall():
            payload = m[3]  # JSONB: driver may return dict or str
            if isinstance(payload, str):
                try:
                    payload = json.loads(payload)
                except (ValueError, TypeError):
                    payload = None
            elif isinstance(payload, dict):
                payload = dict(payload)
            messages.append({
                "id": str(m[0]),
                "role": m[1],
                "content": m[2],
                "payload": payload,
                "created_at": m[4].isoformat() if m[4] else None,
            })
        return {
            "id": str(row[0]),
            "title": row[1],
            "created_at": row[2].isoformat() if row[2] else None,
            "updated_at": row[3].isoformat() if row[3] else None,
            "messages": messages,
        }
    finally:
        session.close()


def delete_session(session_id: str) -> bool:
    """Delete a session and all its messages. Returns True if deleted, False if not found."""
    session = get_session()
    try:
        _ensure_tables(session)
        result = session.execute(
            text("DELETE FROM chat_sessions WHERE id = :id"),
            {"id": session_id},
        )
        session.commit()
        return result.rowcount > 0
    finally:
        session.close()


def append_message(session_id: str, role: str, content: str, payload: dict | None = None) -> bool:
    """Append a message to a session and bump updated_at. Returns True if session exists."""
    session = get_session()
    try:
        _ensure_tables(session)
        # Check session exists
        row = session.execute(
            text("SELECT id FROM chat_sessions WHERE id = :id"),
            {"id": session_id},
        ).fetchone()
        if not row:
            return False
        payload_json = (
            json.dumps(payload, default=_json_serial) if payload is not None else None
        )
        session.execute(
            text("""
                INSERT INTO chat_messages (session_id, role, content, payload)
                VALUES (:session_id, :role, :content, CAST(:payload AS jsonb))
            """),
            {
                "session_id": session_id,
                "role": role,
                "content": content,
                "payload": payload_json,
            },
        )
        # Update updated_at always; set title from user messages only (sidebar shows last question)
        if role == "user" and content:
            session.execute(
                text("UPDATE chat_sessions SET updated_at = now(), title = :title WHERE id = :id"),
                {"id": session_id, "title": content[:500]},
            )
        else:
            session.execute(
                text("UPDATE chat_sessions SET updated_at = now() WHERE id = :id"),
                {"id": session_id},
            )
        session.commit()
        return True
    finally:
        session.close()


def update_session_title(session_id: str, title: str) -> bool:
    """Set session title (e.g. from first user message). Returns True if updated."""
    session = get_session()
    try:
        _ensure_tables(session)
        result = session.execute(
            text("UPDATE chat_sessions SET updated_at = now(), title = :title WHERE id = :id"),
            {"id": session_id, "title": title[:500]},
        )
        session.commit()
        return result.rowcount > 0
    finally:
        session.close()
