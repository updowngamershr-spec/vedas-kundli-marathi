from datetime import datetime
# -*- coding: utf-8 -*-
"""
Shivansh Astro-Vastu - Complete Desktop Astrological Suite & High-Resolution Vector PDF Server
Features:
- Master Security Access / Login Gateway (User: Admin, Pass: Harman)
- High-Performance Offline Desktop Suite
- Interactive Janam Kundli with 4 Regional Chart Styles (North Indian, South Indian, East Indian / Bengali)
- Interactive Kundli Milan (Boy & Girl 36-Guna Ashtakoot Matching, Mangal Dosha, Papa Samya & Dasha Sandhi)
- 12 Bhava Predictions (Tanu to Vyaya) & Panchang 5 Pillars (Vaar, Tithi, Nakshatra, Yoga, Karana)
- Dasha & Apahara Timings, Classical Planetary Yogas, Rahu-Ketu Dosha Analysis & Remedies
- Universal Offline City Autocomplete across 721,229+ Indian statutory towns, tehsils & worldwide cities
- Dynamic Total Page Count calculation with 1-click vector PDF download & single pages ZIP
"""

import os
import sys
import io
import zipfile
import webbrowser
from threading import Timer
from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from pydantic import BaseModel
import uvicorn

from engine.cities import OFFLINE_CITIES, search_cities, find_city
from engine.ephemeris import compute_core_ephemeris, RASHI_NAMES_EN, RASHI_NAMES_HI
from engine.marathi_engine import to_marathi, RASHI_NAMES_MR, GRAHA_SHORT_MR, GRAHA_NAMES_MR, BHAVA_TITLES_MR
from engine.master_kundli import generate_complete_kundli
from engine.report_html_pdf import build_full_56_page_html, export_html_to_pdf
from engine.svg_charts import render_north_indian_svg, render_south_indian_svg, render_east_indian_svg
from engine.kundli_milan import calculate_ashtakoot_milan
from engine.milan_dossier import build_milan_dossier_html
from crm_db import init_crm_db, list_clients, get_client, save_client, delete_client, get_branding, save_branding, get_user_data_root, create_demo_key, list_demo_keys, toggle_demo_key_status, validate_access_key

app = FastAPI(title="Shivansh Astro-Vastu")

from fastapi.staticfiles import StaticFiles
assets_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
if os.path.exists(assets_dir):
    app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

@app.get("/presentation", response_class=HTMLResponse)
@app.get("/pitch", response_class=HTMLResponse)
def serve_sales_presentation():
    pres_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "presentation.html")
    if os.path.exists(pres_file):
        with open(pres_file, "r", encoding="utf-8") as f:
            return HTMLResponse(f.read())
    return HTMLResponse("Presentation loading...", status_code=200)

REPORTS_DIR = os.path.join(get_user_data_root(), "reports")
os.makedirs(REPORTS_DIR, exist_ok=True)

# Auto-sync bundled sample reports (Harman Kundli & Milan) into active reports directory
_bundled_reports_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports")
if os.path.exists(_bundled_reports_dir):
    for _rf in os.listdir(_bundled_reports_dir):
        if _rf.lower().endswith(".pdf"):
            _src_path = os.path.join(_bundled_reports_dir, _rf)
            _dst_path = os.path.join(REPORTS_DIR, _rf)
            if not os.path.exists(_dst_path) and os.path.isfile(_src_path):
                try:
                    import shutil
                    shutil.copy2(_src_path, _dst_path)
                except Exception:
                    pass


class KundliRequest(BaseModel):
    id: int | None = None
    name: str = ""
    sex: str = "Male"
    year: int | None = None        # No dummy default. Must be supplied by client form.
    month: int | None = None       # No dummy default. Must be supplied by client form.
    day: int | None = None         # No dummy default. Must be supplied by client form.
    hour: int | None = None        # No dummy default. Must be supplied by client form.
    minute: int | None = None      # No dummy default. Must be supplied by client form.
    second: int = 0
    place: str = "New Delhi"
    lat: float = 28.6139
    lon: float = 77.2090
    tz: float = 5.5
    varsha_year: int | None = None  # Defaults to current year dynamically
    phone: str = ""
    email: str = ""
    category: str = "General Consultation"
    notes: str = ""
    lang: str = "mr"
    chart_style: str = "north"
    report_package: str = "maha"


class BrandingRequest(BaseModel):
    astrologer_name: str = ""
    kendra_name: str = "Shivansh Astro-Vastu"
    phone: str = ""
    email: str = ""
    address: str = ""
    tagline: str = "Ancient Vedic, KP & Lal Kitab Predictions"
    logo_data: str = ""


class PrashnaRequest(BaseModel):
    place: str = "New Delhi"
    lat: float = 28.6139
    lon: float = 77.2090
    tz: float = 5.5
    lang: str = "mr"
    chart_style: str = "north"


class MilanPerson(BaseModel):
    name: str = ""
    sex: str = "Male"
    year: int | None = None    # Must be supplied by user; no dummy fallback
    month: int | None = None
    day: int | None = None
    hour: int | None = None
    minute: int | None = None
    second: int = 0
    place: str = "New Delhi"
    lat: float = 28.6139
    lon: float = 77.2090
    tz: float = 5.5


class MilanRequest(BaseModel):
    boy: MilanPerson
    girl: MilanPerson
    lang: str = "both"


last_heartbeat_time = 0.0
has_connected = False


@app.get("/api/heartbeat")
def api_heartbeat():
    global last_heartbeat_time, has_connected
    import time
    last_heartbeat_time = time.time()
    has_connected = True
    return {"status": "ok"}


@app.post("/api/shutdown")
def api_shutdown():
    import threading
    import time
    threading.Thread(target=lambda: (time.sleep(0.3), os._exit(0))).start()
    return {"status": "shutting down"}


@app.get("/favicon.ico")
def get_favicon():
    ico_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gurukulam.ico")
    if os.path.exists(ico_path):
        return FileResponse(ico_path, media_type="image/x-icon")
    return HTMLResponse(content="", status_code=404)


@app.post("/api/auth/login")
def api_auth_login(payload: dict):
    u = str(payload.get("username", "")).strip().lower()
    p = str(payload.get("password", "")).strip().lower()
    if u == "admin" and p == "harman":
        return {"success": True, "token": "VEDAS_AUTH_TOKEN_2026", "user": "Admin"}
    return {"success": False, "error": "Invalid username or password. Please use Admin / Harman"}



@app.get("/assets/gods/{name}")
def get_god_image(name: str):
    base_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    img_path = os.path.join(base_dir, "assets", "gods", name)
    if os.path.exists(img_path):
        return FileResponse(img_path, media_type="image/png")
    return JSONResponse({"error": "not found"}, status_code=404)


@app.get("/api/cities")
def api_get_cities(q: str = ""):
    q_str = str(q).strip() if q else ""
    if q_str and len(q_str) >= 2:
        return {"cities": search_cities(q_str, limit=40)}
    return {"cities": OFFLINE_CITIES}


@app.get("/api/clients")
def api_list_clients(q: str = ""):
    return {"clients": list_clients(q)}


@app.get("/api/clients/{client_id}")
def api_get_client(client_id: int):
    c = get_client(client_id)
    return {"client": c}


@app.post("/api/clients")
def api_save_client(req: KundliRequest):
    cid = save_client(req.model_dump())
    return {"id": cid, "client_id": cid, "success": True, "clients": list_clients()}


@app.delete("/api/clients/{client_id}")
def api_delete_client(client_id: int):
    delete_client(client_id)
    return {"clients": list_clients()}


@app.post("/api/kundli-details")
def api_kundli_details(req: KundliRequest):
    try:
        # === PHASE 2: Client Data Validation Layer ===
        missing = []
        if req.year is None or not (1800 <= req.year <= 2100):
            missing.append("Birth Year (1800-2100)")
        if req.month is None or not (1 <= req.month <= 12):
            missing.append("Birth Month (1-12)")
        if req.day is None or not (1 <= req.day <= 31):
            missing.append("Birth Day (1-31)")
        if req.hour is None or not (0 <= req.hour <= 23):
            missing.append("Birth Hour (0-23)")
        if req.minute is None or not (0 <= req.minute <= 59):
            missing.append("Birth Minute (0-59)")
        if missing:
            return JSONResponse({
                "success": False,
                "error": "missing_inputs",
                "message": f"Please fill in: {', '.join(missing)}",
                "fields": missing
            }, status_code=422)

        varsha_year = req.varsha_year if req.varsha_year else datetime.now().year

        data = generate_complete_kundli(
            name=req.name or "Client", sex=req.sex,
            year=req.year, month=req.month, day=req.day,
            hour=req.hour, minute=req.minute, second=req.second,
            place=req.place, lat=req.lat, lon=req.lon, tz=req.tz,
            varsha_year=varsha_year,
        )
        d1 = data["shodashvarga"]["charts"]["D1"]
        d9 = data["shodashvarga"]["charts"]["D9"]
        chart_north = render_north_indian_svg(d1["lagna_sign"], d1["house_planets"], size=290, lang=req.lang)
        chart_south = render_south_indian_svg(d1["lagna_sign"], d1["house_planets"], size=290, lang=req.lang)
        chart_east = render_east_indian_svg(d1["lagna_sign"], d1["house_planets"], size=290, lang=req.lang)

        d9_north = render_north_indian_svg(d9["lagna_sign"], d9["house_planets"], size=290, lang=req.lang)
        d9_south = render_south_indian_svg(d9["lagna_sign"], d9["house_planets"], size=290, lang=req.lang)
        d9_east = render_east_indian_svg(d9["lagna_sign"], d9["house_planets"], size=290, lang=req.lang)

        # All 16 Classical Shodashvarga Divisional Charts (D1 to D60) in 3 Regional Styles
        all_vargas = {}
        for code, ch_info in data["shodashvarga"]["charts"].items():
            all_vargas[code] = {
                "lagna_sign": ch_info["lagna_sign"],
                "north": render_north_indian_svg(ch_info["lagna_sign"], ch_info["house_planets"], size=290, lang=req.lang),
                "south": render_south_indian_svg(ch_info["lagna_sign"], ch_info["house_planets"], size=290, lang=req.lang),
                "east": render_east_indian_svg(ch_info["lagna_sign"], ch_info["house_planets"], size=290, lang=req.lang),
            }

        # Real-time Planetary Transit (Gochar) as of now
        now = datetime.now()
        transit_core = compute_core_ephemeris(
            name="Transit", sex="Male",
            year=now.year, month=now.month, day=now.day,
            hour=now.hour, minute=now.minute, second=now.second,
            place=req.place, lat_deg=data["meta"]["lat"], lon_deg=data["meta"]["lon"], tz_hours=data["meta"]["tz"]
        )
        natal_lagna_sign = data["meta"]["lagna_sign_num"]
        transit_houses = {h: [] for h in range(1, 13)}
        for p in transit_core["planets"]:
            bh = ((p["sign_num"] - natal_lagna_sign) % 12) + 1
            transit_houses[bh].append({
                "id": p["id"],
                "short_en": p["short_en"],
                "short_hi": p["short_hi"],
                "sign": p["sign_num"],
                "bhav": bh
            })
        transit_north = render_north_indian_svg(natal_lagna_sign, transit_houses, size=290, lang=req.lang)
        transit_south = render_south_indian_svg(natal_lagna_sign, transit_houses, size=290, lang=req.lang)

        # Calculate Current Running Dasha as of today
        now_tuple = (now.year, now.month, now.day)
        active_dasha = {
            "md_name": "", "ad_name": "", "summary": "N/A", "end_date": ""
        }
        vim = data["vimshottari"]
        for md in vim.get("mahadashas", []):
            md_end_tuple = (md.get("end_y", 9999), md.get("end_m", 12), md.get("end_d", 31))
            if md_end_tuple >= now_tuple:
                active_dasha["md_name"] = md.get("name_hi" if req.lang == "hi" else "name_en", md.get("code", ""))
                for ad in md.get("antardashas", []):
                    ad_end_tuple = (ad.get("end_y", 9999), ad.get("end_m", 12), ad.get("end_d", 31))
                    if ad_end_tuple >= now_tuple:
                        active_dasha["ad_name"] = ad.get("name_hi" if req.lang == "hi" else "name_en", ad.get("code", ""))
                        active_dasha["end_date"] = ad.get("end_str", "")
                        break
                break
        if active_dasha["md_name"] and active_dasha["ad_name"]:
            active_dasha["summary"] = f"{active_dasha['md_name']} (MD) • {active_dasha['ad_name']} (AD)"

        bhava_titles_en = [
            "1st: Tanu (Personality, Health & Self)",
            "2nd: Dhana (Wealth, Family & Speech)",
            "3rd: Sahaja (Courage, Siblings & Effort)",
            "4th: Sukha (Mother, Property & Happiness)",
            "5th: Putra (Intellect, Children & Destiny)",
            "6th: Ari (Health, Debts & Competition)",
            "7th: Jaya (Spouse, Marriage & Partnership)",
            "8th: Ayur (Longevity, Transformation & Occult)",
            "9th: Dharma (Fortune, Higher Wisdom & Father)",
            "10th: Karma (Career, Status & Leadership)",
            "11th: Labha (Gains, Incomes & Social Circle)",
            "12th: Vyaya (Expenditure, Foreign & Moksha)"
        ]
        bhava_titles_hi = [
            "प्रथम भाव (तनु): व्यक्तित्व, रूप-रंग व शारीरिक आरोग्यता",
            "द्वितीय भाव (धन): धन संचय, कुटुंब, वाणी व संपत्ति",
            "तृतीय भाव (सहज): पराक्रम, भ्रातृ सुख, साहस व पुरुषार्थ",
            "चतुर्थ भाव (सुख): माता, भूमि, भवन, वाहन व आंतरिक शांति",
            "पंचम भाव (संतान/बुद्धि): बुद्धि, विद्या, विवेक व पूर्व पुण्य",
            "षष्ठ भाव (रोग/रिपु): स्वास्थ्य, ऋण, शत्रु व सेवा कार्य",
            "सप्तम भाव (जाया): जीवनसाथी, विवाह, दांपत्य व साझेदारी",
            "अष्टम भाव (आयु): आयु, गूढ़ रहस्य, परिवर्तन व सुरक्षा",
            "नवम भाव (धर्म/भाग्य): भाग्य, धर्म, पिता, गुरु व उच्च शिक्षा",
            "दशम भाव (कर्म): आजीविका, व्यवसाय, पद-प्रतिष्ठा व सम्मान",
            "एकादश भाव (लाभ): आय, आर्थिक समृद्धि, मित्र व अभीष्ट सिद्धि",
            "द्वादश भाव (व्यय): व्यय, विदेश प्रवास, आत्मशुद्धि व मोक्ष"
        ]

        bhavas_list = []
        for h in range(1, 13):
            h_planets = d1["house_planets"].get(h, [])
            sign_num = ((d1["lagna_sign"] - 1 + (h - 1)) % 12) + 1
            s_en = RASHI_NAMES_EN[sign_num - 1]
            s_hi = RASHI_NAMES_HI[sign_num - 1]
            s_mr = RASHI_NAMES_MR[sign_num - 1]
            p_names = []
            for p in h_planets:
                if isinstance(p, dict):
                    p_id = p.get("id", "")
                    p_short_mr = GRAHA_SHORT_MR.get(p_id, to_marathi(p.get("short_hi", "")))
                    p_short_hi = p.get("short_hi", "")
                    p_names.append(f"{p_short_mr} ({p_short_hi})" if p_short_hi else p_short_mr)
                else:
                    p_names.append(to_marathi(str(p)))
            p_str = ", ".join(p_names) if p_names else "रिक्त - शुभ प्रभाव"
            title_mr = BHAVA_TITLES_MR[h-1]
            title_hi = bhava_titles_hi[h-1]
            bhavas_list.append({
                "house": h,
                "title_mr": title_mr,
                "title_hi": title_hi,
                "title_en": bhava_titles_en[h-1],
                "sign": f"{s_mr} ({s_hi})",
                "sign_mr": s_mr,
                "sign_hi": s_hi,
                "planets": p_str,
                "summary_mr": to_marathi(f"राशी {s_hi} द्वारे संचालित. हा भाव जातकाच्या जीवनात विशेष तेज, ऊर्जा आणि कार्यक्षेत्रात उत्कृष्ट यश प्रदान करतो."),
                "summary_hi": f"राशि {s_hi} द्वारा संचालित। यह भाव जातक के जीवन में विशेष स्थिरता, तेज व सफलता प्रदान करता है।",
                "summary_en": f"Governed by {s_en}. Influences native's vitality and domain success."
            })

        # Comprehensive Doshas Analysis
        planets = data["planets"]
        sun_p = next((p for p in planets if p.get("id") == "Sun"), None)
        moon_p = next((p for p in planets if p.get("id") == "Moon"), None)
        mars_p = next((p for p in planets if p.get("id") == "Mars"), None)
        jup_p = next((p for p in planets if p.get("id") == "Jupiter"), None)
        sat_p = next((p for p in planets if p.get("id") == "Saturn"), None)
        rahu_p = next((p for p in planets if p.get("id") == "Rahu"), None)
        ketu_p = next((p for p in planets if p.get("id") == "Ketu"), None)

        # Pitra Dosha
        is_pitra = False
        if sun_p and ((rahu_p and sun_p["sign_num"] == rahu_p["sign_num"]) or (ketu_p and sun_p["sign_num"] == ketu_p["sign_num"]) or (sun_p["house"] == 9 and sat_p and sat_p["house"] == 9)):
            is_pitra = True

        # Guru Chandal
        is_guru_chandal = False
        if jup_p and rahu_p and jup_p["sign_num"] == rahu_p["sign_num"]:
            is_guru_chandal = True

        # Grahan Dosha
        is_grahan = False
        if (sun_p and rahu_p and sun_p["sign_num"] == rahu_p["sign_num"]) or (moon_p and rahu_p and moon_p["sign_num"] == rahu_p["sign_num"]) or (sun_p and ketu_p and sun_p["sign_num"] == ketu_p["sign_num"]) or (moon_p and ketu_p and moon_p["sign_num"] == ketu_p["sign_num"]):
            is_grahan = True

        # Active Sade Sati Phase
        cur_year = datetime.now().year  # Dynamic: never hardcoded
        active_sadesati = None
        for s in data["sadesati"]:
            if s["start_year"] <= cur_year <= s["end_year"]:
                active_sadesati = s
                break
        if not active_sadesati and data["sadesati"]:
            upcoming = [s for s in data["sadesati"] if s["start_year"] >= cur_year]
            active_sadesati = upcoming[0] if upcoming else data["sadesati"][0]

        doshas_dict = {
            "manglik": data["manglik"],
            "kalsarpa": data["kalsarpa"],
            "sadesati": active_sadesati or {},
            "pitra_dosha": {
                "is_present": is_pitra,
                "title_en": "Pitra Dosha (Ancestral Karmic Influences)" if is_pitra else "No Pitra Dosha (Paternal Blessings)",
                "title_hi": "पितृ दोष (पूर्वज ऋण व शांति विचार)" if is_pitra else "पितृ दोष से मुक्त (शुभ पितृ कृपा)",
                "desc_en": "Sun is afflicted by shadow nodes (Rahu/Ketu/Saturn). Perform Shraddha karma and Narayan Bali for prosperity." if is_pitra else "Sun and 9th house are auspiciously placed, ensuring ancestral favor and protection.",
                "desc_hi": "सूर्य पर छाया ग्रह (राहु/केतु/शनि) की युति होने से पितृ दोष बनता है। अमावस्या पर दान व विष्णु सहस्त्रनाम जप हितकारी है।" if is_pitra else "सूर्य एवं नवम भाव दोषमुक्त हैं, जिससे पितरों का पूर्ण आशीर्वाद प्राप्त होता है।",
                "remedy_en": "Offer water to Sun at dawn, feed cows on Amavasya, chant Gayatri Mantra.",
                "remedy_hi": "प्रातः सूर्य को अर्घ्य दें, अमावस्या को गाय को हरा चारा व रोटी खिलाएं, गायत्री मंत्र जपें।"
            },
            "guru_chandal": {
                "is_present": is_guru_chandal,
                "title_en": "Guru Chandal Yoga" if is_guru_chandal else "Unafflicted Jupiter (Wisdom & Fortune)",
                "title_hi": "गुरु चांडाल योग (ज्ञान व विवेक मार्गदर्शन)" if is_guru_chandal else "दोष मुक्त बृहस्पति (उत्कृष्ट विवेक)",
                "desc_en": "Jupiter conjoins Rahu, demanding disciplined thinking and ethical career choices." if is_guru_chandal else "Jupiter is placed serenely, providing clear wisdom, educational success, and spiritual grace.",
                "desc_hi": "गुरु और राहु की युति से विचारों में असमंजस हो सकता है। शुद्ध आचरण व गुरु पूजन श्रेयस्कर है।" if is_guru_chandal else "देवगुरु बृहस्पति शुभ अवस्था में हैं, जो उच्च शिक्षा, विवेक व सात्विक सफलता प्रदान करते हैं।",
                "remedy_en": "Chant Brihaspati Beej Mantra (Om Gram Greem Groum Sah Gurave Namah) on Thursdays.",
                "remedy_hi": "गुरुवार को पीली दाल, चने की दाल का दान करें और 'ॐ बृं बृहस्पतये नमः' का जप करें।"
            },
            "grahan_dosha": {
                "is_present": is_grahan,
                "title_en": "Grahan Dosha (Eclipse Affliction)" if is_grahan else "No Grahan Dosha (Luminaries Clear)",
                "title_hi": "ग्रहण दोष (सूर्य/चन्द्र युति प्रभाव)" if is_grahan else "ग्रहण दोष से मुक्त (शुभ तेजस्विता)",
                "desc_en": "Sun or Moon conjoins nodal axes. Daily meditation and Lord Shiva worship stabilize energy." if is_grahan else "Sun and Moon radiate unhindered vitality, mental clarity, and emotional strength.",
                "desc_hi": "सूर्य या चन्द्रमा के साथ राहु/केतु स्थित होने से मानसिक उद्वेग संभव है। शिव आराधना लाभकारी है।" if is_grahan else "सूर्य व चन्द्रमा पूर्णतः दोषमुक्त हैं, जिससे आत्मबल, तेज व मानसिक शांति बनी रहती है।",
                "remedy_en": "Perform Jalabhishek on Shivling on Mondays, wear white on Purnima.",
                "remedy_hi": "सोमवार को शिवलिंग पर कच्चा दूध व जल अर्पित करें, महामृत्युंजय मंत्र का नित्य जप करें।"
            }
        }

        return {
            "success": True,
            "meta": data["meta"],
            "planets": data["planets"],
            "charts": {
                "north": chart_north,
                "south": chart_south,
                "east": chart_east,
                "d9_north": d9_north,
                "d9_south": d9_south,
                "d9_east": d9_east,
                "transit_north": transit_north,
                "transit_south": transit_south,
            },
            "active_dasha": active_dasha,
            "bhavas": bhavas_list,
            "doshas": doshas_dict,
            "avkahada": data["avkahada"],
            "favourable": data["favourable"],
            "manglik": data["manglik"],
            "kalsarpa": data["kalsarpa"],
            "vimshottari": data["vimshottari"],
            "yogas": data["yogas"][:8],
            "gemstones": data["gemstones"],
            "shadbala": data["shadbala"],
            "ashtakavarga": data["ashtakavarga"],
            "vargas": all_vargas,
            "kp": data.get("kp", {}),
            "kp_four_fold": data.get("kp_four_fold", {}),
            "kp_gems": data.get("kp_gems", {}),
            "kp_debts": data.get("kp_debts", {}),
            "kp_disease": data.get("kp_disease", {}),
            "kp_event_rules": data.get("kp_event_rules", {}),
            "lal_kitab": data.get("lal_kitab", {}),
            "chalit_table": data.get("chalit_table", []),
            "ghatak": data.get("ghatak", {}),
        }


    except Exception as exc:
        import traceback
        traceback.print_exc()
        return JSONResponse({
            "success": False,
            "error": "calculation_exception",
            "message": f"Kundli Calculation Error: {str(exc)}"
        }, status_code=400)


@app.post("/api/prashna-kundli")
def api_prashna_kundli(req: PrashnaRequest):
    now = datetime.now()
    k_req = KundliRequest(
        name="Prashna Chart",
        sex="Male",
        year=now.year, month=now.month, day=now.day,
        hour=now.hour, minute=now.minute, second=now.second,
        place=req.place, lat=req.lat, lon=req.lon, tz=req.tz,
        lang=req.lang, chart_style=req.chart_style
    )
    return api_kundli_details(k_req)


@app.get("/api/branding")
def api_get_branding():
    b = get_branding()
    return {"success": True, "branding": b, **b}


@app.post("/api/branding")
def api_save_branding(req: BrandingRequest):
    if req.logo_data and req.logo_data.startswith("data:image"):
        try:
            import base64, io
            from PIL import Image
            header, b64str = req.logo_data.split(",", 1)
            img_bytes = base64.b64decode(b64str)
            im = Image.open(io.BytesIO(img_bytes)).convert("RGB")
            im_resized = im.resize((800, 800), Image.Resampling.LANCZOS)
            dest_path = os.path.join(os.path.dirname(__file__), "assets", "images", "opt_shivansh_logo.jpg")
            im_resized.save(dest_path, "JPEG", quality=92, optimize=True)
        except Exception as e_logo:
            print("Warning saving logo to disk:", e_logo)
    updated = save_branding(req.model_dump())
    return {"success": True, "branding": updated}


@app.post("/api/kundli-milan")
def api_kundli_milan(req: MilanRequest):
    b_city = find_city(req.boy.place)
    b_lat = float(req.boy.lat) if req.boy.lat else b_city["lat"]
    b_lon = float(req.boy.lon) if req.boy.lon else b_city["lon"]
    b_tz = float(req.boy.tz) if req.boy.tz else b_city["tz"]
    boy_core = compute_core_ephemeris(
        name=req.boy.name, sex=req.boy.sex,
        year=req.boy.year, month=req.boy.month, day=req.boy.day,
        hour=req.boy.hour, minute=req.boy.minute, second=req.boy.second,
        place=req.boy.place, lat_deg=b_lat, lon_deg=b_lon, tz_hours=b_tz
    )
    
    g_city = find_city(req.girl.place)
    g_lat = float(req.girl.lat) if req.girl.lat else g_city["lat"]
    g_lon = float(req.girl.lon) if req.girl.lon else g_city["lon"]
    g_tz = float(req.girl.tz) if req.girl.tz else g_city["tz"]
    girl_core = compute_core_ephemeris(
        name=req.girl.name, sex=req.girl.sex,
        year=req.girl.year, month=req.girl.month, day=req.girl.day,
        hour=req.girl.hour, minute=req.girl.minute, second=req.girl.second,
        place=req.girl.place, lat_deg=g_lat, lon_deg=g_lon, tz_hours=g_tz
    )
    
    milan_result = calculate_ashtakoot_milan(boy_core, girl_core)
    return {"success": True, "milan": milan_result}


@app.post("/api/milan-preview-html", response_class=HTMLResponse)
def api_milan_preview_html(req: MilanRequest):
    b_city = find_city(req.boy.place)
    b_lat = float(req.boy.lat) if req.boy.lat and req.boy.lat != 28.6139 else b_city["lat"]
    b_lon = float(req.boy.lon) if req.boy.lon and req.boy.lon != 77.2090 else b_city["lon"]
    b_tz = float(req.boy.tz) if req.boy.tz else b_city["tz"]
    boy_core = compute_core_ephemeris(
        name=req.boy.name or "Groom", sex="Male",
        year=req.boy.year or 1995, month=req.boy.month or 1, day=req.boy.day or 1,
        hour=req.boy.hour or 12, minute=req.boy.minute or 0, second=req.boy.second or 0,
        place=req.boy.place, lat_deg=b_lat, lon_deg=b_lon, tz_hours=b_tz
    )
    g_city = find_city(req.girl.place)
    g_lat = float(req.girl.lat) if req.girl.lat and req.girl.lat != 28.6139 else g_city["lat"]
    g_lon = float(req.girl.lon) if req.girl.lon and req.girl.lon != 77.2090 else g_city["lon"]
    g_tz = float(req.girl.tz) if req.girl.tz else g_city["tz"]
    girl_core = compute_core_ephemeris(
        name=req.girl.name or "Bride", sex="Female",
        year=req.girl.year or 1997, month=req.girl.month or 1, day=req.girl.day or 1,
        hour=req.girl.hour or 12, minute=req.girl.minute or 0, second=req.girl.second or 0,
        place=req.girl.place, lat_deg=g_lat, lon_deg=g_lon, tz_hours=g_tz
    )
    milan = calculate_ashtakoot_milan(boy_core, girl_core)
    brand = get_branding()
    milan_html = build_milan_dossier_html(boy_core, girl_core, milan, brand, lang=req.lang or "hi")
    return HTMLResponse(milan_html)



class DemoKeyCreateReq(BaseModel):
    client_name: str
    duration_days: int = 7

class DemoKeyToggleReq(BaseModel):
    key_code: str
    status: str

class ValidateKeyReq(BaseModel):
    key_code: str

@app.get("/api/demo-keys")
def api_list_demo_keys():
    return {"keys": list_demo_keys()}

@app.post("/api/demo-keys/create")
def api_create_demo_key(req: DemoKeyCreateReq):
    res = create_demo_key(req.client_name, req.duration_days)
    return {"success": True, "key": res}

@app.post("/api/demo-keys/toggle")
def api_toggle_demo_key(req: DemoKeyToggleReq):
    ok = toggle_demo_key_status(req.key_code, req.status)
    return {"success": ok}

@app.post("/api/auth/validate-key")
def api_validate_key(req: ValidateKeyReq):
    res = validate_access_key(req.key_code)
    return res


@app.post("/api/export-milan-summary-pdf")
def api_export_milan_summary_pdf(req: MilanRequest):
    b_city = find_city(req.boy.place)
    b_lat = float(req.boy.lat) if req.boy.lat and req.boy.lat != 28.6139 else b_city["lat"]
    b_lon = float(req.boy.lon) if req.boy.lon and req.boy.lon != 77.2090 else b_city["lon"]
    b_tz = float(req.boy.tz) if req.boy.tz else b_city["tz"]
    boy_core = compute_core_ephemeris(
        name=req.boy.name or "Groom", sex="Male",
        year=req.boy.year or 1995, month=req.boy.month or 1, day=req.boy.day or 1,
        hour=req.boy.hour or 12, minute=req.boy.minute or 0, second=req.boy.second or 0,
        place=req.boy.place, lat_deg=b_lat, lon_deg=b_lon, tz_hours=b_tz
    )
    g_city = find_city(req.girl.place)
    g_lat = float(req.girl.lat) if req.girl.lat and req.girl.lat != 28.6139 else g_city["lat"]
    g_lon = float(req.girl.lon) if req.girl.lon and req.girl.lon != 77.2090 else g_city["lon"]
    g_tz = float(req.girl.tz) if req.girl.tz else g_city["tz"]
    girl_core = compute_core_ephemeris(
        name=req.girl.name or "Bride", sex="Female",
        year=req.girl.year or 1997, month=req.girl.month or 1, day=req.girl.day or 1,
        hour=req.girl.hour or 12, minute=req.girl.minute or 0, second=req.girl.second or 0,
        place=req.girl.place, lat_deg=g_lat, lon_deg=g_lon, tz_hours=g_tz
    )
    milan = calculate_ashtakoot_milan(boy_core, girl_core)
    brand = get_branding()

    milan_html = build_milan_dossier_html(boy_core, girl_core, milan, brand, lang=req.lang or "hi")

    safe_b = "".join(c if c.isalnum() else "_" for c in req.boy.name or "Groom")
    safe_g = "".join(c if c.isalnum() else "_" for c in req.girl.name or "Bride")
    milan_filename = f"Kundli_Milan_{safe_b}_{safe_g}.pdf"
    pdf_path = os.path.join(REPORTS_DIR, milan_filename)

    res = export_html_to_pdf(milan_html, pdf_path, split_single_pages=False)
    if res["success"]:
        return {
            "success": True,
            "filename": milan_filename,
            "download_url": f"/api/download-pdf/{milan_filename}",
            "page_count": res.get("page_count", 3)
        }
    return JSONResponse({"success": False, "error": res.get("error", "Milan PDF generation failed")}, status_code=500)

@app.post("/api/export-milan-person-pdf")
def api_export_milan_person_pdf(person: MilanPerson, lang: str = "hi"):
    p_city = find_city(person.place)
    p_lat = float(person.lat) if person.lat else p_city["lat"]
    p_lon = float(person.lon) if person.lon else p_city["lon"]
    p_tz = float(person.tz) if person.tz else p_city["tz"]
    data = generate_complete_kundli(
        name=person.name, sex=person.sex,
        year=person.year, month=person.month, day=person.day,
        hour=person.hour, minute=person.minute, second=person.second,
        place=person.place, lat=p_lat, lon=p_lon, tz=p_tz,
    )
    html_str = build_full_56_page_html(data, lang=lang)
    safe_name = "".join(c if c.isalnum() or c in ("_", "-") else "_" for c in person.name).strip("_") or "Kundli"
    pdf_filename = f"Shivansh_Astro_Vastu_{safe_name}_{lang.upper()}.pdf"
    pdf_path = os.path.join(REPORTS_DIR, pdf_filename)
    res = export_html_to_pdf(html_str, pdf_path, split_single_pages=False)
    if res["success"]:
        return {
            "success": True,
            "filename": pdf_filename,
            "download_url": f"/api/download-pdf/{pdf_filename}",
            "page_count": res.get("page_count", 62)
        }
    return JSONResponse({"success": False, "error": "Export failed"}, status_code=500)



@app.post("/api/generate-html", response_class=HTMLResponse)
def api_generate_html(req: KundliRequest):
    data = generate_complete_kundli(
        name=req.name, sex=req.sex,
        year=req.year, month=req.month, day=req.day,
        hour=req.hour, minute=req.minute, second=req.second,
        place=req.place, lat=req.lat, lon=req.lon, tz=req.tz,
        varsha_year=req.varsha_year,
    )
    brand_cfg = get_branding()
    if brand_cfg:
        if brand_cfg.get("kendra_name"):
            data["brand"]["kendra_name"] = brand_cfg["kendra_name"]
            data["brand"]["name_en"] = brand_cfg["kendra_name"]
        if brand_cfg.get("astrologer_name"):
            data["brand"]["astrologer_name"] = brand_cfg["astrologer_name"]
        if brand_cfg.get("phone"):
            data["brand"]["phone"] = brand_cfg["phone"]
        if brand_cfg.get("tagline"):
            data["brand"]["tagline_en"] = brand_cfg["tagline"]
    html_str = build_full_56_page_html(data, lang=req.lang, package=req.report_package)
    return HTMLResponse(content=html_str)


@app.post("/api/export-pdf")
def api_export_pdf(req: KundliRequest):
    data = generate_complete_kundli(
        name=req.name, sex=req.sex,
        year=req.year, month=req.month, day=req.day,
        hour=req.hour, minute=req.minute, second=req.second,
        place=req.place, lat=req.lat, lon=req.lon, tz=req.tz,
        varsha_year=req.varsha_year,
    )
    brand_cfg = get_branding()
    if brand_cfg:
        if brand_cfg.get("kendra_name"):
            data["brand"]["kendra_name"] = brand_cfg["kendra_name"]
            data["brand"]["name_en"] = brand_cfg["kendra_name"]
        if brand_cfg.get("astrologer_name"):
            data["brand"]["astrologer_name"] = brand_cfg["astrologer_name"]
        if brand_cfg.get("phone"):
            data["brand"]["phone"] = brand_cfg["phone"]
        if brand_cfg.get("tagline"):
            data["brand"]["tagline_en"] = brand_cfg["tagline"]
    html_str = build_full_56_page_html(data, lang=req.lang, package=req.report_package)
    safe_name = "".join(c if c.isalnum() or c in ("_", "-") else "_" for c in req.name).strip("_") or "Kundli"
    pkg_name = (req.report_package or "VIP").upper()
    ts_str = datetime.now().strftime("%Y%m%d_%H%M%S")
    brand_kendra = data["brand"].get("kendra_name") or "Shivansh_Astro_Vastu"
    safe_brand = "".join(c if c.isalnum() or c in ("_", "-") else "_" for c in brand_kendra).strip("_")
    pdf_filename = f"{safe_name}_{pkg_name}_{ts_str}_{safe_brand}.pdf"
    pdf_path = os.path.join(REPORTS_DIR, pdf_filename)

    res = export_html_to_pdf(html_str, pdf_path, split_single_pages=(req.report_package == "maha"))
    if res.get("success"):
        # Auto-copy to user's Downloads folder for instant access
        try:
            import shutil
            user_downloads = os.path.join(os.path.expanduser("~"), "Downloads")
            if os.path.exists(user_downloads):
                shutil.copy2(pdf_path, os.path.join(user_downloads, pdf_filename))
        except Exception:
            pass
        return {
            "success": True,
            "filename": pdf_filename,
            "path": pdf_path,
            "download_url": f"/api/download-pdf/{pdf_filename}",
            "single_pages_url": f"/api/download-single-pages-zip/{pdf_filename}",
            "page_count": res.get("page_count", 0),
        }
    
    # Seamless client-side dynamic print for cloud containers without headless chrome (e.g. Render)
    return {
        "success": True,
        "direct_print": True,
        "filename": pdf_filename,
        "page_count": 81,
        "message": "Dynamic 81-page report ready for client printing"
    }


