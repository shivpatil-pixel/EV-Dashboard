
import streamlit as st
import pandas as pd
import random
import math

st.set_page_config(
    page_title="Hybrid Battery + Supercapacitor EV Analyzer",
    page_icon="🔋",
    layout="wide"
)

st.title("🔋 Hybrid Battery + Supercapacitor EV Analyzer")
st.subheader("Developed by: Shivswarup Patil")
st.caption("B.Tech E&TC | JJMCOE | Shivaji University, Kolhapur")
st.caption("Final Year Project | Simulated demo data — no hardware connected")

with st.sidebar:
    st.header("Test Controls")
    mode = st.selectbox(
        "Operating Mode",
        ["Compare Both", "Battery Only", "Hybrid System"]
    )
    samples = st.slider("Test duration (samples)", 20, 100, 50)
    base_v = st.slider("Nominal battery voltage (V)", 11.5, 12.8, 12.4, 0.1)
    load_level = st.slider("Load intensity", 1, 10, 6)
    run = st.button("Run New Test", type="primary")

if "df" not in st.session_state or run:
    random.seed()
    rows = []

    for i in range(samples):
        transient = math.exp(-((i - samples * 0.35) /
                               (samples * 0.08)) ** 2)

        load = random.uniform(1.0, 2.5) + load_level * 0.5 * transient

        battery_only_v = (
            base_v - 0.12 * load_level * transient
            - random.uniform(0, 0.04)
        )
        hybrid_v = (
            base_v - 0.07 * load_level * transient
            - random.uniform(0, 0.03)
        )

        battery_only_i = load + random.uniform(0, 0.3)
        hybrid_i = max(
            0.2, load - 0.15 * load_level * transient
        ) + random.uniform(0, 0.2)

        supercap_v = max(0, 5.0 - 1.2 * transient - i * 0.002)
        supercap_i = 2.0 * load_level * transient + random.uniform(0, 0.3)

        rows.append({
            "Time (s)": i,
            "Battery-only voltage (V)": round(battery_only_v, 3),
            "Hybrid battery voltage (V)": round(hybrid_v, 3),
            "Battery-only current (A)": round(battery_only_i, 3),
            "Hybrid battery current (A)": round(hybrid_i, 3),
            "Supercapacitor voltage (V)": round(supercap_v, 3),
            "Supercapacitor current (A)": round(supercap_i, 3)
        })

    st.session_state["df"] = pd.DataFrame(rows)
    st.session_state["base_v"] = base_v

df = st.session_state["df"]
reference_v = st.session_state["base_v"]

if mode == "Battery Only":
    voltage_col = "Battery-only voltage (V)"
    current_col = "Battery-only current (A)"
elif mode == "Hybrid System":
    voltage_col = "Hybrid battery voltage (V)"
    current_col = "Hybrid battery current (A)"
else:
    voltage_col = "Hybrid battery voltage (V)"
    current_col = "Hybrid battery current (A)"

voltage = df[voltage_col]
current = df[current_col]
sag = max(0, reference_v - voltage.min())
peak_current = current.max()
peak_power = (voltage * current).max()

st.subheader("Performance Summary")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Minimum Battery Voltage", f"{voltage.min():.2f} V")
c2.metric("Voltage Sag", f"{sag:.2f} V")
c3.metric("Voltage Sag (%)", f"{sag / reference_v * 100:.2f}%")
c4.metric("Peak Battery Current", f"{peak_current:.2f} A")

c5, c6 = st.columns(2)
c5.metric("Peak Estimated Power", f"{peak_power:.2f} W")
c6.metric("Selected Mode", mode)

st.subheader("Battery Voltage vs Time")
voltage_cols = ["Battery-only voltage (V)", "Hybrid battery voltage (V)"]
if mode == "Battery Only":
    voltage_cols = ["Battery-only voltage (V)"]
elif mode == "Hybrid System":
    voltage_cols = ["Hybrid battery voltage (V)"]
st.line_chart(df.set_index("Time (s)")[voltage_cols])

st.subheader("Battery Current vs Time")
current_cols = ["Battery-only current (A)", "Hybrid battery current (A)"]
if mode == "Battery Only":
    current_cols = ["Battery-only current (A)"]
elif mode == "Hybrid System":
    current_cols = ["Hybrid battery current (A)"]
st.line_chart(df.set_index("Time (s)")[current_cols])

st.subheader("Supercapacitor Monitoring (Simulated)")
sc1, sc2 = st.columns(2)
sc1.line_chart(df.set_index("Time (s)")["Supercapacitor voltage (V)"])
sc2.line_chart(df.set_index("Time (s)")["Supercapacitor current (A)"])

st.subheader("Test Data")
st.dataframe(df, use_container_width=True)

csv_data = df.to_csv(index=False).encode("utf-8")
st.download_button(
    "Download Test Data (CSV)",
    data=csv_data,
    file_name="ev_hess_test_data.csv",
    mime="text/csv"
)

st.info(
    "Academic software demo: values are simulated, not measured from real hardware. "
    "Use an ESP32 and properly protected sensors for actual measurements."
)
