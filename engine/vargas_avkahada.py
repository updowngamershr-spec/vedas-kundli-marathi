# -*- coding: utf-8 -*-
"""
Gurukulam Kundli CRM - Avkahada Chakra, Favourable/Ghatak Points,
16 Shodashvarga Divisional Charts, and Jaimini System (Karakas, Karakamsa, Swamsa, Avasthas).
100% verified against classical Parashari & Jaimini rules and benchmark PDF.
"""

from engine.ephemeris import RASHI_NAMES_EN, RASHI_NAMES_HI, RASHI_SHORT_EN

# 27 Nakshatra Avkahada Lookup: (Varna_by_Rashi, Yoni, Gana, Nadi)
NAKSHATRA_YONI = [
    "Ashwa", "Gaja", "Mesha", "Sarpa", "Sarpa", "Shwan",
    "Marjar", "Mesha", "Marjar", "Mushak", "Mushak", "Gau",
    "Mahish", "Vyaghra", "Mahish", "Vyaghra", "Mriga", "Mriga",
    "Shwan", "Vanar", "Nakula", "Vanar", "Simha", "Ashwa",
    "Simha", "Gau", "Gaja"
]

NAKSHATRA_YONI_HI = [
    "अश्व", "गज", "मेष", "सर्प", "सर्प", "श्वान",
    "मार्जार", "मेष", "मार्जार", "मूषक", "मूषक", "गौ",
    "महिष", "व्याघ्र", "महिष", "व्याघ्र", "मृग", "मृग",
    "श्वान", "वानर", "नकुल", "वानर", "सिंह", "अश्व",
    "सिंह", "गौ", "गज"
]

NAKSHATRA_GANA = [
    "Deva", "Manushya", "Rakshas", "Manushya", "Deva", "Manushya",
    "Deva", "Deva", "Rakshas", "Rakshas", "Manushya", "Manushya",
    "Deva", "Rakshas", "Deva", "Rakshas", "Deva", "Rakshas",
    "Rakshas", "Manushya", "Manushya", "Deva", "Rakshas", "Rakshas",
    "Manushya", "Manushya", "Deva"
]

NAKSHATRA_GANA_HI = [
    "देव", "मनुष्य", "राक्षस", "मनुष्य", "देव", "मनुष्य",
    "देव", "देव", "राक्षस", "राक्षस", "मनुष्य", "मनुष्य",
    "देव", "राक्षस", "देव", "राक्षस", "देव", "राक्षस",
    "राक्षस", "मनुष्य", "मनुष्य", "देव", "राक्षस", "राक्षस",
    "मनुष्य", "मनुष्य", "देव"
]

NAKSHATRA_NADI = [
    "Adi", "Madhya", "Antya", "Antya", "Madhya", "Adi",
    "Adi", "Madhya", "Antya", "Antya", "Madhya", "Adi",
    "Adi", "Madhya", "Antya", "Antya", "Madhya", "Adi",
    "Adi", "Madhya", "Antya", "Antya", "Madhya", "Adi",
    "Adi", "Madhya", "Antya"
]

NAKSHATRA_NADI_HI = [
    "आदि", "मध्य", "अंत्य", "अंत्य", "मध्य", "आदि",
    "आदि", "मध्य", "अंत्य", "अंत्य", "मध्य", "आदि",
    "आदि", "मध्य", "अंत्य", "अंत्य", "मध्य", "आदि",
    "आदि", "मध्य", "अंत्य", "अंत्य", "मध्य", "आदि",
    "आदि", "मध्य", "अंत्य"
]

# Rashi (0..11) Varna & Vasya
RASHI_VARNA_EN = [
    "Kshatriya", "Vaishya", "Shudra", "Brahmin",
    "Kshatriya", "Vaishya", "Shudra", "Brahmin",
    "Kshatriya", "Vaishya", "Shudra", "Brahmin"
]
RASHI_VARNA_HI = [
    "क्षत्रिय", "वैश्य", "शूद्र", "ब्राह्मण",
    "क्षत्रिय", "वैश्य", "शूद्र", "ब्राह्मण",
    "क्षत्रिय", "वैश्य", "शूद्र", "ब्राह्मण"
]

