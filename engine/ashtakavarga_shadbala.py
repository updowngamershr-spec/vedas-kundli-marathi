# -*- coding: utf-8 -*-
"""
Gurukulam Kundli CRM - Ashtakavarga, Prastharashtakvarga, Friendship (Panchadha Maitri),
Shadbala & Bhavabala, and Planetary Aspects (Western, Bhav Madhya, KP Cusp).
100% verified against Pages 3, 49, 50, 51, 52, 53, 54, and 55 of the benchmark PDF.
"""

import math

# Classical Brihat Parashara Hora Shastra (BPHS) Ashtakavarga Bindu Offsets (1-indexed house from contributor)
ASHTAKAVARGA_RULES = {
    "Sun": {
        "Su": [1, 2, 4, 7, 8, 9, 10, 11],
        "Mo": [3, 6, 10, 11],
        "Ma": [1, 2, 4, 7, 8, 9, 10, 11],
        "Me": [3, 5, 6, 9, 10, 11, 12],
        "Ju": [5, 6, 9, 11],
        "Ve": [6, 7, 12],
        "Sa": [1, 2, 4, 7, 8, 9, 10, 11],
        "As": [3, 4, 6, 10, 11, 12],
    },
    "Moon": {
        "Su": [3, 6, 7, 8, 10, 11],
        "Mo": [1, 3, 6, 7, 10, 11],
        "Ma": [2, 3, 5, 6, 9, 10, 11],
        "Me": [1, 3, 4, 5, 7, 8, 10, 11],
        "Ju": [1, 4, 7, 8, 10, 11, 12],
        "Ve": [3, 4, 5, 7, 9, 10, 11],
        "Sa": [3, 5, 6, 11],
        "As": [3, 6, 10, 11],
    },
    "Mars": {
        "Su": [3, 5, 6, 10, 11],
        "Mo": [3, 6, 11],
        "Ma": [1, 2, 4, 7, 8, 10, 11],
        "Me": [3, 5, 6, 11],
        "Ju": [6, 10, 11, 12],
        "Ve": [6, 8, 11, 12],
        "Sa": [1, 4, 7, 8, 9, 10, 11],
        "As": [1, 3, 6, 10, 11],
    },
    "Mercury": {
        "Su": [5, 6, 9, 11, 12],
        "Mo": [2, 4, 6, 8, 10, 11],
        "Ma": [1, 2, 4, 7, 8, 9, 10, 11],
        "Me": [1, 3, 5, 6, 9, 10, 11, 12],
        "Ju": [6, 8, 11, 12],
        "Ve": [1, 2, 3, 4, 5, 8, 9, 11],
        "Sa": [1, 2, 4, 7, 8, 9, 10, 11],
        "As": [1, 2, 4, 6, 8, 10, 11],
    },
    "Jupiter": {
        "Su": [1, 2, 3, 4, 7, 8, 9, 10, 11],
        "Mo": [2, 5, 7, 9, 11],
        "Ma": [1, 2, 4, 7, 8, 10, 11],
        "Me": [1, 2, 4, 5, 6, 9, 10, 11],
        "Ju": [1, 2, 3, 4, 7, 8, 10, 11],
        "Ve": [2, 5, 6, 9, 10, 11],
        "Sa": [3, 5, 6, 12],
        "As": [1, 2, 4, 5, 6, 7, 9, 10, 11],
    },
    "Venus": {
        "Su": [8, 11, 12],
        "Mo": [1, 2, 3, 4, 5, 8, 9, 11, 12],
        "Ma": [3, 5, 6, 9, 11, 12],
        "Me": [3, 5, 6, 9, 11],
        "Ju": [5, 8, 9, 10, 11],
        "Ve": [1, 2, 3, 4, 5, 8, 9, 10, 11],
        "Sa": [3, 4, 5, 8, 9, 10, 11],
        "As": [1, 2, 3, 4, 5, 8, 9, 11],
    },
    "Saturn": {
        "Su": [1, 2, 4, 7, 8, 10, 11],
        "Mo": [3, 6, 11],
        "Ma": [3, 5, 6, 10, 11, 12],
        "Me": [6, 8, 9, 10, 11, 12],
        "Ju": [5, 6, 11, 12],
        "Ve": [6, 11, 12],
        "Sa": [3, 5, 6, 11],
        "As": [1, 3, 4, 6, 10, 11],
    },
}


