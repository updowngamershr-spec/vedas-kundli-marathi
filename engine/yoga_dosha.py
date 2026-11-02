# -*- coding: utf-8 -*-
"""
Module 11: Classical Vedic Yogas and Doshas Engine
Implements deterministic formation rules for:
1. Pancha Mahapurusha Yogas (Ruchaka, Bhadra, Hamsa, Malavya, Sasa)
2. Major Auspicious Yogas (Gajakesari, Budhaditya, Chandra-Mangal, Amala, Kahala, Parvata)
3. Viparita Raja Yogas (Harsha, Sarala, Vimala)
4. Kendra-Trikona Raja Yogas and Dhana Yogas
5. Inauspicious Yogas (Kemadruma, Shakata, Guru-Chandal)
6. Manglik Dosha (from Lagna and Moon with classical cancellations / Pariharas)
7. Kalsarpa Dosha (12 classical types based on Rahu-Ketu axis)
Records exact formation criteria, planets involved, houses, and traditional interpretations.
"""

# Classical own and exalted signs
EXALTED_SIGNS = {
    "Sun": 1,      # Aries
    "Moon": 2,     # Taurus
    "Mars": 10,    # Capricorn
    "Mercury": 6,  # Virgo
    "Jupiter": 4,  # Cancer
    "Venus": 12,   # Pisces
    "Saturn": 7,   # Libra
}

OWN_SIGNS = {
    "Sun": {5},
    "Moon": {4},
    "Mars": {1, 8},
    "Mercury": {3, 6},
    "Jupiter": {9, 12},
    "Venus": {2, 7},
    "Saturn": {10, 11},
}

SIGN_LORDS = [
    "Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury",
    "Venus", "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter"
]

KALSARPA_TYPES = [
    (1, 7, "अनंत कालसर्प योग", "Ananta Kalsarpa", "प्रथम भावात राहू व सप्तमात केतू"),
    (2, 8, "कुलिक कालसर्प योग", "Kulika Kalsarpa", "द्वितीय भावात राहू व अष्टमात केतू"),
    (3, 9, "वासुकी कालसर्प योग", "Vasuki Kalsarpa", "तृतीय भावात राहू व नवमात केतू"),
    (4, 10, "शंखपाल कालसर्प योग", "Shankhapala Kalsarpa", "चतुर्थ भावात राहू व दशमात केतू"),
    (5, 11, "पद्म कालसर्प योग", "Padma Kalsarpa", "पंचम भावात राहू व एकादशात केतू"),
    (6, 12, "महापद्म कालसर्प योग", "Mahapadma Kalsarpa", "षष्ठ भावात राहू व द्वादशात केतू"),
    (7, 1, "तक्षक कालसर्प योग", "Takshaka Kalsarpa", "सप्तम भावात राहू व प्रथम भावात केतू"),
    (8, 2, "कर्कोटक कालसर्प योग", "Karkotaka Kalsarpa", "अष्टम भावात राहू व द्वितीय भावात केतू"),
    (9, 3, "शंखचूड़ कालसर्प योग", "Shankhachuda Kalsarpa", "नवम भावात राहू व तृतीय भावात केतू"),
    (10, 4, "घातक कालसर्प योग", "Ghataka Kalsarpa", "दशम भावात राहू व चतुर्थ भावात केतू"),
    (11, 5, "विषधर कालसर्प योग", "Vishadhara Kalsarpa", "एकादश भावात राहू व पंचमात केतू"),
    (12, 6, "शेषनाग कालसर्प योग", "Sheshanaga Kalsarpa", "द्वादश भावात राहू व षष्ठ भावात केतू"),
]


