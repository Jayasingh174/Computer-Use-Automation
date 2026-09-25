from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.artifacts.repository import ArtifactRepository
from app.artifacts.validator import ArtifactValidator


router = APIRouter(
    prefix="/api/artifacts",
    tags=["Artifacts"],
)


# ============================================================
# REQUEST MODEL
# ============================================================

class ArtifactCreateRequest(BaseModel):
    artifact: dict[str, Any]


# ============================================================
# REPOSITORY / VALIDATOR
# ============================================================

repository = ArtifactRepository()
validator = ArtifactValidator()


# ============================================================
# SAVE ARTIFACT
# ============================================================

@router.post("")
async def create_artifact(
    request: ArtifactCreateRequest,
):
    """
    Validate and save a capability artifact.

    Flow:

        React
          ↓
        FastAPI
          ↓
        Pydantic Artifact
          ↓
        Validator
          ↓
        Repository
          ↓
        JSON file
    """

    try:

        # ----------------------------------------------------
        # Validate artifact
        # ----------------------------------------------------

        artifact = validator.validate_data(
            request.artifact
        )

        # ----------------------------------------------------
        # Save artifact
        # ----------------------------------------------------

        file_path = repository.save(
            artifact
        )

        return {
            "success": True,
            "artifact_id": artifact.artifact_id,
            "status": artifact.status.value,
            "file": str(file_path),
        }

    except Exception as exc:

        raise HTTPException(
            status_code=400,
            detail={
                "error": "ARTIFACT_SAVE_FAILED",
                "message": str(exc),
            },
        )


# ============================================================
# GET ARTIFACT
# ============================================================

@router.get("/{artifact_id}")
async def get_artifact(
    artifact_id: str,
):
    """
    Load one artifact by ID.
    """

    try:

        artifact = repository.load(
            artifact_id
        )

        return {
            "success": True,
            "artifact": artifact.model_dump(),
        }

    except FileNotFoundError:

        raise HTTPException(
            status_code=404,
            detail={
                "error": "ARTIFACT_NOT_FOUND",
                "artifact_id": artifact_id,
            },
        )

    except Exception as exc:

        raise HTTPException(
            status_code=400,
            detail={
                "error": "ARTIFACT_LOAD_FAILED",
                "message": str(exc),
            },
        )


# ============================================================
# VALIDATE ARTIFACT
# ============================================================

@router.post("/{artifact_id}/validate")
async def validate_artifact(
    artifact_id: str,
):
    """
    Validate an existing saved artifact.
    """

    try:

        artifact = repository.load(
            artifact_id
        )

        validator.validate(
            artifact
        )

        return {
            "success": True,
            "artifact_id": artifact_id,
            "valid": True,
            "message": "Artifact is valid.",
        }

    except FileNotFoundError:

        raise HTTPException(
            status_code=404,
            detail={
                "error": "ARTIFACT_NOT_FOUND",
                "artifact_id": artifact_id,
            },
        )

    except Exception as exc:

        return {
            "success": False,
            "artifact_id": artifact_id,
            "valid": False,
            "error": str(exc),
        }


# ============================================================
# LIST ARTIFACTS
# ============================================================

@router.get("")
async def list_artifacts():
    """
    Return all saved artifacts.
    """

    try:

        artifacts = repository.list()

        return {
            "success": True,
            "count": len(artifacts),
            "artifacts": [
                artifact.model_dump()
                for artifact in artifacts
            ],
        }

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail={
                "error": "ARTIFACT_LIST_FAILED",
                "message": str(exc),
            },
        )