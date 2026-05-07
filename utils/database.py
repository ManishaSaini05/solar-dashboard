# utils/database.py — Neon PostgreSQL storage for inverter readings
import os
import pandas as pd
import psycopg2
from datetime import datetime, timedelta

try:
    from config import NEON_DATABASE_URL
except Exception:
    NEON_DATABASE_URL = os.environ.get("DATABASE_URL", "")


def _conn():
    """Open and return a new psycopg2 connection to Neon PostgreSQL."""
    url = NEON_DATABASE_URL or os.environ.get("DATABASE_URL", "")
    if not url:
        raise RuntimeError(
            "NEON_DATABASE_URL not set. Add it to .streamlit/secrets.toml:\n"
            '  NEON_DATABASE_URL = "postgresql://user:pass@host.neon.tech/db?sslmode=require"'
        )
    return psycopg2.connect(url)


def init_db():
    """Create all tables if they don't exist yet."""
    c = _conn()
    cur = c.cursor()
    stmts = [
        """
        CREATE TABLE IF NOT EXISTS inverter_data (
            id          SERIAL PRIMARY KEY,
            brand       TEXT,
            plant_name  TEXT,
            plant_id    TEXT,
            inverter_sn TEXT,
            power_kw    REAL,
            today_kwh   REAL,
            total_kwh   REAL,
            status      TEXT,
            temperature REAL,
            voltage     REAL,
            current_a   REAL,
            last_update TEXT,
            fetched_at  TEXT NOT NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS alert_log (
            id          SERIAL PRIMARY KEY,
            brand       TEXT,
            plant_name  TEXT,
            inverter_sn TEXT,
            issue       TEXT,
            alerted_at  TEXT NOT NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS intraday_power (
            id         SERIAL PRIMARY KEY,
            plant_name TEXT NOT NULL,
            date       TEXT NOT NULL,
            time_hm    TEXT NOT NULL,
            power_kw   REAL NOT NULL DEFAULT 0,
            UNIQUE(plant_name, date, time_hm)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS daily_yield (
            id         SERIAL PRIMARY KEY,
            plant_name TEXT NOT NULL,
            date       TEXT NOT NULL,
            energy_kwh REAL NOT NULL DEFAULT 0,
            saved_at   TEXT NOT NULL,
            UNIQUE(plant_name, date)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS monthly_yield (
            id         SERIAL PRIMARY KEY,
            plant_name TEXT NOT NULL,
            year_month TEXT NOT NULL,
            energy_kwh REAL NOT NULL DEFAULT 0,
            saved_at   TEXT NOT NULL,
            UNIQUE(plant_name, year_month)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS yearly_yield (
            id         SERIAL PRIMARY KEY,
            plant_name TEXT NOT NULL,
            year       TEXT NOT NULL,
            energy_kwh REAL NOT NULL DEFAULT 0,
            saved_at   TEXT NOT NULL,
            UNIQUE(plant_name, year)
        )
        """,
    ]
    for stmt in stmts:
        cur.execute(stmt)
    c.commit()
    cur.close()
    c.close()


