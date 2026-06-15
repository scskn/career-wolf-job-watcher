from playwright.sync_api import sync_playwright

BOSCH_URL = "https://jobs.bosch.com/tr/?pages=1&country=tr&location=%C4%B0stanbul#"

def main():
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

        page.wait_for_timeout(5000)

        links = page.locator("a").evaluate_all("""
            elements => elements.map(a => ({
                text: (a.innerText || '').trim(),
                href: a.href
            })).filter(x => x.text.length > 3)
        """)

        print(f"Total links found: {len(links)}")
        print("=" * 80)

        for item in links[:80]:
            print("TEXT:", item["text"].replace("\\n", " | "))
            print("HREF:", item["href"])
            print("-" * 80)

        browser.close()

if __name__ == "__main__":
    main()