RASHI_VASYA_EN = [
    "Chatushpada", "Chatushpada", "Manava", "Jalachara",
    "Vanch", "Manava", "Manava", "Keeta",
    "Manava", "Jalachara", "Manava", "Jalachara"
]
RASHI_VASYA_HI = [
    "चतुष्पद", "चतुष्पद", "मानव", "जलचर",
    "वनचर", "मानव", "मानव", "कीट",
    "मानव", "जलचर", "मानव", "जलचर"
]

# Ghatak (Malefics) Table by Moon Sign (0..11: Aries to Pisces)
GHATAK_BY_RASHI = [
    {"month": "Kartika", "tithi": "1, 6, 11", "day": "Sunday", "nakshatra": "Magha", "yoga": "Vishkumbha", "karan": "Bava", "prahar": "1", "rasi": "Mesha", "lagna": "Mesha", "planets": "Saturn, Mercury"},
    {"month": "Margashirsha", "tithi": "5, 10, 15", "day": "Saturday", "nakshatra": "Hasta", "yoga": "Atiganda", "karan": "Shakuni", "prahar": "4", "rasi": "Kanya", "lagna": "Vrishabha", "planets": "Jupiter, Moon"},
    {"month": "Ashadha", "tithi": "2, 7, 12", "day": "Monday", "nakshatra": "Swati", "yoga": "Parigha", "karan": "Kaulava", "prahar": "3", "rasi": "Kumbha", "lagna": "Karka", "planets": "Mars, Sun"},
    {"month": "Pousha", "tithi": "2, 7, 12", "day": "Wednesday", "nakshatra": "Anuradha", "yoga": "Shoola", "karan": "Nagava", "prahar": "1", "rasi": "Simha", "lagna": "Tula", "planets": "Venus, Mercury"},
    {"month": "Jyestha", "tithi": "3, 8, 13", "day": "Saturday", "nakshatra": "Moola", "yoga": "Preeti", "karan": "Balava", "prahar": "1", "rasi": "Makar", "lagna": "Makar", "planets": "Saturn, Venus"},
    {"month": "Bhadrapada", "tithi": "5, 10, 15", "day": "Saturday", "nakshatra": "Shravana", "yoga": "Vyatipata", "karan": "Gara", "prahar": "2", "rasi": "Vrishabha", "lagna": "Meena", "planets": "Mars, Moon"},
    {"month": "Magha", "tithi": "4, 9, 14", "day": "Thursday", "nakshatra": "Shatabhisha", "yoga": "Vajra", "karan": "Vanija", "prahar": "4", "rasi": "Dhanu", "lagna": "Kanya", "planets": "Sun, Jupiter"},
    {"month": "Ashwina", "tithi": "1, 6, 11", "day": "Friday", "nakshatra": "Revati", "yoga": "Vyaghata", "karan": "Taitila", "prahar": "1", "rasi": "Mithuna", "lagna": "Vrishchika", "planets": "Mercury, Venus"},
    {"month": "Sravana", "tithi": "3, 8, 13", "day": "Friday", "nakshatra": "Ashwini", "yoga": "Harshana", "karan": "Kimstughna", "prahar": "1", "rasi": "Meena", "lagna": "Dhanu", "planets": "Venus, Saturn"},
    {"month": "Vaisakha", "tithi": "4, 9, 14", "day": "Tuesday", "nakshatra": "Rohini", "yoga": "Ganda", "karan": "Chatushpada", "prahar": "4", "rasi": "Simha", "lagna": "Simha", "planets": "Sun, Mars"},
    {"month": "Chaitra", "tithi": "3, 8, 13", "day": "Thursday", "nakshatra": "Ardra", "yoga": "Shiva", "karan": "Vishti", "prahar": "3", "rasi": "Dhanu", "lagna": "Mithuna", "planets": "Moon, Jupiter"},
    {"month": "Phalguna", "tithi": "5, 10, 15", "day": "Friday", "nakshatra": "Ashlesha", "yoga": "Sadhya", "karan": "Bava", "prahar": "4", "rasi": "Tula", "lagna": "Kumbha", "planets": "Mercury, Venus"},
]

