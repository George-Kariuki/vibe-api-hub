from datetime import datetime
from urllib.parse import urlencode, quote_plus

import pytz
from dateutil import parser as dateutil_parser
from fastapi import HTTPException


def parse_to_utc(dt_string: str, timezone: str = "UTC") -> datetime:
    """
    Parse a datetime string and return a UTC-aware datetime.

    Accepts ISO 8601 and most human-readable formats via python-dateutil.
    If the datetime string has no timezone info, it is localised using `timezone`.
    If it already carries offset/Z info, the `timezone` param is still validated
    but the embedded offset takes precedence for conversion.
    """
    try:
        dt = dateutil_parser.parse(dt_string)
    except (ValueError, OverflowError, TypeError):
        raise HTTPException(
            status_code=422,
            detail=(
                f"Cannot parse datetime: '{dt_string}'. "
                "Use ISO 8601 format, e.g. '2026-03-15T14:00:00' or '2026-03-15T14:00:00+03:00'."
            ),
        )

    try:
        tz = pytz.timezone(timezone)
    except pytz.exceptions.UnknownTimeZoneError:
        raise HTTPException(
            status_code=422,
            detail=(
                f"Unknown timezone: '{timezone}'. "
                "Use an IANA timezone name, e.g. 'Africa/Nairobi', 'America/New_York', 'UTC'."
            ),
        )

    if dt.tzinfo is None:
        dt = tz.localize(dt)

    return dt.astimezone(pytz.utc)


def to_gcal_format(dt: datetime) -> str:
    """Return a UTC datetime as a Google Calendar date string: YYYYMMDDTHHmmssZ."""
    utc_dt = dt.astimezone(pytz.utc)
    return utc_dt.strftime("%Y%m%dT%H%M%SZ")


def build_gcal_url(
    title: str,
    start_utc: datetime,
    end_utc: datetime,
    details: str | None = None,
    location: str | None = None,
    timezone: str = "UTC",
    attendees: list[str] | None = None,
) -> str:
    """Assemble and return a Google Calendar add-event URL."""
    params: dict[str, str] = {
        "text": title,
        "dates": f"{to_gcal_format(start_utc)}/{to_gcal_format(end_utc)}",
        "ctz": timezone,
    }

    if details:
        params["details"] = details
    if location:
        params["location"] = location
    if attendees:
        params["add"] = ",".join(attendees)

    return (
        "https://calendar.google.com/calendar/r/eventedit?"
        + urlencode(params, quote_via=quote_plus)
    )