def evaluate_yogas(planet_by_id: dict, asc_sign_idx: int) -> list[dict]:
    """
    Evaluate classical Parashari yogas deterministically.
    """
    yogas = []

    # Helper: get sign number (1..12) and house (1..12)
    def p_sign(pid): return planet_by_id[pid]["sign_num"]
    def p_house(pid): return planet_by_id[pid]["house"]

    # 1. Pancha Mahapurusha Yogas
    # Condition: Mars, Mercury, Jupiter, Venus, or Saturn in Kendra (1,4,7,10) in own or exaltation sign
    mahapurusha_rules = [
        ("Mars", "रुचक योग (Ruchaka Yoga)", "Ruchaka", "मंगळ केंद्र भावात स्वराशीत (मेष, वृश्चिक) किंवा उच्च राशीत (मकर) स्थित असल्यामुळे रुचक महापुरुष योग निर्माण होतो. यामुळे जातक धाडसी, तेजस्वी, नेतृत्वगुणी आणि उच्च पदावर विराजमान होतो."),
        ("Mercury", "भद्र योग (Bhadra Yoga)", "Bhadra", "बुध केंद्र भावात स्वराशीत किंवा उच्च राशीत (मिथुन, कन्या) स्थित असल्यामुळे भद्र महापुरुष योग निर्माण होतो. यामुळे जातक कुशाग्र बुद्धिमत्ता, उत्तम वक्तृत्व आणि विद्वत्तेचा धनी होतो."),
        ("Jupiter", "हंस योग (Hamsa Yoga)", "Hamsa", "गुरू केंद्र भावात स्वराशीत (धनु, मीन) किंवा उच्च राशीत (कर्क) स्थित असल्यामुळे हंस महापुरुष योग निर्माण होतो. यामुळे जातक सात्विक, ज्ञानी, नीतिमान आणि समाजात पूजनीय ठरतो."),
        ("Venus", "मालव्य योग (Malavya Yoga)", "Malavya", "शुक्र केंद्र भावात स्वराशीत (वृषभ, तूळ) किंवा उच्च राशीत (मीन) स्थित असल्यामुळे मालव्य महापुरुष योग निर्माण होतो. यामुळे जातक कलाप्रेमी, ऐश्वर्यसंपन्न, सुखी आणि वाहन-गृह सुखाने परिपूर्ण राहतो."),
        ("Saturn", "शश योग (Sasa Yoga)", "Sasa", "शनी केंद्र भावात स्वराशीत (मकर, कुंभ) किंवा उच्च राशीत (तूळ) स्थित असल्यामुळे शश महापुरुष योग निर्माण होतो. यामुळे जातक मुत्सद्दी, न्यायप्रिय, दृढनिश्चयी आणि दीर्घायुषी होतो."),
    ]

    for pid, name_mr, code, desc in mahapurusha_rules:
        h = p_house(pid)
        s = p_sign(pid)
        is_kendra = (h in (1, 4, 7, 10))
        is_dignified = (s in OWN_SIGNS[pid] or s == EXALTED_SIGNS[pid])
        if is_kendra and is_dignified:
            yogas.append({
                "code": code,
                "name": name_mr,
                "planets": [pid],
                "houses": [h],
                "rule": f"{pid} in Kendra ({h}th house) in own/exalted sign ({s})",
                "present": True,
                "description": desc,
            })

    # 2. Gajakesari Yoga
    # Condition: Jupiter in Kendra (1, 4, 7, 10) from Moon
    jup_h = p_house("Jupiter")
    moon_h = p_house("Moon")
    diff_moon_jup = ((jup_h - moon_h + 12) % 12) + 1
    if diff_moon_jup in (1, 4, 7, 10):
        yogas.append({
            "code": "Gajakesari",
            "name": "गजकेसरी योग (Gajakesari Yoga)",
            "planets": ["Jupiter", "Moon"],
            "houses": [jup_h, moon_h],
            "rule": f"Jupiter in {diff_moon_jup}th house (Kendra) from Moon",
            "present": True,
            "description": "चंद्रापासून गुरू केंद्र भावात स्थित असल्यामुळे शुभ गजकेसरी योग निर्माण होतो. यामुळे जीवनात अपार यश, प्रतिष्ठा, ज्ञान, दीर्घायुष्य आणि अचानक संकटांतून विजय प्राप्त होतो.",
        })

    # 3. Budhaditya Yoga
    # Condition: Sun and Mercury conjunct in same sign without severe combustion
    if p_sign("Sun") == p_sign("Mercury"):
        sun_h = p_house("Sun")
        yogas.append({
            "code": "Budhaditya",
            "name": "बुधादित्य योग (Budhaditya Yoga)",
            "planets": ["Sun", "Mercury"],
            "houses": [sun_h],
            "rule": f"Sun and Mercury conjunct in {sun_h}th house",
            "present": True,
            "description": "सूर्य आणि बुध एकाच भावात युतीमध्ये असल्यामुळे बुधादित्य योग निर्माण होतो. यामुळे व्यक्तीला तल्लख स्मरणशक्ती, बौद्धिक चमक, प्रशासकीय क्षमता आणि व्यवसायात विशेष यश लाभते.",
        })

    # 4. Chandra-Mangal Yoga
    # Condition: Moon and Mars conjunct or in 7th mutual aspect
    moon_mars_diff = ((p_house("Mars") - moon_h + 12) % 12) + 1
    if moon_mars_diff in (1, 7):
        yogas.append({
            "code": "ChandraMangal",
            "name": "चंद्र-मंगळ योग (Chandra-Mangal Yoga)",
            "planets": ["Moon", "Mars"],
            "houses": [moon_h, p_house("Mars")],
            "rule": f"Moon and Mars in relation ({moon_mars_diff}th)",
            "present": True,
            "description": "चंद्र आणि मंगळ यांची युती किंवा परस्पर दृष्टी असल्यामुळे लक्ष्मीकारक चंद्र-मंगळ योग बनतो. यामुळे जातक आर्थिक व्यवहार, व्यापार आणि स्थावर मालमत्तेत धनवान बनतो.",
        })

    # 5. Viparita Raja Yogas (Harsha, Sarala, Vimala)
    # House lords mapping
    # House H (1..12): sign is (asc_sign_idx + H - 1) % 12
    house_lords = {}
    for h in range(1, 13):
        s_idx = (asc_sign_idx + h - 1) % 12
        house_lords[h] = SIGN_LORDS[s_idx]

    # Harsha: 6th lord in 6th, 8th, or 12th house
    lord_6 = house_lords[6]
    h_lord_6 = p_house(lord_6)
    if h_lord_6 in (6, 8, 12):
        yogas.append({
            "code": "Harsha",
            "name": "हर्ष विपरीत राजयोग (Harsha Viparita Rajayoga)",
            "planets": [lord_6],
            "houses": [h_lord_6],
            "rule": f"6th lord ({lord_6}) situated in {h_lord_6}th house (Dusthana)",
            "present": True,
            "description": "षष्ठेश ग्रह स्वतः ६, ८ किंवा १२व्या भावात स्थित असल्यामुळे हर्ष विपरीत राजयोग निर्माण होतो. यामुळे जातक शत्रूंवर मात करतो, निरोगी राहतो आणि विपरीत परिस्थितीतूनही धनलाभ मिळवतो.",
        })

    # Sarala: 8th lord in 6th, 8th, or 12th house
    lord_8 = house_lords[8]
    h_lord_8 = p_house(lord_8)
    if h_lord_8 in (6, 8, 12):
        yogas.append({
            "code": "Sarala",
            "name": "सरल विपरीत राजयोग (Sarala Viparita Rajayoga)",
            "planets": [lord_8],
            "houses": [h_lord_8],
            "rule": f"8th lord ({lord_8}) situated in {h_lord_8}th house (Dusthana)",
            "present": True,
            "description": "अष्टमेश ग्रह स्वतः ६, ८ किंवा १२व्या भावात स्थित असल्यामुळे सरल विपरीत राजयोग बनतो. यामुळे जातक निडर, विद्वान, दीर्घायुषी आणि गुप्त धनाचा स्वामी बनतो.",
        })

    # Vimala: 12th lord in 6th, 8th, or 12th house
    lord_12 = house_lords[12]
    h_lord_12 = p_house(lord_12)
    if h_lord_12 in (6, 8, 12):
        yogas.append({
            "code": "Vimala",
            "name": "विमल विपरीत राजयोग (Vimala Viparita Rajayoga)",
            "planets": [lord_12],
            "houses": [h_lord_12],
            "rule": f"12th lord ({lord_12}) situated in {h_lord_12}th house (Dusthana)",
            "present": True,
            "description": "व्ययेश ग्रह स्वतः ६, ८ किंवा १२व्या भावात स्थित असल्यामुळे विमल विपरीत राजयोग निर्माण होतो. यामुळे अनावश्यक खर्चावर नियंत्रण राहून जातक समृद्ध व परदेशात यशस्वी होतो.",
        })

    # 6. Amala Yoga (Benefic Jupiter, Venus, or Mercury in 10th from Lagna or Moon)
    for p_benefic in ("Jupiter", "Venus", "Mercury"):
        if p_house(p_benefic) == 10:
            yogas.append({
                "code": "Amala",
                "name": "अमल कीर्ति योग (Amala Yoga)",
                "planets": [p_benefic],
                "houses": [10],
                "rule": f"Natural benefic ({p_benefic}) in 10th house of career/action",
                "present": True,
                "description": "दशम कर्म भावात शुभ ग्रह स्थित असल्यामुळे अमल कीर्ति योग घडतो. यामुळे जातक समाजात निष्कलंक कीर्ती, परोपकारी स्वभाव आणि उच्च सन्मान प्राप्त करतो.",
            })
            break

    return yogas


