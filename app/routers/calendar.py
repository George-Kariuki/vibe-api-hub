from datetime import timedelta

from fastapi import APIRouter, HTTPException

from app.models.calendar import (
    CalendarLinkByDurationRequest,
    CalendarLinkByRangeRequest,
    CalendarLinkResponse,
)
from app.utils.datetime_utils import build_gcal_url, parse_to_utc

router = APIRouter(prefix="/calendar", tags=["Google Calendar"])


@router.post(
    "/link/by-range",
    response_model=CalendarLinkResponse,
    summary="Generate Google Calendar link — start & end datetime",
    description=(
        "Provide a start and end datetime (in any common format) and receive a fully "
        "formatted Google Calendar add-event URL. \n\n"
        "Useful for no-code platforms (Bubble, FlutterFlow, Adalo, etc.) that cannot "
        "natively construct Google Calendar URLs with dynamic data. \n\n"
        "**Redirect users** to the returned `url` — Google Calendar will open with all "
        "event fields pre-filled."
    ),
)
async def calendar_link_by_range(body: CalendarLinkByRangeRequest) -> CalendarLinkResponse:
    start_utc = parse_to_utc(body.start_datetime, body.timezone)
    end_utc = parse_to_utc(body.end_datetime, body.timezone)

    if end_utc <= start_utc:
        raise HTTPException(
            status_code=422,
            detail="end_datetime must be after start_datetime.",
        )

    duration_minutes = int((end_utc - start_utc).total_seconds() / 60)

    url = build_gcal_url(
        title=body.title,
        start_utc=start_utc,
        end_utc=end_utc,
        details=body.details,
        location=body.location,
        timezone=body.timezone,
    )

    return CalendarLinkResponse(
        url=url,
        title=body.title,
        start_utc=start_utc.isoformat(),
        end_utc=end_utc.isoformat(),
        duration_minutes=duration_minutes,
    )


@router.post(
    "/link/by-duration",
    response_model=CalendarLinkResponse,
    summary="Generate Google Calendar link — start datetime + duration",
    description=(
        "Provide a start datetime and a duration in minutes — the end time is calculated "
        "automatically. Returns a fully formatted Google Calendar add-event URL. \n\n"
        "Useful when the platform stores event length rather than an explicit end time. \n\n"
        "**Common durations:** 15, 30, 45, 60 (1 hr), 90 (1.5 hrs), 120 (2 hrs). \n\n"
        "**Redirect users** to the returned `url` — Google Calendar will open with all "
        "event fields pre-filled."
    ),
)
async def calendar_link_by_duration(body: CalendarLinkByDurationRequest) -> CalendarLinkResponse:
    start_utc = parse_to_utc(body.start_datetime, body.timezone)
    end_utc = start_utc + timedelta(minutes=body.duration_minutes)

    url = build_gcal_url(
        title=body.title,
        start_utc=start_utc,
        end_utc=end_utc,
        details=body.details,
        location=body.location,
        timezone=body.timezone,
    )

    return CalendarLinkResponse(
        url=url,
        title=body.title,
        start_utc=start_utc.isoformat(),
        end_utc=end_utc.isoformat(),
        duration_minutes=body.duration_minutes,
    )
