# # ============================================================
# #  utils/growatt_api.py — Growatt OpenAPI connector
# #  Docs: https://openapi.growatt.com/docs
# # ============================================================

# import hashlib
# import requests
# from config import GROWATT_USERNAME, GROWATT_PASSWORD, GROWATT_BASE_URL


# # ── Session (reused across calls in one refresh cycle) ───────
# _session    = requests.Session()
# _logged_in  = False


# def _md5(text: str) -> str:
#     return hashlib.md5(text.encode("utf-8")).hexdigest()


# def login() -> bool:
#     global _logged_in
#     if not GROWATT_USERNAME or not GROWATT_PASSWORD:
#         print("⚠️  Growatt credentials not configured in config.py")
#         return False

#     try:
#         res = _session.post(
#             f"{GROWATT_BASE_URL}/newTwoLoginAPI.do",
#             data={
#                 "userName": GROWATT_USERNAME,
#                 "password": _md5(GROWATT_PASSWORD),
#             },
#             timeout=15,
#         )
#         data = res.json()
#         if data.get("back", {}).get("success"):
#             _logged_in = True
#             return True
#         print("❌ Growatt login failed:", data)
#         return False
#     except Exception as e:
#         print(f"❌ Growatt login error: {e}")
#         return False


# def get_plants() -> list[dict]:
#     if not _logged_in and not login():
#         return []
#     try:
#         res  = _session.post(f"{GROWATT_BASE_URL}/index/getPlantListTitle", timeout=15)
#         data = res.json()
#         return data if isinstance(data, list) else []
#     except Exception as e:
#         print(f"❌ Growatt plant list error: {e}")
#         return []


# def get_inverters_for_plant(plant_id: str) -> list[dict]:
#     try:
#         res  = _session.post(
#             f"{GROWATT_BASE_URL}/panel/getDevicesByPlantList",
#             data={"plantId": plant_id, "currPage": 1},
#             timeout=15,
#         )
#         data = res.json()
#         return data.get("obj", {}).get("datas", [])
#     except Exception as e:
#         print(f"❌ Growatt inverter list error: {e}")
#         return []


# def fetch_all() -> list[dict]:
#     """Return normalised list matching the DB schema."""
#     if not _logged_in and not login():
#         return []

#     results = []

#     for plant in get_plants():
#         plant_id   = str(plant.get("id", ""))
#         plant_name = plant.get("plantName", "Unknown")

#         for inv in get_inverters_for_plant(plant_id):
#             # Growatt status: 1 = normal, 0 = offline, -1 = fault
#             status_code = inv.get("status", -99)
#             status_map  = {1: "Online", 0: "Offline", -1: "Fault"}
#             status      = status_map.get(status_code, "Unknown")

#             results.append({
#                 "brand":       "Growatt",
#                 "plant_name":  plant_name,
#                 "plant_id":    plant_id,
#                 "inverter_sn": inv.get("sn", ""),
#                 "power_kw":    _safe_float(inv.get("pac")),          # W → kW
#                 "today_kwh":   _safe_float(inv.get("eToday")),
#                 "total_kwh":   _safe_float(inv.get("eTotal")),
#                 "status":      status,
#                 "temperature": _safe_float(inv.get("ipmTemperature")),
#                 "voltage":     _safe_float(inv.get("vac1")),
#                 "current_a":   _safe_float(inv.get("iac1")),
#                 "last_update": inv.get("lastUpdateTime"),
#             })

#     return results


# def _safe_float(val) -> float | None:
#     try:
#         v = float(val)
#         # Growatt reports pac in W
#         return round(v / 1000, 3) if val and "pac" in str(val) else v
#     except (TypeError, ValueError):
#         return None

# utils/growatt_api.py
# import hashlib, requests
# from config import GROWATT_USERNAME, GROWATT_PASSWORD, GROWATT_BASE_URL

# _session   = requests.Session()
# _logged_in = False

# def _md5(t): return hashlib.md5(t.encode()).hexdigest()

# def login():
#     global _logged_in
#     if not GROWATT_USERNAME or not GROWATT_PASSWORD:
#         return False
#     try:
#         r = _session.post(f"{GROWATT_BASE_URL}/newTwoLoginAPI.do",
#                           data={"userName": GROWATT_USERNAME,
#                                 "password": _md5(GROWATT_PASSWORD)}, timeout=15)
#         if r.json().get("back", {}).get("success"):
#             _logged_in = True; return True
#     except Exception as e:
#         print(f"❌ Growatt login: {e}")
#     return False

# def _sf(v):
#     try:    return float(v)
#     except: return None

# def fetch_all():
#     if not _logged_in and not login(): return []
#     results = []
#     try:
#         plants = _session.post(f"{GROWATT_BASE_URL}/index/getPlantListTitle",
#                                timeout=15).json()
#         if not isinstance(plants, list): return []
#         for p in plants:
#             pid   = str(p.get("id",""))
#             pname = p.get("plantName","Unknown")
#             try:
#                 invs = _session.post(
#                     f"{GROWATT_BASE_URL}/panel/getDevicesByPlantList",
#                     data={"plantId": pid, "currPage": 1}, timeout=15
#                 ).json().get("obj",{}).get("datas",[])
#                 for inv in invs:
#                     sc = inv.get("status",-99)
#                     results.append({
#                         "brand":"Growatt","plant_name":pname,"plant_id":pid,
#                         "inverter_sn": inv.get("sn",""),
#                         "power_kw":    _sf(inv.get("pac")),
#                         "today_kwh":   _sf(inv.get("eToday")),
#                         "total_kwh":   _sf(inv.get("eTotal")),
#                         "status":      {1:"Online",0:"Offline",-1:"Fault"}.get(sc,"Unknown"),
#                         "temperature": _sf(inv.get("ipmTemperature")),
#                         "voltage":     _sf(inv.get("vac1")),
#                         "current_a":   _sf(inv.get("iac1")),
#                         "last_update": inv.get("lastUpdateTime"),
#                     })
#             except Exception as e:
#                 print(f"❌ Growatt inverters: {e}")
#     except Exception as e:
#         print(f"❌ Growatt plants: {e}")
#     return results

# ============================================================
#  utils/growatt_api.py
#
#  Uses the `growattServer` library which correctly handles
#  both regular and installer Growatt accounts.
#
#  Install: pip install growattServer
#
#  config.py settings:
#    GROWATT_USERNAME = "EEPUHC001"   ← installer username
#    GROWATT_PASSWORD = "Fractal123"  ← password
#    GROWATT_BASE_URL = "https://server.growatt.com"
# ============================================================

# from config import GROWATT_USERNAME, GROWATT_PASSWORD

# _api       = None
# _logged_in = False


# def _get_api():
#     """Get or create a logged-in growattServer API instance."""
#     global _api, _logged_in

#     if not GROWATT_USERNAME or not GROWATT_PASSWORD:
#         return None

#     if _logged_in and _api:
#         return _api

#     try:
#         import growattServer
#         _api = growattServer.GrowattApi()
#         result = _api.login(GROWATT_USERNAME, GROWATT_PASSWORD)

#         if result.get("result") == 1 or result.get("back", {}).get("success"):
#             _logged_in = True
#             print(f"✅ Growatt login OK as {GROWATT_USERNAME}")
#             return _api
#         else:
#             print(f"❌ Growatt login failed: {result}")
#             return None

#     except ImportError:
#         print("❌ growattServer not installed. Run: pip install growattServer")
#         return None
#     except Exception as e:
#         print(f"❌ Growatt login error: {e}")
#         return None


# def _sf(v):
#     try:    return float(v)
#     except: return None


# def fetch_all():
#     """
#     Fetch all plants and inverters from Growatt.
#     Returns normalised list matching DB schema.
#     """
#     if not GROWATT_USERNAME:
#         return []   # silently skip if not configured

#     api = _get_api()
#     if not api:
#         return []

#     results = []

#     try:
#         plants = api.plant_list()
#         plant_list = plants.get("data", {}).get("data", []) or []

#         # Some versions return a different structure
#         if not plant_list and isinstance(plants.get("data"), list):
#             plant_list = plants["data"]

#         print(f"✅ Growatt: {len(plant_list)} plant(s) found")

#         for plant in plant_list:
#             pid   = str(plant.get("plantId") or plant.get("id", ""))
#             pname = plant.get("plantName") or plant.get("name", "Unknown")

#             try:
#                 # Get all devices for this plant
#                 devices = api.plant_detail(pid, 1)
#                 inv_list = (devices.get("data", {}).get("invList") or
#                             devices.get("invList") or [])

