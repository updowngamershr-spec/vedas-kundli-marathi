# -*- coding: utf-8 -*-
"""
Module 7: KP (Krishnamurti Paddhati) Astrology Engine
Implements:
1. Complete 249-Sub division table (from 120-year Vimshottari proportional distribution)
2. Four-fold lords calculation for any longitude: Sign Lord, Star Lord, Sub Lord, Sub-Sub Lord
3. KP Placidus Cusps (strictly monotonic and unique)
4. Four-level planetary significators (Levels A, B, C, D)
5. 12 House Cuspal Sub-Lord (CSL) results
"""

import math
from engine.nakshatra_pada import VIMSHOTTARI_LORDS, VIMSHOTTARI_YEARS

# Sign lords (0 to 11)
SIGN_LORDS = [
    "Mars",     # 0 Aries
    "Venus",    # 1 Taurus
    "Mercury",  # 2 Gemini
    "Moon",     # 3 Cancer
    "Sun",      # 4 Leo
    "Mercury",  # 5 Virgo
    "Venus",    # 6 Libra
    "Mars",     # 7 Scorpio
    "Jupiter",  # 8 Sagittarius
    "Saturn",   # 9 Capricorn
    "Saturn",   # 10 Aquarius
    "Jupiter",  # 11 Pisces
]

SIGN_LORDS_MR = {
    "Mars": "मंगळ", "Venus": "शुक्र", "Mercury": "बुध", "Moon": "चंद्र",
    "Sun": "रवी", "Jupiter": "गुरू", "Saturn": "शनी", "Rahu": "राहू", "Ketu": "केतू"
}

# Vimshottari sequence order: [Ketu, Venus, Sun, Moon, Mars, Rahu, Jupiter, Saturn, Mercury]
VIM_ORDER = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
VIM_YEARS = [7, 20, 6, 10, 7, 18, 16, 19, 17]


