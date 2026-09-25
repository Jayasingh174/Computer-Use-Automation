from pathlib import Path
import json

from app.artifacts.schema import CapabilityArtifact
from app.artifacts.validator import ArtifactValidator


class ArtifactRepository:
    """
    Handles persistence of CapabilityArtifact objects.

    Responsibilities:
    - Save validated artifacts
    - Load artifacts from disk
    - Validate artifacts after loading
    """

    def __init__(
        self,
        directory: str = "artifacts/examples",
    ):
        self.directory = Path(directory)

        self.directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.validator = ArtifactValidator()

    # =========================================================
    # SAVE ARTIFACT
    # =========================================================

    def save(
        self,
        artifact: CapabilityArtifact,
    ) -> Path:

        # -----------------------------------------------------
        # 1. Validate before saving
        # -----------------------------------------------------

        self.validator.validate(
            artifact
        )

        # -----------------------------------------------------
        # 2. Create file path
        # -----------------------------------------------------

        file_path = (
            self.directory
            / f"{artifact.artifact_id}.json"
        )

        # -----------------------------------------------------
        # 3. Convert Pydantic model → dictionary
        # -----------------------------------------------------

        data = artifact.model_dump(
            mode="json"
        )

        # -----------------------------------------------------
        # 4. Save JSON
        # -----------------------------------------------------

        with file_path.open(
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                data,
                file,
                indent=2,
                ensure_ascii=False,
            )

        return file_path

    # =========================================================
    # LOAD ARTIFACT
    # =========================================================

    def load(
        self,
        artifact_id: str,
    ) -> CapabilityArtifact:

        # -----------------------------------------------------
        # 1. Locate artifact
        # -----------------------------------------------------

        file_path = (
            self.directory
            / f"{artifact_id}.json"
        )

        # -----------------------------------------------------
        # 2. Check existence
        # -----------------------------------------------------

        if not file_path.exists():

            raise FileNotFoundError(
                f"Artifact not found: {artifact_id}"
            )

        # -----------------------------------------------------
        # 3. Read JSON
        # -----------------------------------------------------

        with file_path.open(
            "r",
            encoding="utf-8",
        ) as file:

            data = json.load(file)

        # -----------------------------------------------------
        # 4. Convert JSON → Pydantic model
        # -----------------------------------------------------

        artifact = (
            CapabilityArtifact.model_validate(
                data
            )
        )

        # -----------------------------------------------------
        # 5. Validate business rules
        # -----------------------------------------------------

        self.validator.validate(
            artifact
        )

        return artifact

    # =========================================================
    # DELETE ARTIFACT
    # =========================================================

    def delete(
        self,
        artifact_id: str,
    ) -> bool:

        file_path = (
            self.directory
            / f"{artifact_id}.json"
        )

        if not file_path.exists():
            return False

        file_path.unlink()

        return True

    # =========================================================
    # EXISTS
    # =========================================================

    def exists(
        self,
        artifact_id: str,
    ) -> bool:

        file_path = (
            self.directory
            / f"{artifact_id}.json"
        )

        return file_path.exists()

    # =========================================================
    # LIST ARTIFACTS
    # =========================================================

    def list_artifacts(self) -> list[str]:

        return [
            file.stem
            for file in self.directory.glob(
                "*.json"
            )
        ]