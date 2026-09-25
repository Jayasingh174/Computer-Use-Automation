from datetime import datetime, timezone
from typing import Any, Optional

from app.automation.session import (
    AutomationSession,
    ControlOwner,
    SessionStatus,
)


class HandoffManager:
    """
    Manages transfer of control between the automation agent
    and a human operator.

    Important:
    The browser session is NOT recreated during handoff.

    The human operates the same live Playwright session that
    the agent was using.
    """

    def __init__(
        self,
        session: AutomationSession,
    ):
        self.session = session

        self.intervention_id: Optional[str] = None
        self.reason: Optional[str] = None
        self.context: dict[str, Any] = {}

        self.requested_at: Optional[str] = None
        self.human_started_at: Optional[str] = None
        self.resumed_at: Optional[str] = None

        self.human_actions: list[dict[str, Any]] = []

    # ==========================================================
    # REQUEST HUMAN HANDOFF
    # ==========================================================

    async def request_handoff(
        self,
        reason: str,
        current_step: Optional[int] = None,
        goal: Optional[str] = None,
        observation: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """
        Pause automation and request human intervention.

        The existing browser session remains alive.
        """

        if self.session.status != SessionStatus.ACTIVE:
            raise RuntimeError(
                "Cannot request handoff when session "
                f"status is {self.session.status.value}"
            )

        self.intervention_id = (
            f"intervention_{self.session.session_id}"
        )

        self.reason = reason

        self.requested_at = (
            datetime.now(timezone.utc).isoformat()
        )

        self.context = {
            "goal": goal,
            "current_step": (
                current_step
                if current_step is not None
                else self.session.current_step
            ),
            "observation": observation,
        }

        # ------------------------------------------------------
        # Capture current screenshot BEFORE handing over
        # ------------------------------------------------------

        screenshot = None

        try:
            screenshot = (
                await self.session.capture_screenshot(
                    category="handoff"
                )
            )
        except Exception:
            # Screenshot failure should not destroy
            # the handoff itself.
            screenshot = None

        self.context["screenshot"] = screenshot

        # ------------------------------------------------------
        # Transfer ownership to human
        # ------------------------------------------------------

        self.session.request_human_control(
            reason=reason
        )

        return self.get_intervention()

    # ==========================================================
    # HUMAN TAKES CONTROL
    # ==========================================================

    def start_human_control(self) -> dict[str, Any]:
        """
        Mark the intervention as actively being handled
        by a human operator.

        The same browser session is used.
        """

        if self.session.status != SessionStatus.WAITING_HUMAN:
            raise RuntimeError(
                "Session is not waiting for human intervention."
            )

        if self.session.control_owner != ControlOwner.HUMAN:
            raise RuntimeError(
                "Human does not own the session."
            )

        self.human_started_at = (
            datetime.now(timezone.utc).isoformat()
        )

        return {
            "success": True,
            "intervention_id": self.intervention_id,
            "session_id": self.session.session_id,
            "control_owner": "human",
            "status": self.session.status.value,
            "message": (
                "Human control started on the existing "
                "browser session."
            ),
        }

    # ==========================================================
    # RECORD HUMAN ACTION
    # ==========================================================

    def record_human_action(
        self,
        action_type: str,
        description: str,
        metadata: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """
        Record an action performed by the human.

        Do not store sensitive values such as passwords,
        tokens, or full PII here.
        """

        action = {
            "timestamp": (
                datetime.now(timezone.utc).isoformat()
            ),
            "action_type": action_type,
            "description": description,
            "metadata": metadata or {},
        }

        self.human_actions.append(action)

        return action

    # ==========================================================
    # RESUME AGENT
    # ==========================================================

    async def resume_agent(
        self,
        note: Optional[str] = None,
    ) -> dict[str, Any]:
        """
        Return control from human to agent.

        The current browser page is preserved.
        """

        if self.session.status != SessionStatus.WAITING_HUMAN:
            raise RuntimeError(
                "Session is not waiting for human intervention."
            )

        if self.session.control_owner != ControlOwner.HUMAN:
            raise RuntimeError(
                "Human does not currently own the session."
            )

        if note:
            self.record_human_action(
                action_type="handoff_note",
                description=note,
            )

        self.resumed_at = (
            datetime.now(timezone.utc).isoformat()
        )

        # ------------------------------------------------------
        # Give control back to agent
        # ------------------------------------------------------

        self.session.resume_after_human()

        # ------------------------------------------------------
        # Capture page after human intervention
        # ------------------------------------------------------

        screenshot = None

        try:
            screenshot = (
                await self.session.capture_screenshot(
                    category="handoff"
                )
            )
        except Exception:
            screenshot = None

        return {
            "success": True,
            "intervention_id": self.intervention_id,
            "session_id": self.session.session_id,
            "control_owner": self.session.control_owner.value,
            "status": self.session.status.value,
            "screenshot": screenshot,
            "human_actions": self.human_actions,
            "message": (
                "Human control released. "
                "Agent can resume using the same session."
            ),
        }

    # ==========================================================
    # CURRENT INTERVENTION
    # ==========================================================

    def get_intervention(self) -> dict[str, Any]:
        """
        Return the complete intervention state.
        """

        return {
            "intervention_id": self.intervention_id,
            "session_id": self.session.session_id,
            "reason": self.reason,
            "requested_at": self.requested_at,
            "human_started_at": self.human_started_at,
            "resumed_at": self.resumed_at,
            "context": self.context,
            "human_actions": self.human_actions,
            "session": self.session.get_status(),
        }

    # ==========================================================
    # SAME LIVE PAGE
    # ==========================================================

    def get_live_page(self):
        """
        Return the existing Playwright page.

        This is important because the human must operate
        the SAME live session.
        """

        return self.session.get_page()