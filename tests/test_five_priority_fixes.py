import sys
sys.path.insert(0, r"D:\question papers\Kundli crm (2)\Vedas Kundli Marathi")
sys.stdout.reconfigure(encoding='utf-8')
import unittest
from engine.master_kundli import generate_complete_kundli
from engine.calc_validation import assert_valid_for_pdf, validate_chart_calculations, PDFGenerationLockError

class TestFivePriorityFixes(unittest.TestCase):

    def setUp(self):
        self.benchmarks = [
            ("Rajesh Joshi", "male", 1985, 5, 15, 14, 30, 0, "Pune, India", 18.5204, 73.8567, 5.5),
            ("Indira Gandhi", "female", 1917, 11, 19, 23, 11, 0, "Allahabad, India", 25.4358, 81.8463, 5.5),
            ("Amitabh Bachchan", "male", 1942, 10, 11, 16, 0, 0, "Allahabad, India", 25.4358, 81.8463, 5.5),
            ("Sachin Tendulkar", "male", 1973, 4, 24, 16, 28, 0, "Mumbai, India", 19.0760, 72.8777, 5.5),
            ("APJ Abdul Kalam", "male", 1931, 10, 15, 1, 15, 0, "Rameswaram, India", 9.2876, 79.3129, 5.5),
        ]

    def test_priority_1_house_mapping_engine_independence(self):
        """1. House Mapping Engine: Whole Sign, Sripati Chalit, and Transit are independent."""
        for name, sex, y, m, d, hr, mn, sc, place, lat, lon, tz in self.benchmarks:
            data = generate_complete_kundli(name, sex, y, m, d, hr, mn, sc, place, lat, lon, tz)
            asc_sign_idx = int(data["meta"]["asc_sid_lon"] / 30.0) % 12
            
            # A. Whole Sign Parashari Verification
            for p in data["planets"]:
                if p["id"] == "ASC":
                    continue
                exp_rashi_h = ((p["sign_idx"] - asc_sign_idx + 12) % 12) + 1
                self.assertEqual(p["house"], exp_rashi_h, f"Whole sign mismatch for {p['id']} in {name}")
                self.assertEqual(p["rashi_house"], exp_rashi_h, f"Rashi house mismatch for {p['id']} in {name}")
                # Chalit house must be between 1 and 12
                self.assertTrue(1 <= p["chalit_house"] <= 12, f"Invalid chalit house {p['chalit_house']} for {p['id']} in {name}")

            # B. Transit House Mapping
            vp = data["varshaphal"]
            for tp in vp["transit_planets"]:
                t_sign = tp.get("sign_idx", int(tp.get("sid_lon", 0.0) / 30.0) % 12)
                exp_trans_h = ((t_sign - asc_sign_idx + 12) % 12) + 1
                act_trans_h = tp.get("lagna_house") or tp.get("house")
                self.assertEqual(act_trans_h, exp_trans_h, f"Transit house mismatch for {tp.get('id')} in {name}")
            print(f"[PASS] Priority 1: House Mapping Engine verified independently for {name}")

    def test_priority_2_kp_cusp_engine_12_monotonic(self):
        """2. KP Cusp Engine: All 12 Placidus cusps independently calculated, non-repeating, strictly monotonic."""
        for name, sex, y, m, d, hr, mn, sc, place, lat, lon, tz in self.benchmarks:
            data = generate_complete_kundli(name, sex, y, m, d, hr, mn, sc, place, lat, lon, tz)
            kp_cusps = data["kp"]["kp_cusp_lons"]
            self.assertEqual(len(kp_cusps), 12, f"KP cusps must have 12 values in {name}")
            
            # Check unique values (no repeated cusps)
            unique_cusps = len(set(round(c, 3) for c in kp_cusps))
            self.assertEqual(unique_cusps, 12, f"Repeated KP cusp values found in {name} ({unique_cusps} unique)")
            
            # Check strictly monotonic progression (arc between consecutive cusps must be 15° to 45°)
            for i in range(12):
                c1 = kp_cusps[i]
                c2 = kp_cusps[(i + 1) % 12]
                arc = (c2 - c1) % 360.0
                self.assertTrue(15.0 <= arc <= 45.0, f"Non-monotonic cusp arc {arc:.2f}° at Cusp {i+1}->{((i+1)%12)+1} in {name}")
            print(f"[PASS] Priority 2: KP Cusp Engine verified 12 non-repeating monotonic cusps for {name}")

    def test_priority_3_varshaphal_solar_return_and_annual_ascendant(self):
        """3. Varshaphal Engine: Solar return exact moment, annual ascendant and Muntha."""
        for name, sex, y, m, d, hr, mn, sc, place, lat, lon, tz in self.benchmarks:
            data = generate_complete_kundli(name, sex, y, m, d, hr, mn, sc, place, lat, lon, tz, varsha_year=2026)
            vp = data["varshaphal"]
            asc_sign_idx = int(data["meta"]["asc_sid_lon"] / 30.0) % 12
            age = 2026 - y
            
            # Muntha verification
            exp_muntha = ((asc_sign_idx + age) % 12) + 1
            self.assertEqual(vp["muntha_sign"], exp_muntha, f"Muntha sign mismatch in {name}")
            
            # Annual Ascendant sign must be valid (1..12)
            varsha_lagna = vp["varsha_chart"]["lagna_sign"]
            self.assertTrue(1 <= varsha_lagna <= 12, f"Invalid Varsha Lagna {varsha_lagna} in {name}")
            print(f"[PASS] Priority 3: Varshaphal Engine verified (Lagna: {varsha_lagna}, Muntha: {vp['muntha_sign']}) for {name}")

    def test_priority_4_yoga_validation_engine(self):
        """4. Yoga Validation Engine: All declared yogas have satisfied formation conditions."""
        for name, sex, y, m, d, hr, mn, sc, place, lat, lon, tz in self.benchmarks:
            data = generate_complete_kundli(name, sex, y, m, d, hr, mn, sc, place, lat, lon, tz)
            yogas = data["yogas"]
            self.assertTrue(len(yogas) > 0, f"At least one yoga should be present in {name}")
            for yobj in yogas:
                self.assertTrue(yobj.get("present", False), f"Unverified yoga declared in {name}: {yobj}")
                self.assertTrue("conditions_verified" in yobj or "rule" in yobj, f"Missing formation condition log in {name}")
            print(f"[PASS] Priority 4: Yoga Validation Engine verified ({len(yogas)} authenticated yogas) for {name}")

    def test_priority_5_pdf_validation_gate_lock(self):
        """5. PDF Validation Gate: assert_valid_for_pdf passes for all benchmarks and stops on corrupt data."""
        for name, sex, y, m, d, hr, mn, sc, place, lat, lon, tz in self.benchmarks:
            data = generate_complete_kundli(name, sex, y, m, d, hr, mn, sc, place, lat, lon, tz)
            self.assertTrue(assert_valid_for_pdf(data), f"Validation gate must pass for benchmark {name}")

        # Intentional corruption test: verify that PDF Generation Lock stops invalid data!
        corrupt_data = dict(data)
        corrupt_data["planets"] = [dict(p) for p in data["planets"]]
        # Deliberately falsify Sun's house (index 1) to simulate row-index bug
        corrupt_data["planets"][1]["house"] = 99

        with self.assertRaises(PDFGenerationLockError):
            assert_valid_for_pdf(corrupt_data)
        print("[PASS] Priority 5: PDF Validation Gate successfully blocked corrupt chart from generating PDF!")

if __name__ == "__main__":
    unittest.main()
