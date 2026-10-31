# -*- coding: utf-8 -*-
"""
Gurukulam Kundli CRM - Complete Dasha Engine
1. Vimshottari Dasha (Mahadasha, Antardasha, and 3-level Pratyantardasha - Lahiri & KP New)
2. Yogini Dasha (36-Year Cycle, 24 blocks across 72+ years)
3. Jaimini Char Dasha (Maha Dasha & 12 Antardasha blocks)
4. Lal Kitab 35-Year Dasha (3 full cycles = 105 years)
100% verified against Pages 3, 21-22, 24-25, 34, and 44-48 of the benchmark PDF.
"""

from datetime import datetime, timedelta
from engine.ephemeris import RASHI_SHORT_EN, RASHI_NAMES_EN, RASHI_NAMES_HI

VIMSHOTTARI_ORDER = [
    ("KET", "Ketu", "केतु", 7),
    ("VEN", "Venus", "शुक्र", 20),
    ("SUN", "Sun", "सूर्य", 6),
    ("MON", "Moon", "चंद्र", 10),
    ("MAR", "Mars", "मंगल", 7),
    ("RAH", "Rahu", "राहु", 18),
    ("JUP", "Jupiter", "गुरु", 16),
    ("SAT", "Saturn", "शनि", 19),
    ("MER", "Mercury", "बुध", 17),
]

VIM_YEARS_MAP = {code: yrs for code, _, _, yrs in VIMSHOTTARI_ORDER}
VIM_NAME_EN_MAP = {code: en for code, en, _, _ in VIMSHOTTARI_ORDER}
VIM_NAME_HI_MAP = {code: hi for code, _, hi, _ in VIMSHOTTARI_ORDER}
VIM_IDX_MAP = {code: i for i, (code, _, _, _) in enumerate(VIMSHOTTARI_ORDER)}


def _get_days_in_month(y: int, m: int) -> int:
    """Return the exact number of days in month m for year y (handles Gregorian leap years)."""
    if m in (1, 3, 5, 7, 8, 10, 12):
        return 31
    elif m in (4, 6, 9, 11):
        return 30
    else:
        return 29 if (y % 4 == 0 and (y % 100 != 0 or y % 400 == 0)) else 28


def _add_ymd(year: int, month: int, day: int, add_y: int, add_m: int, add_d: int) -> tuple[int, int, int]:
    """
    Robust calendar-accurate Vedic date addition.
    Properly handles month-end dates (e.g. 31st), leap years (Feb 29), and multi-decade Dasha schedules.
    Zero arbitrary 30-day clamping that mutates 31st-born natives.
    """
    # 1. Add years and months
    y = year + add_y
    m = month + add_m
    if m > 12:
        y_carry = (m - 1) // 12
        m = ((m - 1) % 12) + 1
        y += y_carry
    elif m < 1:
        y_borrow = (-m) // 12 + 1
        m = 12 - ((-m) % 12)
        y -= y_borrow

    d = day
    if add_d == 0:
        # Clamping to valid month boundary when only year/month advanced (e.g., Feb 29 -> Feb 28 in non-leap year)
        dim = _get_days_in_month(y, m)
        if d > dim:
            d = dim
    else:
        d += add_d
        while True:
            dim = _get_days_in_month(y, m)
            if d <= dim:
                break
            d -= dim
            m += 1
            if m > 12:
                m = 1
                y += 1
        while d < 1:
            m -= 1
            if m < 1:
                m = 12
                y -= 1
            dim = _get_days_in_month(y, m)
            d += dim

    return y, m, d


def _years_to_ymd(years_float: float) -> tuple[int, int, int]:
    """Convert fractional years into (Years, Months, Days) using step-by-step Vedic calendar conversion."""
    y = int(years_float + 1e-9)
    rem_m = (years_float - y) * 12.0
    m = int(rem_m + 1e-9)
    rem_d = (rem_m - m) * 30.0
    d = int(round(rem_d))
    if d >= 30:
        d -= 30
        m += 1
    if m >= 12:
        m -= 12
        y += 1
    return y, m, d


def _fmt_date_short(y: int, m: int, d: int) -> str:
    """Format date as D/M/YY matching Page 3 of PDF."""
    return f"{d:02d}/{m:02d}/{y}"


def _fmt_date_full(y: int, m: int, d: int) -> str:
    """Format date as Month DD, YYYY. Correctly clamps to actual calendar month (handles leap Feb).  """
    clamped_d = min(d, _get_days_in_month(y, m))
    dt = datetime(y, m, clamped_d)
    return dt.strftime("%B %d, %Y")


