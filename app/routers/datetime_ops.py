from datetime import datetime, timezone as dt_timezone, timedelta

import pytz
from dateutil.relativedelta import relativedelta
from fastapi import APIRouter, HTTPException, Query

from app.models.datetime_ops import (
    DatetimeConvertRequest,
    DatetimeConvertResponse,
    DatetimeDiffRequest,
    DatetimeDiffResponse,
    DatetimeFormatRequest,
    DatetimeFormatResponse,
    DatetimeNowResponse,
    DatetimeShiftRequest,
    DatetimeShiftResponse,
    DiffBreakdown,
)
from app.utils.datetime_utils import parse_to_utc

router = APIRouter(prefix="/datetime", tags=["Date & Time"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _validate_timezone(tz_str: str) -> pytz.BaseTzInfo:
    try:
        return pytz.timezone(tz_str)
    except pytz.exceptions.UnknownTimeZoneError:
        raise HTTPException(
            status_code=422,
            detail=f"Unknown timezone: '{tz_str}'. Use an IANA timezone name, e.g. 'Africa/Nairobi', 'UTC'.",
        )


def _human(dt: datetime) -> str:
    """Format a datetime as 'March 15, 2026 at 2:30 PM'."""
    hour = dt.strftime("%I").lstrip("0") or "12"
    return f"{dt.strftime('%B')} {dt.day}, {dt.year} at {hour}:{dt.strftime('%M %p')}"


def _build_human_diff(years: int, months: int, days: int, hours: int, minutes: int, seconds: int) -> str:
    """Build a natural language duration string, omitting zero components."""
    parts = []
    if years:
        parts.append(f"{years} year{'s' if years != 1 else ''}")
    if months:
        parts.append(f"{months} month{'s' if months != 1 else ''}")
    if days:
        parts.append(f"{days} day{'s' if days != 1 else ''}")
    if hours:
        parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
    if minutes:
        parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
    if seconds and not (years or months or days):
        parts.append(f"{seconds} second{'s' if seconds != 1 else ''}")
    return ", ".join(parts) if parts else "0 seconds"


def _localize(dt: datetime, tz: pytz.BaseTzInfo) -> datetime:
    """Convert a UTC-aware datetime to the target timezone."""
    return dt.astimezone(tz)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post(
    "/shift",
    response_model=DatetimeShiftResponse,
    summary="Add or subtract a duration from a datetime",
    description=(
        "Shift a datetime forward or backward by a given amount and unit. \n\n"
        "Works in both directions: use `direction: 'add'` to get an **end time** from a start time, "
        "or `direction: 'subtract'` to get a **start time** from an end time. \n\n"
        "Supports `seconds`, `minutes`, `hours`, `days`, `weeks`, `months`, and `years`. "
        "Month and year arithmetic correctly handles end-of-month edge cases "
        "(e.g. Jan 31 + 1 month = Feb 28, not Mar 3)."
    ),
)
async def datetime_shift(body: DatetimeShiftRequest) -> DatetimeShiftResponse:
    tz = _validate_timezone(body.timezone)
    start_utc = parse_to_utc(body.datetime, body.timezone)

    sign = 1 if body.direction == "add" else -1

    if body.unit in ("months", "years"):
        delta = relativedelta(**{body.unit: sign * body.amount})
        result_utc = start_utc + delta
    else:
        unit_map = {
            "seconds": "seconds",
            "minutes": "minutes",
            "hours": "hours",
            "days": "days",
            "weeks": "weeks",
        }
        delta = timedelta(**{unit_map[body.unit]: sign * body.amount})
        result_utc = start_utc + delta

    result_local = _localize(result_utc, tz)

    return DatetimeShiftResponse(
        result_iso=result_local.isoformat(),
        result_date=result_local.strftime("%Y-%m-%d"),
        result_time=result_local.strftime("%H:%M:%S"),
        result_human=_human(result_local),
        original_iso=start_utc.isoformat(),
        timezone=body.timezone,
    )


@router.post(
    "/diff",
    response_model=DatetimeDiffResponse,
    summary="Get the difference between two datetimes",
    description=(
        "Calculate the exact difference between two datetime values. \n\n"
        "Returns a full breakdown (years, months, days, hours, minutes, seconds), "
        "a human-readable summary ('2 days, 6 hours, 5 minutes'), and totals in every unit "
        "so you can pick whichever your no-code platform needs. \n\n"
        "`is_negative: true` means `end` is before `start` — useful for detecting expired "
        "bookings, overdue tasks, or countdown scenarios without extra logic."
    ),
)
async def datetime_diff(body: DatetimeDiffRequest) -> DatetimeDiffResponse:
    start_utc = parse_to_utc(body.start, body.timezone)
    end_utc = parse_to_utc(body.end, body.timezone)

    is_negative = end_utc < start_utc
    earlier, later = (end_utc, start_utc) if is_negative else (start_utc, end_utc)

    rd = relativedelta(later, earlier)
    total_seconds = abs((end_utc - start_utc).total_seconds())

    human = _build_human_diff(rd.years, rd.months, rd.days, rd.hours, rd.minutes, rd.seconds)

    return DatetimeDiffResponse(
        human_readable=human,
        breakdown=DiffBreakdown(
            years=rd.years,
            months=rd.months,
            days=rd.days,
            hours=rd.hours,
            minutes=rd.minutes,
            seconds=rd.seconds,
        ),
        total_seconds=round(total_seconds, 2),
        total_minutes=round(total_seconds / 60, 2),
        total_hours=round(total_seconds / 3600, 2),
        total_days=round(total_seconds / 86400, 2),
        is_negative=is_negative,
        start_iso=start_utc.isoformat(),
        end_iso=end_utc.isoformat(),
    )


@router.get(
    "/now",
    response_model=DatetimeNowResponse,
    summary="Get the current datetime in any timezone",
    description=(
        "Returns the current date and time in the requested timezone. \n\n"
        "No-code platforms often store datetimes in UTC but need to display "
        "the current time in the user's local timezone — this solves that without custom formulas."
    ),
)
async def datetime_now(
    timezone: str = Query("UTC", description="IANA timezone name. Default `UTC`.", examples=["Africa/Nairobi"]),
) -> DatetimeNowResponse:
    tz = _validate_timezone(timezone)
    now = datetime.now(tz)

    return DatetimeNowResponse(
        iso=now.isoformat(),
        date=now.strftime("%Y-%m-%d"),
        time=now.strftime("%H:%M:%S"),
        human=_human(now),
        unix_timestamp=int(now.timestamp()),
        timezone=timezone,
    )


@router.post(
    "/convert",
    response_model=DatetimeConvertResponse,
    summary="Convert a datetime between timezones",
    description=(
        "Convert any datetime from one IANA timezone to another. \n\n"
        "Practical examples: show a UTC-stored event time in the user's local timezone, "
        "convert Nairobi booking times to New York for a global calendar view."
    ),
)
async def datetime_convert(body: DatetimeConvertRequest) -> DatetimeConvertResponse:
    _validate_timezone(body.from_timezone)
    to_tz = _validate_timezone(body.to_timezone)

    utc_dt = parse_to_utc(body.datetime, body.from_timezone)
    converted = _localize(utc_dt, to_tz)

    return DatetimeConvertResponse(
        result_iso=converted.isoformat(),
        result_date=converted.strftime("%Y-%m-%d"),
        result_time=converted.strftime("%H:%M:%S"),
        result_human=_human(converted),
        from_timezone=body.from_timezone,
        to_timezone=body.to_timezone,
        original_iso=utc_dt.isoformat(),
    )


@router.post(
    "/format",
    response_model=DatetimeFormatResponse,
    summary="Format a datetime string into a different format",
    description=(
        "Transform a datetime string into any output format. \n\n"
        "Especially useful for display purposes in no-code platforms that store ISO dates "
        "but need a friendlier format for the UI. \n\n"
        "The `relative` format produces strings like `3 days ago`, `in 2 hours`, or `just now` — "
        "ideal for feeds, notifications, and activity logs."
    ),
)
async def datetime_format(body: DatetimeFormatRequest) -> DatetimeFormatResponse:
    if body.output_format == "custom" and not body.custom_format:
        raise HTTPException(
            status_code=422,
            detail="custom_format is required when output_format is 'custom'.",
        )

    tz = _validate_timezone(body.timezone)
    utc_dt = parse_to_utc(body.datetime, body.timezone)
    local_dt = _localize(utc_dt, tz)

    if body.output_format == "iso":
        result = local_dt.isoformat()
    elif body.output_format == "date_only":
        result = local_dt.strftime("%Y-%m-%d")
    elif body.output_format == "time_only":
        result = local_dt.strftime("%H:%M:%S")
    elif body.output_format == "human":
        result = _human(local_dt)
    elif body.output_format == "human_date":
        result = f"{local_dt.strftime('%B')} {local_dt.day}, {local_dt.year}"
    elif body.output_format == "human_time":
        hour = local_dt.strftime("%I").lstrip("0") or "12"
        result = f"{hour}:{local_dt.strftime('%M %p')}"
    elif body.output_format == "relative":
        now_utc = datetime.now(dt_timezone.utc)
        diff_seconds = (utc_dt - now_utc).total_seconds()
        abs_diff = abs(diff_seconds)

        if abs_diff < 45:
            result = "just now"
        elif abs_diff < 90:
            result = "in a minute" if diff_seconds > 0 else "a minute ago"
        elif abs_diff < 3600:
            mins = round(abs_diff / 60)
            result = f"in {mins} minutes" if diff_seconds > 0 else f"{mins} minutes ago"
        elif abs_diff < 7200:
            result = "in an hour" if diff_seconds > 0 else "an hour ago"
        elif abs_diff < 86400:
            hrs = round(abs_diff / 3600)
            result = f"in {hrs} hours" if diff_seconds > 0 else f"{hrs} hours ago"
        elif abs_diff < 172800:
            result = "tomorrow" if diff_seconds > 0 else "yesterday"
        elif abs_diff < 2592000:
            days = round(abs_diff / 86400)
            result = f"in {days} days" if diff_seconds > 0 else f"{days} days ago"
        elif abs_diff < 31536000:
            months = round(abs_diff / 2592000)
            result = f"in {months} month{'s' if months != 1 else ''}" if diff_seconds > 0 else f"{months} month{'s' if months != 1 else ''} ago"
        else:
            years = round(abs_diff / 31536000)
            result = f"in {years} year{'s' if years != 1 else ''}" if diff_seconds > 0 else f"{years} year{'s' if years != 1 else ''} ago"
    else:  # custom
        try:
            result = local_dt.strftime(body.custom_format)
        except Exception as exc:
            raise HTTPException(
                status_code=422,
                detail=f"Invalid custom_format string: {exc}",
            )

    return DatetimeFormatResponse(
        result=result,
        output_format=body.output_format,
        timezone=body.timezone,
    )
