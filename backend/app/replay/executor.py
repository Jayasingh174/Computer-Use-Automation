from typing import Any

from playwright.async_api import Page

from app.agent.action_executor import ActionExecutor


class ReplayExecutor:
    """
    Executes saved artifact actions deterministically.

    IMPORTANT:
    - No LLM is used.
    - No planner is used.
    - Actions come directly from the saved artifact.
    - ActionExecutor performs the actual Playwright operation.
    """

    def __init__(self, page: Page):
        self.page = page
        self.action_executor = ActionExecutor(page)

    # =========================================================
    # PARAMETER RESOLUTION
    # =========================================================

    def resolve_value(
        self,
        value: Any,
        parameters: dict[str, Any],
    ) -> Any:
        """
        Replace {{parameter}} placeholders with actual values.
        """

        if not isinstance(value, str):
            return value

        resolved = value

        for key, parameter_value in parameters.items():

            placeholder = f"{{{{{key}}}}}"

            resolved = resolved.replace(
                placeholder,
                str(parameter_value),
            )

        return resolved

    # =========================================================
    # EXECUTE ONE ACTION
    # =========================================================

    async def execute_step(
        self,
        step: Any,
        parameters: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Execute one ArtifactAction.
        """

        # -----------------------------------------------------
        # Support Pydantic ArtifactAction
        # -----------------------------------------------------

        if hasattr(step, "model_dump"):
            action_data = step.model_dump()

        elif isinstance(step, dict):
            action_data = step

        else:
            raise TypeError(
                f"Unsupported action type: {type(step).__name__}"
            )

        # -----------------------------------------------------
        # Get action type
        # -----------------------------------------------------

        action_type = action_data.get(
            "action_type"
        )

        if hasattr(action_type, "value"):
            action_type = action_type.value

        # -----------------------------------------------------
        # Get target
        # -----------------------------------------------------

        target = action_data.get(
            "target"
        )

        if target is None:
            target = {}

        # Pydantic Locator → dictionary
        if hasattr(target, "model_dump"):
            target = target.model_dump()

        # -----------------------------------------------------
        # Get value
        # -----------------------------------------------------

        value = action_data.get(
            "value"
        )

        value = self.resolve_value(
            value=value,
            parameters=parameters,
        )

        # -----------------------------------------------------
        # Execute through ActionExecutor
        # -----------------------------------------------------

        result = await self.action_executor.execute(
            action=action_type,
            target=target,
            value=value,
        )

        return {
            "success": True,
            "step": action_data.get("step"),
            "action": action_type,
            "target": target,
            "value": value,
            "result": result,
        }

    # =========================================================
    # EXECUTE ALL ACTIONS
    # =========================================================

    async def execute(
        self,
        steps: list[Any],
        parameters: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Execute all recorded actions sequentially.
        """

        if parameters is None:
            parameters = {}

        results = []

        for step in steps:

            try:

                result = await self.execute_step(
                    step=step,
                    parameters=parameters,
                )

                results.append(result)

            except Exception as exc:

                results.append(
                    {
                        "success": False,
                        "step": (
                            step.step
                            if hasattr(step, "step")
                            else step.get("step")
                        ),
                        "error": {
                            "type": type(exc).__name__,
                            "message": str(exc),
                        },
                    }
                )

                # Deterministic replay should stop
                # when one recorded action fails.
                break

        return results