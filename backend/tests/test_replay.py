import asyncio
import json
from pathlib import Path

from app.artifacts.repository import ArtifactRepository
from app.replay.engine import ReplayEngine


# ============================================================
# CONFIGURATION
# ============================================================

ARTIFACT_ID = "your_artifact_id"

TARGET_URL = "http://localhost:5173"


# ============================================================
# TEST REPLAY
# ============================================================

async def main():

    repository = ArtifactRepository()

    print("\n========================================")
    print("REPLAY TEST")
    print("========================================")

    # --------------------------------------------------------
    # 1. Load artifact
    # --------------------------------------------------------

    print("\n[1] Loading artifact...")

    try:

        artifact = repository.get(
            ARTIFACT_ID
        )

    except Exception as exc:

        print("\n❌ Failed to load artifact")

        print(
            f"Error: {type(exc).__name__}: {exc}"
        )

        return

    if artifact is None:

        print(
            f"\n❌ Artifact not found: {ARTIFACT_ID}"
        )

        return

    print("\n✓ Artifact loaded")

    print(
        f"Artifact ID: "
        f"{getattr(artifact, 'artifact_id', ARTIFACT_ID)}"
    )

    print(
        f"Name: "
        f"{getattr(artifact, 'name', 'Unknown')}"
    )

    print(
        f"Status: "
        f"{getattr(artifact, 'status', 'Unknown')}"
    )

    # --------------------------------------------------------
    # 2. Show actions
    # --------------------------------------------------------

    print("\n========================================")
    print("RECORDED ACTIONS")
    print("========================================")

    actions = getattr(
        artifact,
        "actions",
        [],
    )

    for action in actions:

        if hasattr(action, "model_dump"):

            action_data = action.model_dump()

        else:

            action_data = action

        print(
            json.dumps(
                action_data,
                indent=2,
                default=str,
            )
        )

    # --------------------------------------------------------
    # 3. Create Replay Engine
    # --------------------------------------------------------

    print("\n========================================")
    print("STARTING REPLAY ENGINE")
    print("========================================")

    engine = ReplayEngine(
        artifact=artifact,
        headless=False,
    )

    try:

        # ----------------------------------------------------
        # 4. Run deterministic replay
        # ----------------------------------------------------

        print("\n[2] Executing artifact...")

        print(
            "\nIMPORTANT:"
        )

        print(
            "Replay does NOT use the LLM."
        )

        result = await engine.replay(
            inputs={}
        )

        # ----------------------------------------------------
        # 5. Print result
        # ----------------------------------------------------

        print("\n========================================")
        print("REPLAY RESULT")
        print("========================================")

        print(
            json.dumps(
                result,
                indent=2,
                default=str,
            )
        )

        # ----------------------------------------------------
        # 6. Keep browser open
        # ----------------------------------------------------

        print("\n========================================")
        print("REPLAY FINISHED")
        print("========================================")

        input(
            "\nPress ENTER to close browser..."
        )

    except Exception as exc:

        print("\n========================================")
        print("❌ REPLAY FAILED")
        print("========================================")

        print(
            f"\nError Type: {type(exc).__name__}"
        )

        print(
            f"Error: {exc}"
        )

        raise

    finally:

        # ----------------------------------------------------
        # 7. Close replay engine
        # ----------------------------------------------------

        if hasattr(engine, "close"):

            await engine.close()

        elif hasattr(engine, "session"):

            await engine.session.close()

        print(
            "\n✓ Browser closed"
        )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":

    asyncio.run(main())