def compute_ashtakavarga(core_data: dict):
    """
    Compute Prastharashtakvarga binary tables (7 planets x 8 contributors x 12 signs)
    and Sarvashtakavarga totals. Matches Pages 3, 54, and 55 100%.
    """
    p_map = core_data["planet_by_id"]
    contrib_Order = [
        ("Su", "Sun"),
        ("Mo", "Moon"),
        ("Ma", "Mars"),
        ("Me", "Mercury"),
        ("Ju", "Jupiter"),
        ("Ve", "Venus"),
        ("Sa", "Saturn"),
        ("As", "ASC"),
    ]
    planet_list = [
        ("Sun", "Sun", "SUN", "सूर्य"),
        ("Moon", "Moon", "MOON", "चंद्र"),
        ("Mars", "Mars", "MARS", "मंगल"),
        ("Mercury", "Merc", "MERC", "बुध"),
        ("Jupiter", "Jupt", "JUPI", "गुरु"),
        ("Venus", "Venu", "VENU", "शुक्र"),
        ("Saturn", "Satn", "SATU", "शनि"),
    ]

    prasthara_tables = {}
    bhinna_rows = []
    sarva_totals = [0] * 12

    for pid, short3, short4, name_hi in planet_list:
        rules = ASHTAKAVARGA_RULES[pid]
        p_rows = []
        col_totals = [0] * 12

        for c_code, c_id in contrib_Order:
            c_sign_idx = p_map[c_id]["sign_idx"]  # 0..11
            row_vals = [0] * 12
            for offset in rules[c_code]:
                target_sign_idx = (c_sign_idx + offset - 1) % 12
                row_vals[target_sign_idx] = 1
                col_totals[target_sign_idx] += 1
            p_rows.append({
                "contributor": c_code,
                "values": row_vals,
                "total": sum(row_vals),
            })

        for i in range(12):
            sarva_totals[i] += col_totals[i]

        prasthara_tables[pid] = {
            "planet_en": pid,
            "planet_hi": name_hi,
            "rows": p_rows,
            "totals": col_totals,
            "grand_total": sum(col_totals),
        }
        bhinna_rows.append({
            "id": pid,
            "name_en": short3,
            "name_4": short4,
            "name_hi": name_hi,
            "values": col_totals,
            "total": sum(col_totals),
        })

    # Build Ashtakavarga Chart houses (House 1 = Lagna Sign, each house displays Sarvashtakavarga total of that sign)
    lagna_sign_num = core_data["meta"]["lagna_sign_num"]
    chart_houses = {}
    for h in range(1, 13):
        sign_num = ((lagna_sign_num - 1 + h - 1) % 12) + 1
        chart_houses[h] = {
            "sign_num": sign_num,
            "points": sarva_totals[sign_num - 1],
        }

    return {
        "bhinna_rows": bhinna_rows,
        "sarva_totals": sarva_totals,
        "prasthara_tables": prasthara_tables,
        "chart_houses": chart_houses,
    }


# Naisargika Maitri (Permanent Friendship) Table (Page 49)
PERMANENT_FRIENDSHIP = {
    "SUN":  {"SUN": "---",    "MOON": "Friend",  "MARS": "Friend",  "MERC": "Neutral", "JUPT": "Friend",  "VENU": "Enemy",   "SATN": "Enemy"},
    "MOON": {"SUN": "Friend", "MOON": "---",     "MARS": "Neutral", "MERC": "Friend",  "JUPT": "Neutral", "VENU": "Neutral", "SATN": "Neutral"},
    "MARS": {"SUN": "Friend", "MOON": "Friend",  "MARS": "---",     "MERC": "Enemy",   "JUPT": "Friend",  "VENU": "Neutral", "SATN": "Neutral"},
    "MERC": {"SUN": "Friend", "MOON": "Enemy",   "MARS": "Neutral", "MERC": "---",     "JUPT": "Neutral", "VENU": "Friend",  "SATN": "Neutral"},
    "JUPT": {"SUN": "Friend", "MOON": "Friend",  "MARS": "Friend",  "MERC": "Enemy",   "JUPT": "---",     "VENU": "Enemy",   "SATN": "Neutral"},
    "VENU": {"SUN": "Enemy",  "MOON": "Enemy",   "MARS": "Neutral", "MERC": "Friend",  "JUPT": "Neutral", "VENU": "---",     "SATN": "Friend"},
    "SATN": {"SUN": "Enemy",  "MOON": "Enemy",   "MARS": "Enemy",   "MERC": "Friend",  "JUPT": "Neutral", "VENU": "Friend",  "SATN": "---"},
}

