import json
from pathlib import Path

SEEN_FILE = Path("seen_jobs.json")


def load_seen_jobs() -> set[str]:
    if not SEEN_FILE.exists():
        return set()

    with SEEN_FILE.open("r", encoding="utf-8") as file:
        data = json.load(file)

    return set(data)


def save_seen_jobs(seen_jobs: set[str]) -> None:
    with SEEN_FILE.open("w", encoding="utf-8") as file:
        json.dump(sorted(seen_jobs), file, ensure_ascii=False, indent=2)