import socket
import time
import random

import requests
import urllib3.util.connection
from bs4 import BeautifulSoup

MERCEDES_URL = "https://careers.mercedesbenzturk.com.tr/search/?createNewAlert=false&q=&locationsearch=&optionsFacetsDD_dept=&optionsFacetsDD_location="

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
    "Connection": "close",
}


def force_ipv4() -> None:
    """
    GitHub/cron cloud network bazı domainlerde IPv6/routing problemine düşebilir.
    Mercedes watcher için requests'i IPv4'e zorluyoruz.
    """
    urllib3.util.connection.allowed_gai_family = lambda: socket.AF_INET


def fetch_mercedes_html() -> str:
    force_ipv4()

    last_error = None

    max_attempts = 4
    retry_delays = [10, 30, 60]  # attempt 1-2, 2-3, 3-4 arası bekleme
    timeout = (20, 45)  # connect timeout, read timeout

    for attempt in range(1, max_attempts + 1):
        try:
            print(f"Mercedes fetch attempt {attempt}/{max_attempts} | timeout={timeout}")

            response = requests.get(
                MERCEDES_URL,
                headers=HEADERS,
                timeout=timeout,
                allow_redirects=True,
            )

            response.raise_for_status()

            html = response.text

            if "/job/" not in html:
                raise RuntimeError("Mercedes page loaded but no job links were found in HTML.")

            return html

        except Exception as error:
            last_error = error
            print(f"Mercedes fetch attempt {attempt} failed: {type(error).__name__}: {error}")

            if attempt < max_attempts:
                base_sleep = retry_delays[attempt - 1]
                jitter = random.randint(0, 5)
                sleep_seconds = base_sleep + jitter

                print(f"Waiting {sleep_seconds} seconds before retry...")
                time.sleep(sleep_seconds)

    raise RuntimeError(f"Mercedes fetch failed after {max_attempts} attempts. Last error: {last_error}")


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