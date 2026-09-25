from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class InterventionType(str, Enum):
    """
    Reason why the AI agent needs human intervention.
    """

    SENSITIVE_ACTION = "sensitive_action"
    AUTHENTICATION = "authentication"
    CAPTCHA = "captcha"
    UNKNOWN_STATE = "unknown_state"
    ACTION_FAILED = "action_failed"
    USER_REQUEST = "user_request"
    OTHER = "other"


class InterventionStatus(str, Enum):
    """
    Current state of a human intervention.
    """

    PENDING = "pending"
    HUMAN_CONTROL = "human_control"
    RESUMED = "resumed"
    CANCELLED = "cancelled"


class InterventionRequest(BaseModel):
    """
    Represents a request from the AI agent for human assistance.
    """

    type: InterventionType
    reason: str
    message: Optional[str] = None

    status: InterventionStatus = InterventionStatus.PENDING

    metadata: dict = Field(default_factory=dict)


class InterventionResult(BaseModel):
    """
    Result returned after human intervention.
    """

    success: bool
    status: InterventionStatus
    note: Optional[str] = None
