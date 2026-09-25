import pytest

from app.agent.agent import GroqAgent


# ============================================================
# TEST AGENT START
# ============================================================

@pytest.mark.asyncio
async def test_agent_start():
    """
    Verify that the agent can:

    1. Start browser
    2. Open demo application
    3. Create PageObserver
    4. Capture initial UI observation
    """

    agent = GroqAgent(
        headless=True
    )

    try:

        observation = await agent.start()

        # ----------------------------------------------------
        # Basic checks
        # ----------------------------------------------------

        assert observation is not None

        assert isinstance(
            observation,
            dict,
        )

        # ----------------------------------------------------
        # Session checks
        # ----------------------------------------------------

        status = agent.get_status()

        assert "session_id" in status

        assert status["status"] == "active"

        assert status["control_owner"] == "agent"

        # ----------------------------------------------------
        # Observation checks
        # ----------------------------------------------------

        assert "url" in observation["page"]

    finally:

        await agent.close()


# ============================================================
# TEST OBSERVE
# ============================================================

@pytest.mark.asyncio
async def test_agent_observe():
    """
    Verify that the agent can capture
    the current UI after starting.
    """

    agent = GroqAgent(
        headless=True
    )

    try:

        await agent.start()

        observation = await agent.observe()

        assert observation is not None

        assert isinstance(
            observation,
            dict,
        )

        assert "url" in observation

    finally:

        await agent.close()


# ============================================================
# TEST SESSION STATUS
# ============================================================

@pytest.mark.asyncio
async def test_agent_session_status():
    """
    Verify the session lifecycle.
    """

    agent = GroqAgent(
        headless=True
    )

    try:

        # Before start
        status = agent.get_status()

        assert status["status"] == "created"

        # Start
        await agent.start()

        status = agent.get_status()

        assert status["status"] == "active"

        assert (
            status["control_owner"]
            == "agent"
        )

    finally:

        await agent.close()


# ============================================================
# TEST PLANNER
# ============================================================

@pytest.mark.asyncio
async def test_agent_planner():
    """
    Verify that the agent can send
    the observation and goal to the planner.

    This test requires a valid Groq API key.
    """

    agent = GroqAgent(
        headless=True
    )

    try:

        observation = await agent.start()

        plan = agent.plan(
            goal="Open the member search page",
            observation=observation,
        )

        assert plan is not None

        # Pydantic planner response
        assert hasattr(
            plan,
            "model_dump",
        )

        plan_data = plan.model_dump()

        assert isinstance(
            plan_data,
            dict,
        )

    finally:

        await agent.close()


# ============================================================
# TEST COMPLETE AGENT FLOW
# ============================================================

@pytest.mark.asyncio
async def test_complete_agent_flow():
    """
    Complete discovery flow:

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
    """

    agent = GroqAgent(
        headless=True
    )

    try:

        # ----------------------------------------------------
        # 1. Start
        # ----------------------------------------------------

        observation = await agent.start()

        assert observation

        # ----------------------------------------------------
        # 2. Plan
        # ----------------------------------------------------

        plan = agent.plan(
            goal=(
                "Look up member 12345 "
                "and read their account details."
            ),
            observation=observation,
        )

        # ----------------------------------------------------
        # 3. Verify plan
        # ----------------------------------------------------

        assert plan is not None

        plan_data = plan.model_dump()

        assert isinstance(
            plan_data,
            dict,
        )

        assert "success" in plan_data

    finally:

        # ----------------------------------------------------
        # 4. Cleanup
        # ----------------------------------------------------

        await agent.close()
