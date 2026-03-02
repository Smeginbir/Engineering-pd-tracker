print("Script started")

import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import json
import requests
from bs4 import BeautifulSoup

SHEET_NAME = "Western Canada Engineering PD Tracker"

KEYWORDS = {
    "Technical – Electrical": ["electrical", "power", "controls"],
    "Technical – Mechanical": ["mechanical", "hvac", "piping"],
    "Leadership / Administration": ["management", "leadership", "governance", "compliance"],
    "Project Management": ["project management", "pmp", "risk"]
}

EVENT_SOURCES = [
    {"name": "APEGA", "url": "https://www.apega.ca/events"},
    {"name": "Engineers Canada", "url": "https://engineerscanada.ca/news-and-events"},
    {"name": "EGBC", "url": "https://www.egbc.ca/Events"},
    {"name": "PEO", "url": "https://www.peo.on.ca/events"},
]

# Google Auth
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds_dict = json.loads(os.environ["GOOGLE_CREDS"])
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)
sheet = client.open(SHEET_NAME).sheet1


def classify(text):
    text = text.lower()
    for category, words in KEYWORDS.items():
        for word in words:
            if word in text:
                return category
    return None


def role_from_category(category):
    mapping = {
        "Technical – Electrical": "Electrical Engineer",
        "Technical – Mechanical": "Mechanical Engineer",
        "Leadership / Administration": "Engineering Administrator",
        "Project Management": "Project Manager"
    }
    return mapping.get(category, "Engineering Manager")


def scrape_events(source):
    events = []
    try:
        response = requests.get(source["url"], timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")

        for link in soup.find_all("a"):
            title = link.get_text(strip=True)
            url = link.get("href")

            if title and len(title) > 15:
                if url and not url.startswith("http"):
                    url = source["url"]

                events.append({
                    "title": title,
                    "url": url,
                    "source": source["name"]
                })

    except Exception as e:
        print(f"Error scraping {source['name']}: {e}")

    return events


def run():
    today = datetime.date.today().isoformat()

    for source in EVENT_SOURCES:
        events = scrape_events(source)

        for event in events:
            category = classify(event["title"])
            if not category:
                continue

            role = role_from_category(category)

            sheet.append_row([
                today,
                event["title"],
                category,
                role,
                source["name"],
                "Canada",
                "Online",
                event["url"],
                event["source"]
            ])


if __name__ == "__main__":
    run()

print("Script completed successfully")
