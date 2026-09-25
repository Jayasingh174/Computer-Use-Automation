from typing import Optional

from playwright.async_api import (
    async_playwright,
    Browser,
    BrowserContext,
    Page,
    Playwright,
)

from app.safety.allowlist import AllowlistManager


class BrowserManager:
    """
    Manages the Playwright browser lifecycle.

    Responsibilities:
    - Start Playwright
    - Launch Chromium
    - Create browser context
    - Create page
    - Navigate to allowed URLs
    - Close browser resources
    """

    def __init__(self, headless: bool = False):

        self.headless = headless

        # Security
        self.allowlist = AllowlistManager()

        # Playwright resources
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None

    # ==================================================
    # START
    # ==================================================

    async def start(self) -> Page:
        """
        Start Playwright, Chromium, browser context,
        and a new page.
        """

        self.playwright = await async_playwright().start()

        self.browser = await self.playwright.chromium.launch(
            headless=self.headless
        )

        self.context = await self.browser.new_context(
            viewport={
                "width": 1440,
                "height": 900,
            }
        )

        self.page = await self.context.new_page()

        return self.page

    # ==================================================
    # NAVIGATE
    # ==================================================

    async def goto(self, url: str):
        """
        Navigate to a URL after validating it
        against the security allowlist.
        """

        if self.page is None:
            raise RuntimeError(
                "Browser has not been started."
            )

        # Security check
        self.allowlist.validate_url(url)

        await self.page.goto(
            url,
            wait_until="domcontentloaded",
        )

    # ==================================================
    # GET PAGE
    # ==================================================

    def get_page(self) -> Page:
        """
        Return the active Playwright page.
        """

        if self.page is None:
            raise RuntimeError(
                "Browser has not been started."
            )

        return self.page

    # ==================================================
    # CLOSE
    # ==================================================

    async def close(self):
        """
        Close browser resources safely.
        """

        if self.context:
            await self.context.close()

        if self.browser:
            await self.browser.close()

        if self.playwright:
            await self.playwright.stop()

        self.page = None
        self.context = None
        self.browser = None
        self.playwright = None