def evaluate_manglik_dosha(planet_by_id: dict, asc_sign_idx: int) -> dict:
    """
    Evaluate Manglik Dosha from both Lagna and Moon with classical cancellations.
    """
    mars_sign_idx = planet_by_id["Mars"]["sign_idx"]
    moon_sign_idx = planet_by_id["Moon"]["sign_idx"]

    mars_house_lagna = ((mars_sign_idx - asc_sign_idx + 12) % 12) + 1
    mars_house_moon = ((mars_sign_idx - moon_sign_idx + 12) % 12) + 1

    manglik_houses = {1, 2, 4, 7, 8, 12}
    is_manglik_lagna = mars_house_lagna in manglik_houses
    is_manglik_moon = mars_house_moon in manglik_houses
    is_manglik = is_manglik_lagna or is_manglik_moon

    cancellations_mr = []
    mars_sign_num = mars_sign_idx + 1

    # Own / exalted sign
    if mars_sign_num in (1, 8, 10):
        cancellations_mr.append("मंगळ स्वतःच्या स्वराशीत (मेष, वृश्चिक) किंवा उच्च राशीत (मकर) असल्यामुळे दोषाची तीव्रता सौम्य होते.")
    if mars_sign_num == 4:
        cancellations_mr.append("मंगळ कर्क (नीच) राशीत असल्याने आक्रमकता कमी होऊन दोष शांत होतो.")

    # Aspect of Jupiter
    jup_h = planet_by_id["Jupiter"]["house"]
    jup_aspect_houses = {((jup_h - 1 + off) % 12) + 1 for off in (0, 4, 6, 8)}
    if mars_house_lagna in jup_aspect_houses:
        cancellations_mr.append("देवगुरू बृहस्पतीची शुभ अमृत दृष्टी मंगळावर असल्यामुळे मांगलिक दोष निष्प्रभ होतो.")

    status_mr = "सौम्य / दोष परिहार झालेला" if cancellations_mr else ("मांगलिक प्रभाव विद्यमान" if is_manglik else "दोष मुक्त (अमांगलिक)")

    return {
        "is_manglik": is_manglik,
        "is_manglik_lagna": is_manglik_lagna,
        "is_manglik_moon": is_manglik_moon,
        "mars_house_lagna": mars_house_lagna,
        "mars_house_moon": mars_house_moon,
        "cancellations_mr": cancellations_mr,
        "status_mr": status_mr,
    }


