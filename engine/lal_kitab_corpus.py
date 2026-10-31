# -*- coding: utf-8 -*-
"""
Gurukulam Kundli CRM - Lal Kitab Hindi Corpus Decoder, Parser & Sutra Evaluator
Extracts and cleans all 108 (9 Planets x 12 Houses) Lal Kitab predictions & remedies,
Job & Promotion Dasha/Transit/Jaimini rules, and 60 Chamatkari Phaladesh Sutras
from 167329767-Lal-Kitab-Hindi.txt, and stores a permanent offline JSON database in E:\\Kundli crm\\data\\.
"""

import os
import re
import json


def clean_corrupted_devanagari(raw_text: str) -> str:
    """
    Deterministically reverses the legacy PDF-to-text glyph mapping corruption
    present in 167329767-Lal-Kitab-Hindi.txt.
    """
    s = raw_text.replace("\f", "\n")

    # Fix split multi-line words like "दस\nू रे" -> "दूसरे", "दख\nु ी" -> "दुखी", "दभ\nु ारग्य" -> "दुर्भाग्य"
    s = re.sub(r"दस\s*\n\s*ू\s*रे", "दूसरे", s)
    s = re.sub(r"दख\s*\n\s*ु\s*", "दुख", s)
    s = re.sub(r"दधि\s*\n\s*ू\s*", "दूध ", s)
    s = re.sub(r"दभ\s*\n\s*ु\s*ारग्य", "दुर्भाग्य", s)
    s = re.sub(r"संकट", "संकट", s)
    s = re.sub(r"सञ्चयक्ति\s*\n\s*ु", "संयुक्त", s)
    s = re.sub(r"संचयक्ति\s*\n\s*ु", "संयुक्त", s)
    s = re.sub(r"तुरत\s*\n\s*ंच", "तुरंत", s)
    s = re.sub(r"डबल कमाईड\s*\n\s*ंच", "डबल माइंड", s)

    # 1. Remove spurious 'क' inserted after whitespace before every word/number
    s = re.sub(r"(^|[\s\(\-\|—–,/])क(?=[\u0900-\u097F0-9])", r"\1", s)
    s = re.sub(r"\s+क(?=\s|$)", " ", s)

    # 2. Reverse multi-char glyph substitutions
    s = s.replace("पत", "प")
    s = s.replace("शि", "श")
    s = s.replace("थि", "थ")
    s = s.replace("धि", "ध")
    s = s.replace("ंच", "ं")
    s = s.replace("कि", "क")

    # 3. Move visual-order 'ि' (U+093F) placed before a consonant/conjunct to after it (RUN ONCE)
    s = re.sub(r"ि((?:[क-ह]\u094d)*[क-ह])", r"\1ि", s)

    # 4. Fix split reph & conjunct artifacts AFTER chhoti-i inversion
    replacements = {
        "ति स्थति": "स्थिति",
        "ति स्थत": "स्थित",
        "ति स्थर": "स्थिर",
        "अति स्थर": "अस्थिर",
        "नाति स्तक": "नास्तिक",
        "मति न्दर": "मन्दिर",
        "मिश्रति": "मिश्रित",
        "सूयर": "सूर्य",
        "धामिर ि": "धार्मिक",
        "धामिर क": "धार्मिक",
        "धामिरक": "धार्मिक",
        "आथिर ि": "आर्थिक",
        "आथिर क": "आर्थिक",
        "आथिरक": "आर्थिक",
        "वाषिर ि": "वार्षिक",
        "वाषिर क": "वार्षिक",
        "निमारण": "निर्माण",
        "दीघारय कु": "दीर्घायु",
        "दीघारयु": "दीर्घायु",
        "आशीवारद": "आशीर्वाद",
        "चतुथिर": "चतुर्थ",
        "चतुथर": "चतुर्थ",
        "अथिर": "अर्थ",
        "अथर": "अर्थ",
        "समथिर न": "समर्थन",
        "समथर न": "समर्थन",
        "निभर र": "निर्भर",
        "दगु ार": "दुर्गा",
        "अजिर त": "अर्जित",
        "कजर दार": "कर्जदार",
        "कजरदार": "कर्जदार",
        "कजार": "कर्जा",
        "चमर रोग": "चर्मरोग",
        "ल्यूकोडमार": "ल्यूकोडर्मा",
        "कमर चािरयों": "कर्मचारियों",
        "कमर चारियों": "कर्मचारियों",
        "कायर": "कार्य",
        "कायो ं मे": "कार्यों में",
        "कायो ं": "कार्यों",
        "मुगो ं को": "मुर्गों को",
        "दश्ु मनों": "दुश्मनों",
        "दष्ु प्रभाव": "दुष्प्रभाव",
        "दरू ": "दूर ",
        "दरू": "दूर",
        "दधू": "दूध",
        "दस ू रे": "दूसरे",
        "दसू रे": "दूसरे",
        "दसू रा": "दूसरा",
        "दख ु ी": "दुखी",
        "दखु ी": "दुखी",
        "दख ु": "दुख",
        "दखु": "दुख",
        "सयंच क्तु": "संयुक्त",
        "संचयक्तु": "संयुक्त",
        "पहु ँचाने": "पहुँचाने",
        "हु ए": "हुए",
        "हु ई": "हुई",
        "बहु त": "बहुत",
        "टु कड़ा": "टुकड़ा",
        "दृष्टस्टी": "दृष्टि",
        "अस्ट्मेश": "अष्टमेश",
        "पापतकिर री": "पापकर्तरी",
        "पतकिर री": "पापकर्तरी",
        "किर व्य": "कर्तव्य",
        "नपुंशक": "नपुंसक",
        "किरशा": "कर्कशा",
        "भिट्टयों": "भट्टियों",
        "वषर": "वर्ष",
        "धूतर": "धूर्त",
        "मूरति यां": "मूर्तियां",
        "मूरति": "मूर्ति",
        "प्रवति र": "प्रवृत्ति",
        "परिवतर न": "परिवर्तन",
        "अंतदर शानाथ": "अंतर्दशानाथ",
        "श्रिमसाध्य": "श्रमसाध्य",
        "श्रिोत": "स्रोत",
        " मे ": " में ",
        " मे\n": " में\n",
    }
    for k, v in replacements.items():
        s = s.replace(k, v)

    s = re.sub(r"\s+क(?=\s|$)", " ", s)
    s = re.sub(r"[ \t]+", " ", s)
    return s.strip()


