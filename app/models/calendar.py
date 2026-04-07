from pydantic import BaseModel, Field, field_validator
from typing import Optional


class CalendarLinkByRangeRequest(BaseModel):
    title: str = Field(
        ...,
        description="Event title",
        examples=["Project Sync Meeting"],
    )
    start_datetime: str = Field(
        ...,
        description=(
            "Event start datetime. Accepts most common formats: ISO 8601 "
            "('2026-03-15T14:00:00'), with UTC offset ('2026-03-15T14:00:00+03:00'), "
            "or with Z suffix ('2026-03-15T11:00:00Z'). "
            "If no timezone info is included, the `timezone` field is used."
        ),
        examples=["2026-03-15T14:00:00"],
    )
    end_datetime: str = Field(
        ...,
        description="Event end datetime. Same format rules as start_datetime.",
        examples=["2026-03-15T15:00:00"],
    )
    details: Optional[str] = Field(
        None,
        description="Event description / notes.",
        examples=["Review Q1 roadmap and finalize launch dates."],
    )
    location: Optional[str] = Field(
        None,
        description="Event location (physical address or virtual meeting link).",
        examples=["Conference Room A"],
    )
    timezone: str = Field(
        "UTC",
        description=(
            "IANA timezone name. Used when datetime strings don't include timezone info. "
            "Also sets the calendar display timezone (ctz)."
        ),
        examples=["Africa/Nairobi", "America/New_York", "Europe/London", "UTC"],
    )
    attendees: Optional[list[str]] = Field(
        None,
        description="List of attendee email addresses to pre-fill on the event.",
        examples=[["alice@example.com", "bob@example.com"]],
    )

    @field_validator("attendees")
    @classmethod
    def validate_attendees(cls, v: Optional[list[str]]) -> Optional[list[str]]:
        if v is None:
            return v
        cleaned = [email.strip() for email in v if email.strip()]
        if not cleaned:
            return None
        for email in cleaned:
            if "@" not in email or "." not in email.split("@")[-1]:
                raise ValueError(f"Invalid email address: '{email}'")
        return cleaned

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "Project Sync Meeting",
                "start_datetime": "2026-03-15T14:00:00",
                "end_datetime": "2026-03-15T15:00:00",
                "details": "Review Q1 roadmap and finalize launch dates.",
                "location": "Conference Room A",
                "timezone": "Africa/Nairobi",
                "attendees": ["alice@example.com", "bob@example.com"],
            }
        }
    }


class CalendarLinkByDurationRequest(BaseModel):
    title: str = Field(
        ...,
        description="Event title",
        examples=["Project Sync Meeting"],
    )
    start_datetime: str = Field(
        ...,
        description=(
            "Event start datetime. Accepts most common formats: ISO 8601 "
            "('2026-03-15T14:00:00'), with UTC offset ('2026-03-15T14:00:00+03:00'), "
            "or with Z suffix ('2026-03-15T11:00:00Z'). "
            "If no timezone info is included, the `timezone` field is used."
        ),
        examples=["2026-03-15T14:00:00"],
    )
    duration_minutes: int = Field(
        ...,
        description="Event duration in minutes. E.g. 30 = 30 min, 60 = 1 hour, 90 = 1.5 hours.",
        examples=[60],
        gt=0,
    )
    details: Optional[str] = Field(
        None,
        description="Event description / notes.",
        examples=["Review Q1 roadmap and finalize launch dates."],
    )
    location: Optional[str] = Field(
        None,
        description="Event location (physical address or virtual meeting link).",
        examples=["Conference Room A"],
    )
    timezone: str = Field(
        "UTC",
        description=(
            "IANA timezone name. Used when datetime strings don't include timezone info. "
            "Also sets the calendar display timezone (ctz)."
        ),
        examples=["Africa/Nairobi", "America/New_York", "Europe/London", "UTC"],
    )
    attendees: Optional[list[str]] = Field(
        None,
        description="List of attendee email addresses to pre-fill on the event.",
        examples=[["alice@example.com", "bob@example.com"]],
    )

    @field_validator("attendees")
    @classmethod
    def validate_attendees(cls, v: Optional[list[str]]) -> Optional[list[str]]:
        if v is None:
            return v
        cleaned = [email.strip() for email in v if email.strip()]
        if not cleaned:
            return None
        for email in cleaned:
            if "@" not in email or "." not in email.split("@")[-1]:
                raise ValueError(f"Invalid email address: '{email}'")
        return cleaned

    model_config = {
        "json_schema_extra": {
            "example": {
                "title": "Project Sync Meeting",
                "start_datetime": "2026-03-15T14:00:00",
                "duration_minutes": 60,
                "details": "Review Q1 roadmap and finalize launch dates.",
                "location": "Conference Room A",
                "timezone": "Africa/Nairobi",
                "attendees": ["alice@example.com", "bob@example.com"],
            }
        }
    }


class CalendarLinkResponse(BaseModel):
    url: str = Field(
        ...,
        description="The fully formatted Google Calendar add-event URL. Redirect users to this link.",
    )
    title: str = Field(..., description="Event title as provided.")
    start_utc: str = Field(..., description="Computed start time in UTC (ISO 8601).")
    end_utc: str = Field(..., description="Computed end time in UTC (ISO 8601).")
    duration_minutes: int = Field(..., description="Total event duration in minutes.")
