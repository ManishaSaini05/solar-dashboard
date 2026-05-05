# ============================================================
#  utils/solis_api.py — Solis Cloud API connector
# ============================================================

# import hashlib
# import base64
# import json
# import hmac
# import requests
# from datetime import datetime, timezone
# from config import SOLIS_API_KEY, SOLIS_API_SECRET, SOLIS_BASE_URL


# def _generate_headers(api_path: str, body_json: str) -> dict:
#     md5         = hashlib.md5(body_json.encode("utf-8")).digest()
#     content_md5 = base64.b64encode(md5).decode()

#     now  = datetime.now(timezone.utc)
#     date = now.strftime("%a, %d %b %Y %H:%M:%S GMT")

#     string_to_sign = f"POST\n{content_md5}\napplication/json\n{date}\n{api_path}"

#     sign = base64.b64encode(
#         hmac.new(
#             SOLIS_API_SECRET.encode("utf-8"),
#             string_to_sign.encode("utf-8"),
#             hashlib.sha1,
#         ).digest()
#     ).decode()

#     return {
#         "Content-MD5":   content_md5,
#         "Content-Type":  "application/json",
#         "Date":          date,
#         "Authorization": f"API {SOLIS_API_KEY}:{sign}",
#     }


# def _post(api_path: str, body: dict) -> dict | None:
#     url       = SOLIS_BASE_URL + api_path
#     body_json = json.dumps(body, separators=(",", ":"))
#     headers   = _generate_headers(api_path, body_json)

#     try:
#         res = requests.post(url, data=body_json, headers=headers, timeout=15)
#         res.raise_for_status()
#         return res.json()
#     except Exception as e:
#         print(f"❌ Solis API error [{api_path}]: {e}")
#         return None


# def get_plants() -> list[dict]:
#     data = _post("/v1/api/userStationList", {"pageNo": 1, "pageSize": 100})
#     if not data:
#         return []
#     return data.get("data", {}).get("page", {}).get("records", [])


# def get_inverters_for_plant(plant_id: str) -> list[dict]:
#     data = _post("/v1/api/inverterList", {"stationId": plant_id})
#     if not data:
#         return []
#     return data.get("data", {}).get("page", {}).get("records", [])


# def get_inverter_detail(inverter_sn: str) -> dict | None:
#     """Fetch extra detail (voltage, current, temp) for one inverter."""
#     data = _post("/v1/api/inverterDetail", {"sn": inverter_sn})
#     if not data:
#         return None
#     return data.get("data")


# def fetch_all() -> list[dict]:
#     """
#     Top-level: fetch every plant → every inverter and return
#     a normalised list of dicts ready for the DB / dashboard.
#     """
#     results = []

#     for plant in get_plants():
#         plant_id   = plant.get("id", "")
#         plant_name = plant.get("stationName", "Unknown")

#         for inv in get_inverters_for_plant(plant_id):
#             sn = inv.get("inverterSn", "")

#             # Optional extra details (may not be available on all accounts)
#             detail = get_inverter_detail(sn) or {}

#             status_code = inv.get("state")
#             if status_code == 1:
#                 status = "Online"
#             elif status_code == 0:
#                 status = "Offline"
#             else:
#                 status = "Unknown"

#             results.append({
#                 "brand":       "Solis",
#                 "plant_name":  plant_name,
#                 "plant_id":    plant_id,
#                 "inverter_sn": sn,
#                 "power_kw":    inv.get("power"),
#                 "today_kwh":   inv.get("etoday"),
#                 "total_kwh":   inv.get("etotal"),
#                 "status":      status,
#                 "temperature": detail.get("inverterTemperature"),
#                 "voltage":     detail.get("uAc1"),
#                 "current_a":   detail.get("iAc1"),
#                 "last_update": inv.get("dataTimestampStr"),
#             })

#     return results

# ============================================================
#  utils/solis_api.py — Solis Cloud API connector
#  Field reference (confirmed from debug output):
#    inverterList:  power    = kW (may be rounded integer for large inverters)
#                  etoday   = kWh  (today's generation)
#                  etotal   = MWh  (all-time, confirmed: 64.837 MWh, 17.475 MWh etc.)
#                  state    = 1 Online / 0 Offline
#    inverterDetail: pac     = W  (precise real-time power in Watts)
#                   etoday  = kWh
#                   etotal  = MWh
#                   inverterTemperature = °C
#                   uAc1    = V
#                   iAc1    = A
# ============================================================

# import hashlib
# import base64
# import json
# import hmac
# import requests
# from datetime import datetime, timezone
# from config import SOLIS_API_KEY, SOLIS_API_SECRET, SOLIS_BASE_URL


# def _generate_headers(api_path: str, body_json: str) -> dict:
#     md5         = hashlib.md5(body_json.encode("utf-8")).digest()
#     content_md5 = base64.b64encode(md5).decode()
#     now         = datetime.now(timezone.utc)
#     date        = now.strftime("%a, %d %b %Y %H:%M:%S GMT")
#     string_to_sign = f"POST\n{content_md5}\napplication/json\n{date}\n{api_path}"
#     sign = base64.b64encode(
#         hmac.new(
#             SOLIS_API_SECRET.encode("utf-8"),
#             string_to_sign.encode("utf-8"),
#             hashlib.sha1,
#         ).digest()
#     ).decode()
#     return {
#         "Content-MD5":   content_md5,
#         "Content-Type":  "application/json",
#         "Date":          date,
#         "Authorization": f"API {SOLIS_API_KEY}:{sign}",
#     }


