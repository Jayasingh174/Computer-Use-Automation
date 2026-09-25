import json
from typing import Any, Optional

from groq import Groq
from pydantic import BaseModel, Field

from app.agent.prompts import (
    SYSTEM_PROMPT,
    build_planner_prompt,
)
from app.config.settings import settings


# ==========================================================
# ACTION TARGET
# ==========================================================


class ActionTarget(BaseModel):
    """
    Describes how the browser element should be located.
    """

    strategy: str

    role: Optional[str] = None

    name: Optional[str] = None

    label: Optional[str] = None

    placeholder: Optional[str] = None

    test_id: Optional[str] = None

    id: Optional[str] = None

    text: Optional[str] = None

    selector: Optional[str] = None

    index: Optional[int] = None


# ==========================================================
# CHECKPOINT
# ==========================================================


class ActionCheckpoint(BaseModel):
    """
    Condition that should be verified after an action.
    """

    type: Optional[str] = None

    value: Optional[str] = None

    target: Optional[ActionTarget] = None


# ==========================================================
# PLANNER ACTION
# ==========================================================


class PlannerAction(BaseModel):
    """
    Structured action returned by the LLM planner.
    """

    action: str

    target: Optional[ActionTarget] = None

    value: Optional[str] = None

    reason: str

    confidence: float = Field(
        ge=0.0,
        le=1.0,
    )

    risk: str

    expected_result: str

    checkpoint: Optional[ActionCheckpoint] = None


# ==========================================================
# PLANNER RESULT
# ==========================================================


class PlannerResult(BaseModel):
    """
    Complete planner result.

    raw_response is useful for debugging/evidence,
    while action is the structured contract consumed
    by ActionExecutor.
    """

    success: bool

    action: Optional[PlannerAction] = None

    raw_response: Optional[str] = None

    error: Optional[str] = None


# ==========================================================
# PLANNER
# ==========================================================


class ComputerUsePlanner:

    def __init__(self):

        self.client = Groq(
            api_key=settings.groq_api_key
        )

        self.model = settings.groq_model

        self.allowed_actions = [
            "navigate",
            "click",
            "fill",
            "select",
            "press",
            "wait",
            "extract",
            "goal_complete",
            "escalate",
        ]

    # ======================================================
    # PLAN
    # ======================================================

    def plan(
        self,
        goal: str,
        observation: dict[str, Any],
    ) -> PlannerResult:

        user_prompt = build_planner_prompt(
            goal=goal,
            observation=observation,
            allowed_actions=self.allowed_actions,
        )

        try:

            completion = self.client.chat.completions.create(
                model=self.model,

                messages=[
                    {
                        "role": "system",
                        "content": SYSTEM_PROMPT,
                    },
                    {
                        "role": "user",
                        "content": user_prompt,
                    },
                ],

                temperature=0.0,

                response_format={
                    "type": "json_object"
                },
            )

            raw_response = (
                completion
                .choices[0]
                .message
                .content
            )

            if not raw_response:
                raise ValueError(
                    "LLM returned an empty response."
                )

            parsed = json.loads(
                raw_response
            )

            action = PlannerAction.model_validate(
                parsed
            )

            # ------------------------------------------
            # Validate action type
            # ------------------------------------------

            if action.action not in self.allowed_actions:

                raise ValueError(
                    f"Unsupported action: "
                    f"{action.action}"
                )

            # ------------------------------------------
            # Validate confidence
            # ------------------------------------------

            if (
                action.confidence < 0.50
                and action.action != "escalate"
            ):

                raise ValueError(
                    "Planner confidence is too low "
                    "for autonomous execution."
                )

            # ------------------------------------------
            # Return structured result
            # ------------------------------------------

            return PlannerResult(
                success=True,
                action=action,
                raw_response=raw_response,
            )

        except Exception as exc:

            return PlannerResult(
                success=False,
                raw_response=None,
                error=str(exc),
            )