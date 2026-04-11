from pydantic import BaseModel, Field, field_validator
from typing import Optional


class RegexExtractRequest(BaseModel):
    text: str = Field(
        ...,
        description="The input text to search through.",
        examples=["Call me at 0712345678 or email me at jay@example.com"],
    )
    pattern: str = Field(
        ...,
        description="The regex pattern to match against the text.",
        examples=[r"\+?[0-9][\d\s\-\(\)]{5,}[0-9]"],
    )
    return_array: bool = Field(
        ...,
        description=(
            "Controls the shape of the result. "
            "`true` — return all matches as an array. "
            "`false` — return only the first match as a single string (or null if no match)."
        ),
        examples=[True],
    )
    case_insensitive: bool = Field(
        False,
        description="Match regardless of upper/lower case. Default `false`.",
    )
    multiline: bool = Field(
        False,
        description=(
            "Makes `^` and `$` match the start/end of each line instead of the whole string. "
            "Default `false`."
        ),
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "text": "Call me at 0712 345 678 or email jay@example.com",
                "pattern": r"\+?[0-9][\d\s\-\(\)]{5,}[0-9]",
                "return_array": True,
                "case_insensitive": False,
                "multiline": False,
            }
        }
    }


class RegexExtractResponse(BaseModel):
    matched: bool = Field(..., description="Whether any match was found.")
    result: Optional[str | list[str]] = Field(
        None,
        description=(
            "If `return_array` was `true`: an array of all matched strings (empty array if no match). "
            "If `return_array` was `false`: the first matched string, or `null` if no match."
        ),
    )
    match_count: int = Field(..., description="Total number of matches found.")
    pattern: str = Field(..., description="The regex pattern that was applied.")


class RegexReplaceRequest(BaseModel):
    text: str = Field(
        ...,
        description="The input text to process.",
        examples=["Hi, call me on 0712 345 678 or email jay@example.com to arrange directly."],
    )
    pattern: str = Field(
        ...,
        description="The regex pattern identifying what to replace.",
        examples=[r"\+?[0-9][\d\s\-\(\)]{5,}[0-9]"],
    )
    replacement: str = Field(
        "",
        description=(
            "The string to substitute in place of each match. "
            "Defaults to `\"\"` which removes the matched text entirely. "
            "Common values: `\"[REDACTED]\"`, `\"***\"`, `\"\"`."
        ),
        examples=["[REDACTED]"],
    )
    case_insensitive: bool = Field(
        False,
        description="Match regardless of upper/lower case. Default `false`.",
    )
    multiline: bool = Field(
        False,
        description=(
            "Makes `^` and `$` match the start/end of each line instead of the whole string. "
            "Default `false`."
        ),
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "text": "Hi, call me on 0712 345 678 or email jay@example.com to arrange directly.",
                "pattern": r"(\+?[0-9][\d\s\-\(\)]{5,}[0-9]|\S+@\S+\.\S+)",
                "replacement": "[REDACTED]",
                "case_insensitive": True,
                "multiline": False,
            }
        }
    }


class RegexReplaceResponse(BaseModel):
    result: str = Field(..., description="The text after all replacements have been applied.")
    replacement_count: int = Field(..., description="Number of substitutions made.")
    original_text: str = Field(..., description="The original text before any changes.")
    pattern: str = Field(..., description="The regex pattern that was applied.")
