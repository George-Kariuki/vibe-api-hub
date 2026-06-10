from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import calendar, text, datetime_ops, lists, files

app = FastAPI(
    title="Vibe API Hub",
    description=(
        "A collection of open utility APIs built for no-code and low-code platform users. "
        "Platforms like Bubble, FlutterFlow, Adalo, AppGyver, and Glide often lack the ability "
        "to generate properly formatted external URLs and handle complex data transformations. "
        "These APIs fill that gap — free to use, open to contributions.\n\n"
        "**GitHub:** https://github.com/George-Kariuki/vibe-api-hub\n\n"
        "All endpoints accept JSON and return JSON. No authentication required."
    ),
    version="1.0.0",
    contact={
        "name": "Vibe API Hub",
        "url": "https://github.com/George-Kariuki/vibe-api-hub",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(calendar.router)
app.include_router(text.router)
app.include_router(datetime_ops.router)
app.include_router(lists.router)
app.include_router(files.router)


@app.get("/", tags=["Health"], summary="Health check")
async def root():
    return {
        "status": "ok",
        "message": "Vide APIs Hub is running.",
        "docs": "/docs",
        "version": "1.0.0",
    }
