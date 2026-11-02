# -*- coding: utf-8 -*-
"""
Gurukulam Kundli CRM - Master Kundli Orchestrator
Combines all astronomical, Parashari, Jaimini, KP (Reader III & KP House Groupings), Tajika Varshaphal, Sade Sati,
Ashtakavarga, Shadbala, Lal Kitab (with 1952 Farman), and SVG Charts
into a single unified data payload.
"""

from datetime import datetime
from engine.cities import find_city
from engine.ephemeris import compute_core_ephemeris
from engine.vargas_avkahada import compute_avkahada_and_points, compute_shodashvarga, compute_jaimini_system
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
):
    """
    Generate the complete Gurukulam Kundli dataset for any person.
    Works 100% Offline. All parameters are REQUIRED (name, sex, year, month, day, hour, minute).
    No hardcoded fallbacks for individual client data.
    """
    city_info = find_city(place)
    lat_val = float(lat) if lat is not None else city_info["lat"]
    lon_val = float(lon) if lon is not None else city_info["lon"]
    tz_val = float(tz) if tz is not None else city_info["tz"]
    if varsha_year is None:
        varsha_year = datetime.now().year

    core = compute_core_ephemeris(
        name=name, sex=sex,
        year=year, month=month, day=day,
        hour=hour, minute=minute, second=second,
        place=place, lat_deg=lat_val, lon_deg=lon_val, tz_hours=tz_val
    )

    moon_sid = core["planet_by_id"]["Moon"]["sid_lon"]
    vimshottari = compute_vimshottari_dasha(moon_sid, year, month, day)
    avkahada_points = compute_avkahada_and_points(core, vimshottari["balance_str"])
    shodashvarga = compute_shodashvarga(core)
    jaimini = compute_jaimini_system(core, shodashvarga)
    yogini = compute_yogini_dasha(moon_sid, year, month, day)
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

    # Authentic Mathematical KP Engine (Reader III + KP House Groupings)
    kp_cusps_list = kp.get("cuspal_positions", [])
    four_fold = compute_four_fold_significators(core["planets"], kp_cusps_list)
    
    asc_csl = kp_cusps_list[0].get("sub", "Jupiter") if kp_cusps_list else "Jupiter"
    eleventh_csl = kp_cusps_list[10].get("sub", "Jupiter") if len(kp_cusps_list) >= 11 else "Jupiter"
    sixth_csl = kp_cusps_list[5].get("sub", "Mercury") if len(kp_cusps_list) >= 6 else "Mercury"

    kp_gems = evaluate_kp_gemstones(asc_csl, eleventh_csl, four_fold["planet_significations"])
    kp_debts = evaluate_kp_debts_and_loans(four_fold["planet_significations"])
    kp_disease = evaluate_kp_disease_and_cure(sixth_csl, eleventh_csl, four_fold["planet_significations"])

    return {
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
    }
