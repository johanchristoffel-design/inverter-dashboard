import os
import sqlite3
import pandas as pd
import streamlit as st

# Streamlit Page Configuration
st.set_page_config(
    page_title="Dual Inverter Dashboard", page_icon="⚡", layout="wide"
)

st.title("⚡ Dual LuxPower System Dashboard")
st.markdown(
    "Real-time aggregated telemetry from both parallel inverters stored in SQLite."
)


# Function to load and aggregate combined data from SQLite safely
def load_data():
  db_path = "inverters.db"
  if not os.path.exists(db_path):
    return pd.DataFrame()

  conn = sqlite3.connect(db_path)
  cursor = conn.cursor()

  # Check if table exists first to prevent crashes
  cursor.execute(
      "SELECT name FROM sqlite_master WHERE type='table' AND"
      " name='inverter_telemetry';"
  )
  table_exists = cursor.fetchone()

  if not table_exists:
    conn.close()
    return pd.DataFrame()

  query = """
    SELECT 
        timestamp,
        AVG(soc) AS combined_soc,
        AVG(bat_v) AS avg_bat_v,
        SUM(batt_w) AS total_batt_w,
        SUM(pv_w) AS total_pv_w,
        SUM(load_w) AS total_load_w,
        SUM(import_w) AS total_import_w,
        SUM(export_w) AS total_export_w,
        AVG(inv_temp) AS avg_inv_temp,
        MAX(today_pv_kwh) AS max_today_pv_kwh
    FROM inverter_telemetry
    GROUP BY timestamp
    ORDER BY timestamp DESC;
    """
  try:
    df = pd.read_sql(query, conn)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
  except Exception:
    df = pd.DataFrame()
  finally:
    conn.close()

  return df


df = load_data()

if df.empty:
  st.warning(
      "⚠️ Database table 'inverter_telemetry' is empty or not found on the"
      " cloud environment."
  )
  st.info(
      "Note: Your local PC runs the 5-minute background logger into"
      " `inverters.db`, but since the database is excluded from GitHub, the"
      " cloud viewer doesn't have your local history file. You can view your"
      " live dashboard seamlessly right on your PC by running `python -m"
      " streamlit run app.py`!"
  )
else:
  # Get latest metrics for top summary cards
  latest = df.iloc[0]

  # --- Top Metric Cards ---
  col1, col2, col3, col4 = st.columns(4)
  col1.metric("Solar Generation (PV)", f"{latest['total_pv_w']:,.0f} W")
  col2.metric("Home Load", f"{latest['total_load_w']:,.0f} W")
  col3.metric("Battery Power", f"{latest['total_batt_w']:,.0f} W")
  col4.metric("Battery SOC", f"{latest['combined_soc']:.0f}%")

  st.markdown("---")

  # --- Interactive Charts ---
  st.subheader("📈 Power Overview History")
  chart_df = df.set_index("timestamp")[
      ["total_pv_w", "total_load_w", "total_batt_w"]
  ]
  st.line_chart(chart_df)

  # --- Raw Data Table ---
  with st.expander("View Raw Combined Database Records"):
    st.dataframe(df, use_container_width=True)