from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


# ============================================================
# ENUM-LIKE TYPES
# ============================================================

ActionType = Literal[
    "navigate",
    "click",
    "type",
    "select",
    "press",
    "wait",
    "extract",
    "screenshot",
    "finish",
]


TargetStrategy = Literal[
    "role",
    "label",
    "text",
    "placeholder",
    "test_id",
    "css",
    "xpath",
    "url",
]


ActionRisk = Literal[
    "safe",
    "reversible",
    "risky",
    "irreversible",
]


CheckpointType = Literal[
    "url",
    "element",
    "text",
    "value",
    "custom",
]


OutputType = Literal[
    "string",
    "integer",
    "number",
    "boolean",
    "object",
    "array",
]


# ============================================================
# TARGET
# ============================================================

class ArtifactTarget(BaseModel):
    """
    Describes how a UI element/control is identified.

    Multiple locator strategies can be stored so that replay
    has a deterministic primary strategy and optional fallbacks.
    """

    strategy: TargetStrategy

    value: str

    description: Optional[str] = None

    priority: int = Field(
        default=1,
        ge=1,
    )

    exact: bool = False


# ============================================================
# ACTION
# ============================================================

class ArtifactAction(BaseModel):
    """
    One deterministic action in a recorded capability.
    """

    step: int = Field(
        ...,
        ge=1,
    )

    action: ActionType

    target: Optional[ArtifactTarget] = None

    value: Optional[str] = None

    risk: ActionRisk = "safe"

    description: Optional[str] = None

    wait_after_ms: int = Field(
        default=500,
        ge=0,
    )

    timeout_ms: int = Field(
        default=10000,
        ge=100,
    )


# ============================================================
# FALLBACK LOCATOR
# ============================================================

class ArtifactLocator(BaseModel):
    """
    Additional locator used when the primary locator cannot
    identify the control.

    Fallbacks are still deterministic. The LLM is NOT called
    during replay to choose a locator.
    """

    strategy: TargetStrategy

    value: str

    priority: int = Field(
        default=1,
        ge=1,
    )


# ============================================================
# CHECKPOINT
# ============================================================

class ArtifactCheckpoint(BaseModel):
    """
    Verifies that the expected UI state has been reached.
    """

    type: CheckpointType

    description: str

    target: Optional[ArtifactTarget] = None

    expected_value: Optional[str] = None

    required: bool = True

    timeout_ms: int = Field(
        default=10000,
        ge=100,
    )


# ============================================================
# INPUT PARAMETER
# ============================================================

class ArtifactInput(BaseModel):
    """
    Typed parameter supplied by the calling AI agent during replay.

    Example:
        member_id: string
    """

    name: str

    type: OutputType

    required: bool = True

    description: Optional[str] = None

    example: Optional[Any] = None


# ============================================================
# OUTPUT FIELD
# ============================================================

class ArtifactOutput(BaseModel):
    """
    Typed value extracted from the application and returned
    to the calling agent.
    """

    name: str

    type: OutputType

    description: Optional[str] = None

    source: Optional[ArtifactTarget] = None

    required: bool = True


# ============================================================
# ERROR HANDLING
# ============================================================

class ArtifactErrorRule(BaseModel):
    """
    Defines how deterministic replay should respond to a
    known runtime condition.
    """

    name: str

    description: str

    detection: ArtifactCheckpoint

    classification: Literal[
        "business_outcome",
        "recoverable",
        "hard_failure",
    ]

    recovery_action: Optional[ArtifactAction] = None

    message: Optional[str] = None


# ============================================================
# CAPABILITY METADATA
# ============================================================

class ArtifactMetadata(BaseModel):
    """
    Metadata describing where and how the capability was created.
    """

    application_name: str

    application_version: Optional[str] = None

    surface_type: Literal[
        "web",
        "legacy_web",
        "desktop",
    ] = "web"

    source_url: str

    tenant_id: Optional[str] = None

    created_by: str = "llm_discovery"


# ============================================================
# MAIN ARTIFACT
# ============================================================

class AutomationArtifact(BaseModel):
    """
    Reusable, versioned computer-use capability.

    This is the central artifact produced by the discovery run
    and consumed by deterministic replay.
    """

    artifact_id: str

    name: str

    description: str

    schema_version: str = "1.0"

    capability_version: int = 1

    status: Literal[
        "draft",
        "approved",
        "deprecated",
    ] = "draft"

    metadata: ArtifactMetadata

    inputs: list[ArtifactInput] = Field(
        default_factory=list
    )

    outputs: list[ArtifactOutput] = Field(
        default_factory=list
    )

    actions: list[ArtifactAction] = Field(
        default_factory=list
    )

    checkpoints: list[ArtifactCheckpoint] = Field(
        default_factory=list
    )

    error_rules: list[ArtifactErrorRule] = Field(
        default_factory=list
    )

    created_at: str

    updated_at: str

    source_session_id: Optional[str] = None      