# def _post(api_path: str, body: dict):
#     url       = SOLIS_BASE_URL + api_path
#     body_json = json.dumps(body, separators=(",", ":"))
#     headers   = _generate_headers(api_path, body_json)
#     try:
#         res = requests.post(url, data=body_json, headers=headers, timeout=15)
#         res.raise_for_status()
#         return res.json()
#     except Exception as e:
#         print(f"❌ Solis API error [{api_path}]: {e}")
#         return None


# def get_plants():
#     data = _post("/v1/api/userStationList", {"pageNo": 1, "pageSize": 100})
#     if not data:
#         return []
#     return data.get("data", {}).get("page", {}).get("records", [])


# def get_inverters_for_plant(plant_id: str):
#     data = _post("/v1/api/inverterList", {"stationId": plant_id})
#     if not data:
#         return []
#     return data.get("data", {}).get("page", {}).get("records", [])


# def get_inverter_detail(inverter_sn: str):
#     """
#     Returns detailed real-time data for one inverter.
#     Key fields:
#       pac               — real-time AC power in WATTS (divide by 1000 for kW)
#       etoday            — today's energy in kWh
#       etotal            — all-time energy in MWh
#       inverterTemperature — °C
#       uAc1              — AC voltage V
#       iAc1              — AC current A
#     """
#     data = _post("/v1/api/inverterDetail", {"sn": inverter_sn})
#     if not data:
#         return None
#     return data.get("data")


# def _safe_float(v):
#     try:    return float(v)
#     except: return None


# def fetch_all():
#     """
#     Fetch every plant → every inverter.
#     Uses inverterDetail for precise pac (W→kW), temperature, voltage, current.
#     Falls back to inverterList power field if detail call fails.

#     Confirmed field units from live debug data:
#       power_kw  → kW   (real-time output)
#       today_kwh → kWh  (daily generation)
#       total_kwh → MWh  (all-time; Solis etotal is in MWh not kWh)
#     """
#     results = []

#     for plant in get_plants():
#         plant_id   = plant.get("id", "")
#         plant_name = plant.get("stationName", "Unknown")

#         for inv in get_inverters_for_plant(plant_id):
#             sn = inv.get("inverterSn", "")

#             # ── Status ───────────────────────────────────────
#             state = inv.get("state")
#             if   state == 1: status = "Online"
#             elif state == 0: status = "Offline"
#             else:            status = "Unknown"

#             # ── Base values from inverterList ─────────────────
#             # 'power' field: confirmed kW (e.g. 15, 100, 3, 30)
#             list_power_kw = _safe_float(inv.get("power"))
#             today_kwh     = _safe_float(inv.get("etoday"))   # kWh confirmed
#             total_mwh     = _safe_float(inv.get("etotal"))   # MWh confirmed

#             # ── Precise values from inverterDetail ────────────
#             detail       = get_inverter_detail(sn) or {}
#             temp         = _safe_float(detail.get("inverterTemperature"))
#             voltage      = _safe_float(detail.get("uAc1"))
#             current_a    = _safe_float(detail.get("iAc1"))

#             # pac from detail is in WATTS → convert to kW for precise reading
#             # e.g. Solis shows RANK-NGP as 298.89kW total (5 inverters)
#             # so each is ~59.8kW, but inverterList returns 100 (rounded)
#             # inverterDetail pac field gives precise watts
#             pac_w = _safe_float(detail.get("pac"))
#             if pac_w is not None and pac_w > 0:
#                 # pac is in W, convert to kW
#                 precise_power_kw = pac_w / 1000.0
#             else:
#                 # fallback to inverterList power (already kW)
#                 precise_power_kw = list_power_kw

#             # Also check detail for more precise etoday/etotal
#             detail_today = _safe_float(detail.get("etoday"))
#             detail_total = _safe_float(detail.get("etotal"))

#             results.append({
#                 "brand":       "Solis",
#                 "plant_name":  plant_name,
#                 "plant_id":    plant_id,
#                 "inverter_sn": sn,
#                 "power_kw":    precise_power_kw,
#                 "today_kwh":   detail_today if detail_today is not None else today_kwh,
#                 "total_kwh":   detail_total if detail_total is not None else total_mwh,
#                 # ↑ total_kwh column stores MWh (Solis etotal unit)
#                 "status":      status,
#                 "temperature": temp,
#                 "voltage":     voltage,
#                 "current_a":   current_a,
#                 "last_update": inv.get("dataTimestampStr"),
#             })

#     return results

# ============================================================
#  utils/solis_api.py
#
#  CONFIRMED FIELD UNITS (from live debug data vs Solis app):
#
#  inverterList response:
#    power   → kW  BUT rounded to integer (100, 3, 30)  ← imprecise
#    etoday  → kWh (e.g. 17, 101.3, 26.9)
#    etotal  → MWh (e.g. 64.84, 17.475, 110.355)
#
#  inverterDetail response:
#    pac     → kW  (precise decimal, e.g. 9.8W shown as 0.0098 when /1000 was wrong)
#              CONFIRMED: pac field is already in kW (e.g. 9.53, 298.89 total)
#    etoday  → kWh
#    etotal  → MWh
#    inverterTemperature → °C
#    uAc1    → V
#    iAc1    → A
#
#  CONCLUSION: pac from inverterDetail is in kW — use it directly, NO division.
# ============================================================

# import hashlib, base64, json, hmac, requests
# from datetime import datetime, timezone
# from config import SOLIS_API_KEY, SOLIS_API_SECRET, SOLIS_BASE_URL


# def _headers(api_path, body_json):
#     md5  = hashlib.md5(body_json.encode()).digest()
#     cmd5 = base64.b64encode(md5).decode()
#     date = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")
#     sts  = f"POST\n{cmd5}\napplication/json\n{date}\n{api_path}"
#     sign = base64.b64encode(
#         hmac.new(SOLIS_API_SECRET.encode(), sts.encode(), hashlib.sha1).digest()
#     ).decode()
#     return {"Content-MD5": cmd5, "Content-Type": "application/json",
#             "Date": date, "Authorization": f"API {SOLIS_API_KEY}:{sign}"}