#                 for inv in inv_list:
#                     sn     = inv.get("deviceSn") or inv.get("sn", "")
#                     status_code = inv.get("status", -99)
#                     status = {1:"Online", 0:"Offline", -1:"Fault"}.get(
#                         int(status_code) if status_code is not None else -99,
#                         "Unknown"
#                     )

#                     # pac is in W for Growatt — convert to kW
#                     pac_w = _sf(inv.get("pac") or inv.get("power", 0))
#                     power_kw = (pac_w / 1000.0) if pac_w else None

#                     results.append({
#                         "brand":       "Growatt",
#                         "plant_name":  pname,
#                         "plant_id":    pid,
#                         "inverter_sn": sn,
#                         "power_kw":    power_kw,
#                         "today_kwh":   _sf(inv.get("eToday") or inv.get("todayEnergy")),
#                         "total_kwh":   _sf(inv.get("eTotal") or inv.get("totalEnergy")),
#                         "status":      status,
#                         "temperature": _sf(inv.get("temperature") or inv.get("ipmTemperature")),
#                         "voltage":     _sf(inv.get("vac1") or inv.get("vacr")),
#                         "current_a":   _sf(inv.get("iac1") or inv.get("iacr")),
#                         "last_update": inv.get("lastUpdateTime") or inv.get("dataLogUpdateTime"),
#                     })

#             except Exception as e:
#                 print(f"❌ Growatt devices for {pname}: {e}")
#                 continue

#     except Exception as e:
#         print(f"❌ Growatt plant list error: {e}")
#         import traceback; traceback.print_exc()
#         global _logged_in
#         _logged_in = False   # force re-login next time

#     return results

# ============================================================
#  utils/growatt_api.py
#  Confirmed login details from browser network inspection:
#    URL:      https://oss.growatt.com/login
#    Fields:   userName, password (PLAIN TEXT), loginTime,
#              isReadPact=0, changeNotice=0, lang=en, type=1
# ============================================================

# import requests
# from datetime import datetime
# from config import GROWATT_USERNAME, GROWATT_PASSWORD

# BASE       = "https://oss.growatt.com"
# _session   = None
# _logged_in = False


# def _sf(v):
#     try:    return float(v)
#     except: return None


# def login():
#     global _session, _logged_in

#     if not GROWATT_USERNAME or not GROWATT_PASSWORD:
#         return False

#     _session = requests.Session()
#     _session.headers.update({
#         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
#         "Referer":    BASE,
#         "Origin":     BASE,
#     })

#     try:
#         r = _session.post(f"{BASE}/login", data={
#             "userName":     GROWATT_USERNAME,
#             "password":     GROWATT_PASSWORD,   # plain text confirmed
#             "loginTime":    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#             "isReadPact":   "0",
#             "changeNotice": "0",
#             "lang":         "en",
#             "type":         "1",
#             "passwordCrc":  "",
#         }, timeout=15)

#         print(f"Growatt login status: {r.status_code}, response: {r.text[:100]}")

#         # Success: response is "1" or contains success indicator
#         if r.status_code == 200 and r.text.strip() in ("1", "true"):
#             _logged_in = True
#             print("✅ Growatt login successful")
#             return True

#         # Some versions return JSON
#         try:
#             data = r.json()
#             if (data.get("result") == 1 or
#                     data.get("back", {}).get("success") or
#                     data.get("success")):
#                 _logged_in = True
#                 print("✅ Growatt login successful (JSON)")
#                 return True
#         except Exception:
#             pass

#         # Check if session cookie was set (another sign of success)
#         if "JSESSIONID" in _session.cookies or "growatt" in str(_session.cookies).lower():
#             _logged_in = True
#             print("✅ Growatt login successful (cookie)")
#             return True

#         print(f"❌ Growatt login failed: {r.text[:200]}")
#         return False

#     except Exception as e:
#         print(f"❌ Growatt login error: {e}")
#         return False


# def fetch_all():
#     global _logged_in

#     if not GROWATT_USERNAME:
#         return []

#     if not _logged_in and not login():
#         return []

#     results = []

#     try:
#         # Get plant list
#         r = _session.post(f"{BASE}/index/getPlantListTitle", timeout=15)
#         plants = r.json() if r.text.strip() else []

#         if not isinstance(plants, list):
#             # Try alternate endpoint
#             r2 = _session.post(f"{BASE}/newTwoLoginAPI.do", timeout=15)
#             plants = []

#         print(f"✅ Growatt: {len(plants)} plant(s)")

#         for plant in plants:
#             pid   = str(plant.get("plantId") or plant.get("id", ""))
#             pname = plant.get("plantName") or plant.get("name", "Unknown")

#             try:
#                 r2   = _session.post(f"{BASE}/panel/getDevicesByPlantList",
#                                      data={"plantId": pid, "currPage": 1},
#                                      timeout=15)
#                 invs = r2.json().get("obj", {}).get("datas", [])

#                 for inv in invs:
#                     sc = inv.get("status", -99)
#                     try: sc = int(sc)
#                     except: sc = -99

#                     pac_w    = _sf(inv.get("pac") or 0)
#                     power_kw = round(pac_w / 1000.0, 3) if pac_w else None

#                     results.append({
#                         "brand":       "Growatt",
#                         "plant_name":  pname,
#                         "plant_id":    pid,
#                         "inverter_sn": inv.get("sn", ""),
#                         "power_kw":    power_kw,
#                         "today_kwh":   _sf(inv.get("eToday")),
#                         "total_kwh":   _sf(inv.get("eTotal")),
#                         "status":      {1:"Online", 0:"Offline", -1:"Fault"}.get(sc, "Unknown"),
#                         "temperature": _sf(inv.get("ipmTemperature")),
#                         "voltage":     _sf(inv.get("vac1")),
#                         "current_a":   _sf(inv.get("iac1")),
#                         "last_update": inv.get("lastUpdateTime"),
#                     })

#             except Exception as e:
#                 print(f"❌ Growatt devices for {pname}: {e}")

#     except Exception as e:
#         print(f"❌ Growatt fetch error: {e}")
#         _logged_in = False

#     return results

# ============================================================
#  utils/growatt_api.py
#  Confirmed from browser network inspection:
#    Login:      POST https://oss.growatt.com/login
#    Plant list: POST https://oss.growatt.com/deviceManage/plantManage/list
#    Password:   plain text (not MD5)
# ============================================================

# import requests
# from datetime import datetime
# from config import GROWATT_USERNAME, GROWATT_PASSWORD

# BASE       = "https://oss.growatt.com"
# _session   = None
# _logged_in = False


# def _sf(v):
#     try:    return float(v)
#     except: return None


# def login():
#     global _session, _logged_in

#     if not GROWATT_USERNAME or not GROWATT_PASSWORD:
#         return False

#     _session = requests.Session()
#     _session.headers.update({
#         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
#         "Referer":    BASE,
#         "Origin":     BASE,
#     })

#     try:
#         r = _session.post(f"{BASE}/login", data={
#             "userName":     GROWATT_USERNAME,
#             "password":     GROWATT_PASSWORD,
#             "loginTime":    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#             "isReadPact":   "0",
#             "changeNotice": "0",
#             "lang":         "en",
#             "type":         "1",
#             "passwordCrc":  "",
#         }, timeout=15)

#         try:
#             data = r.json()
#             if data.get("result") == 1:
#                 _logged_in = True
#                 print("✅ Growatt login successful")
#                 return True
#             print(f"❌ Growatt login failed: {data}")
#             return False
#         except Exception:
#             pass

#         if "JSESSIONID" in _session.cookies or r.status_code == 200:
#             _logged_in = True
#             return True

#         return False

#     except Exception as e:
#         print(f"❌ Growatt login error: {e}")
#         return False


# def _get_plants():
#     """
#     Confirmed URL from browser: POST /deviceManage/plantManage/list
#     Falls back to older endpoints if needed.
#     """
#     endpoints = [
#         ("/deviceManage/plantManage/list", {"pageNum": 1, "pageSize": 20}),
#         ("/index/getPlantListTitle",       {}),
#         ("/manager/getPlantList",          {"currPage": 1}),
#     ]

#     for ep, data in endpoints:
#         try:
#             r = _session.post(f"{BASE}{ep}", data=data, timeout=15)
#             if not r.text.strip():
#                 continue

#             try:
#                 resp = r.json()
#             except Exception:
#                 continue

#             # Handle different response structures
#             # /deviceManage/plantManage/list returns:
#             # {"result":1, "obj":{"datas":[...]} or "data":{"list":[...]}}
#             plants = (
#                 resp.get("obj", {}).get("datas") or
#                 resp.get("obj", {}).get("data")  or
#                 resp.get("data", {}).get("list") or
#                 resp.get("data", {}).get("datas") or
#                 resp.get("datas") or
#                 (resp if isinstance(resp, list) else None)
#             )

