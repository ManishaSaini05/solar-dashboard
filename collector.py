#!/usr/bin/env python3
"""
collector.py — Hourly background data collector for Fractal Energy.
Run by GitHub Actions every 15 minutes. No Streamlit dependency.
Usage: python collector.py
Requires these environment variables (set in GitHub Secrets):
  NEON_DATABASE_URL, SOLIS_API_KEY, SOLIS_API_SECRET, SOLIS_BASE_URL,
  GROWATT_USERNAME, GROWATT_PASSWORD, RATE_PER_KWH
"""
import os
import sys
import time
import traceback
from datetime import datetime

# ── Project root in path ────────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# ── Timestamps ──────────────────────────────────────────────
snap_time = datetime.now()
snap_date = snap_time.strftime("%Y-%m-%d")
snap_hm   = snap_time.strftime("%H:%M")
snap_ts   = snap_time.isoformat(sep=" ", timespec="seconds")
snap_mon  = snap_time.strftime("%Y-%m")

print(f"[collector] ========================================")
print(f"[collector] Starting at {snap_ts}")
print(f"[collector] Python {sys.version}")

# ── Step 1: Verify all required secrets are present ─────────
REQUIRED = [
    "NEON_DATABASE_URL",
    "SOLIS_API_KEY",
    "SOLIS_API_SECRET",
]
missing = [k for k in REQUIRED if not os.environ.get(k)]
if missing:
    print(f"[collector] ❌ MISSING REQUIRED SECRETS: {missing}")
    print(f"[collector] Go to: GitHub repo → Settings → Secrets and variables → Actions")
    print(f"[collector] Add each missing secret as a New repository secret")
    sys.exit(1)

print(f"[collector] ✅ Required secrets present")
print(f"[collector] SOLIS_BASE_URL  = {os.environ.get('SOLIS_BASE_URL', 'not set — will use default')}")
print(f"[collector] GROWATT_USERNAME = {'set ✅' if os.environ.get('GROWATT_USERNAME') else 'not set (Growatt collection will be skipped)'}")
print(f"[collector] NEON_DATABASE_URL = set ✅")

# ── Step 2: Patch config so it reads from os.environ ────────
# config.py normally uses st.secrets which crashes outside Streamlit.
# We monkey-patch the module attributes directly before any import uses them.
def _patch_config():
    """
    Override config.py attributes with environment variable values.
    This runs before any utils module imports config, ensuring they all
    get the correct values from the environment rather than from st.secrets.
    """
    try:
        import config as _cfg
        _cfg.SOLIS_API_KEY    = os.environ.get("SOLIS_API_KEY",    "")
        _cfg.SOLIS_API_SECRET = os.environ.get("SOLIS_API_SECRET", "")
        _cfg.SOLIS_BASE_URL   = os.environ.get("SOLIS_BASE_URL",   "https://www.soliscloud.com:13333")
        _cfg.GROWATT_USERNAME = os.environ.get("GROWATT_USERNAME", "")
        _cfg.GROWATT_PASSWORD = os.environ.get("GROWATT_PASSWORD", "")
        _cfg.SUNGROW_APP_KEY    = os.environ.get("SUNGROW_APP_KEY",    "")
        _cfg.SUNGROW_ACCESS_KEY = os.environ.get("SUNGROW_ACCESS_KEY", "")
        _cfg.NEON_DATABASE_URL  = os.environ.get("NEON_DATABASE_URL",  "")
        try:
            _cfg.RATE_PER_KWH = float(os.environ.get("RATE_PER_KWH", "8.0"))
        except Exception:
            _cfg.RATE_PER_KWH = 8.0
        try:
            _cfg.REFRESH_INTERVAL_SECONDS = int(os.environ.get("REFRESH_INTERVAL_SECONDS", "300"))
        except Exception:
            _cfg.REFRESH_INTERVAL_SECONDS = 300
        _cfg.EMAIL_USER = os.environ.get("EMAIL_USER", "")
        _cfg.EMAIL_PASS = os.environ.get("EMAIL_PASS", "")
        _to = os.environ.get("TO_EMAILS", "")
        _cfg.TO_EMAILS = [e.strip() for e in _to.split(",") if e.strip()]
        print(f"[collector] ✅ config.py patched with environment variables")
    except ImportError:
        print(f"[collector] ⚠️  config.py not found — creating minimal config in memory")
        # Create a minimal config module on the fly
        import types
        _cfg = types.ModuleType("config")
        _cfg.SOLIS_API_KEY    = os.environ.get("SOLIS_API_KEY",    "")
        _cfg.SOLIS_API_SECRET = os.environ.get("SOLIS_API_SECRET", "")
        _cfg.SOLIS_BASE_URL   = os.environ.get("SOLIS_BASE_URL",   "https://www.soliscloud.com:13333")
        _cfg.GROWATT_USERNAME = os.environ.get("GROWATT_USERNAME", "")
        _cfg.GROWATT_PASSWORD = os.environ.get("GROWATT_PASSWORD", "")
        _cfg.SUNGROW_APP_KEY    = ""
        _cfg.SUNGROW_ACCESS_KEY = ""
        _cfg.NEON_DATABASE_URL  = os.environ.get("NEON_DATABASE_URL", "")
        _cfg.RATE_PER_KWH             = float(os.environ.get("RATE_PER_KWH", "8.0"))
        _cfg.REFRESH_INTERVAL_SECONDS = 300
        _cfg.EMAIL_USER = ""
        _cfg.EMAIL_PASS = ""
        _cfg.TO_EMAILS  = []
        sys.modules["config"] = _cfg
        print(f"[collector] ✅ Minimal config module created")
    except Exception as e:
        print(f"[collector] ❌ config patch failed: {e}")
        traceback.print_exc()
        sys.exit(1)

