from pathlib import Path
from datetime import datetime, timezone


class ScreenshotManager:
    """
    Captures screenshots for observation and evidence.
    """

    def __init__(
        self,
        base_directory: str = "evidence",
    ):
        self.base_directory = Path(
            base_directory
        )

        self.base_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

    async def capture(
        self,
        page,
        session_id: str,
        step: int,
        category: str = "discovery",
    ) -> str:

        directory = (
            self.base_directory
            / category
            / session_id
        )

        directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        timestamp = datetime.now(
            timezone.utc
        ).strftime("%Y%m%d_%H%M%S_%f")

        filename = (
            f"step_{step}_{timestamp}.png"
        )

        path = directory / filename

        await page.screenshot(
            path=str(path),
            full_page=True,
        )

        return str(path)