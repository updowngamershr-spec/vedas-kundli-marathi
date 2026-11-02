# -*- coding: utf-8 -*-
"""
Module 5: Nakshatra and Pada Calculation Engine
Calculates Nakshatra (1-27), Pada (1-4), Nakshatra Lord, and Pada Sub-Lord directly
from the exact sidereal longitude of Moon and all planets.
Formulas:
- Nakshatra Index = floor(Sidereal Longitude / 13°20') + 1
- Remaining Longitude = Sidereal Longitude % 13°20'
- Pada = floor(Remaining Longitude / 3°20') + 1
Lord Sequence: Ketu, Venus, Sun, Moon, Mars, Rahu, Jupiter, Saturn, Mercury (repeating 3 times).
"""

import math

NAKSHATRAS = [
    {"num": 1, "name_en": "Ashwini", "name_hi": "अश्विनी", "name_mr": "अश्विनी", "lord_en": "Ketu", "lord_mr": "केतू"},
    {"num": 2, "name_en": "Bharani", "name_hi": "भरणी", "name_mr": "भरणी", "lord_en": "Venus", "lord_mr": "शुक्र"},
    {"num": 3, "name_en": "Krittika", "name_hi": "कृत्तिका", "name_mr": "कृतिका", "lord_en": "Sun", "lord_mr": "रवी"},
    {"num": 4, "name_en": "Rohini", "name_hi": "रोहिणी", "name_mr": "रोहिणी", "lord_en": "Moon", "lord_mr": "चंद्र"},
    {"num": 5, "name_en": "Mrigashira", "name_hi": "मृगशिरा", "name_mr": "मृगशीर्ष", "lord_en": "Mars", "lord_mr": "मंगळ"},
    {"num": 6, "name_en": "Ardra", "name_hi": "आर्द्रा", "name_mr": "आर्द्रा", "lord_en": "Rahu", "lord_mr": "राहू"},
    {"num": 7, "name_en": "Punarvasu", "name_hi": "पुनर्वसु", "name_mr": "पुनर्वसू", "lord_en": "Jupiter", "lord_mr": "गुरू"},
    {"num": 8, "name_en": "Pushya", "name_hi": "पुष्य", "name_mr": "पुष्य", "lord_en": "Saturn", "lord_mr": "शनी"},
    {"num": 9, "name_en": "Ashlesha", "name_hi": "आश्लेषा", "name_mr": "आश्लेषा", "lord_en": "Mercury", "lord_mr": "बुध"},
    {"num": 10, "name_en": "Magha", "name_hi": "मघा", "name_mr": "मघा", "lord_en": "Ketu", "lord_mr": "केतू"},
    {"num": 11, "name_en": "Purva Phalguni", "name_hi": "पूर्वा फाल्गुनी", "name_mr": "पूर्वा फाल्गुनी", "lord_en": "Venus", "lord_mr": "शुक्र"},
    {"num": 12, "name_en": "Uttara Phalguni", "name_hi": "उत्तरा फाल्गुनी", "name_mr": "उत्तरा फाल्गुनी", "lord_en": "Sun", "lord_mr": "रवी"},
    {"num": 13, "name_en": "Hasta", "name_hi": "हस्त", "name_mr": "हस्त", "lord_en": "Moon", "lord_mr": "चंद्र"},
    {"num": 14, "name_en": "Chitra", "name_hi": "चित्रा", "name_mr": "चित्रा", "lord_en": "Mars", "lord_mr": "मंगळ"},
    {"num": 15, "name_en": "Swati", "name_hi": "स्वाति", "name_mr": "स्वाती", "lord_en": "Rahu", "lord_mr": "राहू"},
    {"num": 16, "name_en": "Vishakha", "name_hi": "विशाखा", "name_mr": "विशाखा", "lord_en": "Jupiter", "lord_mr": "गुरू"},
    {"num": 17, "name_en": "Anuradha", "name_hi": "अनुराधा", "name_mr": "अनुराधा", "lord_en": "Saturn", "lord_mr": "शनी"},
    {"num": 18, "name_en": "Jyeshtha", "name_hi": "ज्येष्ठा", "name_mr": "ज्येष्ठा", "lord_en": "Mercury", "lord_mr": "बुध"},
    {"num": 19, "name_en": "Moola", "name_hi": "मूल", "name_mr": "मूळ", "lord_en": "Ketu", "lord_mr": "केतू"},
    {"num": 20, "name_en": "Purva Ashadha", "name_hi": "पूर्वाषाढ़ा", "name_mr": "पूर्वाषाढा", "lord_en": "Venus", "lord_mr": "शुक्र"},
    {"num": 21, "name_en": "Uttara Ashadha", "name_hi": "उत्तराषाढ़ा", "name_mr": "उत्तराषाढा", "lord_en": "Sun", "lord_mr": "रवी"},
    {"num": 22, "name_en": "Shravana", "name_hi": "श्रवण", "name_mr": "श्रवण", "lord_en": "Moon", "lord_mr": "चंद्र"},
    {"num": 23, "name_en": "Dhanishta", "name_hi": "धनिष्ठा", "name_mr": "धनिष्ठा", "lord_en": "Mars", "lord_mr": "मंगळ"},
    {"num": 24, "name_en": "Shatabhisha", "name_hi": "शतभिषा", "name_mr": "शततारका", "lord_en": "Rahu", "lord_mr": "राहू"},
    {"num": 25, "name_en": "Purva Bhadrapada", "name_hi": "पूर्वभाद्रपद", "name_mr": "पूर्वभाद्रपदा", "lord_en": "Jupiter", "lord_mr": "गुरू"},
    {"num": 26, "name_en": "Uttara Bhadrapada", "name_hi": "उत्तरभाद्रपद", "name_mr": "उत्तरभाद्रपदा", "lord_en": "Saturn", "lord_mr": "शनी"},
    {"num": 27, "name_en": "Revati", "name_hi": "रेवती", "name_mr": "रेवती", "lord_en": "Mercury", "lord_mr": "बुध"},
]