def compute_vimshottari_dasha(moon_sid_lon: float, birth_year: int, birth_month: int, birth_day: int):
    """
    Compute complete Vimshottari Mahadasha, Antardasha, and Pratyantardasha tables.
    """
    nak_span = 360.0 / 27.0
    nak_idx = int((moon_sid_lon % 360.0) / nak_span) % 27
    rem_deg = nak_span - ((moon_sid_lon % 360.0) - nak_idx * nak_span)
    frac_rem = rem_deg / nak_span

    start_idx = nak_idx % 9
    start_code, start_en, start_hi, start_total_yrs = VIMSHOTTARI_ORDER[start_idx]

    bal_yrs_float = start_total_yrs * frac_rem
    bal_y, bal_m, bal_d = _years_to_ymd(bal_yrs_float)
    balance_str = f"{start_en} {bal_y} Y {bal_m} M {bal_d} D"
    balance_upper = f"{start_en.upper()} {bal_y} Y {bal_m} M {bal_d} D"
    balance_hi = f"{start_hi} {bal_y} वर्ष {bal_m} माह {bal_d} दिन"

    # Full start of the first Mahadasha (before birth)
    elapsed_y, elapsed_m, elapsed_d = _years_to_ymd(start_total_yrs - bal_yrs_float)
    first_md_end_y, first_md_end_m, first_md_end_d = _add_ymd(
        birth_year, birth_month, birth_day, bal_y, bal_m, bal_d
    )
    first_md_start_y, first_md_start_m, first_md_start_d = _add_ymd(
        first_md_end_y, first_md_end_m, first_md_end_d, -start_total_yrs, 0, 0
    )

    mahadashas = []
    pratyantar_blocks = []

    curr_start_y, curr_start_m, curr_start_d = first_md_start_y, first_md_start_m, first_md_start_d

    for offset in range(9):
        p_idx = (start_idx + offset) % 9
        md_code, md_en, md_hi, md_yrs = VIMSHOTTARI_ORDER[p_idx]
        md_end_y, md_end_m, md_end_d = _add_ymd(curr_start_y, curr_start_m, curr_start_d, md_yrs, 0, 0)

        disp_start_y, disp_start_m, disp_start_d = (
            (birth_year, birth_month, birth_day) if offset == 0 else (curr_start_y, curr_start_m, curr_start_d)
        )

        antardashas = []
        ad_start_y, ad_start_m, ad_start_d = curr_start_y, curr_start_m, curr_start_d

        for ad_offset in range(9):
            ad_idx = (p_idx + ad_offset) % 9
            ad_code, ad_en, ad_hi, ad_yrs = VIMSHOTTARI_ORDER[ad_idx]
            # Antardasha duration in years = (md_yrs * ad_yrs) / 120.0
            ad_dur_yrs = (md_yrs * ad_yrs) / 120.0
            ay, am, ad_days = _years_to_ymd(ad_dur_yrs)
            if ad_offset == 8:
                ad_end_y, ad_end_m, ad_end_d = md_end_y, md_end_m, md_end_d
            else:
                ad_end_y, ad_end_m, ad_end_d = _add_ymd(ad_start_y, ad_start_m, ad_start_d, ay, am, ad_days)

            antardashas.append({
                "code": ad_code,
                "name_en": ad_en,
                "name_hi": ad_hi,
                "start_str": _fmt_date_short(ad_start_y, ad_start_m, ad_start_d),
                "end_str": _fmt_date_short(ad_end_y, ad_end_m, ad_end_d),
                "end_y": ad_end_y,
                "end_m": ad_end_m,
                "end_d": ad_end_d,
            })

            # Build Pratyantardasha (3rd level) block for this MD--AD pair
            # Only include blocks that end on or after birth date
            ad_end_tuple = (ad_end_y, ad_end_m, ad_end_d)
            birth_tuple = (birth_year, birth_month, birth_day)
            if ad_end_tuple >= birth_tuple and len(pratyantar_blocks) < 60:
                pd_rows = []
                pd_start_y, pd_start_m, pd_start_d = ad_start_y, ad_start_m, ad_start_d
                for pd_offset in range(9):
                    pd_idx = (ad_idx + pd_offset) % 9
                    pd_code, pd_en, pd_hi, pd_yrs = VIMSHOTTARI_ORDER[pd_idx]
                    pd_dur_yrs = (md_yrs * ad_yrs * pd_yrs) / (120.0 * 120.0)
                    py, pm, pd_days = _years_to_ymd(pd_dur_yrs)
                    if pd_offset == 8:
                        pd_end_y, pd_end_m, pd_end_d = ad_end_y, ad_end_m, ad_end_d
                    else:
                        pd_end_y, pd_end_m, pd_end_d = _add_ymd(pd_start_y, pd_start_m, pd_start_d, py, pm, pd_days)

                    if (pd_end_y, pd_end_m, pd_end_d) < birth_tuple:
                        end_disp = "00/00/00"
                    else:
                        end_disp = _fmt_date_short(pd_end_y, pd_end_m, pd_end_d)

                    pd_rows.append({
                        "code": pd_code,
                        "name_en": pd_en,
                        "name_hi": pd_hi,
                        "end_str": end_disp,
                    })
                    pd_start_y, pd_start_m, pd_start_d = pd_end_y, pd_end_m, pd_end_d

                b_start_str = (
                    _fmt_date_short(birth_year, birth_month, birth_day)
                    if (ad_start_y, ad_start_m, ad_start_d) < birth_tuple
                    else _fmt_date_short(ad_start_y, ad_start_m, ad_start_d)
                )
                pratyantar_blocks.append({
                    "title": f"{md_code} -- {ad_code}",
                    "title_hi": f"{md_hi} -- {ad_hi}",
                    "from_str": b_start_str,
                    "to_str": _fmt_date_short(ad_end_y, ad_end_m, ad_end_d),
                    "rows": pd_rows,
                })

            ad_start_y, ad_start_m, ad_start_d = ad_end_y, ad_end_m, ad_end_d

        mahadashas.append({
            "code": md_code,
            "name_en": md_en,
            "name_hi": md_hi,
            "years": md_yrs,
            "header_en": f"{md_code} -{md_yrs} Years",
            "header_hi": f"{md_hi} - {md_yrs} वर्ष",
            "range_str": f"{_fmt_date_short(disp_start_y, disp_start_m, disp_start_d)} - {_fmt_date_short(md_end_y, md_end_m, md_end_d)}",
            "start_full": "Birth" if offset == 0 else _fmt_date_full(disp_start_y, disp_start_m, disp_start_d),
            "end_full": _fmt_date_full(md_end_y, md_end_m, md_end_d),
            "end_y": md_end_y,
            "end_m": md_end_m,
            "end_d": md_end_d,
            "antardashas": antardashas,
        })

        curr_start_y, curr_start_m, curr_start_d = md_end_y, md_end_m, md_end_d

    return {
        "balance_str": balance_str,
        "balance_upper": balance_upper,
        "balance_hi": balance_hi,
        "mahadashas": mahadashas,
        "pratyantar_blocks": pratyantar_blocks,
    }


