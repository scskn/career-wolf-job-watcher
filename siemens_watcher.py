import re
from urllib.parse import urlencode

from playwright.sync_api import sync_playwright

SIEMENS_BASE_URL = "https://jobs.siemens.com/en_US/externaljobs/SearchJobs/"

SIEMENS_PARAMS = {
    "42386": "[811999]",
    "42386_format": "17546",
    "listFilterMode": "1",
    "folderSort": "postedDate",
    "folderSortDirection": "ASC",
    "folderRecordsPerPage": "6",
}

RECORDS_PER_PAGE = 6


def build_siemens_search_url(offset: int = 0) -> str:
    params = dict(SIEMENS_PARAMS)

    if offset > 0:
        params["folderOffset"] = str(offset)

    return f"{SIEMENS_BASE_URL}?{urlencode(params)}"


def build_siemens_job_link(job_id: str) -> str:
    return f"https://jobs.siemens.com/en_US/externaljobs/JobDetail/{job_id}"


def extract_jobs_from_current_page(page) -> list[dict]:
    body_text = page.locator("body").inner_text(timeout=15000)
    lines = [line.strip() for line in body_text.splitlines() if line.strip()]

    jobs = []
    seen_ids = set()

    for i, line in enumerate(lines):
        if "Job ID:" not in line:
            continue

        job_id_match = re.search(r"Job ID:\s*(\d+)", line)
        if not job_id_match:
            continue

        job_id = job_id_match.group(1)

        if job_id in seen_ids:
            continue

        seen_ids.add(job_id)

        title = "Unknown Title"

        for j in range(i - 1, -1, -1):
            candidate = lines[j].strip()

            banned = [
                "share",
                "learn more",
                "skip to content",
                "open jobs",
                "filters applied",
                "sorted by most recent",
                "search",
            ]

            if candidate.lower() in banned:
                continue

            if candidate:
                title = candidate
                break

        location = "Türkiye"

        if "•" in line:
            location = line.split("•")[0].strip()

        jobs.append({
            "id": job_id,
            "company": "Siemens",
            "title": title,
            "location": location,
            "link": build_siemens_job_link(job_id),
        })

    return jobs


def get_siemens_jobs() -> list[dict]:
    all_jobs = []
    seen_ids = set()
    seen_page_signatures = set()

    max_pages = 50

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        for page_number in range(1, max_pages + 1):
            offset = (page_number - 1) * RECORDS_PER_PAGE
            url = build_siemens_search_url(offset)

            page.goto(url, wait_until="domcontentloaded", timeout=60000)
            page.wait_for_timeout(5000)

            jobs = extract_jobs_from_current_page(page)

            if page_number == 1 and not jobs:
                raise RuntimeError("Siemens first page loaded but no jobs were found.")

            if not jobs:
                print("Siemens page has no jobs. Stopping pagination.")
                break

            page_signature = "|".join(job["id"] for job in jobs)

            if page_signature in seen_page_signatures:
                print("Siemens page signature repeated. Stopping pagination.")
                break

            seen_page_signatures.add(page_signature)

            print(f"Siemens page {page_number}: {len(jobs)} jobs")

            for job in jobs:
                if job["id"] not in seen_ids:
                    seen_ids.add(job["id"])
                    all_jobs.append(job)

            if len(jobs) < RECORDS_PER_PAGE:
                print("Siemens last page reached. Stopping pagination.")
                break

        browser.close()

    return all_jobs