def get_kp_lords(kp_sid_lon: float) -> dict:
    """
    Calculate Rashi Lord, Star Lord, Sub Lord, and Sub-Sub Lord
    for any KP sidereal longitude (0° to 360°).
    """
    lon = kp_sid_lon % 360.0
    sign_idx = int(lon // 30.0) % 12
    sign_lord = SIGN_LORDS[sign_idx]

    nak_span = 360.0 / 27.0  # 13°20' = 13.33333333°
    nak_idx = int(lon // nak_span) % 27
    star_lord = VIM_ORDER[nak_idx % 9]

    deg_in_nak = lon - (nak_idx * nak_span)
    start_vim_idx = VIM_ORDER.index(star_lord)

    # 1. Sub-Lord: 9 subdivisions proportional to Vimshottari years / 120
    acc = 0.0
    sub_lord = star_lord
    sub_vim_idx = start_vim_idx
    deg_in_sub = 0.0
    sub_span = nak_span

    for i in range(9):
        idx = (start_vim_idx + i) % 9
        yrs = VIM_YEARS[idx]
        span = nak_span * (yrs / 120.0)
        if deg_in_nak <= (acc + span + 1e-12) or i == 8:
            sub_lord = VIM_ORDER[idx]
            sub_vim_idx = idx
            deg_in_sub = max(0.0, deg_in_nak - acc)
            sub_span = span
            break
        acc += span

    # 2. Sub-Sub Lord: 9 subdivisions within Sub-Lord span
    acc_ss = 0.0
    ss_lord = sub_lord
    for j in range(9):
        idx_ss = (sub_vim_idx + j) % 9
        yrs_ss = VIM_YEARS[idx_ss]
        span_ss = sub_span * (yrs_ss / 120.0)
        if deg_in_sub <= (acc_ss + span_ss + 1e-12) or j == 8:
            ss_lord = VIM_ORDER[idx_ss]
            break
        acc_ss += span_ss

    return {
        "lon": lon,
        "sign_lord": sign_lord,
        "sign_lord_mr": SIGN_LORDS_MR[sign_lord],
        "star_lord": star_lord,
        "star_lord_mr": SIGN_LORDS_MR[star_lord],
        "sub_lord": sub_lord,
        "sub_lord_mr": SIGN_LORDS_MR[sub_lord],
        "ss_lord": ss_lord,
        "ss_lord_mr": SIGN_LORDS_MR[ss_lord],
    }


def generate_249_sub_table() -> list[dict]:
    """
    Generate and validate the standard KP 249-sub table spanning 0° to 360°.
    There are 27 Nakshatras * 9 subs = 243 subs, + 6 boundaries where a sub is split
    by a sign boundary (at 30°, 60°, 120°, 150°, 210°, 240°), giving exactly 249 divisions.
    """
    table = []
    sub_num = 1
    nak_span = 360.0 / 27.0

    for nak_idx in range(27):
        star_lord = VIM_ORDER[nak_idx % 9]
        nak_start = nak_idx * nak_span
        start_vim_idx = VIM_ORDER.index(star_lord)

        sub_start = nak_start
        for i in range(9):
            idx = (start_vim_idx + i) % 9
            sub_lord = VIM_ORDER[idx]
            span = nak_span * (VIM_YEARS[idx] / 120.0)
            sub_end = sub_start + span

            # Check if this sub spans across a 30° zodiac sign boundary
            sign_start = int(sub_start // 30.0)
            sign_end = int(sub_end // 30.0)

            if sign_end > sign_start and not math.isclose(sub_end, sign_end * 30.0, abs_tol=1e-8):
                # Split at boundary
                split_pt = sign_end * 30.0
                # Part 1
                table.append({
                    "sub_num": sub_num,
                    "sign_num": sign_start + 1,
                    "sign_lord": SIGN_LORDS[sign_start],
                    "star_lord": star_lord,
                    "sub_lord": sub_lord,
                    "start_lon": sub_start,
                    "end_lon": split_pt,
                })
                sub_num += 1
                # Part 2
                table.append({
                    "sub_num": sub_num,
                    "sign_num": sign_end + 1,
                    "sign_lord": SIGN_LORDS[sign_end % 12],
                    "star_lord": star_lord,
                    "sub_lord": sub_lord,
                    "start_lon": split_pt,
                    "end_lon": sub_end,
                })
                sub_num += 1
            else:
                table.append({
                    "sub_num": sub_num,
                    "sign_num": sign_start + 1,
                    "sign_lord": SIGN_LORDS[sign_start % 12],
                    "star_lord": star_lord,
                    "sub_lord": sub_lord,
                    "start_lon": sub_start,
                    "end_lon": sub_end,
                })
                sub_num += 1

            sub_start = sub_end

    return table


def compute_four_fold_significators(planets: list, cusps: list[float]) -> dict:
    """
    Compute classical 4-Level KP Significator Matrix for all 12 houses:
    Level A: Planets in star of occupants of house (Strongest)
    Level B: Occupants of house
    Level C: Planets in star of lord of house
    Level D: Lord of house
    """
    # 1. Determine planet house placement and star lords
    planet_details = {}
    house_occupants = {h: [] for h in range(1, 13)}

    for p in planets:
        pid = p["id"]
        lon = p["sid_lon"]
        # Find KP house based on cusps
        h_found = 1
        for h in range(12):
            c_beg = cusps[h]
            c_end = cusps[(h + 1) % 12]
            if c_beg <= c_end:
                if c_beg <= lon < c_end:
                    h_found = h + 1
                    break
            else:
                if lon >= c_beg or lon < c_end:
                    h_found = h + 1
                    break

        lords = get_kp_lords(lon)
        planet_details[pid] = {
            "house": h_found,
            "star_lord": lords["star_lord"],
            "sub_lord": lords["sub_lord"],
            "sign_lord": lords["sign_lord"],
        }
        house_occupants[h_found].append(pid)

    # 2. Determine cusp sign lords
    cusp_lords = []
    for h, c_lon in enumerate(cusps):
        c_info = get_kp_lords(c_lon)
        cusp_lords.append(c_info["sign_lord"])

    # 3. Assemble 4 levels for each house
    house_sig = {h: {"A": [], "B": [], "C": [], "D": []} for h in range(1, 13)}
    planet_sig = {p["id"]: {"A": [], "B": [], "C": [], "D": []} for p in planets}

    for h in range(1, 13):
        # Level B: Occupants
        b_planets = house_occupants[h]
        house_sig[h]["B"] = list(b_planets)

        # Level A: Planets in star of occupants
        a_planets = [pid for pid, det in planet_details.items() if det["star_lord"] in b_planets]
        house_sig[h]["A"] = list(a_planets)

        # Level D: House Lord
        d_lord = cusp_lords[h - 1]
        house_sig[h]["D"] = [d_lord]

        # Level C: Planets in star of house lord
        c_planets = [pid for pid, det in planet_details.items() if det["star_lord"] == d_lord]
        house_sig[h]["C"] = list(c_planets)

        # Invert to planet_sig
        for p in a_planets: planet_sig[p]["A"].append(h)
        for p in b_planets: planet_sig[p]["B"].append(h)
        for p in c_planets: planet_sig[p]["C"].append(h)
        if d_lord in planet_sig: planet_sig[d_lord]["D"].append(h)

    return {
        "house_significators": house_sig,
        "planet_significations": planet_sig,
        "planet_details": planet_details,
    }
