import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

from notifier import send_telegram_message

HEALTH_FILE = Path("health_state.json")
HEALTH_INTERVAL = timedelta(hours=2)


def maybe_send_health_check() -> None:
    now = datetime.now(timezone.utc)

    if HEALTH_FILE.exists():
        with HEALTH_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)

        last_sent_raw = data.get("last_sent_utc")

        if last_sent_raw:
            last_sent = datetime.fromisoformat(last_sent_raw)

            if now - last_sent < HEALTH_INTERVAL:
                return

    send_telegram_message(
        "✅ Career Wolf Job Watcher health check\n\n"
        "System is running.\n"
        "Bosch + Mercedes-Benz Türk + Siemens + EPAM are being monitored."
    )

    with HEALTH_FILE.open("w", encoding="utf-8") as file:
        json.dump(
            {"last_sent_utc": now.isoformat()},
            file,
            ensure_ascii=False,
            indent=2,
        )