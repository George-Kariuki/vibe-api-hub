# Vibe API Hub

A collection of open utility APIs built for **no-code and low-code platform users**.

Platforms like Bubble, FlutterFlow, Adalo, AppGyver, and Glide often can't handle complex URL construction, date formatting, or data transformations natively. These APIs fill that gap — free to use, community-driven, open to contributions.

Built with **Python + FastAPI**, hosted on **Vercel**.

---

## Live API

Base URL: `https://vibe-api-hub.vercel.app`

Interactive docs (Swagger UI): [`https://vibe-api-hub.vercel.app/docs`](https://vibe-api-hub.vercel.app/docs)

---

## Available Endpoints

### Date & Time

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/datetime/shift` | Add or subtract a duration from a datetime — get end time from start, or start from end |
| `POST` | `/datetime/diff` | Smart difference between two datetimes with full breakdown and human-readable output |
| `GET` | `/datetime/now` | Current datetime in any timezone |
| `POST` | `/datetime/convert` | Convert a datetime between any two IANA timezones |
| `POST` | `/datetime/format` | Reformat a datetime string — ISO, human-readable, relative ("3 days ago"), or custom |

#### `/datetime/shift`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `datetime` | string | ✅ | The starting (or ending) datetime |
| `direction` | `"add"` \| `"subtract"` | ✅ | Move forward or backward in time |
| `amount` | integer | ✅ | Quantity to shift (must be > 0) |
| `unit` | string | ✅ | `"seconds"` `"minutes"` `"hours"` `"days"` `"weeks"` `"months"` `"years"` |
| `timezone` | string | — | IANA timezone. Default `"UTC"` |

```http
POST /datetime/shift
Content-Type: application/json

{ "datetime": "2026-03-15T14:00:00", "direction": "add", "amount": 30, "unit": "minutes", "timezone": "Africa/Nairobi" }
```

```json
{
  "result_iso": "2026-03-15T14:30:00+03:00",
  "result_date": "2026-03-15",
  "result_time": "14:30:00",
  "result_human": "March 15, 2026 at 2:30 PM",
  "original_iso": "2026-03-15T11:00:00+00:00",
  "timezone": "Africa/Nairobi"
}
```

> Use `direction: "subtract"` to reverse the operation — e.g. given an end time, get the start time.

---

#### `/datetime/diff`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `start` | string | ✅ | The earlier datetime |
| `end` | string | ✅ | The later datetime |
| `timezone` | string | — | IANA timezone. Default `"UTC"` |

```http
POST /datetime/diff
Content-Type: application/json

{ "start": "2026-03-15T08:00:00", "end": "2026-03-17T14:05:30", "timezone": "UTC" }
```

```json
{
  "human_readable": "2 days, 6 hours, 5 minutes, 30 seconds",
  "breakdown": { "years": 0, "months": 0, "days": 2, "hours": 6, "minutes": 5, "seconds": 30 },
  "total_seconds": 194730.0,
  "total_minutes": 3245.5,
  "total_hours": 54.09,
  "total_days": 2.25,
  "is_negative": false,
  "start_iso": "2026-03-15T08:00:00+00:00",
  "end_iso": "2026-03-17T14:05:30+00:00"
}
```

> `is_negative: true` when `end` is before `start` — useful for detecting expired bookings or overdue tasks.

---

#### `/datetime/now`

```http
GET /datetime/now?timezone=Africa/Nairobi
```

```json
{
  "iso": "2026-04-12T14:30:48+03:00",
  "date": "2026-04-12",
  "time": "14:30:48",
  "human": "April 12, 2026 at 2:30 PM",
  "unix_timestamp": 1744457448,
  "timezone": "Africa/Nairobi"
}
```

---

#### `/datetime/convert`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `datetime` | string | ✅ | Datetime to convert |
| `from_timezone` | string | ✅ | Source IANA timezone |
| `to_timezone` | string | ✅ | Target IANA timezone |

```http
POST /datetime/convert
Content-Type: application/json

{ "datetime": "2026-03-15T14:00:00", "from_timezone": "Africa/Nairobi", "to_timezone": "America/New_York" }
```

```json
{
  "result_iso": "2026-03-15T07:00:00-04:00",
  "result_date": "2026-03-15",
  "result_time": "07:00:00",
  "result_human": "March 15, 2026 at 7:00 AM",
  "from_timezone": "Africa/Nairobi",
  "to_timezone": "America/New_York",
  "original_iso": "2026-03-15T11:00:00+00:00"
}
```

---

#### `/datetime/format`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `datetime` | string | ✅ | The datetime to format |
| `output_format` | string | ✅ | `"iso"` `"date_only"` `"time_only"` `"human"` `"human_date"` `"human_time"` `"relative"` `"custom"` |
| `custom_format` | string | — | Required only when `output_format` is `"custom"`. Python strftime string e.g. `"%d/%m/%Y"` |
| `timezone` | string | — | IANA timezone. Default `"UTC"` |

| `output_format` value | Example output |
|-----------------------|----------------|
| `iso` | `2026-03-15T14:00:00+03:00` |
| `date_only` | `2026-03-15` |
| `time_only` | `14:00:00` |
| `human` | `March 15, 2026 at 2:00 PM` |
| `human_date` | `March 15, 2026` |
| `human_time` | `2:00 PM` |
| `relative` | `3 days ago` / `in 2 hours` / `just now` |
| `custom` | Any strftime string, e.g. `%d/%m/%Y` → `15/03/2026` |

```http
POST /datetime/format
Content-Type: application/json

{ "datetime": "2024-01-01T00:00:00", "output_format": "relative", "timezone": "UTC" }
```

```json
{ "result": "2 years ago", "output_format": "relative", "timezone": "UTC" }
```

---

### Text Utilities

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/text/regex/extract` | Extract regex matches from a string — returns first match or all matches as array |
| `POST` | `/text/regex/replace` | Replace / redact regex matches in a string with a substitution |

---

### List Utilities

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/lists/random-pick` | Pick N random items from a list in one call (unique by default, optional duplicates) |

#### Request fields — `/lists/random-pick`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `items` | array of strings | ✅ | List of IDs/items to pick from |
| `count` | integer | ✅ | Number of picks you want (must be > 0) |
| `allow_duplicates` | boolean | — | Default `false`. If `true`, picks may repeat |
| `seed` | integer | — | Optional seed for deterministic output |

**Behavior:**
- If `allow_duplicates` is `false` and `count >= items.length`, the API returns **all items** in randomized order.
- If `allow_duplicates` is `true`, `count` can exceed the number of items and picks may repeat.

#### Example — Unique picks (no duplicates)

```http
POST /lists/random-pick
Content-Type: application/json

{
  "items": ["rec_1", "rec_2", "rec_3", "rec_4", "rec_5"],
  "count": 3,
  "allow_duplicates": false,
  "seed": 42
}
```

**Response:**
```json
{
  "picks": ["rec_2", "rec_5", "rec_1"],
  "count_requested": 3,
  "count_returned": 3,
  "input_size": 5,
  "allow_duplicates": false,
  "seed": 42
}
```

#### Example — Allow duplicates

```http
POST /lists/random-pick
Content-Type: application/json

{
  "items": ["rec_1", "rec_2", "rec_3"],
  "count": 5,
  "allow_duplicates": true
}
```

**Response:**
```json
{
  "picks": ["rec_2", "rec_2", "rec_1", "rec_3", "rec_2"],
  "count_requested": 5,
  "count_returned": 5,
  "input_size": 3,
  "allow_duplicates": true,
  "seed": null
}
```

---

### File Utilities

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/files/convert-to-json` | Upload a CSV or Excel (.xlsx) file and get its contents back as JSON rows |

This endpoint accepts `multipart/form-data` (a file upload), not JSON. Send the file under the field name `file`. The first row is treated as the column header by default, and each subsequent row becomes one JSON object.

#### Form fields — `/files/convert-to-json`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `file` | file | ✅ | The `.csv` or `.xlsx` file to convert |
| `has_header` | boolean | — | Treat first row as column names. Default `true`. If `false`, keys are `column_1`, `column_2`, ... |
| `delimiter` | string | — | CSV delimiter character. Ignored for Excel. Default `","` |
| `sheet_index` | integer | — | Excel sheet index (0-based). Ignored for CSV. Default `0` |
| `skip_empty_rows` | boolean | — | Drop fully empty rows. Default `true` |
| `max_rows` | integer | — | Maximum number of data rows allowed. Default `10000` |

#### Example — Convert a CSV

```bash
curl -X POST https://vibe-api-hub.vercel.app/files/convert-to-json \
  -F "file=@users.csv" \
  -F "has_header=true"
```

**Response:**
```json
{
  "rows": [
    { "Name": "Alice", "Email": "alice@example.com", "Age": "30" },
    { "Name": "Bob", "Email": "bob@example.com", "Age": "25" }
  ],
  "row_count": 2,
  "columns": ["Name", "Email", "Age"],
  "filename": "users.csv",
  "file_type": "csv"
}
```

#### Example — Convert an Excel sheet

```bash
curl -X POST https://vibe-api-hub.vercel.app/files/convert-to-json \
  -F "file=@report.xlsx" \
  -F "sheet_index=0"
```

**Notes:**
- Only `.csv` and `.xlsx` are supported. Other file types return a `422` with a clear message.
- Uploads are subject to the host's request body limit (~4.5MB on Vercel). Keep files small/medium for reliable serverless performance.
- The `max_rows` cap (default 10,000) protects against serverless timeouts and memory limits; exceeding it returns a `422`.
- For no-code platforms: use a file upload / custom API action that sends `multipart/form-data` with the `file` field, then map the returned `rows` array to your database records.

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
│   └── index.py              # Vercel serverless entry point (Mangum adapter)
├── app/
│   ├── main.py               # FastAPI app, CORS, router registration
│   ├── routers/
│   │   ├── calendar.py       # /calendar endpoints
│   │   ├── lists.py          # /lists endpoints
│   │   ├── text.py           # /text endpoints
│   │   ├── datetime_ops.py   # /datetime endpoints
│   │   └── files.py          # /files endpoints
│   ├── models/
│   │   ├── calendar.py       # Pydantic request/response models
│   │   ├── lists.py          # Pydantic request/response models
│   │   ├── text.py           # Pydantic request/response models
│   │   ├── datetime_ops.py   # Pydantic request/response models
│   │   └── files.py          # Pydantic request/response models
│   └── utils/
│       ├── datetime_utils.py # Date parsing, UTC conversion, URL builder
│       └── file_parsers.py   # CSV and Excel parsing helpers
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
