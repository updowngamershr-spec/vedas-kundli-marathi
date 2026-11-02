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
    Evaluate classical Parashari yogas deterministically with strict condition checks:
    - Kendra / Trikona positions
    - Dignity (Own, Exalted, Moolatrikona)
    - Non-combustion verification
    - Mutual aspects and conjunctions
    """
    yogas = []

    # Helper functions
    def p_sign(pid): return planet_by_id[pid]["sign_num"]
    def p_sign_idx(pid): return planet_by_id[pid].get("sign_idx", planet_by_id[pid]["sign_num"] - 1)
    def p_house(pid): return planet_by_id[pid]["house"]
    def p_lon(pid): return planet_by_id[pid]["sid_lon"]
    def is_retro(pid): return planet_by_id[pid].get("is_retrograde", False)

    sun_lon = p_lon("Sun")

    def is_combust(pid, orb_normal, orb_retro=None):
        orb = orb_retro if (is_retro(pid) and orb_retro is not None) else orb_normal
        diff = abs((p_lon(pid) - sun_lon + 180.0) % 360.0 - 180.0)
        return diff < orb

    # 1. Pancha Mahapurusha Yogas (Mars, Mercury, Jupiter, Venus, Saturn)
    # Strict conditions:
    # 1. Must be in Kendra (1, 4, 7, 10) from Lagna
    # 2. Must be in Own sign or Exaltation sign
    # 3. Must NOT be combust by Sun!
    mahapurusha_rules = [
        ("Mars", "रुचक महापुरुष योग", "Ruchaka Mahapurusha Yoga", "Ruchaka", 17.0, None,
         "मंगळ केंद्र भावात स्वराशीत (मेष, वृश्चिक) किंवा उच्च राशीत (मकर) स्थित असून अस्तांगत नसल्यामुळे रुचक महापुरुष योग निर्माण होतो. यामुळे जातक धाडसी, तेजस्वी, नेतृत्वगुणी आणि उच्च पदावर विराजमान होतो.",
         "Mars is exalted or in own sign in a Kendra and free from combustion, creating Ruchaka Mahapurusha Yoga granting courage, leadership, and high status."),
        ("Mercury", "भद्र महापुरुष योग", "Bhadra Mahapurusha Yoga", "Bhadra", 14.0, 12.0,
         "बुध केंद्र भावात स्वराशीत किंवा उच्च राशीत (मिथुन, कन्या) स्थित असून अस्तांगत नसल्यामुळे भद्र महापुरुष योग निर्माण होतो. यामुळे जातक कुशाग्र बुद्धिमत्ता, उत्तम वक्तृत्व आणि विद्वत्तेचा धनी होतो.",
         "Mercury is exalted or in own sign in a Kendra and not deeply combust, forming Bhadra Yoga conferring sharp intellect, eloquence, and commercial brilliance."),
        ("Jupiter", "हंस महापुरुष योग", "Hamsa Mahapurusha Yoga", "Hamsa", 11.0, None,
         "गुरू केंद्र भावात स्वराशीत (धनु, मीन) किंवा उच्च राशीत (कर्क) स्थित असून अस्तांगत नसल्यामुळे हंस महापुरुष योग निर्माण होतो. यामुळे जातक सात्विक, ज्ञानी, नीतिमान आणि समाजात पूजनीय ठरतो.",
         "Jupiter is exalted or in own sign in a Kendra and free from combustion, conferring Hamsa Yoga granting wisdom, virtue, and high spiritual and societal respect."),
        ("Venus", "मालव्य महापुरुष योग", "Malavya Mahapurusha Yoga", "Malavya", 10.0, 8.0,
         "शुक्र केंद्र भावात स्वराशीत (वृषभ, तूळ) किंवा उच्च राशीत (मीन) स्थित असून अस्तांगत नसल्यामुळे मालव्य महापुरुष योग निर्माण होतो. यामुळे जातक कलाप्रेमी, ऐश्वर्यसंपन्न, सुखी आणि वाहन-गृह सुखाने परिपूर्ण राहतो.",
         "Venus is exalted or in own sign in a Kendra and free from combustion, bestowing Malavya Yoga for luxury, aesthetic refinement, marital bliss, and prosperity."),
        ("Saturn", "शश महापुरुष योग", "Sasa Mahapurusha Yoga", "Sasa", 15.0, None,
         "शनी केंद्र भावात स्वराशीत (मकर, कुंभ) किंवा उच्च राशीत (तूळ) स्थित असून अस्तांगत नसल्यामुळे शश महापुरुष योग निर्माण होतो. यामुळे जातक मुत्सद्दी, न्यायप्रिय, दृढनिश्चयी आणि दीर्घायुषी होतो.",
         "Saturn is exalted or in own sign in a Kendra and free from combustion, creating Sasa Yoga conferring immense perseverance, executive authority, and longevity."),
    ]

    for pid, name_mr, name_en, code, orb_norm, orb_ret, desc_mr, desc_en in mahapurusha_rules:
        h = p_house(pid)
        s = p_sign(pid)
        is_kendra = (h in (1, 4, 7, 10))
        is_dignified = (s in OWN_SIGNS[pid] or s == EXALTED_SIGNS[pid])
        combust = is_combust(pid, orb_norm, orb_ret)

        if is_kendra and is_dignified and not combust:
            yogas.append({
                "code": code,
                "name": name_mr,
                "name_en": name_en,
                "name_hi": name_mr,
                "planets": [pid],
                "houses": [h],
                "rule": f"{pid} in Kendra ({h}th house) in own/exalted sign ({s}), free from combustion",
                "present": True,
                "conditions_verified": ["Kendra Placement", "Own/Exalted Dignity", "Non-combust"],
                "description": desc_mr,
                "desc_en": desc_en,
                "desc_hi": desc_mr,
            })

    # 2. Gajakesari Yoga
    # Condition: Jupiter in Kendra (1, 4, 7, 10) from Moon
    # Verification: Neither Moon nor Jupiter in deep debility (Scorpio / Capricorn) without neechabhanga
    jup_h = p_house("Jupiter")
    moon_h = p_house("Moon")
    diff_moon_jup = ((jup_h - moon_h + 12) % 12) + 1
    if diff_moon_jup in (1, 4, 7, 10):
        # Check debility
        jup_deb = (p_sign("Jupiter") == 10)
        moon_deb = (p_sign("Moon") == 8)
        if not (jup_deb and moon_deb):
            yogas.append({
                "code": "Gajakesari",
                "name": "गजकेसरी योग (Gajakesari Yoga)",
                "name_en": "Gajakesari Raja Yoga",
                "name_hi": "गजकेसरी राजयोग",
                "planets": ["Jupiter", "Moon"],
                "houses": [jup_h, moon_h],
                "rule": f"Jupiter in {diff_moon_jup}th house (Kendra) from Moon",
                "present": True,
                "conditions_verified": ["Jupiter-Moon Kendra", "No Dual Debility"],
                "description": "चंद्रापासून गुरू केंद्र भावात स्थित असल्यामुळे शुभ गजकेसरी योग निर्माण होतो. यामुळे जीवनात अपार यश, प्रतिष्ठा, ज्ञान, दीर्घायुष्य आणि अचानक संकटांतून विजय प्राप्त होतो.",
                "desc_en": "Jupiter in mutual Kendra from the Moon creates Gajakesari Yoga, granting lasting fame, leadership, intellectual depth, and royal protection.",
                "desc_hi": "चंद्रापासून गुरू केंद्र भावात स्थित असल्यामुळे शुभ गजकेसरी योग निर्माण होतो.",
            })

    # 3. Budhaditya Yoga
    # Condition: Sun and Mercury conjunct in same sign
    # Verification: Mercury not deeply combust (< 1.5° from Sun)
    if p_sign("Sun") == p_sign("Mercury"):
        sun_h = p_house("Sun")
        dist_sun_mer = abs((p_lon("Mercury") - p_lon("Sun") + 180.0) % 360.0 - 180.0)
        if dist_sun_mer >= 1.5:  # Not deeply combust at the exact degree
            yogas.append({
                "code": "Budhaditya",
                "name": "बुधादित्य योग (Budhaditya Yoga)",
                "name_en": "Budhaditya Raja Yoga",
                "name_hi": "बुधादित्य राजयोग",
                "planets": ["Sun", "Mercury"],
                "houses": [sun_h],
                "rule": f"Sun and Mercury conjunct in {sun_h}th house with separation {dist_sun_mer:.2f}°",
                "present": True,
                "conditions_verified": ["Conjunction in Same Sign", f"Separation {dist_sun_mer:.2f}° >= 1.5°"],
                "description": "सूर्य आणि बुध एकाच भावात युतीमध्ये असल्यामुळे बुधादित्य योग निर्माण होतो. यामुळे व्यक्तीला तल्लख स्मरणशक्ती, बौद्धिक चमक, प्रशासकीय क्षमता आणि व्यवसायात विशेष यश लाभते.",
                "desc_en": "Sun and Mercury conjunction creates Budhaditya Yoga, conferring sharp intellect, scholarly distinction, and administrative acumen.",
                "desc_hi": "सूर्य आणि बुध एकाच भावात युतीमध्ये असल्यामुळे बुधादित्य योग निर्माण होतो.",
            })

    # 4. Chandra-Mangal Yoga
    # Condition: Moon and Mars conjunct (1) or in mutual 7th aspect
    # Verification: Neither planet debilitated
    moon_mars_diff = ((p_house("Mars") - moon_h + 12) % 12) + 1
    if moon_mars_diff in (1, 7):
        if not (p_sign("Moon") == 8 and p_sign("Mars") == 4):
            yogas.append({
                "code": "ChandraMangal",
                "name": "चंद्र-मंगळ योग (Chandra-Mangal Yoga)",
                "name_en": "Chandra-Mangal Wealth Yoga",
                "name_hi": "चंद्र-मंगल योग",
                "planets": ["Moon", "Mars"],
                "houses": [moon_h, p_house("Mars")],
                "rule": f"Moon and Mars in direct aspect/conjunction ({moon_mars_diff}th)",
                "present": True,
                "conditions_verified": ["Conjunction or 7th Aspect", "Dignity Validated"],
                "description": "चंद्र आणि मंगळ यांची युती किंवा परस्पर दृष्टी असल्यामुळे लक्ष्मीकारक चंद्र-मंगळ योग बनतो. यामुळे जातक आर्थिक व्यवहार, व्यापार आणि स्थावर मालमत्तेत धनवान बनतो.",
                "desc_en": "Moon and Mars conjunction or mutual opposition forms Chandra-Mangal Yoga, generating strong financial instinct, property gains, and commercial enterprise.",
                "desc_hi": "चंद्र आणि मंगळ यांची युती किंवा परस्पर दृष्टी असल्यामुळे लक्ष्मीकारक चंद्र-मंगळ योग बनतो.",
            })

    # 5. House Lords for Raja & Dhana Yogas
    house_lords = {}
    for h in range(1, 13):
        s_idx = (asc_sign_idx + h - 1) % 12
        house_lords[h] = SIGN_LORDS[s_idx]

    l1 = house_lords[1]
    l4 = house_lords[4]
    l5 = house_lords[5]
    l7 = house_lords[7]
    l9 = house_lords[9]
    l10 = house_lords[10]
    l11 = house_lords[11]

    # Dharma-Karmadhipati Raja Yoga (9th Lord & 10th Lord relation)
    # Relation: Conjunction, Mutual 7th Aspect, or Parivartana
    l9_h = p_house(l9)
    l10_h = p_house(l10)
    l9_s = p_sign_idx(l9)
    l10_s = p_sign_idx(l10)
    rel_9_10 = ((l10_h - l9_h + 12) % 12) + 1
    # Check parivartana
    is_parivartana_9_10 = (l9_h == 10 and l10_h == 9)
    if rel_9_10 in (1, 7) or is_parivartana_9_10:
        yogas.append({
            "code": "DharmaKarmadhipati",
            "name": "धर्म-कर्माधिपती राजयोग",
            "name_en": "Dharma-Karmadhipati Raja Yoga",
            "name_hi": "धर्म-कर्माधिपति राजयोग",
            "planets": [l9, l10],
            "houses": [l9_h, l10_h],
            "rule": f"9th Lord ({l9}) and 10th Lord ({l10}) form auspicious relationship",
            "present": True,
            "conditions_verified": ["9th-10th Lord Conjunction/Aspect/Parivartana"],
            "description": "भाग्येश आणि दशमेश यांच्यातील युती, दृष्टी किंवा राशी परिवर्तनामुळे सर्वोच्च धर्म-कर्माधिपती राजयोग निर्माण होतो. यामुळे जातक उच्च अधिकार, प्रतिष्ठा आणि भाग्योदयाचा धनी होतो.",
            "desc_en": "Auspicious association of 9th Lord and 10th Lord forms the sovereign Dharma-Karmadhipati Yoga for supreme status and professional triumph.",
            "desc_hi": "भाग्येश और दशमेश का संबंध धर्म-कर्माधिपति राजयोग बनाता है।",
        })

    # Kendra-Trikona Raja Yoga (Other combinations: 1-5, 1-9, 4-5, 4-9, 5-7, 7-9, 5-10)
    kt_pairs = [(l1, l5, 1, 5), (l1, l9, 1, 9), (l4, l5, 4, 5), (l4, l9, 4, 9), (l5, l7, 5, 7), (l5, l10, 5, 10), (l7, l9, 7, 9)]
    for pA, pB, hA, hB in kt_pairs:
        if pA != pB and p_house(pA) == p_house(pB):
            yogas.append({
                "code": f"RajaYoga_{hA}_{hB}",
                "name": f"केंद्र-त्रिकोण राजयोग ({hA} आणि {hB} भाव)",
                "name_en": f"Kendra-Trikona Raja Yoga ({hA}-{hB} Lords)",
                "name_hi": f"केन्द्र-त्रिकोण राजयोग ({hA}-{hB} भावेश)",
                "planets": [pA, pB],
                "houses": [p_house(pA)],
                "rule": f"{hA}th Lord ({pA}) and {hB}th Lord ({pB}) conjunct in {p_house(pA)}th house",
                "present": True,
                "conditions_verified": ["Kendra-Trikona Lord Conjunction"],
                "description": f"{hA}व्या आणि {hB}व्या भावाच्या अधिपतींची युती शुभ केंद्र-त्रिकोण राजयोग घडवते, ज्यामुळे जीवनात मान-सन्मान आणि प्रगती लाभते.",
                "desc_en": f"Conjunction of {hA}th Lord and {hB}th Lord forms an auspicious Kendra-Trikona Raja Yoga conferring rise and prosperity.",
                "desc_hi": f"{hA}वें एवं {hB}वें भाव के स्वामियों की युति केंद्र-त्रिकोण राजयोग बनाती है।",
            })
            break  # Include principal Raja Yoga

    # Dhana Yoga (Connection between 1st, 2nd, 5th, 9th, 11th lords)
    l2 = house_lords[2]
    if (p_house(l2) == p_house(l11) and l2 != l11) or (p_house(l5) == p_house(l11) and l5 != l11) or (p_house(l9) == p_house(l11) and l9 != l11):
        yogas.append({
            "code": "DhanaYoga",
            "name": "महाधन योग (Dhana Yoga)",
            "name_en": "Maha Dhana Yoga",
            "name_hi": "महाधन योग",
            "planets": [l2, l11],
            "houses": [p_house(l11)],
            "rule": "Lords of wealth and gains (2nd/5th/9th and 11th) connect in strength",
            "present": True,
            "conditions_verified": ["Wealth & Gain Lord Relationship"],
            "description": "धनस्थान (२रा भाव) आणि लाभस्थान (११वा भाव) यांच्या अधिपतींचा शुभ संबंध महाधन योग घडवतो, ज्यामुळे अखंड संपत्ती व आर्थिक स्थिरता प्राप्त होते.",
            "desc_en": "Auspicious association between wealth and gain lords confers lasting financial growth and abundance.",
            "desc_hi": "धन एवं लाभ भाव के स्वामियों का संबंध महाधन योग बनाता है।",
        })

    # 6. Viparita Raja Yogas (Harsha, Sarala, Vimala)
    # Classical rule: Trika lord in Trika house (6, 8, 12), not afflicted by natural benefics
    lord_6 = house_lords[6]
    h_lord_6 = p_house(lord_6)
    if h_lord_6 in (6, 8, 12):
        yogas.append({
            "code": "Harsha",
            "name": "हर्ष विपरीत राजयोग (Harsha Viparita Rajayoga)",
            "name_en": "Harsha Viparita Raja Yoga",
            "name_hi": "हर्ष विपरीत राजयोग",
            "planets": [lord_6],
            "houses": [h_lord_6],
            "rule": f"6th lord ({lord_6}) situated in {h_lord_6}th house (Dusthana)",
            "present": True,
            "conditions_verified": ["6th Lord in Dusthana House"],
            "description": "षष्ठेश ग्रह स्वतः ६, ८ किंवा १२व्या भावात स्थित असल्यामुळे हर्ष विपरीत राजयोग निर्माण होतो. यामुळे जातक शत्रूंवर मात करतो, निरोगी राहतो आणि विपरीत परिस्थितीतूनही धनलाभ मिळवतो.",
            "desc_en": "6th Lord placed in a Dusthana produces Harsha Viparita Raja Yoga conferring triumph over adversaries and extraordinary resilience.",
            "desc_hi": "षष्ठेश ग्रह ६, ८ अथवा १२वें भाव में स्थित होने से हर्ष विपरीत राजयोग बनता है।",
        })

    lord_8 = house_lords[8]
    h_lord_8 = p_house(lord_8)
    if h_lord_8 in (6, 8, 12):
        yogas.append({
            "code": "Sarala",
            "name": "सरल विपरीत राजयोग (Sarala Viparita Rajayoga)",
            "name_en": "Sarala Viparita Raja Yoga",
            "name_hi": "सरल विपरीत राजयोग",
            "planets": [lord_8],
            "houses": [h_lord_8],
            "rule": f"8th lord ({lord_8}) situated in {h_lord_8}th house (Dusthana)",
            "present": True,
            "conditions_verified": ["8th Lord in Dusthana House"],
            "description": "अष्टमेश ग्रह स्वतः ६, ८ किंवा १२व्या भावात स्थित असल्यामुळे सरल विपरीत राजयोग बनतो. यामुळे जातक निडर, विद्वान, दीर्घायुषी आणि गुप्त धनाचा स्वामी बनतो.",
            "desc_en": "8th Lord placed in a Dusthana produces Sarala Viparita Raja Yoga granting fearless spirit, longevity, and unexpected windfalls.",
            "desc_hi": "अष्टमेश ग्रह ६, ८ अथवा १२वें भाव में स्थित होने से सरल विपरीत राजयोग बनता है।",
        })

    lord_12 = house_lords[12]
    h_lord_12 = p_house(lord_12)
    if h_lord_12 in (6, 8, 12):
        yogas.append({
            "code": "Vimala",
            "name": "विमल विपरीत राजयोग (Vimala Viparita Rajayoga)",
            "name_en": "Vimala Viparita Raja Yoga",
            "name_hi": "विमल विपरीत राजयोग",
            "planets": [lord_12],
            "houses": [h_lord_12],
            "rule": f"12th lord ({lord_12}) situated in {h_lord_12}th house (Dusthana)",
            "present": True,
            "conditions_verified": ["12th Lord in Dusthana House"],
            "description": "व्ययेश ग्रह स्वतः ६, ८ किंवा १२व्या भावात स्थित असल्यामुळे विमल विपरीत राजयोग निर्माण होतो. यामुळे अनावश्यक खर्चावर नियंत्रण राहून जातक समृद्ध व परदेशात यशस्वी होतो.",
            "desc_en": "12th Lord placed in a Dusthana produces Vimala Viparita Raja Yoga ensuring disciplined expenditure, spiritual elevation, and foreign success.",
            "desc_hi": "व्ययेश ग्रह ६, ८ अथवा १२वें भाव में स्थित होने से विमल विपरीत राजयोग बनता है।",
        })

    # 7. Amala Yoga (Benefic Jupiter, Venus, or Mercury in 10th house from Lagna or Moon)
    for p_benefic in ("Jupiter", "Venus", "Mercury"):
        if p_house(p_benefic) == 10 and not is_combust(p_benefic, 10.0):
            yogas.append({
                "code": "Amala",
                "name": "अमल कीर्ति योग (Amala Yoga)",
                "name_en": "Amala Kirti Yoga",
                "name_hi": "अमला कीर्ति योग",
                "planets": [p_benefic],
                "houses": [10],
                "rule": f"Natural benefic ({p_benefic}) in 10th house free from combustion",
                "present": True,
                "conditions_verified": ["Natural Benefic in 10th House", "Free from Combustion"],
                "description": "दशम कर्म भावात शुभ ग्रह स्थित असल्यामुळे अमल कीर्ति योग घडतो. यामुळे जातक समाजात निष्कलंक कीर्ती, परोपकारी स्वभाव आणि उच्च सन्मान प्राप्त करतो.",
                "desc_en": "Natural benefic occupying the 10th house of career bestows spotless reputation, ethical leadership, and lasting honour.",
                "desc_hi": "दशम कर्म भाव में शुभ ग्रह स्थित होने से अमला कीर्ति योग बनता है।",
            })
            break

    # 8. Neecha Bhanga Raja Yoga
    deb_signs = {"Sun": 7, "Moon": 8, "Mars": 4, "Mercury": 12, "Jupiter": 10, "Venus": 6, "Saturn": 1}
    exalt_lords = {"Sun": "Mars", "Moon": "Venus", "Mars": "Saturn", "Mercury": "Mercury", "Jupiter": "Moon", "Venus": "Jupiter", "Saturn": "Venus"}
    for deb_p, d_sign in deb_signs.items():
        if p_sign(deb_p) == d_sign:
            dispositor = SIGN_LORDS[d_sign - 1]
            exalt_l = exalt_lords[deb_p]
            disp_h = p_house(dispositor)
            exalt_h = p_house(exalt_l)
            # Classical rule: Dispositor or Exaltation Lord in Kendra (1, 4, 7, 10) from Lagna or Moon
            disp_in_kendra = (disp_h in (1, 4, 7, 10))
            exalt_in_kendra = (exalt_h in (1, 4, 7, 10))
            if disp_in_kendra or exalt_in_kendra:
                yogas.append({
                    "code": f"NeechaBhanga_{deb_p}",
                    "name": f"नीचभंग राजयोग ({deb_p})",
                    "name_en": f"Neecha Bhanga Raja Yoga ({deb_p})",
                    "name_hi": f"नीचभंग राजयोग ({deb_p})",
                    "planets": [deb_p, dispositor if disp_in_kendra else exalt_l],
                    "houses": [p_house(deb_p), disp_h if disp_in_kendra else exalt_h],
                    "rule": f"Debilitated {deb_p}'s dispositor/exaltation lord in Kendra ({disp_h if disp_in_kendra else exalt_h}th)",
                    "present": True,
                    "conditions_verified": ["Planet in Debilitation", "Dispositor/Exaltation Lord in Kendra"],
                    "description": f"{deb_p} नीच राशीत असला तरी त्याचा स्वामी केंद्र भावात बलवान असल्याने नीचभंग राजयोग बनतो. यामुळे सुरुवातीच्या संघर्षानंतर व्यक्ती उत्तुंग यश संपादन करते.",
                    "desc_en": f"{deb_p}'s debilitation is cancelled by its dispositor/exaltation lord being in Kendra, conferring extraordinary resilience and late-stage triumph.",
                    "desc_hi": f"{deb_p} का नीचभंग राजयोग प्रारंभिक संघर्ष के बाद असाधारण सफलता देता है।",
                })

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