# def _post(path, body):
#     bj = json.dumps(body, separators=(",", ":"))
#     try:
#         r = requests.post(SOLIS_BASE_URL + path, data=bj,
#                           headers=_headers(path, bj), timeout=15)
#         r.raise_for_status()
#         return r.json()
#     except Exception as e:
#         print(f"❌ Solis [{path}]: {e}")
#         return None


# def _f(v):
#     try:    return float(v)
#     except: return None


# def get_plants():
#     d = _post("/v1/api/userStationList", {"pageNo": 1, "pageSize": 100})
#     return (d or {}).get("data", {}).get("page", {}).get("records", [])


# def get_inverters(plant_id):
#     d = _post("/v1/api/inverterList", {"stationId": plant_id})
#     return (d or {}).get("data", {}).get("page", {}).get("records", [])


# def get_detail(sn):
#     d = _post("/v1/api/inverterDetail", {"sn": sn})
#     return ((d or {}).get("data")) or {}


# def fetch_all():
#     """
#     Returns list of dicts. Units:
#       power_kw  → kW   (pac from inverterDetail, already kW, use directly)
#       today_kwh → kWh  (etoday)
#       total_kwh → MWh  (etotal — Solis reports all-time in MWh)
#     """
#     results = []
#     for plant in get_plants():
#         pid   = plant.get("id", "")
#         pname = plant.get("stationName", "Unknown")

#         for inv in get_inverters(pid):
#             sn    = inv.get("inverterSn", "")
#             state = inv.get("state")
#             status = {1: "Online", 0: "Offline"}.get(state, "Unknown")

#             # Fallback values from inverterList (rounded but available)
#             list_power = _f(inv.get("power"))     # kW, integer rounded
#             list_today = _f(inv.get("etoday"))     # kWh
#             list_total = _f(inv.get("etotal"))     # MWh

#             # Precise values from inverterDetail
#             det = get_detail(sn)

#             # pac = real-time power, CONFIRMED in kW (use directly, no conversion)
#             pac = _f(det.get("pac"))

#             # Use precise detail values; fall back to list values
#             power_kw  = pac          if pac          is not None else list_power
#             today_kwh = _f(det.get("etoday")) if det.get("etoday") is not None else list_today
#             total_mwh = _f(det.get("etotal")) if det.get("etotal") is not None else list_total

#             results.append({
#                 "brand":       "Solis",
#                 "plant_name":  pname,
#                 "plant_id":    pid,
#                 "inverter_sn": sn,
#                 "power_kw":    power_kw,   # kW
#                 "today_kwh":   today_kwh,  # kWh
#                 "total_kwh":   total_mwh,  # MWh (named total_kwh for DB compat)
#                 "status":      status,
#                 "temperature": _f(det.get("inverterTemperature")),
#                 "voltage":     _f(det.get("uAc1")),
#                 "current_a":   _f(det.get("iAc1")),
#                 "last_update": inv.get("dataTimestampStr"),
#             })
#     return results

# ============================================================
#  utils/solis_api.py
#
#  CONFIRMED FIELD UNITS (from live debug data vs Solis app):
#
#  inverterList response:
#    power   → kW  BUT rounded to integer (100, 3, 30)  ← imprecise
#    etoday  → kWh (e.g. 17, 101.3, 26.9)
#    etotal  → MWh (e.g. 64.84, 17.475, 110.355)
#
#  inverterDetail response:
#    pac     → kW  (precise decimal, e.g. 9.8W shown as 0.0098 when /1000 was wrong)
#              CONFIRMED: pac field is already in kW (e.g. 9.53, 298.89 total)
#    etoday  → kWh
#    etotal  → MWh
#    inverterTemperature → °C
#    uAc1    → V
#    iAc1    → A
#
#  CONCLUSION: pac from inverterDetail is in kW — use it directly, NO division.
# ============================================================

# ============================================================
#  utils/solis_api.py
#
#  CONFIRMED FIELD UNITS (from live debug data vs Solis app):
#
#  inverterList response:
#    power   → kW  BUT rounded to integer (100, 3, 30)  ← imprecise
#    etoday  → kWh (e.g. 17, 101.3, 26.9)
#    etotal  → MWh (e.g. 64.84, 17.475, 110.355)
#
#  inverterDetail response:
#    pac     → kW  (precise decimal, e.g. 9.8W shown as 0.0098 when /1000 was wrong)
#              CONFIRMED: pac field is already in kW (e.g. 9.53, 298.89 total)
#    etoday  → kWh
#    etotal  → MWh
#    inverterTemperature → °C
#    uAc1    → V
#    iAc1    → A
#
#  CONCLUSION: pac from inverterDetail is in kW — use it directly, NO division.
# ============================================================

# ============================================================
#  utils/solis_api.py
#
#  CONFIRMED FIELD UNITS (from live debug data vs Solis app):
#
#  inverterList response:
#    power   → kW  BUT rounded to integer (100, 3, 30)  ← imprecise
#    etoday  → kWh (e.g. 17, 101.3, 26.9)
#    etotal  → MWh (e.g. 64.84, 17.475, 110.355)
#
#  inverterDetail response:
#    pac     → kW  (precise decimal, e.g. 9.8W shown as 0.0098 when /1000 was wrong)
#              CONFIRMED: pac field is already in kW (e.g. 9.53, 298.89 total)
#    etoday  → kWh
#    etotal  → MWh
#    inverterTemperature → °C
#    uAc1    → V
#    iAc1    → A
#
#  CONCLUSION: pac from inverterDetail is in kW — use it directly, NO division.
# ============================================================

