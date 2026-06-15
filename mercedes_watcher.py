from playwright.sync_api import sync_playwright

MERCEDES_URL = "https://careers.mercedesbenzturk.com.tr/search/?createNewAlert=false&q=&locationsearch=&optionsFacetsDD_dept=&optionsFacetsDD_location="


def get_mercedes_jobs() -> list[dict]:
    jobs = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(MERCEDES_URL, wait_until="domcontentloaded", timeout=60000)

        page.wait_for_timeout(5000)

        links = page.locator("a").evaluate_all("""
            elements => elements.map(a => ({
                text: (a.innerText || '').trim(),
                href: a.href
            })).filter(x => x.text.length > 3)
        """)

        browser.close()

    seen_ids = set()

    for item in links:
        title = item["text"].strip()
        link = item["href"].strip()

        if "careers.mercedesbenzturk.com.tr/job/" not in link:
            continue

        # Link sonundaki numeric SuccessFactors job id
        # örn: /1395805933/
        job_id = link.rstrip("/").split("/")[-1]

        if job_id in seen_ids:
            continue

        seen_ids.add(job_id)

        jobs.append({
            "id": job_id,
            "company": "Mercedes-Benz Türk",
            "title": title,
            "location": "Türkiye",
            "link": link,
        })

    return jobs