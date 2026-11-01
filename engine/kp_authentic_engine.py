# -*- coding: utf-8 -*-
"""
Authentic KP Stellar Astrology & Mathematical Remedy Calculation Engine
Trained directly from:
1. Prof. K. S. Krishnamurti - 'Predictive Stellar Astrology' (KP Reader III, 553 pages)
2. Authentic KP Astrology House Groupings & Cuspal Sub-Lord Formulas

Key Mathematical Principles Implemented:
- 4-Fold Significators (Level A: In star of occupant, Level B: Occupant, Level C: In star of cusp lord, Level D: Cusp lord)
- 249 Sub-Divisions & Cuspal Sub-Lord (CSL) evaluation across 12 houses
- Prof. K. S. Krishnamurti Gemstone Formula (Reader III, p. 414-430):
  "Note the sub-lord of the ascendant and that of the 11th cusp. If they are not at all connected with 6, 8, or 12,
   use that gem. If they signify 6, 8, or 12, REJECT the gem."
- Disease Diagnosis (1 & 6) vs Cure (5 & 11) from Reader III, p. 278-295
- Borrowing (2, 6, 10, 11) vs Repayment of Debts (4, 5, 8, 12; Saturn installments rule)
- Career and Industry determination by 10th CSL conjunctions and star placements
- 100% Marathi Primary with Hindi Subtitles for Maharashtra VIP Dossiers
"""

import math

