from typing import Any


class LocatorResolver:
    """
    Resolves stable UI controls using a prioritized
    locator strategy.
    """

    PRIORITY = [
        "test_id",
        "role",
        "label",
        "name",
        "text",
        "css",
    ]

    async def resolve(
        self,
        page,
        locator_data: dict[str, Any],
    ):
        """
        Return a Playwright locator using the
        strongest available strategy.
        """

        strategy = locator_data.get("strategy")
        value = locator_data.get("value")

        if not strategy:
            raise ValueError(
                "Locator strategy is missing."
            )

        if not value:
            raise ValueError(
                "Locator value is missing."
            )

        if strategy == "test_id":
            return page.get_by_test_id(value)

        if strategy == "role":

            role = locator_data.get("role")

            return page.get_by_role(
                role,
                name=value,
            )

        if strategy == "label":
            return page.get_by_label(value)

        if strategy == "name":
            return page.locator(
                f'[name="{value}"]'
            )

        if strategy == "text":
            return page.get_by_text(value)

        if strategy == "css":
            return page.locator(value)

        raise ValueError(
            f"Unsupported locator strategy: {strategy}"
        )

    async def find(
        self,
        page,
        locator_data: dict[str, Any],
    ):
        """
        Resolve and verify that the element exists.
        """

        locator = await self.resolve(
            page,
            locator_data,
        )

        count = await locator.count()

        if count == 0:
            raise LookupError(
                f"Element not found: {locator_data}"
            )

        return locator