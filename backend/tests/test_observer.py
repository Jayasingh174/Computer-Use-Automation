import asyncio

from app.agent.agent import GroqAgent


async def main():

    agent = GroqAgent(
        target_url="http://localhost:5173",
        headless=False,
    )

    try:

        # ==========================================
        # 1. START AGENT
        # ==========================================

        result = await agent.start()

        print("\n==============================")
        print("AGENT STARTED")
        print("==============================")

        # ==========================================
        # 2. SESSION
        # ==========================================

        print("\nSession:")
        print(agent.get_status())

        # ==========================================
        # 3. INITIAL OBSERVATION
        # ==========================================

        print("\nObservation:")

        for key, value in result.items():
            print(f"{key}: {value}")

        # ==========================================
        # 4. TEST USER GOAL
        # ==========================================

        goal = (
            "Look at the current page and determine "
            "what actions are available to the user."
        )

        print("\n==============================")
        print("PLANNING")
        print("==============================")

        # ==========================================
        # 5. ASK PLANNER
        # ==========================================

        plan = agent.plan(
            goal=goal,
            observation=result,
        )

        print("\nPlan:")

        print(
            plan.model_dump()
            if hasattr(plan, "model_dump")
            else plan
        )

        # ==========================================
        # 6. CURRENT SESSION STATUS
        # ==========================================

        print("\n==============================")
        print("SESSION STATUS")
        print("==============================")

        print(agent.get_status())

        # ==========================================
        # 7. KEEP BROWSER OPEN
        # ==========================================

        print("\nBrowser is still open.")

        input(
            "\nPress ENTER to close browser..."
        )

    except Exception as exc:

        print("\n==============================")
        print("AGENT TEST FAILED")
        print("==============================")

        print(
            f"\nError Type: {type(exc).__name__}"
        )

        print(
            f"Error: {exc}"
        )

        print("\nSession:")

        print(
            agent.get_status()
        )

        raise

    finally:

        await agent.close()

        print("\n==============================")
        print("AGENT CLOSED")
        print("==============================")


if __name__ == "__main__":
    asyncio.run(main())