_patch_config()

# ── Step 3: DB connection using env var directly ─────────────
def get_conn():
    try:
        import psycopg2
    except ImportError:
        print("[collector] ❌ psycopg2 not installed — run: pip install psycopg2-binary")
        sys.exit(1)

    db_url = os.environ.get("NEON_DATABASE_URL")
    if not db_url:
        raise RuntimeError("NEON_DATABASE_URL not set in environment")

    # Neon requires sslmode=require
    if "sslmode" not in db_url:
        db_url += "?sslmode=require"

    try:
        conn = psycopg2.connect(db_url)
        print(f"[collector] ✅ Connected to Neon database")
        return conn
    except Exception as e:
        print(f"[collector] ❌ Database connection failed: {e}")
        raise

# ── Step 4: Ensure tables exist ─────────────────────────────
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
    cur.execute("""
        CREATE TABLE IF NOT EXISTS alert_log (
            id          SERIAL PRIMARY KEY,
            plant_name  TEXT,
            inverter_sn TEXT,
            brand       TEXT,
            issue       TEXT,
            alerted_at  TEXT,
            UNIQUE(plant_name, inverter_sn, issue, alerted_at)
        )
    """)
    conn.commit()
    cur.close()
    print("[collector] ✅ Tables verified")

# ── Step 5: Save helpers ─────────────────────────────────────
def save_intraday(conn, plant_name, date_str, time_hm, power_kw):
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO intraday_power (plant_name, date, time_hm, power_kw)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (plant_name, date, time_hm)
            DO UPDATE SET power_kw = EXCLUDED.power_kw
        """, (plant_name, date_str, time_hm, float(power_kw or 0)))
        conn.commit()
        cur.close()
    except Exception as e:
        conn.rollback()
        print(f"  [save_intraday] error for {plant_name}: {e}")

def save_daily_yield(conn, plant_name, date_str, energy_kwh):
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO daily_yield (plant_name, date, energy_kwh, saved_at)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (plant_name, date)
            DO UPDATE SET energy_kwh = EXCLUDED.energy_kwh,
                          saved_at   = EXCLUDED.saved_at
        """, (plant_name, date_str, float(energy_kwh or 0), snap_ts))
        conn.commit()
        cur.close()
    except Exception as e:
        conn.rollback()
        print(f"  [save_daily_yield] error for {plant_name}: {e}")

