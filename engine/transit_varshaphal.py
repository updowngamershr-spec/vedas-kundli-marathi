# -*- coding: utf-8 -*-
"""
Module 12: Transit and Tajika Varshaphal Engine
1. Transit (Gochara): Calculates planetary positions for the exact transit date and time.
2. Tajika Varshaphal (Annual Solar Return):
   - Calculates the exact astronomical moment when the Sidereal Sun matches the Natal Sidereal Sun.
   - Calculates independent Varsha Lagna, annual planets, Muntha, and 1-year Mudda Dashas.
   - Strictly keeps natal chart and annual chart calculations separate.
"""

from datetime import datetime, timedelta
import math
import astronomy
from engine.astronomy_calc import calc_lahiri_ayanamsha
from engine.planetary_longitudes import calculate_planetary_longitudes
from engine.houses_calc import calculate_ascendant_and_mc, calculate_sripati_chalit, map_planetary_houses
from engine.astronomy_calc import calc_true_obliquity

VIM_LORDS_ORDER = ["Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury", "Ketu", "Venus"]
MUDDA_DAYS = {
    "Sun": 110,      # 110/365 of year = 36.5 days
    "Moon": 183,
    "Mars": 128,
    "Rahu": 329,
    "Jupiter": 292,
    "Saturn": 347,
    "Mercury": 310,
    "Ketu": 128,
    "Venus": 365,
}


def find_solar_return_moment(
    natal_sun_sid: float,
    target_year: int,
    birth_month: int,
    birth_day: int,
    birth_hour: int,
    birth_minute: int,
    tz_hours: float
) -> tuple[datetime, float]:
    """
    Use high-precision secant/binary search to find the exact UTC moment in target_year
    when the Sidereal Sun matches natal_sun_sid within 0.0001° (0.36 arcseconds).
    """
    # Safe handling of Feb 29 for non-leap target years
    b_day = birth_day
    if birth_month == 2 and birth_day == 29:
        if not (target_year % 4 == 0 and (target_year % 100 != 0 or target_year % 400 == 0)):
            b_day = 28

    approx_dt_utc = datetime(target_year, birth_month, b_day, birth_hour, birth_minute, 0) - timedelta(hours=tz_hours)

    def _get_sid_sun(dt_u: datetime) -> float:
        t = astronomy.Time.Make(dt_u.year, dt_u.month, dt_u.day, dt_u.hour, dt_u.minute, dt_u.second + dt_u.microsecond / 1e6)
        jd = t.ut + 2451545.0
        ayan = calc_lahiri_ayanamsha(jd)
        ecl = astronomy.SunPosition(t)
        return (ecl.elon - ayan) % 360.0

    # Binary search window of +/- 3 days
    t_low = approx_dt_utc - timedelta(days=2.5)
    t_high = approx_dt_utc + timedelta(days=2.5)

    best_dt = approx_dt_utc
    for _ in range(35):
        mid_dt = t_low + (t_high - t_low) / 2
        sun_mid = _get_sid_sun(mid_dt)
        diff = (sun_mid - natal_sun_sid + 180.0) % 360.0 - 180.0

        if abs(diff) < 0.00005:  # sub-arcsecond convergence
            best_dt = mid_dt
            break

        if diff < 0.0:
            t_low = mid_dt
        else:
            t_high = mid_dt
        best_dt = mid_dt

    t_best = astronomy.Time.Make(best_dt.year, best_dt.month, best_dt.day, best_dt.hour, best_dt.minute, best_dt.second + best_dt.microsecond / 1e6)
    jd_solar_return = t_best.ut + 2451545.0
    return best_dt, jd_solar_return


