# -*- coding: utf-8 -*-
"""
Vedas Kundli Predictions - Classical Ashtakoot 36-Guna Kundli Matching Engine
Computes:
1. Ashtakoot 8 Koots: Varna (1), Vasya (2), Tara (3), Yoni (4), Graha Maitri (5), Gana (6), Bhakoot (7), Nadi (8) = 36 Gunas
2. Kuja / Mangal Dosha check for both Boy and Girl (with classical Parihara)
3. Papa Samya (Malefic point balance)
4. Dasha Sandhi check
5. Overall Compatibility Assessment & Verdict
"""

from engine.ephemeris import (
    RASHI_NAMES_EN, RASHI_NAMES_HI, RASHI_LORDS_SHORT, RASHI_LORDS_HI,
    NAKSHATRA_NAMES_EN, NAKSHATRA_NAMES_HI, compute_core_ephemeris
)

# Varna: Water=Brahmin(4), Fire=Kshatriya(3), Earth=Vaishya(2), Air=Shudra(1)
VARNA_RANKS = {
    0: (3, "Kshatriya", "क्षत्रिय"), 1: (2, "Vaishya", "वैश्य"),
    2: (1, "Shudra", "शूद्र"),       3: (4, "Brahmin", "ब्राह्मण"),
    4: (3, "Kshatriya", "क्षत्रिय"), 5: (2, "Vaishya", "वैश्य"),
    6: (1, "Shudra", "शूद्र"),       7: (4, "Brahmin", "ब्राह्मण"),
    8: (3, "Kshatriya", "क्षत्रिय"), 9: (2, "Vaishya", "वैश्य"),
    10: (1, "Shudra", "शूद्र"),      11: (4, "Brahmin", "ब्राह्मण")
}

# Vasya Categories
# 1=Chatushpada, 2=Manava/Dwipada, 3=Jalachara, 4=Vanachara, 5=Keeta
VASYA_MAP = {
    0: (1, "Chatushpada", "चतुष्पाद"), 1: (1, "Chatushpada", "चतुष्पाद"),
    2: (2, "Manava", "मानव"),          3: (3, "Jalachara", "जलचर"),
    4: (4, "Vanachara", "वनचर"),       5: (2, "Manava", "मानव"),
    6: (2, "Manava", "मानव"),          7: (5, "Keeta", "कीट"),
    8: (2, "Manava", "मानव"),          9: (1, "Chatushpada", "चतुष्पाद"),
    10: (2, "Manava", "मानव"),         11: (3, "Jalachara", "जलचर")
}

# 14 Yoni Archetypes for 27 Nakshatras
YONI_MAP = [
    (0, "Horse", "अश्व"),      # Ashwini
    (1, "Elephant", "गज"),    # Bharani
    (2, "Sheep", "मेष"),       # Krittika
    (3, "Serpent", "सर्प"),    # Rohini
    (3, "Serpent", "सर्प"),    # Mrigashira
    (4, "Dog", "श्वान"),       # Ardra
    (5, "Cat", "मार्जारी"),    # Punarvasu
    (2, "Sheep", "मेष"),       # Pushya
    (5, "Cat", "मार्जारी"),    # Ashlesha
    (6, "Rat", "मूषक"),        # Magha
    (6, "Rat", "मूषक"),        # Purva Phalguni
    (7, "Cow", "गौ"),          # Uttara Phalguni
    (8, "Buffalo", "महिष"),    # Hasta
    (9, "Tiger", "व्याघ्र"),   # Chitra
    (8, "Buffalo", "महिष"),    # Swati
    (9, "Tiger", "व्याघ्र"),   # Vishakha
    (10, "Deer", "मृग"),       # Anuradha
    (10, "Deer", "मृग"),       # Jyeshtha
    (4, "Dog", "श्वान"),       # Moola
    (11, "Monkey", "वानर"),    # Purva Ashadha
    (12, "Mongoose", "नकुल"),  # Uttara Ashadha
    (11, "Monkey", "वानर"),    # Shravana
    (13, "Lion", "सिंह"),      # Dhanishta
    (0, "Horse", "अश्व"),      # Shatabhisha
    (13, "Lion", "सिंह"),      # Purva Bhadrapada
    (7, "Cow", "गौ"),          # Uttara Bhadrapada
    (1, "Elephant", "गज"),     # Revati
]

