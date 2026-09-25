from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.artifacts.repository import ArtifactRepository
from app.artifacts.validator import (
    ArtifactValidator,
    ArtifactValidationError,
)
from app.artifacts.schema import ArtifactStatus
from app.replay.engine import ReplayEngine


router = APIRouter(
    prefix="/api/replay",
    tags=["Replay"],
)


# ============================================================
# REQUEST MODEL
# ============================================================

class ReplayRequest(BaseModel):
    artifact_id: str = Field(
        ...,
        description="ID of the saved automation artifact",
    )

    inputs: dict[str, Any] = Field(
        default_factory=dict,
        description="Input parameters required by the artifact",
    )

    headless: bool = Field(
        default=False,
        description="Run browser in headless mode",
    )


# ============================================================
# DEPENDENCIES
# ============================================================

repository = ArtifactRepository()

validator = ArtifactValidator()


# ============================================================
# REPLAY ENDPOINT
# ============================================================

@router.post("/run")
async def replay_artifact(
    request: ReplayRequest,
):
    """
    Deterministically replay a saved capability artifact.

    IMPORTANT:

    - No LLM is used.
    - Artifact controls the actions.
    - Inputs come from the caller.
    - Artifact is validated before execution.
    """

    # ========================================================
    # 1. LOAD ARTIFACT
    # ========================================================

    try:

        artifact = repository.load(
            request.artifact_id
        )

    except FileNotFoundError as exc:

        raise HTTPException(
            status_code=404,
            detail={
                "error": "ARTIFACT_NOT_FOUND",
                "artifact_id": request.artifact_id,
                "message": str(exc),
            },
        )

    except Exception as exc:

        raise HTTPException(
            status_code=400,
            detail={
                "error": "ARTIFACT_LOAD_ERROR",
                "artifact_id": request.artifact_id,
                "message": str(exc),
            },
        )

    # ========================================================
    # 2. VALIDATE ARTIFACT
    # ========================================================

    try:

        validator.validate(
            artifact
        )

    except ArtifactValidationError as exc:

        raise HTTPException(
            status_code=400,
            detail={
                "error": "INVALID_ARTIFACT",
                "artifact_id": request.artifact_id,
                "message": str(exc),
            },
        )

    # ========================================================
    # 3. CHECK ARTIFACT STATUS
    # ========================================================

    if artifact.status not in (
        ArtifactStatus.APPROVED,
        ArtifactStatus.ACTIVE,
    ):

        raise HTTPException(
            status_code=400,
            detail={
                "error": "ARTIFACT_NOT_REPLAYABLE",
                "artifact_id": request.artifact_id,
                "status": artifact.status.value,
                "message": (
                    "Artifact must be approved or active "
                    "before deterministic replay."
                ),
            },
        )

    # ========================================================
    # 4. VALIDATE REQUIRED INPUTS
    # ========================================================

    missing_inputs: list[str] = []

    for parameter in artifact.parameters:

        if (
            parameter.required
            and parameter.name
            not in request.inputs
        ):

            missing_inputs.append(
                parameter.name
            )

    if missing_inputs:

        raise HTTPException(
            status_code=422,
            detail={
                "error": "MISSING_INPUTS",
                "artifact_id": request.artifact_id,
                "required_inputs": missing_inputs,
            },
        )

    # ========================================================
    # 5. CREATE REPLAY ENGINE
    # ========================================================

    try:

        engine = ReplayEngine(
            artifact=artifact,
            headless=request.headless,
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail={
                "error": "REPLAY_ENGINE_INITIALIZATION_FAILED",
                "message": str(exc),
            },
        )

    # ========================================================
    # 6. EXECUTE DETERMINISTIC REPLAY
    # ========================================================

    try:

        result = await engine.replay(
            inputs=request.inputs,
        )

        return {
            "success": result.get(
                "success",
                False,
            ),
            "artifact_id": artifact.artifact_id,
            "artifact_version": artifact.version,
            "mode": "deterministic_replay",
            "llm_used": False,
            "result": result,
        }

    # ========================================================
    # 7. REPLAY FAILURE
    # ========================================================

    except Exception as exc:

        return {
            "success": False,
            "artifact_id": artifact.artifact_id,
            "artifact_version": artifact.version,
            "mode": "deterministic_replay",
            "llm_used": False,
            "result": {
                "status": "failure",
                "error": {
                    "type": type(exc).__name__,
                    "message": str(exc),
                },
            },
        }
     finally:
        await engine.close()
