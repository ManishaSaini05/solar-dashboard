import streamlit as st
import plotly.graph_objects as go
import random
import math

try:
    from config import RATE_PER_KWH, REFRESH_INTERVAL_SECONDS
except Exception:
    RATE_PER_KWH = 8.0
    REFRESH_INTERVAL_SECONDS = 300

st.set_page_config(
    page_title="Fractal Energy · Solar Monitor",
    page_icon="☀️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Hide sidebar completely */
[data-testid="stSidebar"],
[data-testid="stSidebarCollapsedControl"],
[data-testid="collapsedControl"] {
    display: none !important;
}
section[data-testid="stSidebar"] { display: none !important; }

/* Remove default top padding */
.block-container { padding-top: 0 !important; }

/* ── Top nav ── */
.tnav {
    background: #0D2B45;
    display: flex;
    align-items: center;
    padding: 0 28px;
    height: 56px;
    gap: 4px;
    position: sticky;
    top: 0;
    z-index: 999;
}
.tnav .brand {
    font-size: 17px;
    font-weight: 700;
    color: #F5A623;
    margin-right: 32px;
    white-space: nowrap;
}
.tnav .brand span { color: #fff; font-weight: 400; font-size: 13px; margin-left: 6px; }
.ntab {
    color: #9DB5C8;
    text-decoration: none;
    font-size: 13.5px;
    padding: 6px 16px;
    border-radius: 6px;
    transition: all .15s;
}
.ntab:hover { color: #fff; background: rgba(255,255,255,.08); }
.ntab.act { color: #F5A623; background: rgba(245,166,35,.12); font-weight: 600; }
.tnav .spacer { flex: 1; }
.bell { position: relative; margin-right: 8px; cursor: pointer; }
.bell svg { fill: #9DB5C8; }
.bell .badge {
    position: absolute;
    top: -4px; right: -4px;
    background: #C85A00;
    color: #fff;
    font-size: 10px;
    font-weight: 700;
    border-radius: 50%;
    width: 16px; height: 16px;
    display: flex; align-items: center; justify-content: center;
}
.avatar {
    width: 32px; height: 32px;
    border-radius: 50%;
    background: #1A6FA8;
    color: #fff;
    font-weight: 700;
    font-size: 13px;
    display: flex; align-items: center; justify-content: center;
    cursor: pointer;
}

/* ── KPI cards ── */
.krow { display: flex; gap: 16px; margin: 20px 0 8px; }
.kcard {
    flex: 1;
    background: #fff;
    border: 1px solid #E5EBF0;
    border-radius: 12px;
    padding: 20px 22px;
    box-shadow: 0 1px 4px rgba(0,0,0,.04);
}
.kcard .klabel { font-size: 12px; color: #6B7E8F; text-transform: uppercase; letter-spacing: .6px; }
.kcard .kval { font-size: 28px; font-weight: 700; color: #0D2B45; margin: 6px 0 4px; }
.kcard .ktag { font-size: 12px; }
.kcard .ktag.up { color: #2E9B5F; }
.kcard .ktag.dn { color: #C85A00; }
.kcard.amb { border-top: 3px solid #F5A623; }

/* ── Chart box ── */
.cbox {
    background: #fff;
    border: 1px solid #E5EBF0;
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 1px 4px rgba(0,0,0,.04);
    margin-bottom: 16px;
}
.cbox h4 { margin: 0 0 14px; font-size: 14px; color: #0D2B45; font-weight: 600; }

/* ── Data table ── */
.dtbl { width: 100%; border-collapse: collapse; font-size: 13.5px; }
.dtbl th { background: #F0F5FA; color: #4A6278; font-size: 11.5px; text-transform: uppercase;
           letter-spacing: .5px; padding: 10px 14px; text-align: left; }
.dtbl td { padding: 10px 14px; border-bottom: 1px solid #EEF2F6; color: #1C3040; }
.dtbl tr:hover td { background: #F8FAFB; }
.dtbl a { color: #1A6FA8; text-decoration: none; font-weight: 600; }
.dtbl a:hover { text-decoration: underline; }

/* ── Status badges ── */
.bg-gr { background: #E6F5EE; color: #1E7B4A; padding: 3px 10px; border-radius: 12px; font-size: 12px; font-weight: 600; }
.bg-am { background: #FEF3E2; color: #A05A00; padding: 3px 10px; border-radius: 12px; font-size: 12px; font-weight: 600; }
.bg-rd { background: #FDEAEA; color: #B91C1C; padding: 3px 10px; border-radius: 12px; font-size: 12px; font-weight: 600; }
.bg-bl { background: #E8F1FA; color: #1A6FA8; padding: 3px 10px; border-radius: 12px; font-size: 12px; font-weight: 600; }

/* ── Alarm cards ── */
.almc {
    background: #fff;
    border: 1px solid #E5EBF0;
    border-radius: 10px;
    padding: 14px 18px;
    margin-bottom: 10px;
    border-left: 4px solid #ccc;
}
.almc.critical { border-left-color: #B91C1C; }
.almc.warning  { border-left-color: #F5A623; }
.almc.info     { border-left-color: #1A6FA8; }
.almc.resolved { border-left-color: #2E9B5F; opacity: .7; }
.almc .atitle  { font-weight: 600; font-size: 14px; color: #1C3040; }
.almc .ameta   { font-size: 12px; color: #6B7E8F; margin-top: 3px; }

/* ── Fault banner ── */
.fbanner {
    background: #FEF3E2;
    border: 1px solid #F5A623;
    border-radius: 8px;
    padding: 10px 16px;
    font-size: 13px;
    color: #7A4500;
    margin: 12px 0;
}

/* ── Stat cards (all-plants bottom row) ── */
.scrow { display: flex; gap: 16px; margin-top: 24px; }
.scard { flex: 1; border-radius: 12px; padding: 18px 22px; }
.scard.gr { background: #E6F5EE; border: 1px solid #B4E0C8; }
.scard.am { background: #FEF3E2; border: 1px solid #F5D09A; }
.scard.rd { background: #FDEAEA; border: 1px solid #F4AEAE; }
.scard .sv { font-size: 26px; font-weight: 700; margin: 4px 0; }
.scard.gr .sv { color: #1E7B4A; }
.scard.am .sv { color: #A05A00; }
.scard.rd .sv { color: #B91C1C; }
.scard .sl { font-size: 12px; color: #4A6278; text-transform: uppercase; letter-spacing: .5px; }

/* ── Login column coloring ── */
[data-testid="column"]:first-child {
    background: #0D2B45 !important;
    border-radius: 0 !important;
    padding: 60px 40px !important;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
}
[data-testid="column"]:last-child {
    background: #ffffff !important;
    padding: 60px 48px !important;
    min-height: 100vh;
}
/* ── Filter pills ── */
div[data-testid="stHorizontalBlock"] div[role="radiogroup"] label {
    border: 1.5px solid #CBD8E3;
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 13px;
    cursor: pointer;
    color: #4A6278;
    background: #fff;
}
div[data-testid="stHorizontalBlock"] div[role="radiogroup"] label[data-baseweb="radio"]:has(input:checked) {
    background: #0D2B45;
    color: #fff;
    border-color: #0D2B45;
}
</style>
""", unsafe_allow_html=True)

# ── Mock data ─────────────────────────────────────────────────────────────────
MOCK_PLANTS = [
    {"id":"P01","name":"Andheri Solar Farm","brand":"Growatt","capacity":250,"location":"Mumbai, MH","status":"online","power_kw":187.4,"today_kwh":1124.2,"total_mwh":4231.8,"n_inv":10,"n_online":10},
    {"id":"P02","name":"Bandra Rooftop","brand":"Solis","capacity":80,"location":"Mumbai, MH","status":"online","power_kw":61.2,"today_kwh":367.4,"total_mwh":1382.5,"n_inv":4,"n_online":4},
    {"id":"P03","name":"Pune Industrial","brand":"Sungrow","capacity":500,"location":"Pune, MH","status":"warning","power_kw":312.6,"today_kwh":1875.4,"total_mwh":7843.2,"n_inv":20,"n_online":18},
    {"id":"P04","name":"Nashik Wind-Solar","brand":"Growatt","capacity":120,"location":"Nashik, MH","status":"online","power_kw":98.4,"today_kwh":590.4,"total_mwh":2214.7,"n_inv":6,"n_online":6},
    {"id":"P05","name":"Aurangabad Plant","brand":"Solis","capacity":180,"location":"Aurangabad, MH","status":"fault","power_kw":0.0,"today_kwh":48.2,"total_mwh":1987.6,"n_inv":8,"n_online":2},
    {"id":"P06","name":"Nagpur Solar Hub","brand":"Sungrow","capacity":320,"location":"Nagpur, MH","status":"online","power_kw":256.8,"today_kwh":1540.8,"total_mwh":5621.4,"n_inv":14,"n_online":14},
    {"id":"P07","name":"Solapur Field","brand":"Growatt","capacity":150,"location":"Solapur, MH","status":"online","power_kw":127.5,"today_kwh":765.0,"total_mwh":3102.9,"n_inv":6,"n_online":6},
    {"id":"P08","name":"Kolhapur Agri-Solar","brand":"Solis","capacity":90,"location":"Kolhapur, MH","status":"warning","power_kw":54.3,"today_kwh":325.8,"total_mwh":1245.3,"n_inv":4,"n_online":3},
    {"id":"P09","name":"Thane Commercial","brand":"Sungrow","capacity":60,"location":"Thane, MH","status":"online","power_kw":51.2,"today_kwh":307.2,"total_mwh":987.6,"n_inv":3,"n_online":3},
    {"id":"P10","name":"Navi Mumbai Hub","brand":"Growatt","capacity":200,"location":"Navi Mumbai, MH","status":"online","power_kw":168.4,"today_kwh":1010.4,"total_mwh":3876.5,"n_inv":8,"n_online":8},
    {"id":"P11","name":"Vasai Rooftop","brand":"Solis","capacity":45,"location":"Vasai, MH","status":"fault","power_kw":0.0,"today_kwh":12.6,"total_mwh":456.8,"n_inv":2,"n_online":0},
]

MOCK_ALARMS = [
    {"id":"A01","plant_id":"P05","plant_name":"Aurangabad Plant","severity":"critical","status":"active","title":"Inverter Offline — Units 3,4,5,6,7,8","ts":"2026-05-07 06:14"},
    {"id":"A02","plant_id":"P11","plant_name":"Vasai Rooftop","severity":"critical","status":"active","title":"All Inverters Offline","ts":"2026-05-07 05:52"},
    {"id":"A03","plant_id":"P03","plant_name":"Pune Industrial","severity":"warning","status":"active","title":"Grid Voltage High — Inverter 12,15","ts":"2026-05-07 08:30"},
    {"id":"A04","plant_id":"P08","plant_name":"Kolhapur Agri-Solar","severity":"warning","status":"active","title":"Communication Lost — Inverter 4","ts":"2026-05-07 07:45"},
    {"id":"A05","plant_id":"P02","plant_name":"Bandra Rooftop","severity":"info","status":"active","title":"Scheduled Maintenance Window Tomorrow","ts":"2026-05-06 17:00"},
    {"id":"A06","plant_id":"P01","plant_name":"Andheri Solar Farm","severity":"info","status":"active","title":"Firmware Update Available","ts":"2026-05-05 10:22"},
    {"id":"A07","plant_id":"P06","plant_name":"Nagpur Solar Hub","severity":"warning","status":"resolved","title":"String Underperformance — Array C","ts":"2026-05-04 13:15"},
    {"id":"A08","plant_id":"P04","plant_name":"Nashik Wind-Solar","severity":"critical","status":"resolved","title":"DC Isolation Fault — Inverter 2","ts":"2026-05-03 09:48"},
    {"id":"A09","plant_id":"P07","plant_name":"Solapur Field","severity":"info","status":"resolved","title":"Inverter Restarted After Update","ts":"2026-05-02 08:00"},
]

def mock_hourly():
    base = [0,0,0,0,0,0,2.1,8.4,15.2,22.8,28.6,32.1,34.5,33.8,30.2,24.7,17.3,9.6,3.4,0.8,0,0,0,0]
    return [max(0, v + random.uniform(-1.5, 1.5)) for v in base]

def mock_monthly():
    return [random.uniform(120, 320) for _ in range(12)]

def mock_annual():
    return {y: [random.uniform(100, 350) for _ in range(12)] for y in [2023, 2024, 2025]}

def mock_daily():
    return [random.uniform(200, 600) for _ in range(30)]

def mock_inverters(plant):
    n = plant["n_inv"]
    rows = []
    for i in range(1, n + 1):
        online = i <= plant["n_online"]
        rows.append({
            "num": i,
            "status": "Online" if online else "Fault",
            "power": round(random.uniform(20, 40), 1) if online else 0.0,
            "today": round(random.uniform(120, 250), 1) if online else 0.0,
            "temp": round(random.uniform(38, 55), 1) if online else "--",
            "eff": round(random.uniform(95.2, 98.8), 1) if online else "--",
        })
    return rows

# ── Session state ─────────────────────────────────────────────────────────────
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = ""
if "sel_plant" not in st.session_state:
    st.session_state.sel_plant = "P01"

# ── Routing ───────────────────────────────────────────────────────────────────
_page = st.query_params.get("page", "plants")
_pid_param = st.query_params.get("plant", "")
if _pid_param:
    st.session_state.sel_plant = _pid_param

_pid = st.session_state.sel_plant
_plant = next((p for p in MOCK_PLANTS if p["id"] == _pid), MOCK_PLANTS[0])

# ── Top nav helper ────────────────────────────────────────────────────────────
def topnav(active: str):
    n_active = sum(1 for a in MOCK_ALARMS if a["status"] == "active")
    tabs = [
        ("dashboard", "Dashboard"),
        ("reports",   "Reports"),
        ("alarms",    f"Alarms"),
        ("settings",  "Settings"),
    ]
    links = ""
    for key, label in tabs:
        cls = "ntab act" if active == key else "ntab"
        links += f'<a class="{cls}" href="?page={key}&plant={_pid}">{label}</a>'
    badge_html = f'<span class="badge">{n_active}</span>' if n_active else ""
    st.markdown(f"""
    <div class="tnav">
      <div class="brand">☀ Fractal Energy <span>Solar Monitor</span></div>
      {links}
      <div class="spacer"></div>
      <div class="bell">
        <svg width="20" height="20" viewBox="0 0 24 24"><path d="M12 2a7 7 0 0 1 7 7v3.586l1.707 1.707A1 1 0 0 1 20 16H4a1 1 0 0 1-.707-1.707L5 12.586V9a7 7 0 0 1 7-7zm0 18a2 2 0 0 1-2-2h4a2 2 0 0 1-2 2z"/></svg>
        {badge_html}
      </div>
      <div class="avatar">MS</div>
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  LOGIN
# ══════════════════════════════════════════════════════════════════════════════
if not st.session_state.logged_in:
    left, right = st.columns(2)
    with left:
        st.markdown("""
        <div style="text-align:center;color:#fff;padding-top:40px;">
          <div style="font-size:64px;margin-bottom:16px;">☀️</div>
          <div style="font-size:26px;font-weight:700;color:#F5A623;line-height:1.2;">Fractal Energy</div>
          <div style="font-size:15px;color:#9DB5C8;margin-top:8px;">Unified Inverter Monitoring</div>
          <div style="margin-top:40px;font-size:13px;color:#5A7A93;line-height:1.8;">
            Real-time visibility across<br>your entire solar portfolio
          </div>
        </div>
        """, unsafe_allow_html=True)
    with right:
        st.markdown("<div style='height:80px'></div>", unsafe_allow_html=True)
        st.markdown("### Sign in to your account")
        st.markdown("<div style='color:#6B7E8F;font-size:14px;margin-bottom:24px;'>Monitor your solar plants in real time</div>", unsafe_allow_html=True)
        email = st.text_input("Email address", placeholder="you@fractalenergy.in", key="li_email")
        password = st.text_input("Password", type="password", placeholder="••••••••", key="li_pass")
        remember = st.checkbox("Remember me for 30 days")
        col_btn, col_fp = st.columns([2, 1])
        with col_btn:
            login_btn = st.button("Sign In", type="primary", use_container_width=True)
        with col_fp:
            st.markdown("<div style='padding-top:8px;font-size:13px;color:#1A6FA8;cursor:pointer;'>Forgot password?</div>", unsafe_allow_html=True)

        if login_btn:
            valid = (
                (email == "admin" and password == "1234") or
                (email == "manisha.s@fractalenergy.in" and password == "fractal123")
            )
            if valid:
                st.session_state.logged_in = True
                st.session_state.user = email
                st.query_params["page"] = "plants"
                st.rerun()
            else:
                st.error("Invalid credentials. Try admin / 1234 or manisha.s@fractalenergy.in / fractal123")
    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
#  ALL PLANTS
# ══════════════════════════════════════════════════════════════════════════════
elif _page == "plants":
    total_mwp = sum(p["capacity"] for p in MOCK_PLANTS) / 1000
    st.markdown(f"""
    <div style="background:#0D2B45;padding:18px 32px 14px;display:flex;align-items:center;gap:12px;">
      <span style="font-size:22px;">☀️</span>
      <span style="font-size:18px;font-weight:700;color:#F5A623;">Fractal Energy</span>
      <span style="color:#9DB5C8;font-size:13px;margin-left:4px;">Solar Monitor</span>
      <div style="flex:1"></div>
      <div class="avatar" style="width:32px;height:32px;border-radius:50%;background:#1A6FA8;color:#fff;font-weight:700;font-size:13px;display:flex;align-items:center;justify-content:center;">MS</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='padding:0 24px;'>", unsafe_allow_html=True)
    st.markdown(f"## All Plants")
    st.markdown(f"<div style='color:#6B7E8F;font-size:14px;margin-top:-12px;margin-bottom:20px;'>Total fleet capacity: <b>{total_mwp:.2f} MWp</b></div>", unsafe_allow_html=True)

    sc1, sc2, sc3 = st.columns([3, 2, 1])
    with sc1:
        search = st.text_input("", placeholder="🔍  Search plants by name or location…", label_visibility="collapsed")
    with sc2:
        brand_filter = st.selectbox("", ["All Brands", "Growatt", "Solis", "Sungrow"], label_visibility="collapsed")
    with sc3:
        st.button("+ Add Plant", type="primary", use_container_width=True)

    filtered = MOCK_PLANTS
    if search:
        q = search.lower()
        filtered = [p for p in filtered if q in p["name"].lower() or q in p["location"].lower()]
    if brand_filter != "All Brands":
        filtered = [p for p in filtered if p["brand"] == brand_filter]

    def status_dot(s):
        c = {"online":"#2E9B5F","warning":"#F5A623","fault":"#B91C1C"}.get(s,"#9DB5C8")
        return f'<span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:{c};margin-right:6px;"></span>'

    def status_badge(s):
        cls = {"online":"bg-gr","warning":"bg-am","fault":"bg-rd"}.get(s,"bg-bl")
        label = s.capitalize()
        return f'<span class="{cls}">{label}</span>'

    def power_color(p, status):
        if status == "fault": return f'<span style="color:#B91C1C;font-weight:600;">{p:.1f} kW</span>'
        if status == "warning": return f'<span style="color:#A05A00;font-weight:600;">{p:.1f} kW</span>'
        return f'<span style="color:#1E7B4A;font-weight:600;">{p:.1f} kW</span>'

    rows_html = ""
    for p in filtered:
        rows_html += f"""
        <tr>
          <td>{status_dot(p['status'])}<a href="?page=dashboard&plant={p['id']}">{p['name']}</a></td>
          <td>{p['brand']}</td>
          <td>{p['capacity']} kWp</td>
          <td>{power_color(p['power_kw'], p['status'])}</td>
          <td>{p['today_kwh']:,.1f} kWh</td>
          <td>{status_badge(p['status'])}</td>
          <td style="color:#9DB5C8;font-size:18px;cursor:pointer;">⋯</td>
        </tr>"""

    st.markdown(f"""
    <div class="cbox" style="margin-top:8px;">
      <table class="dtbl">
        <thead><tr>
          <th>Plant Name</th><th>Brand</th><th>Capacity</th>
          <th>Current Power</th><th>Daily Yield</th><th>Status</th><th></th>
        </tr></thead>
        <tbody>{rows_html}</tbody>
      </table>
    </div>
    """, unsafe_allow_html=True)

    n_online  = sum(1 for p in MOCK_PLANTS if p["status"] == "online")
    cur_out   = sum(p["power_kw"] for p in MOCK_PLANTS)
    n_alarms  = sum(1 for a in MOCK_ALARMS if a["status"] == "active")
    fleet_pct = round(n_online / len(MOCK_PLANTS) * 100)

    st.markdown(f"""
    <div class="scrow">
      <div class="scard gr">
        <div class="sl">Fleet Health</div>
        <div class="sv">{fleet_pct}%</div>
        <div style="font-size:12px;color:#4A8C63;">{n_online} of {len(MOCK_PLANTS)} plants online</div>
      </div>
      <div class="scard am">
        <div class="sl">Current Output</div>
        <div class="sv">{cur_out/1000:.2f} MW</div>
        <div style="font-size:12px;color:#7A5010;">Across all active plants</div>
      </div>
      <div class="scard rd">
        <div class="sl">Active Alarms</div>
        <div class="sv">{n_alarms}</div>
        <div style="font-size:12px;color:#8B1A1A;">Requires attention</div>
      </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
elif _page == "dashboard":
    topnav("dashboard")

    plant_alarms = [a for a in MOCK_ALARMS if a["plant_id"] == _pid and a["status"] == "active"]
    if plant_alarms:
        st.markdown(f"""<div class="fbanner">⚠️ {len(plant_alarms)} active alarm(s) for this plant —
        <a href="?page=alarms&plant={_pid}" style="color:#7A4500;font-weight:600;">View Alarms</a></div>""",
        unsafe_allow_html=True)

    back_col, title_col = st.columns([1, 8])
    with back_col:
        if st.button("← Back"):
            st.query_params["page"] = "plants"
            st.rerun()
    with title_col:
        st.markdown(f"""
        <div style="margin-top:4px;">
          <span style="font-size:18px;font-weight:700;color:#0D2B45;">{_plant['name']}</span>
          <span style="margin:0 8px;color:#CBD8E3;">|</span>
          <span style="font-size:13px;color:#6B7E8F;">{_plant['brand']} · {_plant['location']} · {_plant['capacity']} kWp</span>
        </div>
        """, unsafe_allow_html=True)

    period = st.radio("Period", ["Daily", "Monthly", "Annual", "Total"], horizontal=True, label_visibility="collapsed", key="dash_period")

    if period == "Daily":
        yield_val, unit = _plant["today_kwh"], "kWh"
        savings = round(_plant["today_kwh"] * RATE_PER_KWH, 0)
        co2 = round(_plant["today_kwh"] * 0.82 / 1000, 2)
        trees = round(co2 * 45, 0)
    elif period == "Monthly":
        yield_val, unit = round(_plant["today_kwh"] * 26, 0), "kWh"
        savings = round(yield_val * RATE_PER_KWH, 0)
        co2 = round(yield_val * 0.82 / 1000, 2)
        trees = round(co2 * 45, 0)
    elif period == "Annual":
        yield_val, unit = round(_plant["total_mwh"] * 1000 * 0.4, 0), "kWh"
        savings = round(yield_val * RATE_PER_KWH, 0)
        co2 = round(yield_val * 0.82 / 1000, 2)
        trees = round(co2 * 45, 0)
    else:
        yield_val, unit = _plant["total_mwh"] * 1000, "kWh"
        savings = round(yield_val * RATE_PER_KWH, 0)
        co2 = round(yield_val * 0.82 / 1000, 2)
        trees = round(co2 * 45, 0)

    st.markdown(f"""
    <div class="krow">
      <div class="kcard">
        <div class="klabel">Energy Yield</div>
        <div class="kval">{yield_val:,.0f} <span style="font-size:16px;font-weight:400;color:#6B7E8F;">{unit}</span></div>
        <div class="ktag up">↑ 4.2% vs last period</div>
      </div>
      <div class="kcard">
        <div class="klabel">Savings</div>
        <div class="kval">₹{savings:,.0f}</div>
        <div class="ktag up">↑ 3.8% vs last period</div>
      </div>
      <div class="kcard">
        <div class="klabel">CO₂ Avoided</div>
        <div class="kval">{co2:,.2f} <span style="font-size:16px;font-weight:400;color:#6B7E8F;">tons</span></div>
        <div class="ktag up">↑ 4.2% vs last period</div>
      </div>
      <div class="kcard">
        <div class="klabel">Trees Equivalent</div>
        <div class="kval">{trees:,.0f}</div>
        <div class="ktag up">↑ 4.2% vs last period</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    ch1, ch2 = st.columns(2)
    with ch1:
        hours = list(range(24))
        hourly_data = mock_hourly()
        fig = go.Figure(go.Bar(
            x=hours, y=hourly_data,
            marker_color="#1A6FA8",
            hovertemplate="%{x}:00 — %{y:.1f} kW<extra></extra>",
        ))
        fig.update_layout(
            title="Hourly Power Output (kW)",
            xaxis_title="Hour", yaxis_title="kW",
            plot_bgcolor="#fff", paper_bgcolor="#fff",
            margin=dict(l=10, r=10, t=40, b=10),
            height=300,
        )
        fig.update_xaxes(tickvals=list(range(0,24,3)), ticktext=[f"{h}:00" for h in range(0,24,3)])
        st.markdown('<div class="cbox">', unsafe_allow_html=True)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with ch2:
        brands = ["Growatt", "Solis", "Sungrow"]
        brand_counts = [sum(p["capacity"] for p in MOCK_PLANTS if p["brand"] == b) for b in brands]
        fig2 = go.Figure(go.Pie(
            labels=brands, values=brand_counts,
            marker_colors=["#1A6FA8", "#F5A623", "#2E9B5F"],
            hole=0.45,
            hovertemplate="%{label}: %{value} kWp (%{percent})<extra></extra>",
        ))
        fig2.update_layout(
            title="Fleet Capacity by Brand (kWp)",
            plot_bgcolor="#fff", paper_bgcolor="#fff",
            margin=dict(l=10, r=10, t=40, b=10),
            height=300,
            legend=dict(orientation="h", y=-0.1),
        )
        st.markdown('<div class="cbox">', unsafe_allow_html=True)
        st.plotly_chart(fig2, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("#### Inverter Details")
    inv_rows = ""
    for inv in mock_inverters(_plant):
        s_cls = "bg-gr" if inv["status"] == "Online" else "bg-rd"
        inv_rows += f"""<tr>
          <td>INV-{inv['num']:02d}</td>
          <td><span class="{s_cls}">{inv['status']}</span></td>
          <td>{inv['power']} kW</td>
          <td>{inv['today']} kWh</td>
          <td>{inv['temp']} °C</td>
          <td>{inv['eff']}%</td>
        </tr>"""

    st.markdown(f"""
    <div class="cbox">
      <table class="dtbl">
        <thead><tr>
          <th>Inverter</th><th>Status</th><th>Power</th><th>Today</th><th>Temp</th><th>Efficiency</th>
        </tr></thead>
        <tbody>{inv_rows}</tbody>
      </table>
    </div>
    """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  REPORTS
# ══════════════════════════════════════════════════════════════════════════════
elif _page == "reports":
    topnav("reports")

    plant_alarms = [a for a in MOCK_ALARMS if a["plant_id"] == _pid and a["status"] == "active"]
    if plant_alarms:
        st.markdown(f'<div class="fbanner">⚠️ {len(plant_alarms)} active alarm(s) — <a href="?page=alarms&plant={_pid}" style="color:#7A4500;font-weight:600;">View</a></div>', unsafe_allow_html=True)

    st.markdown(f"### Reports — {_plant['name']}")

    tc1, tc2, tc3, tc4, tc5 = st.columns([2, 1.5, 1.5, 1, 1])
    with tc1:
        st.selectbox("Plant", [p["name"] for p in MOCK_PLANTS],
                     index=next((i for i, p in enumerate(MOCK_PLANTS) if p["id"] == _pid), 0),
                     label_visibility="collapsed")
    with tc2:
        st.selectbox("View", ["Monthly", "Daily", "Annual"], label_visibility="collapsed")
    with tc3:
        st.date_input("Date", label_visibility="collapsed")
    with tc4:
        st.button("⬇ CSV", use_container_width=True)
    with tc5:
        st.button("⬇ Excel", use_container_width=True)

    months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    monthly = mock_monthly()
    total_yr = sum(monthly)
    avg_mo   = total_yr / 12
    peak_mo  = max(monthly)
    savings_yr = round(total_yr * RATE_PER_KWH, 0)
    co2_yr = round(total_yr * 0.82 / 1000, 2)

    st.markdown(f"""
    <div class="krow">
      <div class="kcard amb">
        <div class="klabel">Annual Yield</div>
        <div class="kval">{total_yr:,.0f} <span style="font-size:14px;color:#6B7E8F;">kWh</span></div>
        <div class="ktag up">↑ 6.1% vs last year</div>
      </div>
      <div class="kcard amb">
        <div class="klabel">Avg Monthly</div>
        <div class="kval">{avg_mo:,.0f} <span style="font-size:14px;color:#6B7E8F;">kWh</span></div>
        <div class="ktag up">↑ 6.1% vs last year</div>
      </div>
      <div class="kcard amb">
        <div class="klabel">Peak Month</div>
        <div class="kval">{peak_mo:,.0f} <span style="font-size:14px;color:#6B7E8F;">kWh</span></div>
        <div class="ktag up">↑ 2.3% vs last year</div>
      </div>
      <div class="kcard amb">
        <div class="klabel">Annual Savings</div>
        <div class="kval">₹{savings_yr:,.0f}</div>
        <div class="ktag up">↑ 6.1% vs last year</div>
      </div>
      <div class="kcard amb">
        <div class="klabel">CO₂ Avoided</div>
        <div class="kval">{co2_yr:,.1f} <span style="font-size:14px;color:#6B7E8F;">t</span></div>
        <div class="ktag up">↑ 6.1% vs last year</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    rc1, rc2 = st.columns(2)
    with rc1:
        fig_m = go.Figure(go.Bar(x=months, y=monthly, marker_color="#1A6FA8",
                                  hovertemplate="%{x}: %{y:,.0f} kWh<extra></extra>"))
        fig_m.update_layout(title="Monthly Energy Production (kWh)", plot_bgcolor="#fff",
                             paper_bgcolor="#fff", margin=dict(l=10,r=10,t=40,b=10), height=300)
        st.markdown('<div class="cbox">', unsafe_allow_html=True)
        st.plotly_chart(fig_m, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with rc2:
        annual_data = mock_annual()
        colors = ["#9DB5C8", "#1A6FA8", "#0D2B45"]
        fig_a = go.Figure()
        for i, (yr, vals) in enumerate(annual_data.items()):
            fig_a.add_trace(go.Bar(name=str(yr), x=months, y=vals,
                                    marker_color=colors[i],
                                    hovertemplate=f"{yr} %{{x}}: %{{y:,.0f}} kWh<extra></extra>"))
        fig_a.update_layout(title="Year-on-Year Comparison (kWh)", barmode="group",
                             plot_bgcolor="#fff", paper_bgcolor="#fff",
                             margin=dict(l=10,r=10,t=40,b=10), height=300,
                             legend=dict(orientation="h", y=1.15))
        st.markdown('<div class="cbox">', unsafe_allow_html=True)
        st.plotly_chart(fig_a, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

    days = [f"May {i+1}" for i in range(30)]
    daily = mock_daily()
    fig_d = go.Figure(go.Bar(x=days, y=daily, marker_color="#F5A623",
                              hovertemplate="%{x}: %{y:,.0f} kWh<extra></extra>"))
    fig_d.update_layout(title="Daily Production — May 2026 (kWh)", plot_bgcolor="#fff",
                         paper_bgcolor="#fff", margin=dict(l=10,r=10,t=40,b=10), height=280)
    st.markdown('<div class="cbox">', unsafe_allow_html=True)
    st.plotly_chart(fig_d, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  ALARMS
# ══════════════════════════════════════════════════════════════════════════════
elif _page == "alarms":
    topnav("alarms")
    st.markdown("### Alarms & Notifications")

    fc1, fc2 = st.columns([3, 2])
    with fc1:
        sev_filter = st.radio("Severity", ["All", "Critical", "Warning", "Info", "Resolved"],
                               horizontal=True, label_visibility="collapsed", key="alm_sev")
    with fc2:
        plant_names = ["All Plants"] + [p["name"] for p in MOCK_PLANTS]
        plant_sel = st.selectbox("Plant", plant_names, label_visibility="collapsed")

    filtered_alarms = MOCK_ALARMS
    if sev_filter == "Resolved":
        filtered_alarms = [a for a in filtered_alarms if a["status"] == "resolved"]
    elif sev_filter != "All":
        filtered_alarms = [a for a in filtered_alarms if a["severity"] == sev_filter.lower() and a["status"] == "active"]
    else:
        pass

    if plant_sel != "All Plants":
        filtered_alarms = [a for a in filtered_alarms if a["plant_name"] == plant_sel]

    if not filtered_alarms:
        st.info("No alarms match the selected filters.")
    else:
        for alm in filtered_alarms:
            sev_cls = alm["severity"] if alm["status"] == "active" else "resolved"
            sev_badge = {
                "critical": '<span class="bg-rd">Critical</span>',
                "warning":  '<span class="bg-am">Warning</span>',
                "info":     '<span class="bg-bl">Info</span>',
            }.get(alm["severity"], '<span class="bg-gr">Resolved</span>')
            res_tag = ' <span style="color:#2E9B5F;font-size:12px;margin-left:8px;">✓ Resolved</span>' if alm["status"] == "resolved" else ""
            st.markdown(f"""
            <div class="almc {sev_cls}">
              <div class="atitle">{alm['title']}{res_tag}</div>
              <div class="ameta">
                {sev_badge}
                &nbsp;·&nbsp; <a href="?page=dashboard&plant={alm['plant_id']}" style="color:#1A6FA8;">{alm['plant_name']}</a>
                &nbsp;·&nbsp; {alm['ts']}
              </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<div style='margin-top:24px;color:#9DB5C8;font-size:12px;text-align:center;'>Alarms are refreshed every 5 minutes. Contact support for persistent critical faults.</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
#  SETTINGS
# ══════════════════════════════════════════════════════════════════════════════
elif _page == "settings":
    topnav("settings")
    st.markdown("### Settings")
    st.markdown("""
    <div class="cbox" style="max-width:560px;">
      <h4 style="margin-bottom:16px;">Account Settings</h4>
      <p style="color:#6B7E8F;font-size:14px;">Settings configuration coming soon.</p>
    </div>
    """, unsafe_allow_html=True)

else:
    st.query_params["page"] = "plants"
    st.rerun()
