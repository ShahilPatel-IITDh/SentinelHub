import streamlit as st
import requests
import pandas as pd
from streamlit_autorefresh import st_autorefresh

BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Sentinel Dashboard", layout="wide")
st_autorefresh(interval=5000, key="refresh")

if "last_error_count" not in st.session_state:
    st.session_state["last_error_count"] = 0


# ---------------- LOGIN ---------------- #

st.sidebar.title("🔐 Manager Login")

emp_id = st.sidebar.text_input("Employee ID")
password = st.sidebar.text_input("Password", type="password")

if st.sidebar.button("Login"):
    try:
        res = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"employee_id": emp_id, "password": password}
        )

        if res.status_code == 200:
            st.session_state["token"] = res.json()["access_token"]
            st.session_state["manager_id"] = int(emp_id)
            st.sidebar.success("Logged in!")
        else:
            st.sidebar.error(res.text)

    except Exception as e:
        st.sidebar.error(str(e))


# ---------------- MAIN ---------------- #

if "token" in st.session_state:

    headers = {"Authorization": f"Bearer {st.session_state['token']}"}
    manager_id = st.session_state["manager_id"]

    st.title("📊 Sentinel Monitoring Dashboard")

    # ---------------- SUMMARY ---------------- #
    summary_res = requests.get(
        f"{BASE_URL}/api/node/summary/{manager_id}",
        headers=headers
    )

    if summary_res.status_code == 200:
        summary = summary_res.json()

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Total Machines", summary["total_machines"])
        col2.metric("Active Machines", summary["active_machines"])
        col3.metric("Inactive Machines", summary["inactive_machines"])
        col4.metric("Total Processes", summary["total_processes"])

    st.divider()

    # ---------------- LOGS ---------------- #
    st.subheader("📄 Process Logs")

    logs_res = requests.get(
        f"{BASE_URL}/api/node/logs/{manager_id}",
        headers=headers
    )

    if logs_res.status_code == 200:
        logs = logs_res.json()

        if logs:
            df = pd.DataFrame(logs)
            df["timestamp"] = pd.to_datetime(df["timestamp"])

            # 🔍 Search
            search = st.text_input("Search process")

            if search:
                df = df[df["process_name"].str.contains(search, case=False)]

            # 👤 Employee filter
            employees = sorted(df["employee_id"].unique().tolist())
            selected_employee = st.selectbox(
                "Filter by Employee",
                ["All"] + employees
            )

            if selected_employee != "All":
                df = df[df["employee_id"] == selected_employee]

            # 🖥️ Machine filter
            machines = df["machine_mac"].unique().tolist()
            selected_machine = st.selectbox(
                "Filter by Machine",
                ["All"] + machines
            )

            if selected_machine != "All":
                df = df[df["machine_mac"] == selected_machine]

            df = df.sort_values(by="timestamp", ascending=False)

            st.dataframe(df.head(20), use_container_width=True)

        else:
            st.info("No logs available")

    st.divider()

    # ---------------- METRICS ---------------- #
    st.subheader("🧠 System Performance")

    metrics_res = requests.get(
        f"{BASE_URL}/api/node/metrics/{manager_id}",
        headers=headers
    )

    if metrics_res.status_code == 200:
        metrics = metrics_res.json()

        if metrics:
            mdf = pd.DataFrame(metrics)
            mdf["timestamp"] = pd.to_datetime(mdf["timestamp"])

            machines = mdf["mac_address"].unique().tolist()

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

                st.line_chart(
                    machine_df.set_index("timestamp")[["cpu", "memory", "disk"]]
                )

    st.divider()

    # ---------------- ERROR LOGS ---------------- #
    st.subheader("🚨 System Alerts")

    error_res = requests.get(
        f"{BASE_URL}/api/node/errors/{manager_id}",
        headers=headers
    )

    if error_res.status_code == 200:
        errors = error_res.json()

        if errors:
            edf = pd.DataFrame(errors)
            edf["timestamp"] = pd.to_datetime(edf["timestamp"])

            # 🔥 Toast for new alerts
            current_count = len(edf)
            if current_count > st.session_state["last_error_count"]:
                st.toast("🚨 New alert detected!", icon="⚠️")

            st.session_state["last_error_count"] = current_count

            # 🔥 Latest alert banner
            latest = edf.sort_values(by="timestamp", ascending=False).iloc[0]

            if latest["severity"].upper() == "HIGH":
                st.error(f"🚨 {latest['message']}")
            elif latest["severity"].upper() == "MEDIUM":
                st.warning(f"⚠️ {latest['message']}")
            else:
                st.info(f"ℹ️ {latest['message']}")

            # 🔍 Filters
            machines = edf["mac_address"].unique().tolist()
            selected_machine = st.selectbox(
                "Filter Alerts by Machine",
                ["All"] + machines
            )

            if selected_machine != "All":
                edf = edf[edf["mac_address"] == selected_machine]

            # 🎨 Row coloring
            def highlight(row):
                sev = row["severity"].upper()
                if sev == "HIGH":
                    return ["background-color:#5c0000;color:white"] * len(row)
                elif sev == "MEDIUM":
                    return ["background-color:#663c00;color:white"] * len(row)
                else:
                    return ["background-color:#003300;color:white"] * len(row)

            st.dataframe(
                edf.sort_values(by="timestamp", ascending=False)
                   .style.apply(highlight, axis=1),
                use_container_width=True
            )

        else:
            st.success("✅ No active issues")

else:
    st.title("🔒 Please login to continue")