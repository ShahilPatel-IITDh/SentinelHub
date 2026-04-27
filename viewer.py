import time
import requests

BASE_URL = "http://127.0.0.1:8000"

EMPLOYEE_ID = 100
PASSWORD = "123456"


def login():
    url = f"{BASE_URL}/api/auth/login"

    data = {
        "employee_id": EMPLOYEE_ID,
        "password": PASSWORD
    }

    res = requests.post(url, json=data)

    if res.status_code != 200:
        print("❌ Login failed:", res.text)
        return None

    token = res.json()["access_token"]
    return token


def fetch_logs(token):
    url = f"{BASE_URL}/api/node/logs/{EMPLOYEE_ID}"

    headers = {
        "Authorization": f"Bearer {token}"
    }

    res = requests.get(url, headers=headers)

    if res.status_code == 401:
        return "TOKEN_EXPIRED"

    if res.status_code != 200:
        print("Error:", res.text)
        return []

    return res.json()


# 🔥 MAIN LOOP
token = login()

while True:
    print("\n==============================")
    print("🔥 LIVE SYSTEM MONITOR")
    print("==============================")

    logs = fetch_logs(token)

    # 🔁 Auto re-login if token expired
    if logs == "TOKEN_EXPIRED":
        print("🔄 Token expired, logging in again...")
        token = login()
        continue

    if not logs:
        print("No logs found")
    else:
        for log in logs[:10]:
            print(
                f"{log['process_name']} | {log['ip_address']} | {log['timestamp']}"
            )

    time.sleep(5)