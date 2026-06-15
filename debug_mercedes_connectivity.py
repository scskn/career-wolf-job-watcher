import requests

URLS = [
    "https://careers.mercedesbenzturk.com.tr/",
    "https://careers.mercedesbenzturk.com.tr/search/?createNewAlert=false&q=&locationsearch=&optionsFacetsDD_dept=&optionsFacetsDD_location=",
    "https://career5.successfactors.eu/",
    "https://career5.successfactors.eu/career?company=mercedesbe",
    "https://career5.successfactors.eu/career?career_company=mercedesbe&company=mercedesbe&lang=en_US",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


for url in URLS:
    print("=" * 100)
    print("URL:", url)

    try:
        response = requests.get(url, headers=HEADERS, timeout=30, allow_redirects=True)
        print("STATUS:", response.status_code)
        print("FINAL URL:", response.url)
        print("TEXT START:", response.text[:300].replace("\n", " "))
    except Exception as error:
        print("ERROR:", type(error).__name__, error)