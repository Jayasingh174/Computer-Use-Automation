from enum import Enum
from typing import Any, Optional


class ErrorCategory(str, Enum):
    BUSINESS_OUTCOME = "business_outcome"
    RECOVERABLE = "recoverable"
    HARD_FAILURE = "hard_failure"
    SAFETY_BLOCK = "safety_block"
    TIMEOUT = "timeout"
    UNKNOWN = "unknown"


class ReplayError:
    """
    Structured replay error.

    Separates:
    - expected business outcomes
    - recoverable conditions
    - hard failures
    """

    def __init__(
        self,
        category: ErrorCategory,
        message: str,
        step: int,
        expected: Optional[str] = None,
        observed: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
    ):

        self.category = category

        self.message = message

        self.step = step

        self.expected = expected

        self.observed = observed

        self.details = details or {}

    def to_dict(self) -> dict[str, Any]:

        return {
            "category": self.category.value,
            "message": self.message,
            "step": self.step,
            "expected": self.expected,
            "observed": self.observed,
            "details": self.details,
        }


class ReplayErrorHandler:
    """
    Classifies and handles replay errors.
    """

    def classify(
        self,
        error: Exception,
        step: int,
    ) -> ReplayError:

        message = str(error)

        message_lower = message.lower()

        if "timeout" in message_lower:

            return ReplayError(
                category=ErrorCategory.TIMEOUT,
                message=message,
                step=step,
            )

        if "not found" in message_lower:

            return ReplayError(
                category=ErrorCategory.BUSINESS_OUTCOME,
                message=message,
                step=step,
            )

        if "permission" in message_lower:

            return ReplayError(
                category=ErrorCategory.SAFETY_BLOCK,
                message=message,
                step=step,
            )

        return ReplayError(
            category=ErrorCategory.HARD_FAILURE,
            message=message,
            step=step,
        )