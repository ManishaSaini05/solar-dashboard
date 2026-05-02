# # ============================================================
# #  utils/database.py — SQLite storage for inverter readings
# # ============================================================

# import sqlite3
# import pandas as pd
# import os
# from datetime import datetime
# from config import DB_PATH

# # Auto-create the data folder if it doesn't exist
# os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)


# def get_connection():
#     conn = sqlite3.connect(DB_PATH, check_same_thread=False)
#     conn.row_factory = sqlite3.Row
#     return conn


# def init_db():
#     """Create tables if they don't exist yet."""
#     conn = get_connection()
#     cur = conn.cursor()

#     cur.executescript("""
#         CREATE TABLE IF NOT EXISTS inverter_data (
#             id          INTEGER PRIMARY KEY AUTOINCREMENT,
#             brand       TEXT    NOT NULL,
#             plant_name  TEXT    NOT NULL,
#             plant_id    TEXT,
#             inverter_sn TEXT,
#             power_kw    REAL,
#             today_kwh   REAL,
#             total_kwh   REAL,
#             status      TEXT,
#             temperature REAL,
#             voltage     REAL,
#             current_a   REAL,
#             last_update TEXT,
#             fetched_at  TEXT    NOT NULL
#         );

#         CREATE TABLE IF NOT EXISTS alert_log (
#             id          INTEGER PRIMARY KEY AUTOINCREMENT,
#             brand       TEXT,
#             plant_name  TEXT,
#             inverter_sn TEXT,
#             issue       TEXT,
#             alerted_at  TEXT    NOT NULL
#         );
#     """)
#     conn.commit()
#     conn.close()


# def save_readings(records: list[dict]):
#     """
#     Upsert a list of inverter reading dicts.
#     Each dict must have keys matching the inverter_data columns.
#     """
#     if not records:
#         return

#     conn = get_connection()
#     cur = conn.cursor()
#     now = datetime.now().isoformat(sep=" ", timespec="seconds")

#     for r in records:
#         cur.execute("""
#             INSERT INTO inverter_data
#                 (brand, plant_name, plant_id, inverter_sn,
#                  power_kw, today_kwh, total_kwh, status,
#                  temperature, voltage, current_a, last_update, fetched_at)
#             VALUES
#                 (:brand, :plant_name, :plant_id, :inverter_sn,
#                  :power_kw, :today_kwh, :total_kwh, :status,
#                  :temperature, :voltage, :current_a, :last_update, :fetched_at)
#         """, {**r, "fetched_at": now})

#     conn.commit()
#     conn.close()


# def log_alert(brand, plant_name, inverter_sn, issue):
#     conn = get_connection()
#     conn.execute("""
#         INSERT INTO alert_log (brand, plant_name, inverter_sn, issue, alerted_at)
#         VALUES (?, ?, ?, ?, ?)
#     """, (brand, plant_name, inverter_sn, issue,
#           datetime.now().isoformat(sep=" ", timespec="seconds")))
#     conn.commit()
#     conn.close()


# def get_recent_readings(hours: int = 24) -> pd.DataFrame:
#     conn = get_connection()
#     df = pd.read_sql(f"""
#         SELECT * FROM inverter_data
#         WHERE fetched_at >= datetime('now', '-{hours} hours')
#         ORDER BY fetched_at DESC
#     """, conn)
#     conn.close()
#     return df


# def get_alert_log(limit: int = 50) -> pd.DataFrame:
#     conn = get_connection()
#     df = pd.read_sql(f"""
#         SELECT * FROM alert_log ORDER BY alerted_at DESC LIMIT {limit}
#     """, conn)
#     conn.close()
#     return df


# def get_power_history(plant_name: str, days: int = 7) -> pd.DataFrame:
#     conn = get_connection()
#     df = pd.read_sql("""
#         SELECT DATE(fetched_at) as date, AVG(power_kw) as avg_power,
#                MAX(today_kwh) as daily_kwh
#         FROM inverter_data
#         WHERE plant_name = ?
#           AND fetched_at >= datetime('now', ? || ' days')
#         GROUP BY DATE(fetched_at)
#         ORDER BY date
#     """, conn, params=(plant_name, f"-{days}"))
#     conn.close()
#     return df

# utils/database.py
import sqlite3, os, pandas as pd
from datetime import datetime
from config import DB_PATH

os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

def _conn():
    c = sqlite3.connect(DB_PATH, check_same_thread=False)
    c.row_factory = sqlite3.Row
    return c

def init_db():
    c = _conn()
    c.executescript("""
        CREATE TABLE IF NOT EXISTS inverter_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            brand TEXT, plant_name TEXT, plant_id TEXT, inverter_sn TEXT,
            power_kw REAL, today_kwh REAL, total_kwh REAL, status TEXT,
            temperature REAL, voltage REAL, current_a REAL,
            last_update TEXT, fetched_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS alert_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            brand TEXT, plant_name TEXT, inverter_sn TEXT,
            issue TEXT, alerted_at TEXT NOT NULL
        );
    """)
    c.commit(); c.close()

def save_readings(records):
    if not records: return
    c = _conn(); now = datetime.now().isoformat(sep=" ", timespec="seconds")
    for r in records:
        c.execute("""INSERT INTO inverter_data
            (brand,plant_name,plant_id,inverter_sn,power_kw,today_kwh,total_kwh,
             status,temperature,voltage,current_a,last_update,fetched_at)
            VALUES(:brand,:plant_name,:plant_id,:inverter_sn,:power_kw,:today_kwh,
                   :total_kwh,:status,:temperature,:voltage,:current_a,:last_update,:fa)""",
            {**r, "fa": now})
    c.commit(); c.close()

def log_alert(brand, plant, sn, issue):
    c = _conn()
    c.execute("INSERT INTO alert_log(brand,plant_name,inverter_sn,issue,alerted_at) VALUES(?,?,?,?,?)",
              (brand, plant, sn, issue, datetime.now().isoformat(sep=" ",timespec="seconds")))
    c.commit(); c.close()

def get_history(hours=168):
    c = _conn()
    df = pd.read_sql(f"""SELECT * FROM inverter_data
        WHERE fetched_at >= datetime('now','-{hours} hours')
        ORDER BY fetched_at DESC""", c)
    c.close(); return df

def get_alert_log(limit=100):
    c = _conn()
    df = pd.read_sql(f"SELECT * FROM alert_log ORDER BY alerted_at DESC LIMIT {limit}", c)
    c.close(); return df