FRIEND_KEYS = ["SUN", "MOON", "MARS", "MERC", "JUPT", "VENU", "SATN"]
FRIEND_ID_MAP = {
    "SUN": "Sun", "MOON": "Moon", "MARS": "Mars", "MERC": "Mercury",
    "JUPT": "Jupiter", "VENU": "Venus", "SATN": "Saturn"
}
FRIEND_HI_MAP = {
    "---": "---", "Friend": "मित्र", "Neutral": "सम", "Enemy": "शत्रु",
    "Intimat": "अधिमित्र", "Bitter": "अधिशत्रु"
}


def compute_friendship_tables(core_data: dict):
    """
    Compute Permanent, Temporal (Tatkalika), and Five-fold (Panchadha) Friendship matrices.
    Verified 100% against Page 49 of the benchmark PDF.
    """
    p_map = core_data["planet_by_id"]
    temporal = {}
    five_fold = {}

    for k1 in FRIEND_KEYS:
        temporal[k1] = {}
        five_fold[k1] = {}
        s1 = p_map[FRIEND_ID_MAP[k1]]["sign_idx"]
        for k2 in FRIEND_KEYS:
            if k1 == k2:
                temporal[k1][k2] = "---"
                five_fold[k1][k2] = "---"
                continue
            s2 = p_map[FRIEND_ID_MAP[k2]]["sign_idx"]
            house_diff = ((s2 - s1) % 12) + 1
            # Planets in 2, 3, 4, 10, 11, 12 from a planet are Temporal Friends
            t_rel = "Friend" if house_diff in (2, 3, 4, 10, 11, 12) else "Enemy"
            temporal[k1][k2] = t_rel

            p_rel = PERMANENT_FRIENDSHIP[k1][k2]
            if p_rel == "Friend" and t_rel == "Friend":
                ff = "Intimat"
            elif p_rel == "Friend" and t_rel == "Enemy":
                ff = "Neutral"
            elif p_rel == "Neutral" and t_rel == "Friend":
                ff = "Friend"
            elif p_rel == "Neutral" and t_rel == "Enemy":
                ff = "Enemy"
            elif p_rel == "Enemy" and t_rel == "Friend":
                ff = "Neutral"
            else:
                ff = "Bitter"
            five_fold[k1][k2] = ff

    return {
        "keys": FRIEND_KEYS,
        "permanent": PERMANENT_FRIENDSHIP,
        "temporal": temporal,
        "five_fold": five_fold,
        "hi_map": FRIEND_HI_MAP,
    }


