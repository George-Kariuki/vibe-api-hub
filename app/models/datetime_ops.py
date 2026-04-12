from typing import Literal, Optional
from pydantic import BaseModel, Field


class DatetimeShiftRequest(BaseModel):
    datetime: str = Field(
        ...,
        description="The starting datetime in ISO 8601 or any common format.",
        examples=["2026-03-15T14:00:00"],
    )
    direction: Literal["add", "subtract"] = Field(
        ...,
        description="`add` to move forward in time, `subtract` to move backward.",
        examples=["add"],
    )
    amount: int = Field(
        ...,
        description="The quantity to add or subtract.",
        examples=[30],
        gt=0,
    )
    unit: Literal["seconds", "minutes", "hours", "days", "weeks", "months", "years"] = Field(
        ...,
        description="The time unit for the shift.",
        examples=["minutes"],
    )
    timezone: str = Field(
        "UTC",
        description="IANA timezone of the input datetime. Default `UTC`.",
        examples=["Africa/Nairobi", "America/New_York", "UTC"],
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "datetime": "2026-03-15T14:00:00",
                "direction": "add",
                "amount": 30,
                "unit": "minutes",
                "timezone": "Africa/Nairobi",
            }
        }
    }


class DatetimeShiftResponse(BaseModel):
    result_iso: str = Field(..., description="Result datetime in ISO 8601 format.")
    result_date: str = Field(..., description="Date portion only: YYYY-MM-DD.")
    result_time: str = Field(..., description="Time portion only: HH:MM:SS.")
    result_human: str = Field(..., description="Human-readable result, e.g. 'March 15, 2026 at 2:30 PM'.")
    original_iso: str = Field(..., description="The input datetime in ISO 8601 (UTC).")
    timezone: str = Field(..., description="Timezone used.")


class DatetimeDiffRequest(BaseModel):
    start: str = Field(
        ...,
        description="The earlier datetime.",
        examples=["2026-03-15T08:00:00"],
    )
    end: str = Field(
        ...,
        description="The later datetime.",
        examples=["2026-03-17T14:05:00"],
    )
    timezone: str = Field(
        "UTC",
        description="IANA timezone for interpreting naive datetime strings. Default `UTC`.",
        examples=["Africa/Nairobi", "UTC"],
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "start": "2026-03-15T08:00:00",
                "end": "2026-03-17T14:05:30",
                "timezone": "UTC",
            }
        }
    }


class DiffBreakdown(BaseModel):
    years: int
    months: int
    days: int
    hours: int
    minutes: int
    seconds: int


class DatetimeDiffResponse(BaseModel):
    human_readable: str = Field(
        ...,
        description="Natural language breakdown, e.g. '2 days, 6 hours, 5 minutes'.",
    )
    breakdown: DiffBreakdown = Field(
        ...,
        description="Individual components of the difference.",
    )
    total_seconds: float = Field(..., description="Total difference expressed in seconds.")
    total_minutes: float = Field(..., description="Total difference expressed in minutes.")
    total_hours: float = Field(..., description="Total difference expressed in hours.")
    total_days: float = Field(..., description="Total difference expressed in days.")
    is_negative: bool = Field(
        ...,
        description="`true` when end is before start — useful for detecting expired or overdue items.",
    )
    start_iso: str
    end_iso: str


class DatetimeNowResponse(BaseModel):
    iso: str = Field(..., description="Current datetime in ISO 8601.")
    date: str = Field(..., description="Current date: YYYY-MM-DD.")
    time: str = Field(..., description="Current time: HH:MM:SS.")
    human: str = Field(..., description="Human-readable, e.g. 'March 15, 2026 at 2:00 PM'.")
    unix_timestamp: int = Field(..., description="Unix epoch timestamp (seconds).")
    timezone: str


class DatetimeConvertRequest(BaseModel):
    datetime: str = Field(
        ...,
        description="The datetime string to convert.",
        examples=["2026-03-15T14:00:00"],
    )
    from_timezone: str = Field(
        ...,
        description="IANA timezone the input datetime is in.",
        examples=["Africa/Nairobi"],
    )
    to_timezone: str = Field(
        ...,
        description="IANA timezone to convert into.",
        examples=["America/New_York"],
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "datetime": "2026-03-15T14:00:00",
                "from_timezone": "Africa/Nairobi",
                "to_timezone": "America/New_York",
            }
        }
    }


class DatetimeConvertResponse(BaseModel):
    result_iso: str = Field(..., description="Converted datetime in ISO 8601.")
    result_date: str = Field(..., description="Converted date: YYYY-MM-DD.")
    result_time: str = Field(..., description="Converted time: HH:MM:SS.")
    result_human: str = Field(..., description="Human-readable converted datetime.")
    from_timezone: str
    to_timezone: str
    original_iso: str = Field(..., description="Input datetime expressed in ISO 8601 (UTC).")


class DatetimeFormatRequest(BaseModel):
    datetime: str = Field(
        ...,
        description="The datetime string to format.",
        examples=["2026-03-15T14:00:00"],
    )
    output_format: Literal[
        "iso", "date_only", "time_only", "human", "human_date", "human_time", "relative", "custom"
    ] = Field(
        ...,
        description=(
            "The output format: \n"
            "- `iso` → `2026-03-15T14:00:00+03:00` \n"
            "- `date_only` → `2026-03-15` \n"
            "- `time_only` → `14:00:00` \n"
            "- `human` → `March 15, 2026 at 2:00 PM` \n"
            "- `human_date` → `March 15, 2026` \n"
            "- `human_time` → `2:00 PM` \n"
            "- `relative` → `3 days ago` / `in 2 hours` / `just now` \n"
            "- `custom` → uses `custom_format` as a Python strftime string"
        ),
        examples=["human"],
    )
    custom_format: Optional[str] = Field(
        None,
        description="Required when `output_format` is `custom`. Python strftime format string, e.g. `%d/%m/%Y %H:%M`.",
        examples=["%d/%m/%Y %H:%M"],
    )
    timezone: str = Field(
        "UTC",
        description="IANA timezone for interpreting naive datetime strings and applying to output.",
        examples=["Africa/Nairobi", "UTC"],
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "datetime": "2026-03-15T14:00:00",
                "output_format": "human",
                "timezone": "Africa/Nairobi",
            }
        }
    }


class DatetimeFormatResponse(BaseModel):
    result: str = Field(..., description="The formatted datetime string.")
    output_format: str
    timezone: str