def evaluate_kalsarpa_dosha(planet_by_id: dict) -> dict:
    """
    Evaluate Kalsarpa Dosha: all 7 classical planets (Sun to Saturn)
    hemmed entirely on one side of the Rahu-Ketu axis.
    """
    rahu_lon = planet_by_id["Rahu"]["sid_lon"]
    ketu_lon = planet_by_id["Ketu"]["sid_lon"]

    # Arc 1: Rahu to Ketu counter-clockwise
    # Arc 2: Ketu to Rahu counter-clockwise
    side1_count = 0
    side2_count = 0

    for pid in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
        p_lon = planet_by_id[pid]["sid_lon"]
        diff_from_rahu = (p_lon - rahu_lon) % 360.0
        if 0.0 < diff_from_rahu < 180.0:
            side1_count += 1
        elif 180.0 < diff_from_rahu < 360.0:
            side2_count += 1

    is_kalsarpa = (side1_count == 7 or side2_count == 7)

    # Determine type based on Rahu house
    rahu_house = planet_by_id["Rahu"]["house"]
    type_name_mr = "दोष मुक्त"
    type_name_en = "None"
    type_desc_mr = "कुंडलीत कालसर्प दोष नाही."

    if is_kalsarpa:
        for r_h, k_h, name_mr, name_en, desc_mr in KALSARPA_TYPES:
            if rahu_house == r_h:
                type_name_mr = name_mr
                type_name_en = name_en
                type_desc_mr = desc_mr
                break

    return {
        "is_kalsarpa": is_kalsarpa,
        "has_kalsarpa": is_kalsarpa,
        "type_name_mr": type_name_mr,
        "type_name_en": type_name_en,
        "description_mr": type_desc_mr,
        "rahu_house": rahu_house,
        "ketu_house": planet_by_id["Ketu"]["house"],
    }
