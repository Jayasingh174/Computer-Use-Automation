import pytest

from app.agent.agent import GroqAgent
from app.automation.session import (
    AutomationSession,
    SessionStatus,
)


# ============================================================
# TEST: AGENT OBSERVE BEFORE START
# ============================================================

@pytest.mark.asyncio
async def test_observe_before_start():

    agent = GroqAgent(
        headless=True
    )

    with pytest.raises(
        RuntimeError,
        match="Agent has not been started",
    ):
        await agent.observe()


# ============================================================
# TEST: SESSION GET PAGE BEFORE START
# ============================================================

def test_get_page_before_start():

    session = AutomationSession(
        headless=True
    )

    with pytest.raises(
        RuntimeError,
        match="Browser session has not been started",
    ):
        session.get_page()


# ============================================================
# TEST: START SESSION TWICE
# ============================================================

@pytest.mark.asyncio
async def test_start_session_twice():

    session = AutomationSession(
        headless=True
    )

    try:

        await session.start()

        with pytest.raises(
            RuntimeError,
            match="Cannot start session",
        ):
            await session.start()

    finally:

        await session.close()


# ============================================================
# TEST: PAUSE INVALID SESSION
# ============================================================

def test_pause_created_session():

    session = AutomationSession(
        headless=True
    )

    with pytest.raises(
        RuntimeError,
        match="Cannot pause session",
    ):
        session.pause()


# ============================================================
# TEST: HUMAN RESUME WITHOUT HANDOFF
# ============================================================

def test_resume_without_handoff():

    session = AutomationSession(
        headless=True
    )

    with pytest.raises(
        RuntimeError,
        match="Session is not waiting for human intervention",
    ):
        session.resume_after_human()


# ============================================================
# TEST: HUMAN HANDOFF
# ============================================================

@pytest.mark.asyncio
async def test_human_handoff():

    session = AutomationSession(
        headless=True
    )

    try:

        await session.start()

        session.request_human_control(
            reason="Agent requires human verification."
        )

        status = session.get_status()

        assert (
            status["status"]
            == SessionStatus.WAITING_HUMAN.value
        )

        assert (
            status["control_owner"]
            == "human"
        )

        assert (
            status["last_error"]
            == "Agent requires human verification."
        )

    finally:

        await session.close()


# ============================================================
# TEST: RESUME AFTER HUMAN
# ============================================================

@pytest.mark.asyncio
async def test_resume_after_human():

    session = AutomationSession(
        headless=True
    )

    try:

        await session.start()

        session.request_human_control(
            reason="Manual verification required."
        )

        session.resume_after_human()

        status = session.get_status()

        assert (
            status["status"]
            == SessionStatus.ACTIVE.value
        )

        assert (
            status["control_owner"]
            == "agent"
        )

    finally:

        await session.close()


# ============================================================
# TEST: COMPLETE SESSION
# ============================================================

@pytest.mark.asyncio
async def test_complete_session():

    session = AutomationSession(
        headless=True
    )

    try:

        await session.start()

        session.complete()

        status = session.get_status()

        assert (
            status["status"]
            == SessionStatus.COMPLETED.value
        )

    finally:

        await session.close()


# ============================================================
# TEST: FAIL SESSION
# ============================================================

def test_fail_session():

    session = AutomationSession(
        headless=True
    )

    session.fail(
        "Browser navigation failed."
    )

    status = session.get_status()

    assert (
        status["status"]
        == SessionStatus.FAILED.value
    )

    assert (
        status["last_error"]
        == "Browser navigation failed."
    )


# ============================================================
# TEST: AGENT CLOSE
# ============================================================

@pytest.mark.asyncio
async def test_agent_close():

    agent = GroqAgent(
        headless=True
    )

    await agent.start()

    await agent.close()

    status = agent.get_status()

    assert (
        status["status"]
        == SessionStatus.CLOSED.value
    )