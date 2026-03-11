from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import connect_to_mongo, close_mongo_connection
from app.routes import (
    auth,
    users,
    onboarding,
    tasks,
    checkins,
    setbacks,
    community,
    chat,
    analytics,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    yield
    await close_mongo_connection()


app = FastAPI(
    title="ManUp API",
    description="Backend API for the ManUp recovery app",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1", tags=["Auth"])
app.include_router(users.router, prefix="/api/v1", tags=["Users"])
app.include_router(onboarding.router, prefix="/api/v1", tags=["Onboarding"])
app.include_router(tasks.router, prefix="/api/v1", tags=["Tasks"])
app.include_router(checkins.router, prefix="/api/v1", tags=["Check-ins"])
app.include_router(setbacks.router, prefix="/api/v1", tags=["Setbacks"])
app.include_router(community.router, prefix="/api/v1", tags=["Community"])
app.include_router(chat.router, prefix="/api/v1", tags=["Chat"])
app.include_router(analytics.router, prefix="/api/v1", tags=["Analytics"])


@app.get("/")
async def root():
    return {"status": "ok", "app": "ManUp API"}


@app.get("/api/v1/health")
async def health():
    return {"status": "healthy", "version": "1.0.0"}
