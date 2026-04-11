import re

from fastapi import APIRouter, HTTPException

from app.models.text import (
    RegexExtractRequest,
    RegexExtractResponse,
    RegexReplaceRequest,
    RegexReplaceResponse,
)

router = APIRouter(prefix="/text", tags=["Text Utilities"])


def _compile_pattern(pattern: str, case_insensitive: bool, multiline: bool) -> re.Pattern:
    """Compile a regex pattern with the requested flags, raising a clean 422 on invalid syntax."""
    flags = 0
    if case_insensitive:
        flags |= re.IGNORECASE
    if multiline:
        flags |= re.MULTILINE
    try:
        return re.compile(pattern, flags)
    except re.error as exc:
        raise HTTPException(
            status_code=422,
            detail=f"Invalid regex pattern: {exc}",
        )


@router.post(
    "/regex/extract",
    response_model=RegexExtractResponse,
    summary="Extract regex matches from text",
    description=(
        "Apply a regex pattern to a block of text and extract matches. \n\n"
        "Set `return_array: true` to get **all matches** as an array — useful for pulling "
        "every phone number or email out of a message. \n\n"
        "Set `return_array: false` to get only the **first match** as a single string "
        "(or `null` if nothing matched) — useful as a simple contains-check. \n\n"
        "Practical example: extract all phone numbers from a chat message before storing it."
    ),
)
async def regex_extract(body: RegexExtractRequest) -> RegexExtractResponse:
    compiled = _compile_pattern(body.pattern, body.case_insensitive, body.multiline)
    matches = compiled.findall(body.text)

    # findall returns a list of strings for simple patterns, or tuples for grouped patterns.
    # Flatten tuples to their first capture group so the response is always a list of strings.
    flat: list[str] = []
    for m in matches:
        flat.append(m[0] if isinstance(m, tuple) else m)

    matched = len(flat) > 0

    if body.return_array:
        result: str | list[str] | None = flat
    else:
        result = flat[0] if flat else None

    return RegexExtractResponse(
        matched=matched,
        result=result,
        match_count=len(flat),
        pattern=body.pattern,
    )


@router.post(
    "/regex/replace",
    response_model=RegexReplaceResponse,
    summary="Replace regex matches in text",
    description=(
        "Find all occurrences of a pattern in a text and replace them with a substitution string. \n\n"
        "Leave `replacement` empty (`\"\"`) to **remove** all matches entirely. \n\n"
        "Use `\"[REDACTED]\"` or `\"***\"` to **mask** sensitive content. \n\n"
        "Practical example: scrub phone numbers and email addresses from chat messages "
        "so users can't bypass your platform — inspired by a real request from the Adalo community. \n\n"
        "**Pattern for phone numbers + emails:** `(\\+?[0-9][\\d\\s\\-\\(\\)]{5,}[0-9]|\\S+@\\S+\\.\\S+)`"
    ),
)
async def regex_replace(body: RegexReplaceRequest) -> RegexReplaceResponse:
    compiled = _compile_pattern(body.pattern, body.case_insensitive, body.multiline)
    result, count = compiled.subn(body.replacement, body.text)

    return RegexReplaceResponse(
        result=result,
        replacement_count=count,
        original_text=body.text,
        pattern=body.pattern,
    )
