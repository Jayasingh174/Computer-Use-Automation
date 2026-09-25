from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from playwright.async_api import Page


class ObservationError(Exception):
    """Raised when the browser state cannot be observed."""


class PageObserver:
    """
    Converts the current Playwright page into a structured
    observation that can be consumed by the planner/LLM.

    Responsibilities:
    - Read current browser state
    - Extract visible UI information
    - Identify interactive controls
    - Capture screenshots
    - Return structured JSON-compatible data

    Does NOT:
    - Call the LLM
    - Decide what action to take
    - Execute browser actions
    """

    def __init__(
        self,
        page: Page,
        evidence_dir: str = "evidence/discovery",
    ):
        self.page = page

        self.evidence_dir = Path(evidence_dir)

        self.evidence_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

    # ==================================================
    # PUBLIC OBSERVE METHOD
    # ==================================================

    async def observe(
        self,
        step: int = 0,
        capture_screenshot: bool = True,
    ) -> dict[str, Any]:

        observation_id = (
            f"obs_{uuid4().hex[:12]}"
        )

        observed_at = datetime.now(
            timezone.utc
        ).isoformat()

        try:

            # ------------------------------------------
            # Basic page information
            # ------------------------------------------

            url = self.page.url

            title = await self.page.title()

            # ------------------------------------------
            # Visible page text
            # ------------------------------------------

            visible_text = await self._get_visible_text()

            # ------------------------------------------
            # Interactive elements
            # ------------------------------------------

            elements = await self._get_interactive_elements()

            # ------------------------------------------
            # Forms / inputs
            # ------------------------------------------

            inputs = await self._get_inputs()

            # ------------------------------------------
            # Buttons
            # ------------------------------------------

            buttons = await self._get_buttons()

            # ------------------------------------------
            # Links
            # ------------------------------------------

            links = await self._get_links()

            # ------------------------------------------
            # Screenshot
            # ------------------------------------------

            screenshot_path = None

            if capture_screenshot:

                screenshot_path = (
                    await self._capture_screenshot(
                        observation_id,
                        step,
                    )
                )

            # ------------------------------------------
            # Final observation
            # ------------------------------------------

            observation = {
                "observation_id": observation_id,

                "timestamp": observed_at,

                "step": step,

                "page": {
                    "url": url,
                    "title": title,
                },

                "visible_text": visible_text,

                "interactive_elements": elements,

                "inputs": inputs,

                "buttons": buttons,

                "links": links,

                "screenshot": screenshot_path,
            }

            return observation

        except Exception as exc:

            raise ObservationError(
                f"Failed to observe page: {exc}"
            ) from exc

    # ==================================================
    # VISIBLE TEXT
    # ==================================================

    async def _get_visible_text(self) -> str:

        body = self.page.locator("body")

        if await body.count() == 0:
            return ""

        text = await body.inner_text()

        return text.strip()

    # ==================================================
    # INTERACTIVE ELEMENTS
    # ==================================================

    async def _get_interactive_elements(
        self,
    ) -> list[dict[str, Any]]:

        elements = []

        locator = self.page.locator(
            """
            button,
            input,
            textarea,
            select,
            a,
            [role="button"],
            [role="link"],
            [role="textbox"],
            [role="checkbox"],
            [role="radio"],
            [role="combobox"]
            """
        )

        count = await locator.count()

        for index in range(count):

            element = locator.nth(index)

            try:

                if not await element.is_visible():
                    continue

                data = await self._describe_element(
                    element,
                    index,
                )

                elements.append(data)

            except Exception:
                # One broken element should not
                # break the complete observation.
                continue

        return elements

    # ==================================================
    # DESCRIBE ELEMENT
    # ==================================================

    async def _describe_element(
        self,
        element,
        index: int,
    ) -> dict[str, Any]:

        tag_name = await element.evaluate(
            "(el) => el.tagName.toLowerCase()"
        )

        role = await element.get_attribute(
            "role"
        )

        element_id = await element.get_attribute(
            "id"
        )

        name = await element.get_attribute(
            "name"
        )

        placeholder = await element.get_attribute(
            "placeholder"
        )

        aria_label = await element.get_attribute(
            "aria-label"
        )

        test_id = await element.get_attribute(
            "data-testid"
        )

        text = ""

        try:
            text = (
                await element.inner_text()
            ).strip()
        except Exception:
            pass

        value = None

        try:

            if tag_name in {
                "input",
                "textarea",
                "select",
            }:

                value = await element.input_value()

        except Exception:
            pass

        input_type = await element.get_attribute(
            "type"
        )

        disabled = await element.is_disabled()

        checked = None

        try:

            if input_type in {
                "checkbox",
                "radio",
            }:

                checked = await element.is_checked()

        except Exception:
            pass

        return {
            "index": index,

            "tag": tag_name,

            "role": role,

            "id": element_id,

            "name": name,

            "text": text,

            "aria_label": aria_label,

            "placeholder": placeholder,

            "test_id": test_id,

            "input_type": input_type,

            "value": self._safe_value(value),

            "disabled": disabled,

            "checked": checked,
        }

    # ==================================================
    # INPUTS
    # ==================================================

    async def _get_inputs(
        self,
    ) -> list[dict[str, Any]]:

        inputs = []

        locator = self.page.locator(
            "input, textarea, select"
        )

        count = await locator.count()

        for index in range(count):

            element = locator.nth(index)

            try:

                if not await element.is_visible():
                    continue

                tag = await element.evaluate(
                    "(el) => el.tagName.toLowerCase()"
                )

                input_type = (
                    await element.get_attribute(
                        "type"
                    )
                )

                label = await self._get_label(
                    element
                )

                placeholder = (
                    await element.get_attribute(
                        "placeholder"
                    )
                )

                name = (
                    await element.get_attribute(
                        "name"
                    )
                )

                inputs.append(
                    {
                        "index": index,
                        "tag": tag,
                        "type": input_type,
                        "name": name,
                        "label": label,
                        "placeholder": placeholder,
                        "disabled": await element.is_disabled(),
                    }
                )

            except Exception:
                continue

        return inputs

    # ==================================================
    # BUTTONS
    # ==================================================

    async def _get_buttons(
        self,
    ) -> list[dict[str, Any]]:

        buttons = []

        locator = self.page.locator(
            "button, input[type='button'], "
            "input[type='submit'], "
            "[role='button']"
        )

        count = await locator.count()

        for index in range(count):

            element = locator.nth(index)

            try:

                if not await element.is_visible():
                    continue

                text = ""

                try:
                    text = (
                        await element.inner_text()
                    ).strip()
                except Exception:
                    pass

                aria_label = (
                    await element.get_attribute(
                        "aria-label"
                    )
                )

                value = (
                    await element.get_attribute(
                        "value"
                    )
                )

                buttons.append(
                    {
                        "index": index,
                        "text": text,
                        "aria_label": aria_label,
                        "value": value,
                        "disabled": await element.is_disabled(),
                    }
                )

            except Exception:
                continue

        return buttons

    # ==================================================
    # LINKS
    # ==================================================

    async def _get_links(
        self,
    ) -> list[dict[str, Any]]:

        links = []

        locator = self.page.locator(
            "a, [role='link']"
        )

        count = await locator.count()

        for index in range(count):

            element = locator.nth(index)

            try:

                if not await element.is_visible():
                    continue

                text = ""

                try:
                    text = (
                        await element.inner_text()
                    ).strip()
                except Exception:
                    pass

                href = (
                    await element.get_attribute(
                        "href"
                    )
                )

                aria_label = (
                    await element.get_attribute(
                        "aria-label"
                    )
                )

                links.append(
                    {
                        "index": index,
                        "text": text,
                        "href": href,
                        "aria_label": aria_label,
                    }
                )

            except Exception:
                continue

        return links

    # ==================================================
    # LABEL
    # ==================================================

    async def _get_label(
        self,
        element,
    ) -> str | None:

        element_id = await element.get_attribute(
            "id"
        )

        if element_id:

            label = self.page.locator(
                f"label[for='{element_id}']"
            )

            if await label.count() > 0:

                try:
                    return (
                        await label.inner_text()
                    ).strip()
                except Exception:
                    pass

        aria_label = await element.get_attribute(
            "aria-label"
        )

        if aria_label:
            return aria_label

        return None

    # ==================================================
    # SCREENSHOT
    # ==================================================

    async def _capture_screenshot(
        self,
        observation_id: str,
        step: int,
    ) -> str:

        filename = (
            f"step_{step}_{observation_id}.png"
        )

        path = (
            self.evidence_dir /
            filename
        )

        await self.page.screenshot(
            path=str(path),
            full_page=True,
        )

        return str(path)

    # ==================================================
    # VALUE REDACTION
    # ==================================================

    @staticmethod
    def _safe_value(
        value: Any,
    ) -> Any:

        if value is None:
            return None

        return str(value)