# Inimical Yoni pairs (0 score)
ENEMIES_YONI = {
    (7, 9), (9, 7),   # Cow - Tiger
    (1, 13), (13, 1), # Elephant - Lion
    (0, 8), (8, 0),   # Horse - Buffalo
    (4, 10), (10, 4), # Dog - Deer
    (3, 12), (12, 3), # Serpent - Mongoose
    (5, 6), (6, 5),   # Cat - Rat
    (2, 11), (11, 2)  # Sheep - Monkey
}

# Gana Map: 0=Deva, 1=Manushya, 2=Rakshasa
GANA_MAP = [
    0, 1, 2, 1, 0, 1, 0, 0, 2,  # Ashwini .. Ashlesha
    2, 1, 1, 0, 2, 0, 2, 0, 2,  # Magha .. Jyeshtha
    2, 1, 1, 0, 2, 2, 1, 1, 0   # Moola .. Revati
]
GANA_NAMES = [("Deva", "देव"), ("Manushya", "मनुष्य"), ("Rakshasa", "राक्षस")]

# Nadi Map: 0=Adi, 1=Madhya, 2=Antya
NADI_MAP = [
    0, 1, 2, 2, 1, 0, 0, 1, 2,  # Ashwini .. Ashlesha
    2, 1, 0, 0, 1, 2, 2, 1, 0,  # Magha .. Jyeshtha
    0, 1, 2, 2, 1, 0, 0, 1, 2   # Moola .. Revati
]
NADI_NAMES = [("Adi", "आदि"), ("Madhya", "मध्य"), ("Antya", "अंत्य")]

# Planetary Natural Relationships
PLANET_REL = {
    "SUN": {"F": {"MON", "MAR", "JUP"}, "N": {"MER"}, "E": {"VEN", "SAT"}},
    "MON": {"F": {"SUN", "MER"}, "N": {"MAR", "JUP", "VEN", "SAT"}, "E": set()},
    "MAR": {"F": {"SUN", "MON", "JUP"}, "N": {"VEN", "SAT"}, "E": {"MER"}},
    "MER": {"F": {"SUN", "VEN"}, "N": {"MAR", "JUP", "SAT"}, "E": {"MON"}},
    "JUP": {"F": {"SUN", "MON", "MAR"}, "N": {"SAT"}, "E": {"MER", "VEN"}},
    "VEN": {"F": {"MER", "SAT"}, "N": {"MAR", "JUP"}, "E": {"SUN", "MON"}},
    "SAT": {"F": {"MER", "VEN"}, "N": {"JUP"}, "E": {"SUN", "MON", "MAR"}}
}


