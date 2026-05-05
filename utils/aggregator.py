# # ============================================================
# #  utils/data_aggregator.py
# #  Pulls data from all three brands, saves to DB, checks alerts
# # ============================================================

# import streamlit as st
# from utils import solis_api, growatt_api, sungrow_api
# from utils.database import save_readings, log_alert
# from utils.alerts import send_email_alert
# from config import ALERT_POWER_THRESHOLD


# BRAND_FETCHERS = {
#     "Solis":   solis_api.fetch_all,
#     "Growatt": growatt_api.fetch_all,
#     "Sungrow": sungrow_api.fetch_all,
# }


# def fetch_all_brands(brands=None):
#     all_records = []
#     active = brands or list(BRAND_FETCHERS.keys())

#     for brand in active:
#         fetcher = BRAND_FETCHERS.get(brand)
#         if fetcher is None:
#             continue
#         try:
#             records = fetcher()
#             all_records.extend(records)
#         except Exception as e:
#             st.warning(f"⚠️ Could not fetch {brand} data: {e}")

#     if all_records:
#         save_readings(all_records)

#     return all_records


# def check_and_send_alerts(records, session_state):
#     if "alert_sent" not in session_state:
#         session_state.alert_sent = {}

#     fired = []

#     for r in records:
#         key   = f"{r['brand']}::{r['plant_name']}::{r['inverter_sn']}"
#         issue = None
#         power = r.get("power_kw")

#         if power is None:
#             issue = "No data received from inverter"
#         elif power == 0:
#             issue = "Inverter reporting zero power output"
#         elif r.get("status", "").lower() in ("offline", "fault"):
#             issue = f"Inverter status: {r['status']}"

#         if issue:
#             fired.append({**r, "issue": issue})
#             if not session_state.alert_sent.get(key):
#                 ok = send_email_alert(
#                     r["brand"], r["plant_name"],
#                     r.get("inverter_sn", "N/A"), issue
#                 )
#                 if ok:
#                     log_alert(r["brand"], r["plant_name"],
#                               r.get("inverter_sn"), issue)
#                 session_state.alert_sent[key] = True
#         else:
#             session_state.alert_sent[key] = False

#     return fired

# utils/aggregator.py
import streamlit as st
from utils import solis_api, growatt_api, sungrow_api
from utils.database import save_readings, log_alert
from utils.alerts import send_email_alert
from utils.database import save_intraday, save_daily_yield
from datetime import datetime

FETCHERS = {"Solis": solis_api.fetch_all,
            "Growatt": growatt_api.fetch_all,
            "Sungrow": sungrow_api.fetch_all}

def fetch_all_brands(brands=None):
    all_records = []
    for b in (brands or list(FETCHERS.keys())):
        try:
            recs = FETCHERS[b]()
            all_records.extend(recs)
        except Exception as e:
            st.warning(f"⚠️ {b} fetch failed: {e}")
    if all_records:
        save_readings(all_records)
        # ✅ NEW: store intraday + daily
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_hm  = now.strftime("%H:%M")

        plant_map = {}

        for r in all_records:
            plant = r.get("plant_name")
            power = float(r.get("power_kw") or 0)
            energy = float(r.get("today_kwh") or 0)

            # ---- intraday ----
            save_intraday(
                plant,
                date_str,
                [{"time_hm": time_hm, "power_kw": power}]
            )

            # ---- daily yield aggregation ----
            if plant not in plant_map:
                plant_map[plant] = 0
            plant_map[plant] += energy

        # ---- save daily yield ----
        for plant, total_kwh in plant_map.items():
            save_daily_yield(plant, date_str, total_kwh)
            
    return all_records



def check_alerts(records, ss):
    if "alert_sent" not in ss: ss.alert_sent = {}
    fired = []
    for r in records:
        key   = f"{r['brand']}::{r['plant_name']}::{r['inverter_sn']}"
        power = r.get("power_kw")
        issue = None
        if power is None:          issue = "No data received from inverter"
        elif float(power or 0)==0: issue = "Inverter reporting zero power output"
        elif (r.get("status","")).lower() in ("offline","fault"):
            issue = f"Inverter status: {r['status']}"
        if issue:
            fired.append({**r, "issue": issue})
            if not ss.alert_sent.get(key):
                if send_email_alert(r["brand"],r["plant_name"],r.get("inverter_sn",""),issue):
                    log_alert(r["brand"],r["plant_name"],r.get("inverter_sn"),issue)
                ss.alert_sent[key] = True
        else:
            ss.alert_sent[key] = False
    return fired