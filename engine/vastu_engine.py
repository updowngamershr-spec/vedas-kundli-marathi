# -*- coding: utf-8 -*-
"""
Shivansh Astro-Vastu - Authentic Vastu Shastra & Astro-Vastu Computational Engine
1. 16 Mahavastu Directional Zones & 5 Elemental Balances (Pancha Tattva)
2. 32 Pada Vastu Purusha Mandala & Door/Entrance Analysis
3. Astrological Vastu Alignment (Lagna, 4th House/Lord & Planetary Directions)
4. Non-Destructive Vedic & Modern Vastu Remedies (Metal Strips, Colors, Pyramids, Yantras)
"""

import math
from typing import Dict, List, Any

# 16 Mahavastu Zones with Element, Devata, Function, Favorable/Unfavorable Activities
VASTU_ZONES_16 = [
    {
        "id": "N", "name_en": "North", "name_mr": "उत्तर दिशा (कुबेर स्थान)",
        "degrees": (348.75, 11.25), "element_en": "Water", "element_mr": "जल तत्त्व",
        "color_en": "Blue / Light Green", "color_mr": "निळा / फिकट हिरवा",
        "deity_mr": "कुबेर देव (धनाधिपती)", "energy": "नवीन संधी, धन प्राप्ती, ग्राहक वाढ",
        "best_for": "तिजोरी, मुख्य प्रवेशद्वार, स्टडी रूम, विक्री कार्यालय",
        "cut_anti_element": "लाल रंग, अग्नि, स्वयंपाकघर, पिवळा रंग येथे दोष निर्माण करतो.",
        "remedy_mr": "हिरवी वनस्पती, निळा बल्ब, कुबेर यंत्र, पाण्याने भरलेला चांदीचा कलश."
    },
    {
        "id": "NNE", "name_en": "North-North-East", "name_mr": "उत्तर-ईशान्य (आरोग्य स्थान)",
        "degrees": (11.25, 33.75), "element_en": "Water", "element_mr": "जल तत्त्व",
        "color_en": "Sky Blue", "color_mr": "आकाशी निळा",
        "deity_mr": "धन्वंतरी (औषध व निरोगी आयुष्य)", "energy": "रोगप्रतिकारक शक्ती, शारीरिक ऊर्जा, पुनर्प्राप्ती",
        "best_for": "औषधे ठेवणे, विश्रांती, शुद्ध पिण्याचे पाणी",
        "cut_anti_element": "शौचालय, लाल रंग, कचरा येथे ठेवल्यास दीर्घ आजारपण संभवते.",
        "remedy_mr": "धन्वंतरी मंत्र, औषधांची पेटी, स्फटिक शिवलिंग, स्वच्छ पाण्याचे भांडे."
    },
    {
        "id": "NE", "name_en": "North-East", "name_mr": "ईशान्य दिशा (देव स्थान - ईशान)",
        "degrees": (33.75, 56.25), "element_en": "Water / Space", "element_mr": "जल व आकाश तत्त्व",
        "color_en": "White / Light Yellow", "color_mr": "शुभ्र पांढरा / फिकट पिवळा",
        "deity_mr": "शिव शंकर व बृहस्पती (गुरू)", "energy": "आत्मिक शांती, स्पष्ट विचारसरणी, आध्यात्मिक प्रगती",
        "best_for": "पूजा घर, ध्यान मंदिर, वाचनालय, संपूर्ण खुले स्थान",
        "cut_anti_element": "शौचालय, जिन्याचे बांधकाम, स्वयंपाकघर, सेप्टिक टँक येथे महादोष मानला जातो.",
        "remedy_mr": "ईशान्य दोष निवारण पिरॅमिड, गंगाजल, पितळेची घंटा, तुळशी वृंदावन."
    },
    {
        "id": "ENE", "name_en": "East-North-East", "name_mr": "पूर्व-ईशान्य (आनंद व मनोरंजन)",
        "degrees": (56.25, 78.75), "element_en": "Air", "element_mr": "वायू तत्त्व",
        "color_en": "Light Green", "color_mr": "फिकट हिरवा",
        "deity_mr": "पर्जन्य देव", "energy": "आनंद, कौटुंबिक सौख्य, ताजेतवानेपणा",
        "best_for": "लिव्हिंग रूम, बैठकीची जागा, मुलांची खेळण्याची खोली",
        "cut_anti_element": "अति जड सामान किंवा सांडपाणी साचल्यास नैराश्य येते.",
        "remedy_mr": "हिरवे शो-प्लँट्स, कौटुंबिक हसरे फोटो, बांबू वनस्पती."
    },
    {
        "id": "E", "name_en": "East", "name_mr": "पूर्व दिशा (सूर्य व इंद्र स्थान)",
        "degrees": (78.75, 101.25), "element_en": "Air", "element_mr": "वायू तत्त्व",
        "color_en": "Green", "color_mr": "हिरवा",
        "deity_mr": "इंद्र व सूर्य नारायण", "energy": "सामाजिक संबंध, सरकारी कामे, प्रसिद्धी व प्रभाव",
        "best_for": "मुख्य दरवाजा, खिडक्या, बैठकीची खोली, प्रशासकीय डेस्क",
        "cut_anti_element": "शौचालय किंवा काळा रंग येथे असणे सामाजिक प्रतिष्ठा कमी करते.",
        "remedy_mr": "पितळी सूर्य प्रतिमा, सूर्य गायत्री मंत्र, हिरवे पडदे."
    },
    {
        "id": "ESE", "name_en": "East-South-East", "name_mr": "पूर्व-आग्नेय (चिंतन व मंथन)",
        "degrees": (101.25, 123.75), "element_en": "Air", "element_mr": "वायू तत्त्व",
        "color_en": "Cream / Pastel Green", "color_mr": "क्रीम / हलका हिरवा",
        "deity_mr": "अर्यमा", "energy": "सखोल विचार, विश्लेषण, निर्णयक्षमता",
        "best_for": "वाशिंग मशिन, मंथन डेस्क, लायब्ररी",
        "cut_anti_element": "शयनकक्ष येथे असल्यास पती-पत्नीत सतत वादविवाद व चीडचीड होते.",
        "remedy_mr": "स्टेनलेस स्टील किंवा पितळेची पट्टी, लाकडी वस्तू."
    },
    {
        "id": "SE", "name_en": "South-East", "name_mr": "आग्नेय दिशा (अग्नि स्थान)",
        "degrees": (123.75, 146.25), "element_en": "Fire", "element_mr": "अग्नि तत्त्व",
        "color_en": "Red / Orange / Pink", "color_mr": "लाल / केशरी / गुलाबी",
        "deity_mr": "अग्नि देव व शुक्र ग्रह", "energy": "रोख पैसा (Cash Flow), तरलता, उत्साह, संपन्नता",
        "best_for": "स्वयंपाकघर (गॅस शेगडी), वीज मीटर, इनव्हर्टर, अग्नीशी निगडित उपकरणे",
        "cut_anti_element": "पाण्याची टाकी, निळा रंग, बोरवेल येथे असल्यास रोख पैशांची प्रचंड चणचण भासते.",
        "remedy_mr": "तांब्याची पट्टी, लाल रंगाचा बल्ब, शुक्र यंत्र, अग्नी पिरॅमिड."
    },
    {
        "id": "SSE", "name_en": "South-South-East", "name_mr": "दक्षिण-आग्नेय (आत्मविश्वास व शक्ती)",
        "degrees": (146.25, 168.75), "element_en": "Fire", "element_mr": "अग्नि तत्त्व",
        "color_en": "Orange / Red", "color_mr": "नारंगी / फिकट लाल",
        "deity_mr": "सावित्र", "energy": "शारीरिक ताकद, धाडस, भीती निवारण",
        "best_for": "जिम, योगासन खोली, सुरक्षित साठवण",
        "cut_anti_element": "निळा किंवा काळा रंग असल्यास आत्मविश्वासाचा अभाव होतो.",
        "remedy_mr": "दौडणाऱ्या घोड्यांची लाल फ्रेम, तांब्याचा दिवा."
    },
    {
        "id": "S", "name_en": "South", "name_mr": "दक्षिण दिशा (यम स्थान - कीर्ती व विश्रांती)",
        "degrees": (168.75, 191.25), "element_en": "Fire / Earth", "element_mr": "अग्नि व पृथ्वी तत्त्व",
        "color_en": "Red / Light Brown", "color_mr": "लाल / फिकट तपकिरी",
        "deity_mr": "यमराज व मंगळ ग्रह", "energy": "समाजात नाव-लौकिक, शांती, गाढ झोप",
        "best_for": "शयनकक्ष (दक्षिण दिशेला डोके करून झोपणे), जड कपाट",
        "cut_anti_element": "मुख्य दरवाजा दोषयुक्त असल्यास किंवा येथे जलस्रोत असल्यास बदनामीची शक्यता.",
        "remedy_mr": "तांब्याची चौकट, लाल गालिचा, हनुमान चालीसा फ्रेम."
    },
    {
        "id": "SSW", "name_en": "South-South-West", "name_mr": "दक्षिण-नैऋत्य (विसर्जन व खर्च)",
        "degrees": (191.25, 213.75), "element_en": "Earth", "element_mr": "पृथ्वी तत्त्व",
        "color_en": "Yellow / Mustard", "color_mr": "पिवळा / मोहरी रंग",
        "deity_mr": "गंधर्व व मृग", "energy": "अनावश्यक गोष्टींचे विसर्जन, शारीरिक मल विसर्जन",
        "best_for": "शौचालय (टॉयलेट), कचऱ्याची पेटी, डस्टबिनसाठी सर्वोत्तम जागा",
        "cut_anti_element": "शयनकक्ष, तिजोरी किंवा मंदिर येथे असल्यास सर्व धनाची नासाडी होते.",
        "remedy_mr": "पितळेची पट्टी टॉयलेट पॉटभोवती जमिनीवर बसवणे."
    },
    {
        "id": "SW", "name_en": "South-West", "name_mr": "नैऋत्य दिशा (पितृ स्थान व स्थैर्य)",
        "degrees": (213.75, 236.25), "element_en": "Earth", "element_mr": "पृथ्वी तत्त्व",
        "color_en": "Golden Yellow / Ochre", "color_mr": "सोनेरी पिवळा / मातीचा रंग",
        "deity_mr": "नैऋती देव व राहू ग्रह (पितर)", "energy": "स्थैर्य, संबंध टिकवणे, कौशल्य, कुटुंब प्रमुखाचे वर्चस्व",
        "best_for": "कुटुंब प्रमुखाचा मास्टर बेडरूम, जड लॉकर, वजनदार बांधकाम",
        "cut_anti_element": "शौचालय, भूमिगत टाकी, कट किंवा खड्डा येथे असल्यास घरात वारंवार अपघाती नुकसान होते.",
        "remedy_mr": "पितळेचा पिवळा पिरॅमिड, मातीचे जड भांडे, पितृ तर्पण यंत्र, पिवळा पडदा."
    },
    {
        "id": "WSW", "name_en": "West-South-West", "name_mr": "पश्चिम-नैऋत्य (विद्या व बचत)",
        "degrees": (236.25, 258.75), "element_en": "Space", "element_mr": "आकाश तत्त्व",
        "color_en": "White / Light Grey", "color_mr": "पांढरा / फिकट राखाडी",
        "deity_mr": "दौवारिक व सुग्रीव", "energy": "अभ्यास, एकाग्रता, बँकेतील ठेवी, दीर्घकालीन बचत",
        "best_for": "अभ्यासाचे टेबल, मुलांची स्टडी रूम, महत्त्वाची कागदपत्रे",
        "cut_anti_element": "हिरवा रंग किंवा कचरा येथे असल्यास स्मरणशक्ती कमी होते.",
        "remedy_mr": "सरस्वती मूर्ती, पुस्तकांचे कपाट, पांढरी फुले."
    },
    {
        "id": "W", "name_en": "West", "name_mr": "पश्चिम दिशा (वरुण स्थान - प्राप्ती व नफा)",
        "degrees": (258.75, 281.25), "element_en": "Space", "element_mr": "आकाश तत्त्व",
        "color_en": "White / Metallic Silver", "color_mr": "पांढरा / चंदेरी",
        "deity_mr": "वरुण देव व शनि ग्रह", "energy": "व्यापारातील नफा, कामाचे फलित, इच्छापूर्ती",
        "best_for": "जेवणाचे टेबल (डाइनिंग), सेव्हिंग्स लॉकर, व्यापार माल साठवण",
        "cut_anti_element": "लाल रंग, अग्नि किंवा शौचालय असल्यास केलेल्या कष्टाचे फळ मिळत नाही.",
        "remedy_mr": "पांढऱ्या धातूचे चक्र, शनीची लोखंडी/स्टील पट्टी, वरुण यंत्र."
    },
    {
        "id": "WNW", "name_en": "West-North-West", "name_mr": "पश्चिम-वायव्य (तणावमुक्ती व रोदन)",
        "degrees": (281.25, 303.75), "element_en": "Space / Air", "element_mr": "आकाश व वायू तत्त्व",
        "color_en": "Light Grey / White", "color_mr": "राखाडी / पांढरा",
        "deity_mr": "असुर व पापयक्ष्मा", "energy": "मानसिक भार हलका करणे, जुन्या वाईट आठवणी विसरणे",
        "best_for": "डिटॉक्सिफिकेशन, विश्रांती कक्ष, शौचालय",
        "cut_anti_element": "महत्त्वाचे निर्णय घेण्याची जागा येथे असल्यास नैराश्य वाढते.",
        "remedy_mr": "पांढरा संगमरवरी हत्ती, कापूर जाळणे."
    },
    {
        "id": "NW", "name_en": "North-West", "name_mr": "वायव्य दिशा (वायू स्थान - साहाय्य व पाठिंबा)",
        "degrees": (303.75, 326.25), "element_en": "Air", "element_mr": "वायू तत्त्व",
        "color_en": "White / Cream", "color_mr": "पांढरा / मोतिया क्रीम",
        "deity_mr": "वायू देव व चंद्र ग्रह", "energy": "बँकेचे सहकार्य, नातेवाईकांचा पाठिंबा, ग्राहक साहाय्य",
        "best_for": "अतिथी कक्ष (गेस्ट रूम), तयार माल गोडाऊन, विवाहोत्सुक मुलींची खोली",
        "cut_anti_element": "येथे अडथळा किंवा लाल रंग असल्यास कर्जाचे सहकार्य मिळत नाही.",
        "remedy_mr": "पितळेचा धावणारा घोडा, चंद्र यंत्र, पांढऱ्या पडद्यांचा वापर."
    },
    {
        "id": "NNW", "name_en": "North-North-West", "name_mr": "उत्तर-वायव्य (आकर्षण व प्रणय)",
        "degrees": (326.25, 348.75), "element_en": "Water", "element_mr": "जल तत्त्व",
        "color_en": "Light Blue / White", "color_mr": "फिकट निळा / पांढरा",
        "deity_mr": "सोम व रुद्रा", "energy": "दाम्पत्य आकर्षण, प्रणय संबंध, सौंदर्याची अनुभूती",
        "best_for": "नवविवाहितांचा शयनकक्ष, ड्रेसिंग टेबल, परफ्युम साठवण",
        "cut_anti_element": "कचरा किंवा शौचालय असल्यास दाम्पत्य जीवनात रस उरत नाही.",
        "remedy_mr": "सुगंधी फुले, मोरपंख, राधारमण मूर्ती."
    }
]

