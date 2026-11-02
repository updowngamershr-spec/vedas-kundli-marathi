# -*- coding: utf-8 -*-
"""
Module 14: Complete 100% Pure Marathi Language Engine
Transforms all English abbreviations, astrological jargon, Dasha dates,
Western aspect symbols, KP headers, and Hindi grammar into pure, elegant,
grammatically authentic Maharashtrian Marathi.
Zero residual English strings, zero Hindi verbs or postpositions.
"""

import re

# Devanagari letter definition
DEVA_LETTER = r'[\u0904-\u0939\u093d\u0950\u0958-\u0961\u0972-\u097f\u093e-\u094c\u0962-\u0963\u0901-\u0903\u093c\u094d]'

RASHI_NAMES_MR = [
    "मेष", "वृषभ", "मिथुन", "कर्क", "सिंह", "कन्या",
    "तूळ", "वृश्चिक", "धनु", "मकर", "कुंभ", "मीन"
]

GRAHA_NAMES_MR = {
    "Sun": "सूर्य", "Moon": "चंद्र", "Mars": "मंगळ", "Mercury": "बुध",
    "Jupiter": "गुरू", "Venus": "शुक्र", "Saturn": "शनि",
    "Rahu": "राहू", "Ketu": "केतू", "Ascendant": "लग्न", "ASC": "लग्न",
    "Uranus": "हर्षल", "Neptune": "नेपच्यून", "Pluto": "प्लूटो"
}

def to_marathi_with_hindi(en_txt: str, hi_txt: str = "") -> str:
    """Translate text to pure Marathi, accepting either English or Hindi input."""
    base = hi_txt if hi_txt else en_txt
    return to_marathi(base)


# Exact title mappings
MARATHI_TITLES_MAP = {
    "Panchang, Avkahada & Favourable Points": "पंचांग, अवकहडा आणि अनुकूल घटक",
    "Traditional Kundli & Vimshottari Dasha": "पारंपरिक जन्मकुंडली, नवांश व विंशोत्तरी दशा",
    "Planetary Positions & Chalit Bhava": "ग्रह स्थिती, अष्टकवर्ग आणि भाव चलित कोष्टक",
    "Your Ascendant": "आपले जन्म लग्न फलादेश",
    "Nakshatra Phal": "नक्षत्र फलादेश",
    "Life Predictions": "संपूर्ण जीवन फलादेश",
    "Manglik Details / Mangal Dosha": "मंगळ दोष विचार आणि सात्विक उपाय",
    "Sadesati Report": "शनी साडेसाती व ढय्या संपूर्ण विवरण",
    "Kalsarpa Dosh": "कालसर्प योग विचार व मार्गदर्शन",
    "Varshaphal (Annual Predictions) Details": "ताजिक वर्षफळ तपशील आणि वर्ष कुंडली",
    "Vimshottari Mahadasha Phal (Dasha Predictions)": "विंशोत्तरी महादशा सविस्तर फलादेश",
    "Yogini Dasha": "योगिनी दशा कोष्टक",
    "Jamini System - Karakamsa and Swamsa": "जैमिनी पद्धती — कारकांश, स्वांश व ग्रह अवस्था",
    "Char Dasha": "जैमिनी चर दशा चक्र",
    "Transit Today": "वर्तमान गोचर ग्रह स्थिती व फलादेश",
    "Lal Kitab Prediction": "लाल किताब फलादेश व अचूक सात्विक उपाय",
    "Lal Kitab Calculation": "लाल किताब गणित, टेवा व दशा चक्र",
    "Planet Consideration in Astrology": "नवग्रह फलादेश व विशेष सूत्र विचार",
    "Shodashvarga Table": "षोडशवर्ग राशी व भाव कोष्टक",
    "Shodashvarga Charts": "षोडशवर्ग कुंडली चक्र (१६ वर्ग कुंडल्या)",
    "KP System / Nakshatra Nadi": "कृष्णमूर्ती पद्धती (के.पी. व नक्षत्र नाडी)",
    "Vimshottari Dasha - Pratyantar": "विंशोत्तरी प्रत्यंतर दशा कोष्टक",
    "Friendship Table": "ग्रह मैत्री चक्र (नैसर्गिक, तात्कालिक व पंचधा मैत्री)",
    "Shadbala and Bhavabala – Strength Calculations": "षड्बल व भावबल — ग्रह आणि भाव सामर्थ्य गणना",
    "Planetary Aspects (Western)": "पाश्चात्य ग्रह दृष्टी चक्र (Western Aspects)",
    "Aspects On Bhav Madhya": "भाव मध्यावरील ग्रह दृष्टी",
    "Aspects On KP Cusp": "के.पी. भाव संधीवरील ग्रह दृष्टी",
    "Ashtakvarga Table": "अष्टकवर्ग कोष्टक व सर्वाष्टकवर्ग चक्र",
    "Prastharashtakvarga Tables": "प्रस्ताराष्टकवर्ग कोष्टके (७ ग्रह व ८ घटक)",
    "Table of Contents & Index": "अनुक्रमणिका व संपूर्ण विषय सूची",
    "Your Rashi & Identity Guide — Superpowers, Lucky Factors & Life Guidance": "आपल्या राशीचा संपूर्ण परिचय — श्रेष्ठ गुणधर्म, शुभ घटक व जीवन मार्गदर्शन",
    "Comprehensive Marriage & Partner Compatibility Guide (विवाह एवं दांपत्य सुख सम्पूर्ण विश्लेषण)": "विवाह आणि दांपत्य सुख संपूर्ण विश्लेषण — वर-वधू कुंडली मिलान",
    "100% Ad-Free Sacred Report": "१००% प्रामाणिक व पवित्र वैदिक कुंडली",
    "78-Page Complete Authentic Edition": "७८ पानांची संपूर्ण प्रामाणिक बृहत् पत्रिका",
    "Ancient Vedic, KP & Lal Kitab Predictions": "प्राचीन वैदिक, के.पी. आणि लाल किताब फलादेश",
    "Consulting Astrologer: Mayur Mandhare (BE.E&TC)": "मार्गदर्शक ज्योतिषी: मयूर मांधरे (BE.E&TC)",
    "Shivansh Astro-Vastu — Brihat Kundli": "शिवांश ॲस्ट्रो-वास्तू — बृहत् जन्मकुंडली",
}