HOUSE_WORD_TO_NUM = {
    "First": 1, "Second": 2, "Third": 3, "Fourth": 4,
    "Fifth": 5, "Sixth": 6, "Seventh": 7, "Eighth": 8,
    "Ninth": 9, "Tenth": 10, "Eleventh": 11, "Twelvth": 12, "Twelfth": 12,
}

PLANET_HI_NAMES = {
    "Sun": "सूर्य", "Moon": "चंद्रमा", "Mars": "मंगल", "Mercury": "बुध",
    "Jupiter": "बृहस्पति (गुरु)", "Venus": "शुक्र", "Saturn": "शनि",
    "Rahu": "राहु", "Ketu": "केतु"
}

HOUSE_HI_ORDINAL = {
    1: "पहले (प्रथम)", 2: "दूसरे (द्वितीय)", 3: "तीसरे (तृतीय)", 4: "चौथे (चतुर्थ)",
    5: "पांचवें (पंचम)", 6: "छठे (षष्ठ)", 7: "सातवें (सप्तम)", 8: "आठवें (अष्टम)",
    9: "नौवें (नवम)", 10: "दसवें (दशम)", 11: "ग्यारहवें (एकादश)", 12: "बारहवें (द्वादश)"
}


def build_lal_kitab_corpus(txt_path: str = None, out_json_path: str = None):
    """
    Parse the Lal Kitab text source and cache the cleaned corpus inside this project.
    Paths are resolved locally so the application does not depend on a missing E: drive
    or another Windows user's Downloads folder.
    """
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    data_dir = os.path.join(project_root, "data")

    if out_json_path is None:
        out_json_path = os.path.join(data_dir, "lal_kitab_hindi_cleaned.json")

    if txt_path is None:
        candidates = [
            os.path.join(data_dir, "167329767-Lal-Kitab-Hindi.txt"),
            os.path.join(project_root, "167329767-Lal-Kitab-Hindi.txt"),
            os.path.join(os.path.expanduser("~"), "Downloads", "167329767-Lal-Kitab-Hindi.txt"),
        ]
        txt_path = next((candidate for candidate in candidates if os.path.isfile(candidate)), candidates[0])

    os.makedirs(os.path.dirname(os.path.abspath(out_json_path)), exist_ok=True)

    # Use the cached database when the original source text is not present.
    if not os.path.isfile(txt_path) and os.path.isfile(out_json_path):
        with open(out_json_path, "r", encoding="utf-8") as f:
            return json.load(f)

    # Do not crash all Kundli generation if the optional source text has not been copied
    # to this machine. The rest of the report can still be generated without Lal Kitab data.
    if not os.path.isfile(txt_path):
        print(
            "WARNING: Lal Kitab source text was not found. "
            "Copy '167329767-Lal-Kitab-Hindi.txt' into the project's data folder "
            "to enable Lal Kitab corpus predictions."
        )
        return {"planet_house_predictions": {}, "extra_sutras_hi": ""}

    with open(txt_path, "r", encoding="utf-8") as source_file:
        raw_full = source_file.read()
    split_idx = raw_full.find("नौकिरी किनम्न")
    if split_idx != -1:
        main_part = raw_full[:split_idx]
        extra_part = raw_full[split_idx:]
    else:
        main_part = raw_full
        extra_part = ""

    pattern = re.compile(r"Prediction for ([A-Za-z]+) in ([A-Za-z]+) house in Hindi according to Lal Kitab")
    matches = list(pattern.finditer(main_part))

    corpus = {}
    for idx, m in enumerate(matches):
        planet = m.group(1)
        house_word = m.group(2)
        house_num = HOUSE_WORD_TO_NUM.get(house_word, 1)
        start_pos = m.end()
        end_pos = matches[idx + 1].start() if idx + 1 < len(matches) else len(main_part)
        chunk = main_part[start_pos:end_pos]
        # Remove the trailing next Hindi heading line if present
        chunk_lines = [ln for ln in chunk.splitlines() if "लाल किकिताब" not in ln and "अनुसार" not in ln and "===" not in ln]
        cleaned_chunk = clean_corrupted_devanagari("\n".join(chunk_lines))

        # Split into prediction paragraph(s) and remedies (उपाय:)
        if "उपाय:" in cleaned_chunk:
            pred_part, rem_part = cleaned_chunk.split("उपाय:", 1)
        else:
            pred_part, rem_part = cleaned_chunk, ""

        pred_text = " ".join(ln.strip() for ln in pred_part.splitlines() if ln.strip())
        # Parse numbered remedies (1) ... (2) ...
        rem_items = []
        for rm in re.split(r"\(\d+\)", rem_part):
            rm_clean = " ".join(ln.strip() for ln in rm.splitlines() if ln.strip())
            if rm_clean:
                rem_items.append(rm_clean)

        key = f"{planet}_{house_num}"
        corpus[key] = {
            "planet": planet,
            "planet_hi": PLANET_HI_NAMES.get(planet, planet),
            "house": house_num,
            "title_hi": f"लाल किताब के अनुसार {PLANET_HI_NAMES.get(planet, planet)} का {HOUSE_HI_ORDINAL[house_num]} भाव में फल",
            "title_en": f"{planet} in your {house_num}{'st' if house_num==1 else 'nd' if house_num==2 else 'rd' if house_num==3 else 'th'} house:",
            "prediction_hi": pred_text,
            "remedies_hi": rem_items,
        }

    # Add Sun_9 (9th house Sun in Lal Kitab) which was missing in the raw text file
    if "Sun_9" not in corpus:
        corpus["Sun_9"] = {
            "planet": "Sun",
            "planet_hi": "सूर्य",
            "house": 9,
            "title_hi": "लाल किताब के अनुसार सूर्य का नौवें (नवम) भाव में फल",
            "title_en": "Sun in your 9th house:",
            "prediction_hi": (
                "नवम भाव बृहस्पति का पक्का घर है जो सूर्य का मित्र है। यदि सूर्य यहाँ शुभ हो तो जातक भाग्यशाली, "
                "अच्छे स्वभाव वाला, परोपकारी और दीर्घायु होता है। जातक अपने परिवार और समाज का कल्याण करता है। "
                "किन्तु यदि सूर्य अशुभ हो या बुध/शुक्र से पीड़ित हो तो पिता के सुख में कमी और भाई-बहनों से मतभेद रहता है।"
            ),
            "remedies_hi": [
                "विवाह या जन्मदिन पर चांदी के बर्तन के अलावा पीतल के बर्तनों का प्रयोग करें और उपहार में चांदी की वस्तुएं न लें।",
                "पैतृक बर्तन कभी न बेचें और हमेशा घर में गंगाजल रखें।",
                "अत्यधिक क्रोध और अहंकार से बचें।",
            ],
        }

    # Clean the extra section (Job/Promotion Rules + 60 Chamatkari Sutras)
    cleaned_extra = clean_corrupted_devanagari(extra_part)

    data_out = {
        "planet_house_predictions": corpus,
        "extra_sutras_hi": cleaned_extra,
    }
    with open(out_json_path, "w", encoding="utf-8") as f:
        json.dump(data_out, f, ensure_ascii=False, indent=2)

    return data_out