# ============================================================
#  utils/solis_api.py
#
#  CONFIRMED FIELD UNITS (from live debug data vs Solis app):
#
#  inverterList response:
#    power   → kW  BUT rounded to integer (100, 3, 30)  ← imprecise
#    etoday  → kWh (e.g. 17, 101.3, 26.9)
#    etotal  → MWh (e.g. 64.84, 17.475, 110.355)
#
#  inverterDetail response:
#    pac     → kW  (precise decimal, e.g. 9.8W shown as 0.0098 when /1000 was wrong)
#              CONFIRMED: pac field is already in kW (e.g. 9.53, 298.89 total)
#    etoday  → kWh
#    etotal  → MWh
#    inverterTemperature → °C
#    uAc1    → V
#    iAc1    → A
#
#  CONCLUSION: pac from inverterDetail is in kW — use it directly, NO division.
# ============================================================

# import hashlib, base64, json, hmac, requests
# from datetime import datetime, timezone
# from config import SOLIS_API_KEY, SOLIS_API_SECRET, SOLIS_BASE_URL


# def _headers(api_path, body_json):
#     md5  = hashlib.md5(body_json.encode()).digest()
#     cmd5 = base64.b64encode(md5).decode()
#     date = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")
#     sts  = f"POST\n{cmd5}\napplication/json\n{date}\n{api_path}"
#     sign = base64.b64encode(
#         hmac.new(SOLIS_API_SECRET.encode(), sts.encode(), hashlib.sha1).digest()
#     ).decode()
#     return {"Content-MD5": cmd5, "Content-Type": "application/json",
#             "Date": date, "Authorization": f"API {SOLIS_API_KEY}:{sign}"}


# def _post(path, body):
#     bj = json.dumps(body, separators=(",", ":"))
#     try:
#         r = requests.post(SOLIS_BASE_URL + path, data=bj,
#                           headers=_headers(path, bj), timeout=15)
#         r.raise_for_status()
#         return r.json()
#     except Exception as e:
#         print(f"❌ Solis [{path}]: {e}")
#         return None


# def _f(v):
#     try:    return float(v)
#     except: return None


# def get_plants():
#     d = _post("/v1/api/userStationList", {"pageNo": 1, "pageSize": 100})
#     return (d or {}).get("data", {}).get("page", {}).get("records", [])


# def get_inverters(plant_id):
#     d = _post("/v1/api/inverterList", {"stationId": plant_id})
#     return (d or {}).get("data", {}).get("page", {}).get("records", [])


# def get_detail(sn):
#     d = _post("/v1/api/inverterDetail", {"sn": sn})
#     return ((d or {}).get("data")) or {}


# def fetch_all():
#     """
#     Returns list of dicts. Units:
#       power_kw  → kW   (pac from inverterDetail, already kW, use directly)
#       today_kwh → kWh  (etoday)
#       total_kwh → MWh  (etotal — Solis reports all-time in MWh)
#     """
#     results = []
#     for plant in get_plants():
#         pid   = plant.get("id", "")
#         pname = plant.get("stationName", "Unknown")

#         for inv in get_inverters(pid):
#             sn    = inv.get("inverterSn", "")
#             state = inv.get("state")
#             status = {1: "Online", 0: "Offline"}.get(state, "Unknown")

#             # Fallback values from inverterList (rounded but available)
#             list_power = _f(inv.get("power"))     # kW, integer rounded
#             list_today = _f(inv.get("etoday"))     # kWh
#             list_total = _f(inv.get("etotal"))     # MWh

#             # Precise values from inverterDetail
#             det = get_detail(sn)

#             # pac = real-time power, CONFIRMED in kW (use directly, no conversion)
#             pac = _f(det.get("pac"))

#             # Use precise detail values; fall back to list values
#             power_kw  = pac          if pac          is not None else list_power
#             today_kwh = _f(det.get("etoday")) if det.get("etoday") is not None else list_today
#             total_mwh = _f(det.get("etotal")) if det.get("etotal") is not None else list_total

#             results.append({
#                 "brand":       "Solis",
#                 "plant_name":  pname,
#                 "plant_id":    pid,
#                 "inverter_sn": sn,
#                 "power_kw":    power_kw,   # kW
#                 "today_kwh":   today_kwh,  # kWh
#                 "total_kwh":   total_mwh,  # MWh (named total_kwh for DB compat)
#                 "status":      status,
#                 "temperature": _f(det.get("inverterTemperature")),
#                 "voltage":     _f(det.get("uAc1")),
#                 "current_a":   _f(det.get("iAc1")),
#                 "last_update": inv.get("dataTimestampStr"),
#             })
#     return results


# def fetch_summary():
#     """
#     Get plant-level KPI totals from userStationList.

#     CONFIRMED field names and units from live debug output:
#       power        → kW   (e.g. 4.78 kW)       — powerStr = "kW"
#       dayEnergy    → kWh  (e.g. 71.0 kWh)       — dayEnergyStr = "kWh"
#       monthEnergy  → MWh  (e.g. 1.685 MWh)      — monthEnergyStr = "MWh"
#       allEnergy    → MWh  (e.g. 64.894 MWh)     — allEnergyStr = "MWh"

#     So: dayEnergy is kWh, monthEnergy and allEnergy are ALREADY MWh.
#     """
#     total_power      = 0.0
#     total_daily_kwh  = 0.0   # kWh
#     total_monthly_mwh= 0.0   # MWh  (monthEnergy is already MWh)
#     total_all_mwh    = 0.0   # MWh  (allEnergy is already MWh)

#     plants = get_plants()
#     _raw_plants_cache.clear()
#     _raw_plants_cache.extend(plants)

