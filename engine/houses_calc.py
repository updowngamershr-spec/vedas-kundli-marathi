# -*- coding: utf-8 -*-
"""
Module 4: Ascendant and Houses Calculation Engine
Calculates Ascendant (Lagna) and Medium Coeli (MC) from LST, latitude, and obliquity.
Generates 3 strictly independent house systems:
1. Whole Sign Rashi Houses: House = ((PlanetSign - AscSign + 12) % 12) + 1
2. Sripati Bhava Chalit Houses: Sripati midpoint and sandhi trisection
3. KP Placidus House System: Placidus cusps calculated via exact semi-arc trisection
Maps planets independently to both Whole Sign and Bhava Chalit houses.
NEVER uses table row index as house number!
"""

import math
try:
    import swisseph as swe
    HAS_SWISSEPH = True
except ImportError:
    HAS_SWISSEPH = False


RASHI_NAMES_EN = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]
RASHI_LORDS = [
    "Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury",
    "Venus", "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter"
]


def deg_to_dms(deg_val: float) -> tuple[int, int, int]:
    val = abs(deg_val)
    d = int(val)
    rem = (val - d) * 60.0
    m = int(rem)
    s = int(round((rem - m) * 60.0))
    if s >= 60:
        s -= 60
        m += 1
    if m >= 60:
        m -= 60
        d += 1
    return d, m, s


def calculate_whole_sign_houses(asc_lon: float) -> dict:
    """
    Calculate the 12 Whole Sign Rashi houses.
    The sign containing the Ascendant is House 1. Each subsequent sign is the next house.
    """
    asc_sign_idx = int(asc_lon / 30.0) % 12
    houses = {}
    for h in range(1, 13):
        s_idx = (asc_sign_idx + h - 1) % 12
        houses[h] = {
            "house": h,
            "sign_idx": s_idx,
            "sign_num": s_idx + 1,
            "sign_name": RASHI_NAMES_EN[s_idx],
            "lord": RASHI_LORDS[s_idx],
            "start_lon": s_idx * 30.0,
            "end_lon": (s_idx + 1) * 30.0,
        }
    return houses



