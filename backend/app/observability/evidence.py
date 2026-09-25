from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional
import json


class EvidenceManager:
    """
    Manages evidence generated during computer-use runs.

    Evidence can include:
    - screenshots
    - structured observations
    - agent actions
    - replay results
    - failures
    - human handoff information

    Sensitive values should be redacted before being persisted.
    """

    def __init__(
        self,
        base_dir: str = "evidence",
    ):
        self.base_dir = Path(base_dir)

        self.discovery_dir = (
            self.base_dir / "discovery"
        )

        self.replay_dir = (
            self.base_dir / "replay"
        )

        self.failure_dir = (
            self.base_dir / "failure"
        )

        self.handoff_dir = (
            self.base_dir / "handoff"
        )

        for directory in [
            self.discovery_dir,
            self.replay_dir,
            self.failure_dir,
            self.handoff_dir,
        ]:
            directory.mkdir(
                parents=True,
                exist_ok=True,
            )

    # ==================================================
    # TIMESTAMP
    # ==================================================

    @staticmethod
    def timestamp() -> str:
        return datetime.now(
            timezone.utc
        ).isoformat()

    # ==================================================
    # SAVE JSON EVIDENCE
    # ==================================================

    def save_json(
        self,
        directory: Path,
        filename: str,
        data: dict[str, Any],
    ) -> str:

        directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        file_path = directory / filename

        with file_path.open(
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                data,
                file,
                indent=2,
                ensure_ascii=False,
                default=str,
            )

        return str(file_path)

    # ==================================================
    # DISCOVERY EVIDENCE
    # ==================================================

    def save_discovery(
        self,
        session_id: str,
        goal: str,
        steps: list[dict[str, Any]],
        artifact: Optional[dict[str, Any]] = None,
    ) -> str:

        data = {
            "type": "discovery_run",
            "session_id": session_id,
            "goal": goal,
            "created_at": self.timestamp(),
            "steps": steps,
            "artifact": artifact,
        }

        return self.save_json(
            self.discovery_dir,
            f"{session_id}_discovery.json",
            data,
        )

    # ==================================================
    # REPLAY EVIDENCE
    # ==================================================

    def save_replay(
        self,
        session_id: str,
        artifact_id: str,
        inputs: dict[str, Any],
        result: dict[str, Any],
    ) -> str:

        data = {
            "type": "replay_run",
            "session_id": session_id,
            "artifact_id": artifact_id,
            "inputs": inputs,
            "result": result,
            "created_at": self.timestamp(),
        }

        return self.save_json(
            self.replay_dir,
            f"{session_id}_replay.json",
            data,
        )

    # ==================================================
    # FAILURE EVIDENCE
    # ==================================================

    def save_failure(
        self,
        session_id: str,
        step: int,
        error: str,
        expected: Optional[str] = None,
        observed: Optional[str] = None,
        screenshot_path: Optional[str] = None,
    ) -> str:

        data = {
            "type": "failure",
            "session_id": session_id,
            "step": step,
            "error": error,
            "expected": expected,
            "observed": observed,
            "screenshot": screenshot_path,
            "created_at": self.timestamp(),
        }

        return self.save_json(
            self.failure_dir,
            f"{session_id}_step_{step}_failure.json",
            data,
        )

    # ==================================================
    # HANDOFF EVIDENCE
    # ==================================================

    def save_handoff(
        self,
        intervention_id: str,
        session_id: str,
        reason: str,
        current_step: int,
        screenshot_path: Optional[str] = None,
        human_actions: Optional[
            list[dict[str, Any]]
        ] = None,
    ) -> str:

        data = {
            "type": "human_handoff",
            "intervention_id": intervention_id,
            "session_id": session_id,
            "reason": reason,
            "current_step": current_step,
            "screenshot": screenshot_path,
            "human_actions": human_actions or [],
            "created_at": self.timestamp(),
        }

        return self.save_json(
            self.handoff_dir,
            f"{intervention_id}_handoff.json",
            data,
        )

    # ==================================================
    # SAVE SCREENSHOT
    # ==================================================

    async def save_screenshot(
        self,
        page,
        session_id: str,
        category: str = "discovery",
        step: int = 0,
    ) -> str:

        if category == "discovery":
            directory = self.discovery_dir

        elif category == "replay":
            directory = self.replay_dir

        elif category == "failure":
            directory = self.failure_dir

        elif category == "handoff":
            directory = self.handoff_dir

        else:
            raise ValueError(
                f"Unknown evidence category: {category}"
            )

        directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        file_path = (
            directory
            / f"{session_id}_step_{step}.png"
        )

        await page.screenshot(
            path=str(file_path),
            full_page=True,
        )

        return str(file_path)