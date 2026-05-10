# SentinelHub

Distributed system monitoring for LAN environments: monitored nodes send metrics and process information to a central FastAPI server; managers can inspect aggregated data via an optional dashboard.

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green)
![Architecture](https://img.shields.io/badge/Architecture-Client--Server-orange)

---

## Overview

- **Nodes (clients)** authenticate with the server and periodically POST heartbeat payloads (CPU, memory, disk, processes, machine identifiers).
- **Managers** use JWT-protected endpoints to view logs, metrics, summaries, and error logs for their team (employees reporting to that manager, plus the manager).
- **Storage** uses SQLite via SQLAlchemy (`sqlite:///./sentinel.db` relative to the server working directory).

---

## Architecture

```
                    Dashboard (Streamlit)
                             |
                             v
                   FastAPI (server/)
                             |
              +--------------+---------------+
              |                              |
              v                              v
         SQLite (sentinel.db)          Business logic / services
              ^
              |
    +---------+---------+
    v                   v
 Node client        Node client
 (client/)          (client/)
```

---

## Repository layout

| Path | Purpose |
|------|---------|
| `server/` | FastAPI application, SQLAlchemy models, routes, services |
| `client/` | CLI agent: login, heartbeat loop, optional log fetch |
| `dashboard/` | Streamlit UI for manager login and team views |

---

## Backend capabilities (current)

| Area | Implementation |
|------|----------------|
| Authentication | JWT access tokens (HS256), configured via environment |
| Passwords | Hashed with **bcrypt** (direct library usage in `server/core/security.py`) |
| REST API | OpenAPI docs at `/docs` when the server is running |
| Persistence | SQLite; tables created on startup (`Base.metadata.create_all`) |

### HTTP API summary

**Public**

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | Service identity message |
| GET | `/health` | Simple health JSON |
| POST | `/api/auth/register` | Register user (password policy enforced in routes) |
| POST | `/api/auth/login` | Login; returns bearer token |

**Authenticated (Bearer token)**

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/node/heartbeat` | Ingest metrics and processes for the logged-in user |
| GET | `/api/node/logs/{manager_id}` | Process logs for manager’s team (manager-only) |
| GET | `/api/node/summary/{manager_id}` | Aggregated counts (manager-only) |
| GET | `/api/node/metrics/{manager_id}` | Recent system metrics (manager-only) |
| GET | `/api/node/errors/{manager_id}` | Error log entries (manager-only) |

**Unauthenticated management endpoints (known limitation)**

| Method | Path | Description |
|--------|------|-------------|
| PUT | `/api/auth/assign-manager` | Assign reporting manager to an employee |
| PUT | `/api/auth/update-designation` | Update user designation |

These two endpoints are not protected by JWT today; restrict network access or add authentication before production use.

---

## Configuration

Create a `.env` file in `server/` (or ensure variables are set in the environment). The server loads it via `python-dotenv`.

| Variable | Purpose | Default |
|----------|---------|---------|
| `SECRET_KEY` | JWT signing secret | Development fallback in code (override in production) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT lifetime | `60` |

---

## Prerequisites

- Python 3.10 or newer recommended (3.11 is commonly used).
- pip

---

## Installation

### 1. Clone and enter the repository

```bash
cd SentinelHub
```

### 2. Server dependencies

From the repository root:

```bash
python -m pip install -r requirements.txt
```

`requirements.txt` includes FastAPI, Uvicorn, SQLAlchemy, python-dotenv, bcrypt, and python-jose.

### 3. Client dependencies

The heartbeat client uses `requests`, `python-dotenv`, and `psutil`:

```bash
python -m pip install requests python-dotenv psutil
```

### 4. Dashboard dependencies

```bash
python -m pip install streamlit pandas requests streamlit-autorefresh
```

Optional: set `SERVER_URL` / service URL in environment or `.env` for clients; the dashboard currently defaults to `http://127.0.0.1:8000` in code unless you change it.

---

## Running the server

Use the `server` directory as the working directory so package imports (`db`, `routes`, etc.) resolve.

```bash
cd server
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Alternatively:

```bash
cd server
python main.py
```

Interactive API documentation: `http://127.0.0.1:8000/docs`

---

## Registration and login

Registration expects JSON aligned with the `RegisterUser` schema (see `server/schemas/schemas.py`), for example:

```json
{
  "name": "BEL Employee",
  "employee_id": 123456,
  "password": "YourPass1!",
  "designation": "engineer",
  "reporting_officer_id": null
}
```

Password rules (register): minimum length 8, uppercase, lowercase, digit, and one of `!@#$%^&*`, and at most **72 bytes** when UTF-8 encoded (bcrypt limit). Use `null` for no reporting officer; sending `0` for `reporting_officer_id` is treated as no manager.

Login:

```json
{
  "employee_id": 123456,
  "password": "YourPass1!"
}
```

Response includes `access_token` for `Authorization: Bearer <token>`.

---

## Running the client

```bash
cd client
python client.py
```

The client logs in, sends heartbeats on an interval, and may fetch logs for the configured employee context (managers use their own employee ID when accessing manager-scoped endpoints).

---

## Running the dashboard

```bash
cd dashboard
streamlit run app.py
```

Log in as a user with **manager** designation to use team-scoped endpoints from the UI.

---

## Database file

SQLite database file: `sentinel.db` is created under the **current working directory** when the server runs (typically `server/sentinel.db` if you start Uvicorn from `server/`).

---

## Production readiness

This project is intended as a **foundation / prototype**, not a hardened production deployment.

**Already in place:** JWT authentication for protected node routes, bcrypt password hashing, structured logging and metrics persistence.

**Still recommended before production:** HTTPS termination, secrets management, authenticated administrative routes, rate limiting, backups, monitoring, and deployment-specific hardening. WebSockets, push notifications, and horizontal scaling are not implemented.

---

## Roadmap ideas

- Secure `assign-manager` and `update-designation` with role-based authentication.
- Optional POST endpoint for client-reported errors (schema exists; wiring may be added).
- WebSocket or SSE for live dashboard updates.
- TLS and reverse proxy documentation.

---

## Contributing

1. Fork the repository  
2. Create a branch for your changes  
3. Submit a pull request with a clear description  
