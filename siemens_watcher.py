import re
from playwright.sync_api import sync_playwright

SIEMENS_URL = "https://jobs.siemens.com/en_US/externaljobs/SearchJobs/?42386=%5B811999%5D&42386_format=17546&listFilterMode=1&folderSort=postedDate&folderSortDirection=ASC&folderRecordsPerPage=6&"


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


def find_enabled_next_link(page):
    next_links = page.locator("a").filter(has_text=re.compile(r"^\s*Next\s*.*$", re.IGNORECASE))
    count = next_links.count()

    for index in range(count):
        link = next_links.nth(index)

        try:
            if not link.is_visible(timeout=2000):
                continue

            if not link.is_enabled(timeout=2000):
                continue

            return link

        except Exception:
            continue

    return None


def click_next_page(page) -> bool:
    next_link = find_enabled_next_link(page)

    if next_link is None:
        print("Siemens next link is not available or disabled. Stopping pagination.")
        return False

    before_text = page.locator("body").inner_text(timeout=15000)

    try:
        next_link.click(timeout=10000)

        try:
            page.wait_for_function(
                "(oldText) => document.body.innerText !== oldText",
                arg=before_text,
                timeout=15000,
            )
        except Exception:
            page.wait_for_timeout(5000)

        after_text = page.locator("body").inner_text(timeout=15000)

        if after_text == before_text:
            print("Siemens page did not change after clicking Next. Stopping pagination.")
            return False

        return True

    except Exception as error:
        print(f"Siemens next click failed: {type(error).__name__}: {error}")
        return False


def get_siemens_jobs() -> list[dict]:
    all_jobs = []
    seen_ids = set()
    seen_page_signatures = set()

    max_pages = 50

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(SIEMENS_URL, wait_until="domcontentloaded", timeout=60000)

        page.wait_for_timeout(5000)

        page_number = 1

        while page_number <= max_pages:
            jobs = extract_jobs_from_current_page(page)

            if page_number == 1 and not jobs:
                raise RuntimeError("Siemens first page loaded but no jobs were found.")

            page_signature = "|".join(job["id"] for job in jobs)

            if not page_signature:
                print("Siemens page has no job signature. Stopping pagination.")
                break

            if page_signature in seen_page_signatures:
                print("Siemens page signature repeated. Stopping pagination.")
                break

            seen_page_signatures.add(page_signature)

            print(f"Siemens page {page_number}: {len(jobs)} jobs")

            for job in jobs:
                if job["id"] not in seen_ids:
                    seen_ids.add(job["id"])
                    all_jobs.append(job)

            if not click_next_page(page):
                break

            page.wait_for_timeout(2000)
            page_number += 1

        browser.close()

    return all_jobs