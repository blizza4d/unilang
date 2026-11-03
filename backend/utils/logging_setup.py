import json
import logging
import re
from datetime import datetime, timezone
from middleware.request_context import current_document_id, current_request_id

KEY_PATTERNS = [
    re.compile(r"sk-[A-Za-z0-9_-]{20,}"),
    re.compile(r"AIza[A-Za-z0-9_-]{35}"),
]


class SensitiveDataFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if record.args:
            try:
                record.msg = record.getMessage()
                record.args = ()
            except Exception:
                pass
        msg = str(record.msg)
        for pat in KEY_PATTERNS:
            msg = pat.sub("[REDACTED_API_KEY]", msg)
        record.msg = msg
        return True



class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_obj = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": current_request_id.get(""),
            "document_id": current_document_id.get(""),
        }
        if hasattr(record, "duration_ms"):
            log_obj["duration_ms"] = getattr(record, "duration_ms")
        if hasattr(record, "stage"):
            log_obj["stage"] = getattr(record, "stage")
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_obj)


def configure_structured_logging(level: str = "INFO") -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    handler.addFilter(SensitiveDataFilter())

    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    root_logger.handlers = [handler]


def setup_logging(log_level: str = "INFO", json_format: bool = True) -> None:
    if json_format:
        configure_structured_logging(log_level)
    else:
        logging.basicConfig(level=getattr(logging, log_level.upper(), logging.INFO))

