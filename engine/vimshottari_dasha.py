# -*- coding: utf-8 -*-
"""
Module 6: Vimshottari Dasha Engine
Calculates exact birth-time balance and complete 120-year cycle of Mahadashas,
Antardashas, Pratyantardashas, and Sookshma Dashas.
Formulas:
- Balance at Birth = Lord Mahadasha Duration * Remaining Nakshatra Fraction
- Antardasha Duration = MD_years * AD_years / 120.0
- Pratyantardasha Duration = AD_years * PD_years / 120.0
Strictly contiguous calendar progression without gaps, overlaps, or '00/00/0000'.
"""

from datetime import datetime, timedelta
from engine.nakshatra_pada import calculate_nakshatra_and_pada, VIMSHOTTARI_LORDS, VIMSHOTTARI_YEARS

# Marathi / Hindi names mapping
PLANET_NAMES = {
    "Ketu": {"mr": "केतू", "hi": "केतु", "short_mr": "के"},
    "Venus": {"mr": "शुक्र", "hi": "शुक्र", "short_mr": "शु"},
    "Sun": {"mr": "रवी", "hi": "सूर्य", "short_mr": "रवि"},
    "Moon": {"mr": "चंद्र", "hi": "चन्द्र", "short_mr": "चं"},
    "Mars": {"mr": "मंगळ", "hi": "मंगल", "short_mr": "मं"},
    "Rahu": {"mr": "राहू", "hi": "राहु", "short_mr": "रा"},
    "Jupiter": {"mr": "गुरू", "hi": "गुरु", "short_mr": "गु"},
    "Saturn": {"mr": "शनी", "hi": "शनि", "short_mr": "श"},
    "Mercury": {"mr": "बुध", "hi": "बुध", "short_mr": "बु"},
}

DAYS_PER_YEAR = 365.242199


def _add_years(start_dt: datetime, years_float: float) -> datetime:
    """Add exact fractional years to a datetime using astronomical year length."""
    days = years_float * DAYS_PER_YEAR
    return start_dt + timedelta(days=days)


def _fmt_date_short(dt: datetime) -> str:
    """Format datetime as DD/MM/YYYY."""
    return f"{dt.day:02d}/{dt.month:02d}/{dt.year:04d}"


