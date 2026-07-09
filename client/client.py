import time
import requests
import os
import socket
from dotenv import load_dotenv
from monitor import get_system_stats
import uuid

# Load environment variables
load_dotenv()

BASE_URL = os.getenv("SERVER_URL", "http://127.0.0.1:8000")


# ---------------- LOGIN ---------------- #

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


# ---------------- HEARTBEAT ---------------- #

def send_heartbeat(token, employee_id):
    url = f"{BASE_URL}/api/node/heartbeat"

    headers = {
        "Authorization": f"Bearer {token}"
    }

    # 🔥 Collect system stats
    stats = get_system_stats()

    # Basic machine info
    hostname = stats["hostname"]
    ip_address = socket.gethostbyname(hostname)
    mac_address = hex(uuid.getnode())

    # Dummy process list (you can upgrade later)
    processes = ["python", "chrome", "system"]

    data = {
        "mac_address": mac_address,
        "hostname": hostname,
        "ip_address": ip_address,
        "processes": processes,

        # ✅ PERFORMANCE METRICS
        "cpu_percent": stats["cpu_percent"],
        "memory_percent": stats["memory_percent"],
        "disk_percent": stats["disk_percent"]
    }

    try:
        res = requests.post(url, json=data, headers=headers)
    except Exception as e:
        print("❌ Heartbeat error:", str(e))
        return False

    if res.status_code == 401:
        return "TOKEN_EXPIRED"

    if res.status_code != 200:
        print("⚠️ Heartbeat failed:", res.text)
        return False

    return True


# ---------------- FETCH LOGS ---------------- #

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


# ---------------- MAIN LOOP ---------------- #

def main():
    token, employee_id = login()

    if not token:
        print("❌ Initial login failed. Exiting...")
        return

    while True:
        print("\n==============================")
        print("🔥 LIVE SYSTEM MONITOR")
        print("==============================")

        # 🔁 Send heartbeat first
        hb = send_heartbeat(token, employee_id)

        if hb == "TOKEN_EXPIRED":
            print("🔄 Token expired, logging in again...")
            token, employee_id = login()
            continue

        # 🔁 Fetch logs
        logs = fetch_logs(token, employee_id)

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