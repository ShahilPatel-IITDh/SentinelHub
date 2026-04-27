# SentinelHub

**SentinelHub** is a centralized LAN-based system monitoring solution designed for organizational transparency and software compliance. It allows managers to oversee installed applications and active processes on assigned junior workstations in real-time.

## Project Vision
The goal of SentinelHub is to provide Team Leads with a high-level overview of the software environment across their team's hardware. By utilizing an Agent-Server architecture, SentinelHub ensures that every node on the LAN is accounted for, while maintaining strict Role-Based Access Control (RBAC).

## Tech Stack
- **Language:** Python 3.x (Back-end & Front-end)
- **Framework:** Flask / FastAPI
- **Database:** MySQL
- **Core Libraries:** 
    - `psutil`: For process and system utilization tracking.
    - `winreg`: For fetching installed software lists (Windows).
    - `requests`: For data transmission between Agent and Hub.
    - `Flask-SQLAlchemy`: For ORM-based database management.

## System Architecture
### 1. SentinelNode (Client-Side)
A lightweight background agent installed on the Junior's PC. 
- **Inventory Scan:** Lists all installed `.exe` applications.
- **Pulse Check:** Sends a heartbeat to the server every 5 minutes with current running processes.
- **Identity:** Identifies the machine via Windows Username and MAC Address.

### 2. SentinelServer (The Core)
The central brain of the project.
- **Data Intake:** REST API endpoints to receive system logs from nodes.
- **Manager Logic:** Ensures Manager A can only see Junior X, Y, and Z based on MySQL assignments.
- **Database:** Stores historical logs of application usage.

### 3. SentinelDash (Management UI)
A clean, Python-powered dashboard.
- **Login System:** Secure authentication for Seniors.
- **Search & Filter:** Filter by junior name, online status, or specific application.

## Security and Privacy
- **Intranet Deployment**: Designed to run strictly within the company LAN.
- **RBAC**: Managers can only access data for their assigned juniors.
- **Data Encryption**: All data transmitted between SentinelNode and SentinelServer is encrypted using cryptographic protocols to ensure confidentiality.



---

## ⚙️ Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/ShahilPatel-IITDh/SentinelHub.git
cd SentinelHub

### 2. Create virtual environment
```bash
python -m venv venv
```
Activate:
**Windows:**
```bash
venv\Scripts\activate
```
**Mac/Linux:**

```bash
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## ▶️ Running the Server

```bash
uvicorn main:app --reload
```

Server runs at:
👉 http://127.0.0.1:8000

---

## 📡 API Endpoints

### 🔐 Authentication

* POST `/auth/login`

### 🖥️ Nodes

* GET `/nodes`
* POST `/nodes`

### ❤️ Heartbeat

* POST `/heartbeat`

### 📊 Logs & Summary

* GET `/logs`
* GET `/summary`

---