def save_readings(records):
    if not records:
        return
    c = _conn()
    cur = c.cursor()
    now = datetime.now().isoformat(sep=" ", timespec="seconds")
    for r in records:
        fa = r.get("fetched_at") or now
        cur.execute(
            """
            INSERT INTO inverter_data
                (brand, plant_name, plant_id, inverter_sn,
                 power_kw, today_kwh, total_kwh, status,
                 temperature, voltage, current_a, last_update, fetched_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                r.get("brand"), r.get("plant_name"), r.get("plant_id"),
                r.get("inverter_sn"), r.get("power_kw"), r.get("today_kwh"),
                r.get("total_kwh"), r.get("status"), r.get("temperature"),
                r.get("voltage"), r.get("current_a"), r.get("last_update"), fa,
            ),
        )
    c.commit()
    cur.close()
    c.close()


def log_alert(brand, plant, sn, issue):
    c = _conn()
    cur = c.cursor()
    cur.execute(
        "INSERT INTO alert_log (brand, plant_name, inverter_sn, issue, alerted_at) "
        "VALUES (%s, %s, %s, %s, %s)",
        (brand, plant, sn, issue, datetime.now().isoformat(sep=" ", timespec="seconds")),
    )
    c.commit()
    cur.close()
    c.close()


def get_history(hours=168):
    threshold = (datetime.now() - timedelta(hours=hours)).strftime("%Y-%m-%d %H:%M:%S")
    c = _conn()
    df = pd.read_sql(
        "SELECT * FROM inverter_data WHERE fetched_at >= %s ORDER BY fetched_at DESC",
        c, params=(threshold,),
    )
    c.close()
    return df


def get_alert_log(limit=100):
    c = _conn()
    df = pd.read_sql(
        f"SELECT * FROM alert_log ORDER BY alerted_at DESC LIMIT {int(limit)}",
        c,
    )
    c.close()
    return df


# ── Intraday power ────────────────────────────────────────────────────────────

def save_intraday(plant_name, date_str, points):
    if not points:
        return
    c = _conn()
    cur = c.cursor()
    for p in points:
        cur.execute(
            """
            INSERT INTO intraday_power (plant_name, date, time_hm, power_kw)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (plant_name, date, time_hm)
            DO UPDATE SET power_kw = EXCLUDED.power_kw
            """,
            (plant_name, date_str, p["time_hm"], float(p["power_kw"] or 0)),
        )
    c.commit()
    cur.close()
    c.close()


def get_intraday(plant_name, date_str):
    c = _conn()
    df = pd.read_sql(
        "SELECT time_hm, power_kw FROM intraday_power "
        "WHERE plant_name=%s AND date=%s ORDER BY time_hm",
        c, params=(plant_name, date_str),
    )
    c.close()
    return df


# ── Daily yield ───────────────────────────────────────────────────────────────

def save_daily_yield(plant_name, date_str, energy_kwh):
    c = _conn()
    cur = c.cursor()
    cur.execute(
        """
        INSERT INTO daily_yield (plant_name, date, energy_kwh, saved_at)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (plant_name, date)
        DO UPDATE SET energy_kwh = EXCLUDED.energy_kwh,
                      saved_at   = EXCLUDED.saved_at
        """,
        (plant_name, date_str, float(energy_kwh or 0),
         datetime.now().isoformat(sep=" ", timespec="seconds")),
    )
    c.commit()
    cur.close()
    c.close()


def get_daily_yield(plant_name, days=30):
    threshold = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    c = _conn()
    df = pd.read_sql(
        "SELECT date, energy_kwh FROM daily_yield "
        "WHERE plant_name=%s AND date >= %s ORDER BY date",
        c, params=(plant_name, threshold),
    )
    c.close()
    return df


def get_daily_yield_month(plant_name, year_month):
    c = _conn()
    df = pd.read_sql(
        "SELECT date, energy_kwh FROM daily_yield "
        "WHERE plant_name=%s AND date LIKE %s ORDER BY date",
        c, params=(plant_name, f"{year_month}-%"),
    )
    c.close()
    return df


# ── Monthly yield ─────────────────────────────────────────────────────────────

def save_monthly_yield(plant_name, year_month, energy_kwh):
    c = _conn()
    cur = c.cursor()
    cur.execute(
        """
        INSERT INTO monthly_yield (plant_name, year_month, energy_kwh, saved_at)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (plant_name, year_month)
        DO UPDATE SET energy_kwh = EXCLUDED.energy_kwh,
                      saved_at   = EXCLUDED.saved_at
        """,
        (plant_name, year_month, float(energy_kwh or 0),
         datetime.now().isoformat(sep=" ", timespec="seconds")),
    )
    c.commit()
    cur.close()
    c.close()


def get_monthly_yield(plant_name, year_str=None):
    c = _conn()
    if year_str:
        df = pd.read_sql(
            "SELECT year_month, energy_kwh FROM monthly_yield "
            "WHERE plant_name=%s AND year_month LIKE %s ORDER BY year_month",
            c, params=(plant_name, f"{year_str}-%"),
        )
    else:
        df = pd.read_sql(
            "SELECT year_month, energy_kwh FROM monthly_yield "
            "WHERE plant_name=%s ORDER BY year_month",
            c, params=(plant_name,),
        )
    c.close()
    return df


def get_all_monthly_yield(year_str=None):
    c = _conn()
    if year_str:
        df = pd.read_sql(
            "SELECT year_month, SUM(energy_kwh) AS energy_kwh FROM monthly_yield "
            "WHERE year_month LIKE %s GROUP BY year_month ORDER BY year_month",
            c, params=(f"{year_str}-%",),
        )
    else:
        df = pd.read_sql(
            "SELECT year_month, SUM(energy_kwh) AS energy_kwh FROM monthly_yield "
            "GROUP BY year_month ORDER BY year_month",
            c,
        )
    c.close()
    return df


# ── Yearly yield ──────────────────────────────────────────────────────────────

def save_yearly_yield(plant_name, year, energy_kwh):
    c = _conn()
    cur = c.cursor()
    cur.execute(
        """
        INSERT INTO yearly_yield (plant_name, year, energy_kwh, saved_at)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (plant_name, year)
        DO UPDATE SET energy_kwh = EXCLUDED.energy_kwh,
                      saved_at   = EXCLUDED.saved_at
        """,
        (plant_name, str(year), float(energy_kwh or 0),
         datetime.now().isoformat(sep=" ", timespec="seconds")),
    )
    c.commit()
    cur.close()
    c.close()


def get_yearly_yield(plant_name):
    c = _conn()
    df = pd.read_sql(
        "SELECT year, energy_kwh FROM yearly_yield "
        "WHERE plant_name=%s ORDER BY year",
        c, params=(plant_name,),
    )
    c.close()
    return df


def get_all_yearly_yield():
    c = _conn()
    df = pd.read_sql(
        "SELECT year, SUM(energy_kwh) AS energy_kwh FROM yearly_yield "
        "GROUP BY year ORDER BY year",
        c,
    )
    c.close()
    return df