#             if plants is not None:
#                 print(f"✅ Growatt plants from {ep}: {len(plants)} plant(s)")
#                 return plants

#             print(f"  Growatt {ep}: unexpected format: {str(resp)[:150]}")

#         except Exception as e:
#             print(f"  Growatt {ep} error: {e}")

#     return []


# def _get_inverters(plant_id):
#     """Get inverters for a plant."""
#     endpoints = [
#         ("/panel/getDevicesByPlantList",     {"plantId": plant_id, "currPage": 1}),
#         ("/deviceManage/plantManage/detail", {"plantId": plant_id}),
#         ("/inverter/list",                   {"plantId": plant_id, "pageNum": 1, "pageSize": 20}),
#     ]

#     for ep, data in endpoints:
#         try:
#             r = _session.post(f"{BASE}{ep}", data=data, timeout=15)
#             if not r.text.strip():
#                 continue
#             resp = r.json()

#             invs = (
#                 resp.get("obj", {}).get("datas") or
#                 resp.get("obj", {}).get("invList") or
#                 resp.get("data", {}).get("list") or
#                 resp.get("datas") or
#                 resp.get("invList") or
#                 []
#             )

#             if invs:
#                 return invs

#         except Exception as e:
#             print(f"  Growatt inverters {ep}: {e}")

#     return []


# def fetch_all():
#     global _logged_in

#     if not GROWATT_USERNAME:
#         return []

#     if not _logged_in and not login():
#         return []

#     results = []

#     try:
#         plants = _get_plants()

#         for plant in plants:
#             pid   = str(plant.get("plantId") or plant.get("id") or plant.get("plant_id", ""))
#             pname = plant.get("plantName") or plant.get("name") or plant.get("plant_name", "Unknown")

#             invs = _get_inverters(pid)

#             for inv in invs:
#                 sc = inv.get("status", -99)
#                 try: sc = int(sc)
#                 except: sc = -99

#                 pac_w    = _sf(inv.get("pac") or 0)
#                 power_kw = round(pac_w / 1000.0, 3) if pac_w else None

#                 results.append({
#                     "brand":       "Growatt",
#                     "plant_name":  pname,
#                     "plant_id":    pid,
#                     "inverter_sn": inv.get("sn") or inv.get("deviceSn", ""),
#                     "power_kw":    power_kw,
#                     "today_kwh":   _sf(inv.get("eToday") or inv.get("todayEnergy")),
#                     "total_kwh":   _sf(inv.get("eTotal") or inv.get("totalEnergy")),
#                     "status":      {1:"Online", 0:"Offline", -1:"Fault"}.get(sc, "Unknown"),
#                     "temperature": _sf(inv.get("ipmTemperature") or inv.get("temperature")),
#                     "voltage":     _sf(inv.get("vac1") or inv.get("vacr")),
#                     "current_a":   _sf(inv.get("iac1") or inv.get("iacr")),
#                     "last_update": inv.get("lastUpdateTime") or inv.get("dataLogUpdateTime"),
#                 })

#     except Exception as e:
#         print(f"❌ Growatt fetch_all error: {e}")
#         import traceback; traceback.print_exc()
#         _logged_in = False

#     print(f"✅ Growatt: {len(results)} inverter(s) fetched")
#     return results
# import cloudscraper
# import requests
# from datetime import datetime
# from config import GROWATT_USERNAME, GROWATT_PASSWORD, GROWATT_BASE_URL

# BASE = GROWATT_BASE_URL

# session = cloudscraper.create_scraper()

# session.headers.update({
#     "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
#     "Accept": "application/json, text/javascript, */*; q=0.01",
#     "Accept-Language": "en-US,en;q=0.9",
#     "X-Requested-With": "XMLHttpRequest",
#     "Referer": "https://oss.growatt.com/",
#     "Origin": "https://oss.growatt.com",
#     "Connection": "keep-alive"
# })


# def _sf(v):
#     try:
#         return float(v)
#     except:
#         return None


# def login():
#     try:
#         headers = {
#             "User-Agent": "Mozilla/5.0",
#             "X-Requested-With": "XMLHttpRequest",
#             "Referer": BASE,
#             "Origin": BASE
#         }

#         payload = {
#             "userName": GROWATT_USERNAME,
#             "password": GROWATT_PASSWORD,
#             "loginTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#             "lang": "en"
#         }

#         r = session.post(
#             f"{BASE}/login",
#             data=payload,
#             headers=headers,
#             timeout=20
#         )

#         print("LOGIN STATUS:", r.status_code)
#         print("LOGIN TEXT:", r.text[:500])

#         if r.status_code == 200:
#             return True

#         return False

#     except Exception as e:
#         print("LOGIN ERROR:", e)
#         return False


# def get_plants():
#     endpoints = [
#         "/deviceManage/plantManage/list",
#         "/index/getPlantListTitle",
#         "/PlantListAPI.do"
#     ]

#     for ep in endpoints:

#         try:
#             r = session.post(
#                 f"{BASE}{ep}",
#                 data={"pageNum": 1, "pageSize": 50},
#                 timeout=20
#             )

#             print("PLANT URL:", ep)
#             print("PLANT RESPONSE:", r.text[:1000])

#             try:
#                 j = r.json()
#             except:
#                 continue

#             if isinstance(j, dict):

#                 plants = (
#                     j.get("obj", {}).get("datas", []) or
#                     j.get("data", {}).get("list", []) or
#                     j.get("datas", []) or
#                     []
#                 )

#                 if plants:
#                     return plants

#         except Exception as e:
#             print(ep, e)

#     return []


# def get_inverters(plant_id):
#     endpoints = [
#         "/panel/getDevicesByPlantList",
#         "/inverter/list"
#     ]

#     for ep in endpoints:

#         try:
#             r = session.post(
#                 f"{BASE}{ep}",
#                 data={
#                     "plantId": plant_id,
#                     "pageNum": 1,
#                     "pageSize": 50
#                 },
#                 timeout=20
#             )

#             print("INV URL:", ep)
#             print("INV RESPONSE:", r.text[:1000])

#             try:
#                 j = r.json()
#             except:
#                 continue

#             invs = (
#                 j.get("obj", {}).get("datas", []) or
#                 j.get("data", {}).get("list", []) or
#                 j.get("datas", []) or
#                 []
#             )

#             if invs:
#                 return invs

#         except:
#             pass

#     return []


# def fetch_all():

#     if not login():
#         return []

#     final = []

#     plants = get_plants()

#     print("TOTAL PLANTS:", len(plants))

#     for p in plants:

#         pid = str(p.get("plantId") or p.get("id") or "")
#         pname = p.get("plantName") or p.get("name") or "Plant"

#         invs = get_inverters(pid)

#         for inv in invs:

#             pac = _sf(inv.get("pac") or 0)

#             final.append({
#                 "brand": "Growatt",
#                 "plant_name": pname,
#                 "plant_id": pid,
#                 "inverter_sn": inv.get("sn", ""),
#                 "power_kw": round(pac / 1000, 3),
#                 "today_kwh": _sf(inv.get("eToday")),
#                 "total_kwh": _sf(inv.get("eTotal")),
#                 "status": "Online",
#                 "temperature": _sf(inv.get("temperature")),
#                 "last_update": inv.get("lastUpdateTime")
#             })

#     print("FINAL RECORDS:", len(final))

#     return final

# import requests
# from config import GROWATT_BASE_URL

# BASE = GROWATT_BASE_URL

# session = requests.Session()

# session.headers.update({
#     "User-Agent": "Mozilla/5.0",
#     "Referer": BASE,
#     "Origin": BASE,
#     "X-Requested-With": "XMLHttpRequest"
# })

# # PASTE YOUR REAL COOKIES HERE
# session.cookies.set("JSESSIONID", "PASTE_HERE")
# session.cookies.set("SERVERID", "PASTE_HERE")


# def fetch_all():

#     r = session.post(
#         f"{BASE}/deviceManage/plantManage/list",
#         data={
#             "page": 1,
#             "pageNum": 1,
#             "pageSize": 50,
#             "groupId": -1,
#             "plantType": -1,
#             "order": 9
#         },
#         timeout=20
#     )

#     print("STATUS:", r.status_code)
#     print("RAW RESPONSE:")
#     print(r.text[:3000])

#     try:
#         j = r.json()
#     except Exception as e:
#         print("JSON ERROR:", e)
#         return []

#     plants = j.get("obj", {}).get("datas", [])

#     final = []

