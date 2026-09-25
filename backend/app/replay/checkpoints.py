from typing import Any

from playwright.async_api import Page


class CheckpointVerifier:
    """
    Verifies that the expected UI state has been reached.
    """

    def __init__(
        self,
        page: Page,
    ):
        self.page = page

    async def verify(
        self,
        checkpoint: dict[str, Any],
    ) -> dict[str, Any]:

        checkpoint_type = checkpoint.get(
            "type"
        )

        # ----------------------------------------
        # URL checkpoint
        # ----------------------------------------

        if checkpoint_type == "url":

            expected = checkpoint["value"]

            actual = self.page.url

            success = (
                actual == expected
                or expected in actual
            )

            return {
                "success": success,
                "type": "url",
                "expected": expected,
                "observed": actual,
            }

        # ----------------------------------------
        # Text checkpoint
        # ----------------------------------------

        if checkpoint_type == "text":

            expected = checkpoint["value"]

            body_text = await self.page.locator(
                "body"
            ).inner_text()

            success = (
                expected.lower()
                in body_text.lower()
            )

            return {
                "success": success,
                "type": "text",
                "expected": expected,
                "observed": (
                    body_text[:1000]
                ),
            }

        # ----------------------------------------
        # Element checkpoint
        # ----------------------------------------

        if checkpoint_type == "element":

            selector = checkpoint["selector"]

            locator = self.page.locator(
                selector
            )

            success = await locator.count() > 0

            return {
                "success": success,
                "type": "element",
                "selector": selector,
            }

        raise ValueError(
            f"Unsupported checkpoint type: "
            f"{checkpoint_type}"
        )