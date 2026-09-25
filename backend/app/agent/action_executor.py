from typing import Any

from app.automation.session import AutomationSession
from app.safety.allowlist import AllowlistManager
from app.safety.policy import ActionPolicy


class ActionExecutor:
    """
    Executes validated computer-use actions.

    Safety validation happens before any browser
    interaction.
    """

    def __init__(
        self,
        session: AutomationSession,
    ):
        self.session = session

        self.policy = ActionPolicy()
        self.allowlist = AllowlistManager()

    async def execute(
        self,
        action: dict[str, Any],
    ) -> dict[str, Any]:

        # -----------------------------------------
        # 1. Safety validation
        # -----------------------------------------

        safety_result = self.policy.validate(
            action
        )

        # -----------------------------------------
        # 2. Get browser page
        # -----------------------------------------

        page = self.session.get_page()

        action_type = action["type"]

        # -----------------------------------------
        # 3. Execute navigation
        # -----------------------------------------

        if action_type == "navigate":

            url = action["url"]

            self.allowlist.validate_url(url)

            await page.goto(url)

            return {
                "success": True,
                "action": action_type,
                "risk": safety_result["risk"],
                "url": url,
            }

        # -----------------------------------------
        # 4. Click
        # -----------------------------------------

        if action_type == "click":

            locator = action["locator"]

            await page.locator(locator).click()

            return {
                "success": True,
                "action": action_type,
                "risk": safety_result["risk"],
            }

        # -----------------------------------------
        # 5. Type
        # -----------------------------------------

        if action_type == "type":

            locator = action["locator"]
            value = action["value"]

            await page.locator(locator).fill(value)

            return {
                "success": True,
                "action": action_type,
                "risk": safety_result["risk"],
            }

        # -----------------------------------------
        # 6. Read
        # -----------------------------------------

        if action_type == "read":

            locator = action["locator"]

            text = await page.locator(
                locator
            ).inner_text()

            return {
                "success": True,
                "action": action_type,
                "risk": safety_result["risk"],
                "value": text,
            }

        # -----------------------------------------
        # 7. Wait
        # -----------------------------------------

        if action_type == "wait":

            milliseconds = action.get(
                "milliseconds",
                1000,
            )

            await page.wait_for_timeout(
                milliseconds
            )

            return {
                "success": True,
                "action": action_type,
                "risk": safety_result["risk"],
            }

        raise ValueError(
            f"Unsupported action: {action_type}"
        )