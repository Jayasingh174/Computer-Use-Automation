from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field, ConfigDict


# ============================================================
# ENUMS
# ============================================================

class ActionType(str, Enum):
    NAVIGATE = "navigate"
    CLICK = "click"
    TYPE = "type"
    SELECT = "select"
    PRESS = "press"
    WAIT = "wait"
    EXTRACT = "extract"


class LocatorStrategy(str, Enum):
    TEST_ID = "test_id"
    ROLE = "role"
    LABEL = "label"
    TEXT = "text"
    CSS = "css"
    XPATH = "xpath"
    URL = "url"


class RiskLevel(str, Enum):
    SAFE = "safe"
    REQUIRES_CONFIRMATION = "requires_confirmation"
    BLOCKED = "blocked"


class ArtifactStatus(str, Enum):
    DRAFT = "draft"
    APPROVED = "approved"
    ACTIVE = "active"
    DISABLED = "disabled"


class ParameterType(str, Enum):
    STRING = "string"
    INTEGER = "integer"
    NUMBER = "number"
    BOOLEAN = "boolean"


# ============================================================
# LOCATOR
# ============================================================

class Locator(BaseModel):
    """
    Describes how an element/control should be located
    during deterministic replay.
    """

    model_config = ConfigDict(
        extra="forbid"
    )

    strategy: LocatorStrategy

    value: str

    fallback: Optional["Locator"] = None

    description: Optional[str] = None


# ============================================================
# ACTION
# ============================================================

class ArtifactAction(BaseModel):
    """
    One deterministic action in the recorded workflow.
    """

    model_config = ConfigDict(
        extra="forbid"
    )

    step: int

    action_type: ActionType

    target: Optional[Locator] = None

    value: Optional[Any] = None

    description: Optional[str] = None

    risk_level: RiskLevel = RiskLevel.SAFE

    timeout_ms: int = 10000


# ============================================================
# CHECKPOINT
# ============================================================

class Checkpoint(BaseModel):
    """
    Confirms that the expected UI state has been reached.
    """

    model_config = ConfigDict(
        extra="forbid"
    )

    type: str

    locator: Optional[Locator] = None

    expected_value: Optional[str] = None

    description: str


# ============================================================
# PARAMETER
# ============================================================

class ArtifactParameter(BaseModel):
    """
    Input supplied by the calling AI agent.
    """

    model_config = ConfigDict(
        extra="forbid"
    )

    name: str

    type: ParameterType

    required: bool = True

    description: str

    example: Optional[Any] = None


# ============================================================
# OUTPUT
# ============================================================

class ArtifactOutput(BaseModel):
    """
    Data returned to the calling AI agent.
    """

    model_config = ConfigDict(
        extra="forbid"
    )

    name: str

    type: ParameterType

    source: Locator

    description: str


# ============================================================
# CAPABILITY ARTIFACT
# ============================================================

class CapabilityArtifact(BaseModel):
    """
    Reusable computer-use capability.

    This is the contract between discovery and replay.
    """

    model_config = ConfigDict(
        extra="forbid"
    )

    artifact_id: str

    name: str

    description: str

    version: str = "1.0.0"

    status: ArtifactStatus = ArtifactStatus.DRAFT

    application: str

    target_url: str

    created_at: str

    updated_at: str

    parameters: list[ArtifactParameter] = Field(
        default_factory=list
    )

    actions: list[ArtifactAction] = Field(
        default_factory=list
    )

    outputs: list[ArtifactOutput] = Field(
        default_factory=list
    )

    checkpoint: Checkpoint

    metadata: dict[str, Any] = Field(
        default_factory=dict
    )