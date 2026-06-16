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


def find_enabled_next_button(page):
    next_buttons = page.locator(
        "button, a, [role='button'], [role='link']"
    ).filter(
        has_text=re.compile(r"^\s*Next\s*.*$", re.IGNORECASE)
    )

    count = next_buttons.count()

    for index in range(count):
        button = next_buttons.nth(index)

        try:
            if not button.is_visible(timeout=2000):
                continue

            if not button.is_enabled(timeout=2000):
                continue

            return button

        except Exception:
            continue

    return None


def click_next_page(page) -> bool:
    next_button = find_enabled_next_button(page)

    if next_button is None:
        print("EPAM next button is not available or disabled. Stopping pagination.")
        return False

    before_text = page.locator("body").inner_text(timeout=15000)

    next_button.click(timeout=10000)

    try:
        page.wait_for_function(
            "(oldText) => document.body.innerText !== oldText",
            arg=before_text,
            timeout=20000,
        )
    except Exception:
        page.wait_for_timeout(5000)

    after_text = page.locator("body").inner_text(timeout=15000)

    if after_text == before_text:
        print("EPAM page did not change after clicking Next. Stopping pagination.")
        return False

    return True


def get_epam_jobs() -> list[dict]:
    all_jobs = []
    seen_ids = set()
    seen_page_signatures = set()

    max_pages = 50

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(EPAM_URL, wait_until="domcontentloaded", timeout=60000)

        page.wait_for_timeout(8000)

        page_number = 1

        while page_number <= max_pages:
            jobs = extract_epam_jobs_from_current_page(page)

            if page_number == 1 and not jobs:
                raise RuntimeError("EPAM first page loaded but no jobs were found.")

            page_signature = "|".join(job["id"] for job in jobs)

            if not page_signature:
                print("EPAM page has no job signature. Stopping pagination.")
                break

            if page_signature in seen_page_signatures:
                print("EPAM page signature repeated. Stopping pagination.")
                break

            seen_page_signatures.add(page_signature)

            print(f"EPAM page {page_number}: {len(jobs)} jobs")

            for job in jobs:
                if job["id"] not in seen_ids:
                    seen_ids.add(job["id"])
                    all_jobs.append(job)

            if not click_next_page(page):
                break

            page.wait_for_timeout(3000)
            page_number += 1

        browser.close()

    return all_jobs