from urllib.parse import urlparse

from app.config.settings import settings


class AllowlistManager:
    """
    Controls which URLs/domains the automation system
    is allowed to access.
    """

    def __init__(self):
        self.allowed_domains = {
            settings.demo_app_domain
        }

        self.allowed_routes = [
            "/",
            "/login",
            "/member-search",
            "/member-details",
            "/account-details",
            "/confirmation",
        ]

    def is_allowed_url(self, url: str) -> bool:
        """
        Check whether a URL belongs to the configured
        allowed domain and route.
        """

        parsed = urlparse(url)

        domain = parsed.hostname
        path = parsed.path or "/"

        if domain not in self.allowed_domains:
            return False

        return any(
            path == route or path.startswith(route + "/")
            for route in self.allowed_routes
        )

    def validate_url(self, url: str) -> None:
        """
        Raise an exception when URL is outside the allowlist.
        """

        if not self.is_allowed_url(url):
            raise PermissionError(
                f"URL is outside safety allowlist: {url}"
            )