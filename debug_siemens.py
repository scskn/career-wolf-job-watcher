from playwright.sync_api import sync_playwright

SIEMENS_URL = "https://jobs.siemens.com/en_US/externaljobs/SearchJobs/?42386=%5B811999%5D&42386_format=17546&listFilterMode=1&folderSort=postedDate&folderSortDirection=ASC&folderRecordsPerPage=6&"


def extract_visible_jobs(page):
    cards = page.locator("body").evaluate("""
        body => {
            const text = body.innerText;
            const blocks = text.split('\\n\\n');

            return blocks
                .map(x => x.trim())
                .filter(x => x.includes('Job ID:'))
                .map(x => x.replace(/\\n/g, ' | '));
        }
    """)

    return cards


def main():
    all_cards = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(SIEMENS_URL, wait_until="networkidle", timeout=60000)

        page.wait_for_timeout(5000)

        page_no = 1

        while True:
            print(f"\nPAGE {page_no}")
            print("=" * 80)

            cards = extract_visible_jobs(page)

            for card in cards:
                print(card)
                print("-" * 80)

            all_cards.extend(cards)

            try:
                next_button = page.get_by_text("Next >>", exact=True)

                if next_button.count() == 0:
                    break

                next_button.first.click(timeout=5000)
                page.wait_for_timeout(5000)
                page_no += 1

            except Exception:
                break

        browser.close()

    print("\nTOTAL RAW CARDS:", len(all_cards))


if __name__ == "__main__":
    main()