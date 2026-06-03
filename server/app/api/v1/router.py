from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.resumes import router as resumes_router
from app.api.v1.retrieval import router as retrieval_router
from app.api.v1.analysis import router as analysis_router
from app.api.v1.builder import router as builder_router
from app.api.v1.roadmap import router as roadmap_router
from app.api.v1.admin import router as admin_router
from app.api.v1.interview import router as interview_router

api_router = APIRouter()

api_router.include_router(auth_router)
api_router.include_router(resumes_router)
api_router.include_router(retrieval_router)
api_router.include_router(analysis_router)
api_router.include_router(builder_router)
api_router.include_router(roadmap_router)
api_router.include_router(admin_router)
api_router.include_router(interview_router)