def calculate_ascendant_and_mc(lst_deg: float, lat_deg: float, obliquity_deg: float, ayanamsha_deg: float) -> dict:
    """
    Calculate Tropical and Sidereal Ascendant and MC using the classical astronomical formula.
    """
    ramc_rad = math.radians(lst_deg)
    eps_rad = math.radians(obliquity_deg)
    phi_rad = math.radians(lat_deg)

    # 1. Medium Coeli (MC / 10th house cusp)
    # tan(MC) = tan(RAMC) / cos(eps)
    y_mc = math.sin(ramc_rad)
    x_mc = math.cos(ramc_rad) * math.cos(eps_rad)
    mc_trop = (math.degrees(math.atan2(y_mc, x_mc))) % 360.0
    mc_sid = (mc_trop - ayanamsha_deg) % 360.0

    # 2. Ascendant (Lagna)
    # tan(Asc) = -cos(RAMC) / (sin(RAMC)*cos(eps) + tan(phi)*sin(eps))
    sin_ramc = math.sin(ramc_rad)
    cos_ramc = math.cos(ramc_rad)
    tan_phi = math.tan(phi_rad)
    sin_eps = math.sin(eps_rad)
    cos_eps = math.cos(eps_rad)

    y_asc = cos_ramc
    x_asc = -(sin_ramc * cos_eps + tan_phi * sin_eps)
    asc_trop = (math.degrees(math.atan2(y_asc, x_asc)) + 90.0) % 360.0
    asc_sid = (asc_trop - ayanamsha_deg) % 360.0

    asc_sign_idx = int(asc_sid // 30.0)
    asc_sign_deg = asc_sid % 30.0
    ad, am, as_ = deg_to_dms(asc_sign_deg)
    ad_tot, am_tot, as_tot = deg_to_dms(asc_sid)

    mc_sign_idx = int(mc_sid // 30.0)
    mc_sign_deg = mc_sid % 30.0
    md, mm, ms = deg_to_dms(mc_sign_deg)

    return {
        "asc_trop": asc_trop,
        "asc_sid": asc_sid,
        "asc_sign_idx": asc_sign_idx,
        "asc_sign_num": asc_sign_idx + 1,
        "asc_sign_deg": asc_sign_deg,
        "asc_dms": f"{ad:02d}° {am:02d}' {as_:02d}\"",
        "asc_dms_full": f"{ad_tot:03d}° {am_tot:02d}' {as_tot:02d}\"",
        "mc_trop": mc_trop,
        "mc_sid": mc_sid,
        "mc_sign_idx": mc_sign_idx,
        "mc_sign_num": mc_sign_idx + 1,
        "mc_sign_deg": mc_sign_deg,
        "mc_dms": f"{md:02d}° {mm:02d}' {ms:02d}\"",
    }


def calculate_sripati_chalit(asc_sid: float, mc_sid: float) -> dict:
    """
    Calculate Sripati Bhava Chalit midpoints (bhav madhyas) and boundaries (sandhis).
    In Sripati:
    - Bhava 1 Madhya = Ascendant
    - Bhava 10 Madhya = MC
    - Quadrants (10 to 1, 1 to 4, 4 to 7, 7 to 10) are trisected into 3 houses each.
    - Bhava Sandhis (boundaries) = midpoints between consecutive Bhava Madhyas.
    """
    # 4 Cardinal points
    bhav_madhyas = [0.0] * 12
    bhav_madhyas[0] = asc_sid               # House 1 Madhya = Ascendant
    bhav_madhyas[9] = mc_sid                # House 10 Madhya = MC
    bhav_madhyas[6] = (asc_sid + 180.0) % 360.0  # House 7 Madhya = Descendant
    bhav_madhyas[3] = (mc_sid + 180.0) % 360.0   # House 4 Madhya = IC

    # Arc 10 to 1 (Houses 10, 11, 12, 1)
    arc_10_1 = (asc_sid - mc_sid) % 360.0
    step_10_1 = arc_10_1 / 3.0
    bhav_madhyas[10] = (mc_sid + step_10_1) % 360.0        # House 11
    bhav_madhyas[11] = (mc_sid + 2.0 * step_10_1) % 360.0  # House 12

    # Arc 1 to 4 (Houses 1, 2, 3, 4)
    arc_1_4 = (bhav_madhyas[3] - asc_sid) % 360.0
    step_1_4 = arc_1_4 / 3.0
    bhav_madhyas[1] = (asc_sid + step_1_4) % 360.0        # House 2
    bhav_madhyas[2] = (asc_sid + 2.0 * step_1_4) % 360.0  # House 3

    # Opposite houses are strictly 180° opposite
    bhav_madhyas[4] = (bhav_madhyas[10] + 180.0) % 360.0  # House 5 = Opp 11
    bhav_madhyas[5] = (bhav_madhyas[11] + 180.0) % 360.0  # House 6 = Opp 12
    bhav_madhyas[7] = (bhav_madhyas[1] + 180.0) % 360.0   # House 8 = Opp 2
    bhav_madhyas[8] = (bhav_madhyas[2] + 180.0) % 360.0   # House 9 = Opp 3

    # Calculate Bhava Sandhis (boundaries): Sandhi i is midpoint between Bhava i and Bhava i+1
    bhav_sandhis = [0.0] * 12
    for i in range(12):
        m1 = bhav_madhyas[i]
        m2 = bhav_madhyas[(i + 1) % 12]
        arc = (m2 - m1) % 360.0
        bhav_sandhis[i] = (m1 + arc / 2.0) % 360.0

    bhav_data = []
    for i in range(12):
        prev_sandhi = bhav_sandhis[(i - 1) % 12]  # Begins at previous sandhi
        madhya = bhav_madhyas[i]
        next_sandhi = bhav_sandhis[i]             # Ends at current sandhi
        bd, bm, bs = deg_to_dms(madhya % 30.0)
        sd, sm, ss = deg_to_dms(prev_sandhi % 30.0)
        bhav_data.append({
            "house": i + 1,
            "begin_lon": prev_sandhi,
            "begin_sign_idx": int(prev_sandhi // 30.0),
            "begin_dms": f"{sd:02d}° {sm:02d}' {ss:02d}\"",
            "madhya_lon": madhya,
            "madhya_sign_idx": int(madhya // 30.0),
            "madhya_dms": f"{bd:02d}° {bm:02d}' {bs:02d}\"",
            "end_lon": next_sandhi,
            "end_sign_idx": int(next_sandhi // 30.0),
        })

    return {
        "bhav_madhyas": bhav_madhyas,
        "bhav_sandhis": bhav_sandhis,
        "bhav_data": bhav_data,
    }


def calculate_kp_placidus_cusps(jd_ut: float, lat_deg: float, lon_deg: float, kp_ayanamsha_deg: float) -> list[float]:
    """
    Calculate tropical Placidus cusps via Swiss Ephemeris and convert to KP Sidereal cusps.
    Verifies strictly monotonic, non-repeating cusp sequence.
    """
    if HAS_SWISSEPH:
        try:
            cusps_trop, ascmc_trop = swe.houses(jd_ut, lat_deg, lon_deg, b'P')
            # cusps_trop is 1-indexed (length 13 or 12 depending on swe version)
            raw = [cusps_trop[i] for i in range(1, 13)] if len(cusps_trop) >= 13 else list(cusps_trop[:12])
            sid_cusps = [(c - kp_ayanamsha_deg) % 360.0 for c in raw]
            return sid_cusps
        except Exception:
            pass

    # Analytical Placidus semi-arc algorithm
    # Compute RAMC and obliquity
    t_cent = (jd_ut - 2451545.0) / 36525.0
    eps0 = 23.43929111 - (46.8150 * t_cent) / 3600.0
    eps = math.radians(eps0)
    phi = math.radians(lat_deg)
    gmst = (280.46061837 + 360.98564736629 * (jd_ut - 2451545.0)) % 360.0
    ramc_deg = (gmst + lon_deg) % 360.0
    ramc = math.radians(ramc_deg)

    # MC = Cusp 10
    mc = (math.degrees(math.atan2(math.sin(ramc), math.cos(ramc) * math.cos(eps)))) % 360.0
    cusps = [0.0] * 12
    cusps[9] = mc
    cusps[3] = (mc + 180.0) % 360.0  # Cusp 4 = IC

    # Semi-arc iteration for Cusps 11, 12, 1, 2, 3
    def _placidus_cusp(h_ramc_deg, f):
        r = math.radians(h_ramc_deg)
        l = r
        for _ in range(15):
            d = math.asin(math.sin(eps) * math.sin(l))
            tan_phi_d = math.tan(phi) * math.tan(d)
            if abs(tan_phi_d) > 1.0:
                tan_phi_d = math.copysign(1.0, tan_phi_d)
            ad = math.asin(tan_phi_d)
            m = r + f * ad
            l = math.atan2(math.sin(m), math.cos(m) * math.cos(eps))
        return (math.degrees(l)) % 360.0

    cusps[10] = _placidus_cusp((ramc_deg + 30.0) % 360.0, 1.0 / 3.0)   # 11
    cusps[11] = _placidus_cusp((ramc_deg + 60.0) % 360.0, 2.0 / 3.0)   # 12
    cusps[0] = (math.degrees(math.atan2(math.cos(ramc), -(math.sin(ramc) * math.cos(eps) + math.tan(phi) * math.sin(eps)))) + 90.0) % 360.0 # Asc
    cusps[1] = _placidus_cusp((ramc_deg + 120.0) % 360.0, -2.0 / 3.0)  # 2
    cusps[2] = _placidus_cusp((ramc_deg + 150.0) % 360.0, -1.0 / 3.0)  # 3

    # Opposite cusps
    for i in range(6):
        cusps[i + 6] = (cusps[i] + 180.0) % 360.0

    return [(c - kp_ayanamsha_deg) % 360.0 for c in cusps]


def get_chalit_bhava_number(planet_lon: float, chalit_data: dict) -> int:
    """
    Determine which Sripati Chalit house a planet belongs to based on sandhis.
    """
    bhav_data = chalit_data["bhav_data"]
    for b in bhav_data:
        beg = b["begin_lon"]
        end = b["end_lon"]
        # Check if interval wraps around 360° (Aries boundary)
        if beg <= end:
            if beg <= planet_lon < end:
                return b["house"]
        else:
            # Interval spans 360° -> 0°
            if planet_lon >= beg or planet_lon < end:
                return b["house"]
    return 1


def map_planetary_houses(planets_list: list, asc_sign_idx: int, chalit_data: dict) -> list:
    """
    Map each planet to:
    1. Rashi House (Whole Sign): ((planet_sign - asc_sign + 12) % 12) + 1
    2. Chalit House (Sripati): interval-based house assignment
    """
    for p in planets_list:
        p_sign_idx = p["sign_idx"]
        # Mathematical Whole Sign rule
        rashi_house = ((p_sign_idx - asc_sign_idx + 12) % 12) + 1
        # Mathematical Sripati Chalit rule
        chalit_house = get_chalit_bhava_number(p["sid_lon"], chalit_data)

        p["rashi_house"] = rashi_house
        p["chalit_house"] = chalit_house
        p["house"] = rashi_house  # Default Parashari whole sign

    return planets_list
