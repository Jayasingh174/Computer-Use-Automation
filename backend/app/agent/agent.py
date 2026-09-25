from typing import Any, Optional

from app.automation.session import AutomationSession
from app.agent.observer import PageObserver
from app.agent.planner import ComputerUsePlanner
from app.agent.action_executor import ActionExecutor
from app.escalation.handoff import HandoffManager

class GroqAgent:
    """
    Main computer-use discovery agent.

    Responsibilities:
    - Start browser session
    - Observe the live UI
    - Ask the LLM planner for the next action
    - Execute the approved action
    - Repeat observe -> plan -> execute
    - Handle completion and human escalation
    """

    def __init__(
        self,
        target_url: Optional[str] = None,
        headless: bool = False,
    ):
        self.session = AutomationSession(
            target_url=target_url,
            headless=headless,
        )

        self.planner = ComputerUsePlanner()

        self.observer: Optional[PageObserver] = None

        self.action_executor: Optional[ActionExecutor] = None

        self.handoff = HandoffManager(self.session)

    # ==========================================================
    # START
    # ==========================================================

    async def start(self) -> dict[str, Any]:
        """
        Start browser session and create the
        observer and action executor.
        """

        page = await self.session.start()

        # Observe the live page
        self.observer = PageObserver(page)

        # Executor uses the SAME session/browser
        self.action_executor = ActionExecutor(
            self.session
        )

        observation = await self.observer.observe(
            step=self.session.next_step()
        )

        return observation

    # ==========================================================
    # OBSERVE
    # ==========================================================

    async def observe(self) -> dict[str, Any]:
        """
        Capture the current UI state.
        """

        if self.observer is None:
            raise RuntimeError(
                "Agent has not been started."
            )

        return await self.observer.observe(
            step=self.session.next_step()
        )

    # ==========================================================
    # PLAN
    # ==========================================================

    def plan(
        self,
        goal: str,
        observation: dict[str, Any],
    ):
        """
        Ask Groq planner for the next action.
        """

        return self.planner.plan(
            goal=goal,
            observation=observation,
        )

    # ==========================================================
    # EXECUTE
    # ==========================================================

    async def execute(
        self,
        action: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Execute one planned action.
        """

        if self.action_executor is None:
            raise RuntimeError(
                "Agent has not been started."
            )

        return await self.action_executor.execute(
            action
        )

    # ==========================================================
    # MAIN COMPUTER-USE LOOP
    # ==========================================================

    async def run(
        self,
        goal: str,
        max_steps: int = 20,
    ) -> dict[str, Any]:
        """
        Run the complete computer-use discovery loop.

        Flow:

            OBSERVE
                ↓
            PLAN
                ↓
            EXECUTE
                ↓
            OBSERVE
                ↓
              ...

        until:
        - goal is completed
        - human intervention is required
        - maximum steps are reached
        - an unexpected error occurs
        """

        try:

            # --------------------------------------------------
            # Start session
            # --------------------------------------------------

            await self.start()

            # --------------------------------------------------
            # Agent loop
            # --------------------------------------------------

            for _ in range(max_steps):

                # ==============================================
                # 1. OBSERVE
                # ==============================================

                observation = await self.observe()

                # ==============================================
                # 2. PLAN
                # ==============================================

                action = self.plan(
                    goal=goal,
                    observation=observation,
                )

                # Make sure planner returned a dictionary
                if not isinstance(action, dict):

                    self.session.fail(
                        "Planner returned invalid action."
                    )

                    return {
                        "success": False,
                        "status": "failed",
                        "error": (
                            "Planner returned invalid action."
                        ),
                    }

                action_type = action.get("action")

                # ==============================================
                # 3. DONE
                # ==============================================

                if action_type == "done":

                    self.session.complete()

                    return {
                        "success": True,
                        "status": "completed",
                        "goal": goal,
                        "action": action,
                        "session": self.get_status(),
                    }

                # ==============================================
                # 4. HUMAN HANDOFF
                # ==============================================

                if action_type == "human_handoff":

                    reason = action.get(
                        "reason",
                        "Agent requested human intervention.",
                    )

                    self.session.request_human_control(
                        reason=reason
                    )

                    return {
                        "success": False,
                        "status": "waiting_human",
                        "goal": goal,
                        "reason": reason,
                        "action": action,
                        "session": self.get_status(),
                    }

                # ==============================================
                # 5. EXECUTE
                # ==============================================

                result = await self.execute(
                    action
                )

                # ==============================================
                # 6. CHECK EXECUTION RESULT
                # ==============================================

                if not result.get("success", False):

                    self.session.fail(
                        result.get(
                            "error",
                            "Action execution failed.",
                        )
                    )

                    return {
                        "success": False,
                        "status": "failed",
                        "goal": goal,
                        "action": action,
                        "execution": result,
                        "session": self.get_status(),
                    }

                # ==============================================
                # Continue loop
                #
                # Next iteration observes the UI again.
                # ==============================================

            # --------------------------------------------------
            # MAX STEPS
            # --------------------------------------------------

            self.session.fail(
                "Maximum agent steps exceeded."
            )

            return {
                "success": False,
                "status": "max_steps_exceeded",
                "goal": goal,
                "max_steps": max_steps,
                "session": self.get_status(),
            }

        except Exception as exc:

            self.session.fail(
                str(exc)
            )

            return {
                "success": False,
                "status": "failed",
                "goal": goal,
                "error": str(exc),
                "session": self.get_status(),
            }

    # ==========================================================
    # STATUS
    # ==========================================================

    def get_status(self) -> dict:
        """
        Return current session status.
        """

        return self.session.get_status()

    # ==========================================================
    # CLOSE
    # ==========================================================

    async def close(self):
        """
        Close the browser session.
        """

        await self.session.close()

    async def request_human(self,reason: str,goal: Optional[str] = None,observation: Optional[dict] = None):
        return await self.handoff.request_handoff(
        reason=reason,
        current_step=self.session.current_step,
        goal=goal,
        observation=observation,
    )