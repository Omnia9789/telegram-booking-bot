import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
DB_PATH = os.getenv("DB_PATH", "bookings.db")

# Business hours / available slots (24h format, simple demo config)
AVAILABLE_SLOTS = ["10:00", "11:00", "12:00", "14:00", "15:00", "16:00", "17:00"]

SERVICES = {
    "haircut": "Haircut — 30 min",
    "massage": "Massage — 60 min",
    "consult": "Consultation — 15 min",
}
