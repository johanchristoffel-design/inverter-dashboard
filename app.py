import pandas as pd
import sqlite3
import streamlit as st

# Streamlit Page Configuration
st.set_page_config(
    page_title='Dual Inverter Dashboard', page_icon='⚡', layout='wide'
)

st.title('⚡ Dual LuxPower System Dashboard')
st.markdown(
    'Real-time aggregated telemetry from both parallel inverters stored in SQLite.'
)


# Function to load and aggregate combined data from SQLite
def load_data():
  conn = sqlite3.connect('inverters.db')
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
  df = pd.read_sql(query, conn)
  conn.close()
  df['timestamp'] = pd.to_datetime(df['timestamp'])
  return df


df = load_data()

if df.empty:
  st.warning(
      'No data found in database yet. Make sure your logging script has run!'
  )
else:
  # Get latest metrics for top summary cards
  latest = df.iloc[0]

  # --- Top Metric Cards ---
  col1, col2, col3, col4 = st.columns(4)
  col1.metric('Solar Generation (PV)', f"{latest['total_pv_w']:,.0f} W")
  col2.metric('Home Load', f"{latest['total_load_w']:,.0f} W")
  col3.metric('Battery Power', f"{latest['total_batt_w']:,.0f} W")
  col4.metric('Battery SOC', f"{latest['combined_soc']:.0f}%")

  st.markdown('---')

  # --- Interactive Charts ---
  st.subheader('📈 Power Overview History')
  chart_df = df.set_index('timestamp')[
      ['total_pv_w', 'total_load_w', 'total_batt_w']
  ]
  st.line_chart(chart_df)

  # --- Raw Data Table ---
  with st.expander('View Raw Combined Database Records'):
    st.dataframe(df, use_container_width=True)