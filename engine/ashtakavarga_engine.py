# -*- coding: utf-8 -*-
"""
Module 9: Ashtakavarga Engine
Implements Parashari Bhinnashtakavarga rules for all 7 classical planets
from 8 reference points (Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Lagna).
Mathematical Invariants Verified:
- Sun Bhinnashtakavarga = 48 bindus
- Moon Bhinnashtakavarga = 49 bindus
- Mars Bhinnashtakavarga = 39 bindus
- Mercury Bhinnashtakavarga = 54 bindus
- Jupiter Bhinnashtakavarga = 56 bindus
- Venus Bhinnashtakavarga = 52 bindus
- Saturn Bhinnashtakavarga = 39 bindus
- Sarvashtakavarga Total = 337 bindus (STRICT MATHEMATICAL INVARIANT)
Zero artificial adjustments.
"""

# Classical Parashari Bindu Allocations (Houses 1-12 from contributor)
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

CONTRIBUTORS = [
    ("Su", "Sun", "रवि"),
    ("Mo", "Moon", "चन्द्र"),
    ("Ma", "Mars", "मंगळ"),
    ("Me", "Mercury", "बुध"),
    ("Ju", "Jupiter", "गुरू"),
    ("Ve", "Venus", "शुक्र"),
    ("Sa", "Saturn", "शनी"),
    ("As", "Asc", "लग्न"),
]

EXPECTED_TOTALS = {
    "Sun": 48,
    "Moon": 49,
    "Mars": 39,
    "Mercury": 54,
    "Jupiter": 56,
    "Venus": 52,
    "Saturn": 39,
}


def calculate_ashtakavarga(planet_by_id: dict, asc_sign_idx: int) -> dict:
    """
    Calculate 7 individual Bhinnashtakavargas and Sarvashtakavarga.
    Strictly verifies traditional invariant totals.
    """
    contributor_signs = {
        "Su": planet_by_id["Sun"]["sign_idx"],
        "Mo": planet_by_id["Moon"]["sign_idx"],
        "Ma": planet_by_id["Mars"]["sign_idx"],
        "Me": planet_by_id["Mercury"]["sign_idx"],
        "Ju": planet_by_id["Jupiter"]["sign_idx"],
        "Ve": planet_by_id["Venus"]["sign_idx"],
        "Sa": planet_by_id["Saturn"]["sign_idx"],
        "As": asc_sign_idx,
    }

    prasthara_tables = {}
    bhinna_tables = {}
    bhinna_totals = {}
    sarvashtakavarga_signs = [0] * 12
    validation_status = {}

    for pid in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
        rules = ASHTAKAVARGA_RULES[pid]
        p_rows = []
        col_totals = [0] * 12

        for c_code, c_id, c_name_mr in CONTRIBUTORS:
            c_sign = contributor_signs[c_code]
            row_vals = [0] * 12
            for offset in rules[c_code]:
                target_sign = (c_sign + offset - 1) % 12
                row_vals[target_sign] = 1
                col_totals[target_sign] += 1

            p_rows.append({
                "code": c_code,
                "contributor_en": c_id,
                "contributor_mr": c_name_mr,
                "values": row_vals,
                "total": sum(row_vals),
            })

        actual_total = sum(col_totals)
        expected_total = EXPECTED_TOTALS[pid]
        passed = (actual_total == expected_total)

        validation_status[pid] = {
            "expected": expected_total,
            "actual": actual_total,
            "pass": passed,
        }

        prasthara_tables[pid] = {
            "planet": pid,
            "rows": p_rows,
            "totals": col_totals,
            "grand_total": actual_total,
        }
        bhinna_tables[pid] = col_totals
        bhinna_totals[pid] = actual_total

        # Accumulate to Sarvashtakavarga
        for s in range(12):
            sarvashtakavarga_signs[s] += col_totals[s]

    total_sarva = sum(sarvashtakavarga_signs)
    sarva_passed = (total_sarva == 337)
    validation_status["Sarvashtakavarga"] = {
        "expected": 337,
        "actual": total_sarva,
        "pass": sarva_passed,
    }

    # Map sign-wise Sarvashtakavarga to 12 Houses relative to Lagna
    sarvashtakavarga_houses = [0] * 12
    for h in range(12):
        s_idx = (asc_sign_idx + h) % 12
        sarvashtakavarga_houses[h] = sarvashtakavarga_signs[s_idx]

    return {
        "bhinna_tables": bhinna_tables,
        "bhinna_totals": bhinna_totals,
        "sarvashtakavarga_signs": sarvashtakavarga_signs,
        "sarvashtakavarga_houses": sarvashtakavarga_houses,
        "total_bindus": total_sarva,
        "sarvashtakavarga_total": total_sarva,
        "prasthara_tables": prasthara_tables,
        "validation": validation_status,
        "is_valid": sarva_passed and all(v["pass"] for v in validation_status.values()),
    }
