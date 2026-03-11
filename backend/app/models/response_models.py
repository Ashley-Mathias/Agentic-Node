from typing import Optional

from pydantic import BaseModel


class QueryResponse(BaseModel):
    type: str
    chart_type: Optional[str] = None
    chart_data: Optional[dict] = None
    chart_image: Optional[str] = None
    table: Optional[list[dict]] = None
    summary: str
    sql_query: Optional[str] = None
    error: Optional[str] = None


class UploadResponse(BaseModel):
    filename: str
    chunks_stored: int
    message: str
