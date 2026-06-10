from typing import Any

from pydantic import BaseModel, Field


class FileConvertResponse(BaseModel):
    rows: list[dict[str, Any]] = Field(
        ...,
        description="The parsed data as an array of row objects, one per row.",
        examples=[[{"Name": "Alice", "Email": "alice@example.com"}]],
    )
    row_count: int = Field(..., description="Number of rows returned.")
    columns: list[str] = Field(
        ...,
        description="Column names (keys) in the order they appear.",
        examples=[["Name", "Email"]],
    )
    filename: str = Field(..., description="The original uploaded filename.")
    file_type: str = Field(..., description="Detected file type: 'csv' or 'xlsx'.")
