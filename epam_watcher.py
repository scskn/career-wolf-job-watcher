import re
from playwright.sync_api import sync_playwright

EPAM_URL = "https://careers.epam.com/en/jobs/turkiye?search=&sort_by=hot&vacancy_type=remote,hybrid"


def extract_epam_jobs_from_current_page(page) -> list[dict]:
    links = page.locator("a").evaluate_all("""
        elements => elements.map(a => ({
            text: (a.innerText || '').trim(),
            href: a.href
        })).filter(x => x.text.length > 3)
    """)

    jobs = []
    seen_ids = set()

    for item in links:
        title = item["text"].strip()
        link = item["href"].strip()

        if "careers.epam.com/en/vacancy/" not in link:
            continue

        job_id = link.rstrip("/").split("/")[-1]

        if job_id in seen_ids:
            continue

        seen_ids.add(job_id)

        jobs.append({
            "id": job_id,
            "company": "EPAM",
            "title": title,
            "location": "Türkiye / Remote-Hybrid",
            "link": link,
        })

    return jobs


def click_next_page(page, page_number: int) -> bool:
    before_text = page.locator("body").inner_text(timeout=15000)

    next_page_number = str(page_number + 1)

    candidates = [
        page.locator("a, button, [role='button'], [role='link'], li").filter(
            has_text=re.compile(r"^\s*Next\s*.*$", re.IGNORECASE)
        ),
        page.locator("a, button, [role='button'], [role='link'], li").filter(
            has_text=re.compile(rf"^\s*{next_page_number}\s*$")
        ),
        page.get_by_text("Next", exact=False),
    ]

    for candidate in candidates:
        try:
            if candidate.count() == 0:
                continue

            candidate.last.click(timeout=10000)

            try:
                page.wait_for_function(
                    "(oldText) => document.body.innerText !== oldText",
                    arg=before_text,
                    timeout=20000,
                )
            except Exception:
                page.wait_for_timeout(5000)

            after_text = page.locator("body").inner_text(timeout=15000)

            if after_text != before_text:
                return True

        except Exception as error:
            print(f"EPAM next click candidate failed: {type(error).__name__}: {error}")

    return False


def get_epam_jobs() -> list[dict]:
    all_jobs = []
    seen_ids = set()
    seen_page_signatures = set()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(EPAM_URL, wait_until="domcontentloaded", timeout=60000)

        page.wait_for_timeout(8000)

        for page_number in range(1, 20):
            jobs = extract_epam_jobs_from_current_page(page)

            if page_number == 1 and not jobs:
                raise RuntimeError("EPAM first page loaded but no jobs were found.")

            page_signature = "|".join(job["id"] for job in jobs)

            if not page_signature:
                break

            if page_signature in seen_page_signatures:
                break

            seen_page_signatures.add(page_signature)

            print(f"EPAM page {page_number}: {len(jobs)} jobs")

            for job in jobs:
                if job["id"] not in seen_ids:
                    seen_ids.add(job["id"])
                    all_jobs.append(job)

            if not click_next_page(page, page_number):
                break

            page.wait_for_timeout(3000)

        browser.close()

    return all_jobs