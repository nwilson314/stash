from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from stash.config import settings
from loguru import logger

from stash.router import links
from stash.router import users

app = FastAPI()
app.include_router(links.router)
app.include_router(users.router)

@app.middleware("http")
async def log_request_origin(request, call_next):
    logger.info(f"Incoming request from origin: {request.headers.get('origin')}")
    logger.info(f"Request headers: {request.headers}")
    response = await call_next(request)
    return response

if settings.ENVIRONMENT == "dev":
    logger.warning("Running in development mode - allowing specific origins")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",  # Local development
            "http://localhost:5173",  # Vite default port
            "https://stash-peach.vercel.app"  # Production deployment
        ],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization", "accept"],
        expose_headers=["*"],
        max_age=3600,  # Cache preflight requests for 1 hour
    )
else:
    logger.warning("Running in production mode - allowing specific origins")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "https://stash-peach.vercel.app",  # Production deployment
            "http://localhost:5173",
        ],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization", "accept"],
        expose_headers=["*"],
        max_age=3600,  # Cache preflight requests for 1 hour
    )


@app.get("/")
async def root():
    return {
        "message": "Hello, World!",
    }