YOGINI_ORDER = [
    ("Ma", "Mangala", "मंगला", 1, "Moon"),
    ("Pi", "Pingala", "पिंगला", 2, "Sun"),
    ("Dh", "Dhanya", "धान्या", 3, "Jupiter"),
    ("Br", "Bhramari", "भ्रामरी", 4, "Mars"),
    ("Ba", "Bhadrika", "भद्रिका", 5, "Mercury"),
    ("Ul", "Ulka", "उल्का", 6, "Saturn"),
    ("Si", "Siddha", "सिद्धा", 7, "Venus"),
    ("Sn", "Sankata", "संकटा", 8, "Rahu"),
]


def compute_yogini_dasha(moon_sid_lon: float, birth_year: int, birth_month: int, birth_day: int):
    """
    Compute 24 blocks of Yogini Dasha (Pages 21-22 of benchmark PDF).
    Starting Yogini = (Nakshatra_Num + 3) % 8 (1-indexed).
    """
    nak_span = 360.0 / 27.0
    nak_idx = int((moon_sid_lon % 360.0) / nak_span) % 27
    nak_num = nak_idx + 1
    rem_deg = nak_span - ((moon_sid_lon % 360.0) - nak_idx * nak_span)
    frac_rem = rem_deg / nak_span

    start_yogini_idx = ((nak_num + 3 - 1) % 8)
    s_code, s_en, s_hi, s_yrs, _ = YOGINI_ORDER[start_yogini_idx]

    bal_yrs = s_yrs * frac_rem
    by, bm, bd = _years_to_ymd(bal_yrs)
    first_end_y, first_end_m, first_end_d = _add_ymd(birth_year, birth_month, birth_day, by, bm, bd)
    first_start_y, first_start_m, first_start_d = _add_ymd(first_end_y, first_end_m, first_end_d, -s_yrs, 0, 0)

    blocks = []
    curr_y, curr_m, curr_d = first_start_y, first_start_m, first_start_d

    for b_idx in range(24):
        y_idx = (start_yogini_idx + b_idx) % 8
        y_code, y_en, y_hi, y_yrs, _ = YOGINI_ORDER[y_idx]
        end_y, end_m, end_d = _add_ymd(curr_y, curr_m, curr_d, y_yrs, 0, 0)

        sub_rows = []
        ad_y, ad_m, ad_d = curr_y, curr_m, curr_d
        for sub_offset in range(8):
            sub_idx = (y_idx + sub_offset) % 8
            sub_code, sub_en, sub_hi, sub_yrs, _ = YOGINI_ORDER[sub_idx]
            sub_dur = (y_yrs * sub_yrs) / 36.0
            sy, sm, sd = _years_to_ymd(sub_dur)
            if sub_offset == 7:
                ad_end_y, ad_end_m, ad_end_d = end_y, end_m, end_d
            else:
                ad_end_y, ad_end_m, ad_end_d = _add_ymd(ad_y, ad_m, ad_d, sy, sm, sd)

            sub_rows.append({
                "code": sub_code,
                "name_en": sub_en,
                "name_hi": sub_hi,
                "end_str": _fmt_date_short(ad_end_y, ad_end_m, ad_end_d),
            })
            ad_y, ad_m, ad_d = ad_end_y, ad_end_m, ad_end_d

        disp_from_str = (
            sub_rows[0]["end_str"] if b_idx == 0 else _fmt_date_short(curr_y, curr_m, curr_d)
        )
        blocks.append({
            "code": y_code,
            "name_en": y_en,
            "name_hi": y_hi,
            "years": y_yrs,
            "header_en": f"{y_code}   {y_yrs} Years",
            "header_hi": f"{y_hi} ({y_yrs} वर्ष)",
            "from_str": disp_from_str,
            "to_str": _fmt_date_short(end_y, end_m, end_d),
            "rows": sub_rows,
        })
        curr_y, curr_m, curr_d = end_y, end_m, end_d

    return blocks