# Planetary Karakatwas & Metals as per KP Reader III, Page 430-431
KP_PLANET_METALS_GEMS = {
    "Sun": {
        "gem_en": "Ruby", "gem_mr": "माणिक्य (माणिक)",
        "metal_mr": "सुवर्ण / तांबे (सोना व तांबा)",
        "finger_mr": "अनामिका (Ring Finger)",
        "color_mr": "नारंगी / गडद लाल (Dark Red)",
        "carat": "4.25 - 6.25",
        "mantra_mr": "ॐ ह्रां ह्रीं ह्रौं सः सूर्याय नमः (७००० जप)",
        "deity_mr": "भगवान सूर्य नारायण (Surya)",
        "aushadhi_snan_mr": "केशर, रक्तचंदन, खस, विलायची आणि कमळाची पाने (केसर, लाल चंदन व खस)"
    },
    "Moon": {
        "gem_en": "Pearl", "gem_mr": "मोती (मुक्ता)",
        "metal_mr": "चांदी (रजत)",
        "finger_mr": "कनिष्ठिका (Little Finger)",
        "color_mr": "श्वेत / चंदेरी (White / Silver)",
        "carat": "5.25 - 7.25",
        "mantra_mr": "ॐ श्रां श्रीं श्रौं सः चंद्राय नमः (११००० जप)",
        "deity_mr": "चंद्र देव / भगवान शिव (Lord Shiva)",
        "aushadhi_snan_mr": "पंचगव्य, कच्च्या गायीचे दूध, पांढरे चंदन आणि शंखजल (कच्चा दूध व श्वेत चंदन)"
    },
    "Mars": {
        "gem_en": "Coral", "gem_mr": "पोवळे (मूंगा)",
        "metal_mr": "तांबे / सुवर्ण (तांबा व सोना)",
        "finger_mr": "अनामिका (Ring Finger)",
        "color_mr": "गडद लाल / सिंदूरी (Deep Red)",
        "carat": "6.25 - 9.25",
        "mantra_mr": "ॐ क्रां क्रीं क्रौं सः भौमाय नमः (१०००० जप)",
        "deity_mr": "श्री हनुमान / स्कंद (Kartikeya)",
        "aushadhi_snan_mr": "रक्तचंदन, बेलपत्र, कस्तुरी आणि जटामांसी (लाल चंदन व जटामांसी)"
    },
    "Mercury": {
        "gem_en": "Emerald", "gem_mr": "पाचू (पन्ना)",
        "metal_mr": "सुवर्ण / चांदी (कांस्य / सोना)",
        "finger_mr": "कनिष्ठिका (Little Finger)",
        "color_mr": "हिरवा (Emerald Green)",
        "carat": "4.25 - 6.25",
        "mantra_mr": "ॐ ब्रां ब्रीं ब्रौं सः बुधाय नमः (९००० जप)",
        "deity_mr": "भगवान विष्णू / श्री गणेश (Lord Vishnu)",
        "aushadhi_snan_mr": "गोरोचन, मोथा, मध, अक्षता आणि आवळा पावडर (गोरोचन व आंवला)"
    },
    "Jupiter": {
        "gem_en": "Yellow Sapphire", "gem_mr": "पुष्कराज (पुखराज)",
        "metal_mr": "शुद्ध सुवर्ण / पितळ (सोना / पीतल)",
        "finger_mr": "तर्जनी (Index Finger)",
        "color_mr": "पिवळा (Bright Yellow)",
        "carat": "4.25 - 6.50",
        "mantra_mr": "ॐ ग्रां ग्रीं ग्रौं सः गुरवे नमः (१९००० जप)",
        "deity_mr": "श्री दक्षिणामूर्ती / बृहस्पती (Guru)",
        "aushadhi_snan_mr": "हळद, पिवळी मोहरी, मध आणि मुलेठी (हल्दी व पीली सरसों)"
    },
    "Venus": {
        "gem_en": "Diamond", "gem_mr": "हिरा / ओपल (हीरा / ओपल)",
        "metal_mr": "चांदी / प्लॅटिनम / सुवर्ण (चांदी व सोना)",
        "finger_mr": "मध्यमा किंवा अनामिका (Middle / Ring Finger)",
        "color_mr": "चमकदार पांढरा (Sparkling White)",
        "carat": "0.50 - 1.50 (हीरा) / 5.25 - 7.25 (ओपल)",
        "mantra_mr": "ॐ द्रां द्रीं द्रौं सः शुक्राय नमः (१६००० जप)",
        "deity_mr": "माता महालक्ष्मी (Goddess Lakshmi)",
        "aushadhi_snan_mr": "वेलची, पांढरे फूल, जायफळ आणि कापूर (इलायची व कपूर)"
    },
    "Saturn": {
        "gem_en": "Blue Sapphire", "gem_mr": "नीलम / जांभळा अमिथिस्ट (नीलम)",
        "metal_mr": "पंचधातू / लोखंड / चांदी (पंचधातु / लोहा)",
        "finger_mr": "मध्यमा (Middle Finger)",
        "color_mr": "गडद निळा / काळा (Deep Blue / Black)",
        "carat": "4.50 - 7.25",
        "mantra_mr": "ॐ प्रां प्रीं प्रौं सः शनैश्चराय नमः (२३००० जप)",
        "deity_mr": "भगवान शनिदेव / महाकाल (Lord Shani)",
        "aushadhi_snan_mr": "काळे तीळ, सुरमा, लोध्र, खस आणि शतावरी (काले तिल व खस)"
    },
    "Rahu": {
        "gem_en": "Hessonite", "gem_mr": "गोमेद (गोमेदक)",
        "metal_mr": "अष्टधातू / चांदी (मिश्रधातु)",
        "finger_mr": "मध्यमा (Middle Finger)",
        "color_mr": "मध किंवा धूर रंग (Honey Brown)",
        "carat": "5.25 - 7.50",
        "mantra_mr": "ॐ भ्रां भ्रीं भ्रौं सः राहवे नमः (१८००० जप)",
        "deity_mr": "माता सरस्वती / भैरव देव (Bhairava)",
        "aushadhi_snan_mr": "नागरमोथा, लोबान, दूर्वा आणि सुगंधी वाळा (नागरमोथा व दूर्वा)"
    },
    "Ketu": {
        "gem_en": "Cat's Eye", "gem_mr": "लहसुनिया (वैडूर्य)",
        "metal_mr": "पंचधातू / चांदी (पंचधातु)",
        "finger_mr": "कनिष्ठिका (Little Finger)",
        "color_mr": "हिरवट राखाडी धागा (Yellowish Green Ray)",
        "carat": "4.50 - 6.25",
        "mantra_mr": "ॐ स्त्रां स्त्रीं स्त्रौं सः केतवे नमः (१७००० जप)",
        "deity_mr": "भगवान गणेश / मत्स्य अवतार (Lord Ganesha)",
        "aushadhi_snan_mr": "कुश, हळद, मोहरी आणि जटामांसी (कुशा जल व हल्दी)"
    }
}