#     for p in plants:
#         final.append({
#             "brand": "Growatt",
#             "plant_name": p.get("plantName"),
#             "plant_id": p.get("plantId"),
#             "power_kw": p.get("pac"),
#             "today_kwh": p.get("eToday"),
#             "total_kwh": p.get("eTotal"),
#             "status": "Online"
#         })

#     return final

# import requests
# import browser_cookie3

# BASE = "https://oss.growatt.com"


# def fetch_all():

#     session = requests.Session()

#     # Load Chrome cookies for Growatt
#     cookies = browser_cookie3.chrome(domain_name="oss.growatt.com")
#     session.cookies.update(cookies)

#     session.headers.update({
#         "User-Agent": "Mozilla/5.0",
#         "X-Requested-With": "XMLHttpRequest",
#         "Referer": BASE,
#         "Origin": BASE
#     })

#     r = session.post(
#         f"{BASE}/deviceManage/plantManage/list",
#         data={
#             "page": 1,
#             "pageNum": 1,
#             "pageSize": 50,
#             "groupId": -1,
#             "plantType": -1,
#             "order": 9
#         },
#         timeout=20
#     )

#     print("STATUS:", r.status_code)
#     print(r.text[:1000])

#     j = r.json()

#     plants = j.get("obj", {}).get("datas", [])

#     final = []

#     for p in plants:
#         final.append({
#             "brand": "Growatt",
#             "plant_name": p.get("plantName"),
#             "plant_id": p.get("plantId"),
#             "power_kw": p.get("pac"),
#             "today_kwh": p.get("eToday"),
#             "total_kwh": p.get("eTotal"),
#             "status": "Online"
#         })

#     return final

# import requests

# BASE = "https://oss.growatt.com"


# def fetch_all():

#     session = requests.Session()

#     session.headers.update({
#         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
#         "Accept": "application/json, text/javascript, */*; q=0.01",
#         "X-Requested-With": "XMLHttpRequest",
#         "Referer": BASE,
#         "Origin": BASE
#     })

#     # Your real cookies
#     session.cookies.set(
#         "JSESSIONID",
#         "affd0314-727f-4f3d-91cc-6093c7266eb0"
#     )

#     session.cookies.set(
#         "SERVERID",
#         "833d80aef55d08edeccc52340c6b2e34|1777279257|1777267672"
#     )

#     r = session.post(
#         f"{BASE}/deviceManage/plantManage/list",
#         data={
#             "page": 1,
#             "pageNum": 1,
#             "pageSize": 50,
#             "groupId": -1,
#             "plantType": -1,
#             "order": 9
#         },
#         timeout=20
#     )

#     print("STATUS:", r.status_code)
#     print("RAW:", r.text[:1000])

#     try:
#         j = r.json()
#     except:
#         return []

#     # plants = j.get("obj", {}).get("datas", [])
#     obj = j.get("obj", {})
#     pagers = obj.get("pagers", [])

#     if pagers and len(pagers) > 0:
#         plants = pagers[0].get("datas", [])
#     else:
#         plants = []

#     final = []

#     for p in plants:
#         # print(p.get("plantNameEncryption"), "RAW STATUS =", p.get("status"))

#         print("RAW PLANT OBJECT:")
#         print(p)
#         print("--------------")

#         # final.append({
#         #     "brand": "Growatt",
#         #     "plant_name": p.get("plantNameEncryption"),
#         #     "plant_id": p.get("pId"),
#         #     "inverter_sn": p.get("pId"),   # temporary unique id
#         #     "power_kw": float(p.get("nominalPower", 0)) / 1000,
#         #     "today_kwh": float(p.get("eToday", 0)),
#         #     "total_kwh": float(p.get("eTotal", 0)),
#         #     # "status": p.get("status"),
#         #     "status": {
#         #         "1": "Online",
#         #         "3": "Abnormal",
#         #         "0": "Offline",
#         #         "-1": "Fault",
#         #         "2": "Warning"
#         #     }.get(str(p.get("status")), "Unknown"),
#         #     }.get(str(p.get("status")), "Unknown"),
#         #     "temperature": None,
#         #     "voltage": None,
#         #     "current_a": None,
#         #     "last_update": p.get("creatDate")
#         # })
#         final.append({
#             "brand": "Growatt",
#             "plant_name": p.get("plantNameEncryption"),
#             "plant_id": p.get("pId"),
#             "inverter_sn": p.get("pId"),
#             "power_kw": float(p.get("nominalPower", 0)) / 1000,
#             "today_kwh": float(p.get("eToday", 0)),
#             "total_kwh": float(p.get("eTotal", 0)),
#             "status": {
#                 "1": "Online",
#                 "3": "Abnormal",
#                 "0": "Offline",
#                 "-1": "Fault",
#                 "2": "Warning"
#             }.get(str(p.get("status")), "Unknown"),
#             "temperature": None,
#             "voltage": None,
#             "current_a": None,
#             "last_update": p.get("creatDate")
#         })

#     return final

# ============================================================
#  utils/growatt_api.py
#  Confirmed working implementation from live browser inspection
#  Login:      POST https://oss.growatt.com/login (plain password)
#  Plant list: POST https://oss.growatt.com/deviceManage/plantManage/list
#  Inverters:  POST https://oss.growatt.com/deviceManage/deviceList
# ============================================================

# import requests
# from datetime import datetime
# from config import GROWATT_USERNAME, GROWATT_PASSWORD

# BASE       = "https://oss.growatt.com"
# _session   = None
# _logged_in = False


# def _sf(v):
#     try:    return float(v)
#     except: return None


# def login():
#     global _session, _logged_in

#     if not GROWATT_USERNAME or not GROWATT_PASSWORD:
#         return False

#     _session = requests.Session()
#     _session.headers.update({
#         "User-Agent":      "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
#         "Accept":          "application/json, text/javascript, */*; q=0.01",
#         "X-Requested-With":"XMLHttpRequest",
#         "Referer":         BASE,
#         "Origin":          BASE,
#     })

#     try:
#         r = _session.post(f"{BASE}/login", data={
#             "userName":     GROWATT_USERNAME,
#             "password":     GROWATT_PASSWORD,   # plain text confirmed
#             "loginTime":    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#             "isReadPact":   "0",
#             "changeNotice": "0",
#             "lang":         "en",
#             "type":         "1",
#             "passwordCrc":  "",
#         }, timeout=15)

#         data = r.json()
#         if data.get("result") == 1:
#             _logged_in = True
#             print("✅ Growatt login successful")
#             return True

#         print(f"❌ Growatt login failed: {data}")
#         return False

#     except Exception as e:
#         print(f"❌ Growatt login error: {e}")
#         return False


# def _get_plants():
#     """Fetch all plants using confirmed endpoint and response structure."""
#     try:
#         r = _session.post(f"{BASE}/deviceManage/plantManage/list", data={
#             "page":      1,
#             "pageNum":   1,
#             "pageSize":  50,
#             "groupId":   -1,
#             "plantType": -1,
#             "order":     9,
#         }, timeout=20)

#         j      = r.json()
#         obj    = j.get("obj", {})
#         pagers = obj.get("pagers", [])

#         if pagers and len(pagers) > 0:
#             return pagers[0].get("datas", [])

#         # Fallback structure
#         return obj.get("datas", [])

#     except Exception as e:
#         print(f"❌ Growatt plant list error: {e}")
#         return []


# def _get_inverters(plant_id):
#     """
#     Fetch inverter-level data for a plant.
#     Tries multiple endpoints to get per-inverter readings.
#     """
#     endpoints = [
#         ("/deviceManage/deviceList", {
#             "plantId": plant_id, "pageNum": 1, "pageSize": 50,
#             "deviceType": 1,
#         }),
#         ("/panel/getDevicesByPlantList", {
#             "plantId": plant_id, "currPage": 1,
#         }),
#         ("/newTwoPlantAPI.do?action=getDeviceListByPlantId", {
#             "plantId": plant_id,
#         }),
#     ]

#     for ep, data in endpoints:
#         try:
#             r    = _session.post(f"{BASE}{ep}", data=data, timeout=15)
#             if not r.text.strip():
#                 continue
#             resp = r.json()

#             invs = (
#                 resp.get("obj", {}).get("datas") or
#                 resp.get("obj", {}).get("invList") or
#                 resp.get("obj", {}).get("data") or
#                 resp.get("data", {}).get("list") or
#                 resp.get("datas") or
#                 resp.get("invList") or
#                 []
#             )

#             if invs:
#                 print(f"✅ Growatt inverters for plant {plant_id}: {len(invs)} device(s)")
#                 return invs

#         except Exception as e:
#             print(f"  Growatt inverters {ep}: {e}")

#     return []


# def fetch_all():
#     """
#     Fetch all Growatt plants and inverters.
#     Falls back to plant-level data if inverter endpoint unavailable.
#     """
#     global _logged_in

