import asyncio
import json

from app.agent.planner import ComputerUsePlanner


async def main():

    planner = ComputerUsePlanner()

    goal = (
        "Look up member 12345 and read "
        "their current savings balance."
    )

    observation = {
        "observation_id": "obs_test_001",

        "step": 1,

        "page": {
            "url": "http://localhost:5173/member-search",
            "title": "Member Search",
        },

        "visible_text": (
            "Member Search\n"
            "Enter Member ID\n"
            "Search"
        ),

        "interactive_elements": [
            {
                "index": 0,
                "tag": "input",
                "role": "textbox",
                "id": "member-id",
                "name": "memberId",
                "placeholder": "Enter Member ID",
                "text": "",
                "aria_label": "Member ID",
                "disabled": False,
            },
            {
                "index": 1,
                "tag": "button",
                "role": "button",
                "text": "Search",
                "aria_label": "Search",
                "disabled": False,
            },
        ],
    }

    result = planner.plan(
        goal=goal,
        observation=observation,
    )

    print(
        json.dumps(
            result.model_dump(),
            indent=2,
        )
    )


if __name__ == "__main__":
    asyncio.run(main())