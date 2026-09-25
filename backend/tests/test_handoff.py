import pytest

from app.automation.session import (
    AutomationSession,
    SessionStatus,
    ControlOwner,
)
from app.escalation.manager import InterventionManager, EscalationManager
from app.escalation.intervention import InterventionRequest, InterventionReason, InterventionStatus,

# ============================================================
# TEST 1: REQUEST HUMAN HANDOFF
# ============================================================

@pytest.mark.asyncio
async def test_request_human_handoff():

    session = AutomationSession(
        headless=True
    )

    try:
        # Start session
        await session.start()

        assert (
            session.status
            == SessionStatus.ACTIVE
        )

        # Request human control
        session.request_human_control(
            reason="Agent requires human verification."
        )

        # Verify session state
        assert (
            session.status
            == SessionStatus.WAITING_HUMAN
        )

        # Verify control ownership
        assert (
            session.control_owner
            == ControlOwner.HUMAN
        )

        # Verify reason
        assert (
            session.last_error
            == "Agent requires human verification."
        )

    finally:
        await session.close()


# ============================================================
# TEST 2: HUMAN RESUMES AGENT
# ============================================================

@pytest.mark.asyncio
async def test_resume_after_human():

    session = AutomationSession(
        headless=True
    )

    try:
        await session.start()

        # Agent → Human
        session.request_human_control(
            reason="Manual verification required."
        )

        assert (
            session.status
            == SessionStatus.WAITING_HUMAN
        )

        # Human → Agent
        session.resume_after_human()

        assert (
            session.status
            == SessionStatus.ACTIVE
        )

        assert (
            session.control_owner
            == ControlOwner.AGENT
        )

    finally:
        await session.close()


# ============================================================
# TEST 3: INVALID HANDOFF
# ============================================================

def test_handoff_from_invalid_state():

    session = AutomationSession(
        headless=True
    )

    # Session is CREATED, not ACTIVE
    assert (
        session.status
        == SessionStatus.CREATED
    )

    with pytest.raises(
        RuntimeError,
        match="Cannot request human control",
    ):
        session.request_human_control(
            reason="Test handoff"
        )


# ============================================================
# TEST 4: INVALID HUMAN RESUME
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
# TEST 5: COMPLETE HANDOFF LIFECYCLE
# ============================================================

@pytest.mark.asyncio
async def test_complete_handoff_lifecycle():

    session = AutomationSession(
        headless=True
    )

    try:

        # ----------------------------------------------------
        # STEP 1: Agent starts
        # ----------------------------------------------------

        await session.start()

        status = session.get_status()

        assert status["status"] == "active"
        assert status["control_owner"] == "agent"

        # ----------------------------------------------------
        # STEP 2: Agent requests human
        # ----------------------------------------------------

        session.request_human_control(
            reason="Sensitive action requires human approval."
        )

        status = session.get_status()

        assert (
            status["status"]
            == "waiting_human"
        )

        assert (
            status["control_owner"]
            == "human"
        )

        # ----------------------------------------------------
        # STEP 3: Human resumes
        # ----------------------------------------------------

        session.resume_after_human()

        status = session.get_status()

        assert (
            status["status"]
            == "active"
        )

        assert (
            status["control_owner"]
            == "agent"
        )

    finally:

        await session.close()


# ============================================================
# TEST 6: ESCALATION MANAGER
# ============================================================

def test_escalation_manager_creation():

    manager = EscalationManager()

    assert manager is not None


# ============================================================
# TEST 7: INTERVENTION MANAGER CREATION
# ============================================================

def test_intervention_manager_creation():

    manager = InterventionManager()

    assert manager is not None