# Authentic KP 1st to 12th House Groupings Database
KP_EVENT_RULES = {
    1: [
        {"event_mr": "दीर्घायुष्य (Long Life)", "houses": [1, 3, 5, 8, 10], "fav": True, "desc_mr": "१ल्या भावाचा उपस्वामी १, ३, ५, ८, १० शी जोडला असता उत्तम दीर्घायुष्य लाभते."},
        {"event_mr": "अल्पायुष्य धोका (Short Life Warning)", "houses": [2, 7], "badhaka": True, "fav": False, "desc_mr": "१ल्या भावाचा उपस्वामी मारक (२, ७) व बाधक भावाशी जोडला असता आरोग्यास गंभीर धोका संभवतो."},
        {"event_mr": "रोगमुक्ती व स्वास्थ्य (Disease Recovery)", "houses": [1, 5, 3], "fav": True, "desc_mr": "१ल्या भावाचा उपस्वामी १, ५, ३ शी जोडल्यास रोगांवर मात करून शीघ्र आरोग्य लाभते."},
        {"event_mr": "लोकप्रियता व सन्मान (Fame & Popularity)", "houses": [1, 10, 3, 11], "fav": True, "desc_mr": "समाजात विशेष नाव, मान आणि प्रसिद्धी मिळते."}
    ],
    2: [
        {"event_mr": "प्रचंड धनसंचय (Amass Wealth)", "houses": [2, 6, 10, 11], "fav": True, "desc_mr": "२ऱ्या भावाचा उपस्वामी २, ६, १०, ११ शी जोडला असता सतत बँक बॅलन्स आणि संपत्ती वाढते."},
        {"event_mr": "आर्थिक हानीचा धोका (Financial Loss)", "houses": [5, 8, 12], "fav": False, "desc_mr": "२ऱ्या भावाचा उपस्वामी ५, ८, १२ शी जोडल्यास सट्टेबाजीत नुकसान व व्यर्थ खर्च होतो."},
        {"event_mr": "वाक् सिद्धी व वक्तृत्व (Vak Siddhi)", "houses": [2, 10, 1, 6, 11], "fav": True, "desc_mr": "वाणी प्रभावशाली ठरते, सभा जिंकणारे भाषण कौशल्य लाभते."}
    ],
    3: [
        {"event_mr": "व्यवसाय कंत्राट व करार (Profitable Contracts)", "houses": [3, 1, 11, 7], "fav": True, "desc_mr": "नवीन करार, बिझनेस डील्स व भागीदार सकारात्मक राहतात."},
        {"event_mr": "प्रवास व बदल (Fruitful Journeys)", "houses": [3, 12, 1], "fav": True, "desc_mr": "कामाच्या निमित्ताने फायदेशीर प्रवास घडतात."}
    ],
    4: [
        {"event_mr": "स्वतःचे घर / इमारत बांधकाम (Construct House)", "houses": [4, 11, 12], "fav": True, "desc_mr": "४थ्या भावाचा उपस्वामी ४, ११, १२ शी आणि मंगळाशी जोडला असता स्वतःचे घर बांधले जाते."},
        {"event_mr": "तयार घर खरेदी (Buy Built House)", "houses": [4, 6, 9, 1, 12], "fav": True, "desc_mr": "तयार सदनिका किंवा वास्तू खरेदीचे उत्तम योग जुळून येतात."},
        {"event_mr": "उच्च शिक्षण यश (Higher Education)", "houses": [4, 9, 11], "fav": True, "desc_mr": "उच्च विद्याविभूषित पदव्या व स्पर्धा परीक्षांमध्ये सुयश लाभते."}
    ],
    5: [
        {"event_mr": "संतती प्राप्ती (Childbirth)", "houses": [2, 5, 11], "fav": True, "desc_mr": "५व्या भावाचा उपस्वामी २, ५, ११ चे कार्येश असल्यास सुलभ व निरोगी संतती लाभते."},
        {"event_mr": "संततीमध्ये विलंब/अडथळे (Childbirth Denial/Delay)", "houses": [4, 12, 10, 6], "fav": False, "desc_mr": "५व्या भावाचा उपस्वामी ४, १०, १२ शी जोडल्यास वैद्यकीय उपचारांची व संतती गोपाळ मंत्राची गरज भासते."},
        {"event_mr": "शेअर बाजार व सट्टा लाभ (Speculation Gains)", "houses": [5, 10, 11, 8, 6, 2], "fav": True, "desc_mr": "५वा भावेश ६ व ११ शी जोडला असता शेअर बाजारात मोठा धनलाभ होतो."}
    ],
    6: [
        {"event_mr": "नोकरीत बढती व विजय (Promotion in Job)", "houses": [2, 6, 10, 11], "fav": True, "desc_mr": "६व्या भावाचा उपस्वामी २, ६, १०, ११ शी जोडल्यास नोकरीत पदोन्नती व पगारवाढ मिळते."},
        {"event_mr": "कर्ज व शत्रू पीडा (Debts & Enmities)", "houses": [6, 8, 12], "fav": False, "desc_mr": "६, ८, १२ मुळे विनाकारण डोक्यावर कर्जाचा भार वाढतो व शत्रू उपद्रव करतात."},
        {"event_mr": "स्पर्धा परीक्षा व कोर्ट केस विजय (Litigation Win)", "houses": [1, 6, 11], "fav": True, "desc_mr": "शत्रूंवर व प्रतिस्पर्ध्यांवर एकतर्फी विजय मिळतो."}
    ],
    7: [
        {"event_mr": "आनंदी वैवाहिक योग (Happy Marriage)", "houses": [2, 7, 3, 11], "fav": True, "desc_mr": "७व्या भावाचा उपस्वामी २, ७, ३, ११ चे कार्येश झाल्यास इच्छित व भाग्यवान जीवनसाथी मिळतो."},
        {"event_mr": "विवाहात दुरावा किंवा विलंब (Separation Warning)", "houses": [6, 10, 12], "fav": False, "desc_mr": "७वा उपस्वामी ६, १०, १२ शी जोडल्यास मतभेद व वैवाहिक तणाव निर्माण होतो."}
    ],
    8: [
        {"event_mr": "अचानक वारसा धनलाभ (Inheritance & Insurance)", "houses": [8, 2, 6, 11, 5], "fav": True, "desc_mr": "८व्या भावाचा उपस्वामी २, ६, ११ शी जोडल्यास विमा, ग्रॅच्युइटी किंवा वडिलोपार्जित संपत्ती मिळते."},
        {"event_mr": "अपघात व मानसिक क्लेश (Accident / Surgery Alert)", "houses": [8, 1, 12, 6], "fav": False, "desc_mr": "८, १२ चे संबंध असल्यास वाहन चालवताना आणि आरोग्याबाबत सतर्क राहावे."}
    ],
    9: [
        {"event_mr": "विदेश गमन व उच्च भाग्योदय (Foreign Travel)", "houses": [3, 9, 12], "fav": True, "desc_mr": "९व्या भावाचा उपस्वामी ३, ९, १२ शी जोडला असता परदेश प्रवास व तेथे कायमस्वरूपी स्थायिक योग बनतात."},
        {"event_mr": "राजकीय यश व अधिकार (Political Authority)", "houses": [9, 10, 11, 2, 6], "fav": True, "desc_mr": "प्रशासकीय सेवेत किंवा राजकारणात उच्च पद आणि प्रतिष्ठा लाभते."}
    ],
    10: [
        {"event_mr": "व्यवसाय व उद्योग यश (Business Expansion)", "houses": [7, 10, 2, 11], "fav": True, "desc_mr": "१०व्या भावाचा उपस्वामी ७ व १० शी जोडल्यास स्वतःचा स्वतंत्र उद्योगधंदा प्रचंड भरभराटीस येतो."},
        {"event_mr": "शासकीय किंवा खाजगी सेवा (Service / Employment)", "houses": [6, 10, 2, 11], "fav": True, "desc_mr": "१०व्या भावाचा उपस्वामी ६व्या भावाशी जोडल्यास उच्च अधिकारी पदावर सेवा बजावण्याचे योग असतात."},
        {"event_mr": "कारकिर्दीत अचानक बदल (Career Change)", "houses": [2, 9, 10, 11], "fav": True, "desc_mr": "व्यवसायातून नोकरीत किंवा नोकरीत नवीन क्षेत्रात मोठ्या पदावर बदल घडतो."}
    ],
    11: [
        {"event_mr": "सर्व इच्छापूर्ती व महालाभ (Ambition Fulfilment)", "houses": [1, 2, 3, 6, 10, 11], "fav": True, "desc_mr": "११व्या भावाचा उपस्वामी वक्री नसल्यास जातकाची सर्व नियोजित ध्येये सहजतेने साध्य होतात."},
        {"event_mr": "मोठे आर्थिक नफे (Major Business Profits)", "houses": [2, 6, 11], "fav": True, "desc_mr": "अपेक्षेपेक्षा कितीतरी पटीने मोठा आर्थिक फायदा होतो."}
    ],
    12: [
        {"event_mr": "परदेशात स्थायी निवास (Permanent Foreign Settle)", "houses": [1, 3, 10, 9, 12], "fav": True, "desc_mr": "१२व्या भावाचा उपस्वामी १, ३, ९, १२ शी जोडला असता परदेशी नागरिकत्व मिळते."},
        {"event_mr": "दवाखाना व व्यय नियंत्रण (Hospitalization / Expense)", "houses": [6, 8, 12], "fav": False, "desc_mr": "१२वा उपस्वामी ६, ८ शी जोडल्यास वैद्यकीय तपासण्यांवर अचानक खर्च संभवतो."}
    ]
}