# English months & weekdays to Marathi
CALENDAR_MAP = [
    (r'\bJanuary\b', 'जानेवारी'),
    (r'\bFebruary\b', 'फेब्रुवारी'),
    (r'\bMarch\b', 'मार्च'),
    (r'\bApril\b', 'एप्रिल'),
    (r'\bMay\b', 'मे'),
    (r'\bJune\b', 'जून'),
    (r'\bJuly\b', 'जुलै'),
    (r'\bAugust\b', 'ऑगस्ट'),
    (r'\bSeptember\b', 'सप्टेंबर'),
    (r'\bOctober\b', 'ऑक्टोबर'),
    (r'\bNovember\b', 'नोव्हेंबर'),
    (r'\bDecember\b', 'डिसेंबर'),
    (r'\bMonday\b', 'सोमवार'),
    (r'\bTuesday\b', 'मंगळवार'),
    (r'\bWednesday\b', 'बुधवार'),
    (r'\bThursday\b', 'गुरुवार'),
    (r'\bFriday\b', 'शुक्रवार'),
    (r'\bSaturday\b', 'शनिवार'),
    (r'\bSunday\b', 'रविवार'),
]

# Western aspect codes to Marathi
ASPECTS_MAP = [
    ("CONJ-CONJUNCTION", "युती (CONJ - ०°)"),
    ("OPPN-OPPOSITION", "प्रतियुती (OPPN - १८०°)"),
    ("SQUR-SQUARE", "केंद्र दृष्टी (SQUR - ९०°)"),
    ("TRIN-TRINE", "त्रिकोण दृष्टी (TRIN - १२०°)"),
    ("SEXT-SEXTILE", "लाभ दृष्टी (SEXT - ६०°)"),
    ("QCUN-QUINCUNC", "षडाष्टक (QCUN - १५०°)"),
    ("NONL-NONILE", "नवम दृष्टी (NONL - ४०°)"),
    ("SSQU-SEMI SQUARE", "अर्ध-केंद्र (SSQU - ४५°)"),
    ("QUIN-QUINLILE", "पंचम दृष्टी (QUIN - ७२°)"),
    ("SQQD-SESQUIQUA..", "पादोन दृष्टी (SQQD - १३५°)"),
    ("Abbr-Aspect", "दृष्टी प्रकार"),
    (r'\bCONJ\b', 'युती'),
    (r'\bOPPN\b', 'प्रतियुती'),
    (r'\bSQUR\b', 'केंद्र'),
    (r'\bTRIN\b', 'त्रिकोण'),
    (r'\bSEXT\b', 'लाभ'),
    (r'\bQCUN\b', 'षडाष्टक'),
    (r'\bNONL\b', 'नवम'),
]

