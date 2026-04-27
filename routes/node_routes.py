from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from db.database import SessionLocal
from db.models import User
from schemas.schemas import Heartbeat
from services.heartbeat_service import process_heartbeat
from services.log_service import get_manager_logs
from services.summary_service import get_summary

from core.security import decode_token

router = APIRouter(prefix="/api/node")

security = HTTPBearer()


# ---------------- DB ---------------- #

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------- AUTH ---------------- #

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials

    try:
        user_id = decode_token(token)
        return user_id
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


# ---------------- HEARTBEAT ---------------- #

@router.post("/heartbeat")
def heartbeat(
    data: Heartbeat,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)
):
    return process_heartbeat(db, data, user_id)


# ---------------- LOGS ---------------- #

@router.get("/logs/{manager_id}")
def get_logs(
    manager_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)
):
    # ✅ allow manager OR their employee
    if user_id != manager_id:
        user = db.query(User).filter(User.employee_id == user_id).first()

        if not user or user.reporting_officer_id != manager_id:
            raise HTTPException(status_code=403, detail="Access denied")

    return get_manager_logs(db, manager_id)


# ---------------- SUMMARY ---------------- #

@router.get("/summary/{manager_id}")
def summary(
    manager_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)
):
    if user_id != manager_id:
        user = db.query(User).filter(User.employee_id == user_id).first()

        if not user or user.reporting_officer_id != manager_id:
            raise HTTPException(status_code=403, detail="Access denied")

    return get_summary(db, manager_id)


from fastapi.responses import HTMLResponse

@router.get("/dashboard", response_class=HTMLResponse)
def dashboard():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Sentinel Dashboard</title>

        <style>
            body {
                background: #f8fafc;
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
                color: #1e293b;
            }

            .container {
                max-width: 1200px;
                margin: auto;
                padding: 20px;
            }

            h1 {
                color: #0ea5e9;
                margin-bottom: 10px;
            }

            .stats {
                display: flex;
                gap: 20px;
                margin-bottom: 20px;
            }

            .card {
                background: white;
                padding: 15px;
                border-radius: 10px;
                box-shadow: 0 4px 10px rgba(0,0,0,0.05);
                flex: 1;
                text-align: center;
            }

            .card h2 {
                margin: 0;
                color: #0ea5e9;
            }

            .table-card {
                background: white;
                border-radius: 10px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.05);
                padding: 20px;
            }

            table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 10px;
                font-size: 14px;
            }

            thead {
                background: #e2e8f0;
            }

            th, td {
                padding: 10px;
                text-align: left;
            }

            td {
                border-bottom: 1px solid #e2e8f0;
            }

            tr:hover {
                background: #f1f5f9;
            }

            .danger {
                color: red;
                font-weight: bold;
            }

            .safe {
                color: green;
            }

            .footer {
                margin-top: 10px;
                font-size: 12px;
                color: #64748b;
            }
        </style>
    </head>

    <body>
        <div class="container">
            <h1>🔥 Sentinel Live Dashboard</h1>

            <div class="stats">
                <div class="card">
                    <h2 id="count">0</h2>
                    <p>Total Logs</p>
                </div>

                <div class="card">
                    <h2 id="machines">0</h2>
                    <p>Machines</p>
                </div>

                <div class="card">
                    <h2 id="updated">--</h2>
                    <p>Last Updated</p>
                </div>
            </div>

            <div class="table-card">
                <table>
                    <thead>
                        <tr>
                            <th>Process</th>
                            <th>Machine</th>
                            <th>IP</th>
                            <th>Time</th>
                        </tr>
                    </thead>
                    <tbody id="logs">
                        <tr><td colspan="4">Loading...</td></tr>
                    </tbody>
                </table>

                <div class="footer">
                    Auto-refresh every 3 seconds
                </div>
            </div>
        </div>

        <script>
            let token = "";

            async function login() {
                const res = await fetch("/api/auth/login", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({
                        employee_id: 100,
                        password: "123456"
                    })
                });

                const data = await res.json();
                token = data.access_token;
            }

            function formatTime(ts) {
                return new Date(ts).toLocaleTimeString();
            }

            function isSuspicious(name) {
                const risky = ["powershell", "cmd", "taskkill"];
                return risky.some(r => name.toLowerCase().includes(r));
            }

            async function fetchLogs() {
                if (!token) return;

                const res = await fetch("/api/node/logs/100", {
                    headers: {
                        "Authorization": "Bearer " + token
                    }
                });

                if (res.status === 401) {
                    await login();
                    return;
                }

                const data = await res.json();

                const table = document.getElementById("logs");
                table.innerHTML = "";

                document.getElementById("count").innerText = data.length;

                const machines = new Set(data.map(d => d.hostname));
                document.getElementById("machines").innerText = machines.size;

                document.getElementById("updated").innerText =
                    new Date().toLocaleTimeString();

                data.slice(0, 20).forEach(log => {
                    const danger = isSuspicious(log.process_name);

                    const row = `
                        <tr>
                            <td class="${danger ? 'danger' : 'safe'}">
                                ${log.process_name}
                            </td>
                            <td>${log.hostname}</td>
                            <td>${log.ip_address}</td>
                            <td>${formatTime(log.timestamp)}</td>
                        </tr>
                    `;
                    table.innerHTML += row;
                });
            }

            async function start() {
                await login();
                fetchLogs();
                setInterval(fetchLogs, 3000);
            }

            start();
        </script>
    </body>
    </html>
    """