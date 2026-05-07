import streamlit as st


def _s(key, default=""):
    try:
        return st.secrets[key]
    except Exception:
        return default


# ── Solis ────────────────────────────────────────────────────
SOLIS_API_KEY    = _s("SOLIS_API_KEY",    "")
SOLIS_API_SECRET = _s("SOLIS_API_SECRET", "")
SOLIS_BASE_URL   = _s("SOLIS_BASE_URL",   "https://www.soliscloud.com:13333")

# ── Growatt ──────────────────────────────────────────────────
GROWATT_USERNAME = _s("GROWATT_USERNAME", "")
GROWATT_PASSWORD = _s("GROWATT_PASSWORD", "")
GROWATT_BASE_URL = _s("GROWATT_BASE_URL", "https://oss.growatt.com")

# ── Sungrow ──────────────────────────────────────────────────
SUNGROW_APP_KEY    = _s("SUNGROW_APP_KEY",    "")
SUNGROW_ACCESS_KEY = _s("SUNGROW_ACCESS_KEY", "")
SUNGROW_BASE_URL   = _s("SUNGROW_BASE_URL",   "https://gateway.isolarcloud.com.hk")

# ── Email Alerts ─────────────────────────────────────────────
EMAIL_USER     = _s("EMAIL_USER",     "")
EMAIL_PASSWORD = _s("EMAIL_PASSWORD", "")
_to_raw        = _s("TO_EMAILS", "")
TO_EMAILS      = [e.strip() for e in _to_raw.split(",") if e.strip()]

# ── App Settings ─────────────────────────────────────────────
REFRESH_INTERVAL_SECONDS = int(_s("REFRESH_INTERVAL_SECONDS", "300"))
DB_PATH                  = _s("DB_PATH", "data/solar_data.db")  # kept for legacy reference

# ── Neon PostgreSQL ───────────────────────────────────────────
NEON_DATABASE_URL = _s("NEON_DATABASE_URL", "")
try:
    RATE_PER_KWH = float(_s("RATE_PER_KWH", "8.0"))
except Exception:
    RATE_PER_KWH = 8.0
