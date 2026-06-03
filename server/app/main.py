from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from contextlib import asynccontextmanager
from app.config import get_settings

settings = get_settings()

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Backend API for RViewer AI Resume Intelligence Platform",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[url.strip() for url in settings.ALLOWED_ORIGINS.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.core.interview.session_manager import session_manager
from app.api.v1.router import api_router
from app.api.v1.auth import router as auth_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await session_manager.start_cleanup_task()
    yield
    # Shutdown
    await session_manager.stop_cleanup_task()

app.router.lifespan_context = lifespan

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "version": settings.VERSION}

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {"message": "RViewer AI API", "docs": "/docs"}
