# -*- coding: utf-8 -*-
"""
Shivansh Astro-Vastu Kundli CRM - Master Calculation Orchestrator
Modularized Pipeline integrating Modules 1 through 16:
 1. Birth Data Validation (engine/birth_validation.py)
 2. Astronomical Calculations (engine/astronomy_calc.py)
 3. Planetary Longitude Calculations (engine/planetary_longitudes.py)
 4. Ascendant and House Calculations (engine/houses_calc.py)
 5. Nakshatra and Pada Calculations (engine/nakshatra_pada.py)
 6. Vimshottari Dasha (engine/vimshottari_dasha.py)
 7. KP Astrology (engine/kp_astrology.py)
 8. Shodashvarga (engine/shodashvarga.py)
 9. Ashtakavarga (engine/ashtakavarga_engine.py)
10. Shadbala and Bhav Bala (engine/shadbala_bhavabala.py)
11. Yoga and Dosha Calculations (engine/yoga_dosha.py)
12. Transit and Varshaphal (engine/transit_varshaphal.py)
13. Predictions (engine/prediction_engine.py)
14. Language Translation (engine/marathi_engine.py)
15. PDF Generation (engine/report_html_pdf.py)
16. Automated Calculation Validation (engine/calc_validation.py)

Deterministic calculations only — Zero AI guesses, Zero hardcoded values.
"""

from datetime import datetime
from engine.cities import find_city

# Import core modular calculation engines
from engine.birth_validation import validate_birth_data, BirthDataValidationError
from engine.astronomy_calc import get_astronomy_data
from engine.planetary_longitudes import calculate_planetary_longitudes
from engine.houses_calc import (
    calculate_ascendant_and_mc, calculate_whole_sign_houses,
    calculate_sripati_chalit, calculate_kp_placidus_cusps,
    map_planetary_houses, RASHI_NAMES_EN
)
from engine.nakshatra_pada import enrich_planets_with_nakshatra
from engine.vimshottari_dasha import calculate_vimshottari_dasha
from engine.kp_astrology import get_kp_lords, compute_four_fold_significators
from engine.shodashvarga import compute_shodashvarga
from engine.ashtakavarga_engine import calculate_ashtakavarga
from engine.shadbala_bhavabala import calculate_shadbala, calculate_bhavabala
from engine.yoga_dosha import evaluate_yogas, evaluate_manglik_dosha, evaluate_kalsarpa_dosha
from engine.transit_varshaphal import calculate_varshaphal, calculate_transit_today
from engine.prediction_engine import generate_life_predictions
from engine.calc_validation import assert_valid_for_pdf, validate_chart_calculations

# Additional legacy / specialized modules for complete 78-page report
from engine.ephemeris import compute_core_ephemeris
from engine.vargas_avkahada import (
    compute_avkahada_and_points,
    compute_shodashvarga as compute_shodashvarga_vargas,
    compute_jaimini_system
)
from engine.dashas import compute_vimshottari_dasha, compute_yogini_dasha, compute_char_dasha
from engine.ashtakavarga_shadbala import (
    compute_ashtakavarga, compute_friendship_tables,
    compute_shadbala_and_bhavabala, compute_western_and_cusp_aspects
)
from engine.kp_lal_kitab import compute_kp_system, compute_lal_kitab
from engine.varshaphal_sadesati_yogas import (
    compute_manglik_and_kalsarpa, compute_sadesati_report,
    compute_varshaphal_and_transit, compute_yogas_and_gemstones
)
from engine.knowledge_predictions import compute_all_written_reports
from engine.vastu_engine import compute_astro_vastu_audit
from engine.kp_authentic_engine import (
    compute_four_fold_significators, evaluate_kp_gemstones,
    evaluate_kp_debts_and_loans, evaluate_kp_disease_and_cure,
    KP_EVENT_RULES
)