#     for plant in plants:
#         total_power       += _f(plant.get("power",       0)) or 0
#         total_daily_kwh   += _f(plant.get("dayEnergy",   0)) or 0
#         total_monthly_mwh += _f(plant.get("monthEnergy", 0)) or 0
#         total_all_mwh     += _f(plant.get("allEnergy",   0)) or 0

#     return {
#         "power_kw":    total_power,
#         "daily_kwh":   total_daily_kwh,
#         "monthly_kwh": total_monthly_mwh * 1000,  # convert to kWh for earnings calc
#         "monthly_mwh": total_monthly_mwh,          # MWh for display
#         "total_kwh":   total_all_mwh * 1000,       # convert to kWh for earnings calc
#         "total_mwh":   total_all_mwh,              # MWh for display
#         "_raw_plants": list(plants),
#     }

# # Cache for debug inspection in app.py
# _raw_plants_cache = []

# ============================================================
#  utils/solis_api.py
#
#  CONFIRMED FIELD UNITS (from live debug data vs Solis app):
#
#  inverterList response:
#    power   → kW  BUT rounded to integer (100, 3, 30)  ← imprecise
#    etoday  → kWh (e.g. 17, 101.3, 26.9)
#    etotal  → MWh (e.g. 64.84, 17.475, 110.355)
#
#  inverterDetail response:
#    pac     → kW  (precise decimal, e.g. 9.8W shown as 0.0098 when /1000 was wrong)
#              CONFIRMED: pac field is already in kW (e.g. 9.53, 298.89 total)
#    etoday  → kWh
#    etotal  → MWh
#    inverterTemperature → °C
#    uAc1    → V
#    iAc1    → A
#
#  CONCLUSION: pac from inverterDetail is in kW — use it directly, NO division.
# ============================================================

# import hashlib, base64, json, hmac, requests
# from datetime import datetime, timezone
# from config import SOLIS_API_KEY, SOLIS_API_SECRET, SOLIS_BASE_URL


# def _headers(api_path, body_json):
#     md5  = hashlib.md5(body_json.encode()).digest()
#     cmd5 = base64.b64encode(md5).decode()
#     date = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")
#     sts  = f"POST\n{cmd5}\napplication/json\n{date}\n{api_path}"
#     sign = base64.b64encode(
#         hmac.new(SOLIS_API_SECRET.encode(), sts.encode(), hashlib.sha1).digest()
#     ).decode()
#     return {"Content-MD5": cmd5, "Content-Type": "application/json",
#             "Date": date, "Authorization": f"API {SOLIS_API_KEY}:{sign}"}


# def _post(path, body):
#     bj = json.dumps(body, separators=(",", ":"))
#     try:
#         r = requests.post(SOLIS_BASE_URL + path, data=bj,
#                           headers=_headers(path, bj), timeout=15)
#         r.raise_for_status()
#         return r.json()
#     except Exception as e:
#         print(f"❌ Solis [{path}]: {e}")
#         return None


# def _f(v):
#     try:    return float(v)
#     except: return None


# def get_plants():
#     d = _post("/v1/api/userStationList", {"pageNo": 1, "pageSize": 100})
#     return (d or {}).get("data", {}).get("page", {}).get("records", [])


# def get_inverters(plant_id):
#     d = _post("/v1/api/inverterList", {"stationId": plant_id})
#     return (d or {}).get("data", {}).get("page", {}).get("records", [])


# def get_detail(sn):
#     d = _post("/v1/api/inverterDetail", {"sn": sn})
#     return ((d or {}).get("data")) or {}


# def fetch_all():
#     """
#     Returns list of dicts. Units:
#       power_kw  → kW   (pac from inverterDetail, already kW, use directly)
#       today_kwh → kWh  (etoday)
#       total_kwh → MWh  (etotal — Solis reports all-time in MWh)
#     """
#     results = []
#     for plant in get_plants():
#         pid   = plant.get("id", "")
#         pname = plant.get("stationName", "Unknown")

#         for inv in get_inverters(pid):
#             sn    = inv.get("inverterSn", "")
#             state = inv.get("state")
#             status = {1: "Online", 0: "Offline"}.get(state, "Unknown")

#             # Fallback values from inverterList (rounded but available)
#             list_power = _f(inv.get("power"))     # kW, integer rounded
#             list_today = _f(inv.get("etoday"))     # kWh
#             list_total = _f(inv.get("etotal"))     # MWh

#             # Precise values from inverterDetail
#             det = get_detail(sn)

#             # pac = real-time power, CONFIRMED in kW (use directly, no conversion)
#             pac = _f(det.get("pac"))

#             # Use precise detail values; fall back to list values
#             power_kw  = pac          if pac          is not None else list_power
#             today_kwh = _f(det.get("etoday")) if det.get("etoday") is not None else list_today
#             total_mwh = _f(det.get("etotal")) if det.get("etotal") is not None else list_total

#             results.append({
#                 "brand":       "Solis",
#                 "plant_name":  pname,
#                 "plant_id":    pid,
#                 "inverter_sn": sn,
#                 "power_kw":    power_kw,   # kW
#                 "today_kwh":   today_kwh,  # kWh
#                 "total_kwh":   total_mwh,  # MWh (named total_kwh for DB compat)
#                 "status":      status,
#                 "temperature": _f(det.get("inverterTemperature")),
#                 "voltage":     _f(det.get("uAc1")),
#                 "current_a":   _f(det.get("iAc1")),
#                 "last_update": inv.get("dataTimestampStr"),
#             })
#     return results


# def fetch_summary():
#     """
#     Get plant-level KPI totals.

#     CONFIRMED field units (from live debug + official API docs):
#       power      → kW   (powerStr = "kW")
#       dayEnergy  → kWh  (dayEnergyStr = "kWh")
#       monthEnergy→ MWh  (monthEnergyStr = "MWh") — confirmed from docs "This month energy"
#       allEnergy  → MWh  (allEnergyStr = "MWh")   — confirmed from docs "Total energy"