# KP and Table headers to Marathi
HEADERS_MAP = [
    (r'\bSign Lord\b', 'राशी स्वामी'),
    (r'\bStar Lord\b', 'नक्षत्र स्वामी'),
    (r'\bSub Lord\b', 'उपस्वामी'),
    (r'\bSub-Sub Lord\b', 'उप-उपस्वामी'),
    (r'\bCusp\b', 'कस्प (भाव संधि)'),
    (r'\bDegree\b', 'अंश / कला'),
    (r'\bHouse\b', 'भाव'),
    (r'\bPlanet\b', 'ग्रह'),
    (r'\bTotal\b', 'एकूण'),
    (r'\bToT\b', 'एकूण'),
    (r'\bOrb\b', 'कक्षा (अंश)'),
    (r'\bWeight\b', 'तीव्रता / बल'),
    (r'\bStrength Source\b', 'बलाचा प्रकार'),
    (r'\bBhav Strength\b', 'भाव बल'),
    (r'\bBhav Begin\b', 'भाव आरंभ'),
    (r'\bMid Bhav\b', 'भाव मध्य'),
    (r'\bBhav\b', 'भाव'),
    (r'\bBal\. Dasa:\b', 'जन्मावेळची दशा शिल्लक:'),
    (r'\bDasa Balance:\b', 'दशा शिल्लक:'),
    (r'\bName:\b', 'नाव:'),
    (r'\bDate:\b', 'दिनांक:'),
    (r'\bTime:\b', 'वेळ:'),
    (r'\bSex:\b', 'लिंग:'),
    (r'\bPlace:\b', 'जन्मस्थान:'),
    (r'\bAyan Type:\b', 'अयनांश प्रकार:'),
    (r'\bJulian Day:\b', 'ज्युलियन डे (JD):'),
    (r'\bAsc Lord:\b', 'लग्नेश:'),
    (r'\bBenefic\b', 'शुभ'),
    (r'\bMalefic\b', 'अशुभ'),
    (r'\bYears\b', 'वर्षे'),
    (r'\bYear\b', 'वर्षे'),
    (r'\bMonths\b', 'महिने'),
    (r'\bDays\b', 'दिवस'),
    (r'\bDay Lord\b', 'वार स्वामी (दिनपती)'),
    (r'\bRasi Lord\b', 'राशी स्वामी'),
    (r'\bNak Lord\b', 'नक्षत्र स्वामी'),
]

# Planet codes to Marathi
PLANET_CODES_MAP = [
    (r'\bSUN\b', 'रवी'),
    (r'\bMON\b', 'चंद्र'),
    (r'\bMOON\b', 'चंद्र'),
    (r'\bMAR\b', 'मंगळ'),
    (r'\bMARS\b', 'मंगळ'),
    (r'\bMER\b', 'बुध'),
    (r'\bMERC\b', 'बुध'),
    (r'\bJUP\b', 'गुरू'),
    (r'\bJUPT\b', 'गुरू'),
    (r'\bVEN\b', 'शुक्र'),
    (r'\bVENU\b', 'शुक्र'),
    (r'\bSAT\b', 'शनी'),
    (r'\bSATN\b', 'शनी'),
    (r'\bRAH\b', 'राहू'),
    (r'\bKET\b', 'केतू'),
    (r'\bASC\b', 'लग्न'),
    (r'\bAsc\b', 'लग्न'),
]