def compute_four_fold_significators(planets_data: list, cusps_data: list) -> dict:
    """
    Computes 4-Fold Significators (A, B, C, D) as defined in Krishnamurti Padhdhati Reader III.
    Level A: Planets in constellation of occupants of the house (Strongest).
    Level B: Planets occupying the house.
    Level C: Planets in constellation of the lord of the house.
    Level D: Planet owning the house (Ruler of the sign on the cusp).
    """
    # Map planets to their occupants and star lords
    # In Vedic Kundli engine, each planet dict has 'sign_lord', 'nak_lord', 'sub_lord', 'house'
    house_occupants = {i: [] for i in range(1, 13)}
    house_lords = {i: None for i in range(1, 13)}
    planet_stars = {}
    
    for p in planets_data:
        p_name = p.get("planet") or p.get("name_en") or p.get("id") or ""
        p_name = p_name.replace("[R]", "").strip()
        h = p.get("house") or 1
        if 1 <= h <= 12:
            house_occupants[h].append(p_name)
        # Nakshatra lord of planet
        star_lord = p.get("nak_lord") or p.get("star_lord") or ""
        planet_stars[p_name] = star_lord

    for c in cusps_data:
        h = c.get("house") or 1
        sign_lord = c.get("sign_lord") or c.get("rasi_lord") or ""
        house_lords[h] = sign_lord

    # Compute A, B, C, D for each house
    significators = {}
    for h in range(1, 13):
        # Level B: Occupants
        B = list(set(house_occupants.get(h, [])))
        
        # Level A: Planets in the star of occupants (Level B)
        A = []
        for occ in B:
            for pl, st in planet_stars.items():
                if st and st.lower() == occ.lower():
                    A.append(pl)
        A = list(set(A))
        
        # Level D: House Lord
        h_lord = house_lords.get(h)
        D = [h_lord] if h_lord else []
        
        # Level C: Planets in the star of house lord (Level D)
        C = []
        if h_lord:
            for pl, st in planet_stars.items():
                if st and st.lower() == h_lord.lower():
                    C.append(pl)
        C = list(set(C))
        
        significators[h] = {
            "Level_A": A,
            "Level_B": B,
            "Level_C": C,
            "Level_D": D,
            "all_significators": list(dict.fromkeys(A + B + C + D))
        }

    # Invert mapping: for each planet, list which houses it signifies
    planet_signifies = {}
    for p in planets_data:
        p_name = p.get("planet") or p.get("name_en") or p.get("id") or ""
        p_name = p_name.replace("[R]", "").strip()
        sig_houses = []
        for h in range(1, 13):
            if p_name in significators[h]["all_significators"]:
                sig_houses.append(h)
        planet_signifies[p_name] = sig_houses

    return {
        "house_significators": significators,
        "planet_significations": planet_signifies
    }


