from typing import Optional

from fastapi import APIRouter

from app.agent.agent import GroqAgent


router = APIRouter(
    prefix="/interventions",
    tags=["Interventions"],
)


# Temporary in-memory agent registry.
# Later this can become a proper session store.
agents: dict[str, GroqAgent] = {}


@router.post("/{session_id}/take-control")
async def take_control(session_id: str):

    agent = agents.get(session_id)

    if agent is None:
        return {
            "success": False,
            "error": "Session not found",
        }

    result = agent.start_human_control()

    return result


@router.post("/{session_id}/resume")
async def resume_agent(
    session_id: str,
    note: Optional[str] = None,
):

    agent = agents.get(session_id)

    if agent is None:
        return {
            "success": False,
            "error": "Session not found",
        }

    result = await agent.resume_from_human(
        note=note
    )

    return result


@router.get("/{session_id}")
async def intervention_status(
    session_id: str,
):

    agent = agents.get(session_id)

    if agent is None:
        return {
            "success": False,
            "error": "Session not found",
        }

    return agent.handoff.get_intervention()