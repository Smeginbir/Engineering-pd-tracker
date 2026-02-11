import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# -------------------------
# CONFIG
# -------------------------

SHEET_NAME = "Western Canada Engineering PD Tracker"

KEYWORDS = {
    "Technical – Electrical": ["electrical", "power", "controls"],
    "Technical – Mechanical": ["mechanical", "hvac", "piping"],
    "Leadership / Administration": ["management", "leadership", "governance", "compliance"],
    "Project Management": ["project management", "pmp", "risk"]
}

# -------------------------
# GOOGLE SHEETS CONNECTION
# -------------------------

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

creds = ServiceAccountCredentials.from_json_keyfile_name(
    "service_account.json", scope
)

client = gspread.authorize(creds)
sheet = client.open(SHEET_NAME).sheet1

# -------------------------
# SAMPLE EVENTS (BEGINNER VERSION)
# -------------------------

sample_events = [
    {"title": "Electrical Power Systems Webinar – Alberta", "url": "https://example.com", "source": "Sample"},
    {"title": "Mechanical HVAC Design Online Course", "url": "https://example.com", "source": "Sample"},
    {"title": "Engineering Leadership for Managers – Canada", "url": "https://example.com", "source": "Sample"}
]

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

def run():
    today = datetime.date.today().isoformat()

    for event in sample_events:
        category = classify(event["title"])
        if not category:
            continue

        role = role_from_category(category)

        sheet.append_row([
            today,
            event["title"],
            category,
            role,
            "Provider TBD",
            "Canada",
            "Online",
            event["url"],
            event["source"]
        ])

if __name__ == "__main__":
    run()
