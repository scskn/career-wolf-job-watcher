from playwright.sync_api import sync_playwright

EPAM_URL = "https://careers.epam.com/en/jobs/turkiye?search=&sort_by=hot&vacancy_type=remote,hybrid"


def main():
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

        print(f"Total links found: {len(links)}")
        print("=" * 80)

        for item in links[:120]:
            print("TEXT:", item["text"].replace("\\n", " | "))
            print("HREF:", item["href"])
            print("-" * 80)

        browser.close()


if __name__ == "__main__":
    main()