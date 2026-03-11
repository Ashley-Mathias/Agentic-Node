import re
import logging

from sqlalchemy import text

from app.database.connection import get_session
from app.config import get_settings

logger = logging.getLogger(__name__)

_FORBIDDEN_PATTERNS = [
    r"\bDROP\b",
    r"\bDELETE\b",
    r"\bUPDATE\b",
    r"\bINSERT\b",
    r"\bALTER\b",
    r"\bCREATE\b",
    r"\bTRUNCATE\b",
    r"\bGRANT\b",
    r"\bREVOKE\b",
    r"\bEXEC\b",
    r"\bEXECUTE\b",
]


def validate_sql(sql: str) -> tuple[bool, str]:
    """Validate that *sql* is a read-only SELECT statement.

    Returns (is_valid, message).
    """
    cleaned = sql.strip().rstrip(";")
    upper = cleaned.upper()

    if not upper.startswith("SELECT"):
        return False, "Only SELECT queries are allowed"

    for pattern in _FORBIDDEN_PATTERNS:
        if re.search(pattern, upper):
            keyword = pattern.replace(r"\b", "")
            return False, f"Forbidden keyword detected: {keyword}"

    if ";" in cleaned:
        return False, "Multiple statements are not allowed"

    return True, "Valid"


def execute_sql(sql: str) -> tuple[list[dict], list[str]]:
    """Execute a validated SQL query and return (rows_as_dicts, column_names).

    Raises ValueError if SQL validation fails or a generic Exception on
    database errors.
    """
    is_valid, message = validate_sql(sql)
    if not is_valid:
        raise ValueError(f"SQL validation failed: {message}")

    settings = get_settings()
    session = get_session()
    try:
        result = session.execute(text(sql))
        columns = list(result.keys())
        rows = [
            dict(zip(columns, row))
            for row in result.fetchmany(settings.max_query_rows)
        ]
        logger.info("Query returned %d rows, %d columns", len(rows), len(columns))
        return rows, columns
    except Exception:
        logger.exception("SQL execution error")
        raise
    finally:
        session.close()