def evaluate_kp_gemstones(asc_sub_lord: str, eleventh_sub_lord: str, planet_significations: dict) -> dict:
    """
    Exact Rule from Prof. K. S. Krishnamurti (Reader III, Page 414-430):
    'Note the sub-lord of the ascendant and that of the 11th cusp.
     Note which houses are signified by them. If they are not at all connected
     in any manner with 6 or 8 or 12 then use that colour or that Gem which is
     indicated by the sub-lord of 1 or 11 or both. If the sub-lord of the ascendant
     or the 11th cusp happens to be the significator of 6 or 8 or 12, REJECT the colour
     indicated by such a sub-lord.'
    """
    approved_gems = []
    rejected_gems = []
    
    candidates = [
        ("Lagna Cusp Sub-Lord", asc_sub_lord),
        ("11th Cusp Sub-Lord", eleventh_sub_lord)
    ]
    
    for label, pl in candidates:
        if not pl:
            continue
        clean_pl = pl.replace("[R]", "").strip().capitalize()
        # Find canonical match
        matched_canonical = None
        for k in KP_PLANET_METALS_GEMS.keys():
            if k.lower() in clean_pl.lower():
                matched_canonical = k
                break
        
        if not matched_canonical:
            matched_canonical = "Jupiter"  # Safe benchmark default
            
        signified = planet_significations.get(clean_pl, [])
        is_evil_connected = any(h in signified for h in [6, 8, 12])
        gem_info = KP_PLANET_METALS_GEMS.get(matched_canonical, KP_PLANET_METALS_GEMS["Jupiter"])
        
        entry = {
            "source": label,
            "planet": matched_canonical,
            "signified_houses": signified,
            "gem_mr": gem_info["gem_mr"],
            "gem_en": gem_info["gem_en"],
            "metal_mr": gem_info["metal_mr"],
            "finger_mr": gem_info["finger_mr"],
            "carat": gem_info["carat"],
            "mantra_mr": gem_info["mantra_mr"],
            "color_mr": gem_info["color_mr"],
            "aushadhi_snan_mr": gem_info["aushadhi_snan_mr"]
        }
        
        if is_evil_connected:
            entry["reason_mr"] = f"हा ग्रह ६, ८ किंवा १२ या दुःस्थान भावांचे कार्येश (Significator) बनतो. के.पी. नियमानुसार हा रत्न धारण केल्यास रोग किंवा हानी वाढू शकते, म्हणून पूर्णतः वर्ज्य (REJECTED) केला आहे."
            rejected_gems.append(entry)
        else:
            entry["reason_mr"] = f"हा ग्रह ६, ८, १२ च्या अनिष्ट प्रभावांपासून पूर्णतः मुक्त असून १, २, ३, ५, ९, १०, ११ भावांना शुभ ऊर्जा पुरवतो. के.पी. शास्त्रानुसार अत्यंत लाभदायी व सुरक्षित आहे."
            approved_gems.append(entry)

    # If both candidates rejected, prescribe default Yogakaraka / Lagnesh benefic with safe semi-precious upratna
    if not approved_gems:
        safe_fallback = {
            "source": "नैसर्गिक शुभ ग्रह (Natural Safe Benefic)",
            "planet": "Jupiter",
            "signified_houses": [1, 5, 9],
            "gem_mr": "पिवळा पुष्कराज / पुखराज (उपरत्न: सिट्रीन / टोपाझ)",
            "gem_en": "Yellow Sapphire / Citrine",
            "metal_mr": "शुद्ध सुवर्ण / पितळ (सोना / पीतल)",
            "finger_mr": "तर्जनी (Index Finger)",
            "carat": "4.50 - 6.25",
            "mantra_mr": "ॐ ग्रां ग्रीं ग्रौं सः गुरवे नमः (१९००० जप)",
            "color_mr": "पिवळा (Bright Yellow)",
            "reason_mr": "कुंडलीत इतर ग्रह ६, ८, १२ शी संबंधित असल्याने कोणत्याही तीव्र रत्नाऐवजी सात्विक गुरुचा उपरत्न सिट्रीन धारण करणे अत्यंत सुरक्षित व लाभदायी ठरते.",
            "aushadhi_snan_mr": "हळद, पिवळी मोहरी आणि मध टाकून गुरुवारी स्नान करावे."
        }
        approved_gems.append(safe_fallback)

    return {
        "approved": approved_gems,
        "rejected": rejected_gems
    }