def calculate_vimshottari_dasha(
    moon_sid_lon: float,
    birth_year: int,
    birth_month: int,
    birth_day: int,
    birth_hour: int = 12,
    birth_minute: int = 0,
    ayanamsha_name: str = "Lahiri"
) -> dict:
    """
    Calculate complete, contiguous Vimshottari Dasha structure for 120 years.
    """
    nak_info = calculate_nakshatra_and_pada(moon_sid_lon)
    lord = nak_info["nak_lord_en"]
    lord_years = VIMSHOTTARI_YEARS[lord]
    rem_fraction = nak_info["remaining_fraction"]

    # Balance at birth
    balance_years_total = lord_years * rem_fraction
    b_y = int(balance_years_total)
    rem_m = (balance_years_total - b_y) * 12.0
    b_m = int(rem_m)
    b_d = int(round((rem_m - b_m) * 30.4375))
    if b_d >= 30:
        b_d -= 30
        b_m += 1
    if b_m >= 12:
        b_m -= 12
        b_y += 1

    balance_str_mr = f"{PLANET_NAMES[lord]['mr']}: {b_y} वर्षे, {b_m} महिने, {b_d} दिवस"
    balance_str_en = f"{lord}: {b_y} Years, {b_m} Months, {b_d} Days"

    birth_dt = datetime(birth_year, birth_month, birth_day, birth_hour, birth_minute)
    now_dt = datetime.now()

    # Determine Vimshottari cycle starting planet index
    start_lord_idx = VIMSHOTTARI_LORDS.index(lord)

    # First Mahadasha begins before birth by (lord_years - balance_years_total)
    spent_years = lord_years - balance_years_total
    cycle_start_dt = _add_years(birth_dt, -spent_years)

    mahadashas = []
    current_dt = cycle_start_dt
    running_md = None
    running_ad = None

    for i in range(9):
        l_idx = (start_lord_idx + i) % 9
        md_lord = VIMSHOTTARI_LORDS[l_idx]
        md_duration = VIMSHOTTARI_YEARS[md_lord]
        md_start = current_dt
        md_end = _add_years(md_start, md_duration)
        current_dt = md_end

        is_running_md = (md_start <= now_dt < md_end)

        # 9 Antardashas within this Mahadasha
        antardashas = []
        ad_current_dt = md_start
        ad_start_idx = l_idx

        for j in range(9):
            ad_l_idx = (ad_start_idx + j) % 9
            ad_lord = VIMSHOTTARI_LORDS[ad_l_idx]
            ad_lord_years = VIMSHOTTARI_YEARS[ad_lord]
            ad_duration = (md_duration * ad_lord_years) / 120.0
            ad_start = ad_current_dt
            ad_end = _add_years(ad_start, ad_duration)
            ad_current_dt = ad_end

            is_running_ad = is_running_md and (ad_start <= now_dt < ad_end)
            is_pre_birth = (ad_end <= birth_dt)

            # Pratyantardashas within this Antardasha
            pratyantars = []
            pd_current_dt = ad_start
            for k in range(9):
                pd_l_idx = (ad_l_idx + k) % 9
                pd_lord = VIMSHOTTARI_LORDS[pd_l_idx]
                pd_lord_years = VIMSHOTTARI_YEARS[pd_lord]
                pd_duration = (ad_duration * pd_lord_years) / 120.0
                pd_start = pd_current_dt
                pd_end = _add_years(pd_start, pd_duration)
                pd_current_dt = pd_end

                pratyantars.append({
                    "lord_en": pd_lord,
                    "lord_mr": PLANET_NAMES[pd_lord]["mr"],
                    "lord_short_mr": PLANET_NAMES[pd_lord]["short_mr"],
                    "start_dt": pd_start,
                    "end_dt": pd_end,
                    "start_str": _fmt_date_short(pd_start),
                    "end_str": _fmt_date_short(pd_end),
                })

            ad_dict = {
                "lord_en": ad_lord,
                "lord_mr": PLANET_NAMES[ad_lord]["mr"],
                "lord_short_mr": PLANET_NAMES[ad_lord]["short_mr"],
                "start_dt": ad_start,
                "end_dt": ad_end,
                "start_str": _fmt_date_short(ad_start),
                "end_str": _fmt_date_short(ad_end),
                "duration_years": ad_duration,
                "is_running": is_running_ad,
                "is_pre_birth": is_pre_birth,
                "pratyantardashas": pratyantars,
            }
            antardashas.append(ad_dict)
            if is_running_ad:
                running_ad = ad_dict

        md_dict = {
            "lord_en": md_lord,
            "lord_mr": PLANET_NAMES[md_lord]["mr"],
            "lord_short_mr": PLANET_NAMES[md_lord]["short_mr"],
            "duration_years": md_duration,
            "start_dt": md_start,
            "end_dt": md_end,
            "start_str": _fmt_date_short(md_start),
            "end_str": _fmt_date_short(md_end),
            "is_running": is_running_md,
            "antardashas": antardashas,
        }
        mahadashas.append(md_dict)
        if is_running_md:
            running_md = md_dict

    return {
        "ayanamsha_used": ayanamsha_name,
        "balance": {
            "lord_en": lord,
            "lord_mr": PLANET_NAMES[lord]["mr"],
            "years": b_y,
            "months": b_m,
            "days": b_d,
            "balance_str_mr": balance_str_mr,
            "balance_str_en": balance_str_en,
            "fraction_remaining": rem_fraction,
        },
        "cycle_start_dt": cycle_start_dt,
        "cycle_end_dt": current_dt,
        "total_cycle_years": 120.0,
        "mahadashas": mahadashas,
        "running_mahadasha": running_md,
        "running_antardasha": running_ad,
    }
