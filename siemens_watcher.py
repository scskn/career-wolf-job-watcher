import re
from playwright.sync_api import sync_playwright

SIEMENS_URL = "https://jobs.siemens.com/en_US/externaljobs/SearchJobs/?42386=%5B811999%5D&42386_format=17546&listFilterMode=1&folderSort=postedDate&folderSortDirection=ASC&folderRecordsPerPage=6&"


def get_siemens_jobs() -> list[dict]:
    jobs = []
    seen_ids = set()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(SIEMENS_URL, wait_until="networkidle", timeout=60000)

        page.wait_for_timeout(6000)

        body_text = page.locator("body").inner_text()

        browser.close()

    lines = [line.strip() for line in body_text.splitlines() if line.strip()]

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

        # Title normalde Job ID satırının hemen üstündeki satır
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
            "link": SIEMENS_URL,
        })

    return jobs