def save_monthly_yield(conn, plant_name, month_str, energy_kwh, source="collector"):
    try:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO report_monthly_yield (plant_name, month, source, energy_kwh, updated_at)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (plant_name, month)
            DO UPDATE SET energy_kwh = EXCLUDED.energy_kwh,
                          source     = EXCLUDED.source,
                          updated_at = EXCLUDED.updated_at
        """, (plant_name, month_str, source, float(energy_kwh or 0), snap_ts))
        conn.commit()
        cur.close()
    except Exception as e:
        conn.rollback()
        print(f"  [save_monthly_yield] error for {plant_name}: {e}")

# ── Step 6: Collect from Solis ───────────────────────────────
def collect_solis(conn):
    print(f"\n[collector] ── Solis ──────────────────────────────")

    solis_key = os.environ.get("SOLIS_API_KEY", "")
    if not solis_key:
        print("[collector] Solis API key not set — skipping")
        return

    try:
        from utils.solis_api import get_plants, fetch_all, _to_kwh
    except Exception as e:
        print(f"[collector] ❌ Cannot import solis_api: {e}")
        traceback.print_exc()
        return

    # Fetch plant list
    try:
        plants = get_plants()
        print(f"[collector] Solis plants found: {len(plants)}")
        if not plants:
            print("[collector] ⚠️  No plants returned — check SOLIS_API_KEY and SOLIS_API_SECRET")
            return
    except Exception as e:
        print(f"[collector] ❌ get_plants() failed: {e}")
        traceback.print_exc()
        return

    # Fetch live inverter readings
    try:
        records = fetch_all()
        print(f"[collector] Solis records fetched: {len(records)}")
    except Exception as e:
        print(f"[collector] ❌ fetch_all() failed: {e}")
        traceback.print_exc()
        records = []

    # Aggregate power and yield per plant
    plant_power = {}
    plant_kwh   = {}
    for r in records:
        pn = r.get("plant_name", "")
        if pn:
            plant_power[pn] = plant_power.get(pn, 0.0) + float(r.get("power_kw") or 0)
            plant_kwh[pn]   = plant_kwh.get(pn, 0.0)   + float(r.get("today_kwh") or 0)

    # Save intraday power point (one per 15-min run)
    saved_count = 0
    for pn, pwr in plant_power.items():
        save_intraday(conn, pn, snap_date, snap_hm, pwr)
        print(f"  ✅ {pn}: {pwr:.2f} kW @ {snap_hm}")
        saved_count += 1

    # Save daily yield (running total for today)
    for pn, kwh in plant_kwh.items():
        if kwh > 0:
            save_daily_yield(conn, pn, snap_date, kwh)

    # Save monthly yield from the accurate monthEnergy API field
    for p in plants:
        pn = p.get("stationName", "")
        if not pn:
            continue
        try:
            me_val = p.get("monthEnergy")
            me_str = p.get("monthEnergyStr", "kWh")
            if me_val is not None:
                mkwh = _to_kwh(me_val, me_str)
                if mkwh > 0:
                    save_monthly_yield(conn, pn, snap_mon, mkwh, source="solis_api")
                    print(f"  ✅ Monthly {pn}: {mkwh:.1f} kWh for {snap_mon}")
        except Exception as me_err:
            print(f"  ⚠️  Monthly save failed for {pn}: {me_err}")

    print(f"[collector] Solis complete — {saved_count} plants saved")

# ── Step 7: Collect from Growatt ─────────────────────────────
def collect_growatt(conn):
    print(f"\n[collector] ── Growatt ─────────────────────────────")

    if not os.environ.get("GROWATT_USERNAME"):
        print("[collector] GROWATT_USERNAME not set — skipping Growatt")
        return

    try:
        from utils.growatt_api import login, fetch_all, _get_plants, _chart_data
    except Exception as e:
        print(f"[collector] ❌ Cannot import growatt_api: {e}")
        traceback.print_exc()
        return

    try:
        if not login():
            print("[collector] ❌ Growatt login failed — check GROWATT_USERNAME and GROWATT_PASSWORD")
            return
        print("[collector] ✅ Growatt login successful")
    except Exception as e:
        print(f"[collector] ❌ Growatt login error: {e}")
        return

    try:
        records = fetch_all()
        print(f"[collector] Growatt records fetched: {len(records)}")
    except Exception as e:
        print(f"[collector] ❌ Growatt fetch_all() failed: {e}")
        traceback.print_exc()
        records = []

    plant_power = {}
    plant_kwh   = {}
    for r in records:
        pn = r.get("plant_name", "")
        if pn:
            plant_power[pn] = plant_power.get(pn, 0.0) + float(r.get("power_kw") or 0)
            plant_kwh[pn]   = plant_kwh.get(pn, 0.0)   + float(r.get("today_kwh") or 0)

    saved_count = 0
    for pn, pwr in plant_power.items():
        save_intraday(conn, pn, snap_date, snap_hm, pwr)
        print(f"  ✅ {pn}: {pwr:.2f} kW @ {snap_hm}")
        saved_count += 1

    for pn, kwh in plant_kwh.items():
        if kwh > 0:
            save_daily_yield(conn, pn, snap_date, kwh)

    # Save monthly yield from Growatt chart API
    try:
        plants = _get_plants()
        for p in plants:
            pid   = str(p.get("pId") or p.get("plantId", ""))
            pname = p.get("plantNameEncryption") or p.get("plantName", "")
            if not pid or not pname:
                continue
            try:
                data      = _chart_data(pid, "year",
                                        f"{snap_time.year}-01",
                                        f"{snap_time.year}-12")
                month_map = data.get("year", {})
                if snap_mon in month_map:
                    mkwh = float(month_map[snap_mon] or 0)
                    if mkwh > 0:
                        save_monthly_yield(conn, pname, snap_mon, mkwh, source="growatt_api")
                        print(f"  ✅ Monthly {pname}: {mkwh:.1f} kWh for {snap_mon}")
            except Exception as ge:
                print(f"  ⚠️  Monthly save failed for {pname}: {ge}")
    except Exception as e:
        print(f"  ⚠️  Growatt monthly fetch error: {e}")

    print(f"[collector] Growatt complete — {saved_count} plants saved")

# ── Step 8: Main ─────────────────────────────────────────────
if __name__ == "__main__":
    start = time.time()
    exit_code = 0

    try:
        conn = get_conn()
        init_tables(conn)
        collect_solis(conn)
        collect_growatt(conn)
        conn.close()
        elapsed = round(time.time() - start, 1)
        print(f"\n[collector] ✅ Completed in {elapsed}s at {datetime.now().strftime('%H:%M:%S')}")
    except Exception as e:
        print(f"\n[collector] ❌ FATAL ERROR: {e}")
        traceback.print_exc()
        exit_code = 1

    sys.exit(exit_code)