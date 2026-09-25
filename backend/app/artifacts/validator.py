from app.artifacts.schema import (
    CapabilityArtifact,
    ArtifactAction,
    ActionType,
    RiskLevel,
    Locator,
    Checkpoint,
)


class ArtifactValidationError(Exception):
    """
    Raised when a capability artifact fails validation.
    """

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)


class ArtifactValidator:
    """
    Validates CapabilityArtifact objects before they are:

    1. Saved
    2. Approved
    3. Replayed
    """

    # =========================================================
    # PUBLIC VALIDATION
    # =========================================================

    def validate(
        self,
        artifact: CapabilityArtifact,
    ) -> bool:

        errors: list[str] = []

        # -----------------------------------------------------
        # Basic artifact fields
        # -----------------------------------------------------

        if not artifact.artifact_id.strip():
            errors.append(
                "artifact_id cannot be empty."
            )

        if not artifact.name.strip():
            errors.append(
                "name cannot be empty."
            )

        if not artifact.description.strip():
            errors.append(
                "description cannot be empty."
            )

        if not artifact.application.strip():
            errors.append(
                "application cannot be empty."
            )

        if not artifact.target_url.strip():
            errors.append(
                "target_url cannot be empty."
            )

        if not artifact.created_at.strip():
            errors.append(
                "created_at cannot be empty."
            )

        if not artifact.updated_at.strip():
            errors.append(
                "updated_at cannot be empty."
            )

        # -----------------------------------------------------
        # Version
        # -----------------------------------------------------

        if not artifact.version.strip():
            errors.append(
                "version cannot be empty."
            )

        # -----------------------------------------------------
        # Actions
        # -----------------------------------------------------

        if not artifact.actions:
            errors.append(
                "Artifact must contain at least one action."
            )

        else:
            errors.extend(
                self._validate_actions(
                    artifact.actions
                )
            )

        # -----------------------------------------------------
        # Parameters
        # -----------------------------------------------------

        parameter_names = set()

        for parameter in artifact.parameters:

            if not parameter.name.strip():
                errors.append(
                    "Parameter name cannot be empty."
                )

            if parameter.name in parameter_names:
                errors.append(
                    f"Duplicate parameter: "
                    f"{parameter.name}"
                )

            parameter_names.add(
                parameter.name
            )

        # -----------------------------------------------------
        # Outputs
        # -----------------------------------------------------

        output_names = set()

        for output in artifact.outputs:

            if not output.name.strip():
                errors.append(
                    "Output name cannot be empty."
                )

            if output.name in output_names:
                errors.append(
                    f"Duplicate output: "
                    f"{output.name}"
                )

            output_names.add(
                output.name
            )

        # -----------------------------------------------------
        # Checkpoint
        # -----------------------------------------------------

        errors.extend(
            self._validate_checkpoint(
                artifact.checkpoint
            )
        )

        # -----------------------------------------------------
        # Final result
        # -----------------------------------------------------

        if errors:

            raise ArtifactValidationError(
                "\n".join(
                    f"- {error}"
                    for error in errors
                )
            )

        return True

    # =========================================================
    # ACTION VALIDATION
    # =========================================================

    def _validate_actions(
        self,
        actions: list[ArtifactAction],
    ) -> list[str]:

        errors: list[str] = []

        expected_step = 1

        for action in actions:

            # ---------------------------------------------
            # Step number
            # ---------------------------------------------

            if action.step != expected_step:

                errors.append(
                    f"Expected action step "
                    f"{expected_step}, "
                    f"got {action.step}."
                )

            expected_step += 1

            # ---------------------------------------------
            # Timeout
            # ---------------------------------------------

            if action.timeout_ms <= 0:

                errors.append(
                    f"Step {action.step}: "
                    f"timeout_ms must be greater than 0."
                )

            # ---------------------------------------------
            # Action-specific validation
            # ---------------------------------------------

            if action.action_type in {
                ActionType.CLICK,
                ActionType.TYPE,
                ActionType.SELECT,
                ActionType.PRESS,
                ActionType.EXTRACT,
            }:

                if action.target is None:

                    errors.append(
                        f"Step {action.step}: "
                        f"{action.action_type.value} "
                        f"requires a target locator."
                    )

            # ---------------------------------------------
            # Navigate
            # ---------------------------------------------

            if action.action_type == ActionType.NAVIGATE:

                if action.value is None:

                    errors.append(
                        f"Step {action.step}: "
                        f"navigate requires a URL."
                    )

            # ---------------------------------------------
            # Type
            # ---------------------------------------------

            if action.action_type == ActionType.TYPE:

                if action.value is None:

                    errors.append(
                        f"Step {action.step}: "
                        f"type requires a value."
                    )

            # ---------------------------------------------
            # Press
            # ---------------------------------------------

            if action.action_type == ActionType.PRESS:

                if action.value is None:

                    errors.append(
                        f"Step {action.step}: "
                        f"press requires a key value."
                    )

            # ---------------------------------------------
            # Wait
            # ---------------------------------------------

            if action.action_type == ActionType.WAIT:

                if action.value is None:

                    errors.append(
                        f"Step {action.step}: "
                        f"wait requires a duration."
                    )

            # ---------------------------------------------
            # Risk
            # ---------------------------------------------

            if (
                action.risk_level
                == RiskLevel.BLOCKED
            ):

                errors.append(
                    f"Step {action.step}: "
                    f"blocked actions cannot be "
                    f"executed."
                )

            # ---------------------------------------------
            # Locator validation
            # ---------------------------------------------

            if action.target:

                errors.extend(
                    self._validate_locator(
                        action.target,
                        f"Step {action.step}"
                    )
                )

        return errors

    # =========================================================
    # LOCATOR VALIDATION
    # =========================================================

    def _validate_locator(
        self,
        locator: Locator,
        context: str,
    ) -> list[str]:

        errors: list[str] = []

        if not locator.value.strip():

            errors.append(
                f"{context}: locator value "
                f"cannot be empty."
            )

        # ---------------------------------------------
        # Validate fallback recursively
        # ---------------------------------------------

        if locator.fallback:

            errors.extend(
                self._validate_locator(
                    locator.fallback,
                    f"{context} fallback"
                )
            )

        return errors

    # =========================================================
    # CHECKPOINT VALIDATION
    # =========================================================

    def _validate_checkpoint(
        self,
        checkpoint: Checkpoint,
    ) -> list[str]:

        errors: list[str] = []

        if not checkpoint.type.strip():

            errors.append(
                "Checkpoint type cannot be empty."
            )

        if not checkpoint.description.strip():

            errors.append(
                "Checkpoint description "
                "cannot be empty."
            )

        # ---------------------------------------------
        # Locator-based checkpoint
        # ---------------------------------------------

        if checkpoint.locator:

            errors.extend(
                self._validate_locator(
                    checkpoint.locator,
                    "Checkpoint"
                )
            )

        # ---------------------------------------------
        # At least one verification mechanism
        # ---------------------------------------------

        if (
            checkpoint.locator is None
            and checkpoint.expected_value is None
        ):

            errors.append(
                "Checkpoint must contain either "
                "a locator or expected_value."
            )

        return errors