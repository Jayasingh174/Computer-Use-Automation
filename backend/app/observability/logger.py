import json
from pathlib import Path
from typing import Any

from app.safety.redaction import redact_data


class AutomationLogger:

    def __init__(self, log_directory: str = "evidence"):
        self.log_directory = Path(log_directory)
        self.log_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

    def log(
        self,
        event: str,
        data: dict[str, Any],
    ):

        safe_data = redact_data(data)

        record = {
            "event": event,
            "data": safe_data,
        }

        log_file = self.log_directory / "automation.log"

        with log_file.open(
            "a",
            encoding="utf-8",
        ) as file:

            file.write(
                json.dumps(
                    record,
                    ensure_ascii=False,
                )
                + "\n"
            )