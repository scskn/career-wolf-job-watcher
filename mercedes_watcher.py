from playwright.sync_api import sync_playwright

MERCEDES_URL = "https://careers.mercedesbenzturk.com.tr/search/?createNewAlert=false&q=&locationsearch=&optionsFacetsDD_dept=&optionsFacetsDD_location="


def get_mercedes_jobs() -> list[dict]:
    jobs = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        )

        page = context.new_page()
        page.set_default_timeout(120000)
        page.set_default_navigation_timeout(120000)

        # Sayfayı hafiflet: image/font/media yükleme, HTML yeterli.
        page.route(
            "**/*",
            lambda route: route.abort()
            if route.request.resource_type in ["image", "media", "font"]
            else route.continue_()
        )

        page.goto(MERCEDES_URL, wait_until="commit", timeout=120000)

        # JS biraz yerleşsin
        page.wait_for_timeout(10000)

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