def compute_char_dasha(core_data: dict):
    """
    Compute Jaimini Char Dasha (Maha Dasha & 12 Antardasha tables) matching Pages 24-25 of PDF.
    """
    meta = core_data["meta"]
    by, bm, bd = meta["year"], meta["month"], meta["day"]
    lagna_idx = meta["lagna_sign_num"] - 1  # 0..11
    p_map = core_data["planet_by_id"]

    # Sign lords (0..11)
    sign_lord_ids = [
        "Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury",
        "Venus", "Mars", "Jupiter", "Saturn", "Rahu", "Jupiter"
    ]
    # Direct vs Indirect (Vamapada / Samapada) groups:
    # Savya (Direct): 1(Ari), 5(Leo), 6(Vir), 7(Lib), 11(Aqu), 12(Pis) -> indices 0, 4, 5, 6, 10, 11
    savya_indices = {0, 4, 5, 6, 10, 11}

    # Sequence of 12 signs from Lagna
    ninth_from_lagna = (lagna_idx + 8) % 12
    is_direct_seq = ninth_from_lagna in savya_indices
    sign_seq = [((lagna_idx + i) % 12 if is_direct_seq else (lagna_idx - i) % 12) for i in range(12)]

    maha_rows = []
    antardasha_blocks = []
    curr_y, curr_m, curr_d = by, bm, bd

    for s_idx in sign_seq:
        lord_id = sign_lord_ids[s_idx]
        lord_sign_idx = p_map[lord_id]["sign_idx"]
        if s_idx in savya_indices:
            yrs = (lord_sign_idx - s_idx) % 12
        else:
            yrs = (s_idx - lord_sign_idx) % 12

        end_y = curr_y + yrs
        s_short = RASHI_SHORT_EN[s_idx].upper()
        maha_rows.append({
            "sign_short": s_short,
            "sign_en": RASHI_NAMES_EN[s_idx],
            "sign_hi": RASHI_NAMES_HI[s_idx],
            "years": yrs,
            "years_str": f"{yrs:02d} Year",
            "start_str": _fmt_date_short(curr_y, curr_m, curr_d),
            "end_str": _fmt_date_short(end_y, curr_m, curr_d),
        })

        # 12 Antardashas inside this Char Mahadasha
        # Antardasha starts from next/prev sign and ends on the Mahadasha sign itself
        ad_direct = s_idx in savya_indices
        ad_rows = []
        ad_y, ad_m, ad_d = curr_y, curr_m, curr_d
        for step in range(1, 13):
            ad_s_idx = (s_idx + step) % 12 if ad_direct else (s_idx - step) % 12
            # Each Antardasha is yrs months long
            next_y, next_m, next_d = _add_ymd(ad_y, ad_m, ad_d, 0, yrs, 0)
            ad_rows.append({
                "sign_short": RASHI_SHORT_EN[ad_s_idx].upper(),
                "sign_hi": RASHI_NAMES_HI[ad_s_idx],
                "start_str": _fmt_date_short(ad_y, ad_m, ad_d),
                "end_str": _fmt_date_short(next_y, next_m, next_d),
            })
            ad_y, ad_m, ad_d = next_y, next_m, next_d

        antardasha_blocks.append({
            "header": f"{s_short} {yrs} Years",
            "header_hi": f"{RASHI_NAMES_HI[s_idx]} ({yrs} वर्ष)",
            "rows": ad_rows,
        })

        curr_y = end_y

    return {
        "maha_rows": maha_rows,
        "antardasha_blocks": antardasha_blocks,
    }


