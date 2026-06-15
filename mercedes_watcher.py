import socket
import time
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
    "Connection": "close",
}


def force_ipv4() -> None:
    """
    GitHub runner bazen domain'e bağlanırken IPv6/DNS tarafında takılabiliyor.
    Mercedes request'leri için IPv4'e zorluyoruz.
    """
    original_getaddrinfo = socket.getaddrinfo

    def getaddrinfo_ipv4(host, port, family=0, type=0, proto=0, flags=0):
        return original_getaddrinfo(host, port, socket.AF_INET, type, proto, flags)

    socket.getaddrinfo = getaddrinfo_ipv4


def fetch_mercedes_html() -> str:
    force_ipv4()

    last_error = None

    for attempt in range(1, 6):
        try:
            print(f"Mercedes fetch attempt {attempt}/5")

            response = requests.get(
                MERCEDES_URL,
                headers=HEADERS,
                timeout=(20, 90),  # connect timeout, read timeout
                allow_redirects=True,
            )

            response.raise_for_status()

            if "/job/" not in response.text:
                print("Mercedes page fetched, but no job links found in HTML.")

            return response.text

        except Exception as error:
            last_error = error
            print(f"Mercedes fetch attempt {attempt} failed: {type(error).__name__}: {error}")
            time.sleep(10 * attempt)

    raise last_error


def get_mercedes_jobs() -> list[dict]:
    html = fetch_mercedes_html()
    soup = BeautifulSoup(html, "html.parser")

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
        elif not link.startswith("http"):
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