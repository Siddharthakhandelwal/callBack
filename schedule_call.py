import os
import requests
from datetime import datetime, timezone
from supabase import create_client, Client
from dotenv import load_dotenv
import time
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
API_BASE_URL = "https://pythonscripts-sie1.onrender.com"  # e.g., "https://yourdomain.com"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def send_to_api(row):
    endpoint_map = {
        "real estate": "/state",
        "doctor": "/doctor",
        "general": "/make-call"
    }

    model = row["model"].strip().lower()
    endpoint = endpoint_map.get(model)
    
    if not endpoint:
        print(f"Unknown model type: {model}")
        return

    payload = {
        "name": row["name"],
        "phone": row["phone_number"],
        "mail": row["email"],
        "user_mail": row["user_mail"]
    }

    try:
        response = requests.post(f"{API_BASE_URL}{endpoint}", json=payload)
        print(f"[{datetime.now()}] Sent data to {endpoint}. Status: {response.status_code}")
    except Exception as e:
        print(f"Error sending to API: {e}")

def check_and_trigger_calls():
    try:
        response = supabase.table("user_records").select("*").order("call_back", desc=False).execute()

        data = response.data

        now_utc = datetime.now(timezone.utc)

        for row in data:
            call_back = row.get("call_back")
            if call_back == None or call_back == "None" or call_back == "" or call_back=="NULL":
                # print(row)
                continue

            # Convert to datetime (ensure it's timezone-aware)
            call_back_time = datetime.fromisoformat(call_back)

            # Trigger only if time matches exactly (within 60 seconds)
            if abs((now_utc - call_back_time).total_seconds()) <= 60:
                send_to_api(row)
                time.sleep(60)

    except Exception as e:
        print(f"Error fetching or processing data: {e}")

if __name__ == "__main__":
    check_and_trigger_calls()
