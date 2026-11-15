import sqlite3
import pandas as pd

# Path to your actual log file
csv_path = r'C:\Users\Johan\Documents\Maluti_scripts\luxpower_log1.csv'
df = pd.read_csv(csv_path)

# Setup SQLite Database Connection (creates 'inverters.db' locally)
conn = sqlite3.connect('inverters.db')
cursor = conn.cursor()

# Create table schema matching your inverter telemetry metrics
cursor.execute(
    """
CREATE TABLE IF NOT EXISTS inverter_telemetry (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    sn TEXT,
    status TEXT,
    soc REAL,
    bat_v REAL,
    batt_w REAL,
    batt_a REAL,
    pv_w REAL,
    pv_v REAL,
    pv_a REAL,
    ipv1 REAL,
    ipv2 REAL,
    load_w REAL,
    load_a REAL,
    import_w REAL,
    import_a REAL,
    export_w REAL,
    inv_temp REAL,
    bat_temp REAL,
    vac REAL,
    fac REAL,
    today_pv_kwh REAL,
    today_discharge_kwh REAL,
    today_import_kwh REAL,
    today_export_kwh REAL,
    today_load_kwh REAL
)
"""
)
conn.commit()

# Append dataframe rows into SQLite
df.to_sql('inverter_telemetry', conn, if_exists='append', index=False)
conn.close()

print('Successfully updated inverters.db with new logs!')