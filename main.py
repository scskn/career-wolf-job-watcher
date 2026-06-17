from notifier import send_telegram_message
from storage import load_seen_jobs, save_seen_jobs
from bosch_watcher import get_bosch_jobs
from mercedes_watcher import get_mercedes_jobs
from siemens_watcher import get_siemens_jobs
from epam_watcher import get_epam_jobs
from health import maybe_send_health_check

WATCHERS = [
    {
        "company": "Bosch",
        "init_key": "SYSTEM::BOSCH_INITIALIZED_V2",
        "getter": get_bosch_jobs,
    },
    {
        "company": "Siemens",
        "init_key": "SYSTEM::SIEMENS_INITIALIZED_ALL_PAGES_V1",
        "getter": get_siemens_jobs,
    },
    {
        "company": "EPAM",
        "init_key": "SYSTEM::EPAM_INITIALIZED_ALL_PAGES_V1",
        "getter": get_epam_jobs,
    },
    {
        "company": "Mercedes-Benz Türk",
        "init_key": "SYSTEM::MERCEDES_INITIALIZED_V1",
        "getter": get_mercedes_jobs,
    },
]


def format_job_message(job: dict) -> str:
    return f"""🚨 NEW JOB ALERT

Company: {job["company"]}
Title: {job["title"]}
Job ID: {job["id"]}
Location: {job["location"]}

Link:
{job["link"]}
"""


def make_job_key(job: dict) -> str:
    return f'{job["company"]}::{job["id"]}::{job["title"]}'


def initialize_company(seen_jobs: set[str], watcher: dict, current_jobs: list[dict]) -> None:
    for job in current_jobs:
        seen_jobs.add(make_job_key(job))

    seen_jobs.add(watcher["init_key"])

    top_titles = "\n".join([f"- {job['title']}" for job in current_jobs[:5]])

    send_telegram_message(
        f"""✅ {watcher["company"]} watcher initialized

Current jobs found: {len(current_jobs)}

Top jobs:
{top_titles}

From now on, only NEW {watcher["company"]} jobs will trigger alerts."""
    )

    print(f'{watcher["company"]} baseline completed. Current jobs saved: {len(current_jobs)}')


def check_company(seen_jobs: set[str], watcher: dict) -> None:
    company = watcher["company"]

    try:
        current_jobs = watcher["getter"]()
    except Exception as error:
        send_telegram_message(
            f"""⚠️ {company} watcher error

{type(error).__name__}: {error}

Other company watchers will continue."""
        )
        print(f"{company} failed: {type(error).__name__}: {error}")
        return

    if watcher["init_key"] not in seen_jobs:
        initialize_company(seen_jobs, watcher, current_jobs)
        return

    new_jobs = []

    for job in current_jobs:
        job_key = make_job_key(job)

        if job_key not in seen_jobs:
            new_jobs.append(job)
            seen_jobs.add(job_key)

    for job in new_jobs:
        send_telegram_message(format_job_message(job))

    print(f"{company} checked. Current jobs: {len(current_jobs)} | New jobs found: {len(new_jobs)}")


def run_once():
    seen_jobs = load_seen_jobs()

    for watcher in WATCHERS:
        check_company(seen_jobs, watcher)
        save_seen_jobs(seen_jobs)

    maybe_send_health_check()

if __name__ == "__main__":
    try:
        run_once()
    except Exception as error:
        send_telegram_message(f"⚠️ Watcher error\n\n{type(error).__name__}: {error}")
        raise