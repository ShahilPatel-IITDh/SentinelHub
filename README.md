# SentinelHub

### Distributed System Monitoring Platform (LAN-Based)

![Python](https://img.shields.io/badge/Python-3.x-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green)
![Architecture](https://img.shields.io/badge/Architecture-Client--Server-orange)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)
![Beginner Friendly](https://img.shields.io/badge/Level-Beginner%20Friendly-yellow)

---

# What is SentinelHub?

SentinelHub is a **real-time system monitoring platform** where:

* Multiple computers send their data
* One server processes everything
*One dashboard shows everything

---

# 🧠 Understand It Like You're 10 Years Old

Imagine:

* Every computer is a **student**
* The server is the **teacher**
* The dashboard is the **report card**

👉 Students send their marks → Teacher collects → Report card shows results

---

# Architecture Diagram

```
         Dashboard (Sentinel-Dash)
                  │
                  ▼
        Server (FastAPI Backend)
                  │
          ┌───────┴────────┐
          ▼                ▼
     🗄️ Database     ⚙️ Business Logic
                  ▲
                  │
      ┌───────────┼───────────┐
      ▼           ▼           ▼
🖥️ Node        🖥️ Node      🖥️ Node
(Client)      (Client)     (Client)
```

---

# 📁 Project Structure

```
SentinelHub/
│
├── server/        # 🔥 Backend (MOST IMPORTANT)
├── client/        # Sends system data
├── dashboard/     # Displays data
```

---

# What is Built

## Core Achievements

### Distributed Monitoring System

* Multiple clients send system data to one server

### Real-Time Data Flow (Simulated)

* Continuous data updates (heartbeat mechanism)

### Backend API (FastAPI)

* Handles:

  * Register
  * Login
  * Data ingestion
  * Data retrieval

### System Metrics Tracking

* CPU usage
* Memory usage
* Disk usage
* Running processes

### Logging System

* Structured logs
* Severity levels (INFO, ERROR, etc.)

### Dashboard Integration

* Displays live system data

### Database Integration

* Stores:

  * Users
  * Logs
  * Metrics

---

# Current-Status

This project is **NOT production-ready yet**.

### Missing Features:

* No JWT authentication
* No password hashing (or basic)
* No HTTPS security
* No WebSockets (real-time streaming)
* No load balancing

👉 This is a **strong prototype / foundation system**

---

# FULL SETUP GUIDE (EXTREMELY DETAILED)

Follow this EXACTLY.

---

## STEP 0: Install Python

Download:
https://www.python.org/downloads/

During install:

Check **"Add Python to PATH"**

---

## 📦 STEP 1: Install Dependencies

Open Command Prompt:

```
pip install fastapi uvicorn psutil requests
```

Wait until it finishes.

---

# STEP 2: Start the Server (MOST IMPORTANT)

---

## Go to server folder

```
cd C:\SentinelHub\server
```

---

## Run server

```
uvicorn main:app --reload
```

---

## Open API Page

Open browser:

```
http://127.0.0.1:8000/docs
```

👉 If this opens → Server is working ✅

---

# STEP 3: Register User

---

## Find:

```
POST /register
```

Click → Try it out

---

## Enter:

```json
{
  "username": "testuser",
  "password": "1234"
}
```

Click → Execute

---

## Output:

```
User created successfully
```

---

# STEP 4: Run Client

---

## Open NEW terminal

```
cd C:\SentinelHub\client
```

---

## Run:

```
python client.py
```

---

## What happens?

Client sends:

* CPU
* Memory
* Disk
* Processes

to server continuously

---

# STEP 5: Run Dashboard

---

## Open ANOTHER terminal

```
cd C:\SentinelHub\dashboard
```

---

## Run:

```
python dashboard.py
```

---

# SUCCESS CHECK

| Component | Expected        |
| --------- | --------------- |
| Server    | Running + logs  |
| Client    | Sending data    |
| Dashboard | Showing metrics |

---

# TEST FLOW

1. Start server
2. Register user
3. Run client
4. Run dashboard

---

# Data Flow (Simple)

```
Client → Server → Database
        ↓
     Dashboard
```

---

# Clean Repository Note

This version contains only:

✔ server
✔ client
✔ dashboard

Removed:

* Old backend structure
* Cache files
* Unused folders

---

# Common Errors + Fixes

## uvicorn not found

```
pip install uvicorn
```

## Python not recognized

Reinstall Python with PATH enabled

## Dashboard not updating

Check:

* Server running
* Client running

---

# FUTURE IMPROVEMENTS 

---

## Security Upgrades

* JWT Authentication
* Password hashing (bcrypt)
* HTTPS support

---

## Real-Time Features

* WebSockets (live updates)
* Live alerts

---

## Notification System

* Email alerts for:

  * High CPU usage
  * System crash
  * Unauthorized access

---

## Role-Based Access

* Admin
* Manager
* User

---

## Deployment

* Docker containers
* Cloud deployment (AWS / Azure / GCP)

---

## Advanced Dashboard

* Charts (CPU trends)
* Historical data
* Filters per machine

---

## AI Additions 

* Anomaly detection
* Predict system failures
* Smart alerts

---

## Scalability

* Load balancing
* Microservices architecture

---

# Contribution Guide

1. Fork repository
2. Create new branch
3. Make changes
4. Submit Pull Request

---


