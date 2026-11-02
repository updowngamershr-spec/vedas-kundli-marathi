# -*- coding: utf-8 -*-
"""
Module 8: Shodashvarga (16 Divisional Charts) Engine
Calculates all 16 Parashari divisional charts:
D1 (Rashi), D2 (Hora), D3 (Drekkana), D4 (Chaturthamsha), D7 (Saptamsha),
D9 (Navamsha), D10 (Dashamsha), D12 (Dwadamsha), D16 (Shodashamsha),
D20 (Vimshamsha), D24 (Chaturvimshamsha), D27 (Saptavimshamsha/Bhamsha),
D30 (Trimshamsha), D40 (Khavedamsha), D45 (Akshavedamsha), D60 (Shashtiamsha).
Follows traditional odd/even sign division rules strictly.
"""

SHODASHVARGA_INFO = [
    {"code": "D1", "num": 1, "name_en": "Rashi", "name_mr": "राशी", "area_mr": "शारीरिक शरीर व सामान्य जीवन"},
    {"code": "D2", "num": 2, "name_en": "Hora", "name_mr": "होरा", "area_mr": "संपत्ती, धन व समृद्धी"},
    {"code": "D3", "num": 3, "name_en": "Drekkana", "name_mr": "द्रेष्काण", "area_mr": "भावंडे, धैर्य व पराक्रम"},
    {"code": "D4", "num": 4, "name_en": "Chaturthamsha", "name_mr": "चतुर्थांश", "area_mr": "भाग्य, स्थावर मालमत्ता व निवास"},
    {"code": "D7", "num": 7, "name_en": "Saptamsha", "name_mr": "सप्तांश", "area_mr": "संतती, मुले व वंश वृद्धी"},
    {"code": "D9", "num": 9, "name_en": "Navamsha", "name_mr": "नवांश", "area_mr": "वैवाहिक जीवन, जोडीदार व धर्म"},
    {"code": "D10", "num": 10, "name_en": "Dashamsha", "name_mr": "दशांश", "area_mr": "कारकीर्द, व्यवसाय, यश व सन्मान"},
    {"code": "D12", "num": 12, "name_en": "Dwadamsha", "name_mr": "द्वादशांश", "area_mr": "आई-वडील व पूर्वज"},
    {"code": "D16", "num": 16, "name_en": "Shodashamsha", "name_mr": "षोडशांश", "area_mr": "वाहने, भौतिक सुखे व प्रवास"},
    {"code": "D20", "num": 20, "name_en": "Vimshamsha", "name_mr": "विंशांश", "area_mr": "आध्यात्मिक प्रगती व उपासना"},
    {"code": "D24", "num": 24, "name_en": "Chaturvimshamsha", "name_mr": "चतुर्विंशांश", "area_mr": "उच्च शिक्षण, ज्ञान व विद्या"},
    {"code": "D27", "num": 27, "name_en": "Saptavimshamsha", "name_mr": "सप्तविंशांश", "area_mr": "शक्ती, सामर्थ्य व दुर्बलता"},
    {"code": "D30", "num": 30, "name_en": "Trimshamsha", "name_mr": "त्रिंशांश", "area_mr": "अरिष्ट, संकटे व पाप-पुण्य फळ"},
    {"code": "D40", "num": 40, "name_en": "Khavedamsha", "name_mr": "खवेदांश", "area_mr": "शुभ व अशुभ घटना"},
    {"code": "D45", "num": 45, "name_en": "Akshavedamsha", "name_mr": "अक्षवेदांश", "area_mr": "चरित्र, नैतिकता व सर्वसाधारण फळ"},
    {"code": "D60", "num": 60, "name_en": "Shashtiamsha", "name_mr": "षष्ट्यंश", "area_mr": "सूक्ष्म प्रारब्ध व पूर्वजन्माचे संचित"},
]


