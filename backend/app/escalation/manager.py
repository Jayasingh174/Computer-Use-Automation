from typing import Any, Optional

from app.automation.session import AutomationSession
from app.escalation.intervention import (
    InterventionReason,
    InterventionRequest,
)


class InterventionManager:
    """
    Manages human-in-the-loop escalation.

    Responsibilities:

    1. Detect/create intervention requests.
    2. Pause automation.
    3. Transfer control to human.
    4. Track human actions.
    5. Resume automation after resolution.
    """

    def __init__(self):

        self.interventions: dict[
            str,
            InterventionRequest,
        ] = {}

    # ==================================================
    # CREATE INTERVENTION
    # ==================================================

    async def create_intervention(
        self,
        session: AutomationSession,
        reason: InterventionReason,
        message: str,
        goal: Optional[str] = None,
        observation: Optional[dict[str, Any]] = None,
    ) -> InterventionRequest:

        screenshot_path = None

        # ------------------------------------------
        # Capture screenshot
        # ------------------------------------------

        try:

            page = session.get_page()

            screenshot_path = (
                f"evidence/handoff/"
                f"{session.session_id}_"
                f"step_{session.current_step}.png"
            )

            await page.screenshot(
                path=screenshot_path,
                full_page=True,
            )

        except Exception:
            # Screenshot failure should not prevent
            # human escalation.
            screenshot_path = None

        # ------------------------------------------
        # Create request
        # ------------------------------------------

        intervention = InterventionRequest(
            session_id=session.session_id,
            reason=reason,
            message=message,
            current_step=session.current_step,
            goal=goal,
            screenshot_path=screenshot_path,
            observation=observation,
        )

        self.interventions[
            intervention.intervention_id
        ] = intervention

        # ------------------------------------------
        # Transfer control
        # ------------------------------------------

        session.request_human_control(
            reason=message
        )

        return intervention

    # ==================================================
    # GET INTERVENTION
    # ==================================================

    def get_intervention(
        self,
        intervention_id: str,
    ) -> InterventionRequest:

        intervention = self.interventions.get(
            intervention_id
        )

        if intervention is None:

            raise KeyError(
                f"Intervention not found: "
                f"{intervention_id}"
            )

        return intervention

    # ==================================================
    # LIST INTERVENTIONS
    # ==================================================

    def list_interventions(self) -> list[dict[str, Any]]:

        return [
            intervention.to_dict()
            for intervention
            in self.interventions.values()
        ]

    # ==================================================
    # ASSIGN HUMAN
    # ==================================================

    def assign_operator(
        self,
        intervention_id: str,
        operator_id: str,
    ):

        intervention = self.get_intervention(
            intervention_id
        )

        intervention.assign_operator(
            operator_id
        )

        return intervention.to_dict()

    # ==================================================
    # RECORD HUMAN ACTION
    # ==================================================

    def record_human_action(
        self,
        intervention_id: str,
        action: str,
        details: Optional[dict[str, Any]] = None,
    ):

        intervention = self.get_intervention(
            intervention_id
        )

        intervention.record_human_action(
            action=action,
            details=details,
        )

        return intervention.to_dict()

    # ==================================================
    # RESOLVE
    # ==================================================

    async def resolve_intervention(
        self,
        intervention_id: str,
        session: AutomationSession,
        resolution: str,
    ):

        intervention = self.get_intervention(
            intervention_id
        )

        intervention.resolve(
            resolution
        )

        # ------------------------------------------
        # Give control back to agent
        # ------------------------------------------

        session.resume_after_human()

        return {
            "success": True,
            "intervention": intervention.to_dict(),
            "session": session.get_status(),
        }

    # ==================================================
    # CANCEL
    # ==================================================

    def cancel_intervention(
        self,
        intervention_id: str,
    ):

        intervention = self.get_intervention(
            intervention_id
        )

        intervention.cancel()

        return intervention.to_dict()