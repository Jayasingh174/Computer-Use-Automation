from typing import Generator

from app.agent.agent import GroqAgent
from app.automation.session import AutomationSession


# ============================================================
# AGENT DEPENDENCY
# ============================================================

def get_agent() -> Generator[GroqAgent, None, None]:
    """
    Create a GroqAgent for a request.

    Used by FastAPI routes through Depends().
    """

    agent = GroqAgent()

    try:
        yield agent

    finally:
        # Agent cleanup is async, so the route should
        # explicitly close it when necessary.
        pass


# ============================================================
# SESSION DEPENDENCY
# ============================================================

def get_session() -> Generator[AutomationSession, None, None]:
    """
    Create an automation session for a request.
    """

    session = AutomationSession()

    try:
        yield session

    finally:
        # Browser cleanup is handled explicitly by
        # the route/agent lifecycle.
        pass