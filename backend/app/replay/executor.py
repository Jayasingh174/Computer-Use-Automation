from typing import Any

from app.agent.action_executor import ActionExecutor
from app.automation.session import AutomationSession


class ReplayExecutor:
    def __init__(self, session: AutomationSession):
        self.session = session
        self.action_executor = ActionExecutor(session)

    def resolve_value(self, value: Any, parameters: dict[str, Any]) -> Any:
        if not isinstance(value, str):
            return value
        resolved = value
        for key, parameter_value in parameters.items():
            placeholder = f"{{{{{key}}}}}"
            resolved = resolved.replace(placeholder, str(parameter_value))
        return resolved

    async def execute_step(self, step: Any, parameters: dict[str, Any]) -> dict[str, Any]:
        action_data = step.model_dump() if hasattr(step, "model_dump") else step

        action_type = action_data.get("action_type")
        if hasattr(action_type, "value"):
            action_type = action_type.value

        target = action_data.get("target") or {}
        if hasattr(target, "model_dump"):
            target = target.model_dump()

        value = self.resolve_value(action_data.get("value"), parameters)

        # ActionExecutor.execute() expects ONE dict with a "type" key
        # (see fix #4 for the canonical action-dict shape).
        result = await self.action_executor.execute({
            "type": action_type,
            "locator": target,
            "value": value,
        })

        return {
            "success": True,
            "step": action_data.get("step"),
            "action": action_type,
            "target": target,
            "value": value,
            "result": result,
        }

    async def execute(self, steps: list[Any], parameters: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        parameters = parameters or {}
        results = []
        for step in steps:
            try:
                results.append(await self.execute_step(step, parameters))
            except Exception as exc:
                results.append({
                    "success": False,
                    "step": step.step if hasattr(step, "step") else step.get("step"),
                    "error": {"type": type(exc).__name__, "message": str(exc)},
                })
                break
        return results