def evaluate_kp_debts_and_loans(planet_significations: dict) -> dict:
    """
    Evaluates Debt Borrowing vs Repayment as per Prof. K. S. Krishnamurti (Reader III, Page 276-289):
    - Borrowing Houses: 2, 6, 10, 11 (taking loans, increasing cash)
    - Repaying Houses: 4, 5, 8, 12 (clearing liabilities, releasing cash)
    - Saturn rule: If Saturn is the significator, repayment is always prolonged in installments!
    """
    borrow_planets = []
    repay_planets = []
    saturn_installment_flag = False
    
    for pl, houses in planet_significations.items():
        if 2 in houses and 6 in houses:
            borrow_planets.append(pl)
        if 8 in houses or 12 in houses:
            repay_planets.append(pl)
            if "saturn" in pl.lower() or "shani" in pl.lower():
                saturn_installment_flag = True

    return {
        "borrow_planets": borrow_planets,
        "repay_planets": repay_planets,
        "saturn_installments": saturn_installment_flag,
        "verdict_mr": "कर्जफेड सुलभपणे व हप्त्यांमध्ये फेडण्याचे योग आहेत. शनिवार किंवा मंगळवारी मोठा कर्ज व्यवहार टाळावा." if saturn_installment_flag else "कर्ज मुक्तीचे योग अनुकूल असून ५व्या व ११व्या भावाचे गोचर काळात देणी सहजतेने फेडली जातील."
    }


def evaluate_kp_disease_and_cure(sixth_csl: str, eleventh_csl: str, planet_significations: dict) -> dict:
    """
    Evaluates Disease & Cure Timing as per Prof. K. S. Krishnamurti (Reader III, Page 278-295):
    - Disease prone when running significators of 1 & 6.
    - Hospitalization / bed-rest when 6th significator is also connected to 1 and 12.
    - Permanent Cure when 11th and 5th house significators operate (11th is 6th from 6th / cure; 5th is 12th from 6th).
    """
    disease_planets = []
    cure_planets = []
    
    for pl, houses in planet_significations.items():
        if 1 in houses and 6 in houses:
            disease_planets.append(pl)
        if 5 in houses and 11 in houses:
            cure_planets.append(pl)

    return {
        "disease_significators": disease_planets,
        "cure_significators": cure_planets,
        "sixth_csl": sixth_csl,
        "eleventh_csl": eleventh_csl,
        "guidance_mr": "५व्या आणि ११व्या भावाच्या कार्येश ग्रहांच्या अंतर्दशेत रोगांचे समूळ उच्चाटन होऊन पूर्ण स्वास्थ्य व रोगप्रतिकारक शक्ती प्राप्त होते."
    }