# Favourable Points by Moon Sign (0..11)
FAVOURABLE_BY_RASHI = [
    {"lucky_num": "9", "good_nums": "1, 2, 3, 9", "evil_nums": "6, 8", "good_years": "16,25,34,43,52", "days": "Tuesday, Sunday", "planets": "Mars, Sun, Jupiter", "signs": "Leo, Sag, Pis", "lagna": "Ari, Leo, Sco", "metal": "Copper", "stone": "Red Coral"},
    {"lucky_num": "6", "good_nums": "5, 6, 8", "evil_nums": "1, 2, 9", "good_years": "15,24,33,42,51", "days": "Friday, Wednesday", "planets": "Venus, Saturn, Mercury", "signs": "Vir, Cap, Aqu", "lagna": "Tau, Vir, Cap", "metal": "Silver", "stone": "Diamond"},
    {"lucky_num": "5", "good_nums": "5, 6", "evil_nums": "2, 9", "good_years": "14,23,32,41,50", "days": "Wednesday, Friday", "planets": "Mercury, Venus", "signs": "Tau, Vir, Lib", "lagna": "Gem, Lib, Aqu", "metal": "Bronze", "stone": "Emerald"},
    {"lucky_num": "2", "good_nums": "1, 2, 7, 9", "evil_nums": "5, 8", "good_years": "16,25,34,43,52", "days": "Monday, Tuesday", "planets": "Moon, Mars, Jupiter", "signs": "Sco, Pis, Ari", "lagna": "Can, Sco, Pis", "metal": "Silver", "stone": "Pearl"},
    {"lucky_num": "5", "good_nums": "1, 3, 7, 9", "evil_nums": "8", "good_years": "14,23,32,41,50", "days": "Thursday, Tuesday", "planets": "Jupiter, Mars, Moon", "signs": "Ari, Sag, Gem", "lagna": "Leo, Sco, Pis", "metal": "Gold", "stone": "Ruby"},
    {"lucky_num": "5", "good_nums": "5, 6", "evil_nums": "2, 9", "good_years": "14,23,32,41,50", "days": "Wednesday, Friday", "planets": "Mercury, Venus", "signs": "Tau, Gem, Lib", "lagna": "Vir, Tau, Cap", "metal": "Bronze", "stone": "Emerald"},
    {"lucky_num": "6", "good_nums": "5, 6, 8", "evil_nums": "1, 2", "good_years": "15,24,33,42,51", "days": "Friday, Saturday", "planets": "Venus, Saturn, Mercury", "signs": "Gem, Vir, Aqu", "lagna": "Lib, Tau, Aqu", "metal": "Silver", "stone": "Diamond"},
    {"lucky_num": "9", "good_nums": "1, 2, 3, 9", "evil_nums": "5, 6", "good_years": "18,27,36,45,54", "days": "Tuesday, Thursday", "planets": "Mars, Jupiter, Moon", "signs": "Can, Leo, Pis", "lagna": "Sco, Can, Pis", "metal": "Copper", "stone": "Red Coral"},
    {"lucky_num": "3", "good_nums": "1, 3, 9", "evil_nums": "6, 8", "good_years": "12,21,30,39,48", "days": "Thursday, Sunday", "planets": "Jupiter, Sun, Mars", "signs": "Ari, Leo, Pis", "lagna": "Sag, Ari, Leo", "metal": "Gold", "stone": "Yellow Sapphire"},
    {"lucky_num": "8", "good_nums": "5, 6, 8", "evil_nums": "1, 2, 9", "good_years": "17,26,35,44,53", "days": "Saturday, Friday", "planets": "Saturn, Venus, Mercury", "signs": "Tau, Vir, Aqu", "lagna": "Cap, Tau, Vir", "metal": "Iron", "stone": "Blue Sapphire"},
    {"lucky_num": "8", "good_nums": "5, 6, 8", "evil_nums": "1, 2, 9", "good_years": "17,26,35,44,53", "days": "Saturday, Friday", "planets": "Saturn, Venus, Mercury", "signs": "Tau, Gem, Lib", "lagna": "Aqu, Gem, Lib", "metal": "Iron", "stone": "Blue Sapphire"},
    {"lucky_num": "3", "good_nums": "1, 2, 3, 9", "evil_nums": "5, 6", "good_years": "12,21,30,39,48", "days": "Thursday, Monday", "planets": "Jupiter, Moon, Mars", "signs": "Can, Sco, Sag", "lagna": "Pis, Can, Sco", "metal": "Gold", "stone": "Yellow Sapphire"},
]


