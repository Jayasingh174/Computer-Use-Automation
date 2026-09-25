from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import (
    agent,
    replay,
    artifacts,
    sessions,
    interventions,
)


# ============================================================
# APPLICATION
# ============================================================

app = FastAPI(
    title="Computer-Use Automation System",
    description=(
        "LLM-driven computer-use automation with "
        "deterministic replay."
    ),
    version="1.0.0",
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get(
    "/health",
    tags=["Health"],
)
async def health_check():

    return {
        "status": "healthy",
        "service": "computer-use-automation",
        "version": "1.0.0",
    }


# ============================================================
# AGENT ROUTES
# ============================================================

app.include_router(
    agent.router,
    prefix="/api/agent",
    tags=["Agent"],
)


# ============================================================
# SESSION ROUTES
# ============================================================

app.include_router(
    sessions.router,
    prefix="/api/sessions",
    tags=["Sessions"],
)


# ============================================================
# REPLAY ROUTES
# ============================================================

app.include_router(
    replay.router,
    prefix="/api/replay",
    tags=["Replay"],
)


# ============================================================
# ARTIFACT ROUTES
# ============================================================

app.include_router(
    artifacts.router,
    prefix="/api/artifacts",
    tags=["Artifacts"],
)


# ============================================================
# HUMAN INTERVENTION ROUTES
# ============================================================

app.include_router(
    interventions.router,
    prefix="/api/interventions",
    tags=["Interventions"],
)