# Zodiac sign names and abbreviations
SIGNS_MAP = [
    (r'\bAries\b', 'मेष'),
    (r'\bTaurus\b', 'वृषभ'),
    (r'\bGemini\b', 'मिथुन'),
    (r'\bCancer\b', 'कर्क'),
    (r'\bLeo\b', 'सिंह'),
    (r'\bVirgo\b', 'कन्या'),
    (r'\bLibra\b', 'तूळ'),
    (r'\bScorpio\b', 'वृश्चिक'),
    (r'\bSagittarius\b', 'धनु'),
    (r'\bCapricorn\b', 'मकर'),
    (r'\bAquarius\b', 'कुंभ'),
    (r'\bPisces\b', 'मीन'),
    (r'\bAr\b', 'मेष'),
    (r'\bTa\b', 'वृषभ'),
    (r'\bGe\b', 'मिथुन'),
    (r'\bCa\b', 'कर्क'),
    (r'\bLe\b', 'सिंह'),
    (r'\bVi\b', 'कन्या'),
    (r'\bLi\b', 'तूळ'),
    (r'\bSc\b', 'वृश्चिक'),
    (r'\bSco\b', 'वृश्चिक'),
    (r'\bSa\b', 'धनु'),
    (r'\bCap\b', 'मकर'),
    (r'\bAq\b', 'कुंभ'),
    (r'\bPi\b', 'मीन'),
    (r'\bPis\b', 'मीन'),
]

# High-priority multi-word phrases (Hindi to pure Marathi)
MARATHI_PHRASES = [
    ("प्रस्ताराष्टकवर्ग तालिकाएं", "प्रस्ताराष्टकवर्ग कोष्टके"),
    ("प्रस्ताराष्टकवर्ग तालिकाएँ", "प्रस्ताराष्टकवर्ग कोष्टके"),
    ("तालिकाएं", "कोष्टके"),
    ("तालिकाएँ", "कोष्टके"),
    ("तालिका", "कोष्टक"),
    ("वर्षफल", "वर्षफळ"),
    ("महादशाएं", "महादशा चक्र"),
    ("अंतर्दशाएं", "अंतर्दशा चक्र"),
    ("दशाएं", "दशा चक्र"),
    ("दशाएँ", "दशा चक्र"),
    ("कुंडलीएं", "कुंडल्या"),
    ("होने के कारण", "असल्यामुळे"),
    ("प्राप्त होता है", "प्राप्त होतो"),
    ("प्राप्त होती है", "प्राप्त होते"),
    ("प्राप्त होते हैं", "प्राप्त होतात"),
    ("कहा जाता है", "मानले जाते"),
    ("जाता है", "जातो"),
    ("जाती है", "जाते"),
    ("जाते हैं", "जातात"),
    ("होता है", "होतो"),
    ("होती है", "होते"),
    ("होते हैं", "होतात"),
    ("करता है", "करतो"),
    ("करती है", "करते"),
    ("करते हैं", "करतात"),
    ("सकता है", "शकेल"),
    ("सकती है", "शकेल"),
    ("सकते हैं", "शकतील"),
    ("के लिए", "साठी"),
    ("के साथ", "सोबत"),
    ("के बाद", "नंतर"),
    ("के अनुसार", "नुसार"),
    ("के कारण", "कारणामुळे"),
    ("के प्रभाव से", "प्रभावामुळे"),
    ("के रूप में", "स्वरूपात"),
    ("होगा", "होईल"),
    ("होगी", "होईल"),
    ("होंगे", "होतील"),
    ("जाएगा", "जाईल"),
    ("जाएगी", "जाईल"),
    ("जाएंगे", "जातील"),
    ("देंगे", "देतील"),
    ("देंगी", "देतील"),
    ("सकेंगे", "शकतील"),
    ("सकेंगी", "शकतील"),
    ("बहुत अच्छा", "अत्यंत उत्तम"),
    ("बहुत अच्छे", "अत्यंत उत्तम"),
    ("बहुत अच्छी", "अत्यंत उत्तम"),
    ("बहुत", "पुष्कळ / अत्यंत"),
    ("ज्यादा", "अधिक"),
    ("अच्छा साबित", "उत्तम सिद्ध"),
    ("साबित होगा", "ठरेल"),
    ("साबित होगी", "ठरेल"),
    ("साबित होंगे", "ठरतील"),
    ("फायदेमंद", "लाभदायक"),
    ("हानिकारक", "नुकसानकारक"),
    ("पैसों की बरसात", "धनाची विपुल आवक"),
    ("खाली हो तो", "रिक्त असल्यास"),
    ("उम्र के साथ", "वयानुसार"),
    ("चिकित्सक या वैद्य", "डॉक्टर किंवा वैद्य"),
    ("अपने पूर्वजों की श्राद्ध करे", "आपल्या पूर्वजांचे श्राद्ध करावे"),
    ("अपने पूर्वजों का श्राद्ध करें", "आपल्या पूर्वजांचे श्राद्ध करावे"),
    ("श्राद्ध करें", "श्राद्ध करावे"),
    ("दान करें", "दान करावे"),
    ("पूजा करें", "पूजा करावी"),
    ("जप करें", "जप करावा"),
    ("धारण करें", "धारण करावे"),
    ("रखें", "ठेवावे"),
    ("नीम के पेड़ लगाएं", "कडुनिंबाचे झाड लावावे"),
    ("बिस्तर के सिरहाने", "उशाशी"),
    ("एक बर्तन में पानी रखे", "एका पात्रात पाणी ठेवावे"),
    ("सुबह उसे किसी गमले में डाल दे", "सकाळी ते झाडाच्या कुंडीत टाकावे"),
    ("काले कपड़े में", "काळ्या कापडात"),
    ("बांधकर", "बांधून"),
    ("लोहे के बर्तन में", "लोखंडी पात्रात"),
    ("अंधेरे कमरे में", "अंधाऱ्या खोलीत"),
    ("रखने से उत्तम परिणाम मिलेंगे", "ठेवल्यास अत्यंत शुभ फळ प्राप्त होईल"),
]