VIMSHOTTARI_LORDS = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
VIMSHOTTARI_YEARS = {"Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7, "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17}


def calculate_nakshatra_and_pada(sid_lon_deg: float) -> dict:
    """
    Calculate exact Nakshatra, Pada, and degrees within Pada.
    """
    norm_lon = sid_lon_deg % 360.0
    nak_len = 13.0 + (20.0 / 60.0)  # 13°20' = 13.33333333°
    pada_len = 3.0 + (20.0 / 60.0)  # 3°20'  = 3.33333333°

    nak_idx = int(norm_lon // nak_len)  # 0 to 26
    rem_lon = norm_lon - (nak_idx * nak_len)
    pada_idx = int(rem_lon // pada_len)  # 0 to 3

    nak_num = nak_idx + 1
    pada_num = pada_idx + 1

    nak_meta = NAKSHATRAS[nak_idx]
    lord_en = nak_meta["lord_en"]
    lord_mr = nak_meta["lord_mr"]

    # Degree, minute, second inside the Nakshatra
    rem_d = int(rem_lon)
    rem_m = int((rem_lon - rem_d) * 60.0)
    rem_s = int(round(((rem_lon - rem_d) * 60.0 - rem_m) * 60.0))

    # Fraction traversed and remaining
    traversed_frac = rem_lon / nak_len
    remaining_frac = 1.0 - traversed_frac

    return {
        "nak_idx": nak_idx,
        "nak_num": nak_num,
        "nak_name_en": nak_meta["name_en"],
        "nak_name_hi": nak_meta["name_hi"],
        "nak_name_mr": nak_meta["name_mr"],
        "pada": pada_num,
        "nak_lord_en": lord_en,
        "nak_lord_mr": lord_mr,
        "nak_duration_years": VIMSHOTTARI_YEARS[lord_en],
        "rem_lon_deg": rem_lon,
        "rem_dms": f"{rem_d:02d}° {rem_m:02d}' {rem_s:02d}\"",
        "traversed_fraction": traversed_frac,
        "remaining_fraction": remaining_frac,
    }


def enrich_planets_with_nakshatra(planets_list: list) -> list:
    """Enrich each planet with its exact Nakshatra, Pada, and Lord."""
    for p in planets_list:
        nak_info = calculate_nakshatra_and_pada(p["sid_lon"])
        p["nakshatra"] = nak_info["nak_name_en"]
        p["nakshatra_mr"] = nak_info["nak_name_mr"]
        p["nakshatra_hi"] = nak_info["nak_name_hi"]
        p["nak_num"] = nak_info["nak_num"]
        p["pada"] = nak_info["pada"]
        p["nak_lord_en"] = nak_info["nak_lord_en"]
        p["nak_lord_mr"] = nak_info["nak_lord_mr"]
        p["nak_pada_str"] = f"{nak_info['nak_name_mr']} ({nak_info['pada']})"
    return planets_list
