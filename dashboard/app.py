import streamlit as st
import requests
import pandas as pd
from streamlit_autorefresh import st_autorefresh
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("SERVER_URL", "http://127.0.0.1:8000").rstrip("/")

#------------------ HELPERS for authorization ---------------- #
def get_auth_headers():
    token = st.session_state.get("token")

    if not token:
        return {}

    return {
        "Authorization": f"Bearer {token}"
    }

def api_get(path):
    try:
        response = requests.get(
            f"{BASE_URL}{path}",
            headers=get_auth_headers(),
            timeout=10
        )

        if response.status_code == 401:
            st.error("Session expired or invalid token. Please login again.")
            st.session_state.clear()
            st.stop()

        if response.status_code == 403:
            st.error("Access denied. You do not have permission to view this data.")
            return None

        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        st.error(f"API request failed: {e}")
        return None

@st.cache_data(ttl=60)
def get_juniors_cached(token):
    return api_get("/api/node/juniors")


@st.cache_data(ttl=5)
def get_dashboard_live_cached(token):
    return api_get("/api/node/dashboard/live")

st.set_page_config(page_title="Sentinel Dashboard", layout="wide")


if "last_error_count" not in st.session_state:
    st.session_state["last_error_count"] = 0


# ---------------- AUTHENTICATION ---------------- #



# ---------------- MAIN ---------------- #

def rerun_app():
    try:
        st.rerun()
    except AttributeError:
        st.experimental_rerun()



if st.session_state.get("is_logged_in") and st.session_state.get("token"):
    st_autorefresh(interval=5000, key="dashboard_refresh")
    st.title("📊 Sentinel Hierarchy Monitoring Dashboard")
    st.info("Monitoring Scope: Direct Juniors Only")

    logged_employee_id = st.session_state.get("employee_id")
    st.sidebar.success(f"Logged in as Employee ID: {logged_employee_id}")

    if st.sidebar.button("Logout"):
        st.cache_data.clear()
        st.session_state.clear()
        rerun_app()

    # ---------------- DIRECT JUNIORS ---------------- #
    st.subheader("👥 Direct Juniors")

    juniors = get_juniors_cached(st.session_state["token"])

    if juniors:
        junior_df = pd.DataFrame(juniors)
        st.dataframe(junior_df, use_container_width=True)
    else:
        st.warning("No direct juniors assigned under your hierarchy.")

    st.divider()
    # ======================================================
    # FETCH DASHBOARD DATA (ONE API CALL)
    # ======================================================

    dashboard_data = get_dashboard_live_cached(
        st.session_state["token"]
    )
    summary = dashboard_data.get("summary", {})
    logs = dashboard_data.get("logs", [])
    metrics = dashboard_data.get("metrics", [])
    errors = dashboard_data.get("errors", [])

    
    # ---------------- SUMMARY ---------------- #
    st.subheader("Team Summary")

    # summary = get_summary_cached(st.session_state["token"])

    if summary:
        col1, col2, col3, col4, col5 = st.columns(5)

        col1.metric("Total Juniors", summary.get("total_juniors", 0))
        col2.metric("Total Machines", summary.get("total_machines", 0))
        col3.metric("Active Machines", summary.get("active_machines", 0))
        col4.metric("Inactive Machines", summary.get("inactive_machines", 0))
        col5.metric("Total Processes", summary.get("total_processes", 0))
    else:
        st.info("No summary data available.")

    st.divider()

    # ---------------- LOGS ---------------- #
    st.subheader("Process Logs")

    # logs = get_logs_cached(st.session_state["token"])

    if logs:
        df = pd.DataFrame(logs)

        if "timestamp" in df.columns:
            df["timestamp"] = pd.to_datetime(df["timestamp"])

        search = st.text_input("Search process")

        if search and "process_name" in df.columns:
            df = df[df["process_name"].str.contains(search, case=False, na=False)]

        if "employee_id" in df.columns:
            employees = sorted(df["employee_id"].dropna().unique().tolist())
            selected_employee = st.selectbox(
                "Filter by Employee",
                ["All"] + employees
            )

            if selected_employee != "All":
                df = df[df["employee_id"] == selected_employee]

        machine_column = None

        if "machine_mac" in df.columns:
            machine_column = "machine_mac"
        elif "mac_address" in df.columns:
            machine_column = "mac_address"

        if machine_column:
            machines = df[machine_column].dropna().unique().tolist()
            selected_machine = st.selectbox(
                "Filter by Machine",
                ["All"] + machines
            )

            if selected_machine != "All":
                df = df[df[machine_column] == selected_machine]

        if "timestamp" in df.columns:
            df = df.sort_values(by="timestamp", ascending=False)

        st.dataframe(df.head(20), use_container_width=True)

    else:
        st.info("No process logs available for your direct juniors.")

    st.divider()

    # ---------------- METRICS ---------------- #
    st.subheader("System Performance")

    # metrics = get_metrics_cached(st.session_state["token"])

    if metrics:
        mdf = pd.DataFrame(metrics)

        if "timestamp" in mdf.columns:
            mdf["timestamp"] = pd.to_datetime(mdf["timestamp"])

        if "mac_address" in mdf.columns:
            machines = mdf["mac_address"].dropna().unique().tolist()

            selected_machine = st.selectbox(
                "Select Machine",
                ["All"] + machines
            )

            machines_to_show = (
                machines[:5] if selected_machine == "All"
                else [selected_machine]
            )

            for machine in machines_to_show:
                st.markdown(f"### 🖥️ {machine}")

                machine_df = mdf[mdf["mac_address"] == machine]

                if "timestamp" in machine_df.columns:
                    machine_df = machine_df.sort_values(by="timestamp")

                metric_columns = []

                for col in ["cpu_percent", "memory_percent", "disk_percent"]:
                    if col in machine_df.columns:
                        metric_columns.append(col)

                for col in ["cpu", "memory", "disk"]:
                    if col in machine_df.columns:
                        metric_columns.append(col)

                if metric_columns and "timestamp" in machine_df.columns:
                    st.line_chart(
                        machine_df.set_index("timestamp")[metric_columns]
                    )
                else:
                    st.dataframe(machine_df, use_container_width=True)
        else:
            st.dataframe(mdf, use_container_width=True)

    else:
        st.info("No metrics available for your direct juniors.")

    st.divider()

    # ---------------- ERROR LOGS ---------------- #
    st.subheader("System Alerts")

    # errors = get_errors_cached(st.session_state["token"])

    if errors:
        edf = pd.DataFrame(errors)

        if "timestamp" in edf.columns:
            edf["timestamp"] = pd.to_datetime(edf["timestamp"])

        current_count = len(edf)

        if current_count > st.session_state["last_error_count"]:
            st.toast("New alert detected!", icon="⚠️")

        st.session_state["last_error_count"] = current_count

        if "timestamp" in edf.columns:
            edf = edf.sort_values(by="timestamp", ascending=False)

        latest = edf.iloc[0]

        severity = str(latest.get("severity", "")).upper()
        message = latest.get("message", "New system alert detected.")

        if severity == "HIGH":
            st.error(f" {message}")
        elif severity == "MEDIUM":
            st.warning(f" {message}")
        else:
            st.info(f" {message}")

        if "mac_address" in edf.columns:
            machines = edf["mac_address"].dropna().unique().tolist()
            selected_machine = st.selectbox(
                "Filter Alerts by Machine",
                ["All"] + machines
            )

            if selected_machine != "All":
                edf = edf[edf["mac_address"] == selected_machine]

        def highlight(row):
            sev = str(row.get("severity", "")).upper()

            if sev == "HIGH":
                return ["background-color:#5c0000;color:white"] * len(row)
            elif sev == "MEDIUM":
                return ["background-color:#663c00;color:white"] * len(row)
            else:
                return ["background-color:#003300;color:white"] * len(row)

        st.dataframe(
            edf.style.apply(highlight, axis=1),
            use_container_width=True
        )

    else:
        st.success(" No active issues for your direct juniors.")

