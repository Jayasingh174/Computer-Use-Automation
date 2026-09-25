from enum import Enum
from typing import Optional
from uuid import uuid4

from playwright.async_api import Page

from app.automation.browser import BrowserManager
from app.config.settings import settings
from app.automation.screenshots import ScreenshotManager


class SessionStatus(str, Enum):
    CREATED = "created"
    ACTIVE = "active"
    PAUSED = "paused"
    WAITING_HUMAN = "waiting_human"
    COMPLETED = "completed"
    FAILED = "failed"
    CLOSED = "closed"


class ControlOwner(str, Enum):
    AGENT = "agent"
    HUMAN = "human"


class AutomationSession:
    """
    Represents one persistent computer-use session.

    A session owns:
    - session ID
    - browser
    - Playwright page
    - session status
    - current controller

    The same session can be used by the agent and later
    handed over to a human operator.
    """

    def __init__(
        self,
        target_url: Optional[str] = None,
        headless: bool = False,
    ):
        self.session_id = f"session_{uuid4().hex[:12]}"

        self.target_url = (
            target_url
            or settings.demo_app_url
        )

        self.browser = BrowserManager(
            headless=headless
        )

        self.page: Optional[Page] = None

        self.status = SessionStatus.CREATED

        self.control_owner = ControlOwner.AGENT

        self.current_step = 0

        self.last_error: Optional[str] = None

        self.metadata = {}

        self.screenshot_manager = ScreenshotManager()

    # ==================================================
    # START SESSION
    # ==================================================

    async def start(self) -> Page:
        """
        Start browser and navigate to the target application.
        """

        if self.status != SessionStatus.CREATED:
            raise RuntimeError(
                f"Cannot start session in status: "
                f"{self.status}"
            )

        try:
            self.page = await self.browser.start()

            await self.browser.goto(
                self.target_url
            )

            self.status = SessionStatus.ACTIVE

            self.control_owner = (
                ControlOwner.AGENT
            )

            return self.page

        except Exception as exc:
            self.status = SessionStatus.FAILED

            self.last_error = str(exc)

            raise

    # ==================================================
    # GET PAGE
    # ==================================================

    def get_page(self) -> Page:
        """
        Return the active Playwright page.
        """

        if self.page is None:
            raise RuntimeError(
                "Browser session has not been started."
            )

        return self.page

    # ==================================================
    # STEP MANAGEMENT
    # ==================================================

    def next_step(self) -> int:
        """
        Increment and return the current step number.
        """

        self.current_step += 1

        return self.current_step

    # ==================================================
    # AGENT CONTROL
    # ==================================================

    def acquire_agent_control(self):
        """
        Give control of the live session to the agent.
        """

        if self.status == SessionStatus.CLOSED:
            raise RuntimeError(
                "Cannot acquire control of a closed session."
            )

        if self.status == SessionStatus.COMPLETED:
            raise RuntimeError(
                "Cannot acquire control of a completed session."
            )

        self.control_owner = ControlOwner.AGENT

        self.status = SessionStatus.ACTIVE

    # ==================================================
    # HUMAN HANDOFF
    # ==================================================

    def request_human_control(
        self,
        reason: str,
    ):
        """
        Pause automation and transfer ownership
        to a human operator.
        """

        if self.status != SessionStatus.ACTIVE:
            raise RuntimeError(
                f"Cannot request human control "
                f"from status: {self.status}"
            )

        self.control_owner = ControlOwner.HUMAN

        self.status = SessionStatus.WAITING_HUMAN

        self.last_error = reason

    # ==================================================
    # HUMAN RESUME
    # ==================================================

    def resume_after_human(self):
        """
        Return control from the human to the agent.
        """

        if self.status != SessionStatus.WAITING_HUMAN:
            raise RuntimeError(
                "Session is not waiting for human intervention."
            )

        self.control_owner = ControlOwner.AGENT

        self.status = SessionStatus.ACTIVE

    # ==================================================
    # PAUSE
    # ==================================================

    def pause(self):
        """
        Pause automation without closing the browser.
        """

        if self.status != SessionStatus.ACTIVE:
            raise RuntimeError(
                f"Cannot pause session from status: "
                f"{self.status}"
            )

        self.status = SessionStatus.PAUSED

    # ==================================================
    # COMPLETE
    # ==================================================

    def complete(self):
        """
        Mark the session as successfully completed.
        """

        if self.status == SessionStatus.CLOSED:
            raise RuntimeError(
                "Cannot complete a closed session."
            )

        self.status = SessionStatus.COMPLETED

    # ==================================================
    # FAIL
    # ==================================================

    def fail(self, error: str):
        """
        Mark the session as failed.
        """

        self.status = SessionStatus.FAILED

        self.last_error = error

    # ==================================================
    # STATUS
    # ==================================================

    def get_status(self) -> dict:
        return {
            "session_id": self.session_id,
            "status": self.status.value,
            "control_owner": self.control_owner.value,
            "current_step": self.current_step,
            "target_url": self.target_url,
            "last_error": self.last_error,
        }

    # ==================================================
    # CLOSE
    # ==================================================

    async def close(self):
        """
        Close the browser and end the session.
        """

        await self.browser.close()

        self.page = None

        self.status = SessionStatus.CLOSED

    async def capture_screenshot(self,category: str = "discovery",) -> str:
        page = self.get_page()

        return await self.screenshot_manager.capture(
        page=page,
        session_id=self.session_id,
        step=self.current_step,
        category=category,
    )