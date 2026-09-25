from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.agent.agent import GroqAgent
from app.api.dependencies import get_agent
from app.models.agent import (
    AgentRunRequest,
    AgentRunResponse,
)

from app.api.routes.interventions import agents  # or move `agents` to a shared module, see note below

# ============================================================
# ROUTER
# ============================================================

router = APIRouter(
    prefix="/api/agent",
    tags=["Agent"],
)


# ============================================================
# TEST REQUEST MODEL
# ============================================================

class AgentTestRequest(BaseModel):
    prompt: str


# ============================================================
# START AGENT
# ============================================================
@router.post("/start")
async def start_agent(agent: GroqAgent = Depends(get_agent)):
    try:
        observation = await agent.start()
        agents[agent.session.session_id] = agent
        return {"success": True, "session": agent.get_status(), "observation": observation}

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail={
                "error": "AGENT_START_FAILED",
                "message": str(exc),
            },
        )


# ============================================================
# TEST AGENT
# ============================================================

@router.post("/test-agent")
async def test_agent(
    request: AgentTestRequest,
):
    """
    Test the complete discovery flow.

    Flow:

        User Goal
             ↓
        GroqAgent
             ↓
        Browser
             ↓
        Observer
             ↓
        Planner
             ↓
        Groq LLM
             ↓
        Structured Plan
    """

    agent = GroqAgent(
        headless=False,
    )

    try:

        # ----------------------------------------------------
        # 1. Start browser
        # ----------------------------------------------------

        observation = await agent.start()

        # ----------------------------------------------------
        # 2. Ask planner
        # ----------------------------------------------------

        plan = agent.plan(
            goal=request.prompt,
            observation=observation,
        )

        # ----------------------------------------------------
        # 3. Return plan
        # ----------------------------------------------------

        return {
            "success": plan.success,
            "goal": request.prompt,
            "observation": observation,
            "plan": plan.model_dump(),
            "session": agent.get_status(),
        }

    except Exception as exc:

        return {
            "success": False,
            "goal": request.prompt,
            "error": str(exc),
            "session": agent.get_status(),
        }

    finally:

        await agent.close()


# ============================================================
# RUN AGENT
# ============================================================

@router.post(
    "/run",
    response_model=AgentRunResponse,
)
async def run_agent(
    request: AgentRunRequest,
):
    """
    Main agent execution endpoint.

    Current flow:

        Goal
          ↓
        Agent
          ↓
        Browser
          ↓
        Observer
          ↓
        Planner
          ↓
        Plan

    Action execution can be added next.
    """

    agent = GroqAgent(
        target_url=request.target_url,
        headless=request.headless,
    )

    try:

        # ----------------------------------------------------
        # 1. Start browser
        # ----------------------------------------------------

        observation = await agent.start()

        # ----------------------------------------------------
        # 2. Generate plan
        # ----------------------------------------------------

        plan = agent.plan(
            goal=request.goal,
            observation=observation,
        )

        # ----------------------------------------------------
        # 3. Return agent result
        # ----------------------------------------------------

        return AgentRunResponse(
            success=True,
            session_id=agent.session.session_id,
            status=agent.session.status.value,
            goal=request.goal,
            current_step=agent.session.current_step,
            steps=[
                plan.model_dump()
            ],
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail={
                "error": "AGENT_RUN_FAILED",
                "message": str(exc),
            },
        )

    finally:

        await agent.close()
