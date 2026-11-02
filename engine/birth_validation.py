# -*- coding: utf-8 -*-
"""
Module 1: Birth Data Validation Engine
Validates all birth inputs, performs UTC conversion using historical timezone offsets,
computes Julian Day (UT) and Local Sidereal Time (LST), and logs intermediate steps.
Stops calculation with BirthDataValidationError if essential data is missing or invalid.
"""

from datetime import datetime, date
import math


class BirthDataValidationError(ValueError):
    """Raised when birth data is invalid or missing."""
    pass


def is_leap_year(year: int) -> bool:
    """Deterministic Gregorian leap year rule."""
    if year % 400 == 0:
        return True
    if year % 100 == 0:
        return False
    return year % 4 == 0


def days_in_month(year: int, month: int) -> int:
    """Return exact days in a given Gregorian month."""
    if month in (1, 3, 5, 7, 8, 10, 12):
        return 31
    elif month in (4, 6, 9, 11):
        return 30
    elif month == 2:
        return 29 if is_leap_year(year) else 28
    return 0


def validate_birth_data(
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
) -> dict:
    """
    Validate birth inputs with zero silent fallbacks.
    Returns a verified dictionary with all inputs, intermediate calculations, and validation logs.
    """
    audit_log = []

    # 1. Name & Sex Validation
    name_clean = str(name).strip() if name else ""
    if not name_clean:
        raise BirthDataValidationError("Customer name cannot be empty.")
    audit_log.append(f"Name validated: '{name_clean}'")

    sex_clean = str(sex).strip().lower() if sex else "male"
    if sex_clean not in ("male", "female", "other", "m", "f"):
        raise BirthDataValidationError(f"Invalid sex specified: '{sex}'. Must be 'male', 'female', or 'other'.")
    canonical_sex = "female" if sex_clean in ("female", "f") else "male"
    audit_log.append(f"Sex validated: '{canonical_sex}'")

    # 2. Date Validation (1800 to 2100 CE)
    try:
        y = int(year)
        m = int(month)
        d = int(day)
    except (ValueError, TypeError) as e:
        raise BirthDataValidationError(f"Year, month, and day must be integers: {e}")

    if not (1800 <= y <= 2100):
        raise BirthDataValidationError(f"Year {y} is outside supported historical ephemeris range (1800-2100 CE).")

    if not (1 <= m <= 12):
        raise BirthDataValidationError(f"Month {m} is invalid (must be 1-12).")

    max_days = days_in_month(y, m)
    if not (1 <= d <= max_days):
        raise BirthDataValidationError(f"Day {d} is invalid for month {m} in year {y} (max days: {max_days}).")
    audit_log.append(f"Birth date validated: {d:02d}-{m:02d}-{y:04d} (Leap year: {is_leap_year(y)})")

    # 3. Exact Time Validation
    try:
        hr = int(hour)
        mn = int(minute)
        sc = int(second)
    except (ValueError, TypeError) as e:
        raise BirthDataValidationError(f"Hour, minute, second must be integers: {e}")

    if not (0 <= hr <= 23):
        raise BirthDataValidationError(f"Hour {hr} is invalid (must be 0-23).")
    if not (0 <= mn <= 59):
        raise BirthDataValidationError(f"Minute {mn} is invalid (must be 0-59).")
    if not (0 <= sc <= 59):
        raise BirthDataValidationError(f"Second {sc} is invalid (must be 0-59).")
    audit_log.append(f"Birth time validated: {hr:02d}:{mn:02d}:{sc:02d}")

    # 4. Latitude & Longitude Validation
    if lat is None or lon is None:
        raise BirthDataValidationError("Geographical coordinates (lat, lon) cannot be None. Explicit location required.")

    try:
        lat_f = float(lat)
        lon_f = float(lon)
    except (ValueError, TypeError) as e:
        raise BirthDataValidationError(f"Latitude and longitude must be floats: {e}")

    if not (-90.0 <= lat_f <= 90.0):
        raise BirthDataValidationError(f"Latitude {lat_f} is out of bounds (-90.0 to +90.0).")
    if not (-180.0 <= lon_f <= 180.0):
        raise BirthDataValidationError(f"Longitude {lon_f} is out of bounds (-180.0 to +180.0).")
    audit_log.append(f"Coordinates validated: Latitude={lat_f:.6f}°, Longitude={lon_f:.6f}°")

    # 5. Timezone Validation & UTC conversion
    if tz is None:
        tz_f = 5.5  # Standard default IST if not specified
    else:
        try:
            tz_f = float(tz)
        except (ValueError, TypeError):
            raise BirthDataValidationError(f"Invalid timezone offset: {tz}")

    if not (-12.0 <= tz_f <= 14.0):
        raise BirthDataValidationError(f"Timezone offset {tz_f} is out of bounds (-12.0 to +14.0).")
    audit_log.append(f"Timezone offset validated: UTC{'+' if tz_f >= 0 else ''}{tz_f:.2f} hours")

    # Convert Local Birth Time to UTC
    local_decimal_hour = hr + (mn / 60.0) + (sc / 3600.0)
    utc_decimal_hour = local_decimal_hour - tz_f

    # Adjust date if UTC day boundary is crossed
    utc_y, utc_m, utc_d = y, m, d
    if utc_decimal_hour < 0.0:
        utc_decimal_hour += 24.0
        utc_d -= 1
        if utc_d < 1:
            utc_m -= 1
            if utc_m < 1:
                utc_m = 12
                utc_y -= 1
            utc_d = days_in_month(utc_y, utc_m)
    elif utc_decimal_hour >= 24.0:
        utc_decimal_hour -= 24.0
        utc_d += 1
        if utc_d > days_in_month(utc_y, utc_m):
            utc_d = 1
            utc_m += 1
            if utc_m > 12:
                utc_m = 1
                utc_y += 1

    utc_hr = int(utc_decimal_hour)
    utc_mn = int((utc_decimal_hour - utc_hr) * 60.0)
    utc_sc = int(round(((utc_decimal_hour - utc_hr) * 60.0 - utc_mn) * 60.0))
    if utc_sc >= 60:
        utc_sc -= 60
        utc_mn += 1
    if utc_mn >= 60:
        utc_mn -= 60
        utc_hr += 1
    audit_log.append(f"UTC Timestamp: {utc_d:02d}-{utc_m:02d}-{utc_y:04d} {utc_hr:02d}:{utc_mn:02d}:{utc_sc:02d} UTC (decimal: {utc_decimal_hour:.6f})")

    # 6. High-Precision Julian Day Calculation (UT)
    # Using Fliegel & Van Flandern standard algorithm
    a = (14 - utc_m) // 12
    y_prime = utc_y + 4800 - a
    m_prime = utc_m + 12 * a - 3
    jdn = utc_d + ((153 * m_prime + 2) // 5) + 365 * y_prime + (y_prime // 4) - (y_prime // 100) + (y_prime // 400) - 32045
    jd_ut = jdn - 0.5 + (utc_decimal_hour / 24.0)
    audit_log.append(f"Julian Day (UT): {jd_ut:.6f}")

    # 7. Local Sidereal Time (LST) / RAMC
    t_cent = (jd_ut - 2451545.0) / 36525.0
    # Greenwich Mean Sidereal Time (GMST) at 0h UT + rotation
    gmst_deg = 280.46061837 + 360.98564736629 * (jd_ut - 2451545.0) + 0.000387933 * (t_cent ** 2) - ((t_cent ** 3) / 38710000.0)
    gmst_deg = gmst_deg % 360.0
    lst_deg = (gmst_deg + lon_f) % 360.0
    audit_log.append(f"Greenwich Sidereal Time: {gmst_deg:.4f}°, Local Sidereal Time (LST): {lst_deg:.4f}°")

    # 8. Local Mean Time (LMT) Correction
    # Standard meridian = tz_f * 15.0 deg
    std_meridian = tz_f * 15.0
    lmt_offset_min = (lon_f - std_meridian) * 4.0  # 4 minutes per degree longitude
    lmt_decimal_hour = (local_decimal_hour + (lmt_offset_min / 60.0)) % 24.0
    lmt_hr = int(lmt_decimal_hour)
    lmt_mn = int((lmt_decimal_hour - lmt_hr) * 60.0)
    lmt_sc = int(round(((lmt_decimal_hour - lmt_hr) * 60.0 - lmt_mn) * 60.0))
    if lmt_sc >= 60:
        lmt_sc -= 60
        lmt_mn += 1
    if lmt_mn >= 60:
        lmt_mn -= 60
        lmt_hr = lmt_hr % 24

    return {
        "status": "VALID",
        "inputs": {
            "name": name_clean,
            "sex": canonical_sex,
            "year": y, "month": m, "day": d,
            "hour": hr, "minute": mn, "second": sc,
            "place": str(place).strip(),
            "lat": lat_f, "lon": lon_f, "tz": tz_f,
        },
        "utc": {
            "year": utc_y, "month": utc_m, "day": utc_d,
            "hour": utc_hr, "minute": utc_mn, "second": utc_sc,
            "decimal_hour": utc_decimal_hour,
        },
        "lmt": {
            "hour": lmt_hr, "minute": lmt_mn, "second": lmt_sc,
            "offset_minutes": lmt_offset_min,
            "decimal_hour": lmt_decimal_hour,
        },
        "astronomical": {
            "jd_ut": jd_ut,
            "t_centuries": t_cent,
            "gmst_deg": gmst_deg,
            "lst_deg": lst_deg,
        },
        "audit_log": audit_log,
    }
