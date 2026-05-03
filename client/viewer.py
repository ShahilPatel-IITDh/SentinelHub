import time
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Only system config comes from .env
BASE_URL = os.getenv("SERVER_URL", "http://127.0.0.1:8000")


def login():
    employee_id = int(input("Enter Employee ID: "))
    password = input("Enter Password: ")

    url = f"{BASE_URL}/api/auth/login"

    data = {
        "employee_id": employee_id,
        "password": password
    }

    try:
        res = requests.post(url, json=data)
    except Exception as e:
        print("❌ Connection error:", str(e))
        return None, None

    if res.status_code != 200:
        print("❌ Login failed:", res.text)
        return None, None

    token = res.json().get("access_token")
    return token, employee_id


def fetch_logs(token, employee_id):
    url = f"{BASE_URL}/api/node/logs/{employee_id}"

    headers = {
        "Authorization": f"Bearer {token}"
    }

    try:
        res = requests.get(url, headers=headers)
    except Exception as e:
        print("❌ Fetch error:", str(e))
        return []

    if res.status_code == 401:
        return "TOKEN_EXPIRED"

    if res.status_code != 200:
        print("⚠️ Error:", res.text)
        return []

    return res.json()


def main():
    token, employee_id = login()

    if not token:
        print("❌ Initial login failed. Exiting...")
        return

    while True:
        print("\n==============================")
        print("🔥 LIVE SYSTEM MONITOR")
        print("==============================")

        logs = fetch_logs(token, employee_id)

        # 🔁 Auto re-login if token expired
        if logs == "TOKEN_EXPIRED":
            print("🔄 Token expired, logging in again...")
            token, employee_id = login()
            continue

        if not logs:
            print("No logs found")
        else:
            for log in logs[:10]:
                print(
                    f"{log.get('process_name')} | "
                    f"{log.get('ip_address')} | "
                    f"{log.get('timestamp')}"
                )

        time.sleep(5)


if __name__ == "__main__":
    main()