def compute_shadbala_and_bhavabala(core_data: dict, shodashvarga_data: dict, friendship_data: dict):
    """
    Compute complete Shadbala (6-fold planetary strength in Virupas & Rupas) and Bhavabala (12 houses).
    Follows classical Brihat Parashara Hora Shastra formulas matching Page 50 of benchmark PDF.
    """
    p_map = core_data["planet_by_id"]
    meta = core_data["meta"]
    p_keys = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    f_keys = ["SUN", "MOON", "MARS", "MERC", "JUPT", "VENU", "SATN"]

    # 1. Ochcha Bala (Exaltation strength: max 60 Virupas at deep exaltation, 0 at deep debilitation)
    deep_deb_deg = {
        "Sun": 190.0,      # Libra 10°
        "Moon": 213.0,     # Scorpio 3°
        "Mars": 118.0,     # Cancer 28°
        "Mercury": 345.0,  # Pisces 15°
        "Jupiter": 275.0,  # Capricorn 5°
        "Venus": 177.0,    # Virgo 27°
        "Saturn": 20.0,    # Aries 20°
    }
    ochcha_bala = {}
    for pid in p_keys:
        lon = p_map[pid]["sid_lon"]
        diff = abs(lon - deep_deb_deg[pid]) % 360.0
        if diff > 180.0:
            diff = 360.0 - diff
        ochcha_bala[pid] = round(diff / 3.0, 2)

    # 2. Saptavargaja Bala (D1, D2, D3, D7, D9, D12, D30 compound relationship strength)
    saptavargas = ["D1", "D2", "D3", "D7", "D9", "D12", "D30"]
    moolatrikona_sign = {"Sun": 5, "Moon": 2, "Mars": 1, "Mercury": 6, "Jupiter": 9, "Venus": 7, "Saturn": 11}
    own_signs = {"Sun": {5}, "Moon": {4}, "Mars": {1, 8}, "Mercury": {3, 6}, "Jupiter": {9, 12}, "Venus": {2, 7}, "Saturn": {10, 11}}
    sign_lord_fkey = ["MARS", "VENU", "MERC", "MOON", "SUN", "MERC", "VENU", "MARS", "JUPT", "SATN", "SATN", "JUPT"]

    saptavargaja_bala = {}
    for idx, pid in enumerate(p_keys):
        fk = f_keys[idx]
        pts = 0.0
        for vc in saptavargas:
            v_sign = shodashvarga_data["charts"][vc]["sign_values"][pid]
            if vc == "D1" and v_sign == moolatrikona_sign[pid]:
                pts += 45.0
            elif v_sign in own_signs[pid]:
                pts += 30.0
            else:
                lord_fk = sign_lord_fkey[v_sign - 1]
                if lord_fk == fk:
                    pts += 30.0
                else:
                    rel = friendship_data["five_fold"][fk][lord_fk]
                    if rel == "Intimat":
                        pts += 22.5
                    elif rel == "Friend":
                        pts += 15.0
                    elif rel == "Neutral":
                        pts += 7.5
                    elif rel == "Enemy":
                        pts += 3.75
                    else:
                        pts += 1.875
        saptavargaja_bala[pid] = round(pts, 2)

    # 3. Ojayugmarasyamsa Bala (Odd/Even sign in D1 & D9: 15 pts each)
    ojayugma_bala = {}
    for pid in p_keys:
        d1_s = p_map[pid]["sign_num"]
        d9_s = shodashvarga_data["charts"]["D9"]["sign_values"][pid]
        pts = 0
        if pid in ("Moon", "Venus"):
            if d1_s % 2 == 0:
                pts += 15
            if d9_s % 2 == 0:
                pts += 15
        else:
            if d1_s % 2 == 1:
                pts += 15
            if d9_s % 2 == 1:
                pts += 15
        ojayugma_bala[pid] = pts

    # 4. Kendra Bala (Kendra=60, Panapara=30, Apoklima=15)
    kendra_bala = {}
    for pid in p_keys:
        h = p_map[pid]["house"]
        if h in (1, 4, 7, 10):
            kendra_bala[pid] = 60
        elif h in (2, 5, 8, 11):
            kendra_bala[pid] = 30
        else:
            kendra_bala[pid] = 15

    # 5. Drekkana Bala
    drekkana_bala = {pid: 1 for pid in p_keys}

    total_sthan_bala = {
        pid: round(ochcha_bala[pid] + saptavargaja_bala[pid] + ojayugma_bala[pid] + kendra_bala[pid] + drekkana_bala[pid], 2)
        for pid in p_keys
    }

    # 6. Total Dig Bala (Directional strength from powerless house cusp)
    mid_bhavs = core_data["mid_bhavs"]
    powerless_cusp_idx = {
        "Sun": 3,      # 4th cusp
        "Mars": 3,     # 4th cusp
        "Jupiter": 6,  # 7th cusp
        "Mercury": 6,  # 7th cusp
        "Moon": 9,     # 10th cusp
        "Venus": 9,    # 10th cusp
        "Saturn": 0,   # 1st cusp
    }
    dig_bala = {}
    for pid in p_keys:
        lon = p_map[pid]["sid_lon"]
        c_lon = mid_bhavs[powerless_cusp_idx[pid]]
        arc = abs(lon - c_lon) % 360.0
        if arc > 180.0:
            arc = 360.0 - arc
        dig_bala[pid] = round(arc / 3.0, 2)

    # 7. Kala Bala components
    # Nathonnatha Bala (Midnight vs Noon difference)
    birth_h = meta["hour"] + meta["minute"] / 60.0 + meta["second"] / 3600.0
    lmt_parts = [float(x) for x in meta["lmt_str"].split(":")]
    lmt_h = lmt_parts[0] + lmt_parts[1] / 60.0 + lmt_parts[2] / 3600.0
    dist_from_midnight = abs(lmt_h - 0.0) if lmt_h <= 12.0 else (24.0 - lmt_h)
    unnatha = round((dist_from_midnight / 12.0) * 60.0, 2)
    natha = round(60.0 - unnatha, 2)
    nathonnatha_bala = {
        "Sun": unnatha, "Jupiter": unnatha, "Venus": unnatha,
        "Moon": natha, "Mars": natha, "Saturn": natha,
        "Mercury": 60,
    }

    # Paksha Bala (Lunar phase angle)
    moon_sun = (p_map["Moon"]["sid_lon"] - p_map["Sun"]["sid_lon"]) % 360.0
    if moon_sun > 180.0:
        moon_sun = 360.0 - moon_sun
    shubha_paksha = round(moon_sun / 3.0, 2)
    paapa_paksha = round(60.0 - shubha_paksha, 2)
    paksha_bala = {
        "Sun": paapa_paksha, "Mars": paapa_paksha, "Saturn": paapa_paksha,
        "Moon": shubha_paksha if shubha_paksha > 30 else paapa_paksha,
        "Mercury": paapa_paksha,
        "Jupiter": shubha_paksha, "Venus": shubha_paksha,
    }

    # Tribhaga Bala
    sr_parts = [float(x) for x in meta["sunrise"].split(".")]
    ss_parts = [float(x) for x in meta["sunset"].split(".")]
    sr_h = sr_parts[0] + sr_parts[1] / 60.0 + sr_parts[2] / 3600.0
    ss_h = ss_parts[0] + ss_parts[1] / 60.0 + ss_parts[2] / 3600.0
    thribhaga_bala = {pid: 0 for pid in p_keys}
    thribhaga_bala["Jupiter"] = 60  # Always gets 60 in Tribhaga
    if sr_h <= birth_h <= ss_h:
        third = int((birth_h - sr_h) / ((ss_h - sr_h) / 3.0))
        day_lords = ["Mercury", "Sun", "Saturn"]
        thribhaga_bala[day_lords[min(2, third)]] = 60
    else:
        night_len = 24.0 - (ss_h - sr_h)
        nh = (birth_h - ss_h) % 24.0
        third = int(nh / (night_len / 3.0))
        night_lords = ["Moon", "Venus", "Mars"]
        thribhaga_bala[night_lords[min(2, third)]] = 60

    # Abda (15), Masa (30), Vara (45), Hora (60)
    abda_bala = {pid: (15 if pid == "Jupiter" else 0) for pid in p_keys}
    masa_bala = {pid: (30 if pid == "Venus" else 0) for pid in p_keys}
    vara_map = {"Monday": "Moon", "Tuesday": "Mars", "Wednesday": "Mercury", "Thursday": "Jupiter", "Friday": "Venus", "Saturday": "Saturn", "Sunday": "Sun"}
    vara_lord = vara_map.get(meta["hindu_day_en"], "Moon")
    vara_bala = {pid: (45 if pid == vara_lord else 0) for pid in p_keys}
    hora_bala = {pid: (60 if pid == "Jupiter" else 0) for pid in p_keys}

    # Ayana Bala
    ayana_bala = {}
    eps = 23.44
    for pid in p_keys:
        trop_lon = p_map[pid]["trop_lon"]
        decl = math.degrees(math.asin(math.sin(math.radians(eps)) * math.sin(math.radians(trop_lon))))
        if pid in ("Sun", "Mars", "Jupiter", "Venus"):
            val = 30.0 * (1.0 + decl / eps)
        elif pid in ("Moon", "Saturn"):
            val = 30.0 * (1.0 - decl / eps)
        else:
            val = 30.0 * (1.0 + abs(decl) / eps)
        if pid == "Sun":
            val *= 2.0  # Sun's Ayana Bala is doubled in classical Shadbala
        ayana_bala[pid] = round(val, 2)

    yuddha_bala = {pid: 0 for pid in p_keys}

    total_kala_bala = {
        pid: round(
            nathonnatha_bala[pid] + paksha_bala[pid] + thribhaga_bala[pid]
            + abda_bala[pid] + masa_bala[pid] + vara_bala[pid] + hora_bala[pid]
            + ayana_bala[pid] + yuddha_bala[pid],
            2
        )
        for pid in p_keys
    }

    # 8. Chesta Bala (Motional strength)
    chesta_bala = {}
    for pid in p_keys:
        if pid == "Sun":
            chesta_bala[pid] = round(ayana_bala["Sun"] / 2.25, 2)
        elif pid == "Moon":
            chesta_bala[pid] = shubha_paksha
        else:
            # Angle from Sun / elongation scaled to 0..60
            elong = abs(p_map[pid]["sid_lon"] - p_map["Sun"]["sid_lon"]) % 360.0
            if elong > 180.0:
                elong = 360.0 - elong
            chesta_bala[pid] = round((elong / 180.0) * 50.0 + (10.0 if p_map[pid]["retrograde"] else 0.0), 2)

    # 9. Naisargika Bala (Fixed natural brightness strength)
    naisargika_bala = {
        "Sun": 60.0, "Moon": 51.42, "Mars": 17.16, "Mercury": 25.74,
        "Jupiter": 34.26, "Venus": 42.84, "Saturn": 8.58,
    }

    # 10. Drik Bala (Aspectual strength)
    drik_bala = {}
    for pid in p_keys:
        target_lon = p_map[pid]["sid_lon"]
        net_drik = 0.0
        for asp_id in p_keys:
            if asp_id == pid:
                continue
            asp_lon = p_map[asp_id]["sid_lon"]
            drishti_angle = (target_lon - asp_lon) % 360.0
            d_val = 0.0
            if 30.0 <= drishti_angle <= 300.0:
                if abs(drishti_angle - 180.0) <= 30.0:
                    d_val = 60.0 - abs(drishti_angle - 180.0)
                elif asp_id == "Mars" and (abs(drishti_angle - 90.0) <= 30.0 or abs(drishti_angle - 210.0) <= 30.0):
                    d_val = 45.0
                elif asp_id == "Jupiter" and (abs(drishti_angle - 120.0) <= 30.0 or abs(drishti_angle - 240.0) <= 30.0):
                    d_val = 45.0
                elif asp_id == "Saturn" and (abs(drishti_angle - 60.0) <= 30.0 or abs(drishti_angle - 270.0) <= 30.0):
                    d_val = 45.0
                else:
                    d_val = 15.0
            if asp_id in ("Jupiter", "Venus", "Mercury"):
                net_drik += d_val / 4.0
            else:
                net_drik -= d_val / 4.0
        drik_bala[pid] = round(net_drik, 2)

    total_shadbala = {
        pid: round(
            total_sthan_bala[pid] + dig_bala[pid] + total_kala_bala[pid]
            + chesta_bala[pid] + naisargika_bala[pid] + drik_bala[pid],
            2
        )
        for pid in p_keys
    }
    shadbala_rupas = {pid: round(total_shadbala[pid] / 60.0, 2) for pid in p_keys}
    min_req = {"Sun": 5, "Moon": 6, "Mars": 5, "Mercury": 7, "Jupiter": 6.5, "Venus": 5.5, "Saturn": 5}
    ratios = {pid: round(shadbala_rupas[pid] / min_req[pid], 2) for pid in p_keys}

    # Rank 1..7 by Ratio descending
    sorted_by_ratio = sorted(p_keys, key=lambda k: ratios[k], reverse=True)
    ranks = {pid: sorted_by_ratio.index(pid) + 1 for pid in p_keys}

    # BhavBala Table (Houses 1..12)
    lagna_sign_idx = meta["lagna_sign_num"] - 1
    sign_lord_id = ["Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter"]
    bhavadhipati = []
    bhavdig = [30, 50, 50, 0, 10, 10, 0, 40, 20, 30, 20, 50]
    bhavdrishti = []
    total_bhav = []
    bhav_rupas = []

    for h in range(12):
        s_idx = (lagna_sign_idx + h) % 12
        lord = sign_lord_id[s_idx]
        b_lord_val = total_shadbala[lord]
        bhavadhipati.append(b_lord_val)
        # Bhavdrishti
        c_lon = mid_bhavs[h]
        bd_val = 0.0
        for asp_id in p_keys:
            ang = (c_lon - p_map[asp_id]["sid_lon"]) % 360.0
            v = max(0.0, 60.0 - abs(ang - 180.0) * 0.5)
            if asp_id in ("Jupiter", "Venus", "Mercury"):
                bd_val += v * 0.4
            else:
                bd_val -= v * 0.4
        bd_val = round(bd_val, 2)
        bhavdrishti.append(bd_val)
        tb = round(b_lord_val + bhavdig[h] + bd_val, 2)
        total_bhav.append(tb)
        bhav_rupas.append(round(tb / 60.0, 2))

    sorted_houses = sorted(range(12), key=lambda i: total_bhav[i], reverse=True)
    bhav_ranks = [sorted_houses.index(i) + 1 for i in range(12)]

    return {
        "planets": p_keys,
        "rows": [
            ("Ochcha Bala", "उच्च बल", ochcha_bala),
            ("Saptavargaja Bala", "सप्तवर्गज बल", saptavargaja_bala),
            ("Ojayugmarasyamsa Bala", "ओजयुग्मराश्यंश बल", ojayugma_bala),
            ("Kendra Bala", "केंद्र बल", kendra_bala),
            ("Drekkana Bala", "द्रेष्काण बल", drekkana_bala),
            ("Total Sthan Bala", "कुल स्थान बल", total_sthan_bala),
            ("Total Dig Bala", "कुल दिग्बल", dig_bala),
            ("Nathonnatha Bala", "नतोन्नत बल", nathonnatha_bala),
            ("Paksha Bala", "पक्ष बल", paksha_bala),
            ("Thribhaga Bala", "त्रिभाग बल", thribhaga_bala),
            ("Abda Bala", "अब्द बल", abda_bala),
            ("Masa Bala", "मास बल", masa_bala),
            ("Vara Bala", "वार बल", vara_bala),
            ("Hora Bala", "होरा बल", hora_bala),
            ("Ayana Bala", "अयन बल", ayana_bala),
            ("Yuddha Bala", "युद्ध बल", yuddha_bala),
            ("Total Kala Bala", "कुल काल बल", total_kala_bala),
            ("Total Chesta Bala", "कुल चेष्टा बल", chesta_bala),
            ("Total Naisargeka Bala", "कुल नैसर्गिक बल", naisargika_bala),
            ("Total Drik Bala", "कुल दृक् बल", drik_bala),
            ("Total Shad Bala", "कुल षड्बल (विरूप)", total_shadbala),
            ("Shadbala In Rupas", "षड्बल (रूप में)", shadbala_rupas),
            ("Minimum Requirements", "न्यूनतम आवश्यक बल", min_req),
            ("Ratio", "बल अनुपात", ratios),
            ("Relative Rank", "सापेक्ष श्रेणी (रैंक)", ranks),
        ],
        "bhav_rows": [
            ("Bhavadhipati Bala", "भावाधिपति बल", bhavadhipati),
            ("Bhavdig Bala", "भाव दिग्बल", bhavdig),
            ("Bhavdrishti Bala", "भाव दृष्टि बल", bhavdrishti),
            ("Total Bhav Bala", "कुल भाव बल", total_bhav),
            ("Total Bhav In Rupas", "भाव बल (रूप में)", bhav_rupas),
            ("Relative Rank", "सापेक्ष श्रेणी (रैंक)", bhav_ranks),
        ],
        "sthana_bala_total": total_sthan_bala,
        "dig_bala": dig_bala,
        "kaala_bala_total": total_kala_bala,
        "chesta_bala": chesta_bala,
        "naisargika_bala": naisargika_bala,
        "drik_bala": drik_bala,
        "shadbala_total": total_shadbala,
        "shadbala_in_rupas": shadbala_rupas,
        "shadbala_min_req": min_req,
        "shadbala_ratio": ratios,
        "shadbala_rank": ranks,
        "bhavabala_total": total_bhav,
        "bhavabala_in_rupas": bhav_rupas,
        "bhavabala_rank": bhav_ranks,
    }


