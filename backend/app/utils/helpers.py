from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import json
import re


def utc_now() -> str:
    """
    Return the current UTC timestamp in ISO format.
    """
    return datetime.now(timezone.utc).isoformat()


def generate_id(
    prefix: str,
    length: int = 12,
) -> str:
    """
    Generate a simple unique identifier.
    """

    from uuid import uuid4

    return f"{prefix}_{uuid4().hex[:length]}"


def ensure_directory(
    directory: str | Path,
) -> Path:
    """
    Create a directory if it does not exist.
    """

    path = Path(directory)

    path.mkdir(
        parents=True,
        exist_ok=True,
    )

    return path


def save_json(
    file_path: str | Path,
    data: Any,
) -> str:
    """
    Save Python data as JSON.
    """

    path = Path(file_path)

    path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with path.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            data,
            file,
            indent=2,
            ensure_ascii=False,
            default=str,
        )

    return str(path)


def load_json(
    file_path: str | Path,
) -> Any:
    """
    Load JSON from disk.
    """

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"File not found: {path}"
        )

    with path.open(
        "r",
        encoding="utf-8",
    ) as file:

        return json.load(file)


def redact_text(
    text: str,
) -> str:
    """
    Basic redaction for common sensitive values.

    This is intentionally conservative.
    Production systems should use a stronger
    data classification/redaction layer.
    """

    if not text:
        return text

    # Email
    text = re.sub(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
        "[REDACTED_EMAIL]",
        text,
    )

    # Authorization headers
    text = re.sub(
        r"(?i)(authorization\s*[:=]\s*)([^\s]+)",
        r"\1[REDACTED]",
        text,
    )

    # API keys / tokens
    text = re.sub(
        r"(?i)(api[_-]?key|token|secret|password)\s*[:=]\s*[^\s,]+",
        r"\1=[REDACTED]",
        text,
    )

    return text


def safe_filename(
    value: str,
) -> str:
    """
    Convert arbitrary text into a filesystem-safe filename.
    """

    value = re.sub(
        r"[^a-zA-Z0-9._-]",
        "_",
        value,
    )

    return value[:150]


def deep_redact(
    value: Any,
) -> Any:
    """
    Recursively redact sensitive dictionary fields.
    """

    sensitive_keys = {
        "password",
        "token",
        "secret",
        "api_key",
        "authorization",
        "access_token",
        "refresh_token",
        "credentials",
    }

    if isinstance(value, dict):

        result = {}

        for key, item in value.items():

            if key.lower() in sensitive_keys:

                result[key] = "[REDACTED]"

            else:

                result[key] = deep_redact(item)

        return result

    if isinstance(value, list):

        return [
            deep_redact(item)
            for item in value
        ]

    if isinstance(value, str):

        return redact_text(value)

    return value