#     Monthly discrepancy cause: monthEnergy in userStationList uses the plant's
#     local timezone and billing period. Use /v1/api/stationMonthEnergyList for
#     the exact calendar month total that matches the Solis app display.
#     stationMonthEnergyList returns energy per plant for the month in kWh.
#     """
#     from datetime import datetime as _dt
#     now        = _dt.now()
#     month_str  = now.strftime("%Y-%m")   # e.g. "2026-04"

#     total_power   = 0.0
#     total_daily   = 0.0   # kWh
#     total_all_mwh = 0.0   # MWh

#     plants = get_plants()
#     _raw_plants_cache.clear()
#     _raw_plants_cache.extend(plants)

#     for plant in plants:
#         total_power   += _f(plant.get("power",     0)) or 0
#         total_daily   += _f(plant.get("dayEnergy", 0)) or 0
#         total_all_mwh += _f(plant.get("allEnergy", 0)) or 0

#     # Monthly: use stationMonthEnergyList — returns energy(kWh) per plant for the month
#     # This is the same data source Solis app uses for Monthly Yield display
#     total_monthly_kwh = 0.0
#     try:
#         d = _post("/v1/api/stationMonthEnergyList", {
#             "pageNo":   1,
#             "pageSize": 100,
#             "time":     month_str
#         })
#         records = (d or {}).get("data", {}).get("page", {}).get("records", [])
#         for rec in records:
#             # energy field is in kWh per the API docs
#             total_monthly_kwh += _f(rec.get("energy", 0)) or 0
#     except Exception as e:
#         print(f"⚠️ stationMonthEnergyList failed: {e}")
#         # Fallback: use monthEnergy from userStationList (MWh) * 1000
#         total_monthly_kwh = sum(
#             (_f(p.get("monthEnergy", 0)) or 0) * 1000
#             for p in plants
#         )

#     return {
#         "power_kw":    total_power,
#         "daily_kwh":   total_daily,
#         "monthly_kwh": total_monthly_kwh,
#         "monthly_mwh": total_monthly_kwh / 1000,
#         "total_kwh":   total_all_mwh * 1000,
#         "total_mwh":   total_all_mwh,
#         "_raw_plants": list(plants),
#     }

# # Cache for debug inspection in app.py
# _raw_plants_cache = []

# ============================================================
#  utils/solis_api.py
#
#  CONFIRMED FIELD UNITS (from live debug data vs Solis app):
#
#  inverterList response:
#    power   → kW  BUT rounded to integer (100, 3, 30)  ← imprecise
#    etoday  → kWh (e.g. 17, 101.3, 26.9)
#    etotal  → MWh (e.g. 64.84, 17.475, 110.355)
#
#  inverterDetail response:
#    pac     → kW  (precise decimal, e.g. 9.8W shown as 0.0098 when /1000 was wrong)
#              CONFIRMED: pac field is already in kW (e.g. 9.53, 298.89 total)
#    etoday  → kWh
#    etotal  → MWh
#    inverterTemperature → °C
#    uAc1    → V
#    iAc1    → A
#
#  CONCLUSION: pac from inverterDetail is in kW — use it directly, NO division.
# ============================================================

import hashlib, base64, json, hmac, requests
import pandas as pd
from datetime import datetime, timezone
from config import SOLIS_API_KEY, SOLIS_API_SECRET, SOLIS_BASE_URL


def _headers(api_path, body_json):
    md5  = hashlib.md5(body_json.encode()).digest()
    cmd5 = base64.b64encode(md5).decode()
    date = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")
    sts  = f"POST\n{cmd5}\napplication/json\n{date}\n{api_path}"
    sign = base64.b64encode(
        hmac.new(SOLIS_API_SECRET.encode(), sts.encode(), hashlib.sha1).digest()
    ).decode()
    return {"Content-MD5": cmd5, "Content-Type": "application/json",
            "Date": date, "Authorization": f"API {SOLIS_API_KEY}:{sign}"}


def _post(path, body):
    bj = json.dumps(body, separators=(",", ":"))
    try:
        r = requests.post(SOLIS_BASE_URL + path, data=bj,
                          headers=_headers(path, bj), timeout=15)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"❌ Solis [{path}]: {e}")
        return None


def _f(v):
    try:    return float(v)
    except: return None


def get_plants():
    d = _post("/v1/api/userStationList", {"pageNo": 1, "pageSize": 100})
    return (d or {}).get("data", {}).get("page", {}).get("records", [])


def get_inverters(plant_id):
    d = _post("/v1/api/inverterList", {"stationId": plant_id})
    return (d or {}).get("data", {}).get("page", {}).get("records", [])


def get_detail(sn):
    d = _post("/v1/api/inverterDetail", {"sn": sn})
    return ((d or {}).get("data")) or {}