#     if not GROWATT_USERNAME:
#         return []

#     if not _logged_in and not login():
#         return []

#     results = []

#     try:
#         plants = _get_plants()
#         print(f"✅ Growatt: {len(plants)} plant(s) found")

#         for p in plants:
#             pid   = str(p.get("pId") or p.get("plantId") or p.get("id", ""))
#             pname = p.get("plantNameEncryption") or p.get("plantName") or "Unknown"

#             # Try to get per-inverter data
#             invs = _get_inverters(pid)

#             if invs:
#                 for inv in invs:
#                     sc = inv.get("status", -99)
#                     try: sc = int(sc)
#                     except: sc = -99

#                     pac_w    = _sf(inv.get("pac") or 0)
#                     power_kw = round(pac_w / 1000.0, 3) if pac_w else None

#                     results.append({
#                         "brand":       "Growatt",
#                         "plant_name":  pname,
#                         "plant_id":    pid,
#                         "inverter_sn": inv.get("sn") or inv.get("deviceSn", pid),
#                         "power_kw":    power_kw,
#                         "today_kwh":   _sf(inv.get("eToday") or inv.get("todayEnergy")),
#                         "total_kwh":   _sf(inv.get("eTotal") or inv.get("totalEnergy")),
#                         "status":      {1:"Online", 0:"Offline", -1:"Fault",
#                                         3:"Abnormal", 2:"Warning"}.get(sc, "Unknown"),
#                         "temperature": _sf(inv.get("ipmTemperature") or inv.get("temperature")),
#                         "voltage":     _sf(inv.get("vac1") or inv.get("vacr")),
#                         "current_a":   _sf(inv.get("iac1") or inv.get("iacr")),
#                         "last_update": inv.get("lastUpdateTime") or inv.get("dataLogUpdateTime"),
#                     })
#             else:
#                 # Fallback: use plant-level data as a single record
#                 status_map = {"1":"Online","3":"Abnormal","0":"Offline","-1":"Fault","2":"Warning"}
#                 nom_power  = _sf(p.get("nominalPower", 0))
#                 power_kw   = round(nom_power / 1000.0, 3) if nom_power else None

#                 results.append({
#                     "brand":       "Growatt",
#                     "plant_name":  pname,
#                     "plant_id":    pid,
#                     "inverter_sn": pid,
#                     "power_kw":    power_kw,
#                     "today_kwh":   _sf(p.get("eToday", 0)),
#                     "total_kwh":   _sf(p.get("eTotal", 0)),
#                     "status":      status_map.get(str(p.get("status")), "Unknown"),
#                     "temperature": None,
#                     "voltage":     None,
#                     "current_a":   None,
#                     "last_update": p.get("creatDate"),
#                 })

#     except Exception as e:
#         print(f"❌ Growatt fetch_all error: {e}")
#         import traceback; traceback.print_exc()
#         _logged_in = False

#     print(f"✅ Growatt total: {len(results)} record(s)")
#     return results


# # ── Historical data for Reports ──────────────────────────────

# def get_plant_daily_history(plant_id, month_str):
#     """
#     Get per-day energy for a Growatt plant for a given month.
#     month_str: "2026-04"
#     Returns list of dicts: [{date, energy_kwh, income}]
#     """
#     if not _logged_in:
#         login()

#     try:
#         year, month = month_str.split("-")
#         r = _session.post(f"{BASE}/energy/energyReportByMonth", data={
#             "plantId": plant_id,
#             "year":    year,
#             "month":   month,
#         }, timeout=15)

#         j    = r.json()
#         rows = (j.get("obj", {}).get("datas") or
#                 j.get("data", {}).get("list") or
#                 j.get("datas") or [])

#         result = []
#         for row in rows:
#             energy = _sf(row.get("energy") or row.get("eToday") or 0) or 0
#             result.append({
#                 "date":       row.get("date") or row.get("time", ""),
#                 "energy_kwh": energy,
#                 "income":     _sf(row.get("income") or 0) or 0,
#             })
#         return result

#     except Exception as e:
#         print(f"❌ Growatt daily history error: {e}")
#         return []


# def get_plant_monthly_history(plant_id, year_str):
#     """
#     Get per-month energy for a Growatt plant for a given year.
#     Returns list of dicts: [{month, energy_kwh, income}]
#     """
#     if not _logged_in:
#         login()

#     try:
#         r = _session.post(f"{BASE}/energy/energyReportByYear", data={
#             "plantId": plant_id,
#             "year":    year_str,
#         }, timeout=15)

#         j    = r.json()
#         rows = (j.get("obj", {}).get("datas") or
#                 j.get("data", {}).get("list") or [])

#         result = []
#         for row in rows:
#             energy = _sf(row.get("energy") or 0) or 0
#             result.append({
#                 "month":      row.get("month") or row.get("time", ""),
#                 "energy_kwh": energy,
#                 "income":     _sf(row.get("income") or 0) or 0,
#             })
#         return result

#     except Exception as e:
#         print(f"❌ Growatt monthly history error: {e}")
#         return []

# ============================================================
#  utils/growatt_api.py
#  Confirmed working implementation from live browser inspection
#  Login:      POST https://oss.growatt.com/login (plain password)
#  Plant list: POST https://oss.growatt.com/deviceManage/plantManage/list
#  Inverters:  POST https://oss.growatt.com/deviceManage/deviceList
# ============================================================

# ============================================================
#  utils/growatt_api.py
#  Confirmed working implementation from live browser inspection
#  Login:      POST https://oss.growatt.com/login (plain password)
#  Plant list: POST https://oss.growatt.com/deviceManage/plantManage/list
#  Inverters:  POST https://oss.growatt.com/deviceManage/deviceList
# ============================================================

# import requests
# from datetime import datetime
# from config import GROWATT_USERNAME, GROWATT_PASSWORD

# BASE       = "https://oss.growatt.com"
# _session   = None
# _logged_in = False


# def _sf(v):
#     try:    return float(v)
#     except: return None


# def login():
#     global _session, _logged_in

#     if not GROWATT_USERNAME or not GROWATT_PASSWORD:
#         return False

#     _session = requests.Session()
#     _session.headers.update({
#         "User-Agent":      "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
#         "Accept":          "application/json, text/javascript, */*; q=0.01",
#         "X-Requested-With":"XMLHttpRequest",
#         "Referer":         BASE,
#         "Origin":          BASE,
#     })

#     try:
#         r = _session.post(f"{BASE}/login", data={
#             "userName":     GROWATT_USERNAME,
#             "password":     GROWATT_PASSWORD,   # plain text confirmed
#             "loginTime":    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#             "isReadPact":   "0",
#             "changeNotice": "0",
#             "lang":         "en",
#             "type":         "1",
#             "passwordCrc":  "",
#         }, timeout=15)

#         data = r.json()
#         if data.get("result") == 1:
#             _logged_in = True
#             print("✅ Growatt login successful")
#             return True

#         print(f"❌ Growatt login failed: {data}")
#         return False

#     except Exception as e:
#         print(f"❌ Growatt login error: {e}")
#         return False


# def _get_plants():
#     """Fetch all plants using confirmed endpoint and response structure."""
#     try:
#         r = _session.post(f"{BASE}/deviceManage/plantManage/list", data={
#             "page":      1,
#             "pageNum":   1,
#             "pageSize":  50,
#             "groupId":   -1,
#             "plantType": -1,
#             "order":     9,
#         }, timeout=20)

#         j      = r.json()
#         obj    = j.get("obj", {})
#         pagers = obj.get("pagers", [])

#         if pagers and len(pagers) > 0:
#             return pagers[0].get("datas", [])

#         # Fallback structure
#         return obj.get("datas", [])

#     except Exception as e:
#         print(f"❌ Growatt plant list error: {e}")
#         return []


# def _get_inverters(plant_id):
#     """
#     Fetch inverter-level data for a plant.
#     Tries multiple endpoints to get per-inverter readings.
#     """
#     endpoints = [
#         ("/deviceManage/deviceList", {
#             "plantId": plant_id, "pageNum": 1, "pageSize": 50,
#             "deviceType": 1,
#         }),
#         ("/panel/getDevicesByPlantList", {
#             "plantId": plant_id, "currPage": 1,
#         }),
#         ("/newTwoPlantAPI.do?action=getDeviceListByPlantId", {
#             "plantId": plant_id,
#         }),
#     ]

#     for ep, data in endpoints:
#         try:
#             r    = _session.post(f"{BASE}{ep}", data=data, timeout=15)
#             if not r.text.strip():
#                 continue
#             resp = r.json()