# Single words with boundaries
MARATHI_SINGLE_WORDS = [
    ("एवं", "आणि"),
    ("तथा", "तसेच"),
    ("या", "किंवा"),
    ("अथवा", "किंवा"),
    ("किन्तु", "परंतु"),
    ("परन्तु", "परंतु"),
    ("लेकिन", "परंतु"),
    ("क्योंकि", "कारण"),
    ("इसलिए", "म्हणून"),
    ("नहीं", "नाही"),
    ("अगर", "जर"),
    ("तो", "तर"),
    ("जब", "जेव्हा"),
    ("तब", "तेव्हा"),
    ("जहां", "जिथे"),
    ("वहां", "तिथे"),
    ("यहाँ", "येथे"),
    ("वहाँ", "तेथे"),
    ("जैसे", "जसे"),
    ("वैसे", "तसे"),
    ("आपकी", "आपली"),
    ("आपका", "आपले"),
    ("आपके", "आपल्या"),
    ("आपको", "आपणास"),
    ("मुझको", "मला"),
    ("उसकी", "त्याची"),
    ("उसका", "त्याचा"),
    ("उसके", "त्याच्या"),
    ("उनका", "त्यांचे"),
    ("उनकी", "त्यांची"),
    ("उनके", "त्यांचे"),
    ("इनका", "यांचे"),
    ("इनकी", "यांची"),
    ("इनके", "यांचे"),
    ("जातक", "जातक"),
    ("जातिका", "जातिका"),
    ("स्त्री", "स्त्री"),
    ("पुरुष", "पुरुष"),
    ("पत्थर", "रत्न"),
    ("अंगूठी", "अंगठी"),
    ("उंगली", "बोट"),
    ("सोना", "सोने"),
    ("चांदी", "चांदी"),
    ("तांबा", "तांबे"),
    ("लोहा", "लोखंड"),
    ("पानी", "पाणी"),
    ("दूध", "दूध"),
    ("दही", "दही"),
    ("घी", "तूप"),
    ("चावल", "तांदूळ"),
    ("गेहूं", "गहू"),
]


