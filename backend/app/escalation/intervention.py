from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional
from uuid import uuid4


class InterventionStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CANCELLED = "cancelled"


class InterventionReason(str, Enum):
    AGENT_STUCK = "agent_stuck"
    REPLAY_FAILURE = "replay_failure"
    RISKY_ACTION = "risky_action"
    UNEXPECTED_STATE = "unexpected_state"
    PERMISSION_DENIED = "permission_denied"
    SESSION_TIMEOUT = "session_timeout"
    UNKNOWN = "unknown"


class InterventionRequest:
    """
    Represents a request for human intervention.

    This object contains the minimum context required
    for an operator to understand why automation stopped.
    """

    def __init__(
        self,
        session_id: str,
        reason: InterventionReason,
        message: str,
        current_step: int = 0,
        goal: Optional[str] = None,
        screenshot_path: Optional[str] = None,
        observation: Optional[dict[str, Any]] = None,
    ):
        self.intervention_id = (
            f"int_{uuid4().hex[:12]}"
        )

        self.session_id = session_id

        self.reason = reason

        self.message = message

        self.current_step = current_step

        self.goal = goal

        self.screenshot_path = screenshot_path

        self.observation = observation or {}

        self.status = InterventionStatus.PENDING

        self.created_at = datetime.now(
            timezone.utc
        ).isoformat()

        self.updated_at = self.created_at

        self.operator_id: Optional[str] = None

        self.human_actions: list[dict[str, Any]] = []

    # -----------------------------------------
    # Assign operator
    # -----------------------------------------

    def assign_operator(
        self,
        operator_id: str,
    ):
        self.operator_id = operator_id

        self.status = InterventionStatus.IN_PROGRESS

        self.updated_at = datetime.now(
            timezone.utc
        ).isoformat()

    # -----------------------------------------
    # Record human action
    # -----------------------------------------

    def record_human_action(
        self,
        action: str,
        details: Optional[dict[str, Any]] = None,
    ):
        self.human_actions.append(
            {
                "action": action,
                "details": details or {},
                "timestamp": datetime.now(
                    timezone.utc
                ).isoformat(),
            }
        )

        self.updated_at = datetime.now(
            timezone.utc
        ).isoformat()

    # -----------------------------------------
    # Resolve
    # -----------------------------------------

    def resolve(
        self,
        resolution: str,
    ):
        self.record_human_action(
            action="resolution",
            details={
                "resolution": resolution,
            },
        )

        self.status = InterventionStatus.RESOLVED

        self.updated_at = datetime.now(
            timezone.utc
        ).isoformat()

    # -----------------------------------------
    # Cancel
    # -----------------------------------------

    def cancel(self):
        self.status = InterventionStatus.CANCELLED

        self.updated_at = datetime.now(
            timezone.utc
        ).isoformat()

    # -----------------------------------------
    # Serialization
    # -----------------------------------------

    def to_dict(self) -> dict[str, Any]:

        return {
            "intervention_id": self.intervention_id,
            "session_id": self.session_id,
            "reason": self.reason.value,
            "message": self.message,
            "current_step": self.current_step,
            "goal": self.goal,
            "screenshot_path": self.screenshot_path,
            "observation": self.observation,
            "status": self.status.value,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "operator_id": self.operator_id,
            "human_actions": self.human_actions,
        }