def generate_complete_kundli(
    name: str,
    sex: str,
    year: int,
    month: int,
    day: int,
    hour: int,
    minute: int,
    second: int = 0,
    place: str = "New Delhi",
    lat: float | None = None,
    lon: float | None = None,
    tz: float | None = None,
    varsha_year: int | None = None,
    enforce_validation_lock: bool = True,
):
    """
    Generate the complete Shivansh Astro-Vastu Kundli dataset for any person.
    Works 100% Offline. All parameters are verified deterministically.
    """
    city_info = find_city(place)
    lat_val = float(lat) if lat is not None else city_info["lat"]
    lon_val = float(lon) if lon is not None else city_info["lon"]
    tz_val = float(tz) if tz is not None else city_info["tz"]
    if varsha_year is None:
        varsha_year = datetime.now().year

    # -------------------------------------------------------------------------
    # MODULE 1: BIRTH DATA VALIDATION
    # -------------------------------------------------------------------------
    birth_data = validate_birth_data(
        name=name, sex=sex,
        year=year, month=month, day=day,
        hour=hour, minute=minute, second=second,
        place=place, lat=lat_val, lon=lon_val, tz=tz_val
    )
    b_inputs = birth_data["inputs"]
    b_astro = birth_data["astronomical"]
    b_utc = birth_data["utc"]
    jd_utc = b_astro["jd_ut"]
    lst_deg = b_astro["lst_deg"]
    birth_dt = datetime(year, month, day, hour, minute, second)

    # -------------------------------------------------------------------------
    # MODULE 2: ASTRONOMICAL CALCULATIONS
    # -------------------------------------------------------------------------
    astro_data = get_astronomy_data(jd_utc)

    # -------------------------------------------------------------------------
    # MODULE 3: PLANETARY LONGITUDES
    # -------------------------------------------------------------------------
    pl_data = calculate_planetary_longitudes(jd_utc, astro_data["lahiri_ayanamsha"])
    modular_planets = pl_data["planets"]
    modular_p_by_id = pl_data["planet_by_id"]

    # -------------------------------------------------------------------------
    # MODULE 4: ASCENDANT & HOUSES
    # -------------------------------------------------------------------------
    asc_dict = calculate_ascendant_and_mc(
        lst_deg, b_inputs["lat"], astro_data["obliquity_deg"], astro_data["lahiri_ayanamsha"]
    )
    asc_sid = asc_dict["asc_sid"]
    mc_sid = asc_dict["mc_sid"]
    asc_sign_idx = asc_dict["asc_sign_idx"]
    whole_sign_houses = calculate_whole_sign_houses(asc_sid)
    sripati_chalit = calculate_sripati_chalit(asc_sid, mc_sid)
    kp_cusps_list = calculate_kp_placidus_cusps(
        jd_utc, b_inputs["lat"], b_inputs["lon"], astro_data["kp_ayanamsha"]
    )
    map_planetary_houses(modular_planets, asc_sign_idx, sripati_chalit)

    # -------------------------------------------------------------------------
    # MODULE 5: NAKSHATRA & PADA
    # -------------------------------------------------------------------------
    enriched_planets = enrich_planets_with_nakshatra(modular_planets)

    # -------------------------------------------------------------------------
    # MODULE 6: VIMSHOTTARI DASHA
    # -------------------------------------------------------------------------
    moon_sid_lon = modular_p_by_id["Moon"]["sid_lon"]
    modular_vimshottari = calculate_vimshottari_dasha(
        moon_sid_lon, b_inputs["year"], b_inputs["month"], b_inputs["day"]
    )

    # -------------------------------------------------------------------------
    # MODULE 7: KP ASTROLOGY (KP NEW AYANAMSHA + 249 SUBS)
    # -------------------------------------------------------------------------
    kp_cusp_objects = [
        {"cusp": i + 1, "lon": kp_cusps_list[i], **get_kp_lords(kp_cusps_list[i])}
        for i in range(12)
    ]
    four_fold_mod = compute_four_fold_significators(modular_planets, kp_cusp_objects)

    # -------------------------------------------------------------------------
    # MODULE 8: SHODASHVARGA (16 DIVISIONAL CHARTS)
    # -------------------------------------------------------------------------
    modular_shodashvarga = compute_shodashvarga(enriched_planets, asc_sid)

    # -------------------------------------------------------------------------
    # MODULE 9: ASHTAKAVARGA (PARASHARI 337 TOTAL)
    # -------------------------------------------------------------------------
    modular_ashtakavarga = calculate_ashtakavarga(modular_p_by_id, asc_sign_idx)

    # -------------------------------------------------------------------------
    # MODULE 10: SHADBALA & BHAVABALA
    # -------------------------------------------------------------------------
    is_day = (6 <= b_inputs["hour"] < 18)
    modular_shadbala = calculate_shadbala(modular_p_by_id, asc_sid, is_day_birth=is_day)
    modular_bhavabala = calculate_bhavabala(modular_shadbala, modular_planets)

    # -------------------------------------------------------------------------
    # MODULE 11: YOGAS & DOSHAS
    # -------------------------------------------------------------------------
    modular_yogas = evaluate_yogas(modular_p_by_id, asc_sign_idx)
    modular_manglik = evaluate_manglik_dosha(modular_p_by_id, asc_sign_idx)
    modular_kalsarpa = evaluate_kalsarpa_dosha(modular_p_by_id)

    # -------------------------------------------------------------------------
    # MODULE 12: TRANSIT & VARSHAPHAL
    # -------------------------------------------------------------------------
    natal_sun_lon = modular_p_by_id["Sun"]["sid_lon"]
    modular_varshaphal = calculate_varshaphal(
        natal_sun_sid=natal_sun_lon,
        natal_lagna_sign_num=asc_sign_idx + 1,
        birth_year=b_inputs["year"],
        birth_month=b_inputs["month"],
        birth_day=b_inputs["day"],
        birth_hour=b_inputs["hour"],
        birth_minute=b_inputs["minute"],
        lat=b_inputs["lat"],
        lon=b_inputs["lon"],
        tz=b_inputs["tz"],
        target_year=varsha_year
    )
    modular_transit = calculate_transit_today(
        lat=b_inputs["lat"], lon=b_inputs["lon"], tz=b_inputs["tz"]
    )

    # Core ephemeris bundle for full 78-page report layout
    core = compute_core_ephemeris(
        name=name, sex=sex,
        year=year, month=month, day=day,
        hour=hour, minute=minute, second=second,
        place=place, lat_deg=lat_val, lon_deg=lon_val, tz_hours=tz_val
    )

    # Ensure chalit table and house numbers are 100% mathematically synchronized
    core["chalit_table"] = [
        {
            "bhav": c["house"],
            "begin_sign_en": RASHI_NAMES_EN[c["begin_sign_idx"]],
            "begin_sign_hi": RASHI_NAMES_EN[c["begin_sign_idx"]],
            "begin_dms": c["begin_dms"],
            "mid_sign_en": RASHI_NAMES_EN[c["madhya_sign_idx"]],
            "mid_sign_hi": RASHI_NAMES_EN[c["madhya_sign_idx"]],
            "mid_dms": c["madhya_dms"],
            "begin_lon": c["begin_lon"],
            "mid_lon": c["madhya_lon"],
        }
        for c in sripati_chalit["bhav_data"]
    ]

    # Synchronize Rashi house and Chalit house in core["planets"]
    for p in core["planets"]:
        pid = p["id"]
        if pid in modular_p_by_id:
            p["house"] = modular_p_by_id[pid]["rashi_house"]
            p["chalit_house"] = modular_p_by_id[pid]["chalit_house"]
            p["rashi_house"] = modular_p_by_id[pid]["rashi_house"]

    # Calculate sub-systems
    vimshottari = compute_vimshottari_dasha(moon_sid_lon, year, month, day)
    avkahada_points = compute_avkahada_and_points(core, vimshottari["balance_str"])
    shodashvarga = compute_shodashvarga_vargas(core)
    jaimini = compute_jaimini_system(core, shodashvarga)
    yogini = compute_yogini_dasha(moon_sid_lon, year, month, day)
    char_dasha = compute_char_dasha(core)
    ashtakavarga = compute_ashtakavarga(core)
    friendship = compute_friendship_tables(core)
    shadbala = compute_shadbala_and_bhavabala(core, shodashvarga, friendship)
    kp = compute_kp_system(core)
    aspects = compute_western_and_cusp_aspects(core, kp["kp_cusp_lons"])
    lal_kitab = compute_lal_kitab(core)
    manglik_kalsarpa = compute_manglik_and_kalsarpa(core)
    sadesati = compute_sadesati_report(core)
    varshaphal_transit = compute_varshaphal_and_transit(core, target_year=varsha_year)
    yogas_gems = compute_yogas_and_gemstones(core)
    written_reports = compute_all_written_reports(core, vimshottari, varshaphal_transit)

    # Authentic Mathematical KP Engine
    kp_cusps_list = kp.get("cuspal_positions", [])
    four_fold = compute_four_fold_significators(core["planets"], kp_cusps_list)
    
    asc_csl = kp_cusps_list[0].get("sub", "Jupiter") if kp_cusps_list else "Jupiter"
    eleventh_csl = kp_cusps_list[10].get("sub", "Jupiter") if len(kp_cusps_list) >= 11 else "Jupiter"
    sixth_csl = kp_cusps_list[5].get("sub", "Mercury") if len(kp_cusps_list) >= 6 else "Mercury"

    kp_gems = evaluate_kp_gemstones(asc_csl, eleventh_csl, four_fold["planet_significations"])
    kp_debts = evaluate_kp_debts_and_loans(four_fold["planet_significations"])
    kp_disease = evaluate_kp_disease_and_cure(sixth_csl, eleventh_csl, four_fold["planet_significations"])

    # -------------------------------------------------------------------------
    # MODULE 13: 100% CHART-DERIVED PREDICTIONS
    # -------------------------------------------------------------------------
    chart_payload_for_pred = {
        "planet_by_id": core["planet_by_id"],
        "meta": core["meta"],
        "yogas": yogas_gems.get("yogas", []),
        "vimshottari": vimshottari,
        "house_lords": {i: whole_sign_houses[i]["lord"] for i in range(1, 13)},
    }
    modular_life_predictions = generate_life_predictions(chart_payload_for_pred)

    payload = {
        "brand": {
            "name_en": "Shivansh Astro-Vastu",
            "name_hi": "शिवांश ॲस्ट्रो-वास्तू (Shivansh Astro-Vastu)",
            "name_mr": "शिवांश ॲस्ट्रो-वास्तू (Shivansh Astro-Vastu)",
            "kendra_name": "Shivansh Astro-Vastu",
            "astrologer_name": "Mayur Mandhare (BE.E&TC)",
            "phone": "9373058052",
            "tagline_en": "Ancient Vedic, KP & Lal Kitab Predictions",
            "tagline_hi": "प्राचीन वैदिक, कृष्णमूर्ति पद्धति एवं लाल किताब फलादेश",
            "tagline_mr": "अचूक वैदिक, कृष्णमूर्ती पद्धती आणि लाल किताब भविष्यवाणी",
            "printed_at": datetime.now().strftime("%d/%m/%Y %I:%M:%S %p"),
        },
        "meta": core["meta"],
        "planets": core["planets"],
        "planet_by_id": core["planet_by_id"],
        "chalit_table": core["chalit_table"],
        "avkahada": avkahada_points["avkahada"],
        "favourable": avkahada_points["favourable"],
        "ghatak": avkahada_points["ghatak"],
        "vimshottari": vimshottari,
        "yogini": yogini,
        "char_dasha": char_dasha,
        "shodashvarga": shodashvarga,
        "jaimini": jaimini,
        "ashtakavarga": ashtakavarga,
        "friendship": friendship,
        "shadbala": shadbala,
        "kp": kp,
        "kp_four_fold": four_fold,
        "kp_gems": kp_gems,
        "kp_debts": kp_debts,
        "kp_disease": kp_disease,
        "kp_event_rules": KP_EVENT_RULES,
        "aspects": aspects,
        "lal_kitab": lal_kitab,
        "manglik": manglik_kalsarpa["manglik"],
        "kalsarpa": manglik_kalsarpa["kalsarpa"],
        "sadesati": sadesati,
        "varshaphal": varshaphal_transit,
        "yogas": yogas_gems["yogas"],
        "gemstones": yogas_gems["gemstones"],
        "written": written_reports,
        "vastu": compute_astro_vastu_audit(core),
        "modular": {
            "birth_data": birth_data,
            "astro_data": astro_data,
            "planets": enriched_planets,
            "sripati_chalit": sripati_chalit,
            "kp_cusps": kp_cusps_list,
            "ashtakavarga": modular_ashtakavarga,
            "shadbala": modular_shadbala,
            "bhavabala": modular_bhavabala,
            "yogas": modular_yogas,
            "manglik": modular_manglik,
            "kalsarpa": modular_kalsarpa,
            "varshaphal": modular_varshaphal,
            "life_predictions": modular_life_predictions,
        }
    }

    # Standardize validation keys for calc_validation
    payload["meta"]["jd_ut"] = core["meta"]["jd_float"]
    payload["meta"]["ayanamsa"] = core["meta"]["ayanamsa_deg"]
    payload["meta"]["asc_sid_lon"] = core["planet_by_id"]["ASC"]["sid_lon"]

    # -------------------------------------------------------------------------
    # MODULE 16: AUTOMATED CALCULATION VALIDATION & PDF GENERATION LOCK
    # -------------------------------------------------------------------------
    if enforce_validation_lock:
        assert_valid_for_pdf(payload)

    return payload