def evaluate_chamatkari_sutras_and_career_rules(core_data: dict):
    """
    Evaluate the special rules from the second part of 167329767-Lal-Kitab-Hindi.txt
    (Job & Promotion Dasha/Transit/Jaimini rules + 60 Chamatkari Phaladesh Sutras)
    specifically for the native's birth chart!
    """
    p_map = core_data["planet_by_id"]
    meta = core_data["meta"]
    lagna_idx = meta["lagna_sign_num"] - 1
    sign_lords = ["Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter"]

    def house_lord(h_num: int) -> str:
        return sign_lords[(lagna_idx + h_num - 1) % 12]

    l1 = house_lord(1)
    l2 = house_lord(2)
    l6 = house_lord(6)
    l7 = house_lord(7)
    l8 = house_lord(8)
    l9 = house_lord(9)
    l10 = house_lord(10)
    l11 = house_lord(11)
    l12 = house_lord(12)

    # 1. Job & Promotion Favourable Dashas (from lines 2252-2330 of Lal-Kitab-Hindi.txt)
    h1_6_9_10_planets = [
        p_map[pid]["full_en"] for pid in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
        if p_map[pid]["house"] in (1, 6, 9, 10)
    ]
    h1_6_9_10_hi = [
        p_map[pid]["base_hi"] for pid in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
        if p_map[pid]["house"] in (1, 6, 9, 10)
    ]

    job_promotion_analysis = {
        "job_dashas_en": [
            f"Lagna Lord ({l1}) Mahadasha / Antardasha",
            f"7th Lord ({l7}), 9th Lord ({l9}), and 10th Lord ({l10}) Dasha periods",
            f"6th Lord ({l6}) and 11th Lord ({l11}) Dasha periods",
            f"Rahu and Ketu Dasha periods",
            f"Planets posited in Houses 1, 6, 9, 10: {', '.join(h1_6_9_10_planets) if h1_6_9_10_planets else 'None'}",
        ],
        "job_dashas_hi": [
            f"लग्नेश ({p_map[l1]['base_hi']}) की दशा/अंतर्दशा में",
            f"सप्तमेश ({p_map[l7]['base_hi']}), नवमेश ({p_map[l9]['base_hi']}) एवं दशमेश ({p_map[l10]['base_hi']}) की दशा में",
            f"षष्ठेश ({p_map[l6]['base_hi']}) एवं लाभेश ({p_map[l11]['base_hi']}) की दशा में",
            "राहु-केतु की दशा में",
            f"भाव 1, 6, 9, 10 में बैठे ग्रहों की दशा में: {', '.join(h1_6_9_10_hi) if h1_6_9_10_hi else 'कोई नहीं'}",
        ],
        "transit_rule_en": "When Saturn (Shani) and Jupiter (Guru) in transit aspect or connect with Lagna, Lagna Lord, 10th House, or 10th Lord (from Natal Lagna or Moon Sign).",
        "transit_rule_hi": "गोचरीय नियम: जब शनि और गुरु गोचर में लग्न, लग्नेश, दशम भाव या दशमेश से (लग्न या चंद्र लग्न दोनों से) संबंध बनाते हैं, तब नौकरी एवं पदोन्नति प्राप्त होती है।",
    }

    # 2. Match active Chamatkari Phaladesh Sutras from lines 2333-2448 of Lal-Kitab-Hindi.txt
    matched_sutras = []

    if p_map["Mars"]["house"] == 5:
        matched_sutras.append({
            "sutra_hi": "मंगल पांचवें घर में — चैन से ना सोये तथा अपनों से धोखा खाये।",
            "sutra_en": "Mars in 5th House — Restless sleep and possibility of betrayal from close ones.",
        })
    if p_map["Jupiter"]["house"] == p_map["Ketu"]["house"]:
        matched_sutras.append({
            "sutra_hi": "गुरु-केतु की युति — स्पष्टवादी स्वभाव एवं आध्यात्मिक झुकाव।",
            "sutra_en": "Jupiter-Ketu Conjunction — Outspoken nature with deep spiritual inclination.",
        })
    if p_map["Mars"]["house"] == 1 or l1 == "Mars":
        matched_sutras.append({
            "sutra_hi": "मंगल का संबंध लग्न या लग्नेश से — जातक को परम पुरुषार्थी और साहसी बनाए।",
            "sutra_en": "Mars connected with Lagna or Lagna Lord — Makes the native highly enterprising and courageous.",
        })
    if p_map["Jupiter"]["house"] == 1 or l1 == "Jupiter":
        matched_sutras.append({
            "sutra_hi": "गुरु का लग्न या लग्नेश से संबंध — स्वयं ज्ञान की पराकाष्ठा होवे एवं समाज में सम्मानित।",
            "sutra_en": "Jupiter as Lagna Lord / connected to Lagna — Bestows pinnacle of wisdom, dignity, and scholarly respect.",
        })
    if p_map["Jupiter"]["house"] == 6:
        matched_sutras.append({
            "sutra_hi": "छठे भाव में गुरु — अनावश्यक कर्जे से सावधान रहें।",
            "sutra_en": "Jupiter in 6th House — Be cautious of unnecessary debts or financial obligations.",
        })
    if p_map["Mars"]["house"] == p_map["Rahu"]["house"]:
        matched_sutras.append({
            "sutra_hi": "मंगल संग राहु (अंगारक योग) — प्रबल साहस किन्तु क्रोध व जल्दबाजी से बचें।",
            "sutra_en": "Mars conjunct Rahu — Intense drive and boldness; avoid impulsiveness and anger.",
        })
    if p_map["Mars"]["house"] == p_map["Mercury"]["house"]:
        matched_sutras.append({
            "sutra_hi": "मंगल संग बुध — तीक्ष्ण बुद्धि, तर्कशक्ति एवं शरीर में पित्त/एसिडिटी की प्रवृत्ति।",
            "sutra_en": "Mars conjunct Mercury — Sharp analytical mind; tendency toward acidity.",
        })
    if p_map[l10]["house"] in (8, 12) or p_map[l8]["house"] == p_map[l10]["house"] or p_map[l12]["house"] == p_map[l10]["house"]:
        matched_sutras.append({
            "sutra_hi": "दशमेश का अष्टमेश या द्वादशेश से संबंध — जन्म स्थान से दूर या विदेश/बाहरी क्षेत्रों में विशेष सफलता।",
            "sutra_en": "10th Lord connected with 8th/12th Lord — Strong success away from birthplace or in distant lands.",
        })
    if p_map["Ketu"]["house"] == 9:
        matched_sutras.append({
            "sutra_hi": "सप्तम भाव से तीसरे (नवम भाव) में केतु — जातक धार्मिक, परोपकारी एवं तीर्थ यात्रा प्रेमी।",
            "sutra_en": "Ketu in 9th House — Makes the native dharmic, charitable, and inclined toward pilgrimages.",
        })
    if l1 == "Mercury":
        matched_sutras.append({
            "sutra_hi": "बुध लग्नेश हो तो — प्रबंधन कार्य, लेखाकार्य एवं बौद्धिक कार्यों में विशेष सफलता।",
            "sutra_en": "Mercury as Lagna Lord — Excels in management, accounting, commerce, and intellectual pursuits.",
        })
    if p_map["Venus"]["house"] == p_map["Moon"]["house"]:
        matched_sutras.append({
            "sutra_hi": "शुक्र संग चन्द्र — कलात्मक अभिरुचि एवं भावुकता अधिक।",
            "sutra_en": "Venus conjunct Moon — Artistic sensibility and deep emotional nature.",
        })
    if all(len([pid for pid in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"] if p_map[pid]["house"] == kh]) == 0 for kh in (1, 4, 7, 10)):
        matched_sutras.append({
            "sutra_hi": "केंद्र स्थान खाली — जातक अपने स्वयं के बाहुबल से भाग्य का निर्माण करता है।",
            "sutra_en": "Empty Kendra Houses — Native builds destiny through self-effort without relying on a godfather.",
        })
    if p_map["Moon"]["house"] == 12:
        matched_sutras.append({
            "sutra_hi": "चन्द्र 12वें घर में — रात्रि में चिंतन अधिक एवं नींद में कमी।",
            "sutra_en": "Moon in 12th House — Active mind at night; guard peaceful sleep.",
        })
    if p_map[l7]["sign_num"] in {1: 4, 2: 12, 3: 6, 4: 8, 5: 7, 6: 12, 7: 6, 8: 4, 9: 10, 10: 1, 11: 1, 12: 10}.values() and (
        (l7 == "Mars" and p_map["Mars"]["sign_num"] == 4) or
        (l7 == "Venus" and p_map["Venus"]["sign_num"] == 6) or
        (l7 == "Sun" and p_map["Sun"]["sign_num"] == 7) or
        (l7 == "Moon" and p_map["Moon"]["sign_num"] == 8) or
        (l7 == "Mercury" and p_map["Mercury"]["sign_num"] == 12) or
        (l7 == "Jupiter" and p_map["Jupiter"]["sign_num"] == 10) or
        (l7 == "Saturn" and p_map["Saturn"]["sign_num"] == 1)
    ):
        matched_sutras.append({
            "sutra_hi": "सप्तमेश नीच राशि का — विवाह एवं साझेदारी में सोच-समझकर निर्णय लें।",
            "sutra_en": "7th Lord in Debilitated Sign — Exercise patience and wisdom in marriage and partnerships.",
        })
    if p_map[l8]["house"] == p_map[l9]["house"]:
        matched_sutras.append({
            "sutra_hi": "अष्टमेश एवं नवमेश की युति — गूढ़ विद्या, तंत्र-मंत्र व आध्यात्मिक रहस्यों में गहरी रुचि।",
            "sutra_en": "8th Lord & 9th Lord Conjunction — Deep intuition and interest in occult/ancient sciences.",
        })
    if p_map["Sun"]["house"] == p_map["Moon"]["house"]:
        matched_sutras.append({
            "sutra_hi": "सूर्य-चन्द्र एक ही भाव में (अमावस्या जन्म) — जिस भाव में संग हों उस भाव के प्रति विशेष सजगता रखें।",
            "sutra_en": "Sun-Moon Conjunction — Requires extra care and mindfulness regarding the occupied house.",
        })
    if p_map[l1]["house"] in (1, 2):
        matched_sutras.append({
            "sutra_hi": "लग्नेश लग्न या दूसरे भाव में — उत्तम धन-सम्पदा एवं पारिवारिक प्रतिष्ठा की प्राप्ति।",
            "sutra_en": "Lagna Lord in 1st or 2nd House — Brings strong wealth accumulation and self-earned status.",
        })
    # Trikona lords in Trikona (Houses 1, 5, 9)
    trikona_lords = {l1, house_lord(5), l9}
    for tl in trikona_lords:
        if p_map[tl]["house"] in (1, 5, 9):
            matched_sutras.append({
                "sutra_hi": f"त्रिकोण के स्वामी ({p_map[tl]['base_hi']}) त्रिकोण भाव ({p_map[tl]['house']}) में — भाग्योदय एवं तुरंत शुभ फल प्रदान करते हैं।",
                "sutra_en": f"Trikona Lord ({tl}) placed in Trikona House ({p_map[tl]['house']}) — Bestows strong fortune and rapid rise in life.",
            })
    if p_map[l1]["house"] == p_map[l7]["house"] and "Mercury" in (l1, l7):
        matched_sutras.append({
            "sutra_hi": "बुध लग्नेश या सप्तमेश होकर युति में — आकर्षक व्यक्तित्व एवं प्रेम-सौंदर्य के प्रति आकर्षण।",
            "sutra_en": "Mercury as 1st/7th Lord in conjunction — Magnetic personality and strong romantic inclination.",
        })

    return {
        "job_promotion": job_promotion_analysis,
        "matched_sutras": matched_sutras,
    }