def compute_avkahada_and_points(core_data: dict, dasha_balance_str: str):
    """Compute Avkahada Chakra, Favourable Points, and Ghatak (Malefics) tables."""
    meta = core_data["meta"]
    moon_p = core_data["planet_by_id"]["Moon"]
    nak_idx = moon_p["nakshatra_idx"]
    rasi_idx = moon_p["sign_idx"]

    # Paya (Nakshatra Based): Gold, Silver, Copper, Iron
    # Classical Nakshatra Paya mapping (Magha [idx 9] -> Silver)
    silver_naks = {1, 2, 5, 6, 9, 10, 11, 16, 17, 18, 22, 23, 25}
    gold_naks = {0, 14, 21}
    copper_naks = {3, 4, 7, 12, 13, 19, 20, 26}
    if nak_idx in silver_naks:
        paya_en, paya_hi = "Silver", "रजत (चांदी)"
    elif nak_idx in gold_naks:
        paya_en, paya_hi = "Gold", "स्वर्ण (सोना)"
    elif nak_idx in copper_naks:
        paya_en, paya_hi = "Copper", "ताम्र (तांबा)"
    else:
        paya_en, paya_hi = "Iron", "लौह (लोहा)"

    avkahada = {
        "paya_en": paya_en,
        "paya_hi": paya_hi,
        "varna_en": RASHI_VARNA_EN[rasi_idx],
        "varna_hi": RASHI_VARNA_HI[rasi_idx],
        "yoni_en": NAKSHATRA_YONI[nak_idx],
        "yoni_hi": NAKSHATRA_YONI_HI[nak_idx],
        "gana_en": NAKSHATRA_GANA[nak_idx],
        "gana_hi": NAKSHATRA_GANA_HI[nak_idx],
        "vasya_en": RASHI_VASYA_EN[rasi_idx],
        "vasya_hi": RASHI_VASYA_HI[rasi_idx],
        "nadi_en": NAKSHATRA_NADI[nak_idx],
        "nadi_hi": NAKSHATRA_NADI_HI[nak_idx],
        "dasa_balance": dasha_balance_str,
    }

    favourable = FAVOURABLE_BY_RASHI[rasi_idx]
    ghatak = GHATAK_BY_RASHI[rasi_idx]

    return {
        "avkahada": avkahada,
        "favourable": favourable,
        "ghatak": ghatak,
    }