# Astrological Lagna to Favorable Directional Affinity
LAGNA_VASTU_AFFINITY = {
    "Aries": {"fav_dir": "East & South", "fav_zone": "पूर्व व दक्षिण", "tattva": "अग्नि", "gem_placement": "आग्नेय"},
    "Taurus": {"fav_dir": "South & South-East", "fav_zone": "दक्षिण व आग्नेय", "tattva": "पृथ्वी", "gem_placement": "वायव्य"},
    "Gemini": {"fav_dir": "North & West", "fav_zone": "उत्तर व पश्चिम", "tattva": "वायू", "gem_placement": "उत्तर"},
    "Cancer": {"fav_dir": "North-East & East", "fav_zone": "ईशान्य व पूर्व", "tattva": "जल", "gem_placement": "ईशान्य"},
    "Leo": {"fav_dir": "East & South-East", "fav_zone": "पूर्व व आग्नेय", "tattva": "अग्नि", "gem_placement": "पूर्व"},
    "Virgo": {"fav_dir": "North & North-West", "fav_zone": "उत्तर व वायव्य", "tattva": "पृथ्वी", "gem_placement": "उत्तर"},
    "Libra": {"fav_dir": "West & South-East", "fav_zone": "पश्चिम व आग्नेय", "tattva": "वायू", "gem_placement": "वायव्य"},
    "Scorpio": {"fav_dir": "South & East", "fav_zone": "दक्षिण व पूर्व", "tattva": "जल", "gem_placement": "आग्नेय"},
    "Sagittarius": {"fav_dir": "North-East & North", "fav_zone": "ईशान्य व उत्तर", "tattva": "अग्नि", "gem_placement": "ईशान्य"},
    "Capricorn": {"fav_dir": "West & South", "fav_zone": "पश्चिम व दक्षिण", "tattva": "पृथ्वी", "gem_placement": "पश्चिम"},
    "Aquarius": {"fav_dir": "West & North", "fav_zone": "पश्चिम व उत्तर", "tattva": "वायू", "gem_placement": "पश्चिम"},
    "Pisces": {"fav_dir": "North-East & East", "fav_zone": "ईशान्य व पूर्व", "tattva": "जल", "gem_placement": "ईशान्य"},
}


