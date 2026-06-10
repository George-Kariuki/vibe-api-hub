from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.models.files import FileConvertResponse
from app.utils.file_parsers import detect_file_type, parse_csv, parse_xlsx

router = APIRouter(prefix="/files", tags=["File Utilities"])


@router.post(
    "/convert-to-json",
    response_model=FileConvertResponse,
    summary="Convert an uploaded CSV or Excel file to JSON",
    description=(
        "Upload a `.csv` or `.xlsx` file and receive its contents as a JSON array of row objects. \n\n"
        "Send the file as `multipart/form-data` with the field name `file`. The first row is treated "
        "as the column header by default (`has_header=true`), and each subsequent row becomes one object. \n\n"
        "Useful for no-code platforms (Bubble, Adalo, FlutterFlow) that can upload a file but can't parse "
        "spreadsheet data into records natively. \n\n"
        "**Serverless limits:** uploads are subject to the host's request body size limit (~4.5MB on Vercel). "
        "The `max_rows` cap (default 10,000) keeps responses within the serverless time/memory budget."
    ),
)
async def convert_to_json(
    file: UploadFile = File(..., description="The .csv or .xlsx file to convert."),
    has_header: bool = Form(True, description="Treat the first row as column names. Default true."),
    delimiter: str = Form(",", description="CSV delimiter character. Ignored for Excel. Default ','."),
    sheet_index: int = Form(0, description="Excel sheet index (0-based). Ignored for CSV. Default 0."),
    skip_empty_rows: bool = Form(True, description="Drop fully empty rows. Default true."),
    max_rows: int = Form(10000, description="Maximum number of data rows allowed. Default 10000."),
) -> FileConvertResponse:
    if max_rows <= 0:
        raise HTTPException(status_code=422, detail="max_rows must be greater than 0.")

    file_type = detect_file_type(file.filename or "")
    content = await file.read()

    if not content:
        raise HTTPException(status_code=422, detail="The uploaded file is empty.")

    if file_type == "csv":
        rows, columns = parse_csv(content, has_header, delimiter, skip_empty_rows, max_rows)
    else:
        rows, columns = parse_xlsx(content, has_header, sheet_index, skip_empty_rows, max_rows)

    return FileConvertResponse(
        rows=rows,
        row_count=len(rows),
        columns=columns,
        filename=file.filename or "",
        file_type=file_type,
    )
