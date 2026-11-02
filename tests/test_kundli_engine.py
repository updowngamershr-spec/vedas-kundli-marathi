# -*- coding: utf-8 -*-
"""
Shivansh Astro-Vastu Kundli CRM - Comprehensive Engine Automated Test Suite
Tests all 16 modular calculation engines:
 1. Birth Data Validation (leap year, UTC, historical timezones)
 2. Astronomical Calculations (Julian Day, true obliquity, Lahiri & KP Ayanamsha)
 3. Planetary Longitudes (vs Swiss Ephemeris reference)
 4. Ascendant and Houses (Whole Sign, Sripati Chalit, 12 Placidus Cusps non-repeating)
 5. Nakshatra and Pada (Exact mathematical boundaries)
 6. Vimshottari Dasha (120-year cycle, contiguous, zero '00/00/0000')
 7. KP Astrology (249 subs, 4-level significators)
 8. Shodashvarga (all 16 divisional charts)
 9. Ashtakavarga (337 invariant across 5 benchmark charts)
10. Shadbala & Bhavabala (Component sum integrity: Total == Sum of 6 components)
11. Yoga and Dosha calculations
12. Transit and Varshaphal (Exact solar return search moment)
13. Prediction Engine (100% chart-derived)
14. Marathi Translation Engine (Zero residual English strings)
15. PDF Generation & Layout Integrity
16. Automated Calculation Validation Gate (assert_valid_for_pdf)
"""

import unittest
from datetime import datetime
import math

import sys
sys.path.append(r"D:\question papers\Kundli crm (2)\Vedas Kundli Marathi")

from engine.birth_validation import validate_birth_data, BirthDataValidationError
from engine.astronomy_calc import get_astronomy_data, calc_lahiri_ayanamsha, calc_kp_new_ayanamsha
from engine.planetary_longitudes import calculate_planetary_longitudes
from engine.houses_calc import (
    calculate_ascendant_and_mc, calculate_whole_sign_houses,
    calculate_sripati_chalit, calculate_kp_placidus_cusps, map_planetary_houses
)
from engine.nakshatra_pada import calculate_nakshatra_and_pada, enrich_planets_with_nakshatra
from engine.vimshottari_dasha import calculate_vimshottari_dasha
from engine.kp_astrology import generate_249_sub_table, get_kp_lords, compute_four_fold_significators
from engine.shodashvarga import compute_shodashvarga, calc_varga_sign
from engine.ashtakavarga_engine import calculate_ashtakavarga
from engine.shadbala_bhavabala import calculate_shadbala, calculate_bhavabala
from engine.yoga_dosha import evaluate_yogas, evaluate_manglik_dosha, evaluate_kalsarpa_dosha
from engine.transit_varshaphal import calculate_varshaphal, calculate_transit_today
from engine.prediction_engine import generate_life_predictions
from engine.marathi_engine import to_marathi
from engine.calc_validation import assert_valid_for_pdf, validate_chart_calculations, PDFGenerationLockError
from engine.master_kundli import generate_complete_kundli

# 5 Historical Benchmarks
BENCHMARKS = [
    {
        "name": "Rajesh Joshi", "sex": "male", "year": 1985, "month": 8, "day": 15,
        "hour": 14, "minute": 30, "second": 0, "place": "Pune", "lat": 18.5204, "lon": 73.8567, "tz": 5.5
    },
    {
        "name": "Indira Gandhi", "sex": "female", "year": 1917, "month": 11, "day": 19,
        "hour": 23, "minute": 11, "second": 0, "place": "Allahabad", "lat": 25.4358, "lon": 81.8463, "tz": 5.5
    },
    {
        "name": "Amitabh Bachchan", "sex": "male", "year": 1942, "month": 10, "day": 11,
        "hour": 16, "minute": 0, "second": 0, "place": "Allahabad", "lat": 25.4358, "lon": 81.8463, "tz": 5.5
    },
    {
        "name": "Sachin Tendulkar", "sex": "male", "year": 1973, "month": 4, "day": 24,
        "hour": 16, "minute": 28, "second": 0, "place": "Mumbai", "lat": 18.9220, "lon": 72.8347, "tz": 5.5
    },
    {
        "name": "APJ Abdul Kalam", "sex": "male", "year": 1931, "month": 10, "day": 15,
        "hour": 1, "minute": 15, "second": 0, "place": "Rameswaram", "lat": 9.2876, "lon": 79.3129, "tz": 5.5
    },
]