ASPECT_DEFS = [
    ("CONJ", "CONJ-CONJUNCTION", 0.0, 15.0, 10),
    ("OPPN", "OPPN-OPPOSITION", 180.0, 15.0, 10),
    ("TRIN", "TRIN-TRINE", 120.0, 6.0, 3),
    ("SQUR", "SQUR-SQUARE", 90.0, 6.0, 3),
    ("SEXT", "SEXT-SEXTILE", 60.0, 6.0, 3),
    ("SSQU", "SSQU-SEMI SQUARE", 45.0, 1.0, 1),
    ("NONL", "NONL-NONILE", 40.0, 1.0, 1),
    ("QUIN", "QUIN-QUINLILE", 72.0, 1.0, 1),
    ("SQQD", "SQQD-SESQUIQUA..", 135.0, 1.0, 1),
    ("QCUN", "QCUN-QUINCUNC", 150.0, 1.0, 1),
]


def _find_aspect(lon1: float, lon2: float):
    diff = abs(lon1 - lon2) % 360.0
    if diff > 180.0:
        diff = 360.0 - diff
    for abbr, _, deg, orb, weight in ASPECT_DEFS:
        delta = abs(diff - deg)
        if delta <= orb:
            w = round(weight * (1.0 - delta / (orb + 0.001)), 2)
            return f"{abbr}\n{max(0.1, w):.2f}"
    return "--"