def calculate_varshaphal(
    natal_sun_sid: float,
    natal_lagna_sign_num: int,
    birth_year: int,
    birth_month: int,
    birth_day: int,
    birth_hour: int,
    birth_minute: int,
    lat: float,
    lon: float,
    tz: float,
    target_year: int
) -> dict:
    """
    Calculate complete Tajika Varshaphal for target_year from first principles.
    """
    solar_dt_utc, jd_varsha = find_solar_return_moment(
        natal_sun_sid, target_year, birth_month, birth_day, birth_hour, birth_minute, tz
    )
    solar_dt_local = solar_dt_utc + timedelta(hours=tz)
    ayan_varsha = calc_lahiri_ayanamsha(jd_varsha)
    obl_varsha = calc_true_obliquity(jd_varsha)

    # 1. Calculate Varsha Lagna
    t_varsha = (jd_varsha - 2451545.0) / 36525.0
    gmst = (280.46061837 + 360.98564736629 * (jd_varsha - 2451545.0)) % 360.0
    lst_varsha = (gmst + lon) % 360.0
    varsha_ascmc = calculate_ascendant_and_mc(lst_varsha, lat, obl_varsha, ayan_varsha)
    varsha_lagna_sign = varsha_ascmc["asc_sign_num"]

    # 2. Calculate Annual Planetary Positions
    varsha_planets_data = calculate_planetary_longitudes(jd_varsha, ayan_varsha)
    varsha_chalit = calculate_sripati_chalit(varsha_ascmc["asc_sid"], varsha_ascmc["mc_sid"])
    varsha_planets = map_planetary_houses(varsha_planets_data["planets"], varsha_ascmc["asc_sign_idx"], varsha_chalit)

    # 3. Calculate Muntha (Moves 1 sign per year of age)
    age = target_year - birth_year
    muntha_sign_num = ((natal_lagna_sign_num - 1 + age) % 12) + 1
    # House occupied by Muntha in Varsha Chart
    muntha_house = ((muntha_sign_num - varsha_lagna_sign + 12) % 12) + 1

    # 4. Mudda Dasha (1-year Vimshottari cycle)
    mudda_dashas = []
    curr_dt = solar_dt_local
    for p_name in ["Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury", "Ketu", "Venus"]:
        days_span = (MUDDA_DAYS[p_name] * 365.25) / 2190.0  # proportional
        end_dt = curr_dt + timedelta(days=days_span)
        mudda_dashas.append({
            "planet_en": p_name,
            "start_dt": curr_dt,
            "end_dt": end_dt,
            "start_str": f"{curr_dt.day:02d}/{curr_dt.month:02d}/{curr_dt.year}",
            "end_str": f"{end_dt.day:02d}/{end_dt.month:02d}/{end_dt.year}",
            "days": round(days_span, 1),
        })
        curr_dt = end_dt

    return {
        "target_year": target_year,
        "age": age,
        "solar_return_dt_utc": solar_dt_utc,
        "solar_return_dt_local": solar_dt_local,
        "jd_varsha": jd_varsha,
        "varsha_lagna_sign": varsha_lagna_sign,
        "muntha_sign": muntha_sign_num,
        "muntha_house": muntha_house,
        "varsha_planets": varsha_planets,
        "varsha_ascmc": varsha_ascmc,
        "mudda_dashas": mudda_dashas,
    }


def calculate_transit_today(lat: float, lon: float, tz: float) -> dict:
    """
    Calculate Gochara (Transit) planetary positions for current real-time moment.
    """
    now_dt = datetime.now()
    now_utc = now_dt - timedelta(hours=tz)
    t = astronomy.Time.Make(now_utc.year, now_utc.month, now_utc.day, now_utc.hour, now_utc.minute, now_utc.second)
    jd_now = t.ut + 2451545.0
    ayan_now = calc_lahiri_ayanamsha(jd_now)

    transit_data = calculate_planetary_longitudes(jd_now, ayan_now)
    return {
        "transit_dt": now_dt,
        "jd_transit": jd_now,
        "ayanamsha": ayan_now,
        "planets": transit_data["planets"],
        "planet_by_id": transit_data["planet_by_id"],
    }