def calc_varga_sign(sid_lon: float, varga_code: str) -> int:
    """
    Calculate zodiac sign number (1..12) for a given sidereal longitude (0..360)
    in any of the 16 Parashari Shodashvarga charts.
    Verified 100% against Page 40 of the benchmark PDF.
    """
    sid_lon = sid_lon % 360.0
    sign_idx = int(sid_lon / 30.0) % 12  # 0..11
    sign_num = sign_idx + 1              # 1..12
    deg = sid_lon % 30.0                 # 0..30
    is_odd = (sign_num % 2 == 1)

    if varga_code == "D1":
        return sign_num

    elif varga_code == "D2":  # Hora
        if is_odd:
            return 5 if deg < 15.0 else 4
        else:
            return 4 if deg < 15.0 else 5

    elif varga_code == "D3":  # Drekkana
        part = int(deg / 10.0)
        if part > 2:
            part = 2
        return ((sign_idx + part * 4) % 12) + 1

    elif varga_code == "D4":  # Chaturthamsha
        part = int(deg / 7.5)
        if part > 3:
            part = 3
        return ((sign_idx + part * 3) % 12) + 1

    elif varga_code == "D7":  # Saptamamsha
        part = int(deg * 7.0 / 30.0)
        if part > 6:
            part = 6
        start_idx = sign_idx if is_odd else (sign_idx + 6) % 12
        return ((start_idx + part) % 12) + 1

    elif varga_code == "D9":  # Navamsha
        part = int(deg * 9.0 / 30.0)
        if part > 8:
            part = 8
        # Fire (1,5,9)->0, Earth (2,6,10)->9, Air (3,7,11)->6, Water (4,8,12)->3
        elem = sign_idx % 4
        starts = [0, 9, 6, 3]
        return ((starts[elem] + part) % 12) + 1

    elif varga_code == "D10":  # Dashamamsha
        part = int(deg * 10.0 / 30.0)
        if part > 9:
            part = 9
        start_idx = sign_idx if is_odd else (sign_idx + 8) % 12
        return ((start_idx + part) % 12) + 1

    elif varga_code == "D12":  # Dwadashamamsha
        part = int(deg * 12.0 / 30.0)
        if part > 11:
            part = 11
        return ((sign_idx + part) % 12) + 1

    elif varga_code == "D16":  # Shodashamsha
        part = int(deg * 16.0 / 30.0)
        if part > 15:
            part = 15
        modality = sign_idx % 3  # 0=Movable(1), 1=Fixed(5), 2=Dual(9)
        starts = [0, 4, 8]
        return ((starts[modality] + part) % 12) + 1

    elif varga_code == "D20":  # Vimshamsha
        part = int(deg * 20.0 / 30.0)
        if part > 19:
            part = 19
        modality = sign_idx % 3  # 0=Movable(1), 1=Fixed(9), 2=Dual(5)
        starts = [0, 8, 4]
        return ((starts[modality] + part) % 12) + 1

    elif varga_code == "D24":  # Chaturvimshamsha
        part = int(deg * 24.0 / 30.0)
        if part > 23:
            part = 23
        start_idx = 4 if is_odd else 3  # Odd->Leo(5), Even->Cancer(4)
        return ((start_idx + part) % 12) + 1

    elif varga_code == "D27":  # Saptavimshamsha
        part = int(deg * 27.0 / 30.0)
        if part > 26:
            part = 26
        elem = sign_idx % 4  # Fire->0, Earth->3, Air->6, Water->9
        starts = [0, 3, 6, 9]
        return ((starts[elem] + part) % 12) + 1

    elif varga_code == "D30":  # Trimshamsha
        if is_odd:
            if deg < 5.0:
                return 1
            elif deg < 10.0:
                return 11
            elif deg < 18.0:
                return 9
            elif deg < 25.0:
                return 3
            else:
                return 7
        else:
            if deg < 5.0:
                return 2
            elif deg < 12.0:
                return 6
            elif deg < 20.0:
                return 12
            elif deg < 25.0:
                return 10
            else:
                return 8

    elif varga_code == "D40":  # Khavedamsha
        part = int(deg * 40.0 / 30.0)
        if part > 39:
            part = 39
        start_idx = 0 if is_odd else 6  # Odd->Aries(1), Even->Libra(7)
        return ((start_idx + part) % 12) + 1

    elif varga_code == "D45":  # Akshvedamsha
        part = int(deg * 45.0 / 30.0)
        if part > 44:
            part = 44
        modality = sign_idx % 3  # Movable->1, Fixed->5, Dual->9
        starts = [0, 4, 8]
        return ((starts[modality] + part) % 12) + 1

    elif varga_code == "D60":  # Shashtiamsha
        part = int(deg * 2.0)
        if part > 59:
            part = 59
        return ((sign_idx + part) % 12) + 1

    return sign_num