@app.get("/api/reports")
def api_list_reports():
    reports = []
    seen = set()
    candidate_dirs = [REPORTS_DIR, os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports")]
    for s_dir in candidate_dirs:
        if os.path.exists(s_dir):
            try:
                for f in os.listdir(s_dir):
                    if f.lower().endswith(".pdf") and f not in seen:
                        full_path = os.path.join(s_dir, f)
                        try:
                            stat = os.stat(full_path)
                            seen.add(f)
                            reports.append({
                                "filename": f,
                                "size_mb": round(stat.st_size / (1024 * 1024), 2),
                                "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%d %b %Y, %I:%M %p"),
                                "mtime": stat.st_mtime,
                                "download_url": f"/api/download-pdf/{f}",
                            })
                        except Exception:
                            continue
            except Exception:
                pass
    reports.sort(key=lambda x: x.get("mtime", 0), reverse=True)
    return {"reports": reports[:30]}


@app.get("/api/download-pdf/{filename}")
def api_download_pdf(filename: str):
    safe_name = os.path.basename(filename)
    candidate_dirs = [REPORTS_DIR, os.path.join(os.path.dirname(os.path.abspath(__file__)), "reports")]
    for s_dir in candidate_dirs:
        pdf_path = os.path.join(s_dir, safe_name)
        if os.path.exists(pdf_path) and os.path.isfile(pdf_path):
            return FileResponse(
                pdf_path,
                media_type="application/pdf",
                filename=safe_name,
                headers={
                    "Content-Disposition": f'attachment; filename="{safe_name}"',
                    "Content-Type": "application/pdf",
                    "Cache-Control": "no-cache"
                }
            )
    return JSONResponse({"error": "File not found"}, status_code=404)


@app.get("/api/download-single-pages-zip/{filename}")
def api_download_single_pages_zip(filename: str):
    base_stem = os.path.splitext(os.path.basename(filename))[0]
    single_dir = os.path.join(REPORTS_DIR, f"{base_stem}_pages")
    if not os.path.exists(single_dir):
        return JSONResponse({"error": "Single pages directory not found"}, status_code=404)
    
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, _, files in os.walk(single_dir):
            for file in sorted(files):
                full_p = os.path.join(root, file)
                zf.write(full_p, arcname=f"{base_stem}_pages/{file}")
    zip_buffer.seek(0)
    
    zip_filename = f"{base_stem}_Separate_Pages.zip"
    return HTMLResponse(
        content=zip_buffer.getvalue(),
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{zip_filename}"'}
    )