def to_marathi(text: str) -> str:
    """
    Transforms any astrological text (English or Hindi) into pure, natural Marathi.
    """
    if not text:
        return ""
    s = str(text).strip()

    # 1. Exact title shortcut
    if s in MARATHI_TITLES_MAP:
        return MARATHI_TITLES_MAP[s]

    # 2. Strip external AstroSage remnants
    s = re.sub(r'https?://[^\s]*astrosage[^\s]*', '', s)

    # 3. Clean Dasha date ranges: 'From 15/08/1985 - To 23/04/1987' -> '15/08/1985 ते 23/04/1987'
    s = re.sub(r'\bFrom\s+([0-9/.\-]+)\s*-\s*To\s+([0-9/.\-]+)', r'\1 ते \2', s)
    s = re.sub(r'\bFrom\s+([A-Za-z]+ [0-9, ]+)\s*-\s*To\s+([A-Za-z]+ [0-9, ]+)', r'\1 ते \2', s)
    s = re.sub(r'\bBirth पासून\s+([A-Za-z]+ [0-9, ]+)', r'जन्मापासून \1 पर्यंत', s)
    s = re.sub(r'\bFrom\b\s*', '', s)
    s = re.sub(r'\s*-\s*To\b\s*', ' ते ', s)

    # 4. Clean Dasha names: 'JUP -16 Years' -> 'गुरू महादशा - १६ वर्षे'
    s = re.sub(r'\bSUN\s*-\s*([0-9]+)\s*Years\b', r'रवी महादशा - \1 वर्षे', s)
    s = re.sub(r'\bMON\s*-\s*([0-9]+)\s*Years\b', r'चंद्र महादशा - \1 वर्षे', s)
    s = re.sub(r'\bMAR\s*-\s*([0-9]+)\s*Years\b', r'मंगळ महादशा - \1 वर्षे', s)
    s = re.sub(r'\bRAH\s*-\s*([0-9]+)\s*Years\b', r'राहू महादशा - \1 वर्षे', s)
    s = re.sub(r'\bJUP\s*-\s*([0-9]+)\s*Years\b', r'गुरू महादशा - \1 वर्षे', s)
    s = re.sub(r'\bSAT\s*-\s*([0-9]+)\s*Years\b', r'शनी महादशा - \1 वर्षे', s)
    s = re.sub(r'\bMER\s*-\s*([0-9]+)\s*Years\b', r'बुध महादशा - \1 वर्षे', s)
    s = re.sub(r'\bKET\s*-\s*([0-9]+)\s*Years\b', r'केतू महादशा - \1 वर्षे', s)
    s = re.sub(r'\bVEN\s*-\s*([0-9]+)\s*Years\b', r'शुक्र महादशा - \1 वर्षे', s)

    # 5. English Calendar months & days
    for pat, rep in CALENDAR_MAP:
        s = re.sub(pat, rep, s)

    # 6. Western Aspect mappings
    for pat, rep in ASPECTS_MAP:
        if pat.startswith(r'\b'):
            s = re.sub(pat, rep, s)
        else:
            s = s.replace(pat, rep)

    # 7. KP & Table headers
    for pat, rep in HEADERS_MAP:
        s = re.sub(pat, rep, s)

    # 8. Planet codes
    for pat, rep in PLANET_CODES_MAP:
        s = re.sub(pat, rep, s)

    # 9. Signs and abbreviations
    for pat, rep in SIGNS_MAP:
        s = re.sub(pat, rep, s)

    # 10. Multi-word Hindi phrases to pure Marathi
    for k, v in MARATHI_PHRASES:
        if k in s:
            s = s.replace(k, v)

    # 11. Single words with Devanagari boundary
    for w, r in MARATHI_SINGLE_WORDS:
        pat = rf'(?<!{DEVA_LETTER})' + re.escape(w) + rf'(?!{DEVA_LETTER})'
        s = re.sub(pat, r, s)

    # 12. Clean double spaces and punctuation artifacts
    s = re.sub(r'\s+', ' ', s)
    s = s.replace(" ,", ",").replace(" .", ".").replace(" :", ":")

    return s.strip()
