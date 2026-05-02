# # ============================================================
# #  utils/sungrow_api.py — Sungrow iSolarCloud OpenAPI connector
# #  Docs: https://developer.isolarcloud.com
# # ============================================================

# import time
# import hashlib
# import requests
# from config import SUNGROW_APP_KEY, SUNGROW_ACCESS_KEY, SUNGROW_BASE_URL

# _token        = None
# _token_expiry = 0


# def _get_token() -> str | None:
#     global _token, _token_expiry

#     if not SUNGROW_APP_KEY or not SUNGROW_ACCESS_KEY:
#         print("⚠️  Sungrow credentials not configured in config.py")
#         return None

#     if _token and time.time() < _token_expiry:
#         return _token

#     try:
#         res = requests.post(
#             f"{SUNGROW_BASE_URL}/openapi/login",
#             json={
#                 "appkey":     SUNGROW_APP_KEY,
#                 "user_account": SUNGROW_ACCESS_KEY,
#                 "user_password": "",
#             },
#             timeout=15,
#         )
#         data = res.json()
#         if data.get("result_code") == "1":
#             _token        = data["result_data"]["token"]
#             _token_expiry = time.time() + 3500   # tokens valid ~1 hr
#             return _token
#         print("❌ Sungrow login failed:", data.get("result_msg"))
#         return None
#     except Exception as e:
#         print(f"❌ Sungrow login error: {e}")
#         return None


# def _headers() -> dict:
#     token = _get_token()
#     return {
#         "Content-Type": "application/json",
#         "token":        token or "",
#         "appkey":       SUNGROW_APP_KEY,
#     }


# def get_plants() -> list[dict]:
#     token = _get_token()
#     if not token:
#         return []
#     try:
#         res  = requests.post(
#             f"{SUNGROW_BASE_URL}/openapi/getPsList",
#             json={},
#             headers=_headers(),
#             timeout=15,
#         )
#         data = res.json()
#         return data.get("result_data", {}).get("pageList", [])
#     except Exception as e:
#         print(f"❌ Sungrow plant list error: {e}")
#         return []


# def get_inverters_for_plant(ps_id: str) -> list[dict]:
#     try:
#         res  = requests.post(
#             f"{SUNGROW_BASE_URL}/openapi/getDeviceList",
#             json={"ps_id": ps_id},
#             headers=_headers(),
#             timeout=15,
#         )
#         data = res.json()
#         return data.get("result_data", {}).get("pageList", [])
#     except Exception as e:
#         print(f"❌ Sungrow inverter list error: {e}")
#         return []


# def fetch_all() -> list[dict]:
#     """Return normalised list matching the DB schema."""
#     token = _get_token()
#     if not token:
#         return []

#     results = []

#     for plant in get_plants():
#         ps_id      = str(plant.get("ps_id", ""))
#         plant_name = plant.get("ps_name", "Unknown")

#         for inv in get_inverters_for_plant(ps_id):
#             # Sungrow device_status: 1=running, 0=standby, -1=fault
#             sc     = inv.get("device_status", -99)
#             status = {1: "Online", 0: "Standby", -1: "Fault"}.get(sc, "Unknown")

#             results.append({
#                 "brand":       "Sungrow",
#                 "plant_name":  plant_name,
#                 "plant_id":    ps_id,
#                 "inverter_sn": inv.get("dev_sn", ""),
#                 "power_kw":    _safe_float(inv.get("p_ac")),
#                 "today_kwh":   _safe_float(inv.get("daily_energy")),
#                 "total_kwh":   _safe_float(inv.get("total_energy")),
#                 "status":      status,
#                 "temperature": _safe_float(inv.get("temperature")),
#                 "voltage":     _safe_float(inv.get("u_ac")),
#                 "current_a":   _safe_float(inv.get("i_ac")),
#                 "last_update": inv.get("update_time"),
#             })

#     return results


# def _safe_float(val) -> float | None:
#     try:
#         return float(val)
#     except (TypeError, ValueError):
#         return None

# utils/sungrow_api.py
import time, requests
from config import SUNGROW_APP_KEY, SUNGROW_ACCESS_KEY, SUNGROW_BASE_URL

_token = None; _expiry = 0

def _get_token():
    global _token, _expiry
    if not SUNGROW_APP_KEY or not SUNGROW_ACCESS_KEY: return None
    if _token and time.time() < _expiry: return _token
    try:
        r = requests.post(f"{SUNGROW_BASE_URL}/openapi/login",
                          json={"appkey": SUNGROW_APP_KEY,
                                "user_account": SUNGROW_ACCESS_KEY,
                                "user_password": ""}, timeout=15)
        d = r.json()
        if d.get("result_code") == "1":
            _token = d["result_data"]["token"]; _expiry = time.time()+3500
            return _token
    except Exception as e:
        print(f"❌ Sungrow login: {e}")
    return None

def _sf(v):
    try:    return float(v)
    except: return None

def fetch_all():
    token = _get_token()
    if not token: return []
    hdrs = {"Content-Type":"application/json","token":token,"appkey":SUNGROW_APP_KEY}
    results = []
    try:
        plants = requests.post(f"{SUNGROW_BASE_URL}/openapi/getPsList",
                               json={}, headers=hdrs, timeout=15
                               ).json().get("result_data",{}).get("pageList",[])
        for p in plants:
            ps_id = str(p.get("ps_id",""))
            pname = p.get("ps_name","Unknown")
            try:
                devs = requests.post(f"{SUNGROW_BASE_URL}/openapi/getDeviceList",
                                     json={"ps_id":ps_id}, headers=hdrs, timeout=15
                                     ).json().get("result_data",{}).get("pageList",[])
                for d in devs:
                    sc = d.get("device_status",-99)
                    results.append({
                        "brand":"Sungrow","plant_name":pname,"plant_id":ps_id,
                        "inverter_sn": d.get("dev_sn",""),
                        "power_kw":    _sf(d.get("p_ac")),
                        "today_kwh":   _sf(d.get("daily_energy")),
                        "total_kwh":   _sf(d.get("total_energy")),
                        "status":      {1:"Online",0:"Standby",-1:"Fault"}.get(sc,"Unknown"),
                        "temperature": _sf(d.get("temperature")),
                        "voltage":     _sf(d.get("u_ac")),
                        "current_a":   _sf(d.get("i_ac")),
                        "last_update": d.get("update_time"),
                    })
            except: pass
    except Exception as e:
        print(f"❌ Sungrow: {e}")
    return results