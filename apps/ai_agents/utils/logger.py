import json
import traceback
from pathlib import Path
from datetime import datetime, timezone as tz


JOURNAL_DIR = Path(__file__).resolve().parents[4] / "_dev_journal"
ERROR_LOG = JOURNAL_DIR / "01_error_log.md"


def log_failure(context: str, error: str, metadata: dict = None, exc: Exception = None):
    """
    Auto-appends structured failure entries to the dev journal.
    Call this from any except block. Never raises.

    Usage:
        except Exception as e:
            log_failure("widget_weather", str(e), {"lat": lat}, exc=e)
    """
    try:
        JOURNAL_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now(tz.utc).isoformat()
        tb = ""
        if exc:
            tb = f"\n```\n{traceback.format_exc()}\n```\n"

        entry = (
            f"\n---\n\n"
            f"### ❌ `{context}`\n\n"
            f"**Timestamp:** `{timestamp}`  \n"
            f"**Error:** {error}  \n"
            f"**Metadata:** `{json.dumps(metadata or {}, default=str)}`\n"
            f"{tb}"
        )
        with open(ERROR_LOG, "a", encoding="utf-8") as f:
            f.write(entry)
    except Exception:
        pass  # Logging must NEVER crash the app