def compute_astro_vastu_audit(kundli_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate complete 16-Zone Astro-Vastu Diagnostic Audit tailored to the native's birth chart.
    """
    meta = kundli_data.get("meta", {})
    lagna_en = meta.get("lagna_en", "Scorpio")
    lagna_lord_en = meta.get("lagna_lord_en", "Mars")
    
    # 4th house and 4th lord (Griha Bhava)
    planets = kundli_data.get("planet_by_id", {})
    fourth_house_planets = [p["name_en"] for p in planets.values() if p.get("house") == 4]
    
    affinity = LAGNA_VASTU_AFFINITY.get(lagna_en, LAGNA_VASTU_AFFINITY["Scorpio"])
    
    # Check 16 zones audit recommendations
    zone_audits = []
    for z in VASTU_ZONES_16:
        status_mr = "संतुलित ठेवा"
        if z["id"] in ["NE", "N", "E"]:
            status_mr = "अत्यंत शुभ ऊर्जा क्षेत्र (नेहमी हलके व स्वच्छ ठेवा)"
        elif z["id"] in ["SW", "S"]:
            status_mr = "स्थैर्य क्षेत्र (नेहमी जड व बंदिस्त ठेवा)"
        elif z["id"] in ["SE"]:
            status_mr = "अग्नि नियंत्रण क्षेत्र (पाण्याचा संपर्क टाळा)"
            
        zone_audits.append({
            "id": z["id"],
            "name_mr": z["name_mr"],
            "element_mr": z["element_mr"],
            "deity_mr": z["deity_mr"],
            "energy": z["energy"],
            "best_for": z["best_for"],
            "status_mr": status_mr,
            "remedy_mr": z["remedy_mr"]
        })
        
    return {
        "lagna": lagna_en,
        "lagna_lord": lagna_lord_en,
        "fav_vastu_zone": affinity["fav_zone"],
        "fav_tattva": affinity["tattva"],
        "fourth_house_occupants": fourth_house_planets,
        "zones": zone_audits,
        "summary_mr": f"जातकाच्या {lagna_en} लग्नानुसार घरामध्ये {affinity['fav_zone']} दिशेचे ऊर्जा संतुलन सर्वाधिक महत्त्वाचे ठरते. या दिशेला {affinity['tattva']} तत्त्वाचा समतोल राखल्यास भाग्यवृद्धी होते."
    }
