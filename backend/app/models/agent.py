from typing import Any, Optional

from pydantic import BaseModel, Field


# ============================================================
# Agent Run Request
# ============================================================

class AgentRunRequest(BaseModel):
    """
    Input provided by the caller to start a computer-use
    discovery run.
    """

    goal: str = Field(
        ...,
        description="Natural-language goal the agent must accomplish.",
        min_length=1,
    )

    target_url: Optional[str] = Field(
        default=None,
        description="URL of the application the agent should operate.",
    )

    headless: bool = Field(
        default=False,
        description="Run browser in headless mode.",
    )


# ============================================================
# Agent Test Request
# ============================================================

class AgentTestRequest(BaseModel):
    """
    Simple request used to test the LLM connection.
    """

    prompt: str = Field(
        ...,
        description="Prompt sent to the LLM.",
        min_length=1,
    )


# ============================================================
# Agent Action
# ============================================================

class AgentAction(BaseModel):
    """
    Action selected by the planner.
    """

    action: str = Field(
        ...,
        description="Action type such as click, type, navigate, read, wait, or finish.",
    )

    target: Optional[str] = Field(
        default=None,
        description="Target element or control.",
    )

    value: Optional[str] = Field(
        default=None,
        description="Value associated with the action.",
    )

    reasoning: Optional[str] = Field(
        default=None,
        description="Short explanation for why the action was selected.",
    )


# ============================================================
# Agent Step
# ============================================================

class AgentStep(BaseModel):
    """
    Represents one observe -> decide -> act cycle.
    """

    step: int

    observation: Optional[dict[str, Any]] = None

    action: Optional[AgentAction] = None

    status: str = "pending"

    error: Optional[str] = None


# ============================================================
# Agent Run Response
# ============================================================

class AgentRunResponse(BaseModel):
    """
    Response returned after an agent discovery run.
    """

    success: bool

    session_id: str

    status: str

    goal: str

    current_step: int = 0

    steps: list[AgentStep] = Field(
        default_factory=list
    )

    artifact_id: Optional[str] = None

    output: Optional[dict[str, Any]] = None

    error: Optional[str] = None