#             invs = (
#                 resp.get("obj", {}).get("datas") or
#                 resp.get("obj", {}).get("invList") or
#                 resp.get("obj", {}).get("data") or
#                 resp.get("data", {}).get("list") or
#                 resp.get("datas") or
#                 resp.get("invList") or
#                 []
#             )

#             if invs:
#                 print(f"✅ Growatt inverters for plant {plant_id}: {len(invs)} device(s)")
#                 return invs

#         except Exception as e:
#             print(f"  Growatt inverters {ep}: {e}")

#     return []


# def fetch_all():
#     """
#     Fetch all Growatt plants and inverters.
#     Falls back to plant-level data if inverter endpoint unavailable.
#     """
#     global _logged_in

#     if not GROWATT_USERNAME:
#         return []

#     if not _logged_in and not login():
#         return []

#     results = []

#     try:
#         plants = _get_plants()
#         print(f"✅ Growatt: {len(plants)} plant(s) found")

#         for p in plants:
#             pid   = str(p.get("pId") or p.get("plantId") or p.get("id", ""))
#             pname = p.get("plantNameEncryption") or p.get("plantName") or "Unknown"

#             # Try to get per-inverter data
#             invs = _get_inverters(pid)

#             if invs:
#                 for inv in invs:
#                     sc = inv.get("status", -99)
#                     try: sc = int(sc)
#                     except: sc = -99

#                     pac_w    = _sf(inv.get("pac") or 0)
#                     power_kw = round(pac_w / 1000.0, 3) if pac_w else None

#                     results.append({
#                         "brand":       "Growatt",
#                         "plant_name":  pname,
#                         "plant_id":    pid,
#                         "inverter_sn": inv.get("sn") or inv.get("deviceSn", pid),
#                         "power_kw":    power_kw,
#                         "today_kwh":   _sf(inv.get("eToday") or inv.get("todayEnergy")),
#                         "total_kwh":   _sf(inv.get("eTotal") or inv.get("totalEnergy")),
#                         "status":      {1:"Online", 0:"Offline", -1:"Fault",
#                                         3:"Abnormal", 2:"Warning"}.get(sc, "Unknown"),
#                         "temperature": _sf(inv.get("ipmTemperature") or inv.get("temperature")),
#                         "voltage":     _sf(inv.get("vac1") or inv.get("vacr")),
#                         "current_a":   _sf(inv.get("iac1") or inv.get("iacr")),
#                         "last_update": inv.get("lastUpdateTime") or inv.get("dataLogUpdateTime"),
#                     })
#             else:
#                 # Fallback: use plant-level data as a single record
#                 status_map = {"1":"Online","3":"Abnormal","0":"Offline","-1":"Fault","2":"Warning"}
#                 nom_power  = _sf(p.get("nominalPower", 0))
#                 power_kw   = round(nom_power / 1000.0, 3) if nom_power else None

#                 results.append({
#                     "brand":       "Growatt",
#                     "plant_name":  pname,
#                     "plant_id":    pid,
#                     "inverter_sn": pid,
#                     "power_kw":    power_kw,
#                     "today_kwh":   _sf(p.get("eToday", 0)),
#                     "total_kwh":   _sf(p.get("eTotal", 0)),
#                     "status":      status_map.get(str(p.get("status")), "Unknown"),
#                     "temperature": None,
#                     "voltage":     None,
#                     "current_a":   None,
#                     "last_update": p.get("creatDate"),
#                 })

#     except Exception as e:
#         print(f"❌ Growatt fetch_all error: {e}")
#         import traceback; traceback.print_exc()
#         _logged_in = False

#     print(f"✅ Growatt total: {len(results)} record(s)")
#     return results


# # ── Historical data for Reports ──────────────────────────────

# def _try_endpoints(data_list, path_data_pairs):
#     """Try multiple endpoints, return first non-empty list result."""
#     global _session, _logged_in
#     if not _logged_in or _session is None:
#         login()
#     if _session is None:
#         return []
#     for ep, post_data in path_data_pairs:
#         try:
#             r = _session.post(f"{BASE}{ep}", data=post_data, timeout=15)
#             if not r.text.strip(): continue
#             j = r.json()
#             # Try common response structures
#             rows = (j.get("obj", {}).get("datas") or
#                     j.get("obj", {}).get("data")  or
#                     j.get("data", {}).get("list") or
#                     j.get("data", {}).get("datas") or
#                     j.get("datas") or
#                     j.get("list")  or [])
#             if rows:
#                 print(f"✅ Growatt history OK via {ep}: {len(rows)} rows")
#                 return rows
#         except Exception as e:
#             print(f"  Growatt {ep}: {e}")
#     return []


# def get_plant_daily_history(plant_id, month_str):
#     """
#     Get per-day energy for a Growatt plant for a given month.
#     month_str: "2026-04"
#     Returns list of dicts: [{date, energy_kwh, income}]
#     """
#     global _session
#     if not _logged_in or _session is None: login()
#     if _session is None: return []
#     year, month = month_str.split("-")

#     rows = _try_endpoints([], [
#         ("/newTwoPlantAPI.do?action=getPlantEnergyByDay",
#          {"plantId": plant_id, "year": year, "month": month}),
#         ("/energy/energyByDay",
#          {"plantId": plant_id, "year": year, "month": month}),
#         ("/panel/chart/storage/getStorageEnergyDayChart",
#          {"plantId": plant_id, "date": f"{year}-{month}-01"}),
#         ("/dataAnalysis/month",
#          {"plantId": plant_id, "year": year, "month": month}),
#     ])

#     result = []
#     for row in rows:
#         energy = _sf(row.get("energy") or row.get("eToday") or
#                      row.get("energe") or row.get("value") or 0) or 0
#         date_str = (row.get("date") or row.get("time") or
#                     row.get("day")  or row.get("ymd")  or "")
#         if energy > 0 or date_str:
#             result.append({
#                 "date":       date_str,
#                 "energy_kwh": energy,
#                 "income":     _sf(row.get("money") or row.get("income") or 0) or 0,
#             })
#     return result


# def get_plant_monthly_history(plant_id, year_str):
#     """
#     Get per-month energy for a Growatt plant for a given year.
#     Returns list of dicts: [{month, energy_kwh, income}]
#     """
#     global _session
#     if not _logged_in or _session is None: login()
#     if _session is None: return []
#     rows = _try_endpoints([], [
#         ("/newTwoPlantAPI.do?action=getPlantEnergyByMonth",
#          {"plantId": plant_id, "year": year_str}),
#         ("/energy/energyByMonth",
#          {"plantId": plant_id, "year": year_str}),
#         ("/dataAnalysis/year",
#          {"plantId": plant_id, "year": year_str}),
#     ])

#     result = []
#     for row in rows:
#         energy = _sf(row.get("energy") or row.get("energe") or
#                      row.get("value") or 0) or 0
#         month_str = (row.get("month") or row.get("time") or
#                      row.get("date")  or row.get("ym")   or "")
#         if energy > 0 or month_str:
#             result.append({
#                 "month":      month_str,
#                 "energy_kwh": energy,
#                 "income":     _sf(row.get("money") or row.get("income") or 0) or 0,
#             })
#     return result


# # ============================================================
# #  utils/growatt_api.py
# #  Confirmed working implementation from live browser inspection
# #  Login:      POST https://oss.growatt.com/login (plain password)
# #  Plant list: POST https://oss.growatt.com/deviceManage/plantManage/list
# #  Inverters:  POST https://oss.growatt.com/deviceManage/deviceList
# # ============================================================

# import requests
# from datetime import datetime
# from config import GROWATT_USERNAME, GROWATT_PASSWORD

# BASE       = "https://oss.growatt.com"
# _session   = None
# _logged_in = False


# def _sf(v):
#     try:    return float(v)
#     except: return None


# def login():
#     global _session, _logged_in

#     if not GROWATT_USERNAME or not GROWATT_PASSWORD:
#         return False

#     _session = requests.Session()
#     _session.headers.update({
#         "User-Agent":      "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
#         "Accept":          "application/json, text/javascript, */*; q=0.01",
#         "X-Requested-With":"XMLHttpRequest",
#         "Referer":         BASE,
#         "Origin":          BASE,
#     })

#     try:
#         r = _session.post(f"{BASE}/login", data={
#             "userName":     GROWATT_USERNAME,
#             "password":     GROWATT_PASSWORD,   # plain text confirmed
#             "loginTime":    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#             "isReadPact":   "0",
#             "changeNotice": "0",
#             "lang":         "en",
#             "type":         "1",
#             "passwordCrc":  "",
#         }, timeout=15)

#         data = r.json()
#         if data.get("result") == 1:
#             _logged_in = True
#             print("✅ Growatt login successful")
#             return True

