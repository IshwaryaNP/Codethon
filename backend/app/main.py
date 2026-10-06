from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config import settings
from app.db import connect_to_mongo, close_mongo_connection
from app.auth.router import router as auth_router
from app.routers.subjects import router as subjects_router
from app.routers.topics import router as topics_router
from app.routers.events import router as events_router
from app.routers.availability import router as availability_router
from app.routers.sessions import router as sessions_router
from app.routers.scheduler import router as scheduler_router
from app.routers.dashboard import router as dashboard_router
from app.routers.quizzes import router as quizzes_router
from app.routers.syllabus import router as syllabus_router
from app.routers.summaries import router as summaries_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    yield
    await close_mongo_connection()

app = FastAPI(
    title="Intelligent Study Planner & Progress Tracker API",
    version="1.0.0",
    description="Adaptive Study Planner backend powered by FastAPI, Motor MongoDB, Monte Carlo Readiness, and Anthropic API.",
    lifespan=lifespan
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth_router)
app.include_router(subjects_router)
app.include_router(topics_router)
app.include_router(events_router)
app.include_router(availability_router)
app.include_router(sessions_router)
app.include_router(scheduler_router)
app.include_router(dashboard_router)
app.include_router(quizzes_router)
app.include_router(syllabus_router)
app.include_router(summaries_router)

@app.get("/health")
async def health_check():
    return {"status": "ok", "app": "Intelligent Study Planner", "version": "1.0.0"}