else:
    # st.title("Please login to continue")
    # st.info("Login with your employee ID and password to view hierarchy-based monitoring data.")
    st.title("Sentinel Authentication")
    st.markdown("Please login or register to access the Sentinel Hierarchy Monitoring Dashboard.")
    st.divider()

    left,centre,right = st.columns([1,2,1])

    with centre:
        tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        emp_id = st.text_input("Employee ID")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            if not emp_id or not password:
                st.error("Please enter both Employee ID and Password.")
            else:
                try:
                    res = requests.post(
                        f"{BASE_URL}/api/auth/login",
                        json={
                            "employee_id": emp_id,
                            "password": password
                        },
                        timeout=10
                    )

                    if res.status_code == 200:
                        data = res.json()
                        
                        st.cache_data.clear()

                        st.session_state["token"] = data.get("access_token")
                        st.session_state["employee_id"] = emp_id
                        st.session_state["is_logged_in"] = True

                        st.success("Logged in successfully!")
                        st.rerun()
                    else:
                        st.error("Invalid employee ID or password.")

                except ValueError:
                    st.error("Employee ID must be a number.")

                except requests.exceptions.RequestException as e:
                    st.error(f"Server connection failed: {e}")



    # REGISTER
    # ==========================================================

    with tab2:

        st.subheader("Register New User")

        name = st.text_input(
            "Full Name"
        )

        new_emp_id = st.number_input(
            "Employee ID",
            min_value=1,
            step=1
        )

        new_password = st.text_input(
            "Password",
            type="password",
            key="register_password"
        )

        # ---------------- FETCH POSTS ---------------- #

        posts = []

        try:
            post_response = requests.get(
                f"{BASE_URL}/api/auth/posts",
                timeout=5
            )

            if post_response.status_code == 200:
                posts = post_response.json()

        except:
            pass

        if not posts:
            st.error(
                "Could not load posts from server."
            )

        else:

            post_map = {
                p["title"]: p["id"]
                for p in posts
            }

            selected_post = st.selectbox("Select Post", list(post_map.keys()))

            # ---------------- FETCH USERS ---------------- #

            users = []

            try:
                user_response = requests.get(
                    f"{BASE_URL}/api/auth/users",
                    timeout=5
                )

                if user_response.status_code == 200:
                    users = user_response.json()

            except:
                pass

            officer_map = {
                f'{u["employee_id"]} - {u["name"]}':
                u["employee_id"]
                for u in users
            }

            selected_officer = st.selectbox( "Reporting Officer",["None"] + list(officer_map.keys()) )

            reporting_officer = None

            if selected_officer != "None":
                reporting_officer = officer_map[
                    selected_officer
                ]

            # ---------------- REGISTER BUTTON ---------------- #

            if st.button("Register"):

                if not name:
                    st.error("Name is required.")

                elif not new_password:
                    st.error(
                        "Password is required."
                    )

                else:

                    payload = {
                        "name": name,
                        "employee_id": int(new_emp_id),
                        "password": new_password,
                        "designation": selected_post,
                        "post_id": post_map[selected_post],
                        "reporting_officer_id": reporting_officer
                    }

                    try:
                        response = requests.post(
                            f"{BASE_URL}/api/auth/register",
                            json=payload,
                            timeout=10
                        )

                        if response.status_code in [200, 201]:
                            st.success(
                                "User registered successfully!"
                            )

                        else:
                            st.error(
                                response.text
                            )

                    except requests.exceptions.RequestException as e:
                        st.error(str(e))

