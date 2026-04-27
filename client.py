import requests
import psutil
import socket
import uuid
import time

BASE_URL = "http://127.0.0.1:8000"


# ---------------- SYSTEM INFO ---------------- #

def get_system_info():
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname)

    # Get MAC address
    mac = ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff)
                   for ele in range(0, 8 * 6, 8)][::-1])

    return hostname, ip_address, mac


# ---------------- GET PROCESSES ---------------- #

def get_running_processes():
    processes = []

    for proc in psutil.process_iter(['name']):
        try:
            name = proc.info['name']
            if name:
                processes.append(name)
        except:
            continue

    return list(set(processes))  # remove duplicates


# ---------------- LOGIN ---------------- #

def login():
    print("Logging in...")

    res = requests.post(f"{BASE_URL}/api/auth/login", json={
        "employee_id": 100,   # ⚠️ change if needed
        "password": "123456"
    })

    data = res.json()
    print("LOGIN RESPONSE:", data)

    if "access_token" not in data:
        raise Exception("Login failed")

    return data["access_token"]


# ---------------- HEARTBEAT ---------------- #

def send_heartbeat(token):
    headers = {
        "Authorization": f"Bearer {token}"
    }

    hostname, ip_address, mac = get_system_info()
    processes = get_running_processes()

    payload = {
        "mac_address": mac,
        "hostname": hostname,
        "ip_address": ip_address,
        "processes": processes[:20]   # limit to avoid overload
    }

    res = requests.post(
        f"{BASE_URL}/api/node/heartbeat",
        json=payload,
        headers=headers
    )

    print(f"Heartbeat: {res.status_code} | Processes: {len(processes)}")


# ---------------- MAIN LOOP ---------------- #

def main():
    token = login()

    print("Starting heartbeat...")

    while True:
        try:
            send_heartbeat(token)
            time.sleep(5)  # every 5 seconds
        except Exception as e:
            print("Error:", e)
            time.sleep(5)


if __name__ == "__main__":
    main()