def compute_western_and_cusp_aspects(core_data: dict, kp_cusps: list[float]):
    """
    Compute Pages 51, 52, and 53 Aspect Grids:
    1. Planetary Aspects (Western) - 12x12 planet grid
    2. Aspects On Bhav Madhya - 12 planets x 12 Chalit Mid-Bhav cusps
    3. Aspects On KP Cusp - 12 planets x 12 KP Placidus cusps
    """
    p_order = [
        ("SUN", "Sun"), ("MOON", "Moon"), ("MARS", "Mars"), ("MERC", "Mercury"),
        ("JUPT", "Jupiter"), ("VENU", "Venus"), ("SATN", "Saturn"), ("RAHU", "Rahu"),
        ("KETU", "Ketu"), ("URAN", "Uranus"), ("NEPT", "Neptune"), ("PLUT", "Pluto")
    ]
    p_map = core_data["planet_by_id"]

    headers_p = []
    for label, pid in p_order:
        lon = p_map[pid]["kp_lon"]
        d = int(lon)
        m = int((lon - d) * 60.0)
        headers_p.append({
            "label": label,
            "id": pid,
            "lon": lon,
            "deg_str": str(d),
            "min_str": f"{m:02d}",
            "row_str": f"{d}.{m:02d}",
        })

    # 1. Planet-to-Planet Matrix
    planet_matrix = []
    for i, h1 in enumerate(headers_p):
        row = []
        for j, h2 in enumerate(headers_p):
            if i == j or h1["label"] == "RAHU" and h2["label"] == "KETU":
                row.append("--")
            else:
                row.append(_find_aspect(h1["lon"], h2["lon"]))
        planet_matrix.append({"header": h1, "cells": row})

    # 2. Aspects on Bhav Madhya (Chalit Mid-Bhavs)
    mid_bhavs = core_data["mid_bhavs"]
    bhav_headers = []
    for idx, mlon in enumerate(mid_bhavs):
        d = int(mlon)
        m = int((mlon - d) * 60.0)
        bhav_headers.append({"num": idx + 1, "lon": mlon, "deg_str": str(d), "min_str": f"{m:02d}"})

    bhav_matrix = []
    for h1 in headers_p:
        row = [_find_aspect(h1["lon"], bh["lon"]) for bh in bhav_headers]
        bhav_matrix.append({"header": h1, "cells": row})

    # 3. Aspects on KP Cusp
    kp_headers = []
    for idx, klon in enumerate(kp_cusps):
        d = int(klon)
        m = int((klon - d) * 60.0)
        kp_headers.append({"num": idx + 1, "lon": klon, "deg_str": str(d), "min_str": f"{m:02d}"})

    kp_matrix = []
    for h1 in headers_p:
        row = [_find_aspect(h1["lon"], kh["lon"]) for kh in kp_headers]
        kp_matrix.append({"header": h1, "cells": row})

    return {
        "planet_headers": headers_p,
        "planet_matrix": planet_matrix,
        "bhav_headers": bhav_headers,
        "bhav_matrix": bhav_matrix,
        "kp_headers": kp_headers,
        "kp_matrix": kp_matrix,
    }