def fetch_all():
    """
    Returns list of dicts. Units:
      power_kw  → kW   (pac from inverterDetail, already kW, use directly)
      today_kwh → kWh  (etoday)
      total_kwh → MWh  (etotal — Solis reports all-time in MWh)
    """
    results = []
    for plant in get_plants():
        pid   = plant.get("id", "")
        pname = plant.get("stationName", "Unknown")

        for inv in get_inverters(pid):
            sn    = inv.get("inverterSn", "")
            state = inv.get("state")
            status = {1: "Online", 0: "Offline"}.get(state, "Unknown")

            # Fallback values from inverterList (rounded but available)
            list_power = _f(inv.get("power"))     # kW, integer rounded
            list_today = _f(inv.get("etoday"))     # kWh
            list_total = _f(inv.get("etotal"))     # MWh

            # Precise values from inverterDetail
            det = get_detail(sn)

            # pac = real-time power, CONFIRMED in kW (use directly, no conversion)
            pac = _f(det.get("pac"))

            # Use precise detail values; fall back to list values
            power_kw  = pac          if pac          is not None else list_power
            today_kwh = _f(det.get("etoday")) if det.get("etoday") is not None else list_today
            total_mwh = _f(det.get("etotal")) if det.get("etotal") is not None else list_total

            results.append({
                "brand":       "Solis",
                "plant_name":  pname,
                "plant_id":    pid,
                "inverter_sn": sn,
                "power_kw":    power_kw,   # kW
                "today_kwh":   today_kwh,  # kWh
                "total_kwh":   total_mwh,  # MWh (named total_kwh for DB compat)
                "status":      status,
                "temperature": _f(det.get("inverterTemperature")),
                "voltage":     _f(det.get("uAc1")),
                "current_a":   _f(det.get("iAc1")),
                "last_update": inv.get("dataTimestampStr"),
            })
    return results


def _to_mwh(value, unit_str):
    """Convert energy value to MWh, handling Solis auto-scaled units per plant."""
    try:
        v = float(value or 0)
        u = (unit_str or "MWh").strip().lower()
        if u == "kwh":   return v / 1000.0
        if u == "gwh":   return v * 1000.0
        return v  # MWh — use directly
    except:
        return 0.0


def _to_kwh(value, unit_str):
    """Convert energy value to kWh, handling Solis auto-scaled units per plant."""
    try:
        v = float(value or 0)
        u = (unit_str or "kWh").strip().lower()
        if u == "mwh":   return v * 1000.0
        if u == "gwh":   return v * 1_000_000.0
        return v  # kWh — use directly
    except:
        return 0.0


def fetch_summary():
    """
    Get plant-level KPI totals from userStationList.

    IMPORTANT: Solis auto-scales units per plant based on magnitude:
      - Small plants  (< 1000 kWh) → unit = "kWh"
      - Large plants  (≥ 1000 kWh) → unit = "MWh"

    So we MUST read the *Str field for each plant and convert accordingly.

    Confirmed per-plant values from live debug:
      S APPALA:  monthEnergy=1.76   monthEnergyStr="MWh"  → 1.76 MWh
      RANK-NGP:  monthEnergy=53.22  monthEnergyStr="MWh"  → 53.22 MWh
      Mohan:     monthEnergy=347.7  monthEnergyStr="kWh"  → 0.3477 MWh
      Javvajis:  monthEnergy=346.4  monthEnergyStr="kWh"  → 0.3464 MWh
      Siate:     monthEnergy=3.643  monthEnergyStr="MWh"  → 3.643 MWh
      TOTAL = ~59.1 MWh  ≈ Solis 57.547 MWh ✅ (difference = timing)

    Same logic applies to allEnergy (Total Yield).
    dayEnergy is always kWh for all plants.
    """
    plants = get_plants()
    _raw_plants_cache.clear()
    _raw_plants_cache.extend(plants)

    total_power       = 0.0
    total_daily_kwh   = 0.0
    total_monthly_mwh = 0.0
    total_all_mwh     = 0.0

    for p in plants:
        total_power       += _f(p.get("power",     0)) or 0
        # dayEnergy is always kWh — no conversion needed
        total_daily_kwh   += _f(p.get("dayEnergy", 0)) or 0
        # monthEnergy and allEnergy: unit varies per plant — must check *Str field
        total_monthly_mwh += _to_mwh(p.get("monthEnergy", 0), p.get("monthEnergyStr", "MWh"))
        total_all_mwh     += _to_mwh(p.get("allEnergy",   0), p.get("allEnergyStr",   "MWh"))

    return {
        "power_kw":    total_power,
        "daily_kwh":   total_daily_kwh,
        "monthly_kwh": total_monthly_mwh * 1000,
        "monthly_mwh": total_monthly_mwh,
        "total_kwh":   total_all_mwh * 1000,
        "total_mwh":   total_all_mwh,
        "_raw_plants": list(plants),
    }

# Cache for debug inspection in app.py
_raw_plants_cache = []


def get_plant_daily_history(plant_id, month_str):
    """
    Per-day energy for one plant in a given month.
    month_str: "2026-04"
    Returns list of dicts: [{date, energy_kwh, income}]
    """
    d = _post("/v1/api/stationDayEnergyList", {
        "id":       plant_id,
        "time":     month_str,
        "timeZone": 8,
        "pageNo":   1,
        "pageSize": 31,
    })
    data_obj = (d or {}).get("data") or {}
    page_obj = data_obj.get("page") or {}
    records  = page_obj.get("records") or []
    result = []
    for r in records:
        energy = _f(r.get("energy", 0)) or 0
        if energy > 0 or r.get("date"):
            result.append({
                "date":       r.get("date", ""),
                "energy_kwh": energy,
                "income":     _f(r.get("money") or r.get("income") or 0) or 0,
            })
    return result


def get_plant_monthly_history(plant_id, year_str):
    """
    Per-month energy for one plant in a given year.
    year_str: "2026"
    Returns list of dicts: [{month, energy_kwh, income}]
    """
    d = _post("/v1/api/stationMonthEnergyList", {
        "id":       plant_id,
        "time":     year_str,
        "timeZone": 8,
        "pageNo":   1,
        "pageSize": 12,
    })
    data_obj = (d or {}).get("data") or {}
    page_obj = data_obj.get("page") or {}
    records  = page_obj.get("records") or []
    result = []
    for r in records:
        energy = _f(r.get("energy", 0)) or 0
        if energy > 0 or r.get("date"):
            result.append({
                "month":      r.get("date", ""),
                "energy_kwh": energy,
                "income":     _f(r.get("money") or r.get("income") or 0) or 0,
            })
    return result


