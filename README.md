# Vibe API Hub

A collection of open utility APIs built for **no-code and low-code platform users**.

Platforms like Bubble, FlutterFlow, Adalo, AppGyver, and Glide often can't handle complex URL construction, date formatting, or data transformations natively. These APIs fill that gap — free to use, community-driven, open to contributions.

Built with **Python + FastAPI**, hosted on **Vercel**.

---

## Live API

> Coming soon — deploy URL will be listed here after first Vercel deployment.

Interactive docs (Swagger UI): `https://your-deployment.vercel.app/docs`

---

## Available Endpoints

### Text Utilities

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/text/regex/extract` | Extract regex matches from a string — returns first match or all matches as array |
| `POST` | `/text/regex/replace` | Replace / redact regex matches in a string with a substitution |

#### Request fields — `/text/regex/extract`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `text` | string | ✅ | The input text to search |
| `pattern` | string | ✅ | The regex pattern |
| `return_array` | boolean | ✅ | `true` = all matches as array, `false` = first match as string (or `null`) |
| `case_insensitive` | boolean | — | Default `false` |
| `multiline` | boolean | — | Default `false` |

#### Example — Extract (all matches)

```http
POST /text/regex/extract
Content-Type: application/json

{
  "text": "Call me at 0712 345 678 or email jay@example.com",
  "pattern": "\\+?[0-9][\\d\\s\\-\\(\\)]{5,}[0-9]",
  "return_array": true
}
```

**Response:**
```json
{
  "matched": true,
  "result": ["0712 345 678"],
  "match_count": 1,
  "pattern": "\\+?[0-9][\\d\\s\\-\\(\\)]{5,}[0-9]"
}
```

---

#### Request fields — `/text/regex/replace`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `text` | string | ✅ | The input text to process |
| `pattern` | string | ✅ | The regex pattern identifying what to replace |
| `replacement` | string | — | Substitution string. Default `""` (removes matches). E.g. `"[REDACTED]"` |
| `case_insensitive` | boolean | — | Default `false` |
| `multiline` | boolean | — | Default `false` |

#### Example — Replace (redact phone numbers & emails)

This is the direct solution to blocking contact details in no-code platform chats (e.g. Adalo, Bubble):

```http
POST /text/regex/replace
Content-Type: application/json

{
  "text": "Hi, call me on 0712 345 678 or email jay@example.com to arrange directly.",
  "pattern": "(\\+?[0-9][\\d\\s\\-\\(\\)]{5,}[0-9]|\\S+@\\S+\\.\\S+)",
  "replacement": "[REDACTED]",
  "case_insensitive": true
}
```

**Response:**
```json
{
  "result": "Hi, call me on [REDACTED] or email [REDACTED] to arrange directly.",
  "replacement_count": 2,
  "original_text": "Hi, call me on 0712 345 678 or email jay@example.com to arrange directly.",
  "pattern": "(\\+?[0-9][\\d\\s\\-\\(\\)]{5,}[0-9]|\\S+@\\S+\\.\\S+)"
}
```

**Notes:**
- Both endpoints validate the regex pattern and return a `422` with a clear message if it's invalid.
- Use `return_array: false` on `/extract` as a simple "does this text contain X?" check — `matched` will be `true` or `false`.
- The combined pattern `(\+?[0-9][\d\s\-\(\)]{5,}[0-9]|\S+@\S+\.\S+)` catches both phone numbers and email addresses in a single call.

---

### Google Calendar

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/calendar/link/by-range` | Generate a Google Calendar link using start & end datetime |
| `POST` | `/calendar/link/by-duration` | Generate a Google Calendar link using start datetime + duration in minutes |

#### Request fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `title` | string | ✅ | Event title |
| `start_datetime` | string | ✅ | Start datetime (see datetime formats below) |
| `end_datetime` | string | ✅ *by-range only* | End datetime |
| `duration_minutes` | integer | ✅ *by-duration only* | Duration in minutes (e.g. 30, 60, 90) |
| `timezone` | string | — | IANA timezone name. Default: `"UTC"` |
| `details` | string | — | Event description / notes |
| `location` | string | — | Physical address or meeting link |
| `attendees` | array of strings | — | List of attendee email addresses to pre-fill |

#### Example — By Range

```http
POST /calendar/link/by-range
Content-Type: application/json

{
  "title": "Project Sync Meeting",
  "start_datetime": "2026-03-15T14:00:00",
  "end_datetime": "2026-03-15T15:00:00",
  "details": "Review Q1 roadmap and finalize launch dates.",
  "location": "Conference Room A",
  "timezone": "Africa/Nairobi",
  "attendees": ["alice@example.com", "bob@example.com"]
}
```

**Response:**
```json
{
  "url": "https://calendar.google.com/calendar/r/eventedit?text=Project+Sync+Meeting&dates=20260315T110000Z%2F20260315T120000Z&ctz=Africa%2FNairobi&details=Review+Q1+roadmap+and+finalize+launch+dates.&location=Conference+Room+A&add=alice%40example.com%2Cbob%40example.com",
  "title": "Project Sync Meeting",
  "start_utc": "2026-03-15T11:00:00+00:00",
  "end_utc": "2026-03-15T12:00:00+00:00",
  "duration_minutes": 60
}
```

#### Example — By Duration

```http
POST /calendar/link/by-duration
Content-Type: application/json

{
  "title": "Project Sync Meeting",
  "start_datetime": "2026-03-15T14:00:00",
  "duration_minutes": 60,
  "details": "Review Q1 roadmap and finalize launch dates.",
  "location": "Conference Room A",
  "timezone": "Africa/Nairobi",
  "attendees": ["alice@example.com", "bob@example.com"]
}
```

**Notes:**
- `attendees` is optional on both endpoints. Omit it or pass `null` if not needed.
- Attendee emails are validated — each must contain `@` and a valid domain.
- Datetime strings can include timezone offset (`+03:00`, `Z`) or be left naive — if naive, the `timezone` field is used to localise them.
- The `timezone` field also sets the Google Calendar display timezone (`ctz`). Use IANA timezone names: `Africa/Nairobi`, `America/New_York`, `Europe/London`, `UTC`, etc.
- Redirect your users to the returned `url` — Google Calendar opens with all fields pre-filled.

---

## Running Locally

```bash
# Clone and set up
git clone https://github.com/George-Kariuki/vibe-api-hub.git
cd vibe-api-hub

python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

pip install -r requirements.txt

# Start the dev server
uvicorn app.main:app --reload
```

Then open `http://localhost:8000/docs` for the interactive Swagger UI.

---

## Project Structure

```
vibe-api-hub/
├── api/
│   └── index.py          # Vercel serverless entry point (Mangum adapter)
├── app/
│   ├── main.py           # FastAPI app, CORS, router registration
│   ├── routers/
│   │   ├── calendar.py   # /calendar endpoints
│   │   └── text.py       # /text endpoints
│   ├── models/
│   │   ├── calendar.py   # Pydantic request/response models
│   │   └── text.py       # Pydantic request/response models
│   └── utils/
│       └── datetime_utils.py  # Date parsing, UTC conversion, URL builder
├── requirements.txt
├── vercel.json
└── README.md
```

---

## Contributing

Contributions are welcome. If you have a utility that no-code platforms can't handle natively, open a PR.

**To add a new endpoint:**

1. Create `app/routers/your_category.py` with an `APIRouter`
2. Create `app/models/your_category.py` with Pydantic models
3. Register your router in `app/main.py`
4. Document your endpoint in this README

Please keep endpoints stateless, dependency-light, and clearly documented for non-technical users.

---

## License

MIT
