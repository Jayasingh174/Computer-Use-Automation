from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.automation.session import (
    AutomationSession,
    SessionStatus,
)


router = APIRouter(
    prefix="/api/sessions",
    tags=["Sessions"],
)


# ============================================================
# IN-MEMORY SESSION STORE
# ============================================================

sessions: dict[str, AutomationSession] = {}


# ============================================================
# REQUEST MODELS
# ============================================================

class CreateSessionRequest(BaseModel):
    target_url: Optional[str] = None
    headless: bool = False


class HumanHandoffRequest(BaseModel):
    reason: str


# ============================================================
# CREATE SESSION
# ============================================================

@router.post("")
async def create_session(
    request: CreateSessionRequest,
):
    """
    Create and start a browser automation session.
    """

    session = AutomationSession(
        target_url=request.target_url,
        headless=request.headless,
    )

    try:
        await session.start()

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail={
                "message": "Failed to start automation session.",
                "error": str(exc),
            },
        )

    sessions[session.session_id] = session

    return {
        "success": True,
        "session": session.get_status(),
    }


# ============================================================
# GET SESSION
# ============================================================

@router.get("/{session_id}")
async def get_session(
    session_id: str,
):
    """
    Get the current state of an automation session.
    """

    session = sessions.get(session_id)

    if session is None:

        raise HTTPException(
            status_code=404,
            detail="Session not found.",
        )

    return {
        "success": True,
        "session": session.get_status(),
    }


# ============================================================
# PAUSE SESSION
# ============================================================

@router.post("/{session_id}/pause")
async def pause_session(
    session_id: str,
):
    """
    Pause automation without closing the browser.
    """

    session = sessions.get(session_id)

    if session is None:

        raise HTTPException(
            status_code=404,
            detail="Session not found.",
        )

    try:

        session.pause()

    except Exception as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    return {
        "success": True,
        "session": session.get_status(),
    }


# ============================================================
# REQUEST HUMAN HANDOFF
# ============================================================

@router.post("/{session_id}/handoff")
async def request_human_handoff(
    session_id: str,
    request: HumanHandoffRequest,
):
    """
    Pause the agent and transfer control
    of the live browser session to a human.
    """

    session = sessions.get(session_id)

    if session is None:

        raise HTTPException(
            status_code=404,
            detail="Session not found.",
        )

    try:

        session.request_human_control(
            reason=request.reason
        )

    except Exception as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    return {
        "success": True,
        "message": "Human control requested.",
        "session": session.get_status(),
    }


# ============================================================
# RESUME AFTER HUMAN
# ============================================================

@router.post("/{session_id}/resume")
async def resume_session(
    session_id: str,
):
    """
    Return control from the human operator
    back to the automation agent.
    """

    session = sessions.get(session_id)

    if session is None:

        raise HTTPException(
            status_code=404,
            detail="Session not found.",
        )

    try:

        session.resume_after_human()

    except Exception as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    return {
        "success": True,
        "message": "Agent control restored.",
        "session": session.get_status(),
    }


# ============================================================
# AGENT CONTROL
# ============================================================

@router.post("/{session_id}/agent-control")
async def acquire_agent_control(
    session_id: str,
):
    """
    Explicitly give control of the session to the agent.
    """

    session = sessions.get(session_id)

    if session is None:

        raise HTTPException(
            status_code=404,
            detail="Session not found.",
        )

    try:

        session.acquire_agent_control()

    except Exception as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    return {
        "success": True,
        "message": "Agent control acquired.",
        "session": session.get_status(),
    }


# ============================================================
# COMPLETE SESSION
# ============================================================

@router.post("/{session_id}/complete")
async def complete_session(
    session_id: str,
):
    """
    Mark the automation session as completed.
    """

    session = sessions.get(session_id)

    if session is None:

        raise HTTPException(
            status_code=404,
            detail="Session not found.",
        )

    try:

        session.complete()

    except Exception as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    return {
        "success": True,
        "message": "Session completed.",
        "session": session.get_status(),
    }


# ============================================================
# FAIL SESSION
# ============================================================

@router.post("/{session_id}/fail")
async def fail_session(
    session_id: str,
    request: HumanHandoffRequest,
):
    """
    Mark the session as failed.
    """

    session = sessions.get(session_id)

    if session is None:

        raise HTTPException(
            status_code=404,
            detail="Session not found.",
        )

    session.fail(
        request.reason
    )

    return {
        "success": True,
        "message": "Session marked as failed.",
        "session": session.get_status(),
    }


# ============================================================
# CLOSE SESSION
# ============================================================

@router.delete("/{session_id}")
async def close_session(
    session_id: str,
):
    """
    Close the browser and permanently close
    the automation session.
    """

    session = sessions.get(session_id)

    if session is None:

        raise HTTPException(
            status_code=404,
            detail="Session not found.",
        )

    try:

        await session.close()

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        )

    return {
        "success": True,
        "message": "Session closed.",
        "session": session.get_status(),
    }