#         print(f"❌ Growatt login failed: {data}")
#         return False

#     except Exception as e:
#         print(f"❌ Growatt login error: {e}")
#         return False


# def _get_plants():
#     """Fetch all plants using confirmed endpoint and response structure."""
#     try:
#         r = _session.post(f"{BASE}/deviceManage/plantManage/list", data={
#             "page":      1,
#             "pageNum":   1,
#             "pageSize":  50,
#             "groupId":   -1,
#             "plantType": -1,
#             "order":     9,
#         }, timeout=20)

#         j      = r.json()
#         obj    = j.get("obj", {})
#         pagers = obj.get("pagers", [])

#         if pagers and len(pagers) > 0:
#             return pagers[0].get("datas", [])

#         # Fallback structure
#         return obj.get("datas", [])

#     except Exception as e:
#         print(f"❌ Growatt plant list error: {e}")
#         return []


# def _get_inverters(plant_id):
#     """
#     Fetch inverter-level data for a plant.
#     Tries multiple endpoints to get per-inverter readings.
#     """
#     endpoints = [
#         ("/deviceManage/deviceList", {
#             "plantId": plant_id, "pageNum": 1, "pageSize": 50,
#             "deviceType": 1,
#         }),
#         ("/panel/getDevicesByPlantList", {
#             "plantId": plant_id, "currPage": 1,
#         }),
#         ("/newTwoPlantAPI.do?action=getDeviceListByPlantId", {
#             "plantId": plant_id,
#         }),
#     ]

#     for ep, data in endpoints:
#         try:
#             r    = _session.post(f"{BASE}{ep}", data=data, timeout=15)
#             if not r.text.strip():
#                 continue
#             resp = r.json()

#             invs = (
#                 resp.get("obj", {}).get("datas") or
#                 resp.get("obj", {}).get("invList") or
#                 resp.get("obj", {}).get("data") or
#                 resp.get("data", {}).get("list") or
#                 resp.get("datas") or
#                 resp.get("invList") or
#                 []
#             )

#             if invs:
#                 print(f"✅ Growatt inverters for plant {plant_id}: {len(invs)} device(s)")
#                 return invs

#         except Exception as e:
#             print(f"  Growatt inverters {ep}: {e}")

#     return []


# def fetch_all():
#     """
#     Fetch all Growatt plants and inverters.
#     Falls back to plant-level data if inverter endpoint unavailable.
#     """
#     global _logged_in

#     if not GROWATT_USERNAME:
#         return []

#     if not _logged_in and not login():
#         return []

#     results = []

#     try:
#         plants = _get_plants()
#         print(f"✅ Growatt: {len(plants)} plant(s) found")

#         for p in plants:
#             pid   = str(p.get("pId") or p.get("plantId") or p.get("id", ""))
#             pname = p.get("plantNameEncryption") or p.get("plantName") or "Unknown"

#             # Try to get per-inverter data
#             invs = _get_inverters(pid)

#             if invs:
#                 for inv in invs:
#                     sc = inv.get("status", -99)
#                     try: sc = int(sc)
#                     except: sc = -99

#                     pac_w    = _sf(inv.get("pac") or 0)
#                     power_kw = round(pac_w / 1000.0, 3) if pac_w else None

#                     results.append({
#                         "brand":       "Growatt",
#                         "plant_name":  pname,
#                         "plant_id":    pid,
#                         "inverter_sn": inv.get("sn") or inv.get("deviceSn", pid),
#                         "power_kw":    power_kw,
#                         "today_kwh":   _sf(inv.get("eToday") or inv.get("todayEnergy")),
#                         "total_kwh":   _sf(inv.get("eTotal") or inv.get("totalEnergy")),
#                         "status":      {1:"Online", 0:"Offline", -1:"Fault",
#                                         3:"Abnormal", 2:"Warning"}.get(sc, "Unknown"),
#                         "temperature": _sf(inv.get("ipmTemperature") or inv.get("temperature")),
#                         "voltage":     _sf(inv.get("vac1") or inv.get("vacr")),
#                         "current_a":   _sf(inv.get("iac1") or inv.get("iacr")),
#                         "last_update": inv.get("lastUpdateTime") or inv.get("dataLogUpdateTime"),
#                     })
#             else:
#                 # Fallback: use plant-level data as a single record
#                 status_map = {"1":"Online","3":"Abnormal","0":"Offline","-1":"Fault","2":"Warning"}
#                 nom_power  = _sf(p.get("nominalPower", 0))
#                 power_kw   = round(nom_power / 1000.0, 3) if nom_power else None

#                 results.append({
#                     "brand":       "Growatt",
#                     "plant_name":  pname,
#                     "plant_id":    pid,
#                     "inverter_sn": pid,
#                     "power_kw":    power_kw,
#                     "today_kwh":   _sf(p.get("eToday", 0)),
#                     "total_kwh":   _sf(p.get("eTotal", 0)),
#                     "status":      status_map.get(str(p.get("status")), "Unknown"),
#                     "temperature": None,
#                     "voltage":     None,
#                     "current_a":   None,
#                     "last_update": p.get("creatDate"),
#                 })

#     except Exception as e:
#         print(f"❌ Growatt fetch_all error: {e}")
#         import traceback; traceback.print_exc()
#         _logged_in = False

#     print(f"✅ Growatt total: {len(results)} record(s)")
#     return results


# # ── Historical data for Reports ──────────────────────────────


# # ── Confirmed endpoint from browser network inspection ───────
# # POST /deviceManage/getDevicesChartData
# # Payload: serverId=1, plantId, startDate=YYYY-MM, endDate=YYYY-MM, param=year|month
# # Response (param=year):  [{"year":{"2026-01":2781.7,"2026-02":8332.1,...}}]
# # Response (param=month): [{"month":{"2026-04-01":123.4,"2026-04-02":456.7,...}}]

# CHART_EP = "/deviceManage/getDevicesChartData"


# def _chart_data(plant_id, param, start_date, end_date):
#     """Call confirmed chart endpoint. Returns first item from response list."""
#     global _session, _logged_in
#     if not _logged_in or _session is None:
#         login()
#     if _session is None:
#         return {}
#     try:
#         r = _session.post(f"{BASE}{CHART_EP}", data={
#             "serverId":  "1",
#             "plantId":   plant_id,
#             "startDate": start_date,
#             "endDate":   end_date,
#             "param":     param,
#         }, timeout=15)
#         if not r.text.strip():
#             return {}
#         j = r.json()
#         if isinstance(j, list) and len(j) > 0:
#             return j[0]
#         return {}
#     except Exception as e:
#         print(f"❌ Growatt chart data error: {e}")
#         return {}


# def get_plant_daily_history(plant_id, month_str):
#     """
#     Get per-day energy for a Growatt plant for a given month.
#     month_str: "2026-04"
#     Returns list of dicts: [{date, energy_kwh, income}]
#     Uses param=month → {"month":{"2026-04-01":123.4,...}}
#     """
#     data    = _chart_data(plant_id, "month", month_str, month_str)
#     day_map = data.get("month", {})
#     return [
#         {"date": d, "energy_kwh": _sf(v) or 0, "income": 0.0}
#         for d, v in sorted(day_map.items())
#     ]


# def get_plant_monthly_history(plant_id, year_str):
#     """
#     Get per-month energy for a Growatt plant for a given year.
#     Returns list of dicts: [{month, energy_kwh, income}]
#     Uses param=year → {"year":{"2026-01":2781.7,...}}
#     """
#     data      = _chart_data(plant_id, "year", f"{year_str}-01", f"{year_str}-12")
#     month_map = data.get("year", {})
#     return [
#         {"month": m, "energy_kwh": _sf(v) or 0, "income": 0.0}
#         for m, v in sorted(month_map.items())
#     ]

# ============================================================
#  utils/growatt_api.py
#  Confirmed working implementation from live browser inspection
#  Login:      POST https://oss.growatt.com/login (plain password)
#  Plant list: POST https://oss.growatt.com/deviceManage/plantManage/list
#  Inverters:  POST https://oss.growatt.com/deviceManage/deviceList
# ============================================================

import requests
from datetime import datetime
from config import GROWATT_USERNAME, GROWATT_PASSWORD

BASE       = "https://oss.growatt.com"
_session   = None
_logged_in = False


def _sf(v):
    try:    return float(v)
    except: return None