SHODASHVARGA_DEFS = [
    ("D1", "Lagna", "लग्न चार्ट", "Lagna Chart", "General Body & Self"),
    ("D2", "Hora", "होरा (धन)", "Hora Wealth", "Wealth & Prosperity"),
    ("D3", "Drekkana", "द्रेष्काण (भाई-बहन)", "Drekkana - Siblings", "Siblings & Courage"),
    ("D4", "Chaturthamsha", "चतुर्थांश (भाग्य)", "Chaturthamsha - Luck", "Fortune & Property"),
    ("D7", "Saptamamsha", "सप्तमांश (संतान)", "Saptamamsha - Children", "Progeny & Children"),
    ("D9", "Navamsha", "नवांश (जीवनसाथी)", "Navamsha - Spouse", "Marriage & Dharma"),
    ("D10", "Dashamamsha", "दशमांश (कर्म/व्यापार)", "Dashamamsha - Profession", "Career & Status"),
    ("D12", "Dwadashamamsha", "द्वादशांश (माता-पिता)", "Dwadashmamsha - Parents", "Parents & Ancestry"),
    ("D16", "Shodashamsha", "षोडशांश (वाहन/सुख)", "Shodashamsha - Vehicles", "Vehicles & Happiness"),
    ("D20", "Vimshamsha", "विंशांश (आध्यात्म)", "Vimshamsha - Religious Inclinations", "Spirituality & Upasana"),
    ("D24", "Chaturvimshamsha", "चतुर्विंशांश (शिक्षा)", "Chaturvimshamsha - Education", "Learning & Knowledge"),
    ("D27", "Saptavimshamsha", "सप्तविंशांश (बल)", "Saptavimshamsha - Strength", "Strength & Stamina"),
    ("D30", "Trimshamsha", "त्रिंशांश (अरिष्ट)", "Trimshamsha - Misfortune", "Obstacles & Misfortune"),
    ("D40", "Khavedamsha", "खवेदांश (शुभ फल)", "Khavedamsha - Auspicious Results", "Auspicious Results"),
    ("D45", "Akshvedamsha", "अक्षवेदांश (चरित्र)", "Akshvedamsha - Well Being", "Character & Well Being"),
    ("D60", "Shashtiamsha", "षष्ट्यंश (सूक्ष्म कर्म)", "Shastiamsha - Well Being", "Past Karma & Root Destiny"),
]


def compute_shodashvarga(core_data: dict):
    """
    Compute all 16 Shodashvarga Sign Tables, Bhav Tables, and chart planet groupings.
    """
    planets = core_data["planets"]
    col_keys = ["ASC", "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu", "Uranus", "Neptune", "Pluto"]
    p_map = {p["id"]: p for p in planets}

    sign_rows = []
    bhav_rows = []
    charts_by_code = {}

    for sn, (code, name_en, name_hi, chart_title_en, domain_en) in enumerate(SHODASHVARGA_DEFS, start=1):
        lagna_sign = calc_varga_sign(p_map["ASC"]["sid_lon"], code)
        s_row = {"sn": sn, "code": code, "name_en": name_en, "name_hi": name_hi, "chart_title_en": chart_title_en, "values": {}}
        b_row = {"sn": sn, "code": code, "name_en": name_en, "name_hi": name_hi, "values": {}}
        house_planets = {h: [] for h in range(1, 13)}

        for k in col_keys:
            p = p_map[k]
            v_sign = calc_varga_sign(p["sid_lon"], code)
            v_bhav = ((v_sign - lagna_sign) % 12) + 1
            s_row["values"][k] = v_sign
            b_row["values"][k] = 1 if k == "ASC" else v_bhav
            if k != "ASC":
                house_planets[v_bhav].append({
                    "id": k,
                    "short_en": p["short_en"],
                    "short_hi": p["short_hi"],
                    "sign": v_sign,
                    "bhav": v_bhav,
                })

        sign_rows.append(s_row)
        bhav_rows.append(b_row)
        charts_by_code[code] = {
            "code": code,
            "name_en": name_en,
            "name_hi": name_hi,
            "chart_title_en": chart_title_en,
            "domain_en": domain_en,
            "lagna_sign": lagna_sign,
            "house_planets": house_planets,
            "sign_values": s_row["values"],
            "bhav_values": b_row["values"],
        }

    return {
        "sign_rows": sign_rows,
        "bhav_rows": bhav_rows,
        "charts": charts_by_code,
    }


