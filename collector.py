#!/usr/bin/env python3
"""
collector.py — Hourly background data collector for Fractal Energy.
Run by GitHub Actions every hour. No Streamlit dependency.
Usage: python collector.py
Requires: NEON_DATABASE_URL, SOLIS_API_KEY, SOLIS_API_SECRET, etc. in environment.
"""
import os
import sys
import time
from datetime import datetime

# ── Make sure project root is in path ──────────────────────
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

snap_time = datetime.now()
snap_date = snap_time.strftime("%Y-%m-%d")
snap_hm   = snap_time.strftime("%H:%M")
snap_ts   = snap_time.isoformat(sep=" ", timespec="seconds")
snap_mon  = snap_time.strftime("%Y-%m")

print(f"[collector] Starting at {snap_ts}")

# ── DB connection ───────────────────────────────────────────
def get_conn():
    import psycopg2
    db_url = os.environ.get("NEON_DATABASE_URL")
    if not db_url:
        raise RuntimeError("NEON_DATABASE_URL not set")
    return psycopg2.connect(db_url)

# ── Ensure tables exist ─────────────────────────────────────
def init_tables(conn):
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS intraday_power (
            id         SERIAL PRIMARY KEY,
            plant_name TEXT NOT NULL,
            date       TEXT NOT NULL,
            time_hm    TEXT NOT NULL,
            power_kw   REAL NOT NULL DEFAULT 0,
            UNIQUE(plant_name, date, time_hm)
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS daily_yield (
            id         SERIAL PRIMARY KEY,
            plant_name TEXT NOT NULL,
            date       TEXT NOT NULL,
            energy_kwh REAL NOT NULL DEFAULT 0,
            saved_at   TEXT,
            UNIQUE(plant_name, date)
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS report_monthly_yield (
            id         SERIAL PRIMARY KEY,
            plant_name TEXT NOT NULL,
            month      TEXT NOT NULL,
            source     TEXT NOT NULL DEFAULT 'collector',
            energy_kwh REAL NOT NULL DEFAULT 0,
            updated_at TEXT NOT NULL,
            UNIQUE(plant_name, month)
        )
    """)
    conn.commit()
    cur.close()
    print("[collector] Tables verified")

# ── Save helpers ────────────────────────────────────────────
def save_intraday(conn, plant_name, date_str, time_hm, power_kw):
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO intraday_power (plant_name, date, time_hm, power_kw)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (plant_name, date, time_hm) DO UPDATE SET power_kw = EXCLUDED.power_kw
    """, (plant_name, date_str, time_hm, float(power_kw or 0)))
    conn.commit()
    cur.close()

def save_daily_yield(conn, plant_name, date_str, energy_kwh):
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO daily_yield (plant_name, date, energy_kwh, saved_at)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (plant_name, date) DO UPDATE SET energy_kwh = EXCLUDED.energy_kwh, saved_at = EXCLUDED.saved_at
    """, (plant_name, date_str, float(energy_kwh or 0), snap_ts))
    conn.commit()
    cur.close()

def save_monthly_yield(conn, plant_name, month_str, energy_kwh):
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO report_monthly_yield (plant_name, month, source, energy_kwh, updated_at)
        VALUES (%s, %s, 'collector', %s, %s)
        ON CONFLICT (plant_name, month) DO UPDATE
        SET energy_kwh = EXCLUDED.energy_kwh, updated_at = EXCLUDED.updated_at
    """, (plant_name, month_str, float(energy_kwh or 0), snap_ts))
    conn.commit()
    cur.close()

# ── Fetch from Solis ────────────────────────────────────────
def collect_solis(conn):
    print("[collector] Fetching Solis...")
    try:
        from utils.solis_api import get_plants, fetch_all, _to_kwh
        plants = get_plants()
        records = fetch_all()

        # Aggregate power per plant
        plant_power = {}
        plant_kwh   = {}
        for r in records:
            pn = r.get("plant_name", "")
            if pn:
                plant_power[pn] = plant_power.get(pn, 0.0) + float(r.get("power_kw") or 0)
                plant_kwh[pn]   = plant_kwh.get(pn, 0.0)   + float(r.get("today_kwh") or 0)

        # Save intraday power point
        for pn, pwr in plant_power.items():
            save_intraday(conn, pn, snap_date, snap_hm, pwr)
            print(f"  [Solis] {pn}: {pwr:.2f} kW saved @ {snap_hm}")

        # Save daily yield
        for pn, kwh in plant_kwh.items():
            if kwh > 0:
                save_daily_yield(conn, pn, snap_date, kwh)

        # Save monthly yield from API (accurate monthEnergy field)
        for p in plants:
            pn = p.get("stationName", "")
            if pn and p.get("monthEnergy") is not None:
                mkwh = _to_kwh(p.get("monthEnergy", 0), p.get("monthEnergyStr", "kWh"))
                if mkwh > 0:
                    save_monthly_yield(conn, pn, snap_mon, mkwh)

        print(f"[collector] Solis done — {len(plant_power)} plants")
    except Exception as e:
        import traceback
        print(f"[collector] Solis ERROR: {e}")
        traceback.print_exc()

# ── Fetch from Growatt ──────────────────────────────────────
def collect_growatt(conn):
    print("[collector] Fetching Growatt...")
    try:
        from utils.growatt_api import login, fetch_all, _get_plants, _chart_data

        if not login():
            print("[collector] Growatt login failed")
            return

        records = fetch_all()

        plant_power = {}
        plant_kwh   = {}
        for r in records:
            pn = r.get("plant_name", "")
            if pn:
                plant_power[pn] = plant_power.get(pn, 0.0) + float(r.get("power_kw") or 0)
                plant_kwh[pn]   = plant_kwh.get(pn, 0.0)   + float(r.get("today_kwh") or 0)

        for pn, pwr in plant_power.items():
            save_intraday(conn, pn, snap_date, snap_hm, pwr)
            print(f"  [Growatt] {pn}: {pwr:.2f} kW saved @ {snap_hm}")

        for pn, kwh in plant_kwh.items():
            if kwh > 0:
                save_daily_yield(conn, pn, snap_date, kwh)

        # Monthly yield from Growatt chart API
        plants = _get_plants()
        for p in plants:
            pid   = str(p.get("pId") or p.get("plantId", ""))
            pname = p.get("plantNameEncryption") or p.get("plantName", "")
            if not pid or not pname:
                continue
            try:
                data      = _chart_data(pid, "year", f"{snap_time.year}-01", f"{snap_time.year}-12")
                month_map = data.get("year", {})
                if snap_mon in month_map:
                    mkwh = float(month_map[snap_mon] or 0)
                    if mkwh > 0:
                        save_monthly_yield(conn, pname, snap_mon, mkwh)
            except Exception as _ge:
                print(f"  [Growatt monthly] {pname}: {_ge}")

        print(f"[collector] Growatt done — {len(plant_power)} plants")
    except Exception as e:
        import traceback
        print(f"[collector] Growatt ERROR: {e}")
        traceback.print_exc()

# ── Main ────────────────────────────────────────────────────
if __name__ == "__main__":
    try:
        conn = get_conn()
        init_tables(conn)
        collect_solis(conn)
        collect_growatt(conn)
        conn.close()
        print(f"[collector] Completed at {datetime.now().strftime('%H:%M:%S')}")
    except Exception as e:
        import traceback
        print(f"[collector] FATAL ERROR: {e}")
        traceback.print_exc()
        sys.exit(1)
