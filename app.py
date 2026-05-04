# # ============================================================
# #  app.py — Main entry point for the Solar Dashboard
# #  Run with:  streamlit run app.py
# # ============================================================

# import streamlit as st
# from streamlit_autorefresh import st_autorefresh
# import pandas as pd
# import plotly.express as px
# import plotly.graph_objects as go
# from datetime import datetime

# from config import REFRESH_INTERVAL_SECONDS
# from utils.database import init_db, get_recent_readings, get_alert_log, get_power_history
# from utils.data_aggregator import fetch_all_brands, check_and_send_alerts

# # ── Page config ──────────────────────────────────────────────
# st.set_page_config(
#     page_title  = "Solar Dashboard",
#     page_icon   = "☀️",
#     layout      = "wide",
#     initial_sidebar_state = "expanded",
# )

# # ── Custom CSS ───────────────────────────────────────────────
# st.markdown("""
# <style>
#   /* ── Google Fonts ── */
#   @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500;600&display=swap');

#   /* ── Root palette ── */
#   :root {
#     --bg:        #0c0f14;
#     --surface:   #141820;
#     --surface2:  #1c2230;
#     --border:    #2a3347;
#     --accent:    #f5a623;
#     --accent2:   #4fc97e;
#     --danger:    #e84855;
#     --muted:     #6b7a99;
#     --text:      #e8ecf4;
#     --text2:     #a3aec4;
#   }

#   /* ── Global ── */
#   html, body, [data-testid="stAppViewContainer"] {
#     background: var(--bg) !important;
#     color: var(--text);
#     font-family: 'DM Sans', sans-serif;
#   }
#   [data-testid="stSidebar"] {
#     background: var(--surface) !important;
#     border-right: 1px solid var(--border);
#   }
#   [data-testid="stHeader"] { background: transparent !important; }

#   /* ── Metric cards ── */
#   .metric-card {
#     background: var(--surface);
#     border: 1px solid var(--border);
#     border-radius: 12px;
#     padding: 20px 24px;
#     margin-bottom: 12px;
#     position: relative;
#     overflow: hidden;
#   }
#   .metric-card::before {
#     content: '';
#     position: absolute;
#     top: 0; left: 0;
#     width: 4px; height: 100%;
#     background: var(--accent);
#     border-radius: 4px 0 0 4px;
#   }
#   .metric-card.green::before { background: var(--accent2); }
#   .metric-card.red::before   { background: var(--danger); }

#   .metric-label {
#     font-size: 11px;
#     letter-spacing: .1em;
#     text-transform: uppercase;
#     color: var(--muted);
#     font-family: 'Space Mono', monospace;
#     margin-bottom: 6px;
#   }
#   .metric-value {
#     font-size: 28px;
#     font-weight: 600;
#     color: var(--text);
#     line-height: 1.1;
#   }
#   .metric-unit {
#     font-size: 14px;
#     color: var(--muted);
#     margin-left: 4px;
#   }

#   /* ── Inverter card ── */
#   .inv-card {
#     background: var(--surface);
#     border: 1px solid var(--border);
#     border-radius: 14px;
#     padding: 22px;
#     margin-bottom: 16px;
#     transition: border-color .2s;
#   }
#   .inv-card:hover { border-color: var(--accent); }
#   .inv-card.offline { border-color: var(--danger); }
#   .inv-header {
#     display: flex;
#     justify-content: space-between;
#     align-items: flex-start;
#     margin-bottom: 16px;
#   }
#   .inv-name {
#     font-size: 17px;
#     font-weight: 600;
#     color: var(--text);
#   }
#   .inv-plant {
#     font-size: 12px;
#     color: var(--muted);
#     margin-top: 2px;
#     font-family: 'Space Mono', monospace;
#   }
#   .badge {
#     font-size: 11px;
#     font-weight: 700;
#     padding: 4px 10px;
#     border-radius: 999px;
#     font-family: 'Space Mono', monospace;
#     letter-spacing: .05em;
#   }
#   .badge-online  { background: rgba(79,201,126,.15); color: #4fc97e; border: 1px solid #4fc97e55; }
#   .badge-offline { background: rgba(232,72,85,.15);  color: #e84855; border: 1px solid #e8485555; }
#   .badge-unknown { background: rgba(107,122,153,.15);color: #6b7a99; border: 1px solid #6b7a9955; }

#   .brand-tag {
#     font-size: 10px;
#     letter-spacing: .12em;
#     text-transform: uppercase;
#     font-family: 'Space Mono', monospace;
#     padding: 3px 8px;
#     border-radius: 4px;
#     margin-right: 8px;
#   }
#   .brand-solis   { background:#1a2a40; color:#5b9bd5; }
#   .brand-growatt { background:#1a2e1a; color:#4fc97e; }
#   .brand-sungrow { background:#2e1a1a; color:#e87055; }

#   .inv-stats {
#     display: grid;
#     grid-template-columns: repeat(3, 1fr);
#     gap: 12px;
#   }
#   .inv-stat-label { font-size: 10px; color: var(--muted); text-transform:uppercase; letter-spacing:.08em; }
#   .inv-stat-val   { font-size: 18px; font-weight:600; color: var(--text); margin-top:3px; }
#   .inv-stat-unit  { font-size: 11px; color: var(--muted); }
#   .inv-footer {
#     margin-top: 14px;
#     font-size: 11px;
#     color: var(--muted);
#     font-family: 'Space Mono', monospace;
#   }

#   /* ── Alert banner ── */
#   .alert-banner {
#     background: rgba(232,72,85,.12);
#     border: 1px solid rgba(232,72,85,.4);
#     border-radius: 10px;
#     padding: 14px 18px;
#     margin-bottom: 10px;
#     display: flex;
#     align-items: flex-start;
#     gap: 12px;
#   }
#   .alert-icon  { font-size: 20px; }
#   .alert-title { font-weight: 600; color: #e84855; font-size: 14px; }
#   .alert-body  { font-size: 13px; color: var(--text2); margin-top: 2px; }

#   /* ── Section headings ── */
#   .section-title {
#     font-family: 'Space Mono', monospace;
#     font-size: 11px;
#     letter-spacing: .15em;
#     text-transform: uppercase;
#     color: var(--muted);
#     border-bottom: 1px solid var(--border);
#     padding-bottom: 10px;
#     margin: 28px 0 16px;
#   }

#   /* ── Summary bar ── */
#   .summary-bar {
#     background: var(--surface);
#     border: 1px solid var(--border);
#     border-radius: 12px;
#     padding: 18px 24px;
#     display: flex;
#     gap: 32px;
#     align-items: center;
#     margin-bottom: 24px;
#     flex-wrap: wrap;
#   }
#   .summary-item { text-align: center; }
#   .summary-val  { font-size: 22px; font-weight:700; color: var(--accent); font-family:'Space Mono',monospace; }
#   .summary-lbl  { font-size: 10px; color: var(--muted); text-transform:uppercase; letter-spacing:.1em; margin-top:2px; }

#   /* ── Streamlit overrides ── */
#   .stButton > button {
#     background: var(--surface2) !important;
#     color: var(--text) !important;
#     border: 1px solid var(--border) !important;
#     border-radius: 8px !important;
#     font-family: 'Space Mono', monospace !important;
#     font-size: 12px !important;
#     letter-spacing: .05em !important;
#     padding: 8px 18px !important;
#     transition: border-color .2s !important;
#   }
#   .stButton > button:hover { border-color: var(--accent) !important; }

#   div[data-testid="stSelectbox"] label,
#   div[data-testid="stMultiSelect"] label { color: var(--muted) !important; }

#   .stDataFrame { border-radius: 10px; overflow: hidden; }

#   /* hide default streamlit decoration */
#   #MainMenu, footer, header { visibility: hidden; }
# </style>
# """, unsafe_allow_html=True)


# # ── Init DB ──────────────────────────────────────────────────
# init_db()

# # ── Auto-refresh ─────────────────────────────────────────────
# st_autorefresh(interval=REFRESH_INTERVAL_SECONDS * 1000, key="solar_refresh")

# # ── Sidebar ──────────────────────────────────────────────────
# with st.sidebar:
#     st.markdown("""
#     <div style="padding:8px 0 24px;">
#       <div style="font-family:'Space Mono',monospace;font-size:18px;font-weight:700;color:#f5a623;">
#         ☀ SOLAR HQ
#       </div>
#       <div style="font-size:11px;color:#6b7a99;margin-top:4px;">Unified Inverter Monitor</div>
#     </div>
#     """, unsafe_allow_html=True)

#     st.markdown("**Brands to fetch**")
#     brands_all = ["Solis", "Growatt", "Sungrow"]
#     selected_brands = []
#     for b in brands_all:
#         if st.checkbox(b, value=(b == "Solis"), key=f"cb_{b}"):
#             selected_brands.append(b)

#     st.divider()

#     if st.button("🔄 Refresh Now"):
#         st.cache_data.clear()
#         st.rerun()

#     st.divider()
#     st.markdown("""
#     <div style="font-size:11px;color:#6b7a99;font-family:'Space Mono',monospace;">
#       Auto-refresh: every 5 min<br>
#       Last check:<br>
#     """ + f"<span style='color:#e8ecf4'>{datetime.now().strftime('%H:%M:%S')}</span></div>",
#     unsafe_allow_html=True)

#     st.divider()
#     page = st.radio(
#         "Navigate",
#         ["🏠 Overview", "⚡ Inverters", "📈 History", "🚨 Alerts", "⚙️ Settings"],
#         label_visibility="collapsed",
#     )


# # ── Fetch data ───────────────────────────────────────────────
# @st.cache_data(ttl=REFRESH_INTERVAL_SECONDS)
# def load_data(brands):
#     return fetch_all_brands(list(brands))


# with st.spinner("Fetching inverter data…"):
#     records = load_data(tuple(selected_brands))

# active_alerts = check_and_send_alerts(records, st.session_state)

# df_all = pd.DataFrame(records) if records else pd.DataFrame()


# # ─────────────────────────────────────────────────────────────
# # PAGE: OVERVIEW
# # ─────────────────────────────────────────────────────────────
# if page == "🏠 Overview":
#     st.markdown("""
#     <h1 style="font-size:30px;font-weight:700;margin-bottom:4px;">
#       Solar Dashboard <span style="color:#f5a623;">Overview</span>
#     </h1>
#     <p style="color:#6b7a99;font-size:14px;margin-top:0;">Real-time performance across all plants & brands</p>
#     """, unsafe_allow_html=True)

#     if df_all.empty:
#         st.warning("⚠️ No data received. Check your credentials in config.py and try refreshing.")
#         st.stop()

#     # ── Summary KPIs ─────────────────────────────────────────
#     total_power  = df_all["power_kw"].sum() if "power_kw" in df_all else 0
#     total_today  = df_all["today_kwh"].sum() if "today_kwh" in df_all else 0
#     total_all    = df_all["total_kwh"].sum()  if "total_kwh" in df_all else 0
#     n_inv        = len(df_all)
#     n_online     = (df_all.get("status", pd.Series()) == "Online").sum()
#     n_alerts     = len(active_alerts)

#     c1, c2, c3, c4, c5, c6 = st.columns(6)
#     kpis = [
#         (c1, "Total Power", f"{total_power:,.1f}", "kW",  ""),
#         (c2, "Today's Energy", f"{total_today:,.1f}", "kWh", "green"),
#         (c3, "All-time Energy", f"{total_all:,.0f}", "kWh", "green"),
#         (c4, "Inverters", str(n_inv), "", ""),
#         (c5, "Online", str(n_online), f"/ {n_inv}", "green"),
#         (c6, "Active Alerts", str(n_alerts), "", "red" if n_alerts else ""),
#     ]
#     for col, lbl, val, unit, cls in kpis:
#         with col:
#             st.markdown(f"""
#             <div class="metric-card {cls}">
#               <div class="metric-label">{lbl}</div>
#               <div class="metric-value">{val}<span class="metric-unit">{unit}</span></div>
#             </div>
#             """, unsafe_allow_html=True)

#     # ── Active alerts ─────────────────────────────────────────
#     if active_alerts:
#         st.markdown('<div class="section-title">🚨 Active Alerts</div>', unsafe_allow_html=True)
#         for a in active_alerts:
#             st.markdown(f"""
#             <div class="alert-banner">
#               <div class="alert-icon">⚠️</div>
#               <div>
#                 <div class="alert-title">{a['plant_name']} — {a.get('inverter_sn','')}</div>
#                 <div class="alert-body">{a['issue']}</div>
#               </div>
#             </div>
#             """, unsafe_allow_html=True)

#     # ── Power by brand chart ──────────────────────────────────
#     st.markdown('<div class="section-title">Power by Brand</div>', unsafe_allow_html=True)

#     brand_df = df_all.groupby("brand")["power_kw"].sum().reset_index()
#     fig_brand = px.bar(
#         brand_df, x="brand", y="power_kw", color="brand",
#         color_discrete_map={"Solis": "#5b9bd5", "Growatt": "#4fc97e", "Sungrow": "#e87055"},
#         labels={"power_kw": "Power (kW)", "brand": ""},
#     )
#     fig_brand.update_layout(
#         plot_bgcolor  = "rgba(0,0,0,0)",
#         paper_bgcolor = "rgba(0,0,0,0)",
#         font_color    = "#a3aec4",
#         showlegend    = False,
#         margin        = dict(l=0, r=0, t=10, b=0),
#         height        = 240,
#         bargap        = 0.4,
#     )
#     fig_brand.update_traces(marker_line_width=0)
#     fig_brand.update_xaxes(showgrid=False, zeroline=False)
#     fig_brand.update_yaxes(showgrid=True, gridcolor="#2a3347", zeroline=False)
#     st.plotly_chart(fig_brand, use_container_width=True)

#     # ── Power by plant chart ──────────────────────────────────
#     st.markdown('<div class="section-title">Power by Plant</div>', unsafe_allow_html=True)

#     plant_df = df_all.groupby(["plant_name","brand"])["power_kw"].sum().reset_index()
#     fig_plant = px.bar(
#         plant_df, x="plant_name", y="power_kw", color="brand",
#         color_discrete_map={"Solis": "#5b9bd5", "Growatt": "#4fc97e", "Sungrow": "#e87055"},
#         labels={"power_kw": "Power (kW)", "plant_name": ""},
#     )
#     fig_plant.update_layout(
#         plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
#         font_color="#a3aec4", margin=dict(l=0,r=0,t=10,b=0), height=260,
#         legend=dict(bgcolor="rgba(0,0,0,0)", font_color="#a3aec4"),
#     )
#     fig_plant.update_traces(marker_line_width=0)
#     fig_plant.update_xaxes(showgrid=False, zeroline=False)
#     fig_plant.update_yaxes(showgrid=True, gridcolor="#2a3347", zeroline=False)
#     st.plotly_chart(fig_plant, use_container_width=True)


# # ─────────────────────────────────────────────────────────────
# # PAGE: INVERTERS
# # ─────────────────────────────────────────────────────────────
# elif page == "⚡ Inverters":
#     st.markdown("""
#     <h1 style="font-size:30px;font-weight:700;margin-bottom:4px;">
#       Inverter <span style="color:#f5a623;">Details</span>
#     </h1>
#     <p style="color:#6b7a99;font-size:14px;margin-top:0;">Live readings for every inverter</p>
#     """, unsafe_allow_html=True)

#     if df_all.empty:
#         st.warning("⚠️ No data. Check credentials and refresh.")
#         st.stop()

#     # Filters
#     col_f1, col_f2 = st.columns([2,2])
#     with col_f1:
#         brand_filter = st.selectbox("Filter by brand", ["All"] + list(df_all["brand"].unique()))
#     with col_f2:
#         plant_opts = ["All"] + sorted(df_all["plant_name"].unique().tolist())
#         plant_filter = st.selectbox("Filter by plant", plant_opts)

#     view = df_all.copy()
#     if brand_filter != "All":
#         view = view[view["brand"] == brand_filter]
#     if plant_filter != "All":
#         view = view[view["plant_name"] == plant_filter]

#     alert_sns = {a.get("inverter_sn") for a in active_alerts}

#     for _, row in view.iterrows():
#         sn      = row.get("inverter_sn", "N/A")
#         status  = row.get("status", "Unknown")
#         brand   = row.get("brand", "")

#         status_badge = {
#             "Online":  "badge-online",
#             "Offline": "badge-offline",
#             "Fault":   "badge-offline",
#         }.get(status, "badge-unknown")

#         brand_cls = f"brand-{brand.lower()}"
#         card_cls  = "inv-card offline" if sn in alert_sns else "inv-card"

#         power = row.get("power_kw")
#         today = row.get("today_kwh")
#         total = row.get("total_kwh")
#         temp  = row.get("temperature")
#         volt  = row.get("voltage")
#         curr  = row.get("current_a")

#         def fmt(v, dec=1):
#             return f"{v:.{dec}f}" if v is not None else "—"

#         extra_cells = ""
#         if temp is not None:
#             extra_cells += (
#                 '<div>'
#                 '<div class="inv-stat-label">Temperature</div>'
#                 f'<div class="inv-stat-val">{fmt(temp)}<span class="inv-stat-unit"> °C</span></div>'
#                 '</div>'
#             )
#         if volt is not None:
#             extra_cells += (
#                 '<div>'
#                 '<div class="inv-stat-label">AC Voltage</div>'
#                 f'<div class="inv-stat-val">{fmt(volt)}<span class="inv-stat-unit"> V</span></div>'
#                 '</div>'
#             )
#         if curr is not None:
#             extra_cells += (
#                 '<div>'
#                 '<div class="inv-stat-label">AC Current</div>'
#                 f'<div class="inv-stat-val">{fmt(curr)}<span class="inv-stat-unit"> A</span></div>'
#                 '</div>'
#             )

#         full_card = (
#             f'<div class="{card_cls}">'
#               '<div class="inv-header">'
#                 '<div>'
#                   f'<span class="brand-tag {brand_cls}">{brand}</span>'
#                   f'<div class="inv-name" style="margin-top:8px;">{row.get("plant_name","")}</div>'
#                   f'<div class="inv-plant">S/N: {sn}</div>'
#                 '</div>'
#                 f'<span class="badge {status_badge}">{status}</span>'
#               '</div>'
#               '<div class="inv-stats">'
#                 '<div>'
#                   '<div class="inv-stat-label">Power Now</div>'
#                   f'<div class="inv-stat-val">{fmt(power)}<span class="inv-stat-unit"> kW</span></div>'
#                 '</div>'
#                 '<div>'
#                   '<div class="inv-stat-label">Today\'s Generation</div>'
#                   f'<div class="inv-stat-val">{fmt(today)}<span class="inv-stat-unit"> kWh</span></div>'
#                 '</div>'
#                 '<div>'
#                   '<div class="inv-stat-label">Total Generation</div>'
#                   f'<div class="inv-stat-val">{fmt(total, 0)}<span class="inv-stat-unit"> kWh</span></div>'
#                 '</div>'
#                 + extra_cells +
#               '</div>'
#               f'<div class="inv-footer">Last update: {row.get("last_update", "—")}</div>'
#             '</div>'
#         )

#         st.markdown(full_card, unsafe_allow_html=True)


# # ─────────────────────────────────────────────────────────────
# # PAGE: HISTORY
# # ─────────────────────────────────────────────────────────────
# elif page == "📈 History":
#     st.markdown("""
#     <h1 style="font-size:30px;font-weight:700;margin-bottom:4px;">
#       Historical <span style="color:#f5a623;">Data</span>
#     </h1>
#     <p style="color:#6b7a99;font-size:14px;margin-top:0;">Trend analysis from local database</p>
#     """, unsafe_allow_html=True)

#     hist_df = get_recent_readings(hours=168)   # 7 days

#     if hist_df.empty:
#         st.info("📭 No historical data yet. Data accumulates after the first few refreshes.")
#         st.stop()

#     col_h1, col_h2 = st.columns([2,1])
#     with col_h1:
#         plant_sel = st.selectbox("Select plant", sorted(hist_df["plant_name"].unique()))
#     with col_h2:
#         days_sel = st.selectbox("Period", [1, 3, 7, 14, 30], index=2, format_func=lambda x: f"{x} days")

#     plant_hist = hist_df[hist_df["plant_name"] == plant_sel].copy()
#     plant_hist["fetched_at"] = pd.to_datetime(plant_hist["fetched_at"])
#     plant_hist = plant_hist.sort_values("fetched_at")

#     st.markdown('<div class="section-title">Power Output Over Time</div>', unsafe_allow_html=True)
#     fig_line = px.line(
#         plant_hist, x="fetched_at", y="power_kw",
#         color="inverter_sn",
#         labels={"fetched_at":"Time", "power_kw":"Power (kW)", "inverter_sn":"Inverter"},
#     )
#     fig_line.update_layout(
#         plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
#         font_color="#a3aec4", margin=dict(l=0,r=0,t=10,b=0), height=320,
#         legend=dict(bgcolor="rgba(0,0,0,0)"),
#     )
#     fig_line.update_xaxes(showgrid=False, zeroline=False)
#     fig_line.update_yaxes(showgrid=True, gridcolor="#2a3347", zeroline=False)
#     st.plotly_chart(fig_line, use_container_width=True)

#     st.markdown('<div class="section-title">Daily Energy (kWh)</div>', unsafe_allow_html=True)
#     daily = (plant_hist.groupby(plant_hist["fetched_at"].dt.date)["today_kwh"]
#              .max().reset_index())
#     daily.columns = ["date","today_kwh"]
#     fig_bar = px.bar(daily, x="date", y="today_kwh",
#                      labels={"date":"Date","today_kwh":"Energy (kWh)"},
#                      color_discrete_sequence=["#f5a623"])
#     fig_bar.update_layout(
#         plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
#         font_color="#a3aec4", margin=dict(l=0,r=0,t=10,b=0), height=260,
#     )
#     fig_bar.update_traces(marker_line_width=0)
#     fig_bar.update_xaxes(showgrid=False, zeroline=False)
#     fig_bar.update_yaxes(showgrid=True, gridcolor="#2a3347", zeroline=False)
#     st.plotly_chart(fig_bar, use_container_width=True)

#     st.markdown('<div class="section-title">Raw Data</div>', unsafe_allow_html=True)
#     st.dataframe(
#         plant_hist[["fetched_at","inverter_sn","brand","power_kw","today_kwh","total_kwh","status"]]
#                 .rename(columns={
#                     "fetched_at":"Timestamp","inverter_sn":"S/N","brand":"Brand",
#                     "power_kw":"Power kW","today_kwh":"Today kWh",
#                     "total_kwh":"Total kWh","status":"Status"
#                 }),
#         use_container_width=True, hide_index=True,
#     )


# # ─────────────────────────────────────────────────────────────
# # PAGE: ALERTS
# # ─────────────────────────────────────────────────────────────
# elif page == "🚨 Alerts":
#     st.markdown("""
#     <h1 style="font-size:30px;font-weight:700;margin-bottom:4px;">
#       Alert <span style="color:#f5a623;">Log</span>
#     </h1>
#     <p style="color:#6b7a99;font-size:14px;margin-top:0;">All alerts that have triggered email notifications</p>
#     """, unsafe_allow_html=True)

#     # Current alerts
#     if active_alerts:
#         st.markdown('<div class="section-title">🔴 Currently Active</div>', unsafe_allow_html=True)
#         for a in active_alerts:
#             st.markdown(f"""
#             <div class="alert-banner">
#               <div class="alert-icon">🚨</div>
#               <div>
#                 <div class="alert-title">{a['brand']} · {a['plant_name']} · {a.get('inverter_sn','')}</div>
#                 <div class="alert-body">{a['issue']}</div>
#               </div>
#             </div>
#             """, unsafe_allow_html=True)
#     else:
#         st.success("✅ All inverters operating normally — no active alerts.")

#     # Historical log
#     st.markdown('<div class="section-title">Historical Alert Log</div>', unsafe_allow_html=True)
#     alert_log = get_alert_log(100)
#     if alert_log.empty:
#         st.info("No alerts have been logged yet.")
#     else:
#         st.dataframe(alert_log.rename(columns={
#             "brand":"Brand","plant_name":"Plant","inverter_sn":"S/N",
#             "issue":"Issue","alerted_at":"Time"
#         }), use_container_width=True, hide_index=True)


# # ─────────────────────────────────────────────────────────────
# # PAGE: SETTINGS
# # ─────────────────────────────────────────────────────────────
# elif page == "⚙️ Settings":
#     st.markdown("""
#     <h1 style="font-size:30px;font-weight:700;margin-bottom:4px;">
#       Configuration <span style="color:#f5a623;">Settings</span>
#     </h1>
#     <p style="color:#6b7a99;font-size:14px;margin-top:0;">
#       Edit <code>config.py</code> in the project root to update credentials.
#     </p>
#     """, unsafe_allow_html=True)

#     st.markdown('<div class="section-title">API Status</div>', unsafe_allow_html=True)

#     from config import (
#         SOLIS_API_KEY, GROWATT_USERNAME, SUNGROW_APP_KEY,
#         EMAIL_USER, TO_EMAILS
#     )

#     status_rows = [
#         ("Solis",   "✅ Configured" if SOLIS_API_KEY else "❌ Missing",   SOLIS_API_KEY[:8]+"…" if SOLIS_API_KEY else "—"),
#         ("Growatt", "✅ Configured" if GROWATT_USERNAME else "⚠️ Not set", GROWATT_USERNAME or "Set GROWATT_USERNAME in config.py"),
#         ("Sungrow", "✅ Configured" if SUNGROW_APP_KEY else "⚠️ Not set", SUNGROW_APP_KEY[:8]+"…" if SUNGROW_APP_KEY else "Set SUNGROW_APP_KEY in config.py"),
#     ]

#     for brand, status, hint in status_rows:
#         col1, col2, col3 = st.columns([1,1,3])
#         col1.markdown(f"**{brand}**")
#         col2.markdown(status)
#         col3.markdown(f"`{hint}`")

#     st.divider()
#     st.markdown('<div class="section-title">Email Alerts</div>', unsafe_allow_html=True)
#     st.markdown(f"**From:** `{EMAIL_USER}`")
#     st.markdown(f"**To:**   `{', '.join(TO_EMAILS)}`")

#     st.divider()
#     st.markdown('<div class="section-title">Project Structure</div>', unsafe_allow_html=True)
#     st.code("""
# solar_dashboard/
# ├── app.py                  ← Main Streamlit app (run this)
# ├── config.py               ← ✏️  All credentials & settings
# ├── requirements.txt        ← pip install -r requirements.txt
# ├── data/
# │   └── solar_data.db       ← SQLite database (auto-created)
# └── utils/
#     ├── __init__.py
#     ├── database.py         ← DB read/write helpers
#     ├── alerts.py           ← Email alert sender
#     ├── solis_api.py        ← Solis Cloud connector
#     ├── growatt_api.py      ← Growatt connector
#     ├── sungrow_api.py      ← Sungrow iSolarCloud connector
#     └── data_aggregator.py  ← Combines all brands + alert logic
#     """, language="")

#     st.divider()
#     st.markdown("**To add Growatt/Sungrow**, open `config.py` and fill in the credential fields, then refresh.")

# ============================================================
#  app.py — Solar Dashboard  |  streamlit run app.py
# ============================================================

# ============================================================
#  app.py — Solar Dashboard  |  streamlit run app.py
# ============================================================

# ============================================================
#  app.py — Solar Dashboard  |  streamlit run app.py
# ============================================================

# ============================================================
#  app.py — Solar Dashboard  |  streamlit run app.py
# ============================================================

# import streamlit as st
# from streamlit_autorefresh import st_autorefresh
# import pandas as pd
# import plotly.express as px
# from datetime import datetime, date

# from config import REFRESH_INTERVAL_SECONDS
# from utils.database import init_db, get_recent_readings, get_alert_log
# from utils.data_aggregator import fetch_all_brands, check_and_send_alerts

# # ── Page config ──────────────────────────────────────────────
# st.set_page_config(
#     page_title="Solar Dashboard",
#     page_icon="☀️",
#     layout="wide",
#     initial_sidebar_state="expanded",
# )

# # ── CSS ──────────────────────────────────────────────────────
# st.markdown("""
# <style>
# @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
# :root {
#   --bg:#f0f2f5; --surface:#fff; --border:#e4e6ef;
#   --accent:#f5821f; --danger:#e84855; --warning:#ffa800;
#   --text:#181c32; --text2:#7e8299; --sub:#a1a5b7;
# }
# html,body,[data-testid="stAppViewContainer"]{
#   background:var(--bg)!important;font-family:'Inter',sans-serif;color:var(--text);
# }
# [data-testid="stHeader"]{background:transparent!important;}
# [data-testid="stSidebar"]{background:#1e1e2d!important;border-right:none!important;}
# [data-testid="stSidebar"] *{color:#9899ac!important;}
# #MainMenu,footer,header{visibility:hidden;}

# .kpi-card{background:#fff;border-radius:12px;padding:22px 20px;border:1px solid var(--border);
#   display:flex;align-items:flex-start;gap:14px;box-shadow:0 2px 8px rgba(0,0,0,.04);}
# .kpi-icon{width:46px;height:46px;border-radius:50%;display:flex;align-items:center;
#   justify-content:center;font-size:20px;flex-shrink:0;}
# .kpi-icon.power{background:#fff3e8;}.kpi-icon.daily{background:#fff0e8;}
# .kpi-icon.monthly{background:#e8f4ff;}.kpi-icon.total{background:#fff8e8;}
# .kpi-label{font-size:13px;color:var(--text2);font-weight:500;margin-bottom:5px;}
# .kpi-value{font-size:24px;font-weight:700;color:var(--text);line-height:1.1;}
# .kpi-unit{font-size:13px;font-weight:500;color:var(--text2);margin-left:2px;}
# .kpi-sub{font-size:12px;color:var(--sub);margin-top:5px;}
# .kpi-sub span{color:var(--text);font-weight:500;}

# .sec-title{font-size:20px;font-weight:700;color:var(--text);margin-bottom:4px;}
# .sec-sub{font-size:13px;color:var(--text2);margin-bottom:16px;}
# .divider{height:1px;background:var(--border);margin:16px 0;}

# .device-card{background:#fff;border:1px solid var(--border);border-radius:12px;
#   padding:20px 22px;margin-bottom:14px;box-shadow:0 2px 6px rgba(0,0,0,.04);}
# .device-header{display:flex;justify-content:space-between;align-items:flex-start;
#   margin-bottom:14px;padding-bottom:12px;border-bottom:1px solid var(--border);}
# .device-name{font-size:16px;font-weight:700;color:var(--text);}
# .device-sn{font-size:12px;color:var(--sub);margin-top:3px;}
# .device-grid{display:grid;grid-template-columns:repeat(6,1fr);gap:14px;}
# .dp-label{font-size:11px;color:var(--text2);text-transform:uppercase;letter-spacing:.06em;}
# .dp-val{font-size:16px;font-weight:600;color:var(--text);margin-top:2px;}
# .dp-unit{font-size:11px;color:var(--sub);}
# .device-footer{margin-top:12px;font-size:11px;color:var(--sub);}

# .badge{display:inline-block;font-size:11px;font-weight:600;padding:3px 10px;border-radius:20px;}
# .badge-online{background:#e8f9ef;color:#1e9e5e;}
# .badge-offline{background:#fde8ea;color:#d9363e;}
# .badge-warning{background:#fff4de;color:#b37400;}
# .badge-unknown{background:#f3f3f3;color:#888;}

# .btag{font-size:10px;font-weight:700;padding:2px 8px;border-radius:4px;
#   letter-spacing:.08em;text-transform:uppercase;}
# .btag-solis{background:#e8f0fb;color:#2563b0;}
# .btag-growatt{background:#e8fbee;color:#1a7a3c;}
# .btag-sungrow{background:#fef0e8;color:#b85a10;}

# .ptable{background:#fff;border-radius:12px;border:1px solid var(--border);
#   overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,.04);}
# .pth{display:grid;grid-template-columns:2fr 1fr 1.2fr 0.8fr 1fr 1.2fr 1.4fr 1fr;
#   padding:12px 20px;background:#f9f9f9;border-bottom:1px solid var(--border);
#   font-size:11px;font-weight:600;color:var(--text2);text-transform:uppercase;
#   letter-spacing:.06em;gap:8px;}
# .ptr{display:grid;grid-template-columns:2fr 1fr 1.2fr 0.8fr 1fr 1.2fr 1.4fr 1fr;
#   padding:14px 20px;border-bottom:1px solid var(--border);font-size:13px;
#   align-items:center;gap:8px;}
# .ptr:last-child{border-bottom:none;}
# .ptr:hover{background:#fafafa;}
# .plink{color:var(--accent);font-weight:600;}

# .alh{display:grid;grid-template-columns:1fr 1fr 1fr 1.5fr 1.3fr 2fr 1.2fr;
#   padding:10px 18px;background:#f9f9f9;border:1px solid var(--border);
#   border-radius:8px;font-size:11px;font-weight:600;color:var(--text2);
#   text-transform:uppercase;letter-spacing:.06em;gap:8px;margin-bottom:4px;}
# .alr{display:grid;grid-template-columns:1fr 1fr 1fr 1.5fr 1.3fr 2fr 1.2fr;
#   padding:13px 18px;background:#fff;border:1px solid var(--border);
#   border-radius:8px;font-size:13px;align-items:center;gap:8px;margin-bottom:6px;}
# .alr.crit{border-left:3px solid var(--danger);}
# .alr.warn{border-left:3px solid var(--warning);}

# .debug-box{background:#1e1e2d;border-radius:8px;padding:16px;
#   font-family:monospace;font-size:12px;color:#a8ff78;margin-bottom:12px;}

# .stButton>button{background:var(--accent)!important;color:#fff!important;
#   border:none!important;border-radius:6px!important;font-weight:600!important;
#   font-size:13px!important;padding:8px 20px!important;}
# </style>
# """, unsafe_allow_html=True)

# # ── Init ─────────────────────────────────────────────────────
# init_db()
# st_autorefresh(interval=REFRESH_INTERVAL_SECONDS * 1000, key="solar_refresh")

# # ── Helpers ──────────────────────────────────────────────────
# def fmt(v, dec=1):
#     try:    return f"{float(v):.{dec}f}"
#     except: return "—"

# def sbadge(s):
#     s = (s or "").strip().lower()
#     if s == "online":            return '<span class="badge badge-online">Online</span>'
#     if s in ("offline","fault"): return '<span class="badge badge-offline">Offline</span>'
#     return '<span class="badge badge-unknown">Unknown</span>'

# def btag(b):
#     return f'<span class="btag btag-{(b or "").lower()}">{b}</span>'

# def chart_style(fig, height=300):
#     fig.update_layout(
#         plot_bgcolor="white", paper_bgcolor="white",
#         font_color="#7e8299", margin=dict(l=0,r=0,t=10,b=0),
#         height=height, legend=dict(bgcolor="white"), bargap=0.3,
#     )
#     fig.update_traces(marker_line_width=0)
#     fig.update_xaxes(showgrid=False, zeroline=False)
#     fig.update_yaxes(showgrid=True, gridcolor="#f0f2f5", zeroline=False)

# def earn(v_kwh):
#     """Format earnings from kWh value at ₹4/kWh"""
#     RATE = 4.0
#     v = v_kwh * RATE
#     if v >= 1_000_000: return f"₹{v/1_000_000:.3f}M"
#     if v >= 1_000:     return f"₹{v/1_000:.3f}K"
#     return f"₹{v:.2f}"

# # ── Sidebar ──────────────────────────────────────────────────
# with st.sidebar:
#     st.markdown("""
#     <div style="padding:20px 16px 28px;">
#       <div style="display:flex;align-items:center;gap:10px;margin-bottom:36px;">
#         <div style="width:36px;height:36px;background:#f5821f;border-radius:8px;
#                     display:flex;align-items:center;justify-content:center;font-size:18px;">☀</div>
#         <div>
#           <div style="color:#fff;font-weight:700;font-size:15px;">Solar HQ</div>
#           <div style="color:#6b6b80;font-size:11px;">Fractal Energy</div>
#         </div>
#       </div>
#     </div>
#     """, unsafe_allow_html=True)

#     page = st.radio(
#         "Nav",
#         ["📊  Overview", "🔧  O&M", "📈  Report", "⚙️  Service"],
#         label_visibility="collapsed",
#     )
#     page = page.split("  ", 1)[1].strip()

#     st.divider()
#     st.markdown(
#         "<div style='color:#6b6b80;font-size:11px;text-transform:uppercase;"
#         "letter-spacing:.1em;margin-bottom:8px;'>Data Sources</div>",
#         unsafe_allow_html=True)
#     selected_brands = [b for b in ["Solis","Growatt","Sungrow"]
#                        if st.checkbox(b, value=(b == "Solis"), key=f"cb_{b}")]
#     st.divider()

#     show_debug = st.checkbox("🔍 Show Debug Info", value=False)

#     if st.button("🔄 Refresh"):
#         st.cache_data.clear()
#         st.rerun()
#     st.markdown(
#         f"<div style='color:#6b6b80;font-size:11px;margin-top:8px;'>"
#         f"Updated: {datetime.now().strftime('%H:%M:%S')}</div>",
#         unsafe_allow_html=True)

# # ── Fetch ─────────────────────────────────────────────────────
# @st.cache_data(ttl=REFRESH_INTERVAL_SECONDS)
# def load_data(brands):
#     return fetch_all_brands(list(brands))

# with st.spinner("Loading inverter data…"):
#     records = load_data(tuple(selected_brands))

# active_alerts = check_and_send_alerts(records, st.session_state)

# # ── Build DataFrame with explicit numeric conversion ──────────
# if records:
#     df = pd.DataFrame(records)
#     for col in ["power_kw", "today_kwh", "total_kwh", "temperature", "voltage", "current_a"]:
#         if col in df.columns:
#             df[col] = pd.to_numeric(df[col], errors="coerce")
#     if "status" in df.columns:
#         df["status"] = df["status"].astype(str).str.strip()
# else:
#     df = pd.DataFrame()

# # ── Debug panel ───────────────────────────────────────────────
# if show_debug and not df.empty:
#     st.markdown("### 🔍 Debug: Raw API Data")
#     st.dataframe(df, use_container_width=True)
#     st.markdown("**Column dtypes:**")
#     st.write(df.dtypes.to_dict())
#     st.markdown("**Sample values:**")
#     for col in ["power_kw","today_kwh","total_kwh","status"]:
#         if col in df.columns:
#             st.write(f"`{col}`: {df[col].tolist()}")
#     st.divider()


# # ═════════════════════════════════════════════════════════════
# # OVERVIEW
# # ═════════════════════════════════════════════════════════════
# if page == "Overview":
#     st.markdown('<div class="sec-title">Plant Overview</div>', unsafe_allow_html=True)

#     if df.empty:
#         st.warning("⚠️ No data received. Check your credentials in config.py then click Refresh.")
#         st.info("💡 Tip: Enable **Show Debug Info** in the sidebar to see what the API returns.")
#         st.stop()

#     # ── KPI calculations ─────────────────────────────────────
#     # Confirmed units from debug data + Solis app comparison:
#     #   power_kw  → kW   (inverterDetail pac/1000, precise)
#     #   today_kwh → kWh  (etoday, e.g. 15, 101, 26.9)
#     #   total_kwh → MWh  (etotal, e.g. 64.837, 17.475, 110.352)
#     #
#     # Solis app shows:
#     #   Power        329.68 kW  = sum of pac/1000 per inverter
#     #   Daily Yield  574 kWh    = sum of etoday
#     #   Total Yield  850.178 MWh= sum of etotal (already MWh)

#     total_power_kw = df["power_kw"].sum()     # kW
#     daily_kwh      = df["today_kwh"].sum()    # kWh
#     total_raw      = df["total_kwh"].sum()    # MWh (etotal is already MWh)

#     # Monthly yield: best from DB history; fallback to today's daily if DB is new
#     hist = get_recent_readings(hours=720)
#     monthly_kwh = 0.0
#     if not hist.empty and "today_kwh" in hist.columns:
#         hist["fetched_at"] = pd.to_datetime(hist["fetched_at"])
#         hist["today_kwh"]  = pd.to_numeric(hist["today_kwh"], errors="coerce")
#         this_month = hist[hist["fetched_at"].dt.month == datetime.now().month]
#         if not this_month.empty:
#             # Max reading per inverter per day → sum across all days & inverters
#             monthly_kwh = float(
#                 this_month
#                 .groupby([this_month["fetched_at"].dt.date, "inverter_sn"])["today_kwh"]
#                 .max().sum()
#             )
#     if monthly_kwh < daily_kwh:
#         monthly_kwh = float(daily_kwh)   # floor: at minimum today's yield

#     # Online count
#     n_online = int((df["status"].str.lower() == "online").sum())
#     n_total  = len(df)

#     # ── KPI cards ────────────────────────────────────────────
#     c1, c2, c3, c4 = st.columns(4)

#     with c1:
#         st.markdown(f"""
#         <div class="kpi-card">
#           <div class="kpi-icon power">⚡</div>
#           <div>
#             <div class="kpi-label">Power</div>
#             <div class="kpi-value">{fmt(total_power_kw,2)}<span class="kpi-unit"> kW</span></div>
#             <div class="kpi-sub">Inverters online: <span>{n_online} / {n_total}</span> &nbsp;|&nbsp; Capacity: <span>{fmt(total_power_kw,2)} kW</span></div>
#           </div>
#         </div>""", unsafe_allow_html=True)

#     with c2:
#         st.markdown(f"""
#         <div class="kpi-card">
#           <div class="kpi-icon daily">🔋</div>
#           <div>
#             <div class="kpi-label">Daily Yield</div>
#             <div class="kpi-value">{fmt(daily_kwh,1)}<span class="kpi-unit"> kWh</span></div>
#             <div class="kpi-sub">Daily Earning: <span>{earn(daily_kwh)}</span></div>
#           </div>
#         </div>""", unsafe_allow_html=True)

#     with c3:
#         # Monthly in MWh if ≥ 1000 kWh
#         if monthly_kwh >= 1000:
#             m_val, m_unit = fmt(monthly_kwh / 1000, 3), "MWh"
#         else:
#             m_val, m_unit = fmt(monthly_kwh, 1), "kWh"
#         st.markdown(f"""
#         <div class="kpi-card">
#           <div class="kpi-icon monthly">📅</div>
#           <div>
#             <div class="kpi-label">Monthly Yield</div>
#             <div class="kpi-value">{m_val}<span class="kpi-unit"> {m_unit}</span></div>
#             <div class="kpi-sub">Monthly Earning: <span>{earn(monthly_kwh)}</span></div>
#           </div>
#         </div>""", unsafe_allow_html=True)

#     with c4:
#         # total_raw is in MWh from Solis; convert to kWh for earnings
#         st.markdown(f"""
#         <div class="kpi-card">
#           <div class="kpi-icon total">📊</div>
#           <div>
#             <div class="kpi-label">Total Yield</div>
#             <div class="kpi-value">{fmt(total_raw,3)}<span class="kpi-unit"> MWh</span></div>
#             <div class="kpi-sub">Total Earning: <span>{earn(total_raw * 1000)}</span></div>
#           </div>
#         </div>""", unsafe_allow_html=True)

#     st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

#     if active_alerts:
#         st.error(f"🚨 {len(active_alerts)} active alert(s) — see O&M → Alarm Information")

#     st.markdown(
#         '<div style="font-size:16px;font-weight:700;margin-bottom:10px;'
#         'color:#181c32;">Power by Plant</div>',
#         unsafe_allow_html=True)
#     plant_df = df.groupby(["plant_name","brand"])["power_kw"].sum().reset_index()
#     fig = px.bar(plant_df, x="plant_name", y="power_kw", color="brand",
#                  color_discrete_map={"Solis":"#2563b0","Growatt":"#1a7a3c","Sungrow":"#b85a10"},
#                  labels={"power_kw":"Power (kW)","plant_name":"","brand":"Brand"})
#     chart_style(fig, 280)
#     st.plotly_chart(fig, use_container_width=True)


# # ═════════════════════════════════════════════════════════════
# # O&M
# # ═════════════════════════════════════════════════════════════
# elif page == "O&M":
#     sub = st.radio("", ["Alarm Information","Device Overview"],
#                    horizontal=True, label_visibility="collapsed")

#     # ── Build alarm list once (used in both sub-pages) ────────
#     alarm_log = get_alert_log(200)
#     all_alarms = []
#     for a in active_alerts:
#         all_alarms.append({
#             "device_type":   "Inverter",
#             "level":         "Critical",
#             "status":        "Active",
#             "plant_name":    a.get("plant_name","—"),
#             "sn":            a.get("inverter_sn","—"),
#             "alarm_content": a.get("issue","—"),
#             "brand":         a.get("brand","—"),
#             "time":          datetime.now().strftime("%Y-%m-%d %H:%M"),
#         })
#     if not alarm_log.empty:
#         for _, row in alarm_log.iterrows():
#             all_alarms.append({
#                 "device_type":   "Inverter",
#                 "level":         "Warning",
#                 "status":        "Resolved",
#                 "plant_name":    row.get("plant_name","—"),
#                 "sn":            row.get("inverter_sn","—"),
#                 "alarm_content": row.get("issue","—"),
#                 "brand":         row.get("brand","—"),
#                 "time":          row.get("alerted_at","—"),
#             })

#     # ── Alarm Information ─────────────────────────────────────
#     if sub == "Alarm Information":
#         st.markdown('<div class="sec-title">Alarm Information</div>', unsafe_allow_html=True)

#         # All dropdown options derived from actual data
#         plant_names = sorted(set(a["plant_name"] for a in all_alarms if a["plant_name"] != "—"))
#         sn_list     = sorted(set(a["sn"]         for a in all_alarms if a["sn"]         != "—"))
#         brand_list  = sorted(set(a["brand"]       for a in all_alarms if a["brand"]      != "—"))

#         fc1, fc2, fc3, fc4 = st.columns(4)
#         with fc1:
#             f_plant  = st.selectbox("Plant Name",  ["All"] + plant_names)
#         with fc2:
#             f_sn     = st.selectbox("SN",          ["All"] + sn_list)
#         with fc3:
#             f_status = st.selectbox("Status",      ["All","Active","Resolved"])
#         with fc4:
#             f_level  = st.selectbox("Alarm Level", ["All","Critical","Warning"])

#         st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

#         # Apply filters
#         filtered = all_alarms[:]
#         if f_plant  != "All": filtered = [a for a in filtered if a["plant_name"] == f_plant]
#         if f_sn     != "All": filtered = [a for a in filtered if a["sn"]         == f_sn]
#         if f_status != "All": filtered = [a for a in filtered if a["status"]     == f_status]
#         if f_level  != "All": filtered = [a for a in filtered if a["level"]      == f_level]

#         if not filtered:
#             st.success("✅ No alarms found — all systems operating normally.")
#         else:
#             st.markdown(f"**{len(filtered)} alarm(s)**")
#             st.markdown("""
#             <div class="alh">
#               <div>Device Type</div><div>Level</div><div>Status</div>
#               <div>Plant Name</div><div>SN</div><div>Alarm Content</div><div>Time</div>
#             </div>""", unsafe_allow_html=True)
#             for a in filtered:
#                 lbadge = ('<span class="badge badge-offline">Critical</span>'
#                           if a["level"] == "Critical"
#                           else '<span class="badge badge-warning">Warning</span>')
#                 sbdg   = ('<span class="badge badge-online">Active</span>'
#                           if a["status"] == "Active"
#                           else '<span class="badge badge-unknown">Resolved</span>')
#                 rcls   = "alr crit" if a["level"] == "Critical" else "alr warn"
#                 st.markdown(
#                     f'<div class="{rcls}">'
#                       f'<div>{a["device_type"]}</div>'
#                       f'<div>{lbadge}</div><div>{sbdg}</div>'
#                       f'<div>{btag(a["brand"])} {a["plant_name"]}</div>'
#                       f'<div style="font-size:11px;color:#a1a5b7;">{a["sn"]}</div>'
#                       f'<div>{a["alarm_content"]}</div>'
#                       f'<div style="font-size:11px;color:#a1a5b7;">{a["time"]}</div>'
#                     f'</div>', unsafe_allow_html=True)

#     # ── Device Overview ───────────────────────────────────────
#     else:
#         st.markdown('<div class="sec-title">Device Overview</div>', unsafe_allow_html=True)
#         st.markdown('<div class="sec-sub">Live readings for every inverter</div>',
#                     unsafe_allow_html=True)

#         if df.empty:
#             st.warning("⚠️ No data. Check credentials and refresh.")
#             st.stop()

#         # Dropdowns from live data
#         brand_opts = ["All"] + sorted(df["brand"].dropna().unique().tolist())
#         plant_opts = ["All"] + sorted(df["plant_name"].dropna().unique().tolist())
#         sn_opts    = ["All"] + sorted(df["inverter_sn"].dropna().unique().tolist())
#         status_opts= ["All"] + sorted(df["status"].dropna().unique().tolist())

#         fc1, fc2, fc3, fc4 = st.columns(4)
#         with fc1: brand_f  = st.selectbox("Brand",   brand_opts,  key="do_brand")
#         with fc2: plant_f  = st.selectbox("Plant",   plant_opts,  key="do_plant")
#         with fc3: sn_f     = st.selectbox("S/N",     sn_opts,     key="do_sn")
#         with fc4: status_f = st.selectbox("Status",  status_opts, key="do_status")

#         view = df.copy()
#         if brand_f  != "All": view = view[view["brand"]        == brand_f]
#         if plant_f  != "All": view = view[view["plant_name"]   == plant_f]
#         if sn_f     != "All": view = view[view["inverter_sn"]  == sn_f]
#         if status_f != "All": view = view[view["status"]       == status_f]

#         st.markdown(f"**{len(view)} inverter(s) shown**")
#         alert_sns = {a.get("inverter_sn") for a in active_alerts}

#         for _, row in view.iterrows():
#             sn    = str(row.get("inverter_sn","N/A"))
#             brand = str(row.get("brand",""))

#             params = [
#                 ("Power Now",   fmt(row.get("power_kw"), 2),  "kW"),
#                 ("Daily Yield", fmt(row.get("today_kwh"), 1), "kWh"),
#                 ("Total Yield", fmt(row.get("total_kwh"), 3), "MWh"),
#                 ("Temperature", fmt(row.get("temperature"),1),"°C"),
#                 ("AC Voltage",  fmt(row.get("voltage"), 1),   "V"),
#                 ("AC Current",  fmt(row.get("current_a"), 1), "A"),
#             ]
#             param_html = "".join(
#                 f'<div><div class="dp-label">{lbl}</div>'
#                 f'<div class="dp-val">{val}<span class="dp-unit"> {unit}</span></div></div>'
#                 for lbl, val, unit in params
#             )
#             border = "border-left:3px solid #e84855;" if sn in alert_sns else ""
#             st.markdown(
#                 f'<div class="device-card" style="{border}">'
#                   f'<div class="device-header">'
#                     f'<div>'
#                       f'<div class="device-name">{row.get("plant_name","")}</div>'
#                       f'<div class="device-sn">S/N: {sn}&nbsp;·&nbsp;{btag(brand)}</div>'
#                     f'</div>'
#                     + sbadge(str(row.get("status",""))) +
#                   f'</div>'
#                   f'<div class="device-grid">{param_html}</div>'
#                   f'<div class="device-footer">⏱ Last update: {row.get("last_update","—")}</div>'
#                 f'</div>', unsafe_allow_html=True)


# # ═════════════════════════════════════════════════════════════
# # REPORT
# # ═════════════════════════════════════════════════════════════
# elif page == "Report":
#     st.markdown('<div class="sec-title">Plant Report</div>', unsafe_allow_html=True)

#     rtype = st.radio("", ["Daily Report","Monthly Report","Annual Report","Total Report"],
#                      horizontal=True, label_visibility="collapsed")
#     st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

#     # Plant dropdown from live data
#     plant_opts = (["All Plants"] + sorted(df["plant_name"].dropna().unique().tolist())
#                   if not df.empty else ["No data"])
#     fc1, fc2 = st.columns([2,1])
#     with fc1: sel_plant = st.selectbox("Select Plant", plant_opts)
#     with fc2: sel_date  = st.date_input("Select Date",  value=date.today())

#     hist_df = get_recent_readings(hours=8760)
#     if hist_df.empty:
#         st.info("📭 No historical data yet — accumulates automatically every 5 minutes.")
#         st.stop()

#     hist_df["fetched_at"] = pd.to_datetime(hist_df["fetched_at"])
#     hist_df["power_kw"]   = pd.to_numeric(hist_df.get("power_kw"),  errors="coerce")
#     hist_df["today_kwh"]  = pd.to_numeric(hist_df.get("today_kwh"), errors="coerce")

#     if sel_plant not in ("All Plants","No data"):
#         hist_df = hist_df[hist_df["plant_name"] == sel_plant]

#     if rtype == "Daily Report":
#         day = hist_df[hist_df["fetched_at"].dt.date == sel_date].sort_values("fetched_at")
#         if day.empty:
#             st.info(f"No data recorded for {sel_date}.")
#         else:
#             fig = px.line(day, x="fetched_at", y="power_kw", color="inverter_sn",
#                           labels={"fetched_at":"Time","power_kw":"Power (kW)","inverter_sn":"Inverter"})
#             chart_style(fig, 320)
#             st.plotly_chart(fig, use_container_width=True)
#             summary = (day.groupby(["plant_name","inverter_sn","brand"])
#                        .agg(Peak_Power_kW=("power_kw","max"),
#                             Daily_Yield_kWh=("today_kwh","max"))
#                        .reset_index()
#                        .rename(columns={"plant_name":"Plant","inverter_sn":"S/N","brand":"Brand"}))
#             st.dataframe(summary, use_container_width=True, hide_index=True)

#     elif rtype == "Monthly Report":
#         mdf = hist_df[(hist_df["fetched_at"].dt.year  == sel_date.year) &
#                       (hist_df["fetched_at"].dt.month == sel_date.month)]
#         if mdf.empty:
#             st.info(f"No data for {sel_date.strftime('%B %Y')}.")
#         else:
#             daily = mdf.groupby(mdf["fetched_at"].dt.date)["today_kwh"].max().reset_index()
#             daily.columns = ["Date","Daily Yield (kWh)"]
#             fig = px.bar(daily, x="Date", y="Daily Yield (kWh)",
#                          color_discrete_sequence=["#f5821f"])
#             chart_style(fig, 300)
#             st.plotly_chart(fig, use_container_width=True)
#             total_m = daily["Daily Yield (kWh)"].sum()
#             st.metric("Month Total", f"{total_m:.1f} kWh", delta=f"≈ {earn(total_m)} earned")

#     elif rtype == "Annual Report":
#         ydf = hist_df[hist_df["fetched_at"].dt.year == sel_date.year]
#         if ydf.empty:
#             st.info(f"No data for {sel_date.year}.")
#         else:
#             monthly = ydf.groupby(ydf["fetched_at"].dt.month)["today_kwh"].sum().reset_index()
#             monthly.columns = ["Month","Total Yield (kWh)"]
#             monthly["Month"] = monthly["Month"].apply(
#                 lambda m: date(sel_date.year, int(m), 1).strftime("%b"))
#             fig = px.bar(monthly, x="Month", y="Total Yield (kWh)",
#                          color_discrete_sequence=["#2563b0"])
#             chart_style(fig, 300)
#             st.plotly_chart(fig, use_container_width=True)

#     else:
#         yearly = hist_df.groupby(hist_df["fetched_at"].dt.year)["today_kwh"].sum().reset_index()
#         yearly.columns = ["Year","Total Yield (kWh)"]
#         fig = px.bar(yearly, x="Year", y="Total Yield (kWh)",
#                      color_discrete_sequence=["#1a7a3c"])
#         chart_style(fig, 280)
#         st.plotly_chart(fig, use_container_width=True)
#         if not df.empty:
#             grand = (df.groupby(["plant_name","brand"])["total_kwh"]
#                      .sum().reset_index()
#                      .rename(columns={"plant_name":"Plant","brand":"Brand",
#                                       "total_kwh":"Total Yield (MWh)"}))
#             st.dataframe(grand, use_container_width=True, hide_index=True)


# # ═════════════════════════════════════════════════════════════
# # SERVICE
# # ═════════════════════════════════════════════════════════════
# elif page == "Service":
#     sub2 = st.radio("", ["Plant Management","Settings"],
#                     horizontal=True, label_visibility="collapsed")

#     if sub2 == "Plant Management":
#         st.markdown('<div class="sec-title">Plant Management</div>', unsafe_allow_html=True)

#         if df.empty:
#             st.warning("⚠️ No data available.")
#             st.stop()

#         # Dropdowns from live data
#         brand_opts2 = ["All"] + sorted(df["brand"].dropna().unique().tolist())
#         plant_opts2 = ["All"] + sorted(df["plant_name"].dropna().unique().tolist())

#         fc1, fc2 = st.columns(2)
#         with fc1: f_name  = st.selectbox("Plant Name", plant_opts2, key="pm_plant")
#         with fc2: f_brand = st.selectbox("Brand",      brand_opts2, key="pm_brand")

#         st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

#         ps = (df.groupby(["plant_name","brand"])
#               .agg(power_kw  =("power_kw",    "sum"),
#                    daily_kwh =("today_kwh",   "sum"),
#                    total_mwh =("total_kwh",   "sum"),
#                    inverters =("inverter_sn", "count"))
#               .reset_index())

#         if f_name  != "All": ps = ps[ps["plant_name"] == f_name]
#         if f_brand != "All": ps = ps[ps["brand"]      == f_brand]

#         st.markdown(f"**Total {len(ps)} plant(s)**")

#         st.markdown('<div class="ptable"><div class="pth">'
#                     '<div>Plant Name</div><div>Brand</div><div>Organisation</div>'
#                     '<div>Inverters</div><div>Power (kW)</div>'
#                     '<div>Daily Yield (kWh)</div><div>Total Yield (MWh)</div><div>Status</div>'
#                     '</div>', unsafe_allow_html=True)

#         for _, row in ps.iterrows():
#             plant_rows = df[df["plant_name"] == row["plant_name"]]
#             has_on  = (plant_rows["status"].str.lower() == "online").any()
#             has_off = plant_rows["status"].str.lower().isin(["offline","fault"]).any()
#             pst     = "Online" if has_on and not has_off else ("Fault" if has_off else "Unknown")
#             inv_total = int(row["inverters"])
#             inv_online= int((plant_rows["status"].str.lower() == "online").sum())
#             st.markdown(
#                 f'<div class="ptr">'
#                   f'<div class="plink">{row["plant_name"]}</div>'
#                   + btag(row["brand"]) +
#                   f'<div>Fractal Energy</div>'
#                   f'<div>{inv_online}/{inv_total}</div>'
#                   f'<div>{fmt(row["power_kw"],2)} kW</div>'
#                   f'<div>{fmt(row["daily_kwh"],1)} kWh</div>'
#                   f'<div>{fmt(row["total_mwh"],3)} MWh</div>'
#                   + sbadge(pst) +
#                 f'</div>', unsafe_allow_html=True)

#         st.markdown('</div>', unsafe_allow_html=True)

#     else:
#         st.markdown('<div class="sec-title">Settings</div>', unsafe_allow_html=True)
#         from config import (SOLIS_API_KEY, GROWATT_USERNAME,
#                             SUNGROW_APP_KEY, EMAIL_USER, TO_EMAILS)
#         st.markdown("#### API Credentials")
#         for brand, ok, hint in [
#             ("Solis",   bool(SOLIS_API_KEY),
#              SOLIS_API_KEY[:8]+"…" if SOLIS_API_KEY else "Not configured"),
#             ("Growatt", bool(GROWATT_USERNAME),
#              GROWATT_USERNAME or "Set GROWATT_USERNAME in config.py"),
#             ("Sungrow", bool(SUNGROW_APP_KEY),
#              SUNGROW_APP_KEY[:8]+"…" if SUNGROW_APP_KEY else "Set SUNGROW_APP_KEY in config.py"),
#         ]:
#             c1,c2,c3 = st.columns([1,1,3])
#             c1.markdown(f"**{brand}**")
#             c2.markdown("✅ OK" if ok else "⚠️ Not set")
#             c3.markdown(f"`{hint}`")
#         st.divider()
#         st.markdown("#### Email Alerts")
#         st.markdown(f"**From:** `{EMAIL_USER}`")
#         st.markdown(f"**To:** `{', '.join(TO_EMAILS)}`")
#         st.divider()
#         st.info("Earnings rate: ₹4.00 / kWh — edit the `earn()` function in app.py to adjust.")

# ============================================================
#  app.py  —  Solar Dashboard  |  streamlit run app.py
# ============================================================
# import streamlit as st
# from streamlit_autorefresh import st_autorefresh
# import pandas as pd
# import plotly.express as px
# import plotly.graph_objects as go
# from datetime import datetime, date, timedelta

# from config import REFRESH_INTERVAL_SECONDS, RATE_PER_KWH
# from utils.database import init_db, get_history, get_alert_log
# from utils.aggregator import fetch_all_brands, check_alerts

# # ─────────────────────────────────────────────────────────────
# st.set_page_config(page_title="Solar Dashboard", page_icon="☀️",
#                    layout="wide", initial_sidebar_state="expanded")

# st.markdown("""
# <style>
# @import url('https://fonts.googleapis.com/css2?family=Inter:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800&display=swap');

# *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

# :root {
#   --bg:       #f5f6fa;
#   --card:     #ffffff;
#   --border:   #e8eaf0;
#   --sidebar:  #1a1d2e;
#   --sidebar2: #252840;
#   --accent:   #f5821f;
#   --accent-l: #fff4eb;
#   --green:    #22c55e;
#   --green-l:  #dcfce7;
#   --red:      #ef4444;
#   --red-l:    #fee2e2;
#   --yellow:   #f59e0b;
#   --yellow-l: #fef3c7;
#   --blue:     #3b82f6;
#   --blue-l:   #dbeafe;
#   --text:     #0f172a;
#   --text2:    #64748b;
#   --text3:    #94a3b8;
#   --shadow:   0 1px 3px rgba(0,0,0,.08), 0 4px 16px rgba(0,0,0,.04);
#   --shadow-lg:0 8px 32px rgba(0,0,0,.10);
# }

# html, body, [data-testid="stAppViewContainer"] {
#   background: var(--bg) !important;
#   font-family: 'Inter', sans-serif !important;
#   color: var(--text);
# }
# [data-testid="stHeader"]  { background: transparent !important; display: none; }
# [data-testid="stSidebar"] { background: var(--sidebar) !important; }
# [data-testid="stSidebar"] > div { padding-top: 0 !important; }
# section[data-testid="stSidebarContent"] { padding: 0 !important; }
# #MainMenu, footer { visibility: hidden; }
# [data-testid="stDecoration"] { display: none; }
# .block-container { padding: 28px 32px !important; max-width: 100% !important; }

# /* ── Sidebar nav ── */
# .nav-logo {
#   padding: 24px 20px 20px;
#   border-bottom: 1px solid rgba(255,255,255,.08);
#   margin-bottom: 8px;
# }
# .nav-logo-icon {
#   width: 40px; height: 40px; background: var(--accent);
#   border-radius: 10px; display: flex; align-items: center;
#   justify-content: center; font-size: 20px; margin-bottom: 10px;
# }
# .nav-logo-title { color: #fff; font-weight: 700; font-size: 16px; }
# .nav-logo-sub   { color: #6b7280; font-size: 12px; margin-top: 2px; }

# .nav-section {
#   padding: 6px 16px 4px;
#   font-size: 10px; font-weight: 600; color: #4b5563;
#   text-transform: uppercase; letter-spacing: .1em;
# }

# /* ── KPI cards ── */
# .kpi-grid { display: grid; grid-template-columns: repeat(4,1fr); gap: 16px; margin-bottom: 24px; }
# .kpi-card {
#   background: var(--card); border-radius: 14px; padding: 22px 20px;
#   border: 1px solid var(--border); box-shadow: var(--shadow);
#   display: flex; gap: 14px; align-items: flex-start;
#   transition: box-shadow .2s;
# }
# .kpi-card:hover { box-shadow: var(--shadow-lg); }
# .kpi-icon {
#   width: 48px; height: 48px; border-radius: 12px; flex-shrink: 0;
#   display: flex; align-items: center; justify-content: center; font-size: 22px;
# }
# .kpi-body { flex: 1; min-width: 0; }
# .kpi-label { font-size: 12px; color: var(--text2); font-weight: 500;
#              text-transform: uppercase; letter-spacing: .06em; margin-bottom: 6px; }
# .kpi-value { font-size: 26px; font-weight: 700; color: var(--text); line-height: 1; }
# .kpi-unit  { font-size: 13px; font-weight: 500; color: var(--text2); margin-left: 3px; }
# .kpi-meta  { font-size: 12px; color: var(--text3); margin-top: 7px; }
# .kpi-meta b { color: var(--text2); font-weight: 500; }

# /* ── Page header ── */
# .page-hdr { margin-bottom: 24px; }
# .page-hdr h1 { font-size: 22px; font-weight: 700; color: var(--text); }
# .page-hdr p  { font-size: 13px; color: var(--text2); margin-top: 4px; }

# /* ── Section header ── */
# .sec-hdr {
#   font-size: 14px; font-weight: 600; color: var(--text);
#   margin-bottom: 14px; padding-bottom: 10px;
#   border-bottom: 1px solid var(--border);
#   display: flex; align-items: center; gap: 8px;
# }

# /* ── Card wrapper ── */
# .card {
#   background: var(--card); border-radius: 14px; padding: 20px 22px;
#   border: 1px solid var(--border); box-shadow: var(--shadow); margin-bottom: 16px;
# }
# .card-title {
#   font-size: 15px; font-weight: 600; color: var(--text);
#   margin-bottom: 16px; padding-bottom: 12px; border-bottom: 1px solid var(--border);
# }

# /* ── Inverter card ── */
# .inv-card {
#   background: var(--card); border-radius: 14px; padding: 20px 22px;
#   border: 1px solid var(--border); box-shadow: var(--shadow);
#   margin-bottom: 14px; transition: border-color .15s, box-shadow .15s;
# }
# .inv-card:hover { border-color: var(--accent); box-shadow: var(--shadow-lg); }
# .inv-card.alert { border-left: 3px solid var(--red); }
# .inv-header {
#   display: flex; justify-content: space-between; align-items: flex-start;
#   margin-bottom: 16px; padding-bottom: 14px; border-bottom: 1px solid var(--border);
# }
# .inv-name { font-size: 15px; font-weight: 700; color: var(--text); }
# .inv-meta { font-size: 11px; color: var(--text3); margin-top: 3px; }
# .inv-params { display: grid; grid-template-columns: repeat(6,1fr); gap: 14px; }
# .param-label { font-size: 10px; color: var(--text2); text-transform: uppercase;
#                letter-spacing: .07em; margin-bottom: 3px; }
# .param-val   { font-size: 16px; font-weight: 600; color: var(--text); }
# .param-unit  { font-size: 11px; color: var(--text3); margin-left: 2px; }
# .inv-footer  { margin-top: 12px; font-size: 11px; color: var(--text3); }

# /* ── Table ── */
# .tbl { background: var(--card); border-radius: 14px; border: 1px solid var(--border);
#        overflow: hidden; box-shadow: var(--shadow); }
# .tbl-hdr, .tbl-row {
#   display: grid; padding: 0 20px; align-items: center; gap: 10px;
# }
# .tbl-hdr {
#   background: #f8fafc; border-bottom: 1px solid var(--border);
#   font-size: 11px; font-weight: 600; color: var(--text2);
#   text-transform: uppercase; letter-spacing: .07em; height: 42px;
# }
# .tbl-row {
#   min-height: 52px; border-bottom: 1px solid var(--border);
#   font-size: 13px; transition: background .1s;
# }
# .tbl-row:last-child { border-bottom: none; }
# .tbl-row:hover { background: #fafbfc; }
# .tbl-plant  { grid-template-columns: 2fr 1fr 1.1fr 1fr 1fr 1.1fr 1.3fr 1fr; }
# .tbl-alarm  { grid-template-columns: 1fr 1fr 1fr 1.5fr 1.4fr 2.2fr 1.2fr; }
# .cell-link  { color: var(--accent); font-weight: 600; cursor: pointer; }
# .cell-link:hover { text-decoration: underline; }

# /* ── Badges ── */
# .badge {
#   display: inline-flex; align-items: center; gap: 5px;
#   font-size: 11px; font-weight: 600; padding: 3px 10px; border-radius: 20px;
# }
# .badge::before { content:''; width:6px; height:6px; border-radius:50%; }
# .b-online  { background: var(--green-l);  color: #15803d; }
# .b-online::before  { background: var(--green); }
# .b-offline { background: var(--red-l);    color: #b91c1c; }
# .b-offline::before { background: var(--red); }
# .b-warning { background: var(--yellow-l); color: #92400e; }
# .b-warning::before { background: var(--yellow); }
# .b-unknown { background: #f1f5f9; color: #64748b; }
# .b-unknown::before { background: #94a3b8; }
# .b-active  { background: var(--red-l);    color: #b91c1c; }
# .b-active::before  { background: var(--red); }
# .b-resolved{ background: var(--green-l);  color: #15803d; }
# .b-resolved::before{ background: var(--green); }
# .b-critical{ background: var(--red-l);    color: #b91c1c; font-weight:700; }
# .b-critical::before{ background: var(--red); }

# /* ── Brand chips ── */
# .chip {
#   display: inline-block; font-size: 10px; font-weight: 700; padding: 2px 8px;
#   border-radius: 5px; letter-spacing: .08em; text-transform: uppercase;
# }
# .chip-solis   { background: #dbeafe; color: #1d4ed8; }
# .chip-growatt { background: #dcfce7; color: #15803d; }
# .chip-sungrow { background: #ffedd5; color: #c2410c; }

# /* ── Alert strip ── */
# .alert-strip {
#   background: #fef2f2; border: 1px solid #fecaca; border-radius: 10px;
#   padding: 14px 18px; margin-bottom: 18px; display: flex; gap: 12px; align-items: flex-start;
# }
# .alert-strip-ico { font-size: 18px; flex-shrink: 0; }
# .alert-strip-ttl { font-size: 14px; font-weight: 600; color: var(--red); }
# .alert-strip-msg { font-size: 13px; color: #7f1d1d; margin-top: 2px; }

# /* ── Stat row (summary bar) ── */
# .stat-row {
#   background: var(--card); border-radius: 12px; padding: 14px 22px;
#   border: 1px solid var(--border); display: flex; gap: 28px; margin-bottom: 20px;
#   align-items: center; flex-wrap: wrap;
# }
# .stat-item { text-align: center; }
# .stat-val { font-size: 18px; font-weight: 700; color: var(--text); }
# .stat-lbl { font-size: 11px; color: var(--text3); margin-top: 2px; }

# /* ── Streamlit overrides ── */
# .stButton > button {
#   background: var(--accent) !important; color: #fff !important;
#   border: none !important; border-radius: 8px !important;
#   font-family: 'Inter', sans-serif !important; font-weight: 600 !important;
#   font-size: 13px !important; padding: 9px 22px !important;
#   transition: opacity .15s !important;
# }
# .stButton > button:hover { opacity: .88 !important; }
# div[data-testid="stSelectbox"] > label,
# div[data-testid="stTextInput"]  > label { font-size: 12px !important; font-weight: 500 !important; }
# [data-testid="stRadio"] > label { font-size: 13px !important; }
# .stRadio > div { gap: 4px !important; }
# .stAlert { border-radius: 10px !important; }
# </style>
# """, unsafe_allow_html=True)

# # ── Bootstrap ─────────────────────────────────────────────────
# init_db()
# st_autorefresh(interval=REFRESH_INTERVAL_SECONDS * 1000, key="solar_ar")

# # ── Helpers ──────────────────────────────────────────────────
# def f(v, d=1, na="—"):
#     try:    return f"{float(v):.{d}f}"
#     except: return na

# def badge(s, kind=None):
#     s = (s or "").strip()
#     sl = s.lower()
#     if kind == "level":
#         cls = "b-critical" if sl == "critical" else "b-warning"
#     elif kind == "status_alarm":
#         cls = "b-active" if sl == "active" else "b-resolved"
#     else:
#         if sl == "online":            cls = "b-online"
#         elif sl in ("offline","fault"): cls = "b-offline"
#         else:                          cls = "b-unknown"
#     return f'<span class="badge {cls}">{s}</span>'

# def chip(b):
#     return f'<span class="chip chip-{(b or "").lower()}">{b}</span>'

# def earn(kwh):
#     v = float(kwh or 0) * RATE_PER_KWH
#     if v >= 1_000_000: return f"₹{v/1_000_000:.3f}M"
#     if v >= 1_000:     return f"₹{v/1_000:.3f}K"
#     return f"₹{v:.2f}"

# def chart(fig, h=300):
#     fig.update_layout(plot_bgcolor="#fff", paper_bgcolor="#fff", font_color="#64748b",
#                       margin=dict(l=0,r=0,t=10,b=0), height=h,
#                       legend=dict(bgcolor="#fff", font=dict(size=12)),
#                       bargap=0.3, font_family="Inter")
#     fig.update_traces(marker_line_width=0)
#     fig.update_xaxes(showgrid=False, zeroline=False, tickfont_size=11)
#     fig.update_yaxes(showgrid=True, gridcolor="#f1f5f9", zeroline=False, tickfont_size=11)
#     return fig

# BRAND_COLORS = {"Solis":"#3b82f6","Growatt":"#22c55e","Sungrow":"#f5821f"}

# # ── Sidebar ──────────────────────────────────────────────────
# with st.sidebar:
#     st.markdown("""
#     <div class="nav-logo">
#       <div class="nav-logo-icon">☀</div>
#       <div class="nav-logo-title">Solar Dashboard</div>
#       <div class="nav-logo-sub">Fractal Energy</div>
#     </div>""", unsafe_allow_html=True)

#     page = st.radio("", ["📊  Overview","🔧  O&M","📈  Report","🗺  Service","⚙️  Settings"],
#                     label_visibility="collapsed")
#     page = page.split("  ",1)[1].strip()

#     st.markdown('<div class="nav-section">Data Sources</div>', unsafe_allow_html=True)
#     sel_brands = [b for b in ["Solis","Growatt","Sungrow"]
#                   if st.checkbox(b, value=(b=="Solis"), key=f"cb_{b}")]

#     st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)
#     if st.button("🔄 Refresh Now"):
#         st.cache_data.clear(); st.rerun()

#     show_debug = st.checkbox("🔍 Debug mode", value=False)

#     st.markdown(
#         f"<div style='padding:16px;font-size:11px;color:#4b5563;border-top:1px solid "
#         f"rgba(255,255,255,.08);margin-top:12px;'>"
#         f"⏱ {datetime.now().strftime('%d %b %Y  %H:%M:%S')}<br>"
#         f"Auto-refresh every {REFRESH_INTERVAL_SECONDS//60} min</div>",
#         unsafe_allow_html=True)

# # ── Fetch + clean data ────────────────────────────────────────
# @st.cache_data(ttl=REFRESH_INTERVAL_SECONDS)
# def load(brands):
#     return fetch_all_brands(list(brands))

# with st.spinner("Fetching live data…"):
#     records = load(tuple(sel_brands))

# alerts = check_alerts(records, st.session_state)

# df = pd.DataFrame()
# if records:
#     df = pd.DataFrame(records)
#     for c in ["power_kw","today_kwh","total_kwh","temperature","voltage","current_a"]:
#         if c in df.columns:
#             df[c] = pd.to_numeric(df[c], errors="coerce")
#     if "status" in df.columns:
#         df["status"] = df["status"].astype(str).str.strip()

# # ── Debug ────────────────────────────────────────────────────
# if show_debug and not df.empty:
#     st.markdown("### 🔍 Debug: Raw API Data")
#     st.dataframe(df, use_container_width=True)
#     st.write("**power_kw values:**", df["power_kw"].tolist())
#     st.write("**today_kwh values:**", df["today_kwh"].tolist())
#     st.write("**total_kwh values (MWh):**", df["total_kwh"].tolist())
#     st.divider()


# # ═════════════════════════════════════════════════════════════
# #  OVERVIEW
# # ═════════════════════════════════════════════════════════════
# if page == "Overview":
#     st.markdown('<div class="page-hdr"><h1>Plant Overview</h1>'
#                 '<p>Real-time performance across all plants</p></div>',
#                 unsafe_allow_html=True)

#     if df.empty:
#         st.warning("⚠️ No data. Verify credentials in config.py and click Refresh.")
#         if not show_debug:
#             st.info("💡 Enable **Debug mode** in the sidebar to inspect the API response.")
#         st.stop()

#     # ── KPI values ───────────────────────────────────────────
#     total_power = float(df["power_kw"].sum())
#     daily_kwh   = float(df["today_kwh"].sum())
#     # total_kwh stores MWh (Solis etotal unit)
#     total_mwh   = float(df["total_kwh"].sum())

#     # Monthly from DB; floor = today
#     hist = get_history(hours=720)
#     monthly_kwh = daily_kwh
#     if not hist.empty and "today_kwh" in hist.columns:
#         hist["fetched_at"] = pd.to_datetime(hist["fetched_at"])
#         hist["today_kwh"]  = pd.to_numeric(hist["today_kwh"], errors="coerce")
#         m = hist[hist["fetched_at"].dt.month == datetime.now().month]
#         if not m.empty:
#             v = float(m.groupby([m["fetched_at"].dt.date,"inverter_sn"])["today_kwh"].max().sum())
#             monthly_kwh = max(v, daily_kwh)

#     n_on = int((df["status"].str.lower()=="online").sum())
#     n_tot= len(df)

#     # Capacity from Solis plant data — use power_kw as a proxy display
#     col1,col2,col3,col4 = st.columns(4)
#     kpis = [
#         (col1,"⚡","power","Power",f(total_power,2),"kW",
#          f"Inverters: <b>{n_on}/{n_tot} online</b>"),
#         (col2,"🔋","daily","Daily Yield",f(daily_kwh,1),"kWh",
#          f"Earning today: <b>{earn(daily_kwh)}</b>"),
#         (col3,"📅","monthly","Monthly Yield",
#          f(monthly_kwh/1000,3) if monthly_kwh>=1000 else f(monthly_kwh,1),
#          "MWh" if monthly_kwh>=1000 else "kWh",
#          f"Earning this month: <b>{earn(monthly_kwh)}</b>"),
#         (col4,"📊","total","Total Yield",f(total_mwh,3),"MWh",
#          f"Total earning: <b>{earn(total_mwh*1000)}</b>"),
#     ]
#     icon_bg = {"power":"#fff4eb","daily":"#fff4eb","monthly":"#eff6ff","total":"#fffbeb"}
#     for col,ico,kind,lbl,val,unit,meta in kpis:
#         with col:
#             st.markdown(f"""
#             <div class="kpi-card">
#               <div class="kpi-icon" style="background:{icon_bg[kind]};">{ico}</div>
#               <div class="kpi-body">
#                 <div class="kpi-label">{lbl}</div>
#                 <div class="kpi-value">{val}<span class="kpi-unit">{unit}</span></div>
#                 <div class="kpi-meta">{meta}</div>
#               </div>
#             </div>""", unsafe_allow_html=True)

#     # ── Alert strip ───────────────────────────────────────────
#     if alerts:
#         for a in alerts[:3]:
#             st.markdown(f"""
#             <div class="alert-strip">
#               <div class="alert-strip-ico">🚨</div>
#               <div>
#                 <div class="alert-strip-ttl">{a['plant_name']} — {a.get('inverter_sn','')}</div>
#                 <div class="alert-strip-msg">{a['issue']}</div>
#               </div>
#             </div>""", unsafe_allow_html=True)

#     # ── Charts row ────────────────────────────────────────────
#     ch1, ch2 = st.columns([3,2])

#     with ch1:
#         st.markdown('<div class="sec-hdr">⚡ Power by Plant (kW)</div>', unsafe_allow_html=True)
#         pdf = df.groupby(["plant_name","brand"])["power_kw"].sum().reset_index()
#         fig = px.bar(pdf, x="plant_name", y="power_kw", color="brand",
#                      color_discrete_map=BRAND_COLORS,
#                      labels={"power_kw":"Power (kW)","plant_name":"","brand":"Brand"})
#         st.plotly_chart(chart(fig,280), use_container_width=True)

#     with ch2:
#         st.markdown('<div class="sec-hdr">📊 Daily Yield Share</div>', unsafe_allow_html=True)
#         pief = df.groupby("plant_name")["today_kwh"].sum().reset_index()
#         fig2 = px.pie(pief, names="plant_name", values="today_kwh",
#                       color_discrete_sequence=px.colors.qualitative.Pastel,
#                       hole=0.45)
#         fig2.update_traces(textposition="outside", textinfo="label+percent")
#         fig2.update_layout(plot_bgcolor="#fff", paper_bgcolor="#fff",
#                            font_family="Inter", font_color="#64748b",
#                            margin=dict(l=0,r=0,t=10,b=0), height=280,
#                            showlegend=False)
#         st.plotly_chart(fig2, use_container_width=True)

#     # ── Plant summary table ───────────────────────────────────
#     st.markdown('<div class="sec-hdr" style="margin-top:8px;">🌱 Plant List</div>',
#                 unsafe_allow_html=True)

#     ps = (df.groupby(["plant_name","brand"])
#           .agg(power_kw=("power_kw","sum"),
#                today_kwh=("today_kwh","sum"),
#                total_kwh=("total_kwh","sum"),
#                inv_count=("inverter_sn","count"))
#           .reset_index())

#     st.markdown('<div class="tbl">', unsafe_allow_html=True)
#     st.markdown(
#         '<div class="tbl-hdr tbl-plant">'
#         '<div>Plant Name</div><div>Brand</div><div>Inverters</div>'
#         '<div>Power (kW)</div><div>Daily Yield</div>'
#         '<div>Total Yield</div><div>Earning Today</div><div>Status</div>'
#         '</div>', unsafe_allow_html=True)

#     for _, row in ps.iterrows():
#         pr = df[df["plant_name"]==row["plant_name"]]
#         on = int((pr["status"].str.lower()=="online").sum())
#         tot= int(row["inv_count"])
#         pst= "Online" if on==tot and tot>0 else ("Offline" if on==0 else "Warning")
#         st.markdown(
#             f'<div class="tbl-row tbl-plant">'
#               f'<div class="cell-link">{row["plant_name"]}</div>'
#               f'<div>{chip(row["brand"])}</div>'
#               f'<div>{on}/{tot}</div>'
#               f'<div><b>{f(row["power_kw"],2)}</b> kW</div>'
#               f'<div>{f(row["today_kwh"],1)} kWh</div>'
#               f'<div>{f(row["total_kwh"],3)} MWh</div>'
#               f'<div>{earn(row["today_kwh"])}</div>'
#               f'<div>{badge(pst)}</div>'
#             f'</div>', unsafe_allow_html=True)
#     st.markdown('</div>', unsafe_allow_html=True)


# # ═════════════════════════════════════════════════════════════
# #  O&M
# # ═════════════════════════════════════════════════════════════
# elif page == "O&M":
#     sub = st.radio("", ["🔔  Alarm Information","⚡  Device Overview"],
#                    horizontal=True, label_visibility="collapsed")
#     sub = sub.split("  ",1)[1].strip()
#     st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

#     # Build alarm list
#     alarm_log = get_alert_log(200)
#     all_alarms = []
#     for a in alerts:
#         all_alarms.append({"device_type":"Inverter","level":"Critical","status":"Active",
#             "plant_name":a.get("plant_name","—"),"sn":a.get("inverter_sn","—"),
#             "content":a.get("issue","—"),"brand":a.get("brand","—"),
#             "time":datetime.now().strftime("%Y-%m-%d %H:%M")})
#     if not alarm_log.empty:
#         for _, r in alarm_log.iterrows():
#             all_alarms.append({"device_type":"Inverter","level":"Warning","status":"Resolved",
#                 "plant_name":r.get("plant_name","—"),"sn":r.get("inverter_sn","—"),
#                 "content":r.get("issue","—"),"brand":r.get("brand","—"),
#                 "time":r.get("alerted_at","—")})

#     # ── Alarm Information ─────────────────────────────────────
#     if sub == "Alarm Information":
#         st.markdown('<div class="page-hdr"><h1>Alarm Information</h1>'
#                     '<p>All detected faults and alert history</p></div>',
#                     unsafe_allow_html=True)

#         plant_opts = ["All"] + sorted({a["plant_name"] for a in all_alarms if a["plant_name"]!="—"})
#         sn_opts    = ["All"] + sorted({a["sn"]         for a in all_alarms if a["sn"]        !="—"})
#         brand_opts = ["All"] + sorted({a["brand"]       for a in all_alarms if a["brand"]     !="—"})

#         with st.container():
#             fc1,fc2,fc3,fc4,fc5 = st.columns(5)
#             with fc1: fp = st.selectbox("Plant Name",  plant_opts)
#             with fc2: fs = st.selectbox("SN",          sn_opts)
#             with fc3: fb = st.selectbox("Brand",       brand_opts)
#             with fc4: fst= st.selectbox("Status",      ["All","Active","Resolved"])
#             with fc5: fl = st.selectbox("Level",       ["All","Critical","Warning"])

#         filt = all_alarms[:]
#         if fp  !="All": filt=[a for a in filt if a["plant_name"]==fp]
#         if fs  !="All": filt=[a for a in filt if a["sn"]        ==fs]
#         if fb  !="All": filt=[a for a in filt if a["brand"]     ==fb]
#         if fst !="All": filt=[a for a in filt if a["status"]    ==fst]
#         if fl  !="All": filt=[a for a in filt if a["level"]     ==fl]

#         # Summary counts
#         n_active  = sum(1 for a in filt if a["status"]=="Active")
#         n_resolved= sum(1 for a in filt if a["status"]=="Resolved")
#         sc1,sc2,sc3 = st.columns(3)
#         sc1.metric("Total Alarms",    len(filt))
#         sc2.metric("Active",   n_active,   delta_color="inverse")
#         sc3.metric("Resolved", n_resolved)

#         if not filt:
#             st.success("✅ No alarms match the current filters — all systems normal.")
#         else:
#             st.markdown('<div class="tbl">', unsafe_allow_html=True)
#             st.markdown(
#                 '<div class="tbl-hdr tbl-alarm">'
#                 '<div>Device Type</div><div>Level</div><div>Status</div>'
#                 '<div>Plant Name</div><div>SN</div><div>Issue</div><div>Time</div>'
#                 '</div>', unsafe_allow_html=True)
#             for a in filt:
#                 st.markdown(
#                     f'<div class="tbl-row tbl-alarm">'
#                       f'<div>{a["device_type"]}</div>'
#                       f'<div>{badge(a["level"],"level")}</div>'
#                       f'<div>{badge(a["status"],"status_alarm")}</div>'
#                       f'<div>{chip(a["brand"])} {a["plant_name"]}</div>'
#                       f'<div style="font-size:11px;color:var(--text3);">{a["sn"]}</div>'
#                       f'<div>{a["content"]}</div>'
#                       f'<div style="font-size:11px;color:var(--text3);">{a["time"]}</div>'
#                     f'</div>', unsafe_allow_html=True)
#             st.markdown('</div>', unsafe_allow_html=True)

#     # ── Device Overview ───────────────────────────────────────
#     else:
#         st.markdown('<div class="page-hdr"><h1>Device Overview</h1>'
#                     '<p>Live readings for every inverter</p></div>',
#                     unsafe_allow_html=True)
#         if df.empty:
#             st.warning("⚠️ No data."); st.stop()

#         brand_opts2 = ["All"] + sorted(df["brand"].dropna().unique())
#         plant_opts2 = ["All"] + sorted(df["plant_name"].dropna().unique())
#         sn_opts2    = ["All"] + sorted(df["inverter_sn"].dropna().unique())
#         stat_opts2  = ["All"] + sorted(df["status"].dropna().unique())

#         fc1,fc2,fc3,fc4 = st.columns(4)
#         with fc1: bf = st.selectbox("Brand",  brand_opts2, key="do_b")
#         with fc2: pf = st.selectbox("Plant",  plant_opts2, key="do_p")
#         with fc3: sf = st.selectbox("S/N",    sn_opts2,    key="do_s")
#         with fc4: stf= st.selectbox("Status", stat_opts2,  key="do_st")

#         vw = df.copy()
#         if bf !="All": vw=vw[vw["brand"]       ==bf]
#         if pf !="All": vw=vw[vw["plant_name"]  ==pf]
#         if sf !="All": vw=vw[vw["inverter_sn"] ==sf]
#         if stf!="All": vw=vw[vw["status"]      ==stf]

#         # Summary strip
#         st.markdown(
#             f'<div class="stat-row">'
#               f'<div class="stat-item"><div class="stat-val">{len(vw)}</div>'
#               f'<div class="stat-lbl">Inverters</div></div>'
#               f'<div class="stat-item"><div class="stat-val">'
#               f'{f(vw["power_kw"].sum(),2)} kW</div>'
#               f'<div class="stat-lbl">Total Power</div></div>'
#               f'<div class="stat-item"><div class="stat-val">'
#               f'{f(vw["today_kwh"].sum(),1)} kWh</div>'
#               f'<div class="stat-lbl">Daily Yield</div></div>'
#               f'<div class="stat-item"><div class="stat-val">'
#               f'{int((vw["status"].str.lower()=="online").sum())}</div>'
#               f'<div class="stat-lbl">Online</div></div>'
#             f'</div>', unsafe_allow_html=True)

#         alert_sns = {a.get("inverter_sn") for a in alerts}
#         for _, row in vw.iterrows():
#             sn    = str(row.get("inverter_sn","N/A"))
#             brand = str(row.get("brand",""))
#             st_   = str(row.get("status",""))
#             params = [
#                 ("Power Now",   f(row.get("power_kw"),2),  "kW"),
#                 ("Daily Yield", f(row.get("today_kwh"),1), "kWh"),
#                 ("Total Yield", f(row.get("total_kwh"),3), "MWh"),
#                 ("Temperature", f(row.get("temperature"),1),"°C"),
#                 ("AC Voltage",  f(row.get("voltage"),1),   "V"),
#                 ("AC Current",  f(row.get("current_a"),1), "A"),
#             ]
#             p_html = "".join(
#                 f'<div><div class="param-label">{l}</div>'
#                 f'<div class="param-val">{v}<span class="param-unit"> {u}</span></div></div>'
#                 for l,v,u in params)
#             a_cls = "inv-card alert" if sn in alert_sns else "inv-card"
#             st.markdown(
#                 f'<div class="{a_cls}">'
#                   f'<div class="inv-header">'
#                     f'<div><div class="inv-name">{row.get("plant_name","")}</div>'
#                     f'<div class="inv-meta">S/N: {sn} &nbsp;·&nbsp; {chip(brand)}'
#                     f' &nbsp;·&nbsp; {row.get("last_update","—")}</div></div>'
#                     + badge(st_) +
#                   f'</div>'
#                   f'<div class="inv-params">{p_html}</div>'
#                 f'</div>', unsafe_allow_html=True)


# # ═════════════════════════════════════════════════════════════
# #  REPORT
# # ═════════════════════════════════════════════════════════════
# elif page == "Report":
#     st.markdown('<div class="page-hdr"><h1>Plant Report</h1>'
#                 '<p>Historical generation analysis</p></div>',
#                 unsafe_allow_html=True)

#     rtype = st.radio("", ["Daily","Monthly","Annual","Total"],
#                      horizontal=True, label_visibility="collapsed")

#     plant_opts = (["All Plants"] + sorted(df["plant_name"].dropna().unique())
#                   if not df.empty else ["No data"])
#     fc1,fc2 = st.columns([2,1])
#     with fc1: sel_plant = st.selectbox("Select Plant", plant_opts)
#     with fc2: sel_date  = st.date_input("Date", value=date.today())

#     hist_df = get_history(hours=8760)
#     if hist_df.empty:
#         st.info("📭 No history yet — data accumulates every 5 minutes. Come back soon.")
#         st.stop()

#     hist_df["fetched_at"] = pd.to_datetime(hist_df["fetched_at"])
#     hist_df["power_kw"]   = pd.to_numeric(hist_df.get("power_kw"), errors="coerce")
#     hist_df["today_kwh"]  = pd.to_numeric(hist_df.get("today_kwh"),errors="coerce")
#     hist_df["total_kwh"]  = pd.to_numeric(hist_df.get("total_kwh"),errors="coerce")

#     if sel_plant != "All Plants":
#         hist_df = hist_df[hist_df["plant_name"]==sel_plant]

#     if rtype == "Daily":
#         day = hist_df[hist_df["fetched_at"].dt.date==sel_date].sort_values("fetched_at")
#         if day.empty:
#             st.info(f"No data for {sel_date}.")
#         else:
#             fig = px.line(day, x="fetched_at", y="power_kw", color="inverter_sn",
#                           labels={"fetched_at":"Time","power_kw":"Power (kW)","inverter_sn":"Inverter"})
#             st.plotly_chart(chart(fig,320), use_container_width=True)
#             sm = (day.groupby(["plant_name","inverter_sn","brand"])
#                   .agg(Peak_kW=("power_kw","max"), Daily_kWh=("today_kwh","max"))
#                   .reset_index())
#             sm.columns = ["Plant","S/N","Brand","Peak Power (kW)","Daily Yield (kWh)"]
#             st.dataframe(sm, use_container_width=True, hide_index=True)

#     elif rtype == "Monthly":
#         mdf = hist_df[(hist_df["fetched_at"].dt.year==sel_date.year) &
#                       (hist_df["fetched_at"].dt.month==sel_date.month)]
#         if mdf.empty:
#             st.info(f"No data for {sel_date.strftime('%B %Y')}.")
#         else:
#             daily = mdf.groupby(mdf["fetched_at"].dt.date)["today_kwh"].max().reset_index()
#             daily.columns = ["Date","Daily Yield (kWh)"]
#             fig = px.bar(daily, x="Date", y="Daily Yield (kWh)",
#                          color_discrete_sequence=[BRAND_COLORS["Solis"]])
#             st.plotly_chart(chart(fig,300), use_container_width=True)
#             tot = daily["Daily Yield (kWh)"].sum()
#             m1,m2 = st.columns(2)
#             m1.metric("Month Total", f"{tot:.1f} kWh")
#             m2.metric("Estimated Earning", earn(tot))

#     elif rtype == "Annual":
#         ydf = hist_df[hist_df["fetched_at"].dt.year==sel_date.year]
#         if ydf.empty:
#             st.info(f"No data for {sel_date.year}.")
#         else:
#             monthly = ydf.groupby(ydf["fetched_at"].dt.month)["today_kwh"].sum().reset_index()
#             monthly.columns = ["Month","kWh"]
#             monthly["Month"] = monthly["Month"].apply(
#                 lambda m: date(sel_date.year,int(m),1).strftime("%b"))
#             fig = px.bar(monthly, x="Month", y="kWh", color_discrete_sequence=["#3b82f6"])
#             st.plotly_chart(chart(fig,300), use_container_width=True)

#     else:  # Total
#         yearly = hist_df.groupby(hist_df["fetched_at"].dt.year)["today_kwh"].sum().reset_index()
#         yearly.columns = ["Year","kWh"]
#         fig = px.bar(yearly, x="Year", y="kWh", color_discrete_sequence=["#22c55e"])
#         st.plotly_chart(chart(fig,280), use_container_width=True)
#         if not df.empty:
#             gt = (df.groupby(["plant_name","brand"])["total_kwh"].sum().reset_index()
#                   .rename(columns={"plant_name":"Plant","brand":"Brand","total_kwh":"Total Yield (MWh)"}))
#             st.dataframe(gt, use_container_width=True, hide_index=True)


# # ═════════════════════════════════════════════════════════════
# #  SERVICE  (Plant Management)
# # ═════════════════════════════════════════════════════════════
# elif page == "Service":
#     st.markdown('<div class="page-hdr"><h1>Plant Management</h1>'
#                 '<p>All registered plants and their details</p></div>',
#                 unsafe_allow_html=True)

#     if df.empty:
#         st.warning("⚠️ No data."); st.stop()

#     brand_opts = ["All"] + sorted(df["brand"].dropna().unique())
#     plant_opts = ["All"] + sorted(df["plant_name"].dropna().unique())

#     fc1,fc2 = st.columns(2)
#     with fc1: pf2 = st.selectbox("Plant", plant_opts, key="pm_p")
#     with fc2: bf2 = st.selectbox("Brand", brand_opts, key="pm_b")

#     ps = (df.groupby(["plant_name","brand"])
#           .agg(power_kw=("power_kw","sum"),today_kwh=("today_kwh","sum"),
#                total_kwh=("total_kwh","sum"),inv_count=("inverter_sn","count"))
#           .reset_index())
#     if pf2!="All": ps=ps[ps["plant_name"]==pf2]
#     if bf2!="All": ps=ps[ps["brand"]==bf2]

#     # Summary
#     st.markdown(
#         f'<div class="stat-row">'
#           f'<div class="stat-item"><div class="stat-val">{len(ps)}</div>'
#           f'<div class="stat-lbl">Plants</div></div>'
#           f'<div class="stat-item"><div class="stat-val">'
#           f'{f(ps["power_kw"].sum(),2)} kW</div>'
#           f'<div class="stat-lbl">Total Power</div></div>'
#           f'<div class="stat-item"><div class="stat-val">'
#           f'{f(ps["today_kwh"].sum(),1)} kWh</div>'
#           f'<div class="stat-lbl">Daily Yield</div></div>'
#           f'<div class="stat-item"><div class="stat-val">'
#           f'{f(ps["total_kwh"].sum(),1)} MWh</div>'
#           f'<div class="stat-lbl">Total Yield</div></div>'
#         f'</div>', unsafe_allow_html=True)

#     st.markdown('<div class="tbl">', unsafe_allow_html=True)
#     st.markdown(
#         '<div class="tbl-hdr tbl-plant">'
#         '<div>Plant Name</div><div>Brand</div><div>Organisation</div>'
#         '<div>Inverters</div><div>Power (kW)</div>'
#         '<div>Daily Yield</div><div>Total Yield</div><div>Status</div>'
#         '</div>', unsafe_allow_html=True)

#     for _, row in ps.iterrows():
#         pr = df[df["plant_name"]==row["plant_name"]]
#         on = int((pr["status"].str.lower()=="online").sum())
#         tot= int(row["inv_count"])
#         pst= "Online" if on==tot and tot>0 else ("Offline" if on==0 else "Warning")
#         st.markdown(
#             f'<div class="tbl-row tbl-plant">'
#               f'<div class="cell-link">{row["plant_name"]}</div>'
#               f'<div>{chip(row["brand"])}</div>'
#               f'<div>Fractal Energy</div>'
#               f'<div>{on}/{tot}</div>'
#               f'<div><b>{f(row["power_kw"],2)}</b> kW</div>'
#               f'<div>{f(row["today_kwh"],1)} kWh</div>'
#               f'<div>{f(row["total_kwh"],3)} MWh</div>'
#               f'<div>{badge(pst)}</div>'
#             f'</div>', unsafe_allow_html=True)
#     st.markdown('</div>', unsafe_allow_html=True)


# # ═════════════════════════════════════════════════════════════
# #  SETTINGS
# # ═════════════════════════════════════════════════════════════
# elif page == "Settings":
#     st.markdown('<div class="page-hdr"><h1>Settings</h1>'
#                 '<p>API credentials, alerts and app configuration</p></div>',
#                 unsafe_allow_html=True)

#     from config import (SOLIS_API_KEY,GROWATT_USERNAME,SUNGROW_APP_KEY,
#                         EMAIL_USER,TO_EMAILS,RATE_PER_KWH)

#     st.markdown("#### 🔑 API Credentials")
#     creds = [
#         ("Solis",   bool(SOLIS_API_KEY),
#          SOLIS_API_KEY[:10]+"…" if SOLIS_API_KEY else "Not configured"),
#         ("Growatt", bool(GROWATT_USERNAME),
#          GROWATT_USERNAME or "Set GROWATT_USERNAME in config.py"),
#         ("Sungrow", bool(SUNGROW_APP_KEY),
#          SUNGROW_APP_KEY[:10]+"…" if SUNGROW_APP_KEY else "Set SUNGROW_APP_KEY in config.py"),
#     ]
#     for brand,ok,hint in creds:
#         c1,c2,c3 = st.columns([1,1,4])
#         c1.markdown(f"**{brand}**")
#         c2.markdown("✅ Connected" if ok else "⚠️ Not set")
#         c3.markdown(f"`{hint}`")

#     st.divider()
#     st.markdown("#### 📧 Email Alerts")
#     st.markdown(f"**Sender:** `{EMAIL_USER}`")
#     st.markdown(f"**Recipients:** `{', '.join(TO_EMAILS)}`")

#     st.divider()
#     st.markdown("#### 💰 Tariff Rate")
#     st.info(f"Current rate: **₹{RATE_PER_KWH}/kWh** — edit `RATE_PER_KWH` in config.py")

#     st.divider()
#     st.markdown("#### 🗂 Project Files")
#     st.code("""
# solar_dashboard/
# ├── app.py              ← Run this:  streamlit run app.py
# ├── config.py           ← ✏️  All credentials & settings
# ├── requirements.txt
# ├── data/
# │   └── solar_data.db   ← Auto-created SQLite database
# └── utils/
#     ├── solis_api.py    ← Solis Cloud connector
#     ├── growatt_api.py  ← Growatt connector
#     ├── sungrow_api.py  ← Sungrow iSolarCloud connector
#     ├── aggregator.py   ← Merges brands + alert logic
#     ├── database.py     ← SQLite read/write
#     └── alerts.py       ← Email notifications
#     """, language="")

# ============================================================
#  app.py  —  Solar Dashboard  |  streamlit run app.py
# ============================================================

# ============================================================
#  app.py  —  Solar Dashboard  |  streamlit run app.py
# ============================================================


# ============================================================
#  app.py  —  Solar Dashboard  |  streamlit run app.py
# ============================================================
# import streamlit as st
# from streamlit_autorefresh import st_autorefresh
# import pandas as pd
# import plotly.express as px
# import plotly.graph_objects as go
# from datetime import datetime, date, timedelta

# from config import REFRESH_INTERVAL_SECONDS, RATE_PER_KWH
# from utils.database import init_db, get_history, get_alert_log
# from utils.aggregator import fetch_all_brands, check_alerts

# # ─────────────────────────────────────────────────────────────
# st.set_page_config(page_title="Solar Dashboard", page_icon="☀️",
#                    layout="wide", initial_sidebar_state="expanded")

# st.markdown("""
# <style>
# @import url('https://fonts.googleapis.com/css2?family=Inter:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800&display=swap');

# *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

# :root {
#   --bg:       #f5f6fa;
#   --card:     #ffffff;
#   --border:   #e8eaf0;
#   --sidebar:  #1a1d2e;
#   --sidebar2: #252840;
#   --accent:   #f5821f;
#   --accent-l: #fff4eb;
#   --green:    #22c55e;
#   --green-l:  #dcfce7;
#   --red:      #ef4444;
#   --red-l:    #fee2e2;
#   --yellow:   #f59e0b;
#   --yellow-l: #fef3c7;
#   --blue:     #3b82f6;
#   --blue-l:   #dbeafe;
#   --text:     #0f172a;
#   --text2:    #64748b;
#   --text3:    #94a3b8;
#   --shadow:   0 1px 3px rgba(0,0,0,.08), 0 4px 16px rgba(0,0,0,.04);
#   --shadow-lg:0 8px 32px rgba(0,0,0,.10);
# }

# html, body, [data-testid="stAppViewContainer"] {
#   background: var(--bg) !important;
#   font-family: 'Inter', sans-serif !important;
#   color: var(--text);
# }
# [data-testid="stHeader"]  { background: transparent !important; display: none; }
# [data-testid="stSidebar"] { background: var(--sidebar) !important; }
# [data-testid="stSidebar"] > div { padding-top: 0 !important; }
# section[data-testid="stSidebarContent"] { padding: 0 !important; }
# #MainMenu, footer { visibility: hidden; }
# [data-testid="stDecoration"] { display: none; }
# .block-container { padding: 28px 32px !important; max-width: 100% !important; }

# /* ── Sidebar nav ── */
# .nav-logo {
#   padding: 24px 20px 20px;
#   border-bottom: 1px solid rgba(255,255,255,.08);
#   margin-bottom: 8px;
# }
# .nav-logo-icon {
#   width: 40px; height: 40px; background: var(--accent);
#   border-radius: 10px; display: flex; align-items: center;
#   justify-content: center; font-size: 20px; margin-bottom: 10px;
# }
# .nav-logo-title { color: #fff; font-weight: 700; font-size: 16px; }
# .nav-logo-sub   { color: #6b7280; font-size: 12px; margin-top: 2px; }

# .nav-section {
#   padding: 6px 16px 4px;
#   font-size: 10px; font-weight: 600; color: #4b5563;
#   text-transform: uppercase; letter-spacing: .1em;
# }

# /* ── KPI cards ── */
# .kpi-grid { display: grid; grid-template-columns: repeat(4,1fr); gap: 16px; margin-bottom: 24px; }
# .kpi-card {
#   background: var(--card); border-radius: 14px; padding: 22px 20px;
#   border: 1px solid var(--border); box-shadow: var(--shadow);
#   display: flex; gap: 14px; align-items: flex-start;
#   transition: box-shadow .2s;
# }
# .kpi-card:hover { box-shadow: var(--shadow-lg); }
# .kpi-icon {
#   width: 48px; height: 48px; border-radius: 12px; flex-shrink: 0;
#   display: flex; align-items: center; justify-content: center; font-size: 22px;
# }
# .kpi-body { flex: 1; min-width: 0; }
# .kpi-label { font-size: 12px; color: var(--text2); font-weight: 500;
#              text-transform: uppercase; letter-spacing: .06em; margin-bottom: 6px; }
# .kpi-value { font-size: 26px; font-weight: 700; color: var(--text); line-height: 1; }
# .kpi-unit  { font-size: 13px; font-weight: 500; color: var(--text2); margin-left: 3px; }
# .kpi-meta  { font-size: 12px; color: var(--text3); margin-top: 7px; }
# .kpi-meta b { color: var(--text2); font-weight: 500; }

# /* ── Page header ── */
# .page-hdr { margin-bottom: 24px; }
# .page-hdr h1 { font-size: 22px; font-weight: 700; color: var(--text); }
# .page-hdr p  { font-size: 13px; color: var(--text2); margin-top: 4px; }

# /* ── Section header ── */
# .sec-hdr {
#   font-size: 14px; font-weight: 600; color: var(--text);
#   margin-bottom: 14px; padding-bottom: 10px;
#   border-bottom: 1px solid var(--border);
#   display: flex; align-items: center; gap: 8px;
# }

# /* ── Card wrapper ── */
# .card {
#   background: var(--card); border-radius: 14px; padding: 20px 22px;
#   border: 1px solid var(--border); box-shadow: var(--shadow); margin-bottom: 16px;
# }
# .card-title {
#   font-size: 15px; font-weight: 600; color: var(--text);
#   margin-bottom: 16px; padding-bottom: 12px; border-bottom: 1px solid var(--border);
# }

# /* ── Inverter card ── */
# .inv-card {
#   background: var(--card); border-radius: 14px; padding: 20px 22px;
#   border: 1px solid var(--border); box-shadow: var(--shadow);
#   margin-bottom: 14px; transition: border-color .15s, box-shadow .15s;
# }
# .inv-card:hover { border-color: var(--accent); box-shadow: var(--shadow-lg); }
# .inv-card.alert { border-left: 3px solid var(--red); }
# .inv-header {
#   display: flex; justify-content: space-between; align-items: flex-start;
#   margin-bottom: 16px; padding-bottom: 14px; border-bottom: 1px solid var(--border);
# }
# .inv-name { font-size: 15px; font-weight: 700; color: var(--text); }
# .inv-meta { font-size: 11px; color: var(--text3); margin-top: 3px; }
# .inv-params { display: grid; grid-template-columns: repeat(6,1fr); gap: 14px; }
# .param-label { font-size: 10px; color: var(--text2); text-transform: uppercase;
#                letter-spacing: .07em; margin-bottom: 3px; }
# .param-val   { font-size: 16px; font-weight: 600; color: var(--text); }
# .param-unit  { font-size: 11px; color: var(--text3); margin-left: 2px; }
# .inv-footer  { margin-top: 12px; font-size: 11px; color: var(--text3); }

# /* ── Table ── */
# .tbl { background: var(--card); border-radius: 14px; border: 1px solid var(--border);
#        overflow: hidden; box-shadow: var(--shadow); }
# .tbl-hdr, .tbl-row {
#   display: grid; padding: 0 20px; align-items: center; gap: 10px;
# }
# .tbl-hdr {
#   background: #f8fafc; border-bottom: 1px solid var(--border);
#   font-size: 11px; font-weight: 600; color: var(--text2);
#   text-transform: uppercase; letter-spacing: .07em; height: 42px;
# }
# .tbl-row {
#   min-height: 52px; border-bottom: 1px solid var(--border);
#   font-size: 13px; transition: background .1s;
# }
# .tbl-row:last-child { border-bottom: none; }
# .tbl-row:hover { background: #fafbfc; }
# .tbl-plant  { grid-template-columns: 2fr 1fr 1.1fr 1fr 1fr 1.1fr 1.3fr 1fr; }
# .tbl-alarm  { grid-template-columns: 1fr 1fr 1fr 1.5fr 1.4fr 2.2fr 1.2fr; }
# .cell-link  { color: var(--accent); font-weight: 600; cursor: pointer; }
# .cell-link:hover { text-decoration: underline; }

# /* ── Badges ── */
# .badge {
#   display: inline-flex; align-items: center; gap: 5px;
#   font-size: 11px; font-weight: 600; padding: 3px 10px; border-radius: 20px;
# }
# .badge::before { content:''; width:6px; height:6px; border-radius:50%; }
# .b-online  { background: var(--green-l);  color: #15803d; }
# .b-online::before  { background: var(--green); }
# .b-offline { background: var(--red-l);    color: #b91c1c; }
# .b-offline::before { background: var(--red); }
# .b-warning { background: var(--yellow-l); color: #92400e; }
# .b-warning::before { background: var(--yellow); }
# .b-unknown { background: #f1f5f9; color: #64748b; }
# .b-unknown::before { background: #94a3b8; }
# .b-active  { background: var(--red-l);    color: #b91c1c; }
# .b-active::before  { background: var(--red); }
# .b-resolved{ background: var(--green-l);  color: #15803d; }
# .b-resolved::before{ background: var(--green); }
# .b-critical{ background: var(--red-l);    color: #b91c1c; font-weight:700; }
# .b-critical::before{ background: var(--red); }

# /* ── Brand chips ── */
# .chip {
#   display: inline-block; font-size: 10px; font-weight: 700; padding: 2px 8px;
#   border-radius: 5px; letter-spacing: .08em; text-transform: uppercase;
# }
# .chip-solis   { background: #dbeafe; color: #1d4ed8; }
# .chip-growatt { background: #dcfce7; color: #15803d; }
# .chip-sungrow { background: #ffedd5; color: #c2410c; }

# /* ── Alert strip ── */
# .alert-strip {
#   background: #fef2f2; border: 1px solid #fecaca; border-radius: 10px;
#   padding: 14px 18px; margin-bottom: 18px; display: flex; gap: 12px; align-items: flex-start;
# }
# .alert-strip-ico { font-size: 18px; flex-shrink: 0; }
# .alert-strip-ttl { font-size: 14px; font-weight: 600; color: var(--red); }
# .alert-strip-msg { font-size: 13px; color: #7f1d1d; margin-top: 2px; }

# /* ── Stat row (summary bar) ── */
# .stat-row {
#   background: var(--card); border-radius: 12px; padding: 14px 22px;
#   border: 1px solid var(--border); display: flex; gap: 28px; margin-bottom: 20px;
#   align-items: center; flex-wrap: wrap;
# }
# .stat-item { text-align: center; }
# .stat-val { font-size: 18px; font-weight: 700; color: var(--text); }
# .stat-lbl { font-size: 11px; color: var(--text3); margin-top: 2px; }

# /* ── Streamlit overrides ── */
# .stButton > button {
#   background: var(--accent) !important; color: #fff !important;
#   border: none !important; border-radius: 8px !important;
#   font-family: 'Inter', sans-serif !important; font-weight: 600 !important;
#   font-size: 13px !important; padding: 9px 22px !important;
#   transition: opacity .15s !important;
# }
# .stButton > button:hover { opacity: .88 !important; }
# div[data-testid="stSelectbox"] > label,
# div[data-testid="stTextInput"]  > label { font-size: 12px !important; font-weight: 500 !important; }
# [data-testid="stRadio"] > label { font-size: 13px !important; }
# .stRadio > div { gap: 4px !important; }
# .stAlert { border-radius: 10px !important; }
# </style>
# """, unsafe_allow_html=True)

# # ── Bootstrap ─────────────────────────────────────────────────
# init_db()
# st_autorefresh(interval=REFRESH_INTERVAL_SECONDS * 1000, key="solar_ar")

# # ── Helpers ──────────────────────────────────────────────────
# def f(v, d=1, na="—"):
#     try:    return f"{float(v):.{d}f}"
#     except: return na

# def badge(s, kind=None):
#     s = (s or "").strip()
#     sl = s.lower()
#     if kind == "level":
#         cls = "b-critical" if sl == "critical" else "b-warning"
#     elif kind == "status_alarm":
#         cls = "b-active" if sl == "active" else "b-resolved"
#     else:
#         if sl == "online":            cls = "b-online"
#         elif sl in ("offline","fault"): cls = "b-offline"
#         else:                          cls = "b-unknown"
#     return f'<span class="badge {cls}">{s}</span>'

# def chip(b):
#     return f'<span class="chip chip-{(b or "").lower()}">{b}</span>'

# def earn(kwh):
#     v = float(kwh or 0) * RATE_PER_KWH
#     if v >= 1_000_000: return f"₹{v/1_000_000:.3f}M"
#     if v >= 1_000:     return f"₹{v/1_000:.3f}K"
#     return f"₹{v:.2f}"

# def chart(fig, h=300):
#     fig.update_layout(plot_bgcolor="#fff", paper_bgcolor="#fff", font_color="#64748b",
#                       margin=dict(l=0,r=0,t=10,b=0), height=h,
#                       legend=dict(bgcolor="#fff", font=dict(size=12)),
#                       bargap=0.3, font_family="Inter")
#     fig.update_traces(marker_line_width=0)
#     fig.update_xaxes(showgrid=False, zeroline=False, tickfont_size=11)
#     fig.update_yaxes(showgrid=True, gridcolor="#f1f5f9", zeroline=False, tickfont_size=11)
#     return fig

# BRAND_COLORS = {"Solis":"#3b82f6","Growatt":"#22c55e","Sungrow":"#f5821f"}

# # ── Sidebar ──────────────────────────────────────────────────
# with st.sidebar:
#     st.markdown("""
#     <div class="nav-logo">
#       <div class="nav-logo-icon">☀</div>
#       <div class="nav-logo-title">Solar Dashboard</div>
#       <div class="nav-logo-sub">Fractal Energy</div>
#     </div>""", unsafe_allow_html=True)

#     page = st.radio("", ["📊  Overview","🔧  O&M","📈  Report","🗺  Service","⚙️  Settings"],
#                     label_visibility="collapsed")
#     page = page.split("  ",1)[1].strip()

#     st.markdown('<div class="nav-section">Data Sources</div>', unsafe_allow_html=True)
#     sel_brands = [b for b in ["Solis","Growatt","Sungrow"]
#                   if st.checkbox(b, value=(b=="Solis"), key=f"cb_{b}")]

#     st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)
#     if st.button("🔄 Refresh Now"):
#         st.cache_data.clear(); st.rerun()

#     show_debug = st.checkbox("🔍 Debug mode", value=False)

#     st.markdown(
#         f"<div style='padding:16px;font-size:11px;color:#4b5563;border-top:1px solid "
#         f"rgba(255,255,255,.08);margin-top:12px;'>"
#         f"⏱ {datetime.now().strftime('%d %b %Y  %H:%M:%S')}<br>"
#         f"Auto-refresh every {REFRESH_INTERVAL_SECONDS//60} min</div>",
#         unsafe_allow_html=True)

# # ── Fetch + clean data ────────────────────────────────────────
# @st.cache_data(ttl=REFRESH_INTERVAL_SECONDS)
# def load(brands):
#     return fetch_all_brands(list(brands))

# with st.spinner("Fetching live data…"):
#     records = load(tuple(sel_brands))

# alerts = check_alerts(records, st.session_state)

# df = pd.DataFrame()
# if records:
#     df = pd.DataFrame(records)
#     for c in ["power_kw","today_kwh","total_kwh","temperature","voltage","current_a"]:
#         if c in df.columns:
#             df[c] = pd.to_numeric(df[c], errors="coerce")
#     if "status" in df.columns:
#         df["status"] = df["status"].astype(str).str.strip()

# # ── Debug ────────────────────────────────────────────────────
# if show_debug:
#     st.markdown("### 🔍 Debug: Raw API Data")
#     if not df.empty:
#         st.dataframe(df, use_container_width=True)
#         st.write("**power_kw:**",   df["power_kw"].tolist())
#         st.write("**today_kwh:**",  df["today_kwh"].tolist())
#         st.write("**total_kwh (MWh):**", df["total_kwh"].tolist())

#     st.markdown("### 🔍 Debug: userStationList raw fields")
#     try:
#         from utils.solis_api import fetch_summary as _fsum, _raw_plants_cache
#         summ = _fsum()
#         st.write("**fetch_summary() returned:**", summ)
#         if _raw_plants_cache:
#             st.markdown("**First plant — all fields:**")
#             p = _raw_plants_cache[0]
#             rows = [{"field": k, "value": str(v)} for k, v in sorted(p.items())]
#             import pandas as _pd
#             st.dataframe(_pd.DataFrame(rows), use_container_width=True, hide_index=True)
#             st.markdown("**Fields likely containing energy:**")
#             energy_keys = [k for k in p if any(x in k.lower() for x in
#                           ["energy","power","kwh","mwh","day","month","all","total","yield"])]
#             for k in sorted(energy_keys):
#                 st.write(f"  `{k}` = `{p.get(k)}`")
#     except Exception as ex:
#         st.error(f"Debug error: {ex}")
#     st.divider()


# # ═════════════════════════════════════════════════════════════
# #  OVERVIEW
# # ═════════════════════════════════════════════════════════════
# if page == "Overview":
#     st.markdown('<div class="page-hdr"><h1>Plant Overview</h1>'
#                 '<p>Real-time performance across all plants</p></div>',
#                 unsafe_allow_html=True)

#     if df.empty:
#         st.warning("⚠️ No data. Verify credentials in config.py and click Refresh.")
#         if not show_debug:
#             st.info("💡 Enable **Debug mode** in the sidebar to inspect the API response.")
#         st.stop()

#     # ── KPI values ───────────────────────────────────────────
#     # Step 1: get plant-level summary from Solis userStationList
#     # This gives accurate daily, monthly, total directly from Solis
#     # Fields: stationPower(kW), dayEnergy(kWh), monthEnergy(kWh), allEnergy(kWh)
#     total_power   = float(df["power_kw"].sum())   # fallback
#     daily_kwh     = float(df["today_kwh"].sum())  # fallback kWh
#     total_mwh     = float(df["total_kwh"].sum())  # fallback MWh (from etotal)
#     monthly_kwh   = 0.0

#     try:
#         if "Solis" in sel_brands:
#             from utils.solis_api import fetch_summary as _fs
#             summ = _fs()
#             # CONFIRMED units:
#             #   power_kw    → kW
#             #   daily_kwh   → kWh  (dayEnergy field)
#             #   monthly_mwh → MWh  (monthEnergy field, already MWh)
#             #   total_mwh   → MWh  (allEnergy field, already MWh)
#             if summ.get("power_kw",    0) > 0: total_power = float(summ["power_kw"])
#             if summ.get("daily_kwh",   0) > 0: daily_kwh   = float(summ["daily_kwh"])
#             if summ.get("monthly_mwh", 0) > 0: monthly_mwh = float(summ["monthly_mwh"])
#             if summ.get("total_mwh",   0) > 0: total_mwh   = float(summ["total_mwh"])
#     except Exception as e:
#         monthly_mwh = 0.0

#     # Monthly fallback from DB if API returned 0
#     if monthly_kwh == 0:
#         hist = get_history(hours=720)
#         monthly_kwh_db = daily_kwh
#         if not hist.empty and "today_kwh" in hist.columns:
#             hist["fetched_at"] = pd.to_datetime(hist["fetched_at"])
#             hist["today_kwh"]  = pd.to_numeric(hist["today_kwh"], errors="coerce")
#             m = hist[hist["fetched_at"].dt.month == datetime.now().month]
#             if not m.empty:
#                 v = float(m.groupby([m["fetched_at"].dt.date,"inverter_sn"])["today_kwh"].max().sum())
#                 monthly_kwh_db = max(v, daily_kwh)
#         monthly_mwh = monthly_kwh_db / 1000

#     monthly_kwh = monthly_mwh * 1000  # for earnings calculation

#     # Display units — match Solis exactly
#     # daily_kwh is in kWh → show MWh when >= 1000
#     # monthly_mwh is already MWh → always show as MWh
#     # total_mwh is already MWh → always show as MWh
#     if daily_kwh >= 1000:
#         daily_val, daily_unit = f(daily_kwh / 1000, 3), "MWh"
#     else:
#         daily_val, daily_unit = f(daily_kwh, 1), "kWh" 

#     n_on = int((df["status"].str.lower()=="online").sum())
#     n_tot= len(df)

#     col1,col2,col3,col4 = st.columns(4)
#     kpis = [
#         (col1,"⚡","power","Power",f(total_power,2),"kW",
#          f"Inverters: <b>{n_on}/{n_tot} online</b>"),
#         (col2,"🔋","daily","Daily Yield", daily_val, daily_unit,
#          f"Earning today: <b>{earn(daily_kwh)}</b>"),
#         (col3,"📅","monthly","Monthly Yield",
#          f(monthly_mwh, 3), "MWh",
#          f"Earning this month: <b>{earn(monthly_kwh)}</b>"),
#         (col4,"📊","total","Total Yield",f(total_mwh,3),"MWh",
#          f"Total earning: <b>{earn(total_mwh*1000)}</b>"),
#     ]
#     icon_bg = {"power":"#fff4eb","daily":"#fff4eb","monthly":"#eff6ff","total":"#fffbeb"}
#     for col,ico,kind,lbl,val,unit,meta in kpis:
#         with col:
#             st.markdown(f"""
#             <div class="kpi-card">
#               <div class="kpi-icon" style="background:{icon_bg[kind]};">{ico}</div>
#               <div class="kpi-body">
#                 <div class="kpi-label">{lbl}</div>
#                 <div class="kpi-value">{val}<span class="kpi-unit">{unit}</span></div>
#                 <div class="kpi-meta">{meta}</div>
#               </div>
#             </div>""", unsafe_allow_html=True)

#     # ── Alert strip ───────────────────────────────────────────
#     if alerts:
#         for a in alerts[:3]:
#             st.markdown(f"""
#             <div class="alert-strip">
#               <div class="alert-strip-ico">🚨</div>
#               <div>
#                 <div class="alert-strip-ttl">{a['plant_name']} — {a.get('inverter_sn','')}</div>
#                 <div class="alert-strip-msg">{a['issue']}</div>
#               </div>
#             </div>""", unsafe_allow_html=True)

#     # ── Charts row ────────────────────────────────────────────
#     ch1, ch2 = st.columns([3,2])

#     with ch1:
#         st.markdown('<div class="sec-hdr">⚡ Power by Plant (kW)</div>', unsafe_allow_html=True)
#         pdf = df.groupby(["plant_name","brand"])["power_kw"].sum().reset_index()
#         fig = px.bar(pdf, x="plant_name", y="power_kw", color="brand",
#                      color_discrete_map=BRAND_COLORS,
#                      labels={"power_kw":"Power (kW)","plant_name":"","brand":"Brand"})
#         st.plotly_chart(chart(fig,280), use_container_width=True)

#     with ch2:
#         st.markdown('<div class="sec-hdr">📊 Daily Yield Share</div>', unsafe_allow_html=True)
#         pief = df.groupby("plant_name")["today_kwh"].sum().reset_index()
#         fig2 = px.pie(pief, names="plant_name", values="today_kwh",
#                       color_discrete_sequence=px.colors.qualitative.Pastel,
#                       hole=0.45)
#         fig2.update_traces(textposition="outside", textinfo="label+percent")
#         fig2.update_layout(plot_bgcolor="#fff", paper_bgcolor="#fff",
#                            font_family="Inter", font_color="#64748b",
#                            margin=dict(l=0,r=0,t=10,b=0), height=280,
#                            showlegend=False)
#         st.plotly_chart(fig2, use_container_width=True)

#     # ── Plant summary table ───────────────────────────────────
#     st.markdown('<div class="sec-hdr" style="margin-top:8px;">🌱 Plant List</div>',
#                 unsafe_allow_html=True)

#     ps = (df.groupby(["plant_name","brand"])
#           .agg(power_kw=("power_kw","sum"),
#                today_kwh=("today_kwh","sum"),
#                total_kwh=("total_kwh","sum"),
#                inv_count=("inverter_sn","count"))
#           .reset_index())

#     st.markdown('<div class="tbl">', unsafe_allow_html=True)
#     st.markdown(
#         '<div class="tbl-hdr tbl-plant">'
#         '<div>Plant Name</div><div>Brand</div><div>Inverters</div>'
#         '<div>Power (kW)</div><div>Daily Yield</div>'
#         '<div>Total Yield</div><div>Earning Today</div><div>Status</div>'
#         '</div>', unsafe_allow_html=True)

#     for _, row in ps.iterrows():
#         pr  = df[df["plant_name"]==row["plant_name"]]
#         on  = int((pr["status"].str.lower()=="online").sum())
#         tot = int(row["inv_count"])
#         pst = "Online" if on==tot and tot>0 else ("Offline" if on==0 else "Warning")
#         dy  = float(row["today_kwh"] or 0)
#         dy_str = f"{dy/1000:.3f} MWh" if dy >= 1000 else f"{dy:.1f} kWh"
#         st.markdown(
#             f'<div class="tbl-row tbl-plant">'
#               f'<div class="cell-link">{row["plant_name"]}</div>'
#               f'<div>{chip(row["brand"])}</div>'
#               f'<div>{on}/{tot}</div>'
#               f'<div><b>{f(row["power_kw"],2)}</b> kW</div>'
#               f'<div>{dy_str}</div>'
#               f'<div>{f(row["total_kwh"],3)} MWh</div>'
#               f'<div>{earn(dy)}</div>'
#               f'<div>{badge(pst)}</div>'
#             f'</div>', unsafe_allow_html=True)
#     st.markdown('</div>', unsafe_allow_html=True)


# # ═════════════════════════════════════════════════════════════
# #  O&M
# # ═════════════════════════════════════════════════════════════
# elif page == "O&M":
#     sub = st.radio("", ["🔔  Alarm Information","⚡  Device Overview"],
#                    horizontal=True, label_visibility="collapsed")
#     sub = sub.split("  ",1)[1].strip()
#     st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

#     # Build alarm list
#     alarm_log = get_alert_log(200)
#     all_alarms = []
#     for a in alerts:
#         all_alarms.append({"device_type":"Inverter","level":"Critical","status":"Active",
#             "plant_name":a.get("plant_name","—"),"sn":a.get("inverter_sn","—"),
#             "content":a.get("issue","—"),"brand":a.get("brand","—"),
#             "time":datetime.now().strftime("%Y-%m-%d %H:%M")})
#     if not alarm_log.empty:
#         for _, r in alarm_log.iterrows():
#             all_alarms.append({"device_type":"Inverter","level":"Warning","status":"Resolved",
#                 "plant_name":r.get("plant_name","—"),"sn":r.get("inverter_sn","—"),
#                 "content":r.get("issue","—"),"brand":r.get("brand","—"),
#                 "time":r.get("alerted_at","—")})

#     # ── Alarm Information ─────────────────────────────────────
#     if sub == "Alarm Information":
#         st.markdown('<div class="page-hdr"><h1>Alarm Information</h1>'
#                     '<p>All detected faults and alert history</p></div>',
#                     unsafe_allow_html=True)

#         plant_opts = ["All"] + sorted({a["plant_name"] for a in all_alarms if a["plant_name"]!="—"})
#         sn_opts    = ["All"] + sorted({a["sn"]         for a in all_alarms if a["sn"]        !="—"})
#         brand_opts = ["All"] + sorted({a["brand"]       for a in all_alarms if a["brand"]     !="—"})

#         with st.container():
#             fc1,fc2,fc3,fc4,fc5 = st.columns(5)
#             with fc1: fp = st.selectbox("Plant Name",  plant_opts)
#             with fc2: fs = st.selectbox("SN",          sn_opts)
#             with fc3: fb = st.selectbox("Brand",       brand_opts)
#             with fc4: fst= st.selectbox("Status",      ["All","Active","Resolved"])
#             with fc5: fl = st.selectbox("Level",       ["All","Critical","Warning"])

#         filt = all_alarms[:]
#         if fp  !="All": filt=[a for a in filt if a["plant_name"]==fp]
#         if fs  !="All": filt=[a for a in filt if a["sn"]        ==fs]
#         if fb  !="All": filt=[a for a in filt if a["brand"]     ==fb]
#         if fst !="All": filt=[a for a in filt if a["status"]    ==fst]
#         if fl  !="All": filt=[a for a in filt if a["level"]     ==fl]

#         # Summary counts
#         n_active  = sum(1 for a in filt if a["status"]=="Active")
#         n_resolved= sum(1 for a in filt if a["status"]=="Resolved")
#         sc1,sc2,sc3 = st.columns(3)
#         sc1.metric("Total Alarms",    len(filt))
#         sc2.metric("Active",   n_active,   delta_color="inverse")
#         sc3.metric("Resolved", n_resolved)

#         if not filt:
#             st.success("✅ No alarms match the current filters — all systems normal.")
#         else:
#             st.markdown('<div class="tbl">', unsafe_allow_html=True)
#             st.markdown(
#                 '<div class="tbl-hdr tbl-alarm">'
#                 '<div>Device Type</div><div>Level</div><div>Status</div>'
#                 '<div>Plant Name</div><div>SN</div><div>Issue</div><div>Time</div>'
#                 '</div>', unsafe_allow_html=True)
#             for a in filt:
#                 st.markdown(
#                     f'<div class="tbl-row tbl-alarm">'
#                       f'<div>{a["device_type"]}</div>'
#                       f'<div>{badge(a["level"],"level")}</div>'
#                       f'<div>{badge(a["status"],"status_alarm")}</div>'
#                       f'<div>{chip(a["brand"])} {a["plant_name"]}</div>'
#                       f'<div style="font-size:11px;color:var(--text3);">{a["sn"]}</div>'
#                       f'<div>{a["content"]}</div>'
#                       f'<div style="font-size:11px;color:var(--text3);">{a["time"]}</div>'
#                     f'</div>', unsafe_allow_html=True)
#             st.markdown('</div>', unsafe_allow_html=True)

#     # ── Device Overview ───────────────────────────────────────
#     else:
#         st.markdown('<div class="page-hdr"><h1>Device Overview</h1>'
#                     '<p>Live readings for every inverter</p></div>',
#                     unsafe_allow_html=True)
#         if df.empty:
#             st.warning("⚠️ No data."); st.stop()

#         brand_opts2 = ["All"] + sorted(df["brand"].dropna().unique())
#         plant_opts2 = ["All"] + sorted(df["plant_name"].dropna().unique())
#         sn_opts2    = ["All"] + sorted(df["inverter_sn"].dropna().unique())
#         stat_opts2  = ["All"] + sorted(df["status"].dropna().unique())

#         fc1,fc2,fc3,fc4 = st.columns(4)
#         with fc1: bf = st.selectbox("Brand",  brand_opts2, key="do_b")
#         with fc2: pf = st.selectbox("Plant",  plant_opts2, key="do_p")
#         with fc3: sf = st.selectbox("S/N",    sn_opts2,    key="do_s")
#         with fc4: stf= st.selectbox("Status", stat_opts2,  key="do_st")

#         vw = df.copy()
#         if bf !="All": vw=vw[vw["brand"]       ==bf]
#         if pf !="All": vw=vw[vw["plant_name"]  ==pf]
#         if sf !="All": vw=vw[vw["inverter_sn"] ==sf]
#         if stf!="All": vw=vw[vw["status"]      ==stf]

#         # Summary strip
#         st.markdown(
#             f'<div class="stat-row">'
#               f'<div class="stat-item"><div class="stat-val">{len(vw)}</div>'
#               f'<div class="stat-lbl">Inverters</div></div>'
#               f'<div class="stat-item"><div class="stat-val">'
#               f'{f(vw["power_kw"].sum(),2)} kW</div>'
#               f'<div class="stat-lbl">Total Power</div></div>'
#               f'<div class="stat-item"><div class="stat-val">'
#               f'{f(vw["today_kwh"].sum(),1)} kWh</div>'
#               f'<div class="stat-lbl">Daily Yield</div></div>'
#               f'<div class="stat-item"><div class="stat-val">'
#               f'{int((vw["status"].str.lower()=="online").sum())}</div>'
#               f'<div class="stat-lbl">Online</div></div>'
#             f'</div>', unsafe_allow_html=True)

#         alert_sns = {a.get("inverter_sn") for a in alerts}
#         for _, row in vw.iterrows():
#             sn    = str(row.get("inverter_sn","N/A"))
#             brand = str(row.get("brand",""))
#             st_   = str(row.get("status",""))
#             params = [
#                 ("Power Now",   f(row.get("power_kw"),2),  "kW"),
#                 ("Daily Yield", f(row.get("today_kwh"),1), "kWh"),
#                 ("Total Yield", f(row.get("total_kwh"),3), "MWh"),
#                 ("Temperature", f(row.get("temperature"),1),"°C"),
#                 ("AC Voltage",  f(row.get("voltage"),1),   "V"),
#                 ("AC Current",  f(row.get("current_a"),1), "A"),
#             ]
#             p_html = "".join(
#                 f'<div><div class="param-label">{l}</div>'
#                 f'<div class="param-val">{v}<span class="param-unit"> {u}</span></div></div>'
#                 for l,v,u in params)
#             a_cls = "inv-card alert" if sn in alert_sns else "inv-card"
#             st.markdown(
#                 f'<div class="{a_cls}">'
#                   f'<div class="inv-header">'
#                     f'<div><div class="inv-name">{row.get("plant_name","")}</div>'
#                     f'<div class="inv-meta">S/N: {sn} &nbsp;·&nbsp; {chip(brand)}'
#                     f' &nbsp;·&nbsp; {row.get("last_update","—")}</div></div>'
#                     + badge(st_) +
#                   f'</div>'
#                   f'<div class="inv-params">{p_html}</div>'
#                 f'</div>', unsafe_allow_html=True)


# # ═════════════════════════════════════════════════════════════
# #  REPORT
# # ═════════════════════════════════════════════════════════════
# elif page == "Report":
#     st.markdown('<div class="page-hdr"><h1>Plant Report</h1>'
#                 '<p>Historical generation analysis</p></div>',
#                 unsafe_allow_html=True)

#     rtype = st.radio("", ["Daily","Monthly","Annual","Total"],
#                      horizontal=True, label_visibility="collapsed")

#     plant_opts = (["All Plants"] + sorted(df["plant_name"].dropna().unique())
#                   if not df.empty else ["No data"])
#     fc1,fc2 = st.columns([2,1])
#     with fc1: sel_plant = st.selectbox("Select Plant", plant_opts)
#     with fc2: sel_date  = st.date_input("Date", value=date.today())

#     hist_df = get_history(hours=8760)
#     if hist_df.empty:
#         st.info("📭 No history yet — data accumulates every 5 minutes. Come back soon.")
#         st.stop()

#     hist_df["fetched_at"] = pd.to_datetime(hist_df["fetched_at"])
#     hist_df["power_kw"]   = pd.to_numeric(hist_df.get("power_kw"), errors="coerce")
#     hist_df["today_kwh"]  = pd.to_numeric(hist_df.get("today_kwh"),errors="coerce")
#     hist_df["total_kwh"]  = pd.to_numeric(hist_df.get("total_kwh"),errors="coerce")

#     if sel_plant != "All Plants":
#         hist_df = hist_df[hist_df["plant_name"]==sel_plant]

#     if rtype == "Daily":
#         day = hist_df[hist_df["fetched_at"].dt.date==sel_date].sort_values("fetched_at")
#         if day.empty:
#             st.info(f"No data for {sel_date}.")
#         else:
#             fig = px.line(day, x="fetched_at", y="power_kw", color="inverter_sn",
#                           labels={"fetched_at":"Time","power_kw":"Power (kW)","inverter_sn":"Inverter"})
#             st.plotly_chart(chart(fig,320), use_container_width=True)
#             sm = (day.groupby(["plant_name","inverter_sn","brand"])
#                   .agg(Peak_kW=("power_kw","max"), Daily_kWh=("today_kwh","max"))
#                   .reset_index())
#             sm.columns = ["Plant","S/N","Brand","Peak Power (kW)","Daily Yield (kWh)"]
#             st.dataframe(sm, use_container_width=True, hide_index=True)

#     elif rtype == "Monthly":
#         mdf = hist_df[(hist_df["fetched_at"].dt.year==sel_date.year) &
#                       (hist_df["fetched_at"].dt.month==sel_date.month)]
#         if mdf.empty:
#             st.info(f"No data for {sel_date.strftime('%B %Y')}.")
#         else:
#             daily = mdf.groupby(mdf["fetched_at"].dt.date)["today_kwh"].max().reset_index()
#             daily.columns = ["Date","Daily Yield (kWh)"]
#             fig = px.bar(daily, x="Date", y="Daily Yield (kWh)",
#                          color_discrete_sequence=[BRAND_COLORS["Solis"]])
#             st.plotly_chart(chart(fig,300), use_container_width=True)
#             tot = daily["Daily Yield (kWh)"].sum()
#             m1,m2 = st.columns(2)
#             m1.metric("Month Total", f"{tot:.1f} kWh")
#             m2.metric("Estimated Earning", earn(tot))

#     elif rtype == "Annual":
#         ydf = hist_df[hist_df["fetched_at"].dt.year==sel_date.year]
#         if ydf.empty:
#             st.info(f"No data for {sel_date.year}.")
#         else:
#             monthly = ydf.groupby(ydf["fetched_at"].dt.month)["today_kwh"].sum().reset_index()
#             monthly.columns = ["Month","kWh"]
#             monthly["Month"] = monthly["Month"].apply(
#                 lambda m: date(sel_date.year,int(m),1).strftime("%b"))
#             fig = px.bar(monthly, x="Month", y="kWh", color_discrete_sequence=["#3b82f6"])
#             st.plotly_chart(chart(fig,300), use_container_width=True)

#     else:  # Total
#         yearly = hist_df.groupby(hist_df["fetched_at"].dt.year)["today_kwh"].sum().reset_index()
#         yearly.columns = ["Year","kWh"]
#         fig = px.bar(yearly, x="Year", y="kWh", color_discrete_sequence=["#22c55e"])
#         st.plotly_chart(chart(fig,280), use_container_width=True)
#         if not df.empty:
#             gt = (df.groupby(["plant_name","brand"])["total_kwh"].sum().reset_index()
#                   .rename(columns={"plant_name":"Plant","brand":"Brand","total_kwh":"Total Yield (MWh)"}))
#             st.dataframe(gt, use_container_width=True, hide_index=True)


# # ═════════════════════════════════════════════════════════════
# #  SERVICE  (Plant Management)
# # ═════════════════════════════════════════════════════════════
# elif page == "Service":
#     st.markdown('<div class="page-hdr"><h1>Plant Management</h1>'
#                 '<p>All registered plants and their details</p></div>',
#                 unsafe_allow_html=True)

#     if df.empty:
#         st.warning("⚠️ No data."); st.stop()

#     brand_opts = ["All"] + sorted(df["brand"].dropna().unique())
#     plant_opts = ["All"] + sorted(df["plant_name"].dropna().unique())

#     fc1,fc2 = st.columns(2)
#     with fc1: pf2 = st.selectbox("Plant", plant_opts, key="pm_p")
#     with fc2: bf2 = st.selectbox("Brand", brand_opts, key="pm_b")

#     ps = (df.groupby(["plant_name","brand"])
#           .agg(power_kw=("power_kw","sum"),today_kwh=("today_kwh","sum"),
#                total_kwh=("total_kwh","sum"),inv_count=("inverter_sn","count"))
#           .reset_index())
#     if pf2!="All": ps=ps[ps["plant_name"]==pf2]
#     if bf2!="All": ps=ps[ps["brand"]==bf2]

#     # Summary
#     st.markdown(
#         f'<div class="stat-row">'
#           f'<div class="stat-item"><div class="stat-val">{len(ps)}</div>'
#           f'<div class="stat-lbl">Plants</div></div>'
#           f'<div class="stat-item"><div class="stat-val">'
#           f'{f(ps["power_kw"].sum(),2)} kW</div>'
#           f'<div class="stat-lbl">Total Power</div></div>'
#           f'<div class="stat-item"><div class="stat-val">'
#           f'{f(ps["today_kwh"].sum(),1)} kWh</div>'
#           f'<div class="stat-lbl">Daily Yield</div></div>'
#           f'<div class="stat-item"><div class="stat-val">'
#           f'{f(ps["total_kwh"].sum(),1)} MWh</div>'
#           f'<div class="stat-lbl">Total Yield</div></div>'
#         f'</div>', unsafe_allow_html=True)

#     st.markdown('<div class="tbl">', unsafe_allow_html=True)
#     st.markdown(
#         '<div class="tbl-hdr tbl-plant">'
#         '<div>Plant Name</div><div>Brand</div><div>Organisation</div>'
#         '<div>Inverters</div><div>Power (kW)</div>'
#         '<div>Daily Yield</div><div>Total Yield</div><div>Status</div>'
#         '</div>', unsafe_allow_html=True)

#     for _, row in ps.iterrows():
#         pr  = df[df["plant_name"]==row["plant_name"]]
#         on  = int((pr["status"].str.lower()=="online").sum())
#         tot = int(row["inv_count"])
#         pst = "Online" if on==tot and tot>0 else ("Offline" if on==0 else "Warning")
#         dy  = float(row["today_kwh"] or 0)
#         dy_str = f"{dy/1000:.3f} MWh" if dy >= 1000 else f"{dy:.1f} kWh"
#         st.markdown(
#             f'<div class="tbl-row tbl-plant">'
#               f'<div class="cell-link">{row["plant_name"]}</div>'
#               f'<div>{chip(row["brand"])}</div>'
#               f'<div>Fractal Energy</div>'
#               f'<div>{on}/{tot}</div>'
#               f'<div><b>{f(row["power_kw"],2)}</b> kW</div>'
#               f'<div>{dy_str}</div>'
#               f'<div>{f(row["total_kwh"],3)} MWh</div>'
#               f'<div>{badge(pst)}</div>'
#             f'</div>', unsafe_allow_html=True)
#     st.markdown('</div>', unsafe_allow_html=True)


# # ═════════════════════════════════════════════════════════════
# #  SETTINGS
# # ═════════════════════════════════════════════════════════════
# elif page == "Settings":
#     st.markdown('<div class="page-hdr"><h1>Settings</h1>'
#                 '<p>API credentials, alerts and app configuration</p></div>',
#                 unsafe_allow_html=True)

#     from config import (SOLIS_API_KEY,GROWATT_USERNAME,SUNGROW_APP_KEY,
#                         EMAIL_USER,TO_EMAILS,RATE_PER_KWH)

#     st.markdown("#### 🔑 API Credentials")
#     creds = [
#         ("Solis",   bool(SOLIS_API_KEY),
#          SOLIS_API_KEY[:10]+"…" if SOLIS_API_KEY else "Not configured"),
#         ("Growatt", bool(GROWATT_USERNAME),
#          GROWATT_USERNAME or "Set GROWATT_USERNAME in config.py"),
#         ("Sungrow", bool(SUNGROW_APP_KEY),
#          SUNGROW_APP_KEY[:10]+"…" if SUNGROW_APP_KEY else "Set SUNGROW_APP_KEY in config.py"),
#     ]
#     for brand,ok,hint in creds:
#         c1,c2,c3 = st.columns([1,1,4])
#         c1.markdown(f"**{brand}**")
#         c2.markdown("✅ Connected" if ok else "⚠️ Not set")
#         c3.markdown(f"`{hint}`")

#     st.divider()
#     st.markdown("#### 📧 Email Alerts")
#     st.markdown(f"**Sender:** `{EMAIL_USER}`")
#     st.markdown(f"**Recipients:** `{', '.join(TO_EMAILS)}`")

#     st.divider()
#     st.markdown("#### 💰 Tariff Rate")
#     st.info(f"Current rate: **₹{RATE_PER_KWH}/kWh** — edit `RATE_PER_KWH` in config.py")

#     st.divider()
#     st.markdown("#### 🗂 Project Files")
#     st.code("""
# solar_dashboard/
# ├── app.py              ← Run this:  streamlit run app.py
# ├── config.py           ← ✏️  All credentials & settings
# ├── requirements.txt
# ├── data/
# │   └── solar_data.db   ← Auto-created SQLite database
# └── utils/
#     ├── solis_api.py    ← Solis Cloud connector
#     ├── growatt_api.py  ← Growatt connector
#     ├── sungrow_api.py  ← Sungrow iSolarCloud connector
#     ├── aggregator.py   ← Merges brands + alert logic
#     ├── database.py     ← SQLite read/write
#     └── alerts.py       ← Email notifications
#     """, language="")

# ============================================================
#  app.py  —  Solar Dashboard  |  streamlit run app.py
# ============================================================
# import streamlit as st
# from streamlit_autorefresh import st_autorefresh
# import pandas as pd
# import plotly.express as px
# import plotly.graph_objects as go
# from datetime import datetime, date, timedelta

# from config import REFRESH_INTERVAL_SECONDS, RATE_PER_KWH
# from utils.database import init_db, get_history, get_alert_log
# from utils.aggregator import fetch_all_brands, check_alerts

# # ─────────────────────────────────────────────────────────────
# st.set_page_config(page_title="Solar Dashboard", page_icon="☀️",
#                    layout="wide", initial_sidebar_state="expanded")

# st.markdown("""
# <style>
# @import url('https://fonts.googleapis.com/css2?family=Inter:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800&display=swap');

# *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

# :root {
#   --bg:       #f5f6fa;
#   --card:     #ffffff;
#   --border:   #e8eaf0;
#   --sidebar:  #1a1d2e;
#   --sidebar2: #252840;
#   --accent:   #f5821f;
#   --accent-l: #fff4eb;
#   --green:    #22c55e;
#   --green-l:  #dcfce7;
#   --red:      #ef4444;
#   --red-l:    #fee2e2;
#   --yellow:   #f59e0b;
#   --yellow-l: #fef3c7;
#   --blue:     #3b82f6;
#   --blue-l:   #dbeafe;
#   --text:     #0f172a;
#   --text2:    #64748b;
#   --text3:    #94a3b8;
#   --shadow:   0 1px 3px rgba(0,0,0,.08), 0 4px 16px rgba(0,0,0,.04);
#   --shadow-lg:0 8px 32px rgba(0,0,0,.10);
# }

# html, body, [data-testid="stAppViewContainer"] {
#   background: var(--bg) !important;
#   font-family: 'Inter', sans-serif !important;
#   color: var(--text);
# }
# [data-testid="stHeader"]  { background: transparent !important; display: none; }
# [data-testid="stSidebar"] { background: var(--sidebar) !important; }
# [data-testid="stSidebar"] > div { padding-top: 0 !important; }
# section[data-testid="stSidebarContent"] { padding: 0 !important; }
# #MainMenu, footer { visibility: hidden; }
# [data-testid="stDecoration"] { display: none; }
# .block-container { padding: 28px 32px !important; max-width: 100% !important; }

# /* ── Sidebar nav ── */
# .nav-logo {
#   padding: 24px 20px 20px;
#   border-bottom: 1px solid rgba(255,255,255,.08);
#   margin-bottom: 8px;
# }
# .nav-logo-icon {
#   width: 40px; height: 40px; background: var(--accent);
#   border-radius: 10px; display: flex; align-items: center;
#   justify-content: center; font-size: 20px; margin-bottom: 10px;
# }
# .nav-logo-title { color: #fff; font-weight: 700; font-size: 16px; }
# .nav-logo-sub   { color: #6b7280; font-size: 12px; margin-top: 2px; }

# .nav-section {
#   padding: 6px 16px 4px;
#   font-size: 10px; font-weight: 600; color: #4b5563;
#   text-transform: uppercase; letter-spacing: .1em;
# }

# /* ── KPI cards ── */
# .kpi-grid { display: grid; grid-template-columns: repeat(4,1fr); gap: 16px; margin-bottom: 24px; }
# .kpi-card {
#   background: var(--card); border-radius: 14px; padding: 22px 20px;
#   border: 1px solid var(--border); box-shadow: var(--shadow);
#   display: flex; gap: 14px; align-items: flex-start;
#   transition: box-shadow .2s;
# }
# .kpi-card:hover { box-shadow: var(--shadow-lg); }
# .kpi-icon {
#   width: 48px; height: 48px; border-radius: 12px; flex-shrink: 0;
#   display: flex; align-items: center; justify-content: center; font-size: 22px;
# }
# .kpi-body { flex: 1; min-width: 0; }
# .kpi-label { font-size: 12px; color: var(--text2); font-weight: 500;
#              text-transform: uppercase; letter-spacing: .06em; margin-bottom: 6px; }
# .kpi-value { font-size: 26px; font-weight: 700; color: var(--text); line-height: 1; }
# .kpi-unit  { font-size: 13px; font-weight: 500; color: var(--text2); margin-left: 3px; }
# .kpi-meta  { font-size: 12px; color: var(--text3); margin-top: 7px; }
# .kpi-meta b { color: var(--text2); font-weight: 500; }

# /* ── Page header ── */
# .page-hdr { margin-bottom: 24px; }
# .page-hdr h1 { font-size: 22px; font-weight: 700; color: var(--text); }
# .page-hdr p  { font-size: 13px; color: var(--text2); margin-top: 4px; }

# /* ── Section header ── */
# .sec-hdr {
#   font-size: 14px; font-weight: 600; color: var(--text);
#   margin-bottom: 14px; padding-bottom: 10px;
#   border-bottom: 1px solid var(--border);
#   display: flex; align-items: center; gap: 8px;
# }

# /* ── Card wrapper ── */
# .card {
#   background: var(--card); border-radius: 14px; padding: 20px 22px;
#   border: 1px solid var(--border); box-shadow: var(--shadow); margin-bottom: 16px;
# }
# .card-title {
#   font-size: 15px; font-weight: 600; color: var(--text);
#   margin-bottom: 16px; padding-bottom: 12px; border-bottom: 1px solid var(--border);
# }

# /* ── Inverter card ── */
# .inv-card {
#   background: var(--card); border-radius: 14px; padding: 20px 22px;
#   border: 1px solid var(--border); box-shadow: var(--shadow);
#   margin-bottom: 14px; transition: border-color .15s, box-shadow .15s;
# }
# .inv-card:hover { border-color: var(--accent); box-shadow: var(--shadow-lg); }
# .inv-card.alert { border-left: 3px solid var(--red); }
# .inv-header {
#   display: flex; justify-content: space-between; align-items: flex-start;
#   margin-bottom: 16px; padding-bottom: 14px; border-bottom: 1px solid var(--border);
# }
# .inv-name { font-size: 15px; font-weight: 700; color: var(--text); }
# .inv-meta { font-size: 11px; color: var(--text3); margin-top: 3px; }
# .inv-params { display: grid; grid-template-columns: repeat(6,1fr); gap: 14px; }
# .param-label { font-size: 10px; color: var(--text2); text-transform: uppercase;
#                letter-spacing: .07em; margin-bottom: 3px; }
# .param-val   { font-size: 16px; font-weight: 600; color: var(--text); }
# .param-unit  { font-size: 11px; color: var(--text3); margin-left: 2px; }
# .inv-footer  { margin-top: 12px; font-size: 11px; color: var(--text3); }

# /* ── Table ── */
# .tbl { background: var(--card); border-radius: 14px; border: 1px solid var(--border);
#        overflow: hidden; box-shadow: var(--shadow); }
# .tbl-hdr, .tbl-row {
#   display: grid; padding: 0 20px; align-items: center; gap: 10px;
# }
# .tbl-hdr {
#   background: #f8fafc; border-bottom: 1px solid var(--border);
#   font-size: 11px; font-weight: 600; color: var(--text2);
#   text-transform: uppercase; letter-spacing: .07em; height: 42px;
# }
# .tbl-row {
#   min-height: 52px; border-bottom: 1px solid var(--border);
#   font-size: 13px; transition: background .1s;
# }
# .tbl-row:last-child { border-bottom: none; }
# .tbl-row:hover { background: #fafbfc; }
# .tbl-plant  { grid-template-columns: 2fr 1fr 1.1fr 1fr 1fr 1.1fr 1.3fr 1fr; }
# .tbl-alarm  { grid-template-columns: 1fr 1fr 1fr 1.5fr 1.4fr 2.2fr 1.2fr; }
# .cell-link  { color: var(--accent); font-weight: 600; cursor: pointer; }
# .cell-link:hover { text-decoration: underline; }

# /* ── Badges ── */
# .badge {
#   display: inline-flex; align-items: center; gap: 5px;
#   font-size: 11px; font-weight: 600; padding: 3px 10px; border-radius: 20px;
# }
# .badge::before { content:''; width:6px; height:6px; border-radius:50%; }
# .b-online  { background: var(--green-l);  color: #15803d; }
# .b-online::before  { background: var(--green); }
# .b-offline { background: var(--red-l);    color: #b91c1c; }
# .b-offline::before { background: var(--red); }
# .b-warning { background: var(--yellow-l); color: #92400e; }
# .b-warning::before { background: var(--yellow); }
# .b-unknown { background: #f1f5f9; color: #64748b; }
# .b-unknown::before { background: #94a3b8; }
# .b-active  { background: var(--red-l);    color: #b91c1c; }
# .b-active::before  { background: var(--red); }
# .b-resolved{ background: var(--green-l);  color: #15803d; }
# .b-resolved::before{ background: var(--green); }
# .b-critical{ background: var(--red-l);    color: #b91c1c; font-weight:700; }
# .b-critical::before{ background: var(--red); }

# /* ── Brand chips ── */
# .chip {
#   display: inline-block; font-size: 10px; font-weight: 700; padding: 2px 8px;
#   border-radius: 5px; letter-spacing: .08em; text-transform: uppercase;
# }
# .chip-solis   { background: #dbeafe; color: #1d4ed8; }
# .chip-growatt { background: #dcfce7; color: #15803d; }
# .chip-sungrow { background: #ffedd5; color: #c2410c; }

# /* ── Alert strip ── */
# .alert-strip {
#   background: #fef2f2; border: 1px solid #fecaca; border-radius: 10px;
#   padding: 14px 18px; margin-bottom: 18px; display: flex; gap: 12px; align-items: flex-start;
# }
# .alert-strip-ico { font-size: 18px; flex-shrink: 0; }
# .alert-strip-ttl { font-size: 14px; font-weight: 600; color: var(--red); }
# .alert-strip-msg { font-size: 13px; color: #7f1d1d; margin-top: 2px; }

# /* ── Stat row (summary bar) ── */
# .stat-row {
#   background: var(--card); border-radius: 12px; padding: 14px 22px;
#   border: 1px solid var(--border); display: flex; gap: 28px; margin-bottom: 20px;
#   align-items: center; flex-wrap: wrap;
# }
# .stat-item { text-align: center; }
# .stat-val { font-size: 18px; font-weight: 700; color: var(--text); }
# .stat-lbl { font-size: 11px; color: var(--text3); margin-top: 2px; }

# /* ── Streamlit overrides ── */
# .stButton > button {
#   background: var(--accent) !important; color: #fff !important;
#   border: none !important; border-radius: 8px !important;
#   font-family: 'Inter', sans-serif !important; font-weight: 600 !important;
#   font-size: 13px !important; padding: 9px 22px !important;
#   transition: opacity .15s !important;
# }
# .stButton > button:hover { opacity: .88 !important; }
# div[data-testid="stSelectbox"] > label,
# div[data-testid="stTextInput"]  > label { font-size: 12px !important; font-weight: 500 !important; }
# [data-testid="stRadio"] > label { font-size: 13px !important; }
# .stRadio > div { gap: 4px !important; }
# .stAlert { border-radius: 10px !important; }
# </style>
# """, unsafe_allow_html=True)

# # ── Bootstrap ─────────────────────────────────────────────────
# init_db()
# st_autorefresh(interval=REFRESH_INTERVAL_SECONDS * 1000, key="solar_ar")

# # ── Helpers ──────────────────────────────────────────────────
# def f(v, d=1, na="—"):
#     try:    return f"{float(v):.{d}f}"
#     except: return na

# def badge(s, kind=None):
#     s = (s or "").strip()
#     sl = s.lower()
#     if kind == "level":
#         cls = "b-critical" if sl == "critical" else "b-warning"
#     elif kind == "status_alarm":
#         cls = "b-active" if sl == "active" else "b-resolved"
#     else:
#         if sl == "online":            cls = "b-online"
#         elif sl in ("offline","fault"): cls = "b-offline"
#         else:                          cls = "b-unknown"
#     return f'<span class="badge {cls}">{s}</span>'

# def chip(b):
#     return f'<span class="chip chip-{(b or "").lower()}">{b}</span>'

# def earn(kwh):
#     v = float(kwh or 0) * RATE_PER_KWH
#     if v >= 1_000_000: return f"₹{v/1_000_000:.3f}M"
#     if v >= 1_000:     return f"₹{v/1_000:.3f}K"
#     return f"₹{v:.2f}"

# def chart(fig, h=300):
#     fig.update_layout(plot_bgcolor="#fff", paper_bgcolor="#fff", font_color="#64748b",
#                       margin=dict(l=0,r=0,t=10,b=0), height=h,
#                       legend=dict(bgcolor="#fff", font=dict(size=12)),
#                       bargap=0.3, font_family="Inter")
#     fig.update_traces(marker_line_width=0)
#     fig.update_xaxes(showgrid=False, zeroline=False, tickfont_size=11)
#     fig.update_yaxes(showgrid=True, gridcolor="#f1f5f9", zeroline=False, tickfont_size=11)
#     return fig

# BRAND_COLORS = {"Solis":"#3b82f6","Growatt":"#22c55e","Sungrow":"#f5821f"}

# # ── Sidebar ──────────────────────────────────────────────────
# with st.sidebar:
#     st.markdown("""
#     <div class="nav-logo">
#       <div class="nav-logo-icon">☀</div>
#       <div class="nav-logo-title">Solar Dashboard</div>
#       <div class="nav-logo-sub">Fractal Energy</div>
#     </div>""", unsafe_allow_html=True)

#     page = st.radio("", ["📊  Overview","🔧  O&M","📈  Report","🗺  Service","⚙️  Settings"],
#                     label_visibility="collapsed")
#     page = page.split("  ",1)[1].strip()

#     st.markdown('<div class="nav-section">Data Sources</div>', unsafe_allow_html=True)
#     sel_brands = [b for b in ["Solis","Growatt","Sungrow"]
#                   if st.checkbox(b, value=(b=="Solis"), key=f"cb_{b}")]

#     st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)
#     if st.button("🔄 Refresh Now"):
#         st.cache_data.clear(); st.rerun()

#     show_debug = st.checkbox("🔍 Debug mode", value=False)

#     st.markdown(
#         f"<div style='padding:16px;font-size:11px;color:#4b5563;border-top:1px solid "
#         f"rgba(255,255,255,.08);margin-top:12px;'>"
#         f"⏱ {datetime.now().strftime('%d %b %Y  %H:%M:%S')}<br>"
#         f"Auto-refresh every {REFRESH_INTERVAL_SECONDS//60} min</div>",
#         unsafe_allow_html=True)

# # ── Fetch + clean data ────────────────────────────────────────
# @st.cache_data(ttl=REFRESH_INTERVAL_SECONDS)
# def load(brands):
#     return fetch_all_brands(list(brands))

# with st.spinner("Fetching live data…"):
#     records = load(tuple(sel_brands))

# alerts = check_alerts(records, st.session_state)

# df = pd.DataFrame()
# if records:
#     df = pd.DataFrame(records)
#     for c in ["power_kw","today_kwh","total_kwh","temperature","voltage","current_a"]:
#         if c in df.columns:
#             df[c] = pd.to_numeric(df[c], errors="coerce")
#     if "status" in df.columns:
#         df["status"] = df["status"].astype(str).str.strip()

# # ── Debug ────────────────────────────────────────────────────
# if show_debug:
#     st.markdown("### 🔍 Debug: Raw API Data")
#     if not df.empty:
#         st.dataframe(df, use_container_width=True)
#         st.write("**power_kw:**",   df["power_kw"].tolist())
#         st.write("**today_kwh:**",  df["today_kwh"].tolist())
#         st.write("**total_kwh (MWh):**", df["total_kwh"].tolist())

#     st.markdown("### 🔍 Debug: userStationList raw fields")
#     try:
#         from utils.solis_api import fetch_summary as _fsum, _raw_plants_cache
#         summ = _fsum()
#         st.write("**fetch_summary() returned:**", summ)
#         if _raw_plants_cache:
#             st.markdown("**First plant — all fields:**")
#             p = _raw_plants_cache[0]
#             rows = [{"field": k, "value": str(v)} for k, v in sorted(p.items())]
#             import pandas as _pd
#             st.dataframe(_pd.DataFrame(rows), use_container_width=True, hide_index=True)
#             st.markdown("**Fields likely containing energy:**")
#             energy_keys = [k for k in p if any(x in k.lower() for x in
#                           ["energy","power","kwh","mwh","day","month","all","total","yield"])]
#             for k in sorted(energy_keys):
#                 st.write(f"  `{k}` = `{p.get(k)}`")
#     except Exception as ex:
#         st.error(f"Debug error: {ex}")
#     st.divider()


# # ═════════════════════════════════════════════════════════════
# #  OVERVIEW
# # ═════════════════════════════════════════════════════════════
# if page == "Overview":
#     st.markdown('<div class="page-hdr"><h1>Plant Overview</h1>'
#                 '<p>Real-time performance across all plants</p></div>',
#                 unsafe_allow_html=True)

#     if df.empty:
#         st.warning("⚠️ No data. Verify credentials in config.py and click Refresh.")
#         if not show_debug:
#             st.info("💡 Enable **Debug mode** in the sidebar to inspect the API response.")
#         st.stop()

#     # ── KPI values ───────────────────────────────────────────
#     # Fallback from inverter-level data
#     total_power  = float(df["power_kw"].sum())
#     daily_kwh    = float(df["today_kwh"].sum())
#     total_mwh    = float(df["total_kwh"].sum())
#     monthly_mwh  = 0.0

#     # Prefer plant-level summary from Solis API (more accurate, correct units)
#     try:
#         if "Solis" in sel_brands:
#             from utils.solis_api import fetch_summary as _fs
#             summ = _fs()
#             if summ.get("power_kw",    0) > 0: total_power = float(summ["power_kw"])
#             if summ.get("daily_kwh",   0) > 0: daily_kwh   = float(summ["daily_kwh"])
#             if summ.get("monthly_mwh", 0) > 0: monthly_mwh = float(summ["monthly_mwh"])
#             if summ.get("total_mwh",   0) > 0: total_mwh   = float(summ["total_mwh"])
#     except Exception:
#         pass

#     # Monthly fallback from DB if API returned 0
#     if monthly_mwh == 0:
#         hist = get_history(hours=720)
#         monthly_kwh_db = daily_kwh
#         if not hist.empty and "today_kwh" in hist.columns:
#             hist["fetched_at"] = pd.to_datetime(hist["fetched_at"])
#             hist["today_kwh"]  = pd.to_numeric(hist["today_kwh"], errors="coerce")
#             m = hist[hist["fetched_at"].dt.month == datetime.now().month]
#             if not m.empty:
#                 v = float(m.groupby([m["fetched_at"].dt.date,"inverter_sn"])["today_kwh"].max().sum())
#                 monthly_kwh_db = max(v, daily_kwh)
#         monthly_mwh = monthly_kwh_db / 1000

#     monthly_kwh = monthly_mwh * 1000   # kWh for earnings

#     # ── Display formatting — match Solis exactly ─────────────
#     # Daily: kWh → show as MWh when >= 1000 kWh  (e.g. 2424 kWh → 2.424 MWh)
#     if daily_kwh >= 1000:
#         daily_val, daily_unit = f(daily_kwh / 1000, 3), "MWh"
#     else:
#         daily_val, daily_unit = f(daily_kwh, 1), "kWh"

#     # Monthly: always MWh  (e.g. 59.39 MWh)
#     monthly_val, monthly_unit = f(monthly_mwh, 3), "MWh"

#     # Total: show GWh when >= 1000 MWh  (e.g. 1751 MWh → 1.751 GWh)
#     if total_mwh >= 1000:
#         total_val, total_unit = f(total_mwh / 1000, 3), "GWh"
#         total_kwh_earn = total_mwh * 1000
#     else:
#         total_val, total_unit = f(total_mwh, 3), "MWh"
#         total_kwh_earn = total_mwh * 1000

#     n_on = int((df["status"].str.lower()=="online").sum())
#     n_tot= len(df)

#     col1,col2,col3,col4 = st.columns(4)
#     kpis = [
#         (col1,"⚡","power","Power",f(total_power,2),"kW",
#          f"Inverters: <b>{n_on}/{n_tot} online</b>"),
#         (col2,"🔋","daily","Daily Yield", daily_val, daily_unit,
#          f"Earning today: <b>{earn(daily_kwh)}</b>"),
#         (col3,"📅","monthly","Monthly Yield", monthly_val, monthly_unit,
#          f"Earning this month: <b>{earn(monthly_kwh)}</b>"),
#         (col4,"📊","total","Total Yield", total_val, total_unit,
#          f"Total earning: <b>{earn(total_kwh_earn)}</b>"),
#     ]
#     icon_bg = {"power":"#fff4eb","daily":"#fff4eb","monthly":"#eff6ff","total":"#fffbeb"}
#     for col,ico,kind,lbl,val,unit,meta in kpis:
#         with col:
#             st.markdown(f"""
#             <div class="kpi-card">
#               <div class="kpi-icon" style="background:{icon_bg[kind]};">{ico}</div>
#               <div class="kpi-body">
#                 <div class="kpi-label">{lbl}</div>
#                 <div class="kpi-value">{val}<span class="kpi-unit">{unit}</span></div>
#                 <div class="kpi-meta">{meta}</div>
#               </div>
#             </div>""", unsafe_allow_html=True)

#     # ── Alert strip ───────────────────────────────────────────
#     if alerts:
#         for a in alerts[:3]:
#             st.markdown(f"""
#             <div class="alert-strip">
#               <div class="alert-strip-ico">🚨</div>
#               <div>
#                 <div class="alert-strip-ttl">{a['plant_name']} — {a.get('inverter_sn','')}</div>
#                 <div class="alert-strip-msg">{a['issue']}</div>
#               </div>
#             </div>""", unsafe_allow_html=True)

#     # ── Charts row ────────────────────────────────────────────
#     ch1, ch2 = st.columns([3,2])

#     with ch1:
#         st.markdown('<div class="sec-hdr">⚡ Power by Plant (kW)</div>', unsafe_allow_html=True)
#         pdf = df.groupby(["plant_name","brand"])["power_kw"].sum().reset_index()
#         fig = px.bar(pdf, x="plant_name", y="power_kw", color="brand",
#                      color_discrete_map=BRAND_COLORS,
#                      labels={"power_kw":"Power (kW)","plant_name":"","brand":"Brand"})
#         st.plotly_chart(chart(fig,280), use_container_width=True)

#     with ch2:
#         st.markdown('<div class="sec-hdr">📊 Daily Yield Share</div>', unsafe_allow_html=True)
#         pief = df.groupby("plant_name")["today_kwh"].sum().reset_index()
#         fig2 = px.pie(pief, names="plant_name", values="today_kwh",
#                       color_discrete_sequence=px.colors.qualitative.Pastel,
#                       hole=0.45)
#         fig2.update_traces(textposition="outside", textinfo="label+percent")
#         fig2.update_layout(plot_bgcolor="#fff", paper_bgcolor="#fff",
#                            font_family="Inter", font_color="#64748b",
#                            margin=dict(l=0,r=0,t=10,b=0), height=280,
#                            showlegend=False)
#         st.plotly_chart(fig2, use_container_width=True)

#     # ── Plant summary table ───────────────────────────────────
#     st.markdown('<div class="sec-hdr" style="margin-top:8px;">🌱 Plant List</div>',
#                 unsafe_allow_html=True)

#     ps = (df.groupby(["plant_name","brand"])
#           .agg(power_kw=("power_kw","sum"),
#                today_kwh=("today_kwh","sum"),
#                total_kwh=("total_kwh","sum"),
#                inv_count=("inverter_sn","count"))
#           .reset_index())

#     st.markdown('<div class="tbl">', unsafe_allow_html=True)
#     st.markdown(
#         '<div class="tbl-hdr tbl-plant">'
#         '<div>Plant Name</div><div>Brand</div><div>Inverters</div>'
#         '<div>Power (kW)</div><div>Daily Yield</div>'
#         '<div>Total Yield</div><div>Earning Today</div><div>Status</div>'
#         '</div>', unsafe_allow_html=True)

#     for _, row in ps.iterrows():
#         pr  = df[df["plant_name"]==row["plant_name"]]
#         on  = int((pr["status"].str.lower()=="online").sum())
#         tot = int(row["inv_count"])
#         pst = "Online" if on==tot and tot>0 else ("Offline" if on==0 else "Warning")
#         dy  = float(row["today_kwh"] or 0)
#         dy_str = f"{dy/1000:.3f} MWh" if dy >= 1000 else f"{dy:.1f} kWh"
#         # Total yield per plant: stored as MWh, show GWh if >= 1000
#         ty = float(row["total_kwh"] or 0)
#         ty_str = f"{ty/1000:.3f} GWh" if ty >= 1000 else f"{ty:.3f} MWh"
#         st.markdown(
#             f'<div class="tbl-row tbl-plant">'
#               f'<div class="cell-link">{row["plant_name"]}</div>'
#               f'<div>{chip(row["brand"])}</div>'
#               f'<div>{on}/{tot}</div>'
#               f'<div><b>{f(row["power_kw"],2)}</b> kW</div>'
#               f'<div>{dy_str}</div>'
#               f'<div>{ty_str}</div>'
#               f'<div>{earn(dy)}</div>'
#               f'<div>{badge(pst)}</div>'
#             f'</div>', unsafe_allow_html=True)
#     st.markdown('</div>', unsafe_allow_html=True)


# # ═════════════════════════════════════════════════════════════
# #  O&M
# # ═════════════════════════════════════════════════════════════
# elif page == "O&M":
#     sub = st.radio("", ["🔔  Alarm Information","⚡  Device Overview"],
#                    horizontal=True, label_visibility="collapsed")
#     sub = sub.split("  ",1)[1].strip()
#     st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

#     # Build alarm list
#     alarm_log = get_alert_log(200)
#     all_alarms = []
#     for a in alerts:
#         all_alarms.append({"device_type":"Inverter","level":"Critical","status":"Active",
#             "plant_name":a.get("plant_name","—"),"sn":a.get("inverter_sn","—"),
#             "content":a.get("issue","—"),"brand":a.get("brand","—"),
#             "time":datetime.now().strftime("%Y-%m-%d %H:%M")})
#     if not alarm_log.empty:
#         for _, r in alarm_log.iterrows():
#             all_alarms.append({"device_type":"Inverter","level":"Warning","status":"Resolved",
#                 "plant_name":r.get("plant_name","—"),"sn":r.get("inverter_sn","—"),
#                 "content":r.get("issue","—"),"brand":r.get("brand","—"),
#                 "time":r.get("alerted_at","—")})

#     # ── Alarm Information ─────────────────────────────────────
#     if sub == "Alarm Information":
#         st.markdown('<div class="page-hdr"><h1>Alarm Information</h1>'
#                     '<p>All detected faults and alert history</p></div>',
#                     unsafe_allow_html=True)

#         plant_opts = ["All"] + sorted({a["plant_name"] for a in all_alarms if a["plant_name"]!="—"})
#         sn_opts    = ["All"] + sorted({a["sn"]         for a in all_alarms if a["sn"]        !="—"})
#         brand_opts = ["All"] + sorted({a["brand"]       for a in all_alarms if a["brand"]     !="—"})

#         with st.container():
#             fc1,fc2,fc3,fc4,fc5 = st.columns(5)
#             with fc1: fp = st.selectbox("Plant Name",  plant_opts)
#             with fc2: fs = st.selectbox("SN",          sn_opts)
#             with fc3: fb = st.selectbox("Brand",       brand_opts)
#             with fc4: fst= st.selectbox("Status",      ["All","Active","Resolved"])
#             with fc5: fl = st.selectbox("Level",       ["All","Critical","Warning"])

#         filt = all_alarms[:]
#         if fp  !="All": filt=[a for a in filt if a["plant_name"]==fp]
#         if fs  !="All": filt=[a for a in filt if a["sn"]        ==fs]
#         if fb  !="All": filt=[a for a in filt if a["brand"]     ==fb]
#         if fst !="All": filt=[a for a in filt if a["status"]    ==fst]
#         if fl  !="All": filt=[a for a in filt if a["level"]     ==fl]

#         # Summary counts
#         n_active  = sum(1 for a in filt if a["status"]=="Active")
#         n_resolved= sum(1 for a in filt if a["status"]=="Resolved")
#         sc1,sc2,sc3 = st.columns(3)
#         sc1.metric("Total Alarms",    len(filt))
#         sc2.metric("Active",   n_active,   delta_color="inverse")
#         sc3.metric("Resolved", n_resolved)

#         if not filt:
#             st.success("✅ No alarms match the current filters — all systems normal.")
#         else:
#             st.markdown('<div class="tbl">', unsafe_allow_html=True)
#             st.markdown(
#                 '<div class="tbl-hdr tbl-alarm">'
#                 '<div>Device Type</div><div>Level</div><div>Status</div>'
#                 '<div>Plant Name</div><div>SN</div><div>Issue</div><div>Time</div>'
#                 '</div>', unsafe_allow_html=True)
#             for a in filt:
#                 st.markdown(
#                     f'<div class="tbl-row tbl-alarm">'
#                       f'<div>{a["device_type"]}</div>'
#                       f'<div>{badge(a["level"],"level")}</div>'
#                       f'<div>{badge(a["status"],"status_alarm")}</div>'
#                       f'<div>{chip(a["brand"])} {a["plant_name"]}</div>'
#                       f'<div style="font-size:11px;color:var(--text3);">{a["sn"]}</div>'
#                       f'<div>{a["content"]}</div>'
#                       f'<div style="font-size:11px;color:var(--text3);">{a["time"]}</div>'
#                     f'</div>', unsafe_allow_html=True)
#             st.markdown('</div>', unsafe_allow_html=True)

#     # ── Device Overview ───────────────────────────────────────
#     else:
#         st.markdown('<div class="page-hdr"><h1>Device Overview</h1>'
#                     '<p>Live readings for every inverter</p></div>',
#                     unsafe_allow_html=True)
#         if df.empty:
#             st.warning("⚠️ No data."); st.stop()

#         brand_opts2 = ["All"] + sorted(df["brand"].dropna().unique())
#         plant_opts2 = ["All"] + sorted(df["plant_name"].dropna().unique())
#         sn_opts2    = ["All"] + sorted(df["inverter_sn"].dropna().unique())
#         stat_opts2  = ["All"] + sorted(df["status"].dropna().unique())

#         fc1,fc2,fc3,fc4 = st.columns(4)
#         with fc1: bf = st.selectbox("Brand",  brand_opts2, key="do_b")
#         with fc2: pf = st.selectbox("Plant",  plant_opts2, key="do_p")
#         with fc3: sf = st.selectbox("S/N",    sn_opts2,    key="do_s")
#         with fc4: stf= st.selectbox("Status", stat_opts2,  key="do_st")

#         vw = df.copy()
#         if bf !="All": vw=vw[vw["brand"]       ==bf]
#         if pf !="All": vw=vw[vw["plant_name"]  ==pf]
#         if sf !="All": vw=vw[vw["inverter_sn"] ==sf]
#         if stf!="All": vw=vw[vw["status"]      ==stf]

#         # Summary strip
#         st.markdown(
#             f'<div class="stat-row">'
#               f'<div class="stat-item"><div class="stat-val">{len(vw)}</div>'
#               f'<div class="stat-lbl">Inverters</div></div>'
#               f'<div class="stat-item"><div class="stat-val">'
#               f'{f(vw["power_kw"].sum(),2)} kW</div>'
#               f'<div class="stat-lbl">Total Power</div></div>'
#               f'<div class="stat-item"><div class="stat-val">'
#               f'{f(vw["today_kwh"].sum(),1)} kWh</div>'
#               f'<div class="stat-lbl">Daily Yield</div></div>'
#               f'<div class="stat-item"><div class="stat-val">'
#               f'{int((vw["status"].str.lower()=="online").sum())}</div>'
#               f'<div class="stat-lbl">Online</div></div>'
#             f'</div>', unsafe_allow_html=True)

#         alert_sns = {a.get("inverter_sn") for a in alerts}
#         for _, row in vw.iterrows():
#             sn    = str(row.get("inverter_sn","N/A"))
#             brand = str(row.get("brand",""))
#             st_   = str(row.get("status",""))
#             params = [
#                 ("Power Now",   f(row.get("power_kw"),2),  "kW"),
#                 ("Daily Yield", f(row.get("today_kwh"),1), "kWh"),
#                 ("Total Yield", f(row.get("total_kwh"),3), "MWh"),
#                 ("Temperature", f(row.get("temperature"),1),"°C"),
#                 ("AC Voltage",  f(row.get("voltage"),1),   "V"),
#                 ("AC Current",  f(row.get("current_a"),1), "A"),
#             ]
#             p_html = "".join(
#                 f'<div><div class="param-label">{l}</div>'
#                 f'<div class="param-val">{v}<span class="param-unit"> {u}</span></div></div>'
#                 for l,v,u in params)
#             a_cls = "inv-card alert" if sn in alert_sns else "inv-card"
#             st.markdown(
#                 f'<div class="{a_cls}">'
#                   f'<div class="inv-header">'
#                     f'<div><div class="inv-name">{row.get("plant_name","")}</div>'
#                     f'<div class="inv-meta">S/N: {sn} &nbsp;·&nbsp; {chip(brand)}'
#                     f' &nbsp;·&nbsp; {row.get("last_update","—")}</div></div>'
#                     + badge(st_) +
#                   f'</div>'
#                   f'<div class="inv-params">{p_html}</div>'
#                 f'</div>', unsafe_allow_html=True)


# # ═════════════════════════════════════════════════════════════
# #  REPORT
# # ═════════════════════════════════════════════════════════════
# elif page == "Report":
#     st.markdown('<div class="page-hdr"><h1>Plant Report</h1>'
#                 '<p>Historical generation analysis</p></div>',
#                 unsafe_allow_html=True)

#     rtype = st.radio("", ["Daily","Monthly","Annual","Total"],
#                      horizontal=True, label_visibility="collapsed")

#     plant_opts = (["All Plants"] + sorted(df["plant_name"].dropna().unique())
#                   if not df.empty else ["No data"])
#     fc1,fc2 = st.columns([2,1])
#     with fc1: sel_plant = st.selectbox("Select Plant", plant_opts)
#     with fc2: sel_date  = st.date_input("Date", value=date.today())

#     hist_df = get_history(hours=8760)
#     if hist_df.empty:
#         st.info("📭 No history yet — data accumulates every 5 minutes. Come back soon.")
#         st.stop()

#     hist_df["fetched_at"] = pd.to_datetime(hist_df["fetched_at"])
#     hist_df["power_kw"]   = pd.to_numeric(hist_df.get("power_kw"), errors="coerce")
#     hist_df["today_kwh"]  = pd.to_numeric(hist_df.get("today_kwh"),errors="coerce")
#     hist_df["total_kwh"]  = pd.to_numeric(hist_df.get("total_kwh"),errors="coerce")

#     if sel_plant != "All Plants":
#         hist_df = hist_df[hist_df["plant_name"]==sel_plant]

#     if rtype == "Daily":
#         day = hist_df[hist_df["fetched_at"].dt.date==sel_date].sort_values("fetched_at")
#         if day.empty:
#             st.info(f"No data for {sel_date}.")
#         else:
#             fig = px.line(day, x="fetched_at", y="power_kw", color="inverter_sn",
#                           labels={"fetched_at":"Time","power_kw":"Power (kW)","inverter_sn":"Inverter"})
#             st.plotly_chart(chart(fig,320), use_container_width=True)
#             sm = (day.groupby(["plant_name","inverter_sn","brand"])
#                   .agg(Peak_kW=("power_kw","max"), Daily_kWh=("today_kwh","max"))
#                   .reset_index())
#             sm.columns = ["Plant","S/N","Brand","Peak Power (kW)","Daily Yield (kWh)"]
#             st.dataframe(sm, use_container_width=True, hide_index=True)

#     elif rtype == "Monthly":
#         mdf = hist_df[(hist_df["fetched_at"].dt.year==sel_date.year) &
#                       (hist_df["fetched_at"].dt.month==sel_date.month)]
#         if mdf.empty:
#             st.info(f"No data for {sel_date.strftime('%B %Y')}.")
#         else:
#             daily = mdf.groupby(mdf["fetched_at"].dt.date)["today_kwh"].max().reset_index()
#             daily.columns = ["Date","Daily Yield (kWh)"]
#             fig = px.bar(daily, x="Date", y="Daily Yield (kWh)",
#                          color_discrete_sequence=[BRAND_COLORS["Solis"]])
#             st.plotly_chart(chart(fig,300), use_container_width=True)
#             tot = daily["Daily Yield (kWh)"].sum()
#             m1,m2 = st.columns(2)
#             m1.metric("Month Total", f"{tot:.1f} kWh")
#             m2.metric("Estimated Earning", earn(tot))

#     elif rtype == "Annual":
#         ydf = hist_df[hist_df["fetched_at"].dt.year==sel_date.year]
#         if ydf.empty:
#             st.info(f"No data for {sel_date.year}.")
#         else:
#             monthly = ydf.groupby(ydf["fetched_at"].dt.month)["today_kwh"].sum().reset_index()
#             monthly.columns = ["Month","kWh"]
#             monthly["Month"] = monthly["Month"].apply(
#                 lambda m: date(sel_date.year,int(m),1).strftime("%b"))
#             fig = px.bar(monthly, x="Month", y="kWh", color_discrete_sequence=["#3b82f6"])
#             st.plotly_chart(chart(fig,300), use_container_width=True)

#     else:  # Total
#         yearly = hist_df.groupby(hist_df["fetched_at"].dt.year)["today_kwh"].sum().reset_index()
#         yearly.columns = ["Year","kWh"]
#         fig = px.bar(yearly, x="Year", y="kWh", color_discrete_sequence=["#22c55e"])
#         st.plotly_chart(chart(fig,280), use_container_width=True)
#         if not df.empty:
#             gt = (df.groupby(["plant_name","brand"])["total_kwh"].sum().reset_index()
#                   .rename(columns={"plant_name":"Plant","brand":"Brand","total_kwh":"Total Yield (MWh)"}))
#             st.dataframe(gt, use_container_width=True, hide_index=True)


# # ═════════════════════════════════════════════════════════════
# #  SERVICE  (Plant Management)
# # ═════════════════════════════════════════════════════════════
# elif page == "Service":
#     st.markdown('<div class="page-hdr"><h1>Plant Management</h1>'
#                 '<p>All registered plants and their details</p></div>',
#                 unsafe_allow_html=True)

#     if df.empty:
#         st.warning("⚠️ No data."); st.stop()

#     brand_opts = ["All"] + sorted(df["brand"].dropna().unique())
#     plant_opts = ["All"] + sorted(df["plant_name"].dropna().unique())

#     fc1,fc2 = st.columns(2)
#     with fc1: pf2 = st.selectbox("Plant", plant_opts, key="pm_p")
#     with fc2: bf2 = st.selectbox("Brand", brand_opts, key="pm_b")

#     ps = (df.groupby(["plant_name","brand"])
#           .agg(power_kw=("power_kw","sum"),today_kwh=("today_kwh","sum"),
#                total_kwh=("total_kwh","sum"),inv_count=("inverter_sn","count"))
#           .reset_index())
#     if pf2!="All": ps=ps[ps["plant_name"]==pf2]
#     if bf2!="All": ps=ps[ps["brand"]==bf2]

#     # Summary
#     st.markdown(
#         f'<div class="stat-row">'
#           f'<div class="stat-item"><div class="stat-val">{len(ps)}</div>'
#           f'<div class="stat-lbl">Plants</div></div>'
#           f'<div class="stat-item"><div class="stat-val">'
#           f'{f(ps["power_kw"].sum(),2)} kW</div>'
#           f'<div class="stat-lbl">Total Power</div></div>'
#           f'<div class="stat-item"><div class="stat-val">'
#           f'{f(ps["today_kwh"].sum(),1)} kWh</div>'
#           f'<div class="stat-lbl">Daily Yield</div></div>'
#           f'<div class="stat-item"><div class="stat-val">'
#           f'{f(ps["total_kwh"].sum(),1)} MWh</div>'
#           f'<div class="stat-lbl">Total Yield</div></div>'
#         f'</div>', unsafe_allow_html=True)

#     st.markdown('<div class="tbl">', unsafe_allow_html=True)
#     st.markdown(
#         '<div class="tbl-hdr tbl-plant">'
#         '<div>Plant Name</div><div>Brand</div><div>Organisation</div>'
#         '<div>Inverters</div><div>Power (kW)</div>'
#         '<div>Daily Yield</div><div>Total Yield</div><div>Status</div>'
#         '</div>', unsafe_allow_html=True)

#     for _, row in ps.iterrows():
#         pr  = df[df["plant_name"]==row["plant_name"]]
#         on  = int((pr["status"].str.lower()=="online").sum())
#         tot = int(row["inv_count"])
#         pst = "Online" if on==tot and tot>0 else ("Offline" if on==0 else "Warning")
#         dy  = float(row["today_kwh"] or 0)
#         dy_str = f"{dy/1000:.3f} MWh" if dy >= 1000 else f"{dy:.1f} kWh"
#         ty  = float(row["total_kwh"] or 0)
#         ty_str2 = f"{ty/1000:.3f} GWh" if ty >= 1000 else f"{ty:.3f} MWh"
#         st.markdown(
#             f'<div class="tbl-row tbl-plant">'
#               f'<div class="cell-link">{row["plant_name"]}</div>'
#               f'<div>{chip(row["brand"])}</div>'
#               f'<div>Fractal Energy</div>'
#               f'<div>{on}/{tot}</div>'
#               f'<div><b>{f(row["power_kw"],2)}</b> kW</div>'
#               f'<div>{dy_str}</div>'
#               f'<div>{ty_str2}</div>'
#               f'<div>{badge(pst)}</div>'
#             f'</div>', unsafe_allow_html=True)
#     st.markdown('</div>', unsafe_allow_html=True)


# # ═════════════════════════════════════════════════════════════
# #  SETTINGS
# # ═════════════════════════════════════════════════════════════
# elif page == "Settings":
#     st.markdown('<div class="page-hdr"><h1>Settings</h1>'
#                 '<p>API credentials, alerts and app configuration</p></div>',
#                 unsafe_allow_html=True)

#     from config import (SOLIS_API_KEY,GROWATT_USERNAME,SUNGROW_APP_KEY,
#                         EMAIL_USER,TO_EMAILS,RATE_PER_KWH)

#     st.markdown("#### 🔑 API Credentials")
#     creds = [
#         ("Solis",   bool(SOLIS_API_KEY),
#          SOLIS_API_KEY[:10]+"…" if SOLIS_API_KEY else "Not configured"),
#         ("Growatt", bool(GROWATT_USERNAME),
#          GROWATT_USERNAME or "Set GROWATT_USERNAME in config.py"),
#         ("Sungrow", bool(SUNGROW_APP_KEY),
#          SUNGROW_APP_KEY[:10]+"…" if SUNGROW_APP_KEY else "Set SUNGROW_APP_KEY in config.py"),
#     ]
#     for brand,ok,hint in creds:
#         c1,c2,c3 = st.columns([1,1,4])
#         c1.markdown(f"**{brand}**")
#         c2.markdown("✅ Connected" if ok else "⚠️ Not set")
#         c3.markdown(f"`{hint}`")

#     st.divider()
#     st.markdown("#### 📧 Email Alerts")
#     st.markdown(f"**Sender:** `{EMAIL_USER}`")
#     st.markdown(f"**Recipients:** `{', '.join(TO_EMAILS)}`")

#     st.divider()
#     st.markdown("#### 💰 Tariff Rate")
#     st.info(f"Current rate: **₹{RATE_PER_KWH}/kWh** — edit `RATE_PER_KWH` in config.py")

#     st.divider()
#     st.markdown("#### 🗂 Project Files")
#     st.code("""
# solar_dashboard/
# ├── app.py              ← Run this:  streamlit run app.py
# ├── config.py           ← ✏️  All credentials & settings
# ├── requirements.txt
# ├── data/
# │   └── solar_data.db   ← Auto-created SQLite database
# └── utils/
#     ├── solis_api.py    ← Solis Cloud connector
#     ├── growatt_api.py  ← Growatt connector
#     ├── sungrow_api.py  ← Sungrow iSolarCloud connector
#     ├── aggregator.py   ← Merges brands + alert logic
#     ├── database.py     ← SQLite read/write
#     └── alerts.py       ← Email notifications
#     """, language="")

# ============================================================
#  app.py  —  Solar Dashboard  |  streamlit run app.py
# ============================================================
# import streamlit as st
# from streamlit_autorefresh import st_autorefresh
# import pandas as pd
# import plotly.express as px
# import plotly.graph_objects as go
# from datetime import datetime, date, timedelta

# from config import REFRESH_INTERVAL_SECONDS, RATE_PER_KWH
# from utils.database import init_db, get_history, get_alert_log
# from utils.aggregator import fetch_all_brands, check_alerts

# # ─────────────────────────────────────────────────────────────
# st.set_page_config(page_title="Solar Dashboard · Fractal Energy",
#                    page_icon="☀️", layout="wide",
#                    initial_sidebar_state="expanded")

# # ══════════════════════════════════════════════════════════════
# #  GLOBAL CSS  —  Navy · Teal · Amber theme
# # ══════════════════════════════════════════════════════════════
# st.markdown("""
# <style>
# @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

# *,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}

# :root{
#   /* ── Palette ── */
#   --navy:      #0a1628;
#   --navy2:     #0f2044;
#   --navy3:     #1a2f5a;
#   --teal:      #0d9488;
#   --teal-l:    #ccfbf1;
#   --teal-d:    #0f766e;
#   --amber:     #f59e0b;
#   --amber-l:   #fef3c7;
#   --amber-d:   #d97706;
#   --orange:    #f97316;
#   --orange-l:  #ffedd5;
#   --red:       #ef4444;
#   --red-l:     #fee2e2;
#   --green:     #10b981;
#   --green-l:   #d1fae5;
#   --sky:       #38bdf8;
#   --sky-l:     #e0f2fe;

#   /* ── Surfaces ── */
#   --bg:        #f0f4f8;
#   --card:      #ffffff;
#   --border:    #e2e8f0;
#   --border2:   #cbd5e1;

#   /* ── Text ── */
#   --text:      #0f172a;
#   --text2:     #475569;
#   --text3:     #94a3b8;

#   /* ── Shadows ── */
#   --shadow:    0 1px 4px rgba(10,22,40,.06),0 4px 20px rgba(10,22,40,.05);
#   --shadow-lg: 0 8px 40px rgba(10,22,40,.12);
#   --shadow-teal:0 4px 20px rgba(13,148,136,.25);
# }

# /* ── Fonts ── */
# html,body,[data-testid="stAppViewContainer"]{
#   background:var(--bg)!important;
#   font-family:'Plus Jakarta Sans',sans-serif!important;
#   color:var(--text);
# }
# [data-testid="stHeader"]{background:transparent!important;display:none;}
# #MainMenu,footer{visibility:hidden;}
# [data-testid="stDecoration"]{display:none;}
# .block-container{padding:28px 32px!important;max-width:100%!important;}

# /* ══ SIDEBAR ══════════════════════════════════════════════ */
# [data-testid="stSidebar"]{
#   background:var(--navy)!important;
#   border-right:1px solid rgba(255,255,255,.06)!important;
# }
# [data-testid="stSidebar"]>div{padding-top:0!important;}
# section[data-testid="stSidebarContent"]{padding:0!important;}

# .sb-logo{
#   padding:24px 20px 18px;
#   border-bottom:1px solid rgba(255,255,255,.07);
#   margin-bottom:6px;
#   display:flex;align-items:center;gap:12px;
# }
# .sb-logo-icon{
#   width:42px;height:42px;background:linear-gradient(135deg,var(--teal),var(--teal-d));
#   border-radius:12px;display:flex;align-items:center;justify-content:center;
#   font-size:20px;flex-shrink:0;box-shadow:var(--shadow-teal);
# }
# .sb-logo-title{color:#fff;font-weight:800;font-size:15px;letter-spacing:-.3px;}
# .sb-logo-sub{color:#64748b;font-size:11px;margin-top:1px;}
# .sb-section{
#   padding:14px 20px 4px;
#   font-size:10px;font-weight:700;color:#334155;
#   text-transform:uppercase;letter-spacing:.12em;
# }
# .sb-time{
#   padding:14px 20px;font-size:11px;color:#475569;
#   border-top:1px solid rgba(255,255,255,.06);margin-top:6px;
#   font-family:'JetBrains Mono',monospace;
# }

# /* ══ LOGIN PAGE ═══════════════════════════════════════════ */
# .login-wrap{
#   min-height:100vh;display:flex;align-items:center;justify-content:center;
#   background:linear-gradient(135deg,var(--navy) 0%,var(--navy2) 50%,#0d2b4e 100%);
#   padding:20px;
# }
# .login-card{
#   background:rgba(255,255,255,.04);
#   border:1px solid rgba(255,255,255,.1);
#   border-radius:20px;padding:48px 44px;width:100%;max-width:420px;
#   backdrop-filter:blur(20px);
#   box-shadow:0 20px 60px rgba(0,0,0,.4);
# }
# .login-logo{
#   width:60px;height:60px;
#   background:linear-gradient(135deg,var(--teal),var(--teal-d));
#   border-radius:16px;display:flex;align-items:center;justify-content:center;
#   font-size:28px;margin:0 auto 20px;
#   box-shadow:0 8px 24px rgba(13,148,136,.4);
# }
# .login-title{
#   font-size:24px;font-weight:800;color:#fff;text-align:center;
#   letter-spacing:-.4px;margin-bottom:6px;
# }
# .login-sub{font-size:13px;color:#64748b;text-align:center;margin-bottom:32px;}
# .login-label{font-size:13px;font-weight:600;color:#94a3b8;margin-bottom:6px;}
# .login-error{
#   background:rgba(239,68,68,.12);border:1px solid rgba(239,68,68,.3);
#   border-radius:8px;padding:10px 14px;font-size:13px;color:#fca5a5;
#   margin-bottom:16px;text-align:center;
# }

# /* ══ PAGE HEADER ══════════════════════════════════════════ */
# .page-hdr{margin-bottom:24px;}
# .page-hdr h1{
#   font-size:24px;font-weight:800;color:var(--text);
#   letter-spacing:-.5px;line-height:1.2;
# }
# .page-hdr p{font-size:13px;color:var(--text3);margin-top:4px;}

# /* ══ KPI CARDS ════════════════════════════════════════════ */
# .kpi-card{
#   background:var(--card);border-radius:16px;padding:24px 22px;
#   border:1px solid var(--border);box-shadow:var(--shadow);
#   display:flex;gap:16px;align-items:flex-start;
#   transition:transform .15s,box-shadow .15s;
#   position:relative;overflow:hidden;
# }
# .kpi-card::after{
#   content:'';position:absolute;top:0;left:0;right:0;height:3px;
#   background:linear-gradient(90deg,var(--teal),var(--sky));
#   border-radius:16px 16px 0 0;
# }
# .kpi-card.amber::after{background:linear-gradient(90deg,var(--amber),var(--orange));}
# .kpi-card.green::after{background:linear-gradient(90deg,var(--green),var(--teal));}
# .kpi-card.navy::after{background:linear-gradient(90deg,var(--navy3),var(--sky));}
# .kpi-card:hover{transform:translateY(-2px);box-shadow:var(--shadow-lg);}

# .kpi-icon{
#   width:50px;height:50px;border-radius:13px;flex-shrink:0;
#   display:flex;align-items:center;justify-content:center;font-size:22px;
# }
# .kpi-icon.teal  {background:var(--teal-l);color:var(--teal);}
# .kpi-icon.amber {background:var(--amber-l);color:var(--amber-d);}
# .kpi-icon.green {background:var(--green-l);color:var(--green);}
# .kpi-icon.navy  {background:var(--sky-l);color:#0284c7;}

# .kpi-label{
#   font-size:11px;color:var(--text3);font-weight:700;
#   text-transform:uppercase;letter-spacing:.1em;margin-bottom:6px;
# }
# .kpi-value{
#   font-size:28px;font-weight:800;color:var(--text);
#   line-height:1;letter-spacing:-.5px;
# }
# .kpi-unit{font-size:14px;font-weight:600;color:var(--text2);margin-left:3px;}
# .kpi-meta{font-size:12px;color:var(--text3);margin-top:8px;line-height:1.4;}
# .kpi-meta b{color:var(--teal);font-weight:600;}

# /* ══ SECTION HEADER ═══════════════════════════════════════ */
# .sec-hdr{
#   font-size:13px;font-weight:700;color:var(--text);
#   display:flex;align-items:center;gap:8px;
#   margin-bottom:14px;padding-bottom:10px;
#   border-bottom:2px solid var(--border);
# }
# .sec-hdr-dot{
#   width:8px;height:8px;border-radius:50%;
#   background:linear-gradient(135deg,var(--teal),var(--sky));
#   flex-shrink:0;
# }

# /* ══ CARD WRAPPER ═════════════════════════════════════════ */
# .card{
#   background:var(--card);border-radius:16px;padding:22px;
#   border:1px solid var(--border);box-shadow:var(--shadow);margin-bottom:16px;
# }

# /* ══ INVERTER CARD ════════════════════════════════════════ */
# .inv-card{
#   background:var(--card);border-radius:16px;padding:22px;
#   border:1px solid var(--border);box-shadow:var(--shadow);
#   margin-bottom:14px;transition:border-color .15s,box-shadow .15s;
# }
# .inv-card:hover{border-color:var(--primary);box-shadow:var(--shadow-teal);}
# .inv-card.alert-card{border-left:3px solid var(--red);}
# .inv-header{
#   display:flex;justify-content:space-between;align-items:flex-start;
#   margin-bottom:18px;padding-bottom:14px;
#   border-bottom:1px solid var(--border);
# }
# .inv-name{font-size:15px;font-weight:700;color:var(--text);letter-spacing:-.3px;}
# .inv-meta{font-size:11px;color:var(--text3);margin-top:3px;font-family:'JetBrains Mono',monospace;}
# .inv-params{display:grid;grid-template-columns:repeat(6,1fr);gap:16px;}
# .param-label{
#   font-size:10px;color:var(--text3);text-transform:uppercase;
#   letter-spacing:.08em;font-weight:600;margin-bottom:4px;
# }
# .param-val{font-size:18px;font-weight:700;color:var(--text);letter-spacing:-.3px;}
# .param-unit{font-size:11px;color:var(--text3);margin-left:2px;}
# .inv-footer{margin-top:14px;font-size:11px;color:var(--text3);font-family:'JetBrains Mono',monospace;}

# /* ══ TABLES ═══════════════════════════════════════════════ */
# .tbl{
#   background:var(--card);border-radius:16px;
#   border:1px solid var(--border);overflow:hidden;box-shadow:var(--shadow);
# }
# .tbl-hdr,.tbl-row{
#   display:grid;padding:0 20px;align-items:center;gap:10px;
# }
# .tbl-hdr{
#   background:linear-gradient(90deg,#f8fafc,#f1f5f9);
#   border-bottom:2px solid var(--border);
#   font-size:10px;font-weight:700;color:var(--text3);
#   text-transform:uppercase;letter-spacing:.1em;height:44px;
# }
# .tbl-row{
#   min-height:54px;border-bottom:1px solid var(--border);
#   font-size:13px;transition:background .1s;
# }
# .tbl-row:last-child{border-bottom:none;}
# .tbl-row:hover{background:#f8fafc;}
# .tbl-plant{grid-template-columns:2fr 1fr 1.1fr 1fr 1fr 1.1fr 1.3fr 1fr;}
# .tbl-alarm{grid-template-columns:1fr 1fr 1fr 1.5fr 1.4fr 2.2fr 1.2fr;}
# .cell-link{color:var(--primary);font-weight:700;cursor:pointer;font-size:13px;}

# /* ══ BADGES ═══════════════════════════════════════════════ */
# .badge{
#   display:inline-flex;align-items:center;gap:5px;
#   font-size:11px;font-weight:700;padding:4px 10px;
#   border-radius:20px;letter-spacing:.02em;
# }
# .badge::before{content:'';width:6px;height:6px;border-radius:50%;}
# .b-online {background:var(--green-l);color:#065f46;}
# .b-online::before{background:var(--green);}
# .b-offline{background:var(--red-l);color:#991b1b;}
# .b-offline::before{background:var(--red);}
# .b-warning{background:var(--amber-l);color:#92400e;}
# .b-warning::before{background:var(--amber);}
# .b-unknown{background:#f1f5f9;color:#64748b;}
# .b-unknown::before{background:#94a3b8;}
# .b-active {background:var(--red-l);color:#991b1b;}
# .b-active::before{background:var(--red);}
# .b-resolved{background:var(--green-l);color:#065f46;}
# .b-resolved::before{background:var(--green);}
# .b-critical{background:var(--red-l);color:#991b1b;font-weight:800;}
# .b-critical::before{background:var(--red);}

# /* ══ CHIPS ════════════════════════════════════════════════ */
# .chip{
#   display:inline-block;font-size:10px;font-weight:800;
#   padding:3px 9px;border-radius:6px;
#   letter-spacing:.1em;text-transform:uppercase;
# }
# .chip-solis  {background:#dbeafe;color:#1e40af;}
# .chip-growatt{background:#d1fae5;color:#065f46;}
# .chip-sungrow{background:#ffedd5;color:#c2410c;}

# /* ══ ALERT STRIP ══════════════════════════════════════════ */
# .alert-strip{
#   background:linear-gradient(135deg,#fff1f2,#ffe4e6);
#   border:1px solid #fecdd3;border-left:4px solid var(--red);
#   border-radius:12px;padding:16px 18px;margin-bottom:12px;
#   display:flex;gap:14px;align-items:flex-start;
# }
# .alert-strip-ico{font-size:20px;flex-shrink:0;}
# .alert-strip-ttl{font-size:14px;font-weight:700;color:var(--red);}
# .alert-strip-msg{font-size:12px;color:#7f1d1d;margin-top:3px;}

# /* ══ STAT ROW ═════════════════════════════════════════════ */
# .stat-row{
#   background:var(--card);border-radius:14px;padding:16px 24px;
#   border:1px solid var(--border);display:flex;gap:32px;
#   margin-bottom:20px;align-items:center;flex-wrap:wrap;
#   box-shadow:var(--shadow);
# }
# .stat-item{text-align:center;}
# .stat-val{font-size:20px;font-weight:800;color:var(--text);letter-spacing:-.3px;}
# .stat-lbl{font-size:10px;color:var(--text3);margin-top:2px;font-weight:600;text-transform:uppercase;letter-spacing:.08em;}

# /* ══ STREAMLIT OVERRIDES ══════════════════════════════════ */
# .stButton>button{
#   background:linear-gradient(135deg,var(--teal),var(--teal-d))!important;
#   color:#fff!important;border:none!important;border-radius:10px!important;
#   font-family:'Plus Jakarta Sans',sans-serif!important;
#   font-weight:700!important;font-size:13px!important;
#   padding:10px 24px!important;letter-spacing:.01em!important;
#   box-shadow:0 4px 12px rgba(13,148,136,.3)!important;
#   transition:all .15s!important;
# }
# .stButton>button:hover{transform:translateY(-1px)!important;box-shadow:0 6px 20px rgba(13,148,136,.4)!important;}
# div[data-testid="stSelectbox"]>label,
# div[data-testid="stTextInput"]>label{
#   font-size:12px!important;font-weight:700!important;
#   color:var(--text2)!important;text-transform:uppercase!important;letter-spacing:.06em!important;
# }
# [data-testid="stRadio"]>label{font-size:13px!important;font-weight:600!important;}
# .stRadio>div{gap:4px!important;}
# .stAlert{border-radius:12px!important;}
# div[data-testid="stTextInput"] input{
#   border-radius:10px!important;border-color:var(--border2)!important;
#   font-size:14px!important;font-family:'Plus Jakarta Sans',sans-serif!important;
# }
# div[data-testid="stSelectbox"]>div>div{
#   border-radius:10px!important;border-color:var(--border2)!important;
#   font-size:13px!important;
# }

# /* ══ LOGIN STREAMLIT INPUT OVERRIDES ═══════════════════════ */
# .login-page [data-testid="stTextInput"] input{
#   background:rgba(255,255,255,.08)!important;
#   border:1px solid rgba(255,255,255,.15)!important;
#   border-radius:10px!important;color:#fff!important;
#   font-size:14px!important;padding:12px 14px!important;
# }
# .login-page .stButton>button{
#   width:100%!important;padding:14px!important;font-size:15px!important;
# }

# /* ══ DIVIDER ══════════════════════════════════════════════ */
# .divider{height:1px;background:var(--border);margin:20px 0;}

# /* ══ METRIC OVERRIDES ═════════════════════════════════════ */
# [data-testid="stMetric"]{
#   background:var(--card);border-radius:12px;padding:16px 18px;
#   border:1px solid var(--border);box-shadow:var(--shadow);
# }
# [data-testid="stMetricLabel"]{font-size:11px!important;font-weight:700!important;color:var(--text3)!important;text-transform:uppercase!important;letter-spacing:.08em!important;}
# [data-testid="stMetricValue"]{font-size:24px!important;font-weight:800!important;color:var(--text)!important;letter-spacing:-.4px!important;}
# </style>
# """, unsafe_allow_html=True)

# # ══════════════════════════════════════════════════════════════
# #  INIT
# # ══════════════════════════════════════════════════════════════
# init_db()

# # ══════════════════════════════════════════════════════════════
# #  LOGIN
# # ══════════════════════════════════════════════════════════════
# USERS = {
#     "admin": "1234"
# }

# if "logged_in" not in st.session_state:
#     st.session_state.logged_in = False
#     st.session_state.user = ""

# if not st.session_state.logged_in:
#     # Full-screen dark login — hide sidebar
#     st.markdown("""
#     <style>
#     [data-testid="stSidebar"]{display:none!important;}
#     .block-container{padding:0!important;max-width:100%!important;}
#     </style>""", unsafe_allow_html=True)

#     st.markdown("""
#     <div style="min-height:100vh;display:flex;align-items:center;justify-content:center;
#     background:linear-gradient(135deg,#0a1628 0%,#0f2044 55%,#0d2b4e 100%);padding:20px;">
#       <div style="width:100%;max-width:420px;">
#         <div style="text-align:center;margin-bottom:32px;">
#           <div style="width:68px;height:68px;background:linear-gradient(135deg,#0d9488,#0f766e);
#             border-radius:18px;display:flex;align-items:center;justify-content:center;
#             font-size:32px;margin:0 auto 16px;box-shadow:0 8px 24px rgba(13,148,136,.4);">☀️</div>
#           <div style="font-size:26px;font-weight:800;color:#fff;letter-spacing:-.5px;">Solar Dashboard</div>
#           <div style="font-size:13px;color:#64748b;margin-top:6px;">Fractal Energy · Monitoring Platform</div>
#         </div>
#         <div style="background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.1);
#           border-radius:20px;padding:36px 32px;backdrop-filter:blur(20px);
#           box-shadow:0 20px 60px rgba(0,0,0,.4);">
#     """, unsafe_allow_html=True)

#     email    = st.text_input("Email Address",    placeholder="your@email.com")
#     password = st.text_input("Password",         placeholder="••••••••", type="password")

#     if st.button("Sign In →", use_container_width=True):
#         if email in USERS and USERS[email] == password:
#             st.session_state.logged_in = True
#             st.session_state.user = email
#             st.rerun()
#         else:
#             st.error("Invalid email or password. Please try again.")

#     st.markdown("""
#         <div style="text-align:center;margin-top:20px;font-size:12px;color:#475569;">
#           Secured by Fractal Energy · v2.0
#         </div>
#         </div></div></div>
#     """, unsafe_allow_html=True)
#     st.stop()

# # ══════════════════════════════════════════════════════════════
# #  AUTHENTICATED APP
# # ══════════════════════════════════════════════════════════════
# st_autorefresh(interval=REFRESH_INTERVAL_SECONDS * 1000, key="solar_ar")

# # ── Helpers ──────────────────────────────────────────────────
# def f(v, d=1, na="—"):
#     try:    return f"{float(v):.{d}f}"
#     except: return na

# def badge(s, kind=None):
#     s  = (s or "").strip()
#     sl = s.lower()
#     if kind == "level":
#         cls = "b-critical" if sl == "critical" else "b-warning"
#     elif kind == "status_alarm":
#         cls = "b-active" if sl == "active" else "b-resolved"
#     else:
#         if sl == "online":              cls = "b-online"
#         elif sl in ("offline","fault"): cls = "b-offline"
#         else:                           cls = "b-unknown"
#     return f'<span class="badge {cls}">{s}</span>'

# def chip(b):
#     return f'<span class="chip chip-{(b or "").lower()}">{b}</span>'

# def earn(kwh):
#     v = float(kwh or 0) * RATE_PER_KWH
#     if v >= 1_000_000: return f"₹{v/1_000_000:.3f}M"
#     if v >= 1_000:     return f"₹{v/1_000:.3f}K"
#     return f"₹{v:.2f}"

# def chart_style(fig, h=300):
#     fig.update_layout(
#         plot_bgcolor="#fff", paper_bgcolor="#fff",
#         font_color="#64748b", font_family="Inter",
#         margin=dict(l=0,r=0,t=16,b=0), height=h,
#         legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=12, color="#64748b")),
#         bargap=0.28,
#     )
#     fig.update_traces(marker_line_width=0)
#     fig.update_xaxes(showgrid=False, zeroline=False, tickfont_size=11,
#                      tickfont_color="#94a3b8", linecolor="#e2e8f0")
#     fig.update_yaxes(showgrid=True, gridcolor="#f1f5f9", zeroline=False,
#                      tickfont_size=11, tickfont_color="#94a3b8")
#     return fig

# PALETTE = ["#0d9488","#f59e0b","#3b82f6","#f97316","#10b981","#8b5cf6","#06b6d4","#ec4899"]
# BRAND_COLORS = {"Solis":"#3b82f6","Growatt":"#10b981","Sungrow":"#f97316"}

# def sec(title, icon=""):
#     st.markdown(f'<div class="sec-hdr"><div class="sec-hdr-dot"></div>{icon} {title}</div>',
#                 unsafe_allow_html=True)

# # ── Sidebar ──────────────────────────────────────────────────
# with st.sidebar:
#     st.markdown(f"""
#     <div class="sb-logo">
#       <div class="sb-logo-icon">☀</div>
#       <div>
#         <div class="sb-logo-title">Solar Dashboard</div>
#         <div class="sb-logo-sub">Fractal Energy</div>
#       </div>
#     </div>""", unsafe_allow_html=True)

#     page = st.radio("", ["📊  Overview","🔧  O&M","📈  Report","🗺  Service","⚙️  Settings"],
#                     label_visibility="collapsed")
#     page = page.split("  ",1)[1].strip()

#     st.markdown('<div class="sb-section">Data Sources</div>', unsafe_allow_html=True)
#     sel_brands = [b for b in ["Solis","Growatt","Sungrow"]
#                   if st.checkbox(b, value=(b=="Solis"), key=f"cb_{b}")]

#     st.markdown('<div style="height:6px"></div>', unsafe_allow_html=True)
#     if st.button("🔄  Refresh Now"):
#         st.cache_data.clear(); st.rerun()

#     show_debug = st.checkbox("🔍  Debug", value=False)

#     # Logout
#     st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)
#     if st.button("🚪  Sign Out"):
#         st.session_state.logged_in = False
#         st.rerun()

#     st.markdown(f"""
#     <div class="sb-time">
#       ⏱ {datetime.now().strftime('%d %b %Y')}<br>
#       <b style="color:#94a3b8;">{datetime.now().strftime('%H:%M:%S')}</b><br>
#       <span style="color:#334155;">Auto-refresh {REFRESH_INTERVAL_SECONDS//60} min</span>
#     </div>""", unsafe_allow_html=True)

# # ── Fetch data ────────────────────────────────────────────────
# @st.cache_data(ttl=REFRESH_INTERVAL_SECONDS)
# def load(brands):
#     return fetch_all_brands(list(brands))

# with st.spinner("Fetching live data…"):
#     records = load(tuple(sel_brands))

# alerts = check_alerts(records, st.session_state)

# df = pd.DataFrame()
# if records:
#     df = pd.DataFrame(records)
#     for c in ["power_kw","today_kwh","total_kwh","temperature","voltage","current_a"]:
#         if c in df.columns:
#             df[c] = pd.to_numeric(df[c], errors="coerce")
#     if "status" in df.columns:
#         df["status"] = df["status"].astype(str).str.strip()

# # ── Debug ─────────────────────────────────────────────────────
# if show_debug and not df.empty:
#     st.markdown("### 🔍 Debug: Raw API Data")
#     st.dataframe(df, use_container_width=True)
#     try:
#         from utils.solis_api import fetch_summary as _fsum, _raw_plants_cache
#         summ = _fsum()
#         st.write("**fetch_summary():**", summ)
#     except Exception as ex:
#         st.error(f"Debug error: {ex}")
#     st.divider()


# # ══════════════════════════════════════════════════════════════
# #  OVERVIEW
# # ══════════════════════════════════════════════════════════════
# if page == "Overview":
#     st.markdown('<div class="page-hdr"><h1>Plant Overview</h1>'
#                 '<p>Real-time performance across all plants</p></div>',
#                 unsafe_allow_html=True)

#     if df.empty:
#         st.warning("⚠️ No data. Check credentials in config.py and click Refresh.")
#         st.stop()

#     # ── KPI values ────────────────────────────────────────────
#     total_power = float(df["power_kw"].sum())
#     daily_kwh   = float(df["today_kwh"].sum())
#     total_mwh   = float(df["total_kwh"].sum())
#     monthly_mwh = 0.0

#     try:
#         if "Solis" in sel_brands:
#             from utils.solis_api import fetch_summary as _fs
#             summ = _fs()
#             if summ.get("power_kw",    0) > 0: total_power = float(summ["power_kw"])
#             if summ.get("daily_kwh",   0) > 0: daily_kwh   = float(summ["daily_kwh"])
#             if summ.get("monthly_mwh", 0) > 0: monthly_mwh = float(summ["monthly_mwh"])
#             if summ.get("total_mwh",   0) > 0: total_mwh   = float(summ["total_mwh"])
#     except Exception: pass

#     if monthly_mwh == 0:
#         hist = get_history(hours=720)
#         monthly_kwh_db = daily_kwh
#         if not hist.empty and "today_kwh" in hist.columns:
#             hist["fetched_at"] = pd.to_datetime(hist["fetched_at"])
#             hist["today_kwh"]  = pd.to_numeric(hist["today_kwh"], errors="coerce")
#             m = hist[hist["fetched_at"].dt.month == datetime.now().month]
#             if not m.empty:
#                 v = float(m.groupby([m["fetched_at"].dt.date,"inverter_sn"])["today_kwh"].max().sum())
#                 monthly_kwh_db = max(v, daily_kwh)
#         monthly_mwh = monthly_kwh_db / 1000
#     monthly_kwh = monthly_mwh * 1000

#     # Display units
#     daily_val,daily_unit = (f(daily_kwh/1000,3),"MWh") if daily_kwh>=1000 else (f(daily_kwh,1),"kWh")
#     mo_val,mo_unit       = f(monthly_mwh,3), "MWh"
#     if total_mwh >= 1000:
#         tot_val,tot_unit,tot_earn = f(total_mwh/1000,3),"GWh",total_mwh*1000
#     else:
#         tot_val,tot_unit,tot_earn = f(total_mwh,3),"MWh",total_mwh*1000

#     n_on  = int((df["status"].str.lower()=="online").sum())
#     n_tot = len(df)

#     # ── 4 KPI cards ──────────────────────────────────────────
#     c1,c2,c3,c4 = st.columns(4)
#     kpis = [
#         (c1,"teal","teal","⚡","Power",f(total_power,2),"kW",
#          f"Inverters: <b>{n_on}/{n_tot} online</b>"),
#         (c2,"amber","amber","🔋","Daily Yield",daily_val,daily_unit,
#          f"Earning today: <b>{earn(daily_kwh)}</b>"),
#         (c3,"green","green","📅","Monthly Yield",mo_val,mo_unit,
#          f"Earning this month: <b>{earn(monthly_kwh)}</b>"),
#         (c4,"navy","navy","📊","Total Yield",tot_val,tot_unit,
#          f"Total earning: <b>{earn(tot_earn)}</b>"),
#     ]
#     for col,card_cls,ico_cls,ico,lbl,val,unit,meta in kpis:
#         with col:
#             st.markdown(f"""
#             <div class="kpi-card {card_cls}">
#               <div class="kpi-icon {ico_cls}">{ico}</div>
#               <div>
#                 <div class="kpi-label">{lbl}</div>
#                 <div class="kpi-value">{val}<span class="kpi-unit"> {unit}</span></div>
#                 <div class="kpi-meta">{meta}</div>
#               </div>
#             </div>""", unsafe_allow_html=True)

#     st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)

#     # ── Alert strips ─────────────────────────────────────────
#     if alerts:
#         for a in alerts[:3]:
#             st.markdown(f"""
#             <div class="alert-strip">
#               <div class="alert-strip-ico">🚨</div>
#               <div>
#                 <div class="alert-strip-ttl">{a['plant_name']} — {a.get('inverter_sn','')}</div>
#                 <div class="alert-strip-msg">{a['issue']}</div>
#               </div>
#             </div>""", unsafe_allow_html=True)

#     # ── Charts ───────────────────────────────────────────────
#     ch1, ch2 = st.columns([3, 2])

#     with ch1:
#         sec("Power by Plant (kW)")
#         pdf = df.groupby(["plant_name","brand"])["power_kw"].sum().reset_index()
#         fig = px.bar(pdf, x="plant_name", y="power_kw", color="brand",
#                      color_discrete_map=BRAND_COLORS,
#                      labels={"power_kw":"Power (kW)","plant_name":"","brand":"Brand"})
#         fig.update_traces(marker_cornerradius=4)
#         st.plotly_chart(chart_style(fig, 290), use_container_width=True)

#     with ch2:
#         sec("Daily Yield Share")
#         pief = df.groupby("plant_name")["today_kwh"].sum().reset_index()
#         fig2 = go.Figure(go.Pie(
#             labels=pief["plant_name"],
#             values=pief["today_kwh"],
#             hole=0.52,
#             marker=dict(colors=PALETTE, line=dict(color="#fff", width=2)),
#             textposition="outside",
#             textinfo="label+percent",
#             textfont=dict(size=11, family="Plus Jakarta Sans"),
#             pull=[0.04]*len(pief),
#         ))
#         fig2.update_layout(
#             plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
#             font_family="Inter", font_color="#64748b",
#             margin=dict(l=60, r=60, t=20, b=20), height=290,
#             showlegend=False,
#             annotations=[dict(text=f"<b>{f(pief['today_kwh'].sum(),1)}</b><br>kWh",
#                               font=dict(size=14,color="#0f172a",family="Plus Jakarta Sans"),
#                               showarrow=False)]
#         )
#         st.plotly_chart(fig2, use_container_width=True)

#     # ── Plant table ──────────────────────────────────────────
#     sec("Plant List")
#     ps = (df.groupby(["plant_name","brand"])
#           .agg(power_kw=("power_kw","sum"), today_kwh=("today_kwh","sum"),
#                total_kwh=("total_kwh","sum"), inv_count=("inverter_sn","count"))
#           .reset_index())

#     st.markdown('<div class="tbl">', unsafe_allow_html=True)
#     st.markdown(
#         '<div class="tbl-hdr tbl-plant">'
#         '<div>Plant Name</div><div>Brand</div><div>Inverters</div>'
#         '<div>Power (kW)</div><div>Daily Yield</div>'
#         '<div>Total Yield</div><div>Earning Today</div><div>Status</div>'
#         '</div>', unsafe_allow_html=True)

#     for _, row in ps.iterrows():
#         pr   = df[df["plant_name"]==row["plant_name"]]
#         on   = int((pr["status"].str.lower()=="online").sum())
#         tot  = int(row["inv_count"])
#         pst  = "Online" if on==tot and tot>0 else ("Offline" if on==0 else "Warning")
#         dy   = float(row["today_kwh"] or 0)
#         dy_s = f"{dy/1000:.3f} MWh" if dy>=1000 else f"{dy:.1f} kWh"
#         ty   = float(row["total_kwh"] or 0)
#         ty_s = f"{ty/1000:.3f} GWh" if ty>=1000 else f"{ty:.3f} MWh"
#         st.markdown(
#             f'<div class="tbl-row tbl-plant">'
#               f'<div class="cell-link">{row["plant_name"]}</div>'
#               f'<div>{chip(row["brand"])}</div>'
#               f'<div>{on}/{tot}</div>'
#               f'<div><b>{f(row["power_kw"],2)}</b> kW</div>'
#               f'<div>{dy_s}</div><div>{ty_s}</div>'
#               f'<div>{earn(dy)}</div><div>{badge(pst)}</div>'
#             f'</div>', unsafe_allow_html=True)
#     st.markdown('</div>', unsafe_allow_html=True)


# # ══════════════════════════════════════════════════════════════
# #  O&M
# # ══════════════════════════════════════════════════════════════
# elif page == "O&M":
#     sub = st.radio("", ["🔔  Alarm Information","⚡  Device Overview"],
#                    horizontal=True, label_visibility="collapsed")
#     sub = sub.split("  ",1)[1].strip()
#     st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

#     alarm_log = get_alert_log(200)
#     all_alarms = []
#     for a in alerts:
#         all_alarms.append({"device_type":"Inverter","level":"Critical","status":"Active",
#             "plant_name":a.get("plant_name","—"),"sn":a.get("inverter_sn","—"),
#             "content":a.get("issue","—"),"brand":a.get("brand","—"),
#             "time":datetime.now().strftime("%Y-%m-%d %H:%M")})
#     if not alarm_log.empty:
#         for _, r in alarm_log.iterrows():
#             all_alarms.append({"device_type":"Inverter","level":"Warning","status":"Resolved",
#                 "plant_name":r.get("plant_name","—"),"sn":r.get("inverter_sn","—"),
#                 "content":r.get("issue","—"),"brand":r.get("brand","—"),
#                 "time":r.get("alerted_at","—")})

#     if sub == "Alarm Information":
#         st.markdown('<div class="page-hdr"><h1>Alarm Information</h1>'
#                     '<p>Fault detection and alert history</p></div>',
#                     unsafe_allow_html=True)

#         plant_opts = ["All"] + sorted(df["plant_name"].dropna().unique()) if not df.empty else ["All"]
#         sn_opts    = ["All"] + sorted(df["inverter_sn"].dropna().unique()) if not df.empty else ["All"]
#         brand_opts = ["All"] + sorted(df["brand"].dropna().unique())       if not df.empty else ["All"]

#         fc1,fc2,fc3,fc4,fc5 = st.columns(5)
#         with fc1: fp = st.selectbox("Plant Name",  plant_opts)
#         with fc2: fs = st.selectbox("S/N",         sn_opts)
#         with fc3: fb = st.selectbox("Brand",        brand_opts)
#         with fc4: fst= st.selectbox("Status",       ["All","Active","Resolved"])
#         with fc5: fl = st.selectbox("Level",        ["All","Critical","Warning"])

#         filt = all_alarms[:]
#         if fp !="All": filt=[a for a in filt if a["plant_name"]==fp]
#         if fs !="All": filt=[a for a in filt if a["sn"]        ==fs]
#         if fb !="All": filt=[a for a in filt if a["brand"]     ==fb]
#         if fst!="All": filt=[a for a in filt if a["status"]    ==fst]
#         if fl !="All": filt=[a for a in filt if a["level"]     ==fl]

#         m1,m2,m3 = st.columns(3)
#         m1.metric("Total", len(filt))
#         m2.metric("Active",   sum(1 for a in filt if a["status"]=="Active"))
#         m3.metric("Resolved", sum(1 for a in filt if a["status"]=="Resolved"))

#         if not filt:
#             st.success("✅ No alarms — all systems operating normally.")
#         else:
#             st.markdown('<div class="tbl">', unsafe_allow_html=True)
#             st.markdown('<div class="tbl-hdr tbl-alarm">'
#                         '<div>Device</div><div>Level</div><div>Status</div>'
#                         '<div>Plant</div><div>S/N</div><div>Issue</div><div>Time</div>'
#                         '</div>', unsafe_allow_html=True)
#             for a in filt:
#                 st.markdown(
#                     f'<div class="tbl-row tbl-alarm">'
#                       f'<div>{a["device_type"]}</div>'
#                       f'<div>{badge(a["level"],"level")}</div>'
#                       f'<div>{badge(a["status"],"status_alarm")}</div>'
#                       f'<div>{chip(a["brand"])} {a["plant_name"]}</div>'
#                       f'<div style="font-size:11px;color:var(--text3);font-family:\'JetBrains Mono\',monospace;">{a["sn"]}</div>'
#                       f'<div>{a["content"]}</div>'
#                       f'<div style="font-size:11px;color:var(--text3);">{a["time"]}</div>'
#                     f'</div>', unsafe_allow_html=True)
#             st.markdown('</div>', unsafe_allow_html=True)

#     else:
#         st.markdown('<div class="page-hdr"><h1>Device Overview</h1>'
#                     '<p>Live readings for every inverter</p></div>',
#                     unsafe_allow_html=True)
#         if df.empty:
#             st.warning("⚠️ No data."); st.stop()

#         fc1,fc2,fc3,fc4 = st.columns(4)
#         with fc1: bf = st.selectbox("Brand",  ["All"]+sorted(df["brand"].dropna().unique()),       key="do_b")
#         with fc2: pf = st.selectbox("Plant",  ["All"]+sorted(df["plant_name"].dropna().unique()),  key="do_p")
#         with fc3: sf = st.selectbox("S/N",    ["All"]+sorted(df["inverter_sn"].dropna().unique()), key="do_s")
#         with fc4: stf= st.selectbox("Status", ["All"]+sorted(df["status"].dropna().unique()),      key="do_st")

#         vw = df.copy()
#         if bf !="All": vw=vw[vw["brand"]       ==bf]
#         if pf !="All": vw=vw[vw["plant_name"]  ==pf]
#         if sf !="All": vw=vw[vw["inverter_sn"] ==sf]
#         if stf!="All": vw=vw[vw["status"]      ==stf]

#         st.markdown(
#             f'<div class="stat-row">'
#               f'<div class="stat-item"><div class="stat-val">{len(vw)}</div><div class="stat-lbl">Inverters</div></div>'
#               f'<div class="stat-item"><div class="stat-val">{f(vw["power_kw"].sum(),2)} kW</div><div class="stat-lbl">Total Power</div></div>'
#               f'<div class="stat-item"><div class="stat-val">{f(vw["today_kwh"].sum(),1)} kWh</div><div class="stat-lbl">Daily Yield</div></div>'
#               f'<div class="stat-item"><div class="stat-val">{int((vw["status"].str.lower()=="online").sum())}</div><div class="stat-lbl">Online</div></div>'
#             f'</div>', unsafe_allow_html=True)

#         alert_sns = {a.get("inverter_sn") for a in alerts}
#         for _, row in vw.iterrows():
#             sn    = str(row.get("inverter_sn","N/A"))
#             brand = str(row.get("brand",""))
#             st_   = str(row.get("status",""))
#             params = [
#                 ("Power Now",   f(row.get("power_kw"),2),  "kW"),
#                 ("Daily Yield", f(row.get("today_kwh"),1), "kWh"),
#                 ("Total Yield", f(row.get("total_kwh"),3), "MWh"),
#                 ("Temperature", f(row.get("temperature"),1),"°C"),
#                 ("AC Voltage",  f(row.get("voltage"),1),   "V"),
#                 ("AC Current",  f(row.get("current_a"),1), "A"),
#             ]
#             p_html = "".join(
#                 f'<div><div class="param-label">{l}</div>'
#                 f'<div class="param-val">{v}<span class="param-unit"> {u}</span></div></div>'
#                 for l,v,u in params)
#             border = "border-left:3px solid var(--red);" if sn in alert_sns else ""
#             st.markdown(
#                 f'<div class="inv-card" style="{border}">'
#                   f'<div class="inv-header">'
#                     f'<div><div class="inv-name">{row.get("plant_name","")}</div>'
#                     f'<div class="inv-meta">S/N: {sn} · {chip(brand)} · {row.get("last_update","—")}</div></div>'
#                     + badge(st_) +
#                   f'</div>'
#                   f'<div class="inv-params">{p_html}</div>'
#                 f'</div>', unsafe_allow_html=True)


# # ══════════════════════════════════════════════════════════════
# #  REPORT  —  all line charts
# # ══════════════════════════════════════════════════════════════
# elif page == "Report":
#     st.markdown('<div class="page-hdr"><h1>Plant Report</h1>'
#                 '<p>Historical generation analysis</p></div>',
#                 unsafe_allow_html=True)

#     rtype = st.radio("", ["Daily","Monthly","Annual","Total"],
#                      horizontal=True, label_visibility="collapsed")
#     st.markdown('<div style="height:10px"></div>', unsafe_allow_html=True)

#     plant_opts = (["All Plants"]+sorted(df["plant_name"].dropna().unique())
#                   if not df.empty else ["No data"])
#     fc1,fc2 = st.columns([2,1])
#     with fc1: sel_plant = st.selectbox("Select Plant", plant_opts)
#     with fc2: sel_date  = st.date_input("Date", value=date.today())

#     hist_df = get_history(hours=8760)
#     if hist_df.empty:
#         st.info("📭 No history yet — data accumulates every 5 minutes.")
#         st.stop()

#     hist_df["fetched_at"] = pd.to_datetime(hist_df["fetched_at"])
#     for c in ["power_kw","today_kwh","total_kwh"]:
#         if c in hist_df.columns:
#             hist_df[c] = pd.to_numeric(hist_df[c], errors="coerce")
#     if sel_plant != "All Plants":
#         hist_df = hist_df[hist_df["plant_name"]==sel_plant]

#     # ── Shared line chart style ───────────────────────────────
#     def line_chart(fig, h=340):
#         fig = chart_style(fig, h)
#         # Apply line width only to scatter/line traces, not bar traces
#         fig.update_traces(selector=dict(type="scatter"), line=dict(width=2.5))
#         fig.update_layout(hovermode="x unified")
#         return fig

#     if rtype == "Daily":
#         day = hist_df[hist_df["fetched_at"].dt.date==sel_date].sort_values("fetched_at")
#         if day.empty:
#             st.info(f"No data recorded for {sel_date}.")
#         else:
#             sec("Power Output Throughout the Day (kW)")
#             fig = px.line(day, x="fetched_at", y="power_kw", color="inverter_sn",
#                           color_discrete_sequence=PALETTE,
#                           labels={"fetched_at":"Time","power_kw":"Power (kW)","inverter_sn":"Inverter"})
#             st.plotly_chart(line_chart(fig, 360), use_container_width=True)

#             sec("Daily Energy Generation per Inverter (kWh)")
#             sm = (day.groupby(["plant_name","inverter_sn","brand"])
#                   .agg(Peak_kW=("power_kw","max"), Daily_kWh=("today_kwh","max"))
#                   .reset_index().rename(columns={"plant_name":"Plant","inverter_sn":"S/N","brand":"Brand"}))
#             st.dataframe(sm, use_container_width=True, hide_index=True)

#     elif rtype == "Monthly":
#         mdf = hist_df[(hist_df["fetched_at"].dt.year==sel_date.year) &
#                       (hist_df["fetched_at"].dt.month==sel_date.month)]
#         if mdf.empty:
#             st.info(f"No data for {sel_date.strftime('%B %Y')}.")
#         else:
#             daily = mdf.groupby(mdf["fetched_at"].dt.date)["today_kwh"].max().reset_index()
#             daily.columns = ["Date","Daily Yield (kWh)"]
#             daily["Date"] = pd.to_datetime(daily["Date"])

#             sec(f"Daily Generation — {sel_date.strftime('%B %Y')}")
#             fig = px.line(daily, x="Date", y="Daily Yield (kWh)",
#                           color_discrete_sequence=["#0d9488"],
#                           markers=True)
#             fig.update_traces(line=dict(width=2.5), marker=dict(size=6))
#             fig.add_traces(px.bar(daily, x="Date", y="Daily Yield (kWh)",
#                                   color_discrete_sequence=["rgba(13,148,136,.12)"]).data)
#             st.plotly_chart(line_chart(fig, 360), use_container_width=True)

#             tot = daily["Daily Yield (kWh)"].sum()
#             m1,m2,m3 = st.columns(3)
#             m1.metric("Month Total", f"{tot:.1f} kWh")
#             m2.metric("Month Total (MWh)", f"{tot/1000:.3f} MWh")
#             m3.metric("Estimated Earning", earn(tot))

#     elif rtype == "Annual":
#         ydf = hist_df[hist_df["fetched_at"].dt.year==sel_date.year]
#         if ydf.empty:
#             st.info(f"No data for {sel_date.year}.")
#         else:
#             monthly = ydf.groupby(ydf["fetched_at"].dt.month)["today_kwh"].sum().reset_index()
#             monthly.columns = ["Month","kWh"]
#             monthly["Month"] = monthly["Month"].apply(
#                 lambda m: date(sel_date.year,int(m),1).strftime("%b"))

#             sec(f"Monthly Generation — {sel_date.year}")
#             fig = px.line(monthly, x="Month", y="kWh",
#                           color_discrete_sequence=["#f59e0b"], markers=True)
#             fig.update_traces(line=dict(width=2.5), marker=dict(size=8, color="#f59e0b"))
#             fig.add_traces(px.bar(monthly, x="Month", y="kWh",
#                                   color_discrete_sequence=["rgba(245,158,11,.12)"]).data)
#             st.plotly_chart(line_chart(fig, 360), use_container_width=True)

#     else:  # Total
#         yearly = hist_df.groupby(hist_df["fetched_at"].dt.year)["today_kwh"].sum().reset_index()
#         yearly.columns = ["Year","kWh"]

#         sec("All-time Annual Generation")
#         fig = px.line(yearly, x="Year", y="kWh",
#                       color_discrete_sequence=["#3b82f6"], markers=True)
#         fig.update_traces(line=dict(width=2.5), marker=dict(size=8))
#         st.plotly_chart(line_chart(fig, 320), use_container_width=True)

#         if not df.empty:
#             sec("Total Yield per Plant")
#             gt = (df.groupby(["plant_name","brand"])["total_kwh"].sum().reset_index()
#                   .rename(columns={"plant_name":"Plant","brand":"Brand","total_kwh":"Total Yield (MWh)"}))
#             st.dataframe(gt, use_container_width=True, hide_index=True)


# # ══════════════════════════════════════════════════════════════
# #  SERVICE
# # ══════════════════════════════════════════════════════════════
# elif page == "Service":
#     st.markdown('<div class="page-hdr"><h1>Plant Management</h1>'
#                 '<p>All registered plants and operational details</p></div>',
#                 unsafe_allow_html=True)
#     if df.empty:
#         st.warning("⚠️ No data."); st.stop()

#     fc1,fc2 = st.columns(2)
#     with fc1: pf2 = st.selectbox("Plant", ["All"]+sorted(df["plant_name"].dropna().unique()), key="pm_p")
#     with fc2: bf2 = st.selectbox("Brand", ["All"]+sorted(df["brand"].dropna().unique()),      key="pm_b")

#     ps = (df.groupby(["plant_name","brand"])
#           .agg(power_kw=("power_kw","sum"), today_kwh=("today_kwh","sum"),
#                total_kwh=("total_kwh","sum"), inv_count=("inverter_sn","count"))
#           .reset_index())
#     if pf2!="All": ps=ps[ps["plant_name"]==pf2]
#     if bf2!="All": ps=ps[ps["brand"]==bf2]

#     st.markdown(
#         f'<div class="stat-row">'
#           f'<div class="stat-item"><div class="stat-val">{len(ps)}</div><div class="stat-lbl">Plants</div></div>'
#           f'<div class="stat-item"><div class="stat-val">{f(ps["power_kw"].sum(),2)} kW</div><div class="stat-lbl">Total Power</div></div>'
#           f'<div class="stat-item"><div class="stat-val">{f(ps["today_kwh"].sum(),1)} kWh</div><div class="stat-lbl">Daily Yield</div></div>'
#           f'<div class="stat-item"><div class="stat-val">{f(ps["total_kwh"].sum(),1)} MWh</div><div class="stat-lbl">Total Yield</div></div>'
#         f'</div>', unsafe_allow_html=True)

#     st.markdown('<div class="tbl">', unsafe_allow_html=True)
#     st.markdown('<div class="tbl-hdr tbl-plant">'
#                 '<div>Plant Name</div><div>Brand</div><div>Organisation</div>'
#                 '<div>Inverters</div><div>Power (kW)</div>'
#                 '<div>Daily Yield</div><div>Total Yield</div><div>Status</div>'
#                 '</div>', unsafe_allow_html=True)
#     for _, row in ps.iterrows():
#         pr   = df[df["plant_name"]==row["plant_name"]]
#         on   = int((pr["status"].str.lower()=="online").sum())
#         tot  = int(row["inv_count"])
#         pst  = "Online" if on==tot and tot>0 else ("Offline" if on==0 else "Warning")
#         dy   = float(row["today_kwh"] or 0)
#         dy_s = f"{dy/1000:.3f} MWh" if dy>=1000 else f"{dy:.1f} kWh"
#         ty   = float(row["total_kwh"] or 0)
#         ty_s = f"{ty/1000:.3f} GWh" if ty>=1000 else f"{ty:.3f} MWh"
#         st.markdown(
#             f'<div class="tbl-row tbl-plant">'
#               f'<div class="cell-link">{row["plant_name"]}</div>'
#               f'<div>{chip(row["brand"])}</div>'
#               f'<div>Fractal Energy</div>'
#               f'<div>{on}/{tot}</div>'
#               f'<div><b>{f(row["power_kw"],2)}</b> kW</div>'
#               f'<div>{dy_s}</div><div>{ty_s}</div>'
#               f'<div>{badge(pst)}</div>'
#             f'</div>', unsafe_allow_html=True)
#     st.markdown('</div>', unsafe_allow_html=True)


# # ══════════════════════════════════════════════════════════════
# #  SETTINGS
# # ══════════════════════════════════════════════════════════════
# elif page == "Settings":
#     st.markdown('<div class="page-hdr"><h1>Settings</h1>'
#                 '<p>Credentials, alerts and app configuration</p></div>',
#                 unsafe_allow_html=True)

#     from config import (SOLIS_API_KEY, GROWATT_USERNAME, SUNGROW_APP_KEY,
#                         EMAIL_USER, TO_EMAILS, RATE_PER_KWH)

#     st.markdown("#### 🔑 API Credentials")
#     for brand,ok,hint in [
#         ("Solis",   bool(SOLIS_API_KEY),
#          SOLIS_API_KEY[:10]+"…" if SOLIS_API_KEY else "Not configured"),
#         ("Growatt", bool(GROWATT_USERNAME),
#          GROWATT_USERNAME or "Set GROWATT_USERNAME in config.py"),
#         ("Sungrow", bool(SUNGROW_APP_KEY),
#          SUNGROW_APP_KEY[:10]+"…" if SUNGROW_APP_KEY else "Set SUNGROW_APP_KEY in config.py"),
#     ]:
#         c1,c2,c3 = st.columns([1,1,4])
#         c1.markdown(f"**{brand}**")
#         c2.markdown("✅ OK" if ok else "⚠️ Not set")
#         c3.markdown(f"`{hint}`")

#     st.divider()
#     st.markdown("#### 📧 Email Alerts")
#     st.markdown(f"**Sender:** `{EMAIL_USER}`")
#     st.markdown(f"**Recipients:** `{', '.join(TO_EMAILS)}`")
#     st.divider()
#     st.markdown("#### 💰 Tariff Rate")
#     st.info(f"Current rate: **₹{RATE_PER_KWH}/kWh** — edit `RATE_PER_KWH` in config.py")
#     st.divider()
#     st.markdown("#### 👤 Logged in as")
#     st.info(f"`{st.session_state.user}`")
#     st.divider()
#     st.markdown("#### 🗂 Project Structure")
#     st.code("""
# solar_dashboard/
# ├── app.py              ← streamlit run app.py
# ├── config.py           ← ✏️  credentials & settings
# ├── requirements.txt
# ├── data/solar_data.db  ← auto-created
# └── utils/
#     ├── solis_api.py    ├── growatt_api.py
#     ├── sungrow_api.py  ├── aggregator.py
#     ├── database.py     └── alerts.py
#     """, language="")

# ============================================================
#  app.py  —  Solar Dashboard  |  streamlit run app.py
# ============================================================
# import streamlit as st
# from streamlit_autorefresh import st_autorefresh
# import pandas as pd
# import plotly.express as px
# import plotly.graph_objects as go
# from datetime import datetime, date, timedelta

# from config import REFRESH_INTERVAL_SECONDS, RATE_PER_KWH
# from utils.database import init_db, get_history, get_alert_log
# from utils.aggregator import fetch_all_brands, check_alerts

# # ─────────────────────────────────────────────────────────────
# st.set_page_config(page_title="Solar Dashboard · Fractal Energy",
#                    page_icon="☀️", layout="wide",
#                    initial_sidebar_state="expanded")

# # ══════════════════════════════════════════════════════════════
# #  GLOBAL CSS  —  Navy · Teal · Amber theme
# # ══════════════════════════════════════════════════════════════
# st.markdown("""
# <style>
# @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

# *,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}

# :root{
#   /* ── Palette ── */
#   --navy:      #0a1628;
#   --navy2:     #0f2044;
#   --navy3:     #1a2f5a;
#   --teal:      #0d9488;
#   --teal-l:    #ccfbf1;
#   --teal-d:    #0f766e;
#   --amber:     #f59e0b;
#   --amber-l:   #fef3c7;
#   --amber-d:   #d97706;
#   --orange:    #f97316;
#   --orange-l:  #ffedd5;
#   --red:       #ef4444;
#   --red-l:     #fee2e2;
#   --green:     #10b981;
#   --green-l:   #d1fae5;
#   --sky:       #38bdf8;
#   --sky-l:     #e0f2fe;

#   /* ── Surfaces ── */
#   --bg:        #f0f4f8;
#   --card:      #ffffff;
#   --border:    #e2e8f0;
#   --border2:   #cbd5e1;

#   /* ── Text ── */
#   --text:      #0f172a;
#   --text2:     #475569;
#   --text3:     #94a3b8;

#   /* ── Shadows ── */
#   --shadow:    0 1px 4px rgba(10,22,40,.06),0 4px 20px rgba(10,22,40,.05);
#   --shadow-lg: 0 8px 40px rgba(10,22,40,.12);
#   --shadow-teal:0 4px 20px rgba(13,148,136,.25);
# }

# /* ── Fonts ── */
# html,body,[data-testid="stAppViewContainer"]{
#   background:var(--bg)!important;
#   font-family:'Plus Jakarta Sans',sans-serif!important;
#   color:var(--text);
# }
# [data-testid="stHeader"]{background:transparent!important;display:none;}
# #MainMenu,footer{visibility:hidden;}
# [data-testid="stDecoration"]{display:none;}
# .block-container{padding:28px 32px!important;max-width:100%!important;}

# /* ══ SIDEBAR ══════════════════════════════════════════════ */
# [data-testid="stSidebar"]{
#   background:var(--navy)!important;
#   border-right:1px solid rgba(255,255,255,.06)!important;
# }
# [data-testid="stSidebar"]>div{padding-top:0!important;}
# section[data-testid="stSidebarContent"]{padding:0!important;}

# .sb-logo{
#   padding:24px 20px 18px;
#   border-bottom:1px solid rgba(255,255,255,.07);
#   margin-bottom:6px;
#   display:flex;align-items:center;gap:12px;
# }
# .sb-logo-icon{
#   width:42px;height:42px;background:linear-gradient(135deg,var(--teal),var(--teal-d));
#   border-radius:12px;display:flex;align-items:center;justify-content:center;
#   font-size:20px;flex-shrink:0;box-shadow:var(--shadow-teal);
# }
# .sb-logo-title{color:#fff;font-weight:800;font-size:15px;letter-spacing:-.3px;}
# .sb-logo-sub{color:#64748b;font-size:11px;margin-top:1px;}
# .sb-section{
#   padding:14px 20px 4px;
#   font-size:10px;font-weight:700;color:#334155;
#   text-transform:uppercase;letter-spacing:.12em;
# }
# .sb-time{
#   padding:14px 20px;font-size:11px;color:#475569;
#   border-top:1px solid rgba(255,255,255,.06);margin-top:6px;
#   font-family:'JetBrains Mono',monospace;
# }

# /* ══ LOGIN PAGE ═══════════════════════════════════════════ */
# .login-wrap{
#   min-height:100vh;display:flex;align-items:center;justify-content:center;
#   background:linear-gradient(135deg,var(--navy) 0%,var(--navy2) 50%,#0d2b4e 100%);
#   padding:20px;
# }
# .login-card{
#   background:rgba(255,255,255,.04);
#   border:1px solid rgba(255,255,255,.1);
#   border-radius:20px;padding:48px 44px;width:100%;max-width:420px;
#   backdrop-filter:blur(20px);
#   box-shadow:0 20px 60px rgba(0,0,0,.4);
# }
# .login-logo{
#   width:60px;height:60px;
#   background:linear-gradient(135deg,var(--teal),var(--teal-d));
#   border-radius:16px;display:flex;align-items:center;justify-content:center;
#   font-size:28px;margin:0 auto 20px;
#   box-shadow:0 8px 24px rgba(13,148,136,.4);
# }
# .login-title{
#   font-size:24px;font-weight:800;color:#fff;text-align:center;
#   letter-spacing:-.4px;margin-bottom:6px;
# }
# .login-sub{font-size:13px;color:#64748b;text-align:center;margin-bottom:32px;}
# .login-label{font-size:13px;font-weight:600;color:#94a3b8;margin-bottom:6px;}
# .login-error{
#   background:rgba(239,68,68,.12);border:1px solid rgba(239,68,68,.3);
#   border-radius:8px;padding:10px 14px;font-size:13px;color:#fca5a5;
#   margin-bottom:16px;text-align:center;
# }

# /* ══ PAGE HEADER ══════════════════════════════════════════ */
# .page-hdr{margin-bottom:24px;}
# .page-hdr h1{
#   font-size:24px;font-weight:800;color:var(--text);
#   letter-spacing:-.5px;line-height:1.2;
# }
# .page-hdr p{font-size:13px;color:var(--text3);margin-top:4px;}

# /* ══ KPI CARDS ════════════════════════════════════════════ */
# .kpi-card{
#   background:var(--card);border-radius:16px;padding:24px 22px;
#   border:1px solid var(--border);box-shadow:var(--shadow);
#   display:flex;gap:16px;align-items:flex-start;
#   transition:transform .15s,box-shadow .15s;
#   position:relative;overflow:hidden;
# }
# .kpi-card::after{
#   content:'';position:absolute;top:0;left:0;right:0;height:3px;
#   background:linear-gradient(90deg,var(--teal),var(--sky));
#   border-radius:16px 16px 0 0;
# }
# .kpi-card.amber::after{background:linear-gradient(90deg,var(--amber),var(--orange));}
# .kpi-card.green::after{background:linear-gradient(90deg,var(--green),var(--teal));}
# .kpi-card.navy::after{background:linear-gradient(90deg,var(--navy3),var(--sky));}
# .kpi-card:hover{transform:translateY(-2px);box-shadow:var(--shadow-lg);}

# .kpi-icon{
#   width:50px;height:50px;border-radius:13px;flex-shrink:0;
#   display:flex;align-items:center;justify-content:center;font-size:22px;
# }
# .kpi-icon.teal  {background:var(--teal-l);color:var(--teal);}
# .kpi-icon.amber {background:var(--amber-l);color:var(--amber-d);}
# .kpi-icon.green {background:var(--green-l);color:var(--green);}
# .kpi-icon.navy  {background:var(--sky-l);color:#0284c7;}

# .kpi-label{
#   font-size:11px;color:var(--text3);font-weight:700;
#   text-transform:uppercase;letter-spacing:.1em;margin-bottom:6px;
# }
# .kpi-value{
#   font-size:28px;font-weight:800;color:var(--text);
#   line-height:1;letter-spacing:-.5px;
# }
# .kpi-unit{font-size:14px;font-weight:600;color:var(--text2);margin-left:3px;}
# .kpi-meta{font-size:12px;color:var(--text3);margin-top:8px;line-height:1.4;}
# .kpi-meta b{color:var(--teal);font-weight:600;}

# /* ══ SECTION HEADER ═══════════════════════════════════════ */
# .sec-hdr{
#   font-size:13px;font-weight:700;color:var(--text);
#   display:flex;align-items:center;gap:8px;
#   margin-bottom:14px;padding-bottom:10px;
#   border-bottom:2px solid var(--border);
# }
# .sec-hdr-dot{
#   width:8px;height:8px;border-radius:50%;
#   background:linear-gradient(135deg,var(--teal),var(--sky));
#   flex-shrink:0;
# }

# /* ══ CARD WRAPPER ═════════════════════════════════════════ */
# .card{
#   background:var(--card);border-radius:16px;padding:22px;
#   border:1px solid var(--border);box-shadow:var(--shadow);margin-bottom:16px;
# }

# /* ══ INVERTER CARD ════════════════════════════════════════ */
# .inv-card{
#   background:var(--card);border-radius:16px;padding:22px;
#   border:1px solid var(--border);box-shadow:var(--shadow);
#   margin-bottom:14px;transition:border-color .15s,box-shadow .15s;
# }
# .inv-card:hover{border-color:var(--primary);box-shadow:var(--shadow-teal);}
# .inv-card.alert-card{border-left:3px solid var(--red);}
# .inv-header{
#   display:flex;justify-content:space-between;align-items:flex-start;
#   margin-bottom:18px;padding-bottom:14px;
#   border-bottom:1px solid var(--border);
# }
# .inv-name{font-size:15px;font-weight:700;color:var(--text);letter-spacing:-.3px;}
# .inv-meta{font-size:11px;color:var(--text3);margin-top:3px;font-family:'JetBrains Mono',monospace;}
# .inv-params{display:grid;grid-template-columns:repeat(6,1fr);gap:16px;}
# .param-label{
#   font-size:10px;color:var(--text3);text-transform:uppercase;
#   letter-spacing:.08em;font-weight:600;margin-bottom:4px;
# }
# .param-val{font-size:18px;font-weight:700;color:var(--text);letter-spacing:-.3px;}
# .param-unit{font-size:11px;color:var(--text3);margin-left:2px;}
# .inv-footer{margin-top:14px;font-size:11px;color:var(--text3);font-family:'JetBrains Mono',monospace;}

# /* ══ TABLES ═══════════════════════════════════════════════ */
# .tbl{
#   background:var(--card);border-radius:16px;
#   border:1px solid var(--border);overflow:hidden;box-shadow:var(--shadow);
# }
# .tbl-hdr,.tbl-row{
#   display:grid;padding:0 20px;align-items:center;gap:10px;
# }
# .tbl-hdr{
#   background:linear-gradient(90deg,#f8fafc,#f1f5f9);
#   border-bottom:2px solid var(--border);
#   font-size:10px;font-weight:700;color:var(--text3);
#   text-transform:uppercase;letter-spacing:.1em;height:44px;
# }
# .tbl-row{
#   min-height:54px;border-bottom:1px solid var(--border);
#   font-size:13px;transition:background .1s;
# }
# .tbl-row:last-child{border-bottom:none;}
# .tbl-row:hover{background:#f8fafc;}
# .tbl-plant{grid-template-columns:2fr 1fr 1.1fr 1fr 1fr 1.1fr 1.3fr 1fr;}
# .tbl-alarm{grid-template-columns:1fr 1fr 1fr 1.5fr 1.4fr 2.2fr 1.2fr;}
# .cell-link{color:var(--primary);font-weight:700;cursor:pointer;font-size:13px;}

# /* ══ BADGES ═══════════════════════════════════════════════ */
# .badge{
#   display:inline-flex;align-items:center;gap:5px;
#   font-size:11px;font-weight:700;padding:4px 10px;
#   border-radius:20px;letter-spacing:.02em;
# }
# .badge::before{content:'';width:6px;height:6px;border-radius:50%;}
# .b-online {background:var(--green-l);color:#065f46;}
# .b-online::before{background:var(--green);}
# .b-offline{background:var(--red-l);color:#991b1b;}
# .b-offline::before{background:var(--red);}
# .b-warning{background:var(--amber-l);color:#92400e;}
# .b-warning::before{background:var(--amber);}
# .b-unknown{background:#f1f5f9;color:#64748b;}
# .b-unknown::before{background:#94a3b8;}
# .b-active {background:var(--red-l);color:#991b1b;}
# .b-active::before{background:var(--red);}
# .b-resolved{background:var(--green-l);color:#065f46;}
# .b-resolved::before{background:var(--green);}
# .b-critical{background:var(--red-l);color:#991b1b;font-weight:800;}
# .b-critical::before{background:var(--red);}

# /* ══ CHIPS ════════════════════════════════════════════════ */
# .chip{
#   display:inline-block;font-size:10px;font-weight:800;
#   padding:3px 9px;border-radius:6px;
#   letter-spacing:.1em;text-transform:uppercase;
# }
# .chip-solis  {background:#dbeafe;color:#1e40af;}
# .chip-growatt{background:#d1fae5;color:#065f46;}
# .chip-sungrow{background:#ffedd5;color:#c2410c;}

# /* ══ ALERT STRIP ══════════════════════════════════════════ */
# .alert-strip{
#   background:linear-gradient(135deg,#fff1f2,#ffe4e6);
#   border:1px solid #fecdd3;border-left:4px solid var(--red);
#   border-radius:12px;padding:16px 18px;margin-bottom:12px;
#   display:flex;gap:14px;align-items:flex-start;
# }
# .alert-strip-ico{font-size:20px;flex-shrink:0;}
# .alert-strip-ttl{font-size:14px;font-weight:700;color:var(--red);}
# .alert-strip-msg{font-size:12px;color:#7f1d1d;margin-top:3px;}

# /* ══ STAT ROW ═════════════════════════════════════════════ */
# .stat-row{
#   background:var(--card);border-radius:14px;padding:16px 24px;
#   border:1px solid var(--border);display:flex;gap:32px;
#   margin-bottom:20px;align-items:center;flex-wrap:wrap;
#   box-shadow:var(--shadow);
# }
# .stat-item{text-align:center;}
# .stat-val{font-size:20px;font-weight:800;color:var(--text);letter-spacing:-.3px;}
# .stat-lbl{font-size:10px;color:var(--text3);margin-top:2px;font-weight:600;text-transform:uppercase;letter-spacing:.08em;}

# /* ══ STREAMLIT OVERRIDES ══════════════════════════════════ */
# .stButton>button{
#   background:linear-gradient(135deg,var(--teal),var(--teal-d))!important;
#   color:#fff!important;border:none!important;border-radius:10px!important;
#   font-family:'Plus Jakarta Sans',sans-serif!important;
#   font-weight:700!important;font-size:13px!important;
#   padding:10px 24px!important;letter-spacing:.01em!important;
#   box-shadow:0 4px 12px rgba(13,148,136,.3)!important;
#   transition:all .15s!important;
# }
# .stButton>button:hover{transform:translateY(-1px)!important;box-shadow:0 6px 20px rgba(13,148,136,.4)!important;}
# div[data-testid="stSelectbox"]>label,
# div[data-testid="stTextInput"]>label{
#   font-size:12px!important;font-weight:700!important;
#   color:var(--text2)!important;text-transform:uppercase!important;letter-spacing:.06em!important;
# }
# [data-testid="stRadio"]>label{font-size:13px!important;font-weight:600!important;}
# .stRadio>div{gap:4px!important;}
# .stAlert{border-radius:12px!important;}
# div[data-testid="stTextInput"] input{
#   border-radius:10px!important;border-color:var(--border2)!important;
#   font-size:14px!important;font-family:'Plus Jakarta Sans',sans-serif!important;
# }
# div[data-testid="stSelectbox"]>div>div{
#   border-radius:10px!important;border-color:var(--border2)!important;
#   font-size:13px!important;
# }

# /* ══ LOGIN STREAMLIT INPUT OVERRIDES ═══════════════════════ */
# .login-page [data-testid="stTextInput"] input{
#   background:rgba(255,255,255,.08)!important;
#   border:1px solid rgba(255,255,255,.15)!important;
#   border-radius:10px!important;color:#fff!important;
#   font-size:14px!important;padding:12px 14px!important;
# }
# .login-page .stButton>button{
#   width:100%!important;padding:14px!important;font-size:15px!important;
# }

# /* ══ DIVIDER ══════════════════════════════════════════════ */
# .divider{height:1px;background:var(--border);margin:20px 0;}

# /* ══ METRIC OVERRIDES ═════════════════════════════════════ */
# [data-testid="stMetric"]{
#   background:var(--card);border-radius:12px;padding:16px 18px;
#   border:1px solid var(--border);box-shadow:var(--shadow);
# }
# [data-testid="stMetricLabel"]{font-size:11px!important;font-weight:700!important;color:var(--text3)!important;text-transform:uppercase!important;letter-spacing:.08em!important;}
# [data-testid="stMetricValue"]{font-size:24px!important;font-weight:800!important;color:var(--text)!important;letter-spacing:-.4px!important;}
# </style>
# """, unsafe_allow_html=True)

# # ══════════════════════════════════════════════════════════════
# #  INIT
# # ══════════════════════════════════════════════════════════════
# init_db()

# # ══════════════════════════════════════════════════════════════
# #  LOGIN
# # ══════════════════════════════════════════════════════════════
# USERS = {
#     "admin": "1234"
# }

# if "logged_in" not in st.session_state:
#     st.session_state.logged_in = False
#     st.session_state.user = ""

# if not st.session_state.logged_in:
#     # Full-screen dark login — hide sidebar
#     st.markdown("""
#     <style>
#     [data-testid="stSidebar"]{display:none!important;}
#     .block-container{padding:0!important;max-width:100%!important;}
#     </style>""", unsafe_allow_html=True)

#     st.markdown("""
#     <div style="min-height:100vh;display:flex;align-items:center;justify-content:center;
#     background:linear-gradient(135deg,#0a1628 0%,#0f2044 55%,#0d2b4e 100%);padding:20px;">
#       <div style="width:100%;max-width:420px;">
#         <div style="text-align:center;margin-bottom:32px;">
#           <div style="width:68px;height:68px;background:linear-gradient(135deg,#0d9488,#0f766e);
#             border-radius:18px;display:flex;align-items:center;justify-content:center;
#             font-size:32px;margin:0 auto 16px;box-shadow:0 8px 24px rgba(13,148,136,.4);">☀️</div>
#           <div style="font-size:26px;font-weight:800;color:#fff;letter-spacing:-.5px;">Solar Dashboard</div>
#           <div style="font-size:13px;color:#64748b;margin-top:6px;">Fractal Energy · Monitoring Platform</div>
#         </div>
#         <div style="background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.1);
#           border-radius:20px;padding:36px 32px;backdrop-filter:blur(20px);
#           box-shadow:0 20px 60px rgba(0,0,0,.4);">
#     """, unsafe_allow_html=True)

#     email    = st.text_input("Email Address",    placeholder="your@email.com")
#     password = st.text_input("Password",         placeholder="••••••••", type="password")

#     if st.button("Sign In →", use_container_width=True):
#         if email in USERS and USERS[email] == password:
#             st.session_state.logged_in = True
#             st.session_state.user = email
#             st.rerun()
#         else:
#             st.error("Invalid email or password. Please try again.")

#     st.markdown("""
#         <div style="text-align:center;margin-top:20px;font-size:12px;color:#475569;">
#           Secured by Fractal Energy · v2.0
#         </div>
#         </div></div></div>
#     """, unsafe_allow_html=True)
#     st.stop()

# # ══════════════════════════════════════════════════════════════
# #  AUTHENTICATED APP
# # ══════════════════════════════════════════════════════════════
# st_autorefresh(interval=REFRESH_INTERVAL_SECONDS * 1000, key="solar_ar")

# # ── Helpers ──────────────────────────────────────────────────
# def f(v, d=1, na="—"):
#     try:    return f"{float(v):.{d}f}"
#     except: return na

# def badge(s, kind=None):
#     s  = (s or "").strip()
#     sl = s.lower()
#     if kind == "level":
#         cls = "b-critical" if sl == "critical" else "b-warning"
#     elif kind == "status_alarm":
#         cls = "b-active" if sl == "active" else "b-resolved"
#     else:
#         if sl == "online":              cls = "b-online"
#         elif sl in ("offline","fault"): cls = "b-offline"
#         else:                           cls = "b-unknown"
#     return f'<span class="badge {cls}">{s}</span>'

# def chip(b):
#     return f'<span class="chip chip-{(b or "").lower()}">{b}</span>'

# def earn(kwh):
#     v = float(kwh or 0) * RATE_PER_KWH
#     if v >= 1_000_000: return f"₹{v/1_000_000:.3f}M"
#     if v >= 1_000:     return f"₹{v/1_000:.3f}K"
#     return f"₹{v:.2f}"

# def chart_style(fig, h=300):
#     fig.update_layout(
#         plot_bgcolor="#fff", paper_bgcolor="#fff",
#         font_color="#64748b", font_family="Inter",
#         margin=dict(l=0,r=0,t=16,b=0), height=h,
#         legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=12, color="#64748b")),
#         bargap=0.28,
#     )
#     fig.update_traces(marker_line_width=0)
#     fig.update_xaxes(showgrid=False, zeroline=False, tickfont_size=11,
#                      tickfont_color="#94a3b8", linecolor="#e2e8f0")
#     fig.update_yaxes(showgrid=True, gridcolor="#f1f5f9", zeroline=False,
#                      tickfont_size=11, tickfont_color="#94a3b8")
#     return fig

# PALETTE = ["#0d9488","#f59e0b","#3b82f6","#f97316","#10b981","#8b5cf6","#06b6d4","#ec4899"]
# BRAND_COLORS = {"Solis":"#3b82f6","Growatt":"#10b981","Sungrow":"#f97316"}

# def sec(title, icon=""):
#     st.markdown(f'<div class="sec-hdr"><div class="sec-hdr-dot"></div>{icon} {title}</div>',
#                 unsafe_allow_html=True)

# # ── Sidebar ──────────────────────────────────────────────────
# with st.sidebar:
#     st.markdown(f"""
#     <div class="sb-logo">
#       <div class="sb-logo-icon">☀</div>
#       <div>
#         <div class="sb-logo-title">Solar Dashboard</div>
#         <div class="sb-logo-sub">Fractal Energy</div>
#       </div>
#     </div>""", unsafe_allow_html=True)

#     page = st.radio("", ["📊  Overview","🔧  O&M","📈  Report","🗺  Service","⚙️  Settings"],
#                     label_visibility="collapsed")
#     page = page.split("  ",1)[1].strip()

#     st.markdown('<div class="sb-section">Data Sources</div>', unsafe_allow_html=True)
#     sel_brands = [b for b in ["Solis","Growatt","Sungrow"]
#                   if st.checkbox(b, value=(b=="Solis"), key=f"cb_{b}")]

#     st.markdown('<div style="height:6px"></div>', unsafe_allow_html=True)
#     if st.button("🔄  Refresh Now"):
#         st.cache_data.clear(); st.rerun()

#     show_debug = st.checkbox("🔍  Debug", value=False)

#     # Logout
#     st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)
#     if st.button("🚪  Sign Out"):
#         st.session_state.logged_in = False
#         st.rerun()

#     st.markdown(f"""
#     <div class="sb-time">
#       ⏱ {datetime.now().strftime('%d %b %Y')}<br>
#       <b style="color:#94a3b8;">{datetime.now().strftime('%H:%M:%S')}</b><br>
#       <span style="color:#334155;">Auto-refresh {REFRESH_INTERVAL_SECONDS//60} min</span>
#     </div>""", unsafe_allow_html=True)

# # ── Fetch data ────────────────────────────────────────────────
# @st.cache_data(ttl=REFRESH_INTERVAL_SECONDS)
# def load(brands):
#     result = fetch_all_brands(list(brands))
#     if not result:
#         raise RuntimeError("empty")   # prevent caching empty result
#     return result

# with st.spinner("Fetching live data…"):
#     try:
#         records = load(tuple(sel_brands))
#     except Exception:
#         # Cache returned empty or errored — fetch fresh without cache
#         records = fetch_all_brands(list(sel_brands))
#         if not records:
#             st.cache_data.clear()     # clear so next refresh retries

# alerts = check_alerts(records, st.session_state)

# df = pd.DataFrame()
# if records:
#     df = pd.DataFrame(records)
#     for c in ["power_kw","today_kwh","total_kwh","temperature","voltage","current_a"]:
#         if c in df.columns:
#             df[c] = pd.to_numeric(df[c], errors="coerce")
#     if "status" in df.columns:
#         df["status"] = df["status"].astype(str).str.strip()

# # ── Debug ─────────────────────────────────────────────────────
# if show_debug and not df.empty:
#     st.markdown("### 🔍 Debug: Raw API Data")
#     st.dataframe(df, use_container_width=True)
#     try:
#         from utils.solis_api import fetch_summary as _fsum, _raw_plants_cache
#         summ = _fsum()
#         st.write("**fetch_summary():**", summ)
#     except Exception as ex:
#         st.error(f"Debug error: {ex}")
#     st.divider()


# # ══════════════════════════════════════════════════════════════
# #  OVERVIEW
# # ══════════════════════════════════════════════════════════════
# if page == "Overview":
#     st.markdown('<div class="page-hdr"><h1>Plant Overview</h1>'
#                 '<p>Real-time performance across all plants</p></div>',
#                 unsafe_allow_html=True)

#     if df.empty:
#         st.warning("⚠️ No data. Check credentials in config.py and click Refresh.")
#         st.stop()

#     # ── KPI values ────────────────────────────────────────────
#     total_power = float(df["power_kw"].sum())
#     daily_kwh   = float(df["today_kwh"].sum())
#     total_mwh   = float(df["total_kwh"].sum())
#     monthly_mwh = 0.0

#     try:
#         if "Solis" in sel_brands:
#             from utils.solis_api import fetch_summary as _fs
#             summ = _fs()
#             if summ.get("power_kw",    0) > 0: total_power = float(summ["power_kw"])
#             # daily_kwh: use df sum (inverterList etoday) — most accurate per-inverter value
#             # fetch_summary dayEnergy can be partial; df["today_kwh"].sum() is always correct
#             if summ.get("monthly_mwh", 0) > 0: monthly_mwh = float(summ["monthly_mwh"])
#             if summ.get("total_mwh",   0) > 0: total_mwh   = float(summ["total_mwh"])
#     except Exception: pass

#     # Always use inverter-level sum for daily yield — it's the most accurate
#     # (confirmed: df sum = 1697.5 kWh matches Solis, API dayEnergy can lag)
#     daily_kwh = float(df["today_kwh"].sum())

#     if monthly_mwh == 0:
#         hist = get_history(hours=720)
#         monthly_kwh_db = daily_kwh
#         if not hist.empty and "today_kwh" in hist.columns:
#             hist["fetched_at"] = pd.to_datetime(hist["fetched_at"])
#             hist["today_kwh"]  = pd.to_numeric(hist["today_kwh"], errors="coerce")
#             m = hist[hist["fetched_at"].dt.month == datetime.now().month]
#             if not m.empty:
#                 v = float(m.groupby([m["fetched_at"].dt.date,"inverter_sn"])["today_kwh"].max().sum())
#                 monthly_kwh_db = max(v, daily_kwh)
#         monthly_mwh = monthly_kwh_db / 1000
#     monthly_kwh = monthly_mwh * 1000

#     # Display units
#     daily_val,daily_unit = (f(daily_kwh/1000,3),"MWh") if daily_kwh>=1000 else (f(daily_kwh,1),"kWh")
#     mo_val,mo_unit       = f(monthly_mwh,3), "MWh"
#     if total_mwh >= 1000:
#         tot_val,tot_unit,tot_earn = f(total_mwh/1000,3),"GWh",total_mwh*1000
#     else:
#         tot_val,tot_unit,tot_earn = f(total_mwh,3),"MWh",total_mwh*1000

#     n_on  = int((df["status"].str.lower()=="online").sum())
#     n_tot = len(df)

#     # ── 4 KPI cards ──────────────────────────────────────────
#     c1,c2,c3,c4 = st.columns(4)
#     kpis = [
#         (c1,"teal","teal","⚡","Power",f(total_power,2),"kW",
#          f"Inverters: <b>{n_on}/{n_tot} online</b>"),
#         (c2,"amber","amber","🔋","Daily Yield",daily_val,daily_unit,
#          f"Earning today: <b>{earn(daily_kwh)}</b>"),
#         (c3,"green","green","📅","Monthly Yield",mo_val,mo_unit,
#          f"Earning this month: <b>{earn(monthly_kwh)}</b>"),
#         (c4,"navy","navy","📊","Total Yield",tot_val,tot_unit,
#          f"Total earning: <b>{earn(tot_earn)}</b>"),
#     ]
#     for col,card_cls,ico_cls,ico,lbl,val,unit,meta in kpis:
#         with col:
#             st.markdown(f"""
#             <div class="kpi-card {card_cls}">
#               <div class="kpi-icon {ico_cls}">{ico}</div>
#               <div>
#                 <div class="kpi-label">{lbl}</div>
#                 <div class="kpi-value">{val}<span class="kpi-unit"> {unit}</span></div>
#                 <div class="kpi-meta">{meta}</div>
#               </div>
#             </div>""", unsafe_allow_html=True)

#     st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)

#     # ── Alert strips ─────────────────────────────────────────
#     if alerts:
#         for a in alerts[:3]:
#             st.markdown(f"""
#             <div class="alert-strip">
#               <div class="alert-strip-ico">🚨</div>
#               <div>
#                 <div class="alert-strip-ttl">{a['plant_name']} — {a.get('inverter_sn','')}</div>
#                 <div class="alert-strip-msg">{a['issue']}</div>
#               </div>
#             </div>""", unsafe_allow_html=True)

#     # ── Charts ───────────────────────────────────────────────
#     ch1, ch2 = st.columns([3, 2])

#     with ch1:
#         sec("Power by Plant (kW)")
#         pdf = df.groupby(["plant_name","brand"])["power_kw"].sum().reset_index()
#         fig = px.bar(pdf, x="plant_name", y="power_kw", color="brand",
#                      color_discrete_map=BRAND_COLORS,
#                      labels={"power_kw":"Power (kW)","plant_name":"","brand":"Brand"})
#         fig.update_traces(marker_cornerradius=4)
#         st.plotly_chart(chart_style(fig, 290), use_container_width=True)

#     with ch2:
#         sec("Daily Yield Share")
#         pief = df.groupby("plant_name")["today_kwh"].sum().reset_index()
#         fig2 = go.Figure(go.Pie(
#             labels=pief["plant_name"],
#             values=pief["today_kwh"],
#             hole=0.52,
#             marker=dict(colors=PALETTE, line=dict(color="#fff", width=2)),
#             textposition="outside",
#             textinfo="label+percent",
#             textfont=dict(size=11, family="Plus Jakarta Sans"),
#             pull=[0.04]*len(pief),
#         ))
#         fig2.update_layout(
#             plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
#             font_family="Inter", font_color="#64748b",
#             margin=dict(l=60, r=60, t=20, b=20), height=290,
#             showlegend=False,
#             annotations=[dict(text=f"<b>{f(pief['today_kwh'].sum(),1)}</b><br>kWh",
#                               font=dict(size=14,color="#0f172a",family="Plus Jakarta Sans"),
#                               showarrow=False)]
#         )
#         st.plotly_chart(fig2, use_container_width=True)

#     # ── Plant table ──────────────────────────────────────────
#     sec("Plant List")
#     ps = (df.groupby(["plant_name","brand"])
#           .agg(power_kw=("power_kw","sum"), today_kwh=("today_kwh","sum"),
#                total_kwh=("total_kwh","sum"), inv_count=("inverter_sn","count"))
#           .reset_index())

#     st.markdown('<div class="tbl">', unsafe_allow_html=True)
#     st.markdown(
#         '<div class="tbl-hdr tbl-plant">'
#         '<div>Plant Name</div><div>Brand</div><div>Inverters</div>'
#         '<div>Power (kW)</div><div>Daily Yield</div>'
#         '<div>Total Yield</div><div>Earning Today</div><div>Status</div>'
#         '</div>', unsafe_allow_html=True)

#     for _, row in ps.iterrows():
#         pr   = df[df["plant_name"]==row["plant_name"]]
#         on   = int((pr["status"].str.lower()=="online").sum())
#         tot  = int(row["inv_count"])
#         pst  = "Online" if on==tot and tot>0 else ("Offline" if on==0 else "Warning")
#         dy   = float(row["today_kwh"] or 0)
#         dy_s = f"{dy/1000:.3f} MWh" if dy>=1000 else f"{dy:.1f} kWh"
#         ty   = float(row["total_kwh"] or 0)
#         ty_s = f"{ty/1000:.3f} GWh" if ty>=1000 else f"{ty:.3f} MWh"
#         st.markdown(
#             f'<div class="tbl-row tbl-plant">'
#               f'<div class="cell-link">{row["plant_name"]}</div>'
#               f'<div>{chip(row["brand"])}</div>'
#               f'<div>{on}/{tot}</div>'
#               f'<div><b>{f(row["power_kw"],2)}</b> kW</div>'
#               f'<div>{dy_s}</div><div>{ty_s}</div>'
#               f'<div>{earn(dy)}</div><div>{badge(pst)}</div>'
#             f'</div>', unsafe_allow_html=True)
#     st.markdown('</div>', unsafe_allow_html=True)


# # ══════════════════════════════════════════════════════════════
# #  O&M
# # ══════════════════════════════════════════════════════════════
# elif page == "O&M":
#     sub = st.radio("", ["🔔  Alarm Information","⚡  Device Overview"],
#                    horizontal=True, label_visibility="collapsed")
#     sub = sub.split("  ",1)[1].strip()
#     st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

#     alarm_log = get_alert_log(200)
#     all_alarms = []
#     for a in alerts:
#         all_alarms.append({"device_type":"Inverter","level":"Critical","status":"Active",
#             "plant_name":a.get("plant_name","—"),"sn":a.get("inverter_sn","—"),
#             "content":a.get("issue","—"),"brand":a.get("brand","—"),
#             "time":datetime.now().strftime("%Y-%m-%d %H:%M")})
#     if not alarm_log.empty:
#         for _, r in alarm_log.iterrows():
#             all_alarms.append({"device_type":"Inverter","level":"Warning","status":"Resolved",
#                 "plant_name":r.get("plant_name","—"),"sn":r.get("inverter_sn","—"),
#                 "content":r.get("issue","—"),"brand":r.get("brand","—"),
#                 "time":r.get("alerted_at","—")})

#     if sub == "Alarm Information":
#         st.markdown('<div class="page-hdr"><h1>Alarm Information</h1>'
#                     '<p>Fault detection and alert history</p></div>',
#                     unsafe_allow_html=True)

#         plant_opts = ["All"] + sorted(df["plant_name"].dropna().unique()) if not df.empty else ["All"]
#         sn_opts    = ["All"] + sorted(df["inverter_sn"].dropna().unique()) if not df.empty else ["All"]
#         brand_opts = ["All"] + sorted(df["brand"].dropna().unique())       if not df.empty else ["All"]

#         fc1,fc2,fc3,fc4,fc5 = st.columns(5)
#         with fc1: fp = st.selectbox("Plant Name",  plant_opts)
#         with fc2: fs = st.selectbox("S/N",         sn_opts)
#         with fc3: fb = st.selectbox("Brand",        brand_opts)
#         with fc4: fst= st.selectbox("Status",       ["All","Active","Resolved"])
#         with fc5: fl = st.selectbox("Level",        ["All","Critical","Warning"])

#         filt = all_alarms[:]
#         if fp !="All": filt=[a for a in filt if a["plant_name"]==fp]
#         if fs !="All": filt=[a for a in filt if a["sn"]        ==fs]
#         if fb !="All": filt=[a for a in filt if a["brand"]     ==fb]
#         if fst!="All": filt=[a for a in filt if a["status"]    ==fst]
#         if fl !="All": filt=[a for a in filt if a["level"]     ==fl]

#         m1,m2,m3 = st.columns(3)
#         m1.metric("Total", len(filt))
#         m2.metric("Active",   sum(1 for a in filt if a["status"]=="Active"))
#         m3.metric("Resolved", sum(1 for a in filt if a["status"]=="Resolved"))

#         if not filt:
#             st.success("✅ No alarms — all systems operating normally.")
#         else:
#             st.markdown('<div class="tbl">', unsafe_allow_html=True)
#             st.markdown('<div class="tbl-hdr tbl-alarm">'
#                         '<div>Device</div><div>Level</div><div>Status</div>'
#                         '<div>Plant</div><div>S/N</div><div>Issue</div><div>Time</div>'
#                         '</div>', unsafe_allow_html=True)
#             for a in filt:
#                 st.markdown(
#                     f'<div class="tbl-row tbl-alarm">'
#                       f'<div>{a["device_type"]}</div>'
#                       f'<div>{badge(a["level"],"level")}</div>'
#                       f'<div>{badge(a["status"],"status_alarm")}</div>'
#                       f'<div>{chip(a["brand"])} {a["plant_name"]}</div>'
#                       f'<div style="font-size:11px;color:var(--text3);font-family:\'JetBrains Mono\',monospace;">{a["sn"]}</div>'
#                       f'<div>{a["content"]}</div>'
#                       f'<div style="font-size:11px;color:var(--text3);">{a["time"]}</div>'
#                     f'</div>', unsafe_allow_html=True)
#             st.markdown('</div>', unsafe_allow_html=True)

#     else:
#         st.markdown('<div class="page-hdr"><h1>Device Overview</h1>'
#                     '<p>Live readings for every inverter</p></div>',
#                     unsafe_allow_html=True)
#         if df.empty:
#             st.warning("⚠️ No data."); st.stop()

#         fc1,fc2,fc3,fc4 = st.columns(4)
#         with fc1: bf = st.selectbox("Brand",  ["All"]+sorted(df["brand"].dropna().unique()),       key="do_b")
#         with fc2: pf = st.selectbox("Plant",  ["All"]+sorted(df["plant_name"].dropna().unique()),  key="do_p")
#         with fc3: sf = st.selectbox("S/N",    ["All"]+sorted(df["inverter_sn"].dropna().unique()), key="do_s")
#         with fc4: stf= st.selectbox("Status", ["All"]+sorted(df["status"].dropna().unique()),      key="do_st")

#         vw = df.copy()
#         if bf !="All": vw=vw[vw["brand"]       ==bf]
#         if pf !="All": vw=vw[vw["plant_name"]  ==pf]
#         if sf !="All": vw=vw[vw["inverter_sn"] ==sf]
#         if stf!="All": vw=vw[vw["status"]      ==stf]

#         st.markdown(
#             f'<div class="stat-row">'
#               f'<div class="stat-item"><div class="stat-val">{len(vw)}</div><div class="stat-lbl">Inverters</div></div>'
#               f'<div class="stat-item"><div class="stat-val">{f(vw["power_kw"].sum(),2)} kW</div><div class="stat-lbl">Total Power</div></div>'
#               f'<div class="stat-item"><div class="stat-val">{f(vw["today_kwh"].sum(),1)} kWh</div><div class="stat-lbl">Daily Yield</div></div>'
#               f'<div class="stat-item"><div class="stat-val">{int((vw["status"].str.lower()=="online").sum())}</div><div class="stat-lbl">Online</div></div>'
#             f'</div>', unsafe_allow_html=True)

#         alert_sns = {a.get("inverter_sn") for a in alerts}
#         for _, row in vw.iterrows():
#             sn    = str(row.get("inverter_sn","N/A"))
#             brand = str(row.get("brand",""))
#             st_   = str(row.get("status",""))
#             params = [
#                 ("Power Now",   f(row.get("power_kw"),2),  "kW"),
#                 ("Daily Yield", f(row.get("today_kwh"),1), "kWh"),
#                 ("Total Yield", f(row.get("total_kwh"),3), "MWh"),
#                 ("Temperature", f(row.get("temperature"),1),"°C"),
#                 ("AC Voltage",  f(row.get("voltage"),1),   "V"),
#                 ("AC Current",  f(row.get("current_a"),1), "A"),
#             ]
#             p_html = "".join(
#                 f'<div><div class="param-label">{l}</div>'
#                 f'<div class="param-val">{v}<span class="param-unit"> {u}</span></div></div>'
#                 for l,v,u in params)
#             border = "border-left:3px solid var(--red);" if sn in alert_sns else ""
#             st.markdown(
#                 f'<div class="inv-card" style="{border}">'
#                   f'<div class="inv-header">'
#                     f'<div><div class="inv-name">{row.get("plant_name","")}</div>'
#                     f'<div class="inv-meta">S/N: {sn} · {chip(brand)} · {row.get("last_update","—")}</div></div>'
#                     + badge(st_) +
#                   f'</div>'
#                   f'<div class="inv-params">{p_html}</div>'
#                 f'</div>', unsafe_allow_html=True)


# # ══════════════════════════════════════════════════════════════
# #  REPORT  — pulls historical data from Solis API directly
# # ══════════════════════════════════════════════════════════════
# elif page == "Report":
#     st.markdown('<div class="page-hdr"><h1>Plant Report</h1>'
#                 '<p>Historical generation data from Solis Cloud</p></div>',
#                 unsafe_allow_html=True)

#     rtype = st.radio("", ["Daily","Monthly","Annual","Total"],
#                      horizontal=True, label_visibility="collapsed")
#     st.markdown('<div style="height:10px"></div>', unsafe_allow_html=True)

#     # Plant selector — always from live df
#     plant_opts = (["All Plants"] + sorted(df["plant_name"].dropna().unique().tolist())
#                   if not df.empty else ["No data"])

#     fc1, fc2 = st.columns([2, 1])
#     with fc1: sel_plant = st.selectbox("Select Plant", plant_opts)
#     with fc2: sel_date  = st.date_input("Date", value=date.today())

#     # Shared line chart helper
#     def line_chart(fig, h=360):
#         fig = chart_style(fig, h)
#         fig.update_traces(selector=dict(type="scatter"), line=dict(width=2.5))
#         fig.update_layout(hovermode="x unified")
#         return fig

#     # Get plant IDs for selected plant
#     from utils.solis_api import (get_plants as _get_plants,
#                                   get_all_plants_daily, get_all_plants_monthly,
#                                   get_plant_daily_history, get_plant_monthly_history)

#     @st.cache_data(ttl=300)
#     def _plants_cached():
#         return _get_plants()

#     all_solis_plants = _plants_cached()
#     plant_id_map = {p.get("stationName"): p.get("id") for p in all_solis_plants}

#     # ── DAILY ────────────────────────────────────────────────
#     if rtype == "Daily":
#         # Daily uses local DB (power readings every 5 min) — Solis API
#         # doesn't have per-minute history, only daily totals
#         hist_df = get_history(hours=8760)

#         if hist_df.empty:
#             st.info("📭 No intraday data yet — app collects readings every 5 min. Check back later.")
#         else:
#             hist_df["fetched_at"] = pd.to_datetime(hist_df["fetched_at"])
#             hist_df["power_kw"]   = pd.to_numeric(hist_df["power_kw"],  errors="coerce")
#             hist_df["today_kwh"]  = pd.to_numeric(hist_df["today_kwh"], errors="coerce")
#             if sel_plant != "All Plants":
#                 hist_df = hist_df[hist_df["plant_name"] == sel_plant]

#             day = hist_df[hist_df["fetched_at"].dt.date == sel_date].sort_values("fetched_at")
#             if day.empty:
#                 st.info(f"No intraday data for {sel_date}. Try today's date or a recent date.")
#             else:
#                 sec("Power Output Throughout the Day (kW)")
#                 fig = px.line(day, x="fetched_at", y="power_kw", color="inverter_sn",
#                               color_discrete_sequence=PALETTE,
#                               labels={"fetched_at":"Time","power_kw":"Power (kW)",
#                                       "inverter_sn":"Inverter"})
#                 st.plotly_chart(line_chart(fig, 360), use_container_width=True)

#                 sec("Peak Power & Daily Generation per Inverter")
#                 sm = (day.groupby(["plant_name","inverter_sn","brand"])
#                       .agg(Peak_kW=("power_kw","max"), Daily_kWh=("today_kwh","max"))
#                       .reset_index()
#                       .rename(columns={"plant_name":"Plant","inverter_sn":"S/N","brand":"Brand"}))
#                 st.dataframe(sm, use_container_width=True, hide_index=True)

#     # ── MONTHLY ───────────────────────────────────────────────
#     elif rtype == "Monthly":
#         month_str = sel_date.strftime("%Y-%m")

#         with st.spinner(f"Fetching daily data for {sel_date.strftime('%B %Y')} from Solis…"):
#             if sel_plant == "All Plants":
#                 api_df = get_all_plants_daily(month_str)
#                 if not api_df.empty:
#                     daily = (api_df.groupby("date")["energy_kwh"]
#                              .sum().reset_index())
#                     daily.columns = ["Date","Daily Yield (kWh)"]
#                     income_df = api_df.groupby("date")["income"].sum().reset_index()
#                     income_df.columns = ["Date","Income (INR)"]
#                     daily = daily.merge(income_df, on="Date", how="left")
#                 else:
#                     daily = pd.DataFrame()
#             else:
#                 pid = plant_id_map.get(sel_plant)
#                 if pid:
#                     rows = get_plant_daily_history(pid, month_str)
#                     daily = pd.DataFrame(rows).rename(columns={"date":"Date","energy_kwh":"Daily Yield (kWh)","income":"Income (INR)"}) if rows else pd.DataFrame()
#                     if not daily.empty:
#                         daily["Date"] = pd.to_datetime(daily["Date"], errors="coerce")
#                 else:
#                     daily = pd.DataFrame()

#         if daily.empty or "Daily Yield (kWh)" not in daily.columns:
#             st.info(f"No data from Solis API for {sel_date.strftime('%B %Y')}.")
#         else:
#             daily = daily.dropna(subset=["Date"]).sort_values("Date")

#             # Combined bar + line chart matching Solis style
#             sec(f"Daily Generation — {sel_date.strftime('%B %Y')}")
#             fig = go.Figure()
#             # Bar: yield
#             fig.add_trace(go.Bar(
#                 x=daily["Date"], y=daily["Daily Yield (kWh)"],
#                 name="Yield (kWh)", marker_color="rgba(13,148,136,.25)",
#                 marker_line_width=0,
#             ))
#             # Line: yield trend
#             fig.add_trace(go.Scatter(
#                 x=daily["Date"], y=daily["Daily Yield (kWh)"],
#                 name="Yield", mode="lines+markers",
#                 line=dict(color="#0d9488", width=2.5),
#                 marker=dict(size=5, color="#0d9488"),
#             ))
#             # Line: revenue (right axis)
#             if "Income (INR)" in daily.columns:
#                 fig.add_trace(go.Scatter(
#                     x=daily["Date"], y=daily["Income (INR)"],
#                     name="Revenue (INR)", mode="lines+markers",
#                     line=dict(color="#f59e0b", width=2, dash="dot"),
#                     marker=dict(size=5, color="#f59e0b"),
#                     yaxis="y2",
#                 ))
#             fig.update_layout(
#                 plot_bgcolor="#fff", paper_bgcolor="#fff",
#                 font_family="Inter", font_color="#64748b",
#                 margin=dict(l=0,r=60,t=16,b=0), height=380,
#                 hovermode="x unified", bargap=0.25,
#                 legend=dict(bgcolor="rgba(0,0,0,0)", orientation="h",
#                             yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
#                 yaxis=dict(title="kWh", showgrid=True, gridcolor="#f1f5f9",
#                            zeroline=False, tickfont_size=11),
#                 yaxis2=dict(title="INR", overlaying="y", side="right",
#                             showgrid=False, zeroline=False, tickfont_size=11),
#             )
#             fig.update_xaxes(showgrid=False, zeroline=False, tickfont_size=11,
#                              tickformat="%d", dtick="D1")
#             st.plotly_chart(fig, use_container_width=True)

#             tot = daily["Daily Yield (kWh)"].sum()
#             m1,m2,m3 = st.columns(3)
#             m1.metric("Month Total", f"{tot:.1f} kWh")
#             m2.metric("Month Total (MWh)", f"{tot/1000:.3f} MWh")
#             m3.metric("Estimated Earning", earn(tot))

#     # ── ANNUAL ────────────────────────────────────────────────
#     elif rtype == "Annual":
#         year_str = str(sel_date.year)

#         with st.spinner(f"Fetching monthly data for {year_str} from Solis…"):
#             if sel_plant == "All Plants":
#                 api_df = get_all_plants_monthly(year_str)
#                 if not api_df.empty:
#                     monthly = (api_df.groupby("month")["energy_kwh"]
#                                .sum().reset_index())
#                     monthly.columns = ["Month","kWh"]
#                 else:
#                     monthly = pd.DataFrame()
#             else:
#                 pid = plant_id_map.get(sel_plant)
#                 if pid:
#                     rows = get_plant_monthly_history(pid, year_str)
#                     monthly = pd.DataFrame(rows).rename(columns={"month":"Month","energy_kwh":"kWh"}) if rows else pd.DataFrame()
#                 else:
#                     monthly = pd.DataFrame()

#         if monthly.empty or "kWh" not in monthly.columns:
#             st.info(f"No data from Solis API for {year_str}.")
#         else:
#             monthly = monthly[monthly["kWh"] > 0]

#             sec(f"Monthly Generation — {year_str}")
#             fig = go.Figure()
#             fig.add_trace(go.Bar(
#                 x=monthly["Month"], y=monthly["kWh"],
#                 name="Yield (kWh)", marker_color="rgba(245,158,11,.3)",
#                 marker_line_width=0,
#             ))
#             fig.add_trace(go.Scatter(
#                 x=monthly["Month"], y=monthly["kWh"],
#                 name="Trend", mode="lines+markers",
#                 line=dict(color="#f59e0b", width=2.5),
#                 marker=dict(size=7, color="#f59e0b"),
#             ))
#             fig.update_layout(
#                 plot_bgcolor="#fff", paper_bgcolor="#fff",
#                 font_family="Inter", font_color="#64748b",
#                 margin=dict(l=0,r=0,t=16,b=0), height=360,
#                 hovermode="x unified", bargap=0.3,
#                 legend=dict(bgcolor="rgba(0,0,0,0)"),
#                 yaxis=dict(showgrid=True, gridcolor="#f1f5f9",
#                            zeroline=False, tickfont_size=11),
#             )
#             fig.update_xaxes(showgrid=False, zeroline=False, tickfont_size=11)
#             st.plotly_chart(fig, use_container_width=True)

#             tot_yr = monthly["kWh"].sum()
#             m1,m2,m3 = st.columns(3)
#             m1.metric("Year Total", f"{tot_yr:.1f} kWh")
#             m2.metric("Year Total (MWh)", f"{tot_yr/1000:.3f} MWh")
#             m3.metric("Est. Annual Earning", earn(tot_yr))

#     # ── TOTAL ─────────────────────────────────────────────────
#     else:
#         sec("Total Yield per Plant (All-time)")
#         if not df.empty:
#             gt = (df.groupby(["plant_name","brand"])
#                   .agg(total_mwh=("total_kwh","sum"), daily_kwh=("today_kwh","sum"))
#                   .reset_index())

#             fig = go.Figure()
#             for i, row in gt.iterrows():
#                 fig.add_trace(go.Bar(
#                     x=[row["plant_name"]], y=[row["total_mwh"]],
#                     name=row["plant_name"],
#                     marker_color=PALETTE[i % len(PALETTE)],
#                     marker_line_width=0,
#                 ))
#             fig.update_layout(
#                 plot_bgcolor="#fff", paper_bgcolor="#fff",
#                 font_family="Inter", font_color="#64748b",
#                 margin=dict(l=0,r=0,t=16,b=0), height=340,
#                 showlegend=False, bargap=0.35,
#                 yaxis=dict(title="MWh", showgrid=True, gridcolor="#f1f5f9",
#                            zeroline=False, tickfont_size=11),
#             )
#             fig.update_xaxes(showgrid=False, zeroline=False, tickfont_size=11)
#             st.plotly_chart(fig, use_container_width=True)

#             gt_disp = gt.rename(columns={"plant_name":"Plant","brand":"Brand",
#                                           "total_mwh":"Total Yield (MWh)",
#                                           "daily_kwh":"Today (kWh)"})
#             st.dataframe(gt_disp, use_container_width=True, hide_index=True)


# # ══════════════════════════════════════════════════════════════
# #  SERVICE
# # ══════════════════════════════════════════════════════════════
# elif page == "Service":
#     st.markdown('<div class="page-hdr"><h1>Plant Management</h1>'
#                 '<p>All registered plants and operational details</p></div>',
#                 unsafe_allow_html=True)
#     if df.empty:
#         st.warning("⚠️ No data."); st.stop()

#     fc1,fc2 = st.columns(2)
#     with fc1: pf2 = st.selectbox("Plant", ["All"]+sorted(df["plant_name"].dropna().unique()), key="pm_p")
#     with fc2: bf2 = st.selectbox("Brand", ["All"]+sorted(df["brand"].dropna().unique()),      key="pm_b")

#     ps = (df.groupby(["plant_name","brand"])
#           .agg(power_kw=("power_kw","sum"), today_kwh=("today_kwh","sum"),
#                total_kwh=("total_kwh","sum"), inv_count=("inverter_sn","count"))
#           .reset_index())
#     if pf2!="All": ps=ps[ps["plant_name"]==pf2]
#     if bf2!="All": ps=ps[ps["brand"]==bf2]

#     st.markdown(
#         f'<div class="stat-row">'
#           f'<div class="stat-item"><div class="stat-val">{len(ps)}</div><div class="stat-lbl">Plants</div></div>'
#           f'<div class="stat-item"><div class="stat-val">{f(ps["power_kw"].sum(),2)} kW</div><div class="stat-lbl">Total Power</div></div>'
#           f'<div class="stat-item"><div class="stat-val">{f(ps["today_kwh"].sum(),1)} kWh</div><div class="stat-lbl">Daily Yield</div></div>'
#           f'<div class="stat-item"><div class="stat-val">{f(ps["total_kwh"].sum(),1)} MWh</div><div class="stat-lbl">Total Yield</div></div>'
#         f'</div>', unsafe_allow_html=True)

#     st.markdown('<div class="tbl">', unsafe_allow_html=True)
#     st.markdown('<div class="tbl-hdr tbl-plant">'
#                 '<div>Plant Name</div><div>Brand</div><div>Organisation</div>'
#                 '<div>Inverters</div><div>Power (kW)</div>'
#                 '<div>Daily Yield</div><div>Total Yield</div><div>Status</div>'
#                 '</div>', unsafe_allow_html=True)
#     for _, row in ps.iterrows():
#         pr   = df[df["plant_name"]==row["plant_name"]]
#         on   = int((pr["status"].str.lower()=="online").sum())
#         tot  = int(row["inv_count"])
#         pst  = "Online" if on==tot and tot>0 else ("Offline" if on==0 else "Warning")
#         dy   = float(row["today_kwh"] or 0)
#         dy_s = f"{dy/1000:.3f} MWh" if dy>=1000 else f"{dy:.1f} kWh"
#         ty   = float(row["total_kwh"] or 0)
#         ty_s = f"{ty/1000:.3f} GWh" if ty>=1000 else f"{ty:.3f} MWh"
#         st.markdown(
#             f'<div class="tbl-row tbl-plant">'
#               f'<div class="cell-link">{row["plant_name"]}</div>'
#               f'<div>{chip(row["brand"])}</div>'
#               f'<div>Fractal Energy</div>'
#               f'<div>{on}/{tot}</div>'
#               f'<div><b>{f(row["power_kw"],2)}</b> kW</div>'
#               f'<div>{dy_s}</div><div>{ty_s}</div>'
#               f'<div>{badge(pst)}</div>'
#             f'</div>', unsafe_allow_html=True)
#     st.markdown('</div>', unsafe_allow_html=True)


# # ══════════════════════════════════════════════════════════════
# #  SETTINGS
# # ══════════════════════════════════════════════════════════════
# elif page == "Settings":
#     st.markdown('<div class="page-hdr"><h1>Settings</h1>'
#                 '<p>Credentials, alerts and app configuration</p></div>',
#                 unsafe_allow_html=True)

#     from config import (SOLIS_API_KEY, GROWATT_USERNAME, SUNGROW_APP_KEY,
#                         EMAIL_USER, TO_EMAILS, RATE_PER_KWH)

#     st.markdown("#### 🔑 API Credentials")
#     for brand,ok,hint in [
#         ("Solis",   bool(SOLIS_API_KEY),
#          SOLIS_API_KEY[:10]+"…" if SOLIS_API_KEY else "Not configured"),
#         ("Growatt", bool(GROWATT_USERNAME),
#          GROWATT_USERNAME or "Set GROWATT_USERNAME in config.py"),
#         ("Sungrow", bool(SUNGROW_APP_KEY),
#          SUNGROW_APP_KEY[:10]+"…" if SUNGROW_APP_KEY else "Set SUNGROW_APP_KEY in config.py"),
#     ]:
#         c1,c2,c3 = st.columns([1,1,4])
#         c1.markdown(f"**{brand}**")
#         c2.markdown("✅ OK" if ok else "⚠️ Not set")
#         c3.markdown(f"`{hint}`")

#     st.divider()
#     st.markdown("#### 📧 Email Alerts")
#     st.markdown(f"**Sender:** `{EMAIL_USER}`")
#     st.markdown(f"**Recipients:** `{', '.join(TO_EMAILS)}`")
#     st.divider()
#     st.markdown("#### 💰 Tariff Rate")
#     st.info(f"Current rate: **₹{RATE_PER_KWH}/kWh** — edit `RATE_PER_KWH` in config.py")
#     st.divider()
#     st.markdown("#### 👤 Logged in as")
#     st.info(f"`{st.session_state.user}`")
#     st.divider()
#     st.markdown("#### 🗂 Project Structure")
#     st.code("""
# solar_dashboard/
# ├── app.py              ← streamlit run app.py
# ├── config.py           ← ✏️  credentials & settings
# ├── requirements.txt
# ├── data/solar_data.db  ← auto-created
# └── utils/
#     ├── solis_api.py    ├── growatt_api.py
#     ├── sungrow_api.py  ├── aggregator.py
#     ├── database.py     └── alerts.py
#     """, language="")




# # ============================================================
# #  app.py  —  Solar Dashboard  |  streamlit run app.py # working for cluade (reports not wirking)
# # ============================================================
# import streamlit as st
# from streamlit_autorefresh import st_autorefresh
# import pandas as pd
# import plotly.express as px
# import plotly.graph_objects as go
# from datetime import datetime, date, timedelta

# from config import REFRESH_INTERVAL_SECONDS, RATE_PER_KWH
# from utils.database import init_db, get_history, get_alert_log
# from utils.aggregator import fetch_all_brands, check_alerts

# # ─────────────────────────────────────────────────────────────
# st.set_page_config(page_title="Solar Dashboard · Fractal Energy",
#                    page_icon="☀️", layout="wide",
#                    initial_sidebar_state="expanded")

# # ══════════════════════════════════════════════════════════════
# #  GLOBAL CSS  —  Navy · Teal · Amber theme
# # ══════════════════════════════════════════════════════════════
# st.markdown("""
# <style>
# @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

# *,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}

# :root{
#   /* ── Palette ── */
#   --navy:      #0a1628;
#   --navy2:     #0f2044;
#   --navy3:     #1a2f5a;
#   --teal:      #0d9488;
#   --teal-l:    #ccfbf1;
#   --teal-d:    #0f766e;
#   --amber:     #f59e0b;
#   --amber-l:   #fef3c7;
#   --amber-d:   #d97706;
#   --orange:    #f97316;
#   --orange-l:  #ffedd5;
#   --red:       #ef4444;
#   --red-l:     #fee2e2;
#   --green:     #10b981;
#   --green-l:   #d1fae5;
#   --sky:       #38bdf8;
#   --sky-l:     #e0f2fe;

#   /* ── Surfaces ── */
#   --bg:        #f0f4f8;
#   --card:      #ffffff;
#   --border:    #e2e8f0;
#   --border2:   #cbd5e1;

#   /* ── Text ── */
#   --text:      #0f172a;
#   --text2:     #475569;
#   --text3:     #94a3b8;

#   /* ── Shadows ── */
#   --shadow:    0 1px 4px rgba(10,22,40,.06),0 4px 20px rgba(10,22,40,.05);
#   --shadow-lg: 0 8px 40px rgba(10,22,40,.12);
#   --shadow-teal:0 4px 20px rgba(13,148,136,.25);
# }

# /* ── Fonts ── */
# html,body,[data-testid="stAppViewContainer"]{
#   background:var(--bg)!important;
#   font-family:'Plus Jakarta Sans',sans-serif!important;
#   color:var(--text);
# }
# [data-testid="stHeader"]{background:transparent!important;display:none;}
# #MainMenu,footer{visibility:hidden;}
# [data-testid="stDecoration"]{display:none;}
# .block-container{padding:28px 32px!important;max-width:100%!important;}

# /* ══ SIDEBAR ══════════════════════════════════════════════ */
# [data-testid="stSidebar"]{
#   background:var(--navy)!important;
#   border-right:1px solid rgba(255,255,255,.06)!important;
# }
# [data-testid="stSidebar"]>div{padding-top:0!important;}
# section[data-testid="stSidebarContent"]{padding:0!important;}

# .sb-logo{
#   padding:24px 20px 18px;
#   border-bottom:1px solid rgba(255,255,255,.07);
#   margin-bottom:6px;
#   display:flex;align-items:center;gap:12px;
# }
# .sb-logo-icon{
#   width:42px;height:42px;background:linear-gradient(135deg,var(--teal),var(--teal-d));
#   border-radius:12px;display:flex;align-items:center;justify-content:center;
#   font-size:20px;flex-shrink:0;box-shadow:var(--shadow-teal);
# }
# .sb-logo-title{color:#fff;font-weight:800;font-size:15px;letter-spacing:-.3px;}
# .sb-logo-sub{color:#64748b;font-size:11px;margin-top:1px;}
# .sb-section{
#   padding:14px 20px 4px;
#   font-size:10px;font-weight:700;color:#334155;
#   text-transform:uppercase;letter-spacing:.12em;
# }
# .sb-time{
#   padding:14px 20px;font-size:11px;color:#475569;
#   border-top:1px solid rgba(255,255,255,.06);margin-top:6px;
#   font-family:'JetBrains Mono',monospace;
# }

# /* ══ LOGIN PAGE ═══════════════════════════════════════════ */
# .login-wrap{
#   min-height:100vh;display:flex;align-items:center;justify-content:center;
#   background:linear-gradient(135deg,var(--navy) 0%,var(--navy2) 50%,#0d2b4e 100%);
#   padding:20px;
# }
# .login-card{
#   background:rgba(255,255,255,.04);
#   border:1px solid rgba(255,255,255,.1);
#   border-radius:20px;padding:48px 44px;width:100%;max-width:420px;
#   backdrop-filter:blur(20px);
#   box-shadow:0 20px 60px rgba(0,0,0,.4);
# }
# .login-logo{
#   width:60px;height:60px;
#   background:linear-gradient(135deg,var(--teal),var(--teal-d));
#   border-radius:16px;display:flex;align-items:center;justify-content:center;
#   font-size:28px;margin:0 auto 20px;
#   box-shadow:0 8px 24px rgba(13,148,136,.4);
# }
# .login-title{
#   font-size:24px;font-weight:800;color:#fff;text-align:center;
#   letter-spacing:-.4px;margin-bottom:6px;
# }
# .login-sub{font-size:13px;color:#64748b;text-align:center;margin-bottom:32px;}
# .login-label{font-size:13px;font-weight:600;color:#94a3b8;margin-bottom:6px;}
# .login-error{
#   background:rgba(239,68,68,.12);border:1px solid rgba(239,68,68,.3);
#   border-radius:8px;padding:10px 14px;font-size:13px;color:#fca5a5;
#   margin-bottom:16px;text-align:center;
# }

# /* ══ PAGE HEADER ══════════════════════════════════════════ */
# .page-hdr{margin-bottom:24px;}
# .page-hdr h1{
#   font-size:24px;font-weight:800;color:var(--text);
#   letter-spacing:-.5px;line-height:1.2;
# }
# .page-hdr p{font-size:13px;color:var(--text3);margin-top:4px;}

# /* ══ KPI CARDS ════════════════════════════════════════════ */
# .kpi-card{
#   background:var(--card);border-radius:16px;padding:24px 22px;
#   border:1px solid var(--border);box-shadow:var(--shadow);
#   display:flex;gap:16px;align-items:flex-start;
#   transition:transform .15s,box-shadow .15s;
#   position:relative;overflow:hidden;
# }
# .kpi-card::after{
#   content:'';position:absolute;top:0;left:0;right:0;height:3px;
#   background:linear-gradient(90deg,var(--teal),var(--sky));
#   border-radius:16px 16px 0 0;
# }
# .kpi-card.amber::after{background:linear-gradient(90deg,var(--amber),var(--orange));}
# .kpi-card.green::after{background:linear-gradient(90deg,var(--green),var(--teal));}
# .kpi-card.navy::after{background:linear-gradient(90deg,var(--navy3),var(--sky));}
# .kpi-card:hover{transform:translateY(-2px);box-shadow:var(--shadow-lg);}

# .kpi-icon{
#   width:50px;height:50px;border-radius:13px;flex-shrink:0;
#   display:flex;align-items:center;justify-content:center;font-size:22px;
# }
# .kpi-icon.teal  {background:var(--teal-l);color:var(--teal);}
# .kpi-icon.amber {background:var(--amber-l);color:var(--amber-d);}
# .kpi-icon.green {background:var(--green-l);color:var(--green);}
# .kpi-icon.navy  {background:var(--sky-l);color:#0284c7;}

# .kpi-label{
#   font-size:11px;color:var(--text3);font-weight:700;
#   text-transform:uppercase;letter-spacing:.1em;margin-bottom:6px;
# }
# .kpi-value{
#   font-size:28px;font-weight:800;color:var(--text);
#   line-height:1;letter-spacing:-.5px;
# }
# .kpi-unit{font-size:14px;font-weight:600;color:var(--text2);margin-left:3px;}
# .kpi-meta{font-size:12px;color:var(--text3);margin-top:8px;line-height:1.4;}
# .kpi-meta b{color:var(--teal);font-weight:600;}

# /* ══ SECTION HEADER ═══════════════════════════════════════ */
# .sec-hdr{
#   font-size:13px;font-weight:700;color:var(--text);
#   display:flex;align-items:center;gap:8px;
#   margin-bottom:14px;padding-bottom:10px;
#   border-bottom:2px solid var(--border);
# }
# .sec-hdr-dot{
#   width:8px;height:8px;border-radius:50%;
#   background:linear-gradient(135deg,var(--teal),var(--sky));
#   flex-shrink:0;
# }

# /* ══ CARD WRAPPER ═════════════════════════════════════════ */
# .card{
#   background:var(--card);border-radius:16px;padding:22px;
#   border:1px solid var(--border);box-shadow:var(--shadow);margin-bottom:16px;
# }

# /* ══ INVERTER CARD ════════════════════════════════════════ */
# .inv-card{
#   background:var(--card);border-radius:16px;padding:22px;
#   border:1px solid var(--border);box-shadow:var(--shadow);
#   margin-bottom:14px;transition:border-color .15s,box-shadow .15s;
# }
# .inv-card:hover{border-color:var(--primary);box-shadow:var(--shadow-teal);}
# .inv-card.alert-card{border-left:3px solid var(--red);}
# .inv-header{
#   display:flex;justify-content:space-between;align-items:flex-start;
#   margin-bottom:18px;padding-bottom:14px;
#   border-bottom:1px solid var(--border);
# }
# .inv-name{font-size:15px;font-weight:700;color:var(--text);letter-spacing:-.3px;}
# .inv-meta{font-size:11px;color:var(--text3);margin-top:3px;font-family:'JetBrains Mono',monospace;}
# .inv-params{display:grid;grid-template-columns:repeat(6,1fr);gap:16px;}
# .param-label{
#   font-size:10px;color:var(--text3);text-transform:uppercase;
#   letter-spacing:.08em;font-weight:600;margin-bottom:4px;
# }
# .param-val{font-size:18px;font-weight:700;color:var(--text);letter-spacing:-.3px;}
# .param-unit{font-size:11px;color:var(--text3);margin-left:2px;}
# .inv-footer{margin-top:14px;font-size:11px;color:var(--text3);font-family:'JetBrains Mono',monospace;}

# /* ══ TABLES ═══════════════════════════════════════════════ */
# .tbl{
#   background:var(--card);border-radius:16px;
#   border:1px solid var(--border);overflow:hidden;box-shadow:var(--shadow);
# }
# .tbl-hdr,.tbl-row{
#   display:grid;padding:0 20px;align-items:center;gap:10px;
# }
# .tbl-hdr{
#   background:linear-gradient(90deg,#f8fafc,#f1f5f9);
#   border-bottom:2px solid var(--border);
#   font-size:10px;font-weight:700;color:var(--text3);
#   text-transform:uppercase;letter-spacing:.1em;height:44px;
# }
# .tbl-row{
#   min-height:54px;border-bottom:1px solid var(--border);
#   font-size:13px;transition:background .1s;
# }
# .tbl-row:last-child{border-bottom:none;}
# .tbl-row:hover{background:#f8fafc;}
# .tbl-plant{grid-template-columns:2fr 1fr 1.1fr 1fr 1fr 1.1fr 1.3fr 1fr;}
# .tbl-alarm{grid-template-columns:1fr 1fr 1fr 1.5fr 1.4fr 2.2fr 1.2fr;}
# .cell-link{color:var(--primary);font-weight:700;cursor:pointer;font-size:13px;}

# /* ══ BADGES ═══════════════════════════════════════════════ */
# .badge{
#   display:inline-flex;align-items:center;gap:5px;
#   font-size:11px;font-weight:700;padding:4px 10px;
#   border-radius:20px;letter-spacing:.02em;
# }
# .badge::before{content:'';width:6px;height:6px;border-radius:50%;}
# .b-online {background:var(--green-l);color:#065f46;}
# .b-online::before{background:var(--green);}
# .b-offline{background:var(--red-l);color:#991b1b;}
# .b-offline::before{background:var(--red);}
# .b-warning{background:var(--amber-l);color:#92400e;}
# .b-warning::before{background:var(--amber);}
# .b-unknown{background:#f1f5f9;color:#64748b;}
# .b-unknown::before{background:#94a3b8;}
# .b-active {background:var(--red-l);color:#991b1b;}
# .b-active::before{background:var(--red);}
# .b-resolved{background:var(--green-l);color:#065f46;}
# .b-resolved::before{background:var(--green);}
# .b-critical{background:var(--red-l);color:#991b1b;font-weight:800;}
# .b-critical::before{background:var(--red);}

# /* ══ CHIPS ════════════════════════════════════════════════ */
# .chip{
#   display:inline-block;font-size:10px;font-weight:800;
#   padding:3px 9px;border-radius:6px;
#   letter-spacing:.1em;text-transform:uppercase;
# }
# .chip-solis  {background:#dbeafe;color:#1e40af;}
# .chip-growatt{background:#d1fae5;color:#065f46;}
# .chip-sungrow{background:#ffedd5;color:#c2410c;}

# /* ══ ALERT STRIP ══════════════════════════════════════════ */
# .alert-strip{
#   background:linear-gradient(135deg,#fff1f2,#ffe4e6);
#   border:1px solid #fecdd3;border-left:4px solid var(--red);
#   border-radius:12px;padding:16px 18px;margin-bottom:12px;
#   display:flex;gap:14px;align-items:flex-start;
# }
# .alert-strip-ico{font-size:20px;flex-shrink:0;}
# .alert-strip-ttl{font-size:14px;font-weight:700;color:var(--red);}
# .alert-strip-msg{font-size:12px;color:#7f1d1d;margin-top:3px;}

# /* ══ STAT ROW ═════════════════════════════════════════════ */
# .stat-row{
#   background:var(--card);border-radius:14px;padding:16px 24px;
#   border:1px solid var(--border);display:flex;gap:32px;
#   margin-bottom:20px;align-items:center;flex-wrap:wrap;
#   box-shadow:var(--shadow);
# }
# .stat-item{text-align:center;}
# .stat-val{font-size:20px;font-weight:800;color:var(--text);letter-spacing:-.3px;}
# .stat-lbl{font-size:10px;color:var(--text3);margin-top:2px;font-weight:600;text-transform:uppercase;letter-spacing:.08em;}

# /* ══ STREAMLIT OVERRIDES ══════════════════════════════════ */
# .stButton>button{
#   background:linear-gradient(135deg,var(--teal),var(--teal-d))!important;
#   color:#fff!important;border:none!important;border-radius:10px!important;
#   font-family:'Plus Jakarta Sans',sans-serif!important;
#   font-weight:700!important;font-size:13px!important;
#   padding:10px 24px!important;letter-spacing:.01em!important;
#   box-shadow:0 4px 12px rgba(13,148,136,.3)!important;
#   transition:all .15s!important;
# }
# .stButton>button:hover{transform:translateY(-1px)!important;box-shadow:0 6px 20px rgba(13,148,136,.4)!important;}
# div[data-testid="stSelectbox"]>label,
# div[data-testid="stTextInput"]>label{
#   font-size:12px!important;font-weight:700!important;
#   color:var(--text2)!important;text-transform:uppercase!important;letter-spacing:.06em!important;
# }
# [data-testid="stRadio"]>label{font-size:13px!important;font-weight:600!important;}
# .stRadio>div{gap:4px!important;}
# .stAlert{border-radius:12px!important;}
# div[data-testid="stTextInput"] input{
#   border-radius:10px!important;border-color:var(--border2)!important;
#   font-size:14px!important;font-family:'Plus Jakarta Sans',sans-serif!important;
# }
# div[data-testid="stSelectbox"]>div>div{
#   border-radius:10px!important;border-color:var(--border2)!important;
#   font-size:13px!important;
# }

# /* ══ LOGIN STREAMLIT INPUT OVERRIDES ═══════════════════════ */
# .login-page [data-testid="stTextInput"] input{
#   background:rgba(255,255,255,.08)!important;
#   border:1px solid rgba(255,255,255,.15)!important;
#   border-radius:10px!important;color:#fff!important;
#   font-size:14px!important;padding:12px 14px!important;
# }
# .login-page .stButton>button{
#   width:100%!important;padding:14px!important;font-size:15px!important;
# }

# /* ══ DIVIDER ══════════════════════════════════════════════ */
# .divider{height:1px;background:var(--border);margin:20px 0;}

# /* ══ METRIC OVERRIDES ═════════════════════════════════════ */
# [data-testid="stMetric"]{
#   background:var(--card);border-radius:12px;padding:16px 18px;
#   border:1px solid var(--border);box-shadow:var(--shadow);
# }
# [data-testid="stMetricLabel"]{font-size:11px!important;font-weight:700!important;color:var(--text3)!important;text-transform:uppercase!important;letter-spacing:.08em!important;}
# [data-testid="stMetricValue"]{font-size:24px!important;font-weight:800!important;color:var(--text)!important;letter-spacing:-.4px!important;}
# </style>
# """, unsafe_allow_html=True)

# # ══════════════════════════════════════════════════════════════
# #  INIT
# # ══════════════════════════════════════════════════════════════
# init_db()

# # ══════════════════════════════════════════════════════════════
# #  LOGIN
# # ══════════════════════════════════════════════════════════════
# USERS = {
#     "admin": "1234"
# }

# if "logged_in" not in st.session_state:
#     st.session_state.logged_in = False
#     st.session_state.user = ""

# if not st.session_state.logged_in:
#     # Full-screen dark login — hide sidebar
#     st.markdown("""
#     <style>
#     [data-testid="stSidebar"]{display:none!important;}
#     .block-container{padding:0!important;max-width:100%!important;}
#     </style>""", unsafe_allow_html=True)

#     st.markdown("""
#     <div style="min-height:100vh;display:flex;align-items:center;justify-content:center;
#     background:linear-gradient(135deg,#0a1628 0%,#0f2044 55%,#0d2b4e 100%);padding:20px;">
#       <div style="width:100%;max-width:420px;">
#         <div style="text-align:center;margin-bottom:32px;">
#           <div style="width:68px;height:68px;background:linear-gradient(135deg,#0d9488,#0f766e);
#             border-radius:18px;display:flex;align-items:center;justify-content:center;
#             font-size:32px;margin:0 auto 16px;box-shadow:0 8px 24px rgba(13,148,136,.4);">☀️</div>
#           <div style="font-size:26px;font-weight:800;color:#fff;letter-spacing:-.5px;">Solar Dashboard</div>
#           <div style="font-size:13px;color:#64748b;margin-top:6px;">Fractal Energy · Monitoring Platform</div>
#         </div>
#         <div style="background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.1);
#           border-radius:20px;padding:36px 32px;backdrop-filter:blur(20px);
#           box-shadow:0 20px 60px rgba(0,0,0,.4);">
#     """, unsafe_allow_html=True)

#     email    = st.text_input("Email Address",    placeholder="your@email.com")
#     password = st.text_input("Password",         placeholder="••••••••", type="password")

#     if st.button("Sign In →", use_container_width=True):
#         if email in USERS and USERS[email] == password:
#             st.session_state.logged_in = True
#             st.session_state.user = email
#             st.rerun()
#         else:
#             st.error("Invalid email or password. Please try again.")

#     st.markdown("""
#         <div style="text-align:center;margin-top:20px;font-size:12px;color:#475569;">
#           Secured by Fractal Energy · v2.0
#         </div>
#         </div></div></div>
#     """, unsafe_allow_html=True)
#     st.stop()

# # ══════════════════════════════════════════════════════════════
# #  AUTHENTICATED APP
# # ══════════════════════════════════════════════════════════════
# st_autorefresh(interval=REFRESH_INTERVAL_SECONDS * 1000, key="solar_ar")

# # ── Helpers ──────────────────────────────────────────────────
# def f(v, d=1, na="—"):
#     try:    return f"{float(v):.{d}f}"
#     except: return na

# def badge(s, kind=None):
#     s  = (s or "").strip()
#     sl = s.lower()
#     if kind == "level":
#         cls = "b-critical" if sl == "critical" else "b-warning"
#     elif kind == "status_alarm":
#         cls = "b-active" if sl == "active" else "b-resolved"
#     else:
#         if sl == "online":              cls = "b-online"
#         elif sl in ("offline","fault"): cls = "b-offline"
#         else:                           cls = "b-unknown"
#     return f'<span class="badge {cls}">{s}</span>'

# def chip(b):
#     return f'<span class="chip chip-{(b or "").lower()}">{b}</span>'

# def earn(kwh):
#     v = float(kwh or 0) * RATE_PER_KWH
#     if v >= 1_000_000: return f"₹{v/1_000_000:.3f}M"
#     if v >= 1_000:     return f"₹{v/1_000:.3f}K"
#     return f"₹{v:.2f}"

# def chart_style(fig, h=300):
#     fig.update_layout(
#         plot_bgcolor="#fff", paper_bgcolor="#fff",
#         font_color="#64748b", font_family="Inter",
#         margin=dict(l=0,r=0,t=16,b=0), height=h,
#         legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=12, color="#64748b")),
#         bargap=0.28,
#     )
#     fig.update_traces(marker_line_width=0)
#     fig.update_xaxes(showgrid=False, zeroline=False, tickfont_size=11,
#                      tickfont_color="#94a3b8", linecolor="#e2e8f0")
#     fig.update_yaxes(showgrid=True, gridcolor="#f1f5f9", zeroline=False,
#                      tickfont_size=11, tickfont_color="#94a3b8")
#     return fig

# PALETTE = ["#0d9488","#f59e0b","#3b82f6","#f97316","#10b981","#8b5cf6","#06b6d4","#ec4899"]
# BRAND_COLORS = {"Solis":"#3b82f6","Growatt":"#10b981","Sungrow":"#f97316"}

# def sec(title, icon=""):
#     st.markdown(f'<div class="sec-hdr"><div class="sec-hdr-dot"></div>{icon} {title}</div>',
#                 unsafe_allow_html=True)

# # ── Sidebar ──────────────────────────────────────────────────
# with st.sidebar:
#     st.markdown(f"""
#     <div class="sb-logo">
#       <div class="sb-logo-icon">☀</div>
#       <div>
#         <div class="sb-logo-title">Solar Dashboard</div>
#         <div class="sb-logo-sub">Fractal Energy</div>
#       </div>
#     </div>""", unsafe_allow_html=True)

#     page = st.radio("", ["📊  Overview","🔧  O&M","📈  Report","🗺  Service","⚙️  Settings"],
#                     label_visibility="collapsed")
#     page = page.split("  ",1)[1].strip()

#     # st.markdown('<div class="sb-section">Data Sources</div>', unsafe_allow_html=True)
#     # sel_brands = [b for b in ["Solis","Growatt","Sungrow"]
#     #               if st.checkbox(b, value=(b=="Solis"), key=f"cb_{b}")]

#     st.markdown('<div class="sb-section">Data Sources</div>', unsafe_allow_html=True)

#     sel_brands = st.multiselect(
#         "Select Brands",
#         ["Solis", "Growatt", "Sungrow"],
#         default=["Solis"]
#     )

#     if not sel_brands:
#         st.warning("Please select at least one brand.")
#         st.stop()

#     st.markdown('<div style="height:6px"></div>', unsafe_allow_html=True)
#     if st.button("🔄  Refresh Now"):
#         st.cache_data.clear(); st.rerun()

#     show_debug = st.checkbox("🔍  Debug", value=False)

#     # Logout
#     st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)
#     if st.button("🚪  Sign Out"):
#         st.session_state.logged_in = False
#         st.rerun()

#     st.markdown(f"""
#     <div class="sb-time">
#       ⏱ {datetime.now().strftime('%d %b %Y')}<br>
#       <b style="color:#94a3b8;">{datetime.now().strftime('%H:%M:%S')}</b><br>
#       <span style="color:#334155;">Auto-refresh {REFRESH_INTERVAL_SECONDS//60} min</span>
#     </div>""", unsafe_allow_html=True)

# # ── Fetch data ────────────────────────────────────────────────
# @st.cache_data(ttl=REFRESH_INTERVAL_SECONDS)
# def load(brands):
#     result = fetch_all_brands(list(brands))
#     if not result:
#         raise RuntimeError("empty")   # prevent caching empty result
#     return result

# with st.spinner("Fetching live data…"):
#     try:
#         records = load(tuple(sel_brands))
#     except Exception:
#         # Cache returned empty or errored — fetch fresh without cache
#         records = fetch_all_brands(list(sel_brands))
#         if not records:
#             st.cache_data.clear()     # clear so next refresh retries

# alerts = check_alerts(records, st.session_state)

# df = pd.DataFrame()
# if records:
#     df = pd.DataFrame(records)
#     for c in ["power_kw","today_kwh","total_kwh","temperature","voltage","current_a"]:
#         if c in df.columns:
#             df[c] = pd.to_numeric(df[c], errors="coerce")
#     if "status" in df.columns:
#         df["status"] = df["status"].astype(str).str.strip()

# # ── Debug ─────────────────────────────────────────────────────
# if show_debug and not df.empty:
#     st.markdown("### 🔍 Debug: Raw API Data")
#     st.dataframe(df, use_container_width=True)
#     try:
#         from utils.solis_api import fetch_summary as _fsum, _raw_plants_cache
#         summ = _fsum()
#         st.write("**fetch_summary():**", summ)
#     except Exception as ex:
#         st.error(f"Debug error: {ex}")
#     st.divider()


# # ══════════════════════════════════════════════════════════════
# #  OVERVIEW
# # ══════════════════════════════════════════════════════════════
# if page == "Overview":
#     st.markdown('<div class="page-hdr"><h1>Plant Overview</h1>'
#                 '<p>Real-time performance across all plants</p></div>',
#                 unsafe_allow_html=True)

#     if df.empty:
#         st.warning("⚠️ No data. Check credentials in config.py and click Refresh.")
#         st.stop()

#     # ── KPI values ────────────────────────────────────────────
#     total_power = float(df["power_kw"].sum())
#     daily_kwh   = float(df["today_kwh"].sum())
#     total_mwh   = float(df["total_kwh"].sum())
#     monthly_mwh = 0.0

#     try:
#         if "Solis" in sel_brands:
#             from utils.solis_api import fetch_summary as _fs
#             summ = _fs()
#             if summ.get("power_kw",    0) > 0: total_power = float(summ["power_kw"])
#             # daily_kwh: use df sum (inverterList etoday) — most accurate per-inverter value
#             # fetch_summary dayEnergy can be partial; df["today_kwh"].sum() is always correct
#             if summ.get("monthly_mwh", 0) > 0: monthly_mwh = float(summ["monthly_mwh"])
#             if summ.get("total_mwh",   0) > 0: total_mwh   = float(summ["total_mwh"])
#     except Exception: pass

#     # Always use inverter-level sum for daily yield — it's the most accurate
#     # (confirmed: df sum = 1697.5 kWh matches Solis, API dayEnergy can lag)
#     daily_kwh = float(df["today_kwh"].sum())

#     if monthly_mwh == 0:
#         hist = get_history(hours=720)
#         monthly_kwh_db = daily_kwh
#         if not hist.empty and "today_kwh" in hist.columns:
#             hist["fetched_at"] = pd.to_datetime(hist["fetched_at"])
#             hist["today_kwh"]  = pd.to_numeric(hist["today_kwh"], errors="coerce")
#             m = hist[hist["fetched_at"].dt.month == datetime.now().month]
#             if not m.empty:
#                 v = float(m.groupby([m["fetched_at"].dt.date,"inverter_sn"])["today_kwh"].max().sum())
#                 monthly_kwh_db = max(v, daily_kwh)
#         monthly_mwh = monthly_kwh_db / 1000
#     monthly_kwh = monthly_mwh * 1000

#     # Display units
#     daily_val,daily_unit = (f(daily_kwh/1000,3),"MWh") if daily_kwh>=1000 else (f(daily_kwh,1),"kWh")
#     mo_val,mo_unit       = f(monthly_mwh,3), "MWh"
#     if total_mwh >= 1000:
#         tot_val,tot_unit,tot_earn = f(total_mwh/1000,3),"GWh",total_mwh*1000
#     else:
#         tot_val,tot_unit,tot_earn = f(total_mwh,3),"MWh",total_mwh*1000

#     n_on  = int((df["status"].str.lower()=="online").sum())
#     n_tot = len(df)

#     # ── 4 KPI cards ──────────────────────────────────────────
#     c1,c2,c3,c4 = st.columns(4)
#     kpis = [
#         (c1,"teal","teal","⚡","Power",f(total_power,2),"kW",
#          f"Inverters: <b>{n_on}/{n_tot} online</b>"),
#         (c2,"amber","amber","🔋","Daily Yield",daily_val,daily_unit,
#          f"Earning today: <b>{earn(daily_kwh)}</b>"),
#         (c3,"green","green","📅","Monthly Yield",mo_val,mo_unit,
#          f"Earning this month: <b>{earn(monthly_kwh)}</b>"),
#         (c4,"navy","navy","📊","Total Yield",tot_val,tot_unit,
#          f"Total earning: <b>{earn(tot_earn)}</b>"),
#     ]
#     for col,card_cls,ico_cls,ico,lbl,val,unit,meta in kpis:
#         with col:
#             st.markdown(f"""
#             <div class="kpi-card {card_cls}">
#               <div class="kpi-icon {ico_cls}">{ico}</div>
#               <div>
#                 <div class="kpi-label">{lbl}</div>
#                 <div class="kpi-value">{val}<span class="kpi-unit"> {unit}</span></div>
#                 <div class="kpi-meta">{meta}</div>
#               </div>
#             </div>""", unsafe_allow_html=True)

#     st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)

#     # ── Alert strips ─────────────────────────────────────────
#     if alerts:
#         for a in alerts[:3]:
#             st.markdown(f"""
#             <div class="alert-strip">
#               <div class="alert-strip-ico">🚨</div>
#               <div>
#                 <div class="alert-strip-ttl">{a['plant_name']} — {a.get('inverter_sn','')}</div>
#                 <div class="alert-strip-msg">{a['issue']}</div>
#               </div>
#             </div>""", unsafe_allow_html=True)

#     # ── Charts ───────────────────────────────────────────────
#     ch1, ch2 = st.columns([3, 2])

#     with ch1:
#         sec("Power by Plant (kW)")
#         pdf = df.groupby(["plant_name","brand"])["power_kw"].sum().reset_index()
#         fig = px.bar(pdf, x="plant_name", y="power_kw", color="brand",
#                      color_discrete_map=BRAND_COLORS,
#                      labels={"power_kw":"Power (kW)","plant_name":"","brand":"Brand"})
#         fig.update_traces(marker_cornerradius=4)
#         st.plotly_chart(chart_style(fig, 290), use_container_width=True)

#     with ch2:
#         sec("Daily Yield Share")
#         pief = df.groupby("plant_name")["today_kwh"].sum().reset_index()
#         fig2 = go.Figure(go.Pie(
#             labels=pief["plant_name"],
#             values=pief["today_kwh"],
#             hole=0.52,
#             marker=dict(colors=PALETTE, line=dict(color="#fff", width=2)),
#             textposition="outside",
#             textinfo="label+percent",
#             textfont=dict(size=11, family="Plus Jakarta Sans"),
#             pull=[0.04]*len(pief),
#         ))
#         fig2.update_layout(
#             plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
#             font_family="Inter", font_color="#64748b",
#             margin=dict(l=60, r=60, t=20, b=20), height=290,
#             showlegend=False,
#             annotations=[dict(text=f"<b>{f(pief['today_kwh'].sum(),1)}</b><br>kWh",
#                               font=dict(size=14,color="#0f172a",family="Plus Jakarta Sans"),
#                               showarrow=False)]
#         )
#         st.plotly_chart(fig2, use_container_width=True)

#     # ── Plant table ──────────────────────────────────────────
#     sec("Plant List")
#     ps = (df.groupby(["plant_name","brand"])
#           .agg(power_kw=("power_kw","sum"), today_kwh=("today_kwh","sum"),
#                total_kwh=("total_kwh","sum"), inv_count=("inverter_sn","count"))
#           .reset_index())

#     st.markdown('<div class="tbl">', unsafe_allow_html=True)
#     st.markdown(
#         '<div class="tbl-hdr tbl-plant">'
#         '<div>Plant Name</div><div>Brand</div><div>Inverters</div>'
#         '<div>Power (kW)</div><div>Daily Yield</div>'
#         '<div>Total Yield</div><div>Earning Today</div><div>Status</div>'
#         '</div>', unsafe_allow_html=True)

#     for _, row in ps.iterrows():
#         pr   = df[df["plant_name"]==row["plant_name"]]
#         on   = int((pr["status"].str.lower()=="online").sum())
#         tot  = int(row["inv_count"])
#         pst  = "Online" if on==tot and tot>0 else ("Offline" if on==0 else "Warning")
#         dy   = float(row["today_kwh"] or 0)
#         dy_s = f"{dy/1000:.3f} MWh" if dy>=1000 else f"{dy:.1f} kWh"
#         ty   = float(row["total_kwh"] or 0)
#         ty_s = f"{ty/1000:.3f} GWh" if ty>=1000 else f"{ty:.3f} MWh"
#         st.markdown(
#             f'<div class="tbl-row tbl-plant">'
#               f'<div class="cell-link">{row["plant_name"]}</div>'
#               f'<div>{chip(row["brand"])}</div>'
#               f'<div>{on}/{tot}</div>'
#               f'<div><b>{f(row["power_kw"],2)}</b> kW</div>'
#               f'<div>{dy_s}</div><div>{ty_s}</div>'
#               f'<div>{earn(dy)}</div><div>{badge(pst)}</div>'
#             f'</div>', unsafe_allow_html=True)
#     st.markdown('</div>', unsafe_allow_html=True)


# # ══════════════════════════════════════════════════════════════
# #  O&M
# # ══════════════════════════════════════════════════════════════
# elif page == "O&M":
#     sub = st.radio("", ["🔔  Alarm Information","⚡  Device Overview"],
#                    horizontal=True, label_visibility="collapsed")
#     sub = sub.split("  ",1)[1].strip()
#     st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

#     alarm_log = get_alert_log(200)
#     all_alarms = []
#     for a in alerts:
#         all_alarms.append({"device_type":"Inverter","level":"Critical","status":"Active",
#             "plant_name":a.get("plant_name","—"),"sn":a.get("inverter_sn","—"),
#             "content":a.get("issue","—"),"brand":a.get("brand","—"),
#             "time":datetime.now().strftime("%Y-%m-%d %H:%M")})
#     if not alarm_log.empty:
#         for _, r in alarm_log.iterrows():
#             all_alarms.append({"device_type":"Inverter","level":"Warning","status":"Resolved",
#                 "plant_name":r.get("plant_name","—"),"sn":r.get("inverter_sn","—"),
#                 "content":r.get("issue","—"),"brand":r.get("brand","—"),
#                 "time":r.get("alerted_at","—")})

#     if sub == "Alarm Information":
#         st.markdown('<div class="page-hdr"><h1>Alarm Information</h1>'
#                     '<p>Fault detection and alert history</p></div>',
#                     unsafe_allow_html=True)

#         plant_opts = ["All"] + sorted(df["plant_name"].dropna().unique()) if not df.empty else ["All"]
#         sn_opts    = ["All"] + sorted(df["inverter_sn"].dropna().unique()) if not df.empty else ["All"]
#         brand_opts = ["All"] + sorted(df["brand"].dropna().unique())       if not df.empty else ["All"]

#         fc1,fc2,fc3,fc4,fc5 = st.columns(5)
#         with fc1: fp = st.selectbox("Plant Name",  plant_opts)
#         with fc2: fs = st.selectbox("S/N",         sn_opts)
#         with fc3: fb = st.selectbox("Brand",        brand_opts)
#         with fc4: fst= st.selectbox("Status",       ["All","Active","Resolved"])
#         with fc5: fl = st.selectbox("Level",        ["All","Critical","Warning"])

#         filt = all_alarms[:]
#         if fp !="All": filt=[a for a in filt if a["plant_name"]==fp]
#         if fs !="All": filt=[a for a in filt if a["sn"]        ==fs]
#         if fb !="All": filt=[a for a in filt if a["brand"]     ==fb]
#         if fst!="All": filt=[a for a in filt if a["status"]    ==fst]
#         if fl !="All": filt=[a for a in filt if a["level"]     ==fl]

#         m1,m2,m3 = st.columns(3)
#         m1.metric("Total", len(filt))
#         m2.metric("Active",   sum(1 for a in filt if a["status"]=="Active"))
#         m3.metric("Resolved", sum(1 for a in filt if a["status"]=="Resolved"))

#         if not filt:
#             st.success("✅ No alarms — all systems operating normally.")
#         else:
#             st.markdown('<div class="tbl">', unsafe_allow_html=True)
#             st.markdown('<div class="tbl-hdr tbl-alarm">'
#                         '<div>Device</div><div>Level</div><div>Status</div>'
#                         '<div>Plant</div><div>S/N</div><div>Issue</div><div>Time</div>'
#                         '</div>', unsafe_allow_html=True)
#             for a in filt:
#                 st.markdown(
#                     f'<div class="tbl-row tbl-alarm">'
#                       f'<div>{a["device_type"]}</div>'
#                       f'<div>{badge(a["level"],"level")}</div>'
#                       f'<div>{badge(a["status"],"status_alarm")}</div>'
#                       f'<div>{chip(a["brand"])} {a["plant_name"]}</div>'
#                       f'<div style="font-size:11px;color:var(--text3);font-family:\'JetBrains Mono\',monospace;">{a["sn"]}</div>'
#                       f'<div>{a["content"]}</div>'
#                       f'<div style="font-size:11px;color:var(--text3);">{a["time"]}</div>'
#                     f'</div>', unsafe_allow_html=True)
#             st.markdown('</div>', unsafe_allow_html=True)

#     else:
#         st.markdown('<div class="page-hdr"><h1>Device Overview</h1>'
#                     '<p>Live readings for every inverter</p></div>',
#                     unsafe_allow_html=True)
#         if df.empty:
#             st.warning("⚠️ No data."); st.stop()

#         fc1,fc2,fc3,fc4 = st.columns(4)
#         with fc1: bf = st.selectbox("Brand",  ["All"]+sorted(df["brand"].dropna().unique()),       key="do_b")
#         with fc2: pf = st.selectbox("Plant",  ["All"]+sorted(df["plant_name"].dropna().unique()),  key="do_p")
#         with fc3: sf = st.selectbox("S/N",    ["All"]+sorted(df["inverter_sn"].dropna().unique()), key="do_s")
#         with fc4: stf= st.selectbox("Status", ["All"]+sorted(df["status"].dropna().unique()),      key="do_st")

#         vw = df.copy()
#         if bf !="All": vw=vw[vw["brand"]       ==bf]
#         if pf !="All": vw=vw[vw["plant_name"]  ==pf]
#         if sf !="All": vw=vw[vw["inverter_sn"] ==sf]
#         if stf!="All": vw=vw[vw["status"]      ==stf]

#         st.markdown(
#             f'<div class="stat-row">'
#               f'<div class="stat-item"><div class="stat-val">{len(vw)}</div><div class="stat-lbl">Inverters</div></div>'
#               f'<div class="stat-item"><div class="stat-val">{f(vw["power_kw"].sum(),2)} kW</div><div class="stat-lbl">Total Power</div></div>'
#               f'<div class="stat-item"><div class="stat-val">{f(vw["today_kwh"].sum(),1)} kWh</div><div class="stat-lbl">Daily Yield</div></div>'
#               f'<div class="stat-item"><div class="stat-val">{int((vw["status"].str.lower()=="online").sum())}</div><div class="stat-lbl">Online</div></div>'
#             f'</div>', unsafe_allow_html=True)

#         alert_sns = {a.get("inverter_sn") for a in alerts}
#         for _, row in vw.iterrows():
#             sn    = str(row.get("inverter_sn","N/A"))
#             brand = str(row.get("brand",""))
#             st_   = str(row.get("status",""))
#             params = [
#                 ("Power Now",   f(row.get("power_kw"),2),  "kW"),
#                 ("Daily Yield", f(row.get("today_kwh"),1), "kWh"),
#                 ("Total Yield", f(row.get("total_kwh"),3), "MWh"),
#                 ("Temperature", f(row.get("temperature"),1),"°C"),
#                 ("AC Voltage",  f(row.get("voltage"),1),   "V"),
#                 ("AC Current",  f(row.get("current_a"),1), "A"),
#             ]
#             p_html = "".join(
#                 f'<div><div class="param-label">{l}</div>'
#                 f'<div class="param-val">{v}<span class="param-unit"> {u}</span></div></div>'
#                 for l,v,u in params)
#             border = "border-left:3px solid var(--red);" if sn in alert_sns else ""
#             st.markdown(
#                 f'<div class="inv-card" style="{border}">'
#                   f'<div class="inv-header">'
#                     f'<div><div class="inv-name">{row.get("plant_name","")}</div>'
#                     f'<div class="inv-meta">S/N: {sn} · {chip(brand)} · {row.get("last_update","—")}</div></div>'
#                     + badge(st_) +
#                   f'</div>'
#                   f'<div class="inv-params">{p_html}</div>'
#                 f'</div>', unsafe_allow_html=True)


# # ══════════════════════════════════════════════════════════════
# #  REPORT  — pulls historical data from Solis API directly
# # ══════════════════════════════════════════════════════════════
# elif page == "Report":
#     st.markdown('<div class="page-hdr"><h1>Plant Report</h1>'
#                 '<p>Historical generation data from Solis Cloud</p></div>',
#                 unsafe_allow_html=True)

#     rtype = st.radio("", ["Daily","Monthly","Annual","Total"],
#                      horizontal=True, label_visibility="collapsed")
#     st.markdown('<div style="height:10px"></div>', unsafe_allow_html=True)

#     # Plant selector — always from live df
#     plant_opts = (["All Plants"] + sorted(df["plant_name"].dropna().unique().tolist())
#                   if not df.empty else ["No data"])

#     fc1, fc2 = st.columns([2, 1])
#     with fc1: sel_plant = st.selectbox("Select Plant", plant_opts)
#     with fc2: sel_date  = st.date_input("Date", value=date.today())

#     # Shared line chart helper
#     def line_chart(fig, h=360):
#         fig = chart_style(fig, h)
#         fig.update_traces(selector=dict(type="scatter"), line=dict(width=2.5))
#         fig.update_layout(hovermode="x unified")
#         return fig

#     # Get plant IDs for selected plant
#     # from utils.solis_api import (get_plants as _get_solis_plants,
#     #                               get_all_plants_daily, get_all_plants_monthly,
#     #                               get_plant_daily_history   as solis_daily,
#     #                               get_plant_monthly_history as solis_monthly)
#     # from utils.growatt_api import (get_plant_daily_history   as growatt_daily,
#     #                                get_plant_monthly_history as growatt_monthly,
#     #                                _get_plants               as _get_growatt_plants)

#     from utils.solis_api import get_plants as _get_solis_plants

# # Safe fallback imports
#     try:
#         from utils.solis_api import get_plant_daily_history as solis_daily
#     except ImportError:
#         def solis_daily(*args, **kwargs):
#             return []

#     try:
#         from utils.solis_api import get_plant_monthly_history as solis_monthly
#     except ImportError:
#         def solis_monthly(*args, **kwargs):
#             return []

#     try:
#         from utils.solis_api import get_all_plants_daily
#     except ImportError:
#         def get_all_plants_daily(*args, **kwargs):
#             return pd.DataFrame()

#     try:
#         from utils.solis_api import get_all_plants_monthly
#     except ImportError:
#         def get_all_plants_monthly(*args, **kwargs):
#             return pd.DataFrame()

#     from utils.growatt_api import (
#         get_plant_daily_history as growatt_daily,
#         get_plant_monthly_history as growatt_monthly,
#         _get_plants as _get_growatt_plants
#     )

#     # @st.cache_data(ttl=300)
#     # def _plants_cached():
#     #     plants = []
#     #     try:
#     #         for p in _get_solis_plants():
#     #             plants.append({"name": p.get("stationName"), "id": p.get("id"), "brand": "Solis"})
#     #     except Exception: pass
#     #     try:
#     #         for p in _get_growatt_plants():
#     #             pid   = str(p.get("pId") or p.get("plantId",""))
#     #             pname = p.get("plantNameEncryption") or p.get("plantName","")
#     #             plants.append({"name": pname, "id": pid, "brand": "Growatt"})
#     #     except Exception: pass
#     #     return plants

#     # all_plants    = _plants_cached()
#     @st.cache_data(ttl=300)
#     def _plants_cached(brands):
#         plants = []

#         if "Solis" in brands:
#             try:
#                 for p in _get_solis_plants():
#                     plants.append({
#                         "name": p.get("stationName"),
#                         "id": p.get("id"),
#                         "brand": "Solis"
#                     })
#             except:
#                 pass

#         if "Growatt" in brands:
#             try:
#                 for p in _get_growatt_plants():
#                     pid = str(p.get("pId") or p.get("plantId", ""))
#                     pname = p.get("plantNameEncryption") or p.get("plantName", "")
#                     plants.append({
#                         "name": pname,
#                         "id": pid,
#                         "brand": "Growatt"
#                     })
#             except:
#                 pass

#         return plants


#     all_plants = _plants_cached(tuple(sel_brands))
#     plant_id_map  = {p["name"]: (p["id"], p["brand"]) for p in all_plants}

#     def get_daily_history(plant_name, month_str):
#         info = plant_id_map.get(plant_name)
#         if not info: return []
#         pid, brand = info
#         if brand == "Growatt": return growatt_daily(pid, month_str)
#         return solis_daily(pid, month_str)

#     def get_monthly_history(plant_name, year_str):
#         info = plant_id_map.get(plant_name)
#         if not info: return []
#         pid, brand = info
#         if brand == "Growatt": return growatt_monthly(pid, year_str)
#         return solis_monthly(pid, year_str)

#     # ── DAILY ────────────────────────────────────────────────
#     if rtype == "Daily":
#         # Daily uses local DB (power readings every 5 min) — Solis API
#         # doesn't have per-minute history, only daily totals
#         hist_df = get_history(hours=8760)

#         if hist_df.empty:
#             st.info("📭 No intraday data yet — app collects readings every 5 min. Check back later.")
#         else:
#             hist_df["fetched_at"] = pd.to_datetime(hist_df["fetched_at"])
#             hist_df["power_kw"]   = pd.to_numeric(hist_df["power_kw"],  errors="coerce")
#             hist_df["today_kwh"]  = pd.to_numeric(hist_df["today_kwh"], errors="coerce")
#             if sel_plant != "All Plants":
#                 hist_df = hist_df[hist_df["plant_name"] == sel_plant]

#             day = hist_df[hist_df["fetched_at"].dt.date == sel_date].sort_values("fetched_at")
#             if day.empty:
#                 st.info(f"No intraday data for {sel_date}. Try today's date or a recent date.")
#             else:
#                 sec("Power Output Throughout the Day (kW)")
#                 fig = px.line(day, x="fetched_at", y="power_kw", color="inverter_sn",
#                               color_discrete_sequence=PALETTE,
#                               labels={"fetched_at":"Time","power_kw":"Power (kW)",
#                                       "inverter_sn":"Inverter"})
#                 st.plotly_chart(line_chart(fig, 360), use_container_width=True)

#                 sec("Peak Power & Daily Generation per Inverter")
#                 sm = (day.groupby(["plant_name","inverter_sn","brand"])
#                       .agg(Peak_kW=("power_kw","max"), Daily_kWh=("today_kwh","max"))
#                       .reset_index()
#                       .rename(columns={"plant_name":"Plant","inverter_sn":"S/N","brand":"Brand"}))
#                 st.dataframe(sm, use_container_width=True, hide_index=True)

#     # ── MONTHLY ───────────────────────────────────────────────
#     elif rtype == "Monthly":
#         month_str = sel_date.strftime("%Y-%m")

#         with st.spinner(f"Fetching daily data for {sel_date.strftime('%B %Y')}…"):
#             if sel_plant == "All Plants":
#                 api_df = get_all_plants_daily(month_str)
#                 if not api_df.empty:
#                     daily = (api_df.groupby("date")["energy_kwh"]
#                              .sum().reset_index())
#                     daily.columns = ["Date","Daily Yield (kWh)"]
#                     income_df = api_df.groupby("date")["income"].sum().reset_index()
#                     income_df.columns = ["Date","Income (INR)"]
#                     daily = daily.merge(income_df, on="Date", how="left")
#                 else:
#                     daily = pd.DataFrame()
#             else:
#                 rows = get_daily_history(sel_plant, month_str)
#                 if rows:
#                     daily = pd.DataFrame(rows).rename(columns={
#                         "date":"Date","energy_kwh":"Daily Yield (kWh)","income":"Income (INR)"})
#                     daily["Date"] = pd.to_datetime(daily["Date"], errors="coerce")
#                 else:
#                     daily = pd.DataFrame()

#         if daily.empty or "Daily Yield (kWh)" not in daily.columns:
#             st.info(f"No data from Solis API for {sel_date.strftime('%B %Y')}.")
#         else:
#             daily = daily.dropna(subset=["Date"]).sort_values("Date")

#             # Combined bar + line chart matching Solis style
#             sec(f"Daily Generation — {sel_date.strftime('%B %Y')}")
#             fig = go.Figure()
#             # Bar: yield
#             fig.add_trace(go.Bar(
#                 x=daily["Date"], y=daily["Daily Yield (kWh)"],
#                 name="Yield (kWh)", marker_color="rgba(13,148,136,.25)",
#                 marker_line_width=0,
#             ))
#             # Line: yield trend
#             fig.add_trace(go.Scatter(
#                 x=daily["Date"], y=daily["Daily Yield (kWh)"],
#                 name="Yield", mode="lines+markers",
#                 line=dict(color="#0d9488", width=2.5),
#                 marker=dict(size=5, color="#0d9488"),
#             ))
#             # Line: revenue (right axis)
#             if "Income (INR)" in daily.columns:
#                 fig.add_trace(go.Scatter(
#                     x=daily["Date"], y=daily["Income (INR)"],
#                     name="Revenue (INR)", mode="lines+markers",
#                     line=dict(color="#f59e0b", width=2, dash="dot"),
#                     marker=dict(size=5, color="#f59e0b"),
#                     yaxis="y2",
#                 ))
#             fig.update_layout(
#                 plot_bgcolor="#fff", paper_bgcolor="#fff",
#                 font_family="Inter", font_color="#64748b",
#                 margin=dict(l=0,r=60,t=16,b=0), height=380,
#                 hovermode="x unified", bargap=0.25,
#                 legend=dict(bgcolor="rgba(0,0,0,0)", orientation="h",
#                             yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
#                 yaxis=dict(title="kWh", showgrid=True, gridcolor="#f1f5f9",
#                            zeroline=False, tickfont_size=11),
#                 yaxis2=dict(title="INR", overlaying="y", side="right",
#                             showgrid=False, zeroline=False, tickfont_size=11),
#             )
#             fig.update_xaxes(showgrid=False, zeroline=False, tickfont_size=11,
#                              tickformat="%d", dtick="D1")
#             st.plotly_chart(fig, use_container_width=True)

#             tot = daily["Daily Yield (kWh)"].sum()
#             m1,m2,m3 = st.columns(3)
#             m1.metric("Month Total", f"{tot:.1f} kWh")
#             m2.metric("Month Total (MWh)", f"{tot/1000:.3f} MWh")
#             m3.metric("Estimated Earning", earn(tot))

#     # ── ANNUAL ────────────────────────────────────────────────
#     elif rtype == "Annual":
#         year_str = str(sel_date.year)

#         with st.spinner(f"Fetching monthly data for {year_str}…"):
#             if sel_plant == "All Plants":
#                 api_df = get_all_plants_monthly(year_str)
#                 if not api_df.empty:
#                     monthly = (api_df.groupby("month")["energy_kwh"]
#                                .sum().reset_index())
#                     monthly.columns = ["Month","kWh"]
#                 else:
#                     monthly = pd.DataFrame()
#             else:
#                 rows = get_monthly_history(sel_plant, year_str)
#                 if rows:
#                     monthly = pd.DataFrame(rows).rename(columns={"month":"Month","energy_kwh":"kWh"})
#                 else:
#                     monthly = pd.DataFrame()

#         if monthly.empty or "kWh" not in monthly.columns:
#             st.info(f"No data from Solis API for {year_str}.")
#         else:
#             monthly = monthly[monthly["kWh"] > 0]

#             sec(f"Monthly Generation — {year_str}")
#             fig = go.Figure()
#             fig.add_trace(go.Bar(
#                 x=monthly["Month"], y=monthly["kWh"],
#                 name="Yield (kWh)", marker_color="rgba(245,158,11,.3)",
#                 marker_line_width=0,
#             ))
#             fig.add_trace(go.Scatter(
#                 x=monthly["Month"], y=monthly["kWh"],
#                 name="Trend", mode="lines+markers",
#                 line=dict(color="#f59e0b", width=2.5),
#                 marker=dict(size=7, color="#f59e0b"),
#             ))
#             fig.update_layout(
#                 plot_bgcolor="#fff", paper_bgcolor="#fff",
#                 font_family="Inter", font_color="#64748b",
#                 margin=dict(l=0,r=0,t=16,b=0), height=360,
#                 hovermode="x unified", bargap=0.3,
#                 legend=dict(bgcolor="rgba(0,0,0,0)"),
#                 yaxis=dict(showgrid=True, gridcolor="#f1f5f9",
#                            zeroline=False, tickfont_size=11),
#             )
#             fig.update_xaxes(showgrid=False, zeroline=False, tickfont_size=11)
#             st.plotly_chart(fig, use_container_width=True)

#             tot_yr = monthly["kWh"].sum()
#             m1,m2,m3 = st.columns(3)
#             m1.metric("Year Total", f"{tot_yr:.1f} kWh")
#             m2.metric("Year Total (MWh)", f"{tot_yr/1000:.3f} MWh")
#             m3.metric("Est. Annual Earning", earn(tot_yr))

#     # ── TOTAL ─────────────────────────────────────────────────
#     else:
#         sec("Total Yield per Plant (All-time)")
#         if not df.empty:
#             gt = (df.groupby(["plant_name","brand"])
#                   .agg(total_mwh=("total_kwh","sum"), daily_kwh=("today_kwh","sum"))
#                   .reset_index())

#             fig = go.Figure()
#             for i, row in gt.iterrows():
#                 fig.add_trace(go.Bar(
#                     x=[row["plant_name"]], y=[row["total_mwh"]],
#                     name=row["plant_name"],
#                     marker_color=PALETTE[i % len(PALETTE)],
#                     marker_line_width=0,
#                 ))
#             fig.update_layout(
#                 plot_bgcolor="#fff", paper_bgcolor="#fff",
#                 font_family="Inter", font_color="#64748b",
#                 margin=dict(l=0,r=0,t=16,b=0), height=340,
#                 showlegend=False, bargap=0.35,
#                 yaxis=dict(title="MWh", showgrid=True, gridcolor="#f1f5f9",
#                            zeroline=False, tickfont_size=11),
#             )
#             fig.update_xaxes(showgrid=False, zeroline=False, tickfont_size=11)
#             st.plotly_chart(fig, use_container_width=True)

#             gt_disp = gt.rename(columns={"plant_name":"Plant","brand":"Brand",
#                                           "total_mwh":"Total Yield (MWh)",
#                                           "daily_kwh":"Today (kWh)"})
#             st.dataframe(gt_disp, use_container_width=True, hide_index=True)


# # ══════════════════════════════════════════════════════════════
# #  SERVICE
# # ══════════════════════════════════════════════════════════════
# elif page == "Service":
#     st.markdown('<div class="page-hdr"><h1>Plant Management</h1>'
#                 '<p>All registered plants and operational details</p></div>',
#                 unsafe_allow_html=True)
#     if df.empty:
#         st.warning("⚠️ No data."); st.stop()

#     fc1,fc2 = st.columns(2)
#     with fc1: pf2 = st.selectbox("Plant", ["All"]+sorted(df["plant_name"].dropna().unique()), key="pm_p")
#     with fc2: bf2 = st.selectbox("Brand", ["All"]+sorted(df["brand"].dropna().unique()),      key="pm_b")

#     ps = (df.groupby(["plant_name","brand"])
#           .agg(power_kw=("power_kw","sum"), today_kwh=("today_kwh","sum"),
#                total_kwh=("total_kwh","sum"), inv_count=("inverter_sn","count"))
#           .reset_index())
#     if pf2!="All": ps=ps[ps["plant_name"]==pf2]
#     if bf2!="All": ps=ps[ps["brand"]==bf2]

#     st.markdown(
#         f'<div class="stat-row">'
#           f'<div class="stat-item"><div class="stat-val">{len(ps)}</div><div class="stat-lbl">Plants</div></div>'
#           f'<div class="stat-item"><div class="stat-val">{f(ps["power_kw"].sum(),2)} kW</div><div class="stat-lbl">Total Power</div></div>'
#           f'<div class="stat-item"><div class="stat-val">{f(ps["today_kwh"].sum(),1)} kWh</div><div class="stat-lbl">Daily Yield</div></div>'
#           f'<div class="stat-item"><div class="stat-val">{f(ps["total_kwh"].sum(),1)} MWh</div><div class="stat-lbl">Total Yield</div></div>'
#         f'</div>', unsafe_allow_html=True)

#     st.markdown('<div class="tbl">', unsafe_allow_html=True)
#     st.markdown('<div class="tbl-hdr tbl-plant">'
#                 '<div>Plant Name</div><div>Brand</div><div>Organisation</div>'
#                 '<div>Inverters</div><div>Power (kW)</div>'
#                 '<div>Daily Yield</div><div>Total Yield</div><div>Status</div>'
#                 '</div>', unsafe_allow_html=True)
#     for _, row in ps.iterrows():
#         pr   = df[df["plant_name"]==row["plant_name"]]
#         on   = int((pr["status"].str.lower()=="online").sum())
#         tot  = int(row["inv_count"])
#         pst  = "Online" if on==tot and tot>0 else ("Offline" if on==0 else "Warning")
#         dy   = float(row["today_kwh"] or 0)
#         dy_s = f"{dy/1000:.3f} MWh" if dy>=1000 else f"{dy:.1f} kWh"
#         ty   = float(row["total_kwh"] or 0)
#         ty_s = f"{ty/1000:.3f} GWh" if ty>=1000 else f"{ty:.3f} MWh"
#         st.markdown(
#             f'<div class="tbl-row tbl-plant">'
#               f'<div class="cell-link">{row["plant_name"]}</div>'
#               f'<div>{chip(row["brand"])}</div>'
#               f'<div>Fractal Energy</div>'
#               f'<div>{on}/{tot}</div>'
#               f'<div><b>{f(row["power_kw"],2)}</b> kW</div>'
#               f'<div>{dy_s}</div><div>{ty_s}</div>'
#               f'<div>{badge(pst)}</div>'
#             f'</div>', unsafe_allow_html=True)
#     st.markdown('</div>', unsafe_allow_html=True)


# # ══════════════════════════════════════════════════════════════
# #  SETTINGS
# # ══════════════════════════════════════════════════════════════
# elif page == "Settings":
#     st.markdown('<div class="page-hdr"><h1>Settings</h1>'
#                 '<p>Credentials, alerts and app configuration</p></div>',
#                 unsafe_allow_html=True)

#     from config import (SOLIS_API_KEY, GROWATT_USERNAME, SUNGROW_APP_KEY,
#                         EMAIL_USER, TO_EMAILS, RATE_PER_KWH)

#     st.markdown("#### 🔑 API Credentials")
#     for brand,ok,hint in [
#         ("Solis",   bool(SOLIS_API_KEY),
#          SOLIS_API_KEY[:10]+"…" if SOLIS_API_KEY else "Not configured"),
#         ("Growatt", bool(GROWATT_USERNAME),
#          GROWATT_USERNAME or "Set GROWATT_USERNAME in config.py"),
#         ("Sungrow", bool(SUNGROW_APP_KEY),
#          SUNGROW_APP_KEY[:10]+"…" if SUNGROW_APP_KEY else "Set SUNGROW_APP_KEY in config.py"),
#     ]:
#         c1,c2,c3 = st.columns([1,1,4])
#         c1.markdown(f"**{brand}**")
#         c2.markdown("✅ OK" if ok else "⚠️ Not set")
#         c3.markdown(f"`{hint}`")

#     st.divider()
#     st.markdown("#### 📧 Email Alerts")
#     st.markdown(f"**Sender:** `{EMAIL_USER}`")
#     st.markdown(f"**Recipients:** `{', '.join(TO_EMAILS)}`")
#     st.divider()
#     st.markdown("#### 💰 Tariff Rate")
#     st.info(f"Current rate: **₹{RATE_PER_KWH}/kWh** — edit `RATE_PER_KWH` in config.py")
#     st.divider()
#     st.markdown("#### 👤 Logged in as")
#     st.info(f"`{st.session_state.user}`")
#     st.divider()
#     st.markdown("#### 🗂 Project Structure")
#     st.code("""
# solar_dashboard/
# ├── app.py              ← streamlit run app.py
# ├── config.py           ← ✏️  credentials & settings
# ├── requirements.txt
# ├── data/solar_data.db  ← auto-created
# └── utils/
#     ├── solis_api.py    ├── growatt_api.py
#     ├── sungrow_api.py  ├── aggregator.py
#     ├── database.py     └── alerts.py
#     """, language="")




# # ============================================================
# #  app.py  —  Solar Dashboard  |  streamlit run app.py
# # ============================================================
# import streamlit as st
# from streamlit_autorefresh import st_autorefresh
# import pandas as pd
# import plotly.express as px
# import plotly.graph_objects as go
# from datetime import datetime, date, timedelta

# from config import REFRESH_INTERVAL_SECONDS, RATE_PER_KWH
# from utils.database import init_db, get_history, get_alert_log
# from utils.aggregator import fetch_all_brands, check_alerts

# # ─────────────────────────────────────────────────────────────
# st.set_page_config(page_title="Solar Dashboard · Fractal Energy",
#                    page_icon="☀️", layout="wide",
#                    initial_sidebar_state="expanded")

# # ══════════════════════════════════════════════════════════════
# #  GLOBAL CSS  —  Navy · Teal · Amber theme
# # ══════════════════════════════════════════════════════════════
# st.markdown("""
# <style>
# @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

# *,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}

# :root{
#   /* ── Palette ── */
#   --navy:      #0a1628;
#   --navy2:     #0f2044;
#   --navy3:     #1a2f5a;
#   --teal:      #0d9488;
#   --teal-l:    #ccfbf1;
#   --teal-d:    #0f766e;
#   --amber:     #f59e0b;
#   --amber-l:   #fef3c7;
#   --amber-d:   #d97706;
#   --orange:    #f97316;
#   --orange-l:  #ffedd5;
#   --red:       #ef4444;
#   --red-l:     #fee2e2;
#   --green:     #10b981;
#   --green-l:   #d1fae5;
#   --sky:       #38bdf8;
#   --sky-l:     #e0f2fe;

#   /* ── Surfaces ── */
#   --bg:        #f0f4f8;
#   --card:      #ffffff;
#   --border:    #e2e8f0;
#   --border2:   #cbd5e1;

#   /* ── Text ── */
#   --text:      #0f172a;
#   --text2:     #475569;
#   --text3:     #94a3b8;

#   /* ── Shadows ── */
#   --shadow:    0 1px 4px rgba(10,22,40,.06),0 4px 20px rgba(10,22,40,.05);
#   --shadow-lg: 0 8px 40px rgba(10,22,40,.12);
#   --shadow-teal:0 4px 20px rgba(13,148,136,.25);
# }

# /* ── Fonts ── */
# html,body,[data-testid="stAppViewContainer"]{
#   background:var(--bg)!important;
#   font-family:'Plus Jakarta Sans',sans-serif!important;
#   color:var(--text);
# }
# [data-testid="stHeader"]{background:transparent!important;display:none;}
# #MainMenu,footer{visibility:hidden;}
# [data-testid="stDecoration"]{display:none;}
# .block-container{padding:28px 32px!important;max-width:100%!important;}

# /* ══ SIDEBAR ══════════════════════════════════════════════ */
# [data-testid="stSidebar"]{
#   background:var(--navy)!important;
#   border-right:1px solid rgba(255,255,255,.06)!important;
# }
# [data-testid="stSidebar"]>div{padding-top:0!important;}
# section[data-testid="stSidebarContent"]{padding:0!important;}

# .sb-logo{
#   padding:24px 20px 18px;
#   border-bottom:1px solid rgba(255,255,255,.07);
#   margin-bottom:6px;
#   display:flex;align-items:center;gap:12px;
# }
# .sb-logo-icon{
#   width:42px;height:42px;background:linear-gradient(135deg,var(--teal),var(--teal-d));
#   border-radius:12px;display:flex;align-items:center;justify-content:center;
#   font-size:20px;flex-shrink:0;box-shadow:var(--shadow-teal);
# }
# .sb-logo-title{color:#fff;font-weight:800;font-size:15px;letter-spacing:-.3px;}
# .sb-logo-sub{color:#64748b;font-size:11px;margin-top:1px;}
# .sb-section{
#   padding:14px 20px 4px;
#   font-size:10px;font-weight:700;color:#334155;
#   text-transform:uppercase;letter-spacing:.12em;
# }
# .sb-time{
#   padding:14px 20px;font-size:11px;color:#475569;
#   border-top:1px solid rgba(255,255,255,.06);margin-top:6px;
#   font-family:'JetBrains Mono',monospace;
# }

# /* ══ LOGIN PAGE ═══════════════════════════════════════════ */
# .login-wrap{
#   min-height:100vh;display:flex;align-items:center;justify-content:center;
#   background:linear-gradient(135deg,var(--navy) 0%,var(--navy2) 50%,#0d2b4e 100%);
#   padding:20px;
# }
# .login-card{
#   background:rgba(255,255,255,.04);
#   border:1px solid rgba(255,255,255,.1);
#   border-radius:20px;padding:48px 44px;width:100%;max-width:420px;
#   backdrop-filter:blur(20px);
#   box-shadow:0 20px 60px rgba(0,0,0,.4);
# }
# .login-logo{
#   width:60px;height:60px;
#   background:linear-gradient(135deg,var(--teal),var(--teal-d));
#   border-radius:16px;display:flex;align-items:center;justify-content:center;
#   font-size:28px;margin:0 auto 20px;
#   box-shadow:0 8px 24px rgba(13,148,136,.4);
# }
# .login-title{
#   font-size:24px;font-weight:800;color:#fff;text-align:center;
#   letter-spacing:-.4px;margin-bottom:6px;
# }
# .login-sub{font-size:13px;color:#64748b;text-align:center;margin-bottom:32px;}
# .login-label{font-size:13px;font-weight:600;color:#94a3b8;margin-bottom:6px;}
# .login-error{
#   background:rgba(239,68,68,.12);border:1px solid rgba(239,68,68,.3);
#   border-radius:8px;padding:10px 14px;font-size:13px;color:#fca5a5;
#   margin-bottom:16px;text-align:center;
# }

# /* ══ PAGE HEADER ══════════════════════════════════════════ */
# .page-hdr{margin-bottom:24px;}
# .page-hdr h1{
#   font-size:24px;font-weight:800;color:var(--text);
#   letter-spacing:-.5px;line-height:1.2;
# }
# .page-hdr p{font-size:13px;color:var(--text3);margin-top:4px;}

# /* ══ KPI CARDS ════════════════════════════════════════════ */
# .kpi-card{
#   background:var(--card);border-radius:16px;padding:24px 22px;
#   border:1px solid var(--border);box-shadow:var(--shadow);
#   display:flex;gap:16px;align-items:flex-start;
#   transition:transform .15s,box-shadow .15s;
#   position:relative;overflow:hidden;
# }
# .kpi-card::after{
#   content:'';position:absolute;top:0;left:0;right:0;height:3px;
#   background:linear-gradient(90deg,var(--teal),var(--sky));
#   border-radius:16px 16px 0 0;
# }
# .kpi-card.amber::after{background:linear-gradient(90deg,var(--amber),var(--orange));}
# .kpi-card.green::after{background:linear-gradient(90deg,var(--green),var(--teal));}
# .kpi-card.navy::after{background:linear-gradient(90deg,var(--navy3),var(--sky));}
# .kpi-card:hover{transform:translateY(-2px);box-shadow:var(--shadow-lg);}

# .kpi-icon{
#   width:50px;height:50px;border-radius:13px;flex-shrink:0;
#   display:flex;align-items:center;justify-content:center;font-size:22px;
# }
# .kpi-icon.teal  {background:var(--teal-l);color:var(--teal);}
# .kpi-icon.amber {background:var(--amber-l);color:var(--amber-d);}
# .kpi-icon.green {background:var(--green-l);color:var(--green);}
# .kpi-icon.navy  {background:var(--sky-l);color:#0284c7;}

# .kpi-label{
#   font-size:11px;color:var(--text3);font-weight:700;
#   text-transform:uppercase;letter-spacing:.1em;margin-bottom:6px;
# }
# .kpi-value{
#   font-size:28px;font-weight:800;color:var(--text);
#   line-height:1;letter-spacing:-.5px;
# }
# .kpi-unit{font-size:14px;font-weight:600;color:var(--text2);margin-left:3px;}
# .kpi-meta{font-size:12px;color:var(--text3);margin-top:8px;line-height:1.4;}
# .kpi-meta b{color:var(--teal);font-weight:600;}

# /* ══ SECTION HEADER ═══════════════════════════════════════ */
# .sec-hdr{
#   font-size:13px;font-weight:700;color:var(--text);
#   display:flex;align-items:center;gap:8px;
#   margin-bottom:14px;padding-bottom:10px;
#   border-bottom:2px solid var(--border);
# }
# .sec-hdr-dot{
#   width:8px;height:8px;border-radius:50%;
#   background:linear-gradient(135deg,var(--teal),var(--sky));
#   flex-shrink:0;
# }

# /* ══ CARD WRAPPER ═════════════════════════════════════════ */
# .card{
#   background:var(--card);border-radius:16px;padding:22px;
#   border:1px solid var(--border);box-shadow:var(--shadow);margin-bottom:16px;
# }

# /* ══ INVERTER CARD ════════════════════════════════════════ */
# .inv-card{
#   background:var(--card);border-radius:16px;padding:22px;
#   border:1px solid var(--border);box-shadow:var(--shadow);
#   margin-bottom:14px;transition:border-color .15s,box-shadow .15s;
# }
# .inv-card:hover{border-color:var(--primary);box-shadow:var(--shadow-teal);}
# .inv-card.alert-card{border-left:3px solid var(--red);}
# .inv-header{
#   display:flex;justify-content:space-between;align-items:flex-start;
#   margin-bottom:18px;padding-bottom:14px;
#   border-bottom:1px solid var(--border);
# }
# .inv-name{font-size:15px;font-weight:700;color:var(--text);letter-spacing:-.3px;}
# .inv-meta{font-size:11px;color:var(--text3);margin-top:3px;font-family:'JetBrains Mono',monospace;}
# .inv-params{display:grid;grid-template-columns:repeat(6,1fr);gap:16px;}
# .param-label{
#   font-size:10px;color:var(--text3);text-transform:uppercase;
#   letter-spacing:.08em;font-weight:600;margin-bottom:4px;
# }
# .param-val{font-size:18px;font-weight:700;color:var(--text);letter-spacing:-.3px;}
# .param-unit{font-size:11px;color:var(--text3);margin-left:2px;}
# .inv-footer{margin-top:14px;font-size:11px;color:var(--text3);font-family:'JetBrains Mono',monospace;}

# /* ══ TABLES ═══════════════════════════════════════════════ */
# .tbl{
#   background:var(--card);border-radius:16px;
#   border:1px solid var(--border);overflow:hidden;box-shadow:var(--shadow);
# }
# .tbl-hdr,.tbl-row{
#   display:grid;padding:0 20px;align-items:center;gap:10px;
# }
# .tbl-hdr{
#   background:linear-gradient(90deg,#f8fafc,#f1f5f9);
#   border-bottom:2px solid var(--border);
#   font-size:10px;font-weight:700;color:var(--text3);
#   text-transform:uppercase;letter-spacing:.1em;height:44px;
# }
# .tbl-row{
#   min-height:54px;border-bottom:1px solid var(--border);
#   font-size:13px;transition:background .1s;
# }
# .tbl-row:last-child{border-bottom:none;}
# .tbl-row:hover{background:#f8fafc;}
# .tbl-plant{grid-template-columns:2fr 1fr 1.1fr 1fr 1fr 1.1fr 1.3fr 1fr;}
# .tbl-alarm{grid-template-columns:1fr 1fr 1fr 1.5fr 1.4fr 2.2fr 1.2fr;}
# .cell-link{color:var(--primary);font-weight:700;cursor:pointer;font-size:13px;}

# /* ══ BADGES ═══════════════════════════════════════════════ */
# .badge{
#   display:inline-flex;align-items:center;gap:5px;
#   font-size:11px;font-weight:700;padding:4px 10px;
#   border-radius:20px;letter-spacing:.02em;
# }
# .badge::before{content:'';width:6px;height:6px;border-radius:50%;}
# .b-online {background:var(--green-l);color:#065f46;}
# .b-online::before{background:var(--green);}
# .b-offline{background:var(--red-l);color:#991b1b;}
# .b-offline::before{background:var(--red);}
# .b-warning{background:var(--amber-l);color:#92400e;}
# .b-warning::before{background:var(--amber);}
# .b-unknown{background:#f1f5f9;color:#64748b;}
# .b-unknown::before{background:#94a3b8;}
# .b-active {background:var(--red-l);color:#991b1b;}
# .b-active::before{background:var(--red);}
# .b-resolved{background:var(--green-l);color:#065f46;}
# .b-resolved::before{background:var(--green);}
# .b-critical{background:var(--red-l);color:#991b1b;font-weight:800;}
# .b-critical::before{background:var(--red);}

# /* ══ CHIPS ════════════════════════════════════════════════ */
# .chip{
#   display:inline-block;font-size:10px;font-weight:800;
#   padding:3px 9px;border-radius:6px;
#   letter-spacing:.1em;text-transform:uppercase;
# }
# .chip-solis  {background:#dbeafe;color:#1e40af;}
# .chip-growatt{background:#d1fae5;color:#065f46;}
# .chip-sungrow{background:#ffedd5;color:#c2410c;}

# /* ══ ALERT STRIP ══════════════════════════════════════════ */
# .alert-strip{
#   background:linear-gradient(135deg,#fff1f2,#ffe4e6);
#   border:1px solid #fecdd3;border-left:4px solid var(--red);
#   border-radius:12px;padding:16px 18px;margin-bottom:12px;
#   display:flex;gap:14px;align-items:flex-start;
# }
# .alert-strip-ico{font-size:20px;flex-shrink:0;}
# .alert-strip-ttl{font-size:14px;font-weight:700;color:var(--red);}
# .alert-strip-msg{font-size:12px;color:#7f1d1d;margin-top:3px;}

# /* ══ STAT ROW ═════════════════════════════════════════════ */
# .stat-row{
#   background:var(--card);border-radius:14px;padding:16px 24px;
#   border:1px solid var(--border);display:flex;gap:32px;
#   margin-bottom:20px;align-items:center;flex-wrap:wrap;
#   box-shadow:var(--shadow);
# }
# .stat-item{text-align:center;}
# .stat-val{font-size:20px;font-weight:800;color:var(--text);letter-spacing:-.3px;}
# .stat-lbl{font-size:10px;color:var(--text3);margin-top:2px;font-weight:600;text-transform:uppercase;letter-spacing:.08em;}

# /* ══ STREAMLIT OVERRIDES ══════════════════════════════════ */
# .stButton>button{
#   background:linear-gradient(135deg,var(--teal),var(--teal-d))!important;
#   color:#fff!important;border:none!important;border-radius:10px!important;
#   font-family:'Plus Jakarta Sans',sans-serif!important;
#   font-weight:700!important;font-size:13px!important;
#   padding:10px 24px!important;letter-spacing:.01em!important;
#   box-shadow:0 4px 12px rgba(13,148,136,.3)!important;
#   transition:all .15s!important;
# }
# .stButton>button:hover{transform:translateY(-1px)!important;box-shadow:0 6px 20px rgba(13,148,136,.4)!important;}
# div[data-testid="stSelectbox"]>label,
# div[data-testid="stTextInput"]>label{
#   font-size:12px!important;font-weight:700!important;
#   color:var(--text2)!important;text-transform:uppercase!important;letter-spacing:.06em!important;
# }
# [data-testid="stRadio"]>label{font-size:13px!important;font-weight:600!important;}
# .stRadio>div{gap:4px!important;}
# .stAlert{border-radius:12px!important;}
# div[data-testid="stTextInput"] input{
#   border-radius:10px!important;border-color:var(--border2)!important;
#   font-size:14px!important;font-family:'Plus Jakarta Sans',sans-serif!important;
# }
# div[data-testid="stSelectbox"]>div>div{
#   border-radius:10px!important;border-color:var(--border2)!important;
#   font-size:13px!important;
# }

# /* ══ LOGIN STREAMLIT INPUT OVERRIDES ═══════════════════════ */
# .login-page [data-testid="stTextInput"] input{
#   background:rgba(255,255,255,.08)!important;
#   border:1px solid rgba(255,255,255,.15)!important;
#   border-radius:10px!important;color:#fff!important;
#   font-size:14px!important;padding:12px 14px!important;
# }
# .login-page .stButton>button{
#   width:100%!important;padding:14px!important;font-size:15px!important;
# }

# /* ══ DIVIDER ══════════════════════════════════════════════ */
# .divider{height:1px;background:var(--border);margin:20px 0;}

# /* ══ METRIC OVERRIDES ═════════════════════════════════════ */
# [data-testid="stMetric"]{
#   background:var(--card);border-radius:12px;padding:16px 18px;
#   border:1px solid var(--border);box-shadow:var(--shadow);
# }
# [data-testid="stMetricLabel"]{font-size:11px!important;font-weight:700!important;color:var(--text3)!important;text-transform:uppercase!important;letter-spacing:.08em!important;}
# [data-testid="stMetricValue"]{font-size:24px!important;font-weight:800!important;color:var(--text)!important;letter-spacing:-.4px!important;}
# </style>
# """, unsafe_allow_html=True)

# # ══════════════════════════════════════════════════════════════
# #  INIT
# # ══════════════════════════════════════════════════════════════
# init_db()

# # ══════════════════════════════════════════════════════════════
# #  SESSION STATE
# # ══════════════════════════════════════════════════════════════
# USERS = {
#     "admin@fractalenergy.in":    "Fractal@2024",
#     "abhijit.r@fractalenergy.in":"Welcome#9",
# }

# for key, default in [
#     ("logged_in",      False),
#     ("user",           ""),
#     ("plant_selected", False),
#     ("sel_brands",     ["Solis"]),
#     ("sel_plants",     []),        # list of selected plant names
# ]:
#     if key not in st.session_state:
#         st.session_state[key] = default

# # ══════════════════════════════════════════════════════════════
# #  STEP 1 — LOGIN
# # ══════════════════════════════════════════════════════════════
# DARK_PAGE_CSS = """<style>
# [data-testid="stSidebar"]{display:none!important;}
# .block-container{padding:0!important;max-width:100%!important;}
# </style>"""

# if not st.session_state.logged_in:
#     st.markdown(DARK_PAGE_CSS, unsafe_allow_html=True)
#     st.markdown("""
#     <div style="min-height:100vh;display:flex;align-items:center;justify-content:center;
#     background:linear-gradient(135deg,#0a1628 0%,#0f2044 55%,#0d2b4e 100%);padding:20px;">
#       <div style="width:100%;max-width:420px;">
#         <div style="text-align:center;margin-bottom:32px;">
#           <div style="width:68px;height:68px;background:linear-gradient(135deg,#0d9488,#0f766e);
#             border-radius:18px;display:flex;align-items:center;justify-content:center;
#             font-size:32px;margin:0 auto 16px;box-shadow:0 8px 24px rgba(13,148,136,.4);">☀️</div>
#           <div style="font-size:26px;font-weight:800;color:#fff;letter-spacing:-.5px;">Solar Dashboard</div>
#           <div style="font-size:13px;color:#64748b;margin-top:6px;">Fractal Energy · Monitoring Platform</div>
#         </div>
#         <div style="background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.1);
#           border-radius:20px;padding:36px 32px;backdrop-filter:blur(20px);
#           box-shadow:0 20px 60px rgba(0,0,0,.4);">
#     """, unsafe_allow_html=True)
#     email    = st.text_input("Email Address", placeholder="your@email.com")
#     password = st.text_input("Password",      placeholder="••••••••", type="password")
#     if st.button("Sign In →", use_container_width=True):
#         if email in USERS and USERS[email] == password:
#             st.session_state.logged_in = True
#             st.session_state.user      = email
#             st.rerun()
#         else:
#             st.error("Invalid email or password.")
#     st.markdown("""<div style="text-align:center;margin-top:20px;font-size:12px;color:#475569;">
#       Secured by Fractal Energy · v2.0</div></div></div></div>""",
#     unsafe_allow_html=True)
#     st.stop()

# # ══════════════════════════════════════════════════════════════
# #  STEP 2 — PLANT SELECTOR  (shown once after login)
# # ══════════════════════════════════════════════════════════════
# if not st.session_state.plant_selected:
#     st.markdown(DARK_PAGE_CSS, unsafe_allow_html=True)

#     # Fetch available plants from all brands
#     @st.cache_data(ttl=600)
#     def _fetch_available_plants():
#         available = []
#         try:
#             from utils.solis_api import get_plants as _sp
#             for p in _sp():
#                 available.append({
#                     "brand": "Solis",
#                     "name":  p.get("stationName",""),
#                     "id":    p.get("id",""),
#                     "capacity": str(p.get("capacity","")) + " kWp",
#                 })
#         except Exception as e:
#             print(f"Plant selector Solis error: {e}")
#         try:
#             from utils.growatt_api import _get_plants, login as glogin
#             glogin()
#             for p in _get_plants():
#                 available.append({
#                     "brand": "Growatt",
#                     "name":  p.get("plantNameEncryption") or p.get("plantName",""),
#                     "id":    str(p.get("pId") or p.get("plantId","")),
#                     "capacity": str(p.get("nominalPower","")) + " W",
#                 })
#         except Exception as e:
#             print(f"Plant selector Growatt error: {e}")
#         return available

#     with st.spinner("Loading available plants…"):
#         available_plants = _fetch_available_plants()

#     # Group by brand
#     solis_plants   = [p for p in available_plants if p["brand"] == "Solis"]
#     growatt_plants = [p for p in available_plants if p["brand"] == "Growatt"]

#     # Plant selector UI
#     st.markdown(f"""
#     <div style="min-height:100vh;background:linear-gradient(135deg,#0a1628,#0f2044);
#     display:flex;align-items:center;justify-content:center;padding:32px 20px;">
#       <div style="width:100%;max-width:860px;">
#         <div style="text-align:center;margin-bottom:36px;">
#           <div style="width:60px;height:60px;background:linear-gradient(135deg,#0d9488,#0f766e);
#             border-radius:16px;display:flex;align-items:center;justify-content:center;
#             font-size:28px;margin:0 auto 14px;">☀</div>
#           <div style="font-size:24px;font-weight:800;color:#fff;letter-spacing:-.4px;">
#             Select Plants to Monitor</div>
#           <div style="font-size:13px;color:#64748b;margin-top:6px;">
#             Welcome, {st.session_state.user} · Choose which plants to include in your dashboard</div>
#         </div>
#       </div>
#     </div>
#     """, unsafe_allow_html=True)

#     # Brand tabs
#     brand_tabs = []
#     if solis_plants:   brand_tabs.append("☀️ Solis")
#     if growatt_plants: brand_tabs.append("⚡ Growatt")
#     if not brand_tabs:
#         st.warning("No plants found. Check credentials in config.py")
#         if st.button("Continue anyway"):
#             st.session_state.plant_selected = True
#             st.session_state.sel_brands     = ["Solis"]
#             st.session_state.sel_plants     = []
#             st.rerun()
#         st.stop()

#     sel_plant_names = []

#     if len(brand_tabs) > 1:
#         tabs = st.tabs(brand_tabs)
#     else:
#         tabs = [st.container()]

#     tab_idx = 0
#     if solis_plants:
#         with tabs[tab_idx]:
#             st.markdown("#### Solis Plants")
#             st.caption("Select all Solis plants you want to monitor:")
#             all_solis = st.checkbox("Select All Solis Plants", value=True, key="all_solis")
#             for p in solis_plants:
#                 checked = st.checkbox(
#                     f"🌱 {p['name']}  —  {p['capacity']}",
#                     value=all_solis, key=f"sp_{p['id']}"
#                 )
#                 if checked:
#                     sel_plant_names.append(p["name"])
#         tab_idx += 1

#     if growatt_plants:
#         with tabs[tab_idx]:
#             st.markdown("#### Growatt Plants")
#             st.caption("Select all Growatt plants you want to monitor:")
#             all_growatt = st.checkbox("Select All Growatt Plants", value=True, key="all_growatt")
#             for p in growatt_plants:
#                 checked = st.checkbox(
#                     f"⚡ {p['name']}  —  {p['capacity']}",
#                     value=all_growatt, key=f"gp_{p['id']}"
#                 )
#                 if checked:
#                     sel_plant_names.append(p["name"])

#     st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
#     col_a, col_b = st.columns([3,1])
#     with col_b:
#         if st.button("Continue to Dashboard →", use_container_width=True):
#             # Determine which brands are selected
#             active_brands = []
#             if any(p["name"] in sel_plant_names for p in solis_plants):
#                 active_brands.append("Solis")
#             if any(p["name"] in sel_plant_names for p in growatt_plants):
#                 active_brands.append("Growatt")
#             st.session_state.sel_brands     = active_brands or ["Solis"]
#             st.session_state.sel_plants     = sel_plant_names
#             st.session_state.plant_selected = True
#             st.cache_data.clear()
#             st.rerun()
#     with col_a:
#         st.caption(f"{len(sel_plant_names)} plant(s) selected")
#     st.stop()

# # ══════════════════════════════════════════════════════════════
# #  AUTHENTICATED APP
# # ══════════════════════════════════════════════════════════════
# st_autorefresh(interval=REFRESH_INTERVAL_SECONDS * 1000, key="solar_ar")

# # ── Helpers ──────────────────────────────────────────────────
# def f(v, d=1, na="—"):
#     try:    return f"{float(v):.{d}f}"
#     except: return na

# def badge(s, kind=None):
#     s  = (s or "").strip()
#     sl = s.lower()
#     if kind == "level":
#         cls = "b-critical" if sl == "critical" else "b-warning"
#     elif kind == "status_alarm":
#         cls = "b-active" if sl == "active" else "b-resolved"
#     else:
#         if sl == "online":              cls = "b-online"
#         elif sl in ("offline","fault"): cls = "b-offline"
#         else:                           cls = "b-unknown"
#     return f'<span class="badge {cls}">{s}</span>'

# def chip(b):
#     return f'<span class="chip chip-{(b or "").lower()}">{b}</span>'

# def earn(kwh):
#     v = float(kwh or 0) * RATE_PER_KWH
#     if v >= 1_000_000: return f"₹{v/1_000_000:.3f}M"
#     if v >= 1_000:     return f"₹{v/1_000:.3f}K"
#     return f"₹{v:.2f}"

# def chart_style(fig, h=300):
#     fig.update_layout(
#         plot_bgcolor="#fff", paper_bgcolor="#fff",
#         font_color="#64748b", font_family="Inter",
#         margin=dict(l=0,r=0,t=16,b=0), height=h,
#         legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=12, color="#64748b")),
#         bargap=0.28,
#     )
#     fig.update_traces(marker_line_width=0)
#     fig.update_xaxes(showgrid=False, zeroline=False, tickfont_size=11,
#                      tickfont_color="#94a3b8", linecolor="#e2e8f0")
#     fig.update_yaxes(showgrid=True, gridcolor="#f1f5f9", zeroline=False,
#                      tickfont_size=11, tickfont_color="#94a3b8")
#     return fig

# PALETTE = ["#0d9488","#f59e0b","#3b82f6","#f97316","#10b981","#8b5cf6","#06b6d4","#ec4899"]
# BRAND_COLORS = {"Solis":"#3b82f6","Growatt":"#10b981","Sungrow":"#f97316"}

# def sec(title, icon=""):
#     st.markdown(f'<div class="sec-hdr"><div class="sec-hdr-dot"></div>{icon} {title}</div>',
#                 unsafe_allow_html=True)

# # ── Sidebar ──────────────────────────────────────────────────
# with st.sidebar:
#     st.markdown(f"""
#     <div class="sb-logo">
#       <div class="sb-logo-icon">☀</div>
#       <div>
#         <div class="sb-logo-title">Solar Dashboard</div>
#         <div class="sb-logo-sub">Fractal Energy</div>
#       </div>
#     </div>""", unsafe_allow_html=True)

#     page = st.radio("", ["📊  Overview","🔧  O&M","📈  Report","🗺  Service","⚙️  Settings"],
#                     label_visibility="collapsed")
#     page = page.split("  ",1)[1].strip()

#     st.markdown('<div class="sb-section">Active Plants</div>', unsafe_allow_html=True)
#     sel_brands = st.session_state.get("sel_brands", ["Solis"])
#     sel_plants = st.session_state.get("sel_plants", [])
#     for b in sel_brands:
#         st.markdown(f'<div style="color:#94a3b8;font-size:12px;padding:4px 20px;">'
#                     f'{"☀️" if b=="Solis" else "⚡" if b=="Growatt" else "🔆"} {b}</div>',
#                     unsafe_allow_html=True)
#     if st.button("🔀  Change Plants"):
#         st.session_state.plant_selected = False
#         st.cache_data.clear()
#         st.rerun()

#     st.markdown('<div style="height:6px"></div>', unsafe_allow_html=True)
#     if st.button("🔄  Refresh Now"):
#         st.cache_data.clear(); st.rerun()

#     show_debug = st.checkbox("🔍  Debug", value=False)

#     # Logout
#     st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)
#     if st.button("🚪  Sign Out"):
#         st.session_state.logged_in = False
#         st.rerun()

#     st.markdown(f"""
#     <div class="sb-time">
#       ⏱ {datetime.now().strftime('%d %b %Y')}<br>
#       <b style="color:#94a3b8;">{datetime.now().strftime('%H:%M:%S')}</b><br>
#       <span style="color:#334155;">Auto-refresh {REFRESH_INTERVAL_SECONDS//60} min</span>
#     </div>""", unsafe_allow_html=True)

# # ── Fetch data ────────────────────────────────────────────────
# sel_plants = st.session_state.get("sel_plants", [])

# @st.cache_data(ttl=REFRESH_INTERVAL_SECONDS)
# def load(brands, plants):
#     result = fetch_all_brands(list(brands))
#     if not result:
#         raise RuntimeError("empty")
#     # Filter to selected plants if specified
#     if plants:
#         result = [r for r in result if r.get("plant_name") in plants]
#     return result

# with st.spinner("Fetching live data…"):
#     try:
#         records = load(tuple(sel_brands), tuple(sel_plants))
#     except Exception:
#         records = fetch_all_brands(list(sel_brands))
#         if sel_plants:
#             records = [r for r in records if r.get("plant_name") in sel_plants]
#         if not records:
#             st.cache_data.clear()

# alerts = check_alerts(records, st.session_state)

# df = pd.DataFrame()
# if records:
#     df = pd.DataFrame(records)
#     for c in ["power_kw","today_kwh","total_kwh","temperature","voltage","current_a"]:
#         if c in df.columns:
#             df[c] = pd.to_numeric(df[c], errors="coerce")
#     if "status" in df.columns:
#         df["status"] = df["status"].astype(str).str.strip()

# # ── Debug ─────────────────────────────────────────────────────
# if show_debug and not df.empty:
#     st.markdown("### 🔍 Debug: Raw API Data")
#     st.dataframe(df, use_container_width=True)
#     try:
#         from utils.solis_api import fetch_summary as _fsum, _raw_plants_cache
#         summ = _fsum()
#         st.write("**fetch_summary():**", summ)
#     except Exception as ex:
#         st.error(f"Debug error: {ex}")
#     st.divider()


# # ══════════════════════════════════════════════════════════════
# #  OVERVIEW
# # ══════════════════════════════════════════════════════════════
# if page == "Overview":
#     st.markdown('<div class="page-hdr"><h1>Plant Overview</h1>'
#                 '<p>Real-time performance across all plants</p></div>',
#                 unsafe_allow_html=True)

#     if df.empty:
#         st.warning("⚠️ No data. Check credentials in config.py and click Refresh.")
#         st.stop()

#     # ── KPI values ────────────────────────────────────────────
#     total_power = float(df["power_kw"].sum())
#     daily_kwh   = float(df["today_kwh"].sum())
#     total_mwh   = float(df["total_kwh"].sum())
#     monthly_mwh = 0.0

#     try:
#         if "Solis" in sel_brands:
#             from utils.solis_api import fetch_summary as _fs
#             summ = _fs()
#             if summ.get("power_kw",    0) > 0: total_power = float(summ["power_kw"])
#             # daily_kwh: use df sum (inverterList etoday) — most accurate per-inverter value
#             # fetch_summary dayEnergy can be partial; df["today_kwh"].sum() is always correct
#             if summ.get("monthly_mwh", 0) > 0: monthly_mwh = float(summ["monthly_mwh"])
#             if summ.get("total_mwh",   0) > 0: total_mwh   = float(summ["total_mwh"])
#     except Exception: pass

#     # Always use inverter-level sum for daily yield — it's the most accurate
#     # (confirmed: df sum = 1697.5 kWh matches Solis, API dayEnergy can lag)
#     daily_kwh = float(df["today_kwh"].sum())

#     if monthly_mwh == 0:
#         hist = get_history(hours=720)
#         monthly_kwh_db = daily_kwh
#         if not hist.empty and "today_kwh" in hist.columns:
#             hist["fetched_at"] = pd.to_datetime(hist["fetched_at"])
#             hist["today_kwh"]  = pd.to_numeric(hist["today_kwh"], errors="coerce")
#             m = hist[hist["fetched_at"].dt.month == datetime.now().month]
#             if not m.empty:
#                 v = float(m.groupby([m["fetched_at"].dt.date,"inverter_sn"])["today_kwh"].max().sum())
#                 monthly_kwh_db = max(v, daily_kwh)
#         monthly_mwh = monthly_kwh_db / 1000
#     monthly_kwh = monthly_mwh * 1000

#     # Display units
#     daily_val,daily_unit = (f(daily_kwh/1000,3),"MWh") if daily_kwh>=1000 else (f(daily_kwh,1),"kWh")
#     mo_val,mo_unit       = f(monthly_mwh,3), "MWh"
#     if total_mwh >= 1000:
#         tot_val,tot_unit,tot_earn = f(total_mwh/1000,3),"GWh",total_mwh*1000
#     else:
#         tot_val,tot_unit,tot_earn = f(total_mwh,3),"MWh",total_mwh*1000

#     n_on  = int((df["status"].str.lower()=="online").sum())
#     n_tot = len(df)

#     # ── 4 KPI cards ──────────────────────────────────────────
#     c1,c2,c3,c4 = st.columns(4)
#     kpis = [
#         (c1,"teal","teal","⚡","Power",f(total_power,2),"kW",
#          f"Inverters: <b>{n_on}/{n_tot} online</b>"),
#         (c2,"amber","amber","🔋","Daily Yield",daily_val,daily_unit,
#          f"Earning today: <b>{earn(daily_kwh)}</b>"),
#         (c3,"green","green","📅","Monthly Yield",mo_val,mo_unit,
#          f"Earning this month: <b>{earn(monthly_kwh)}</b>"),
#         (c4,"navy","navy","📊","Total Yield",tot_val,tot_unit,
#          f"Total earning: <b>{earn(tot_earn)}</b>"),
#     ]
#     for col,card_cls,ico_cls,ico,lbl,val,unit,meta in kpis:
#         with col:
#             st.markdown(f"""
#             <div class="kpi-card {card_cls}">
#               <div class="kpi-icon {ico_cls}">{ico}</div>
#               <div>
#                 <div class="kpi-label">{lbl}</div>
#                 <div class="kpi-value">{val}<span class="kpi-unit"> {unit}</span></div>
#                 <div class="kpi-meta">{meta}</div>
#               </div>
#             </div>""", unsafe_allow_html=True)

#     st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)

#     # ── Alert strips ─────────────────────────────────────────
#     if alerts:
#         for a in alerts[:3]:
#             st.markdown(f"""
#             <div class="alert-strip">
#               <div class="alert-strip-ico">🚨</div>
#               <div>
#                 <div class="alert-strip-ttl">{a['plant_name']} — {a.get('inverter_sn','')}</div>
#                 <div class="alert-strip-msg">{a['issue']}</div>
#               </div>
#             </div>""", unsafe_allow_html=True)

#     # ── Charts ───────────────────────────────────────────────
#     ch1, ch2 = st.columns([3, 2])

#     with ch1:
#         sec("Power by Plant (kW)")
#         pdf = df.groupby(["plant_name","brand"])["power_kw"].sum().reset_index()
#         fig = px.bar(pdf, x="plant_name", y="power_kw", color="brand",
#                      color_discrete_map=BRAND_COLORS,
#                      labels={"power_kw":"Power (kW)","plant_name":"","brand":"Brand"})
#         fig.update_traces(marker_cornerradius=4)
#         st.plotly_chart(chart_style(fig, 290), use_container_width=True)

#     with ch2:
#         sec("Daily Yield Share")
#         pief = df.groupby("plant_name")["today_kwh"].sum().reset_index()
#         fig2 = go.Figure(go.Pie(
#             labels=pief["plant_name"],
#             values=pief["today_kwh"],
#             hole=0.52,
#             marker=dict(colors=PALETTE, line=dict(color="#fff", width=2)),
#             textposition="outside",
#             textinfo="label+percent",
#             textfont=dict(size=11, family="Plus Jakarta Sans"),
#             pull=[0.04]*len(pief),
#         ))
#         fig2.update_layout(
#             plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
#             font_family="Inter", font_color="#64748b",
#             margin=dict(l=60, r=60, t=20, b=20), height=290,
#             showlegend=False,
#             annotations=[dict(text=f"<b>{f(pief['today_kwh'].sum(),1)}</b><br>kWh",
#                               font=dict(size=14,color="#0f172a",family="Plus Jakarta Sans"),
#                               showarrow=False)]
#         )
#         st.plotly_chart(fig2, use_container_width=True)

#     # ── Plant table ──────────────────────────────────────────
#     sec("Plant List")
#     ps = (df.groupby(["plant_name","brand"])
#           .agg(power_kw=("power_kw","sum"), today_kwh=("today_kwh","sum"),
#                total_kwh=("total_kwh","sum"), inv_count=("inverter_sn","count"))
#           .reset_index())

#     st.markdown('<div class="tbl">', unsafe_allow_html=True)
#     st.markdown(
#         '<div class="tbl-hdr tbl-plant">'
#         '<div>Plant Name</div><div>Brand</div><div>Inverters</div>'
#         '<div>Power (kW)</div><div>Daily Yield</div>'
#         '<div>Total Yield</div><div>Earning Today</div><div>Status</div>'
#         '</div>', unsafe_allow_html=True)

#     for _, row in ps.iterrows():
#         pr   = df[df["plant_name"]==row["plant_name"]]
#         on   = int((pr["status"].str.lower()=="online").sum())
#         tot  = int(row["inv_count"])
#         pst  = "Online" if on==tot and tot>0 else ("Offline" if on==0 else "Warning")
#         dy   = float(row["today_kwh"] or 0)
#         dy_s = f"{dy/1000:.3f} MWh" if dy>=1000 else f"{dy:.1f} kWh"
#         ty   = float(row["total_kwh"] or 0)
#         ty_s = f"{ty/1000:.3f} GWh" if ty>=1000 else f"{ty:.3f} MWh"
#         st.markdown(
#             f'<div class="tbl-row tbl-plant">'
#               f'<div class="cell-link">{row["plant_name"]}</div>'
#               f'<div>{chip(row["brand"])}</div>'
#               f'<div>{on}/{tot}</div>'
#               f'<div><b>{f(row["power_kw"],2)}</b> kW</div>'
#               f'<div>{dy_s}</div><div>{ty_s}</div>'
#               f'<div>{earn(dy)}</div><div>{badge(pst)}</div>'
#             f'</div>', unsafe_allow_html=True)
#     st.markdown('</div>', unsafe_allow_html=True)


# # ══════════════════════════════════════════════════════════════
# #  O&M
# # ══════════════════════════════════════════════════════════════
# elif page == "O&M":
#     sub = st.radio("", ["🔔  Alarm Information","⚡  Device Overview"],
#                    horizontal=True, label_visibility="collapsed")
#     sub = sub.split("  ",1)[1].strip()
#     st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

#     alarm_log = get_alert_log(200)
#     all_alarms = []
#     for a in alerts:
#         all_alarms.append({"device_type":"Inverter","level":"Critical","status":"Active",
#             "plant_name":a.get("plant_name","—"),"sn":a.get("inverter_sn","—"),
#             "content":a.get("issue","—"),"brand":a.get("brand","—"),
#             "time":datetime.now().strftime("%Y-%m-%d %H:%M")})
#     if not alarm_log.empty:
#         for _, r in alarm_log.iterrows():
#             all_alarms.append({"device_type":"Inverter","level":"Warning","status":"Resolved",
#                 "plant_name":r.get("plant_name","—"),"sn":r.get("inverter_sn","—"),
#                 "content":r.get("issue","—"),"brand":r.get("brand","—"),
#                 "time":r.get("alerted_at","—")})

#     if sub == "Alarm Information":
#         st.markdown('<div class="page-hdr"><h1>Alarm Information</h1>'
#                     '<p>Fault detection and alert history</p></div>',
#                     unsafe_allow_html=True)

#         plant_opts = ["All"] + sorted(df["plant_name"].dropna().unique()) if not df.empty else ["All"]
#         sn_opts    = ["All"] + sorted(df["inverter_sn"].dropna().unique()) if not df.empty else ["All"]
#         brand_opts = ["All"] + sorted(df["brand"].dropna().unique())       if not df.empty else ["All"]

#         fc1,fc2,fc3,fc4,fc5 = st.columns(5)
#         with fc1: fp = st.selectbox("Plant Name",  plant_opts)
#         with fc2: fs = st.selectbox("S/N",         sn_opts)
#         with fc3: fb = st.selectbox("Brand",        brand_opts)
#         with fc4: fst= st.selectbox("Status",       ["All","Active","Resolved"])
#         with fc5: fl = st.selectbox("Level",        ["All","Critical","Warning"])

#         filt = all_alarms[:]
#         if fp !="All": filt=[a for a in filt if a["plant_name"]==fp]
#         if fs !="All": filt=[a for a in filt if a["sn"]        ==fs]
#         if fb !="All": filt=[a for a in filt if a["brand"]     ==fb]
#         if fst!="All": filt=[a for a in filt if a["status"]    ==fst]
#         if fl !="All": filt=[a for a in filt if a["level"]     ==fl]

#         m1,m2,m3 = st.columns(3)
#         m1.metric("Total", len(filt))
#         m2.metric("Active",   sum(1 for a in filt if a["status"]=="Active"))
#         m3.metric("Resolved", sum(1 for a in filt if a["status"]=="Resolved"))

#         if not filt:
#             st.success("✅ No alarms — all systems operating normally.")
#         else:
#             st.markdown('<div class="tbl">', unsafe_allow_html=True)
#             st.markdown('<div class="tbl-hdr tbl-alarm">'
#                         '<div>Device</div><div>Level</div><div>Status</div>'
#                         '<div>Plant</div><div>S/N</div><div>Issue</div><div>Time</div>'
#                         '</div>', unsafe_allow_html=True)
#             for a in filt:
#                 st.markdown(
#                     f'<div class="tbl-row tbl-alarm">'
#                       f'<div>{a["device_type"]}</div>'
#                       f'<div>{badge(a["level"],"level")}</div>'
#                       f'<div>{badge(a["status"],"status_alarm")}</div>'
#                       f'<div>{chip(a["brand"])} {a["plant_name"]}</div>'
#                       f'<div style="font-size:11px;color:var(--text3);font-family:\'JetBrains Mono\',monospace;">{a["sn"]}</div>'
#                       f'<div>{a["content"]}</div>'
#                       f'<div style="font-size:11px;color:var(--text3);">{a["time"]}</div>'
#                     f'</div>', unsafe_allow_html=True)
#             st.markdown('</div>', unsafe_allow_html=True)

#     else:
#         st.markdown('<div class="page-hdr"><h1>Device Overview</h1>'
#                     '<p>Live readings for every inverter</p></div>',
#                     unsafe_allow_html=True)
#         if df.empty:
#             st.warning("⚠️ No data."); st.stop()

#         fc1,fc2,fc3,fc4 = st.columns(4)
#         with fc1: bf = st.selectbox("Brand",  ["All"]+sorted(df["brand"].dropna().unique()),       key="do_b")
#         with fc2: pf = st.selectbox("Plant",  ["All"]+sorted(df["plant_name"].dropna().unique()),  key="do_p")
#         with fc3: sf = st.selectbox("S/N",    ["All"]+sorted(df["inverter_sn"].dropna().unique()), key="do_s")
#         with fc4: stf= st.selectbox("Status", ["All"]+sorted(df["status"].dropna().unique()),      key="do_st")

#         vw = df.copy()
#         if bf !="All": vw=vw[vw["brand"]       ==bf]
#         if pf !="All": vw=vw[vw["plant_name"]  ==pf]
#         if sf !="All": vw=vw[vw["inverter_sn"] ==sf]
#         if stf!="All": vw=vw[vw["status"]      ==stf]

#         st.markdown(
#             f'<div class="stat-row">'
#               f'<div class="stat-item"><div class="stat-val">{len(vw)}</div><div class="stat-lbl">Inverters</div></div>'
#               f'<div class="stat-item"><div class="stat-val">{f(vw["power_kw"].sum(),2)} kW</div><div class="stat-lbl">Total Power</div></div>'
#               f'<div class="stat-item"><div class="stat-val">{f(vw["today_kwh"].sum(),1)} kWh</div><div class="stat-lbl">Daily Yield</div></div>'
#               f'<div class="stat-item"><div class="stat-val">{int((vw["status"].str.lower()=="online").sum())}</div><div class="stat-lbl">Online</div></div>'
#             f'</div>', unsafe_allow_html=True)

#         alert_sns = {a.get("inverter_sn") for a in alerts}
#         for _, row in vw.iterrows():
#             sn    = str(row.get("inverter_sn","N/A"))
#             brand = str(row.get("brand",""))
#             st_   = str(row.get("status",""))
#             params = [
#                 ("Power Now",   f(row.get("power_kw"),2),  "kW"),
#                 ("Daily Yield", f(row.get("today_kwh"),1), "kWh"),
#                 ("Total Yield", f(row.get("total_kwh"),3), "MWh"),
#                 ("Temperature", f(row.get("temperature"),1),"°C"),
#                 ("AC Voltage",  f(row.get("voltage"),1),   "V"),
#                 ("AC Current",  f(row.get("current_a"),1), "A"),
#             ]
#             p_html = "".join(
#                 f'<div><div class="param-label">{l}</div>'
#                 f'<div class="param-val">{v}<span class="param-unit"> {u}</span></div></div>'
#                 for l,v,u in params)
#             border = "border-left:3px solid var(--red);" if sn in alert_sns else ""
#             st.markdown(
#                 f'<div class="inv-card" style="{border}">'
#                   f'<div class="inv-header">'
#                     f'<div><div class="inv-name">{row.get("plant_name","")}</div>'
#                     f'<div class="inv-meta">S/N: {sn} · {chip(brand)} · {row.get("last_update","—")}</div></div>'
#                     + badge(st_) +
#                   f'</div>'
#                   f'<div class="inv-params">{p_html}</div>'
#                 f'</div>', unsafe_allow_html=True)


# # ══════════════════════════════════════════════════════════════
# #  REPORT  — pulls historical data from Solis API directly
# # ══════════════════════════════════════════════════════════════
# elif page == "Report":
#     st.markdown('<div class="page-hdr"><h1>Plant Report</h1>'
#                 '<p>Historical generation data from Solis Cloud</p></div>',
#                 unsafe_allow_html=True)

#     rtype = st.radio("", ["Daily","Monthly","Annual","Total"],
#                      horizontal=True, label_visibility="collapsed")
#     st.markdown('<div style="height:10px"></div>', unsafe_allow_html=True)

#     # Plant selector — always from live df
#     plant_opts = (["All Plants"] + sorted(df["plant_name"].dropna().unique().tolist())
#                   if not df.empty else ["No data"])

#     fc1, fc2 = st.columns([2, 1])
#     with fc1: sel_plant = st.selectbox("Select Plant", plant_opts)
#     with fc2: sel_date  = st.date_input("Date", value=date.today())

#     # Shared line chart helper
#     def line_chart(fig, h=360):
#         fig = chart_style(fig, h)
#         fig.update_traces(selector=dict(type="scatter"), line=dict(width=2.5))
#         fig.update_layout(hovermode="x unified")
#         return fig

#     # Get plant IDs for selected plant
#     from utils.solis_api import (get_plants as _get_solis_plants,
#                                   get_all_plants_daily, get_all_plants_monthly,
#                                   get_plant_daily_history   as solis_daily,
#                                   get_plant_monthly_history as solis_monthly)
#     from utils.growatt_api import (get_plant_daily_history   as growatt_daily,
#                                    get_plant_monthly_history as growatt_monthly,
#                                    _get_plants               as _get_growatt_plants)

#     @st.cache_data(ttl=300)
#     def _plants_cached():
#         plants = []
#         try:
#             for p in _get_solis_plants():
#                 plants.append({"name": p.get("stationName"), "id": p.get("id"), "brand": "Solis"})
#         except Exception: pass
#         try:
#             for p in _get_growatt_plants():
#                 pid   = str(p.get("pId") or p.get("plantId",""))
#                 pname = p.get("plantNameEncryption") or p.get("plantName","")
#                 plants.append({"name": pname, "id": pid, "brand": "Growatt"})
#         except Exception: pass
#         return plants

#     all_plants    = _plants_cached()
#     plant_id_map  = {p["name"]: (p["id"], p["brand"]) for p in all_plants}

#     def get_daily_history(plant_name, month_str):
#         info = plant_id_map.get(plant_name)
#         if not info: return []
#         pid, brand = info
#         if brand == "Growatt": return growatt_daily(pid, month_str)
#         return solis_daily(pid, month_str)

#     def get_monthly_history(plant_name, year_str):
#         info = plant_id_map.get(plant_name)
#         if not info: return []
#         pid, brand = info
#         if brand == "Growatt": return growatt_monthly(pid, year_str)
#         return solis_monthly(pid, year_str)

#     # ── DAILY ────────────────────────────────────────────────
#     if rtype == "Daily":
#         # Determine brand of selected plant
#         sel_brand_for_report = "Solis"
#         if sel_plant != "All Plants":
#             info = plant_id_map.get(sel_plant)
#             if info: sel_brand_for_report = info[1]

#         # For Growatt: use stationDay API (has per-day hourly data)
#         # For Solis: use local DB (5-min readings collected by the app)
#         if sel_brand_for_report == "Growatt" and sel_plant != "All Plants":
#             month_str_d = sel_date.strftime("%Y-%m")
#             with st.spinner("Fetching daily data from Growatt…"):
#                 rows = get_daily_history(sel_plant, month_str_d)

#             if not rows:
#                 st.info(f"No data returned from Growatt for {sel_date.strftime('%B %Y')}.")
#             else:
#                 # Filter to selected date
#                 day_rows = [r for r in rows if r.get("date","").startswith(str(sel_date))]
#                 if not day_rows:
#                     # Show full month as fallback
#                     day_rows = rows
#                     st.info(f"Showing full month data — no hourly breakdown available for {sel_date}.")

#                 daily_df = pd.DataFrame(day_rows)
#                 daily_df["date"] = pd.to_datetime(daily_df["date"], errors="coerce")
#                 daily_df = daily_df.dropna(subset=["date"]).sort_values("date")

#                 sec(f"Daily Generation — {sel_plant} ({sel_date.strftime('%B %Y')})")
#                 fig = go.Figure()
#                 fig.add_trace(go.Bar(
#                     x=daily_df["date"], y=daily_df["energy_kwh"],
#                     name="Yield (kWh)", marker_color="rgba(16,185,129,.25)",
#                     marker_line_width=0,
#                 ))
#                 fig.add_trace(go.Scatter(
#                     x=daily_df["date"], y=daily_df["energy_kwh"],
#                     name="Yield", mode="lines+markers",
#                     line=dict(color="#10b981", width=2.5),
#                     marker=dict(size=6, color="#10b981"),
#                 ))
#                 fig.update_layout(
#                     plot_bgcolor="#fff", paper_bgcolor="#fff",
#                     font_family="Inter", font_color="#64748b",
#                     margin=dict(l=0,r=0,t=16,b=0), height=360,
#                     hovermode="x unified", bargap=0.25,
#                     legend=dict(bgcolor="rgba(0,0,0,0)"),
#                     yaxis=dict(title="kWh", showgrid=True, gridcolor="#f1f5f9", zeroline=False),
#                 )
#                 fig.update_xaxes(showgrid=False, zeroline=False, tickformat="%d %b")
#                 st.plotly_chart(fig, use_container_width=True)

#                 tot = daily_df["energy_kwh"].sum()
#                 c1,c2 = st.columns(2)
#                 c1.metric("Month Total", f"{tot:.1f} kWh")
#                 c2.metric("Estimated Earning", earn(tot))

#         else:
#             # Solis / All Plants — use local DB (5-min power readings)
#             hist_df = get_history(hours=8760)
#             if hist_df.empty:
#                 st.info("📭 No intraday data yet — the app collects readings every 5 min. "
#                         "Come back after the app has been running for a while.")
#             else:
#                 hist_df["fetched_at"] = pd.to_datetime(hist_df["fetched_at"])
#                 hist_df["power_kw"]   = pd.to_numeric(hist_df["power_kw"],  errors="coerce")
#                 hist_df["today_kwh"]  = pd.to_numeric(hist_df["today_kwh"], errors="coerce")
#                 if sel_plant != "All Plants":
#                     hist_df = hist_df[hist_df["plant_name"] == sel_plant]

#                 day = hist_df[hist_df["fetched_at"].dt.date == sel_date].sort_values("fetched_at")
#                 if day.empty:
#                     st.info(f"No intraday data for {sel_date}. "
#                             f"Try today's date — data builds up every 5 minutes the app is running.")
#                 else:
#                     sec("Power Output Throughout the Day (kW)")
#                     fig = px.line(day, x="fetched_at", y="power_kw", color="inverter_sn",
#                                   color_discrete_sequence=PALETTE,
#                                   labels={"fetched_at":"Time","power_kw":"Power (kW)",
#                                           "inverter_sn":"Inverter"})
#                     st.plotly_chart(line_chart(fig, 360), use_container_width=True)

#                     sec("Peak Power & Daily Generation per Inverter")
#                     sm = (day.groupby(["plant_name","inverter_sn","brand"])
#                           .agg(Peak_kW=("power_kw","max"), Daily_kWh=("today_kwh","max"))
#                           .reset_index()
#                           .rename(columns={"plant_name":"Plant","inverter_sn":"S/N","brand":"Brand"}))
#                     st.dataframe(sm, use_container_width=True, hide_index=True)

#     # ── MONTHLY ───────────────────────────────────────────────
#     elif rtype == "Monthly":
#         month_str = sel_date.strftime("%Y-%m")

#         with st.spinner(f"Fetching daily data for {sel_date.strftime('%B %Y')}…"):
#             if sel_plant == "All Plants":
#                 api_df = get_all_plants_daily(month_str)
#                 if not api_df.empty:
#                     daily = (api_df.groupby("date")["energy_kwh"]
#                              .sum().reset_index())
#                     daily.columns = ["Date","Daily Yield (kWh)"]
#                     income_df = api_df.groupby("date")["income"].sum().reset_index()
#                     income_df.columns = ["Date","Income (INR)"]
#                     daily = daily.merge(income_df, on="Date", how="left")
#                 else:
#                     daily = pd.DataFrame()
#             else:
#                 rows = get_daily_history(sel_plant, month_str)
#                 if rows:
#                     daily = pd.DataFrame(rows).rename(columns={
#                         "date":"Date","energy_kwh":"Daily Yield (kWh)","income":"Income (INR)"})
#                     daily["Date"] = pd.to_datetime(daily["Date"], errors="coerce")
#                 else:
#                     daily = pd.DataFrame()

#         if daily.empty or "Daily Yield (kWh)" not in daily.columns:
#             st.info(f"No data from Solis API for {sel_date.strftime('%B %Y')}.")
#         else:
#             daily = daily.dropna(subset=["Date"]).sort_values("Date")

#             # Combined bar + line chart matching Solis style
#             sec(f"Daily Generation — {sel_date.strftime('%B %Y')}")
#             fig = go.Figure()
#             # Bar: yield
#             fig.add_trace(go.Bar(
#                 x=daily["Date"], y=daily["Daily Yield (kWh)"],
#                 name="Yield (kWh)", marker_color="rgba(13,148,136,.25)",
#                 marker_line_width=0,
#             ))
#             # Line: yield trend
#             fig.add_trace(go.Scatter(
#                 x=daily["Date"], y=daily["Daily Yield (kWh)"],
#                 name="Yield", mode="lines+markers",
#                 line=dict(color="#0d9488", width=2.5),
#                 marker=dict(size=5, color="#0d9488"),
#             ))
#             # Line: revenue (right axis)
#             if "Income (INR)" in daily.columns:
#                 fig.add_trace(go.Scatter(
#                     x=daily["Date"], y=daily["Income (INR)"],
#                     name="Revenue (INR)", mode="lines+markers",
#                     line=dict(color="#f59e0b", width=2, dash="dot"),
#                     marker=dict(size=5, color="#f59e0b"),
#                     yaxis="y2",
#                 ))
#             fig.update_layout(
#                 plot_bgcolor="#fff", paper_bgcolor="#fff",
#                 font_family="Inter", font_color="#64748b",
#                 margin=dict(l=0,r=60,t=16,b=0), height=380,
#                 hovermode="x unified", bargap=0.25,
#                 legend=dict(bgcolor="rgba(0,0,0,0)", orientation="h",
#                             yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
#                 yaxis=dict(title="kWh", showgrid=True, gridcolor="#f1f5f9",
#                            zeroline=False, tickfont_size=11),
#                 yaxis2=dict(title="INR", overlaying="y", side="right",
#                             showgrid=False, zeroline=False, tickfont_size=11),
#             )
#             fig.update_xaxes(showgrid=False, zeroline=False, tickfont_size=11,
#                              tickformat="%d", dtick="D1")
#             st.plotly_chart(fig, use_container_width=True)

#             tot = daily["Daily Yield (kWh)"].sum()
#             m1,m2,m3 = st.columns(3)
#             m1.metric("Month Total", f"{tot:.1f} kWh")
#             m2.metric("Month Total (MWh)", f"{tot/1000:.3f} MWh")
#             m3.metric("Estimated Earning", earn(tot))

#     # ── ANNUAL ────────────────────────────────────────────────
#     elif rtype == "Annual":
#         year_str = str(sel_date.year)

#         with st.spinner(f"Fetching monthly data for {year_str}…"):
#             if sel_plant == "All Plants":
#                 api_df = get_all_plants_monthly(year_str)
#                 if not api_df.empty:
#                     monthly = (api_df.groupby("month")["energy_kwh"]
#                                .sum().reset_index())
#                     monthly.columns = ["Month","kWh"]
#                 else:
#                     monthly = pd.DataFrame()
#             else:
#                 rows = get_monthly_history(sel_plant, year_str)
#                 if rows:
#                     monthly = pd.DataFrame(rows).rename(columns={"month":"Month","energy_kwh":"kWh"})
#                 else:
#                     monthly = pd.DataFrame()

#         if monthly.empty or "kWh" not in monthly.columns:
#             st.info(f"No data from Solis API for {year_str}.")
#         else:
#             monthly = monthly[monthly["kWh"] > 0]

#             sec(f"Monthly Generation — {year_str}")
#             fig = go.Figure()
#             fig.add_trace(go.Bar(
#                 x=monthly["Month"], y=monthly["kWh"],
#                 name="Yield (kWh)", marker_color="rgba(245,158,11,.3)",
#                 marker_line_width=0,
#             ))
#             fig.add_trace(go.Scatter(
#                 x=monthly["Month"], y=monthly["kWh"],
#                 name="Trend", mode="lines+markers",
#                 line=dict(color="#f59e0b", width=2.5),
#                 marker=dict(size=7, color="#f59e0b"),
#             ))
#             fig.update_layout(
#                 plot_bgcolor="#fff", paper_bgcolor="#fff",
#                 font_family="Inter", font_color="#64748b",
#                 margin=dict(l=0,r=0,t=16,b=0), height=360,
#                 hovermode="x unified", bargap=0.3,
#                 legend=dict(bgcolor="rgba(0,0,0,0)"),
#                 yaxis=dict(showgrid=True, gridcolor="#f1f5f9",
#                            zeroline=False, tickfont_size=11),
#             )
#             fig.update_xaxes(showgrid=False, zeroline=False, tickfont_size=11)
#             st.plotly_chart(fig, use_container_width=True)

#             tot_yr = monthly["kWh"].sum()
#             m1,m2,m3 = st.columns(3)
#             m1.metric("Year Total", f"{tot_yr:.1f} kWh")
#             m2.metric("Year Total (MWh)", f"{tot_yr/1000:.3f} MWh")
#             m3.metric("Est. Annual Earning", earn(tot_yr))

#     # ── TOTAL ─────────────────────────────────────────────────
#     else:
#         sec("Total Yield per Plant (All-time)")
#         if not df.empty:
#             gt = (df.groupby(["plant_name","brand"])
#                   .agg(total_mwh=("total_kwh","sum"), daily_kwh=("today_kwh","sum"))
#                   .reset_index())

#             fig = go.Figure()
#             for i, row in gt.iterrows():
#                 fig.add_trace(go.Bar(
#                     x=[row["plant_name"]], y=[row["total_mwh"]],
#                     name=row["plant_name"],
#                     marker_color=PALETTE[i % len(PALETTE)],
#                     marker_line_width=0,
#                 ))
#             fig.update_layout(
#                 plot_bgcolor="#fff", paper_bgcolor="#fff",
#                 font_family="Inter", font_color="#64748b",
#                 margin=dict(l=0,r=0,t=16,b=0), height=340,
#                 showlegend=False, bargap=0.35,
#                 yaxis=dict(title="MWh", showgrid=True, gridcolor="#f1f5f9",
#                            zeroline=False, tickfont_size=11),
#             )
#             fig.update_xaxes(showgrid=False, zeroline=False, tickfont_size=11)
#             st.plotly_chart(fig, use_container_width=True)

#             gt_disp = gt.rename(columns={"plant_name":"Plant","brand":"Brand",
#                                           "total_mwh":"Total Yield (MWh)",
#                                           "daily_kwh":"Today (kWh)"})
#             st.dataframe(gt_disp, use_container_width=True, hide_index=True)


# # ══════════════════════════════════════════════════════════════
# #  SERVICE
# # ══════════════════════════════════════════════════════════════
# elif page == "Service":
#     st.markdown('<div class="page-hdr"><h1>Plant Management</h1>'
#                 '<p>All registered plants and operational details</p></div>',
#                 unsafe_allow_html=True)
#     if df.empty:
#         st.warning("⚠️ No data."); st.stop()

#     fc1,fc2 = st.columns(2)
#     with fc1: pf2 = st.selectbox("Plant", ["All"]+sorted(df["plant_name"].dropna().unique()), key="pm_p")
#     with fc2: bf2 = st.selectbox("Brand", ["All"]+sorted(df["brand"].dropna().unique()),      key="pm_b")

#     ps = (df.groupby(["plant_name","brand"])
#           .agg(power_kw=("power_kw","sum"), today_kwh=("today_kwh","sum"),
#                total_kwh=("total_kwh","sum"), inv_count=("inverter_sn","count"))
#           .reset_index())
#     if pf2!="All": ps=ps[ps["plant_name"]==pf2]
#     if bf2!="All": ps=ps[ps["brand"]==bf2]

#     st.markdown(
#         f'<div class="stat-row">'
#           f'<div class="stat-item"><div class="stat-val">{len(ps)}</div><div class="stat-lbl">Plants</div></div>'
#           f'<div class="stat-item"><div class="stat-val">{f(ps["power_kw"].sum(),2)} kW</div><div class="stat-lbl">Total Power</div></div>'
#           f'<div class="stat-item"><div class="stat-val">{f(ps["today_kwh"].sum(),1)} kWh</div><div class="stat-lbl">Daily Yield</div></div>'
#           f'<div class="stat-item"><div class="stat-val">{f(ps["total_kwh"].sum(),1)} MWh</div><div class="stat-lbl">Total Yield</div></div>'
#         f'</div>', unsafe_allow_html=True)

#     st.markdown('<div class="tbl">', unsafe_allow_html=True)
#     st.markdown('<div class="tbl-hdr tbl-plant">'
#                 '<div>Plant Name</div><div>Brand</div><div>Organisation</div>'
#                 '<div>Inverters</div><div>Power (kW)</div>'
#                 '<div>Daily Yield</div><div>Total Yield</div><div>Status</div>'
#                 '</div>', unsafe_allow_html=True)
#     for _, row in ps.iterrows():
#         pr   = df[df["plant_name"]==row["plant_name"]]
#         on   = int((pr["status"].str.lower()=="online").sum())
#         tot  = int(row["inv_count"])
#         pst  = "Online" if on==tot and tot>0 else ("Offline" if on==0 else "Warning")
#         dy   = float(row["today_kwh"] or 0)
#         dy_s = f"{dy/1000:.3f} MWh" if dy>=1000 else f"{dy:.1f} kWh"
#         ty   = float(row["total_kwh"] or 0)
#         ty_s = f"{ty/1000:.3f} GWh" if ty>=1000 else f"{ty:.3f} MWh"
#         st.markdown(
#             f'<div class="tbl-row tbl-plant">'
#               f'<div class="cell-link">{row["plant_name"]}</div>'
#               f'<div>{chip(row["brand"])}</div>'
#               f'<div>Fractal Energy</div>'
#               f'<div>{on}/{tot}</div>'
#               f'<div><b>{f(row["power_kw"],2)}</b> kW</div>'
#               f'<div>{dy_s}</div><div>{ty_s}</div>'
#               f'<div>{badge(pst)}</div>'
#             f'</div>', unsafe_allow_html=True)
#     st.markdown('</div>', unsafe_allow_html=True)


# # ══════════════════════════════════════════════════════════════
# #  SETTINGS
# # ══════════════════════════════════════════════════════════════
# elif page == "Settings":
#     st.markdown('<div class="page-hdr"><h1>Settings</h1>'
#                 '<p>Credentials, alerts and app configuration</p></div>',
#                 unsafe_allow_html=True)

#     from config import (SOLIS_API_KEY, GROWATT_USERNAME, SUNGROW_APP_KEY,
#                         EMAIL_USER, TO_EMAILS, RATE_PER_KWH)

#     st.markdown("#### 🔑 API Credentials")
#     for brand,ok,hint in [
#         ("Solis",   bool(SOLIS_API_KEY),
#          SOLIS_API_KEY[:10]+"…" if SOLIS_API_KEY else "Not configured"),
#         ("Growatt", bool(GROWATT_USERNAME),
#          GROWATT_USERNAME or "Set GROWATT_USERNAME in config.py"),
#         ("Sungrow", bool(SUNGROW_APP_KEY),
#          SUNGROW_APP_KEY[:10]+"…" if SUNGROW_APP_KEY else "Set SUNGROW_APP_KEY in config.py"),
#     ]:
#         c1,c2,c3 = st.columns([1,1,4])
#         c1.markdown(f"**{brand}**")
#         c2.markdown("✅ OK" if ok else "⚠️ Not set")
#         c3.markdown(f"`{hint}`")

#     st.divider()
#     st.markdown("#### 📧 Email Alerts")
#     st.markdown(f"**Sender:** `{EMAIL_USER}`")
#     st.markdown(f"**Recipients:** `{', '.join(TO_EMAILS)}`")
#     st.divider()
#     st.markdown("#### 💰 Tariff Rate")
#     st.info(f"Current rate: **₹{RATE_PER_KWH}/kWh** — edit `RATE_PER_KWH` in config.py")
#     st.divider()
#     st.markdown("#### 👤 Logged in as")
#     st.info(f"`{st.session_state.user}`")
#     st.divider()
#     st.markdown("#### 🗂 Project Structure")
#     st.code("""
# solar_dashboard/
# ├── app.py              ← streamlit run app.py
# ├── config.py           ← ✏️  credentials & settings
# ├── requirements.txt
# ├── data/solar_data.db  ← auto-created
# └── utils/
#     ├── solis_api.py    ├── growatt_api.py
#     ├── sungrow_api.py  ├── aggregator.py
#     ├── database.py     └── alerts.py
#     """, language="")


# import streamlit as st
# from streamlit_autorefresh import st_autorefresh
# import pandas as pd
# import plotly.express as px
# import plotly.graph_objects as go
# from datetime import datetime, date, timedelta

# from config import REFRESH_INTERVAL_SECONDS, RATE_PER_KWH
# from utils.database import init_db, get_history, get_alert_log
# from utils.aggregator import fetch_all_brands, check_alerts

# # ─────────────────────────────────────────────────────────────
# st.set_page_config(
#     page_title="Solar Dashboard · Fractal Energy",
#     page_icon="☀️",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# # ─────────────────────────────────────────────────────────────
# # INIT
# # ─────────────────────────────────────────────────────────────
# init_db()

# # ─────────────────────────────────────────────────────────────
# # AUTO REFRESH
# # ─────────────────────────────────────────────────────────────
# st_autorefresh(interval=REFRESH_INTERVAL_SECONDS * 1000, key="solar_ar")

# # ─────────────────────────────────────────────────────────────
# # HELPERS
# # ─────────────────────────────────────────────────────────────
# def f(v, d=1):
#     try:
#         return f"{float(v):.{d}f}"
#     except:
#         return "0"

# def earn(kwh):
#     val = float(kwh) * RATE_PER_KWH
#     return f"₹{val:,.0f}"

# def chart_style(fig, h=350):
#     fig.update_layout(
#         height=h,
#         plot_bgcolor="white",
#         paper_bgcolor="white",
#         margin=dict(l=10, r=10, t=40, b=10),
#         font=dict(size=13)
#     )
#     return fig

# # ─────────────────────────────────────────────────────────────
# # SIDEBAR
# # ─────────────────────────────────────────────────────────────
# with st.sidebar:
#     st.title("☀️ Solar Dashboard")
#     page = st.radio(
#         "Navigation",
#         ["Overview", "O&M", "Report", "Service", "Settings"]
#     )

#     sel_brands = st.multiselect(
#         "Brands",
#         ["Solis", "Growatt", "Sungrow"],
#         default=["Solis"]
#     )

# # ─────────────────────────────────────────────────────────────
# # LOAD LIVE DATA
# # ─────────────────────────────────────────────────────────────
# @st.cache_data(ttl=REFRESH_INTERVAL_SECONDS)
# def load_data(brands):
#     return fetch_all_brands(list(brands))

# records = load_data(tuple(sel_brands))
# alerts = check_alerts(records, st.session_state)

# df = pd.DataFrame(records)

# if not df.empty:
#     for c in [
#         "power_kw",
#         "today_kwh",
#         "total_kwh",
#         "temperature",
#         "voltage",
#         "current_a"
#     ]:
#         if c in df.columns:
#             df[c] = pd.to_numeric(df[c], errors="coerce")

# # ============================================================
# # REPORT PAGE (FULLY FIXED)
# # ============================================================
# if page == "Report":

#     st.title("📈 Plant Report")
#     st.caption("Corrected Daily / Monthly / Annual / Total values")

#     if df.empty:
#         st.warning("No live plant data found.")
#         st.stop()

#     report_type = st.radio(
#         "Select Report Type",
#         ["Daily", "Monthly", "Annual", "Total"],
#         horizontal=True
#     )

#     plant_list = ["All Plants"] + sorted(df["plant_name"].dropna().unique())
#     selected_plant = st.selectbox("Plant", plant_list)

#     selected_date = st.date_input("Date", date.today())

#     # --------------------------------------------------------
#     # FILTER PLANT
#     # --------------------------------------------------------
#     if selected_plant == "All Plants":
#         live_df = df.copy()
#     else:
#         live_df = df[df["plant_name"] == selected_plant].copy()

#     # --------------------------------------------------------
#     # DAILY REPORT
#     # --------------------------------------------------------
#     if report_type == "Daily":

#         st.subheader("Daily Generation")

#         hist = get_history(hours=48)

#         if hist.empty:
#             st.info("No daily historical data available.")
#         else:
#             hist["fetched_at"] = pd.to_datetime(hist["fetched_at"])
#             hist["power_kw"] = pd.to_numeric(hist["power_kw"], errors="coerce")
#             hist["today_kwh"] = pd.to_numeric(hist["today_kwh"], errors="coerce")

#             if selected_plant != "All Plants":
#                 hist = hist[hist["plant_name"] == selected_plant]

#             hist = hist[hist["fetched_at"].dt.date == selected_date]

#             if hist.empty:
#                 st.info("No data for selected date.")
#             else:
#                 fig = px.line(
#                     hist,
#                     x="fetched_at",
#                     y="power_kw",
#                     color="inverter_sn",
#                     title="Power Curve"
#                 )
#                 st.plotly_chart(chart_style(fig), use_container_width=True)

#                 total_day = hist.groupby("inverter_sn")["today_kwh"].max().sum()

#                 c1, c2 = st.columns(2)
#                 c1.metric("Daily Yield", f"{total_day:.2f} kWh")
#                 c2.metric("Estimated Earnings", earn(total_day))

#     # --------------------------------------------------------
#     # MONTHLY REPORT
#     # --------------------------------------------------------
#     elif report_type == "Monthly":

#         st.subheader("Monthly Generation")

#         hist = get_history(hours=24 * 35)

#         if hist.empty:
#             st.info("No monthly data.")
#         else:
#             hist["fetched_at"] = pd.to_datetime(hist["fetched_at"])
#             hist["today_kwh"] = pd.to_numeric(hist["today_kwh"], errors="coerce")

#             if selected_plant != "All Plants":
#                 hist = hist[hist["plant_name"] == selected_plant]

#             hist = hist[
#                 (hist["fetched_at"].dt.month == selected_date.month) &
#                 (hist["fetched_at"].dt.year == selected_date.year)
#             ]

#             daily = (
#                 hist.groupby(
#                     [
#                         hist["fetched_at"].dt.date,
#                         "inverter_sn"
#                     ]
#                 )["today_kwh"]
#                 .max()
#                 .reset_index()
#             )

#             daily_totals = (
#                 daily.groupby("fetched_at")["today_kwh"]
#                 .sum()
#                 .reset_index()
#             )

#             fig = px.bar(
#                 daily_totals,
#                 x="fetched_at",
#                 y="today_kwh",
#                 title="Daily Yield This Month"
#             )
#             st.plotly_chart(chart_style(fig), use_container_width=True)

#             month_total = daily_totals["today_kwh"].sum()

#             c1, c2 = st.columns(2)
#             c1.metric("Monthly Yield", f"{month_total:.2f} kWh")
#             c2.metric("Estimated Earnings", earn(month_total))

#     # --------------------------------------------------------
#     # ANNUAL REPORT
#     # --------------------------------------------------------
#     elif report_type == "Annual":

#         st.subheader("Annual Generation")

#         hist = get_history(hours=24 * 370)

#         if hist.empty:
#             st.info("No annual data.")
#         else:
#             hist["fetched_at"] = pd.to_datetime(hist["fetched_at"])
#             hist["today_kwh"] = pd.to_numeric(hist["today_kwh"], errors="coerce")

#             if selected_plant != "All Plants":
#                 hist = hist[hist["plant_name"] == selected_plant]

#             hist = hist[
#                 hist["fetched_at"].dt.year == selected_date.year
#             ]

#             daily = (
#                 hist.groupby(
#                     [
#                         hist["fetched_at"].dt.month,
#                         hist["fetched_at"].dt.date,
#                         "inverter_sn"
#                     ]
#                 )["today_kwh"]
#                 .max()
#                 .reset_index()
#             )

#             monthly = (
#                 daily.groupby("fetched_at")["today_kwh"]
#                 .sum()
#                 .reset_index()
#             )

#             monthly.columns = ["Month", "kWh"]

#             fig = px.bar(
#                 monthly,
#                 x="Month",
#                 y="kWh",
#                 title="Monthly Yield"
#             )
#             st.plotly_chart(chart_style(fig), use_container_width=True)

#             annual_total = monthly["kWh"].sum()

#             c1, c2 = st.columns(2)
#             c1.metric("Annual Yield", f"{annual_total:.2f} kWh")
#             c2.metric("Estimated Earnings", earn(annual_total))

#     # --------------------------------------------------------
#     # TOTAL REPORT
#     # --------------------------------------------------------
#     else:

#         st.subheader("Lifetime Generation")

#         total = live_df["total_kwh"].sum()

#         c1, c2 = st.columns(2)
#         c1.metric("Total Yield", f"{total:.2f} kWh")
#         c2.metric("Total Earnings", earn(total))

#         plant_total = (
#             live_df.groupby("plant_name")["total_kwh"]
#             .sum()
#             .reset_index()
#         )

#         fig = px.bar(
#             plant_total,
#             x="plant_name",
#             y="total_kwh",
#             title="Plant Wise Lifetime Yield"
#         )
#         st.plotly_chart(chart_style(fig), use_container_width=True)

# # ============================================================
# #  app.py  —  Solar Dashboard  |  streamlit run app.py
# # ============================================================
# import streamlit as st
# from streamlit_autorefresh import st_autorefresh
# import pandas as pd
# import plotly.express as px
# import plotly.graph_objects as go
# from datetime import datetime, date, timedelta

# from config import REFRESH_INTERVAL_SECONDS, RATE_PER_KWH
# from utils.database import init_db, get_history, get_alert_log
# from utils.aggregator import fetch_all_brands, check_alerts

# # ─────────────────────────────────────────────────────────────
# st.set_page_config(page_title="Solar Dashboard · Fractal Energy",
#                    page_icon="☀️", layout="wide",
#                    initial_sidebar_state="expanded")

# # ══════════════════════════════════════════════════════════════
# #  GLOBAL CSS  —  Navy · Teal · Amber theme
# # ══════════════════════════════════════════════════════════════
# st.markdown("""
# <style>
# @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

# *,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}

# :root{
#   /* ── Palette ── */
#   --navy:      #0a1628;
#   --navy2:     #0f2044;
#   --navy3:     #1a2f5a;
#   --teal:      #0d9488;
#   --teal-l:    #ccfbf1;
#   --teal-d:    #0f766e;
#   --amber:     #f59e0b;
#   --amber-l:   #fef3c7;
#   --amber-d:   #d97706;
#   --orange:    #f97316;
#   --orange-l:  #ffedd5;
#   --red:       #ef4444;
#   --red-l:     #fee2e2;
#   --green:     #10b981;
#   --green-l:   #d1fae5;
#   --sky:       #38bdf8;
#   --sky-l:     #e0f2fe;

#   /* ── Surfaces ── */
#   --bg:        #f0f4f8;
#   --card:      #ffffff;
#   --border:    #e2e8f0;
#   --border2:   #cbd5e1;

#   /* ── Text ── */
#   --text:      #0f172a;
#   --text2:     #475569;
#   --text3:     #94a3b8;

#   /* ── Shadows ── */
#   --shadow:    0 1px 4px rgba(10,22,40,.06),0 4px 20px rgba(10,22,40,.05);
#   --shadow-lg: 0 8px 40px rgba(10,22,40,.12);
#   --shadow-teal:0 4px 20px rgba(13,148,136,.25);
# }

# /* ── Fonts ── */
# html,body,[data-testid="stAppViewContainer"]{
#   background:var(--bg)!important;
#   font-family:'Plus Jakarta Sans',sans-serif!important;
#   color:var(--text);
# }
# [data-testid="stHeader"]{background:transparent!important;display:none;}
# #MainMenu,footer{visibility:hidden;}
# [data-testid="stDecoration"]{display:none;}
# .block-container{padding:28px 32px!important;max-width:100%!important;}

# /* ══ SIDEBAR ══════════════════════════════════════════════ */
# [data-testid="stSidebar"]{
#   background:var(--navy)!important;
#   border-right:1px solid rgba(255,255,255,.06)!important;
# }
# [data-testid="stSidebar"]>div{padding-top:0!important;}
# section[data-testid="stSidebarContent"]{padding:0!important;}

# .sb-logo{
#   padding:24px 20px 18px;
#   border-bottom:1px solid rgba(255,255,255,.07);
#   margin-bottom:6px;
#   display:flex;align-items:center;gap:12px;
# }
# .sb-logo-icon{
#   width:42px;height:42px;background:linear-gradient(135deg,var(--teal),var(--teal-d));
#   border-radius:12px;display:flex;align-items:center;justify-content:center;
#   font-size:20px;flex-shrink:0;box-shadow:var(--shadow-teal);
# }
# .sb-logo-title{color:#fff;font-weight:800;font-size:15px;letter-spacing:-.3px;}
# .sb-logo-sub{color:#64748b;font-size:11px;margin-top:1px;}
# .sb-section{
#   padding:14px 20px 4px;
#   font-size:10px;font-weight:700;color:#334155;
#   text-transform:uppercase;letter-spacing:.12em;
# }
# .sb-time{
#   padding:14px 20px;font-size:11px;color:#475569;
#   border-top:1px solid rgba(255,255,255,.06);margin-top:6px;
#   font-family:'JetBrains Mono',monospace;
# }

# /* ══ LOGIN PAGE ═══════════════════════════════════════════ */
# .login-wrap{
#   min-height:100vh;display:flex;align-items:center;justify-content:center;
#   background:linear-gradient(135deg,var(--navy) 0%,var(--navy2) 50%,#0d2b4e 100%);
#   padding:20px;
# }
# .login-card{
#   background:rgba(255,255,255,.04);
#   border:1px solid rgba(255,255,255,.1);
#   border-radius:20px;padding:48px 44px;width:100%;max-width:420px;
#   backdrop-filter:blur(20px);
#   box-shadow:0 20px 60px rgba(0,0,0,.4);
# }
# .login-logo{
#   width:60px;height:60px;
#   background:linear-gradient(135deg,var(--teal),var(--teal-d));
#   border-radius:16px;display:flex;align-items:center;justify-content:center;
#   font-size:28px;margin:0 auto 20px;
#   box-shadow:0 8px 24px rgba(13,148,136,.4);
# }
# .login-title{
#   font-size:24px;font-weight:800;color:#fff;text-align:center;
#   letter-spacing:-.4px;margin-bottom:6px;
# }
# .login-sub{font-size:13px;color:#64748b;text-align:center;margin-bottom:32px;}
# .login-label{font-size:13px;font-weight:600;color:#94a3b8;margin-bottom:6px;}
# .login-error{
#   background:rgba(239,68,68,.12);border:1px solid rgba(239,68,68,.3);
#   border-radius:8px;padding:10px 14px;font-size:13px;color:#fca5a5;
#   margin-bottom:16px;text-align:center;
# }

# /* ══ PAGE HEADER ══════════════════════════════════════════ */
# .page-hdr{margin-bottom:24px;}
# .page-hdr h1{
#   font-size:24px;font-weight:800;color:var(--text);
#   letter-spacing:-.5px;line-height:1.2;
# }
# .page-hdr p{font-size:13px;color:var(--text3);margin-top:4px;}

# /* ══ KPI CARDS ════════════════════════════════════════════ */
# .kpi-card{
#   background:var(--card);border-radius:16px;padding:24px 22px;
#   border:1px solid var(--border);box-shadow:var(--shadow);
#   display:flex;gap:16px;align-items:flex-start;
#   transition:transform .15s,box-shadow .15s;
#   position:relative;overflow:hidden;
# }
# .kpi-card::after{
#   content:'';position:absolute;top:0;left:0;right:0;height:3px;
#   background:linear-gradient(90deg,var(--teal),var(--sky));
#   border-radius:16px 16px 0 0;
# }
# .kpi-card.amber::after{background:linear-gradient(90deg,var(--amber),var(--orange));}
# .kpi-card.green::after{background:linear-gradient(90deg,var(--green),var(--teal));}
# .kpi-card.navy::after{background:linear-gradient(90deg,var(--navy3),var(--sky));}
# .kpi-card:hover{transform:translateY(-2px);box-shadow:var(--shadow-lg);}

# .kpi-icon{
#   width:50px;height:50px;border-radius:13px;flex-shrink:0;
#   display:flex;align-items:center;justify-content:center;font-size:22px;
# }
# .kpi-icon.teal  {background:var(--teal-l);color:var(--teal);}
# .kpi-icon.amber {background:var(--amber-l);color:var(--amber-d);}
# .kpi-icon.green {background:var(--green-l);color:var(--green);}
# .kpi-icon.navy  {background:var(--sky-l);color:#0284c7;}

# .kpi-label{
#   font-size:11px;color:var(--text3);font-weight:700;
#   text-transform:uppercase;letter-spacing:.1em;margin-bottom:6px;
# }
# .kpi-value{
#   font-size:28px;font-weight:800;color:var(--text);
#   line-height:1;letter-spacing:-.5px;
# }
# .kpi-unit{font-size:14px;font-weight:600;color:var(--text2);margin-left:3px;}
# .kpi-meta{font-size:12px;color:var(--text3);margin-top:8px;line-height:1.4;}
# .kpi-meta b{color:var(--teal);font-weight:600;}

# /* ══ SECTION HEADER ═══════════════════════════════════════ */
# .sec-hdr{
#   font-size:13px;font-weight:700;color:var(--text);
#   display:flex;align-items:center;gap:8px;
#   margin-bottom:14px;padding-bottom:10px;
#   border-bottom:2px solid var(--border);
# }
# .sec-hdr-dot{
#   width:8px;height:8px;border-radius:50%;
#   background:linear-gradient(135deg,var(--teal),var(--sky));
#   flex-shrink:0;
# }

# /* ══ CARD WRAPPER ═════════════════════════════════════════ */
# .card{
#   background:var(--card);border-radius:16px;padding:22px;
#   border:1px solid var(--border);box-shadow:var(--shadow);margin-bottom:16px;
# }

# /* ══ INVERTER CARD ════════════════════════════════════════ */
# .inv-card{
#   background:var(--card);border-radius:16px;padding:22px;
#   border:1px solid var(--border);box-shadow:var(--shadow);
#   margin-bottom:14px;transition:border-color .15s,box-shadow .15s;
# }
# .inv-card:hover{border-color:var(--primary);box-shadow:var(--shadow-teal);}
# .inv-card.alert-card{border-left:3px solid var(--red);}
# .inv-header{
#   display:flex;justify-content:space-between;align-items:flex-start;
#   margin-bottom:18px;padding-bottom:14px;
#   border-bottom:1px solid var(--border);
# }
# .inv-name{font-size:15px;font-weight:700;color:var(--text);letter-spacing:-.3px;}
# .inv-meta{font-size:11px;color:var(--text3);margin-top:3px;font-family:'JetBrains Mono',monospace;}
# .inv-params{display:grid;grid-template-columns:repeat(6,1fr);gap:16px;}
# .param-label{
#   font-size:10px;color:var(--text3);text-transform:uppercase;
#   letter-spacing:.08em;font-weight:600;margin-bottom:4px;
# }
# .param-val{font-size:18px;font-weight:700;color:var(--text);letter-spacing:-.3px;}
# .param-unit{font-size:11px;color:var(--text3);margin-left:2px;}
# .inv-footer{margin-top:14px;font-size:11px;color:var(--text3);font-family:'JetBrains Mono',monospace;}

# /* ══ TABLES ═══════════════════════════════════════════════ */
# .tbl{
#   background:var(--card);border-radius:16px;
#   border:1px solid var(--border);overflow:hidden;box-shadow:var(--shadow);
# }
# .tbl-hdr,.tbl-row{
#   display:grid;padding:0 20px;align-items:center;gap:10px;
# }
# .tbl-hdr{
#   background:linear-gradient(90deg,#f8fafc,#f1f5f9);
#   border-bottom:2px solid var(--border);
#   font-size:10px;font-weight:700;color:var(--text3);
#   text-transform:uppercase;letter-spacing:.1em;height:44px;
# }
# .tbl-row{
#   min-height:54px;border-bottom:1px solid var(--border);
#   font-size:13px;transition:background .1s;
# }
# .tbl-row:last-child{border-bottom:none;}
# .tbl-row:hover{background:#f8fafc;}
# .tbl-plant{grid-template-columns:2fr 1fr 1.1fr 1fr 1fr 1.1fr 1.3fr 1fr;}
# .tbl-alarm{grid-template-columns:1fr 1fr 1fr 1.5fr 1.4fr 2.2fr 1.2fr;}
# .cell-link{color:var(--primary);font-weight:700;cursor:pointer;font-size:13px;}

# /* ══ BADGES ═══════════════════════════════════════════════ */
# .badge{
#   display:inline-flex;align-items:center;gap:5px;
#   font-size:11px;font-weight:700;padding:4px 10px;
#   border-radius:20px;letter-spacing:.02em;
# }
# .badge::before{content:'';width:6px;height:6px;border-radius:50%;}
# .b-online {background:var(--green-l);color:#065f46;}
# .b-online::before{background:var(--green);}
# .b-offline{background:var(--red-l);color:#991b1b;}
# .b-offline::before{background:var(--red);}
# .b-warning{background:var(--amber-l);color:#92400e;}
# .b-warning::before{background:var(--amber);}
# .b-unknown{background:#f1f5f9;color:#64748b;}
# .b-unknown::before{background:#94a3b8;}
# .b-active {background:var(--red-l);color:#991b1b;}
# .b-active::before{background:var(--red);}
# .b-resolved{background:var(--green-l);color:#065f46;}
# .b-resolved::before{background:var(--green);}
# .b-critical{background:var(--red-l);color:#991b1b;font-weight:800;}
# .b-critical::before{background:var(--red);}

# /* ══ CHIPS ════════════════════════════════════════════════ */
# .chip{
#   display:inline-block;font-size:10px;font-weight:800;
#   padding:3px 9px;border-radius:6px;
#   letter-spacing:.1em;text-transform:uppercase;
# }
# .chip-solis  {background:#dbeafe;color:#1e40af;}
# .chip-growatt{background:#d1fae5;color:#065f46;}
# .chip-sungrow{background:#ffedd5;color:#c2410c;}

# /* ══ ALERT STRIP ══════════════════════════════════════════ */
# .alert-strip{
#   background:linear-gradient(135deg,#fff1f2,#ffe4e6);
#   border:1px solid #fecdd3;border-left:4px solid var(--red);
#   border-radius:12px;padding:16px 18px;margin-bottom:12px;
#   display:flex;gap:14px;align-items:flex-start;
# }
# .alert-strip-ico{font-size:20px;flex-shrink:0;}
# .alert-strip-ttl{font-size:14px;font-weight:700;color:var(--red);}
# .alert-strip-msg{font-size:12px;color:#7f1d1d;margin-top:3px;}

# /* ══ STAT ROW ═════════════════════════════════════════════ */
# .stat-row{
#   background:var(--card);border-radius:14px;padding:16px 24px;
#   border:1px solid var(--border);display:flex;gap:32px;
#   margin-bottom:20px;align-items:center;flex-wrap:wrap;
#   box-shadow:var(--shadow);
# }
# .stat-item{text-align:center;}
# .stat-val{font-size:20px;font-weight:800;color:var(--text);letter-spacing:-.3px;}
# .stat-lbl{font-size:10px;color:var(--text3);margin-top:2px;font-weight:600;text-transform:uppercase;letter-spacing:.08em;}

# /* ══ STREAMLIT OVERRIDES ══════════════════════════════════ */
# .stButton>button{
#   background:linear-gradient(135deg,var(--teal),var(--teal-d))!important;
#   color:#fff!important;border:none!important;border-radius:10px!important;
#   font-family:'Plus Jakarta Sans',sans-serif!important;
#   font-weight:700!important;font-size:13px!important;
#   padding:10px 24px!important;letter-spacing:.01em!important;
#   box-shadow:0 4px 12px rgba(13,148,136,.3)!important;
#   transition:all .15s!important;
# }
# .stButton>button:hover{transform:translateY(-1px)!important;box-shadow:0 6px 20px rgba(13,148,136,.4)!important;}
# div[data-testid="stSelectbox"]>label,
# div[data-testid="stTextInput"]>label{
#   font-size:12px!important;font-weight:700!important;
#   color:var(--text2)!important;text-transform:uppercase!important;letter-spacing:.06em!important;
# }
# [data-testid="stRadio"]>label{font-size:13px!important;font-weight:600!important;}
# .stRadio>div{gap:4px!important;}
# .stAlert{border-radius:12px!important;}
# div[data-testid="stTextInput"] input{
#   border-radius:10px!important;border-color:var(--border2)!important;
#   font-size:14px!important;font-family:'Plus Jakarta Sans',sans-serif!important;
# }
# div[data-testid="stSelectbox"]>div>div{
#   border-radius:10px!important;border-color:var(--border2)!important;
#   font-size:13px!important;
# }

# /* ══ LOGIN STREAMLIT INPUT OVERRIDES ═══════════════════════ */
# .login-page [data-testid="stTextInput"] input{
#   background:rgba(255,255,255,.08)!important;
#   border:1px solid rgba(255,255,255,.15)!important;
#   border-radius:10px!important;color:#fff!important;
#   font-size:14px!important;padding:12px 14px!important;
# }
# .login-page .stButton>button{
#   width:100%!important;padding:14px!important;font-size:15px!important;
# }

# /* ══ DIVIDER ══════════════════════════════════════════════ */
# .divider{height:1px;background:var(--border);margin:20px 0;}

# /* ══ METRIC OVERRIDES ═════════════════════════════════════ */
# [data-testid="stMetric"]{
#   background:var(--card);border-radius:12px;padding:16px 18px;
#   border:1px solid var(--border);box-shadow:var(--shadow);
# }
# [data-testid="stMetricLabel"]{font-size:11px!important;font-weight:700!important;color:var(--text3)!important;text-transform:uppercase!important;letter-spacing:.08em!important;}
# [data-testid="stMetricValue"]{font-size:24px!important;font-weight:800!important;color:var(--text)!important;letter-spacing:-.4px!important;}
# </style>
# """, unsafe_allow_html=True)

# # ══════════════════════════════════════════════════════════════
# #  INIT
# # ══════════════════════════════════════════════════════════════
# init_db()

# # ══════════════════════════════════════════════════════════════
# #  SESSION STATE
# # ══════════════════════════════════════════════════════════════
# USERS = {
#     "admin":    "1234"
# }

# for key, default in [
#     ("logged_in",      False),
#     ("user",           ""),
#     ("plant_selected", False),
#     ("sel_brands",     ["Solis"]),
#     ("sel_plants",     []),        # list of selected plant names
# ]:
#     if key not in st.session_state:
#         st.session_state[key] = default

# # ══════════════════════════════════════════════════════════════
# #  STEP 1 — LOGIN
# # ══════════════════════════════════════════════════════════════
# DARK_PAGE_CSS = """<style>
# [data-testid="stSidebar"]{display:none!important;}
# .block-container{padding:0!important;max-width:100%!important;}
# </style>"""

# if not st.session_state.logged_in:
#     st.markdown(DARK_PAGE_CSS, unsafe_allow_html=True)
#     st.markdown("""
#     <div style="min-height:100vh;display:flex;align-items:center;justify-content:center;
#     background:linear-gradient(135deg,#0a1628 0%,#0f2044 55%,#0d2b4e 100%);padding:20px;">
#       <div style="width:100%;max-width:420px;">
#         <div style="text-align:center;margin-bottom:32px;">
#           <div style="width:68px;height:68px;background:linear-gradient(135deg,#0d9488,#0f766e);
#             border-radius:18px;display:flex;align-items:center;justify-content:center;
#             font-size:32px;margin:0 auto 16px;box-shadow:0 8px 24px rgba(13,148,136,.4);">☀️</div>
#           <div style="font-size:26px;font-weight:800;color:#fff;letter-spacing:-.5px;">Solar Dashboard</div>
#           <div style="font-size:13px;color:#64748b;margin-top:6px;">Fractal Energy · Monitoring Platform</div>
#         </div>
#         <div style="background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.1);
#           border-radius:20px;padding:36px 32px;backdrop-filter:blur(20px);
#           box-shadow:0 20px 60px rgba(0,0,0,.4);">
#     """, unsafe_allow_html=True)
#     email    = st.text_input("Email Address", placeholder="your@email.com")
#     password = st.text_input("Password",      placeholder="••••••••", type="password")
#     if st.button("Sign In →", use_container_width=True):
#         if email in USERS and USERS[email] == password:
#             st.session_state.logged_in = True
#             st.session_state.user      = email
#             st.rerun()
#         else:
#             st.error("Invalid email or password.")
#     st.markdown("""<div style="text-align:center;margin-top:20px;font-size:12px;color:#475569;">
#       Secured by Fractal Energy · v2.0</div></div></div></div>""",
#     unsafe_allow_html=True)
#     st.stop()

# # ══════════════════════════════════════════════════════════════
# #  STEP 2 — PLANT SELECTOR  (shown once after login)
# # ══════════════════════════════════════════════════════════════
# if not st.session_state.plant_selected:
#     st.markdown(DARK_PAGE_CSS, unsafe_allow_html=True)

#     # Fetch available plants from all brands
#     @st.cache_data(ttl=600)
#     def _fetch_available_plants():
#         available = []
#         try:
#             from utils.solis_api import get_plants as _sp
#             for p in _sp():
#                 available.append({
#                     "brand": "Solis",
#                     "name":  p.get("stationName",""),
#                     "id":    p.get("id",""),
#                     "capacity": str(p.get("capacity","")) + " kWp",
#                 })
#         except Exception as e:
#             print(f"Plant selector Solis error: {e}")
#         try:
#             from utils.growatt_api import _get_plants, login as glogin
#             glogin()
#             for p in _get_plants():
#                 available.append({
#                     "brand": "Growatt",
#                     "name":  p.get("plantNameEncryption") or p.get("plantName",""),
#                     "id":    str(p.get("pId") or p.get("plantId","")),
#                     "capacity": str(p.get("nominalPower","")) + " W",
#                 })
#         except Exception as e:
#             print(f"Plant selector Growatt error: {e}")
#         return available

#     try:
#         with st.spinner("Loading available plants…"):
#             available_plants = _fetch_available_plants()
#     except Exception as e:
#         st.error(f"Error loading plants: {e}")
#         available_plants = []

#     # Group by brand
#     solis_plants   = [p for p in available_plants if p["brand"] == "Solis"]
#     growatt_plants = [p for p in available_plants if p["brand"] == "Growatt"]

#     # Plant selector UI
#     st.markdown(f"""
#     <div style="min-height:100vh;background:linear-gradient(135deg,#0a1628,#0f2044);
#     display:flex;align-items:center;justify-content:center;padding:32px 20px;">
#       <div style="width:100%;max-width:860px;">
#         <div style="text-align:center;margin-bottom:36px;">
#           <div style="width:60px;height:60px;background:linear-gradient(135deg,#0d9488,#0f766e);
#             border-radius:16px;display:flex;align-items:center;justify-content:center;
#             font-size:28px;margin:0 auto 14px;">☀</div>
#           <div style="font-size:24px;font-weight:800;color:#fff;letter-spacing:-.4px;">
#             Select Plants to Monitor</div>
#           <div style="font-size:13px;color:#64748b;margin-top:6px;">
#             Welcome, {st.session_state.user} · Choose which plants to include in your dashboard</div>
#         </div>
#       </div>
#     </div>
#     """, unsafe_allow_html=True)

#     # Brand tabs
#     brand_tabs = []
#     if solis_plants:   brand_tabs.append("☀️ Solis")
#     if growatt_plants: brand_tabs.append("⚡ Growatt")
#     if not brand_tabs:
#         st.warning("No plants found. Check credentials in config.py")
#         if st.button("Continue anyway"):
#             st.session_state.plant_selected = True
#             st.session_state.sel_brands     = ["Solis"]
#             st.session_state.sel_plants     = []
#             st.rerun()
#         st.stop()

#     sel_plant_names = []

#     if len(brand_tabs) > 1:
#         tabs = st.tabs(brand_tabs)
#     else:
#         tabs = [st.container()]

#     tab_idx = 0
#     if solis_plants:
#         with tabs[tab_idx]:
#             st.markdown("#### Solis Plants")
#             st.caption("Select all Solis plants you want to monitor:")
#             all_solis = st.checkbox("Select All Solis Plants", value=True, key="all_solis")
#             for p in solis_plants:
#                 checked = st.checkbox(
#                     f"🌱 {p['name']}  —  {p['capacity']}",
#                     value=all_solis, key=f"sp_{p['id']}"
#                 )
#                 if checked:
#                     sel_plant_names.append(p["name"])
#         tab_idx += 1

#     if growatt_plants:
#         with tabs[tab_idx]:
#             st.markdown("#### Growatt Plants")
#             st.caption("Select all Growatt plants you want to monitor:")
#             all_growatt = st.checkbox("Select All Growatt Plants", value=True, key="all_growatt")
#             for p in growatt_plants:
#                 checked = st.checkbox(
#                     f"⚡ {p['name']}  —  {p['capacity']}",
#                     value=all_growatt, key=f"gp_{p['id']}"
#                 )
#                 if checked:
#                     sel_plant_names.append(p["name"])

#     st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
#     col_a, col_b = st.columns([3,1])
#     with col_b:
#         if st.button("Continue to Dashboard →", use_container_width=True):
#             # Determine which brands are selected
#             active_brands = []
#             if any(p["name"] in sel_plant_names for p in solis_plants):
#                 active_brands.append("Solis")
#             if any(p["name"] in sel_plant_names for p in growatt_plants):
#                 active_brands.append("Growatt")
#             st.session_state.sel_brands     = active_brands or ["Solis"]
#             st.session_state.sel_plants     = sel_plant_names
#             st.session_state.plant_selected = True
#             st.cache_data.clear()
#             st.rerun()
#     with col_a:
#         st.caption(f"{len(sel_plant_names)} plant(s) selected")
#     st.stop()

# # ══════════════════════════════════════════════════════════════
# #  AUTHENTICATED APP
# # ══════════════════════════════════════════════════════════════
# st_autorefresh(interval=REFRESH_INTERVAL_SECONDS * 1000, key="solar_ar")

# # ── Helpers ──────────────────────────────────────────────────
# def f(v, d=1, na="—"):
#     try:    return f"{float(v):.{d}f}"
#     except: return na

# def badge(s, kind=None):
#     s  = (s or "").strip()
#     sl = s.lower()
#     if kind == "level":
#         cls = "b-critical" if sl == "critical" else "b-warning"
#     elif kind == "status_alarm":
#         cls = "b-active" if sl == "active" else "b-resolved"
#     else:
#         if sl == "online":              cls = "b-online"
#         elif sl in ("offline","fault"): cls = "b-offline"
#         else:                           cls = "b-unknown"
#     return f'<span class="badge {cls}">{s}</span>'

# def chip(b):
#     return f'<span class="chip chip-{(b or "").lower()}">{b}</span>'

# def earn(kwh):
#     v = float(kwh or 0) * RATE_PER_KWH
#     if v >= 1_000_000: return f"₹{v/1_000_000:.3f}M"
#     if v >= 1_000:     return f"₹{v/1_000:.3f}K"
#     return f"₹{v:.2f}"

# def chart_style(fig, h=300):
#     fig.update_layout(
#         plot_bgcolor="#fff", paper_bgcolor="#fff",
#         font_color="#64748b", font_family="Inter",
#         margin=dict(l=0,r=0,t=16,b=0), height=h,
#         legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=12, color="#64748b")),
#         bargap=0.28,
#     )
#     fig.update_traces(marker_line_width=0)
#     fig.update_xaxes(showgrid=False, zeroline=False, tickfont_size=11,
#                      tickfont_color="#94a3b8", linecolor="#e2e8f0")
#     fig.update_yaxes(showgrid=True, gridcolor="#f1f5f9", zeroline=False,
#                      tickfont_size=11, tickfont_color="#94a3b8")
#     return fig

# PALETTE = ["#0d9488","#f59e0b","#3b82f6","#f97316","#10b981","#8b5cf6","#06b6d4","#ec4899"]
# BRAND_COLORS = {"Solis":"#3b82f6","Growatt":"#10b981","Sungrow":"#f97316"}

# def sec(title, icon=""):
#     st.markdown(f'<div class="sec-hdr"><div class="sec-hdr-dot"></div>{icon} {title}</div>',
#                 unsafe_allow_html=True)

# # ── Sidebar — only shown in main dashboard ───────────────────
# with st.sidebar:
#     st.markdown(f"""
#     <div class="sb-logo">
#       <div class="sb-logo-icon">☀</div>
#       <div>
#         <div class="sb-logo-title">Solar Dashboard</div>
#         <div class="sb-logo-sub">Fractal Energy</div>
#       </div>
#     </div>""", unsafe_allow_html=True)

#     if not st.session_state.get("plant_selected", False):
#         # Minimal sidebar during plant selection
#         st.markdown("<div style='color:#64748b;padding:20px;font-size:13px;'>Select plants to continue…</div>",
#                     unsafe_allow_html=True)
#         page = "Overview"
#         sel_brands = st.session_state.get("sel_brands", ["Solis"])
#         sel_plants = []
#         show_debug = False
#     else:
#         page = st.radio("", ["📊  Overview","🔧  O&M","📈  Report","🗺  Service","⚙️  Settings"],
#                         label_visibility="collapsed")
#         page = page.split("  ",1)[1].strip()

#         st.markdown('<div class="sb-section">Active Plants</div>', unsafe_allow_html=True)
#         sel_brands = st.session_state.get("sel_brands", ["Solis"])
#         sel_plants = st.session_state.get("sel_plants", [])
#         for b in sel_brands:
#             st.markdown(f'<div style="color:#94a3b8;font-size:12px;padding:4px 20px;">'
#                         f'{"☀️" if b=="Solis" else "⚡" if b=="Growatt" else "🔆"} {b}</div>',
#                         unsafe_allow_html=True)
#         if st.button("🔀  Change Plants"):
#             st.session_state.plant_selected = False
#             st.cache_data.clear()
#             st.rerun()

#         st.markdown('<div style="height:6px"></div>', unsafe_allow_html=True)
#         if st.button("🔄  Refresh Now"):
#             st.cache_data.clear(); st.rerun()

#         show_debug = st.checkbox("🔍  Debug", value=False)

#         st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)
#         if st.button("🚪  Sign Out"):
#             st.session_state.logged_in = False
#             st.rerun()

#         st.markdown(f"""
#         <div class="sb-time">
#           ⏱ {datetime.now().strftime('%d %b %Y')}<br>
#           <b style="color:#94a3b8;">{datetime.now().strftime('%H:%M:%S')}</b><br>
#           <span style="color:#334155;">Auto-refresh {REFRESH_INTERVAL_SECONDS//60} min</span>
#         </div>""", unsafe_allow_html=True)

# # ── Fetch data (only when plant_selected) ────────────────────
# if not st.session_state.get("plant_selected", False):
#     st.stop()

# sel_plants = st.session_state.get("sel_plants", [])

# @st.cache_data(ttl=REFRESH_INTERVAL_SECONDS)
# def load(brands, plants):
#     result = fetch_all_brands(list(brands))
#     if not result:
#         raise RuntimeError("empty")
#     # Filter to selected plants if specified
#     if plants:
#         result = [r for r in result if r.get("plant_name") in plants]
#     return result

# with st.spinner("Fetching live data…"):
#     try:
#         records = load(tuple(sel_brands), tuple(sel_plants))
#     except Exception:
#         records = fetch_all_brands(list(sel_brands))
#         if sel_plants:
#             records = [r for r in records if r.get("plant_name") in sel_plants]
#         if not records:
#             st.cache_data.clear()

# alerts = check_alerts(records, st.session_state)

# df = pd.DataFrame()
# if records:
#     df = pd.DataFrame(records)
#     for c in ["power_kw","today_kwh","total_kwh","temperature","voltage","current_a"]:
#         if c in df.columns:
#             df[c] = pd.to_numeric(df[c], errors="coerce")
#     if "status" in df.columns:
#         df["status"] = df["status"].astype(str).str.strip()

# # ── Debug ─────────────────────────────────────────────────────
# if show_debug and not df.empty:
#     st.markdown("### 🔍 Debug: Raw API Data")
#     st.dataframe(df, use_container_width=True)
#     try:
#         from utils.solis_api import fetch_summary as _fsum, _raw_plants_cache
#         summ = _fsum()
#         st.write("**fetch_summary():**", summ)
#     except Exception as ex:
#         st.error(f"Debug error: {ex}")
#     st.divider()


# # ══════════════════════════════════════════════════════════════
# #  OVERVIEW
# # ══════════════════════════════════════════════════════════════
# if page == "Overview":
#     st.markdown('<div class="page-hdr"><h1>Plant Overview</h1>'
#                 '<p>Real-time performance across all plants</p></div>',
#                 unsafe_allow_html=True)

#     if df.empty:
#         st.warning("⚠️ No data. Check credentials in config.py and click Refresh.")
#         st.stop()

#     # ── KPI values ────────────────────────────────────────────
#     total_power = float(df["power_kw"].sum())
#     daily_kwh   = float(df["today_kwh"].sum())
#     total_mwh   = float(df["total_kwh"].sum())
#     monthly_mwh = 0.0

#     try:
#         if "Solis" in sel_brands:
#             from utils.solis_api import fetch_summary as _fs
#             summ = _fs()
#             if summ.get("power_kw",    0) > 0: total_power = float(summ["power_kw"])
#             # daily_kwh: use df sum (inverterList etoday) — most accurate per-inverter value
#             # fetch_summary dayEnergy can be partial; df["today_kwh"].sum() is always correct
#             if summ.get("monthly_mwh", 0) > 0: monthly_mwh = float(summ["monthly_mwh"])
#             if summ.get("total_mwh",   0) > 0: total_mwh   = float(summ["total_mwh"])
#     except Exception: pass

#     # Always use inverter-level sum for daily yield — it's the most accurate
#     # (confirmed: df sum = 1697.5 kWh matches Solis, API dayEnergy can lag)
#     daily_kwh = float(df["today_kwh"].sum())

#     if monthly_mwh == 0:
#         hist = get_history(hours=720)
#         monthly_kwh_db = daily_kwh
#         if not hist.empty and "today_kwh" in hist.columns:
#             hist["fetched_at"] = pd.to_datetime(hist["fetched_at"])
#             hist["today_kwh"]  = pd.to_numeric(hist["today_kwh"], errors="coerce")
#             m = hist[hist["fetched_at"].dt.month == datetime.now().month]
#             if not m.empty:
#                 v = float(m.groupby([m["fetched_at"].dt.date,"inverter_sn"])["today_kwh"].max().sum())
#                 monthly_kwh_db = max(v, daily_kwh)
#         monthly_mwh = monthly_kwh_db / 1000
#     monthly_kwh = monthly_mwh * 1000

#     # Display units
#     daily_val,daily_unit = (f(daily_kwh/1000,3),"MWh") if daily_kwh>=1000 else (f(daily_kwh,1),"kWh")
#     mo_val,mo_unit       = f(monthly_mwh,3), "MWh"
#     if total_mwh >= 1000:
#         tot_val,tot_unit,tot_earn = f(total_mwh/1000,3),"GWh",total_mwh*1000
#     else:
#         tot_val,tot_unit,tot_earn = f(total_mwh,3),"MWh",total_mwh*1000

#     n_on  = int((df["status"].str.lower()=="online").sum())
#     n_tot = len(df)

#     # ── 4 KPI cards ──────────────────────────────────────────
#     c1,c2,c3,c4 = st.columns(4)
#     kpis = [
#         (c1,"teal","teal","⚡","Power",f(total_power,2),"kW",
#          f"Inverters: <b>{n_on}/{n_tot} online</b>"),
#         (c2,"amber","amber","🔋","Daily Yield",daily_val,daily_unit,
#          f"Earning today: <b>{earn(daily_kwh)}</b>"),
#         (c3,"green","green","📅","Monthly Yield",mo_val,mo_unit,
#          f"Earning this month: <b>{earn(monthly_kwh)}</b>"),
#         (c4,"navy","navy","📊","Total Yield",tot_val,tot_unit,
#          f"Total earning: <b>{earn(tot_earn)}</b>"),
#     ]
#     for col,card_cls,ico_cls,ico,lbl,val,unit,meta in kpis:
#         with col:
#             st.markdown(f"""
#             <div class="kpi-card {card_cls}">
#               <div class="kpi-icon {ico_cls}">{ico}</div>
#               <div>
#                 <div class="kpi-label">{lbl}</div>
#                 <div class="kpi-value">{val}<span class="kpi-unit"> {unit}</span></div>
#                 <div class="kpi-meta">{meta}</div>
#               </div>
#             </div>""", unsafe_allow_html=True)

#     st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)

#     # ── Alert strips ─────────────────────────────────────────
#     if alerts:
#         for a in alerts[:3]:
#             st.markdown(f"""
#             <div class="alert-strip">
#               <div class="alert-strip-ico">🚨</div>
#               <div>
#                 <div class="alert-strip-ttl">{a['plant_name']} — {a.get('inverter_sn','')}</div>
#                 <div class="alert-strip-msg">{a['issue']}</div>
#               </div>
#             </div>""", unsafe_allow_html=True)

#     # ── Charts ───────────────────────────────────────────────
#     ch1, ch2 = st.columns([3, 2])

#     with ch1:
#         sec("Power by Plant (kW)")
#         pdf = df.groupby(["plant_name","brand"])["power_kw"].sum().reset_index()
#         fig = px.bar(pdf, x="plant_name", y="power_kw", color="brand",
#                      color_discrete_map=BRAND_COLORS,
#                      labels={"power_kw":"Power (kW)","plant_name":"","brand":"Brand"})
#         fig.update_traces(marker_cornerradius=4)
#         st.plotly_chart(chart_style(fig, 290), use_container_width=True)

#     with ch2:
#         sec("Daily Yield Share")
#         pief = df.groupby("plant_name")["today_kwh"].sum().reset_index()
#         fig2 = go.Figure(go.Pie(
#             labels=pief["plant_name"],
#             values=pief["today_kwh"],
#             hole=0.52,
#             marker=dict(colors=PALETTE, line=dict(color="#fff", width=2)),
#             textposition="outside",
#             textinfo="label+percent",
#             textfont=dict(size=11, family="Plus Jakarta Sans"),
#             pull=[0.04]*len(pief),
#         ))
#         fig2.update_layout(
#             plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
#             font_family="Inter", font_color="#64748b",
#             margin=dict(l=60, r=60, t=20, b=20), height=290,
#             showlegend=False,
#             annotations=[dict(text=f"<b>{f(pief['today_kwh'].sum(),1)}</b><br>kWh",
#                               font=dict(size=14,color="#0f172a",family="Plus Jakarta Sans"),
#                               showarrow=False)]
#         )
#         st.plotly_chart(fig2, use_container_width=True)

#     # ── Plant table ──────────────────────────────────────────
#     sec("Plant List")
#     ps = (df.groupby(["plant_name","brand"])
#           .agg(power_kw=("power_kw","sum"), today_kwh=("today_kwh","sum"),
#                total_kwh=("total_kwh","sum"), inv_count=("inverter_sn","count"))
#           .reset_index())

#     st.markdown('<div class="tbl">', unsafe_allow_html=True)
#     st.markdown(
#         '<div class="tbl-hdr tbl-plant">'
#         '<div>Plant Name</div><div>Brand</div><div>Inverters</div>'
#         '<div>Power (kW)</div><div>Daily Yield</div>'
#         '<div>Total Yield</div><div>Earning Today</div><div>Status</div>'
#         '</div>', unsafe_allow_html=True)

#     for _, row in ps.iterrows():
#         pr   = df[df["plant_name"]==row["plant_name"]]
#         on   = int((pr["status"].str.lower()=="online").sum())
#         tot  = int(row["inv_count"])
#         pst  = "Online" if on==tot and tot>0 else ("Offline" if on==0 else "Warning")
#         dy   = float(row["today_kwh"] or 0)
#         dy_s = f"{dy/1000:.3f} MWh" if dy>=1000 else f"{dy:.1f} kWh"
#         ty   = float(row["total_kwh"] or 0)
#         ty_s = f"{ty/1000:.3f} GWh" if ty>=1000 else f"{ty:.3f} MWh"
#         st.markdown(
#             f'<div class="tbl-row tbl-plant">'
#               f'<div class="cell-link">{row["plant_name"]}</div>'
#               f'<div>{chip(row["brand"])}</div>'
#               f'<div>{on}/{tot}</div>'
#               f'<div><b>{f(row["power_kw"],2)}</b> kW</div>'
#               f'<div>{dy_s}</div><div>{ty_s}</div>'
#               f'<div>{earn(dy)}</div><div>{badge(pst)}</div>'
#             f'</div>', unsafe_allow_html=True)
#     st.markdown('</div>', unsafe_allow_html=True)


# # ══════════════════════════════════════════════════════════════
# #  O&M
# # ══════════════════════════════════════════════════════════════
# elif page == "O&M":
#     sub = st.radio("", ["🔔  Alarm Information","⚡  Device Overview"],
#                    horizontal=True, label_visibility="collapsed")
#     sub = sub.split("  ",1)[1].strip()
#     st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

#     alarm_log = get_alert_log(200)
#     all_alarms = []
#     for a in alerts:
#         all_alarms.append({"device_type":"Inverter","level":"Critical","status":"Active",
#             "plant_name":a.get("plant_name","—"),"sn":a.get("inverter_sn","—"),
#             "content":a.get("issue","—"),"brand":a.get("brand","—"),
#             "time":datetime.now().strftime("%Y-%m-%d %H:%M")})
#     if not alarm_log.empty:
#         for _, r in alarm_log.iterrows():
#             all_alarms.append({"device_type":"Inverter","level":"Warning","status":"Resolved",
#                 "plant_name":r.get("plant_name","—"),"sn":r.get("inverter_sn","—"),
#                 "content":r.get("issue","—"),"brand":r.get("brand","—"),
#                 "time":r.get("alerted_at","—")})

#     if sub == "Alarm Information":
#         st.markdown('<div class="page-hdr"><h1>Alarm Information</h1>'
#                     '<p>Fault detection and alert history</p></div>',
#                     unsafe_allow_html=True)

#         plant_opts = ["All"] + sorted(df["plant_name"].dropna().unique()) if not df.empty else ["All"]
#         sn_opts    = ["All"] + sorted(df["inverter_sn"].dropna().unique()) if not df.empty else ["All"]
#         brand_opts = ["All"] + sorted(df["brand"].dropna().unique())       if not df.empty else ["All"]

#         fc1,fc2,fc3,fc4,fc5 = st.columns(5)
#         with fc1: fp = st.selectbox("Plant Name",  plant_opts)
#         with fc2: fs = st.selectbox("S/N",         sn_opts)
#         with fc3: fb = st.selectbox("Brand",        brand_opts)
#         with fc4: fst= st.selectbox("Status",       ["All","Active","Resolved"])
#         with fc5: fl = st.selectbox("Level",        ["All","Critical","Warning"])

#         filt = all_alarms[:]
#         if fp !="All": filt=[a for a in filt if a["plant_name"]==fp]
#         if fs !="All": filt=[a for a in filt if a["sn"]        ==fs]
#         if fb !="All": filt=[a for a in filt if a["brand"]     ==fb]
#         if fst!="All": filt=[a for a in filt if a["status"]    ==fst]
#         if fl !="All": filt=[a for a in filt if a["level"]     ==fl]

#         m1,m2,m3 = st.columns(3)
#         m1.metric("Total", len(filt))
#         m2.metric("Active",   sum(1 for a in filt if a["status"]=="Active"))
#         m3.metric("Resolved", sum(1 for a in filt if a["status"]=="Resolved"))

#         if not filt:
#             st.success("✅ No alarms — all systems operating normally.")
#         else:
#             st.markdown('<div class="tbl">', unsafe_allow_html=True)
#             st.markdown('<div class="tbl-hdr tbl-alarm">'
#                         '<div>Device</div><div>Level</div><div>Status</div>'
#                         '<div>Plant</div><div>S/N</div><div>Issue</div><div>Time</div>'
#                         '</div>', unsafe_allow_html=True)
#             for a in filt:
#                 st.markdown(
#                     f'<div class="tbl-row tbl-alarm">'
#                       f'<div>{a["device_type"]}</div>'
#                       f'<div>{badge(a["level"],"level")}</div>'
#                       f'<div>{badge(a["status"],"status_alarm")}</div>'
#                       f'<div>{chip(a["brand"])} {a["plant_name"]}</div>'
#                       f'<div style="font-size:11px;color:var(--text3);font-family:\'JetBrains Mono\',monospace;">{a["sn"]}</div>'
#                       f'<div>{a["content"]}</div>'
#                       f'<div style="font-size:11px;color:var(--text3);">{a["time"]}</div>'
#                     f'</div>', unsafe_allow_html=True)
#             st.markdown('</div>', unsafe_allow_html=True)

#     else:
#         st.markdown('<div class="page-hdr"><h1>Device Overview</h1>'
#                     '<p>Live readings for every inverter</p></div>',
#                     unsafe_allow_html=True)
#         if df.empty:
#             st.warning("⚠️ No data."); st.stop()

#         fc1,fc2,fc3,fc4 = st.columns(4)
#         with fc1: bf = st.selectbox("Brand",  ["All"]+sorted(df["brand"].dropna().unique()),       key="do_b")
#         with fc2: pf = st.selectbox("Plant",  ["All"]+sorted(df["plant_name"].dropna().unique()),  key="do_p")
#         with fc3: sf = st.selectbox("S/N",    ["All"]+sorted(df["inverter_sn"].dropna().unique()), key="do_s")
#         with fc4: stf= st.selectbox("Status", ["All"]+sorted(df["status"].dropna().unique()),      key="do_st")

#         vw = df.copy()
#         if bf !="All": vw=vw[vw["brand"]       ==bf]
#         if pf !="All": vw=vw[vw["plant_name"]  ==pf]
#         if sf !="All": vw=vw[vw["inverter_sn"] ==sf]
#         if stf!="All": vw=vw[vw["status"]      ==stf]

#         st.markdown(
#             f'<div class="stat-row">'
#               f'<div class="stat-item"><div class="stat-val">{len(vw)}</div><div class="stat-lbl">Inverters</div></div>'
#               f'<div class="stat-item"><div class="stat-val">{f(vw["power_kw"].sum(),2)} kW</div><div class="stat-lbl">Total Power</div></div>'
#               f'<div class="stat-item"><div class="stat-val">{f(vw["today_kwh"].sum(),1)} kWh</div><div class="stat-lbl">Daily Yield</div></div>'
#               f'<div class="stat-item"><div class="stat-val">{int((vw["status"].str.lower()=="online").sum())}</div><div class="stat-lbl">Online</div></div>'
#             f'</div>', unsafe_allow_html=True)

#         alert_sns = {a.get("inverter_sn") for a in alerts}
#         for _, row in vw.iterrows():
#             sn    = str(row.get("inverter_sn","N/A"))
#             brand = str(row.get("brand",""))
#             st_   = str(row.get("status",""))
#             params = [
#                 ("Power Now",   f(row.get("power_kw"),2),  "kW"),
#                 ("Daily Yield", f(row.get("today_kwh"),1), "kWh"),
#                 ("Total Yield", f(row.get("total_kwh"),3), "MWh"),
#                 ("Temperature", f(row.get("temperature"),1),"°C"),
#                 ("AC Voltage",  f(row.get("voltage"),1),   "V"),
#                 ("AC Current",  f(row.get("current_a"),1), "A"),
#             ]
#             p_html = "".join(
#                 f'<div><div class="param-label">{l}</div>'
#                 f'<div class="param-val">{v}<span class="param-unit"> {u}</span></div></div>'
#                 for l,v,u in params)
#             border = "border-left:3px solid var(--red);" if sn in alert_sns else ""
#             st.markdown(
#                 f'<div class="inv-card" style="{border}">'
#                   f'<div class="inv-header">'
#                     f'<div><div class="inv-name">{row.get("plant_name","")}</div>'
#                     f'<div class="inv-meta">S/N: {sn} · {chip(brand)} · {row.get("last_update","—")}</div></div>'
#                     + badge(st_) +
#                   f'</div>'
#                   f'<div class="inv-params">{p_html}</div>'
#                 f'</div>', unsafe_allow_html=True)


# # ══════════════════════════════════════════════════════════════
# #  REPORT  — pulls historical data from Solis API directly
# # ══════════════════════════════════════════════════════════════
# elif page == "Report":
#     st.markdown('<div class="page-hdr"><h1>Plant Report</h1>'
#                 '<p>Historical generation data from Solis Cloud</p></div>',
#                 unsafe_allow_html=True)

#     rtype = st.radio("", ["Daily","Monthly","Annual","Total"],
#                      horizontal=True, label_visibility="collapsed")
#     st.markdown('<div style="height:10px"></div>', unsafe_allow_html=True)

#     # Plant selector — always from live df
#     plant_opts = (["All Plants"] + sorted(df["plant_name"].dropna().unique().tolist())
#                   if not df.empty else ["No data"])

#     fc1, fc2 = st.columns([2, 1])
#     with fc1: sel_plant = st.selectbox("Select Plant", plant_opts)
#     with fc2: sel_date  = st.date_input("Date", value=date.today())

#     # Shared line chart helper
#     def line_chart(fig, h=360):
#         fig = chart_style(fig, h)
#         fig.update_traces(selector=dict(type="scatter"), line=dict(width=2.5))
#         fig.update_layout(hovermode="x unified")
#         return fig

#     # Get plant IDs for selected plant
#     from utils.solis_api import (get_plants as _get_solis_plants,
#                                   get_all_plants_daily, get_all_plants_monthly,
#                                   get_plant_daily_history   as solis_daily,
#                                   get_plant_monthly_history as solis_monthly)
#     from utils.growatt_api import (get_plant_daily_history   as growatt_daily,
#                                    get_plant_monthly_history as growatt_monthly,
#                                    _get_plants               as _get_growatt_plants)

#     @st.cache_data(ttl=300)
#     def _plants_cached():
#         plants = []
#         try:
#             for p in _get_solis_plants():
#                 plants.append({"name": p.get("stationName"), "id": p.get("id"), "brand": "Solis"})
#         except Exception: pass
#         try:
#             for p in _get_growatt_plants():
#                 pid   = str(p.get("pId") or p.get("plantId",""))
#                 pname = p.get("plantNameEncryption") or p.get("plantName","")
#                 plants.append({"name": pname, "id": pid, "brand": "Growatt"})
#         except Exception: pass
#         return plants

#     all_plants    = _plants_cached()
#     plant_id_map  = {p["name"]: (p["id"], p["brand"]) for p in all_plants}

#     def get_daily_history(plant_name, month_str):
#         info = plant_id_map.get(plant_name)
#         if not info: return []
#         pid, brand = info
#         if brand == "Growatt": return growatt_daily(pid, month_str)
#         return solis_daily(pid, month_str)

#     def get_monthly_history(plant_name, year_str):
#         info = plant_id_map.get(plant_name)
#         if not info: return []
#         pid, brand = info
#         if brand == "Growatt": return growatt_monthly(pid, year_str)
#         return solis_monthly(pid, year_str)

#     # ── DAILY ────────────────────────────────────────────────
#     if rtype == "Daily":
#         # Determine brand of selected plant
#         sel_brand_for_report = "Solis"
#         if sel_plant != "All Plants":
#             info = plant_id_map.get(sel_plant)
#             if info: sel_brand_for_report = info[1]

#         # For Growatt: use stationDay API (has per-day hourly data)
#         # For Solis: use local DB (5-min readings collected by the app)
#         if sel_brand_for_report == "Growatt" and sel_plant != "All Plants":
#             month_str_d = sel_date.strftime("%Y-%m")
#             with st.spinner("Fetching daily data from Growatt…"):
#                 rows = get_daily_history(sel_plant, month_str_d)

#             if not rows:
#                 st.info(f"No data returned from Growatt for {sel_date.strftime('%B %Y')}.")
#             else:
#                 # Filter to selected date
#                 day_rows = [r for r in rows if r.get("date","").startswith(str(sel_date))]
#                 if not day_rows:
#                     # Show full month as fallback
#                     day_rows = rows
#                     st.info(f"Showing full month data — no hourly breakdown available for {sel_date}.")

#                 daily_df = pd.DataFrame(day_rows)
#                 daily_df["date"] = pd.to_datetime(daily_df["date"], errors="coerce")
#                 daily_df = daily_df.dropna(subset=["date"]).sort_values("date")

#                 sec(f"Daily Generation — {sel_plant} ({sel_date.strftime('%B %Y')})")
#                 fig = go.Figure()
#                 fig.add_trace(go.Bar(
#                     x=daily_df["date"], y=daily_df["energy_kwh"],
#                     name="Yield (kWh)", marker_color="rgba(16,185,129,.25)",
#                     marker_line_width=0,
#                 ))
#                 fig.add_trace(go.Scatter(
#                     x=daily_df["date"], y=daily_df["energy_kwh"],
#                     name="Yield", mode="lines+markers",
#                     line=dict(color="#10b981", width=2.5),
#                     marker=dict(size=6, color="#10b981"),
#                 ))
#                 fig.update_layout(
#                     plot_bgcolor="#fff", paper_bgcolor="#fff",
#                     font_family="Inter", font_color="#64748b",
#                     margin=dict(l=0,r=0,t=16,b=0), height=360,
#                     hovermode="x unified", bargap=0.25,
#                     legend=dict(bgcolor="rgba(0,0,0,0)"),
#                     yaxis=dict(title="kWh", showgrid=True, gridcolor="#f1f5f9", zeroline=False),
#                 )
#                 fig.update_xaxes(showgrid=False, zeroline=False, tickformat="%d %b")
#                 st.plotly_chart(fig, use_container_width=True)

#                 tot = daily_df["energy_kwh"].sum()
#                 c1,c2 = st.columns(2)
#                 c1.metric("Month Total", f"{tot:.1f} kWh")
#                 c2.metric("Estimated Earning", earn(tot))

#         else:
#             # Solis / All Plants — use local DB (5-min power readings)
#             hist_df = get_history(hours=8760)
#             if hist_df.empty:
#                 st.info("📭 No intraday data yet — the app collects readings every 5 min. "
#                         "Come back after the app has been running for a while.")
#             else:
#                 hist_df["fetched_at"] = pd.to_datetime(hist_df["fetched_at"])
#                 hist_df["power_kw"]   = pd.to_numeric(hist_df["power_kw"],  errors="coerce")
#                 hist_df["today_kwh"]  = pd.to_numeric(hist_df["today_kwh"], errors="coerce")
#                 if sel_plant != "All Plants":
#                     hist_df = hist_df[hist_df["plant_name"] == sel_plant]

#                 day = hist_df[hist_df["fetched_at"].dt.date == sel_date].sort_values("fetched_at")
#                 if day.empty:
#                     st.info(f"No intraday data for {sel_date}. "
#                             f"Try today's date — data builds up every 5 minutes the app is running.")
#                 else:
#                     sec("Power Output Throughout the Day (kW)")
#                     fig = px.line(day, x="fetched_at", y="power_kw", color="inverter_sn",
#                                   color_discrete_sequence=PALETTE,
#                                   labels={"fetched_at":"Time","power_kw":"Power (kW)",
#                                           "inverter_sn":"Inverter"})
#                     st.plotly_chart(line_chart(fig, 360), use_container_width=True)

#                     sec("Peak Power & Daily Generation per Inverter")
#                     sm = (day.groupby(["plant_name","inverter_sn","brand"])
#                           .agg(Peak_kW=("power_kw","max"), Daily_kWh=("today_kwh","max"))
#                           .reset_index()
#                           .rename(columns={"plant_name":"Plant","inverter_sn":"S/N","brand":"Brand"}))
#                     st.dataframe(sm, use_container_width=True, hide_index=True)

#     # ── MONTHLY ───────────────────────────────────────────────
#     elif rtype == "Monthly":
#         month_str = sel_date.strftime("%Y-%m")

#         with st.spinner(f"Fetching daily data for {sel_date.strftime('%B %Y')}…"):
#             if sel_plant == "All Plants":
#                 api_df = get_all_plants_daily(month_str)
#                 if not api_df.empty:
#                     daily = (api_df.groupby("date")["energy_kwh"]
#                              .sum().reset_index())
#                     daily.columns = ["Date","Daily Yield (kWh)"]
#                     income_df = api_df.groupby("date")["income"].sum().reset_index()
#                     income_df.columns = ["Date","Income (INR)"]
#                     daily = daily.merge(income_df, on="Date", how="left")
#                 else:
#                     daily = pd.DataFrame()
#             else:
#                 rows = get_daily_history(sel_plant, month_str)
#                 if rows:
#                     daily = pd.DataFrame(rows).rename(columns={
#                         "date":"Date","energy_kwh":"Daily Yield (kWh)","income":"Income (INR)"})
#                     daily["Date"] = pd.to_datetime(daily["Date"], errors="coerce")
#                 else:
#                     daily = pd.DataFrame()

#         if daily.empty or "Daily Yield (kWh)" not in daily.columns:
#             st.info(f"No data from Solis API for {sel_date.strftime('%B %Y')}.")
#         else:
#             daily = daily.dropna(subset=["Date"]).sort_values("Date")

#             # Combined bar + line chart matching Solis style
#             sec(f"Daily Generation — {sel_date.strftime('%B %Y')}")
#             fig = go.Figure()
#             # Bar: yield
#             fig.add_trace(go.Bar(
#                 x=daily["Date"], y=daily["Daily Yield (kWh)"],
#                 name="Yield (kWh)", marker_color="rgba(13,148,136,.25)",
#                 marker_line_width=0,
#             ))
#             # Line: yield trend
#             fig.add_trace(go.Scatter(
#                 x=daily["Date"], y=daily["Daily Yield (kWh)"],
#                 name="Yield", mode="lines+markers",
#                 line=dict(color="#0d9488", width=2.5),
#                 marker=dict(size=5, color="#0d9488"),
#             ))
#             # Line: revenue (right axis)
#             if "Income (INR)" in daily.columns:
#                 fig.add_trace(go.Scatter(
#                     x=daily["Date"], y=daily["Income (INR)"],
#                     name="Revenue (INR)", mode="lines+markers",
#                     line=dict(color="#f59e0b", width=2, dash="dot"),
#                     marker=dict(size=5, color="#f59e0b"),
#                     yaxis="y2",
#                 ))
#             fig.update_layout(
#                 plot_bgcolor="#fff", paper_bgcolor="#fff",
#                 font_family="Inter", font_color="#64748b",
#                 margin=dict(l=0,r=60,t=16,b=0), height=380,
#                 hovermode="x unified", bargap=0.25,
#                 legend=dict(bgcolor="rgba(0,0,0,0)", orientation="h",
#                             yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
#                 yaxis=dict(title="kWh", showgrid=True, gridcolor="#f1f5f9",
#                            zeroline=False, tickfont_size=11),
#                 yaxis2=dict(title="INR", overlaying="y", side="right",
#                             showgrid=False, zeroline=False, tickfont_size=11),
#             )
#             fig.update_xaxes(showgrid=False, zeroline=False, tickfont_size=11,
#                              tickformat="%d", dtick="D1")
#             st.plotly_chart(fig, use_container_width=True)

#             tot = daily["Daily Yield (kWh)"].sum()
#             m1,m2,m3 = st.columns(3)
#             m1.metric("Month Total", f"{tot:.1f} kWh")
#             m2.metric("Month Total (MWh)", f"{tot/1000:.3f} MWh")
#             m3.metric("Estimated Earning", earn(tot))

#     # ── ANNUAL ────────────────────────────────────────────────
#     elif rtype == "Annual":
#         year_str = str(sel_date.year)

#         with st.spinner(f"Fetching monthly data for {year_str}…"):
#             if sel_plant == "All Plants":
#                 api_df = get_all_plants_monthly(year_str)
#                 if not api_df.empty:
#                     monthly = (api_df.groupby("month")["energy_kwh"]
#                                .sum().reset_index())
#                     monthly.columns = ["Month","kWh"]
#                 else:
#                     monthly = pd.DataFrame()
#             else:
#                 rows = get_monthly_history(sel_plant, year_str)
#                 if rows:
#                     monthly = pd.DataFrame(rows).rename(columns={"month":"Month","energy_kwh":"kWh"})
#                 else:
#                     monthly = pd.DataFrame()

#         if monthly.empty or "kWh" not in monthly.columns:
#             st.info(f"No data from Solis API for {year_str}.")
#         else:
#             monthly = monthly[monthly["kWh"] > 0]

#             sec(f"Monthly Generation — {year_str}")
#             fig = go.Figure()
#             fig.add_trace(go.Bar(
#                 x=monthly["Month"], y=monthly["kWh"],
#                 name="Yield (kWh)", marker_color="rgba(245,158,11,.3)",
#                 marker_line_width=0,
#             ))
#             fig.add_trace(go.Scatter(
#                 x=monthly["Month"], y=monthly["kWh"],
#                 name="Trend", mode="lines+markers",
#                 line=dict(color="#f59e0b", width=2.5),
#                 marker=dict(size=7, color="#f59e0b"),
#             ))
#             fig.update_layout(
#                 plot_bgcolor="#fff", paper_bgcolor="#fff",
#                 font_family="Inter", font_color="#64748b",
#                 margin=dict(l=0,r=0,t=16,b=0), height=360,
#                 hovermode="x unified", bargap=0.3,
#                 legend=dict(bgcolor="rgba(0,0,0,0)"),
#                 yaxis=dict(showgrid=True, gridcolor="#f1f5f9",
#                            zeroline=False, tickfont_size=11),
#             )
#             fig.update_xaxes(showgrid=False, zeroline=False, tickfont_size=11)
#             st.plotly_chart(fig, use_container_width=True)

#             tot_yr = monthly["kWh"].sum()
#             m1,m2,m3 = st.columns(3)
#             m1.metric("Year Total", f"{tot_yr:.1f} kWh")
#             m2.metric("Year Total (MWh)", f"{tot_yr/1000:.3f} MWh")
#             m3.metric("Est. Annual Earning", earn(tot_yr))

#     # ── TOTAL ─────────────────────────────────────────────────
#     else:
#         sec("Total Yield per Plant (All-time)")
#         if not df.empty:
#             gt = (df.groupby(["plant_name","brand"])
#                   .agg(total_mwh=("total_kwh","sum"), daily_kwh=("today_kwh","sum"))
#                   .reset_index())

#             fig = go.Figure()
#             for i, row in gt.iterrows():
#                 fig.add_trace(go.Bar(
#                     x=[row["plant_name"]], y=[row["total_mwh"]],
#                     name=row["plant_name"],
#                     marker_color=PALETTE[i % len(PALETTE)],
#                     marker_line_width=0,
#                 ))
#             fig.update_layout(
#                 plot_bgcolor="#fff", paper_bgcolor="#fff",
#                 font_family="Inter", font_color="#64748b",
#                 margin=dict(l=0,r=0,t=16,b=0), height=340,
#                 showlegend=False, bargap=0.35,
#                 yaxis=dict(title="MWh", showgrid=True, gridcolor="#f1f5f9",
#                            zeroline=False, tickfont_size=11),
#             )
#             fig.update_xaxes(showgrid=False, zeroline=False, tickfont_size=11)
#             st.plotly_chart(fig, use_container_width=True)

#             gt_disp = gt.rename(columns={"plant_name":"Plant","brand":"Brand",
#                                           "total_mwh":"Total Yield (MWh)",
#                                           "daily_kwh":"Today (kWh)"})
#             st.dataframe(gt_disp, use_container_width=True, hide_index=True)


# # ══════════════════════════════════════════════════════════════
# #  SERVICE
# # ══════════════════════════════════════════════════════════════
# elif page == "Service":
#     st.markdown('<div class="page-hdr"><h1>Plant Management</h1>'
#                 '<p>All registered plants and operational details</p></div>',
#                 unsafe_allow_html=True)
#     if df.empty:
#         st.warning("⚠️ No data."); st.stop()

#     fc1,fc2 = st.columns(2)
#     with fc1: pf2 = st.selectbox("Plant", ["All"]+sorted(df["plant_name"].dropna().unique()), key="pm_p")
#     with fc2: bf2 = st.selectbox("Brand", ["All"]+sorted(df["brand"].dropna().unique()),      key="pm_b")

#     ps = (df.groupby(["plant_name","brand"])
#           .agg(power_kw=("power_kw","sum"), today_kwh=("today_kwh","sum"),
#                total_kwh=("total_kwh","sum"), inv_count=("inverter_sn","count"))
#           .reset_index())
#     if pf2!="All": ps=ps[ps["plant_name"]==pf2]
#     if bf2!="All": ps=ps[ps["brand"]==bf2]

#     st.markdown(
#         f'<div class="stat-row">'
#           f'<div class="stat-item"><div class="stat-val">{len(ps)}</div><div class="stat-lbl">Plants</div></div>'
#           f'<div class="stat-item"><div class="stat-val">{f(ps["power_kw"].sum(),2)} kW</div><div class="stat-lbl">Total Power</div></div>'
#           f'<div class="stat-item"><div class="stat-val">{f(ps["today_kwh"].sum(),1)} kWh</div><div class="stat-lbl">Daily Yield</div></div>'
#           f'<div class="stat-item"><div class="stat-val">{f(ps["total_kwh"].sum(),1)} MWh</div><div class="stat-lbl">Total Yield</div></div>'
#         f'</div>', unsafe_allow_html=True)

#     st.markdown('<div class="tbl">', unsafe_allow_html=True)
#     st.markdown('<div class="tbl-hdr tbl-plant">'
#                 '<div>Plant Name</div><div>Brand</div><div>Organisation</div>'
#                 '<div>Inverters</div><div>Power (kW)</div>'
#                 '<div>Daily Yield</div><div>Total Yield</div><div>Status</div>'
#                 '</div>', unsafe_allow_html=True)
#     for _, row in ps.iterrows():
#         pr   = df[df["plant_name"]==row["plant_name"]]
#         on   = int((pr["status"].str.lower()=="online").sum())
#         tot  = int(row["inv_count"])
#         pst  = "Online" if on==tot and tot>0 else ("Offline" if on==0 else "Warning")
#         dy   = float(row["today_kwh"] or 0)
#         dy_s = f"{dy/1000:.3f} MWh" if dy>=1000 else f"{dy:.1f} kWh"
#         ty   = float(row["total_kwh"] or 0)
#         ty_s = f"{ty/1000:.3f} GWh" if ty>=1000 else f"{ty:.3f} MWh"
#         st.markdown(
#             f'<div class="tbl-row tbl-plant">'
#               f'<div class="cell-link">{row["plant_name"]}</div>'
#               f'<div>{chip(row["brand"])}</div>'
#               f'<div>Fractal Energy</div>'
#               f'<div>{on}/{tot}</div>'
#               f'<div><b>{f(row["power_kw"],2)}</b> kW</div>'
#               f'<div>{dy_s}</div><div>{ty_s}</div>'
#               f'<div>{badge(pst)}</div>'
#             f'</div>', unsafe_allow_html=True)
#     st.markdown('</div>', unsafe_allow_html=True)


# # ══════════════════════════════════════════════════════════════
# #  SETTINGS
# # ══════════════════════════════════════════════════════════════
# elif page == "Settings":
#     st.markdown('<div class="page-hdr"><h1>Settings</h1>'
#                 '<p>Credentials, alerts and app configuration</p></div>',
#                 unsafe_allow_html=True)

#     from config import (SOLIS_API_KEY, GROWATT_USERNAME, SUNGROW_APP_KEY,
#                         EMAIL_USER, TO_EMAILS, RATE_PER_KWH)

#     st.markdown("#### 🔑 API Credentials")
#     for brand,ok,hint in [
#         ("Solis",   bool(SOLIS_API_KEY),
#          SOLIS_API_KEY[:10]+"…" if SOLIS_API_KEY else "Not configured"),
#         ("Growatt", bool(GROWATT_USERNAME),
#          GROWATT_USERNAME or "Set GROWATT_USERNAME in config.py"),
#         ("Sungrow", bool(SUNGROW_APP_KEY),
#          SUNGROW_APP_KEY[:10]+"…" if SUNGROW_APP_KEY else "Set SUNGROW_APP_KEY in config.py"),
#     ]:
#         c1,c2,c3 = st.columns([1,1,4])
#         c1.markdown(f"**{brand}**")
#         c2.markdown("✅ OK" if ok else "⚠️ Not set")
#         c3.markdown(f"`{hint}`")

#     st.divider()
#     st.markdown("#### 📧 Email Alerts")
#     st.markdown(f"**Sender:** `{EMAIL_USER}`")
#     st.markdown(f"**Recipients:** `{', '.join(TO_EMAILS)}`")
#     st.divider()
#     st.markdown("#### 💰 Tariff Rate")
#     st.info(f"Current rate: **₹{RATE_PER_KWH}/kWh** — edit `RATE_PER_KWH` in config.py")
#     st.divider()
#     st.markdown("#### 👤 Logged in as")
#     st.info(f"`{st.session_state.user}`")
#     st.divider()
#     st.markdown("#### 🗂 Project Structure")
#     st.code("""
# solar_dashboard/
# ├── app.py              ← streamlit run app.py
# ├── config.py           ← ✏️  credentials & settings
# ├── requirements.txt
# ├── data/solar_data.db  ← auto-created
# └── utils/
#     ├── solis_api.py    ├── growatt_api.py
#     ├── sungrow_api.py  ├── aggregator.py
#     ├── database.py     └── alerts.py
#     """, language="")

# # ============================================================
# #  app.py  —  Solar Dashboard  |  streamlit run app.py
# # ============================================================
# import streamlit as st
# from streamlit_autorefresh import st_autorefresh
# import pandas as pd
# import plotly.express as px
# import plotly.graph_objects as go
# from datetime import datetime, date, timedelta

# from config import REFRESH_INTERVAL_SECONDS, RATE_PER_KWH
# from utils.database import init_db, get_history, get_alert_log
# from utils.aggregator import fetch_all_brands, check_alerts

# # ── GLOBAL STATE (FIXED) ─────────────────────────
# sel_brands     = st.session_state.get("sel_brands", ["Solis"])
# all_sel_plants = st.session_state.get("sel_plants", [])
# active_plant   = st.session_state.get("active_plant", "All Plants")

# # ─────────────────────────────────────────────────────────────
# st.set_page_config(page_title="Solar Dashboard · Fractal Energy",
#                    page_icon="☀️", layout="wide",
#                    initial_sidebar_state="expanded")

# # ══════════════════════════════════════════════════════════════
# #  GLOBAL CSS  —  Navy · Teal · Amber theme
# # ══════════════════════════════════════════════════════════════
# st.markdown("""
# <style>
# @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

# *,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}

# :root{
#   /* ── Palette ── */
#   --navy:      #0a1628;
#   --navy2:     #0f2044;
#   --navy3:     #1a2f5a;
#   --teal:      #0d9488;
#   --teal-l:    #ccfbf1;
#   --teal-d:    #0f766e;
#   --amber:     #f59e0b;
#   --amber-l:   #fef3c7;
#   --amber-d:   #d97706;
#   --orange:    #f97316;
#   --orange-l:  #ffedd5;
#   --red:       #ef4444;
#   --red-l:     #fee2e2;
#   --green:     #10b981;
#   --green-l:   #d1fae5;
#   --sky:       #38bdf8;
#   --sky-l:     #e0f2fe;

#   /* ── Surfaces ── */
#   --bg:        #f0f4f8;
#   --card:      #ffffff;
#   --border:    #e2e8f0;
#   --border2:   #cbd5e1;

#   /* ── Text ── */
#   --text:      #0f172a;
#   --text2:     #475569;
#   --text3:     #94a3b8;

#   /* ── Shadows ── */
#   --shadow:    0 1px 4px rgba(10,22,40,.06),0 4px 20px rgba(10,22,40,.05);
#   --shadow-lg: 0 8px 40px rgba(10,22,40,.12);
#   --shadow-teal:0 4px 20px rgba(13,148,136,.25);
# }

# /* ── Fonts ── */
# html,body,[data-testid="stAppViewContainer"]{
#   background:var(--bg)!important;
#   font-family:'Plus Jakarta Sans',sans-serif!important;
#   color:var(--text);
# }
# [data-testid="stHeader"]{background:transparent!important;display:none;}
# #MainMenu,footer{visibility:hidden;}
# [data-testid="stDecoration"]{display:none;}
# .block-container{padding:28px 32px!important;max-width:100%!important;}

# /* ══ SIDEBAR ══════════════════════════════════════════════ */
# [data-testid="stSidebar"]{
#   background:var(--navy)!important;
#   border-right:1px solid rgba(255,255,255,.06)!important;
# }
# [data-testid="stSidebar"]>div{padding-top:0!important;}
# section[data-testid="stSidebarContent"]{padding:0!important;}

# .sb-logo{
#   padding:24px 20px 18px;
#   border-bottom:1px solid rgba(255,255,255,.07);
#   margin-bottom:6px;
#   display:flex;align-items:center;gap:12px;
# }
# .sb-logo-icon{
#   width:42px;height:42px;background:linear-gradient(135deg,var(--teal),var(--teal-d));
#   border-radius:12px;display:flex;align-items:center;justify-content:center;
#   font-size:20px;flex-shrink:0;box-shadow:var(--shadow-teal);
# }
# .sb-logo-title{color:#fff;font-weight:800;font-size:15px;letter-spacing:-.3px;}
# .sb-logo-sub{color:#64748b;font-size:11px;margin-top:1px;}
# .sb-section{
#   padding:14px 20px 4px;
#   font-size:10px;font-weight:700;color:#334155;
#   text-transform:uppercase;letter-spacing:.12em;
# }
# .sb-time{
#   padding:14px 20px;font-size:11px;color:#475569;
#   border-top:1px solid rgba(255,255,255,.06);margin-top:6px;
#   font-family:'JetBrains Mono',monospace;
# }

# /* ══ LOGIN PAGE ═══════════════════════════════════════════ */
# .login-wrap{
#   min-height:100vh;display:flex;align-items:center;justify-content:center;
#   background:linear-gradient(135deg,var(--navy) 0%,var(--navy2) 50%,#0d2b4e 100%);
#   padding:20px;
# }
# .login-card{
#   background:rgba(255,255,255,.04);
#   border:1px solid rgba(255,255,255,.1);
#   border-radius:20px;padding:48px 44px;width:100%;max-width:420px;
#   backdrop-filter:blur(20px);
#   box-shadow:0 20px 60px rgba(0,0,0,.4);
# }
# .login-logo{
#   width:60px;height:60px;
#   background:linear-gradient(135deg,var(--teal),var(--teal-d));
#   border-radius:16px;display:flex;align-items:center;justify-content:center;
#   font-size:28px;margin:0 auto 20px;
#   box-shadow:0 8px 24px rgba(13,148,136,.4);
# }
# .login-title{
#   font-size:24px;font-weight:800;color:#fff;text-align:center;
#   letter-spacing:-.4px;margin-bottom:6px;
# }
# .login-sub{font-size:13px;color:#64748b;text-align:center;margin-bottom:32px;}
# .login-label{font-size:13px;font-weight:600;color:#94a3b8;margin-bottom:6px;}
# .login-error{
#   background:rgba(239,68,68,.12);border:1px solid rgba(239,68,68,.3);
#   border-radius:8px;padding:10px 14px;font-size:13px;color:#fca5a5;
#   margin-bottom:16px;text-align:center;
# }

# /* ══ PAGE HEADER ══════════════════════════════════════════ */
# .page-hdr{margin-bottom:24px;}
# .page-hdr h1{
#   font-size:24px;font-weight:800;color:var(--text);
#   letter-spacing:-.5px;line-height:1.2;
# }
# .page-hdr p{font-size:13px;color:var(--text3);margin-top:4px;}

# /* ══ KPI CARDS ════════════════════════════════════════════ */
# .kpi-card{
#   background:var(--card);border-radius:16px;padding:24px 22px;
#   border:1px solid var(--border);box-shadow:var(--shadow);
#   display:flex;gap:16px;align-items:flex-start;
#   transition:transform .15s,box-shadow .15s;
#   position:relative;overflow:hidden;
# }
# .kpi-card::after{
#   content:'';position:absolute;top:0;left:0;right:0;height:3px;
#   background:linear-gradient(90deg,var(--teal),var(--sky));
#   border-radius:16px 16px 0 0;
# }
# .kpi-card.amber::after{background:linear-gradient(90deg,var(--amber),var(--orange));}
# .kpi-card.green::after{background:linear-gradient(90deg,var(--green),var(--teal));}
# .kpi-card.navy::after{background:linear-gradient(90deg,var(--navy3),var(--sky));}
# .kpi-card:hover{transform:translateY(-2px);box-shadow:var(--shadow-lg);}

# .kpi-icon{
#   width:50px;height:50px;border-radius:13px;flex-shrink:0;
#   display:flex;align-items:center;justify-content:center;font-size:22px;
# }
# .kpi-icon.teal  {background:var(--teal-l);color:var(--teal);}
# .kpi-icon.amber {background:var(--amber-l);color:var(--amber-d);}
# .kpi-icon.green {background:var(--green-l);color:var(--green);}
# .kpi-icon.navy  {background:var(--sky-l);color:#0284c7;}

# .kpi-label{
#   font-size:11px;color:var(--text3);font-weight:700;
#   text-transform:uppercase;letter-spacing:.1em;margin-bottom:6px;
# }
# .kpi-value{
#   font-size:28px;font-weight:800;color:var(--text);
#   line-height:1;letter-spacing:-.5px;
# }
# .kpi-unit{font-size:14px;font-weight:600;color:var(--text2);margin-left:3px;}
# .kpi-meta{font-size:12px;color:var(--text3);margin-top:8px;line-height:1.4;}
# .kpi-meta b{color:var(--teal);font-weight:600;}

# /* ══ SECTION HEADER ═══════════════════════════════════════ */
# .sec-hdr{
#   font-size:13px;font-weight:700;color:var(--text);
#   display:flex;align-items:center;gap:8px;
#   margin-bottom:14px;padding-bottom:10px;
#   border-bottom:2px solid var(--border);
# }
# .sec-hdr-dot{
#   width:8px;height:8px;border-radius:50%;
#   background:linear-gradient(135deg,var(--teal),var(--sky));
#   flex-shrink:0;
# }

# /* ══ CARD WRAPPER ═════════════════════════════════════════ */
# .card{
#   background:var(--card);border-radius:16px;padding:22px;
#   border:1px solid var(--border);box-shadow:var(--shadow);margin-bottom:16px;
# }

# /* ══ INVERTER CARD ════════════════════════════════════════ */
# .inv-card{
#   background:var(--card);border-radius:16px;padding:22px;
#   border:1px solid var(--border);box-shadow:var(--shadow);
#   margin-bottom:14px;transition:border-color .15s,box-shadow .15s;
# }
# .inv-card:hover{border-color:var(--primary);box-shadow:var(--shadow-teal);}
# .inv-card.alert-card{border-left:3px solid var(--red);}
# .inv-header{
#   display:flex;justify-content:space-between;align-items:flex-start;
#   margin-bottom:18px;padding-bottom:14px;
#   border-bottom:1px solid var(--border);
# }
# .inv-name{font-size:15px;font-weight:700;color:var(--text);letter-spacing:-.3px;}
# .inv-meta{font-size:11px;color:var(--text3);margin-top:3px;font-family:'JetBrains Mono',monospace;}
# .inv-params{display:grid;grid-template-columns:repeat(6,1fr);gap:16px;}
# .param-label{
#   font-size:10px;color:var(--text3);text-transform:uppercase;
#   letter-spacing:.08em;font-weight:600;margin-bottom:4px;
# }
# .param-val{font-size:18px;font-weight:700;color:var(--text);letter-spacing:-.3px;}
# .param-unit{font-size:11px;color:var(--text3);margin-left:2px;}
# .inv-footer{margin-top:14px;font-size:11px;color:var(--text3);font-family:'JetBrains Mono',monospace;}

# /* ══ TABLES ═══════════════════════════════════════════════ */
# .tbl{
#   background:var(--card);border-radius:16px;
#   border:1px solid var(--border);overflow:hidden;box-shadow:var(--shadow);
# }
# .tbl-hdr,.tbl-row{
#   display:grid;padding:0 20px;align-items:center;gap:10px;
# }
# .tbl-hdr{
#   background:linear-gradient(90deg,#f8fafc,#f1f5f9);
#   border-bottom:2px solid var(--border);
#   font-size:10px;font-weight:700;color:var(--text3);
#   text-transform:uppercase;letter-spacing:.1em;height:44px;
# }
# .tbl-row{
#   min-height:54px;border-bottom:1px solid var(--border);
#   font-size:13px;transition:background .1s;
# }
# .tbl-row:last-child{border-bottom:none;}
# .tbl-row:hover{background:#f8fafc;}
# .tbl-plant{grid-template-columns:2fr 1fr 1.1fr 1fr 1fr 1.1fr 1.3fr 1fr;}
# .tbl-alarm{grid-template-columns:1fr 1fr 1fr 1.5fr 1.4fr 2.2fr 1.2fr;}
# .cell-link{color:var(--primary);font-weight:700;cursor:pointer;font-size:13px;}

# /* ══ BADGES ═══════════════════════════════════════════════ */
# .badge{
#   display:inline-flex;align-items:center;gap:5px;
#   font-size:11px;font-weight:700;padding:4px 10px;
#   border-radius:20px;letter-spacing:.02em;
# }
# .badge::before{content:'';width:6px;height:6px;border-radius:50%;}
# .b-online {background:var(--green-l);color:#065f46;}
# .b-online::before{background:var(--green);}
# .b-offline{background:var(--red-l);color:#991b1b;}
# .b-offline::before{background:var(--red);}
# .b-warning{background:var(--amber-l);color:#92400e;}
# .b-warning::before{background:var(--amber);}
# .b-unknown{background:#f1f5f9;color:#64748b;}
# .b-unknown::before{background:#94a3b8;}
# .b-active {background:var(--red-l);color:#991b1b;}
# .b-active::before{background:var(--red);}
# .b-resolved{background:var(--green-l);color:#065f46;}
# .b-resolved::before{background:var(--green);}
# .b-critical{background:var(--red-l);color:#991b1b;font-weight:800;}
# .b-critical::before{background:var(--red);}

# /* ══ CHIPS ════════════════════════════════════════════════ */
# .chip{
#   display:inline-block;font-size:10px;font-weight:800;
#   padding:3px 9px;border-radius:6px;
#   letter-spacing:.1em;text-transform:uppercase;
# }
# .chip-solis  {background:#dbeafe;color:#1e40af;}
# .chip-growatt{background:#d1fae5;color:#065f46;}
# .chip-sungrow{background:#ffedd5;color:#c2410c;}

# /* ══ ALERT STRIP ══════════════════════════════════════════ */
# .alert-strip{
#   background:linear-gradient(135deg,#fff1f2,#ffe4e6);
#   border:1px solid #fecdd3;border-left:4px solid var(--red);
#   border-radius:12px;padding:16px 18px;margin-bottom:12px;
#   display:flex;gap:14px;align-items:flex-start;
# }
# .alert-strip-ico{font-size:20px;flex-shrink:0;}
# .alert-strip-ttl{font-size:14px;font-weight:700;color:var(--red);}
# .alert-strip-msg{font-size:12px;color:#7f1d1d;margin-top:3px;}

# /* ══ STAT ROW ═════════════════════════════════════════════ */
# .stat-row{
#   background:var(--card);border-radius:14px;padding:16px 24px;
#   border:1px solid var(--border);display:flex;gap:32px;
#   margin-bottom:20px;align-items:center;flex-wrap:wrap;
#   box-shadow:var(--shadow);
# }
# .stat-item{text-align:center;}
# .stat-val{font-size:20px;font-weight:800;color:var(--text);letter-spacing:-.3px;}
# .stat-lbl{font-size:10px;color:var(--text3);margin-top:2px;font-weight:600;text-transform:uppercase;letter-spacing:.08em;}

# /* ══ STREAMLIT OVERRIDES ══════════════════════════════════ */
# .stButton>button{
#   background:linear-gradient(135deg,var(--teal),var(--teal-d))!important;
#   color:#fff!important;border:none!important;border-radius:10px!important;
#   font-family:'Plus Jakarta Sans',sans-serif!important;
#   font-weight:700!important;font-size:13px!important;
#   padding:10px 24px!important;letter-spacing:.01em!important;
#   box-shadow:0 4px 12px rgba(13,148,136,.3)!important;
#   transition:all .15s!important;
# }
# .stButton>button:hover{transform:translateY(-1px)!important;box-shadow:0 6px 20px rgba(13,148,136,.4)!important;}
# div[data-testid="stSelectbox"]>label,
# div[data-testid="stTextInput"]>label{
#   font-size:12px!important;font-weight:700!important;
#   color:var(--text2)!important;text-transform:uppercase!important;letter-spacing:.06em!important;
# }
# [data-testid="stRadio"]>label{font-size:13px!important;font-weight:600!important;}
# .stRadio>div{gap:4px!important;}
# .stAlert{border-radius:12px!important;}
# div[data-testid="stTextInput"] input{
#   border-radius:10px!important;border-color:var(--border2)!important;
#   font-size:14px!important;font-family:'Plus Jakarta Sans',sans-serif!important;
# }
# div[data-testid="stSelectbox"]>div>div{
#   border-radius:10px!important;border-color:var(--border2)!important;
#   font-size:13px!important;
# }

# /* ══ LOGIN STREAMLIT INPUT OVERRIDES ═══════════════════════ */
# .login-page [data-testid="stTextInput"] input{
#   background:rgba(255,255,255,.08)!important;
#   border:1px solid rgba(255,255,255,.15)!important;
#   border-radius:10px!important;color:#fff!important;
#   font-size:14px!important;padding:12px 14px!important;
# }
# .login-page .stButton>button{
#   width:100%!important;padding:14px!important;font-size:15px!important;
# }

# /* ══ DIVIDER ══════════════════════════════════════════════ */
# .divider{height:1px;background:var(--border);margin:20px 0;}

# /* ══ METRIC OVERRIDES ═════════════════════════════════════ */
# [data-testid="stMetric"]{
#   background:var(--card);border-radius:12px;padding:16px 18px;
#   border:1px solid var(--border);box-shadow:var(--shadow);
# }
# [data-testid="stMetricLabel"]{font-size:11px!important;font-weight:700!important;color:var(--text3)!important;text-transform:uppercase!important;letter-spacing:.08em!important;}
# [data-testid="stMetricValue"]{font-size:24px!important;font-weight:800!important;color:var(--text)!important;letter-spacing:-.4px!important;}
# </style>
# """, unsafe_allow_html=True)

# # ══════════════════════════════════════════════════════════════
# #  INIT
# # ══════════════════════════════════════════════════════════════
# init_db()

# # ══════════════════════════════════════════════════════════════
# #  SESSION STATE
# # ══════════════════════════════════════════════════════════════
# USERS = {
#     "admin":    "1234"
# }

# for key, default in [
#     ("logged_in",      False),
#     ("user",           ""),
#     ("plant_selected", False),
#     ("sel_brands",     ["Solis"]),
#     ("sel_plants",     []),        # list of selected plant names
# ]:
#     if key not in st.session_state:
#         st.session_state[key] = default

# # ══════════════════════════════════════════════════════════════
# #  STEP 1 — LOGIN
# # ══════════════════════════════════════════════════════════════
# DARK_PAGE_CSS = """<style>
# [data-testid="stSidebar"]{display:none!important;}
# .block-container{padding:0!important;max-width:100%!important;}
# </style>"""

# if not st.session_state.logged_in:
#     st.markdown(DARK_PAGE_CSS, unsafe_allow_html=True)
#     st.markdown("""
#     <div style="min-height:100vh;display:flex;align-items:center;justify-content:center;
#     background:linear-gradient(135deg,#0a1628 0%,#0f2044 55%,#0d2b4e 100%);padding:20px;">
#       <div style="width:100%;max-width:420px;">
#         <div style="text-align:center;margin-bottom:32px;">
#           <div style="width:68px;height:68px;background:linear-gradient(135deg,#0d9488,#0f766e);
#             border-radius:18px;display:flex;align-items:center;justify-content:center;
#             font-size:32px;margin:0 auto 16px;box-shadow:0 8px 24px rgba(13,148,136,.4);">☀️</div>
#           <div style="font-size:26px;font-weight:800;color:#fff;letter-spacing:-.5px;">Solar Dashboard</div>
#           <div style="font-size:13px;color:#64748b;margin-top:6px;">Fractal Energy · Monitoring Platform</div>
#         </div>
#         <div style="background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.1);
#           border-radius:20px;padding:36px 32px;backdrop-filter:blur(20px);
#           box-shadow:0 20px 60px rgba(0,0,0,.4);">
#     """, unsafe_allow_html=True)
#     email    = st.text_input("Email Address", placeholder="your@email.com")
#     password = st.text_input("Password",      placeholder="••••••••", type="password")
#     if st.button("Sign In →", use_container_width=True):
#         if email in USERS and USERS[email] == password:
#             st.session_state.logged_in = True
#             st.session_state.user      = email
#             st.rerun()
#         else:
#             st.error("Invalid email or password.")
#     st.markdown("""<div style="text-align:center;margin-top:20px;font-size:12px;color:#475569;">
#       Secured by Fractal Energy · v2.0</div></div></div></div>""",
#     unsafe_allow_html=True)
#     st.stop()

# # ══════════════════════════════════════════════════════════════
# #  STEP 2 — PLANT SELECTOR  (shown once after login)
# # ══════════════════════════════════════════════════════════════
# if not st.session_state.plant_selected:
#     st.markdown(DARK_PAGE_CSS, unsafe_allow_html=True)

#     # Fetch available plants from all brands
#     @st.cache_data(ttl=600)
#     def _fetch_available_plants():
#         available = []
#         try:
#             from utils.solis_api import get_plants as _sp
#             for p in _sp():
#                 available.append({
#                     "brand": "Solis",
#                     "name":  p.get("stationName",""),
#                     "id":    p.get("id",""),
#                     "capacity": str(p.get("capacity","")) + " kWp",
#                 })
#         except Exception as e:
#             print(f"Plant selector Solis error: {e}")
#         try:
#             from utils.growatt_api import _get_plants, login as glogin
#             glogin()
#             for p in _get_plants():
#                 available.append({
#                     "brand": "Growatt",
#                     "name":  p.get("plantNameEncryption") or p.get("plantName",""),
#                     "id":    str(p.get("pId") or p.get("plantId","")),
#                     "capacity": str(p.get("nominalPower","")) + " W",
#                 })
#         except Exception as e:
#             print(f"Plant selector Growatt error: {e}")
#         return available

#     try:
#         with st.spinner("Loading available plants…"):
#             available_plants = _fetch_available_plants()
#     except Exception as e:
#         st.error(f"Error loading plants: {e}")
#         available_plants = []

#     # Group by brand
#     solis_plants   = [p for p in available_plants if p["brand"] == "Solis"]
#     growatt_plants = [p for p in available_plants if p["brand"] == "Growatt"]

#     # Plant selector UI
#     st.markdown(f"""
#     <div style="min-height:100vh;background:linear-gradient(135deg,#0a1628,#0f2044);
#     display:flex;align-items:center;justify-content:center;padding:32px 20px;">
#       <div style="width:100%;max-width:860px;">
#         <div style="text-align:center;margin-bottom:36px;">
#           <div style="width:60px;height:60px;background:linear-gradient(135deg,#0d9488,#0f766e);
#             border-radius:16px;display:flex;align-items:center;justify-content:center;
#             font-size:28px;margin:0 auto 14px;">☀</div>
#           <div style="font-size:24px;font-weight:800;color:#fff;letter-spacing:-.4px;">
#             Select Plants to Monitor</div>
#           <div style="font-size:13px;color:#64748b;margin-top:6px;">
#             Welcome, {st.session_state.user} · Choose which plants to include in your dashboard</div>
#         </div>
#       </div>
#     </div>
#     """, unsafe_allow_html=True)

#     # Brand tabs
#     brand_tabs = []
#     if solis_plants:   brand_tabs.append("☀️ Solis")
#     if growatt_plants: brand_tabs.append("⚡ Growatt")
#     if not brand_tabs:
#         st.warning("No plants found. Check credentials in config.py")
#         if st.button("Continue anyway"):
#             st.session_state.plant_selected = True
#             st.session_state.sel_brands     = ["Solis"]
#             st.session_state.sel_plants     = []
#             st.rerun()
#         st.stop()

#     sel_plant_names = []

#     if len(brand_tabs) > 1:
#         tabs = st.tabs(brand_tabs)
#     else:
#         tabs = [st.container()]

#     tab_idx = 0
#     if solis_plants:
#         with tabs[tab_idx]:
#             st.markdown("#### Solis Plants")
#             st.caption("Select all Solis plants you want to monitor:")
#             all_solis = st.checkbox("Select All Solis Plants", value=True, key="all_solis")
#             for p in solis_plants:
#                 checked = st.checkbox(
#                     f"🌱 {p['name']}  —  {p['capacity']}",
#                     value=all_solis, key=f"sp_{p['id']}"
#                 )
#                 if checked:
#                     sel_plant_names.append(p["name"])
#         tab_idx += 1

#     if growatt_plants:
#         with tabs[tab_idx]:
#             st.markdown("#### Growatt Plants")
#             st.caption("Select all Growatt plants you want to monitor:")
#             all_growatt = st.checkbox("Select All Growatt Plants", value=True, key="all_growatt")
#             for p in growatt_plants:
#                 checked = st.checkbox(
#                     f"⚡ {p['name']}  —  {p['capacity']}",
#                     value=all_growatt, key=f"gp_{p['id']}"
#                 )
#                 if checked:
#                     sel_plant_names.append(p["name"])

#     st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
#     col_a, col_b = st.columns([3,1])
#     with col_b:
#         if st.button("Continue to Dashboard →", use_container_width=True):
#             # Determine which brands are selected
#             active_brands = []
#             if any(p["name"] in sel_plant_names for p in solis_plants):
#                 active_brands.append("Solis")
#             if any(p["name"] in sel_plant_names for p in growatt_plants):
#                 active_brands.append("Growatt")
#             st.session_state.sel_brands     = active_brands or ["Solis"]
#             st.session_state.sel_plants     = sel_plant_names
#             st.session_state.plant_selected = True
#             st.cache_data.clear()
#             st.rerun()
#     with col_a:
#         st.caption(f"{len(sel_plant_names)} plant(s) selected")
#     st.stop()

# # ══════════════════════════════════════════════════════════════
# #  AUTHENTICATED APP
# # ══════════════════════════════════════════════════════════════
# st_autorefresh(interval=REFRESH_INTERVAL_SECONDS * 1000, key="solar_ar")

# # ── Helpers ──────────────────────────────────────────────────
# def f(v, d=1, na="—"):
#     try:    return f"{float(v):.{d}f}"
#     except: return na

# def badge(s, kind=None):
#     s  = (s or "").strip()
#     sl = s.lower()
#     if kind == "level":
#         cls = "b-critical" if sl == "critical" else "b-warning"
#     elif kind == "status_alarm":
#         cls = "b-active" if sl == "active" else "b-resolved"
#     else:
#         if sl == "online":              cls = "b-online"
#         elif sl in ("offline","fault"): cls = "b-offline"
#         else:                           cls = "b-unknown"
#     return f'<span class="badge {cls}">{s}</span>'

# def chip(b):
#     return f'<span class="chip chip-{(b or "").lower()}">{b}</span>'

# def earn(kwh):
#     v = float(kwh or 0) * RATE_PER_KWH
#     if v >= 1_000_000: return f"₹{v/1_000_000:.3f}M"
#     if v >= 1_000:     return f"₹{v/1_000:.3f}K"
#     return f"₹{v:.2f}"

# def chart_style(fig, h=300):
#     fig.update_layout(
#         plot_bgcolor="#fff", paper_bgcolor="#fff",
#         font_color="#64748b", font_family="Inter",
#         margin=dict(l=0,r=0,t=16,b=0), height=h,
#         legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=12, color="#64748b")),
#         bargap=0.28,
#     )
#     fig.update_traces(marker_line_width=0)
#     fig.update_xaxes(showgrid=False, zeroline=False, tickfont_size=11,
#                      tickfont_color="#94a3b8", linecolor="#e2e8f0")
#     fig.update_yaxes(showgrid=True, gridcolor="#f1f5f9", zeroline=False,
#                      tickfont_size=11, tickfont_color="#94a3b8")
#     return fig

# PALETTE = ["#0d9488","#f59e0b","#3b82f6","#f97316","#10b981","#8b5cf6","#06b6d4","#ec4899"]
# BRAND_COLORS = {"Solis":"#3b82f6","Growatt":"#10b981","Sungrow":"#f97316"}

# def sec(title, icon=""):
#     st.markdown(f'<div class="sec-hdr"><div class="sec-hdr-dot"></div>{icon} {title}</div>',
#                 unsafe_allow_html=True)

# # ── Sidebar — only shown in main dashboard ───────────────────
# with st.sidebar:
#     st.markdown(f"""
#     <div class="sb-logo">
#       <div class="sb-logo-icon">☀</div>
#       <div>
#         <div class="sb-logo-title">Solar Dashboard</div>
#         <div class="sb-logo-sub">Fractal Energy</div>
#       </div>
#     </div>""", unsafe_allow_html=True)

#     if not st.session_state.get("plant_selected", False):
#         # Minimal sidebar during plant selection
#         st.markdown("<div style='color:#64748b;padding:20px;font-size:13px;'>Select plants to continue…</div>",
#                     unsafe_allow_html=True)
#         page = "Overview"
#         sel_brands = st.session_state.get("sel_brands", ["Solis"])
#         sel_plants = []
#         show_debug = False
#     else:
#         page = st.radio("", ["📊  Overview","🔧  O&M","📈  Report","🗺  Service","⚙️  Settings"],
#                         label_visibility="collapsed")
#         page = page.split("  ",1)[1].strip()

#         st.markdown('<div class="sb-section">Active Plant</div>', unsafe_allow_html=True)
#         sel_brands     = st.session_state.get("sel_brands", ["Solis"])
#         all_sel_plants = st.session_state.get("sel_plants", [])
#         plant_choices  = ["All Plants"] + all_sel_plants
#         active_plant   = st.selectbox("View plant", plant_choices,
#                                       key="active_plant",
#                                       label_visibility="collapsed")
#         # st.session_state["active_plant"] = active_plant
#         active_plant = st.session_state["active_plant"]
#         for b in sel_brands:
#             st.markdown(
#                 f'<div style="color:#64748b;font-size:11px;padding:2px 4px;">'
#                 f'{"☀️" if b=="Solis" else "⚡" if b=="Growatt" else "🔆"} {b}</div>',
#                 unsafe_allow_html=True)
#         if st.button("🔀  Change Plants"):
#             st.session_state.plant_selected = False
#             st.cache_data.clear()
#             st.rerun()

#         st.markdown('<div style="height:6px"></div>', unsafe_allow_html=True)
#         if st.button("🔄  Refresh Now"):
#             st.cache_data.clear(); st.rerun()

#         show_debug = st.checkbox("🔍  Debug", value=False)

#         st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)
#         if st.button("🚪  Sign Out"):
#             st.session_state.logged_in = False
#             st.rerun()

#         st.markdown(f"""
#         <div class="sb-time">
#           ⏱ {datetime.now().strftime('%d %b %Y')}<br>
#           <b style="color:#94a3b8;">{datetime.now().strftime('%H:%M:%S')}</b><br>
#           <span style="color:#334155;">Auto-refresh {REFRESH_INTERVAL_SECONDS//60} min</span>
#         </div>""", unsafe_allow_html=True)

# # ── Fetch data (only when plant_selected) ────────────────────
# if not st.session_state.get("plant_selected", False):
#     st.stop()

# all_sel_plants = st.session_state.get("sel_plants", [])
# active_plant   = st.session_state.get("active_plant", "All Plants")

# @st.cache_data(ttl=REFRESH_INTERVAL_SECONDS)
# def load(brands, plants):
#     # Fetch for all login-selected plants
#     result = fetch_all_brands(list(brands))
#     if not result:
#         raise RuntimeError("empty")
#     if plants:
#         result = [r for r in result if r.get("plant_name") in plants]
#     return result

# with st.spinner("Fetching live data…"):
#     try:
#         records = load(tuple(sel_brands), tuple(all_sel_plants))
#     except Exception:
#         records = fetch_all_brands(list(sel_brands))
#         if all_sel_plants:
#             records = [r for r in records if r.get("plant_name") in all_sel_plants]
#         if not records:
#             st.cache_data.clear()

# # Filter to active plant chosen in sidebar
# if active_plant and active_plant != "All Plants":
#     records_view = [r for r in records if r.get("plant_name") == active_plant]
# else:
#     records_view = records

# alerts = check_alerts(records, st.session_state)

# df = pd.DataFrame()
# if records_view:
#     df = pd.DataFrame(records_view)
#     for c in ["power_kw","today_kwh","total_kwh","temperature","voltage","current_a"]:
#         if c in df.columns:
#             df[c] = pd.to_numeric(df[c], errors="coerce")
#     if "status" in df.columns:
#         df["status"] = df["status"].astype(str).str.strip()

# # ── Debug ─────────────────────────────────────────────────────
# if show_debug and not df.empty:
#     st.markdown("### 🔍 Debug: Raw API Data")
#     st.dataframe(df, use_container_width=True)
#     try:
#         from utils.solis_api import fetch_summary as _fsum, _raw_plants_cache
#         summ = _fsum()
#         st.write("**fetch_summary():**", summ)
#     except Exception as ex:
#         st.error(f"Debug error: {ex}")
#     st.divider()


# # ══════════════════════════════════════════════════════════════
# #  OVERVIEW
# # ══════════════════════════════════════════════════════════════
# if page == "Overview":
#     # sel_label = (f"{', '.join(sel_plants)}" if sel_plants
#                 # else f"All {', '.join(sel_brands)} Plants")
#     sel_label = (f"{', '.join(all_sel_plants)}" if all_sel_plants
#                else f"All {', '.join(sel_brands)} Plants")
#     st.markdown(f'<div class="page-hdr"><h1>Plant Overview</h1>'
#                 f'<p>Showing: <b>{sel_label}</b></p></div>',
#                 unsafe_allow_html=True)

#     if df.empty:
#         st.warning("⚠️ No data. Check credentials in config.py and click Refresh.")
#         st.stop()

#     # ── KPI values — always from df (already filtered to selected plants) ──
#     # df is filtered by sel_plants at fetch time, so all sums are correct
#     total_power = float(df["power_kw"].sum())
#     daily_kwh   = float(df["today_kwh"].sum())   # kWh — always use df
#     total_mwh   = float(df["total_kwh"].sum())   # MWh from etotal

#     # Monthly: from DB filtered to selected plants, floor = today's daily
#     monthly_mwh = 0.0
#     hist = get_history(hours=720)
#     if not hist.empty and "today_kwh" in hist.columns:
#         hist["fetched_at"] = pd.to_datetime(hist["fetched_at"])
#         hist["today_kwh"]  = pd.to_numeric(hist["today_kwh"], errors="coerce")
#         # Filter DB history to selected plants too
#         if sel_plants:
#             hist = hist[hist["plant_name"].isin(sel_plants)]
#         m = hist[hist["fetched_at"].dt.month == datetime.now().month]
#         if not m.empty:
#             v = float(m.groupby([m["fetched_at"].dt.date,"inverter_sn"])["today_kwh"].max().sum())
#             monthly_mwh = max(v / 1000, daily_kwh / 1000)

#     # If no DB history yet, use Solis API monthly for Solis-only selections
#     if monthly_mwh == 0 and sel_brands == ["Solis"] and not sel_plants:
#         try:
#             from utils.solis_api import fetch_summary as _fs
#             summ = _fs()
#             if summ.get("monthly_mwh", 0) > 0:
#                 monthly_mwh = float(summ["monthly_mwh"])
#                 # Also update total from Solis API if viewing all plants
#                 if summ.get("total_mwh", 0) > 0:
#                     total_mwh = float(summ["total_mwh"])
#         except Exception:
#             pass

#     if monthly_mwh == 0:
#         monthly_mwh = daily_kwh / 1000   # floor = today

#     monthly_kwh = monthly_mwh * 1000

#     # Display units
#     daily_val,daily_unit = (f(daily_kwh/1000,3),"MWh") if daily_kwh>=1000 else (f(daily_kwh,1),"kWh")
#     mo_val,mo_unit       = f(monthly_mwh,3), "MWh"
#     if total_mwh >= 1000:
#         tot_val,tot_unit,tot_earn = f(total_mwh/1000,3),"GWh",total_mwh*1000
#     else:
#         tot_val,tot_unit,tot_earn = f(total_mwh,3),"MWh",total_mwh*1000

#     n_on  = int((df["status"].str.lower()=="online").sum())
#     n_tot = len(df)

#     # ── 4 KPI cards ──────────────────────────────────────────
#     c1,c2,c3,c4 = st.columns(4)
#     kpis = [
#         (c1,"teal","teal","⚡","Power",f(total_power,2),"kW",
#          f"Inverters: <b>{n_on}/{n_tot} online</b>"),
#         (c2,"amber","amber","🔋","Daily Yield",daily_val,daily_unit,
#          f"Earning today: <b>{earn(daily_kwh)}</b>"),
#         (c3,"green","green","📅","Monthly Yield",mo_val,mo_unit,
#          f"Earning this month: <b>{earn(monthly_kwh)}</b>"),
#         (c4,"navy","navy","📊","Total Yield",tot_val,tot_unit,
#          f"Total earning: <b>{earn(tot_earn)}</b>"),
#     ]
#     for col,card_cls,ico_cls,ico,lbl,val,unit,meta in kpis:
#         with col:
#             st.markdown(f"""
#             <div class="kpi-card {card_cls}">
#               <div class="kpi-icon {ico_cls}">{ico}</div>
#               <div>
#                 <div class="kpi-label">{lbl}</div>
#                 <div class="kpi-value">{val}<span class="kpi-unit"> {unit}</span></div>
#                 <div class="kpi-meta">{meta}</div>
#               </div>
#             </div>""", unsafe_allow_html=True)

#     st.markdown('<div style="height:8px"></div>', unsafe_allow_html=True)

#     # ── Alert strips ─────────────────────────────────────────
#     if alerts:
#         for a in alerts[:3]:
#             st.markdown(f"""
#             <div class="alert-strip">
#               <div class="alert-strip-ico">🚨</div>
#               <div>
#                 <div class="alert-strip-ttl">{a['plant_name']} — {a.get('inverter_sn','')}</div>
#                 <div class="alert-strip-msg">{a['issue']}</div>
#               </div>
#             </div>""", unsafe_allow_html=True)

#     # ── Charts ───────────────────────────────────────────────
#     ch1, ch2 = st.columns([3, 2])

#     with ch1:
#         sec("Power by Plant (kW)")
#         pdf = df.groupby(["plant_name","brand"])["power_kw"].sum().reset_index()
#         fig = px.bar(pdf, x="plant_name", y="power_kw", color="brand",
#                      color_discrete_map=BRAND_COLORS,
#                      labels={"power_kw":"Power (kW)","plant_name":"","brand":"Brand"})
#         fig.update_traces(marker_cornerradius=4)
#         st.plotly_chart(chart_style(fig, 290), use_container_width=True)

#     with ch2:
#         sec("Daily Yield Share")
#         pief = df.groupby("plant_name")["today_kwh"].sum().reset_index()
#         fig2 = go.Figure(go.Pie(
#             labels=pief["plant_name"],
#             values=pief["today_kwh"],
#             hole=0.52,
#             marker=dict(colors=PALETTE, line=dict(color="#fff", width=2)),
#             textposition="outside",
#             textinfo="label+percent",
#             textfont=dict(size=11, family="Plus Jakarta Sans"),
#             pull=[0.04]*len(pief),
#         ))
#         fig2.update_layout(
#             plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
#             font_family="Inter", font_color="#64748b",
#             margin=dict(l=60, r=60, t=20, b=20), height=290,
#             showlegend=False,
#             annotations=[dict(text=f"<b>{f(pief['today_kwh'].sum(),1)}</b><br>kWh",
#                               font=dict(size=14,color="#0f172a",family="Plus Jakarta Sans"),
#                               showarrow=False)]
#         )
#         st.plotly_chart(fig2, use_container_width=True)

#     # ── Plant table ──────────────────────────────────────────
#     sec("Plant List")
#     ps = (df.groupby(["plant_name","brand"])
#           .agg(power_kw=("power_kw","sum"), today_kwh=("today_kwh","sum"),
#                total_kwh=("total_kwh","sum"), inv_count=("inverter_sn","count"))
#           .reset_index())

#     st.markdown('<div class="tbl">', unsafe_allow_html=True)
#     st.markdown(
#         '<div class="tbl-hdr tbl-plant">'
#         '<div>Plant Name</div><div>Brand</div><div>Inverters</div>'
#         '<div>Power (kW)</div><div>Daily Yield</div>'
#         '<div>Total Yield</div><div>Earning Today</div><div>Status</div>'
#         '</div>', unsafe_allow_html=True)

#     for _, row in ps.iterrows():
#         pr   = df[df["plant_name"]==row["plant_name"]]
#         on   = int((pr["status"].str.lower()=="online").sum())
#         tot  = int(row["inv_count"])
#         pst  = "Online" if on==tot and tot>0 else ("Offline" if on==0 else "Warning")
#         dy   = float(row["today_kwh"] or 0)
#         dy_s = f"{dy/1000:.3f} MWh" if dy>=1000 else f"{dy:.1f} kWh"
#         ty   = float(row["total_kwh"] or 0)
#         ty_s = f"{ty/1000:.3f} GWh" if ty>=1000 else f"{ty:.3f} MWh"
#         st.markdown(
#             f'<div class="tbl-row tbl-plant">'
#               f'<div class="cell-link">{row["plant_name"]}</div>'
#               f'<div>{chip(row["brand"])}</div>'
#               f'<div>{on}/{tot}</div>'
#               f'<div><b>{f(row["power_kw"],2)}</b> kW</div>'
#               f'<div>{dy_s}</div><div>{ty_s}</div>'
#               f'<div>{earn(dy)}</div><div>{badge(pst)}</div>'
#             f'</div>', unsafe_allow_html=True)
#     st.markdown('</div>', unsafe_allow_html=True)


# # ══════════════════════════════════════════════════════════════
# #  O&M
# # ══════════════════════════════════════════════════════════════
# elif page == "O&M":
#     sub = st.radio("", ["🔔  Alarm Information","⚡  Device Overview"],
#                    horizontal=True, label_visibility="collapsed")
#     sub = sub.split("  ",1)[1].strip()
#     st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

#     alarm_log = get_alert_log(200)
#     all_alarms = []
#     for a in alerts:
#         all_alarms.append({"device_type":"Inverter","level":"Critical","status":"Active",
#             "plant_name":a.get("plant_name","—"),"sn":a.get("inverter_sn","—"),
#             "content":a.get("issue","—"),"brand":a.get("brand","—"),
#             "time":datetime.now().strftime("%Y-%m-%d %H:%M")})
#     if not alarm_log.empty:
#         for _, r in alarm_log.iterrows():
#             all_alarms.append({"device_type":"Inverter","level":"Warning","status":"Resolved",
#                 "plant_name":r.get("plant_name","—"),"sn":r.get("inverter_sn","—"),
#                 "content":r.get("issue","—"),"brand":r.get("brand","—"),
#                 "time":r.get("alerted_at","—")})

#     if sub == "Alarm Information":
#         st.markdown('<div class="page-hdr"><h1>Alarm Information</h1>'
#                     '<p>Fault detection and alert history</p></div>',
#                     unsafe_allow_html=True)

#         plant_opts = ["All"] + sorted(df["plant_name"].dropna().unique()) if not df.empty else ["All"]
#         sn_opts    = ["All"] + sorted(df["inverter_sn"].dropna().unique()) if not df.empty else ["All"]
#         brand_opts = ["All"] + sorted(df["brand"].dropna().unique())       if not df.empty else ["All"]

#         fc1,fc2,fc3,fc4,fc5 = st.columns(5)
#         with fc1: fp = st.selectbox("Plant Name",  plant_opts)
#         with fc2: fs = st.selectbox("S/N",         sn_opts)
#         with fc3: fb = st.selectbox("Brand",        brand_opts)
#         with fc4: fst= st.selectbox("Status",       ["All","Active","Resolved"])
#         with fc5: fl = st.selectbox("Level",        ["All","Critical","Warning"])

#         filt = all_alarms[:]
#         if fp !="All": filt=[a for a in filt if a["plant_name"]==fp]
#         if fs !="All": filt=[a for a in filt if a["sn"]        ==fs]
#         if fb !="All": filt=[a for a in filt if a["brand"]     ==fb]
#         if fst!="All": filt=[a for a in filt if a["status"]    ==fst]
#         if fl !="All": filt=[a for a in filt if a["level"]     ==fl]

#         m1,m2,m3 = st.columns(3)
#         m1.metric("Total", len(filt))
#         m2.metric("Active",   sum(1 for a in filt if a["status"]=="Active"))
#         m3.metric("Resolved", sum(1 for a in filt if a["status"]=="Resolved"))

#         if not filt:
#             st.success("✅ No alarms — all systems operating normally.")
#         else:
#             st.markdown('<div class="tbl">', unsafe_allow_html=True)
#             st.markdown('<div class="tbl-hdr tbl-alarm">'
#                         '<div>Device</div><div>Level</div><div>Status</div>'
#                         '<div>Plant</div><div>S/N</div><div>Issue</div><div>Time</div>'
#                         '</div>', unsafe_allow_html=True)
#             for a in filt:
#                 st.markdown(
#                     f'<div class="tbl-row tbl-alarm">'
#                       f'<div>{a["device_type"]}</div>'
#                       f'<div>{badge(a["level"],"level")}</div>'
#                       f'<div>{badge(a["status"],"status_alarm")}</div>'
#                       f'<div>{chip(a["brand"])} {a["plant_name"]}</div>'
#                       f'<div style="font-size:11px;color:var(--text3);font-family:\'JetBrains Mono\',monospace;">{a["sn"]}</div>'
#                       f'<div>{a["content"]}</div>'
#                       f'<div style="font-size:11px;color:var(--text3);">{a["time"]}</div>'
#                     f'</div>', unsafe_allow_html=True)
#             st.markdown('</div>', unsafe_allow_html=True)

#     else:
#         st.markdown('<div class="page-hdr"><h1>Device Overview</h1>'
#                     '<p>Live readings for every inverter</p></div>',
#                     unsafe_allow_html=True)
#         if df.empty:
#             st.warning("⚠️ No data."); st.stop()

#         fc1,fc2,fc3,fc4 = st.columns(4)
#         with fc1: bf = st.selectbox("Brand",  ["All"]+sorted(df["brand"].dropna().unique()),       key="do_b")
#         with fc2: pf = st.selectbox("Plant",  ["All"]+sorted(df["plant_name"].dropna().unique()),  key="do_p")
#         with fc3: sf = st.selectbox("S/N",    ["All"]+sorted(df["inverter_sn"].dropna().unique()), key="do_s")
#         with fc4: stf= st.selectbox("Status", ["All"]+sorted(df["status"].dropna().unique()),      key="do_st")

#         vw = df.copy()
#         if bf !="All": vw=vw[vw["brand"]       ==bf]
#         if pf !="All": vw=vw[vw["plant_name"]  ==pf]
#         if sf !="All": vw=vw[vw["inverter_sn"] ==sf]
#         if stf!="All": vw=vw[vw["status"]      ==stf]

#         st.markdown(
#             f'<div class="stat-row">'
#               f'<div class="stat-item"><div class="stat-val">{len(vw)}</div><div class="stat-lbl">Inverters</div></div>'
#               f'<div class="stat-item"><div class="stat-val">{f(vw["power_kw"].sum(),2)} kW</div><div class="stat-lbl">Total Power</div></div>'
#               f'<div class="stat-item"><div class="stat-val">{f(vw["today_kwh"].sum(),1)} kWh</div><div class="stat-lbl">Daily Yield</div></div>'
#               f'<div class="stat-item"><div class="stat-val">{int((vw["status"].str.lower()=="online").sum())}</div><div class="stat-lbl">Online</div></div>'
#             f'</div>', unsafe_allow_html=True)

#         alert_sns = {a.get("inverter_sn") for a in alerts}
#         for _, row in vw.iterrows():
#             sn    = str(row.get("inverter_sn","N/A"))
#             brand = str(row.get("brand",""))
#             st_   = str(row.get("status",""))
#             params = [
#                 ("Power Now",   f(row.get("power_kw"),2),  "kW"),
#                 ("Daily Yield", f(row.get("today_kwh"),1), "kWh"),
#                 ("Total Yield", f(row.get("total_kwh"),3), "MWh"),
#                 ("Temperature", f(row.get("temperature"),1),"°C"),
#                 ("AC Voltage",  f(row.get("voltage"),1),   "V"),
#                 ("AC Current",  f(row.get("current_a"),1), "A"),
#             ]
#             p_html = "".join(
#                 f'<div><div class="param-label">{l}</div>'
#                 f'<div class="param-val">{v}<span class="param-unit"> {u}</span></div></div>'
#                 for l,v,u in params)
#             border = "border-left:3px solid var(--red);" if sn in alert_sns else ""
#             st.markdown(
#                 f'<div class="inv-card" style="{border}">'
#                   f'<div class="inv-header">'
#                     f'<div><div class="inv-name">{row.get("plant_name","")}</div>'
#                     f'<div class="inv-meta">S/N: {sn} · {chip(brand)} · {row.get("last_update","—")}</div></div>'
#                     + badge(st_) +
#                   f'</div>'
#                   f'<div class="inv-params">{p_html}</div>'
#                 f'</div>', unsafe_allow_html=True)


# # ══════════════════════════════════════════════════════════════
# #  REPORT  — pulls historical data from Solis API directly
# # ══════════════════════════════════════════════════════════════
# elif page == "Report":
#     st.markdown('<div class="page-hdr"><h1>Plant Report</h1>'
#                 '<p>Historical generation data from Solis Cloud</p></div>',
#                 unsafe_allow_html=True)

#     rtype = st.radio("", ["Daily","Monthly","Annual","Total"],
#                      horizontal=True, label_visibility="collapsed")
#     st.markdown('<div style="height:10px"></div>', unsafe_allow_html=True)

#     # Plant comes from the sidebar active_plant selector
#     sel_plant = active_plant   # 'All Plants' or a specific plant name

#     fc1, fc2 = st.columns([2, 1])
#     with fc1:
#         st.markdown(
#             f'<div style="background:#f0fdf4;border:1px solid #86efac;border-radius:8px;'
#             f'padding:10px 14px;font-size:13px;font-weight:600;color:#166534;">'
#             f'📍 {sel_plant}</div>',
#             unsafe_allow_html=True)
#     with fc2: sel_date = st.date_input("Date", value=date.today())

#     # Shared line chart helper
#     def line_chart(fig, h=360):
#         fig = chart_style(fig, h)
#         fig.update_traces(selector=dict(type="scatter"), line=dict(width=2.5))
#         fig.update_layout(hovermode="x unified")
#         return fig

#     # Get plant IDs for selected plant
#     from utils.solis_api import (get_plants as _get_solis_plants,
#                                   get_all_plants_daily, get_all_plants_monthly,
#                                   get_plant_daily_history   as solis_daily,
#                                   get_plant_monthly_history as solis_monthly)
#     from utils.growatt_api import (get_plant_daily_history   as growatt_daily,
#                                    get_plant_monthly_history as growatt_monthly,
#                                    _get_plants               as _get_growatt_plants)

#     @st.cache_data(ttl=300)
#     def _plants_cached():
#         plants = []
#         try:
#             for p in _get_solis_plants():
#                 plants.append({"name": p.get("stationName"), "id": p.get("id"), "brand": "Solis"})
#         except Exception: pass
#         try:
#             for p in _get_growatt_plants():
#                 pid   = str(p.get("pId") or p.get("plantId",""))
#                 pname = p.get("plantNameEncryption") or p.get("plantName","")
#                 plants.append({"name": pname, "id": pid, "brand": "Growatt"})
#         except Exception: pass
#         return plants

#     all_plants    = _plants_cached()
#     plant_id_map  = {p["name"]: (p["id"], p["brand"]) for p in all_plants}

#     def get_daily_history(plant_name, month_str):
#         info = plant_id_map.get(plant_name)
#         if not info: return []
#         pid, brand = info
#         if brand == "Growatt": return growatt_daily(pid, month_str)
#         return solis_daily(pid, month_str)

#     def get_monthly_history(plant_name, year_str):
#         info = plant_id_map.get(plant_name)
#         if not info: return []
#         pid, brand = info
#         if brand == "Growatt": return growatt_monthly(pid, year_str)
#         return solis_monthly(pid, year_str)

#     # ── DAILY ────────────────────────────────────────────────
#     if rtype == "Daily":
#         # Determine brand of selected plant
#         sel_brand_for_report = "Solis"
#         if sel_plant != "All Plants":
#             info = plant_id_map.get(sel_plant)
#             if info: sel_brand_for_report = info[1]

#         # For Growatt: use stationDay API (has per-day hourly data)
#         # For Solis: use local DB (5-min readings collected by the app)
#         if sel_brand_for_report == "Growatt" and sel_plant != "All Plants":
#             month_str_d = sel_date.strftime("%Y-%m")
#             with st.spinner("Fetching daily data from Growatt…"):
#                 rows = get_daily_history(sel_plant, month_str_d)

#             if not rows:
#                 st.info(f"No data returned from Growatt for {sel_date.strftime('%B %Y')}.")
#             else:
#                 # Filter to selected date
#                 day_rows = [r for r in rows if r.get("date","").startswith(str(sel_date))]
#                 if not day_rows:
#                     # Show full month as fallback
#                     day_rows = rows
#                     st.info(f"Showing full month data — no hourly breakdown available for {sel_date}.")

#                 daily_df = pd.DataFrame(day_rows)
#                 daily_df["date"] = pd.to_datetime(daily_df["date"], errors="coerce")
#                 daily_df = daily_df.dropna(subset=["date"]).sort_values("date")

#                 sec(f"Daily Generation — {sel_plant} ({sel_date.strftime('%B %Y')})")
#                 fig = go.Figure()
#                 fig.add_trace(go.Bar(
#                     x=daily_df["date"], y=daily_df["energy_kwh"],
#                     name="Yield (kWh)", marker_color="rgba(16,185,129,.25)",
#                     marker_line_width=0,
#                 ))
#                 fig.add_trace(go.Scatter(
#                     x=daily_df["date"], y=daily_df["energy_kwh"],
#                     name="Yield", mode="lines+markers",
#                     line=dict(color="#10b981", width=2.5),
#                     marker=dict(size=6, color="#10b981"),
#                 ))
#                 fig.update_layout(
#                     plot_bgcolor="#fff", paper_bgcolor="#fff",
#                     font_family="Inter", font_color="#64748b",
#                     margin=dict(l=0,r=0,t=16,b=0), height=360,
#                     hovermode="x unified", bargap=0.25,
#                     legend=dict(bgcolor="rgba(0,0,0,0)"),
#                     yaxis=dict(title="kWh", showgrid=True, gridcolor="#f1f5f9", zeroline=False),
#                 )
#                 fig.update_xaxes(showgrid=False, zeroline=False, tickformat="%d %b")
#                 st.plotly_chart(fig, use_container_width=True)

#                 tot = daily_df["energy_kwh"].sum()
#                 c1,c2 = st.columns(2)
#                 c1.metric("Month Total", f"{tot:.1f} kWh")
#                 c2.metric("Estimated Earning", earn(tot))

#         else:
#             # Solis / All Plants — use local DB (5-min power readings)
#             hist_df = get_history(hours=8760)
#             if hist_df.empty:
#                 st.info("📭 No intraday data yet — the app collects readings every 5 min. "
#                         "Come back after the app has been running for a while.")
#             else:
#                 hist_df["fetched_at"] = pd.to_datetime(hist_df["fetched_at"])
#                 hist_df["power_kw"]   = pd.to_numeric(hist_df["power_kw"],  errors="coerce")
#                 hist_df["today_kwh"]  = pd.to_numeric(hist_df["today_kwh"], errors="coerce")
#                 if sel_plant != "All Plants":
#                     hist_df = hist_df[hist_df["plant_name"] == sel_plant]

#                 day = hist_df[hist_df["fetched_at"].dt.date == sel_date].sort_values("fetched_at")
#                 if day.empty:
#                     st.info(f"No intraday data for {sel_date}. "
#                             f"Try today's date — data builds up every 5 minutes the app is running.")
#                 else:
#                     sec("Power Output Throughout the Day (kW)")
#                     fig = px.line(day, x="fetched_at", y="power_kw", color="inverter_sn",
#                                   color_discrete_sequence=PALETTE,
#                                   labels={"fetched_at":"Time","power_kw":"Power (kW)",
#                                           "inverter_sn":"Inverter"})
#                     st.plotly_chart(line_chart(fig, 360), use_container_width=True)

#                     sec("Peak Power & Daily Generation per Inverter")
#                     sm = (day.groupby(["plant_name","inverter_sn","brand"])
#                           .agg(Peak_kW=("power_kw","max"), Daily_kWh=("today_kwh","max"))
#                           .reset_index()
#                           .rename(columns={"plant_name":"Plant","inverter_sn":"S/N","brand":"Brand"}))
#                     st.dataframe(sm, use_container_width=True, hide_index=True)

#     # ── MONTHLY ───────────────────────────────────────────────
#     elif rtype == "Monthly":
#         month_str = sel_date.strftime("%Y-%m")

#         with st.spinner(f"Fetching daily data for {sel_date.strftime('%B %Y')}…"):
#             if sel_plant == "All Plants":
#                 api_df = get_all_plants_daily(month_str)
#                 if not api_df.empty:
#                     daily = (api_df.groupby("date")["energy_kwh"]
#                              .sum().reset_index())
#                     daily.columns = ["Date","Daily Yield (kWh)"]
#                     income_df = api_df.groupby("date")["income"].sum().reset_index()
#                     income_df.columns = ["Date","Income (INR)"]
#                     daily = daily.merge(income_df, on="Date", how="left")
#                 else:
#                     daily = pd.DataFrame()
#             else:
#                 rows = get_daily_history(sel_plant, month_str)
#                 if rows:
#                     daily = pd.DataFrame(rows).rename(columns={
#                         "date":"Date","energy_kwh":"Daily Yield (kWh)","income":"Income (INR)"})
#                     daily["Date"] = pd.to_datetime(daily["Date"], errors="coerce")
#                 else:
#                     daily = pd.DataFrame()

#         if daily.empty or "Daily Yield (kWh)" not in daily.columns:
#             st.info(f"No data from Solis API for {sel_date.strftime('%B %Y')}.")
#         else:
#             daily = daily.dropna(subset=["Date"]).sort_values("Date")

#             # Combined bar + line chart matching Solis style
#             sec(f"Daily Generation — {sel_date.strftime('%B %Y')}")
#             fig = go.Figure()
#             # Bar: yield
#             fig.add_trace(go.Bar(
#                 x=daily["Date"], y=daily["Daily Yield (kWh)"],
#                 name="Yield (kWh)", marker_color="rgba(13,148,136,.25)",
#                 marker_line_width=0,
#             ))
#             # Line: yield trend
#             fig.add_trace(go.Scatter(
#                 x=daily["Date"], y=daily["Daily Yield (kWh)"],
#                 name="Yield", mode="lines+markers",
#                 line=dict(color="#0d9488", width=2.5),
#                 marker=dict(size=5, color="#0d9488"),
#             ))
#             # Line: revenue (right axis)
#             if "Income (INR)" in daily.columns:
#                 fig.add_trace(go.Scatter(
#                     x=daily["Date"], y=daily["Income (INR)"],
#                     name="Revenue (INR)", mode="lines+markers",
#                     line=dict(color="#f59e0b", width=2, dash="dot"),
#                     marker=dict(size=5, color="#f59e0b"),
#                     yaxis="y2",
#                 ))
#             fig.update_layout(
#                 plot_bgcolor="#fff", paper_bgcolor="#fff",
#                 font_family="Inter", font_color="#64748b",
#                 margin=dict(l=0,r=60,t=16,b=0), height=380,
#                 hovermode="x unified", bargap=0.25,
#                 legend=dict(bgcolor="rgba(0,0,0,0)", orientation="h",
#                             yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
#                 yaxis=dict(title="kWh", showgrid=True, gridcolor="#f1f5f9",
#                            zeroline=False, tickfont_size=11),
#                 yaxis2=dict(title="INR", overlaying="y", side="right",
#                             showgrid=False, zeroline=False, tickfont_size=11),
#             )
#             fig.update_xaxes(showgrid=False, zeroline=False, tickfont_size=11,
#                              tickformat="%d", dtick="D1")
#             st.plotly_chart(fig, use_container_width=True)

#             tot = daily["Daily Yield (kWh)"].sum()
#             m1,m2,m3 = st.columns(3)
#             m1.metric("Month Total", f"{tot:.1f} kWh")
#             m2.metric("Month Total (MWh)", f"{tot/1000:.3f} MWh")
#             m3.metric("Estimated Earning", earn(tot))

#     # ── ANNUAL ────────────────────────────────────────────────
#     elif rtype == "Annual":
#         year_str = str(sel_date.year)

#         with st.spinner(f"Fetching monthly data for {year_str}…"):
#             if sel_plant == "All Plants":
#                 api_df = get_all_plants_monthly(year_str)
#                 if not api_df.empty:
#                     monthly = (api_df.groupby("month")["energy_kwh"]
#                                .sum().reset_index())
#                     monthly.columns = ["Month","kWh"]
#                 else:
#                     monthly = pd.DataFrame()
#             else:
#                 rows = get_monthly_history(sel_plant, year_str)
#                 if rows:
#                     monthly = pd.DataFrame(rows).rename(columns={"month":"Month","energy_kwh":"kWh"})
#                 else:
#                     monthly = pd.DataFrame()

#         if monthly.empty or "kWh" not in monthly.columns:
#             st.info(f"No data from Solis API for {year_str}.")
#         else:
#             monthly = monthly[monthly["kWh"] > 0]

#             sec(f"Monthly Generation — {year_str}")
#             fig = go.Figure()
#             fig.add_trace(go.Bar(
#                 x=monthly["Month"], y=monthly["kWh"],
#                 name="Yield (kWh)", marker_color="rgba(245,158,11,.3)",
#                 marker_line_width=0,
#             ))
#             fig.add_trace(go.Scatter(
#                 x=monthly["Month"], y=monthly["kWh"],
#                 name="Trend", mode="lines+markers",
#                 line=dict(color="#f59e0b", width=2.5),
#                 marker=dict(size=7, color="#f59e0b"),
#             ))
#             fig.update_layout(
#                 plot_bgcolor="#fff", paper_bgcolor="#fff",
#                 font_family="Inter", font_color="#64748b",
#                 margin=dict(l=0,r=0,t=16,b=0), height=360,
#                 hovermode="x unified", bargap=0.3,
#                 legend=dict(bgcolor="rgba(0,0,0,0)"),
#                 yaxis=dict(showgrid=True, gridcolor="#f1f5f9",
#                            zeroline=False, tickfont_size=11),
#             )
#             fig.update_xaxes(showgrid=False, zeroline=False, tickfont_size=11)
#             st.plotly_chart(fig, use_container_width=True)

#             tot_yr = monthly["kWh"].sum()
#             m1,m2,m3 = st.columns(3)
#             m1.metric("Year Total", f"{tot_yr:.1f} kWh")
#             m2.metric("Year Total (MWh)", f"{tot_yr/1000:.3f} MWh")
#             m3.metric("Est. Annual Earning", earn(tot_yr))

#     # ── TOTAL ─────────────────────────────────────────────────
#     else:
#         sec("Total Yield per Plant (All-time)")
#         if not df.empty:
#             gt = (df.groupby(["plant_name","brand"])
#                   .agg(total_mwh=("total_kwh","sum"), daily_kwh=("today_kwh","sum"))
#                   .reset_index())

#             fig = go.Figure()
#             for i, row in gt.iterrows():
#                 fig.add_trace(go.Bar(
#                     x=[row["plant_name"]], y=[row["total_mwh"]],
#                     name=row["plant_name"],
#                     marker_color=PALETTE[i % len(PALETTE)],
#                     marker_line_width=0,
#                 ))
#             fig.update_layout(
#                 plot_bgcolor="#fff", paper_bgcolor="#fff",
#                 font_family="Inter", font_color="#64748b",
#                 margin=dict(l=0,r=0,t=16,b=0), height=340,
#                 showlegend=False, bargap=0.35,
#                 yaxis=dict(title="MWh", showgrid=True, gridcolor="#f1f5f9",
#                            zeroline=False, tickfont_size=11),
#             )
#             fig.update_xaxes(showgrid=False, zeroline=False, tickfont_size=11)
#             st.plotly_chart(fig, use_container_width=True)

#             gt_disp = gt.rename(columns={"plant_name":"Plant","brand":"Brand",
#                                           "total_mwh":"Total Yield (MWh)",
#                                           "daily_kwh":"Today (kWh)"})
#             st.dataframe(gt_disp, use_container_width=True, hide_index=True)


# # ══════════════════════════════════════════════════════════════
# #  SERVICE
# # ══════════════════════════════════════════════════════════════
# elif page == "Service":
#     st.markdown('<div class="page-hdr"><h1>Plant Management</h1>'
#                 '<p>All registered plants and operational details</p></div>',
#                 unsafe_allow_html=True)
#     if df.empty:
#         st.warning("⚠️ No data."); st.stop()

#     fc1,fc2 = st.columns(2)
#     with fc1: pf2 = st.selectbox("Plant", ["All"]+sorted(df["plant_name"].dropna().unique()), key="pm_p")
#     with fc2: bf2 = st.selectbox("Brand", ["All"]+sorted(df["brand"].dropna().unique()),      key="pm_b")

#     ps = (df.groupby(["plant_name","brand"])
#           .agg(power_kw=("power_kw","sum"), today_kwh=("today_kwh","sum"),
#                total_kwh=("total_kwh","sum"), inv_count=("inverter_sn","count"))
#           .reset_index())
#     if pf2!="All": ps=ps[ps["plant_name"]==pf2]
#     if bf2!="All": ps=ps[ps["brand"]==bf2]

#     st.markdown(
#         f'<div class="stat-row">'
#           f'<div class="stat-item"><div class="stat-val">{len(ps)}</div><div class="stat-lbl">Plants</div></div>'
#           f'<div class="stat-item"><div class="stat-val">{f(ps["power_kw"].sum(),2)} kW</div><div class="stat-lbl">Total Power</div></div>'
#           f'<div class="stat-item"><div class="stat-val">{f(ps["today_kwh"].sum(),1)} kWh</div><div class="stat-lbl">Daily Yield</div></div>'
#           f'<div class="stat-item"><div class="stat-val">{f(ps["total_kwh"].sum(),1)} MWh</div><div class="stat-lbl">Total Yield</div></div>'
#         f'</div>', unsafe_allow_html=True)

#     st.markdown('<div class="tbl">', unsafe_allow_html=True)
#     st.markdown('<div class="tbl-hdr tbl-plant">'
#                 '<div>Plant Name</div><div>Brand</div><div>Organisation</div>'
#                 '<div>Inverters</div><div>Power (kW)</div>'
#                 '<div>Daily Yield</div><div>Total Yield</div><div>Status</div>'
#                 '</div>', unsafe_allow_html=True)
#     for _, row in ps.iterrows():
#         pr   = df[df["plant_name"]==row["plant_name"]]
#         on   = int((pr["status"].str.lower()=="online").sum())
#         tot  = int(row["inv_count"])
#         pst  = "Online" if on==tot and tot>0 else ("Offline" if on==0 else "Warning")
#         dy   = float(row["today_kwh"] or 0)
#         dy_s = f"{dy/1000:.3f} MWh" if dy>=1000 else f"{dy:.1f} kWh"
#         ty   = float(row["total_kwh"] or 0)
#         ty_s = f"{ty/1000:.3f} GWh" if ty>=1000 else f"{ty:.3f} MWh"
#         st.markdown(
#             f'<div class="tbl-row tbl-plant">'
#               f'<div class="cell-link">{row["plant_name"]}</div>'
#               f'<div>{chip(row["brand"])}</div>'
#               f'<div>Fractal Energy</div>'
#               f'<div>{on}/{tot}</div>'
#               f'<div><b>{f(row["power_kw"],2)}</b> kW</div>'
#               f'<div>{dy_s}</div><div>{ty_s}</div>'
#               f'<div>{badge(pst)}</div>'
#             f'</div>', unsafe_allow_html=True)
#     st.markdown('</div>', unsafe_allow_html=True)


# # ══════════════════════════════════════════════════════════════
# #  SETTINGS
# # ══════════════════════════════════════════════════════════════
# elif page == "Settings":
#     st.markdown('<div class="page-hdr"><h1>Settings</h1>'
#                 '<p>Credentials, alerts and app configuration</p></div>',
#                 unsafe_allow_html=True)

#     from config import (SOLIS_API_KEY, GROWATT_USERNAME, SUNGROW_APP_KEY,
#                         EMAIL_USER, TO_EMAILS, RATE_PER_KWH)

#     st.markdown("#### 🔑 API Credentials")
#     for brand,ok,hint in [
#         ("Solis",   bool(SOLIS_API_KEY),
#          SOLIS_API_KEY[:10]+"…" if SOLIS_API_KEY else "Not configured"),
#         ("Growatt", bool(GROWATT_USERNAME),
#          GROWATT_USERNAME or "Set GROWATT_USERNAME in config.py"),
#         ("Sungrow", bool(SUNGROW_APP_KEY),
#          SUNGROW_APP_KEY[:10]+"…" if SUNGROW_APP_KEY else "Set SUNGROW_APP_KEY in config.py"),
#     ]:
#         c1,c2,c3 = st.columns([1,1,4])
#         c1.markdown(f"**{brand}**")
#         c2.markdown("✅ OK" if ok else "⚠️ Not set")
#         c3.markdown(f"`{hint}`")

#     st.divider()
#     st.markdown("#### 📧 Email Alerts")
#     st.markdown(f"**Sender:** `{EMAIL_USER}`")
#     st.markdown(f"**Recipients:** `{', '.join(TO_EMAILS)}`")
#     st.divider()
#     st.markdown("#### 💰 Tariff Rate")
#     st.info(f"Current rate: **₹{RATE_PER_KWH}/kWh** — edit `RATE_PER_KWH` in config.py")
#     st.divider()
#     st.markdown("#### 👤 Logged in as")
#     st.info(f"`{st.session_state.user}`")
#     st.divider()
#     st.markdown("#### 🗂 Project Structure")
#     st.code("""
# solar_dashboard/
# ├── app.py              ← streamlit run app.py
# ├── config.py           ← ✏️  credentials & settings
# ├── requirements.txt
# ├── data/solar_data.db  ← auto-created
# └── utils/
#     ├── solis_api.py    ├── growatt_api.py
#     ├── sungrow_api.py  ├── aggregator.py
#     ├── database.py     └── alerts.py
#     """, language="")

# ============================================================
#  app.py  —  Solar Dashboard  |  streamlit run app.py
# ============================================================
import streamlit as st
from streamlit_autorefresh import st_autorefresh
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta

from config import REFRESH_INTERVAL_SECONDS, RATE_PER_KWH
from utils.database import init_db, get_history, get_alert_log
from utils.aggregator import fetch_all_brands, check_alerts

# ─────────────────────────────────────────────────────────────
st.set_page_config(page_title="Solar Dashboard · Fractal Energy",
                   page_icon="☀️", layout="wide",
                   initial_sidebar_state="expanded")

# ══════════════════════════════════════════════════════════════
#  GLOBAL CSS  —  Navy · Teal · Amber theme
# ══════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

*,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}

:root{
  /* ── Orange / Amber / Warm palette ── */
  --primary:   #ea580c;
  --primary-l: #fff7ed;
  --primary-d: #c2410c;
  --amber:     #f59e0b;
  --amber-l:   #fffbeb;
  --amber-d:   #b45309;
  --yellow:    #eab308;
  --yellow-l:  #fefce8;

  /* ── Semantic ── */
  --green:     #16a34a;
  --green-l:   #dcfce7;
  --red:       #dc2626;
  --red-l:     #fee2e2;
  --blue:      #2563eb;
  --blue-l:    #eff6ff;

  /* ── Surfaces ── */
  --bg:        #faf7f3;
  --card:      #ffffff;
  --border:    #e7e5e4;
  --border2:   #d6d3d1;

  /* ── Text ── */
  --text:      #1c1917;
  --text2:     #57534e;
  --text3:     #a8a29e;

  /* ── Sidebar ── */
  --sb-bg:     #1c1917;
  --sb-border: rgba(255,255,255,.07);

  /* ── Shadows ── */
  --shadow:    0 1px 3px rgba(28,25,23,.04),0 4px 16px rgba(28,25,23,.04);
  --shadow-lg: 0 8px 32px rgba(28,25,23,.10);
  --shadow-p:  0 4px 20px rgba(234,88,12,.22);

  /* ── legacy aliases for old inline HTML ── */
  --navy:      #1c1917;
  --navy2:     #292524;
  --navy3:     #292524;
  --teal:      #ea580c;
  --teal-l:    #fff7ed;
  --teal-d:    #c2410c;
  --orange:    #f59e0b;
  --orange-l:  #fffbeb;
  --sky:       #f59e0b;
  --sky-l:     #fffbeb;

  /* ── Shadows ── */
  --shadow:    0 1px 4px rgba(10,22,40,.06),0 4px 20px rgba(10,22,40,.05);
  --shadow-lg: 0 8px 40px rgba(10,22,40,.12);
  --shadow-teal:0 4px 20px rgba(234,88,12,.25);
}

/* ── Fonts ── */
html,body,[data-testid="stAppViewContainer"]{
  background:var(--bg)!important;
  font-family:'Inter',sans-serif!important;
  color:var(--text);
}
[data-testid="stHeader"]{background:transparent!important;display:none;}
#MainMenu,footer{visibility:hidden;}
[data-testid="stDecoration"]{display:none;}
.block-container{padding:28px 32px!important;max-width:100%!important;}

/* ══ SIDEBAR ══════════════════════════════════════════════ */
[data-testid="stSidebar"]{
  background:var(--sb-bg)!important;
  border-right:1px solid var(--sb-border)!important;
}
[data-testid="stSidebar"]>div{padding-top:0!important;}
section[data-testid="stSidebarContent"]{padding:0!important;}

.sb-logo{
  padding:22px 18px 16px;
  border-bottom:1px solid var(--sb-border);
  margin-bottom:4px;
  display:flex;align-items:center;gap:11px;
}
.sb-logo-icon{
  width:40px;height:40px;
  background:linear-gradient(135deg,var(--primary),var(--amber));
  border-radius:10px;display:flex;align-items:center;justify-content:center;
  font-size:18px;flex-shrink:0;box-shadow:var(--shadow-p);
}
.sb-logo-title{color:#fafaf9;font-weight:700;font-size:14px;letter-spacing:-.2px;}
.sb-logo-sub{color:#78716c;font-size:11px;margin-top:1px;}
.sb-section{
  padding:16px 18px 5px;
  font-size:9.5px;font-weight:700;color:#57534e;
  text-transform:uppercase;letter-spacing:.13em;
}
.sb-time{
  padding:12px 18px;font-size:10.5px;color:#57534e;
  border-top:1px solid var(--sb-border);margin-top:6px;
  font-family:'JetBrains Mono',monospace;line-height:1.6;
}

/* ── Sidebar radio nav ── */
[data-testid="stSidebar"] [data-testid="stRadio"]>div{gap:2px!important;}
[data-testid="stSidebar"] [data-testid="stRadio"] label{
  border-radius:8px!important;padding:9px 14px!important;
  font-size:13px!important;font-weight:500!important;
  color:#a8a29e!important;transition:all .15s!important;
}
[data-testid="stSidebar"] [data-testid="stRadio"] label:hover{
  background:rgba(255,255,255,.06)!important;color:#fafaf9!important;
}

/* ══ LOGIN PAGE ═══════════════════════════════════════════ */
.login-split{min-height:100vh;display:flex;}
.login-left{
  flex:0 0 42%;
  background:linear-gradient(160deg,#1c1917 0%,#292524 60%,#1a1816 100%);
  padding:60px 48px;display:flex;flex-direction:column;justify-content:center;
  position:relative;overflow:hidden;
}
.login-left::before{
  content:'';position:absolute;top:-120px;right:-80px;width:380px;height:380px;
  border-radius:50%;
  background:radial-gradient(circle,rgba(234,88,12,.18) 0%,transparent 70%);
}
.login-left::after{
  content:'';position:absolute;bottom:-100px;left:-60px;width:300px;height:300px;
  border-radius:50%;
  background:radial-gradient(circle,rgba(245,158,11,.12) 0%,transparent 70%);
}
.login-brand-icon{
  width:54px;height:54px;
  background:linear-gradient(135deg,var(--primary),var(--amber));
  border-radius:14px;display:flex;align-items:center;justify-content:center;
  font-size:26px;margin-bottom:18px;
  box-shadow:0 8px 24px rgba(234,88,12,.3);position:relative;z-index:1;
}
.login-brand-name{
  font-size:28px;font-weight:800;color:#fafaf9;letter-spacing:-.5px;
  margin-bottom:6px;position:relative;z-index:1;
}
.login-brand-sub{
  font-size:14px;color:#78716c;line-height:1.6;margin-bottom:44px;
  max-width:280px;position:relative;z-index:1;
}
.login-stat-row{display:flex;gap:14px;flex-wrap:wrap;position:relative;z-index:1;}
.login-stat-card{
  background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.09);
  border-radius:12px;padding:16px 18px;min-width:86px;
}
.login-stat-val{font-size:22px;font-weight:800;color:#fb923c;line-height:1;}
.login-stat-lbl{font-size:11px;color:#78716c;margin-top:4px;line-height:1.3;}
.login-right{
  flex:1;background:#fff;padding:60px 52px;
  display:flex;flex-direction:column;justify-content:center;
}
.login-right-inner{max-width:360px;}
.login-right-title{
  font-size:24px;font-weight:800;color:var(--text);
  letter-spacing:-.4px;margin-bottom:6px;
}
.login-right-sub{font-size:14px;color:var(--text3);margin-bottom:28px;}
.login-roles{
  margin-top:18px;font-size:12px;color:var(--text3);
  padding-top:14px;border-top:1px solid var(--border);
}
/* right panel input styles */
.login-right [data-testid="stTextInput"] input{
  background:#faf7f3!important;border:1.5px solid var(--border2)!important;
  border-radius:9px!important;font-size:14px!important;
  transition:border-color .15s!important;
}
.login-right [data-testid="stTextInput"] input:focus{
  border-color:var(--primary)!important;
  box-shadow:0 0 0 3px rgba(234,88,12,.1)!important;
}
.login-right .stButton>button{
  width:100%!important;padding:13px!important;font-size:15px!important;
}

/* ══ PAGE HEADER ══════════════════════════════════════════ */
.page-hdr{margin-bottom:24px;}
.page-hdr h1{font-size:24px;font-weight:800;color:var(--text);letter-spacing:-.5px;}
.page-hdr p{font-size:13px;color:var(--text3);margin-top:4px;}

/* ══ TOP NAV BAR ══════════════════════════════════════════ */
.top-nav{
  background:var(--sb-bg);border-radius:12px;
  padding:0 20px;margin-bottom:22px;height:50px;
  display:flex;align-items:center;justify-content:space-between;
  box-shadow:0 2px 10px rgba(0,0,0,.12);
}
.top-nav-brand{
  display:flex;align-items:center;gap:9px;
  font-size:14px;font-weight:700;color:#fafaf9;
}
.top-nav-brand span{
  width:28px;height:28px;
  background:linear-gradient(135deg,var(--primary),var(--amber));
  border-radius:7px;display:flex;align-items:center;justify-content:center;font-size:14px;
}
.top-nav-page{
  font-size:13px;font-weight:600;color:#a8a29e;
}
.top-nav-user{
  width:32px;height:32px;
  background:linear-gradient(135deg,var(--primary),var(--amber));
  border-radius:50%;display:flex;align-items:center;justify-content:center;
  font-size:12px;font-weight:700;color:#fff;
}

/* ══ KPI CARDS ════════════════════════════════════════════ */
.kpi-card{
  background:var(--card);border-radius:14px;padding:22px 20px;
  border:1px solid var(--border);box-shadow:var(--shadow);
  position:relative;overflow:hidden;transition:transform .15s,box-shadow .15s;
}
.kpi-card::after{
  content:'';position:absolute;top:0;left:0;right:0;height:3px;
  background:linear-gradient(90deg,var(--primary),var(--amber));
  border-radius:14px 14px 0 0;
}
.kpi-card.amber::after{background:linear-gradient(90deg,var(--amber),var(--yellow));}
.kpi-card.green::after{background:linear-gradient(90deg,#16a34a,#4ade80);}
.kpi-card.blue::after {background:linear-gradient(90deg,#2563eb,#60a5fa);}
.kpi-card.navy::after {background:linear-gradient(90deg,var(--primary),var(--amber));}
.kpi-card:hover{transform:translateY(-2px);box-shadow:var(--shadow-lg);}

.kpi-icon{
  width:46px;height:46px;border-radius:11px;
  display:flex;align-items:center;justify-content:center;font-size:20px;
  margin-bottom:12px;
}
.kpi-icon.teal  {background:var(--primary-l);color:var(--primary);}
.kpi-icon.orange{background:var(--primary-l);color:var(--primary);}
.kpi-icon.amber {background:var(--amber-l);color:var(--amber-d);}
.kpi-icon.green {background:var(--green-l);color:var(--green);}
.kpi-icon.navy  {background:var(--amber-l);color:var(--amber-d);}

.kpi-label{
  font-size:10.5px;color:var(--text3);font-weight:600;
  text-transform:uppercase;letter-spacing:.1em;margin-bottom:8px;
}
.kpi-value{font-size:28px;font-weight:800;color:var(--text);line-height:1;letter-spacing:-.5px;}
.kpi-unit{font-size:14px;font-weight:600;color:var(--text2);margin-left:3px;}
.kpi-meta{font-size:12px;color:var(--text3);margin-top:8px;line-height:1.4;}
.kpi-meta b{color:var(--primary);font-weight:600;}

/* ══ ALARM CARDS ══════════════════════════════════════════ */
.alarm-card{
  background:var(--card);border-radius:12px;padding:14px 16px;
  border:1px solid var(--border);border-left:4px solid var(--border2);
  margin-bottom:9px;display:flex;gap:12px;align-items:flex-start;
  box-shadow:var(--shadow);
}
.alarm-card.critical{border-left-color:var(--red);background:linear-gradient(90deg,#fff5f5,#fff);}
.alarm-card.warning {border-left-color:var(--amber);background:linear-gradient(90deg,#fffbf0,#fff);}
.alarm-card.info    {border-left-color:var(--blue);background:linear-gradient(90deg,#f0f7ff,#fff);}
.alarm-icon{width:30px;height:30px;border-radius:7px;flex-shrink:0;
  display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:700;}
.alarm-icon.critical{background:var(--red-l);color:var(--red);}
.alarm-icon.warning {background:var(--amber-l);color:var(--amber-d);}
.alarm-icon.info    {background:var(--blue-l);color:var(--blue);}
.alarm-title{font-size:13px;font-weight:700;color:var(--text);}
.alarm-meta{font-size:11px;color:var(--text3);margin-top:3px;}
.alarm-badge{margin-left:auto;padding:3px 9px;border-radius:6px;
  font-size:11px;font-weight:700;flex-shrink:0;}
.alarm-badge.critical{background:var(--red-l);color:var(--red);}
.alarm-badge.warning {background:var(--amber-l);color:var(--amber-d);}
.alarm-badge.info    {background:var(--blue-l);color:var(--blue);}

/* ══ SECTION HEADER ═══════════════════════════════════════ */
.sec-hdr{
  font-size:13px;font-weight:700;color:var(--text);
  display:flex;align-items:center;gap:8px;
  margin-bottom:14px;padding-bottom:10px;
  border-bottom:2px solid var(--border);
}
.sec-hdr-dot{
  width:8px;height:8px;border-radius:50%;
  background:linear-gradient(135deg,var(--primary),var(--amber));
  flex-shrink:0;
}

/* ══ CARD WRAPPER ═════════════════════════════════════════ */
.card{
  background:var(--card);border-radius:16px;padding:22px;
  border:1px solid var(--border);box-shadow:var(--shadow);margin-bottom:16px;
}

/* ══ INVERTER CARD ════════════════════════════════════════ */
.inv-card{
  background:var(--card);border-radius:16px;padding:22px;
  border:1px solid var(--border);box-shadow:var(--shadow);
  margin-bottom:14px;transition:border-color .15s,box-shadow .15s;
}
.inv-card:hover{border-color:var(--primary);box-shadow:var(--shadow-teal);}
.inv-card.alert-card{border-left:3px solid var(--red);}
.inv-header{
  display:flex;justify-content:space-between;align-items:flex-start;
  margin-bottom:18px;padding-bottom:14px;
  border-bottom:1px solid var(--border);
}
.inv-name{font-size:15px;font-weight:700;color:var(--text);letter-spacing:-.3px;}
.inv-meta{font-size:11px;color:var(--text3);margin-top:3px;font-family:'JetBrains Mono',monospace;}
.inv-params{display:grid;grid-template-columns:repeat(6,1fr);gap:16px;}
.param-label{
  font-size:10px;color:var(--text3);text-transform:uppercase;
  letter-spacing:.08em;font-weight:600;margin-bottom:4px;
}
.param-val{font-size:18px;font-weight:700;color:var(--text);letter-spacing:-.3px;}
.param-unit{font-size:11px;color:var(--text3);margin-left:2px;}
.inv-footer{margin-top:14px;font-size:11px;color:var(--text3);font-family:'JetBrains Mono',monospace;}

/* ══ TABLES ═══════════════════════════════════════════════ */
.tbl{
  background:var(--card);border-radius:16px;
  border:1px solid var(--border);overflow:hidden;box-shadow:var(--shadow);
}
.tbl-hdr,.tbl-row{
  display:grid;padding:0 20px;align-items:center;gap:10px;
}
.tbl-hdr{
  background:linear-gradient(90deg,#f8fafc,#f1f5f9);
  border-bottom:2px solid var(--border);
  font-size:10px;font-weight:700;color:var(--text3);
  text-transform:uppercase;letter-spacing:.1em;height:44px;
}
.tbl-row{
  min-height:54px;border-bottom:1px solid var(--border);
  font-size:13px;transition:background .1s;
}
.tbl-row:last-child{border-bottom:none;}
.tbl-row:hover{background:#f8fafc;}
.tbl-plant{grid-template-columns:2fr 1fr 1.1fr 1fr 1fr 1.1fr 1.3fr 1fr;}
.tbl-alarm{grid-template-columns:1fr 1fr 1fr 1.5fr 1.4fr 2.2fr 1.2fr;}
.cell-link{color:var(--primary);font-weight:700;cursor:pointer;font-size:13px;}

/* ══ BADGES ═══════════════════════════════════════════════ */
.badge{
  display:inline-flex;align-items:center;gap:5px;
  font-size:11px;font-weight:700;padding:4px 10px;
  border-radius:20px;letter-spacing:.02em;
}
.badge::before{content:'';width:6px;height:6px;border-radius:50%;}
.b-online {background:var(--green-l);color:#065f46;}
.b-online::before{background:var(--green);}
.b-offline{background:var(--red-l);color:#991b1b;}
.b-offline::before{background:var(--red);}
.b-warning{background:var(--amber-l);color:#92400e;}
.b-warning::before{background:var(--amber);}
.b-unknown{background:#f1f5f9;color:#64748b;}
.b-unknown::before{background:#94a3b8;}
.b-active {background:var(--red-l);color:#991b1b;}
.b-active::before{background:var(--red);}
.b-resolved{background:var(--green-l);color:#065f46;}
.b-resolved::before{background:var(--green);}
.b-critical{background:var(--red-l);color:#991b1b;font-weight:800;}
.b-critical::before{background:var(--red);}

/* ══ CHIPS ════════════════════════════════════════════════ */
.chip{
  display:inline-block;font-size:10px;font-weight:800;
  padding:3px 9px;border-radius:6px;
  letter-spacing:.1em;text-transform:uppercase;
}
.chip-solis  {background:#dbeafe;color:#1e40af;}
.chip-growatt{background:#d1fae5;color:#065f46;}
.chip-sungrow{background:#ffedd5;color:#c2410c;}

/* ══ ALERT STRIP ══════════════════════════════════════════ */
.alert-strip{
  background:linear-gradient(135deg,#fff1f2,#ffe4e6);
  border:1px solid #fecdd3;border-left:4px solid var(--red);
  border-radius:12px;padding:16px 18px;margin-bottom:12px;
  display:flex;gap:14px;align-items:flex-start;
}
.alert-strip-ico{font-size:20px;flex-shrink:0;}
.alert-strip-ttl{font-size:14px;font-weight:700;color:var(--red);}
.alert-strip-msg{font-size:12px;color:#7f1d1d;margin-top:3px;}

/* ══ STAT ROW ═════════════════════════════════════════════ */
.stat-row{
  background:var(--card);border-radius:14px;padding:16px 24px;
  border:1px solid var(--border);display:flex;gap:32px;
  margin-bottom:20px;align-items:center;flex-wrap:wrap;
  box-shadow:var(--shadow);
}
.stat-item{text-align:center;}
.stat-val{font-size:20px;font-weight:800;color:var(--text);letter-spacing:-.3px;}
.stat-lbl{font-size:10px;color:var(--text3);margin-top:2px;font-weight:600;text-transform:uppercase;letter-spacing:.08em;}

/* ══ STREAMLIT OVERRIDES ══════════════════════════════════ */
.stButton>button{
  background:linear-gradient(135deg,var(--primary),var(--primary-d))!important;
  color:#fff!important;border:none!important;border-radius:10px!important;
  font-family:'Inter',sans-serif!important;
  font-weight:700!important;font-size:13px!important;
  padding:10px 24px!important;letter-spacing:.01em!important;
  box-shadow:0 4px 12px rgba(234,88,12,.3)!important;
  transition:all .15s!important;
}
.stButton>button:hover{transform:translateY(-1px)!important;box-shadow:0 6px 20px rgba(234,88,12,.4)!important;}
div[data-testid="stSelectbox"]>label,
div[data-testid="stTextInput"]>label{
  font-size:12px!important;font-weight:700!important;
  color:var(--text2)!important;text-transform:uppercase!important;letter-spacing:.06em!important;
}
[data-testid="stRadio"]>label{font-size:13px!important;font-weight:600!important;}
.stRadio>div{gap:4px!important;}
.stAlert{border-radius:12px!important;}
div[data-testid="stTextInput"] input{
  border-radius:10px!important;border-color:var(--border2)!important;
  font-size:14px!important;font-family:'Inter',sans-serif!important;
}
div[data-testid="stSelectbox"]>div>div{
  border-radius:10px!important;border-color:var(--border2)!important;
  font-size:13px!important;
}

/* ══ LOGIN STREAMLIT INPUT OVERRIDES ═══════════════════════ */
/* Applied when sidebar is hidden = login / loading screens */
[data-testid="stSidebar"]:not([style*="visible"]) ~ * div[data-testid="stTextInput"] input,
.login-inputs div[data-testid="stTextInput"] input{
  background:rgba(255,255,255,.07)!important;
  border:1px solid rgba(255,255,255,.14)!important;
  border-radius:10px!important;color:#fafaf9!important;
  font-size:14px!important;padding:12px 14px!important;
}
.login-inputs div[data-testid="stTextInput"] input:focus{
  border-color:rgba(234,88,12,.6)!important;
  box-shadow:0 0 0 3px rgba(234,88,12,.15)!important;
}
.login-inputs div[data-testid="stTextInput"]>label{
  color:rgba(255,255,255,.5)!important;
}
.login-inputs .stButton>button{
  width:100%!important;padding:14px!important;font-size:15px!important;
  box-shadow:0 6px 20px rgba(234,88,12,.4)!important;
}

/* ══ DIVIDER ══════════════════════════════════════════════ */
.divider{height:1px;background:var(--border);margin:20px 0;}

/* ══ METRIC OVERRIDES ═════════════════════════════════════ */
[data-testid="stMetric"]{
  background:var(--card);border-radius:12px;padding:16px 18px;
  border:1px solid var(--border);box-shadow:var(--shadow);
}
[data-testid="stMetricLabel"]{font-size:11px!important;font-weight:700!important;color:var(--text3)!important;text-transform:uppercase!important;letter-spacing:.08em!important;}
[data-testid="stMetricValue"]{font-size:24px!important;font-weight:800!important;color:var(--text)!important;letter-spacing:-.4px!important;}
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  INIT
# ══════════════════════════════════════════════════════════════
init_db()

# ══════════════════════════════════════════════════════════════
#  SESSION STATE
# ══════════════════════════════════════════════════════════════
USERS = {
    "admin":    "1234"
}

for key, default in [
    ("logged_in",      False),
    ("user",           ""),
    ("plant_selected", False),
    ("sel_brands",     ["Solis"]),
    ("sel_plants",     []),        # list of selected plant names
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ══════════════════════════════════════════════════════════════
#  STEP 1 — LOGIN
# ══════════════════════════════════════════════════════════════
DARK_PAGE_CSS = """<style>
[data-testid="stSidebar"]{display:none!important;}
.block-container{padding:0!important;max-width:100%!important;}
</style>"""

if not st.session_state.logged_in:
    st.markdown(DARK_PAGE_CSS, unsafe_allow_html=True)
    st.markdown("""
    <div style="min-height:100vh;display:flex;align-items:center;justify-content:center;
    background:linear-gradient(135deg,#1c1917 0%,#292524 55%,#1a1816 100%);padding:20px;
    position:fixed;top:0;left:0;right:0;bottom:0;">
      <!-- ambient glows -->
      <div style="position:absolute;top:10%;left:50%;transform:translateX(-50%);
        width:500px;height:500px;border-radius:50%;
        background:radial-gradient(circle,rgba(234,88,12,.08) 0%,transparent 65%);pointer-events:none;"></div>
      <div style="position:absolute;bottom:5%;right:10%;width:350px;height:350px;border-radius:50%;
        background:radial-gradient(circle,rgba(245,158,11,.06) 0%,transparent 65%);pointer-events:none;"></div>
      <div style="width:100%;max-width:440px;position:relative;z-index:1;">
        <!-- icon + brand -->
        <div style="text-align:center;margin-bottom:28px;">
          <div style="width:72px;height:72px;
            background:linear-gradient(135deg,#ea580c,#f59e0b);
            border-radius:20px;display:flex;align-items:center;justify-content:center;
            font-size:34px;margin:0 auto 18px;
            box-shadow:0 10px 32px rgba(234,88,12,.45);">☀️</div>
          <div style="font-size:27px;font-weight:800;color:#fafaf9;letter-spacing:-.5px;">Solar Dashboard</div>
          <div style="font-size:13px;color:#78716c;margin-top:6px;">Fractal Energy · Monitoring Platform</div>
        </div>
        <!-- stat pills -->
        <div style="display:flex;gap:10px;justify-content:center;margin-bottom:28px;">
          <div style="background:rgba(234,88,12,.13);border:1px solid rgba(234,88,12,.25);
            border-radius:10px;padding:10px 18px;text-align:center;">
            <div style="font-size:16px;font-weight:800;color:#fb923c;line-height:1;">Live</div>
            <div style="font-size:10px;color:#78716c;margin-top:3px;">Monitoring</div>
          </div>
          <div style="background:rgba(234,88,12,.13);border:1px solid rgba(234,88,12,.25);
            border-radius:10px;padding:10px 18px;text-align:center;">
            <div style="font-size:16px;font-weight:800;color:#fb923c;line-height:1;">24/7</div>
            <div style="font-size:10px;color:#78716c;margin-top:3px;">Uptime</div>
          </div>
          <div style="background:rgba(234,88,12,.13);border:1px solid rgba(234,88,12,.25);
            border-radius:10px;padding:10px 18px;text-align:center;">
            <div style="font-size:16px;font-weight:800;color:#fb923c;line-height:1;">Auto</div>
            <div style="font-size:10px;color:#78716c;margin-top:3px;">Refresh</div>
          </div>
        </div>
        <!-- form card -->
        <div style="background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.1);
          border-radius:20px;padding:36px 34px;backdrop-filter:blur(20px);
          box-shadow:0 24px 64px rgba(0,0,0,.5);">
          <div style="font-size:16px;font-weight:700;color:#e7e5e4;margin-bottom:18px;">Sign in to continue</div>
    """, unsafe_allow_html=True)

    with st.container():
        st.markdown('<div class="login-inputs">', unsafe_allow_html=True)
        email    = st.text_input("Email Address", placeholder="your@email.com",
                                 label_visibility="visible")
        password = st.text_input("Password", placeholder="••••••••", type="password",
                                 label_visibility="visible")
        if st.button("Sign In →", use_container_width=True):
            if email in USERS and USERS[email] == password:
                st.session_state.logged_in = True
                st.session_state.user      = email
                st.rerun()
            else:
                st.error("Invalid email or password.")
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("""
          <div style="text-align:center;margin-top:18px;font-size:11.5px;color:#57534e;
            padding-top:14px;border-top:1px solid rgba(255,255,255,.07);">
            Secured by Fractal Energy &nbsp;·&nbsp; v2.0</div>
        </div>
      </div>
    </div>""", unsafe_allow_html=True)
    st.stop()

# ══════════════════════════════════════════════════════════════
#  STEP 2 — AUTO-LOAD ALL PLANTS  (runs once after login)
# ══════════════════════════════════════════════════════════════
if not st.session_state.plant_selected:
    st.markdown(DARK_PAGE_CSS, unsafe_allow_html=True)

    @st.cache_data(ttl=600)
    def _fetch_available_plants():
        available = []
        try:
            from utils.solis_api import get_plants as _sp
            for p in _sp():
                cap_raw = p.get("capacity","")
                available.append({
                    "brand":    "Solis",
                    "name":     p.get("stationName",""),
                    "id":       p.get("id",""),
                    "capacity": f"{cap_raw} kWp" if cap_raw else "—",
                    "location": p.get("city","") or p.get("address","") or "—",
                })
        except Exception as e:
            print(f"Plant loader Solis error: {e}")
        try:
            from utils.growatt_api import _get_plants, login as glogin
            glogin()
            for p in _get_plants():
                cap_raw = p.get("nominalPower","")
                available.append({
                    "brand":    "Growatt",
                    "name":     p.get("plantNameEncryption") or p.get("plantName",""),
                    "id":       str(p.get("pId") or p.get("plantId","")),
                    "capacity": f"{float(cap_raw)/1000:.1f} kWp" if cap_raw else "—",
                    "location": p.get("country","") or "—",
                })
        except Exception as e:
            print(f"Plant loader Growatt error: {e}")
        return available

    st.markdown("""
    <div style="min-height:100vh;display:flex;align-items:center;justify-content:center;
    background:linear-gradient(135deg,#1c1917 0%,#292524 55%,#1a1816 100%);
    position:fixed;top:0;left:0;right:0;bottom:0;">
      <div style="text-align:center;color:#fff;">
        <div style="width:72px;height:72px;background:linear-gradient(135deg,#ea580c,#f59e0b);
          border-radius:20px;display:flex;align-items:center;justify-content:center;
          font-size:34px;margin:0 auto 20px;box-shadow:0 10px 32px rgba(234,88,12,.4);">☀️</div>
        <div style="font-size:20px;font-weight:700;color:#fafaf9;">Loading your plants…</div>
        <div style="font-size:13px;color:#78716c;margin-top:8px;">Connecting to Solis &amp; Growatt</div>
      </div>
    </div>""", unsafe_allow_html=True)

    with st.spinner(""):
        available_plants = _fetch_available_plants()

    sel_plant_names = [p["name"] for p in available_plants if p["name"]]
    active_brands   = []
    if any(p["brand"] == "Solis"   for p in available_plants): active_brands.append("Solis")
    if any(p["brand"] == "Growatt" for p in available_plants): active_brands.append("Growatt")

    # Store capacity & location for the Plants portfolio page
    st.session_state.plant_meta = {
        p["name"]: {"capacity": p["capacity"], "location": p["location"], "brand": p["brand"]}
        for p in available_plants if p["name"]
    }
    st.session_state.sel_brands     = active_brands or ["Solis"]
    st.session_state.sel_plants     = sel_plant_names
    st.session_state.plant_selected = True
    st.cache_data.clear()
    st.rerun()

# ══════════════════════════════════════════════════════════════
#  AUTHENTICATED APP
# ══════════════════════════════════════════════════════════════
st_autorefresh(interval=REFRESH_INTERVAL_SECONDS * 1000, key="solar_ar")

# ── Helpers ──────────────────────────────────────────────────
def f(v, d=1, na="—"):
    try:    return f"{float(v):.{d}f}"
    except: return na

def badge(s, kind=None):
    s  = (s or "").strip()
    sl = s.lower()
    if kind == "level":
        cls = "b-critical" if sl == "critical" else "b-warning"
    elif kind == "status_alarm":
        cls = "b-active" if sl == "active" else "b-resolved"
    else:
        if sl == "online":              cls = "b-online"
        elif sl in ("offline","fault"): cls = "b-offline"
        else:                           cls = "b-unknown"
    return f'<span class="badge {cls}">{s}</span>'

def chip(b):
    return f'<span class="chip chip-{(b or "").lower()}">{b}</span>'

def earn(kwh):
    v = float(kwh or 0) * RATE_PER_KWH
    if v >= 1_000_000: return f"₹{v/1_000_000:.3f}M"
    if v >= 1_000:     return f"₹{v/1_000:.3f}K"
    return f"₹{v:.2f}"

def chart_style(fig, h=300):
    fig.update_layout(
        plot_bgcolor="#fff", paper_bgcolor="#fff",
        font_color="#64748b", font_family="Inter",
        margin=dict(l=0,r=0,t=16,b=0), height=h,
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=12, color="#64748b")),
        bargap=0.28,
    )
    fig.update_traces(marker_line_width=0)
    fig.update_xaxes(showgrid=False, zeroline=False, tickfont_size=11,
                     tickfont_color="#94a3b8", linecolor="#e2e8f0")
    fig.update_yaxes(showgrid=True, gridcolor="#f1f5f9", zeroline=False,
                     tickfont_size=11, tickfont_color="#94a3b8")
    return fig

PALETTE = ["#ea580c","#f59e0b","#3b82f6","#f97316","#10b981","#8b5cf6","#06b6d4","#ec4899"]
BRAND_COLORS = {"Solis":"#3b82f6","Growatt":"#10b981","Sungrow":"#f97316"}

def sec(title, icon=""):
    st.markdown(f'<div class="sec-hdr"><div class="sec-hdr-dot"></div>{icon} {title}</div>',
                unsafe_allow_html=True)

# ── Sidebar — only shown in main dashboard ───────────────────
with st.sidebar:
    st.markdown(f"""
    <div class="sb-logo">
      <div class="sb-logo-icon">☀</div>
      <div>
        <div class="sb-logo-title">Solar Dashboard</div>
        <div class="sb-logo-sub">Fractal Energy</div>
      </div>
    </div>""", unsafe_allow_html=True)

    if not st.session_state.get("plant_selected", False):
        # Minimal sidebar while auto-loading plants
        st.markdown("<div style='color:#64748b;padding:20px;font-size:13px;'>Loading plants…</div>",
                    unsafe_allow_html=True)
        page = "Plants"
        sel_brands = st.session_state.get("sel_brands", ["Solis"])
        sel_plants = []
        show_debug = False
    else:
        # Consume pending navigation set by plant-card buttons BEFORE widgets are created
        _nav_opts = {
            "Plants":   "🏭  Plants",
            "Overview": "📊  Overview",
            "O&M":      "🔧  O&M",
            "Report":   "📈  Report",
            "Service":  "🗺  Service",
            "Settings": "⚙️  Settings",
        }
        if "_pending_page" in st.session_state:
            _ppage = st.session_state.pop("_pending_page")
            if _ppage in _nav_opts:
                st.session_state["nav_page"] = _nav_opts[_ppage]
        if "_pending_plant" in st.session_state:
            _pp = st.session_state.pop("_pending_plant")
            _pc = ["All Plants"] + st.session_state.get("sel_plants", [])
            if _pp in _pc:
                st.session_state["active_plant"] = _pp

        page = st.radio("", ["🏭  Plants","📊  Overview","🔧  O&M","📈  Report","🗺  Service","⚙️  Settings"],
                        label_visibility="collapsed", key="nav_page")
        page = page.split("  ",1)[1].strip()

        st.markdown('<div class="sb-section">Active Plant</div>', unsafe_allow_html=True)
        sel_brands     = st.session_state.get("sel_brands", ["Solis"])
        all_sel_plants = st.session_state.get("sel_plants", [])
        plant_choices  = ["All Plants"] + all_sel_plants
        active_plant   = st.selectbox("View plant", plant_choices,
                                      key="active_plant",
                                      label_visibility="collapsed")
        for b in sel_brands:
            st.markdown(
                f'<div style="color:#64748b;font-size:11px;padding:2px 4px;">'
                f'{"☀️" if b=="Solis" else "⚡" if b=="Growatt" else "🔆"} {b}</div>',
                unsafe_allow_html=True)
        if st.button("🔄  Refresh Now"):
            st.cache_data.clear(); st.rerun()

        show_debug = st.checkbox("🔍  Debug", value=False)

        st.markdown('<div style="height:12px"></div>', unsafe_allow_html=True)
        if st.button("🚪  Sign Out"):
            st.session_state.logged_in = False
            st.rerun()

        st.markdown(f"""
        <div class="sb-time">
          ⏱ {datetime.now().strftime('%d %b %Y')}<br>
          <b style="color:#a8a29e;">{datetime.now().strftime('%H:%M:%S')}</b><br>
          <span style="color:#78716c;">Auto-refresh {REFRESH_INTERVAL_SECONDS//60} min</span>
        </div>""", unsafe_allow_html=True)

# ── Fetch data (only when plant_selected) ────────────────────
if not st.session_state.get("plant_selected", False):
    st.stop()

all_sel_plants = st.session_state.get("sel_plants", [])
active_plant   = st.session_state.get("active_plant", "All Plants")

@st.cache_data(ttl=REFRESH_INTERVAL_SECONDS)
def load(brands, plants):
    result = fetch_all_brands(list(brands))
    if not result:
        raise RuntimeError("empty")
    if plants:
        result = [r for r in result if r.get("plant_name") in plants]
    return result

_fetch_errors = []

with st.spinner("Fetching live data…"):
    try:
        records = load(tuple(sel_brands), tuple(all_sel_plants))
    except Exception:
        st.cache_data.clear()
        records = []
        for _brand in sel_brands:
            try:
                from utils import solis_api as _sapi, growatt_api as _gapi
                if _brand == "Solis":
                    _recs = _sapi.fetch_all()
                elif _brand == "Growatt":
                    _recs = _gapi.fetch_all()
                else:
                    _recs = []
                records.extend(_recs)
            except Exception as _e:
                _fetch_errors.append(f"{_brand}: {_e}")
        if all_sel_plants:
            records = [r for r in records if r.get("plant_name") in all_sel_plants]

# ── Persist every refresh's live data to DB (runs on each 5-min auto-refresh) ──
# Save current power snapshot from `records` — no extra API calls needed.
# Over time this builds a complete day-by-day history in the DB.
import time as _time
_now_ts = _time.time()
_last_id_save = st.session_state.get("_last_intraday_save", 0)
if records and (_now_ts - _last_id_save >= 60):   # at most once per minute
    try:
        from datetime import datetime as _dtnow
        from utils.database import save_readings as _sv_r, save_intraday as _sv_id
        _snap_time = _dtnow.now()
        _snap_hm   = _snap_time.strftime("%H:%M")
        _snap_date = _snap_time.strftime("%Y-%m-%d")
        _snap_ts   = _snap_time.isoformat(sep=" ", timespec="seconds")

        # 1) save to inverter_data table (full record with today_kwh, status, etc.)
        _recs_to_save = [{**r, "fetched_at": _snap_ts} for r in records]
        _sv_r(_recs_to_save)

        # 2) save per-plant power to intraday_power (for Day chart)
        _plant_pwr = {}
        for _r in records:
            _pn = _r.get("plant_name", "")
            if _pn:
                _plant_pwr[_pn] = _plant_pwr.get(_pn, 0.0) + float(_r.get("power_kw") or 0)
        for _pn, _pwr in _plant_pwr.items():
            _sv_id(_pn, _snap_date, [{"time_hm": _snap_hm, "power_kw": _pwr}])

        st.session_state["_last_intraday_save"] = _now_ts
    except Exception:
        pass

# Filter to active plant chosen in sidebar
if active_plant and active_plant != "All Plants":
    records_view = [r for r in records if r.get("plant_name") == active_plant]
else:
    records_view = records

alerts = check_alerts(records, st.session_state)

df = pd.DataFrame()
if records_view:
    df = pd.DataFrame(records_view)
    for c in ["power_kw","today_kwh","total_kwh","temperature","voltage","current_a"]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    if "status" in df.columns:
        df["status"] = df["status"].astype(str).str.strip()

# ── Debug ─────────────────────────────────────────────────────
if show_debug and not df.empty:
    st.markdown("### 🔍 Debug: Raw API Data")
    st.dataframe(df, use_container_width=True)
    try:
        from utils.solis_api import fetch_summary as _fsum, _raw_plants_cache
        summ = _fsum()
        st.write("**fetch_summary():**", summ)
    except Exception as ex:
        st.error(f"Debug error: {ex}")
    st.divider()


# ── Unified plant filter vars for all pages ─────────────────
# sel_plants = plants chosen at login (all_sel_plants)
# active_plant = currently viewed plant (from sidebar dropdown)
sel_plants = all_sel_plants  # alias for backward compat

# ══════════════════════════════════════════════════════════════
#  PLANTS — Portfolio overview (default landing page)
# ══════════════════════════════════════════════════════════════
if page == "Plants":
    import io as _io

    plant_meta = st.session_state.get("plant_meta", {})

    # ── Page header ──────────────────────────────────────────
    st.markdown(f"""
<div style="display:flex;justify-content:space-between;align-items:center;
  border-bottom:1px solid #e2e8f0;padding-bottom:16px;margin-bottom:20px;">
  <div>
    <div style="font-size:22px;font-weight:800;color:#0f172a;letter-spacing:-.3px;">
      Plant Portfolio
    </div>
    <div style="font-size:13px;color:#64748b;margin-top:2px;">
      Select a plant and click <b>Open Dashboard</b> for detailed monitoring
    </div>
  </div>
  <div style="font-size:12px;color:#94a3b8;">{datetime.now().strftime('%d %b %Y  %H:%M')}</div>
</div>""", unsafe_allow_html=True)

    if not records:
        st.warning("No plant data — API returned no inverters. Check credentials and click **Refresh Now**.")
        if _fetch_errors:
            for _fe in _fetch_errors:
                st.error(f"🔴 {_fe}")
        # Show what credentials are actually loaded (helps diagnose secrets issues)
        from config import SOLIS_API_KEY, GROWATT_USERNAME
        st.info(
            f"Loaded credentials — "
            f"Solis key: `{'✅ set' if SOLIS_API_KEY else '❌ empty'}` · "
            f"Growatt user: `{'✅ set' if GROWATT_USERNAME else '❌ empty'}`"
        )
    else:
        # ── Build per-plant summary ───────────────────────────
        _pdf = pd.DataFrame(records)
        for _c in ["power_kw","today_kwh","total_kwh"]:
            if _c in _pdf.columns:
                _pdf[_c] = pd.to_numeric(_pdf[_c], errors="coerce").fillna(0)
        if "status" not in _pdf.columns:
            _pdf["status"] = "Unknown"
        if "inverter_sn" not in _pdf.columns:
            _pdf["inverter_sn"] = "—"

        _pg = (_pdf.groupby(["plant_name","brand"]).agg(
            power_kw    = ("power_kw",    "sum"),
            today_kwh   = ("today_kwh",   "sum"),
            total_kwh   = ("total_kwh",   "sum"),
            n_inverters = ("inverter_sn", "nunique"),
            n_online    = ("status",      lambda x: (x.str.lower() == "online").sum()),
            n_total     = ("status",      "count"),
        ).reset_index())

        _pg["Location"] = _pg["plant_name"].map(
            lambda n: plant_meta.get(n, {}).get("location", "—"))
        _pg["Capacity"] = _pg["plant_name"].map(
            lambda n: plant_meta.get(n, {}).get("capacity", "—"))
        _pg["Status"] = _pg.apply(
            lambda r: "Online"  if r["n_online"] == r["n_total"] and r["n_total"] > 0
                 else "Partial" if r["n_online"] > 0
                 else "Offline", axis=1)

        # ── Sort / Filter controls ────────────────────────────
        _fc1, _fc2, _fc3, _fc4 = st.columns([2, 2, 2, 2])
        with _fc1:
            _sort_by = st.selectbox("Sort", ["Default","Best Performing","Worst Performing"],
                                    label_visibility="collapsed")
        with _fc2:
            _brand_f = st.multiselect("Brand", sorted(_pg["brand"].unique().tolist()),
                                      placeholder="All Brands", label_visibility="collapsed")
        with _fc3:
            _status_f = st.multiselect("Status", ["Online","Partial","Offline"],
                                       placeholder="All Status", label_visibility="collapsed")
        with _fc4:
            _search = st.text_input("Search", placeholder="Search plant name…",
                                    label_visibility="collapsed")

        # Apply filters & sort
        _filt = _pg.copy()
        if _brand_f:  _filt = _filt[_filt["brand"].isin(_brand_f)]
        if _status_f: _filt = _filt[_filt["Status"].isin(_status_f)]
        if _search:   _filt = _filt[_filt["plant_name"].str.contains(_search, case=False, na=False)]
        if _sort_by == "Best Performing":  _filt = _filt.sort_values("power_kw", ascending=False)
        elif _sort_by == "Worst Performing": _filt = _filt.sort_values("power_kw", ascending=True)
        _filt = _filt.reset_index(drop=True)

        # ── Two-column layout: table | alerts ────────────────
        _tcol, _acol = st.columns([3.5, 1])

        with _tcol:
            _tbl_df = pd.DataFrame({
                "Select":       [False] * len(_filt),
                "Plant Name":   _filt["plant_name"].tolist(),
                "Brand":        _filt["brand"].tolist(),
                "Location":     _filt["Location"].tolist(),
                "Inverters":    _filt["n_inverters"].astype(int).tolist(),
                "Capacity":     _filt["Capacity"].tolist(),
                "Power (kW)":   _filt["power_kw"].round(2).tolist(),
                "Daily (kWh)":  _filt["today_kwh"].round(1).tolist(),
                "Total (MWh)":  _filt["total_kwh"].round(2).tolist(),
                "Status":       _filt["Status"].tolist(),
            })

            _edited = st.data_editor(
                _tbl_df,
                column_config={
                    "Select":      st.column_config.CheckboxColumn("", width="small"),
                    "Plant Name":  st.column_config.TextColumn("Plant Name", width="large"),
                    "Brand":       st.column_config.TextColumn("Brand",      width="small"),
                    "Location":    st.column_config.TextColumn("Location",   width="medium"),
                    "Inverters":   st.column_config.NumberColumn("Inv.", width="small"),
                    "Capacity":    st.column_config.TextColumn("Capacity",   width="small"),
                    "Power (kW)":  st.column_config.NumberColumn("Power (kW)",  format="%.2f", width="small"),
                    "Daily (kWh)": st.column_config.NumberColumn("Daily (kWh)", format="%.1f", width="small"),
                    "Total (MWh)": st.column_config.NumberColumn("Total (MWh)", format="%.2f", width="small"),
                    "Status":      st.column_config.TextColumn("Status", width="small"),
                },
                disabled=["Plant Name","Brand","Location","Inverters","Capacity",
                          "Power (kW)","Daily (kWh)","Total (MWh)","Status"],
                hide_index=True,
                use_container_width=True,
                height=min(420, 48 + len(_tbl_df) * 36),
                key="plants_table",
            )

            # ── Portfolio totals strip ────────────────────────
            _tp = float(_filt["power_kw"].sum())
            _td = float(_filt["today_kwh"].sum())
            _tt = float(_filt["total_kwh"].sum())
            st.markdown(f"""
<div style="background:linear-gradient(135deg,#1c1917 0%,#292524 100%);border-radius:12px;
  padding:16px 24px;display:flex;gap:28px;flex-wrap:wrap;margin:10px 0 8px;">
  <div><div style="font-size:9px;color:#78716c;text-transform:uppercase;letter-spacing:.6px;">Plants</div>
    <div style="font-size:22px;font-weight:800;color:#fafaf9;">{len(_filt)}</div></div>
  <div><div style="font-size:9px;color:#78716c;text-transform:uppercase;letter-spacing:.6px;">Live Power</div>
    <div style="font-size:22px;font-weight:800;color:#fb923c;">{_tp:.1f}
      <span style="font-size:12px;font-weight:400;color:#78716c;">kW</span></div></div>
  <div><div style="font-size:9px;color:#78716c;text-transform:uppercase;letter-spacing:.6px;">Today's Yield</div>
    <div style="font-size:22px;font-weight:800;color:#fcd34d;">{_td:.1f}
      <span style="font-size:12px;font-weight:400;color:#78716c;">kWh</span></div></div>
  <div><div style="font-size:9px;color:#78716c;text-transform:uppercase;letter-spacing:.6px;">Today's Earning</div>
    <div style="font-size:22px;font-weight:800;color:#f59e0b;">{earn(_td)}</div></div>
  <div><div style="font-size:9px;color:#78716c;text-transform:uppercase;letter-spacing:.6px;">Total Yield</div>
    <div style="font-size:22px;font-weight:800;color:#60a5fa;">{_tt:.1f}
      <span style="font-size:12px;font-weight:400;color:#78716c;">MWh</span></div></div>
</div>""", unsafe_allow_html=True)

            # ── Submit button ─────────────────────────────────
            _selected_plants = _edited[_edited["Select"]]["Plant Name"].tolist() if not _edited.empty else []
            _, _btn_c = st.columns([3, 1])
            with _btn_c:
                _btn_disabled = len(_selected_plants) == 0
                if st.button("Open Dashboard →", use_container_width=True,
                             type="primary", disabled=_btn_disabled,
                             key="open_dashboard_btn"):
                    st.session_state["_pending_plant"] = _selected_plants[0]
                    st.session_state["_pending_page"]  = "Overview"
                    st.rerun()
            if _selected_plants:
                st.caption(f"Selected: **{_selected_plants[0]}**")
            else:
                st.caption("Check a row above, then click Open Dashboard")

        # ── Right: Recent Alerts panel ────────────────────────
        with _acol:
            _alog = get_alert_log(10)
            st.markdown("""
<div style="background:#fff;border:1px solid #e2e8f0;border-radius:12px;
  padding:16px;min-height:320px;">
  <div style="display:flex;align-items:center;gap:8px;margin-bottom:14px;">
    <span style="width:9px;height:9px;background:#ef4444;border-radius:50%;
      display:inline-block;flex-shrink:0;"></span>
    <span style="font-size:13px;font-weight:700;color:#0f172a;">Recent Alerts</span>
  </div>""", unsafe_allow_html=True)

            if not alerts and (_alog.empty):
                st.markdown("""
<div style="text-align:center;padding:28px 8px;color:#94a3b8;">
  <div style="font-size:30px;margin-bottom:8px;">✅</div>
  <div style="font-size:12px;">No active alerts</div>
</div>""", unsafe_allow_html=True)
            else:
                for _al in alerts[:6]:
                    _ac = "#ef4444" if any(k in str(_al.get("issue","")).lower()
                                          for k in ("fault","offline","error")) else "#f59e0b"
                    st.markdown(f"""
<div style="border-left:3px solid {_ac};background:{_ac}10;border-radius:0 8px 8px 0;
  padding:8px 10px;margin-bottom:8px;">
  <div style="font-size:11px;font-weight:700;color:{_ac};">{_al.get('plant_name','—')}</div>
  <div style="font-size:10px;color:#64748b;">{_al.get('inverter_sn','—')}</div>
  <div style="font-size:11px;color:#0f172a;margin-top:2px;">{_al.get('issue','—')}</div>
</div>""", unsafe_allow_html=True)

                if not _alog.empty:
                    st.markdown("""<div style="font-size:10px;font-weight:600;color:#94a3b8;
                      margin:10px 0 6px;text-transform:uppercase;letter-spacing:.5px;">
                      History</div>""", unsafe_allow_html=True)
                    for _, _ar in _alog.head(5).iterrows():
                        st.markdown(f"""
<div style="border-left:2px solid #cbd5e1;padding:5px 10px;margin-bottom:6px;">
  <div style="font-size:10px;font-weight:600;color:#475569;">{_ar.get('plant_name','—')}</div>
  <div style="font-size:10px;color:#94a3b8;">{str(_ar.get('issue','—'))[:50]}</div>
</div>""", unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════
#  OVERVIEW
# ══════════════════════════════════════════════════════════════
elif page == "Overview":
    import io as _io

    _pmeta  = st.session_state.get("plant_meta", {}).get(
        active_plant if active_plant != "All Plants" else "", {})
    _cap_str  = _pmeta.get("capacity", "—")
    _loc_str  = _pmeta.get("location", "—")
    _brand_str = _pmeta.get("brand", sel_brands[0] if sel_brands else "—")

    # ── Resolve plant_id + store raw plant records ────────────────
    _pid_cache     = st.session_state.get("_plant_id_cache")
    _plant_records = st.session_state.get("_plant_records", {})
    _chart_pid     = None
    _chart_brand   = None
    if _pid_cache is None:
        _pid_cache = {}
        _plant_records = {}
        try:
            from utils.solis_api import get_plants as _gsp_k
            for _p in _gsp_k():
                _pn = _p.get("stationName", "")
                # Prefer 'id'; fall back to 'stationId' or 'sn' if id is empty/null
                _pid = (_p.get("id") or _p.get("stationId") or
                        _p.get("plantId") or _p.get("sn") or "")
                _pid_cache[_pn]     = (str(_pid), "Solis")
                _plant_records[_pn] = _p   # keep full record for unit-aware KPIs
        except Exception:
            pass
        try:
            from utils.growatt_api import _get_plants as _ggp_k
            for _p in _ggp_k():
                _pn = _p.get("plantNameEncryption") or _p.get("plantName", "")
                _pid_cache[_pn] = (
                    str(_p.get("pId") or _p.get("plantId", "")), "Growatt")
        except Exception:
            pass
        st.session_state["_plant_id_cache"] = _pid_cache
        st.session_state["_plant_records"]   = _plant_records
    if active_plant != "All Plants" and active_plant in _pid_cache:
        _chart_pid, _chart_brand = _pid_cache[active_plant]

    # Override: use plant_id directly from live df (most reliable — same data as KPIs)
    if active_plant != "All Plants" and not df.empty and "plant_id" in df.columns:
        _df_plant = df[df["plant_name"] == active_plant]
        if not _df_plant.empty:
            _pid_from_df = str(_df_plant.iloc[0].get("plant_id") or "")
            if _pid_from_df:
                _chart_pid   = _pid_from_df
                _chart_brand = str(_df_plant.iloc[0].get("brand") or _chart_brand or "Solis")

    # ── KPI calculations ──────────────────────────────────────
    total_power = float(df["power_kw"].sum()) if not df.empty else 0.0
    daily_kwh   = float(df["today_kwh"].sum()) if not df.empty else 0.0
    total_mwh   = float(df["total_kwh"].sum()) if not df.empty else 0.0
    n_on  = int((df["status"].str.lower()=="online").sum()) if not df.empty else 0
    n_tot = len(df) if not df.empty else 0

    _now_dt      = datetime.now()
    _cur_mon_str = _now_dt.strftime("%Y-%m")
    _cur_yr_str  = str(_now_dt.year)

    # ── Monthly yield ─────────────────────────────────────────────
    # Solis: monthEnergy+monthEnergyStr from userStationList is the real-time
    # running total (same number the Solis app KPI displays).
    # stationDayEnergyList only contains completed days so it misses today.
    monthly_kwh = 0.0
    if _chart_brand == "Solis" and active_plant != "All Plants":
        _prec = _plant_records.get(active_plant, {})
        if _prec:
            try:
                from utils.solis_api import _to_kwh as _s2kwh
                monthly_kwh = _s2kwh(
                    _prec.get("monthEnergy", 0),
                    _prec.get("monthEnergyStr", "kWh"))
            except Exception:
                pass

    if monthly_kwh == 0 and active_plant == "All Plants":
        # Portfolio total from fetch_summary (handles all-plant unit conversion)
        try:
            from utils.solis_api import fetch_summary as _fs
            _summ = _fs()
            if _summ.get("monthly_mwh", 0) > 0:
                monthly_kwh = float(_summ["monthly_mwh"]) * 1000
                if _summ.get("total_mwh", 0) > 0:
                    total_mwh = float(_summ["total_mwh"])
        except Exception:
            pass

    if monthly_kwh == 0 and _chart_brand == "Growatt" and _chart_pid:
        # Growatt: sum completed days from API
        try:
            from utils.growatt_api import get_plant_daily_history as _gpdh_k
            _api_mon = _gpdh_k(_chart_pid, _cur_mon_str)
            if _api_mon:
                monthly_kwh = sum(float(r.get("energy_kwh") or 0) for r in _api_mon)
        except Exception:
            pass

    if monthly_kwh == 0:
        # DB fallback (sparse but better than nothing)
        _hist_mon = get_history(hours=720)
        if not _hist_mon.empty and "today_kwh" in _hist_mon.columns:
            _hist_mon["fetched_at"] = pd.to_datetime(_hist_mon["fetched_at"])
            _hist_mon["today_kwh"]  = pd.to_numeric(_hist_mon["today_kwh"], errors="coerce")
            if active_plant != "All Plants":
                _hist_mon = _hist_mon[_hist_mon["plant_name"] == active_plant]
            elif all_sel_plants:
                _hist_mon = _hist_mon[_hist_mon["plant_name"].isin(all_sel_plants)]
            _m = _hist_mon[_hist_mon["fetched_at"].dt.month == _now_dt.month]
            if not _m.empty:
                monthly_kwh = float(
                    _m.groupby([_m["fetched_at"].dt.date, "inverter_sn"])
                    ["today_kwh"].max().sum())

    if monthly_kwh == 0:
        monthly_kwh = daily_kwh
    monthly_mwh = monthly_kwh / 1000

    # ── Annual yield ──────────────────────────────────────────────
    # Solis: try yearEnergy+yearEnergyStr from userStationList first,
    # then fall back to summing stationMonthEnergyList (per-month kWh).
    annual_kwh = 0.0
    if _chart_brand == "Solis" and active_plant != "All Plants":
        _prec = _plant_records.get(active_plant, {})
        if _prec and _prec.get("yearEnergy") is not None:
            try:
                from utils.solis_api import _to_kwh as _s2kwh
                annual_kwh = _s2kwh(
                    _prec.get("yearEnergy", 0),
                    _prec.get("yearEnergyStr", "kWh"))
            except Exception:
                pass
        if annual_kwh == 0 and _chart_pid:
            try:
                from utils.solis_api import get_plant_monthly_history as _spmhy_k
                _api_yr = _spmhy_k(_chart_pid, _cur_yr_str)
                if _api_yr:
                    annual_kwh = sum(float(r.get("energy_kwh") or 0) for r in _api_yr)
            except Exception:
                pass

    if annual_kwh == 0 and _chart_brand == "Growatt" and _chart_pid:
        try:
            from utils.growatt_api import get_plant_monthly_history as _gpmhy_k
            _api_yr = _gpmhy_k(_chart_pid, _cur_yr_str)
            if _api_yr:
                annual_kwh = sum(float(r.get("energy_kwh") or 0) for r in _api_yr)
        except Exception:
            pass

    if annual_kwh == 0:
        _hy_k = get_history(hours=8760)
        if not _hy_k.empty and "today_kwh" in _hy_k.columns:
            _hy_k["fetched_at"] = pd.to_datetime(_hy_k["fetched_at"])
            _hy_k["today_kwh"]  = pd.to_numeric(_hy_k["today_kwh"], errors="coerce")
            if active_plant != "All Plants":
                _hy_k = _hy_k[_hy_k["plant_name"] == active_plant]
            _hy_k = _hy_k[_hy_k["fetched_at"].dt.year == _now_dt.year]
            if not _hy_k.empty:
                annual_kwh = float(
                    _hy_k.groupby(
                        [_hy_k["fetched_at"].dt.date.rename("_d"), "inverter_sn"])
                    ["today_kwh"].max().sum())

    if annual_kwh == 0:
        annual_kwh = monthly_kwh * 12
    annual_mwh = annual_kwh / 1000

    # Environmental benefits (Indian grid: 0.82 kg CO₂/kWh, 0.34 kg coal/kWh)
    _tot_kwh_env = total_mwh * 1000
    _co2_t  = round(_tot_kwh_env * 0.82  / 1000, 2)
    _trees  = round(_co2_t * 1000 / 21.77, 1)
    _coal_t = round(_tot_kwh_env * 0.34  / 1000, 2)

    # ── Top bar ───────────────────────────────────────────────
    _th1, _th2, _th3 = st.columns([4, 1, 1])
    with _th1:
        _dot = ("🟢" if n_on == n_tot and n_tot > 0
                else "🔴" if n_on == 0 else "🟡")
        _plant_lbl = active_plant if active_plant != "All Plants" else f"All {', '.join(sel_brands)} Plants"
        st.markdown(f"""
<div style="padding:2px 0 14px;">
  <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
    <span style="font-size:20px;font-weight:800;color:#0f172a;">{_plant_lbl}</span>
    <span style="font-size:12px;color:#64748b;background:#f1f5f9;
      border-radius:6px;padding:2px 8px;">{_brand_str}</span>
    {_dot}
  </div>
  <div style="font-size:11px;color:#94a3b8;margin-top:3px;">
    Last Update: {datetime.now().strftime('%d/%m/%Y %H:%M:%S (UTC+05:30)')}
    {f" &nbsp;·&nbsp; PV Capacity: {_cap_str}" if _cap_str != "—" else ""}
    {f" &nbsp;·&nbsp; 📍 {_loc_str}" if _loc_str != "—" else ""}
  </div>
</div>""", unsafe_allow_html=True)
    with _th2:
        if st.button("← All Plants", use_container_width=True):
            st.session_state["_pending_page"] = "Plants"
            st.rerun()
    with _th3:
        _do_export = st.button("📥 Export Report", use_container_width=True,
                               type="primary", key="dash_export_btn")

    if df.empty:
        st.warning("⚠️ No data. Check credentials in config.py and click Refresh.")
        st.stop()

    # ── Alarm banner ─────────────────────────────────────────
    _crit_al = [a for a in alerts if any(k in str(a.get("issue","")).lower()
                                         for k in ("fault","offline","error","fail"))]
    _warn_al = [a for a in alerts if a not in _crit_al]
    if not alerts and n_on == n_tot and n_tot > 0:
        _ab_bg  = "linear-gradient(90deg,#059669,#10b981)"
        _ab_txt = f"✅  All Systems Normal — {n_on}/{n_tot} inverters online · No active alarms"
    elif _crit_al or n_on < n_tot:
        _issues = len(_crit_al) or (n_tot - n_on)
        _ab_bg  = "linear-gradient(90deg,#dc2626,#ef4444)"
        _ab_txt = (f"🚨  {_issues} Critical Alert(s) · {n_on}/{n_tot} online — "
                   + " | ".join(f"{a['plant_name']}: {a['issue']}" for a in (_crit_al or alerts)[:3]))
    else:
        _ab_bg  = "linear-gradient(90deg,#d97706,#f59e0b)"
        _ab_txt = (f"⚠️  {len(_warn_al)} Warning(s) · {n_on}/{n_tot} online — "
                   + " | ".join(f"{a['plant_name']}: {a['issue']}" for a in _warn_al[:3]))
    st.markdown(f"""
<div style="background:{_ab_bg};border-radius:10px;padding:11px 20px;
  margin-bottom:14px;font-size:13px;font-weight:600;color:#fff;
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">
  {_ab_txt}
</div>""", unsafe_allow_html=True)

    # ── 3-column layout: [gauge+KPIs | charts | right panel] ─
    _lc, _mc, _rc = st.columns([1.3, 2.5, 1.2])

    # ── LEFT: Gauge + 4 KPI rows ──────────────────────────────
    with _lc:
        try:
            _cap_kw = float(
                _cap_str.replace("kWp","").replace("kW","").replace("—","0").strip() or 0)
        except Exception:
            _cap_kw = 0.0
        _gmax = max(_cap_kw, total_power * 1.25, 10.0)

        _gfig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=total_power,
            number={"suffix": " kW",
                    "font":   {"size": 26, "color": "#f59e0b",
                               "family": "Plus Jakarta Sans"}},
            gauge={
                "axis": {"range": [0, _gmax], "tickcolor": "#cbd5e1",
                         "tickfont": {"size": 9}, "nticks": 5},
                "bar":  {"color": "#f59e0b", "thickness": 0.18},
                "bgcolor": "rgba(0,0,0,0)",
                "borderwidth": 0,
                "steps": [
                    {"range": [0,           _gmax*0.33], "color": "#f0fdf4"},
                    {"range": [_gmax*0.33,  _gmax*0.66], "color": "#fef9c3"},
                    {"range": [_gmax*0.66,  _gmax],      "color": "#fff7ed"},
                ],
                "threshold": {"line":  {"color": "#ea580c", "width": 3},
                              "thickness": 0.78, "value": total_power},
            }
        ))
        _gfig.update_layout(
            height=210, margin=dict(l=16, r=16, t=20, b=0),
            paper_bgcolor="rgba(0,0,0,0)",
            font_family="Inter",
        )
        if _cap_kw > 0:
            _gfig.add_annotation(
                text=f"PV Capacity: {_cap_str}",
                x=0.5, y=-0.05, showarrow=False,
                font=dict(size=10, color="#94a3b8", family="Plus Jakarta Sans"),
                xanchor="center")
        st.plotly_chart(_gfig, use_container_width=True,
                        config={"displayModeBar": False})

        # 4 KPI value rows
        for _kl, _kv, _ke, _kc, _kb in [
            ("Daily Yield",
             f"{daily_kwh/1000:.3f} MWh" if daily_kwh >= 1000 else f"{daily_kwh:.1f} kWh",
             earn(daily_kwh), "#f59e0b", "#fffbeb"),
            ("Monthly Yield", f"{monthly_mwh:.3f} MWh",
             earn(monthly_kwh), "#ea580c", "#fff7ed"),
            ("Annual Yield",  f"{annual_mwh:.3f} MWh",
             earn(annual_mwh * 1000), "#f59e0b", "#fffbeb"),
            ("Total Yield",
             f"{total_mwh/1000:.3f} GWh" if total_mwh >= 1000 else f"{total_mwh:.3f} MWh",
             earn(total_mwh * 1000), "#3b82f6", "#eff6ff"),
        ]:
            st.markdown(f"""
<div style="background:{_kb};border-left:3px solid {_kc};border-radius:0 10px 10px 0;
  padding:9px 13px;margin-bottom:7px;display:flex;
  justify-content:space-between;align-items:center;">
  <div>
    <div style="font-size:9px;color:#64748b;text-transform:uppercase;
      letter-spacing:.5px;margin-bottom:2px;">{_kl}</div>
    <div style="font-size:17px;font-weight:800;color:{_kc};line-height:1.1;">{_kv}</div>
  </div>
  <div style="text-align:right;">
    <div style="font-size:9px;color:#94a3b8;">≈ INR</div>
    <div style="font-size:12px;font-weight:700;color:#475569;">{_ke}</div>
  </div>
</div>""", unsafe_allow_html=True)

    # ── CENTRE: Operating Data charts ─────────────────────────
    with _mc:
        st.markdown("""
<div style="background:#fff;border:1px solid #e2e8f0;border-radius:12px;
  padding:16px 18px;margin-bottom:0;">
  <div style="font-size:13px;font-weight:700;color:#0f172a;margin-bottom:12px;">
    Operating Data
  </div>""", unsafe_allow_html=True)

        _tab_day, _tab_mon, _tab_yr, _tab_life = st.tabs(["Day", "Month", "Year", "Lifetime"])

        # _chart_pid / _chart_brand already resolved above the KPI block

        with _tab_day:
            # Date picker
            _today = datetime.now().date()
            _sel_date = st.date_input(
                "Select Date", value=_today, max_value=_today,
                key="chart_day_date"
            )
            _dp      = pd.DataFrame()
            _day_src = "db"
            _day_str_api = _sel_date.strftime("%Y-%m-%d")

            # ── Step 1: read from intraday_power DB table (primary) ──────
            from utils.database import get_intraday as _get_id
            _pname_q = active_plant if active_plant != "All Plants" else ""
            if _pname_q:
                _id_df = _get_id(_pname_q, _day_str_api)
            else:
                # All plants: union from DB
                try:
                    from utils.database import _conn as _dbc2
                    _c2 = _dbc2()
                    _id_df = pd.read_sql(
                        "SELECT time_hm, power_kw FROM intraday_power "
                        "WHERE date=? ORDER BY time_hm",
                        _c2, params=(_day_str_api,))
                    _c2.close()
                    if not _id_df.empty:
                        _id_df = _id_df.groupby("time_hm")["power_kw"].sum().reset_index()
                except Exception:
                    _id_df = pd.DataFrame()

            # ── Step 2: build chart DataFrame from DB records ───────────────
            if not _id_df.empty:
                from datetime import datetime as _dtt0
                _dp = pd.DataFrame({
                    "fetched_at": pd.to_datetime(
                        _id_df["time_hm"].apply(
                            lambda t: _dtt0.strptime(f"{_day_str_api} {t}", "%Y-%m-%d %H:%M")
                        )),
                    "power_kw": pd.to_numeric(_id_df["power_kw"], errors="coerce").fillna(0),
                })

            # ── Step 3: fallback to inverter_data snapshots (also our own DB) ──
            if _dp.empty:
                _hd = get_history(hours=168)   # 7 days back
                if not _hd.empty:
                    _hd["fetched_at"] = pd.to_datetime(_hd["fetched_at"])
                    _hd["power_kw"]   = pd.to_numeric(_hd["power_kw"], errors="coerce")
                    if active_plant != "All Plants":
                        _hd = _hd[_hd["plant_name"] == active_plant]
                    _hd = _hd[_hd["fetched_at"].dt.date == _sel_date]
                    if not _hd.empty:
                        _dp = _hd.groupby("fetched_at")["power_kw"].sum().reset_index()

            _flh = round(daily_kwh / _cap_kw, 2) if _cap_kw > 0 else 0.0
            _ds1, _ds2, _ds3 = st.columns(3)
            _ds1.metric("Daily Yield",
                        f"{daily_kwh/1000:.3f} MWh" if daily_kwh >= 1000 else f"{daily_kwh:.1f} kWh")
            _ds2.metric("Daily Earning", earn(daily_kwh))
            _ds3.metric("Full Load Hours", f"{_flh:.2f} h" if _cap_kw > 0 else "—")

            if not _dp.empty:
                # Auto-detect data time range for sensible default zoom
                _t_min = _dp["fetched_at"].min()
                _t_max = _dp["fetched_at"].max()
                # Filter to only include points with actual power > 0 for range calc
                _dp_nonzero = _dp[_dp["power_kw"] > 0]
                if not _dp_nonzero.empty:
                    _t_min = _dp_nonzero["fetched_at"].min() - pd.Timedelta(minutes=30)
                    _t_max = _dp_nonzero["fetched_at"].max() + pd.Timedelta(minutes=30)

                _fd = go.Figure()
                _fd.add_trace(go.Scatter(
                    x=_dp["fetched_at"], y=_dp["power_kw"],
                    fill="tozeroy", fillcolor="rgba(245,158,11,.15)",
                    line=dict(color="#f59e0b", width=2.5),
                    mode="lines", name="Power",
                    hovertemplate="%{x|%H:%M}<br><b>%{y:.2f} kW</b><extra></extra>",
                ))
                _fd.update_layout(
                    plot_bgcolor="#fff", paper_bgcolor="#fff",
                    font_family="Inter", font_color="#64748b",
                    margin=dict(l=0, r=0, t=8, b=50), height=310,
                    hovermode="x unified", showlegend=False,
                    xaxis=dict(
                        showgrid=False, tickformat="%H:%M",
                        title="Time", zeroline=False,
                        range=[_t_min, _t_max],
                        rangeslider=dict(visible=True, thickness=0.08),
                        rangeselector=dict(
                            buttons=[
                                dict(count=4,  label="4h",       step="hour",
                                     stepmode="backward"),
                                dict(count=8,  label="8h",       step="hour",
                                     stepmode="backward"),
                                dict(step="all", label="Full Day"),
                            ],
                            bgcolor="#f8fafc", activecolor="#f59e0b",
                            font=dict(size=10),
                        ),
                    ),
                    yaxis=dict(showgrid=True, gridcolor="#f8fafc",
                               title="Power (kW)", zeroline=False),
                )
                st.plotly_chart(_fd, use_container_width=True,
                                config={"displayModeBar": True, "scrollZoom": True})
                st.caption(f"Source: {'API' if _day_src == 'api' else 'Stored DB'} — {len(_dp)} data points")
            else:
                st.info(f"No data for {_sel_date.strftime('%d %b %Y')} yet. "
                        "Data is stored automatically every 5 min while the app is running.")

        with _tab_mon:
            # Month + Year pickers — shows day-by-day breakdown within the month
            _now = datetime.now()
            _mc1, _mc2 = st.columns(2)
            _sel_mon_idx = _mc1.selectbox(
                "Month",
                options=list(range(1, 13)),
                format_func=lambda m: datetime(2000, m, 1).strftime("%B"),
                index=_now.month - 1, key="chart_mon_month"
            )
            _sel_mon_yr = _mc2.selectbox(
                "Year",
                options=list(range(_now.year - 3, _now.year + 1)),
                index=3, key="chart_mon_year"
            )
            _sel_mon_str = f"{_sel_mon_yr}-{_sel_mon_idx:02d}"

            _mon_rows = []
            _mon_src  = "api"

            # Primary: API — per-day totals for the month
            if _chart_pid:
                try:
                    if _chart_brand == "Solis":
                        from utils.solis_api import get_plant_daily_history as _spdh
                        _mon_rows = _spdh(_chart_pid, _sel_mon_str)
                    else:
                        from utils.growatt_api import get_plant_daily_history as _gpdh
                        _mon_rows = _gpdh(_chart_pid, _sel_mon_str)
                except Exception:
                    pass

            # Fallback: DB grouped by day
            if not _mon_rows:
                _mon_src = "db"
                _hm = get_history(hours=24 * 31 * 3)
                if not _hm.empty and "today_kwh" in _hm.columns:
                    _hm["fetched_at"] = pd.to_datetime(_hm["fetched_at"])
                    _hm["today_kwh"]  = pd.to_numeric(_hm["today_kwh"], errors="coerce")
                    if active_plant != "All Plants":
                        _hm = _hm[_hm["plant_name"] == active_plant]
                    _hm = _hm[(_hm["fetched_at"].dt.year  == _sel_mon_yr) &
                               (_hm["fetched_at"].dt.month == _sel_mon_idx)]
                    if not _hm.empty:
                        _dmdb = (_hm.groupby([_hm["fetched_at"].dt.date, "inverter_sn"])
                                 ["today_kwh"].max().groupby(level=0).sum().reset_index())
                        _dmdb.columns = ["date", "energy_kwh"]
                        _dmdb["date"] = _dmdb["date"].astype(str)
                        _mon_rows = _dmdb.to_dict("records")

            _ms1, _ms2, _ms3 = st.columns(3)
            _ms1.metric("Monthly Yield", f"{monthly_mwh:.3f} MWh")
            _ms2.metric("Monthly Earning", earn(monthly_kwh))
            _mon_days = len(_mon_rows) if _mon_rows else 0
            _ms3.metric("Days with Data", str(_mon_days))

            if _mon_rows:
                _dm_df = pd.DataFrame(_mon_rows)
                _dx = "date" if "date" in _dm_df.columns else _dm_df.columns[0]
                _dm_df[_dx] = pd.to_datetime(_dm_df[_dx], errors="coerce")
                _dm_df = _dm_df.dropna(subset=[_dx]).sort_values(_dx)
                # X-axis: day numbers "01", "02" ... matching Solis app style
                _dm_df["_day"] = _dm_df[_dx].dt.day.apply(lambda d: f"{d:02d}")
                _fm = go.Figure()
                _fm.add_trace(go.Bar(
                    x=_dm_df["_day"], y=_dm_df["energy_kwh"],
                    marker_color="rgba(234,88,12,.55)", name="Yield",
                    marker_cornerradius=2,
                    hovertemplate="Day %{x}<br><b>%{y:.1f} kWh</b><extra></extra>",
                ))
                _fm.add_trace(go.Scatter(
                    x=_dm_df["_day"], y=_dm_df["energy_kwh"],
                    line=dict(color="#ea580c", width=2), mode="lines+markers",
                    marker=dict(size=4), name="Trend",
                ))
                _fm.update_layout(
                    plot_bgcolor="#fff", paper_bgcolor="#fff",
                    font_family="Inter", font_color="#64748b",
                    margin=dict(l=0, r=0, t=8, b=0), height=270,
                    bargap=0.2, hovermode="x unified", showlegend=False,
                    xaxis=dict(showgrid=False, zeroline=False, type="category",
                               title="Day of Month"),
                    yaxis=dict(showgrid=True, gridcolor="#f8fafc",
                               title="kWh", zeroline=False),
                )
                st.plotly_chart(_fm, use_container_width=True,
                                config={"displayModeBar": False})
                _mon_tot = float(_dm_df["energy_kwh"].sum())
                st.caption(
                    f"Source: {'API' if _mon_src == 'api' else 'Local DB'} — "
                    f"{_sel_mon_str} total: {_mon_tot:.1f} kWh")
            else:
                st.info(f"No data for {_sel_mon_str}. Check API credentials.")

        with _tab_yr:
            # Year picker — shows month-by-month breakdown within the year
            import calendar as _cal
            _now_yr = datetime.now().year
            _sel_yr = st.selectbox(
                "Year",
                options=list(range(_now_yr - 3, _now_yr + 1)),
                index=3, key="chart_yr_year"
            )
            _yr_str  = str(_sel_yr)
            _yr_rows = []
            _yr_src  = "api"

            # Primary: API — per-month totals for the year
            if _chart_pid:
                try:
                    if _chart_brand == "Solis":
                        from utils.solis_api import get_plant_monthly_history as _spmhy
                        _yr_rows = _spmhy(_chart_pid, _yr_str)
                    else:
                        from utils.growatt_api import get_plant_monthly_history as _gpmhy
                        _yr_rows = _gpmhy(_chart_pid, _yr_str)
                except Exception:
                    pass

            # Fallback: DB grouped by month
            if not _yr_rows:
                _yr_src = "db"
                _hy = get_history(hours=8760 * 2)
                if not _hy.empty and "today_kwh" in _hy.columns:
                    _hy["fetched_at"] = pd.to_datetime(_hy["fetched_at"])
                    _hy["today_kwh"]  = pd.to_numeric(_hy["today_kwh"], errors="coerce")
                    if active_plant != "All Plants":
                        _hy = _hy[_hy["plant_name"] == active_plant]
                    _hy = _hy[_hy["fetched_at"].dt.year == _sel_yr]
                    if not _hy.empty:
                        _ym = (_hy.groupby([_hy["fetched_at"].dt.year.rename("_yr"),
                                            _hy["fetched_at"].dt.month.rename("_mo"),
                                            "inverter_sn"])["today_kwh"]
                               .max().groupby(level=[0, 1]).sum().reset_index())
                        _ym.columns = ["_yr", "_mo", "energy_kwh"]
                        _ym["month"] = _ym.apply(
                            lambda r: f"{int(r['_yr'])}-{int(r['_mo']):02d}", axis=1)
                        _yr_rows = _ym[["month", "energy_kwh"]].to_dict("records")

            _ys1, _ys2, _ys3 = st.columns(3)
            _ys1.metric("Annual Yield", f"{annual_mwh:.3f} MWh")
            _ys2.metric("Annual Earning", earn(annual_mwh * 1000))
            _ys3.metric("Months with Data", str(len(_yr_rows)))

            if _yr_rows:
                _yr_df = pd.DataFrame(_yr_rows)
                _xc = "month" if "month" in _yr_df.columns else _yr_df.columns[0]
                _yr_df = _yr_df.dropna(subset=[_xc]).sort_values(_xc)
                _yr_df["energy_kwh"] = pd.to_numeric(_yr_df["energy_kwh"], errors="coerce").fillna(0)
                # X-axis: month abbreviations — "2026-01" → "Jan"
                def _mo_abbr(m):
                    try: return _cal.month_abbr[int(str(m).split("-")[1])]
                    except Exception: return str(m)
                _yr_df["_label"] = _yr_df[_xc].apply(_mo_abbr)
                _fy = go.Figure()
                _fy.add_trace(go.Bar(
                    x=_yr_df["_label"], y=_yr_df["energy_kwh"],
                    marker_color="rgba(234,88,12,.55)", name="Yield",
                    marker_cornerradius=2,
                    hovertemplate="%{x}<br><b>%{y:.1f} kWh</b><extra></extra>",
                ))
                _fy.add_trace(go.Scatter(
                    x=_yr_df["_label"], y=_yr_df["energy_kwh"],
                    line=dict(color="#ea580c", width=2), mode="lines+markers",
                    marker=dict(size=5), name="Trend",
                ))
                _fy.update_layout(
                    plot_bgcolor="#fff", paper_bgcolor="#fff",
                    font_family="Inter", font_color="#64748b",
                    margin=dict(l=0, r=0, t=8, b=0), height=270,
                    bargap=0.25, hovermode="x unified", showlegend=False,
                    xaxis=dict(showgrid=False, zeroline=False, type="category",
                               categoryorder="array",
                               categoryarray=[_cal.month_abbr[i] for i in range(1, 13)]),
                    yaxis=dict(showgrid=True, gridcolor="#f8fafc",
                               title="kWh", zeroline=False),
                )
                st.plotly_chart(_fy, use_container_width=True,
                                config={"displayModeBar": False})
                _yr_tot = float(_yr_df["energy_kwh"].sum())
                st.caption(
                    f"Source: {'API' if _yr_src == 'api' else 'Local DB'} — "
                    f"{_yr_str} total: {_yr_tot/1000:.3f} MWh")
            else:
                st.info(f"No data for {_yr_str}. Check API credentials.")

        with _tab_life:
            # Lifetime view — year-by-year totals (all available years)
            _now_yr2     = datetime.now().year
            _life_rows   = []
            _life_src    = "api"

            # Primary: API — sum monthly values for each year
            if _chart_pid:
                for _y in range(_now_yr2 - 4, _now_yr2 + 1):
                    try:
                        if _chart_brand == "Solis":
                            from utils.solis_api import get_plant_monthly_history as _spmhL
                            _mL = _spmhL(_chart_pid, str(_y))
                        else:
                            from utils.growatt_api import get_plant_monthly_history as _gpmhL
                            _mL = _gpmhL(_chart_pid, str(_y))
                        _ytot = sum(float(r.get("energy_kwh", 0)) for r in (_mL or []))
                        if _ytot > 0:
                            _life_rows.append({"year": str(_y), "energy_kwh": _ytot})
                    except Exception:
                        pass

            # Fallback: DB grouped by year
            if not _life_rows:
                _life_src = "db"
                _hyL = get_history(hours=8760 * 5)
                if not _hyL.empty and "today_kwh" in _hyL.columns:
                    _hyL["fetched_at"] = pd.to_datetime(_hyL["fetched_at"])
                    _hyL["today_kwh"]  = pd.to_numeric(_hyL["today_kwh"], errors="coerce")
                    if active_plant != "All Plants":
                        _hyL = _hyL[_hyL["plant_name"] == active_plant]
                    if not _hyL.empty:
                        _ydb = (_hyL.groupby([_hyL["fetched_at"].dt.year.rename("_yr"),
                                              _hyL["fetched_at"].dt.month.rename("_mo"),
                                              "inverter_sn"])["today_kwh"]
                                .max().groupby(level=[0, 1]).sum()
                                .groupby(level=0).sum().reset_index())
                        _ydb.columns = ["year", "energy_kwh"]
                        _ydb["year"] = _ydb["year"].astype(str)
                        _life_rows = _ydb.to_dict("records")

            _tl1, _tl2, _tl3 = st.columns(3)
            _grand_kwh = sum(r.get("energy_kwh", 0) for r in _life_rows)
            _tl1.metric("Total Yield",   f"{_grand_kwh/1000:.3f} MWh")
            _tl2.metric("Total Earning", earn(_grand_kwh))
            _tl3.metric("Years Active",  str(len(_life_rows)))

            if _life_rows:
                _lf_df = pd.DataFrame(_life_rows).sort_values("year")
                _lf_df["energy_kwh"] = pd.to_numeric(_lf_df["energy_kwh"], errors="coerce").fillna(0)
                _fl = go.Figure()
                _fl.add_trace(go.Bar(
                    x=_lf_df["year"], y=_lf_df["energy_kwh"],
                    marker_color="rgba(234,88,12,.55)", name="Yield",
                    marker_cornerradius=3,
                    hovertemplate="%{x}<br><b>%{y:.1f} kWh</b><extra></extra>",
                    text=_lf_df["energy_kwh"].apply(lambda v: f"{v/1000:.2f} MWh"),
                    textposition="outside",
                    textfont=dict(size=11, color="#78716c"),
                ))
                _fl.add_trace(go.Scatter(
                    x=_lf_df["year"], y=_lf_df["energy_kwh"],
                    line=dict(color="#f59e0b", width=2), mode="lines+markers",
                    marker=dict(size=6), name="Trend",
                ))
                _fl.update_layout(
                    plot_bgcolor="#fff", paper_bgcolor="#fff",
                    font_family="Inter", font_color="#64748b",
                    margin=dict(l=0, r=0, t=30, b=0), height=280,
                    bargap=0.35, hovermode="x unified", showlegend=False,
                    xaxis=dict(showgrid=False, zeroline=False, type="category",
                               tickfont=dict(size=13, color="#1c1917")),
                    yaxis=dict(showgrid=True, gridcolor="#f8fafc",
                               title="kWh", zeroline=False),
                )
                st.plotly_chart(_fl, use_container_width=True,
                                config={"displayModeBar": False})
                st.caption(
                    f"Source: {'API' if _life_src == 'api' else 'Local DB'} — "
                    f"lifetime: {_grand_kwh/1000:.3f} MWh across {len(_lf_df)} yr(s)")
            else:
                st.info("No lifetime data available. Verify API credentials.")

        st.markdown("</div>", unsafe_allow_html=True)

    # ── RIGHT: Plant info + Environmental benefits + Inverters ─
    with _rc:
        # Plant Information
        st.markdown(f"""
<div style="background:#fff;border:1px solid #e2e8f0;border-radius:12px;
  padding:16px;margin-bottom:10px;">
  <div style="font-size:13px;font-weight:700;color:#0f172a;margin-bottom:12px;">
    Plant Information
  </div>
  <table style="width:100%;font-size:12px;border-collapse:collapse;line-height:1.8;">
    <tr>
      <td style="color:#94a3b8;width:45%;">Status</td>
      <td style="font-weight:600;color:{'#10b981' if n_on > 0 else '#ef4444'};">
        {'● Online' if n_on > 0 else '● Offline'} ({n_on}/{n_tot})</td>
    </tr>
    <tr>
      <td style="color:#94a3b8;">Plant</td>
      <td style="font-weight:600;color:#0f172a;">{_plant_lbl}</td>
    </tr>
    <tr>
      <td style="color:#94a3b8;">Brand</td>
      <td style="font-weight:600;color:#0f172a;">{_brand_str}</td>
    </tr>
    <tr>
      <td style="color:#94a3b8;">PV Capacity</td>
      <td style="font-weight:600;color:#0f172a;">{_cap_str}</td>
    </tr>
    <tr>
      <td style="color:#94a3b8;">Inverters</td>
      <td style="font-weight:600;color:#0f172a;">{n_on} on / {n_tot} total</td>
    </tr>
    <tr>
      <td style="color:#94a3b8;">Location</td>
      <td style="font-weight:600;color:#0f172a;">{_loc_str}</td>
    </tr>
    <tr>
      <td style="color:#94a3b8;">Tariff</td>
      <td style="font-weight:600;color:#0f172a;">₹{RATE_PER_KWH}/kWh</td>
    </tr>
  </table>
</div>""", unsafe_allow_html=True)

        # Environmental Benefits
        st.markdown(f"""
<div style="background:#fff;border:1px solid #e2e8f0;border-radius:12px;
  padding:16px;margin-bottom:10px;">
  <div style="font-size:13px;font-weight:700;color:#0f172a;margin-bottom:12px;">
    Environmental Benefits
  </div>
  <div style="display:flex;flex-direction:column;gap:10px;">
    <div style="display:flex;align-items:center;gap:10px;">
      <div style="width:34px;height:34px;background:#f0fdf4;border-radius:8px;
        display:flex;align-items:center;justify-content:center;
        font-size:17px;flex-shrink:0;">🌳</div>
      <div>
        <div style="font-size:16px;font-weight:800;color:#10b981;">{_trees:,.1f}</div>
        <div style="font-size:10px;color:#64748b;">Equivalent Trees Planted</div>
      </div>
    </div>
    <div style="display:flex;align-items:center;gap:10px;">
      <div style="width:34px;height:34px;background:#eff6ff;border-radius:8px;
        display:flex;align-items:center;justify-content:center;
        font-size:17px;flex-shrink:0;">☁️</div>
      <div>
        <div style="font-size:16px;font-weight:800;color:#3b82f6;">{_co2_t:,.2f} t</div>
        <div style="font-size:10px;color:#64748b;">CO₂ Reduction</div>
      </div>
    </div>
    <div style="display:flex;align-items:center;gap:10px;">
      <div style="width:34px;height:34px;background:#fffbeb;border-radius:8px;
        display:flex;align-items:center;justify-content:center;
        font-size:17px;flex-shrink:0;">⚡</div>
      <div>
        <div style="font-size:16px;font-weight:800;color:#f59e0b;">{_coal_t:,.2f} t</div>
        <div style="font-size:10px;color:#64748b;">Standard Coal Saved</div>
      </div>
    </div>
  </div>
</div>""", unsafe_allow_html=True)

        # Inverter status list
        if not df.empty:
            st.markdown("""
<div style="background:#fff;border:1px solid #e2e8f0;border-radius:12px;padding:14px;">
  <div style="font-size:13px;font-weight:700;color:#0f172a;margin-bottom:10px;">
    Inverters
  </div>""", unsafe_allow_html=True)
            for _, _inv in df.head(10).iterrows():
                _ist  = str(_inv.get("status","")).lower()
                _ic   = ("#10b981" if _ist == "online"
                         else "#ef4444" if _ist == "offline" else "#f59e0b")
                _ipwr = float(_inv.get("power_kw", 0) or 0)
                _isn  = str(_inv.get("inverter_sn","—"))
                _ipn  = str(_inv.get("plant_name","—"))
                st.markdown(f"""
<div style="display:flex;justify-content:space-between;align-items:center;
  padding:6px 0;border-bottom:1px solid #f8fafc;">
  <div>
    <div style="font-size:11px;font-weight:600;color:#0f172a;">{_isn}</div>
    <div style="font-size:10px;color:#94a3b8;">{_ipn}</div>
  </div>
  <div style="text-align:right;">
    <div style="font-size:12px;font-weight:700;color:#ea580c;">{_ipwr:.1f} kW</div>
    <div style="font-size:10px;font-weight:600;color:{_ic};">
      {'● ' + str(_inv.get('status','—')).capitalize()}</div>
  </div>
</div>""", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

    # ── Excel Export ──────────────────────────────────────────
    if _do_export:
        _xbuf = _io.BytesIO()
        try:
            with pd.ExcelWriter(_xbuf, engine="openpyxl") as _xw:
                pd.DataFrame({
                    "Metric": ["Plant", "Date", "Daily Yield (kWh)", "Monthly Yield (MWh)",
                               "Annual Yield (MWh)", "Total Yield (MWh)",
                               "Live Power (kW)", "Total Savings (INR)",
                               "CO2 Reduction (t)", "Trees Equivalent", "Coal Saved (t)"],
                    "Value": [_plant_lbl, datetime.now().strftime("%Y-%m-%d"),
                              round(daily_kwh, 2), round(monthly_mwh, 3),
                              round(annual_mwh, 3), round(total_mwh, 3),
                              round(total_power, 2),
                              round(total_mwh * 1000 * RATE_PER_KWH, 2),
                              _co2_t, _trees, _coal_t],
                }).to_excel(_xw, sheet_name="KPI Summary", index=False)
                df.to_excel(_xw, sheet_name="Inverter Data", index=False)
                _hexp = get_history(hours=720)
                if not _hexp.empty:
                    if active_plant != "All Plants":
                        _hexp = _hexp[_hexp["plant_name"] == active_plant]
                    _hexp.to_excel(_xw, sheet_name="History (30d)", index=False)
            _xbuf.seek(0)
            st.download_button(
                "📥 Download Excel Report",
                data=_xbuf,
                file_name=f"{_plant_lbl.replace(' ','_')}_report_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="export_download_btn",
            )
        except Exception as _xe:
            st.error(f"Export failed: {_xe}. Install openpyxl: pip install openpyxl")


# ══════════════════════════════════════════════════════════════
#  O&M
# ══════════════════════════════════════════════════════════════
elif page == "O&M":
    sub = st.radio("", ["🔔  Alarm Information","⚡  Device Overview"],
                   horizontal=True, label_visibility="collapsed")
    sub = sub.split("  ",1)[1].strip()
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    alarm_log = get_alert_log(200)
    all_alarms = []
    for a in alerts:
        all_alarms.append({"device_type":"Inverter","level":"Critical","status":"Active",
            "plant_name":a.get("plant_name","—"),"sn":a.get("inverter_sn","—"),
            "content":a.get("issue","—"),"brand":a.get("brand","—"),
            "time":datetime.now().strftime("%Y-%m-%d %H:%M")})
    if not alarm_log.empty:
        for _, r in alarm_log.iterrows():
            all_alarms.append({"device_type":"Inverter","level":"Warning","status":"Resolved",
                "plant_name":r.get("plant_name","—"),"sn":r.get("inverter_sn","—"),
                "content":r.get("issue","—"),"brand":r.get("brand","—"),
                "time":r.get("alerted_at","—")})

    if sub == "Alarm Information":
        st.markdown('<div class="page-hdr"><h1>Alarm Information</h1>'
                    '<p>Fault detection and alert history</p></div>',
                    unsafe_allow_html=True)

        plant_opts = ["All"] + sorted(df["plant_name"].dropna().unique()) if not df.empty else ["All"]
        sn_opts    = ["All"] + sorted(df["inverter_sn"].dropna().unique()) if not df.empty else ["All"]
        brand_opts = ["All"] + sorted(df["brand"].dropna().unique())       if not df.empty else ["All"]

        fc1,fc2,fc3,fc4,fc5 = st.columns(5)
        with fc1: fp = st.selectbox("Plant Name",  plant_opts)
        with fc2: fs = st.selectbox("S/N",         sn_opts)
        with fc3: fb = st.selectbox("Brand",        brand_opts)
        with fc4: fst= st.selectbox("Status",       ["All","Active","Resolved"])
        with fc5: fl = st.selectbox("Level",        ["All","Critical","Warning"])

        filt = all_alarms[:]
        if fp !="All": filt=[a for a in filt if a["plant_name"]==fp]
        if fs !="All": filt=[a for a in filt if a["sn"]        ==fs]
        if fb !="All": filt=[a for a in filt if a["brand"]     ==fb]
        if fst!="All": filt=[a for a in filt if a["status"]    ==fst]
        if fl !="All": filt=[a for a in filt if a["level"]     ==fl]

        m1,m2,m3 = st.columns(3)
        m1.metric("Total", len(filt))
        m2.metric("Active",   sum(1 for a in filt if a["status"]=="Active"))
        m3.metric("Resolved", sum(1 for a in filt if a["status"]=="Resolved"))

        if not filt:
            st.success("✅ No alarms — all systems operating normally.")
        else:
            st.markdown('<div class="tbl">', unsafe_allow_html=True)
            st.markdown('<div class="tbl-hdr tbl-alarm">'
                        '<div>Device</div><div>Level</div><div>Status</div>'
                        '<div>Plant</div><div>S/N</div><div>Issue</div><div>Time</div>'
                        '</div>', unsafe_allow_html=True)
            for a in filt:
                st.markdown(
                    f'<div class="tbl-row tbl-alarm">'
                      f'<div>{a["device_type"]}</div>'
                      f'<div>{badge(a["level"],"level")}</div>'
                      f'<div>{badge(a["status"],"status_alarm")}</div>'
                      f'<div>{chip(a["brand"])} {a["plant_name"]}</div>'
                      f'<div style="font-size:11px;color:var(--text3);font-family:\'JetBrains Mono\',monospace;">{a["sn"]}</div>'
                      f'<div>{a["content"]}</div>'
                      f'<div style="font-size:11px;color:var(--text3);">{a["time"]}</div>'
                    f'</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

    else:
        st.markdown('<div class="page-hdr"><h1>Device Overview</h1>'
                    '<p>Live readings for every inverter</p></div>',
                    unsafe_allow_html=True)
        if df.empty:
            st.warning("⚠️ No data."); st.stop()

        fc1,fc2,fc3,fc4 = st.columns(4)
        with fc1: bf = st.selectbox("Brand",  ["All"]+sorted(df["brand"].dropna().unique()),       key="do_b")
        with fc2: pf = st.selectbox("Plant",  ["All"]+sorted(df["plant_name"].dropna().unique()),  key="do_p")
        with fc3: sf = st.selectbox("S/N",    ["All"]+sorted(df["inverter_sn"].dropna().unique()), key="do_s")
        with fc4: stf= st.selectbox("Status", ["All"]+sorted(df["status"].dropna().unique()),      key="do_st")

        vw = df.copy()
        if bf !="All": vw=vw[vw["brand"]       ==bf]
        if pf !="All": vw=vw[vw["plant_name"]  ==pf]
        if sf !="All": vw=vw[vw["inverter_sn"] ==sf]
        if stf!="All": vw=vw[vw["status"]      ==stf]

        st.markdown(
            f'<div class="stat-row">'
              f'<div class="stat-item"><div class="stat-val">{len(vw)}</div><div class="stat-lbl">Inverters</div></div>'
              f'<div class="stat-item"><div class="stat-val">{f(vw["power_kw"].sum(),2)} kW</div><div class="stat-lbl">Total Power</div></div>'
              f'<div class="stat-item"><div class="stat-val">{f(vw["today_kwh"].sum(),1)} kWh</div><div class="stat-lbl">Daily Yield</div></div>'
              f'<div class="stat-item"><div class="stat-val">{int((vw["status"].str.lower()=="online").sum())}</div><div class="stat-lbl">Online</div></div>'
            f'</div>', unsafe_allow_html=True)

        alert_sns = {a.get("inverter_sn") for a in alerts}
        for _, row in vw.iterrows():
            sn    = str(row.get("inverter_sn","N/A"))
            brand = str(row.get("brand",""))
            st_   = str(row.get("status",""))
            params = [
                ("Power Now",   f(row.get("power_kw"),2),  "kW"),
                ("Daily Yield", f(row.get("today_kwh"),1), "kWh"),
                ("Total Yield", f(row.get("total_kwh"),3), "MWh"),
                ("Temperature", f(row.get("temperature"),1),"°C"),
                ("AC Voltage",  f(row.get("voltage"),1),   "V"),
                ("AC Current",  f(row.get("current_a"),1), "A"),
            ]
            p_html = "".join(
                f'<div><div class="param-label">{l}</div>'
                f'<div class="param-val">{v}<span class="param-unit"> {u}</span></div></div>'
                for l,v,u in params)
            border = "border-left:3px solid var(--red);" if sn in alert_sns else ""
            st.markdown(
                f'<div class="inv-card" style="{border}">'
                  f'<div class="inv-header">'
                    f'<div><div class="inv-name">{row.get("plant_name","")}</div>'
                    f'<div class="inv-meta">S/N: {sn} · {chip(brand)} · {row.get("last_update","—")}</div></div>'
                    + badge(st_) +
                  f'</div>'
                  f'<div class="inv-params">{p_html}</div>'
                f'</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
#  REPORT  — pulls historical data from Solis API directly
# ══════════════════════════════════════════════════════════════
elif page == "Report":
    st.markdown('<div class="page-hdr"><h1>Plant Report</h1>'
                '<p>Historical generation data from Solis Cloud</p></div>',
                unsafe_allow_html=True)

    rtype = st.radio("", ["Daily","Monthly","Annual","Total"],
                     horizontal=True, label_visibility="collapsed")
    st.markdown('<div style="height:10px"></div>', unsafe_allow_html=True)

    # Plant comes from the sidebar active_plant selector
    sel_plant = active_plant   # 'All Plants' or a specific plant name

    fc1, fc2 = st.columns([2, 1])
    with fc1:
        st.markdown(
            f'<div style="background:#f0fdf4;border:1px solid #86efac;border-radius:8px;'
            f'padding:10px 14px;font-size:13px;font-weight:600;color:#166534;">'
            f'📍 {sel_plant}</div>',
            unsafe_allow_html=True)
    with fc2: sel_date = st.date_input("Date", value=date.today())

    # Shared line chart helper
    def line_chart(fig, h=360):
        fig = chart_style(fig, h)
        fig.update_traces(selector=dict(type="scatter"), line=dict(width=2.5))
        fig.update_layout(hovermode="x unified")
        return fig

    # Get plant IDs for selected plant
    from utils.solis_api import (get_plants as _get_solis_plants,
                                  get_all_plants_daily, get_all_plants_monthly,
                                  get_plant_daily_history   as solis_daily,
                                  get_plant_monthly_history as solis_monthly)
    from utils.growatt_api import (get_plant_daily_history   as growatt_daily,
                                   get_plant_monthly_history as growatt_monthly,
                                   _get_plants               as _get_growatt_plants)

    @st.cache_data(ttl=300)
    def _plants_cached():
        plants = []
        try:
            for p in _get_solis_plants():
                plants.append({"name": p.get("stationName"), "id": p.get("id"), "brand": "Solis"})
        except Exception: pass
        try:
            for p in _get_growatt_plants():
                pid   = str(p.get("pId") or p.get("plantId",""))
                pname = p.get("plantNameEncryption") or p.get("plantName","")
                plants.append({"name": pname, "id": pid, "brand": "Growatt"})
        except Exception: pass
        return plants

    all_plants    = _plants_cached()
    plant_id_map  = {p["name"]: (p["id"], p["brand"]) for p in all_plants}

    def get_daily_history(plant_name, month_str):
        info = plant_id_map.get(plant_name)
        if not info: return []
        pid, brand = info
        if brand == "Growatt": return growatt_daily(pid, month_str)
        return solis_daily(pid, month_str)

    def get_monthly_history(plant_name, year_str):
        info = plant_id_map.get(plant_name)
        if not info: return []
        pid, brand = info
        if brand == "Growatt": return growatt_monthly(pid, year_str)
        return solis_monthly(pid, year_str)

    # ── DAILY ────────────────────────────────────────────────
    if rtype == "Daily":
        # Determine brand of selected plant
        sel_brand_for_report = "Solis"
        if sel_plant != "All Plants":
            info = plant_id_map.get(sel_plant)
            if info: sel_brand_for_report = info[1]

        # For Growatt: use stationDay API (has per-day hourly data)
        # For Solis: use local DB (5-min readings collected by the app)
        if sel_brand_for_report == "Growatt" and sel_plant != "All Plants":
            month_str_d = sel_date.strftime("%Y-%m")
            with st.spinner("Fetching daily data from Growatt…"):
                rows = get_daily_history(sel_plant, month_str_d)

            if not rows:
                st.info(f"No data returned from Growatt for {sel_date.strftime('%B %Y')}.")
            else:
                # Filter to selected date
                day_rows = [r for r in rows if r.get("date","").startswith(str(sel_date))]
                if not day_rows:
                    # Show full month as fallback
                    day_rows = rows
                    st.info(f"Showing full month data — no hourly breakdown available for {sel_date}.")

                daily_df = pd.DataFrame(day_rows)
                daily_df["date"] = pd.to_datetime(daily_df["date"], errors="coerce")
                daily_df = daily_df.dropna(subset=["date"]).sort_values("date")

                sec(f"Daily Generation — {sel_plant} ({sel_date.strftime('%B %Y')})")
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=daily_df["date"], y=daily_df["energy_kwh"],
                    name="Yield (kWh)", marker_color="rgba(16,185,129,.25)",
                    marker_line_width=0,
                ))
                fig.add_trace(go.Scatter(
                    x=daily_df["date"], y=daily_df["energy_kwh"],
                    name="Yield", mode="lines+markers",
                    line=dict(color="#10b981", width=2.5),
                    marker=dict(size=6, color="#10b981"),
                ))
                fig.update_layout(
                    plot_bgcolor="#fff", paper_bgcolor="#fff",
                    font_family="Inter", font_color="#64748b",
                    margin=dict(l=0,r=0,t=16,b=0), height=360,
                    hovermode="x unified", bargap=0.25,
                    legend=dict(bgcolor="rgba(0,0,0,0)"),
                    yaxis=dict(title="kWh", showgrid=True, gridcolor="#f1f5f9", zeroline=False),
                )
                fig.update_xaxes(showgrid=False, zeroline=False, tickformat="%d %b")
                st.plotly_chart(fig, use_container_width=True)

                tot = daily_df["energy_kwh"].sum()
                c1,c2 = st.columns(2)
                c1.metric("Month Total", f"{tot:.1f} kWh")
                c2.metric("Estimated Earning", earn(tot))

        else:
            # Solis / All Plants — use local DB (5-min power readings)
            hist_df = get_history(hours=8760)
            if hist_df.empty:
                st.info("📭 No intraday data yet — the app collects readings every 5 min. "
                        "Come back after the app has been running for a while.")
            else:
                hist_df["fetched_at"] = pd.to_datetime(hist_df["fetched_at"])
                hist_df["power_kw"]   = pd.to_numeric(hist_df["power_kw"],  errors="coerce")
                hist_df["today_kwh"]  = pd.to_numeric(hist_df["today_kwh"], errors="coerce")
                if sel_plant != "All Plants":
                    hist_df = hist_df[hist_df["plant_name"] == sel_plant]

                day = hist_df[hist_df["fetched_at"].dt.date == sel_date].sort_values("fetched_at")
                if day.empty:
                    st.info(f"No intraday data for {sel_date}. "
                            f"Try today's date — data builds up every 5 minutes the app is running.")
                else:
                    sec("Power Output Throughout the Day (kW)")
                    fig = px.line(day, x="fetched_at", y="power_kw", color="inverter_sn",
                                  color_discrete_sequence=PALETTE,
                                  labels={"fetched_at":"Time","power_kw":"Power (kW)",
                                          "inverter_sn":"Inverter"})
                    st.plotly_chart(line_chart(fig, 360), use_container_width=True)

                    sec("Peak Power & Daily Generation per Inverter")
                    sm = (day.groupby(["plant_name","inverter_sn","brand"])
                          .agg(Peak_kW=("power_kw","max"), Daily_kWh=("today_kwh","max"))
                          .reset_index()
                          .rename(columns={"plant_name":"Plant","inverter_sn":"S/N","brand":"Brand"}))
                    st.dataframe(sm, use_container_width=True, hide_index=True)

    # ── MONTHLY ───────────────────────────────────────────────
    elif rtype == "Monthly":
        month_str = sel_date.strftime("%Y-%m")

        with st.spinner(f"Fetching daily data for {sel_date.strftime('%B %Y')}…"):
            if sel_plant == "All Plants":
                api_df = get_all_plants_daily(month_str)
                if not api_df.empty:
                    daily = (api_df.groupby("date")["energy_kwh"]
                             .sum().reset_index())
                    daily.columns = ["Date","Daily Yield (kWh)"]
                    income_df = api_df.groupby("date")["income"].sum().reset_index()
                    income_df.columns = ["Date","Income (INR)"]
                    daily = daily.merge(income_df, on="Date", how="left")
                else:
                    daily = pd.DataFrame()
            else:
                rows = get_daily_history(sel_plant, month_str)
                if rows:
                    daily = pd.DataFrame(rows).rename(columns={
                        "date":"Date","energy_kwh":"Daily Yield (kWh)","income":"Income (INR)"})
                    daily["Date"] = pd.to_datetime(daily["Date"], errors="coerce")
                else:
                    daily = pd.DataFrame()

        if daily.empty or "Daily Yield (kWh)" not in daily.columns:
            st.info(f"No data from Solis API for {sel_date.strftime('%B %Y')}.")
        else:
            daily = daily.dropna(subset=["Date"]).sort_values("Date")

            # Combined bar + line chart matching Solis style
            sec(f"Daily Generation — {sel_date.strftime('%B %Y')}")
            fig = go.Figure()
            # Bar: yield
            fig.add_trace(go.Bar(
                x=daily["Date"], y=daily["Daily Yield (kWh)"],
                name="Yield (kWh)", marker_color="rgba(234,88,12,.25)",
                marker_line_width=0,
            ))
            # Line: yield trend
            fig.add_trace(go.Scatter(
                x=daily["Date"], y=daily["Daily Yield (kWh)"],
                name="Yield", mode="lines+markers",
                line=dict(color="#ea580c", width=2.5),
                marker=dict(size=5, color="#ea580c"),
            ))
            # Line: revenue (right axis)
            if "Income (INR)" in daily.columns:
                fig.add_trace(go.Scatter(
                    x=daily["Date"], y=daily["Income (INR)"],
                    name="Revenue (INR)", mode="lines+markers",
                    line=dict(color="#f59e0b", width=2, dash="dot"),
                    marker=dict(size=5, color="#f59e0b"),
                    yaxis="y2",
                ))
            fig.update_layout(
                plot_bgcolor="#fff", paper_bgcolor="#fff",
                font_family="Inter", font_color="#64748b",
                margin=dict(l=0,r=60,t=16,b=0), height=380,
                hovermode="x unified", bargap=0.25,
                legend=dict(bgcolor="rgba(0,0,0,0)", orientation="h",
                            yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
                yaxis=dict(title="kWh", showgrid=True, gridcolor="#f1f5f9",
                           zeroline=False, tickfont_size=11),
                yaxis2=dict(title="INR", overlaying="y", side="right",
                            showgrid=False, zeroline=False, tickfont_size=11),
            )
            fig.update_xaxes(showgrid=False, zeroline=False, tickfont_size=11,
                             tickformat="%d", dtick="D1")
            st.plotly_chart(fig, use_container_width=True)

            tot = daily["Daily Yield (kWh)"].sum()
            m1,m2,m3 = st.columns(3)
            m1.metric("Month Total", f"{tot:.1f} kWh")
            m2.metric("Month Total (MWh)", f"{tot/1000:.3f} MWh")
            m3.metric("Estimated Earning", earn(tot))

    # ── ANNUAL ────────────────────────────────────────────────
    elif rtype == "Annual":
        year_str = str(sel_date.year)

        with st.spinner(f"Fetching monthly data for {year_str}…"):
            if sel_plant == "All Plants":
                api_df = get_all_plants_monthly(year_str)
                if not api_df.empty:
                    monthly = (api_df.groupby("month")["energy_kwh"]
                               .sum().reset_index())
                    monthly.columns = ["Month","kWh"]
                else:
                    monthly = pd.DataFrame()
            else:
                rows = get_monthly_history(sel_plant, year_str)
                if rows:
                    monthly = pd.DataFrame(rows).rename(columns={"month":"Month","energy_kwh":"kWh"})
                else:
                    monthly = pd.DataFrame()

        if monthly.empty or "kWh" not in monthly.columns:
            st.info(f"No data from Solis API for {year_str}.")
        else:
            monthly = monthly[monthly["kWh"] > 0]

            sec(f"Monthly Generation — {year_str}")
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=monthly["Month"], y=monthly["kWh"],
                name="Yield (kWh)", marker_color="rgba(245,158,11,.3)",
                marker_line_width=0,
            ))
            fig.add_trace(go.Scatter(
                x=monthly["Month"], y=monthly["kWh"],
                name="Trend", mode="lines+markers",
                line=dict(color="#f59e0b", width=2.5),
                marker=dict(size=7, color="#f59e0b"),
            ))
            fig.update_layout(
                plot_bgcolor="#fff", paper_bgcolor="#fff",
                font_family="Inter", font_color="#64748b",
                margin=dict(l=0,r=0,t=16,b=0), height=360,
                hovermode="x unified", bargap=0.3,
                legend=dict(bgcolor="rgba(0,0,0,0)"),
                yaxis=dict(showgrid=True, gridcolor="#f1f5f9",
                           zeroline=False, tickfont_size=11),
            )
            fig.update_xaxes(showgrid=False, zeroline=False, tickfont_size=11)
            st.plotly_chart(fig, use_container_width=True)

            tot_yr = monthly["kWh"].sum()
            m1,m2,m3 = st.columns(3)
            m1.metric("Year Total", f"{tot_yr:.1f} kWh")
            m2.metric("Year Total (MWh)", f"{tot_yr/1000:.3f} MWh")
            m3.metric("Est. Annual Earning", earn(tot_yr))

    # ── TOTAL ─────────────────────────────────────────────────
    else:
        sec("Total Yield per Plant (All-time)")
        if not df.empty:
            gt = (df.groupby(["plant_name","brand"])
                  .agg(total_mwh=("total_kwh","sum"), daily_kwh=("today_kwh","sum"))
                  .reset_index())

            fig = go.Figure()
            for i, row in gt.iterrows():
                fig.add_trace(go.Bar(
                    x=[row["plant_name"]], y=[row["total_mwh"]],
                    name=row["plant_name"],
                    marker_color=PALETTE[i % len(PALETTE)],
                    marker_line_width=0,
                ))
            fig.update_layout(
                plot_bgcolor="#fff", paper_bgcolor="#fff",
                font_family="Inter", font_color="#64748b",
                margin=dict(l=0,r=0,t=16,b=0), height=340,
                showlegend=False, bargap=0.35,
                yaxis=dict(title="MWh", showgrid=True, gridcolor="#f1f5f9",
                           zeroline=False, tickfont_size=11),
            )
            fig.update_xaxes(showgrid=False, zeroline=False, tickfont_size=11)
            st.plotly_chart(fig, use_container_width=True)

            gt_disp = gt.rename(columns={"plant_name":"Plant","brand":"Brand",
                                          "total_mwh":"Total Yield (MWh)",
                                          "daily_kwh":"Today (kWh)"})
            st.dataframe(gt_disp, use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════
#  SERVICE
# ══════════════════════════════════════════════════════════════
elif page == "Service":
    st.markdown('<div class="page-hdr"><h1>Plant Management</h1>'
                '<p>All registered plants and operational details</p></div>',
                unsafe_allow_html=True)
    if df.empty:
        st.warning("⚠️ No data."); st.stop()

    fc1,fc2 = st.columns(2)
    with fc1: pf2 = st.selectbox("Plant", ["All"]+sorted(df["plant_name"].dropna().unique()), key="pm_p")
    with fc2: bf2 = st.selectbox("Brand", ["All"]+sorted(df["brand"].dropna().unique()),      key="pm_b")

    ps = (df.groupby(["plant_name","brand"])
          .agg(power_kw=("power_kw","sum"), today_kwh=("today_kwh","sum"),
               total_kwh=("total_kwh","sum"), inv_count=("inverter_sn","count"))
          .reset_index())
    if pf2!="All": ps=ps[ps["plant_name"]==pf2]
    if bf2!="All": ps=ps[ps["brand"]==bf2]

    st.markdown(
        f'<div class="stat-row">'
          f'<div class="stat-item"><div class="stat-val">{len(ps)}</div><div class="stat-lbl">Plants</div></div>'
          f'<div class="stat-item"><div class="stat-val">{f(ps["power_kw"].sum(),2)} kW</div><div class="stat-lbl">Total Power</div></div>'
          f'<div class="stat-item"><div class="stat-val">{f(ps["today_kwh"].sum(),1)} kWh</div><div class="stat-lbl">Daily Yield</div></div>'
          f'<div class="stat-item"><div class="stat-val">{f(ps["total_kwh"].sum(),1)} MWh</div><div class="stat-lbl">Total Yield</div></div>'
        f'</div>', unsafe_allow_html=True)

    st.markdown('<div class="tbl">', unsafe_allow_html=True)
    st.markdown('<div class="tbl-hdr tbl-plant">'
                '<div>Plant Name</div><div>Brand</div><div>Organisation</div>'
                '<div>Inverters</div><div>Power (kW)</div>'
                '<div>Daily Yield</div><div>Total Yield</div><div>Status</div>'
                '</div>', unsafe_allow_html=True)
    for _, row in ps.iterrows():
        pr   = df[df["plant_name"]==row["plant_name"]]
        on   = int((pr["status"].str.lower()=="online").sum())
        tot  = int(row["inv_count"])
        pst  = "Online" if on==tot and tot>0 else ("Offline" if on==0 else "Warning")
        dy   = float(row["today_kwh"] or 0)
        dy_s = f"{dy/1000:.3f} MWh" if dy>=1000 else f"{dy:.1f} kWh"
        ty   = float(row["total_kwh"] or 0)
        ty_s = f"{ty/1000:.3f} GWh" if ty>=1000 else f"{ty:.3f} MWh"
        st.markdown(
            f'<div class="tbl-row tbl-plant">'
              f'<div class="cell-link">{row["plant_name"]}</div>'
              f'<div>{chip(row["brand"])}</div>'
              f'<div>Fractal Energy</div>'
              f'<div>{on}/{tot}</div>'
              f'<div><b>{f(row["power_kw"],2)}</b> kW</div>'
              f'<div>{dy_s}</div><div>{ty_s}</div>'
              f'<div>{badge(pst)}</div>'
            f'</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════
#  SETTINGS
# ══════════════════════════════════════════════════════════════
elif page == "Settings":
    st.markdown('<div class="page-hdr"><h1>Settings</h1>'
                '<p>Credentials, alerts and app configuration</p></div>',
                unsafe_allow_html=True)

    from config import (SOLIS_API_KEY, GROWATT_USERNAME, SUNGROW_APP_KEY,
                        EMAIL_USER, TO_EMAILS, RATE_PER_KWH)

    st.markdown("#### 🔑 API Credentials")
    for brand,ok,hint in [
        ("Solis",   bool(SOLIS_API_KEY),
         SOLIS_API_KEY[:10]+"…" if SOLIS_API_KEY else "Not configured"),
        ("Growatt", bool(GROWATT_USERNAME),
         GROWATT_USERNAME or "Set GROWATT_USERNAME in config.py"),
        ("Sungrow", bool(SUNGROW_APP_KEY),
         SUNGROW_APP_KEY[:10]+"…" if SUNGROW_APP_KEY else "Set SUNGROW_APP_KEY in config.py"),
    ]:
        c1,c2,c3 = st.columns([1,1,4])
        c1.markdown(f"**{brand}**")
        c2.markdown("✅ OK" if ok else "⚠️ Not set")
        c3.markdown(f"`{hint}`")

    st.divider()
    st.markdown("#### 📧 Email Alerts")
    st.markdown(f"**Sender:** `{EMAIL_USER}`")
    st.markdown(f"**Recipients:** `{', '.join(TO_EMAILS)}`")
    st.divider()
    st.markdown("#### 💰 Tariff Rate")
    st.info(f"Current rate: **₹{RATE_PER_KWH}/kWh** — edit `RATE_PER_KWH` in config.py")
    st.divider()
    st.markdown("#### 👤 Logged in as")
    st.info(f"`{st.session_state.user}`")
    st.divider()
    st.markdown("#### 🗂 Project Structure")
    st.code("""
solar_dashboard/
├── app.py              ← streamlit run app.py
├── config.py           ← ✏️  credentials & settings
├── requirements.txt
├── data/solar_data.db  ← auto-created
└── utils/
    ├── solis_api.py    ├── growatt_api.py
    ├── sungrow_api.py  ├── aggregator.py
    ├── database.py     └── alerts.py
    """, language="")