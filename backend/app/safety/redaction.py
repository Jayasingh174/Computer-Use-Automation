import re
from typing import Any


SENSITIVE_KEYS = {
    "password",
    "passwd",
    "token",
    "access_token",
    "refresh_token",
    "api_key",
    "secret",
    "authorization",
    "ssn",
}


def redact_text(value: str) -> str:
    """
    Remove common sensitive values from text.
    """

    if not value:
        return value

    # Email
    value = re.sub(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
        "[REDACTED_EMAIL]",
        value,
    )

    # SSN
    value = re.sub(
        r"\b\d{3}-\d{2}-\d{4}\b",
        "[REDACTED_SSN]",
        value,
    )

    # Long token-like strings
    value = re.sub(
        r"\b[A-Za-z0-9_-]{32,}\b",
        "[REDACTED_TOKEN]",
        value,
    )

    return value


def redact_data(data: Any) -> Any:
    """
    Recursively redact sensitive dictionary values.
    """

    if isinstance(data, dict):

        result = {}

        for key, value in data.items():

            if key.lower() in SENSITIVE_KEYS:
                result[key] = "[REDACTED]"
            else:
                result[key] = redact_data(value)

        return result

    if isinstance(data, list):
        return [
            redact_data(item)
            for item in data
        ]

    if isinstance(data, str):
        return redact_text(data)

    return data