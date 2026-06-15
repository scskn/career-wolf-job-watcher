from playwright.sync_api import sync_playwright

MERCEDES_URL = "https://careers.mercedesbenzturk.com.tr/search/?createNewAlert=false&q=&locationsearch=&optionsFacetsDD_dept=&optionsFacetsDD_location="


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(MERCEDES_URL, wait_until="networkidle", timeout=60000)

        page.wait_for_timeout(5000)

        links = page.locator("a").evaluate_all("""
            elements => elements.map(a => ({
                text: (a.innerText || '').trim(),
                href: a.href
            })).filter(x => x.text.length > 3)
        """)

        print(f"Total links found: {len(links)}")
        print("=" * 80)

        for item in links[:100]:
            print("TEXT:", item["text"].replace("\\n", " | "))
            print("HREF:", item["href"])
            print("-" * 80)

        browser.close()


if __name__ == "__main__":
    main()