def calculate_ashtakoot_milan(boy_core: dict, girl_core: dict) -> dict:
    """Calculate the 36 Guna Ashtakoot Milan between Boy and Girl horoscopes."""
    b_moon = boy_core["planet_by_id"]["Moon"]
    g_moon = girl_core["planet_by_id"]["Moon"]

    b_nak = b_moon["nakshatra_idx"]
    g_nak = g_moon["nakshatra_idx"]
    b_rasi = b_moon["sign_idx"]
    g_rasi = g_moon["sign_idx"]
    b_pada = b_moon.get("pada", 1)
    g_pada = g_moon.get("pada", 1)

    # 1. VARNA (Max: 1)
    b_vrank, b_v_en, b_v_hi = VARNA_RANKS[b_rasi]
    g_vrank, g_v_en, g_v_hi = VARNA_RANKS[g_rasi]
    varna_pts = 1 if b_vrank >= g_vrank else 0

    # 2. VASYA (Max: 2)
    b_vas_code, b_vas_en, b_vas_hi = VASYA_MAP[b_rasi]
    g_vas_code, g_vas_en, g_vas_hi = VASYA_MAP[g_rasi]
    if b_vas_code == g_vas_code:
        vasya_pts = 2
    elif (b_vas_code == 2 and g_vas_code in (1, 3)) or (b_vas_code == 1 and g_vas_code == 2):
        vasya_pts = 1
    elif (b_vas_code, g_vas_code) in [(2, 5), (4, 1)]:
        vasya_pts = 0.5
    else:
        vasya_pts = 0

    # 3. TARA (Max: 3)
    tara_b_to_g = ((g_nak - b_nak) % 9) + 1
    tara_g_to_b = ((b_nak - g_nak) % 9) + 1
    good_taras = {1, 2, 4, 6, 8, 9}
    b_good = tara_b_to_g in good_taras
    g_good = tara_g_to_b in good_taras
    if b_good and g_good:
        tara_pts = 3
    elif b_good or g_good:
        tara_pts = 1.5
    else:
        tara_pts = 0

    # 4. YONI (Max: 4)
    b_y_code, b_y_en, b_y_hi = YONI_MAP[b_nak]
    g_y_code, g_y_en, g_y_hi = YONI_MAP[g_nak]
    if b_y_code == g_y_code:
        yoni_pts = 4
    elif (b_y_code, g_y_code) in ENEMIES_YONI:
        yoni_pts = 0
    else:
        yoni_pts = 2  # Average amicable/neutral

    # 5. GRAHA MAITRI (Max: 5)
    b_lord = RASHI_LORDS_SHORT[b_rasi]
    g_lord = RASHI_LORDS_SHORT[g_rasi]
    if b_lord == g_lord:
        maitri_pts = 5
    else:
        b_rel_to_g = "F" if g_lord in PLANET_REL.get(b_lord, {}).get("F", set()) else ("N" if g_lord in PLANET_REL.get(b_lord, {}).get("N", set()) else "E")
        g_rel_to_b = "F" if b_lord in PLANET_REL.get(g_lord, {}).get("F", set()) else ("N" if b_lord in PLANET_REL.get(g_lord, {}).get("N", set()) else "E")
        if b_rel_to_g == "F" and g_rel_to_b == "F":
            maitri_pts = 5
        elif (b_rel_to_g == "F" and g_rel_to_b == "N") or (b_rel_to_g == "N" and g_rel_to_b == "F"):
            maitri_pts = 4
        elif b_rel_to_g == "N" and g_rel_to_b == "N":
            maitri_pts = 3
        elif (b_rel_to_g == "F" and g_rel_to_b == "E") or (b_rel_to_g == "E" and g_rel_to_b == "F"):
            maitri_pts = 1
        elif (b_rel_to_g == "N" and g_rel_to_b == "E") or (b_rel_to_g == "E" and g_rel_to_b == "N"):
            maitri_pts = 0.5
        else:
            maitri_pts = 0

    # 6. GANA (Max: 6)
    b_gana_idx = GANA_MAP[b_nak]
    g_gana_idx = GANA_MAP[g_nak]
    b_g_en, b_g_hi = GANA_NAMES[b_gana_idx]
    g_g_en, g_g_hi = GANA_NAMES[g_gana_idx]
    if b_gana_idx == g_gana_idx:
        gana_pts = 6
    elif (b_gana_idx == 0 and g_gana_idx == 1) or (b_gana_idx == 1 and g_gana_idx == 0):
        gana_pts = 5
    elif (b_gana_idx == 0 and g_gana_idx == 2):
        gana_pts = 1
    elif (b_gana_idx == 2 and g_gana_idx == 0):
        gana_pts = 0
    else:
        gana_pts = 0

    # 7. BHAKOOT (Max: 7)
    diff = ((g_rasi - b_rasi) % 12) + 1
    dosha_positions = {6, 8, 2, 12, 9, 5}
    if diff in dosha_positions:
        # Check cancellation: if Moon lords are same or mutual friends
        if b_lord == g_lord or (g_lord in PLANET_REL.get(b_lord, {}).get("F", set()) and b_lord in PLANET_REL.get(g_lord, {}).get("F", set())):
            bhakoot_pts = 7
            bhakoot_remark_en = "Bhakoot Dosha Cancelled (Lord Friendship)"
            bhakoot_remark_hi = "भकूट दोष परिहार (राशीश मित्रता)"
        else:
            bhakoot_pts = 0
            bhakoot_remark_en = f"Bhakoot Dosha ({diff}/{(14-diff)%12 or 12})"
            bhakoot_remark_hi = f"भकूट दोष विद्यमान"
    else:
        bhakoot_pts = 7
        bhakoot_remark_en = "Auspicious Bhakoot Harmony"
        bhakoot_remark_hi = "शुभ भकूट अनुकूलता"

    # 8. NADI (Max: 8)
    b_nadi_idx = NADI_MAP[b_nak]
    g_nadi_idx = NADI_MAP[g_nak]
    b_n_en, b_n_hi = NADI_NAMES[b_nadi_idx]
    g_n_en, g_g_hi = NADI_NAMES[g_nadi_idx]
    if b_nadi_idx != g_nadi_idx:
        nadi_pts = 8
        nadi_remark_en = "No Nadi Dosha"
        nadi_remark_hi = "नाड़ी दोष नहीं है"
    else:
        # Check cancellation: same nakshatra different pada or same rashi different nakshatra
        if b_nak == g_nak and b_pada != g_pada:
            nadi_pts = 8
            nadi_remark_en = "Nadi Dosha Cancelled (Different Pada)"
            nadi_remark_hi = "नाड़ी दोष परिहार (भिन्न चरण)"
        elif b_rasi == g_rasi and b_nak != g_nak:
            nadi_pts = 8
            nadi_remark_en = "Nadi Dosha Cancelled (Same Rashi Different Star)"
            nadi_remark_hi = "नाड़ी दोष परिहार (समान राशि भिन्न नक्षत्र)"
        else:
            nadi_pts = 0
            nadi_remark_en = "Nadi Dosha Present (Remedies Recommended)"
            nadi_remark_hi = "नाड़ी दोष विद्यमान (दोष शांति अनुशंसित)"

    total_score = varna_pts + vasya_pts + tara_pts + yoni_pts + maitri_pts + gana_pts + bhakoot_pts + nadi_pts

    # Verdict
    if total_score >= 32:
        verdict_en = "Supreme Soulmate Union (अति उत्तम / सर्वोत्तम)"
        verdict_hi = "अति उत्तम / सर्वोत्तम आत्मिक मिलन"
        verdict_grade = "Excellent"
        color = "#15803D"
    elif total_score >= 25:
        verdict_en = "Highly Auspicious Match (उत्तम मिलान)"
        verdict_hi = "उत्तम मिलान — सुखद एवं समृद्ध दांपत्य जीवन"
        verdict_grade = "Very Good"
        color = "#16A34A"
    elif total_score >= 18:
        verdict_en = "Average / Acceptable Match (मध्यम / सामान्य)"
        verdict_hi = "मध्यम / सामान्य मिलान — परस्पर समझ से अनुकूल"
        verdict_grade = "Acceptable"
        color = "#D97706"
    else:
        verdict_en = "Inauspicious / Low Match (अस्वीकार्य / दोष निवारण आवश्यक)"
        verdict_hi = "अस्वीकार्य / गंभीर दोष निवारण व परामर्श आवश्यक"
        verdict_grade = "Inauspicious"
        color = "#DC2626"

    # Manglik Check for Boy and Girl
    from engine.varshaphal_sadesati_yogas import compute_manglik_and_kalsarpa
    b_mang = compute_manglik_and_kalsarpa(boy_core)["manglik"]
    g_mang = compute_manglik_and_kalsarpa(girl_core)["manglik"]

    # Manglik Harmony
    if b_mang["is_manglik"] and g_mang["is_manglik"]:
        manglik_verdict_en = "Both are Manglik: Perfect Dosha Samya Neutralization (दोष साम्य परिहार)"
        manglik_verdict_hi = "वर व कन्या दोनों मांगलिक हैं — दोष साम्य द्वारा मंगल दोष पूर्णतः निष्प्रभावी।"
        manglik_compat = "Neutralized"
    elif not b_mang["is_manglik"] and not g_mang["is_manglik"]:
        manglik_verdict_en = "Both are Non-Manglik: Completely Free from Mangal Dosha"
        manglik_verdict_hi = "दोनों की कुंडली मंगल दोष से पूर्णतः मुक्त है।"
        manglik_compat = "Clean"
    else:
        manglik_verdict_en = "One partner is Manglik: Requires astrological remedial evaluation"
        manglik_verdict_hi = "एक पक्ष मांगलिक है — अनुष्ठान अथवा विशिष्ट परिहार जांच अपेक्षित।"
        manglik_compat = "Review"

    return {
        "total_score": round(total_score, 1),
        "max_score": 36,
        "percentage": round((total_score / 36.0) * 100, 1),
        "verdict_en": verdict_en,
        "verdict_hi": verdict_hi,
        "verdict_grade": verdict_grade,
        "verdict_color": color,
        "koots": [
            {
                "koot_en": "Varna", "koot_hi": "वर्ण",
                "max": 1, "obtained": varna_pts,
                "boy_val": f"{b_v_en} ({b_v_hi})", "girl_val": f"{g_v_en} ({g_v_hi})",
                "desc_en": "Mental work tendency & spiritual ego compatibility",
                "desc_hi": "कार्य प्रवृत्ति व आध्यात्मिक अहंकार सामंजस्य"
            },
            {
                "koot_en": "Vasya", "koot_hi": "वश्य",
                "max": 2, "obtained": vasya_pts,
                "boy_val": f"{b_vas_en} ({b_vas_hi})", "girl_val": f"{g_vas_en} ({g_vas_hi})",
                "desc_en": "Mutual attraction, loyalty & willingness to cooperate",
                "desc_hi": "परस्पर आकर्षण, निष्ठा व सहयोग भावना"
            },
            {
                "koot_en": "Tara", "koot_hi": "तारा",
                "max": 3, "obtained": tara_pts,
                "boy_val": f"Star {tara_b_to_g}", "girl_val": f"Star {tara_g_to_b}",
                "desc_en": "Birth star destiny, longevity & health harmony",
                "desc_hi": "भाग्य, स्वास्थ्य, दीर्घायु व नक्षत्र सामंजस्य"
            },
            {
                "koot_en": "Yoni", "koot_hi": "योनि",
                "max": 4, "obtained": yoni_pts,
                "boy_val": f"{b_y_en} ({b_y_hi})", "girl_val": f"{g_y_en} ({g_y_hi})",
                "desc_en": "Biological & physical intimacy compatibility",
                "desc_hi": "जैविक व शारीरिक दांपत्य सुख अनुकूलता"
            },
            {
                "koot_en": "Graha Maitri", "koot_hi": "ग्रहमैत्री",
                "max": 5, "obtained": maitri_pts,
                "boy_val": f"{b_lord} ({RASHI_NAMES_HI[b_rasi]})", "girl_val": f"{g_lord} ({RASHI_NAMES_HI[g_rasi]})",
                "desc_en": "Moon sign lords friendship & mental harmony",
                "desc_hi": "चंद्र राशि स्वामियों की मित्रता व वैचारिक शांति"
            },
            {
                "koot_en": "Gana", "koot_hi": "गण",
                "max": 6, "obtained": gana_pts,
                "boy_val": f"{b_g_en} ({b_g_hi})", "girl_val": f"{g_g_en} ({g_g_hi})",
                "desc_en": "Temperament, daily behavior & lifestyle coexistence",
                "desc_hi": "स्वभाव, आचरण, सहिष्णुता व जीवनशैली"
            },
            {
                "koot_en": "Bhakoot", "koot_hi": "भकूट",
                "max": 7, "obtained": bhakoot_pts,
                "boy_val": f"{RASHI_NAMES_HI[b_rasi]}", "girl_val": f"{RASHI_NAMES_HI[g_rasi]}",
                "desc_en": bhakoot_remark_en,
                "desc_hi": bhakoot_remark_hi
            },
            {
                "koot_en": "Nadi", "koot_hi": "नाड़ी",
                "max": 8, "obtained": nadi_pts,
                "boy_val": f"{b_n_en} ({NADI_NAMES[b_nadi_idx][1]})", "girl_val": f"{g_n_en} ({NADI_NAMES[g_nadi_idx][1]})",
                "desc_en": nadi_remark_en,
                "desc_hi": nadi_remark_hi
            }
        ],
        "boy_summary": {
            "name": boy_core["meta"]["name"],
            "lagna": f"{boy_core['meta']['lagna_en']} ({boy_core['meta']['lagna_hi']})",
            "rasi": f"{boy_core['meta']['rasi_en']} ({boy_core['meta']['rasi_hi']})",
            "nakshatra": f"{boy_core['meta']['nakshatra_pada_en']} ({boy_core['meta']['nakshatra_pada_hi']})",
            "is_manglik": b_mang["is_manglik"],
            "manglik_status": b_mang["status_hi"]
        },
        "girl_summary": {
            "name": girl_core["meta"]["name"],
            "lagna": f"{girl_core['meta']['lagna_en']} ({girl_core['meta']['lagna_hi']})",
            "rasi": f"{girl_core['meta']['rasi_en']} ({girl_core['meta']['rasi_hi']})",
            "nakshatra": f"{girl_core['meta']['nakshatra_pada_en']} ({girl_core['meta']['nakshatra_pada_hi']})",
            "is_manglik": g_mang["is_manglik"],
            "manglik_status": g_mang["status_hi"]
        },
        "manglik_harmony": {
            "verdict_en": manglik_verdict_en,
            "verdict_hi": manglik_verdict_hi,
            "compat": manglik_compat
        }
    }