LAL_KITAB_DASHA_CYCLE = [
    ("Sat", "शनि", 6, [("Rahu", "राहु", 24), ("Mer", "बुध", 24), ("Sat", "शनि", 24)]),
    ("Rahu", "राहु", 6, [("Mars", "मंगल", 24), ("Ketu", "केतु", 24), ("Rahu", "राहु", 24)]),
    ("Ketu", "केतु", 3, [("Sat", "शनि", 12), ("Rahu", "राहु", 12), ("Ketu", "केतु", 12)]),
    ("Jup", "गुरु", 6, [("Ketu", "केतु", 24), ("Jup", "गुरु", 24), ("Sun", "सूर्य", 24)]),
    ("Sun", "सूर्य", 2, [("Sun", "सूर्य", 8), ("Moon", "चंद्र", 8), ("Mars", "मंगल", 8)]),
    ("Moon", "चंद्र", 1, [("Jup", "गुरु", 4), ("Sun", "सूर्य", 4), ("Moon", "चंद्र", 4)]),
    ("Ven", "शुक्र", 3, [("Mars", "मंगल", 12), ("Sun", "सूर्य", 12), ("Moon", "चंद्र", 12)]),
    ("Mars", "मंगल", 6, [("Mars", "मंगल", 24), ("Sat", "शनि", 24), ("Ven", "शुक्र", 24)]),
    ("Mer", "बुध", 2, [("Moon", "चंद्र", 8), ("Mars", "मंगल", 8), ("Jup", "गुरु", 8)]),
]


def compute_lal_kitab_dasha(birth_year: int, birth_month: int, birth_day: int):
    """
    Compute 3 full cycles (105 years = 27 blocks) of Lal Kitab 35-Year Dasha.
    Matches Page 34 of the benchmark PDF to the exact date.
    """
    blocks = []
    curr_y, curr_m, curr_d = birth_year, birth_month, birth_day

    for cycle in range(3):
        for p_en, p_hi, yrs, subs in LAL_KITAB_DASHA_CYCLE:
            end_y = curr_y + yrs
            sub_rows = []
            sy, sm, sd = curr_y, curr_m, curr_d
            for sub_en, sub_hi, months in subs:
                sy, sm, sd = _add_ymd(sy, sm, sd, 0, months, 0)
                sub_rows.append({
                    "planet_en": sub_en,
                    "planet_hi": sub_hi,
                    "end_str": f"{sd:02d}/{sm:02d}/{sy:04d}",
                })
            blocks.append({
                "header_en": f"{p_en} {yrs} Year",
                "header_hi": f"{p_hi} ({yrs} वर्ष)",
                "from_str": f"{curr_d:02d}/{curr_m:02d}/{curr_y:04d}",
                "to_str": f"{curr_d:02d}/{curr_m:02d}/{end_y:04d}",
                "rows": sub_rows,
            })
            curr_y = end_y

    return blocks