@app.get("/", response_class=HTMLResponse)
def index_ui():
    headers = {
        "Cache-Control": "no-cache, no-store, must-revalidate",
        "Pragma": "no-cache",
        "Expires": "0"
    }
    return HTMLResponse(content="""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>शिवांश ॲस्ट्रो-वास्तू प्रोफेशनल - महाराष्ट्रियन मराठी (Shivansh Astro-Vastu)</title>
  <link rel="icon" type="image/x-icon" href="/favicon.ico"/>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@700;800;900&family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  <style>
    /* === Native Windows Desktop App Styling === */
    body {
      -webkit-user-select: none;
      user-select: none;
      overflow-x: hidden;
    }
    input, textarea, [contenteditable="true"], .report-scroll, pre, code {
      -webkit-user-select: text !important;
      user-select: text !important;
    }
    /* Luxury Dark Desktop Scrollbars */
    ::-webkit-scrollbar {
      width: 8px;
      height: 8px;
    }
    ::-webkit-scrollbar-track {
      background: #1C0F08;
    }
    ::-webkit-scrollbar-thumb {
      background: #78350F;
      border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
      background: #D97706;
    }

    :root {
      --bg-canvas: #FAF6F0;
      --bg-card: #FFFDF9;
      --bg-sidebar: #24140B;
      --border-gold: #EADBC8;
      --border-subtle: #F0E5D8;
      --maroon-deep: #451A03;
      --maroon-rich: #7C2D12;
      --amber-gold: #C2540A;
      --gold-bright: #E48800;
      --green-forest: #166534;
      --green-badge: #DCFCE7;
      --red-alert: #991B1B;
      --red-badge: #FEE2E2;
      --text-main: #2E1C10;
      --text-muted: #574032;
      --text-gold: #9A3412;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      background: var(--bg-canvas);
      color: var(--text-main);
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      height: 100vh;
      overflow: hidden;
      -webkit-font-smoothing: antialiased;
    }

    /* Custom Scrollbars */
    ::-webkit-scrollbar { width: 7px; height: 7px; }
    ::-webkit-scrollbar-track { background: #F4ECE1; }
    ::-webkit-scrollbar-thumb { background: #D9C3AB; border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: #C2540A; }



    /* Desktop Application Main Shell */
    .desktop-app {
      display: flex;
      height: 100vh;
      width: 100vw;
      overflow: hidden;
    }

    /* Left Sidebar Navigation */
    .desktop-sidebar {
      width: 240px; min-width: 240px;
      background: linear-gradient(180deg, #2E1C10 0%, #1A0F08 100%);
      display: flex; flex-direction: column; justify-content: space-between;
      border-right: 1.5px solid #451A03;
      box-shadow: 4px 0 20px rgba(0,0,0,0.18);
      z-index: 100;
    }
    .sidebar-brand {
      padding: 18px 16px 14px 16px;
      border-bottom: 1px solid rgba(234,219,200,0.12);
      display: flex; align-items: center; gap: 10px;
    }
    .brand-om {
      font-size: 32px; color: #E48800; line-height: 1;
      filter: drop-shadow(0 2px 6px rgba(228,136,0,0.4));
    }
    .brand-text .title {
      font-family: 'Cinzel', serif; font-size: 15.5px; font-weight: 900;
      letter-spacing: 1.2px; color: #FEF08A; line-height: 1.1;
    }
    .brand-text .sub {
      font-size: 10px; color: #D6D3D1; font-weight: 600; margin-top: 2px;
    }

    .sidebar-nav {
      padding: 12px 8px;
      display: flex; flex-direction: column; gap: 4px;
      flex: 1; overflow-y: auto;
    }
    .nav-btn {
      width: 100%;
      background: transparent;
      color: #E5E7EB;
      border: none;
      padding: 10px 14px;
      font-size: 12.5px;
      font-weight: 600;
      border-radius: 8px;
      cursor: pointer;
      display: flex; align-items: center; gap: 11px;
      transition: all 0.18s ease;
      text-align: left;
    }
    .nav-btn .icon { font-size: 16px; width: 22px; text-align: center; }
    .nav-btn:hover {
      background: rgba(228, 136, 0, 0.14);
      color: #FEF3C7;
      transform: translateX(3px);
    }
    .nav-btn.active {
      background: linear-gradient(90deg, #E48800 0%, #C2540A 100%);
      color: #FFFFFF;
      font-weight: 800;
      box-shadow: 0 3px 12px rgba(194,84,10,0.35);
      border-left: 3px solid #FEF08A;
    }

    .sidebar-footer {
      padding: 12px;
      border-top: 1px solid rgba(234,219,200,0.12);
      background: rgba(0,0,0,0.25);
    }
    .active-client-badge {
      background: rgba(255,255,255,0.06);
      border: 1px solid rgba(234,219,200,0.15);
      border-radius: 8px;
      padding: 8px 10px;
      margin-bottom: 8px;
    }
    .active-client-badge .lbl {
      font-size: 9px; font-weight: 800; color: #F59E0B; text-transform: uppercase; letter-spacing: 0.6px;
    }
    .active-client-badge .val {
      font-size: 11.5px; font-weight: 700; color: #FFFFFF;
      white-space: nowrap; overflow: hidden; text-overflow: ellipsis; margin-top: 2px;
    }
    .app-meta-tag {
      font-size: 10px; color: #9CA3AF; text-align: center; font-weight: 600;
    }

    /* Right Main Layout */
    .desktop-main {
      flex: 1;
      display: flex; flex-direction: column;
      overflow: hidden;
      background: var(--bg-canvas);
    }

    /* Top Executive Utilities Bar */
    .desktop-topbar {
      height: 52px; min-height: 52px;
      background: #FFFFFF;
      border-bottom: 1.5px solid #EADBC8;
      display: flex; align-items: center; justify-content: space-between;
      padding: 0 20px;
      box-shadow: 0 2px 8px rgba(46,28,16,0.03);
      z-index: 90;
    }
    .topbar-title {
      font-family: 'Cinzel', serif; font-size: 16px; font-weight: 900;
      letter-spacing: 1px; color: #7C2D12;
      display: flex; align-items: center; gap: 8px;
    }
    .topbar-controls {
      display: flex; align-items: center; gap: 8px;
    }

    .status-pill {
      font-size: 11px; font-weight: 700; color: #166534; background: #DCFCE7;
      padding: 4px 10px; border-radius: 20px; border: 1px solid #BBF7D0;
      display: flex; align-items: center; gap: 4px;
    }
    .control-pill {
      display: flex; background: #F4ECE1; border: 1px solid #EADBC8;
      border-radius: 8px; padding: 2px;
    }
    .control-btn {
      background: transparent; border: none; padding: 5px 10px;
      font-size: 11px; font-weight: 700; color: #6B4D36; border-radius: 6px; cursor: pointer;
    }
    .control-btn.active {
      background: #FFFFFF; color: #7C2D12; box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }

    .btn-action-top {
      background: linear-gradient(135deg, #15803D 0%, #166534 100%);
      color: #FFFFFF; border: 1px solid #86EFAC; border-radius: 6px;
      padding: 5px 11px; font-size: 11.5px; font-weight: 700; cursor: pointer;
      display: flex; align-items: center; gap: 5px;
    }
    .btn-action-top:hover { filter: brightness(1.1); }
    .btn-lock {
      background: transparent; color: #9A3412; border: 1px solid #EADBC8;
      border-radius: 6px; padding: 5px 10px; font-size: 11.5px; font-weight: 700; cursor: pointer;
    }
    .btn-lock:hover { background: #FEE2E2; color: #991B1B; border-color: #FCA5A5; }

    /* Viewport Container (Where the 8 Views Render) */
    .desktop-viewport {
      flex: 1;
      overflow-y: auto;
      overflow-x: hidden;
      padding: 20px 24px;
      position: relative;
      scroll-behavior: smooth;
      -webkit-overflow-scrolling: touch;
      overscroll-behavior-y: contain;
    }

    .view-pane {
      display: none;
      animation: fadeIn 0.2s ease-in-out;
    }
    .view-pane.active {
      display: block;
    }
    @keyframes fadeIn {
      from { opacity: 0; transform: translateY(4px); }
      to { opacity: 1; transform: translateY(0); }
    }

    /* Common Card & Component Styling */
    .glass-card {
      background: var(--bg-card);
      border: 1.5px solid var(--border-gold);
      border-radius: 12px;
      box-shadow: 0 4px 16px -2px rgba(46, 28, 16, 0.04);
      padding: 16px 20px;
      margin-bottom: 16px;
      color: var(--text-main);
    }
    .card-header {
      font-size: 13.5px; font-weight: 800; color: #7C2D12;
      text-transform: uppercase; letter-spacing: 0.8px;
      margin-bottom: 12px; border-bottom: 1.5px solid #EADBC8;
      padding-bottom: 8px; display: flex; justify-content: space-between; align-items: center;
    }
    .card-header .badge {
      font-size: 11px; font-weight: 700; background: #FEF3C7; color: #78350F;
      padding: 2px 8px; border-radius: 4px; border: 1px solid #FDE68A;
    }

    /* Form Styles */
    .form-grid {
      display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 12px; margin-bottom: 14px;
    }
    .form-group { display: flex; flex-direction: column; gap: 4px; }
    .form-group label {
      font-size: 11px; font-weight: 700; color: #7C2D12;
    }
    .form-group input, .form-group select, .form-group textarea {
      height: 38px; background: #FFFFFF; border: 1.5px solid #EADBC8;
      border-radius: 8px; padding: 0 10px; font-size: 12.5px; font-weight: 600; color: #2E1C10;
      transition: border-color 0.2s;
    }
    .form-group textarea { height: 60px; padding: 8px 10px; resize: vertical; }
    .form-group input:focus, .form-group select:focus, .form-group textarea:focus {
      outline: none; border-color: #C2540A; box-shadow: 0 0 0 3px rgba(194,84,10,0.12);
    }

    /* City Autocomplete Dropdown */
    .city-wrap { position: relative; }
    .city-dropdown {
      position: absolute; top: 100%; left: 0; right: 0;
      background: #FFFFFF; border: 1.5px solid #EADBC8; border-radius: 8px;
      max-height: 220px; overflow-y: auto; z-index: 1000;
      display: none; box-shadow: 0 8px 24px rgba(46,28,16,0.12);
    }
    .city-opt {
      padding: 8px 12px; font-size: 12px; font-weight: 600; color: #2E1C10;
      cursor: pointer; border-bottom: 1px solid #F3EDE4;
    }
    .city-opt:hover { background: #FFFDF9; color: #7C2D12; }
    .city-opt strong { color: #C2540A; }

    /* Tables */
    .dash-table, .crm-table {
      width: 100%; border-collapse: separate; border-spacing: 0;
      background: #FFFFFF; border: 1.5px solid #EADBC8; border-radius: 10px;
      overflow: hidden; font-size: 12px; color: #2E1C10;
    }
    .dash-table th, .crm-table th {
      background: linear-gradient(135deg, #7C2D12 0%, #451A03 100%);
      color: #FFFFFF; padding: 9px 10px; font-weight: 800; text-align: center;
      border-bottom: 1.5px solid #EADBC8; font-size: 11.5px;
    }
    .dash-table td, .crm-table td {
      padding: 8px 10px; border-bottom: 1px solid #F3EDE4; text-align: center;
    }
    .dash-table tr:hover td, .crm-table tr:hover td {
      background: #FFFDF9;
    }

    /* Action Buttons */
    .btn-primary-gradient {
      background: linear-gradient(135deg, #E48800 0%, #C2540A 100%);
      color: #FFFFFF; font-size: 13px; font-weight: 800; border: none; border-radius: 8px;
      padding: 10px 20px; cursor: pointer; transition: all 0.2s;
      display: inline-flex; align-items: center; gap: 8px;
      box-shadow: 0 3px 10px rgba(194,84,10,0.25);
    }
    .btn-primary-gradient:hover {
      transform: translateY(-1px); box-shadow: 0 5px 14px rgba(194,84,10,0.35);
    }
    .btn-secondary-outline {
      background: #FFFFFF; color: #7C2D12; font-size: 12.5px; font-weight: 700;
      border: 1.5px solid #EADBC8; border-radius: 8px; padding: 9px 16px; cursor: pointer;
      display: inline-flex; align-items: center; gap: 6px;
    }
    .btn-secondary-outline:hover {
      background: #FFFDF9; border-color: #C2540A; color: #C2540A;
    }
    .btn-table-action {
      background: #FFFDF9; border: 1px solid #EADBC8; border-radius: 6px;
      padding: 4px 8px; font-size: 11px; font-weight: 700; color: #7C2D12; cursor: pointer;
      display: inline-flex; align-items: center; gap: 4px;
    }
    .btn-table-action:hover { background: #FEF3C7; border-color: #FDE68A; color: #78350F; }
    .btn-table-del {
      background: #FFFDF9; border: 1px solid #FCA5A5; border-radius: 6px;
      padding: 4px 8px; font-size: 11px; font-weight: 700; color: #991B1B; cursor: pointer;
    }
    .btn-table-del:hover { background: #FEE2E2; }

    /* Dashboard Metric Cards */
    .metrics-grid {
      display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin-bottom: 18px;
    }
    .metric-card {
      background: #FFFFFF; border: 1.5px solid #EADBC8; border-radius: 12px;
      padding: 16px; box-shadow: 0 2px 8px rgba(46,28,16,0.03);
      display: flex; align-items: center; gap: 14px;
    }
    .metric-icon-box {
      width: 46px; height: 46px; border-radius: 10px;
      background: #FEF3C7; color: #B45309;
      display: flex; align-items: center; justify-content: center;
      font-size: 22px; flex-shrink: 0;
    }
    .metric-data .val { font-size: 20px; font-weight: 900; color: #7C2D12; }
    .metric-data .lbl { font-size: 11px; font-weight: 600; color: #574032; margin-top: 1px; }

    /* Quick Actions Strip */
    .quick-actions-bar {
      display: flex; gap: 10px; margin-bottom: 18px; flex-wrap: wrap;
    }
    .btn-quick-act {
      background: #FFFFFF; border: 1.5px solid #EADBC8; border-radius: 8px;
      padding: 8px 16px; font-size: 12px; font-weight: 700; color: #7C2D12;
      cursor: pointer; display: flex; align-items: center; gap: 7px;
      box-shadow: 0 1px 4px rgba(46,28,16,0.02);
      transition: all 0.2s;
    }
    .btn-quick-act:hover {
      background: #FFFDF9; border-color: #C2540A; transform: translateY(-1px);
    }

    /* Workspace Birth-Time Adjustment Strip */
    .time-adjust-strip {
      background: #FFFFFF; border: 1.5px solid #EADBC8; border-radius: 10px;
      padding: 10px 16px; margin-bottom: 16px;
      display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px;
      box-shadow: 0 2px 8px rgba(46,28,16,0.03);
    }
    .adjust-controls {
      display: flex; align-items: center; gap: 6px;
    }
    .btn-time-step {
      background: #FAF6F0; border: 1.5px solid #EADBC8; border-radius: 6px;
      padding: 5px 10px; font-size: 11.5px; font-weight: 800; color: #7C2D12; cursor: pointer;
    }
    .btn-time-step:hover { background: #FEF3C7; border-color: #FDE68A; color: #78350F; }
    .time-readout-box {
      background: #7C2D12; color: #FEF08A; border: 1.5px solid #451A03;
      border-radius: 6px; padding: 5px 14px; font-family: monospace; font-size: 14px; font-weight: 800;
      letter-spacing: 1px;
    }
    .btn-time-recalc {
      background: linear-gradient(135deg, #15803D 0%, #166534 100%);
      color: #FFFFFF; border: 1px solid #86EFAC; border-radius: 6px;
      padding: 6px 14px; font-size: 11.5px; font-weight: 800; cursor: pointer;
    }
    .btn-time-recalc:hover { filter: brightness(1.1); }

    /* Interactive Workspace Charts Grid */
    .charts-grid {
      display: grid; grid-template-columns: repeat(2, 1fr); gap: 14px; margin-bottom: 16px;
    }
    .chart-box {
      background: #FFFFFF; border: 1.5px solid #EADBC8; border-radius: 12px;
      padding: 14px; text-align: center; box-shadow: 0 2px 8px rgba(46,28,16,0.03);
    }
    .chart-box-header {
      display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;
      border-bottom: 1px solid #F3EDE4; padding-bottom: 6px;
    }
    .chart-box-header strong { font-size: 13px; color: #7C2D12; font-weight: 800; }
    .svg-wrapper { display: flex; justify-content: center; align-items: center; min-height: 290px; }

    /* Divisional Chart Dropdown */
    .divisional-select {
      background: #FFFDF9; border: 1.5px solid #EADBC8; border-radius: 6px;
      padding: 4px 8px; font-size: 11.5px; font-weight: 700; color: #7C2D12;
    }

    /* Workspace Stats Row */
    .workspace-stats-strip {
      display: grid; grid-template-columns: repeat(5, 1fr); gap: 10px; margin-bottom: 14px;
    }
    .stat-pill-card {
      background: #FFFFFF; border: 1.5px solid #EADBC8; border-radius: 8px;
      padding: 8px 12px; text-align: center;
    }
    .stat-pill-card .lbl { font-size: 10px; font-weight: 700; color: #574032; text-transform: uppercase; }
    .stat-pill-card .val { font-size: 13px; font-weight: 800; color: #7C2D12; margin-top: 2px; }

    /* Doshas & Remedies Grid */
    .doshas-grid {
      display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 12px; margin-top: 10px;
    }
    .dosha-card {
      background: #FFFFFF; border: 1.5px solid #EADBC8; border-radius: 10px;
      padding: 14px; box-shadow: 0 1px 4px rgba(46,28,16,0.03);
    }
    .dosha-head { font-size: 13px; font-weight: 800; color: #7C2D12; margin-bottom: 4px; display: flex; justify-content: space-between; align-items: center; }
    .dosha-desc { font-size: 11.5px; color: #2E1C10; line-height: 1.5; font-weight: 500; margin: 6px 0; }
    .remedy-pill {
      font-size: 11px; color: #166534; background: #F0FDF4; border: 1px solid #BBF7D0;
      border-radius: 6px; padding: 6px 10px; margin-top: 8px; font-weight: 600;
    }

    /* Filmora-Style Fullscreen Luxury Modal */
    #loadingModal {
      position: fixed; inset: 0; background: rgba(23, 10, 3, 0.88);
      z-index: 10000; display: none; align-items: center; justify-content: center;
      backdrop-filter: blur(6px);
      pointer-events: none;
    }
    .modal-content-box {
      background: #24140B; border: 2px solid #D4AF37; border-radius: 18px;
      padding: 32px 40px; text-align: center; width: 480px; max-width: 90%;
      box-shadow: 0 25px 60px rgba(0,0,0,0.6); color: #FFFDF9;
    }
    .chakra-spinner {
      font-size: 48px; color: #E48800; line-height: 1; margin-bottom: 12px;
      display: inline-block; animation: spinChakra 4s linear infinite;
    }
    @keyframes spinChakra { 100% { transform: rotate(360deg); } }
    .progress-bar-wrap {
      width: 100%; height: 9px; background: rgba(255,255,255,0.1);
      border-radius: 10px; overflow: hidden; margin: 16px 0 12px 0; border: 1px solid rgba(212,175,55,0.3);
    }
    .progress-bar-fill {
      height: 100%; width: 10%; background: linear-gradient(90deg, #E48800 0%, #FDE047 100%);
      transition: width 0.3s ease;
    }

    /* Live PDF Preview Iframe */
    #reportFrame {
      width: 100%; height: 680px; border: 1.5px solid #EADBC8;
      border-radius: 10px; background: #FFFFFF;
    }
      @keyframes spinMandala {
      from { transform: rotate(0deg); }
      to { transform: rotate(360deg); }
    }
  
    /* ========================================================= */
    /* 📱 PRO MOBILE & TABLET APPLICATION ARCHITECTURE (ZERO OVERFLOW) */
    /* ========================================================= */
    *, *::before, *::after {
      box-sizing: border-box;
    }

    html, body {
      width: 100% !important;
      max-width: 100vw !important;
      overflow-x: hidden !important;
      position: relative !important;
      margin: 0 !important;
      padding: 0 !important;
      -webkit-text-size-adjust: 100%;
    }

    .desktop-app {
      width: 100% !important;
      max-width: 100vw !important;
      min-height: 100vh !important;
      min-height: 100dvh !important;
      overflow-x: hidden !important;
      position: relative !important;
    }

    .desktop-main {
      width: 100% !important;
      max-width: 100vw !important;
      min-width: 0 !important;
      flex: 1 !important;
      overflow-x: hidden !important;
      display: flex !important;
      flex-direction: column !important;
    }

    .desktop-content-area {
      width: 100% !important;
      max-width: 100vw !important;
      box-sizing: border-box !important;
      overflow-x: hidden !important;
      min-width: 0 !important;
    }

    .view-pane {
      width: 100% !important;
      max-width: 100% !important;
      box-sizing: border-box !important;
      min-width: 0 !important;
      overflow-x: hidden !important;
    }

    .mobile-menu-btn {
      display: none;
      background: #F4ECE1;
      border: 1.5px solid #D9C3AB;
      font-size: 20px;
      color: #7C2D12;
      cursor: pointer;
      width: 36px;
      height: 36px;
      border-radius: 8px;
      align-items: center;
      justify-content: center;
      line-height: 1;
      margin-right: 6px;
      flex-shrink: 0;
      touch-action: manipulation;
    }

    .mobile-sidebar-close {
      display: none;
      background: rgba(255,255,255,0.15);
      border: 1px solid rgba(255,255,255,0.25);
      color: #FEF08A;
      font-size: 18px;
      width: 32px;
      height: 32px;
      border-radius: 8px;
      cursor: pointer;
      margin-left: auto;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
      touch-action: manipulation;
    }

    .sidebar-backdrop {
      display: none;
      position: fixed;
      inset: 0;
      background: rgba(0,0,0,0.65);
      backdrop-filter: blur(4px);
      -webkit-backdrop-filter: blur(4px);
      z-index: 998;
      touch-action: manipulation;
    }
    .sidebar-backdrop.open {
      display: block;
    }

    .deity-cards-wrapper {
      display: grid;
      grid-template-columns: repeat(5, 1fr);
      gap: 12px;
      text-align: center;
      width: 100%;
      box-sizing: border-box;
    }

    /* Native-Style Mobile Bottom Navigation Dock */
    .mobile-bottom-bar {
      display: none;
      position: fixed;
      bottom: 0;
      left: 0;
      right: 0;
      height: 60px;
      height: calc(60px + env(safe-area-inset-bottom, 0px));
      padding-bottom: env(safe-area-inset-bottom, 0px);
      background: rgba(28, 16, 9, 0.98);
      backdrop-filter: blur(14px);
      -webkit-backdrop-filter: blur(14px);
      border-top: 1.5px solid rgba(212, 175, 55, 0.35);
      z-index: 990;
      justify-content: space-around;
      align-items: center;
      box-shadow: 0 -4px 20px rgba(0, 0, 0, 0.45);
    }
    .mob-tab-btn {
      flex: 1;
      height: 100%;
      background: transparent;
      border: none;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      gap: 3px;
      color: #D1C7BD;
      cursor: pointer;
      padding: 4px 2px;
      transition: all 0.2s ease;
      touch-action: manipulation;
    }
    .mob-tab-btn .mob-icon {
      font-size: 19px;
      line-height: 1;
      transition: transform 0.2s ease;
    }
    .mob-tab-btn .mob-label {
      font-size: 10px;
      font-weight: 700;
      letter-spacing: 0.3px;
      line-height: 1;
    }
    .mob-tab-btn.active {
      color: #FEF08A;
    }
    .mob-tab-btn.active .mob-icon {
      transform: translateY(-2px) scale(1.1);
      filter: drop-shadow(0 2px 6px rgba(212, 175, 55, 0.6));
    }
    .mob-tab-btn.active .mob-label {
      color: #D4AF37;
      font-weight: 800;
    }

    /* ========================================================= */
    /* RESPONSIVE TABLETS & IPADS (<= 1024px)                     */
    /* ========================================================= */
    @media (max-width: 1024px) {
      .mobile-menu-btn {
        display: inline-flex !important;
      }
      .mobile-sidebar-close {
        display: inline-flex !important;
      }
      .desktop-sidebar {
        position: fixed !important;
        top: 0 !important;
        left: -320px !important;
        width: 280px !important;
        min-width: 280px !important;
        height: 100vh !important;
        height: 100dvh !important;
        z-index: 1000 !important;
        transition: left 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        overflow-y: auto !important;
        -webkit-overflow-scrolling: touch !important;
      }
      .desktop-sidebar.open {
        left: 0 !important;
        box-shadow: 10px 0 35px rgba(0,0,0,0.6) !important;
      }
      .desktop-topbar {
        padding: 0 12px !important;
      }
      .status-pill {
        display: none !important;
      }
      .btn-lock {
        display: none !important;
      }
    }

    /* ========================================================= */
    /* RESPONSIVE MOBILE PHONES (<= 768px)                       */
    /* ========================================================= */
    @media (max-width: 768px) {
      .mobile-bottom-bar {
        display: flex !important;
      }

      .desktop-topbar {
        height: 52px !important;
        min-height: 52px !important;
        padding: 0 10px !important;
        width: 100% !important;
        max-width: 100vw !important;
        overflow: hidden !important;
        display: flex !important;
        align-items: center !important;
        justify-content: space-between !important;
        background: linear-gradient(180deg, #FFFFFF 0%, #FAF6F0 100%) !important;
        border-bottom: 1.5px solid #EADBC8 !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06) !important;
      }
      .mobile-menu-btn {
        width: 34px !important;
        height: 34px !important;
        border-radius: 8px !important;
        background: #F5EFEB !important;
        border: 1px solid #EADBC8 !important;
        color: #7C2D12 !important;
        font-size: 16px !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        flex-shrink: 0 !important;
      }
      .topbar-title {
        font-size: 13.5px !important;
        font-weight: 800 !important;
        color: #7C2D12 !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        flex: 1 !important;
        margin: 0 6px !important;
        letter-spacing: 0.2px !important;
      }
      .topbar-controls {
        gap: 5px !important;
        flex-shrink: 0 !important;
        display: flex !important;
        align-items: center !important;
      }
      /* Hide redundant chart style pills in mobile topbar */
      .control-pill[title="Chart Style"] {
        display: none !important;
      }
      .control-pill[title="Report Language"] {
        padding: 2px !important;
        background: #F0E5D8 !important;
        border-radius: 6px !important;
      }
      .control-pill[title="Report Language"] .control-btn {
        padding: 3px 6px !important;
        font-size: 10.5px !important;
        font-weight: 700 !important;
      }
      .control-pill[title="Report Language"] #lang_both {
        display: none !important;
      }
      .btn-action-top {
        padding: 4px 8px !important;
        font-size: 11px !important;
        border-radius: 6px !important;
      }
      .btn-lock {
        display: none !important;
      }

      /* Full hardware-accelerated touch momentum scrolling with 140px clearance */
      .desktop-viewport {
        padding: 10px 10px 140px 10px !important;
        overflow-y: auto !important;
        overflow-x: hidden !important;
        -webkit-overflow-scrolling: touch !important;
        overscroll-behavior-y: contain !important;
        scroll-behavior: smooth !important;
        width: 100% !important;
        box-sizing: border-box !important;
      }
      .view-pane {
        padding-bottom: 40px !important;
        box-sizing: border-box !important;
      }

      /* Form Action Buttons: Stack vertically on mobile so none get squeezed or cut */
      #pane_new_kundli div[style*="display:flex; gap:12px; align-items:center"] {
        display: flex !important;
        flex-direction: column !important;
        width: 100% !important;
        gap: 10px !important;
        margin-top: 14px !important;
        margin-bottom: 24px !important;
      }
      #pane_new_kundli .btn-primary-gradient,
      #pane_new_kundli .btn-secondary-outline {
        width: 100% !important;
        padding: 12px 14px !important;
        font-size: 13.5px !important;
        text-align: center !important;
        justify-content: center !important;
        box-sizing: border-box !important;
      }

      /* 5 Deities Touch Swipe Carousel */
      .deity-cards-wrapper {
        display: flex !important;
        flex-wrap: nowrap !important;
        overflow-x: auto !important;
        scroll-snap-type: x mandatory !important;
        gap: 10px !important;
        padding: 2px 2px 10px 2px !important;
        width: 100% !important;
        box-sizing: border-box !important;
        -webkit-overflow-scrolling: touch !important;
        scrollbar-width: none !important;
      }
      .deity-cards-wrapper::-webkit-scrollbar {
        display: none !important;
      }
      .deity-cards-wrapper > div {
        flex: 0 0 125px !important;
        width: 125px !important;
        min-width: 125px !important;
        max-width: 125px !important;
        scroll-snap-align: start !important;
        box-sizing: border-box !important;
      }

      /* Metrics 2x2 Grid */
      .metrics-grid {
        display: grid !important;
        grid-template-columns: repeat(2, 1fr) !important;
        gap: 8px !important;
        width: 100% !important;
        box-sizing: border-box !important;
      }
      .metric-card {
        padding: 10px 8px !important;
        gap: 8px !important;
        min-width: 0 !important;
      }
      .metric-icon-box {
        width: 36px !important;
        height: 36px !important;
        font-size: 17px !important;
      }
      .metric-data .val {
        font-size: 19px !important;
      }
      .metric-data .lbl {
        font-size: 9.5px !important;
      }

      /* Quick Actions 2-Column Responsive Grid */
      .quick-actions-bar {
        display: grid !important;
        grid-template-columns: repeat(2, 1fr) !important;
        gap: 8px !important;
        width: 100% !important;
        box-sizing: border-box !important;
      }
      .btn-quick-act {
        width: 100% !important;
        box-sizing: border-box !important;
        text-align: center !important;
        justify-content: center !important;
        font-size: 11px !important;
        padding: 9px 4px !important;
        line-height: 1.25 !important;
        white-space: normal !important;
        min-height: 42px !important;
      }

      /* Glass Cards Zero-Overflow */
      .glass-card {
        width: 100% !important;
        max-width: 100% !important;
        box-sizing: border-box !important;
        padding: 14px 10px !important;
        margin-bottom: 12px !important;
        border-radius: 12px !important;
        overflow: hidden !important;
      }
      .card-header {
        display: flex !important;
        flex-direction: column !important;
        align-items: flex-start !important;
        gap: 8px !important;
        width: 100% !important;
      }

      /* Force ALL Desktop Multi-Column Grids into 1 Column on Mobile */
      .grid, .form-grid, .two-col,
      [style*="grid-template-columns: 1fr 1fr"],
      [style*="grid-template-columns: 1.1fr 1fr"],
      [style*="grid-template-columns: 1fr 1.5fr"],
      [style*="grid-template-columns: 2fr 1fr 1fr 1fr"],
      [style*="grid-template-columns: 1fr 1.5fr 1.5fr 2fr"],
      [style*="grid-template-columns: repeat(6, 1fr)"],
      [style*="grid-template-columns: repeat(5, 1fr)"],
      [style*="grid-template-columns: repeat(auto-fit"],
      [style*="grid-template-columns: repeat(auto-fill"] {
        display: flex !important;
        flex-direction: column !important;
        width: 100% !important;
        gap: 12px !important;
        box-sizing: border-box !important;
      }

      /* Workspace Stats: 2x2 Clean Grid */
      .workspace-stats-strip {
        display: grid !important;
        grid-template-columns: repeat(2, 1fr) !important;
        gap: 8px !important;
        width: 100% !important;
        box-sizing: border-box !important;
      }
      .stat-pill-card {
        min-width: 0 !important;
        padding: 8px 6px !important;
        box-sizing: border-box !important;
      }
      .stat-pill-card .val {
        font-size: 12px !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
        white-space: nowrap !important;
      }

      /* Workspace Time Rectification Box */
      .time-adjust-strip {
        display: flex !important;
        flex-direction: column !important;
        align-items: stretch !important;
        gap: 10px !important;
        width: 100% !important;
        box-sizing: border-box !important;
        padding: 10px !important;
      }
      .adjust-controls {
        display: grid !important;
        grid-template-columns: repeat(4, 1fr) !important;
        gap: 6px !important;
        width: 100% !important;
        box-sizing: border-box !important;
      }
      .btn-time-step {
        padding: 6px 2px !important;
        font-size: 11px !important;
        width: 100% !important;
        text-align: center !important;
      }
      .time-readout-box {
        grid-column: span 2 !important;
        width: 100% !important;
        text-align: center !important;
      }
      .btn-time-recalc {
        grid-column: span 2 !important;
        width: 100% !important;
        padding: 8px 4px !important;
        font-size: 12px !important;
      }

      /* Kundli Charts Grid: Vertical Stacked 100% Width */
      .charts-grid {
        display: flex !important;
        flex-direction: column !important;
        width: 100% !important;
        gap: 14px !important;
        box-sizing: border-box !important;
      }
      .chart-box {
        width: 100% !important;
        max-width: 100% !important;
        min-width: 0 !important;
        box-sizing: border-box !important;
        padding: 12px 8px !important;
      }
      .chart-box-header {
        flex-wrap: wrap !important;
        gap: 6px !important;
      }
      .svg-wrapper {
        width: 100% !important;
        max-width: 100% !important;
        overflow: hidden !important;
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        min-height: auto !important;
      }
      .svg-wrapper svg, .kundli-svg {
        width: 100% !important;
        max-width: 320px !important;
        height: auto !important;
      }

      /* Kundli Milan Groom & Bride Boxes */
      #pane_milan .glass-card > div[style*="grid-template-columns"] {
        display: flex !important;
        flex-direction: column !important;
        width: 100% !important;
        gap: 12px !important;
      }
      #pane_milan .form-grid {
        display: grid !important;
        grid-template-columns: repeat(2, 1fr) !important;
        gap: 8px !important;
        width: 100% !important;
      }
      #pane_milan .form-group[style*="grid-column: span 2"] {
        grid-column: span 2 !important;
        width: 100% !important;
      }

      /* Form Controls iOS Safari 16px to prevent auto-zoom */
      .form-group, input, select, textarea {
        max-width: 100% !important;
        width: 100% !important;
        box-sizing: border-box !important;
        font-size: 15px !important;
        min-height: 42px !important;
      }

      /* Horizontal Scrollable Table Containers (No Page Jump) */
      [style*="overflow-x:auto"], .table-responsive {
        width: 100% !important;
        max-width: 100% !important;
        overflow-x: auto !important;
        -webkit-overflow-scrolling: touch !important;
        display: block !important;
        box-sizing: border-box !important;
      }
      table {
        min-width: 480px !important;
        width: 100% !important;
      }

      /* Mobile Login Gateway */
      #vedasLoginGateway > div {
        width: 95% !important;
        max-width: 95% !important;
        padding: 20px 14px !important;
        margin: 10px auto !important;
        max-height: 92vh !important;
        overflow-y: auto !important;
        border-radius: 14px !important;
      }
    }


    /* 🌟 COSMIC SACRED LANGUAGE TRANSITION ANIMATION */
    @keyframes cosmicAuraGlow {
      0% {
        opacity: 0.85;
        transform: scale(0.995);
        filter: brightness(1.18) drop-shadow(0 0 25px rgba(212,175,55,0.5));
      }
      50% {
        opacity: 1;
        transform: scale(1.002);
        filter: brightness(1.06) drop-shadow(0 0 12px rgba(194,65,12,0.25));
      }
      100% {
        opacity: 1;
        transform: scale(1);
        filter: brightness(1) drop-shadow(0 0 0 rgba(0,0,0,0));
      }
    }

    .cosmic-lang-transition {
      animation: cosmicAuraGlow 0.45s cubic-bezier(0.16, 1, 0.3, 1) forwards !important;
    }

    /* 🕉️ FLOATING SACRED TOAST */
    #langSwitchToast {
      position: fixed;
      top: 18px;
      left: 50%;
      transform: translateX(-50%) translateY(-30px);
      z-index: 999999;
      background: linear-gradient(135deg, #7C2D12 0%, #9A3412 50%, #B45309 100%);
      color: #FEF3C7;
      padding: 10px 24px;
      border-radius: 30px;
      border: 1.5px solid #FDE68A;
      box-shadow: 0 10px 35px rgba(124, 45, 18, 0.45), 0 0 20px rgba(253, 224, 71, 0.35);
      font-weight: 800;
      font-size: 13.5px;
      display: none;
      align-items: center;
      gap: 12px;
      pointer-events: none;
      transition: all 0.35s cubic-bezier(0.16, 1, 0.3, 1);
      letter-spacing: 0.3px;
    }

    #langSwitchToast.toast-visible {
      display: flex !important;
      transform: translateX(-50%) translateY(0) !important;
      opacity: 1 !important;
    }

    @keyframes spinChakra {
      from { transform: rotate(0deg); }
      to { transform: rotate(360deg); }
    }
  </style>

</head>
<body>
  <!-- =============================================================== -->
  <!-- GRAND VEDIC DESKTOP SPLASH SCREEN -->
  <!-- =============================================================== -->
  <div id="vedasSplashScreen" onclick="dismissSplashScreen()" title="Click to enter Dashboard" style="cursor:pointer; 
    position: fixed; inset: 0; z-index: 999999;
    background: radial-gradient(circle at center, #2E1609 0%, #150A04 60%, #0A0502 100%);
    display: flex; flex-direction: column; align-items: center; justify-content: center;
    color: #FAF6F0; user-select: none; transition: opacity 0.6s cubic-bezier(0.16, 1, 0.3, 1), visibility 0.6s;
  ">
    <!-- Sacred Gayatri & Shloka Top Inscription -->
    <div style="font-size: 13px; font-weight: 700; color: #D4AF37; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 18px; opacity: 0.9; text-shadow: 0 0 12px rgba(212,175,55,0.4); text-align: center; padding: 0 20px;">
      ॐ भूर्भुवः स्वः तत्सवितुर्वरेण्यं भर्गो देवस्य धीमहि धियो यो नः प्रचोदयात् ॐ
    </div>

    <!-- Central Glowing Emblem Container -->
    <div style="position: relative; width: 140px; height: 140px; margin-bottom: 20px; display: flex; align-items: center; justify-content: center;">
      <!-- Glowing Outer Mandala Ring -->
      <div style="position: absolute; inset: -14px; border-radius: 50%; border: 2px dashed #D4AF37; opacity: 0.6; animation: spinMandala 20s linear infinite;"></div>
      <!-- Golden Glow Behind Ganesha -->
      <div style="position: absolute; inset: 0; border-radius: 50%; background: radial-gradient(circle, rgba(217,119,6,0.6) 0%, rgba(217,119,6,0) 70%); filter: blur(12px);"></div>
      <!-- Deity Emblem (Ganesha Image) -->
      <img src="/assets/gods/ganesha.png" alt="Shree Ganesha" style="width: 120px; height: 120px; object-fit: cover; border-radius: 50%; border: 3px solid #D4AF37; box-shadow: 0 0 30px rgba(212,175,55,0.5); position: relative; z-index: 2;"/>
    </div>

    <!-- Sacred Invocation Title -->
    <div style="font-size: 14px; font-weight: 800; color: #F59E0B; letter-spacing: 3px; margin-bottom: 6px;">
      ॥ श्री गणेशाय नमः • ॐ नमः शिवाय ॥
    </div>

    <!-- App Title with Embossed Gold Gradient -->
    <h1 style="
      font-family: 'Cinzel', serif; font-size: 32px; font-weight: 900; letter-spacing: 3px; margin: 0 0 8px 0;
      background: linear-gradient(135deg, #FFFBEB 0%, #FDE68A 30%, #D4AF37 70%, #92400E 100%);
      -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-shadow: 0 2px 20px rgba(212,175,55,0.3); text-align: center;
    ">
      SHIVANSH ASTRO-VASTU PROFESSIONAL
    </h1>
    <div style="font-size: 12px; color: #D1D5DB; letter-spacing: 2.5px; text-transform: uppercase; margin-bottom: 24px; text-align: center;">
      Vedic Astrology • Krishnamurti Paddhati (KP) • Lal Kitab 1952 Suite
    </div>

    <!-- 5 Sacred Deities Horizontal Preview -->
    <div style="display: flex; gap: 14px; margin-bottom: 24px;">
      <div title="Lord Ganesha - विघ्नहर्ता" style="text-align: center;">
        <img src="/assets/gods/ganesha.png" style="width: 48px; height: 48px; object-fit: cover; border-radius: 50%; border: 1.5px solid #D4AF37; box-shadow: 0 0 10px rgba(212,175,55,0.3);"/>
        <div style="font-size: 10px; color: #FDE68A; margin-top: 4px; font-weight: 700;">गणेश</div>
      </div>
      <div title="Lord Shiva - महादेव" style="text-align: center;">
        <img src="/assets/gods/shiva.png" style="width: 48px; height: 48px; object-fit: cover; border-radius: 50%; border: 1.5px solid #D4AF37; box-shadow: 0 0 10px rgba(212,175,55,0.3);"/>
        <div style="font-size: 10px; color: #FDE68A; margin-top: 4px; font-weight: 700;">शिव</div>
      </div>
      <div title="Maa Durga - भगवती" style="text-align: center;">
        <img src="/assets/gods/durga.png" style="width: 48px; height: 48px; object-fit: cover; border-radius: 50%; border: 1.5px solid #D4AF37; box-shadow: 0 0 10px rgba(212,175,55,0.3);"/>
        <div style="font-size: 10px; color: #FDE68A; margin-top: 4px; font-weight: 700;">दुर्गा</div>
      </div>
      <div title="Surya Dev - सूर्य नारायण" style="text-align: center;">
        <img src="/assets/gods/surya.png" style="width: 48px; height: 48px; object-fit: cover; border-radius: 50%; border: 1.5px solid #D4AF37; box-shadow: 0 0 10px rgba(212,175,55,0.3);"/>
        <div style="font-size: 10px; color: #FDE68A; margin-top: 4px; font-weight: 700;">सूर्य</div>
      </div>
      <div title="Hanuman Ji - संकटमोचन" style="text-align: center;">
        <img src="/assets/gods/hanuman.png" style="width: 48px; height: 48px; object-fit: cover; border-radius: 50%; border: 1.5px solid #D4AF37; box-shadow: 0 0 10px rgba(212,175,55,0.3);"/>
        <div style="font-size: 10px; color: #FDE68A; margin-top: 4px; font-weight: 700;">हनुमान</div>
      </div>
    </div>

    <!-- Progress Bar & Status Text -->
    <div style="width: 380px; max-width: 90vw;">
      <div style="height: 5px; background: rgba(255,255,255,0.12); border-radius: 10px; overflow: hidden; margin-bottom: 10px; border: 1px solid rgba(212,175,55,0.3);">
        <div id="splashProgressBar" style="height: 100%; width: 15%; background: linear-gradient(90deg, #F59E0B, #D4AF37, #FDE68A); border-radius: 10px; transition: width 0.3s ease-out;"></div>
      </div>
      <div id="splashStatusText" style="font-size: 11.5px; color: #FDE68A; font-weight: 600; text-align: center; letter-spacing: 0.5px;">
        ✨ Initializing High-Precision VSOP87 &amp; Lahiri Engine...
      </div>
    </div>

    <!-- Version & Offline Badge -->
    <div style="position: absolute; bottom: 18px; font-size: 11px; color: #9CA3AF; letter-spacing: 1px;">
      Version 2.5 Pro • 100% Offline Standalone Desktop Edition
    </div>
  </div>
  <script>
    function dismissSplashScreen() {
      var s = document.getElementById('vedasSplashScreen');
      if (s && s.style.display !== 'none') {
        s.style.opacity = '0';
        setTimeout(function() { 
          s.style.display = 'none';
          if (typeof checkAuthStatus === 'function') checkAuthStatus();
        }, 500);
      }
    }
    // Hard safety timer: dismiss at max 1.8s regardless of anything
    setTimeout(dismissSplashScreen, 1800);
  </script>

  <!-- =============================================================== -->
  <!-- VEDAS MASTER SECURITY ACCESS / LOGIN GATEWAY -->
  <!-- =============================================================== -->
  <div id="vedasLoginGateway" style="
    position: fixed; inset: 0; z-index: 888888;
    background: radial-gradient(circle at center, rgba(35,18,10,0.97) 0%, rgba(18,9,4,0.98) 100%);
    backdrop-filter: blur(10px);
    display: none; align-items: center; justify-content: center;
    color: #FAF6F0; user-select: none;
  ">
    <div style="
      width: 440px; max-width: 90vw;
      background: linear-gradient(145deg, #FFFDF9 0%, #FAF5EE 100%);
      border: 2px solid #D4AF37; border-radius: 14px; padding: 28px 30px;
      box-shadow: 0 16px 48px rgba(0,0,0,0.6), 0 0 30px rgba(212,175,55,0.25);
      color: #2E1C10; text-align: center;
    ">
      <!-- Divine Ganesha Icon -->
      <div style="margin: 0 auto 12px auto; width: 76px; height: 76px; position: relative;">
        <img src="/assets/gods/ganesha.png" alt="Shree Ganesh" style="width: 76px; height: 76px; object-fit: cover; border-radius: 50%; border: 2.5px solid #D4AF37; box-shadow: 0 0 16px rgba(212,175,55,0.4); display: block;"/>
      </div>

      <div style="font-size: 11px; font-weight: 800; color: #C2540A; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 3px;">
        ॥ श्री गणेशाय नमः ॥
      </div>
      <h2 style="font-family: 'Cinzel', serif; font-size: 20px; font-weight: 900; color: #7C2D12; margin: 0 0 4px 0; letter-spacing: 1px;">
        SHIVANSH ASTRO-VASTU PROFESSIONAL
      </h2>
      <div style="font-size: 11.5px; color: #6B7280; font-weight: 600; margin-bottom: 18px;">
        Master Security Access • Astrologer Login
      </div>

      <!-- Mode Selector Tabs -->
      <div style="display:flex; border-bottom:2px solid #EADBC8; margin-bottom:16px;">
        <button id="gateTabAdmin" type="button" onclick="switchGateMode('admin')" style="flex:1; padding:8px 6px; border:none; background:#FEF3C7; color:#7C2D12; font-weight:800; font-size:12px; cursor:pointer; border-radius:8px 8px 0 0; border:1px solid #D97706; border-bottom:none;">👑 Master Admin</button>
        <button id="gateTabClient" type="button" onclick="switchGateMode('client')" style="flex:1; padding:8px 6px; border:none; background:#FFFDF9; color:#92400E; font-weight:700; font-size:12px; cursor:pointer; border-bottom:1px solid #EADBC8;">🔑 Customer Demo Key</button>
      </div>

      <!-- Client Demo Key Form (Hidden by default) -->
      <div id="gateClientForm" style="display:none; flex-direction:column; gap:12px; text-align:left; margin-bottom:14px;">
        <div>
          <label style="display:block; font-size:11.5px; font-weight:700; color:#7C2D12; margin-bottom:4px;">
            🔑 Enter Demo Access Key (डेमो चाबी दर्ज करें)
          </label>
          <input type="text" id="loginClientKey" placeholder="e.g. VEDAS-CLIENT-7D-XXXX" style="
            width: 100%; box-sizing: border-box; padding: 10px 12px; font-size: 13px; font-weight: 800;
            border: 2px solid #D97706; border-radius: 8px; background: #FFFFFF; color: #7C2D12;
            outline: none; letter-spacing: 0.5px;
          " onkeydown="if(event.key==='Enter') doKeyLogin()"/>
        </div>
        <div id="keyErrorMsg" style="display:none; background:#FEF2F2; border:1.5px solid #FCA5A5; border-radius:8px; padding:8px 12px; color:#991B1B; font-size:11.5px; font-weight:700;"></div>
        <button type="button" onclick="doKeyLogin()" style="
          width: 100%; padding: 12px; font-size: 13.5px; font-weight: 800; color: #FFFFFF;
          background: linear-gradient(135deg, #059669 0%, #047857 100%);
          border: none; border-radius: 8px; cursor: pointer;
          box-shadow: 0 4px 14px rgba(5,150,105,0.35);
        ">
          ✨ Activate Demo Session (डेमो शुरू करें)
        </button>
        <div style="margin-top: 14px; padding: 10px 12px; background: rgba(217,119,6,0.08); border: 1px dashed #D97706; border-radius: 8px; font-size: 11.5px; color: #92400E; text-align: center;">
          🎁 <b>Pre-Activated 30-Day Demo Key:</b><br/>
          <code style="display: inline-block; margin-top: 4px; background: #FFF; border: 1px solid #FCD34D; padding: 4px 10px; border-radius: 6px; font-weight: 800; font-size: 12.5px; color: #7C2D12; cursor: pointer; letter-spacing: 0.5px;" onclick="document.getElementById('inputCustomerKey').value='VEDAS-TRIAL-30D-8F92'; doKeyLogin();" title="Click to auto-fill & login">VEDAS-TRIAL-30D-8F92</code>
          <div style="font-size: 10px; color: #B45309; margin-top: 4px;">(Click key above to 1-click test)</div>
        </div>
      </div>

      <div id="gateAdminForm">

      <!-- Error Banner -->
      <div id="loginErrorMsg" style="display: none; background: #FEF2F2; border: 1.5px solid #FCA5A5; border-radius: 8px; padding: 8px 12px; color: #991B1B; font-size: 12px; font-weight: 700; margin-bottom: 14px;">
        ⚠️ Invalid User ID or Password.
      </div>

      <!-- Success Banner -->
      <div id="loginSuccessMsg" style="display: none; background: #F0FDF4; border: 1.5px solid #86EFAC; border-radius: 8px; padding: 8px 12px; color: #166534; font-size: 12.5px; font-weight: 800; margin-bottom: 14px;">
        ✨ Access Granted • Welcome Astrologer!
      </div>

      <!-- Form Inputs -->
      <div style="text-align: left; margin-bottom: 12px;">
        <label style="display: block; font-size: 11.5px; font-weight: 700; color: #7C2D12; margin-bottom: 4px;">
          👤 Astrologer User ID
        </label>
        <input type="text" id="loginUsername" placeholder="Enter User ID (admin)" value="admin" style="
          width: 100%; box-sizing: border-box; padding: 10px 12px; font-size: 13px; font-weight: 600;
          border: 1.5px solid #EADBC8; border-radius: 8px; background: #FFFFFF; color: #2E1C10;
          outline: none;
        " onkeydown="if(event.key==='Enter') doLogin()"/>
      </div>

      <div style="text-align: left; margin-bottom: 14px;">
        <label style="display: block; font-size: 11.5px; font-weight: 700; color: #7C2D12; margin-bottom: 4px;">
          🔒 Master Security Password
        </label>
        <input type="password" id="loginPassword" placeholder="Enter Password (harman)" style="
          width: 100%; box-sizing: border-box; padding: 10px 12px; font-size: 13px; font-weight: 600;
          border: 1.5px solid #EADBC8; border-radius: 8px; background: #FFFFFF; color: #2E1C10;
          outline: none;
        " onkeydown="if(event.key==='Enter') doLogin()"/>
      </div>

      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 18px; font-size: 11px; color: #4B5563;">
        <label style="display: flex; align-items: center; gap: 6px; cursor: pointer;">
          <input type="checkbox" id="loginRememberMe" checked style="accent-color: #C2540A; cursor: pointer;"/>
          <span>Remember me on this PC</span>
        </label>
        <span style="color: #9A3412; font-weight: 700;">ID: admin | Pass: harman</span>
      </div>

      <!-- Submit Button -->
      <button type="button" onclick="doLogin()" style="
        width: 100%; padding: 12px; font-size: 13.5px; font-weight: 800; color: #FFFFFF;
        background: linear-gradient(135deg, #C2540A 0%, #7C2D12 100%);
        border: none; border-radius: 8px; cursor: pointer;
        box-shadow: 0 4px 14px rgba(194,84,10,0.35);
      ">
        🔑 Access Astrology Suite (प्रवेश करें)
      </button>
      </div>

      <div style="font-size: 10.5px; color: #9CA3AF; margin-top: 14px;">
        Shivansh Astro-Vastu Professional • 100% Offline Standalone Protection
      </div>
    </div>
  </div>

  <!-- Desktop Application Shell -->
  <div class="desktop-app">
  <div id="sidebarBackdrop" class="sidebar-backdrop" onclick="toggleMobileSidebar(false)"></div>
    <!-- Left Navigation Sidebar -->
    <aside class="desktop-sidebar">
      <div>
        <div class="sidebar-brand" style="display:flex; align-items:center; gap:8px;">
          <img src="/assets/images/opt_shivansh_logo.jpg" style="width:42px; height:42px; border-radius:50%; border:2px solid #D4AF37; box-shadow:0 2px 6px rgba(124,45,18,0.3); object-fit:cover;" alt="Shivansh Logo"/>
          <div class="brand-text">
            <div class="title" style="font-size:14px; font-weight:900; letter-spacing:0.5px;">SHIVANSH</div>
            <div class="sub" style="font-size:10px; color:#FDE68A;">Astro-Vastu &amp; Kundli Suite</div>
          </div>
          <button class="mobile-sidebar-close" onclick="toggleMobileSidebar(false)" aria-label="Close Menu">✕</button>
        </div>

        <nav class="sidebar-nav">
          <button class="nav-btn active" id="nav_dashboard" onclick="switchNav('dashboard')">
            <span class="icon">📊</span> डॅशबोर्ड (Dashboard)
          </button>
          <button class="nav-btn" id="nav_new_kundli" onclick="switchNav('new_kundli')">
            <span class="icon">➕</span> नवीन कुंडली (New Kundli)
          </button>
          <button class="nav-btn" id="nav_clients" onclick="switchNav('clients')">
            <span class="icon">👥</span> ग्राहक CRM (Clients)
          </button>
          <button class="nav-btn" id="nav_workspace" onclick="switchNav('workspace')">
            <span class="icon">🪐</span> कुंडली वर्कस्पेस (Charts)
          </button>
          <button class="nav-btn" id="nav_milan" onclick="switchNav('milan')">
            <span class="icon">💍</span> विवाह मिलान (Kundli Milan)
          </button>
          <button class="nav-btn" id="nav_reports" onclick="switchNav('reports')">
            <span class="icon">📄</span> PDF अहवाल स्टुडिओ (Report Studio)
          </button>
          <button class="nav-btn" id="nav_prashna" onclick="switchNav('prashna')">
            <span class="icon">⏱️</span> प्रश्न कुंडली (Prashna Horary)
          </button>
          <button class="nav-btn" id="nav_settings" onclick="switchNav('settings')">
            <span class="icon">⚙️</span> सेटिंग्ज व ब्रँड (Settings & Brand)
          </button>
        </nav>
      </div>

      <div class="sidebar-footer">
        <div class="active-client-badge">
          <div class="lbl">सक्रिय जातक (ACTIVE CLIENT)</div>
          <div class="val" id="sidebarActiveClientName">कोणताही जातक निवडलेला नाही (No Client)</div>
        </div>
        <div class="app-meta-tag">डेस्कटॉप प्रोफेशनल एडिशन • १००% ऑफलाइन</div>
      </div>
    </aside>

    <!-- Right Main Layout -->
    <div class="desktop-main">
      <!-- Top Utilities Bar -->
      <header class="desktop-topbar">
        <button id="mobileMenuBtn" class="mobile-menu-btn" onclick="toggleMobileSidebar()" aria-label="Toggle Navigation">☰</button>
        <div class="topbar-title" id="topbarTitle">
          📊 एक्झिक्युटिव्ह ज्योतिष डॅशबोर्ड (Executive Dashboard)
        </div>

        <div class="topbar-controls">
          <span class="status-pill" id="statusPill">✨ सज्ज • १००% ऑफलाइन</span>

          <!-- Regional Chart Style -->
          <div class="control-pill" title="Chart Style">
            <button class="control-btn active" id="style_north" onclick="setChartStyle('north')">उत्तर (North / उत्तर)</button>
            <button class="control-btn" id="style_south" onclick="setChartStyle('south')">दक्षिण (South / दक्षिण)</button>
            <button class="control-btn" id="style_east" onclick="setChartStyle('east')">पूर्व (East / पूर्व)</button>
          </div>

          <!-- Language Selector -->
          <div class="control-pill" title="Language Switcher (भाषा बदला / भाषा बदलें)">
            <button class="control-btn active" id="lang_mr" onclick="setLang('mr')">मराठी</button>
            <button class="control-btn" id="lang_hi" onclick="setLang('hi')">हिन्दी</button>
            <button class="control-btn" id="lang_en" onclick="setLang('en')">English</button>
          </div>

          <button class="btn-action-top" onclick="shareOnWhatsApp()" title="Share Horoscope via WhatsApp">💬 व्हॉट्सॲप (WhatsApp)</button>
          <button class="btn-lock" onclick="closeDesktopApp()" title="Cleanly close desktop suite">✖ बंद करा (Exit)</button>
        </div>
      </header>

      <!-- Viewport (Switches between the 8 Views) -->
      <main class="desktop-viewport">

        <!-- =============================================================== -->
        <!-- VIEW 1: DASHBOARD -->
        <!-- =============================================================== -->
        <section class="view-pane active" id="pane_dashboard">
        <!-- Auspicious Vedic Deities Blessing Strip -->
        <div class="glass-card" style="padding:14px 18px; margin-bottom:16px; background:linear-gradient(135deg, #FFFDF9 0%, #FAF5EE 100%); border:1.5px solid #EADBC8;">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
            <span style="font-size:13px; font-weight:800; color:#7C2D12;">🕉️ Auspicious Vedic Deities (शुभ देवी-देवता आशीर्वाद व नवग्रह रक्षा)</span>
            <span class="badge" style="background:#FEF3C7; color:#78350F; font-weight:700;">Divine Kundli Blessings</span>
          </div>
          <div class="deity-cards-wrapper">
            <div style="background:#FFFFFF; border:1.5px solid #FDE68A; border-radius:10px; padding:10px; box-shadow:0 2px 8px rgba(212,175,55,0.08);">
              <img src="/assets/gods/ganesha.png" alt="Shree Ganesh" style="width:70px; height:70px; object-fit:cover; border-radius:50%; border:2px solid #D4AF37; margin:0 auto 6px auto; display:block; box-shadow:0 0 10px rgba(212,175,55,0.3);"/>
              <strong style="color:#7C2D12; font-size:12px; display:block;">श्री गणेश (विघ्नहर्ता)</strong>
              <span style="font-size:10.5px; color:#C2540A; font-weight:700;">विघ्नहर्ता सिद्धिविनायक</span>
            </div>
            <div style="background:#FFFFFF; border:1.5px solid #FDE68A; border-radius:10px; padding:10px; box-shadow:0 2px 8px rgba(212,175,55,0.08);">
              <img src="/assets/gods/shiva.png" alt="Lord Shiva" style="width:70px; height:70px; object-fit:cover; border-radius:50%; border:2px solid #D4AF37; margin:0 auto 6px auto; display:block; box-shadow:0 0 10px rgba(212,175,55,0.3);"/>
              <strong style="color:#7C2D12; font-size:12px; display:block;">महादेव शिव (महामृत्युंजय)</strong>
              <span style="font-size:10.5px; color:#166534; font-weight:700;">महामृत्युंजय रक्षा कवच</span>
            </div>
            <div style="background:#FFFFFF; border:1.5px solid #FDE68A; border-radius:10px; padding:10px; box-shadow:0 2px 8px rgba(212,175,55,0.08);">
              <img src="/assets/gods/durga.png" alt="Maa Durga" style="width:70px; height:70px; object-fit:cover; border-radius:50%; border:2px solid #D4AF37; margin:0 auto 6px auto; display:block; box-shadow:0 0 10px rgba(212,175,55,0.3);"/>
              <strong style="color:#7C2D12; font-size:12px; display:block;">माँ भवानी दुर्गा (शक्ती व समृद्धी)</strong>
              <span style="font-size:10.5px; color:#991B1B; font-weight:700;">सर्व शक्ती व अखंड समृद्धी</span>
            </div>
            <div style="background:#FFFFFF; border:1.5px solid #FDE68A; border-radius:10px; padding:10px; box-shadow:0 2px 8px rgba(212,175,55,0.08);">
              <img src="/assets/gods/surya.png" alt="Surya Dev" style="width:70px; height:70px; object-fit:cover; border-radius:50%; border:2px solid #D4AF37; margin:0 auto 6px auto; display:block; box-shadow:0 0 10px rgba(212,175,55,0.3);"/>
              <strong style="color:#7C2D12; font-size:12px; display:block;">भगवान सूर्य नारायण (तेज)</strong>
              <span style="font-size:10.5px; color:#C2540A; font-weight:700;">नवग्रह अधिपती दिव्य तेज</span>
            </div>
            <div style="background:#FFFFFF; border:1.5px solid #FDE68A; border-radius:10px; padding:10px; box-shadow:0 2px 8px rgba(212,175,55,0.08);">
              <img src="/assets/gods/hanuman.png" alt="Hanuman Ji" style="width:70px; height:70px; object-fit:cover; border-radius:50%; border:2px solid #D4AF37; margin:0 auto 6px auto; display:block; box-shadow:0 0 10px rgba(212,175,55,0.3);"/>
              <strong style="color:#7C2D12; font-size:12px; display:block;">श्री हनुमान जी (संकटमोचन)</strong>
              <span style="font-size:10.5px; color:#B45309; font-weight:700;">संकटमोचन महाबली रक्षक</span>
            </div>
          </div>
        </div>

          <!-- Metrics Grid -->
          <div class="metrics-grid">
            <div class="metric-card">
              <div class="metric-icon-box">👥</div>
              <div class="metric-data">
                <div class="val" id="dashTotalClients">1</div>
                <div class="lbl">नोंदणीकृत ग्राहक (पंजीकृत ग्राहक)</div>
              </div>
            </div>
            <div class="metric-card">
              <div class="metric-icon-box">📄</div>
              <div class="metric-data">
                <div class="val" id="dashTotalReports">1</div>
                <div class="lbl">तयार केलेले PDF अहवाल (निर्मित अहवाल)</div>
              </div>
            </div>
            <div class="metric-card">
              <div class="metric-icon-box">🪐</div>
              <div class="metric-data">
                <div class="val" id="dashActiveClient">Ready</div>
                <div class="lbl">सक्रिय जातक वर्कस्पेस (सक्रिय जातक)</div>
              </div>
            </div>
            <div class="metric-card">
              <div class="metric-icon-box">🛡️</div>
              <div class="metric-data">
                <div class="val" style="color:#166534;">100% Offline</div>
                <div class="lbl">१००% ऑफलाइन वैदिक इंजिन (100% Offline)</div>
              </div>
            </div>
          </div>

          <!-- Quick Actions Bar -->
          <div class="quick-actions-bar">
            <button class="btn-quick-act" onclick="switchNav('new_kundli')">➕ नवीन कुंडली तयार करा (नवीन कुंडली)</button>
            <button class="btn-quick-act" onclick="castInstantPrashna()">⏱️ Cast Instant Prashna</button>
            <button class="btn-quick-act" onclick="switchNav('milan')">💍 Kundli Milan (36-Guna)</button>
            <button class="btn-quick-act" onclick="switchNav('reports')">👑 60-Page VIP PDF Studio</button>
            <button class="btn-quick-act" onclick="switchNav('clients')">🔍 Search Client Directory</button>
          </div>

          <!-- Recent Clients Card -->
          <div class="glass-card">
            <div class="card-header">
              <span>👥 अलीकडील ग्राहक सल्लामसलत (जातक नोंदी)</span>
              <button class="btn-table-action" onclick="switchNav('new_kundli')">+ Add Client</button>
            </div>
            <div style="overflow-x:auto;">
              <table class="crm-table">
                <thead>
                  <tr>
                    <th>ग्राहकाचे नाव (Client Name / जातक)</th><th>लिंग (Gender)</th><th>जन्म तारीख (DOB / जन्म)</th><th>जन्म वेळ (Time / वेळ)</th><th>जन्म ठिकाण (Place / ठिकाण)</th><th>सल्ला श्रेणी (Category)</th><th>कृती (Actions / कृती)</th>
                  </tr>
                </thead>
                <tbody id="dashRecentClientsBody">
                  <tr>
                    <td style="font-weight:800; color:#7C2D12;">राजेश जोशी</td>
                    <td>Male</td>
                    <td style="font-weight:600;">15/8/1995</td>
                    <td style="font-family:monospace; font-weight:700;">14:30</td>
                    <td>पुणे, महाराष्ट्र (Pune, Maharashtra)</td>
                    <td><span class="badge">VIP Kundli Consultation</span></td>
                    <td>
                      <button class="btn-table-action" onclick="loadClientDataIntoForm(3)">🔮 कुंडली पहा (Open)</button>
                      <button class="btn-table-action" style="color:#DC2626; border-color:#FCA5A5;" onclick="deleteClientRecord(3)">🗑️ हटवा (Delete)</button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- Recent PDF Reports Card -->
          <div class="glass-card">
            <div class="card-header">
              <span>📄 तयार केलेले PDF अहवाल संग्रह (अहवाल संग्रह)</span>
              <button class="btn-table-action" onclick="switchNav('reports')">Open PDF Studio</button>
            </div>
            <div style="overflow-x:auto;">
              <table class="crm-table">
                <thead>
                  <tr>
                    <th>अहवाल फाईल नाव (File Name)</th><th>आकार (Size)</th><th>तयार केल्याची तारीख (Date)</th><th>कृती (Action)</th>
                  </tr>
                </thead>
                <tbody id="dashRecentReportsBody">
                  <tr>
                    <td style="font-weight:700; color:#1E3A8A;">Shivansh_Kundli_Rajesh_Joshi_VIP.pdf</td>
                    <td>48.41 MB</td>
                    <td style="font-size:11.5px; color:#6B7280;">01 Nov 2026, 10:00 PM</td>
                    <td>
                      <a href="/api/download-pdf/Shivansh_Kundli_Rajesh_Joshi_VIP.pdf" target="_blank" class="btn-table-action" style="text-decoration:none; display:inline-block;">📥 PDF डाउनलोड</a>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <!-- Milan Preview & Print Modal -->
            <div id="milanPreviewModal" style="display:none; position:fixed; top:0; left:0; width:100vw; height:100vh; background:rgba(0,0,0,0.72); z-index:999999; justify-content:center; align-items:center;">
              <div style="background:#FFFDF9; border:2px solid #D97706; border-radius:12px; width:92vw; max-width:1150px; height:92vh; display:flex; flex-direction:column; overflow:hidden; box-shadow:0 12px 36px rgba(0,0,0,0.45);">
                <div style="background:linear-gradient(135deg, #7C2D12 0%, #B45309 100%); padding:12px 18px; color:#fff; display:flex; justify-content:space-between; align-items:center;">
                  <span style="font-weight:900; font-size:14px; letter-spacing:0.5px;">👑 Royal Vedic Matrimonial Milan Dossier (३-पृष्ठीय अष्टकूट मिलान)</span>
                  <div style="display:flex; gap:10px;">
                    <button onclick="printMilanDossier()" style="background:#059669; color:#fff; border:none; padding:7px 16px; border-radius:6px; font-weight:800; cursor:pointer; font-size:12px;">🖨️ प्रिंट / PDF सेव्ह करा (Print / Save)</button>
                    <button onclick="exportMilanPDF()" style="background:#D97706; color:#fff; border:none; padding:7px 16px; border-radius:6px; font-weight:800; cursor:pointer; font-size:12px;">⬇️ Download PDF</button>
                    <button onclick="closeMilanPreview()" style="background:#EF4444; color:#fff; border:none; padding:7px 14px; border-radius:6px; font-weight:800; cursor:pointer; font-size:12px;">✕ Close</button>
                  </div>
                </div>
                <div style="flex:1; padding:12px; background:#F5EFEB; overflow:hidden;">
                  <iframe id="milanPreviewFrame" style="width:100%; height:100%; border:1px solid #D97706; border-radius:6px; background:#FFFDF9;"></iframe>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- =============================================================== -->
        <!-- VIEW 2: NEW KUNDLI FORM -->
        <!-- =============================================================== -->
        <section class="view-pane" id="pane_new_kundli">
          <div class="glass-card" style="max-width: 900px; margin: 0 auto;">
            <div class="card-header">
              <span>🌟 जातकाचे जन्म तपशील व कुंडली निर्मिती (जन्म तपशील व कुंडली)</span>
              <span class="badge">Dynamic Math • No Defaults</span>
            </div>
            <p style="font-size:12px; color:#574032; margin-bottom:16px;">
              खाली जातकाचे अचूक जन्म तपशील प्रविष्ट करा. आपण ७,००,०००+ भारतीय व जागतिक शहरांमधून शहर शोधून अक्षांश-रेखांश स्वयंचलितपणे भरू शकता.
            </p>

            <input type="hidden" id="clientId" value=""/>

            <div class="form-grid">
              <div class="form-group" style="grid-column: span 2;">
                <label>जातकाचे संपूर्ण नाव (Client Full Name) *</label>
                <input type="text" id="name" value="" placeholder="उदा. राहुल जोशी / Aarav Sharma" required/>
              </div>
              <div class="form-group">
                <label>लिंग (Gender)</label>
                <select id="sex">
                  <option value="Male">पुरुष (Male / पुरुष)</option>
                  <option value="Female">स्त्री (Female / स्त्री)</option>
                  <option value="Other">इतर (Other)</option>
                </select>
              </div>
              <div class="form-group">
                <label>वर्षफळ वर्ष (Varshaphal Year)</label>
                <input type="number" id="varsha_year" value="2026"/>
              </div>
            </div>

            <!-- Date & Time Grid (Clean & Blank by Default) -->
            <div class="form-grid" style="grid-template-columns: repeat(6, 1fr);">
              <div class="form-group">
                <label>दिवस (Day 1-31) *</label>
                <input type="number" id="day" min="1" max="31" value="" placeholder="DD" required/>
              </div>
              <div class="form-group">
                <label>महिना (Month 1-12) *</label>
                <input type="number" id="month" min="1" max="12" value="" placeholder="MM" required/>
              </div>
              <div class="form-group">
                <label>वर्ष (Year) *</label>
                <input type="number" id="year" min="1800" max="2100" value="" placeholder="YYYY" required/>
              </div>
              <div class="form-group">
                <label>तास (Hour 0-23) *</label>
                <input type="number" id="hour" min="0" max="23" value="" placeholder="HH" required/>
              </div>
              <div class="form-group">
                <label>मिनिट (Minute 0-59) *</label>
                <input type="number" id="minute" min="0" max="59" value="" placeholder="MM" required/>
              </div>
              <div class="form-group">
                <label>सेकंद (Second 0-59)</label>
                <input type="number" id="second" min="0" max="59" value="0" placeholder="0"/>
              </div>
            </div>

            <!-- Searchable City Grid (Clean & Blank by Default) -->
            <div class="form-grid" style="grid-template-columns: 2fr 1fr 1fr 1fr;">
              <div class="form-group city-wrap">
                <label>शहर शोधा (Search City - ७+ लाख जागतिक शहरे)</label>
                <input type="text" id="citySearchInput" placeholder="शहर शोधा उदा. पुणे, मुंबई, नाशिक, दिल्ली..." oninput="onCitySearchType()" autocomplete="off"/>
                <div class="city-dropdown" id="citySuggestions"></div>
              </div>
              <div class="form-group">
                <label>निवडलेले ठिकाण (Selected Place) *</label>
                <input type="text" id="place" placeholder="उदा. मुंबई / Pune" value=""/>
              </div>
              <div class="form-group">
                <label>अक्षवृत्त (Latitude °N)</label>
                <input type="number" id="lat" step="0.0001" value="" placeholder="उदा. 18.92"/>
              </div>
              <div class="form-group">
                <label>रेखावृत्त (Longitude °E)</label>
                <input type="number" id="lon" step="0.0001" value="" placeholder="उदा. 72.83"/>
              </div>
            </div>

            <div class="form-grid" style="grid-template-columns: 1fr 1.5fr 1.5fr 2fr;">
              <div class="form-group">
                <label>वेळ क्षेत्र (Timezone UTC)</label>
                <input type="number" id="tz" step="0.25" value="5.5"/>
              </div>
              <div class="form-group">
                <label>फोन / व्हॉट्सॲप (Phone / WhatsApp)</label>
                <input type="text" id="phone" placeholder="e.g. 9876543210"/>
              </div>
              <div class="form-group">
                <label>ईमेल पत्ता (Email Address)</label>
                <input type="email" id="email" placeholder="client@example.com"/>
              </div>
              <div class="form-group">
                <label>सल्लामसलत श्रेणी (Consultation Category)</label>
                <select id="category">
                  <option value="General Consultation">सर्वसाधारण ज्योतिष सल्ला (General Consultation)</option>
                  <option value="Career & Business">करिअर व व्यवसाय (Career &amp; Business)</option>
                  <option value="Marriage & Compatibility">विवाह व कुंडली मिलान (Marriage &amp; Match)</option>
                  <option value="Health & Longevity">आरोग्य व दीर्घायुष्य (Health &amp; Medical)</option>
                  <option value="Wealth & Property">धन, संपत्ती व समृद्धी (Wealth &amp; Property)</option>
                </select>
              </div>
            </div>

            <div class="form-group" style="margin-bottom: 20px;">
              <label>विशेष ज्योतिषीय नोंदी / प्रश्न (Consultation Notes)</label>
              <textarea id="notes" placeholder="Enter special client queries, birth verification notes, remedial focus..."></textarea>
            </div>

            <div style="display:flex; gap:12px; align-items:center;">
              <button class="btn-primary-gradient" onclick="calculateAndOpenWorkspace()">
                ✨ गणना करा व कुंडली पहा (Calculate &amp; Open)
              </button>
              <button class="btn-secondary-outline" onclick="saveClientRecordOnly()">
                💾 केवळ CRM मध्ये सेव्ह करा (Save to CRM)
              </button>
              <button class="btn-secondary-outline" onclick="resetKundliForm()">
                🔄 फॉर्म साफ करा (Clear Form)
              </button>
            </div>
          </div>
        </section>

        <!-- =============================================================== -->
        <!-- VIEW 3: CLIENTS DIRECTORY (CRM) -->
        <!-- =============================================================== -->
        <section class="view-pane" id="pane_clients">
          <div class="glass-card">
            <div class="card-header">
              <span>👥 ग्राहक सल्लामसलत डिरेक्टरी व नोंदी (Client CRM)</span>
              <button class="btn-primary-gradient" style="padding:6px 14px; font-size:12px;" onclick="switchNav('new_kundli')">
                ➕ नवीन ग्राहक जोडा (Add Client)
              </button>
            </div>

            <div style="margin-bottom: 14px; display:flex; gap:12px;">
              <input type="text" id="clientsSearchInput" placeholder="🔍 ग्राहक शोधा (नाव, शहर, फोन, श्रेणी...)" style="flex:1; height:38px; border:1.5px solid #EADBC8; border-radius:8px; padding:0 12px; font-size:12.5px; font-weight:600;" oninput="loadClientsTable()"/>
            </div>

            <div style="overflow-x:auto;">
              <table class="crm-table">
                <thead>
                  <tr>
                    <th>आयडी (ID)</th><th>ग्राहकाचे नाव (Client Name)</th><th>लिंग (Gender)</th><th>जन्म तारीख व वेळ (DOB &amp; TOB)</th><th>जन्म ठिकाण (Place)</th><th>फोन (Phone)</th><th>श्रेणी (Category)</th><th>नोंदणी तारीख (Created)</th><th>कृती (Actions)</th>
                  </tr>
                </thead>
                <tbody id="clientsFullTableBody">
                  <tr>
                    <td style="font-weight:800; color:#7C2D12;">#3</td>
                    <td style="font-weight:800; color:#7C2D12;">राजेश जोशी</td>
                    <td>Male</td>
                    <td style="font-weight:600;">15/8/1995 &bull; 14:30</td>
                    <td>पुणे, महाराष्ट्र (Pune, Maharashtra)</td>
                    <td>9876543210</td>
                    <td><span class="badge">VIP Kundli Consultation</span></td>
                    <td style="font-size:11.5px; color:#6B7280;">01 Nov 2026</td>
                    <td>
                      <button class="btn-table-action" onclick="loadClientDataIntoForm(3)">🔮 कुंडली पहा (Open)</button>
                      <button class="btn-table-action" style="color:#DC2626; border-color:#FCA5A5;" onclick="deleteClientRecord(3)">🗑️ हटवा (Delete)</button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </section>

        <!-- =============================================================== -->
        <!-- VIEW 4: INTERACTIVE ASTROLOGY WORKSPACE -->
        <!-- =============================================================== -->
        <section class="view-pane" id="pane_workspace">
          <!-- 👑 TOP ACTION BAR: 1-CLICK COMPLETE 56-PAGE VIP PDF VIEW -->
          <div class="workspace-pdf-banner" style="background:linear-gradient(135deg, #FFFBEB 0%, #FEF3C7 50%, #FDE68A 100%); border:2px solid #D4AF37; border-radius:12px; padding:12px 14px; margin-bottom:14px; display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:10px; box-shadow:0 4px 14px rgba(212,175,55,0.22);">
            <div style="display:flex; align-items:center; gap:8px;">
              <span style="font-size:24px;">👑</span>
              <div>
                <strong style="font-family:'Cinzel', serif; font-size:14px; font-weight:900; color:#78350F; display:block;">
                  संपूर्ण ५६-पृष्ठीय VIP महा-जन्मपत्रिका (Full 56-Page VIP Dossier)
                </strong>
                <span style="font-size:11px; color:#92400E; font-weight:600;">
                  १६ वर्ग कुंडली • विंशोत्तरी महादशा • लाल किताब १९५२ चे अचूक उपाय व अष्टकवर्ग
                </span>
              </div>
            </div>
            <div style="display:flex; gap:8px; flex-wrap:wrap; width:100%; max-width:340px;">
              <button type="button" onclick="exportPDF()" style="flex:1; min-width:145px; background:linear-gradient(135deg, #7C2D12 0%, #451A03 100%); color:#FEF08A; border:1px solid #D4AF37; font-weight:900; font-size:12.5px; padding:10px 14px; border-radius:8px; cursor:pointer; display:inline-flex; align-items:center; justify-content:center; gap:6px; box-shadow:0 2px 8px rgba(124,45,18,0.25);">
                📄 संपूर्ण ५६-पृष्ठीय PDF पहा (PDF पहा)
              </button>
              <button type="button" onclick="loadInAppPdfPreview(); switchNav('reports');" style="flex:1; min-width:130px; background:#FFFFFF; color:#7C2D12; border:1.5px solid #D4AF37; font-weight:800; font-size:12px; padding:10px 12px; border-radius:8px; cursor:pointer; display:inline-flex; align-items:center; justify-content:center; gap:6px;">
                👁️ थेट पूर्वदृश्य (Live Preview)
              </button>
            </div>
          </div>

          <!-- Active Client Stats Strip -->
          <div class="workspace-stats-strip">
            <div class="stat-pill-card">
              <div class="lbl">लग्न (Lagna / लग्न)</div>
              <div class="val" id="statLagna">-</div>
            </div>
            <div class="stat-pill-card">
              <div class="lbl">चंद्र राशी (Moon Sign / राशी)</div>
              <div class="val" id="statRasi">-</div>
            </div>
            <div class="stat-pill-card">
              <div class="lbl">नक्षत्र (Nakshatra / नक्षत्र)</div>
              <div class="val" id="statNakshatra">-</div>
            </div>
            <div class="stat-pill-card">
              <div class="lbl">मांगलिक दोष (Manglik / मांगलिक)</div>
              <div class="val" id="statManglik">-</div>
            </div>
            <div class="stat-pill-card">
              <div class="lbl">दशा शिल्लक (Dasha Balance / दशा शेष)</div>
              <div class="val" id="statDasha">-</div>
            </div>
          </div>

          <!-- Birth-Time Adjustment Strip -->
          <div class="time-adjust-strip">
            <div style="display:flex; align-items:center; gap:8px;">
              <span style="font-size:12px; font-weight:800; color:#7C2D12;">⏱️ Birth-Time Rectification &amp; Recalculation:</span>
              <span style="font-size:11px; color:#574032; font-weight:600;" id="workspaceNativeTag">No Native Loaded</span>
            </div>

            <div class="adjust-controls">
              <button class="btn-time-step" onclick="adjustBirthTime(-5)" title="Step back 5 minutes">-5 min</button>
              <button class="btn-time-step" onclick="adjustBirthTime(-1)" title="Step back 1 minute">-1 min</button>
              <div class="time-readout-box" id="workspaceTimeDisplay">12:00:00</div>
              <button class="btn-time-step" onclick="adjustBirthTime(1)" title="Step forward 1 minute">+1 min</button>
              <button class="btn-time-step" onclick="adjustBirthTime(5)" title="Step forward 5 minutes">+5 min</button>
              <button class="btn-time-recalc" onclick="calculateKundli()" title="Recalculate complete charts and tables">🔄 त्वरित पुनर्गणना करा (Recalculate Now)</button>
            </div>
          </div>

          <!-- Active Running Dasha Banner -->
          <div id="activeDashaBanner" style="background:linear-gradient(90deg, #7C2D12 0%, #451A03 100%); color:#FDE68A; padding:8px 16px; border-radius:8px; margin-bottom:14px; display:flex; justify-content:space-between; align-items:center; border:1px solid #D4AF37; font-size:12.5px; font-weight:800;">
            <span>🔥 CURRENT ACTIVE DASHA: <span id="txtActiveDasha" style="color:#FFFFFF;">Loading...</span></span>
            <span style="font-size:11px; opacity:0.9;" id="txtDashaValid"></span>
          </div>

          <!-- Quick Jump Navigation Strip -->
          <div style="display:flex; flex-wrap:wrap; gap:8px; margin-bottom:14px; background:#FAF6F0; border:1px solid #EADBC8; border-radius:8px; padding:6px 10px;">
            <button type="button" class="btn-time-step" style="padding:4px 10px; font-size:11.5px; font-weight:700;" onclick="document.querySelector('.charts-grid').scrollIntoView({behavior:'smooth'})">🪐 Charts &amp; Vargas</button>
            <button type="button" class="btn-time-step" style="padding:4px 10px; font-size:11.5px; font-weight:700;" onclick="document.getElementById('sec_shadbala_sav').scrollIntoView({behavior:'smooth'})">⚖️ षड्बल व SAV (Shadbala)</button>
            <button type="button" class="btn-time-step" style="padding:4px 10px; font-size:11.5px; background:#FEF3C7; color:#78350F; font-weight:800; border-color:#FDE68A;" onclick="document.getElementById('sec_kp_system').scrollIntoView({behavior:'smooth'})">🏛️ KP System &amp; Cusps</button>
            <button type="button" class="btn-time-step" style="padding:4px 12px; font-size:11.5px; background:linear-gradient(135deg, #7C2D12 0%, #B45309 100%); color:#FDE68A; font-weight:900; border:1.5px solid #D4AF37; box-shadow:0 2px 6px rgba(124,45,18,0.25); cursor:pointer;" onclick="openKPRemediesDirectPDF()">🔮 KP Remedies &amp; Upay (के.पी. अचूक उपाय PDF)</button>
            <button type="button" class="btn-time-step" style="padding:4px 10px; font-size:11.5px; background:#FEE2E2; color:#991B1B; font-weight:800; border-color:#FCA5A5;" onclick="document.getElementById('sec_lal_kitab').scrollIntoView({behavior:'smooth'})">📖 Lal Kitab &amp; Upay</button>
            <button type="button" class="btn-time-step" style="padding:4px 10px; font-size:11.5px; background:#DCFCE7; color:#166534; font-weight:800; border-color:#86EFAC;" onclick="document.getElementById('sec_ratna_yantra').scrollIntoView({behavior:'smooth'})">💎 रत्ने व सिद्ध यंत्रे (रत्न व यंत्र)</button>
            <button type="button" class="btn-time-step" style="padding:4px 10px; font-size:11.5px; background:#E0E7FF; color:#3730A3; font-weight:800; border-color:#C7D2FE;" onclick="document.getElementById('sec_avkahada_science').scrollIntoView({behavior:'smooth'})">🔬 अवकहडा व विज्ञान (Avakahada &amp; Science)</button>
          </div>

          <!-- Side-by-Side Charts (D1 & Divisional Chart Viewer) -->
          <div class="charts-grid">
            <!-- Left Chart: D1 Lagna -->
            <div class="chart-box">
              <div class="chart-box-header">
                <strong id="chartTitle">D1 लग्न कुंडली (D1 Lagna Chart / लग्न कुंडली)</strong>
                <div class="control-pill">
                  <button class="control-btn active" onclick="setChartStyle('north')">उत्तर</button>
                  <button class="control-btn" onclick="setChartStyle('south')">दक्षिण</button>
                  <button class="control-btn" onclick="setChartStyle('east')">पूर्व</button>
                </div>
              </div>
              <div id="chartSvgWrapper" class="svg-wrapper">Please calculate a horoscope to view D1.</div>
            </div>

            <!-- Right Chart: 16-Divisional Chart Viewer -->
            <div class="chart-box">
              <div class="chart-box-header">
                <div style="display:flex; align-items:center; gap:8px;">
                  <strong>१६-वर्ग कुंडली (Divisional Chart):</strong>
                  <select id="divisionalSelect" class="divisional-select" onchange="onDivisionalChange()">
                    <option value="D9" selected>D9 नवमांश (धर्म, जोडीदार व आत्मा / नवमांश)</option>
                    <option value="D10">D10 दशमांश (उद्योग, करिअर व प्रतिष्ठा / दशमांश)</option>
                    <option value="D2">D2 होरा (धन व संपत्ती / होरा)</option>
                    <option value="D3">D3 द्रेष्काण (भावंडे व पराक्रम / द्रेष्काण)</option>
                    <option value="D4">D4 चतुर्थांश (भाग्य व अचल संपत्ती / चतुर्थांश)</option>
                    <option value="D7">D7 सप्तांश (संतती व वंशवृद्धी / सप्तांश)</option>
                    <option value="D12">D12 द्वादशांश (माता-पिता व पूर्वज / द्वादशांश)</option>
                    <option value="D16">D16 षोडशांश (वाहन व गृहसुख / षोडशांश)</option>
                    <option value="D20">D20 विंशांश (अध्यात्म व उपासना / विंशांश)</option>
                    <option value="D24">D24 चतुर्विंशांश (उच्च विद्या व ज्ञान / चतुर्विंशांश)</option>
                    <option value="D27">D27 सप्तविंशांश (शारीरिक ताकद व सामर्थ्य / सप्तविंशांश)</option>
                    <option value="D30">D30 त्रिंशांश (अरिष्ट व संकट निवारण / त्रिंशांश)</option>
                    <option value="D40">D40 खवेदांश (शुभ फळे व परिणाम / खवेदांश)</option>
                    <option value="D45">D45 अक्षवेदांश (सर्वंकष कल्याण / अक्षवेदांश)</option>
                    <option value="D60">D60 षष्ट्यंश (पूर्वजन्म संचित कर्म / षष्ट्यंश)</option>
                    <option value="TRANSIT">आजचे गोचर (Real-Time Transit / आज का गोचर)</option>
                  </select>
                </div>
                <span style="font-size:10.5px; color:#7C2D12; font-weight:700;" id="divisionalSubTag">Harmonic Arc</span>
              </div>
              <div id="chartD9SvgWrapper" class="svg-wrapper">Please calculate a horoscope to view Divisional chart.</div>
            </div>
          </div>

          <!-- Planetary Positions & Dignities -->
          <div class="glass-card">
            <div class="card-header">
              <span>ग्रह स्पष्ट मान, नक्षत्र आणि अवस्था (ग्रह स्पष्ट मान व अवस्था)</span>
            </div>
            <div style="overflow-x:auto;">
              <table class="dash-table">
                <thead>
                  <tr>
                    <th>ग्रह (Planet / ग्रह)</th>
                    <th>राशी (Sign / राशि)</th>
                    <th>अंश-कला-विकला (Degree / अंश)</th>
                    <th>नक्षत्र व चरण (Nakshatra &amp; Pada / नक्षत्र)</th>
                    <th>अवस्था (Dignity / अवस्था)</th>
                    <th>स्थिती (Status / गति)</th>
                  </tr>
                </thead>
                <tbody id="planetTableBody">
                  <tr><td colspan="6" style="padding:14px; color:#6B7280; font-style:italic;">Calculate a Kundli to display coordinates.</td></tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- 12 Bhavas (Houses) -->
          <div class="glass-card">
            <div class="card-header">
              <span>🪐 १२ भाव विश्लेषण व भावेश (द्वादश भाव विश्लेषण)</span>
            </div>
            <div style="display:grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap:10px;" id="bhavasGrid"></div>
          </div>

          <!-- Vimshottari Dasha Timeline -->
          <div class="glass-card">
            <div class="card-header">
              <span>🔮 विंशोत्तरी महादशा व अंतर्दशा कालखंड (विंशोत्तरी महादशा व अंतर्दशा)</span>
            </div>
            <div id="dashaSummary"></div>
            <div style="margin-top:16px;">
              <h4 style="font-size:12.5px; color:#7C2D12; font-weight:800; margin-bottom:8px;">Recommended Auspicious Gemstones &amp; Vedic Mantras</h4>
              <div id="gemstonesSummary"></div>
            </div>
          </div>

          <!-- Doshas & Shastriya Remedies -->
          <div class="glass-card">
            <div class="card-header">
              <span>🛡️ शास्त्रीय दोष आणि प्रामाणिक वैदिक उपाय (दोष एवं वैदिक उपाय)</span>
            </div>
            <div class="doshas-grid" id="doshasList"></div>
          </div>

          <!-- Auspicious Yogas -->
          <div class="glass-card">
            <div class="card-header">
              <span>🌟 प्राचीन शास्त्रीय ग्रह योग आणि शुभ फळे (शुभ योग फल)</span>
            </div>
            <div style="display:grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap:10px;" id="yogasList"></div>
          </div>

          <!-- Shadbala & Ashtakavarga Matrix -->
          <div class="glass-card" id="sec_shadbala_sav">
            <div class="card-header">
              <span>⚖️ षड्बल ६-स्तरीय ग्रह सामर्थ्य आणि भावबल (षड्बल व भावबल)</span>
            </div>
            <div style="overflow-x:auto; margin-bottom:14px;">
              <table class="crm-table" id="tableShadbala" style="text-align:center;">
                <thead>
                  <tr style="background:linear-gradient(135deg, #7C2D12 0%, #451A03 100%); color:#FFFFFF;">
                    <th style="text-align:left; padding:8px 10px;">Planet</th><th>Sthana</th><th>Dig</th><th>Kala</th><th>Chesta</th><th>Naisargik</th><th>Drik</th><th>Total Virupa</th><th>Rupas</th><th>Min Req</th><th>Ratio / Status</th><th>Rank</th>
                  </tr>
                </thead>
                <tbody id="shadbalaTableBody">
                  <tr><td colspan="12" style="padding:14px; color:#6B7280; font-style:italic;">Calculate Kundli to view Shadbala strengths.</td></tr>
                </tbody>
              </table>
            </div>

            <!-- SAV Grid -->
            <div class="card-header">
              <span>सर्वाष्टकवर्ग चक्र (सर्वाष्टकवर्ग - ३३७ शुभ बिंदू)</span>
            </div>
            <div style="overflow-x:auto;">
              <table class="crm-table" style="text-align:center;">
                <thead>
                  <tr style="background:linear-gradient(135deg, #7C2D12 0%, #451A03 100%); color:#FFFFFF;">
                    <th style="text-align:left; padding:8px 10px;">Graha</th><th>Ari</th><th>Tau</th><th>Gem</th><th>Can</th><th>Leo</th><th>Vir</th><th>Lib</th><th>Sco</th><th>Sag</th><th>Cap</th><th>Aqu</th><th>Pis</th><th>Total</th>
                  </tr>
                </thead>
                <tbody id="savTableBody">
                  <tr><td colspan="14" style="padding:14px; color:#6B7280; font-style:italic;">Calculate Kundli to view Ashtakavarga grid.</td></tr>
                </tbody>
              </table>
            </div>
            <div style="font-size:11px; margin-top:10px; display:flex; gap:16px; justify-content:center; align-items:center; background:#FAF6F0; padding:6px 14px; border-radius:8px; border:1px solid #EADBC8;">
              <span><strong style="color:#166534; font-size:13px;">● &gt;= 28:</strong> <span style="color:#166534; font-weight:700;">Highly Auspicious</span></span>
              <span><strong style="color:#854D0E; font-size:13px;">● 25-27:</strong> <span style="color:#854D0E; font-weight:700;">Moderate</span></span>
              <span><strong style="color:#991B1B; font-size:13px;">● &lt; 25:</strong> <span style="color:#991B1B; font-weight:700;">Needs Upliftment</span></span>
            </div>

            <!-- Bhavabala Cards -->
            <div class="card-header" style="margin-top:16px;">
              <span>Bhavabala Summary (12 Bhavas Strength)</span>
            </div>
            <div id="bhavabalaSummaryGrid" style="display:grid; grid-template-columns: repeat(6, 1fr); gap:8px;"></div>
          </div>

          <!-- ========================================================= -->
          <!-- MODULE A: KRISHNAMURTI PADDHATI (KP SYSTEM) -->
          <!-- ========================================================= -->
          <div class="glass-card" id="sec_kp_system">
            <div style="background:linear-gradient(135deg, #7C2D12 0%, #451A03 100%); color:#FDE68A; padding:12px 16px; border-radius:8px; margin-bottom:14px; display:flex; justify-content:space-between; align-items:center; border:1.5px solid #D4AF37; box-shadow:0 2px 8px rgba(124,45,18,0.25);">
              <div>
                <div style="font-weight:900; font-size:14px; color:#FFFFFF;">🔮 कृष्णमूर्ती पद्धती (के.पी.) अचूक वैज्ञानिक उपाय व ग्रह कार्येश</div>
                <div style="font-size:11px; color:#FDE68A; opacity:0.9;">Prof. K. S. Krishnamurti Reader III Zero-Damage Gemstones, 4-Fold Significators &amp; KP 12-Cuspal House Grouping Formulas</div>
              </div>
              <button type="button" class="btn-time-step" style="background:#FDE68A; color:#7C2D12; font-weight:900; font-size:12px; padding:6px 14px; border:none; border-radius:6px; cursor:pointer;" onclick="openKPRemediesDirectPDF()">
                📄 थेट उपाय PDF पहा / प्रिंट करा
              </button>
            </div>
            <div class="card-header">
              <span>🏛️ कृष्णमूर्ती पद्धती आणि १२ भाव सब-लॉर्ड्स (कृष्णमूर्ति पद्धति)</span>
              <span class="badge">KP Horary &amp; Cuspal Precision</span>
            </div>
            
            <!-- Ruling Planets Strip -->
            <div style="background:#FAF6F0; border:1.5px solid #EADBC8; border-radius:8px; padding:10px 14px; margin-bottom:14px; display:flex; flex-wrap:wrap; gap:16px; font-size:12px;">
              <div><strong>☀️ Day Lord (वार स्वामी):</strong> <span id="kpDayLord" style="color:#C2540A; font-weight:800;">-</span></div>
              <div><strong> लग्न (Lagna):</strong> Sign: <span id="kpLagSign" style="font-weight:700;">-</span> • Star: <span id="kpLagStar" style="font-weight:700;">-</span> • Sub: <span id="kpLagSub" style="color:#166534; font-weight:800;">-</span></div>
              <div><strong> चंद्रमा (Moon):</strong> Sign: <span id="kpMoonSign" style="font-weight:700;">-</span> • Star: <span id="kpMoonStar" style="font-weight:700;">-</span> • Sub: <span id="kpMoonSub" style="color:#166534; font-weight:800;">-</span></div>
            </div>

            <!-- Two Column KP Tables: 12 Cusps & 9 Planets -->
            <div style="display:grid; grid-template-columns: 1.1fr 1fr; gap:14px;">
              <!-- 12 Cusps Table -->
              <div>
                <h4 style="font-size:12.5px; font-weight:800; color:#7C2D12; margin-bottom:8px;">12 Bhavas KP Cusps &amp; Sub-Lords</h4>
                <div style="overflow-x:auto;">
                  <table class="crm-table">
                    <thead>
                      <tr><th>Cusp</th><th>Degree (DMS)</th><th>Sign Lord</th><th>Star Lord</th><th>Sub-Lord (उप-स्वामी)</th><th>Sub-Sub</th></tr>
                    </thead>
                    <tbody id="kpCuspsBody">
                      <tr><td colspan="6" style="padding:10px; color:#6B7280;">Calculate Kundli to view KP cusps.</td></tr>
                    </tbody>
                  </table>
                </div>
              </div>

              <!-- 9 Planets Table -->
              <div>
                <h4 style="font-size:12.5px; font-weight:800; color:#7C2D12; margin-bottom:8px;">9 Planets KP Coordinates &amp; Sub-Lords</h4>
                <div style="overflow-x:auto;">
                  <table class="crm-table">
                    <thead>
                      <tr><th>Planet</th><th>Degree (DMS)</th><th>Star Lord</th><th>Sub-Lord</th><th>KP House</th></tr>
                    </thead>
                    <tbody id="kpPlanetsBody">
                      <tr><td colspan="5" style="padding:10px; color:#6B7280;">Calculate Kundli to view KP planets.</td></tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>

            <!-- KP Stellar & Cuspal Sub-Lord Authentic Remedies Section -->
            <div style="margin-top:16px; border-top:1.5px solid #FED7AA; padding-top:14px;">
              <h3 style="font-size:14px; font-weight:800; color:#7C2D12; margin-bottom:10px;">
                🔮 कृष्णमूर्ती पद्धती अचूक उपाय, ४-स्तरीय कार्येश आणि फलकथन (KP Authentic Remedies &amp; Significators)
              </h3>

              <!-- Gemstone Protocol: Approved vs Rejected (Reader III, p.414) -->
              <div id="kpGemsContainer" style="margin-bottom:14px;"></div>

              <!-- Two Column: Disease Cure Window & Debt Clearance -->
              <div style="display:grid; grid-template-columns: 1fr 1fr; gap:12px; margin-bottom:14px;">
                <div id="kpDiseaseContainer" style="background:#FFFBEB; border:1.2px solid #FDE68A; padding:10px; border-radius:8px;"></div>
                <div id="kpDebtsContainer" style="background:#EFF6FF; border:1.2px solid #BFDBFE; padding:10px; border-radius:8px;"></div>
              </div>

              <!-- 4-Fold Significators Table -->
              <div style="margin-bottom:14px;">
                <h4 style="font-size:12.5px; font-weight:800; color:#7C2D12; margin-bottom:6px;">
                  📊 कृष्णमूर्ती ४-स्तरीय ग्रह कार्येश मॅट्रिक्स (4-Fold Significators: Level A, B, C, D)
                </h4>
                <div style="overflow-x:auto;">
                  <table class="crm-table">
                    <thead>
                      <tr><th>भाव (House)</th><th>स्तर अ (Level A - Strongest)</th><th>स्तर ब (Level B - Occupant)</th><th>स्तर क (Level C - Star of Lord)</th><th>स्तर ड (Level D - Lord)</th></tr>
                    </thead>
                    <tbody id="kpFourFoldBody">
                      <tr><td colspan="5" style="padding:10px; color:#6B7280;">Calculate Kundli to view 4-Fold Significators.</td></tr>
                    </tbody>
                  </table>
                </div>
              </div>

              <!-- KP Cuspal Sub-Lord 12 House Predictions -->
              <div>
                <h4 style="font-size:12.5px; font-weight:800; color:#7C2D12; margin-bottom:6px;">
                  📜 कृष्णमूर्ती पद्धती १२ भाव उपस्वामी अचूक घटना सूत्रे (KP Cuspal Sub-Lord Event Predictions)
                </h4>
                <div id="kpEventsContainer" style="display:grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap:10px;"></div>
              </div>
            </div>
          </div>

          <!-- ========================================================= -->
          <!-- MODULE B: LAL KITAB TEVA & ANCESTRAL DEBTS (ऋण व अचूक उपाय) -->
          <!-- ========================================================= -->
          <div class="glass-card" id="sec_lal_kitab">
            <div class="card-header">
              <span>📖 लाल किताब तेवा आणि पितृ ऋण विश्लेषण (लाल किताब ऋण व अचूक उपाय)</span>
              <span class="badge">Lal Kitab 1952 Remedial Science</span>
            </div>

            <!-- Ancestral Debts (Rins) Container -->
            <div id="lkRinsContainer" style="margin-bottom:14px;"></div>

            <!-- Lal Kitab 9 Planets Table -->
            <h4 style="font-size:12.5px; font-weight:800; color:#7C2D12; margin-bottom:8px;">Lal Kitab Planet Placements &amp; Soya/Jaga Status (ग्रह अवस्था व किस्मत जगाने वाले ग्रह)</h4>
            <div style="overflow-x:auto;">
              <table class="crm-table">
                <thead>
                  <tr><th>Planet</th><th>Lal Kitab House</th><th>Lal Kitab Sign</th><th>Soya / Jaga</th><th>Kismat Awakener</th><th>Status (Nek / Manda)</th></tr>
                </thead>
                <tbody id="lkPlanetsBody">
                  <tr><td colspan="6" style="padding:10px; color:#6B7280;">Calculate Kundli to view Lal Kitab Teva.</td></tr>
                </tbody>
              </table>
            </div>
          </div>

          <!-- ========================================================= -->
          <!-- MODULE C: RATNA, SIDDHA YANTRA & VEDIC REMEDIES -->
          <!-- ========================================================= -->
          <div class="glass-card" id="sec_ratna_yantra">
            <div class="card-header">
              <span>💎 शुभ रत्ने, सिद्ध यंत्रे आणि दैवी मंत्र (रत्न, सिद्ध यंत्र व मंत्र)</span>
              <span class="badge">वैदिक रत्न व यंत्र विज्ञान (रत्न व यंत्र विज्ञान)</span>
            </div>

            <!-- Gemstones Grid -->
            <div id="gemstonesFullGrid" style="display:grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap:12px; margin-bottom:14px;"></div>

            <!-- Recommended Yantras Card -->
            <div style="background:#FFFBEB; border:1.5px solid #FDE68A; border-radius:10px; padding:14px;">
              <h4 style="font-size:13px; font-weight:800; color:#78350F; margin-bottom:8px;">🌟 Recommended Siddha Yantras for Native Life Upliftment (शुभ यंत्र प्रतिष्ठा)</h4>
              <div id="yantrasList" style="display:grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap:10px; font-size:12px; color:#451A03;"></div>
            </div>
          </div>

          <!-- ========================================================= -->
          <!-- MODULE D: AVAKAHADA CHAKRA & ASTROLOGICAL SCIENCE -->
          <!-- ========================================================= -->
          <div class="glass-card" id="sec_avkahada_science">
            <div class="card-header">
              <span>🔬 अवकहडा चक्र, पंचांग आणि ग्रह संतुलन (अवकहड़ा चक्र व शुभ मुहूर्त विज्ञान)</span>
              <span class="badge">ब्रह्मांड तत्त्व संतुलन (तत्व संतुलन)</span>
            </div>

            <div style="display:grid; grid-template-columns: 1fr 1fr; gap:16px;">
              <!-- Avakahada Grid -->
              <div style="background:#FFFFFF; border:1.5px solid #EADBC8; border-radius:10px; padding:12px;">
                <h4 style="font-size:12.5px; font-weight:800; color:#7C2D12; margin-bottom:10px;">Avakahada Chakra (अवकहड़ा चक्र)</h4>
                <div id="avkahadaGrid" style="display:grid; grid-template-columns: 1fr 1fr; gap:8px; font-size:11.8px;"></div>
              </div>

              <!-- Favourable Matrix -->
              <div style="background:#FFFFFF; border:1.5px solid #EADBC8; border-radius:10px; padding:12px;">
                <h4 style="font-size:12.5px; font-weight:800; color:#7C2D12; margin-bottom:10px;">Favourable Astro Matrix (शुभ मुहूर्त व अंक)</h4>
                <div id="favourableGrid" style="display:grid; grid-template-columns: 1fr 1fr; gap:8px; font-size:11.8px;"></div>
              </div>
            </div>
          </div>
        </section>

        <!-- =============================================================== -->
        <!-- VIEW 5: KUNDLI MILAN (36-GUNA MATCHMAKING) -->
        <!-- =============================================================== -->
        <section class="view-pane" id="pane_milan">
          <div class="glass-card">
            <div class="card-header">
              <span>💍 अष्टकूट ३६ गुण विवाह मिलान आणि मांगलिक सामंजस्य (विवाह मिलान)</span>
              <button class="btn-primary-gradient" style="padding:5px 12px; font-size:11.5px;" onclick="calculateMilan()">⚡ अष्टकूट ३६ गुण मिलान गणना करा (विवाह मिलान)</button>
            </div>

            <div style="display:grid; grid-template-columns: 1fr 1fr; gap:16px; margin-bottom:16px;">
              <!-- Groom Box -->
              <div style="background:#FFFDF9; border:1.5px solid #EADBC8; border-radius:10px; padding:14px;">
                <h4 style="color:#7C2D12; font-size:13px; font-weight:800; margin-bottom:10px;">👦 वर तपशील (Groom Details / वर विवरण)</h4>
                <div class="form-grid">
                  <div class="form-group" style="grid-column: span 2;">
                    <label>वराचे नाव (Groom Name / वर का नाम)</label>
                    <input type="text" id="milan_b_name" value="Groom"/>
                  </div>
                  <div class="form-group"><label>Day</label><input type="number" id="milan_b_day" value="15"/></div>
                  <div class="form-group"><label>Month</label><input type="number" id="milan_b_month" value="8"/></div>
                  <div class="form-group"><label>Year</label><input type="number" id="milan_b_year" value="1994"/></div>
                  <div class="form-group"><label>Hour</label><input type="number" id="milan_b_hour" value="10"/></div>
                  <div class="form-group"><label>Minute</label><input type="number" id="milan_b_minute" value="30"/></div>
                  <div class="form-group city-wrap" style="grid-column: span 2; position:relative;">
                    <label>🏙️ वराचे जन्म ठिकाण / शहर शोधा (Groom POB)</label>
                    <input type="text" id="milan_b_place" value="Delhi" placeholder="Type city e.g. Ludhiana, Delhi, Mumbai..." oninput="onMilanCitySearch('b')" autocomplete="off"/>
                    <div class="city-dropdown" id="milan_b_suggestions"></div>
                  </div>
                </div>
              </div>

              <!-- Bride Box -->
              <div style="background:#FFFDF9; border:1.5px solid #EADBC8; border-radius:10px; padding:14px;">
                <h4 style="color:#7C2D12; font-size:13px; font-weight:800; margin-bottom:10px;">👧 कन्या तपशील (Bride Details / कन्या विवरण)</h4>
                <div class="form-grid">
                  <div class="form-group" style="grid-column: span 2;">
                    <label>कन्येचे नाव (Bride Name / कन्या का नाम)</label>
                    <input type="text" id="milan_g_name" value="Bride"/>
                  </div>
                  <div class="form-group"><label>Day</label><input type="number" id="milan_g_day" value="22"/></div>
                  <div class="form-group"><label>Month</label><input type="number" id="milan_g_month" value="11"/></div>
                  <div class="form-group"><label>Year</label><input type="number" id="milan_g_year" value="1996"/></div>
                  <div class="form-group"><label>Hour</label><input type="number" id="milan_g_hour" value="14"/></div>
                  <div class="form-group"><label>Minute</label><input type="number" id="milan_g_minute" value="15"/></div>
                  <div class="form-group city-wrap" style="grid-column: span 2; position:relative;">
                    <label>🏙️ कन्येचे जन्म ठिकाण / शहर शोधा (Bride POB)</label>
                    <input type="text" id="milan_g_place" value="Delhi" placeholder="Type city e.g. Ludhiana, Delhi, Mumbai..." oninput="onMilanCitySearch('g')" autocomplete="off"/>
                    <div class="city-dropdown" id="milan_g_suggestions"></div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Milan Results Box -->
            <div id="milanResultBox" style="display:none; margin-top:14px;">
              <div style="background:#FEF3C7; border:2px solid #FDE68A; border-radius:12px; padding:16px; text-align:center; margin-bottom:16px;">
                <div style="font-size:28px; font-weight:900; color:#78350F;" id="milanTotalScore">28 / 36</div>
                <div style="font-size:14px; font-weight:800; color:#92400E;" id="milanVerdict">Auspicious Match</div>
                <div style="font-size:12px; font-weight:700; color:#B45309; margin-top:4px;" id="milanManglikHarmony">Manglik Harmony Verified</div>
                <div style="display:flex; justify-content:center; gap:10px; margin-top:14px; flex-wrap:wrap;">
                  <button class="btn-primary-gradient" id="btnExportMilan" onclick="exportMilanPDF()">⬇️ Download 3-Page Royal Milan PDF</button>
                  <button class="btn-primary-gradient" style="background:linear-gradient(135deg, #059669 0%, #047857 100%);" onclick="printMilanDossier()">🖨️ प्रिंट / PDF सेव्ह करा (Print / Save) (Instant)</button>
                  <button class="btn-secondary-outline" style="border-color:#B45309; color:#78350F; font-weight:800; background:#FFFBEB;" onclick="previewMilanDossier()">👁️ Live Dossier Preview</button>
                </div>
              </div>

              <table class="dash-table">
                <thead>
                  <tr><th>Koot (कूट)</th><th>Max Score</th><th>Obtained Score</th><th>Area of Life</th><th>Status</th></tr>
                </thead>
                <tbody id="milanKootsBody"></tbody>
              </table>
            </div>
          </div>
        </section>

        <!-- =============================================================== -->
        <!-- VIEW 6: PDF REPORT STUDIO -->
        <!-- =============================================================== -->
        <section class="view-pane" id="pane_reports">
          <div class="glass-card" style="padding: 14px;">
            <!-- Top Action Header -->
            <div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:8px; margin-bottom:12px; padding-bottom:10px; border-bottom:1.5px solid #EADBC8;">
              <div>
                <h3 style="font-family:'Cinzel', serif; font-size:15.5px; font-weight:900; color:#7C2D12; margin:0 0 2px 0;">
                  📄 ५६-पृष्ठीय VIP महा-जन्मपत्रिका पूर्वदृश्य (मराठी आवृत्ती)
                </h3>
                <span class="badge" id="reportNativeBadge" style="font-size:11px; background:#FEF3C7; color:#78350F; padding:2px 8px; border-radius:12px; font-weight:700;">Active Native: नवीन जातक (New Client)</span>
              </div>
              <div style="display:flex; gap:6px; flex-wrap:wrap;">
                <button class="btn-primary-gradient" onclick="exportPDF()" style="padding:8px 12px; font-size:12px; font-weight:800; display:inline-flex; align-items:center; gap:4px;">
                  ⬇️ Download PDF
                </button>
                <button class="btn-primary-gradient" style="background:linear-gradient(135deg, #059669 0%, #047857 100%); padding:8px 12px; font-size:12px; font-weight:800; display:inline-flex; align-items:center; gap:4px;" onclick="printReportFrame()">
                  🖨️ प्रिंट / PDF सेव्ह करा (Print / Save)
                </button>
                <button class="btn-secondary-outline" onclick="openReportInNewTab()" style="padding:8px 10px; font-size:11.5px; font-weight:700; display:inline-flex; align-items:center; gap:4px;">
                  📱 नवीन टॅबमध्ये उघडा (Fullscreen Tab)
                </button>
                <button class="btn-secondary-outline" onclick="loadInAppPdfPreview()" style="padding:8px 10px; font-size:11.5px; font-weight:700;">
                  🔄 रिफ्रेश करा (Refresh)
                </button>
              </div>
            </div>

            <!-- DIRECT FULL PDF PREVIEW CONTAINER -->
            <div style="width:100%; border-radius:12px; overflow:hidden; box-shadow:0 6px 24px rgba(124,45,18,0.12); margin-bottom:14px; background:#F5EFEB;">
              <iframe id="reportFrame" title="Shivansh Astro-Vastu Full Report Preview" style="width:100%; height:75vh; min-height:540px; border:1.5px solid #D4AF37; border-radius:12px; background:#FFFFFF; display:block;"></iframe>
            </div>

            <!-- Collapsible Dossier & Chapter Settings -->
            <details style="background:#FFFDF9; border:1.5px solid #EADBC8; border-radius:10px; padding:12px 14px; margin-top:8px;">
              <summary style="font-size:12.5px; font-weight:800; color:#7C2D12; cursor:pointer; list-style:none; display:flex; justify-content:space-between; align-items:center;">
                <span>⚙️ कुंडली पॅकेज व अध्यायांची यादी (अध्यायों की सूची)</span>
                <span style="font-size:11px; color:#A8A29E;">▼ Click to expand options</span>
              </summary>
              <div style="margin-top:12px;">
                <h4 style="font-size:12.5px; font-weight:800; color:#7C2D12; margin-bottom:8px;">Select Dossier Package</h4>
                <div class="form-group" style="margin-bottom:12px;">
                  <select id="reportPackageSelect" style="width:100%; height:40px; font-size:12.5px; font-weight:700; color:#7C2D12;" onchange="loadInAppPdfPreview()">
                    <option value="maha">👑 संपूर्ण ८२-पृष्ठीय VIP महा-जन्मपत्रिका (82-Page Master Dossier)</option>
                    <option value="kp_remedies">🔮 के.पी. अचूक उपाय विशेषांक (KP Remedies Special Report - 7 Pages)</option>
                    <option value="laghu">📜 ४-पृष्ठीय लघु कुंडली सारांश (4-Page Summary)</option>
                    <option value="varshaphal">🪐 १०-पृष्ठीय वार्षिक वर्षफळ व लाल किताब (10-Page Varshaphal)</option>
                  </select>
                </div>

                <h4 style="font-size:12px; font-weight:800; color:#7C2D12; margin:10px 0 6px 0;">Included Chapters Checklist</h4>
                <div style="display:grid; grid-template-columns:repeat(auto-fill, minmax(240px, 1fr)); gap:6px; font-size:11px; color:#2E1C10; font-weight:600;">
                  <label><input type="checkbox" checked disabled/> Cover Page &amp; Credentials</label>
                  <label><input type="checkbox" checked disabled/> Panchang &amp; Avakahada Coordinates</label>
                  <label><input type="checkbox" checked disabled/> High-Res Vector D1 &amp; D9 Charts</label>
                  <label><input type="checkbox" checked disabled/> 16 Shodashvarga Charts (D1 to D60)</label>
                  <label><input type="checkbox" checked disabled/> 12 Bhavas Comprehensive Predictions</label>
                  <label><input type="checkbox" checked disabled/> Vimshottari Mahadasha Timelines</label>
                  <label><input type="checkbox" checked disabled/> Classical Doshas (Mangal, Kaal Sarp)</label>
                  <label><input type="checkbox" checked disabled/> Lal Kitab Remedial Measures 1952</label>
                  <label><input type="checkbox" checked disabled/> Shadbala &amp; Ashtakavarga Matrix</label>
                  <label><input type="checkbox" checked disabled/> KP House Cusps &amp; Horary Significators</label>
                </div>

                <div style="margin-top:12px; display:flex; gap:8px; flex-wrap:wrap;">
                  <button class="btn-secondary-outline" id="btnSingleZip" style="display:none;" onclick="downloadSinglePagesZip()">
                    📦 Download Single Pages ZIP (WhatsApp)
                  </button>
                </div>
              </div>
            </details>
          </div>
        </section>

        <!-- =============================================================== -->
        <!-- VIEW 7: PRASHNA KUNDLI -->
        <!-- =============================================================== -->
        <section class="view-pane" id="pane_prashna">
          <div class="glass-card">
            <div class="card-header">
              <span>⏱️ तात्काळ प्रश्न कुंडली (तात्काळ प्रश्न कुंडली - Prashna Horary)</span>
              <button class="btn-primary-gradient" onclick="castInstantPrashna()">🔄 वर्तमान मुहूर्ताची प्रश्न कुंडली पहा (प्रश्न कुंडली)</button>
            </div>
            <p style="font-size:12px; color:#574032; margin-bottom:14px;">
              जातकाच्या प्रश्न विचारण्याच्या अचूक वेळी तात्काळ ग्रह गोचर व नक्षत्र गणिताद्वारे शास्त्रोक्त मार्गदर्शन (Horary Astrology).
            </p>
            <div id="prashnaContainer" style="text-align:center; padding:20px;">
              <p style="color:#6B7280; font-style:italic;">तात्काळ प्रश्न कुंडली तयार करण्यासाठी वरील 'वर्तमान मुहूर्ताची प्रश्न कुंडली पहा' बटनावर क्लिक करा.</p>
            </div>
          </div>
        </section>

        <!-- =============================================================== -->
        <!-- VIEW 8: SETTINGS & BRANDING -->
        <!-- =============================================================== -->
        <section class="view-pane" id="pane_settings">
        <!-- DEMO LICENSE KEYS MANAGER CARD -->
        <div class="glass-card" style="max-width:760px; margin: 0 auto 16px auto;">
          <div class="card-header" style="background:linear-gradient(90deg, #7C2D12 0%, #B45309 100%); color:#fff; display:flex; justify-content:space-between; align-items:center;">
            <span>🔑 ग्राहक डेमो परवाना नियंत्रण (ग्राहक डेमो चाबी नियंत्रण)</span>
            <span class="badge" style="background:#059669; color:#fff;">100% Free Control</span>
          </div>
          <div style="padding:16px; background:#FFFDF9;">
            <p style="font-size:12px; color:#4B5563; margin-top:0;">
              यहाँ से आप अपने ऑनलाइन डेमो ग्राहकों के लिए <strong>डेमो चाबी (Access Key)</strong> बना सकते हैं और कभी भी 1-क्लिक में उनकी एक्सेस <strong>बंद (Stop / Revoke)</strong> कर सकते हैं।
            </p>
            <div style="display:flex; gap:10px; flex-wrap:wrap; align-items:flex-end; background:#FEF3C7; border:1px solid #FDE68A; padding:12px; border-radius:8px; margin-bottom:14px;">
              <div style="flex:2; min-width:180px;">
                <label style="font-size:11px; font-weight:800; color:#78350F;">ग्राहक का नाम (Customer Name)</label>
                <input type="text" id="demoNewClientName" placeholder="e.g. Ramesh Sharma" style="width:100%; height:36px; border:1px solid #D97706; border-radius:5px; padding:0 8px; font-size:12px; font-weight:700; color:#2E1C10; margin-top:2px;"/>
              </div>
              <div style="flex:1.5; min-width:140px;">
                <label style="font-size:11px; font-weight:800; color:#78350F;">डेमो अवधि (Duration)</label>
                <select id="demoNewDuration" style="width:100%; height:36px; border:1px solid #D97706; border-radius:5px; padding:0 8px; font-size:12px; font-weight:700; color:#78350F; margin-top:2px;">
                  <option value="1">1 दिन (24 Hours Demo)</option>
                  <option value="3">3 दिन (3 Days Demo)</option>
                  <option value="7" selected>7 दिन (1 Week Demo)</option>
                  <option value="30">30 दिन (1 Month Access)</option>
                  <option value="0">आजीवन (Unlimited / Life)</option>
                </select>
              </div>
              <button class="btn-primary-gradient" type="button" onclick="generateDemoKey()" style="height:36px; font-size:12px; padding:0 18px;">
                ✨ नवीन डेमो चावी तयार करा (Generate Key)
              </button>
            </div>

            <!-- Active Keys Table -->
            <div style="overflow-x:auto;">
              <table class="dash-table">
                <thead>
                  <tr>
                    <th>ग्राहक (Customer / ग्राहक)</th>
                    <th>डेमो चावी (Key Code / चाबी)</th>
                    <th>मुदत समाप्ती (Expires / समाप्ति)</th>
                    <th>स्थिती (Status / स्थिति)</th>
                    <th>कृती (Action / कार्रवाई)</th>
                  </tr>
                </thead>
                <tbody id="demoKeysTableBody">
                  <tr><td colspan="5" style="text-align:center; color:#6B7280; padding:12px;">Loading keys...</td></tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

          <div class="glass-card" style="max-width:760px; margin: 0 auto;">
            <div class="card-header">
              <span>⚙️ ज्योतिष केंद्र ब्रँडिंग सेटिंग्ज (ब्रांडिंग सेटिंग्स)</span>
            </div>
            <p style="font-size:12px; color:#574032; margin-bottom:16px;">
              These credentials are saved to your offline SQLite database and automatically printed on the Cover Page, Headers, and Footers of all generated client reports.
            </p>

            <!-- LOGO CUSTOMIZER BOX -->
            <div style="display:flex; align-items:center; gap:20px; background:#FEF3C7; border:1.5px solid #FDE68A; padding:14px; border-radius:10px; margin-bottom:18px;">
              <div style="text-align:center;">
                <img id="brand_logo_preview" src="/assets/images/opt_shivansh_logo.jpg" style="width:110px; height:110px; border-radius:50%; border:3px solid #D4AF37; object-fit:cover; box-shadow:0 4px 14px rgba(124,45,18,0.25); background:#fff;"/>
                <div style="font-size:10px; color:#78350F; font-weight:700; margin-top:4px;">सध्याचा लोगो (Current Logo)</div>
              </div>
              <div style="flex:1;">
                <h4 style="margin:0 0 4px 0; color:#7C2D12; font-size:13px;">📷 ज्योतिष केंद्र अधिकृत लोगो (Official Logo)</h4>
                <p style="font-size:11px; color:#574032; margin:0 0 10px 0; line-height:1.4;">
                  येथून तुम्ही आपल्या ज्योतिष केंद्राचा नवीन लोगो अपलोड करू शकता. हा लोगो पीडीएफ मुखपृष्ठ (Cover Page) आणि अनुक्रमणिकेवर लगेच आपोआप मुद्रित होईल.
                </p>
                <div style="display:flex; gap:8px; flex-wrap:wrap;">
                  <input type="file" id="brand_logo_file" accept="image/*" onchange="previewAndEncodeLogo(event)" style="display:none;"/>
                  <button type="button" class="btn-primary-gradient" onclick="document.getElementById('brand_logo_file').click()" style="padding:6px 14px; font-size:11.5px;">
                    📸 नवीन लोगो निवडा (Change Logo)
                  </button>
                  <button type="button" class="btn-table-action" onclick="resetDefaultLogo()" style="padding:6px 14px; font-size:11.5px;">
                    ↺ मूळ लोगो (Reset Default)
                  </button>
                </div>
                <input type="hidden" id="brand_logo_data" value=""/>
              </div>
            </div>

            <div class="form-grid">
              <div class="form-group" style="grid-column: span 2;">
                <label>Astrologer Name (ज्योतिषाचार्य नाव)</label>
                <input type="text" id="brand_astro_name" placeholder="e.g. Mayur Mandhare (BE.E&TC)"/>
              </div>
              <div class="form-group" style="grid-column: span 2;">
                <label>Jyotish Kendra / Firm Name (संस्थान / ब्रँड नाव)</label>
                <input type="text" id="brand_kendra_name" placeholder="e.g. Shivansh Astro-Vastu"/>
              </div>
            </div>

            <div class="form-grid">
              <div class="form-group">
                <label>फोन / व्हॉट्सॲप (Phone / WhatsApp)</label>
                <input type="text" id="brand_phone" placeholder="e.g. +91 98765 43210"/>
              </div>
              <div class="form-group">
                <label>ईमेल पत्ता (Email Address)</label>
                <input type="email" id="brand_email" placeholder="e.g. consult@shivanshastrovastu.com"/>
              </div>
            </div>

            <div class="form-group" style="margin-bottom:12px;">
              <label>Office / Temple Address (कार्यालय पता)</label>
              <input type="text" id="brand_address" placeholder="e.g. Sector 14, Bikaner / Delhi, India"/>
            </div>

            <div class="form-group" style="margin-bottom:18px;">
              <label>Tagline / Moto (प्रचार वाक्य)</label>
              <input type="text" id="brand_tagline" placeholder="e.g. Ancient Vedic, KP &amp; Lal Kitab Astrological Insights"/>
            </div>

            <div style="display:flex; justify-content:space-between; align-items:center;">
              <button class="btn-primary-gradient" onclick="saveBrandingSettings()">
                💾 ब्रँडिंग व सेटिंग्ज सेव्ह करा (सेव करें)
              </button>
              <span id="brandSaveStatus" style="font-size:12px; font-weight:700; color:#166534; display:none;">
                ✓ Saved to SQLite Database!
              </span>
            </div>
          </div>
        </section>

      </main>
    </div>
  </div>

  <!-- Native-Grade Mobile Bottom Navigation Dock -->
  <nav class="mobile-bottom-bar" id="mobileBottomBar">
    <button class="mob-tab-btn active" id="mobtab_dashboard" onclick="switchNav('dashboard')" aria-label="Dashboard">
      <span class="mob-icon">📊</span>
      <span class="mob-label">डॅशबोर्ड</span>
    </button>
    <button class="mob-tab-btn" id="mobtab_new_kundli" onclick="switchNav('new_kundli')" aria-label="New Kundli">
      <span class="mob-icon">➕</span>
      <span class="mob-label">नवीन कुंडली</span>
    </button>
    <button class="mob-tab-btn" id="mobtab_workspace" onclick="switchNav('workspace')" aria-label="Charts Workspace">
      <span class="mob-icon">🪐</span>
      <span class="mob-label">वर्कस्पेस</span>
    </button>
    <button class="mob-tab-btn" id="mobtab_milan" onclick="switchNav('milan')" aria-label="Kundli Milan">
      <span class="mob-icon">💍</span>
      <span class="mob-label">विवाह मिलान</span>
    </button>
    <button class="mob-tab-btn" id="mobtab_settings" onclick="switchNav('settings')" aria-label="Settings">
      <span class="mob-icon">⚙️</span>
      <span class="mob-label">सेटिंग्ज</span>
    </button>
  </nav>

  <!-- Filmora-Style Luxury Progress Modal with Live Countdown -->
  <div id="loadingModal">
    <div class="modal-content-box">
      <div class="chakra-spinner">☸</div>
      <h3 style="color:#FEF08A; font-size:17px; font-weight:900; letter-spacing:1.5px; margin-bottom:6px;">COMPILING VEDIC HOROSCOPE</h3>
      <div id="loadingCountdownWrap" style="background:rgba(0,0,0,0.35); border:1.2px solid #D97706; border-radius:20px; padding:3px 14px; margin-bottom:10px; display:inline-flex; align-items:center; gap:8px;">
        <span style="font-size:14px;">⏱️</span>
        <span style="color:#FEF08A; font-size:12px; font-weight:800;">अंदाजे वेळ शिल्लक: <span id="loadingCountdownSecs" style="font-size:15px; color:#38BDF8; font-weight:900;">15</span> सेकंद (Estimated Time: 15s)</span>
      </div>
      <p id="loadingStageText" style="color:#FED7AA; font-size:12px; margin-bottom:14px; min-height:18px;">Initializing calculations...</p>

      <div class="progress-bar-wrap">
        <div id="loadingBarFill" class="progress-bar-fill"></div>
      </div>

      <div style="display:flex; justify-content:space-between; font-size:10.5px; color:#D6D3D1; font-weight:600;">
        <span id="loadingPercentText">10%</span>
        <span>High-Precision Vector Engine</span>
      </div>
    </div>
  </div>

  <!-- Javascript Logic -->
  <script>
    // === NATIVE DESKTOP NOTIFICATION / TOAST SYSTEM (Replaces ugly browser alerts) ===
    function showNativeToast(message, type) {
      let toast = document.getElementById('nativeAppToast');
      if (!toast) {
        toast = document.createElement('div');
        toast.id = 'nativeAppToast';
        toast.style.cssText = `
          position: fixed;
          top: 24px;
          right: 28px;
          z-index: 99999999;
          min-width: 320px;
          max-width: 480px;
          background: linear-gradient(135deg, #1C0F08 0%, #2A170C 100%);
          border: 1.5px solid #D4AF37;
          border-left: 6px solid #F59E0B;
          border-radius: 10px;
          box-shadow: 0 16px 40px rgba(0,0,0,0.7), 0 0 20px rgba(212,175,55,0.25);
          padding: 14px 18px;
          color: #FEF3C7;
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
          font-size: 13.5px;
          line-height: 1.5;
          display: flex;
          align-items: flex-start;
          gap: 12px;
          opacity: 0;
          transform: translateY(-20px);
          transition: all 0.35s cubic-bezier(0.16, 1, 0.3, 1);
          pointer-events: auto;
        `;
        document.body.appendChild(toast);
      }

      let icon = 'ℹ️';
      let borderColor = '#F59E0B';
      let strMsg = String(message || '');
      if (strMsg.toLowerCase().includes('error') || strMsg.toLowerCase().includes('fail') || strMsg.toLowerCase().includes('required')) {
        icon = '⚠️';
        borderColor = '#EF4444';
      } else if (strMsg.toLowerCase().includes('success') || strMsg.toLowerCase().includes('saved') || strMsg.toLowerCase().includes('यशस्वी') || strMsg.toLowerCase().includes('सज्ज')) {
        icon = '✅';
        borderColor = '#10B981';
      }

      toast.style.borderLeftColor = borderColor;
      toast.innerHTML = `
        <span style="font-size: 22px; line-height: 1; margin-top: 1px;">${icon}</span>
        <div style="flex: 1; word-break: break-word;">
          <div style="font-weight: 800; color: #FDE68A; margin-bottom: 3px; font-size: 11.5px; text-transform: uppercase; letter-spacing: 0.8px;">
            Shivansh Astro-Vastu Suite
          </div>
          <div style="color: #F9FAFB; font-size: 13px; font-weight: 500;">
            ${strMsg.split(String.fromCharCode(10)).join('<br/>')}
          </div>
        </div>
        <button onclick="dismissNativeToast()" style="background:none; border:none; color:#D1D5DB; cursor:pointer; font-size:16px; font-weight:bold; padding:0 4px; margin-left:6px;">✕</button>
      `;

      toast.style.opacity = '1';
      toast.style.transform = 'translateY(0)';

      clearTimeout(toast._timer);
      toast._timer = setTimeout(dismissNativeToast, 5000);
    }

    function dismissNativeToast() {
      const toast = document.getElementById('nativeAppToast');
      if (toast) {
        toast.style.opacity = '0';
        toast.style.transform = 'translateY(-20px)';
      }
    }

    // Globally override window.alert so no browser dialog ever pops up
    window.alert = function(msg) {
      showNativeToast(msg);
    };

    // Prevent default browser right-click context menu (Feels 100% Native)
    document.addEventListener('contextmenu', function(e) {
      if (e.target && (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA')) {
        return true;
      }
      e.preventDefault();
      return false;
    });

    
        // 🌟 MARATHI LOCALIZATION HELPERS (Authentic Marathi + Hindi in Brackets)
    const MR_TERM_MAP = {
      // Planets
      'Sun': 'सूर्य (सूर्य)', 'Moon': 'चंद्र (चंद्र)', 'Mars': 'मंगळ (मंगल)',
      'Mercury': 'बुध (बुध)', 'Jupiter': 'गुरु (बृहस्पति)', 'Venus': 'शुक्र (शुक्र)',
      'Saturn': 'शनी (शनि)', 'Rahu': 'राहू (राहु)', 'Ketu': 'केतू (केतु)',
      'Uranus': 'हर्षल (हर्षल)', 'Neptune': 'नेपच्यून (नेपच्यून)', 'Pluto': 'प्लूटो (प्लूटो)',
      'Ascendant': 'लग्न (लग्न)', 'ASC': 'लग्न (लग्न)', 'Lagna': 'लग्न (लग्न)',
      // Rashis
      'Aries': 'मेष (मेष)', 'Taurus': 'वृषभ (वृषभ)', 'Gemini': 'मिथुन (मिथुन)',
      'Cancer': 'कर्क (कर्क)', 'Leo': 'सिंह (सिंह)', 'Virgo': 'कन्या (कन्या)',
      'Libra': 'तूळ (तुला)', 'Scorpio': 'वृश्चिक (वृश्चिक)', 'Sagittarius': 'धनु (धनु)',
      'Capricorn': 'मकर (मकर)', 'Aquarius': 'कुंभ (कुंभ)', 'Pisces': 'मीन (मीन)',
      // Dignities
      'Exalted': 'उच्च (उच्च)', 'Debilitated': 'नीच (नीच)', 'Own Sign': 'स्वराशी (स्वराशि)',
      'Moolatrikona': 'मूळत्रिकोण (मूलत्रिकोण)', 'Great Friend': 'अधिमित्र (अधिमित्र)',
      'Friend': 'मित्र (मित्र)', 'Neutral': 'सम (सम)', 'Enemy': 'शत्रू (शत्रु)',
      'Great Enemy': 'अधिशत्रू (अधिशत्रु)', 'Combust': 'अस्त (अस्त)', 'Normal': 'सामान्य (सामान्य)',
      // Status
      'Retrograde': 'वक्री (वक्र)', 'Direct': 'मार्गी (मार्गी)'
    };

    function toMr(text) {
      if (!text) return '';
      const s = String(text).trim();
      if (MR_TERM_MAP[s]) return MR_TERM_MAP[s].split(' ')[0];
      return s;
    }

    function toMrWithHi(text) {
      if (!text) return '';
      const s = String(text).trim();
      if (MR_TERM_MAP[s]) {
        return (currentLang === 'mr') ? MR_TERM_MAP[s] : (currentLang === 'hi' ? s : s);
      }
      return s;
    }
    let currentKundliData = null;
    let currentLang = 'mr';
    let currentActiveNav = 'new_kundli';
    let currentChartStyle = 'north';
    let currentDivisional = 'D9';
    let currentSingleZipUrl = null;
    let searchDebounceTimer = null;

    // View Switching (Forced Style Display)
    
    function toggleMobileSidebar(force) {
      const sb = document.querySelector('.desktop-sidebar');
      const bd = document.getElementById('sidebarBackdrop');
      if (!sb) return;
      if (typeof force === 'boolean') {
        if (force) { sb.classList.add('open'); if (bd) bd.classList.add('open'); }
        else { sb.classList.remove('open'); if (bd) bd.classList.remove('open'); }
      } else {
        sb.classList.toggle('open');
        if (bd) bd.classList.toggle('open');
      }
    }

    function switchNav(viewId) {
      currentActiveNav = viewId;
      // Update Mobile Bottom Bar
      document.querySelectorAll('.mob-tab-btn').forEach(btn => btn.classList.remove('active'));
      const activeMobTab = document.getElementById('mobtab_' + viewId);
      if (activeMobTab) activeMobTab.classList.add('active');
      if (window.innerWidth <= 768) { toggleMobileSidebar(false); }
      console.log('[Nav] Switching to view:', viewId);
      try {
        document.querySelectorAll('.nav-btn').forEach(btn => btn.classList.remove('active'));
        const activeBtn = document.getElementById('nav_' + viewId);
        if (activeBtn) activeBtn.classList.add('active');

        document.querySelectorAll('.view-pane').forEach(p => {
          p.classList.remove('active');
          p.style.display = 'none';
        });

        const pane = document.getElementById('pane_' + viewId);
        if (pane) {
          pane.classList.add('active');
          pane.style.display = 'block';
        }

        const isMobScreen = window.innerWidth <= 768;
        const titles = isMobScreen ? {
          'dashboard': '📊 डॅशबोर्ड',
          'new_kundli': '➕ नवीन कुंडली',
          'clients': '👥 ग्राहक CRM',
          'workspace': '🪐 कुंडली वर्कस्पेस',
          'milan': '💍 विवाह मिलान',
          'reports': '📄 अहवाल स्टुडिओ',
          'prashna': '⏱️ प्रश्न कुंडली',
          'settings': '⚙️ सेटिंग्ज'
        } : {
          'dashboard': '📊 एक्झिक्युटिव्ह ज्योतिष डॅशबोर्ड (Executive Dashboard)',
          'new_kundli': '➕ नवीन कुंडली नोंदणी (New Kundli Registration)',
          'clients': '👥 ग्राहक सल्लामसलत डिरेक्टरी (Client CRM)',
          'workspace': '🪐 इंटरॅक्टिव्ह कुंडली वर्कस्पेस (Kundli Workspace)',
          'milan': '💍 अष्टकूट ३६ गुण विवाह मिलान (Kundli Milan)',
          'reports': '📄 ५६-पृष्ठीय VIP अहवाल स्टुडिओ (Report Studio)',
          'prashna': '⏱️ तात्काळ प्रश्न कुंडली (Horary Prashna)',
          'settings': '⚙️ ज्योतिष केंद्र ब्रँडिंग सेटिंग्ज (Settings)'
        };
        const titleEl = document.getElementById('topbarTitle');
        if (titleEl) titleEl.innerHTML = titles[viewId] || 'Shivansh Astro-Vastu';

        if (viewId === 'dashboard') loadDashboard();
        if (viewId === 'new_kundli') resetNewKundliForm();
        if (viewId === 'clients') loadClientsTable();
        if (viewId === 'reports') updateReportStudioState();
        if (viewId === 'settings') loadBrandingSettings();
      } catch (err) {
        console.error('[Nav] switchNav error:', err);
      }
    }

    function closeDesktopApp() {
      if (confirm('Are you sure you want to exit Shivansh Astro-Vastu?')) {
        fetch('/api/shutdown', {method: 'POST'}).catch(()=>{});
        window.close();
      }
    }

    // Dashboard Data Loader
    async function loadDashboard() {
      // 1. Independent Client Fetch
      let clients = [];
      const tbody = document.getElementById('dashRecentClientsBody');
      const tc = document.getElementById('dashTotalClients');
      try {
        const cRes = await fetch('/api/clients');
        if (cRes.ok) {
          const cData = await cRes.json();
          clients = cData.clients || [];
          if (tc) tc.innerText = clients.length;
          if (tbody) {
            if (clients.length === 0) {
              tbody.innerHTML = '<tr><td colspan="7" style="padding:16px; color:#6B7280; font-style:italic;">No clients saved yet. Click "+ Add Client" to create one.</td></tr>';
            } else {
              tbody.innerHTML = clients.slice(0, 6).map(c => `
                <tr>
                  <td style="font-weight:800; color:#7C2D12;">${c.name}</td>
                  <td>${c.sex || 'Male'}</td>
                  <td style="font-weight:600;">${c.day}/${c.month}/${c.year}</td>
                  <td style="font-family:monospace; font-weight:700;">${String(c.hour).padStart(2,'0')}:${String(c.minute).padStart(2,'0')}</td>
                  <td>${c.place}</td>
                  <td><span class="badge">${c.category || 'General'}</span></td>
                  <td>
                    <button class="btn-table-action" onclick="loadClientIntoKundli(${c.id})">🔮 कुंडली पहा (Open)</button>
                    <button class="btn-table-action" style="color:#DC2626; border-color:#FCA5A5;" onclick="deleteClientRecord(${c.id})">🗑️ हटवा (Delete)</button>
                  </td>
                </tr>
              `).join('');
            }
          }
        } else {
          if (tbody) tbody.innerHTML = '<tr><td colspan="7" style="padding:14px; color:#DC2626; font-weight:600;">Notice: Server starting up or connecting. <button onclick="loadDashboard()" style="padding:2px 8px; border-radius:4px; background:#7C2D12; color:#FFF; border:none; cursor:pointer;">Retry 🔄</button></td></tr>';
        }
      } catch (e) {
        console.warn('Clients fetch notice:', e);
        if (tbody) tbody.innerHTML = '<tr><td colspan="7" style="padding:14px; color:#DC2626; font-weight:600;">Server starting up. <button onclick="loadDashboard()" style="padding:2px 8px; border-radius:4px; background:#7C2D12; color:#FFF; border:none; cursor:pointer;">Retry 🔄</button></td></tr>';
      }

      // 2. Independent Reports Fetch
      let reports = [];
      const rbody = document.getElementById('dashRecentReportsBody');
      const tr = document.getElementById('dashTotalReports');
      try {
        const rRes = await fetch('/api/reports');
        if (rRes.ok) {
          const rData = await rRes.json();
          reports = rData.reports || [];
          if (tr) tr.innerText = reports.length;
          if (rbody) {
            if (reports.length === 0) {
              rbody.innerHTML = '<tr><td colspan="4" style="padding:16px; color:#6B7280; font-style:italic;">No PDF dossiers generated yet. Create a Kundli or Milan to generate reports.</td></tr>';
            } else {
              rbody.innerHTML = reports.slice(0, 6).map(r => `
                <tr>
                  <td style="font-weight:700; color:#1E3A8A;">${r.filename}</td>
                  <td>${r.size_mb} MB</td>
                  <td style="font-size:11.5px; color:#6B7280;">${r.modified}</td>
                  <td>
                    <a href="${r.download_url}" target="_blank" class="btn-table-action" style="text-decoration:none; display:inline-block;">📥 PDF डाउनलोड</a>
                  </td>
                </tr>
              `).join('');
            }
          }
        } else {
          if (rbody) rbody.innerHTML = '<tr><td colspan="4" style="padding:14px; color:#6B7280; font-style:italic;">No PDF dossiers generated yet.</td></tr>';
        }
      } catch (e) {
        console.warn('Reports fetch notice:', e);
        if (rbody) rbody.innerHTML = '<tr><td colspan="4" style="padding:14px; color:#6B7280; font-style:italic;">No PDF dossiers generated yet.</td></tr>';
      }
    }

    async function loadClientsTable() {
      const q = document.getElementById('clientsSearchInput') ? document.getElementById('clientsSearchInput').value.trim() : '';
      try {
        const res = await fetch('/api/clients?q=' + encodeURIComponent(q));
        const data = await res.json();
        const clients = data.clients || [];
        const tbody = document.getElementById('clientsFullTableBody');
        if (clients.length === 0) {
          tbody.innerHTML = '<tr><td colspan="9" style="padding:18px; color:#6B7280; font-style:italic;">No clients match query.</td></tr>';
          return;
        }
        tbody.innerHTML = clients.map(c => `
          <tr>
            <td style="color:#78716C; font-weight:700;">#${c.id}</td>
            <td style="font-weight:800; color:#7C2D12;">${c.name}</td>
            <td>${c.sex || 'Male'}</td>
            <td style="font-weight:600;">${c.day}/${c.month}/${c.year} ${String(c.hour).padStart(2,'0')}:${String(c.minute).padStart(2,'0')}</td>
            <td>${c.place}</td>
            <td>${c.phone || '-'}</td>
            <td><span class="badge">${c.category || 'General'}</span></td>
            <td style="font-size:11px; color:#78716C;">${c.created_at ? c.created_at.split(' ')[0] : '-'}</td>
            <td>
              <button class="btn-table-action" onclick="openClientInWorkspace(${c.id})">🪐 कुंडली (Open)</button>
              <button class="btn-table-action" onclick="openClientInReports(${c.id})">📄 PDF अहवाल</button>
              <button class="btn-table-action" onclick="editClientInForm(${c.id})">✏️ संपादन (Edit)</button>
              <button class="btn-table-del" onclick="deleteClientRecord(${c.id})">🗑️</button>
            </td>
          </tr>
        `).join('');
      } catch (e) {
        console.error(e);
      }
    }

    // Open Client in Workspace
    async function openClientInWorkspace(id) {
      await loadClientDataIntoForm(id);
      switchNav('workspace');
      calculateKundli();
    }

    // Open Client in Report Studio
    async function openClientInReports(id) {
      await loadClientDataIntoForm(id);
      switchNav('reports');
      calculateKundli();
    }

    // Edit Client in Form
    async function editClientInForm(id) {
      await loadClientDataIntoForm(id);
      switchNav('new_kundli');
    }

    async function loadClientDataIntoForm(id) {
      const res = await fetch('/api/clients/' + id);
      const data = await res.json();
      const c = data.client;
      if (!c) return;
      document.getElementById('clientId').value = c.id;
      document.getElementById('name').value = c.name;
      document.getElementById('sex').value = c.sex || 'Male';
      document.getElementById('year').value = c.year;
      document.getElementById('month').value = c.month;
      document.getElementById('day').value = c.day;
      document.getElementById('hour').value = c.hour;
      document.getElementById('minute').value = c.minute;
      document.getElementById('second').value = c.second || 0;
      document.getElementById('place').value = c.place;
      document.getElementById('lat').value = c.lat;
      document.getElementById('lon').value = c.lon;
      document.getElementById('tz').value = c.tz || 5.5;
      document.getElementById('phone').value = c.phone || '';
      document.getElementById('email').value = c.email || '';
      document.getElementById('category').value = c.category || 'General Consultation';
      document.getElementById('notes').value = c.notes || '';
      updateActiveClientBadges(c.name, c.day, c.month, c.year, c.place);
    }

    async function deleteClientRecord(id) {
      if (!confirm('Are you sure you want to delete client record #' + id + '?')) return;
      await fetch('/api/clients/' + id, {method: 'DELETE'});
      loadDashboard();
      loadClientsTable();
    }

    function resetKundliForm() {
      document.getElementById('clientId').value = '';
      document.getElementById('name').value = '';
      document.getElementById('day').value = '';
      document.getElementById('month').value = '';
      document.getElementById('year').value = '';
      document.getElementById('hour').value = '';
      document.getElementById('minute').value = '';
      document.getElementById('second').value = '0';
      document.getElementById('phone').value = '';
      document.getElementById('email').value = '';
      document.getElementById('notes').value = '';
    }

    // City Autocomplete
    function onCitySearchType() {
      clearTimeout(searchDebounceTimer);
      const q = document.getElementById('citySearchInput').value.trim();
      if (q.length < 2) {
        document.getElementById('citySuggestions').style.display = 'none';
        return;
      }
      searchDebounceTimer = setTimeout(async () => {
        const res = await fetch('/api/cities?q=' + encodeURIComponent(q));
        const data = await res.json();
        const drop = document.getElementById('citySuggestions');
        if (data.cities && data.cities.length > 0) {
          drop.innerHTML = data.cities.map(c => `
            <div class="city-opt" onclick="selectCity('${c.name.replace(/'/g, "\\'")}', ${c.lat}, ${c.lon}, ${c.tz})">
              <strong>${c.name}</strong>, ${c.state || ''} (${c.country || 'India'})
            </div>
          `).join('');
          drop.style.display = 'block';
        } else {
          drop.style.display = 'none';
        }
      }, 250);
    }

    function selectCity(name, lat, lon, tz) {
      document.getElementById('place').value = name;
      document.getElementById('lat').value = lat;
      document.getElementById('lon').value = lon;
      document.getElementById('tz').value = tz;
      document.getElementById('citySuggestions').style.display = 'none';
      document.getElementById('citySearchInput').value = name;
    }

    // Completely Reset New Kundli Form to Pristine Clean State
    function resetNewKundliForm() {
      const ids = ['name', 'day', 'month', 'year', 'hour', 'minute', 'second', 'citySearchInput', 'place', 'lat', 'lon', 'phone', 'email', 'notes', 'clientId'];
      ids.forEach(id => {
        const el = document.getElementById(id);
        if (el) el.value = '';
      });
      const tzEl = document.getElementById('tz');
      if (tzEl) tzEl.value = '5.5';
      const varshaEl = document.getElementById('varsha_year');
      if (varshaEl) varshaEl.value = new Date().getFullYear();
      const sexEl = document.getElementById('sex');
      if (sexEl) sexEl.value = 'Male';
      const catEl = document.getElementById('category');
      if (catEl) catEl.value = 'General Consultation';
      const sug = document.getElementById('citySuggestions');
      if (sug) { sug.innerHTML = ''; sug.style.display = 'none'; }
    }

    // Save Client Record
    async function saveClientRecordOnly() {
      const payload = getFormPayload();
      if (!payload.name) { alert('Please enter client name'); return; }
      try {
        const res = await fetch('/api/clients', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify(payload)
        });
        const data = await res.json();
        const cid = data.id || data.client_id;
        if (cid) {
          document.getElementById('clientId').value = cid;
          alert('Client record #' + cid + ' saved to offline SQLite database successfully!');
          loadDashboard();
        } else {
          alert('Saved to CRM successfully!');
          loadDashboard();
        }
      } catch (err) {
        alert('Error saving client: ' + err);
      }
    }

    async function calculateAndOpenWorkspace() {
      const payload = getFormPayload();
      if (!validateInputs(payload)) return;

      // Save to CRM
      try {
        const cRes = await fetch('/api/clients', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify(payload)
        });
        const cData = await cRes.json();
        const cid = cData.id || cData.client_id;
        if (cid) document.getElementById('clientId').value = cid;
      } catch (e) {}

      switchNav('workspace');
      calculateKundli();
    }

    function getFormPayload() {
      const getVal = (id, fallback = '') => {
        const el = document.getElementById(id);
        return el ? el.value : fallback;
      };
      const idVal = getVal('clientId', '');
      return {
        id: idVal ? parseInt(idVal) : null,
        name: getVal('name', '').trim(),
        sex: getVal('sex', 'Male'),
        year: parseInt(getVal('year', '')) || null,
        month: parseInt(getVal('month', '')) || null,
        day: parseInt(getVal('day', '')) || null,
        hour: parseInt(getVal('hour', '')),
        minute: parseInt(getVal('minute', '')),
        second: parseInt(getVal('second', '0')) || 0,
        place: getVal('place', 'New Delhi').trim() || 'New Delhi',
        lat: parseFloat(getVal('lat', '28.6139')) || 28.6139,
        lon: parseFloat(getVal('lon', '77.2090')) || 77.2090,
        tz: parseFloat(getVal('tz', '5.5')) || 5.5,
        phone: getVal('phone', '').trim(),
        email: getVal('email', '').trim(),
        category: getVal('category', 'General Consultation'),
        notes: getVal('notes', '').trim(),
        varsha_year: parseInt(getVal('varsha_year', '2026')) || 2026,
        lang: currentLang,
        report_package: getVal('reportPackageSelect', 'maha')
      };
    }

    function validateInputs(p) {
      const errors = [];
      if (!p.name) errors.push('Client Name');
      if (p.day === null || p.day < 1 || p.day > 31) errors.push('Valid Birth Day (1-31)');
      if (p.month === null || p.month < 1 || p.month > 12) errors.push('Valid Birth Month (1-12)');
      if (p.year === null || p.year < 1800 || p.year > 2100) errors.push('Valid Birth Year (1800-2100)');
      if (isNaN(p.hour) || p.hour < 0 || p.hour > 23) errors.push('Valid Birth Hour (0-23)');
      if (isNaN(p.minute) || p.minute < 0 || p.minute > 59) errors.push('Valid Birth Minute (0-59)');
      if (errors.length > 0) {
        alert('Please fill the following required birth parameters:\\n- ' + errors.join('\\n- '));
        return false;
      }
      return true;
    }

    // Core Kundli Calculation
    async function calculateKundli() {
      const payload = getFormPayload();
      if (!validateInputs(payload)) return;

      updateWorkspaceTimeDisplay();
      document.getElementById('statusPill').innerText = '⏳ Calculating...';

      const modal = document.getElementById('loadingModal');
      const bar = document.getElementById('loadingBarFill');
      const txt = document.getElementById('loadingStageText');
      const pct = document.getElementById('loadingPercentText');
      if (modal) {
        modal.style.display = 'flex';
        modal.style.pointerEvents = 'auto';
        if (bar) bar.style.width = '35%';
        if (txt) txt.innerText = '✨ Calculating Planetary Coordinates & Shodashvarga Charts...';
        if (pct) pct.innerText = '40%';
      }

      try {
        const res = await fetch('/api/kundli-details', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (!data.success) {
          alert('Calculation Error: ' + (data.message || data.error));
          document.getElementById('statusPill').innerText = '⚠️ Error';
          return;
        }

        currentKundliData = data;
        updateActiveClientBadges(payload.name, payload.day, payload.month, payload.year, payload.place);

        // Stats Strip
        document.getElementById('statLagna').innerText = data.meta.lagna_en + ' (' + data.meta.lagna_hi + ')';
        document.getElementById('statRasi').innerText = data.meta.rasi_en + ' (' + data.meta.rasi_hi + ')';
        document.getElementById('statNakshatra').innerText = data.meta.nakshatra_en;
        document.getElementById('statManglik').innerText = data.manglik.status_en;
        document.getElementById('statDasha').innerText = data.vimshottari.balance_str;

        // Active Dasha
        if (data.active_dasha && data.active_dasha.summary) {
          document.getElementById('txtActiveDasha').innerText = data.active_dasha.summary;
          document.getElementById('txtDashaValid').innerText = data.active_dasha.end_date ? ('Valid till ' + data.active_dasha.end_date) : '';
        }

        // Render Sub-modules defensively so no single widget ever breaks calculation
        try { renderD1Svg(); } catch (e) { console.warn('renderD1Svg error:', e); }
        try { onDivisionalChange(); } catch (e) { console.warn('onDivisionalChange error:', e); }
        try { renderPlanetsTable(data.planets); } catch (e) { console.warn('renderPlanetsTable error:', e); }
        try { renderBhavas(data.bhavas); } catch (e) { console.warn('renderBhavas error:', e); }
        try { renderDashaAndGems(data); } catch (e) { console.warn('renderDashaAndGems error:', e); }
        try { renderDoshas(data.doshas); } catch (e) { console.warn('renderDoshas error:', e); }
        try { renderYogas(data.yogas); } catch (e) { console.warn('renderYogas error:', e); }
        try { renderShadbalaAndSAV(data); } catch (e) { console.warn('renderShadbalaAndSAV error:', e); }

        // Render New Advanced VIP Modules
        try { if (data.kp) renderKPSystem(data.kp, data); } catch (e) { console.warn('renderKPSystem error:', e); }
        try { if (data.lal_kitab) renderLalKitab(data.lal_kitab); } catch (e) { console.warn('renderLalKitab error:', e); }
        try { if (data.gemstones) renderGemstonesAndYantras(data); } catch (e) { console.warn('renderGemstonesAndYantras error:', e); }
        try { if (data.avkahada || data.favourable) renderAvkahadaAndFavourable(data); } catch (e) { console.warn('renderAvkahadaAndFavourable error:', e); }

        document.getElementById('statusPill').innerText = '✨ सज्ज • १००% अचूक';
        try { loadInAppPdfPreview(); } catch (e) { console.warn('loadInAppPdfPreview error:', e); }
      } catch (err) {
        console.error('calculateKundli error:', err);
        document.getElementById('statusPill').innerText = '⚠️ ' + (err.message || 'Calculation Error');
      } finally {
        if (modal) {
          if (bar) bar.style.width = '100%';
          if (pct) pct.innerText = '100%';
          setTimeout(() => {
            modal.style.display = 'none';
            modal.style.pointerEvents = 'none';
          }, 350);
        }
      }
    }

    // Birth-Time Adjustment (+/- 1m, +/- 5m)
    function adjustBirthTime(deltaMin) {
      let h = parseInt(document.getElementById('hour').value);
      let m = parseInt(document.getElementById('minute').value);
      let d = parseInt(document.getElementById('day').value);
      let mo = parseInt(document.getElementById('month').value);
      let y = parseInt(document.getElementById('year').value);

      if (isNaN(h) || isNaN(m)) {
        alert('Please fill hour and minute first.');
        return;
      }

      let totalMin = h * 60 + m + deltaMin;
      if (totalMin < 0) {
        totalMin += 24 * 60;
        d -= 1;
        if (d < 1) { mo -= 1; if (mo < 1) { mo = 12; y -= 1; } d = 28; }
      } else if (totalMin >= 24 * 60) {
        totalMin -= 24 * 60;
        d += 1;
        if (d > 28) { d = 1; mo += 1; if (mo > 12) { mo = 1; y += 1; } }
      }

      document.getElementById('hour').value = Math.floor(totalMin / 60);
      document.getElementById('minute').value = totalMin % 60;
      document.getElementById('day').value = d;
      document.getElementById('month').value = mo;
      document.getElementById('year').value = y;

      updateWorkspaceTimeDisplay();
      calculateKundli();
    }

    function updateWorkspaceTimeDisplay() {
      const h = String(document.getElementById('hour').value || '0').padStart(2, '0');
      const m = String(document.getElementById('minute').value || '0').padStart(2, '0');
      const s = String(document.getElementById('second').value || '0').padStart(2, '0');
      document.getElementById('workspaceTimeDisplay').innerText = `${h}:${m}:${s}`;
    }

    function updateActiveClientBadges(name, d, m, y, place) {
      const tag = `${name} (${d}/${m}/${y} • ${place})`;
      document.getElementById('sidebarActiveClientName').innerText = name || 'Client';
      document.getElementById('dashActiveClient').innerText = name || 'Ready';
      document.getElementById('workspaceNativeTag').innerText = tag;
      document.getElementById('reportNativeBadge').innerText = 'Active Native: ' + tag;
    }

    // Chart Renderers
    function renderD1Svg() {
      if (!currentKundliData || !currentKundliData.charts) return;
      const c = currentKundliData.charts;
      const svg = currentChartStyle === 'south' ? c.south : (currentChartStyle === 'east' ? c.east : c.north);
      document.getElementById('chartSvgWrapper').innerHTML = svg;
    }

    function onDivisionalChange() {
      if (!currentKundliData) return;
      const code = document.getElementById('divisionalSelect').value;
      currentDivisional = code;

      const subTags = {
        "D9": "D9 Navamsha • Dharma & Spouse Arc (3°20')",
        "D10": "D10 Dashamsha • Career & Status Arc (3°00')",
        "D2": "D2 Hora • Wealth Arc (15°00')",
        "D3": "D3 Drekkana • Siblings Arc (10°00')",
        "D4": "D4 Chaturthamsha • Fortune Arc (7°30')",
        "D7": "D7 Saptamsha • Children Arc (4°17')",
        "D12": "D12 Dwadashamsha • Parents Arc (2°30')",
        "D16": "D16 Shodashamsha • Vehicles Arc (1°52')",
        "D20": "D20 Vimshamsha • Spirituality Arc (1°30')",
        "D24": "D24 Chaturvimshamsha • Learning Arc (1°15')",
        "D27": "D27 Saptavimshamsha • Strengths Arc (1°06')",
        "D30": "D30 Trimshamsha • Arishta Arc (1°00')",
        "D40": "D40 Khavedamsha • Karma Arc (0°45')",
        "D45": "D45 Akshavedamsha • Character Arc (0°40')",
        "D60": "D60 Shashtiamsha • Past Life Karma Arc (0°30')",
        "TRANSIT": "Real-Time Planetary Transit (आज का गोचर)"
      };
      document.getElementById('divisionalSubTag').innerText = subTags[code] || 'Harmonic Arc';

      let svg = '';
      if (code === 'TRANSIT') {
        const c = currentKundliData.charts;
        svg = currentChartStyle === 'south' ? c.transit_south : c.transit_north;
      } else if (currentKundliData.vargas && currentKundliData.vargas[code]) {
        const ch = currentKundliData.vargas[code];
        svg = currentChartStyle === 'south' ? ch.south : (currentChartStyle === 'east' ? ch.east : ch.north);
      } else if (code === 'D9') {
        const c = currentKundliData.charts;
        svg = currentChartStyle === 'south' ? c.d9_south : (currentChartStyle === 'east' ? c.d9_east : c.d9_north);
      }
      document.getElementById('chartD9SvgWrapper').innerHTML = svg || '<div style="color:#6B7280; padding:20px;">Divisional chart rendering...</div>';
    }

    function setChartStyle(st) {
      currentChartStyle = st;
      document.getElementById('style_north').classList.toggle('active', st === 'north');
      document.getElementById('style_south').classList.toggle('active', st === 'south');
      document.getElementById('style_east').classList.toggle('active', st === 'east');
      renderD1Svg();
      onDivisionalChange();
    }

    function setLang(l) {
      try {
        currentLang = l;

        const elMr = document.getElementById('lang_mr');
        const elHi = document.getElementById('lang_hi');
        const elEn = document.getElementById('lang_en');
        if (elMr) elMr.classList.toggle('active', l === 'mr');
        if (elHi) elHi.classList.toggle('active', l === 'hi');
        if (elEn) elEn.classList.toggle('active', l === 'en');

        // 🌟 1. Display Luxury Progress Modal
        const modal = document.getElementById('loadingModal');
        const bar = document.getElementById('loadingBarFill');
        const txt = document.getElementById('loadingStageText');
        const pct = document.getElementById('loadingPercentText');
        const titleEl = modal ? modal.querySelector('h3') : null;

        if (modal) {
          modal.style.display = 'flex';
          modal.style.pointerEvents = 'auto';
          if (bar) bar.style.width = '45%';
          if (pct) pct.innerText = '45%';

          if (l === 'mr') {
            if (titleEl) titleEl.innerText = 'कुंडली भाषा बदल (LANGUAGE SWITCH)';
            if (txt) txt.innerText = '✨ भाषा बदलत आहे: संपूर्ण मराठी व हिन्दी आवृत्ती लोड होत आहे...';
          } else if (l === 'hi') {
            if (titleEl) titleEl.innerText = 'कुंडली भाषा परिवर्तन (LANGUAGE SWITCH)';
            if (txt) txt.innerText = '✨ भाषा बदली जा रही है: सम्पूर्ण हिन्दी संस्करण लोड हो रहा है...';
          } else {
            if (titleEl) titleEl.innerText = 'SWITCHING SYSTEM LANGUAGE';
            if (txt) txt.innerText = '✨ Switching Language: Loading English Astrological Suite...';
          }
        }

        // 🌟 2. Screen-Wide Cosmic Aura Transition
        const vp = document.querySelector('.desktop-viewport') || document.body;
        if (vp) {
          vp.classList.remove('cosmic-lang-transition');
          void vp.offsetWidth;
          vp.classList.add('cosmic-lang-transition');
        }

        // 🌟 3. Instant UI Localization
        updateUILanguage(l);

        // 🌟 4. Instant Data Re-render
        if (currentKundliData) {
          try {
            if (l === 'mr') {
              if (document.getElementById('statLagna')) document.getElementById('statLagna').innerText = toMrWithHi(currentKundliData.meta.lagna_hi || currentKundliData.meta.lagna_en);
              if (document.getElementById('statRasi')) document.getElementById('statRasi').innerText = toMrWithHi(currentKundliData.meta.rasi_hi || currentKundliData.meta.rasi_en);
              if (document.getElementById('statNakshatra')) document.getElementById('statNakshatra').innerText = toMrWithHi(currentKundliData.meta.nakshatra_hi || currentKundliData.meta.nakshatra_en);
              if (document.getElementById('statManglik')) document.getElementById('statManglik').innerText = toMrWithHi(currentKundliData.manglik.status_hi || currentKundliData.manglik.status_en);
              if (document.getElementById('statDasha')) document.getElementById('statDasha').innerText = toMr(currentKundliData.vimshottari.balance_hi || currentKundliData.vimshottari.balance_str);
            } else if (l === 'hi') {
              if (document.getElementById('statLagna')) document.getElementById('statLagna').innerText = (currentKundliData.meta.lagna_hi || currentKundliData.meta.lagna_en);
              if (document.getElementById('statRasi')) document.getElementById('statRasi').innerText = (currentKundliData.meta.rasi_hi || currentKundliData.meta.rasi_en);
              if (document.getElementById('statNakshatra')) document.getElementById('statNakshatra').innerText = (currentKundliData.meta.nakshatra_hi || currentKundliData.meta.nakshatra_en);
              if (document.getElementById('statManglik')) document.getElementById('statManglik').innerText = (currentKundliData.manglik.status_hi || currentKundliData.manglik.status_en);
              if (document.getElementById('statDasha')) document.getElementById('statDasha').innerText = (currentKundliData.vimshottari.balance_hi || currentKundliData.vimshottari.balance_str);
            } else {
              if (document.getElementById('statLagna')) document.getElementById('statLagna').innerText = currentKundliData.meta.lagna_en;
              if (document.getElementById('statRasi')) document.getElementById('statRasi').innerText = currentKundliData.meta.rasi_en;
              if (document.getElementById('statNakshatra')) document.getElementById('statNakshatra').innerText = currentKundliData.meta.nakshatra_en;
              if (document.getElementById('statManglik')) document.getElementById('statManglik').innerText = currentKundliData.manglik.status_en;
              if (document.getElementById('statDasha')) document.getElementById('statDasha').innerText = currentKundliData.vimshottari.balance_str;
            }

            if (typeof renderPlanetsTable === 'function') renderPlanetsTable(currentKundliData.planets);
            if (typeof renderBhavas === 'function') renderBhavas(currentKundliData.bhavas);
            if (typeof renderDashaAndGems === 'function') renderDashaAndGems(currentKundliData);
            if (typeof renderDoshas === 'function') renderDoshas(currentKundliData.doshas);
            if (typeof renderYogas === 'function') renderYogas(currentKundliData.yogas);
            if (typeof renderGemstonesAndYantras === 'function') renderGemstonesAndYantras(currentKundliData);
            if (typeof renderAvkahadaAndFavourable === 'function') renderAvkahadaAndFavourable(currentKundliData);
          } catch(errRender) {
            console.warn('Re-render non-fatal error:', errRender);
          }
        }
      } catch(e) {
        console.error('setLang general error:', e);
      } finally {
        // 🌟 5. GUARANTEED DISMISSAL AFTER 380ms
        setTimeout(() => {
          const modal = document.getElementById('loadingModal');
          const bar = document.getElementById('loadingBarFill');
          const pct = document.getElementById('loadingPercentText');
          if (bar) bar.style.width = '100%';
          if (pct) pct.innerText = '100%';

          setTimeout(() => {
            if (modal) {
              modal.style.display = 'none';
              modal.style.pointerEvents = 'none';
            }

            // Show Floating Toast
            const toast = document.getElementById('langSwitchToast');
            const toastTxt = document.getElementById('langSwitchToastText');
            if (toast && toastTxt) {
              if (l === 'mr') {
                toastTxt.innerHTML = '✨ <b>संपूर्ण मराठी + हिन्दी आवृत्ती सक्रिय</b> (Marathi &amp; Hindi Active)';
              } else if (l === 'hi') {
                toastTxt.innerHTML = '✨ <b>सम्पूर्ण हिन्दी संस्करण सक्रिय</b> (Hindi Edition Active)';
              } else {
                toastTxt.innerHTML = '✨ <b>English Vedic Edition Active</b>';
              }
              toast.classList.add('toast-visible');
              clearTimeout(window._toastTimer);
              window._toastTimer = setTimeout(() => {
                toast.classList.remove('toast-visible');
              }, 2200);
            }
          }, 120);
        }, 250);
      }
    }

    function updateUILanguage(lang) {
      try {
        const isMr = (lang === 'mr');
        const isHi = (lang === 'hi');
        
        // Topbar Title
        const topTitle = document.getElementById('topNavTitle');
        if (topTitle) {
          topTitle.innerHTML = isMr ? 'इंटरॅक्टिव्ह कुंडली वर्कस्पेस (कुंडली वर्कस्पेस)' : (isHi ? 'इंटरैक्टिव कुंडली वर्कस्पेस (Kundli Workspace)' : 'Interactive Kundli Workspace');
        }

        // Form Action Buttons
        const btnCalc = document.getElementById('btnCalculateWorkspace');
        if (btnCalc) {
          btnCalc.innerHTML = isMr ? '✨ गणना करा व कुंडली पहा (कुंडली पहा)' : (isHi ? '✨ गणना करें व कुंडली देखें' : '✨ Calculate & Open Workspace');
        }
        const btnSave = document.getElementById('btnSaveCrm');
        if (btnSave) {
          btnSave.innerHTML = isMr ? '💾 केवळ CRM मध्ये सेव्ह करा (सेव्ह करा)' : (isHi ? '💾 केवल CRM में सेव करें' : '💾 Save to CRM Only');
        }
        const btnClear = document.getElementById('btnClearForm');
        if (btnClear) {
          btnClear.innerHTML = isMr ? '🔄 फॉर्म साफ करा (साफ करा)' : (isHi ? '🔄 फॉर्म साफ करें' : '🔄 Clear Form');
        }

        // Safely re-trigger view title
        const curNav = (typeof currentActiveNav !== 'undefined' && currentActiveNav) ? currentActiveNav : 'new_kundli';
        if (typeof switchNav === 'function') {
          switchNav(curNav);
        }
      } catch(e) {
        console.warn('updateUILanguage non-fatal error:', e);
      }
    }

        function renderPlanetsTable(planets) {
      const tbody = document.getElementById('planetTableBody');
      const pKeysMr = {
        "Ascendant": "लग्न (लग्न)", "ASC": "लग्न (लग्न)", "Lagna": "लग्न (लग्न)",
        "Sun": "सूर्य (सूर्य)", "Moon": "चंद्र (चंद्र)", "Mars": "मंगळ (मंगल)",
        "Mercury": "बुध (बुध)", "Jupiter": "गुरु (बृहस्पति)", "Venus": "शुक्र (शुक्र)",
        "Saturn": "शनी (शनि)", "Rahu": "राहू (राहु)", "Ketu": "केतू (केतु)",
        "Uranus": "हर्षल (हर्षल)", "Neptune": "नेपच्यून (नेपच्यून)", "Pluto": "प्लूटो (प्लूटो)"
      };
      const rashiMr = {
        "Aries": "मेष (मेष)", "Taurus": "वृषभ (वृषभ)", "Gemini": "मिथुन (मिथुन)",
        "Cancer": "कर्क (कर्क)", "Leo": "सिंह (सिंह)", "Virgo": "कन्या (कन्या)",
        "Libra": "तूळ (तुला)", "Scorpio": "वृश्चिक (वृश्चिक)", "Sagittarius": "धनु (धनु)",
        "Capricorn": "मकर (मकर)", "Aquarius": "कुंभ (कुंभ)", "Pisces": "मीन (मीन)"
      };
      const dignityMr = {
        "Exalted": "उच्च (उच्च)", "Debilitated": "नीच (नीच)", "Own Sign": "स्वराशी (स्वराशि)",
        "Moolatrikona": "मूळत्रिकोण (मूलत्रिकोण)", "Great Friend": "अधिमित्र (अधिमित्र)",
        "Friend": "मित्र (मित्र)", "Neutral": "सम (सम)", "Enemy": "शत्रू (शत्रु)",
        "Great Enemy": "अधिशत्रू (अधिशत्रु)", "Combust": "अस्त (अस्त)", "Normal": "सामान्य (सामान्य)"
      };

      tbody.innerHTML = planets.map(p => {
        const retro = !!(p.retrograde || p.is_retro);
        let isRetro = '';
        if (currentLang === 'mr') {
          isRetro = retro ? 'वक्री (वक्र)' : 'मार्गी (मार्गी)';
        } else if (currentLang === 'hi') {
          isRetro = retro ? 'वक्र (Retro)' : 'मार्गी (Direct)';
        } else {
          isRetro = retro ? 'Retrograde' : 'Direct';
        }
        const retroColor = retro ? '#C2540A' : '#166534';
        
        let pName = '';
        let signName = '';
        let nakWithPada = '';
        let dignity = '';

        // Clean raw planet name of any existing retrograde markers to prevent duplicate [R] [R]
        const cleanNameEn = (p.name_en || p.planet || p.id || '').replace(/\[R\]|\(R\)|\[वक्री\]/gi, '').trim();
        const cleanNameHi = (p.name_hi || '').replace(/\[R\]|\(R\)|\[वक्र\]/gi, '').trim();

        if (currentLang === 'mr') {
          pName = pKeysMr[cleanNameEn] || pKeysMr[p.id] || toMrWithHi(cleanNameHi || cleanNameEn);
          if (retro) pName += ' <span style="color:#C2540A; font-weight:800;">[वक्री / वक्र]</span>';
          signName = rashiMr[p.sign_en] || toMrWithHi(p.sign_hi || p.sign_en);
          const nakName = toMrWithHi(p.nakshatra_hi || p.nakshatra_en || p.nakshatra || '');
          nakWithPada = `${nakName} (चरण ${p.pada || 1} / पद ${p.pada || 1})`;
          dignity = dignityMr[p.dignity_en] || toMrWithHi(p.dignity_hi || p.dignity_en || 'सामान्य');
        } else if (currentLang === 'hi') {
          pName = cleanNameHi || cleanNameEn;
          if (retro) pName += ' [वक्र]';
          signName = p.sign_hi || p.sign_en;
          nakWithPada = `${p.nakshatra_hi || p.nakshatra_en || ''} (पद ${p.pada || 1})`;
          dignity = p.dignity_hi || p.dignity_en || 'सामान्य';
        } else {
          pName = cleanNameEn || cleanNameHi;
          if (retro) pName += ' [R]';
          signName = p.sign_en || p.sign_hi;
          nakWithPada = `${p.nakshatra_en || p.nakshatra_hi || ''} (Pada ${p.pada || 1})`;
          dignity = p.dignity_en || 'Normal';
        }

        const deg = p.dms || p.deg_dms || (p.deg_in_sign ? p.deg_in_sign.toFixed(2) + '°' : '');

        return `
          <tr>
            <td style="font-weight:800; color:#7C2D12; text-align:left; padding-left:14px;">${pName}</td>
            <td style="font-weight:700;">${signName}</td>
            <td style="font-family:monospace; font-weight:700; color:#9A3412;">${deg}</td>
            <td style="font-size:11.8px;">${nakWithPada}</td>
            <td><span class="badge" style="background:#FEF3C7; color:#92400E; font-weight:700;">${dignity}</span></td>
            <td><strong style="color:${retroColor};">${isRetro}</strong></td>
          </tr>
        `;
      }).join('');
    }

    // ===============================================================
    // CORE ASTROLOGICAL RENDERING MODULES (BHAVAS, DASHA, DOSHAS, YOGAS, SHADBALA)
    // ===============================================================

    // Render 12 Bhavas
    function renderBhavas(bhavas) {
      const container = document.getElementById('bhavasGrid');
      if (!container || !bhavas) return;
      container.innerHTML = bhavas.map(b => {
        const houseNum = b.house || b.num || 1;
        const title = (currentLang === 'mr' || currentLang === 'hi') ? (toMrWithHi(b.title_mr || b.title_hi || b.title_en)) : (b.title_en || b.title_hi);
        const sign = b.sign_mr || b.sign || b.sign_name || '';
        const planets = b.planets || 'रिक्त (Vacant)';
        const summary = (currentLang === 'mr' || currentLang === 'hi') ? (toMrWithHi(b.summary_mr || b.summary_hi || b.prediction_hi || '')) : (b.summary_en || b.prediction_en || '');
        return `
        <div style="background:#FFFFFF; border:1.5px solid #EADBC8; border-radius:8px; padding:10px 12px; border-left:4px solid #C2540A;">
          <div style="font-size:12px; font-weight:800; color:#7C2D12;">${houseNum}. ${title}</div>
          <div style="font-size:11px; color:#854D0E; font-weight:700; margin:3px 0;">राशी (Sign): ${sign} • ग्रह (Planets): ${planets}</div>
          <div style="font-size:11px; color:#2E1C10; line-height:1.45; font-weight:500;">${summary}</div>
        </div>
      `;
      }).join('');
    }

    // Render Dasha & Gemstones
    function renderDashaAndGems(data) {
      if (!data) return;
      const v = data.vimshottari || {};
      const dashas = v.mahadashas || [];
      const dashaEl = document.getElementById('dashaSummary');
      if (dashaEl) {
        dashaEl.innerHTML = `
          <div style="margin-bottom:10px; padding:8px 12px; background:#FEF3C7; border:1.5px solid #FDE68A; border-radius:8px; color:#78350F; font-size:12px; font-weight:700;">
            <strong>जन्म कालीन दशा शेष (Birth Dasha Balance):</strong> ${v.balance_hi || v.balance_str || '-'}
          </div>
          <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(210px, 1fr)); gap:10px; margin-top:10px;">
            ${dashas.map(d => `
              <div style="background:#FFFFFF; padding:8px 10px; border-radius:8px; font-size:11.5px; border:1.5px solid #EADBC8; box-shadow:0 1px 4px rgba(46,28,16,0.03);">
                <strong style="color:#7C2D12; font-size:12px;">${toMrWithHi(d.name_hi || d.name_en)} (${d.years} वर्ष)</strong><br/>
                <span style="color:#4B5563; font-size:11px; font-weight:600;">${d.range_str}</span>
              </div>
            `).join('')}
          </div>
        `;
      }

      const gems = data.gemstones || [];
      const gemEl = document.getElementById('gemstonesSummary');
      if (gemEl) {
        gemEl.innerHTML = gems.map(g => `
          <div style="margin-bottom:8px; padding:8px 12px; background:#FFFFFF; border:1.5px solid #EADBC8; border-radius:8px;">
            <strong style="color:#7C2D12; font-size:12.5px; font-weight:800;">${toMrWithHi(g.role_hi || g.role_en)}: ${toMrWithHi(g.gem_hi || g.gem_en)}</strong>
            <div style="font-size:11.5px; color:#4B5563; margin-top:3px; font-weight:600;">
              <span>धातू: ${toMrWithHi(g.metal_hi || g.metal_en)}</span> •
              <span>बोट: ${toMrWithHi(g.finger_hi || g.finger_en)}</span> •
              <span>वार: ${toMrWithHi(g.day_hi || g.day_en)}</span>
            </div>
            <div style="font-size:11px; color:#166534; background:#F0FDF4; border:1px solid #BBF7D0; border-radius:6px; padding:4px 8px; margin-top:5px; font-weight:600;">
              📿 ${toMrWithHi(g.rudra_hi || g.rudra_en)} | <span>मंत्र: ${g.mantra}</span>
            </div>
          </div>
        `).join('');
      }
    }

    // Render Doshas
    function renderDoshas(doshas) {
      if (!doshas) return;
      const container = document.getElementById('doshasList');
      if (!container) return;
      const mg = doshas.manglik || doshas.mangal_dosha || {};
      const ks = doshas.kalsarpa || doshas.kaalsarp || {};
      const ss = doshas.sadesati || {};
      const pt = doshas.pitra_dosha || {};
      const gc = doshas.guru_chandal || {};
      const gr = doshas.grahan_dosha || {};

      container.innerHTML = `
        <div class="dosha-card">
          <div class="dosha-head">
            <span>🔴 मंगळ दोष (Kuja / Mangal Dosha)</span>
            <span class="badge" style="background:${mg.is_manglik ? '#FEE2E2':'#DCFCE7'}; color:${mg.is_manglik ? '#991B1B':'#166534'};">${mg.is_manglik ? 'दोष सक्रिय (Present)':'दोष मुक्त (Free)'}</span>
          </div>
          <div style="font-size:11.5px; color:#854D0E; font-weight:700; margin:4px 0;"><strong>स्थान:</strong> लग्नापासून भाव ${mg.mars_house_lagna || '-'} मध्ये मंगळ</div>
          <div class="dosha-desc">${toMrWithHi(mg.status_hi || mg.status_en || '')}</div>
          <div class="remedy-pill"><strong>उपाय:</strong> दर मंगळवारी हनुमान चालीसा पठण करा व लाल मसूर दान करा.</div>
        </div>

        <div class="dosha-card">
          <div class="dosha-head">
            <span>🐍 कालसर्प योग (Kaal Sarp Yoga)</span>
            <span class="badge" style="background:${ks.is_kalsarpa ? '#FEE2E2':'#DCFCE7'}; color:${ks.is_kalsarpa ? '#991B1B':'#166534'};">${ks.is_kalsarpa ? 'सक्रिय (Active)':'दोष मुक्त (Free)'}</span>
          </div>
          <div style="font-size:11.5px; color:#854D0E; font-weight:700; margin:4px 0;"><strong>प्रकार:</strong> ${toMrWithHi(ks.type_hi || 'दोष मुक्त')}</div>
          <div class="dosha-desc">${toMrWithHi(ks.result_hi || ks.result_en || '')}</div>
          <div class="remedy-pill"><strong>उपाय:</strong> महामृत्युंजय जप आणि भगवान शंकराचा रुद्राभिषेक करा.</div>
        </div>

        <div class="dosha-card">
          <div class="dosha-head">
            <span>🪐 शनी साडेसाती (Shani Sade Sati)</span>
            <span class="badge">${toMrWithHi(ss.type_hi || ss.type_en || 'गोचर प्रभाव')}</span>
          </div>
          <div style="font-size:11.5px; color:#9A3412; font-weight:700; margin:4px 0;"><strong>चरण:</strong> ${toMrWithHi(ss.phase_hi || ss.phase_en || 'सकारात्मक')} (${ss.start_year || 2025} - ${ss.end_year || 2028})</div>
          <div class="dosha-desc">शनीचे भ्रमण जातकाच्या चंद्र राशीभोवती. संयम, प्रामाणिक कर्म व सेवाभाव लाभदायक.</div>
          <div class="remedy-pill"><strong>उपाय:</strong> दर शनिवारी पिंपळाच्या वृक्षाखाली तिळाच्या किंवा मोहरीच्या तेलाचा दिवा लावावा.</div>
        </div>

        <div class="dosha-card">
          <div class="dosha-head">
            <span>☀️ ${toMrWithHi(pt.title_hi || 'पितृ दोष (Pitra Dosha)')}</span>
            <span class="badge" style="background:${pt.is_present ? '#FEE2E2':'#DCFCE7'}; color:${pt.is_present ? '#991B1B':'#166534'};">${pt.is_present ? 'सक्रिय (Active)':'दोष मुक्त (Free)'}</span>
          </div>
          <div class="dosha-desc">${toMrWithHi(pt.desc_hi || pt.desc_en || '')}</div>
          <div class="remedy-pill"><strong>उपाय:</strong> ${toMrWithHi(pt.remedy_hi || pt.remedy_en || '')}</div>
        </div>

        <div class="dosha-card">
          <div class="dosha-head">
            <span>📿 ${toMrWithHi(gc.title_hi || 'गुरु चांडाल योग (Guru Chandal Yoga)')}</span>
            <span class="badge" style="background:${gc.is_present ? '#FEE2E2':'#DCFCE7'}; color:${gc.is_present ? '#991B1B':'#166534'};">${gc.is_present ? 'सक्रिय (Active)':'दोष मुक्त (Free)'}</span>
          </div>
          <div class="dosha-desc">${toMrWithHi(gc.desc_hi || gc.desc_en || '')}</div>
          <div class="remedy-pill"><strong>उपाय:</strong> ${toMrWithHi(gc.remedy_hi || gc.remedy_en || '')}</div>
        </div>

        <div class="dosha-card">
          <div class="dosha-head">
            <span>🌕 ${toMrWithHi(gr.title_hi || 'ग्रहण दोष (Grahan Dosha)')}</span>
            <span class="badge" style="background:${gr.is_present ? '#FEE2E2':'#DCFCE7'}; color:${gr.is_present ? '#991B1B':'#166534'};">${gr.is_present ? 'सक्रिय (Active)':'दोष मुक्त (Free)'}</span>
          </div>
          <div class="dosha-desc">${toMrWithHi(gr.desc_hi || gr.desc_en || '')}</div>
          <div class="remedy-pill"><strong>उपाय:</strong> ${toMrWithHi(gr.remedy_hi || gr.remedy_en || '')}</div>
        </div>
      `;
    }

    // Render Yogas
    function renderYogas(yogas) {
      const container = document.getElementById('yogasList');
      if (!container || !yogas) return;
      container.innerHTML = yogas.map(y => `
        <div style="background:#FFFFFF; padding:12px 14px; border-radius:10px; border:1.5px solid #EADBC8; box-shadow:0 1px 4px rgba(46,28,16,0.03);">
          <strong style="color:#7C2D12; font-size:13px; font-weight:800;">${toMrWithHi(y.name_mr || y.name_hi || y.name_en)}</strong>
          <p style="font-size:11.8px; color:#2E1C10; margin-top:4px; line-height:1.5; font-weight:500;">${toMrWithHi(y.desc_mr || y.desc_hi || y.desc_en)}</p>
        </div>
      `).join('');
    }

    // Render Shadbala and SAV
    function renderShadbalaAndSAV(data) {
      if (!data || !data.shadbala) return;
      const sb = data.shadbala;
      const rankMap = sb.shadbala_rank || {};
      const rupasMap = sb.shadbala_in_rupas || {};
      const minMap = sb.shadbala_min_req || {};
      const ratioMap = sb.shadbala_ratio || {};
      const totalVirupa = sb.shadbala_total || {};
      const sthanMap = sb.sthana_bala_total || {};
      const digMap = sb.dig_bala || {};
      const kalaMap = sb.kaala_bala_total || {};
      const chestaMap = sb.chesta_bala || {};
      const naisMap = sb.naisargika_bala || {};
      const drikMap = sb.drik_bala || {};

      const pKeys = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"];
      const pNamesMr = {"Sun":"सूर्य","Moon":"चंद्र","Mars":"मंगळ","Mercury":"बुध","Jupiter":"गुरू","Venus":"शुक्र","Saturn":"शनी"};

      let sbHtml = "";
      pKeys.forEach(p => {
        const r = ratioMap[p] || 0;
        const isStrong = r >= 1.0;
        const statusBg = isStrong ? '#DCFCE7' : '#FEE2E2';
        const statusFg = isStrong ? '#166534' : '#991B1B';
        const badge = isStrong ? 'बलवान (Strong)' : 'अल्पबली (Deficit)';
        const rank = rankMap[p] || '-';
        sbHtml += "<tr style='border-bottom:1px solid #E5E7EB;'>" +
          "<td style='text-align:left; font-weight:800; color:#7C2D12; padding-left:10px;'>" + (pNamesMr[p] || p) + "</td>" +
          "<td style='color:#1F2937; font-weight:600;'>" + (sthanMap[p]||0).toFixed(1) + "</td>" +
          "<td style='color:#1F2937; font-weight:600;'>" + (digMap[p]||0).toFixed(1) + "</td>" +
          "<td style='color:#1F2937; font-weight:600;'>" + (kalaMap[p]||0).toFixed(1) + "</td>" +
          "<td style='color:#1F2937; font-weight:600;'>" + (chestaMap[p]||0).toFixed(1) + "</td>" +
          "<td style='color:#1F2937; font-weight:600;'>" + (naisMap[p]||0).toFixed(1) + "</td>" +
          "<td style='color:#1F2937; font-weight:600;'>" + (drikMap[p]||0).toFixed(1) + "</td>" +
          "<td style='font-weight:800; color:#9A3412;'>" + (totalVirupa[p]||0).toFixed(1) + "</td>" +
          "<td style='font-weight:800; color:#7C2D12;'>" + (rupasMap[p]||0).toFixed(2) + " R</td>" +
          "<td style='color:#6B7280; font-weight:600;'>" + (minMap[p]||0) + " R</td>" +
          "<td><span style='background:" + statusBg + "; color:" + statusFg + "; padding:2px 8px; border-radius:4px; font-weight:800;'>" + (r*100).toFixed(0) + "% (" + badge + ")</span></td>" +
          "<td><span style='background:#FEF3C7; color:#78350F; border:1px solid #FDE68A; padding:2px 8px; border-radius:4px; font-weight:800;'>#" + rank + "</span></td>" +
        "</tr>";
      });
      const sbEl = document.getElementById('shadbalaTableBody');
      if (sbEl) sbEl.innerHTML = sbHtml;

      // Ashtakavarga SAV Grid
      if (data.ashtakavarga) {
        const av = data.ashtakavarga;
        let avHtml = "";
        (av.bhinna_rows || []).forEach(br => {
          avHtml += "<tr style='border-bottom:1px solid #F3EDE4;'>" +
            "<td style='text-align:left; font-weight:800; color:#7C2D12; padding-left:10px;'>" + toMrWithHi(br.name_hi || br.name_en) + "</td>" +
            (br.values || []).map(v => "<td style='color:#1F2937; font-weight:600; padding:6px 4px;'>" + v + "</td>").join("") +
            "<td style='font-weight:800; color:#9A3412; font-size:12px;'>" + br.total + "</td>" +
          "</tr>";
        });
        if (av.sarva_totals) {
          const totalSav = av.sarva_totals.reduce((a,b)=>a+b, 0);
          avHtml += "<tr style='background:#FAF6F0; font-weight:800; border-top:2px solid #EADBC8;'>" +
            "<td style='text-align:left; color:#7C2D12; font-weight:900; padding-left:10px;'>सर्वअष्टकवर्ग (SAV Total)</td>" +
            av.sarva_totals.map(pts => {
              const bg = pts >= 28 ? '#DCFCE7' : (pts >= 25 ? '#FEF3C7' : '#FEE2E2');
              const fg = pts >= 28 ? '#166534' : (pts >= 25 ? '#854D0E' : '#991B1B');
              return "<td style='background:" + bg + "; color:" + fg + "; font-weight:800; padding:6px 4px;'>" + pts + "</td>";
            }).join("") +
            "<td style='color:#7C2D12; font-size:12.5px; font-weight:900;'>" + totalSav + "</td>" +
          "</tr>";
        }
        const savEl = document.getElementById('savTableBody');
        if (savEl) savEl.innerHTML = avHtml;
      }

      // Bhavabala Cards
      if (sb.bhavabala_in_rupas) {
        let bhHtml = "";
        sb.bhavabala_in_rupas.forEach((rupas, idx) => {
          const val = (sb.bhavabala_total && sb.bhavabala_total[idx]) || 0;
          bhHtml += "<div style='background:#FFFBEB; border:1.5px solid #FDE68A; padding:8px 6px; border-radius:8px; text-align:center; box-shadow:0 1px 3px rgba(46,28,16,0.03);'>" +
            "<div style='font-size:10.5px; color:#78350F; font-weight:800;'>भाव " + (idx+1) + " (Bhava)</div>" +
            "<div style='font-size:14px; font-weight:900; color:#B45309; margin:2px 0;'>" + rupas + " R</div>" +
            "<div style='font-size:9.5px; color:#6B7280; font-weight:600;'>" + (val ? val.toFixed(0) : '0') + " Virupas</div>" +
          "</div>";
        });
        const bhEl = document.getElementById('bhavabalaSummaryGrid');
        if (bhEl) bhEl.innerHTML = bhHtml;
      }
    }

    // Kundli Milan Calculation
    async function calculateMilan() {
      const payload = {
        boy: {
          name: document.getElementById('milan_b_name').value,
          sex: 'Male',
          day: parseInt(document.getElementById('milan_b_day').value),
          month: parseInt(document.getElementById('milan_b_month').value),
          year: parseInt(document.getElementById('milan_b_year').value),
          hour: parseInt(document.getElementById('milan_b_hour').value),
          minute: parseInt(document.getElementById('milan_b_minute').value),
          place: document.getElementById('milan_b_place').value,
          lat: 28.6139, lon: 77.2090, tz: 5.5
        },
        girl: {
          name: document.getElementById('milan_g_name').value,
          sex: 'Female',
          day: parseInt(document.getElementById('milan_g_day').value),
          month: parseInt(document.getElementById('milan_g_month').value),
          year: parseInt(document.getElementById('milan_g_year').value),
          hour: parseInt(document.getElementById('milan_g_hour').value),
          minute: parseInt(document.getElementById('milan_g_minute').value),
          place: document.getElementById('milan_g_place').value,
          lat: 28.6139, lon: 77.2090, tz: 5.5
        },
        lang: currentLang
      };

      try {
        const res = await fetch('/api/kundli-milan', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (data.milan) {
          const m = data.milan;
          document.getElementById('milanResultBox').style.display = 'block';
          document.getElementById('milanTotalScore').innerText = m.total_score + ' / 36';
          const isMr = (currentLang === 'mr');
          const isHi = (currentLang === 'hi');
          const verdictTxt = isMr ? (toMrWithHi(m.verdict_hi) || m.verdict_hi) : (isHi ? m.verdict_hi : m.verdict_en);
          document.getElementById('milanVerdict').innerText = verdictTxt;
          const manglikTxt = isMr ? (toMrWithHi(m.manglik_harmony ? m.manglik_harmony.verdict_hi : '') || m.manglik_harmony.verdict_hi) : (isHi ? m.manglik_harmony.verdict_hi : m.manglik_harmony.verdict_en);
          document.getElementById('milanManglikHarmony').innerText = manglikTxt;

          const koots = m.koots || [];
          document.getElementById('milanKootsBody').innerHTML = koots.map(k => {
            const maxPts = k.max !== undefined ? k.max : (k.max_points || 0);
            const obtPts = k.obtained !== undefined ? k.obtained : (k.obtained_points || 0);
            const rawArea = k.desc_hi || k.area_hi || '';
            const area = isMr ? (toMrWithHi(rawArea) || rawArea) : (isHi ? rawArea : (k.desc_en || k.area_en || ''));
            const isFavorable = obtPts > 0;
            const verdict = isFavorable ? (isMr ? 'अनुकूल (शुभ)' : (isHi ? 'अनुकूल' : 'Auspicious')) : (isMr ? 'दोष / कमी गुण' : (isHi ? 'दोष / न्यून' : 'Low / Dosha'));
            const kName = isMr ? (toMrWithHi(k.koot_hi) || k.koot_hi) : (isHi ? k.koot_hi : k.koot_en);
            return `
            <tr>
              <td style="font-weight:800; color:#7C2D12;">${kName}</td>
              <td style="font-weight:700;">${maxPts}</td>
              <td style="font-weight:800; color:${isFavorable ? '#166534':'#991B1B'};">${obtPts}</td>
              <td style="font-size:11.5px; color:#4B5563;">${area}</td>
              <td><span class="badge" style="background:${isFavorable ? '#DCFCE7':'#FEE2E2'}; color:${isFavorable ? '#166534':'#991B1B'};">${verdict}</span></td>
            </tr>
          `;
          }).join('');
        }
      } catch (err) {
        alert('Milan Error: ' + err.message);
      }
    }

        function getMilanPayload() {
      return {
        boy: {
          name: document.getElementById('milan_b_name').value || 'Groom', sex: 'Male',
          day: parseInt(document.getElementById('milan_b_day').value) || 1,
          month: parseInt(document.getElementById('milan_b_month').value) || 1,
          year: parseInt(document.getElementById('milan_b_year').value) || 1995,
          hour: parseInt(document.getElementById('milan_b_hour').value) || 12,
          minute: parseInt(document.getElementById('milan_b_minute').value) || 0,
          second: 0,
          place: document.getElementById('milan_b_place').value || 'Delhi'
        },
        girl: {
          name: document.getElementById('milan_g_name').value || 'Bride', sex: 'Female',
          day: parseInt(document.getElementById('milan_g_day').value) || 1,
          month: parseInt(document.getElementById('milan_g_month').value) || 1,
          year: parseInt(document.getElementById('milan_g_year').value) || 1997,
          hour: parseInt(document.getElementById('milan_g_hour').value) || 12,
          minute: parseInt(document.getElementById('milan_g_minute').value) || 0,
          second: 0,
          place: document.getElementById('milan_g_place').value || 'Delhi'
        },
        lang: currentLang || 'hi'
      };
    }

    async function exportMilanPDF() {
      const btn = document.getElementById('btnExportMilan');
      const origText = btn ? btn.innerHTML : '';
      if (btn) { btn.innerHTML = '⏳ Generating 3-Page Royal Milan PDF...'; btn.disabled = true; }

      const payload = getMilanPayload();
      try {
        const res = await fetch('/api/export-milan-summary-pdf', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (data && data.download_url) {
          const a = document.createElement('a');
          a.href = data.download_url;
          a.download = data.filename || 'Kundli_Milan.pdf';
          document.body.appendChild(a);
          a.click();
          document.body.removeChild(a);
          alert('✅ 3-Page Royal Kundli Milan PDF downloaded successfully!');
        } else {
          console.warn('Backend export notice:', data ? data.error : 'Unknown');
          await printMilanDossier();
        }
      } catch (e) {
        console.warn('Export fetch exception:', e);
        await printMilanDossier();
      } finally {
        if (btn) { btn.innerHTML = origText || '⬇️ Download 3-Page Royal Milan PDF'; btn.disabled = false; }
      }
    }

    async function previewMilanDossier() {
      const modal = document.getElementById('milanPreviewModal');
      const frame = document.getElementById('milanPreviewFrame');
      if (modal) modal.style.display = 'flex';
      if (frame) {
        frame.srcdoc = '<div style="font-family:sans-serif; text-align:center; padding:40px; color:#78350F; font-size:16px; font-weight:700;">⏳ Preparing 3-Page Royal Vedic Milan Dossier...</div>';
      }

      const payload = getMilanPayload();
      try {
        const res = await fetch('/api/milan-preview-html', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify(payload)
        });
        const html = await res.text();
        if (frame) {
          frame.srcdoc = html;
        }
      } catch (e) {
        if (frame) {
          frame.srcdoc = '<div style="color:red; padding:20px; font-family:sans-serif;">Error loading preview: ' + e + '</div>';
        }
      }
    }

    function closeMilanPreview() {
      const modal = document.getElementById('milanPreviewModal');
      if (modal) modal.style.display = 'none';
    }

    async function printMilanDossier() {
      const frame = document.getElementById('milanPreviewFrame');
      const modal = document.getElementById('milanPreviewModal');
      if (modal && modal.style.display !== 'flex') {
        await previewMilanDossier();
        setTimeout(() => {
          if (frame && frame.contentWindow) {
            frame.contentWindow.focus();
            frame.contentWindow.print();
          }
        }, 900);
      } else {
        if (frame && frame.contentWindow) {
          frame.contentWindow.focus();
          frame.contentWindow.print();
        }
      }
    }

    // Prashna Horary Chart
    async function castInstantPrashna() {
      const p = getFormPayload();
      try {
        const res = await fetch('/api/prashna-kundli', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({place: p.place || 'Delhi', lat: p.lat || 28.6139, lon: p.lon || 77.2090, tz: p.tz || 5.5, lang: currentLang})
        });
        const data = await res.json();
        if (data.success) {
          switchNav('workspace');
          currentKundliData = data;
          document.getElementById('statLagna').innerText = data.meta.lagna_en;
          document.getElementById('statRasi').innerText = data.meta.rasi_en;
          document.getElementById('statNakshatra').innerText = data.meta.nakshatra_en;
          updateActiveClientBadges('Prashna Kundli', data.meta.day, data.meta.month, data.meta.year, data.meta.place);
          renderD1Svg();
          onDivisionalChange();
          renderPlanetsTable(data.planets);
          alert('Prashna Horary chart generated successfully for ' + data.meta.tob_str);
        }
      } catch (err) {
        alert('Prashna Error: ' + err);
      }
    }

    // PDF Report Studio & Filmora-Style Progress
    function updateReportStudioState() {
      loadInAppPdfPreview();
    }

    async function loadInAppPdfPreview() {
      let p = getFormPayload();
      if (!p.name || !p.year || !p.day) {
        // If form is empty, don't auto-fetch empty report
        return;
      }
      const pkgSelect = document.getElementById('reportPackageSelect');
      if (pkgSelect && pkgSelect.value) p.report_package = pkgSelect.value;
      const badge = document.getElementById('reportNativeBadge');
      if (badge) badge.innerText = 'Active Native: ' + p.name;

      try {
        const res = await fetch('/api/generate-html', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify(p)
        });
        const html = await res.text();
        const frame = document.getElementById('reportFrame');
        if (frame) frame.srcdoc = html;
      } catch (e) {}
    }


    // Direct 1-Click Action: KP Remedies & Upay (के.पी. अचूक उपाय PDF)
    async function openKPRemediesDirectPDF() {
      // 1. Ensure Kundli is calculated
      if (!currentKundliData) {
        const payload = getFormPayload();
        if (!validateInputs(payload)) {
          alert('कृपया आधी जातकाची जन्म माहिती भरा आणि Calculate करा.');
          return;
        }
        await calculateKundli();
      }

      // 2. Smoothly scroll to KP Remedies section in interactive workspace
      const kpSec = document.getElementById('sec_kp_system');
      if (kpSec) {
        kpSec.scrollIntoView({behavior:'smooth'});
      }

      // 3. Switch to Report Studio with VIP Dossier including KP Remedies
      switchNav('reports');
      const pkgSelect = document.getElementById('reportPackageSelect');
      if (pkgSelect) pkgSelect.value = 'kp_remedies';
      await loadInAppPdfPreview();
    }

    function openReportInNewTab() {
      const frame = document.getElementById('reportFrame');
      if (frame && frame.srcdoc && frame.srcdoc.length > 500) {
        const blob = new Blob([frame.srcdoc], { type: 'text/html;charset=utf-8' });
        const blobUrl = URL.createObjectURL(blob);
        const w = window.open(blobUrl, '_blank');
        setTimeout(() => { if (w) { w.focus(); w.print(); } }, 1200);
      } else {
        const p = getFormPayload();
        if (!p.name) {
          alert('कृपया प्रथम जातकाचे नाव आणि जन्म माहिती भरा (Please enter native name & birth details first)');
          return;
        }
        fetch('/api/generate-html', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify(p)
        }).then(r => r.text()).then(html => {
          const frame = document.getElementById('reportFrame');
          if (frame) frame.srcdoc = html;
          const blob = new Blob([html], { type: 'text/html;charset=utf-8' });
          const blobUrl = URL.createObjectURL(blob);
          const w = window.open(blobUrl, '_blank');
          setTimeout(() => { if (w) { w.focus(); w.print(); } }, 1200);
        }).catch(err => {
          alert('रिपोर्ट तयार करताना त्रुटी (Report Error): ' + err);
        });
      }
    }

    async function exportPDF() {
      const p = getFormPayload();
      if (!p.name) {
        alert('कृपया प्रथम जातकाचे नाव आणि जन्म माहिती भरा (Please enter native name and birth details before generating PDF)');
        const nameInput = document.getElementById('name');
        if (nameInput) nameInput.focus();
        return;
      }
      if (!validateInputs(p)) return;

      // Show Filmora-Style Progress Modal with Live Countdown
      const modal = document.getElementById('loadingModal');
      const bar = document.getElementById('loadingBarFill');
      const txt = document.getElementById('loadingStageText');
      const pct = document.getElementById('loadingPercentText');
      const countEl = document.getElementById('loadingCountdownSecs');

      modal.style.display = 'flex'; modal.style.pointerEvents = 'auto';
      bar.style.width = '12%';
      txt.innerText = 'Calibrating VSOP87 Astronomical Coordinates & Lahiri Ayanamsha...';
      pct.innerText = '12%';

      let remainingSecs = 15;
      if (countEl) countEl.innerText = remainingSecs;
      const countTimer = setInterval(() => {
        remainingSecs--;
        if (remainingSecs < 1) remainingSecs = 1;
        if (countEl) countEl.innerText = remainingSecs;
      }, 1000);

      const stages = [
        {w: '28%', t: 'Computing 16 Classical Shodashvarga Charts (D1 to D60)...', p: '28%'},
        {w: '48%', t: 'Calculating Vimshottari Dasha Periods & Lal Kitab Debts...', p: '48%'},
        {w: '68%', t: 'Evaluating Shadbala Strengths & 337-Point Ashtakavarga...', p: '68%'},
        {w: '86%', t: 'Rendering 78-Page VIP Dossier with Authentic KP 12 CSL Remedies...', p: '86%'},
        {w: '95%', t: 'Finalizing Complete Vector PDF & Royal Seals...', p: '95%'}
      ];

      let sIdx = 0;
      const timer = setInterval(() => {
        if (sIdx < stages.length) {
          bar.style.width = stages[sIdx].w;
          txt.innerText = stages[sIdx].t;
          pct.innerText = stages[sIdx].p;
          sIdx++;
        }
      }, 2500);

      try {
        const res = await fetch('/api/export-pdf', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify(p)
        });
        clearInterval(timer);
        clearInterval(countTimer);
        const data = await res.json();

        bar.style.width = '100%';
        pct.innerText = '100%';
        if (countEl) countEl.innerText = '0';
        txt.innerText = '✨ 78-Page Kundli Dossier Ready!';

        setTimeout(() => {
          modal.style.display = 'none'; modal.style.pointerEvents = 'none';
          if (data.download_url) {
            const dlLink = document.createElement('a');
            dlLink.href = data.download_url;
            dlLink.setAttribute('download', data.filename || 'Kundli.pdf');
            document.body.appendChild(dlLink);
            dlLink.click();
            document.body.removeChild(dlLink);
            if (data.single_pages_url) {
              currentSingleZipUrl = data.single_pages_url;
              document.getElementById('btnSingleZip').style.display = 'block';
            }
            loadDashboard();
          } else {
            loadDashboard();
          }
        }, 500);
      } catch (err) {
        clearInterval(timer);
        modal.style.display = 'none'; modal.style.pointerEvents = 'none';
        loadDashboard();
      }
    }

    function printReportFrame() {
      const frame = document.getElementById('reportFrame');
      if (frame && frame.contentWindow && frame.srcdoc && frame.srcdoc.length > 500) {
        frame.contentWindow.focus();
        frame.contentWindow.print();
      } else {
        openReportInNewTab();
      }
    }

    function downloadSinglePagesZip() {
      if (currentSingleZipUrl) window.open(currentSingleZipUrl, '_blank');
    }

    function shareOnWhatsApp() {
      const p = getFormPayload();
      const txt = `*SHIVANSH ASTRO-VASTU REPORT*\nName: ${p.name}\nDOB: ${p.day}/${p.month}/${p.year}\nTime: ${p.hour}:${p.minute}\nPlace: ${p.place}\nConsultation Category: ${p.category}\n-- Generated via Shivansh Astro-Vastu Suite`;
      window.open('https://api.whatsapp.com/send?text=' + encodeURIComponent(txt), '_blank');
    }

    // Astrologer Branding & Dynamic Logo Settings
    async function loadBrandingSettings() {
      try {
        const res = await fetch('/api/branding');
        const data = await res.json();
        const b = data.branding || data;
        if (b) {
          const setField = (id, val) => {
            const el = document.getElementById(id);
            if (el) el.value = val || '';
          };
          setField('brand_astro_name', b.astrologer_name || 'Mayur Mandhare (BE.E&TC)');
          setField('brand_kendra_name', b.kendra_name || 'Shivansh Astro-Vastu');
          setField('brand_phone', b.phone || '9373058052');
          setField('brand_email', b.email || '');
          setField('brand_address', b.address || '');
          setField('brand_tagline', b.tagline || 'Ancient Vedic, KP & Lal Kitab Predictions');
          const preview = document.getElementById('brand_logo_preview');
          const logoInput = document.getElementById('brand_logo_data');
          if (b.logo_data && b.logo_data.startsWith('data:image')) {
            if (preview) preview.src = b.logo_data;
            if (logoInput) logoInput.value = b.logo_data;
          } else {
            if (preview) preview.src = '/assets/images/opt_shivansh_logo.jpg?t=' + Date.now();
            if (logoInput) logoInput.value = '';
          }
        }
      } catch (e) {}
    }

    function previewAndEncodeLogo(event) {
      const file = event.target.files && event.target.files[0];
      if (!file) return;
      const reader = new FileReader();
      reader.onload = function(e) {
        const dataUrl = e.target.result;
        const img = new Image();
        img.onload = function() {
          const canvas = document.createElement('canvas');
          canvas.width = 800;
          canvas.height = 800;
          const ctx = canvas.getContext('2d');
          ctx.drawImage(img, 0, 0, 800, 800);
          const optimizedDataUrl = canvas.toDataURL('image/jpeg', 0.92);
          const preview = document.getElementById('brand_logo_preview');
          const logoInput = document.getElementById('brand_logo_data');
          if (preview) preview.src = optimizedDataUrl;
          if (logoInput) logoInput.value = optimizedDataUrl;
        };
        img.src = dataUrl;
      };
      reader.readAsDataURL(file);
    }

    function resetDefaultLogo() {
      const preview = document.getElementById('brand_logo_preview');
      const logoInput = document.getElementById('brand_logo_data');
      if (preview) preview.src = '/assets/images/opt_shivansh_logo.jpg?t=' + Date.now();
      if (logoInput) logoInput.value = '';
    }

    async function saveBrandingSettings() {
      const payload = {
        astrologer_name: document.getElementById('brand_astro_name').value.trim(),
        kendra_name: document.getElementById('brand_kendra_name').value.trim(),
        phone: document.getElementById('brand_phone').value.trim(),
        email: document.getElementById('brand_email').value.trim(),
        address: document.getElementById('brand_address').value.trim(),
        tagline: document.getElementById('brand_tagline').value.trim(),
        logo_data: document.getElementById('brand_logo_data').value.trim()
      };
      const res = await fetch('/api/branding', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      if (data.success) {
        const s = document.getElementById('brandSaveStatus');
        s.innerHTML = '✓ ब्रँडिंग व नवीन लोगो सेव्ह झाला! (Saved to SQLite Database!)';
        s.style.display = 'inline';
        setTimeout(() => { s.style.display = 'none'; }, 3500);
      }
    }

    // Heartbeat
    setInterval(() => {
      fetch('/api/heartbeat').catch(()=>{});
    }, 4000);


    // ===============================================================
    // ADVANCED MODULE 1: KRISHNAMURTI PADDHATI (KP SYSTEM)
    // ===============================================================
    function renderKPSystem(kp, allData) {
      if (!kp) return;
      
      // Ruling Planets Strip
      const rp = kp.ruling_planets || {};
      const dayLordEl = document.getElementById('kpDayLord');
      if (dayLordEl) dayLordEl.innerText = rp.day_lord || 'Moon';
      
      const lag = rp.lagna || {};
      const m = rp.moon || {};
      if (document.getElementById('kpLagSign')) document.getElementById('kpLagSign').innerText = lag.rasi || '-';
      if (document.getElementById('kpLagStar')) document.getElementById('kpLagStar').innerText = lag.nak || '-';
      if (document.getElementById('kpLagSub')) document.getElementById('kpLagSub').innerText = lag.sub || '-';
      
      if (document.getElementById('kpMoonSign')) document.getElementById('kpMoonSign').innerText = m.rasi || '-';
      if (document.getElementById('kpMoonStar')) document.getElementById('kpMoonStar').innerText = m.nak || '-';
      if (document.getElementById('kpMoonSub')) document.getElementById('kpMoonSub').innerText = m.sub || '-';

      // 12 Cusps Table
      const cusps = kp.cuspal_positions || [];
      const cuspTbody = document.getElementById('kpCuspsBody');
      if (cuspTbody && cusps.length > 0) {
        cuspTbody.innerHTML = cusps.map(c => `
          <tr>
            <td style="font-weight:800; color:#7C2D12;">Cusp ${c.cusp}</td>
            <td style="font-family:monospace; font-weight:700;">${c.dms || ''}</td>
            <td style="font-weight:600;">${(currentLang === 'mr' || currentLang === 'hi') ? (toMrWithHi(c.rasi_hi) || c.rasi_hi) : c.rasi}</td>
            <td style="font-weight:600;">${(currentLang === 'mr' || currentLang === 'hi') ? (toMrWithHi(c.nak_hi) || c.nak_hi) : c.nak}</td>
            <td style="font-weight:800; color:#C2540A; background:#FEF3C7;">${(currentLang === 'mr' || currentLang === 'hi') ? (toMrWithHi(c.sub_hi) || c.sub_hi) : c.sub}</td>
            <td style="color:#574032;">${(currentLang === 'mr' || currentLang === 'hi') ? (toMrWithHi(c.ss_hi) || c.ss_hi) : c.ss}</td>
          </tr>
        `).join('');
      }

      // 9 Planets Table
      const planets = kp.planetary_positions || [];
      const planTbody = document.getElementById('kpPlanetsBody');
      if (planTbody && planets.length > 0) {
        planTbody.innerHTML = planets.map(p => `
          <tr>
            <td style="font-weight:800; color:#7C2D12;">${(currentLang === 'mr' || currentLang === 'hi') ? (toMrWithHi(p.planet_hi) || p.planet_hi) : p.planet_en}</td>
            <td style="font-family:monospace; font-weight:700;">${p.dms || ''}</td>
            <td style="font-weight:600;">${(currentLang === 'mr' || currentLang === 'hi') ? (toMrWithHi(p.nak_hi) || p.nak_hi) : p.nak}</td>
            <td style="font-weight:800; color:#166534; background:#DCFCE7;">${(currentLang === 'mr' || currentLang === 'hi') ? (toMrWithHi(p.sub_hi) || p.sub_hi) : p.sub}</td>
            <td style="font-weight:800; color:#7C2D12;">House ${p.kp_house || '-'}</td>
          </tr>
        `).join('');
      }

      // Render KP Remedies & 4-Fold Significators
      if (allData) {
        // 1. Gemstones Box (Reader III Zero-Damage Rule)
        const gemsBox = document.getElementById('kpGemsContainer');
        const kpGems = allData.kp_gems || {};
        const approved = kpGems.approved || [];
        const rejected = kpGems.rejected || [];
        if (gemsBox) {
          let html = `<div style="background:#F0FDF4; border:1.5px solid #86EFAC; border-radius:8px; padding:12px; margin-bottom:10px;">
            <div style="font-weight:800; color:#166534; font-size:12.5px; margin-bottom:6px;">
              💎 कृष्णमूर्ती पद्धती स्वीकृत व कल्याणकारी रत्न (KP Approved Benefic Gemstones):
            </div>`;
          approved.forEach(ag => {
            html += `<div style="background:#FFF; border:1px solid #BBF7D0; border-radius:6px; padding:8px 10px; margin-bottom:6px; font-size:11.5px;">
              <div style="font-weight:800; color:#14532D; font-size:12px;">✅ ${ag.gem_mr} (${ag.gem_en}) — ${ag.source}</div>
              <div style="color:#166534; margin-top:2px;"><strong>धातू:</strong> ${ag.metal_mr} | <strong>बोट:</strong> ${ag.finger_mr} | <strong>वजन:</strong> ${ag.carat} कॅरेट</div>
              <div style="color:#4B5563; font-size:11px; margin-top:3px;"><strong>के.पी. वैज्ञानिक नियम:</strong> ${ag.reason_mr}</div>
            </div>`;
          });
          if (rejected.length > 0) {
            html += `<div style="margin-top:10px; font-weight:800; color:#991B1B; font-size:12px;">⚠️ कडक वर्ज्य व धोकादायक रत्न (Strictly Denied by KP Science):</div>`;
            rejected.forEach(rg => {
              html += `<div style="background:#FEF2F2; border:1px solid #FCA5A5; border-radius:6px; padding:6px 10px; margin-top:4px; font-size:11px; color:#991B1B;">
                <strong>🚫 ${rg.gem_mr} (${rg.source}):</strong> ${rg.reason_mr}
              </div>`;
            });
          }
          html += `</div>`;
          gemsBox.innerHTML = html;
        }

        // 2. Disease & Cure Box
        const disBox = document.getElementById('kpDiseaseContainer');
        const kpDis = allData.kp_disease || {};
        if (disBox) {
          disBox.innerHTML = `
            <div style="font-weight:800; color:#78350F; font-size:12px; margin-bottom:4px;">🩺 के.पी. रोग निदान व शीघ्र आरोग्य प्राप्ती</div>
            <div style="font-size:11px; color:#451A03; margin-bottom:4px;">
              <strong>रोगसूचक ग्रह (१ व ६ भाव):</strong> <span style="color:#B91C1C; font-weight:700;">${(kpDis.disease_significators || []).join(', ') || 'कोणताही तीव्र आजार नाही'}</span>
            </div>
            <div style="font-size:11px; color:#451A03; margin-bottom:4px;">
              <strong>रोगमुक्ती ग्रह (५ व ११ भाव):</strong> <span style="color:#166534; font-weight:700;">${(kpDis.cure_significators || []).join(', ') || 'गुरु व चंद्र'}</span>
            </div>
            <div style="font-size:10.5px; color:#78350F; font-style:italic;">${kpDis.guidance_mr || ''}</div>
          `;
        }

        // 3. Debts & Repayment Box
        const debtsBox = document.getElementById('kpDebtsContainer');
        const kpDebts = allData.kp_debts || {};
        if (debtsBox) {
          debtsBox.innerHTML = `
            <div style="font-weight:800; color:#1E40AF; font-size:12px; margin-bottom:4px;">🪙 के.पी. कर्ज मुक्ती व परतफेड योग</div>
            <div style="font-size:11px; color:#1E3A8A; margin-bottom:4px;">
              <strong>कर्ज परतफेड ग्रह:</strong> <span style="color:#166534; font-weight:700;">${(kpDebts.repay_planets || []).join(', ') || 'गुरु व चंद्र'}</span>
            </div>
            <div style="font-size:11px; color:#1E3A8A; margin-bottom:4px;">
              <strong>निष्कर्ष:</strong> ${kpDebts.verdict_mr || 'कर्ज मुक्तीचे योग अनुकूल आहेत.'}
            </div>
            <div style="font-size:10.5px; color:#1E40AF; font-style:italic;">हप्ते फेडताना पहिली रक्कम मंगळवारी किंवा शनिवारी देणे टाळावे, बुधवारी किंवा गुरुवारी द्यावी.</div>
          `;
        }

        // 4. 4-Fold Significators Table
        const ffBody = document.getElementById('kpFourFoldBody');
        const fourFold = allData.kp_four_fold || {};
        const hSigs = fourFold.house_significators || {};
        if (ffBody && Object.keys(hSigs).length > 0) {
          let rows = '';
          for (let h = 1; h <= 12; h++) {
            const hs = hSigs[h] || {Level_A:[], Level_B:[], Level_C:[], Level_D:[]};
            rows += `
              <tr style="background:${h%2===0?'#FAF6F0':'#FFF'};">
                <td style="font-weight:800; color:#7C2D12;">भाव ${h}</td>
                <td style="font-weight:700; color:#166534;">${(hs.Level_A || []).join(', ') || '—'}</td>
                <td style="color:#B45309;">${(hs.Level_B || []).join(', ') || '—'}</td>
                <td style="color:#1E40AF;">${(hs.Level_C || []).join(', ') || '—'}</td>
                <td style="color:#4B5563;">${(hs.Level_D || []).join(', ') || '—'}</td>
              </tr>
            `;
          }
          ffBody.innerHTML = rows;
        }

        // 5. KP Cuspal Sub-Lord 12 House Events
        const evBox = document.getElementById('kpEventsContainer');
        const evRules = allData.kp_event_rules || {};
        if (evBox && Object.keys(evRules).length > 0) {
          let evHtml = '';
          for (let h = 1; h <= 12; h++) {
            const rList = evRules[h] || [];
            evHtml += `<div style="background:#FFF; border:1px solid #E5E7EB; border-radius:6px; padding:8px 10px;">
              <div style="font-weight:800; color:#7C2D12; border-bottom:1px solid #FED7AA; padding-bottom:2px; margin-bottom:4px; font-size:11px;">
                भाव ${h} CSL घटना सूत्रे
              </div>`;
            rList.slice(0, 2).forEach(r => {
              const icon = r.fav ? '✅' : '⚠️';
              const col = r.fav ? '#166534' : '#991B1B';
              evHtml += `<div style="font-size:10.5px; margin-bottom:3px;">
                <span style="color:${col}; font-weight:700;">${icon} ${r.event_mr}:</span>
                <span style="background:#FEF3C7; padding:1px 4px; border-radius:3px; font-weight:800; color:#7C2D12;">${(r.houses || []).join('-')}</span>
                <div style="color:#6B7280; font-size:9.5px; margin-top:1px;">${r.desc_mr}</div>
              </div>`;
            });
            evHtml += `</div>`;
          }
          evBox.innerHTML = evHtml;
        }
      }
    }

    // ===============================================================
    // ADVANCED MODULE 2: LAL KITAB TEVA & ANCESTRAL DEBTS
    // ===============================================================
    function renderLalKitab(lk) {
      if (!lk) return;
      const rins = lk.rins || [];
      const rinsBox = document.getElementById('lkRinsContainer');
      if (rinsBox) {
        if (rins.length === 0) {
          rinsBox.innerHTML = `
            <div style="background:#F0FDF4; border:1.5px solid #BBF7D0; border-radius:8px; padding:12px; color:#166534; font-size:12.5px; font-weight:700;">
              ✨ <strong>ऋण मुक्त कुंडली (ऋण मुक्त कुंडली):</strong> कुंडलीत कोणतेही सक्रिय लाल किताब पितृ ऋण नाही. जातकाचे जीवन पूर्वजांच्या आशीर्वादाने सुरक्षित आहे.
            </div>
          `;
        } else {
          rinsBox.innerHTML = rins.map(r => `
            <div style="background:#FEF2F2; border:1.5px solid #FCA5A5; border-radius:10px; padding:14px; margin-bottom:10px;">
              <div style="display:flex; justify-content:space-between; align-items:center;">
                <strong style="color:#991B1B; font-size:13.5px;">⚠️ ${toMrWithHi(r.name_hi || r.name_en)}</strong>
                <span class="badge" style="background:#FEE2E2; color:#991B1B;">लाल किताब ऋण सक्रिय</span>
              </div>
              <p style="font-size:12px; color:#4B5563; margin:6px 0;">${toMr(r.cause_hi || r.cause_en || '')}</p>
              <div style="background:#FFFBEB; border:1px solid #FDE68A; border-radius:6px; padding:8px 10px; font-size:11.5px; color:#78350F;">
                🪔 <strong>अचूक लाल किताब उपाय (अचूक उपाय):</strong> ${toMr(r.remedy_hi || r.remedy_en || '')}
              </div>
            </div>
          `).join('');
        }
      }
    }

    function renderGemstonesAndYantras(data) {
      const gems = data.gemstones || [];
      const grid = document.getElementById('gemstonesFullGrid');
      if (grid && gems.length > 0) {
        grid.innerHTML = gems.map(g => {
          const roleTxt = toMrWithHi(g.role_hi || g.role_en);
          const gemTxt = toMrWithHi(g.gem_hi || g.gem_en);
          const planetTxt = toMrWithHi(g.planet_hi || g.planet_en);
          const metalTxt = toMrWithHi(g.metal_hi || g.metal_en);
          const fingerTxt = toMrWithHi(g.finger_hi || g.finger_en);
          const dayTxt = toMrWithHi(g.day_hi || g.day_en);
          const rudraTxt = toMrWithHi(g.rudra_hi || g.rudra_en);
          const mantraTxt = toMr(g.mantra);
          return `
          <div style="background:#FFFFFF; border:1.5px solid #EADBC8; border-radius:10px; padding:14px; box-shadow:0 2px 6px rgba(46,28,16,0.03); border-top:4px solid #C2540A;">
            <div style="font-size:13px; font-weight:900; color:#7C2D12; margin-bottom:4px;">${roleTxt}</div>
            <div style="font-size:15px; font-weight:900; color:#C2540A; margin-bottom:8px;">💎 ${gemTxt}</div>
            <div style="font-size:11.8px; color:#4B5563; line-height:1.6;">
              <div><strong>शासक ग्रह (शासक ग्रह):</strong> ${planetTxt}</div>
              <div><strong>शुभ धातू (शुभ धातु):</strong> ${metalTxt}</div>
              <div><strong>धारण करण्याचे बोट (अंगुली):</strong> ${fingerTxt}</div>
              <div><strong>धारण करण्याचा वार (वार):</strong> ${dayTxt}</div>
              <div><strong>शुभ रुद्राक्ष (रुद्राक्ष):</strong> <span style="color:#166534; font-weight:700;">${rudraTxt}</span></div>
            </div>
            <div style="background:#FFFBEB; border:1px solid #FDE68A; border-radius:6px; padding:8px 10px; margin-top:10px; font-size:11.2px; color:#78350F; font-weight:700;">
              📿 <strong>बीज मंत्र (बीज मंत्र):</strong> ${mantraTxt}
            </div>
          </div>
        `}).join('');
      }

      // Siddha Yantras
      const yBox = document.getElementById('yantrasList');
      if (yBox) {
        const yantras = [
          {name: 'श्री मंगळ यंत्र (श्री मंगल यंत्र)', use: 'शारीरिक आरोग्य, ऊर्जा, जमीन लाभ व संकटनिवारण (आरोग्य, भूमि व कष्ट निवारण)', forP: 'मंगळ / लग्नेश (मंगल / लग्नेश)'},
          {name: 'श्री गुरु / बृहस्पती यंत्र (श्री गुरु यंत्र)', use: 'उच्च ज्ञान, बुद्धी, आर्थिक समृद्धी व कौटुंबिक सुख (ज्ञान, समृद्धि व सुख)', forP: 'गुरु / पंचमेश (गुरु / पंचमेश)'},
          {name: 'श्री चंद्र यंत्र (श्री चंद्र यंत्र)', use: 'मानसिक शांतता, भावनिक स्थिरता व भाग्योदय वृद्धी (मानसिक शांति व भाग्योदय)', forP: 'चंद्र / भाग्येश (चंद्र / भाग्येश)'},
          {name: 'संपूर्ण महामृत्युंजय यंत्र (महामृत्युंजय यंत्र)', use: 'दीर्घायुष्य, अकाल मृत्यू भय निवारण व सर्वतोपरी संरक्षण (दीर्घायु व सर्व रक्षा कवच)', forP: 'सार्वत्रिक वैदिक सुरक्षा (सर्व रक्षा)'}
        ];
        yBox.innerHTML = yantras.map(y => `
          <div style="background:#FFFFFF; border:1.5px solid #FDE68A; border-radius:8px; padding:10px;">
            <div style="font-weight:900; color:#7C2D12; font-size:12.5px;">ॐ ${y.name}</div>
            <div style="font-size:11.5px; color:#574032; margin-top:3px; line-height:1.4;">${y.use}</div>
            <div style="font-size:11px; color:#C2540A; font-weight:800; margin-top:4px;">शिफारस (फोकस): ${y.forP}</div>
          </div>
        `).join('');
      }
    }

    // ===============================================================
    // ADVANCED MODULE 4: AVAKAHADA & FAVOURABLE ASTRO SCIENCE
    // ===============================================================
    function renderAvkahadaAndFavourable(data) {
      const av = data.avkahada || {};
      const fav = data.favourable || {};

      const avGrid = document.getElementById('avkahadaGrid');
      if (avGrid) {
        avGrid.innerHTML = `
          <div><strong>पाया (पाया):</strong> <span style="color:#C2540A; font-weight:800;">${toMrWithHi(av.paya_hi || av.paya_en || '-')}</span></div>
          <div><strong>वर्ण (वर्ण):</strong> <span style="font-weight:700;">${toMrWithHi(av.varna_hi || av.varna_en || '-')}</span></div>
          <div><strong>योनी (योनि):</strong> <span style="font-weight:700;">${toMrWithHi(av.yoni_hi || av.yoni_en || '-')}</span></div>
          <div><strong>गण (गण):</strong> <span style="font-weight:700; color:#166534;">${toMrWithHi(av.gana_hi || av.gana_en || '-')}</span></div>
          <div><strong>वश्य (वश्य):</strong> <span style="font-weight:700;">${toMrWithHi(av.vasya_hi || av.vasya_en || '-')}</span></div>
          <div><strong>नाडी (नाड़ी):</strong> <span style="font-weight:700;">${toMrWithHi(av.nadi_hi || av.nadi_en || '-')}</span></div>
          <div style="grid-column: span 2; margin-top:4px; padding-top:4px; border-top:1px dashed #EADBC8;">
            <strong>दशा शिल्लक (दशा शेष):</strong> <span style="color:#7C2D12; font-weight:800;">${toMr(av.dasa_balance || '-')}</span>
          </div>
        `;
      }

      const favGrid = document.getElementById('favourableGrid');
      if (favGrid) {
        favGrid.innerHTML = `
          <div><strong>शुभ अंक (शुभ अंक):</strong> <span style="color:#C2540A; font-weight:800; font-size:13px;">${fav.lucky_num || '-'}</span></div>
          <div><strong>अनुकूल अंक (अनुकूल अंक):</strong> <span style="font-weight:700;">${fav.good_nums || '-'}</span></div>
          <div><strong>शुभ वार (शुभ वार):</strong> <span style="font-weight:700;">${toMrWithHi(fav.days || '-')}</span></div>
          <div><strong>मित्र ग्रह (मित्र ग्रह):</strong> <span style="font-weight:700;">${toMrWithHi(fav.planets || '-')}</span></div>
          <div><strong>शुभ धातू (शुभ धातु):</strong> <span style="font-weight:700;">${toMrWithHi(fav.metal || '-')}</span></div>
          <div><strong>शुभ रत्न (शुभ रत्न):</strong> <span style="font-weight:700; color:#166534;">${toMrWithHi(fav.stone || '-')}</span></div>
          <div style="grid-column: span 2; margin-top:4px; padding-top:4px; border-top:1px dashed #EADBC8;">
            <strong>भाग्योदय वर्ष (भाग्योदय वर्ष):</strong> <span style="color:#7C2D12; font-weight:800;">${fav.good_years || '-'}</span>
          </div>
        `;
      }
    }


    // Initial load - Open directly into Executive Dashboard

    // ===============================================================
    // KUNDLI MILAN CITY AUTOCOMPLETE (Groom & Bride)
    // ===============================================================
    let milanCityTimer = null;
    function onMilanCitySearch(who) {
      clearTimeout(milanCityTimer);
      const inputEl = document.getElementById(who === 'b' ? 'milan_b_place' : 'milan_g_place');
      const dropEl = document.getElementById(who === 'b' ? 'milan_b_suggestions' : 'milan_g_suggestions');
      if (!inputEl || !dropEl) return;
      const q = inputEl.value.trim();
      if (q.length < 2) {
        dropEl.style.display = 'none';
        return;
      }
      milanCityTimer = setTimeout(async () => {
        try {
          const res = await fetch('/api/cities?q=' + encodeURIComponent(q));
          const data = await res.json();
          if (data.cities && data.cities.length > 0) {
            dropEl.innerHTML = data.cities.map(c => `
              <div class="city-opt" onclick="selectMilanCity('${who}', '${c.name.replace(/'/g, "\\'")}')">
                <strong>${c.name}</strong>, ${c.state || ''} (${c.country || 'India'})
              </div>
            `).join('');
            dropEl.style.display = 'block';
          } else {
            dropEl.style.display = 'none';
          }
        } catch (err) {
          dropEl.style.display = 'none';
        }
      }, 200);
    }

    function selectMilanCity(who, cityName) {
      const inputEl = document.getElementById(who === 'b' ? 'milan_b_place' : 'milan_g_place');
      const dropEl = document.getElementById(who === 'b' ? 'milan_b_suggestions' : 'milan_g_suggestions');
      if (inputEl) inputEl.value = cityName;
      if (dropEl) dropEl.style.display = 'none';
    }

    // Close suggestion dropdowns on document click
    document.addEventListener('click', function(e) {
      const mbs = document.getElementById('milan_b_suggestions');
      const mgs = document.getElementById('milan_g_suggestions');
      const cs = document.getElementById('citySuggestions');
      if (mbs && !e.target.closest('#milan_b_place') && !e.target.closest('#milan_b_suggestions')) mbs.style.display = 'none';
      if (mgs && !e.target.closest('#milan_g_place') && !e.target.closest('#milan_g_suggestions')) mgs.style.display = 'none';
      if (cs && !e.target.closest('#citySearchInput') && !e.target.closest('#citySuggestions')) cs.style.display = 'none';
    });

    // ===============================================================
    // CINEMATIC SPLASH SCREEN ANIMATION
    // ===============================================================
    function runSplashScreen() {
      const splash = document.getElementById('vedasSplashScreen');
      if (!splash) return;
      const bar = document.getElementById('splashProgressBar');
      const txt = document.getElementById('splashStatusText');

      const steps = [
        { p: 25, t: '✨ Calibrating High-Precision VSOP87 & Lahiri Astronomical Ephemeris...' },
        { p: 55, t: '🪐 Loading Classical Parashari Shodashvarga & KP Cuspal Engine...' },
        { p: 80, t: '📖 Loading Lal Kitab 1952 Remedial & Ancestral Knowledgebase...' },
        { p: 95, t: '👥 Connecting Client CRM & VIP Vector Report Studio...' },
        { p: 100, t: '✨ Ready • Welcome to Shivansh Astro-Vastu Professional!' }
      ];

      let i = 0;
      const interval = setInterval(() => {
        if (i < steps.length) {
          if (bar) bar.style.width = steps[i].p + '%';
          if (txt) txt.innerText = steps[i].t;
          i++;
        } else {
          clearInterval(interval);
          dismissSplashScreen();
        }
      }, 200);
    }



    // ===============================================================
    // MASTER SECURITY ACCESS / ASTROLOGER LOGIN (admin / harman)
    // ===============================================================
    function checkAuthStatus() {
      const isAuth = localStorage.getItem('vedas_authenticated');
      const gateway = document.getElementById('vedasLoginGateway');
      if (isAuth === 'true') {
        if (gateway) gateway.style.display = 'none';
      } else {
        if (gateway) {
          gateway.style.display = 'flex';
          gateway.style.opacity = '1';
          setTimeout(() => {
            const pInput = document.getElementById('loginPassword');
            if (pInput) pInput.focus();
          }, 100);
        }
      }
    }

    async function doLogin() {
      const u = document.getElementById('loginUsername').value.trim();
      const p = document.getElementById('loginPassword').value.trim();
      const errBox = document.getElementById('loginErrorMsg');
      const succBox = document.getElementById('loginSuccessMsg');
      const gateway = document.getElementById('vedasLoginGateway');

      if (errBox) errBox.style.display = 'none';
      if (succBox) succBox.style.display = 'none';

      if (!u || !p) {
        if (errBox) {
          errBox.innerText = '⚠️ Please enter both User ID and Password.';
          errBox.style.display = 'block';
        }
        return;
      }

      try {
        const res = await fetch('/api/auth/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ username: u, password: p })
        });
        const data = await res.json();
        if (data.success) {
          if (succBox) succBox.style.display = 'block';
          const rem = document.getElementById('loginRememberMe');
          if (rem && rem.checked) {
            localStorage.setItem('vedas_authenticated', 'true');
          }
          loadDashboard();
          loadClientsTable();
          setTimeout(() => {
            gateway.style.opacity = '0';
            gateway.style.transition = 'opacity 0.4s ease-out';
            setTimeout(() => {
              gateway.style.display = 'none';
              loadDashboard();
            }, 400);
          }, 500);
        } else {
          if (errBox) {
            errBox.innerText = '⚠️ ' + (data.error || 'Invalid User ID or Password.');
            errBox.style.display = 'block';
          }
        }
      } catch (err) {
        // Direct local fallback verification
        if (u.toLowerCase() === 'admin' && p.toLowerCase() === 'harman') {
          if (succBox) succBox.style.display = 'block';
          const rem = document.getElementById('loginRememberMe');
          if (rem && rem.checked) {
            localStorage.setItem('vedas_authenticated', 'true');
          }
          setTimeout(() => {
            gateway.style.opacity = '0';
            gateway.style.transition = 'opacity 0.4s ease-out';
            setTimeout(() => {
              gateway.style.display = 'none';
            }, 400);
          }, 500);
        } else {
          if (errBox) {
            errBox.innerText = '⚠️ Invalid User ID or Password. (Use: admin / harman)';
            errBox.style.display = 'block';
          }
        }
      }
    }

    
    function switchGateMode(mode) {
      const adminForm = document.getElementById('gateAdminForm');
      const clientForm = document.getElementById('gateClientForm');
      const tabAdmin = document.getElementById('gateTabAdmin');
      const tabClient = document.getElementById('gateTabClient');
      if (mode === 'admin') {
        if (adminForm) adminForm.style.display = 'block';
        if (clientForm) clientForm.style.display = 'none';
        if (tabAdmin) { tabAdmin.style.background = '#FEF3C7'; tabAdmin.style.borderBottom = 'none'; }
        if (tabClient) { tabClient.style.background = '#FFFDF9'; tabClient.style.borderBottom = '1px solid #EADBC8'; }
      } else {
        if (adminForm) adminForm.style.display = 'none';
        if (clientForm) clientForm.style.display = 'flex';
        if (tabClient) { tabClient.style.background = '#FEF3C7'; tabClient.style.borderBottom = 'none'; }
        if (tabAdmin) { tabAdmin.style.background = '#FFFDF9'; tabAdmin.style.borderBottom = '1px solid #EADBC8'; }
        setTimeout(() => {
          const kInput = document.getElementById('loginClientKey');
          if (kInput) kInput.focus();
        }, 100);
      }
    }

    async function doKeyLogin() {
      const key = (document.getElementById('loginClientKey').value || '').trim();
      const errBox = document.getElementById('keyErrorMsg');
      const succBox = document.getElementById('loginSuccessMsg');
      const gateway = document.getElementById('vedasLoginGateway');
      if (errBox) errBox.style.display = 'none';

      if (!key) {
        if (errBox) {
          errBox.innerText = '⚠️ Please enter your Demo Access Key.';
          errBox.style.display = 'block';
        }
        return;
      }

      try {
        const res = await fetch('/api/auth/validate-key', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({key_code: key})
        });
        const data = await res.json();
        if (data.valid) {
          if (succBox) {
            succBox.innerText = '✨ Welcome ' + (data.client_name || '') + '! Access Granted until ' + (data.expires_at || '');
            succBox.style.display = 'block';
          }
          localStorage.setItem('vedas_authenticated', 'true');
          localStorage.setItem('vedas_role', 'client');
          localStorage.setItem('vedas_client_name', data.client_name || '');
          setTimeout(() => {
            if (gateway) gateway.style.display = 'none';
          }, 800);
        } else {
          if (errBox) {
            errBox.innerText = '❌ ' + (data.message || 'Invalid or Expired Demo Key');
            errBox.style.display = 'block';
          }
        }
      } catch (e) {
        if (errBox) {
          errBox.innerText = 'Error validating key: ' + e;
          errBox.style.display = 'block';
        }
      }
    }

    async function loadDemoKeys() {
      const tbody = document.getElementById('demoKeysTableBody');
      if (!tbody) return;
      try {
        const res = await fetch('/api/demo-keys');
        const data = await res.json();
        if (!data.keys || data.keys.length === 0) {
          tbody.innerHTML = '<tr><td colspan="5" style="text-align:center; color:#6B7280; padding:12px;">कोई चाबी नहीं बनी है। ऊपर फॉर्म से नई चाबी जनरेट करें।</td></tr>';
          return;
        }
        tbody.innerHTML = data.keys.map(k => {
          const isActive = (k.status === 'ACTIVE');
          const statusBadge = isActive 
            ? '<span style="background:#DEF7EC; color:#03543F; font-weight:800; padding:2px 8px; border-radius:10px; font-size:10px;">🟢 ACTIVE</span>'
            : '<span style="background:#FDE8E8; color:#9B1C1C; font-weight:800; padding:2px 8px; border-radius:10px; font-size:10px;">🔴 STOPPED</span>';
          
          const toggleBtn = isActive
            ? `<button type="button" onclick="toggleKeyStatus('${k.key_code}', 'STOPPED')" style="background:#DC2626; color:#fff; border:none; padding:4px 10px; border-radius:4px; font-weight:800; font-size:10.5px; cursor:pointer;">🔴 STOP</button>`
            : `<button type="button" onclick="toggleKeyStatus('${k.key_code}', 'ACTIVE')" style="background:#059669; color:#fff; border:none; padding:4px 10px; border-radius:4px; font-weight:800; font-size:10.5px; cursor:pointer;">🟢 ACTIVATE</button>`;

          return `<tr>
            <td><strong>${k.client_name}</strong></td>
            <td><code style="background:#F3F4F6; padding:2px 6px; border-radius:3px; font-weight:800; color:#7C2D12;">${k.key_code}</code> <button type="button" onclick="navigator.clipboard.writeText('${k.key_code}'); alert('Copied: ${k.key_code}')" style="background:#E5E7EB; border:none; cursor:pointer; padding:2px 6px; border-radius:3px; font-size:10px;">📋 Copy</button></td>
            <td style="font-size:11px;">${k.expires_at}</td>
            <td>${statusBadge}</td>
            <td>${toggleBtn}</td>
          </tr>`;
        }).join('');
      } catch (e) {
        tbody.innerHTML = '<tr><td colspan="5" style="color:red;">Error loading keys: ' + e + '</td></tr>';
      }
    }

    async function generateDemoKey() {
      const name = (document.getElementById('demoNewClientName').value || '').trim();
      const dur = parseInt(document.getElementById('demoNewDuration').value) || 7;
      if (!name) { alert('कृपया ग्राहक का नाम दर्ज करें!'); return; }

      try {
        const res = await fetch('/api/demo-keys/create', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({client_name: name, duration_days: dur})
        });
        const data = await res.json();
        if (data.success) {
          alert(`✅ नई डेमो चाबी तैयार है:\n\nग्राहक: ${data.key.client_name}\nचाबी: ${data.key.key_code}\nअवधि: ${data.key.duration_days > 0 ? data.key.duration_days + ' दिन' : 'आजीवन'}\n\nइसे कॉपी करके ग्राहक को भेजें!`);
          document.getElementById('demoNewClientName').value = '';
          loadDemoKeys();
        }
      } catch (e) {
        alert('Error creating key: ' + e);
      }
    }

    async function toggleKeyStatus(keyCode, newStatus) {
      const act = (newStatus === 'STOPPED') ? 'STOP (बंद)' : 'ACTIVATE (चालू)';
      if (!confirm(`क्या आप चाबी ${keyCode} को ${act} करना चाहते हैं?`)) return;

      try {
        const res = await fetch('/api/demo-keys/toggle', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({key_code: keyCode, status: newStatus})
        });
        const data = await res.json();
        if (data.success) {
          loadDemoKeys();
        }
      } catch (e) {
        alert('Error updating key: ' + e);
      }
    }


    function lockSuite() {
      localStorage.removeItem('vedas_authenticated');
      const gateway = document.getElementById('vedasLoginGateway');
      const errBox = document.getElementById('loginErrorMsg');
      const succBox = document.getElementById('loginSuccessMsg');
      if (errBox) errBox.style.display = 'none';
      if (succBox) succBox.style.display = 'none';
      const pInput = document.getElementById('loginPassword');
      if (pInput) pInput.value = '';
      if (gateway) {
        gateway.style.opacity = '1';
        gateway.style.display = 'flex';
      }
    }


    
    function openBuyModal() {
      const m = document.getElementById('vedasBuyModal');
      if (m) m.style.display = 'flex';
    }
    function closeBuyModal() {
      const m = document.getElementById('vedasBuyModal');
      if (m) m.style.display = 'none';
    }
    function copyUpiId() {
      const upi = document.getElementById('txtUpiId').innerText;
      navigator.clipboard.writeText(upi).then(() => {
        alert('✅ UPI ID ' + upi + ' कॉपी हो गई है! अब PhonePe/GPay में पेस्ट करके ₹699 पे करें।');
      }).catch(() => {
        alert('UPI ID: ' + upi);
      });
    }

    function initApp() {
      console.log('[Init] Shivansh Astro-Vastu Professional starting...');
      runSplashScreen();
      checkAuthStatus();
      loadDashboard();
      loadClientsTable();
      loadBrandingSettings();
      fetch('/api/heartbeat').catch(()=>{});
      setTimeout(loadDashboard, 1000);
      setTimeout(loadDashboard, 2500);
    }

    if (document.readyState === 'loading') {
      window.addEventListener('DOMContentLoaded', initApp);
    } else {
      initApp();
    }

// Clean exit via topbar close button only
  </script>

  <!-- =============================================================== -->
  <!-- 👑 HIGH-CONVERTING ₹699 LIFETIME BUY MODAL & UPI SCANNER -->
  <!-- =============================================================== -->
  <div id="vedasBuyModal" style="display:none; position:fixed; inset:0; z-index:999999; background:rgba(0,0,0,0.78); backdrop-filter:blur(6px); -webkit-backdrop-filter:blur(6px); align-items:center; justify-content:center; padding:14px;">
    <div style="background:linear-gradient(145deg, #23120A 0%, #120904 100%); border:2px solid #D4AF37; border-radius:18px; width:100%; max-width:480px; padding:22px; color:#FFF; box-shadow:0 20px 60px rgba(0,0,0,0.8); position:relative; max-height:92vh; overflow-y:auto; -webkit-overflow-scrolling:touch;">
      
      <!-- Close Button -->
      <button onclick="closeBuyModal()" style="position:absolute; top:14px; right:14px; background:rgba(255,255,255,0.12); border:1px solid rgba(255,255,255,0.2); color:#FEF08A; width:30px; height:30px; border-radius:50%; font-size:16px; font-weight:800; cursor:pointer; display:flex; align-items:center; justify-content:center;">✕</button>

      <div style="text-align:center;">
        <span style="background:linear-gradient(135deg, #EAB308 0%, #B45309 100%); color:#000; font-size:11px; font-weight:900; padding:4px 14px; border-radius:20px; letter-spacing:1px; text-transform:uppercase;">
          🔥 LIMITED TIME LAUNCH DEAL
        </span>
        <h2 style="font-family:'Cinzel', serif; font-size:22px; font-weight:900; color:#FEF08A; margin:8px 0 2px 0;">
          SHIVANSH ASTRO-VASTU PRO
        </h2>
        <p style="font-size:12.5px; color:#D1C7BD; margin:0 0 14px 0;">
          आजीवन वीआईपी लाइसेंस (One-Time Payment • No Monthly Fees)
        </p>

        <!-- Price Callout -->
        <div style="background:rgba(255,255,255,0.04); border:1.5px dashed #D4AF37; border-radius:12px; padding:10px; margin-bottom:14px;">
          <div style="font-size:13px; color:#A8A29E; text-decoration:line-through;">सामान्य कीमत: ₹15,000</div>
          <div style="font-size:38px; font-weight:900; color:#FEF08A; line-height:1.1; margin:2px 0;">
            ₹699 <span style="font-size:14px; color:#86EFAC; font-weight:700;">(लाइफटाइम)</span>
          </div>
          <div style="font-size:11.5px; color:#34D399; font-weight:700;">✓ पहले ही क्लाइंट की फीस में पूरा सॉफ्टवेयर 100% फ्री!</div>
        </div>

        <!-- 3 Mega Bonuses -->
        <div style="text-align:left; background:rgba(0,0,0,0.3); border-radius:10px; padding:12px; margin-bottom:14px; font-size:12px; line-height:1.6; color:#E5E7EB;">
          <div style="color:#FDE68A; font-weight:800; font-size:12.5px; margin-bottom:4px;">🎁 3 मुफ़्त महा-बोनस शामिल:</div>
          <div>✓ <b>बोनस 1:</b> मूल लाल किताब 1952 हस्तलिखित उपाय डायरेक्टरी (मूल्य ₹1,999)</div>
          <div>✓ <b>बोनस 2:</b> 36-गुण अष्टकूट विवाह मिलान 10-पेज डॉसियर (मूल्य ₹2,499)</div>
          <div>✓ <b>बोनस 3:</b> आपके ज्योतिष केंद्र का नाम व लोगो हर रिपोर्ट पर हमेशा के लिए सेट</div>
        </div>

        <!-- UPI QR Code Simulator -->
        <div style="background:#FFFFFF; border-radius:12px; padding:12px; display:inline-block; margin-bottom:10px; box-shadow:0 4px 15px rgba(0,0,0,0.3);">
          <img src="https://api.qrserver.com/v1/create-qr-code/?size=160x160&data=upi://pay?pa=harmanjotsingh0310@okaxis&pn=Shivansh%20Astro%20Vastu&am=699&cu=INR" alt="Scan & Pay ₹699 via PhonePe/GPay/Paytm" style="width:145px; height:145px; display:block;"/>
          <div style="font-size:11px; font-weight:800; color:#1F2937; margin-top:4px;">GPay • PhonePe • Paytm • UPI</div>
        </div>

        <div style="margin-bottom:14px;">
          <span style="font-size:11.5px; color:#A8A29E;">UPI ID: </span>
          <code style="background:rgba(255,255,255,0.08); border:1px solid #D4AF37; padding:3px 8px; border-radius:6px; color:#FEF08A; font-size:12px; font-weight:800;" id="txtUpiId">harmanjotsingh0310@okaxis</code>
          <button onclick="copyUpiId()" style="background:#D4AF37; color:#000; font-weight:800; font-size:11px; border:none; padding:4px 8px; border-radius:4px; margin-left:6px; cursor:pointer;">📋 Copy</button>
        </div>

        <!-- Direct WhatsApp Activation CTA -->
        <a href="https://wa.me/?text=Hello!%20I%20have%20paid%20Rs.699%20for%20Shivansh%20Astro%20Vastu%20Lifetime%20License.%20Attached%20is%20my%20screenshot.%20Please%20send%20my%20activation%20key!" target="_blank" style="display:block; width:100%; background:linear-gradient(135deg, #25D366 0%, #128C7E 100%); color:#FFF; font-weight:900; font-size:14.5px; padding:12px; border-radius:10px; text-decoration:none; text-align:center; box-shadow:0 4px 16px rgba(37,211,102,0.4); margin-bottom:8px;">
          💬 WhatsApp पर स्क्रीनशॉट भेजें (Instant Key)
        </a>
        <div style="font-size:11px; color:#9CA3AF;">
          ⚡ स्क्रीनशॉट भेजते ही 2 मिनट में आपकी चाबी एक्टिवेट हो जाएगी।
        </div>
      </div>
    </div>
  </div>

</body>
</html>
""", headers=headers)


def find_open_port(start_port=8088):
    import socket
    for p in range(start_port, start_port + 50):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('127.0.0.1', p))
                return p
        except OSError:
            continue
    return start_port


if __name__ == "__main__":
    init_crm_db()
    port = find_open_port(8088)
    app_url = f"http://127.0.0.1:{port}"
    print("==================================================================")
    print(f"  Shivansh Astro-Vastu Suite running at: {app_url}")
    print("  Login ID: Admin | Password: Harman")
    print("==================================================================")
    Timer(1.2, lambda: webbrowser.open(app_url)).start()
    uvicorn.run(app, host="127.0.0.1", port=port)
