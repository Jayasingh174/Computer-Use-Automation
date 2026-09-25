from enum import Enum
from typing import Any


class ActionRisk(str, Enum):
    SAFE = "safe"
    RISKY = "risky"
    BLOCKED = "blocked"


class ActionPolicy:
    """
    Defines which computer-use actions are permitted.
    """

        SAFE_ACTIONS = {
        "click", "fill", "navigate", "wait", "select", "press", "extract",
    }

    RISKY_ACTIONS = {
        "submit",
        "create_account",
        "delete",
        "transfer",
        "confirm_transaction",
    }

    BLOCKED_ACTIONS = {
        "execute_shell",
        "download_file",
        "upload_file",
        "change_password",
    }

    def classify(self, action_type: str) -> ActionRisk:

        if action_type in self.BLOCKED_ACTIONS:
            return ActionRisk.BLOCKED

        if action_type in self.RISKY_ACTIONS:
            return ActionRisk.RISKY

        if action_type in self.SAFE_ACTIONS:
            return ActionRisk.SAFE

        return ActionRisk.BLOCKED

    def validate(
        self,
        action: dict[str, Any],
        require_confirmation: bool = True,
    ) -> dict[str, Any]:

        action_type = action.get("type")

        if not action_type:
            raise PermissionError(
                "Action type is missing."
            )

        risk = self.classify(action_type)

        if risk == ActionRisk.BLOCKED:
            raise PermissionError(
                f"Action blocked by safety policy: "
                f"{action_type}"
            )

        if (
            risk == ActionRisk.RISKY
            and require_confirmation
        ):
            raise PermissionError(
                f"Risky action requires human confirmation: "
                f"{action_type}"
            )

        return {
            "allowed": True,
            "action_type": action_type,
            "risk": risk.value,
        }