def calc_varga_sign(sid_lon: float, varga_code: str) -> int:
    """
    Calculate zodiac sign number (1..12) for any sidereal longitude (0..360)
    in any of the 16 Shodashvarga charts.
    """
    sid_lon = sid_lon % 360.0
    sign_idx = int(sid_lon // 30.0) % 12  # 0..11
    sign_num = sign_idx + 1              # 1..12
    deg = sid_lon % 30.0                 # 0..30
    is_odd = (sign_num % 2 == 1)

    if varga_code == "D1":
        return sign_num

    elif varga_code == "D2":  # Hora: Odd signs: 0-15 Sun (5), 15-30 Moon (4); Even signs: 0-15 Moon (4), 15-30 Sun (5)
        if is_odd:
            return 5 if deg < 15.0 else 4
        else:
            return 4 if deg < 15.0 else 5

    elif varga_code == "D3":  # Drekkana: 1st 10° same, 2nd 10° 5th, 3rd 10° 9th
        part = min(2, int(deg / 10.0))
        return ((sign_idx + part * 4) % 12) + 1

    elif varga_code == "D4":  # Chaturthamsha: parts of 7.5°
        part = min(3, int(deg / 7.5))
        return ((sign_idx + part * 3) % 12) + 1

    elif varga_code == "D7":  # Saptamsha: parts of 30/7°
        part = min(6, int(deg * 7.0 / 30.0))
        start_idx = sign_idx if is_odd else (sign_idx + 6) % 12
        return ((start_idx + part) % 12) + 1

    elif varga_code == "D9":  # Navamsha: parts of 3°20'
        part = min(8, int(deg * 9.0 / 30.0))
        elem = sign_idx % 4  # Fire (0)->Aries, Earth (1)->Cap, Air (2)->Lib, Water (3)->Can
        starts = [0, 9, 6, 3]
        return ((starts[elem] + part) % 12) + 1

    elif varga_code == "D10":  # Dashamsha: parts of 3°
        part = min(9, int(deg * 10.0 / 30.0))
        start_idx = sign_idx if is_odd else (sign_idx + 8) % 12
        return ((start_idx + part) % 12) + 1

    elif varga_code == "D12":  # Dwadamsha: parts of 2.5°
        part = min(11, int(deg * 12.0 / 30.0))
        return ((sign_idx + part) % 12) + 1

    elif varga_code == "D16":  # Shodashamsha: parts of 1°52'30"
        part = min(15, int(deg * 16.0 / 30.0))
        # Moveable (1,4,7,10)->Aries, Fixed (2,5,8,11)->Leo, Dual (3,6,9,12)->Sagittarius
        m_type = sign_idx % 3
        starts = [0, 4, 8]
        return ((starts[m_type] + part) % 12) + 1

    elif varga_code == "D20":  # Vimshamsha: parts of 1.5°
        part = min(19, int(deg * 20.0 / 30.0))
        # Moveable->Aries, Fixed->Sagittarius, Dual->Leo
        m_type = sign_idx % 3
        starts = [0, 8, 4]
        return ((starts[m_type] + part) % 12) + 1

    elif varga_code == "D24":  # Chaturvimshamsha: parts of 1°15'
        part = min(23, int(deg * 24.0 / 30.0))
        start_idx = 4 if is_odd else 3  # Odd->Leo (5), Even->Cancer (4)
        return ((start_idx + part) % 12) + 1

    elif varga_code == "D27":  # Saptavimshamsha / Bhamsha: parts of 1°06'40"
        part = min(26, int(deg * 27.0 / 30.0))
        elem = sign_idx % 4  # Fire->Aries, Earth->Cancer, Air->Libra, Water->Cap
        starts = [0, 3, 6, 9]
        return ((starts[elem] + part) % 12) + 1

    elif varga_code == "D30":  # Trimshamsha
        # Odd: 0-5 Mars (1), 5-10 Saturn (11), 10-18 Jupiter (9), 18-25 Mercury (3), 25-30 Venus (7)
        # Even: 0-5 Venus (2), 5-12 Mercury (6), 12-20 Jupiter (12), 20-25 Saturn (10), 25-30 Mars (8)
        if is_odd:
            if deg < 5.0: return 1
            elif deg < 10.0: return 11
            elif deg < 18.0: return 9
            elif deg < 25.0: return 3
            else: return 7
        else:
            if deg < 5.0: return 2
            elif deg < 12.0: return 6
            elif deg < 20.0: return 12
            elif deg < 25.0: return 10
            else: return 8

    elif varga_code == "D40":  # Khavedamsha: parts of 45'
        part = min(39, int(deg * 40.0 / 30.0))
        start_idx = 0 if is_odd else 6  # Odd->Aries (1), Even->Libra (7)
        return ((start_idx + part) % 12) + 1

    elif varga_code == "D45":  # Akshavedamsha: parts of 40'
        part = min(44, int(deg * 45.0 / 30.0))
        m_type = sign_idx % 3  # Moveable->Aries, Fixed->Leo, Dual->Sagittarius
        starts = [0, 4, 8]
        return ((starts[m_type] + part) % 12) + 1

    elif varga_code == "D60":  # Shashtiamsha: parts of 30'
        part = min(59, int(deg * 60.0 / 30.0))
        return ((sign_idx + part) % 12) + 1

    return sign_num


def compute_shodashvarga(planets_list: list, asc_sid_lon: float) -> dict:
    """
    Compute planetary positions and house distributions for all 16 divisional charts.
    """
    charts = {}

    for v_info in SHODASHVARGA_INFO:
        code = v_info["code"]
        asc_varga_sign = calc_varga_sign(asc_sid_lon, code)
        house_planets = {h: [] for h in range(1, 13)}
        planet_signs = {}

        for p in planets_list:
            pid = p["id"]
            p_varga_sign = calc_varga_sign(p["sid_lon"], code)
            planet_signs[pid] = p_varga_sign
            # Whole sign house in this varga: ((p_sign - asc_sign + 12) % 12) + 1
            v_house = ((p_varga_sign - asc_varga_sign + 12) % 12) + 1
            house_planets[v_house].append({
                "id": pid,
                "name_mr": p["name_mr"],
                "short_mr": p["short_mr"],
                "sign_num": p_varga_sign,
                "house": v_house,
            })

        charts[code] = {
            "code": code,
            "name_en": v_info["name_en"],
            "name_mr": v_info["name_mr"],
            "area_mr": v_info["area_mr"],
            "lagna_sign": asc_varga_sign,
            "planet_signs": planet_signs,
            "house_planets": house_planets,
        }

    return {
        "charts": charts,
        "vargas_meta": SHODASHVARGA_INFO,
    }
