from typing import Any

from app.automation.session import AutomationSession
from app.replay.executor import ReplayExecutor
from app.replay.checkpoints import CheckpointVerifier
from app.replay.error_handler import (
    ReplayErrorHandler,
)


class ReplayEngine:
    """
    Deterministic artifact replay engine.

    Flow:

        Artifact
           ↓
        Parameters
           ↓
        Recorded Steps
           ↓
        ActionExecutor
           ↓
        Checkpoint
           ↓
        Result
    """

    def __init__(
        self,
        session: AutomationSession,
    ):

        self.session = session

        self.page = session.get_page()

        self.executor = ReplayExecutor(
            page=self.page
        )

        self.checkpoints = CheckpointVerifier(
            page=self.page
        )

        self.error_handler = (
            ReplayErrorHandler()
        )

    async def replay(
        self,
        artifact: dict[str, Any],
        parameters: dict[str, Any],
    ) -> dict[str, Any]:

        artifact_id = artifact.get(
            "artifact_id"
        )

        steps = artifact.get(
            "steps",
            []
        )

        results = []

        # ----------------------------------------
        # Execute each recorded step
        # ----------------------------------------

        for index, step in enumerate(
            steps,
            start=1,
        ):

            self.session.current_step = index

            try:

                result = await self.executor.execute_step(
                    step=step,
                    parameters=parameters,
                )

                results.append(result)

                # --------------------------------
                # Verify checkpoint
                # --------------------------------

                checkpoint = step.get(
                    "checkpoint"
                )

                if checkpoint:

                    verification = (
                        await self.checkpoints.verify(
                            checkpoint
                        )
                    )

                    if not verification[
                        "success"
                    ]:

                        return {
                            "success": False,
                            "status": "checkpoint_failed",
                            "artifact_id": artifact_id,
                            "failed_step": index,
                            "results": results,
                            "checkpoint": verification,
                        }

            except Exception as exc:

                replay_error = (
                    self.error_handler.classify(
                        error=exc,
                        step=index,
                    )
                )

                return {
                    "success": False,
                    "status": (
                        replay_error.category.value
                    ),
                    "artifact_id": artifact_id,
                    "failed_step": index,
                    "results": results,
                    "error": replay_error.to_dict(),
                }

        # ----------------------------------------
        # Artifact success condition
        # ----------------------------------------

        success_condition = artifact.get(
            "success_condition"
        )

        final_checkpoint = None

        if success_condition:

            final_checkpoint = (
                await self.checkpoints.verify(
                    success_condition
                )
            )

            if not final_checkpoint[
                "success"
            ]:

                return {
                    "success": False,
                    "status": "success_condition_failed",
                    "artifact_id": artifact_id,
                    "results": results,
                    "checkpoint": final_checkpoint,
                }

        # ----------------------------------------
        # Extract outputs
        # ----------------------------------------

        outputs = await self.extract_outputs(
            artifact=artifact
        )

        return {
            "success": True,
            "status": "completed",
            "artifact_id": artifact_id,
            "results": results,
            "outputs": outputs,
            "checkpoint": final_checkpoint,
        }

    async def extract_outputs(
        self,
        artifact: dict[str, Any],
    ) -> dict[str, Any]:

        outputs = {}

        output_definitions = artifact.get(
            "outputs",
            []
        )

        for output in output_definitions:

            name = output.get(
                "name"
            )

            selector = output.get(
                "selector"
            )

            if not name or not selector:
                continue

            locator = self.page.locator(
                selector
            )

            if await locator.count() == 0:
                continue

            outputs[name] = (
                await locator.first.inner_text()
            )

        return outputs