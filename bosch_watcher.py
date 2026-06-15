from playwright.sync_api import sync_playwright

BOSCH_URL = "https://jobs.bosch.com/tr/?pages=1&country=tr&location=%C4%B0stanbul#"


def get_bosch_jobs() -> list[dict]:
    jobs = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(BOSCH_URL, wait_until="networkidle", timeout=60000)

        # Cookie popup varsa kapatmayı dener
        for text in ["Accept", "Accept all", "Tümünü kabul et", "Kabul et"]:
            try:
                page.get_by_text(text, exact=False).click(timeout=3000)
                break
            except Exception:
                pass

        page.wait_for_timeout(3000)

        # "Daha fazla göster" butonu varsa bitene kadar bas
        while True:
            try:
                load_more = page.get_by_text("Daha fazla göster", exact=False)

                if load_more.count() == 0:
                    break

                load_more.first.click(timeout=5000)
                page.wait_for_timeout(3000)

            except Exception:
                break

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

        if "/tr/job/" not in link:
            continue

        job_id = link.split("/tr/job/")[-1].split("-")[0]

        if job_id in seen_ids:
            continue

        seen_ids.add(job_id)

        jobs.append({
            "id": job_id,
            "company": "Bosch",
            "title": title,
            "location": "Istanbul / Türkiye",
            "link": link,
        })

    return jobs