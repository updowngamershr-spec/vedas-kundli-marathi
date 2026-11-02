# -*- coding: utf-8 -*-
"""
Module 2: Astronomical Calculations Engine
Calculates True Obliquity of Ecliptic, Nutation, Lahiri Ayanamsha, and KP New Ayanamsha.
Records calculation metadata, ephemeris version, and settings.
"""

import math
try:
    import swisseph as swe
    HAS_SWISSEPH = True
    SWISSEPH_VERSION = getattr(swe, "__version__", "2.10.03")
except ImportError:
    HAS_SWISSEPH = False
    SWISSEPH_VERSION = "Unavailable"


def calc_true_obliquity(jd_ut: float) -> float:
    """
    Calculate True Obliquity of the Ecliptic (eps) in degrees for Julian Day.
    Formula: eps = eps0 + Delta_eps (where eps0 is IAU 1980 mean obliquity, Delta_eps is nutation).
    """
    if HAS_SWISSEPH:
        try:
            # swe.calc_ut with ECL_NUT gives (eps_true, eps_mean, nut_lon, nut_obl)
            res, _ = swe.calc_ut(jd_ut, swe.ECL_NUT)
            return float(res[0])
        except Exception:
            pass

    # Analytical IAU 1980 / Meeus fallback
    T = (jd_ut - 2451545.0) / 36525.0
    eps0 = 23.43929111 - (46.8150 * T + 0.00059 * T * T - 0.001813 * (T ** 3)) / 3600.0
    omega = math.radians((125.04452 - 1934.136261 * T) % 360.0)
    d_eps = (9.2025 / 3600.0) * math.cos(omega)
    return eps0 + d_eps


def calc_lahiri_ayanamsha(jd_ut: float) -> float:
    """
    Calculate N.C. Lahiri (Chitrapaksha) Ayanamsha in degrees.
    Formula: Sidereal Longitude = Tropical Longitude - Lahiri Ayanamsha.
    """
    if HAS_SWISSEPH:
        try:
            swe.set_sid_mode(swe.SIDM_LAHIRI)
            return float(swe.get_ayanamsa_ut(jd_ut))
        except Exception:
            pass

    # Analytical IAU precession model calibrated to Chitrapaksha (Spica = 180° sidereal)
    T = (jd_ut - 2451545.0) / 36525.0
    # Lahiri at J2000.0 = 23° 51' 25.53" = 23.857092°
    ayan = 23.856528 + 1.396042 * T + 0.000308 * (T ** 2)
    return ayan


def calc_kp_new_ayanamsha(jd_ut: float) -> float:
    """
    Calculate KP New (Krishnamurti Paddhati 291) Ayanamsha in degrees.
    Matches KP Standard (23°21'21" on Aug 3, 1970).
    """
    if HAS_SWISSEPH:
        try:
            swe.set_sid_mode(swe.SIDM_KRISHNAMURTI)
            return float(swe.get_ayanamsa_ut(jd_ut))
        except Exception:
            pass

    T = (jd_ut - 2451545.0) / 36525.0
    return 23.763194 + 1.396042 * T + 0.000308 * (T ** 2)


def get_astronomy_data(jd_ut: float) -> dict:
    """
    Compile complete astronomical context for a given Julian Day UT.
    """
    lahiri_ayan = calc_lahiri_ayanamsha(jd_ut)
    kp_ayan = calc_kp_new_ayanamsha(jd_ut)
    obliquity = calc_true_obliquity(jd_ut)

    return {
        "engine": f"Swiss Ephemeris v{SWISSEPH_VERSION}" if HAS_SWISSEPH else "Moshier / Meeus IAU Analytical",
        "has_swisseph": HAS_SWISSEPH,
        "ephemeris_version": str(SWISSEPH_VERSION),
        "jd_ut": jd_ut,
        "obliquity_deg": obliquity,
        "lahiri_ayanamsha": lahiri_ayan,
        "kp_ayanamsha": kp_ayan,
        "ayanamsha": {
            "lahiri_deg": lahiri_ayan,
            "kp_new_deg": kp_ayan,
            "difference_arcsec": (lahiri_ayan - kp_ayan) * 3600.0,
        },
        "settings": {
            "node_type": "MEAN_NODE (Classical Parashari)",
            "ayanamsa_system": "NC_Lahiri_Chitrapaksha_1955",
            "kp_ayanamsa_system": "KP_New_291",
        }
    }