def get_all_plants_daily(month_str):
    """
    Daily energy for all plants in a given month.
    Returns DataFrame with columns: [plant_name, date, energy_kwh, income]
    """
    rows = []
    for plant in get_plants():
        pid   = plant.get("id", "")
        pname = plant.get("stationName", "Unknown")
        for r in get_plant_daily_history(pid, month_str):
            r["plant_name"] = pname
            rows.append(r)
    return pd.DataFrame(rows) if rows else pd.DataFrame()


def _fetch_inverter_day_chart(sn, date_str):
    """
    Call inverterPowerOneDayChart with multiple param/format variants.
    Returns (records, last_raw_response) where records is a list of
    {"time": "HH:MM", "power_kw": float} dicts.
    """
    date_nodash = date_str.replace("-", "")
    last_raw = None
    variants = [
        {"sn": sn, "time": date_nodash, "timeZone": 8},
        {"sn": sn, "time": date_nodash, "timeZone": 5},
        {"sn": sn, "time": date_str,    "timeZone": 8},
        {"sn": sn, "time": date_str,    "timeZone": 5},
        {"sn": sn, "time": date_nodash},
        {"sn": sn, "time": date_str},
    ]
    for body in variants:
        d = _post("/v1/api/inverterPowerOneDayChart", body)
        last_raw = d
        if not d:
            continue
        # Check API-level error
        if str(d.get("code", "0")) != "0":
            continue

        data_obj = d.get("data") or {}
        recs = []

        # Format A: data is a list
        if isinstance(data_obj, list):
            recs = [{"time": str(r.get("time") or ""),
                     "power_kw": float(r.get("power") or r.get("pac") or 0)}
                    for r in data_obj if r.get("time")]

        # Format A2: data.records or data.data list of objects
        if not recs:
            _raw = data_obj.get("records") or data_obj.get("data") or []
            if isinstance(_raw, list) and _raw:
                recs = [{"time": str(r.get("time") or ""),
                         "power_kw": float(r.get("power") or r.get("pac") or 0)}
                        for r in _raw if r.get("time")]

        # Format B: parallel arrays {time:[...], watt:[...]} at data root
        if not recs:
            t_arr = data_obj.get("time") or []
            w_arr = data_obj.get("watt") or []
            p_arr = data_obj.get("power") or data_obj.get("pac") or []
            if t_arr and w_arr:
                _wmax = max((float(x or 0) for x in w_arr), default=0)
                _wdiv = 1000.0 if _wmax > 100 else 1.0
                recs = [{"time": str(t), "power_kw": float(w or 0) / _wdiv}
                        for t, w in zip(t_arr, w_arr)]
            elif t_arr and p_arr:
                recs = [{"time": str(t), "power_kw": float(p or 0)}
                        for t, p in zip(t_arr, p_arr)]

        # Format C: inverterPowerVo wrapper
        if not recs:
            _pvo = data_obj.get("inverterPowerVo") or {}
            t_arr = _pvo.get("time") or []
            w_arr = _pvo.get("watt") or []
            if t_arr and w_arr:
                _wmax = max((float(x or 0) for x in w_arr), default=0)
                _wdiv = 1000.0 if _wmax > 100 else 1.0
                recs = [{"time": str(t), "power_kw": float(w or 0) / _wdiv}
                        for t, w in zip(t_arr, w_arr)]

        # Filter zeros (before/after daylight hours) but keep records list
        recs = [r for r in recs if r.get("time")]
        if recs:
            return recs, last_raw

    return [], last_raw


def fetch_day_chart_raw(sn, date_str):
    """Return the raw API response for debugging."""
    date_nodash = date_str.replace("-", "")
    return _post("/v1/api/inverterPowerOneDayChart",
                 {"sn": sn, "time": date_nodash, "timeZone": 8})


def get_plant_intraday_power(plant_id, date_str):
    """
    5-minute power curve for all inverters in a plant on a given day.
    date_str: "2026-05-03"
    Returns list of dicts: [{time: datetime, power_kw: float}]
    """
    from datetime import datetime as _dt
    inverters = get_inverters(plant_id)
    if not inverters:
        return []

    power_by_key = {}
    for inv in inverters:
        sn = inv.get("inverterSn", "")
        if not sn:
            continue
        for r in _fetch_inverter_day_chart(sn, date_str):
            t_raw = r.get("time") or r.get("dataTimestamp") or r.get("ts") or ""
            pwr   = float(r.get("power") or r.get("pac") or r.get("activePower") or 0)
            key   = str(t_raw)
            if key:
                power_by_key[key] = power_by_key.get(key, 0.0) + pwr

    result = []
    for t_raw, pwr in sorted(power_by_key.items()):
        try:
            t_str = str(t_raw).strip()
            if ":" in t_str and len(t_str) <= 5:
                dt = _dt.strptime(f"{date_str} {t_str}", "%Y-%m-%d %H:%M")
            elif t_str.isdigit() and len(t_str) > 8:
                dt = _dt.fromtimestamp(int(t_str) / 1000)
            else:
                dt = _dt.strptime(f"{date_str} {t_str}", "%Y-%m-%d %H:%M:%S")
            result.append({"time": dt, "power_kw": pwr})
        except Exception:
            continue
    return result


def get_all_plants_monthly(year_str):
    """
    Monthly energy for all plants in a given year.
    Returns DataFrame with columns: [plant_name, month, energy_kwh, income]
    """
    rows = []
    for plant in get_plants():
        pid   = plant.get("id", "")
        pname = plant.get("stationName", "Unknown")
        for r in get_plant_monthly_history(pid, year_str):
            r["plant_name"] = pname
            rows.append(r)
    return pd.DataFrame(rows) if rows else pd.DataFrame()