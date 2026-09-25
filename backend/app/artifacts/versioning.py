import re

from app.artifacts.schema import CapabilityArtifact


VERSION_PATTERN = re.compile(
    r"^(\d+)\.(\d+)\.(\d+)$"
)


class ArtifactVersionManager:
    """
    Handles semantic versioning of automation artifacts.
    """

    # ========================================================
    # PARSE VERSION
    # ========================================================

    @staticmethod
    def parse(
        version: str,
    ) -> tuple[int, int, int]:

        match = VERSION_PATTERN.match(
            version
        )

        if not match:
            raise ValueError(
                f"Invalid artifact version: {version}"
            )

        return (
            int(match.group(1)),
            int(match.group(2)),
            int(match.group(3)),
        )

    # ========================================================
    # INCREMENT PATCH
    # ========================================================

    @staticmethod
    def patch(
        version: str,
    ) -> str:

        major, minor, patch = (
            ArtifactVersionManager.parse(
                version
            )
        )

        return (
            f"{major}.{minor}.{patch + 1}"
        )

    # ========================================================
    # INCREMENT MINOR
    # ========================================================

    @staticmethod
    def minor(
        version: str,
    ) -> str:

        major, minor, patch = (
            ArtifactVersionManager.parse(
                version
            )
        )

        return (
            f"{major}.{minor + 1}.0"
        )

    # ========================================================
    # INCREMENT MAJOR
    # ========================================================

    @staticmethod
    def major(
        version: str,
    ) -> str:

        major, minor, patch = (
            ArtifactVersionManager.parse(
                version
            )
        )

        return (
            f"{major + 1}.0.0"
        )

    # ========================================================
    # CREATE NEW VERSION
    # ========================================================

    @staticmethod
    def create_version(
        artifact: CapabilityArtifact,
        change_type: str = "patch",
    ) -> CapabilityArtifact:

        current_version = artifact.version

        if change_type == "major":

            new_version = (
                ArtifactVersionManager.major(
                    current_version
                )
            )

        elif change_type == "minor":

            new_version = (
                ArtifactVersionManager.minor(
                    current_version
                )
            )

        elif change_type == "patch":

            new_version = (
                ArtifactVersionManager.patch(
                    current_version
                )
            )

        else:

            raise ValueError(
                "change_type must be "
                "'major', 'minor', or 'patch'"
            )

        artifact.version = new_version

        return artifact

    # ========================================================
    # COMPARE
    # ========================================================

    @staticmethod
    def compare(
        version_a: str,
        version_b: str,
    ) -> int:

        a = ArtifactVersionManager.parse(
            version_a
        )

        b = ArtifactVersionManager.parse(
            version_b
        )

        if a < b:
            return -1

        if a > b:
            return 1

        return 0