def login():
    global _session, _logged_in

    if not GROWATT_USERNAME or not GROWATT_PASSWORD:
        return False

    _session = requests.Session()
    _session.headers.update({
        "User-Agent":      "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept":          "application/json, text/javascript, */*; q=0.01",
        "X-Requested-With":"XMLHttpRequest",
        "Referer":         BASE,
        "Origin":          BASE,
    })

    try:
        r = _session.post(f"{BASE}/login", data={
            "userName":     GROWATT_USERNAME,
            "password":     GROWATT_PASSWORD,   # plain text confirmed
            "loginTime":    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "isReadPact":   "0",
            "changeNotice": "0",
            "lang":         "en",
            "type":         "1",
            "passwordCrc":  "",
        }, timeout=15)

        data = r.json()
        if data.get("result") == 1:
            _logged_in = True
            print("✅ Growatt login successful")
            return True

        print(f"❌ Growatt login failed: {data}")
        return False

    except Exception as e:
        print(f"❌ Growatt login error: {e}")
        return False


def _get_plants():
    """Fetch all plants using confirmed endpoint and response structure."""
    try:
        r = _session.post(f"{BASE}/deviceManage/plantManage/list", data={
            "page":      1,
            "pageNum":   1,
            "pageSize":  50,
            "groupId":   -1,
            "plantType": -1,
            "order":     9,
        }, timeout=20)

        j      = r.json()
        obj    = j.get("obj", {})
        pagers = obj.get("pagers", [])

        if pagers and len(pagers) > 0:
            return pagers[0].get("datas", [])

        # Fallback structure
        return obj.get("datas", [])

    except Exception as e:
        print(f"❌ Growatt plant list error: {e}")
        return []


def _get_inverters(plant_id):
    """
    Fetch inverter-level data for a plant.
    OSS Growatt uses /deviceManage/plantManage/list for plant data
    which already includes per-plant totals.
    We get device list from the confirmed deviceList endpoint.
    """
    global _session
    if _session is None:
        return []

    # Confirmed from browser: device list is in the plant detail page
    endpoints = [
        ("/deviceManage/plantManage/getDeviceList",
         {"plantId": plant_id, "pageNum": 1, "pageSize": 50}),
        ("/deviceManage/deviceList/list",
         {"plantId": plant_id, "pageNum": 1, "pageSize": 50}),
        ("/deviceManage/plantManage/detail",
         {"plantId": plant_id}),
    ]

    for ep, data in endpoints:
        try:
            r = _session.post(f"{BASE}{ep}", data=data, timeout=15)
            if not r.text.strip():
                continue
            # Check it's actually JSON (not HTML redirect)
            if r.text.strip().startswith('<'):
                continue
            resp = r.json()
            invs = (
                resp.get("obj", {}).get("datas") or
                resp.get("obj", {}).get("data")  or
                resp.get("data", {}).get("list") or
                resp.get("datas") or []
            )
            if invs:
                print(f"✅ Growatt inverters from {ep}: {len(invs)}")
                return invs
        except Exception as e:
            pass   # silently try next endpoint

    return []  # Plant-level fallback used in fetch_all()


def fetch_all():
    """
    Fetch all Growatt plants and inverters.
    Falls back to plant-level data if inverter endpoint unavailable.
    """
    global _logged_in

    if not GROWATT_USERNAME:
        return []

    if not _logged_in and not login():
        return []

    results = []

    try:
        plants = _get_plants()
        print(f"✅ Growatt: {len(plants)} plant(s) found")

        for p in plants:
            pid   = str(p.get("pId") or p.get("plantId") or p.get("id", ""))
            pname = p.get("plantNameEncryption") or p.get("plantName") or "Unknown"

            # Try to get per-inverter data
            invs = _get_inverters(pid)

            if invs:
                for inv in invs:
                    sc = inv.get("status", -99)
                    try: sc = int(sc)
                    except: sc = -99

                    pac_w    = _sf(inv.get("pac") or 0)
                    power_kw = round(pac_w / 1000.0, 3) if pac_w else None

                    results.append({
                        "brand":       "Growatt",
                        "plant_name":  pname,
                        "plant_id":    pid,
                        "inverter_sn": inv.get("sn") or inv.get("deviceSn", pid),
                        "power_kw":    power_kw,
                        "today_kwh":   _sf(inv.get("eToday") or inv.get("todayEnergy")),
                        "total_kwh":   _sf(inv.get("eTotal") or inv.get("totalEnergy")),
                        "status":      {1:"Online", 0:"Offline", -1:"Fault",
                                        3:"Abnormal", 2:"Warning"}.get(sc, "Unknown"),
                        "temperature": _sf(inv.get("ipmTemperature") or inv.get("temperature")),
                        "voltage":     _sf(inv.get("vac1") or inv.get("vacr")),
                        "current_a":   _sf(inv.get("iac1") or inv.get("iacr")),
                        "last_update": inv.get("lastUpdateTime") or inv.get("dataLogUpdateTime"),
                    })
            else:
                # Fallback: use plant-level data as a single record
                status_map = {"1":"Online","3":"Abnormal","0":"Offline","-1":"Fault","2":"Warning"}
                nom_power  = _sf(p.get("nominalPower", 0))
                power_kw   = round(nom_power / 1000.0, 3) if nom_power else None

                results.append({
                    "brand":       "Growatt",
                    "plant_name":  pname,
                    "plant_id":    pid,
                    "inverter_sn": pid,
                    "power_kw":    power_kw,
                    "today_kwh":   _sf(p.get("eToday", 0)),
                    "total_kwh":   _sf(p.get("eTotal", 0)),
                    "status":      status_map.get(str(p.get("status")), "Unknown"),
                    "temperature": None,
                    "voltage":     None,
                    "current_a":   None,
                    "last_update": p.get("creatDate"),
                })

    except Exception as e:
        print(f"❌ Growatt fetch_all error: {e}")
        import traceback; traceback.print_exc()
        _logged_in = False

    print(f"✅ Growatt total: {len(results)} record(s)")
    return results


# ── Historical data for Reports ──────────────────────────────


# ── Confirmed endpoint from browser network inspection ───────
# POST /deviceManage/getDevicesChartData
# Payload: serverId=1, plantId, startDate=YYYY-MM, endDate=YYYY-MM, param=year|month
# Response (param=year):  [{"year":{"2026-01":2781.7,"2026-02":8332.1,...}}]
# Response (param=month): [{"month":{"2026-04-01":123.4,"2026-04-02":456.7,...}}]

CHART_EP = "/deviceManage/getDevicesChartData"


def _chart_data(plant_id, param, start_date, end_date):
    """Call confirmed chart endpoint. Returns first item from response list."""
    global _session, _logged_in
    if not _logged_in or _session is None:
        login()
    if _session is None:
        return {}
    try:
        r = _session.post(f"{BASE}{CHART_EP}", data={
            "serverId":  "1",
            "plantId":   plant_id,
            "startDate": start_date,
            "endDate":   end_date,
            "param":     param,
        }, timeout=15)
        if not r.text.strip():
            return {}
        j = r.json()
        if isinstance(j, list) and len(j) > 0:
            return j[0]
        return {}
    except Exception as e:
        print(f"❌ Growatt chart data error: {e}")
        return {}


def get_plant_daily_history(plant_id, month_str):
    """
    Get per-day energy for a Growatt plant for a given month.
    month_str: "2026-04"
    Returns list of dicts: [{date, energy_kwh, income}]
    Uses param=month → {"month":{"2026-04-01":123.4,...}}
    """
    data    = _chart_data(plant_id, "month", month_str, month_str)
    day_map = data.get("month", {})
    return [
        {"date": d, "energy_kwh": _sf(v) or 0, "income": 0.0}
        for d, v in sorted(day_map.items())
    ]


def get_plant_monthly_history(plant_id, year_str):
    """
    Get per-month energy for a Growatt plant for a given year.
    Returns list of dicts: [{month, energy_kwh, income}]
    Uses param=year → {"year":{"2026-01":2781.7,...}}
    """
    data      = _chart_data(plant_id, "year", f"{year_str}-01", f"{year_str}-12")
    month_map = data.get("year", {})
    return [
        {"month": m, "energy_kwh": _sf(v) or 0, "income": 0.0}
        for m, v in sorted(month_map.items())
    ]


def get_plant_intraday_power(plant_id, date_str):
    """
    Hourly/5-min power curve for a Growatt plant on a given day.
    date_str: "2026-05-03"
    Returns list of dicts: [{time: datetime, power_kw: float}]
    Uses param=day → {"day": {"HH:MM": kw_value, ...}}
    """
    from datetime import datetime as _dt
    data    = _chart_data(plant_id, "day", date_str, date_str)
    day_map = data.get("day", {})
    result  = []
    for t_str, pwr in sorted(day_map.items()):
        try:
            dt = _dt.strptime(f"{date_str} {t_str}", "%Y-%m-%d %H:%M")
            result.append({"time": dt, "power_kw": float(pwr or 0)})
        except Exception:
            continue
    return result