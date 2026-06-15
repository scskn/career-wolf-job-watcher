import requests
from bs4 import BeautifulSoup

MERCEDES_URL = "https://careers.mercedesbenzturk.com.tr/search/?createNewAlert=false&q=&locationsearch=&optionsFacetsDD_dept=&optionsFacetsDD_location="

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9,tr;q=0.8",
}


def get_mercedes_jobs() -> list[dict]:
    response = requests.get(
        MERCEDES_URL,
        headers=HEADERS,
        timeout=40,
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    jobs = []
    seen_ids = set()

    for a in soup.find_all("a", href=True):
        title = a.get_text(strip=True)
        link = a["href"].strip()

        if not title:
            continue

        if "/job/" not in link:
            continue

        if link.startswith("/"):
            link = "https://careers.mercedesbenzturk.com.tr" + link
        elif link.startswith("http") is False:
            link = "https://careers.mercedesbenzturk.com.tr/" + link.lstrip("/")

        if "careers.mercedesbenzturk.com.tr/job/" not in link:
            continue

        job_id = link.rstrip("/").split("/")[-1]

        if not job_id.isdigit():
            continue

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