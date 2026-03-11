import logging
from typing import Optional

from sqlalchemy import inspect

from app.database.connection import get_engine

logger = logging.getLogger(__name__)

_cached_schema: Optional[dict] = None


def load_schema() -> dict:
    """Introspect all tables from the PostgreSQL database and return a structured schema dict."""
    engine = get_engine()
    inspector = inspect(engine)
    schema: dict = {}

    for table_name in inspector.get_table_names():
        columns = []
        for col in inspector.get_columns(table_name):
            columns.append({
                "name": col["name"],
                "type": str(col["type"]),
                "nullable": col.get("nullable", True),
            })

        pk = inspector.get_pk_constraint(table_name)
        fks = inspector.get_foreign_keys(table_name)

        schema[table_name] = {
            "columns": columns,
            "primary_key": pk.get("constrained_columns", []),
            "foreign_keys": [
                {
                    "column": fk["constrained_columns"],
                    "references_table": fk["referred_table"],
                    "references_columns": fk["referred_columns"],
                }
                for fk in fks
            ],
        }

    logger.info("Loaded schema for %d tables: %s", len(schema), list(schema.keys()))
    return schema


def get_schema() -> dict:
    """Return the cached database schema, loading it on first call."""
    global _cached_schema
    if _cached_schema is None:
        _cached_schema = load_schema()
    return _cached_schema


def refresh_schema() -> dict:
    """Force-reload the database schema."""
    global _cached_schema
    _cached_schema = load_schema()
    return _cached_schema


def format_schema_for_llm(schema: dict) -> str:
    """Format schema as a readable string for inclusion in LLM prompts.

    Only exposes table names, column names, types, and relationships --
    never actual row data.
    """
    lines: list[str] = []
    for table_name, info in schema.items():
        cols = ", ".join(f"{c['name']} ({c['type']})" for c in info["columns"])
        lines.append(f"Table: {table_name}")
        lines.append(f"  Columns: {cols}")
        lines.append(f"  Primary Key: {info['primary_key']}")

        for fk in info["foreign_keys"]:
            lines.append(
                f"  FK: {fk['column']} -> {fk['references_table']}({fk['references_columns']})"
            )
        lines.append("")

    return "\n".join(lines)
