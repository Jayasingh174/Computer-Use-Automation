from typing import Any

from app.automation.session import AutomationSession
from app.automation.locators import LocatorResolver
from app.safety.allowlist import AllowlistManager
from app.safety.policy import ActionPolicy


class ActionExecutor:
    def __init__(self, session: AutomationSession):
        self.session = session
        self.policy = ActionPolicy()
        self.allowlist = AllowlistManager()
        self.locators = LocatorResolver()

    async def execute(self, action: dict[str, Any]) -> dict[str, Any]:
        safety_result = self.policy.validate(action)
        page = self.session.get_page()
        action_type = action["type"]

        if action_type == "navigate":
            url = action["value"]
            self.allowlist.validate_url(url)
            await page.goto(url)
            return {"success": True, "action": action_type, "risk": safety_result["risk"], "url": url}

        if action_type in {"click", "fill", "select", "press", "extract"}:
            locator = await self.locators.find(page, action.get("locator") or {})

            if action_type == "click":
                await locator.click()
                return {"success": True, "action": action_type, "risk": safety_result["risk"]}

            if action_type == "fill":
                await locator.fill(action["value"])
                return {"success": True, "action": action_type, "risk": safety_result["risk"]}

            if action_type == "select":
                await locator.select_option(action["value"])
                return {"success": True, "action": action_type, "risk": safety_result["risk"]}

            if action_type == "press":
                await locator.press(action["value"])
                return {"success": True, "action": action_type, "risk": safety_result["risk"]}

            if action_type == "extract":
                text = await locator.inner_text()
                return {"success": True, "action": action_type, "risk": safety_result["risk"], "value": text}

        if action_type == "wait":
            milliseconds = action.get("value") or 1000
            await page.wait_for_timeout(milliseconds)
            return {"success": True, "action": action_type, "risk": safety_result["risk"]}

        raise ValueError(f"Unsupported action: {action_type}")