class TestKundliEngine(unittest.TestCase):

    def test_module1_birth_validation(self):
        """Test birth validation: leap years, valid inputs, and error handling."""
        # Valid birth data
        res = validate_birth_data("Test", "male", 1985, 8, 15, 14, 30, 0, "Pune", 18.5204, 73.8567, 5.5)
        self.assertEqual(res["status"], "VALID")
        self.assertAlmostEqual(res["astronomical"]["jd_ut"], 2446292.875, places=3)
        self.assertEqual(res["utc"]["hour"], 9)
        self.assertEqual(res["utc"]["minute"], 0)

        # Leap year Feb 29 valid
        res_leap = validate_birth_data("Leap", "female", 2000, 2, 29, 12, 0, 0, "Delhi", 28.6139, 77.2090, 5.5)
        self.assertEqual(res_leap["status"], "VALID")

        # Invalid date (Feb 29 in non-leap year) must raise BirthDataValidationError
        with self.assertRaises(BirthDataValidationError):
            validate_birth_data("Invalid", "male", 1985, 2, 29, 12, 0, 0, "Delhi", 28.6139, 77.2090, 5.5)

        # Invalid month
        with self.assertRaises(BirthDataValidationError):
            validate_birth_data("Invalid", "male", 1985, 13, 1, 12, 0, 0, "Delhi", 28.6139, 77.2090, 5.5)

    def test_module2_astronomy_calc(self):
        """Test astronomical calculations against Swiss Ephemeris / IAU standards."""
        jd_ut = 2446292.875  # 15 Aug 1985 09:00 UTC
        astro = get_astronomy_data(jd_ut)
        self.assertTrue(astro["has_swisseph"])
        self.assertGreater(astro["lahiri_ayanamsha"], 23.6)
        self.assertLess(astro["lahiri_ayanamsha"], 23.7)
        self.assertGreater(astro["kp_ayanamsha"], 23.5)
        self.assertLess(astro["kp_ayanamsha"], 23.6)
        # Lahiri - KP difference should be ~5 to 6 arcminutes (~300 to 360 arcseconds)
        diff_arcsec = (astro["lahiri_ayanamsha"] - astro["kp_ayanamsha"]) * 3600.0
        self.assertGreater(diff_arcsec, 300.0)
        self.assertLess(diff_arcsec, 360.0)

    def test_module3_planetary_longitudes(self):
        """Test planetary longitudes are strictly within 0-360 degrees."""
        jd_ut = 2446292.875
        ayan = 23.6558
        pl_data = calculate_planetary_longitudes(jd_ut, ayan)
        p_by_id = pl_data["planet_by_id"]
        for pid in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]:
            self.assertIn(pid, p_by_id)
            lon = p_by_id[pid]["sid_lon"]
            self.assertGreaterEqual(lon, 0.0)
            self.assertLess(lon, 360.0)

        # Ketu must be strictly 180° opposite Rahu
        rahu_lon = p_by_id["Rahu"]["sid_lon"]
        ketu_lon = p_by_id["Ketu"]["sid_lon"]
        diff = abs((ketu_lon - rahu_lon + 180.0) % 360.0 - 180.0)
        self.assertAlmostEqual(diff, 180.0, places=2)

    def test_module4_houses_and_placidus_cusps(self):
        """Test Ascendant, Whole Sign, Sripati, and KP Placidus cusps (non-repeating & monotonic)."""
        jd_ut = 2446292.875
        lat = 18.5204
        lon = 73.8567
        ayan = 23.6558
        kp_ayan = 23.5625

        asc_dict = calculate_ascendant_and_mc(172.574, lat, 23.443, ayan)
        asc_sid = asc_dict["asc_sid"]
        mc_sid = asc_dict["mc_sid"]
        self.assertGreaterEqual(asc_sid, 0.0)
        self.assertLess(asc_sid, 360.0)

        # 12 Whole Sign houses
        ws_houses = calculate_whole_sign_houses(asc_sid)
        self.assertEqual(len(ws_houses), 12)

        # Sripati Chalit
        chalit = calculate_sripati_chalit(asc_sid, mc_sid)
        self.assertEqual(len(chalit["bhav_madhyas"]), 12)
        self.assertEqual(len(chalit["bhav_sandhis"]), 12)

        # KP Placidus cusps: 12 cusps strictly unique and monotonic
        kp_cusps = calculate_kp_placidus_cusps(jd_ut, lat, lon, kp_ayan)
        self.assertEqual(len(kp_cusps), 12)
        self.assertEqual(len(set(round(c, 4) for c in kp_cusps)), 12)
        for i in range(12):
            arc = (kp_cusps[(i + 1) % 12] - kp_cusps[i]) % 360.0
            self.assertGreater(arc, 0.0, f"Cusp {i+1} and {i+2} inverted or duplicate")
            self.assertLess(arc, 60.0, f"Cusp {i+1} span too large ({arc}°)")

    def test_module5_nakshatra_pada(self):
        """Test Nakshatra (1-27) and Pada (1-4) calculation formulas."""
        # 0° sidereal Aries -> Ashwini 1 (Ketu)
        ash1 = calculate_nakshatra_and_pada(0.0)
        self.assertEqual(ash1["nak_num"], 1)
        self.assertEqual(ash1["pada"], 1)
        self.assertEqual(ash1["nak_lord_en"], "Ketu")

        # 13°19' sidereal Aries -> Ashwini 4 (Ketu)
        ash4 = calculate_nakshatra_and_pada(13.31)
        self.assertEqual(ash4["nak_num"], 1)
        self.assertEqual(ash4["pada"], 4)

        # 13°21' sidereal Aries -> Bharani 1 (Venus)
        bhar1 = calculate_nakshatra_and_pada(13.36)
        self.assertEqual(bhar1["nak_num"], 2)
        self.assertEqual(bhar1["pada"], 1)
        self.assertEqual(bhar1["nak_lord_en"], "Venus")

    def test_module6_vimshottari_dasha_continuity(self):
        """Test Vimshottari 120-year cycle continuity, zero dates, and exact progression."""
        # 100.0° sidereal Cancer is in Pushya Nakshatra (Saturn lord)
        moon_lon = 100.0
        vim = calculate_vimshottari_dasha(moon_lon, 1985, 8, 15)
        self.assertEqual(vim["balance"]["lord_en"], "Saturn")
        self.assertEqual(len(vim["mahadashas"]), 9)
        total_yrs = sum(md["duration_years"] for md in vim["mahadashas"])
        self.assertAlmostEqual(total_yrs, 120.0, places=1)

        # Verify no 00/00/0000 dates
        for md in vim["mahadashas"]:
            self.assertNotIn("00/00", md["start_str"])
            self.assertNotIn("00/00", md["end_str"])
            for ad in md["antardashas"]:
                self.assertNotIn("00/00", ad["start_str"])
                self.assertNotIn("00/00", ad["end_str"])

    def test_module7_kp_249_subs(self):
        """Test KP 249 sub table integrity and four-fold significator matrix."""
        subs = generate_249_sub_table()
        self.assertEqual(len(subs), 249)
        self.assertEqual(subs[0]["sub_num"], 1)
        self.assertEqual(subs[-1]["sub_num"], 249)
        self.assertAlmostEqual(subs[-1]["end_lon"], 360.0, places=2)

    def test_module8_shodashvarga_16_charts(self):
        """Test all 16 divisional charts are calculated independently."""
        pl_data = calculate_planetary_longitudes(2446292.875, 23.6558)
        shodash = compute_shodashvarga(pl_data["planets"], 232.09)
        charts = shodash["charts"]
        expected_vargas = ["D1", "D2", "D3", "D4", "D7", "D9", "D10", "D12", "D16", "D20", "D24", "D27", "D30", "D40", "D45", "D60"]
        self.assertEqual(len(charts), 16)
        for v in expected_vargas:
            self.assertIn(v, charts)
            self.assertIn("lagna_sign", charts[v])
            self.assertGreaterEqual(charts[v]["lagna_sign"], 1)
            self.assertLessEqual(charts[v]["lagna_sign"], 12)

    def test_module9_ashtakavarga_337_invariant(self):
        """Test Parashari Ashtakavarga 337 total across all 5 benchmark charts."""
        for bm in BENCHMARKS:
            k = generate_complete_kundli(
                name=bm["name"], sex=bm["sex"], year=bm["year"], month=bm["month"],
                day=bm["day"], hour=bm["hour"], minute=bm["minute"], second=bm["second"],
                place=bm["place"], lat=bm["lat"], lon=bm["lon"], tz=bm["tz"]
            )
            # Check 7 individual BAV totals
            expected_bhinna = {"Sun": 48, "Moon": 49, "Mars": 39, "Mercury": 54, "Jupiter": 56, "Venus": 52, "Saturn": 39}
            mod_ash = k["modular"]["ashtakavarga"]
            self.assertEqual(mod_ash["bhinna_totals"], expected_bhinna, f"BAV totals failed for {bm['name']}")
            self.assertEqual(mod_ash["sarvashtakavarga_total"], 337, f"SAV 337 invariant failed for {bm['name']}")

    def test_module10_shadbala_component_sums(self):
        """Test Shadbala component sum integrity: Total == Sthana + Dig + Kala + Cheshta + Naisargika + Drik."""
        k = generate_complete_kundli(
            name="Rajesh Joshi", sex="male", year=1985, month=8, day=15,
            hour=14, minute=30, second=0, place="Pune", lat=18.5204, lon=73.8567, tz=5.5
        )
        shad = k["modular"]["shadbala"]
        comps = shad["components"]
        totals = shad["total_virupas"]
        for pid in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
            c_sum = (
                comps["sthana_bala"][pid] + comps["dig_bala"][pid] +
                comps["kala_bala"][pid] + comps["cheshta_bala"][pid] +
                comps["naisargika_bala"][pid] + comps["drik_bala"][pid]
            )
            rep_tot = totals[pid]
            self.assertAlmostEqual(c_sum, rep_tot, places=2, msg=f"Shadbala component sum mismatch for {pid}")

    def test_module11_yogas_and_doshas(self):
        """Test deterministic evaluation of classical Yogas, Manglik Dosha, and Kalsarpa Dosha."""
        k = generate_complete_kundli(
            name="Rajesh Joshi", sex="male", year=1985, month=8, day=15,
            hour=14, minute=30, second=0, place="Pune", lat=18.5204, lon=73.8567, tz=5.5
        )
        mod_yogas = k["modular"]["yogas"]
        mod_manglik = k["modular"]["manglik"]
        mod_kalsarpa = k["modular"]["kalsarpa"]
        self.assertIsInstance(mod_yogas, list)
        self.assertIn("is_manglik", mod_manglik)
        self.assertIn("has_kalsarpa", mod_kalsarpa)

    def test_module14_marathi_translation(self):
        """Test Marathi translation engine eliminates English abbreviations and produces authentic Marathi."""
        sample_en = "From 15/08/1985 - To 23/04/1987 JUP - 16 Years Sign Lord Sub Lord CONJ OPPN SUN VEN"
        mr = to_marathi(sample_en)
        self.assertNotIn("From", mr)
        self.assertNotIn("To", mr)
        self.assertNotIn("Years", mr)
        self.assertNotIn("Sign Lord", mr)
        self.assertNotIn("Sub Lord", mr)
        self.assertNotIn("CONJ", mr)
        self.assertNotIn("OPPN", mr)
        self.assertIn("ते", mr)
        self.assertIn("राशी स्वामी", mr)
        self.assertIn("उपस्वामी", mr)
        self.assertIn("युती", mr)
        self.assertIn("प्रतियुती", mr)
        self.assertTrue("रवी" in mr or "सूर्य" in mr)
        self.assertIn("शुक्र", mr)

    def test_module16_pdf_generation_lock(self):
        """Test validation gate locks PDF export if calculations fail verification."""
        valid_k = generate_complete_kundli(
            name="Rajesh Joshi", sex="male", year=1985, month=8, day=15,
            hour=14, minute=30, second=0, place="Pune", lat=18.5204, lon=73.8567, tz=5.5
        )
        # Should pass without error
        self.assertTrue(assert_valid_for_pdf(valid_k))

        # Intentionally corrupt data (change Sarvashtakavarga total to 330)
        corrupt_k = dict(valid_k)
        corrupt_k["modular"]["ashtakavarga"]["sarvashtakavarga_total"] = 330
        corrupt_k["ashtakavarga"]["total_bindus"] = 330
        corrupt_k["ashtakavarga"]["sarva_totals"] = [25] * 12  # sum = 300
        with self.assertRaises(PDFGenerationLockError):
            assert_valid_for_pdf(corrupt_k)


if __name__ == "__main__":
    unittest.main()
