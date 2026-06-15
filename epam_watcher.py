from playwright.sync_api import sync_playwright

EPAM_URL = "https://careers.epam.com/en/jobs/turkiye?search=&sort_by=hot&vacancy_type=remote,hybrid"


def get_epam_jobs() -> list[dict]:
    jobs = []
    seen_ids = set()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(EPAM_URL, wait_until="networkidle", timeout=60000)

        page.wait_for_timeout(8000)

        links = page.locator("a").evaluate_all("""
            elements => elements.map(a => ({
                text: (a.innerText || '').trim(),
                href: a.href
            })).filter(x => x.text.length > 3)
        """)

        browser.close()

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