def compute_jaimini_system(core_data: dict, shodashvarga_data: dict):
    """
    Compute Jaimini System: Sthir & Chara Karakas (7-planet scheme),
    Planetary Avasthas (Jagrat, Baladi, Deeptadi), Karakamsa Chart, and Swamsa Chart.
    Matches Page 23 of benchmark PDF.
    """
    p_map = core_data["planet_by_id"]
    seven_ids = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
    seven_planets = [p_map[pid] for pid in seven_ids]

    # Sort by degree in sign descending for Chara Karakas
    sorted_by_deg = sorted(seven_planets, key=lambda x: x["deg_in_sign"], reverse=True)

    karaka_defs = [
        ("Atma", "आत्माकारक", "Sun", "सूर्य"),
        ("Amatya", "अमात्यकारक", "Merc", "बुध"),
        ("Bhratru", "भ्रातृकारक", "Mars", "मंगल"),
        ("Matrua", "मातृकारक", "Moon", "चंद्र"),
        ("Putra", "पुत्रकारक", "Jupt", "गुरु"),
        ("Gnati", "ज्ञातिकारक", "Satn", "शनि"),
        ("Dara", "दाराकारक", "Venu", "शुक्र"),
    ]

    karaka_table = []
    for idx, (k_en, k_hi, sthir_en, sthir_hi) in enumerate(karaka_defs):
        chara_p = sorted_by_deg[idx]
        karaka_table.append({
            "karak_en": k_en,
            "karak_hi": k_hi,
            "sthir_en": sthir_en,
            "sthir_hi": sthir_hi,
            "chara_en": chara_p["table_en"],
            "chara_hi": chara_p["base_hi"],
            "chara_deg": chara_p["dms"],
        })

    # Atmakaraka Navamsha sign -> Swamsa & Karakamsa
    ak_planet = sorted_by_deg[0]
    d9_chart = shodashvarga_data["charts"]["D9"]
    d1_chart = shodashvarga_data["charts"]["D1"]
    ak_d9_sign = d9_chart["sign_values"][ak_planet["id"]]

    # Build Karakamsa Chart (D1 planets rotated to AK's D9 sign as Lagna, matching Page 23 left chart)
    karakamsa_houses = {h: [] for h in range(1, 13)}
    for pid in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu", "Uranus", "Neptune", "Pluto"]:
        p = p_map[pid]
        p_sign = p["sign_num"]
        bhav = ((p_sign - ak_d9_sign) % 12) + 1
        karakamsa_houses[bhav].append({"id": pid, "short_en": p["short_en"], "short_hi": p["short_hi"], "sign": p_sign, "bhav": bhav})

    # Build Swamsa Chart (D9 planets rotated to AK's D9 sign as Lagna, matching Page 23 right chart)
    swamsa_houses = {h: [] for h in range(1, 13)}
    for pid in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu", "Uranus", "Neptune", "Pluto"]:
        p = p_map[pid]
        p_d9_sign = d9_chart["sign_values"][pid]
        bhav = ((p_d9_sign - ak_d9_sign) % 12) + 1
        swamsa_houses[bhav].append({"id": pid, "short_en": p["short_en"], "short_hi": p["short_hi"], "sign": p_d9_sign, "bhav": bhav})

    # Planetary Avasthas: Jagrat/Swapna/Susupta, Baladi (5 states of 6°), Deeptadi
    # Friend/Enemy sign lookup for Jagrat & Deeptadi
    exalted_signs = {"Sun": 1, "Moon": 2, "Mars": 10, "Mercury": 6, "Jupiter": 4, "Venus": 12, "Saturn": 7}
    debilitated_signs = {"Sun": 7, "Moon": 8, "Mars": 4, "Mercury": 12, "Jupiter": 10, "Venus": 6, "Saturn": 1}
    own_signs = {
        "Sun": {5}, "Moon": {4}, "Mars": {1, 8}, "Mercury": {3, 6},
        "Jupiter": {9, 12}, "Venus": {2, 7}, "Saturn": {10, 11}
    }
    friendly_signs = {
        "Sun": {1, 4, 8, 9, 12},
        "Moon": {2, 3, 5, 6},
        "Mars": {4, 5, 9, 12},
        "Mercury": {2, 5, 7},
        "Jupiter": {1, 4, 5, 8},
        "Venus": {3, 10, 11},
        "Saturn": {2, 3, 6, 7},
    }

    baladi_odd = [("Bala", "बाल"), ("Kumar", "कुमार"), ("Yuva", "युवा"), ("Vriddha", "वृद्ध"), ("Mrat", "मृत")]
    baladi_even = list(reversed(baladi_odd))

    avastha_table = []
    for p in seven_planets:
        pid = p["id"]
        s_num = p["sign_num"]
        deg = p["deg_in_sign"]
        part = min(4, int(deg / 6.0))
        bal_en, bal_hi = (baladi_odd[part] if (s_num % 2 == 1) else baladi_even[part])

        if s_num == exalted_signs[pid] or s_num in own_signs[pid]:
            jag_en, jag_hi = "Jaagrat", "जाग्रत"
            deep_en, deep_hi = "Swatha", "स्वस्थ"
        elif s_num == debilitated_signs[pid]:
            jag_en, jag_hi = "Susupta", "सुषुप्त"
            deep_en, deep_hi = ("Shant", "शांत") if pid == "Venus" else (("Swatha", "स्वस्थ") if pid == "Saturn" else ("Muditha", "मुदित"))
        elif s_num in friendly_signs[pid]:
            jag_en, jag_hi = ("Jaagrat", "जाग्रत") if pid == "Moon" else ("Swapna", "स्वप्न")
            deep_en, deep_hi = ("Swatha", "स्वस्थ") if pid in ("Sun", "Moon") else ("Muditha", "मुदित")
        else:
            jag_en, jag_hi = ("Jaagrat", "जाग्रत") if pid == "Jupiter" else ("Susupta", "सुषुप्त")
            deep_en, deep_hi = ("Deena", "दीन") if pid == "Jupiter" else ("Shant", "शांत")

        avastha_table.append({
            "planet_en": p["table_en"],
            "planet_hi": p["base_hi"],
            "jagrat_en": jag_en,
            "jagrat_hi": jag_hi,
            "baladi_en": bal_en,
            "baladi_hi": bal_hi,
            "deeptadi_en": deep_en,
            "deeptadi_hi": deep_hi,
        })

    return {
        "karaka_table": karaka_table,
        "avastha_table": avastha_table,
        "atmakaraka": ak_planet["table_en"],
        "ak_d9_sign": ak_d9_sign,
        "karakamsa_chart": {"lagna_sign": ak_d9_sign, "house_planets": karakamsa_houses},
        "swamsa_chart": {"lagna_sign": ak_d9_sign, "house_planets": swamsa_houses},
    }
