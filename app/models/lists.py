from typing import Optional

from fastapi import HTTPException
from pydantic import BaseModel, Field, field_validator


class RandomPickRequest(BaseModel):
    items: list[str] = Field(
        ...,
        description="List of IDs/items to pick from.",
        examples=[["rec_1", "rec_2", "rec_3", "rec_4"]],
    )
    count: int = Field(
        ...,
        description="How many items to pick. Must be > 0.",
        gt=0,
        examples=[3],
    )
    allow_duplicates: bool = Field(
        False,
        description=(
            "If `true`, picks may repeat and `count` may exceed the number of items. "
            "If `false`, picks are unique; if count >= items length, all items are returned (shuffled)."
        ),
        examples=[False],
    )
    seed: Optional[int] = Field(
        None,
        description="Optional random seed for deterministic results (useful for testing/workflows).",
        examples=[12345],
    )

    @field_validator("items")
    @classmethod
    def validate_items(cls, v: list[str]) -> list[str]:
        cleaned = [s.strip() for s in v if isinstance(s, str) and s.strip()]
        if not cleaned:
            raise HTTPException(
                status_code=422,
                detail="items must contain at least one non-empty string.",
            )
        return cleaned

    model_config = {
        "json_schema_extra": {
            "example": {
                "items": ["rec_1", "rec_2", "rec_3", "rec_4", "rec_5"],
                "count": 3,
                "allow_duplicates": False,
                "seed": 42,
            }
        }
    }


class RandomPickResponse(BaseModel):
    picks: list[str] = Field(..., description="The randomly selected items.")
    count_requested: int = Field(..., description="The requested number of picks.")
    count_returned: int = Field(..., description="How many picks were actually returned.")
    input_size: int = Field(..., description="Number of items after cleanup.")
    allow_duplicates: bool = Field(..., description="Whether duplicates were allowed.")
    seed: Optional[int] = Field(None, description="The seed used (if any).")

