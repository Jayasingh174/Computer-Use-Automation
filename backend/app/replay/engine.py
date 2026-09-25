from typing import Any

from app.artifacts.schema import CapabilityArtifact
from app.automation.session import AutomationSession
from app.replay.executor import ReplayExecutor
from app.replay.checkpoints import CheckpointVerifier
from app.replay.error_handler import ReplayErrorHandler


class ReplayEngine:
    def __init__(self, artifact: CapabilityArtifact, headless: bool = False):
        self.artifact = artifact
        self.session = AutomationSession(
            target_url=artifact.target_url,
            headless=headless,
        )
        self.error_handler = ReplayErrorHandler()
        self.executor: ReplayExecutor | None = None
        self.checkpoints: CheckpointVerifier | None = None

    async def replay(self, inputs: dict[str, Any]) -> dict[str, Any]:
        page = await self.session.start()
        self.executor = ReplayExecutor(session=self.session)
        self.checkpoints = CheckpointVerifier(page=page)

        results = []

        for action in self.artifact.actions:
            self.session.current_step = action.step
            try:
                result = await self.executor.execute_step(step=action, parameters=inputs)
                results.append(result)
            except Exception as exc:
                replay_error = self.error_handler.classify(error=exc, step=action.step)
                return {
                    "success": False,
                    "status": replay_error.category.value,
                    "artifact_id": self.artifact.artifact_id,
                    "failed_step": action.step,
                    "results": results,
                    "error": replay_error.to_dict(),
                }

        final_checkpoint = await self.checkpoints.verify({
            "type": self.artifact.checkpoint.type,
            "value": self.artifact.checkpoint.expected_value,
            "selector": (
                self.artifact.checkpoint.locator.value
                if self.artifact.checkpoint.locator else None
            ),
        })

        if not final_checkpoint["success"]:
            return {
                "success": False,
                "status": "checkpoint_failed",
                "artifact_id": self.artifact.artifact_id,
                "results": results,
                "checkpoint": final_checkpoint,
            }

        outputs = await self.extract_outputs()

        return {
            "success": True,
            "status": "completed",
            "artifact_id": self.artifact.artifact_id,
            "results": results,
            "outputs": outputs,
            "checkpoint": final_checkpoint,
        }

    async def extract_outputs(self) -> dict[str, Any]:
        outputs: dict[str, Any] = {}
        page = self.session.get_page()

        for output in self.artifact.outputs:
            locator = page.locator(output.source.value)
            if await locator.count() == 0:
                continue
            outputs[output.name] = await locator.first.inner_text()

        return outputs

    async def close(self):
        await self.session.close()
