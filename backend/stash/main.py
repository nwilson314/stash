from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from stash.config import settings
from loguru import logger

from stash.router import router

app = FastAPI()
app.include_router(router)

if settings.ENVIRONMENT == "dev":
    logger.warning("Running in development mode - allowing CORS for all origins")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    logger.warning("Running in production mode - disabling CORS")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


@app.get("/")
async def root():
    return {
        "message": "Hello, World!",
    }
