from engine.remedy_pages import generate_vip_remedy_pages
# -*- coding: utf-8 -*-
"""
Gurukulam Kundli CRM - Complete 56-Page Royal Colour HTML & PDF Report Generator
Generates all 56 pages matching and surpassing the 55-page AstroSage reference PDF:
- Brand: Gurukulam (गुरुकुलम् ज्योतिष पीठ)
- Royal Vedic Palette: Deep Maroon (#7C2D12), Sacred Saffron (#C2410C), Gold (#D97706), Warm Ivory (#FFFDF7)
- Zero Commercial Ads
- Supports English ('en'), Pure Hindi ('hi'), and Bilingual ('both') modes
- Exports directly to standalone vector PDF via Edge/Chrome Print-to-PDF engine.
"""

import os
import sys
import subprocess
import tempfile
from engine.svg_charts import (
    render_north_indian_svg,
    render_ashtakavarga_svg,
    render_gurukulam_cover_svg,
)
from engine.ephemeris import (
    RASHI_NAMES_EN,
    RASHI_NAMES_HI,
    RASHI_LORDS_EN,
    RASHI_LORDS_HI,
)



import base64

try:
    from engine._logo_b64 import SHIVANSH_LOGO_BASE64
except Exception:
    SHIVANSH_LOGO_BASE64 = ""

def get_image_base64(fname: str) -> str:
    """Return data URI for an optimized asset image."""
    if "logo" in fname and SHIVANSH_LOGO_BASE64:
        return SHIVANSH_LOGO_BASE64
    base_dir = getattr(sys, '_MEIPASS', os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))
    candidates = [
        os.path.join(base_dir, "assets", "images", fname),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "images", fname),
        os.path.join(base_dir, "_internal", "assets", "images", fname),
        os.path.join(os.path.dirname(sys.executable or ""), "_internal", "assets", "images", fname),
    ]
    for img_path in candidates:
        if os.path.exists(img_path):
            with open(img_path, "rb") as f:
                b64 = base64.b64encode(f.read()).decode("ascii")
                ext = "jpeg" if fname.endswith(".jpg") or fname.endswith(".jpeg") else "png"
                return f"data:image/{ext};base64,{b64}"
    if "logo" in fname and SHIVANSH_LOGO_BASE64:
        return SHIVANSH_LOGO_BASE64
    return ""

def _page_wrapper(page_num: int, meta: dict, brand: dict, title_en: str, title_hi: str, inner_html: str, lang: str = "en") -> str:
    """Wrap content in a standard A4 Shivansh Astro-Vastu bordered page with header & footer."""
    if lang in ("mr", "marathi"):
        title_str = to_marathi(title_hi) if title_hi else to_marathi(title_en)
        header_right = "शिवांश ॲस्ट्रो-वास्तू — बृहत् कुंडली"
        footer_brand = brand.get("kendra_name") or "शिवांश ॲस्ट्रो-वास्तू (Shivansh Astro-Vastu)"
        footer_tag = "वैदिक, कृष्णमूर्ती (के.पी.) व लाल किताब १९५२ संहिता"
        footer_print = f"मुद्रण दिनांक: {brand.get('printed_at', '')} | पृष्ठ क्रमांक __PAGE_NUM__ of __TOTAL_PAGES__"
    elif lang == "hi":
        title_str = title_hi if title_hi else title_en
        header_right = "शिवांश ॲस्ट्रो-वास्तू — बृहत् कुंडली"
        footer_brand = brand.get("kendra_name") or "शिवांश ॲस्ट्रो-वास्तू (Shivansh Astro-Vastu)"
        footer_tag = brand.get("tagline_hi", "वैदिक, कृष्णमूर्ति एवं लाल किताब संहिता")
        footer_print = f"मुद्रण तिथि: {brand.get('printed_at', '')} | पृष्ठ संख्या __PAGE_NUM__ of __TOTAL_PAGES__"
    elif lang in ("both", "bilingual"):
        title_str = f"{title_en} / {to_marathi(title_hi)}" if title_hi else title_en
        header_right = "शिवांश ॲस्ट्रो-वास्तू (Shivansh Astro-Vastu) — बृहत् कुंडली"
        footer_brand = brand.get("kendra_name") or brand.get("name_en", "Shivansh Astro-Vastu")
        footer_tag = brand.get("tagline_en", "Ancient Vedic, KP &amp; Lal Kitab Samhita")
        footer_print = f"Printing Date: {brand.get('printed_at', '')} | Page No. __PAGE_NUM__ of __TOTAL_PAGES__"
    else:
        title_str = title_en
        header_right = "Shivansh Astro-Vastu — Brihat Kundli"
        footer_brand = brand.get("kendra_name") or brand.get("name_en", "Shivansh Astro-Vastu")
        footer_tag = brand.get("tagline_en", "Ancient Vedic, KP &amp; Lal Kitab Samhita")
        footer_print = f"Printing Date: {brand.get('printed_at', '')} | Page No. __PAGE_NUM__ of __TOTAL_PAGES__"

    title_banner = f'<div class="section-title">|| {title_str} ||</div>' if title_str else ""
    astro_name = brand.get("astrologer_name") or "Mayur Mandhare (BE.E&TC)"
    astro_phone = brand.get("phone") or "9373058052"
    contact_chip = f"📞 {astro_phone} &nbsp;&bull;&nbsp; {astro_name}" if astro_phone else astro_name

    return f"""
    <div class="kundli-page">
      <div class="page-header">
        <span class="header-name">{meta["name"]}</span>
        <span class="header-contact" style="font-size:10.5px; color:#9A3412; font-weight:800; letter-spacing:0.3px;">{contact_chip}</span>
        <span class="header-brand">{header_right}</span>
      </div>
      <div class="page-body">
        {title_banner}
        {inner_html}
      </div>
      <div class="page-footer">
        <span><strong>{footer_brand}</strong> &nbsp;&bull;&nbsp; {contact_chip} &nbsp;&bull;&nbsp; {footer_tag}</span>
        <span>{footer_print}</span>
      </div>
    </div>
    """


RASHI_GUIDE_DATA = {
    0: {  # Mesha / Aries
        "element_en": "Fire", "element_hi": "अग्नि तत्व",
        "direction_en": "East", "direction_hi": "पूर्व दिशा",
        "superpower_en": "Unyielding Courage, Pioneering Leadership, High Energy & Decisiveness",
        "superpower_hi": "अदम्य साहस, निर्भीक नेतृत्व, उच्च ऊर्जा, त्वरित निर्णय क्षमता व स्वाभिमान",
        "mindset_en": "Direct, fearless, and action-oriented. You initiate projects with supreme confidence and never fear taking risks.",
        "mindset_hi": "निडर, स्पष्टवादी और कर्मठ सोच। चुनौतियों को सीधे स्वीकार करते हैं और नए कार्यों का नेतृत्व करने में सबसे आगे रहते हैं।",
        "pitfalls_en": "Impatience, sudden temper, rushing into commitments without evaluating fine print.",
        "pitfalls_hi": "जल्दबाजी, अत्यधिक उत्तेजना व क्रोध, तथा बिना गहन विश्लेषण के निर्णय लेना।",
        "careers_en": "Administration, Defense, Engineering, Entrepreneurship, Real Estate, Sports.",
        "careers_hi": "प्रशासनिक सेवा, सेना/पुलिस, इंजीनियरिंग, स्वतंत्र व्यवसाय, भूमि व खेलकूद।",
    },
    1: {  # Vrishabha / Taurus
        "element_en": "Earth", "element_hi": "पृथ्वी तत्व",
        "direction_en": "South", "direction_hi": "दक्षिण दिशा",
        "superpower_en": "Rock-solid Stability, Aesthetic Grace, Immense Patience & Financial Acumen",
        "superpower_hi": "अटूट स्थिरता, सौंदर्यबोध, असीम धैर्य, वित्तीय समझ व विश्वसनीय निष्ठा",
        "mindset_en": "Calm, pragmatic, and security-conscious. You build long-term wealth steadily and appreciate comfort, luxury, and art.",
        "mindset_hi": "शांत, व्यावहारिक और सुरक्षा-प्रेमी स्वभाव। धीरे-धीरे ठोस संपत्ति का निर्माण करते हैं और कला व सौंदर्य के पारखी होते हैं।",
        "pitfalls_en": "Stubbornness, reluctance to embrace rapid changes, materialistic over-attachment.",
        "pitfalls_hi": "हठधर्मिता, बदलावों के प्रति अनिच्छा, तथा अत्यधिक संकोच या विलासिता।",
        "careers_en": "Banking, Finance, Architecture, Luxury Goods, Agriculture, Culinary Arts, Music.",
        "careers_hi": "बैंकिंग, वित्त, भवन निर्माण, विलासिता उत्पाद, कृषि, होटल व ललित कलाएं।",
    },
    2: {  # Mithuna / Gemini
        "element_en": "Air", "element_hi": "वायु तत्व",
        "direction_en": "West", "direction_hi": "पश्चिम दिशा",
        "superpower_en": "Brilliant Intellect, Expressive Eloquence, Quick Adaptability & Multi-tasking",
        "superpower_hi": "कुशाग्र बुद्धि, वाकपटुता, बहुमुखी प्रतिभा, तीव्र अनुकूलन व उत्कृष्ट संचार",
        "mindset_en": "Curious, witty, and socially vibrant. Your mind is always buzzing with novel concepts, networking ideas, and analytical solutions.",
        "mindset_hi": "जिज्ञासु, चतुर और हंसमुख स्वभाव। दिमाग हमेशा नए विचारों और रणनीतियों से भरपूर रहता है तथा बातचीत से किसी को भी प्रभावित कर लेते हैं।",
        "pitfalls_en": "Restlessness, indecisiveness, scattering energy across too many goals simultaneously.",
        "pitfalls_hi": "चंचलता, दुविधा, एक साथ कई कार्यों में ऊर्जा बिखेरना व धैर्य की कमी।",
        "careers_en": "Media, Journalism, Software, Trading, Writing, Public Relations, Sales.",
        "careers_hi": "मीडिया, पत्रकारिता, सॉफ्टवेयर/आईटी, व्यापार, जनसंपर्क, अध्यापन व विपणन।",
    },
    3: {  # Karka / Cancer
        "element_en": "Water", "element_hi": "जल तत्व",
        "direction_en": "North", "direction_hi": "उत्तर दिशा",
        "superpower_en": "Deep Empathy, Intuitive Wisdom, Fierce Protective Instinct & Emotional Loyalty",
        "superpower_hi": "गहन संवेदनशीलता, अंतर्ज्ञान, अद्भुत सुरक्षात्मक भावना, मातृत्व स्नेह व निष्ठा",
        "mindset_en": "Deeply perceptive, family-oriented, and emotionally grounded. You possess natural psychological insight and care deeply for loved ones.",
        "mindset_hi": "अत्यंत भावुक, परिवार-वत्सल और अंतर्ज्ञानी। दूसरों के मन की बात तुरंत भांप लेते हैं और अपनों के लिए सर्वस्व न्योछावर करने को तत्पर रहते हैं।",
        "pitfalls_en": "Mood fluctuations, dwelling on past emotional injuries, over-protectiveness.",
        "pitfalls_hi": "मूड में उतार-चढ़ाव, पुरानी बातों को न भूलना, अत्यधिक भावुकता व चिंता।",
        "careers_en": "Healthcare, Psychology, Hospitality, Marine, Real Estate, Education, Counseling.",
        "careers_hi": "चिकित्सा, मनोविज्ञान, हॉस्पिटैलिटी, जल संसाधन, शिक्षा, मानव संसाधन व परामर्श।",
    },
    4: {  # Simha / Leo
        "element_en": "Fire", "element_hi": "अग्नि तत्व",
        "direction_en": "East", "direction_hi": "पूर्व दिशा",
        "superpower_en": "Regal Dignity, Magnanimous Generosity, Commanding Charisma & Radiant Confidence",
        "superpower_hi": "राजसी गरिमा, असीम उदारता, सम्मोहक व्यक्तित्व, आत्मबल व जन्मजात नेतृत्व",
        "mindset_en": "Noble, honorable, and naturally authoritative. You believe in living life king-size, uplifting subordinates, and achieving high social status.",
        "mindset_hi": "तेजस्वी, स्वाभिमानी और स्वभाव से राजा जैसा दृष्टिकोण। दूसरों की सहायता में कभी पीछे नहीं हटते और समाज में आदरणीय स्थान पाते हैं।",
        "pitfalls_en": "Pride, intolerance of criticism, excessive expectation of constant applause.",
        "pitfalls_hi": "अहंकार, आलोचना सहन न कर पाना, दिखावे की प्रवृत्ति व दूसरों पर हावी होना।",
        "careers_en": "Politics, Government Administration, Executive Leadership, Cinema, Luxury Brands.",
        "careers_hi": "राजनीति, उच्च प्रशासनिक पद, प्रबंधन, अभिनय/सिनेमा, एवं बड़े उद्योग का नेतृत्व।",
    },
    5: {  # Kanya / Virgo
        "element_en": "Earth", "element_hi": "पृथ्वी तत्व",
        "direction_en": "South", "direction_hi": "दक्षिण दिशा",
        "superpower_en": "Razor-sharp Analysis, Meticulous Precision, Service Dedication & Practical Problem-solving",
        "superpower_hi": "सूक्ष्म विश्लेषण क्षमता, अनुशासन, समर्पण, कार्यकुशलता व व्यावहारिक समाधान",
        "mindset_en": "Methodical, detail-oriented, and perfectionist. You spot errors others miss and excel at creating flawless organization out of disorder.",
        "mindset_hi": "व्यवस्थित, बारीकियों के पारखी और कर्तव्यनिष्ठ। अव्यवस्था को व्यवस्थित करने में माहिर होते हैं और काम में शत-प्रतिशत शुद्धता चाहते हैं।",
        "pitfalls_en": "Over-criticism of self and others, chronic overthinking, unnecessary health anxiety.",
        "pitfalls_hi": "अत्यधिक मीन-मेख निकालना, अत्यधिक सोचना (Overthinking), चिंता व तनाव।",
        "careers_en": "Data Science, Accounting, Healthcare, Research, Auditing, Publishing, Quality Control.",
        "careers_hi": "डेटा साइंस, सीए/लेखांकन, अनुसंधान, चिकित्सा, संपादन व गुणवत्ता नियंत्रण।",
    },
    6: {  # Tula / Libra
        "element_en": "Air", "element_hi": "वायु तत्व",
        "direction_en": "West", "direction_hi": "पश्चिम दिशा",
        "superpower_en": "Harmonious Diplomacy, Sense of Justice, Refined Elegance & Relationship Mastery",
        "superpower_hi": "संतुलन, न्यायप्रियता, सौम्य शिष्टाचार, कलात्मक सौंदर्यबोध व मित्रता",
        "mindset_en": "Peace-loving, sophisticated, and balanced. You weigh both sides of every coin impartially and strive for win-win outcomes in all connections.",
        "mindset_hi": "शांतिप्रिय, सुरुचिपूर्ण और न्यायसंगत। हर विवाद में निष्पक्ष दृष्टिकोण रखते हैं और जीवन में संतुलन व सौहार्द बनाए रखना आपकी प्राथमिकता है।",
        "pitfalls_en": "Indecision in dilemmas, sacrificing own needs to please others, avoidance of direct conflict.",
        "pitfalls_hi": "निर्णय लेने में अत्यधिक समय लगाना, सबको खुश रखने का प्रयास व संकोच।",
        "careers_en": "Law, Judiciary, Fashion, Diplomatic Service, Public Relations, Interior Design.",
        "careers_hi": "वकालत/न्यायपालिका, फैशन, कूटनीति, जनसंपर्क, डिजाइनिंग व साझेदारी व्यापार।",
    },
    7: {  # Vrishchika / Scorpio
        "element_en": "Water", "element_hi": "जल तत्व",
        "direction_en": "North", "direction_hi": "उत्तर दिशा",
        "superpower_en": "Indomitable Willpower, Mystical Intuition, Deep Loyalty & Unstoppable Resilience",
        "superpower_hi": "अदम्य इच्छाशक्ति, गूढ़ अंतर्दृष्टि, अटूट निष्ठा, दृढ़ संकल्प व संकटमोचन शक्ति",
        "mindset_en": "Intense, deeply transformative, and perceptive. You possess an iron resolve that resurrects from setbacks stronger than ever.",
        "mindset_hi": "गंभीर, रहस्यमयी और असीम आंतरिक शक्ति से संपन्न। किसी भी संकट से दोबारा उठ खड़े होने का साहस रखते हैं और छल-कपट को तुरंत पकड़ लेते हैं।",
        "pitfalls_en": "Secretiveness, suspicion, holding grudges, extreme emotional intensity.",
        "pitfalls_hi": "संदेह की भावना, बदले की भावना या क्रोध को दिल में दबाए रखना, अत्यधिक गोपनीयता।",
        "careers_en": "Investigation, Intelligence, Surgery, Occult Sciences, Mining, High Finance, Forensics.",
        "careers_hi": "जांच एजेंसियां/सीआईडी, शल्य चिकित्सा, गूढ़ ज्योतिष, खनन, वित्तीय विश्लेषण।",
    },
    8: {  # Dhanu / Sagittarius
        "element_en": "Fire", "element_hi": "अग्नि तत्व",
        "direction_en": "East", "direction_hi": "पूर्व दिशा",
        "superpower_en": "Philosophical Wisdom, Boundless Optimism, Truthfulness & Global Vision",
        "superpower_hi": "दार्शनिक विवेक, असीम आशावादिता, सत्यनिष्ठा, विशाल सोच व ज्ञान पिपासा",
        "mindset_en": "Expansive, ethical, and adventurous. You look at the grand divine picture, champion higher knowledge, and inspire others through truth.",
        "mindset_hi": "उदार, धर्मपरायण और दूरदर्शी सोच। जीवन को एक महान यात्रा मानते हैं और हमेशा सत्य, धर्म व उच्च आदर्शों की खोज में अग्रसर रहते हैं।",
        "pitfalls_en": "Over-promising, blunt outspokenness, restive restlessness with routine chores.",
        "pitfalls_hi": "स्पष्टवादिता से अनजाने में ठेस पहुंचाना, अत्यधिक जोखिम लेना, दिनचर्या से ऊबना।",
        "careers_en": "Higher Education, Law, Spiritual Leadership, Global Trade, Publishing, Advisory.",
        "careers_hi": "उच्च शिक्षा, विधि, धार्मिक मार्गदर्शन, अंतरराष्ट्रीय व्यापार, प्रकाशन व कंसल्टेंसी।",
    },
    9: {  # Makara / Capricorn
        "element_en": "Earth", "element_hi": "पृथ्वी तत्व",
        "direction_en": "South", "direction_hi": "दक्षिण दिशा",
        "superpower_en": "Tireless Perseverance, Strategic Mastery, Enduring Integrity & Executive Authority",
        "superpower_hi": "अथक परिश्रम, रणनीतिक दूरदर्शिता, कर्तव्यनिष्ठा, अनुशासन व प्रशासनिक दक्षता",
        "mindset_en": "Disciplined, ambitious, and mature. You construct lasting monuments of success stone by stone, remaining grounded through all storms.",
        "mindset_hi": "गंभीर, दूरदर्शी और कठोर परिश्रमी। बिना विचलित हुए अपने लक्ष्य की ओर बढ़ते हैं और समय के साथ अपनी प्रतिष्ठा व साम्राज्य का विस्तार करते हैं।",
        "pitfalls_en": "Excessive pessimism, workaholism, emotional detachment, rigidity.",
        "pitfalls_hi": "अत्यधिक काम का दबाव, निराशावादी दृष्टिकोण, भावनाओं को प्रकट न करना व कठोरता।",
        "careers_en": "Corporate Governance, Civil Infrastructure, Manufacturing, Heavy Industry, Banking.",
        "careers_hi": "कॉर्पोरेट प्रबंधन, आधारभूत संरचना, विनिर्माण, भारी उद्योग, सिविल सेवा व वित्त।",
    },
    10: {  # Kumbha / Aquarius
        "element_en": "Air", "element_hi": "वायु तत्व",
        "direction_en": "West", "direction_hi": "पश्चिम दिशा",
        "superpower_en": "Visionary Innovation, Humanitarian Ideals, Originality & Progressive Thinking",
        "superpower_hi": "दूरदर्शी नवाचार, जन-कल्याण, मौलिक सोच, स्वतंत्र दृष्टि व सामाजिक उत्थान",
        "mindset_en": "Independent, egalitarian, and scientific. You think ahead of your generation and work passionately for societal progress and novel technology.",
        "mindset_hi": "रूढ़िमुक्त, वैज्ञानिक सोच और जनहितैषी। समय से आगे की सोचते हैं और समाज में सकारात्मक बदलाव व नई तकनीकों के प्रबल समर्थक होते हैं।",
        "pitfalls_en": "Unpredictability, emotional aloofness, rebellious resistance to established norms.",
        "pitfalls_hi": "अचानक अलगाव, अत्यधिक वैराग्य, परंपराओं से अचानक विद्रोह व भावशून्यता।",
        "careers_en": "Information Technology, Space/Aviation, Social Reform, Scientific Research, Electronics.",
        "careers_hi": "आईटी/एआई, अंतरिक्ष/विमानन, समाज सेवा, वैज्ञानिक शोध, इलेक्ट्रॉनिक्स व नवाचार।",
    },
    11: {  # Meena / Pisces
        "element_en": "Water", "element_hi": "जल तत्व",
        "direction_en": "North", "direction_hi": "उत्तर दिशा",
        "superpower_en": "Universal Compassion, Spiritual Transcendence, Creative Genius & Intuitive Healing",
        "superpower_hi": "सर्वसमावेशी करुणा, आध्यात्मिक गहराई, रचनात्मक कल्पना, उपचारक शक्ति व त्याग",
        "mindset_en": "Soulful, imaginative, and divinely connected. You perceive unseen dimensions of life, forgive easily, and channel inspiration through art or faith.",
        "mindset_hi": "शांत, करुणामय और अध्यात्म-प्रिय। भौतिक सीमाओं से परे सोचते हैं, दूसरों के दर्द को अपना समझते हैं और कला व भक्ति में अगाध आनंद पाते हैं।",
        "pitfalls_en": "Escapism from harsh practical realities, over-trusting deceptive people, passivity.",
        "pitfalls_hi": "कड़वी वास्तविकताओं से पलायन, आवश्यकता से अधिक दूसरों पर भरोसा करना व अनिर्णय।",
        "careers_en": "Spiritual Counseling, Arts/Music, Pharmaceuticals, Marine, Philanthropy, Psychology.",
        "careers_hi": "अध्यात्म, कला/संगीत, औषधि निर्माण, जल परिवहन, धर्मार्थ संस्थाएं व मनोवैज्ञानिक।",
    },
}


from engine.marathi_engine import to_marathi, RASHI_NAMES_MR, GRAHA_NAMES_MR, to_marathi_with_hindi

def build_full_56_page_html(data: dict, lang: str = "mr", package: str = "maha") -> str:
    """
    Build the complete 56-page Gurukulam Kundli HTML report.
    `lang`: 'gu' (Gujarati), 'en' (English), 'both' (Bilingual Gujarati+English), or 'hi' (Hindi).
    """
    meta = data["meta"]
    brand = data["brand"]
    avk = data["avkahada"]
    fav = data["favourable"]
    gha = data["ghatak"]
    vim = data["vimshottari"]
    yog = data["yogini"]
    char_d = data["char_dasha"]
    sv = data["shodashvarga"]
    jm = data["jaimini"]
    ash = data["ashtakavarga"]
    fr = data["friendship"]
    shad = data["shadbala"]
    kp = data["kp"]
    asp = data["aspects"]
    lk = data["lal_kitab"]
    mang = data["manglik"]
    kals = data["kalsarpa"]
    sade = data["sadesati"]
    vp = data["varshaphal"]
    yogas = data["yogas"]
    gems = data["gemstones"]
    wrt = data["written"]

    is_mr = (lang in ("mr", "marathi"))
    is_hi = (lang == "hi")
    is_both = (lang in ("both", "bilingual"))
    svg_lang = "mr" if is_mr else ("hi" if is_hi else "en")

    def T(en_txt: str, hi_txt: str) -> str:
        if is_mr:
            return to_marathi(hi_txt) if hi_txt else to_marathi(en_txt)
        elif is_hi:
            return hi_txt if hi_txt else en_txt
        elif is_both:
            return f"{en_txt} <span class='mr-sub'>({to_marathi(hi_txt)})</span>" if (en_txt and hi_txt and en_txt != hi_txt) else (en_txt or hi_txt)
        return en_txt

    def P(en_txt: str, hi_txt: str) -> str:
        if is_mr:
            mr_p = to_marathi(hi_txt) if hi_txt else to_marathi(en_txt)
            return f"""<div class='para-mr' style="font-family:'Noto Sans Devanagari','Rasa',sans-serif; color:#2E1C10; margin-bottom:6px; line-height:1.65; font-size:11.5px;">{mr_p}</div>"""
        elif is_hi:
            return hi_txt
        elif is_both:
            return f"<div class='para-en'>{en_txt}</div><div class='para-mr'>{to_marathi(hi_txt)}</div>"
        return en_txt

    def L(en_val: str, hi_val: str) -> str:
        """Helper to return label or text in active language (pure Marathi when is_mr)."""
        if is_mr:
            return to_marathi(hi_val) if hi_val else to_marathi(en_val)
        elif is_hi:
            return hi_val if hi_val else en_val
        elif is_both:
            return f"{en_val} ({to_marathi(hi_val)})" if (en_val and hi_val and en_val != hi_val) else (en_val or hi_val)
        return en_val or hi_val

    pages = []

    # =========================================================================
    # PAGE 1: ROYAL GURUKULAM COVER PAGE
    # =========================================================================
    d1_chart = sv["charts"]["D1"]
    cover_svg = render_gurukulam_cover_svg(d1_chart["lagna_sign"], d1_chart["house_planets"])
    shloka_text = T("॥ SRI GANESHAYA NAMAHA ॥", "॥ श्री गणेशाय नमः ॥ &nbsp;•&nbsp; ॥ श्री स्वामी समर्थ प्रसन्न ॥ &nbsp;•&nbsp; ॥ ॐ नमो भगवते वासुदेवाय ॥") if is_mr else T("॥ SRI GANESHAYA NAMAHA ॥", "॥ श्री गणेशाय नमः ॥ &nbsp;•&nbsp; ॥ ॐ नमो भगवते वासुदेवाय ॥")
    verse_text = """आदित्यचन्द्रावनिलोऽनलश्च द्यौर्भूमिरापो हृदयं यमश्च ।<br/>अहश्च रात्रिश्च उभे च सन्ध्ये धर्मोअपि जानाति नरस्य वृत्तम् ॥"""
    brand_sub_name = "शिवांश ॲस्ट्रो-वास्तू (महाराष्ट्रियन मराठी आवृत्ती)" if is_mr else brand.get("name_hi", "शिवांश ॲस्ट्रो-वास्तू (Shivansh Astro-Vastu)")
    p1_html = f"""
    <div class="kundli-page cover-page">
      <div class="cover-border-outer">
        <div class="cover-border-inner">
          <div class="cover-shloka">{shloka_text}</div>
          <div class="cover-sanskrit-verse">
            {verse_text}
          </div>
          <div class="cover-emblem" style="text-align:center; margin:14px 0 10px 0;">
            <img src="{brand.get('logo_data') or get_image_base64('opt_shivansh_logo.jpg')}" style="width:215px; height:215px; border-radius:50%; box-shadow:0 6px 25px rgba(124,45,18,0.35); border:3px solid #D4AF37; object-fit:cover;" alt="Shivansh Astro-Vastu Logo"/>
          </div>
          <div class="cover-brand-title" style="font-size:32px; letter-spacing:3px;">{(brand.get("kendra_name") or brand.get("name_en", "SHIVANSH ASTRO-VASTU")).upper()}</div>
          <div class="cover-brand-hindi">{brand_sub_name}</div>
          <div class="cover-astrologer-meta" style="font-size:15px; color:#c59b27; margin: 6px 0 3px; font-weight:bold;">
            Consulting Astrologer: {brand.get("astrologer_name") or "Mayur Mandhare (BE.E&TC)"} &nbsp;&bull;&nbsp; 📞 {brand.get("phone") or "9373058052"}
          </div>
          <div class="cover-tagline">{brand.get("tagline_en", "Brihat Parashari • KP Nakshatra Nadi • Asli Lal Kitab • Tajika Varshaphal")}</div>

          <div class="cover-client-card">
            <div class="cover-client-header">{T("JANMA PATRIKA (HOROSCOPE)", "बृहत् जन्म पत्रिका")}</div>
            <table class="cover-table">
              <tr>
                <td class="lbl">{T("Name", "नाम")}</td><td class="val"><strong>{meta["name"]}</strong></td>
                <td class="lbl">{T("Gender", "लिंग")}</td><td class="val">{L(meta["sex"], meta["sex_hi"])}</td>
              </tr>
              <tr>
                <td class="lbl">{T("Date of Birth", "जन्म तिथि")}</td><td class="val">{meta["dob_str"]} ({L(meta["day_en"], meta["day_hi"])})</td>
                <td class="lbl">{T("Time of Birth", "जन्म समय")}</td><td class="val">{meta["tob_str"]} (IST)</td>
              </tr>
              <tr>
                <td class="lbl">{T("Place of Birth", "जन्म स्थान")}</td><td class="val">{meta["place"]}</td>
                <td class="lbl">{T("Coordinates", "अक्षांश / देशांतर")}</td><td class="val">{meta["lat_dms"]}, {meta["lon_dms"]}</td>
              </tr>
              <tr>
                <td class="lbl">{T("Lagna (Ascendant)", "जन्म लग्न")}</td><td class="val">{L(meta["lagna_en"], meta["lagna_hi"])} ({L(meta["lagna_lord_en"], meta["lagna_lord_hi"])})</td>
                <td class="lbl">{T("Moon Rashi", "जन्म राशि")}</td><td class="val">{L(meta["rasi_en"], meta["rasi_hi"])} ({L(meta["rasi_lord_en"], meta["rasi_lord_hi"])})</td>
              </tr>
              <tr>
                <td class="lbl">{T("Nakshatra-Pada", "नक्षत्र - चरण")}</td><td class="val">{L(meta["nakshatra_pada_en"], meta["nakshatra_pada_hi"])}</td>
                <td class="lbl">{T("Dasha Balance", "दशा भोग्य काल")}</td><td class="val">{L(vim["balance_str"], vim["balance_hi"])}</td>
              </tr>
            </table>
          </div>
          <div class="cover-footer-stamp">
            <span>__TOTAL_PAGES__-Page Complete Authentic Edition</span> • <span>100% Ad-Free Sacred Report</span>
          </div>
        </div>
      </div>
    </div>
    """
    pages.append(p1_html)

    # =========================================================================
    # PAGE 2: TABLE OF CONTENTS / INDEX (अनुक्रमणिका व संपूर्ण विषय सूची)
    # =========================================================================
    toc_img = brand.get("logo_data") or get_image_base64("opt_shivansh_logo.jpg")
    img_tag = f'<img src="{toc_img}" style="width:75px; height:auto; margin-bottom:4px; border-radius:50%; box-shadow:0 3px 10px rgba(124,45,18,0.25); border:2px solid #D4AF37;">' if toc_img else ''

    p_toc_inner = f"""
    <div style="text-align:center; margin-bottom:10px;">
      {img_tag}
      <div style="font-size:14.5px; font-weight:900; color:#7C2D12; letter-spacing:0.5px;">
        {T("COMPLETE KUNDLI INDEX & TABLE OF CONTENTS", "संपूर्ण जन्मकुंडली अनुक्रमणिका व विषय सूची")}
      </div>
      <div style="font-size:10px; color:#854D0E; font-weight:700; margin-top:2px;">
        {T("BPHS Vedic Astrology • Krishnamurti Stellar System (KP) • Lal Kitab 1952 Farman", "बृहत् पाराशर होराशास्त्र • कृष्णमूर्ती पद्धती (के.पी.) • लाल किताब १९५२ फर्मानानुसार")}
      </div>
    </div>

    <div style="display:grid; grid-template-columns: 1fr 1fr; gap:8px; font-size:9.2px; line-height:1.35;">
      <!-- Column 1 -->
      <div>
        <div class="box-heading" style="margin-bottom:3px; font-size:10px; background:linear-gradient(90deg, #7C2D12 0%, #B45309 100%); color:#FDE68A; padding:3px 6px; border-radius:4px;">
          {T("Section I: Core Charts & Foundations", "विभाग १: मूळ कुंडली व पंचांग विज्ञान")}
        </div>
        <table class="data-table ultra-compact" style="margin-bottom:5px; width:100%;">
          <tr><td style="width:75%;"><b>{T("Cover & Native Credentials", "जातक परिचय व मुख्य मुखपृष्ठ")}</b></td><td class="c" style="color:#7C2D12; font-weight:800;">Page 1</td></tr>
          <tr style="background:#FEF3C7;"><td style="font-weight:800; color:#7C2D12;"><b>{T("Index & Table of Contents", "विस्तृत अनुक्रमणिका व विषय सूची")}</b></td><td class="c" style="color:#7C2D12; font-weight:800;">Page 2</td></tr>
          <tr><td>{T("Panchang & Avakahada Chakra", "पंचांग, अवकहडा चक्र व पाया")}</td><td class="c">Page 3</td></tr>
          <tr><td>{T("D1 Lagna & Vimshottari Balance", "पारंपरिक जन्म कुंडली, नवांश व दशा")}</td><td class="c">Page 4</td></tr>
          <tr><td>{T("Planetary Coordinates & Chalit", "ग्रह स्पष्ट, दृष्टी व भाव चलित चक्र")}</td><td class="c">Page 5</td></tr>
        </table>

        <div class="box-heading" style="margin-bottom:3px; font-size:10px; background:linear-gradient(90deg, #7C2D12 0%, #B45309 100%); color:#FDE68A; padding:3px 6px; border-radius:4px;">
          {T("Section II: Ascendant & Life Predictions", "विभाग २: लग्न, नक्षत्र व सविस्तर जीवन फलादेश")}
        </div>
        <table class="data-table ultra-compact" style="margin-bottom:5px; width:100%;">
          <tr><td style="width:75%;"><b>{T("Ascendant Personality & Vitality", "आपले जन्म लग्न फळ (आरोग्य व स्वभाव)")}</b></td><td class="c" style="color:#7C2D12; font-weight:800;">Page 6</td></tr>
          <tr><td>{T("Nakshatra Prediction & Career", "नक्षत्र फलादेश (शिक्षण, धन व कुटुंब)")}</td><td class="c">Page 7</td></tr>
          <tr><td>{T("10 Life Domains Comprehensive Predictions", "१२ भाव सविस्तर व्यक्तिगत जीवन फलादेश")}</td><td class="c">Pages 8-11</td></tr>
        </table>

        <div class="box-heading" style="margin-bottom:3px; font-size:10px; background:linear-gradient(90deg, #7C2D12 0%, #B45309 100%); color:#FDE68A; padding:3px 6px; border-radius:4px;">
          {T("Section III: Doshas & Tajik Varshaphal", "विभाग ३: ग्रहदोष, महादशा व वर्षफळ")}
        </div>
        <table class="data-table ultra-compact" style="margin-bottom:5px; width:100%;">
          <tr><td style="width:75%;"><b>{T("Mangal Dosha Analysis & Remedies", "मांगलिक दोष विचार, प्रभाव व उपाय")}</b></td><td class="c" style="color:#7C2D12; font-weight:800;">Page 12</td></tr>
          <tr><td>{T("Shani Sade Sati 3 Phases & Remedies", "शनी साडेसाती व ढैया (तिन्ही चरणांचे फळ)")}</td><td class="c">Pages 13-16</td></tr>
          <tr><td>{T("Kaal Sarp Yoga Analysis", "कालसर्प योग विचार व शांती विधान")}</td><td class="c">Page 17</td></tr>
          <tr><td>{T("Tajik Annual Varshaphal & Muntha", "ताजिक वर्षफळ, वर्ष कुंडली व मुद्दा दशा")}</td><td class="c">Pages 18-20</td></tr>
        </table>

        <div class="box-heading" style="margin-bottom:3px; font-size:10px; background:linear-gradient(90deg, #7C2D12 0%, #B45309 100%); color:#FDE68A; padding:3px 6px; border-radius:4px;">
          {T("Section IV: Dashas, Jaimini & Transit", "विभाग ४: दशा चक्र, जैमिनी व गोचर")}
        </div>
        <table class="data-table ultra-compact" style="width:100%;">
          <tr><td style="width:75%;"><b>{T("Vimshottari Mahadasha Predictions", "विंशोत्तरी महादशा फलादेश (९ ग्रह)")}</b></td><td class="c" style="color:#7C2D12; font-weight:800;">Pages 21-22</td></tr>
          <tr><td>{T("Yogini Dasha Complete Timetable", "योगिनी दशा संपूर्ण तालिका व उप-दशा")}</td><td class="c">Pages 23-24</td></tr>
          <tr><td>{T("Jaimini Chara Dasha & Karakas", "जैमिनी पद्धती (कारकांश, स्वांश व चर दशा)")}</td><td class="c">Pages 25-27</td></tr>
          <tr><td>{T("Real-time Gochar Transit Predictions", "वर्तमान गोचर फल (९ ग्रहांचे प्रत्यक्ष भ्रमण)")}</td><td class="c">Pages 28-30</td></tr>
        </table>
      </div>

      <!-- Column 2 -->
      <div>
        <div class="box-heading" style="margin-bottom:3px; font-size:10px; background:linear-gradient(90deg, #7C2D12 0%, #B45309 100%); color:#FDE68A; padding:3px 6px; border-radius:4px;">
          {T("Section V: Lal Kitab & Navagraha", "विभाग ५: लाल किताब १९५२ व नवग्रह विचार")}
        </div>
        <table class="data-table ultra-compact" style="margin-bottom:5px; width:100%;">
          <tr><td style="width:75%;"><b>{T("Lal Kitab Predictions & Totke (1-12)", "लाल किताब फलादेश व सात्विक तोडगे")}</b></td><td class="c" style="color:#7C2D12; font-weight:800;">Pages 31-35</td></tr>
          <tr><td>{T("Lal Kitab Teva & 35-Yr Dasha", "लाल किताब गणित, टेवा व ३५-वर्षीय दशा")}</td><td class="c">Page 36</td></tr>
          <tr><td>{T("Navagraha Considerations & Aspects", "नवग्रह फलादेश व विशेष सूत्र विचार")}</td><td class="c">Pages 37-41</td></tr>
        </table>

        <div class="box-heading" style="margin-bottom:3px; font-size:10px; background:linear-gradient(90deg, #7C2D12 0%, #B45309 100%); color:#FDE68A; padding:3px 6px; border-radius:4px;">
          {T("Section VI: Shodashvarga & Strengths", "विभाग ६: षोडशवर्ग, प्रत्यंतर व बल गणना")}
        </div>
        <table class="data-table ultra-compact" style="margin-bottom:5px; width:100%;">
          <tr><td style="width:75%;"><b>{T("16 Divisional Charts (D1 to D60)", "षोडशवर्ग राशी, भाव व १६ कुंडल्या")}</b></td><td class="c" style="color:#7C2D12; font-weight:800;">Pages 42-45</td></tr>
          <tr><td>{T("KP Cuspal Positions & Sub-Lords", "कृष्णमूर्ती पद्धती (KP भाव आरंभ व उपस्वामी)")}</td><td class="c">Page 46</td></tr>
          <tr><td>{T("Pratyantar Dasha Micro-Cycles", "विंशोत्तरी सूक्ष्म प्रत्यंतर दशा तालिका")}</td><td class="c">Pages 47-50</td></tr>
          <tr><td>{T("Friendships, Shadbala & Bhavabala", "ग्रह मैत्री, षड्बल व भावबल गणना")}</td><td class="c">Pages 51-52</td></tr>
          <tr><td>{T("Aspect Grids & KP Sandhi", "पाश्चात्य दृष्टी व के.पी. भाव संधी दृष्टी")}</td><td class="c">Pages 53-54</td></tr>
          <tr><td>{T("Ashtakavarga & Prastharashtakavarga", "अष्टकवर्ग (३३७ बिंदू) व प्रस्ताराष्टकवर्ग")}</td><td class="c">Pages 55-56</td></tr>
        </table>

        <div class="box-heading" style="margin-bottom:3px; font-size:10px; background:linear-gradient(90deg, #7C2D12 0%, #B45309 100%); color:#FDE68A; padding:3px 6px; border-radius:4px;">
          {T("Section VII: Identity, Marriage & Conduct", "विभाग ७: राशी परिचय, विवाह व आचरण")}
        </div>
        <table class="data-table ultra-compact" style="margin-bottom:5px; width:100%;">
          <tr><td style="width:75%;"><b>{T("Personal Rashi Identity & Guide", "आपली राशी परिचय व शुभ घटक मार्गदर्शन")}</b></td><td class="c" style="color:#7C2D12; font-weight:800;">Pages 57-58</td></tr>
          <tr><td>{T("Marriage 36-Guna & Partner Analysis", "विवाह व दांपत्य जीवन (३६ गुण मिलान)")}</td><td class="c">Page 59</td></tr>
          <tr><td>{T("Panchang Phal & Rahu-Ketu Protocol", "पंचांग फलादेश व राहू-केतू विश्लेषण")}</td><td class="c">Page 60</td></tr>
          <tr><td>{T("Conduct Code & Do's and Don'ts", "कुंडली सुलभ मार्गदर्शन व आचरण संहिता")}</td><td class="c">Page 61</td></tr>
        </table>

        <div class="box-heading" style="margin-bottom:3px; font-size:10px; background:linear-gradient(90deg, #7C2D12 0%, #166534 100%); color:#FDE68A; padding:3px 6px; border-radius:4px; border:1px solid #D4AF37;">
          {T("Section VIII: Authentic KP Remedies", "विभाग ८: 🔮 के.पी. वैज्ञानिक उपाय व वैधानिक उद्घोषणा")}
        </div>
        <table class="data-table ultra-compact" style="width:100%; border:1px solid #86EFAC; background:#F0FDF4;">
          <tr><td style="width:75%; color:#166534; font-weight:800;"><b>{T("KP 4-Fold Significators (A, B, C, D)", "के.पी. ४-स्तरीय कार्येश मॅट्रिक्स")}</b></td><td class="c" style="color:#166534; font-weight:800;">Page 62</td></tr>
          <tr><td style="color:#166534; font-weight:800;"><b>{T("KP 12 Cuspal Sub-Lord Calculations", "के.पी. १२ भाव उपस्वामी (CSL) निष्कर्ष")}</b></td><td class="c" style="color:#166534; font-weight:800;">Page 63</td></tr>
          <tr><td style="color:#166534; font-weight:800;"><b>{T("KP Zero-Damage Gemstone Protocol", "के.पी. वैज्ञानिक रत्न व वर्ज्य रत्न इशारा")}</b></td><td class="c" style="color:#166534; font-weight:800;">Page 64</td></tr>
          <tr><td>{T("Medical Astrology & Debt Clearance", "रोग निदान व कर्ज मुक्ती शास्त्रीय विधान")}</td><td class="c">Pages 65-66</td></tr>
          <tr><td>{T("Rudraksha, Yantra & Herbal Bath", "रुद्राक्ष थेरपी, सिद्ध यंत्र व औषधी स्नान")}</td><td class="c">Pages 67-69</td></tr>
          <tr><td>{T("Lal Kitab Totke, Debts & Daan", "लाल किताब तोडगे, ऋण मुक्ती व दान मुहूर्त")}</td><td class="c">Pages 70-72</td></tr>
          <tr><td>{T("Mantras, Stotras, Vastu & Fasting", "बीज मंत्र, स्तोत्रे, वास्तु संतुलन व उपवास")}</td><td class="c">Pages 73-77</td></tr>
          <tr><td><b>{T("Master Legal Disclaimer & Copyright", "वैधानिक उद्घोषणा व सर्वाधिकार सुरक्षित")}</b></td><td class="c" style="color:#7C2D12; font-weight:800;">Page 78</td></tr>
        </table>
      </div>
    </div>

    <div style="margin-top:6px; padding:5px 10px; background:linear-gradient(90deg, #FFFBEB 0%, #FEF3C7 100%); border:1px solid #D4AF37; border-radius:5px; display:flex; justify-content:space-between; align-items:center; font-size:9px; color:#78350F; font-weight:700;">
      <span>🔱 {brand.get("kendra_name", "शिवांश ॲस्ट्रो-वास्तू")} • {brand.get("astrologer_name") or "Mayur Mandhare (BE.E&TC)"} &nbsp;&bull;&nbsp; 📞 {brand.get("phone") or "9373058052"}</span>
      <span>{meta["name"]} — {meta["place"]} ({meta["dob_str"]})</span>
    </div>
    """
    pages.append(_page_wrapper(2, meta, brand, "Table of Contents & Index", "अनुक्रमणिका व संपूर्ण विषय सूची", p_toc_inner, lang))

    # =========================================================================
    # PAGE 2: AVKAHADA CHAKRA, BASIC DETAILS, FAVOURABLE POINTS & GHATAK
    # =========================================================================
    p2_inner = f"""
    <div class="two-col-grid">
      <div>
        <div class="box-heading">{T("Avkahada Chakra", "अवकहड़ा चक्र")}</div>
        <table class="data-table compact">
          <tr><td>{T("Paya (Nakshatra Based)", "पाया (नक्षत्र आधारित)")}</td><td>{L(avk["paya_en"], avk["paya_hi"])}</td></tr>
          <tr><td>{T("Varna", "वर्ण")}</td><td>{L(avk["varna_en"], avk["varna_hi"])}</td></tr>
          <tr><td>{T("Yoni", "योनि")}</td><td>{L(avk["yoni_en"], avk["yoni_hi"])}</td></tr>
          <tr><td>{T("Gana", "गण")}</td><td>{L(avk["gana_en"], avk["gana_hi"])}</td></tr>
          <tr><td>{T("Vasya", "वश्य")}</td><td>{L(avk["vasya_en"], avk["vasya_hi"])}</td></tr>
          <tr><td>{T("Nadi", "नाड़ी")}</td><td>{L(avk["nadi_en"], avk["nadi_hi"])}</td></tr>
          <tr><td>{T("Dasa Balance", "दशा शेष (भोग्य)")}</td><td>{L(vim["balance_str"], vim["balance_hi"])}</td></tr>
          <tr><td>{T("Lagna", "लग्न")}</td><td>{L(meta["lagna_en"], meta["lagna_hi"])}</td></tr>
          <tr><td>{T("Lagna Lord", "लग्नेश")}</td><td>{L(meta["lagna_lord_en"], meta["lagna_lord_hi"])}</td></tr>
          <tr><td>{T("Rasi", "राशि")}</td><td>{L(meta["rasi_en"], meta["rasi_hi"])}</td></tr>
          <tr><td>{T("Rasi Lord", "राशि स्वामी")}</td><td>{L(meta["rasi_lord_en"], meta["rasi_lord_hi"])}</td></tr>
          <tr><td>{T("Nakshatra-Pada", "नक्षत्र - चरण")}</td><td>{L(meta["nakshatra_pada_en"], meta["nakshatra_pada_hi"])}</td></tr>
          <tr><td>{T("Nakshatra Lord", "नक्षत्र स्वामी")}</td><td>{L(meta["nakshatra_lord_en"], meta["nakshatra_lord_hi"])}</td></tr>
          <tr><td>{T("Julian Day", "जूलियन दिन")}</td><td>{meta["julian_day"]}</td></tr>
          <tr><td>{T("SunSign (Indian)", "सूर्य राशि (भारतीय)")}</td><td>{L(meta["sunsign_indian_en"], meta["sunsign_indian_hi"])}</td></tr>
          <tr><td>{T("SunSign (Western)", "सूर्य राशि (पाश्चात्य)")}</td><td>{L(meta["sunsign_west_en"], meta["sunsign_west_hi"])}</td></tr>
          <tr><td>{T("Ayanamsa", "अयनांश")}</td><td>{meta["ayanamsa_dms"]}</td></tr>
          <tr><td>{T("Ayanamsa Name", "अयनांश नाम")}</td><td>Lahiri (Chitrapaksha)</td></tr>
          <tr><td>{T("Obliquity", "क्रांतिपातांश")}</td><td>{meta["obliquity_dms"]}</td></tr>
          <tr><td>{T("Sideral Time", "नाक्षत्र समय (Sidereal)")}</td><td>{meta["sidereal_time"]}</td></tr>
        </table>

        <div class="box-heading mt-10">{T("Favourable Points", "अनुकूल (शुभ) बिंदु")}</div>
        <table class="data-table compact">
          <tr><td>{T("Lucky Numbers", "भाग्यांक")}</td><td>{fav["lucky_num"]}</td></tr>
          <tr><td>{T("Good Numbers", "शुभ अंक")}</td><td>{fav["good_nums"]}</td></tr>
          <tr><td>{T("Evil Numbers", "अशुभ अंक")}</td><td>{fav["evil_nums"]}</td></tr>
          <tr><td>{T("Good Years", "शुभ वर्ष")}</td><td>{fav["good_years"]}</td></tr>
          <tr><td>{T("Lucky Days", "शुभ वार")}</td><td>{fav["days"]}</td></tr>
          <tr><td>{T("Good Planets", "शुभ ग्रह")}</td><td>{fav["planets"]}</td></tr>
          <tr><td>{T("Friendly Signs", "मित्र राशियां")}</td><td>{fav["signs"]}</td></tr>
          <tr><td>{T("Good Lagna", "शुभ लग्न")}</td><td>{fav["lagna"]}</td></tr>
          <tr><td>{T("Lucky Metal", "शुभ धातु")}</td><td>{fav["metal"]}</td></tr>
          <tr><td>{T("Lucky Stone", "शुभ रत्न")}</td><td>{fav["stone"]}</td></tr>
        </table>
      </div>

      <div>
        <div class="box-heading">{T("Basic Details", "पंचांग एवं जन्म विवरण")}</div>
        <table class="data-table compact">
          <tr><td>{T("Sex", "लिंग")}</td><td>{L(meta["sex"], meta["sex_hi"])}</td></tr>
          <tr><td>{T("Date of Birth", "जन्म तिथि")}</td><td>{meta["dob_str"]}</td></tr>
          <tr><td>{T("Time of Birth", "जन्म समय")}</td><td>{meta["tob_str"]}</td></tr>
          <tr><td>{T("Day of Birth", "जन्म वार")}</td><td>{L(meta["day_en"], meta["day_hi"])}</td></tr>
          <tr><td>{T("Ishtkaal", "इष्टकाल (घटी-पल-विपल)")}</td><td>{meta["ishtkaal"]}</td></tr>
          <tr><td>{T("Place of Birth", "जन्म स्थान")}</td><td>{meta["place"]}</td></tr>
          <tr><td>{T("Time Zone", "समय क्षेत्र (Time Zone)")}</td><td>{meta["tz"]}</td></tr>
          <tr><td>{T("Latitude", "अक्षांश")}</td><td>{meta["lat_dms"]}</td></tr>
          <tr><td>{T("Longitude", "देशांतर")}</td><td>{meta["lon_dms"]}</td></tr>
          <tr><td>{T("Local Time Correction", "स्थानीय समय संस्कार")}</td><td>{meta["ltc_str"]}</td></tr>
          <tr><td>{T("War Time Correction", "युद्धकालीन समय संस्कार")}</td><td>{meta["wtc_str"]}</td></tr>
          <tr><td>{T("LMT at Birth", "स्थानीय मध्यम समय (LMT)")}</td><td>{meta["lmt_str"]}</td></tr>
          <tr><td>{T("GMT at Birth", "ग्रीनविच समय (GMT)")}</td><td>{meta["gmt_str"]}</td></tr>
          <tr><td>{T("Tithi", "तिथि")}</td><td>{L(meta["tithi_en"], meta["tithi_hi"])}</td></tr>
          <tr><td>{T("Hindu Week Day", "हिन्दू वार")}</td><td>{L(meta["hindu_day_en"], meta["hindu_day_hi"])}</td></tr>
          <tr><td>{T("Paksha", "पक्ष")}</td><td>{L(meta["paksha_en"], meta["paksha_hi"])}</td></tr>
          <tr><td>{T("Yoga", "योग")}</td><td>{L(meta["yoga_en"], meta["yoga_hi"])}</td></tr>
          <tr><td>{T("Karan", "करण")}</td><td>{L(meta["karana_en"], meta["karana_hi"])}</td></tr>
          <tr><td>{T("Sunrise", "सूर्योदय")}</td><td>{meta["sunrise"]}</td></tr>
          <tr><td>{T("Sunset", "सूर्यास्त")}</td><td>{meta["sunset"]}</td></tr>
          <tr><td>{T("Day Duration", "दिनमान")}</td><td>{meta["day_duration"]}</td></tr>
        </table>

        <div class="box-heading mt-10">{T("Ghatak (Malefics)", "घातक चक्र (त्याज्य)")}</div>
        <table class="data-table compact">
          <tr><td>{T("Bad Day", "घात वार")}</td><td>{gha["day"]}</td></tr>
          <tr><td>{T("Bad Karan", "घात करण")}</td><td>{gha["karan"]}</td></tr>
          <tr><td>{T("Bad Lagna", "घात लग्न")}</td><td>{gha["lagna"]}</td></tr>
          <tr><td>{T("Bad Month", "घात मास")}</td><td>{gha["month"]}</td></tr>
          <tr><td>{T("Bad Nakshatra", "घात नक्षत्र")}</td><td>{gha["nakshatra"]}</td></tr>
          <tr><td>{T("Bad Prahar", "घात प्रहर")}</td><td>{gha["prahar"]}</td></tr>
          <tr><td>{T("Bad Rasi", "घात राशि")}</td><td>{gha["rasi"]}</td></tr>
          <tr><td>{T("Bad Tithi", "घात तिथि")}</td><td>{gha["tithi"]}</td></tr>
          <tr><td>{T("Bad Yoga", "घात योग")}</td><td>{gha["yoga"]}</td></tr>
          <tr><td>{T("Bad Planets", "घात ग्रह")}</td><td>{gha["planets"]}</td></tr>
        </table>
      </div>
    </div>
    """
    pages.append(_page_wrapper(2, meta, brand, "Panchang, Avkahada & Favourable Points", "पंचांग, अवकहड़ा एवं घातक चक्र", p2_inner, lang))

    # =========================================================================
    # PAGE 3: TRADITIONAL KUNDLI OVERVIEW (LAGNA, NAVAMSHA & VIMSHOTTARI DASHA)
    # =========================================================================
    d9_chart = sv["charts"]["D9"]
    svg_lagna = render_north_indian_svg(d1_chart["lagna_sign"], d1_chart["house_planets"], lang=svg_lang, size=260)
    svg_navamsha = render_north_indian_svg(d9_chart["lagna_sign"], d9_chart["house_planets"], lang=svg_lang, size=260)

    # 9 Vimshottari Mahadasha boxes in 3x3 grid
    vim_boxes_html = []
    for md in vim["mahadashas"]:
        ad_lines = "".join(
            f"<tr><td>{L(ad['code'], ad['name_hi'])}</td><td class='c'>{ad['end_str']}</td></tr>"
            for ad in md["antardashas"]
        )
        vim_boxes_html.append(f"""
        <div class="mini-dasha-box">
          <div class="mini-dasha-head">{L(md['header_en'], md['header_hi'])}<br/><span>{md['range_str']}</span></div>
          <table class="mini-table">{ad_lines}</table>
        </div>
        """)

    p3_inner = f"""
    <table class="top-summary-strip">
      <tr>
        <td><b>Name:</b> {meta["name"]}</td>
        <td><b>Julian Day:</b> {meta["julian_day"]}</td>
        <td><b>Asc Lord:</b> {meta["lagna_lord_short"]}</td>
        <td><b>Bal. Dasa:</b> {vim["balance_str"]}</td>
      </tr>
      <tr>
        <td><b>Sex:</b> {meta["sex_short"]} &nbsp;|&nbsp; <b>Date:</b> {meta["dob_dot"]}</td>
        <td><b>Ayan:</b> {meta["ayanamsa_dms"]} (Lahiri)</td>
        <td><b>Asc:</b> {meta["lagna_en"]}</td>
        <td><b>Rasi:</b> {meta["rasi_en"]} ({meta["rasi_lord_short"]})</td>
      </tr>
      <tr>
        <td><b>Time:</b> {meta["tob_dot"]} ({meta["day_en"]}) &nbsp;|&nbsp; <b>SID:</b> {meta["sidereal_time"]}</td>
        <td><b>Place:</b> {meta["place"]} ({meta["lat_short"]}, {meta["lon_short"]})</td>
        <td><b>Tithi:</b> {meta["tithi_en"]} | <b>Yoga:</b> {meta["yoga_en"]}</td>
        <td><b>Star-Pada:</b> {meta["nakshatra_pada_dash"]} ({meta["nakshatra_lord_short"]})</td>
      </tr>
    </table>

    <div class="two-col-grid mt-6">
      <div class="chart-col">
        <div class="chart-title">{T("Lagna Chart (D-1)", "लग्न कुंडली")}</div>
        {svg_lagna}
      </div>
      <div class="chart-col">
        <div class="chart-title">{T("Navamasa Chart (D-9)", "नवांश कुंडली")}</div>
        {svg_navamsha}
      </div>
    </div>

    <div class="box-heading center mt-8">{T("Vimshottari Dasha (Mahadasha & Antardasha Periods)", "विंशोत्तरी महादशा एवं अंतर्दशा चक्र")}</div>
    <div class="three-col-grid mt-4">{"".join(vim_boxes_html)}</div>
    """
    pages.append(_page_wrapper(3, meta, brand, "Traditional Kundli & Vimshottari Dasha", "पारंपरिक जन्म कुंडली, नवांश एवं विंशोत्तरी दशा", p3_inner, lang))

    # =========================================================================
    # PAGE 4: PLANETARY POSITIONS, ASHTAKAVARGA & COMPLETE CHALIT TABLE
    # =========================================================================
    b_beg = [c.get("begin_lon", 0.0) for c in data.get("chalit_table", [])]
    def _get_chalit_bhava(plon: float) -> int:
        plon = plon % 360.0
        for i in range(12):
            s = b_beg[i]
            e = b_beg[(i + 1) % 12]
            arc_tot = (e - s) % 360.0
            arc_p = (plon - s) % 360.0
            if arc_p < arc_tot:
                return i + 1
        return 1

    planet_rows_list = []
    for p in data["planets"]:
        is_asc = (p.get("id") == "ASC")
        r_bhav = 1 if is_asc else p.get("rashi_house", p.get("house", 1))
        c_bhav = 1 if is_asc else (p.get("chalit_house") or _get_chalit_bhava(p.get("sid_lon", 0.0)))
        planet_rows_list.append(
            f"<tr><td><b>{L(p['name_en'], p['name_hi'])}</b></td>"
            f"<td>{L(p['sign_en'], p['sign_hi'])}</td>"
            f"<td class='c'>{p['dms']}</td>"
            f"<td class='c'><b>{r_bhav}</b></td>"
            f"<td class='c'><b>{c_bhav}</b></td>"
            f"<td>{L(p['nakshatra_en'], p['nakshatra_hi'])}</td>"
            f"<td class='c'>{p['pada']}</td></tr>"
        )
    planet_rows_html = "".join(planet_rows_list)

    # Ashtakvarga full table
    av_rows_html = "".join(
        f"<tr><td><b>{L(r['name_en'], r['name_hi'])}</b></td>" + "".join(f"<td class='c'>{v}</td>" for v in r["values"]) + "</tr>"
        for r in ash["bhinna_rows"]
    )
    av_tot_html = "<tr class='tot-row'><td><b>Total</b></td>" + "".join(f"<td class='c'><b>{v}</b></td>" for v in ash["sarva_totals"]) + "</tr>"

    chalit_rows_html = "".join(
        f"<tr><td class='c'><b>{c['bhav']}</b></td><td>{L(c['begin_sign_en'], c['begin_sign_hi'])}</td><td class='c'>{c['begin_dms']}</td><td>{L(c['mid_sign_en'], c['mid_sign_hi'])}</td><td class='c'>{c['mid_dms']}</td></tr>"
        for c in data["chalit_table"]
    )

    p4_table_inner = f"""
    <div class="two-col-grid">
      <div>
        <div class="box-heading">{T("Planetary Positions (Graha Sphuta)", "ग्रह स्पष्ट तालिका")}</div>
        <table class="data-table compact">
          <thead><tr><th>{T("Planets", "ग्रह")}</th><th>{T("Sign", "राशी")}</th><th>{T("Longitude", "अंश")}</th><th>{T("Rashi Bhav", "राशी भाव")}</th><th>{T("Chalit Bhav", "चलित भाव")}</th><th>{T("Nakshatra", "नक्षत्र")}</th><th>{T("Pada", "चरण")}</th></tr></thead>
          <tbody>{planet_rows_html}</tbody>
        </table>

        <div class="box-heading mt-10">{T("Ashtakvarga Table", "अष्टकवर्ग तालिका")}</div>
        <table class="data-table compact">
          <thead><tr><th>Sign No</th>{"".join(f"<th class='c'>{i}</th>" for i in range(1,13))}</tr></thead>
          <tbody>{av_rows_html}{av_tot_html}</tbody>
        </table>
      </div>

      <div>
        <div class="box-heading">{T("Chalit Table (Sripati Bhava — Complete 12 Houses)", "चलित तालिका (श्रीपति भाव — द्वादश भाव संधि)")}</div>
        <table class="data-table compact">
          <thead><tr><th>{T("Bhav", "भाव")}</th><th>{T("Sign", "राशी")}</th><th>{T("Bhav Begin", "भाव आरंभ")}</th><th>{T("Sign", "राशी")}</th><th>{T("Mid Bhav", "भाव मध्य")}</th></tr></thead>
          <tbody>{chalit_rows_html}</tbody>
        </table>

        <div class="disclaimer-card mt-8">
          <h4 style="color:#7C2D12;">✦ {T("Significance of Chalit Bhava in Prediction", "श्रीपति भाव चलित तालिका का महत्व")}</h4>
          <p>{P(
            "In Vedic Astrology, when a planet sits close to the cusp of a house, its functional results shift to the adjoining bhava. The Chalit table accurately delineates the beginning and midpoint of each house so no prediction is miscalculated.",
            "वैदिक ज्योतिष में ग्रह जिस राशि में होता है, कभी-कभी भाव-संधि के निकट होने से उसका फल अगले अथवा पिछले भाव में स्थानान्तरित हो जाता है। यह तालिका प्रत्येक भाव के आरंभ एवं मध्य बिंदु को स्पष्ट करती है।"
          )}</p>
        </div>
      </div>
    </div>
    """
    pages.append(_page_wrapper(4, meta, brand, "Planetary Positions & Chalit Bhava", "ग्रह स्पष्ट, अष्टकवर्ग एवं भाव चलित तालिका", p4_table_inner, lang))

    # =========================================================================
    # PAGE 4: YOUR ASCENDANT
    # =========================================================================
    asc_r = wrt["ascendant_report"]
    p4_inner = f"""
    <div class="prose-block">
      <h3>{T("What is Ascendant (Lagna)?", "लग्न (Ascendant) क्या है?")}</h3>
      <p>{P(
        "The ascendant house is considered very important in Vedic astrology. During the birth of a person, the sign which rises in the eastern sky is called the person's ascendant (Lagna). And, the sign which comes in this first house is called the ascendant sign. The ascendant helps in calculating the minutest events in a person's life through astrology, whereas daily, weekly, monthly, and yearly transit predictions are analyzed on the basis of Moon sign and Sun sign.",
        "वैदिक ज्योतिष में लग्न भाव को अत्यंत महत्वपूर्ण माना गया है। जातक के जन्म के समय पूर्वी क्षितिज में जो राशि उदित हो रही होती है, उसे 'जन्म लग्न' कहा जाता है। प्रथम भाव में आने वाली इस राशि के आधार पर व्यक्ति के शरीर, स्वभाव, स्वास्थ्य, आत्मबल और जीवन की सूक्ष्मतम घटनाओं का आकलन किया जाता है।"
      )}</p>
      <div class="highlight-banner">{T("Your Ascendant is:", "आपका जन्म लग्न है:")} <strong>{L(meta["lagna_en"], meta["lagna_hi"])}</strong></div>

      <h3>{T(f"Health for {meta['lagna_en']} Ascendant", f"{meta['lagna_hi']} लग्न के लिए स्वास्थ्य विचार")}</h3>
      <p>{P(asc_r["health_en"], asc_r["health_hi"])}</p>

      <h3>{T(f"Temperament & Personality For {meta['lagna_en']} Ascendant", f"{meta['lagna_hi']} लग्न का स्वभाव एवं व्यक्तित्व")}</h3>
      <p>{P(asc_r["temp_en"], asc_r["temp_hi"])}</p>

      <h3>{T(f"Physical Appearance For {meta['lagna_en']} Ascendant", f"{meta['lagna_hi']} लग्न की शारीरिक बनावट")}</h3>
      <p>{P(asc_r["phys_en"], asc_r["phys_hi"])}</p>
    </div>
    """
    pages.append(_page_wrapper(4, meta, brand, "Your Ascendant", "आपका जन्म लग्न फल", p4_inner, lang))

    # =========================================================================
    # PAGE 5: NAKSHATRA PHAL
    # =========================================================================
    nak_r = wrt["nakshatra_report"]
    p5_inner = f"""
    <div class="prose-block">
      <p>{P(
        "Nakshatra is the term for lunar mansion in Hindu astrology. A nakshatra is one of 27 sectors along the ecliptic (13°20' each). Each nakshatra is further subdivided into four quarters (or padas of 3°20' each). These play a foundational role in Vedic astrology for Dasha calculation, mental temperament, and auspicious naming.",
        "वैदिक ज्योतिष में क्रांतिवृत्त के 27 नक्षत्रों को चंद्र नक्षत्र मंडल कहा जाता है। प्रत्येक नक्षत्र 13 अंश 20 कला का होता है और इसके 4 चरण (प्रत्येक 3 अंश 20 कला) होते हैं। जन्म के समय चंद्रमा जिस नक्षत्र और चरण में स्थित होता है, उसी से विंशोत्तरी दशा और जातक के आंतरिक स्वभाव का निर्धारण होता है।"
      )}</p>
      <div class="highlight-banner">
        {T("Your Nakshatra :", "आपका जन्म नक्षत्र :")} <strong>{L(nak_r["nakshatra_en"], nak_r["nakshatra_hi"])}</strong>
        &nbsp;&nbsp;|&nbsp;&nbsp;
        {T("Your Nakshatra Pada :", "नक्षत्र चरण :")} <strong>{nak_r["pada"]}</strong>
      </div>

      <h3>{T(f"{meta['nakshatra_en']} Nakshatra Prediction :", f"{meta['nakshatra_hi']} नक्षत्र फल कथन :")}</h3>
      <p>{P(nak_r["prediction_en"], nak_r["prediction_hi"])}</p>

      <h3>{T("Education & Income :", "शिक्षा एवं आय के स्रोत :")}</h3>
      <p>{P(nak_r["education_en"], nak_r["education_hi"])}</p>

      <h3>{T("Family Life :", "पारिवारिक एवं वैवाहिक जीवन :")}</h3>
      <p>{P(nak_r["family_en"], nak_r["family_hi"])}</p>
    </div>
    """
    pages.append(_page_wrapper(5, meta, brand, "Nakshatra Phal", "नक्षत्र फल कथन", p5_inner, lang))

    # =========================================================================
    # PAGES 6, 7, 8, 9: LIFE PREDICTIONS
    # =========================================================================
    lp = wrt["life_predictions"]
    page_lp_slices = [
        (6, lp[0:3]),
        (7, lp[3:6]),
        (8, lp[6:9]),
        (9, lp[9:10]),
    ]
    for p_num, items in page_lp_slices:
        blocks_html = "".join(
            f"<div class='prose-section'><h3>{L(item['title_en'], item['title_hi'])}</h3><p>{P(item['text_en'], item['text_hi'])}</p></div>"
            for item in items
        )
        # On Page 9, also include Gurukulam Classical Yogas summary so the page is rich and informative!
        extra_p9 = ""
        if p_num == 9:
            yoga_cards = "".join(
                f"<div class='yoga-card'><h4>✦ {to_marathi(y.get('name') or y.get('name_hi')) if is_mr else L(y['name_en'], y['name_hi'])}</h4><p>{P(y['desc_en'], y.get('description') or y['desc_hi'])}</p></div>"
                for y in yogas
            )
            extra_p9 = f"""
            <div class="box-heading mt-14">{T("Auspicious Yogas & Raja Yogas in Your Kundli (Shivansh Special)", "कुंडली में निर्मित प्रमुख राजयोग एवं विशेष योग")}</div>
            {yoga_cards}
            """
        pages.append(_page_wrapper(p_num, meta, brand, "Life Predictions", "जीवन फलादेश", f"<div class='prose-block'>{blocks_html}{extra_p9}</div>", lang))

    # =========================================================================
    # PAGE 10: MANGLIK DETAILS / MANGAL DOSHA
    # =========================================================================
    p10_inner = f"""
    <div class="prose-block">
      <p>{P(
        "Generally Manglik Dosha is considered from the position of Lagna and Moon in the birth chart.",
        "वैदिक ज्योतिष में मांगलिक दोष (मंगल दोष) का विचार जन्म कुंडली में लग्न और चंद्रमा दोनों से मंगल की भाव स्थिति के आधार पर किया जाता है।"
      )}</p>
      <p>{P(
        f"In the birth chart, Mangal is placed in {mang['mars_house_lagna_word_en']} house from Lagna, while in the Moon chart Mangal is placed in {mang['mars_house_moon_word_en']} house.",
        f"जन्म कुंडली में मंगल लग्न से {mang['mars_house_lagna_word_hi']} भाव में स्थित है, जबकि चंद्र कुंडली से मंगल {mang['mars_house_moon_word_hi']} भाव में स्थित है।"
      )}</p>
      <div class="highlight-banner"><strong>{L(mang["status_en"], mang["status_hi"])}</strong></div>
      <p>{P(
        "Mangal Dosha is considered to create hurdles or temperamental friction in married life if unchecked. It is considered in classical texts that if a Manglik person marries another Manglik person, or when Mars is in its own/debilitated sign or aspected by benefic Jupiter, the Manglik Dosha gets cancelled and loses its malefic effect.",
        "शास्त्रीय मान्यता के अनुसार यदि दोनों वर-वधू की कुंडली में समान मांगलिक योग हो अथवा मंगल पर शुभ गुरु की दृष्टि या राशिगत परिहार हो, तो मंगल दोष स्वतः निरस्त हो जाता है।"
      )}</p>

      <h3>{T("Remedies (Needs to be performed before marriage)", "विवाह से पूर्व किए जाने वाले शास्त्रीय उपाय")}</h3>
      <p>{P(
        "Kumbha Vivah, Vishnu Vivah and Ashwatha Vivah are the most popular classical remedies for Mangal Dosha. Ashwatha Vivaha means symbolic ritual with a Peepal or Banana tree, and Kumbha Vivah (Ghata Vivaha) is performed with a sacred earthen pot prior to wedding.",
        "कुंभ विवाह, विष्णु विवाह तथा अश्वत्थ (पीपल) विवाह मंगल दोष की शांति के लिए सर्वाधिक प्रचलित वैदिक उपाय हैं।"
      )}</p>

      <h3>{T("Remedies (Can be performed after marriage)", "विवाह के पश्चात नियमित उपासना उपाय")}</h3>
      <ol class="remedy-list">
        <li>{P("Keep Kesariya Ganapati (Orange coloured idol of Lord Ganesha) in worship room and worship daily.", "पूजा घर में केसरिया गणपति की प्रतिमा स्थापित कर प्रतिदिन विधिवत पूजन करें।")}</li>
        <li>{P("Worship Lord Hanuman by reciting Hanuman Chalisa daily.", "प्रतिदिन श्रद्धापूर्वक श्री हनुमान चालीसा का पाठ एवं हनुमान जी की आराधना करें।")}</li>
        <li>{P("Mahamrityunjaya Paath (recitation of Mahamrityunjaya Mantra).", "भगवान शिव के महामृत्युंजय मंत्र का जप अथवा रुद्राभिषेक करें।")}</li>
      </ol>

      <h3>{T("Remedies (Based on Lal Kitab, can be performed after marriage)", "लाल किताब के अनुसार मंगल शांति के अचूक उपाय")}</h3>
      <ol class="remedy-list">
        <li>{P("Feed birds with something sweet.", "पक्षियों को मीठा दाना या बूंदी/मीठी रोटी डालें।")}</li>
        <li>{P("Offer sweet Rotis prepared on Tandoor to dogs.", "तंदूर में बनी मीठी रोटी कुत्तों को खिलाएं।")}</li>
        <li>{P("Worship Banyan (Bargad) tree with milk mixed with something sweet.", "बरगद के वृक्ष की जड़ में मीठा दूध अर्पित करें और गीली मिट्टी का तिलक लगाएं।")}</li>
      </ol>
    </div>
    """
    pages.append(_page_wrapper(10, meta, brand, "Manglik Details / Mangal Dosha", "मांगलिक दोष विचार एवं उपाय", p10_inner, lang))

    # =========================================================================
    # PAGES 11, 12, 13: SADESATI REPORT TABLES (1..17, 18..33, 34..41)
    # =========================================================================
    sade_slices = [
        (11, sade[0:17], True),
        (12, sade[17:33], False),
        (13, sade[33:41], False),
    ]
    for p_num, rows_slice, show_summary in sade_slices:
        top_bio = ""
        if show_summary:
            top_bio = f"""
            <table class="data-table compact mb-10" style="width:75%;margin:0 auto 12px auto;">
              <tr><td><b>{T("Name", "नाम")}</b></td><td>{meta["name"]}</td></tr>
              <tr><td><b>{T("Date", "जन्म तिथि")}</b></td><td>{meta["dob_slash"]}</td></tr>
              <tr><td><b>{T("Time of Birth", "जन्म समय")}</b></td><td>{meta["tob_str"].replace(' ', '')}</td></tr>
              <tr><td><b>{T("Place of Birth", "जन्म स्थान")}</b></td><td>{meta["place"]}</td></tr>
              <tr><td><b>{T("Sex", "लिंग")}</b></td><td>{L(meta["sex"], meta["sex_hi"])}</td></tr>
              <tr><td><b>{T("Rasi", "जन्म राशि")}</b></td><td>{L(meta["rasi_en"], meta["rasi_hi"])}</td></tr>
              <tr><td><b>{T("Tithi", "तिथि")}</b></td><td>{L(meta["tithi_en"], meta["tithi_hi"])}</td></tr>
              <tr><td><b>{T("Nakshatra", "नक्षत्र")}</b></td><td>{L(meta["nakshatra_en"], meta["nakshatra_hi"])}</td></tr>
            </table>
            """
        s_rows = "".join(
            f"<tr><td class='c'>{r['sn']}</td><td>{L(r['type_en'], r['type_hi'])}</td><td>{L(r['rashi_en'], r['rashi_hi'])}</td><td>{r['start_date_en']}</td><td>{r['end_date_en']}</td><td>{L(r['phase_en'], r['phase_hi'])}</td></tr>"
            for r in rows_slice
        )
        p_sade_html = f"""
        {top_bio}
        <table class="data-table compact">
          <thead>
            <tr>
              <th class="c">S.N.</th>
              <th>{T("Sade Sati / Panoti", "साढ़े साती / ढैया")}</th>
              <th>{T("Shani Rashi", "शनि राशि")}</th>
              <th>{T("Start Date", "प्रारंभ तिथि")}</th>
              <th>{T("End Date", "समाप्ति तिथि")}</th>
              <th>{T("Phase", "चरण")}</th>
            </tr>
          </thead>
          <tbody>{s_rows}</tbody>
        </table>
        """
        pages.append(_page_wrapper(p_num, meta, brand, "Sadesati Report", "शनि साढ़े साती एवं ढैया विवरण", p_sade_html, lang))

    # =========================================================================
    # PAGE 14: SHANI SADE SATI PHASE PREDICTIONS
    # =========================================================================
    p14_inner = f"""
    <div class="prose-block">
      <h3>{T("Shani Sade Sati: Rising Phase (First 2.5 Years)", "शनि साढ़े साती: उदय चरण (प्रथम ढैया — द्वादश भाव में शनि)")}</h3>
      <p>{P(
        "This is the starting period of Shani's Sade Sati. In this period Saturn transits in the 12th house from the natal Moon. It calls for careful financial management, patience with colleagues, and avoiding unnecessary disputes or high-risk business ventures. Saturn's nature is of discipline and delayed reward—steady hard work and ethical conduct ensure that everything falls into place.",
        "यह शनि की साढ़े साती का प्रथम चरण है जिसमें शनि जन्म राशि से बारहवें भाव में गोचर करता है। इस अवधि में अपने खर्चों पर नियंत्रण रखें, कार्यक्षेत्र में सहकर्मियों से सामंजस्य बनाए रखें तथा व्यापार में अति-जोखिम से बचें। शनि न्याय और परिश्रम का कारक है, अतः धैर्य और परिश्रम से अंततः उत्तम परिणाम प्राप्त होते हैं।"
      )}</p>

      <h3>{T("Shani Sade Sati: Peak Phase (Middle 2.5 Years)", "शनि साढ़े साती: शिखर चरण (मध्य ढैया — जन्म राशि पर शनि)")}</h3>
      <p>{P(
        "This is the peak of Shani's Sade Sati when Saturn transits directly over the natal Moon. It demands attention to physical health, regular exercise, mental calm, and patience in domestic relationships. Avoid pessimism or haste in decision-making. Spiritual inclination, yoga, and doing the basics right will sail you smoothly through this transformative period.",
        "इस चरण में शनि जन्म के चंद्रमा के ऊपर से गोचर करता है। इस समय स्वास्थ्य, नियमित व्यायाम, मानसिक शांति और पारिवारिक सामंजस्य पर विशेष ध्यान दें। आलस्य व निराशा को त्यागकर आध्यात्मिक चिंतन और अनुशासित जीवनशैली अपनाने से सभी चुनौतियां दूर होती हैं।"
      )}</p>

      <h3>{T("Shani Sade Sati: Setting Phase (Final 2.5 Years)", "शनि साढ़े साती: अस्त चरण (अंतिम ढैया — द्वितीय भाव में शनि)")}</h3>
      <p>{P(
        "In the setting phase of Shani's Sade Sati, Saturn transits in the 2nd house from the natal Moon. You begin feeling relief after the first two phases. Maintain polite speech, careful driving, सात्विक (pure) diet, and prudent domestic budgeting. By the end of this phase, Saturn rewards the native for the discipline learned during the 7.5-year cycle.",
        "साढ़े साती के इस अंतिम चरण में शनि जन्म राशि से दूसरे भाव में गोचर करता है। पिछले दो चरणों की तुलना में राहत का अनुभव होता है। वाणी में मधुरता, वाहन चलाने में सावधानी और सात्विक आहार का पालन करें। उतरती साढ़े साती जातक को परिश्रम का शुभ प्रतिफल देकर जाती है।"
      )}</p>

      <div class="note-box">
        <strong>{T("Shivansh Astro-Vastu Note:", "शिवांश ॲस्ट्रो-वास्तू शास्त्रीय टीप:")}</strong>
        {P(
          "Sade Sati is not universally malefic; its actual effect depends on the ongoing Vimshottari Dasha, Ashtakavarga bindus in Saturn's transit sign, and Saturn's functional nature for your Ascendant.",
          "साढ़े साती सदैव अशुभ नहीं होती; इसका वास्तविक प्रभाव वर्तमान महादशा, अष्टकवर्ग के शुभ बिंदुओं और लग्न के अनुसार शनि के स्वामित्व पर निर्भर करता है।"
        )}
      </div>
    </div>
    """
    pages.append(_page_wrapper(14, meta, brand, "Sadesati Report", "शनि साढ़े साती के तीनों चरणों का फल", p14_inner, lang))

    # =========================================================================
    # PAGE 15: KALSARPA DOSH / YOG
    # =========================================================================
    svg_ks = render_north_indian_svg(d1_chart["lagna_sign"], d1_chart["house_planets"], lang=svg_lang, size=270)
    p15_inner = f"""
    <div class="prose-block">
      <h3>{T("Kalsarpa Dosh / Yog", "कालसर्प दोष / योग विचार")}</h3>
      <p>{P(
        "As per classical definition, when all seven planets are situated within one hemisphere between Rahu and Ketu in the birth chart, astrologers call it Kalsarpa Yoga. However, if planets are well-posited in strong houses or form Raja Yogas, Kalsarpa Yoga does not obstruct success and instead grants extraordinary focus and rise.",
        "जब जन्म कुंडली में राहु और केतु के एक ही ओर सभी सातों ग्रह आ जाते हैं, तब कालसर्प योग का निर्माण होता है। यदि कुंडली में ग्रह शुभ भावों में बलवान हों, तो जातक अपने परिश्रम से उच्च शिखर प्राप्त करता है।"
      )}</p>
      <div class="highlight-banner"><strong>{T("Result:", "निष्कर्ष:")} {L(kals.get("result_en", ""), kals.get("result_hi", ""))}</strong></div>
      <div class="chart-col mt-14">
        <div class="chart-title">{T("Lagna Chart:", "जन्म लग्न कुंडली:")}</div>
        {svg_ks}
      </div>
    </div>
    """
    pages.append(_page_wrapper(15, meta, brand, "Kalsarpa Dosh", "कालसर्प योग विचार", p15_inner, lang))

    # =========================================================================
    # PAGE 16: VARSHAPHAL (ANNUAL PREDICTIONS) DETAILS & CHART
    # =========================================================================
    vm = vp["varsha_meta"]
    svg_varsha = render_north_indian_svg(vp["varsha_chart"]["lagna_sign"], vp["varsha_chart"]["house_planets"], lang=svg_lang, size=265)
    p16_inner = f"""
    <table class="data-table compact">
      <thead>
        <tr>
          <th>{T("Janam (Birth)", "जन्म विवरण (Janam)")}</th>
          <th class="c">{T("Attribute", "विवरण")}</th>
          <th>{T(f"Varsha (Year {vp['varsha_year']})", f"वर्ष कुंडली ({vp['varsha_year']})")}</th>
        </tr>
      </thead>
      <tbody>
        <tr><td>{L(meta["sex"], meta["sex_hi"])}</td><td class="c"><b>{T("Sex", "लिंग")}</b></td><td>{L(vm["sex"], meta["sex_hi"])}</td></tr>
        <tr><td>{meta["dob_slash"]}</td><td class="c"><b>{T("Date of Birth", "जन्म तिथी")}</b></td><td>{vm["dob_slash"]}</td></tr>
        <tr><td>{meta["tob_str"].replace(' ', '')}</td><td class="c"><b>{T("Time of Birth", "जन्म वेळ")}</b></td><td>{vm["tob_str"].replace(' ', '')}</td></tr>
        <tr><td>{L(meta["day_en"], meta["day_hi"])}</td><td class="c"><b>{T("Day of Birth", "जन्म वार")}</b></td><td>{L(vm["day_en"], to_marathi(vm["day_en"]))}</td></tr>
        <tr><td>{meta["place"]}</td><td class="c"><b>{T("Place of Birth", "जन्म ठिकाण")}</b></td><td>{vm["place"]}</td></tr>
        <tr><td>{int(meta["lat"])}</td><td class="c"><b>{T("Latitude", "अक्षांश")}</b></td><td>{int(vm["lat"])}</td></tr>
        <tr><td>{int(meta["lon"])}</td><td class="c"><b>{T("Longitude", "रेखांश")}</b></td><td>{int(vm["lon"])}</td></tr>
        <tr><td>{meta["ltc_str"]}</td><td class="c"><b>{T("Local Time Correction", "स्थानिक वेळ दुरुस्ती")}</b></td><td>{vm["ltc_str"]}</td></tr>
        <tr><td>{meta["wtc_str"]}</td><td class="c"><b>{T("War Time Correction", "वॉर टाईम दुरुस्ती")}</b></td><td>{vm["wtc_str"]}</td></tr>
        <tr><td>{meta["lmt_str"].replace(':', '.')}</td><td class="c"><b>{T("LMT at Birth", "जन्मावेळी LMT")}</b></td><td>{vm["lmt_str"].replace(':', '.')}</td></tr>
        <tr><td>{meta["sunrise"]}</td><td class="c"><b>{T("Sunrise", "सूर्योदय")}</b></td><td>{vm["sunrise"]}</td></tr>
        <tr><td>{meta["sunset"]}</td><td class="c"><b>{T("Sunset", "सूर्यास्त")}</b></td><td>{vm["sunset"]}</td></tr>
        <tr><td>{L(meta["lagna_en"], meta["lagna_hi"])}</td><td class="c"><b>{T("Lagna", "लग्न")}</b></td><td>{L(vm["lagna_en"], to_marathi(vm["lagna_en"]))}</td></tr>
        <tr><td>{L(meta["lagna_lord_short"], meta["lagna_lord_hi"])}</td><td class="c"><b>{T("Lagna Lord", "लग्नेश")}</b></td><td>{L(vm["lagna_lord_short"], to_marathi(vm["lagna_lord_short"]))}</td></tr>
        <tr><td>{L(meta["rasi_en"], meta["rasi_hi"])}</td><td class="c"><b>{T("Rasi", "राशी")}</b></td><td>{L(vm["rasi_en"], to_marathi(vm["rasi_en"]))}</td></tr>
        <tr><td>{L(meta["rasi_lord_short"], meta["rasi_lord_hi"])}</td><td class="c"><b>{T("Rasi Lord", "राशी स्वामी")}</b></td><td>{L(vm["rasi_lord_short"], to_marathi(vm["rasi_lord_short"]))}</td></tr>
        <tr><td>{L(meta["nakshatra_en"], meta["nakshatra_hi"])}</td><td class="c"><b>{T("Nakshatra", "नक्षत्र")}</b></td><td>{L(vm["nakshatra_en"], to_marathi(vm["nakshatra_en"]))}</td></tr>
        <tr><td>{L(meta["nakshatra_lord_short"], meta["nakshatra_lord_hi"])}</td><td class="c"><b>{T("Nakshatra Lord", "नक्षत्र स्वामी")}</b></td><td>{L(vm["nakshatra_lord_short"], to_marathi(vm["nakshatra_lord_short"]))}</td></tr>
        <tr><td>{L(meta["yoga_en"], meta["yoga_hi"])}</td><td class="c"><b>{T("Yoga", "योग")}</b></td><td>{L(vm["yoga_en"], to_marathi(vm["yoga_en"]))}</td></tr>
        <tr><td>{L(meta["karana_en"], meta.get("karana_hi", ""))}</td><td class="c"><b>{T("Karan", "करण")}</b></td><td>{L(vm["karana_en"], to_marathi(vm["karana_en"]))}</td></tr>
        <tr><td>{L(meta["sunsign_west_en"], meta["sunsign_west_hi"])}</td><td class="c"><b>{T("Sun Sign (Western)", "सूर्य राशी (पाश्चात्य)")}</b></td><td>{L(vm["sunsign_west_en"], to_marathi(vm["sunsign_west_en"]))}</td></tr>
        <tr><td>{meta["ayanamsa_dms"]}</td><td class="c"><b>{T("Ayanamsa", "आयनांश")}</b></td><td>{vm["ayanamsa_dms"]}</td></tr>
        <tr><td>Lahiri</td><td class="c"><b>{T("Ayanamsa Name", "आयनांश पद्धती")}</b></td><td>Lahiri</td></tr>
      </tbody>
    </table>

    <div class="chart-col mt-10">
      <div class="chart-title">{T("Varshphal Chart (Solar Return Chart)", "ताजिक वर्षफल कुंडली")}</div>
      {svg_varsha}
    </div>
    """
    pages.append(_page_wrapper(16, meta, brand, "Varshaphal (Annual Predictions) Details", "ताजिक वर्षफल विवरण एवं वर्ष कुंडली", p16_inner, lang))

    # =========================================================================
    # PAGES 17 & 18: VARSHAPHAL MUNTHA & MUDDA DASHA PREDICTIONS
    # =========================================================================
    vd_list = wrt["varsha_dasha_preds"]
    p17_items = "".join(
        f"<div class='prose-section'><h4>{L(vd['header_en'], vd['header_hi'])}<br/><span>{L(vd['sub_en'], vd['sub_hi'])}</span></h4><p>{P(vd['text_en'], vd['text_hi'])}</p></div>"
        for vd in vd_list[:4]
    )
    p17_inner = f"""
    <div class="prose-block">
      <div class="prose-section">
        <h3>{T(f"Muntha: {vp['muntha_bhav']} Bhav", f"वर्ष कुंडली में मुंथा: भाव {vp['muntha_bhav']}")}</h3>
        <p>{P(wrt["muntha_pred_en"], wrt["muntha_pred_hi"])}</p>
      </div>
      {p17_items}
    </div>
    """
    pages.append(_page_wrapper(17, meta, brand, "Varshaphal (Annual Predictions) Details", "वर्षफल मुंथा एवं मुद्दा दशा फलादेश (1)", p17_inner, lang))

    p18_items = "".join(
        f"<div class='prose-section'><h4>{L(vd['header_en'], vd['header_hi'])}<br/><span>{L(vd['sub_en'], vd['sub_hi'])}</span></h4><p>{P(vd['text_en'], vd['text_hi'])}</p></div>"
        for vd in vd_list[4:9]
    )
    pages.append(_page_wrapper(18, meta, brand, "Varshaphal (Annual Predictions) Details", "वर्षफल मुद्दा दशा फलादेश (2)", f"<div class='prose-block'>{p18_items}</div>", lang))

    # =========================================================================
    # PAGES 19 & 20: VIMSHOTTARI MAHADAHSA PHAL (DASHA PREDICTIONS)
    # =========================================================================
    vmp = wrt["vim_maha_preds"]
    for p_num, sl in [(19, vmp[:5]), (20, vmp[5:9])]:
        html_blocks = "".join(
            f"<div class='prose-section'><h4>{L(m['header_en'], m['header_hi'])}<br/><span>{L(m['sub_en'], m['sub_hi'])}</span></h4><p>{P(m['text_en'], m['text_hi'])}</p></div>"
            for m in sl
        )
        pages.append(_page_wrapper(p_num, meta, brand, "Vimshottari Mahadasha Phal (Dasha Predictions)", "विंशोत्तरी महादशा फलादेश", f"<div class='prose-block'>{html_blocks}</div>", lang))

    # =========================================================================
    # PAGES 21 & 22: YOGINI DASHA (12 blocks per page in 4x3 grid)
    # =========================================================================
    for p_num, y_slice in [(21, yog[:12]), (22, yog[12:24])]:
        boxes = []
        for b in y_slice:
            r_html = "".join(f"<tr><td>{r['name_hi'] if is_hi else r['code']}</td><td>{r['end_str']}</td></tr>" for r in b["rows"])
            boxes.append(f"""
            <div class="mini-dasha-box">
              <div class="mini-dasha-head">{L(b['header_en'], b['header_hi'])}</div>
              <table class="mini-table">
                <tr class="sub-hd"><td>From</td><td>{b['from_str']}</td></tr>
                <tr class="sub-hd"><td>To</td><td>{b['to_str']}</td></tr>
                {r_html}
              </table>
            </div>
            """)
        pages.append(_page_wrapper(p_num, meta, brand, "Yogini Dasha", "योगिनी दशा तालिका", f"<div class='four-col-grid'>{''.join(boxes)}</div>", lang))

    # =========================================================================
    # PAGE 23: JAIMINI SYSTEM - KARAKAMSA AND SWAMSA
    # =========================================================================
    svg_kk = render_north_indian_svg(jm["karakamsa_chart"]["lagna_sign"], jm["karakamsa_chart"]["house_planets"], lang=svg_lang, size=255)
    svg_sw = render_north_indian_svg(jm["swamsa_chart"]["lagna_sign"], jm["swamsa_chart"]["house_planets"], lang=svg_lang, size=255)
    kk_rows = "".join(
        f"<tr><td>{L(r['karak_en'], r['karak_hi'])}</td><td>{L(r['sthir_en'], r['sthir_hi'])}</td><td>{L(r['chara_en'], r['chara_hi'])}</td></tr>"
        for r in jm["karaka_table"]
    )
    av_st_rows = "".join(
        f"<tr><td>{L(r['planet_en'], r['planet_hi'])}</td><td>{L(r['jagrat_en'], r['jagrat_hi'])}</td><td>{L(r['baladi_en'], r['baladi_hi'])}</td><td>{L(r['deeptadi_en'], r['deeptadi_hi'])}</td></tr>"
        for r in jm["avastha_table"]
    )
    p23_inner = f"""
    <div class="two-col-grid">
      <div class="chart-col">
        <div class="chart-title">{T("Karakamsa Chart", "कारकांश कुंडली")}</div>
        {svg_kk}
      </div>
      <div class="chart-col">
        <div class="chart-title">{T("Swamsa Chart", "स्वांश कुंडली")}</div>
        {svg_sw}
      </div>
    </div>
    <div class="two-col-grid mt-14">
      <div>
        <div class="box-heading center">{T("Karak (Sthir & Chara)", "जैमिनी स्थिर एवं चर कारक")}</div>
        <table class="data-table compact">
          <thead><tr><th>Karak</th><th>Sthir</th><th>Chara</th></tr></thead>
          <tbody>{kk_rows}</tbody>
        </table>
      </div>
      <div>
        <div class="box-heading center">{T("Avastha (Planetary States)", "ग्रहों की जाग्रतादि एवं बालादि अवस्था")}</div>
        <table class="data-table compact">
          <thead><tr><th>Planets</th><th>Jagrat</th><th>Baladi</th><th>Deeptadi</th></tr></thead>
          <tbody>{av_st_rows}</tbody>
        </table>
      </div>
    </div>
    """
    pages.append(_page_wrapper(23, meta, brand, "Jamini System - Karakamsa and Swamsa", "जैमिनी पद्धति — कारकांश, स्वांश एवं ग्रह अवस्था", p23_inner, lang))

    # =========================================================================
    # PAGES 24 & 25: CHAR DASHA
    # =========================================================================
    m_rows = char_d["maha_rows"]
    ad_blocks = char_d["antardasha_blocks"]

    def _render_char_ad_box(blk):
        r_html = "".join(
            f"<tr><td>{L(r['sign_short'], r['sign_hi'])}</td><td class='c'>{r['start_str']}</td><td class='c'>{r['end_str']}</td></tr>"
            for r in blk["rows"]
        )
        return f"""
        <div class="mini-dasha-box">
          <div class="mini-dasha-head">{L(blk['header'], blk['header_hi'])}</div>
          <table class="mini-table">{r_html}</table>
        </div>
        """

    def _render_maha_slice(ms):
        return "".join(
            f"<tr><td><b>{L(r['sign_short'], r['sign_hi'])}</b> {r['years_str']}</td><td class='c'>{r['start_str']}</td><td class='c'>{r['end_str']}</td></tr>"
            for r in ms
        )

    p24_inner = f"""
    <div class="box-heading center">{T("Char Maha Dasha", "जैमिनी चर महादशा")}</div>
    <div class="two-col-grid">
      <table class="data-table compact"><tbody>{_render_maha_slice(m_rows[0:3])}</tbody></table>
      <table class="data-table compact"><tbody>{_render_maha_slice(m_rows[3:6])}</tbody></table>
    </div>
    <div class="two-col-grid mt-6">
      <table class="data-table compact"><tbody>{_render_maha_slice(m_rows[6:9])}</tbody></table>
      <table class="data-table compact"><tbody>{_render_maha_slice(m_rows[9:12])}</tbody></table>
    </div>
    <div class="box-heading center mt-10">{T("Char Antardasha", "चर अंतर्दशा")}</div>
    <div class="three-col-grid">{"".join(_render_char_ad_box(b) for b in ad_blocks[0:3])}</div>
    """
    pages.append(_page_wrapper(24, meta, brand, "Char Dasha", "जैमिनी चर दशा (1)", p24_inner, lang))

    p25_inner = f"""
    <div class="three-col-grid">{"".join(_render_char_ad_box(b) for b in ad_blocks[3:12])}</div>
    """
    pages.append(_page_wrapper(25, meta, brand, "Char Dasha", "जैमिनी चर अंतर्दशा (2)", p25_inner, lang))

    # =========================================================================
    # PAGES 26, 27, 28: TRANSIT TODAY (GOCHARA)
    # =========================================================================
    tp_list = wrt["transit_preds"]
    for p_num, t_slice in [(26, tp_list[0:3]), (27, tp_list[3:6]), (28, tp_list[6:9])]:
        t_html = "".join(
            f"<div class='prose-section'><h3>{L(t['header_en'], t['header_hi'])}</h3><p>{P(t['text_en'], t['text_hi'])}</p></div>"
            for t in t_slice
        )
        pages.append(_page_wrapper(p_num, meta, brand, f"Transit Today ({vp['transit_date_str']})", f"वर्तमान गोचर फल ({vp['transit_date_str']})", f"<div class='prose-block'>{t_html}</div>", lang))

    # =========================================================================
    # PAGES 29, 30, 31, 32, 33: LAL KITAB PREDICTIONS & REMEDIES (FROM 167329767-Lal-Kitab-Hindi.txt)
    # =========================================================================
    lkw = wrt["lal_kitab_written"]
    lk_page_slices = [
        (29, lkw[0:1]),  # Sun
        (30, lkw[1:3]),  # Moon, Mars
        (31, lkw[3:5]),  # Mercury, Jupiter
        (32, lkw[5:7]),  # Venus, Saturn
        (33, lkw[7:9]),  # Rahu, Ketu
    ]
    for p_num, lk_slice in lk_page_slices:
        lk_blocks = []
        for item in lk_slice:
            rems_source = item.get("remedies_hi") or item.get("remedies_en") or []
            if is_mr:
                rems_html = "<br/>".join([f"• {to_marathi(r)}" for r in rems_source]) if rems_source else "• नियमित कुलदेवता व इष्टदेवता उपासना करावी."
                title_disp = to_marathi(item.get("title_hi") or item.get("title_en") or "")
            elif is_hi:
                rems_html = "<br/>".join([f"• {r}" for r in rems_source]) if rems_source else "• नियमित कुलदेवता एवं इष्टदेवता की आराधना करें।"
                title_disp = item.get("title_hi") or item.get("title_en") or ""
            elif is_both:
                rems_en = item.get("remedies_en") or []
                rems_hi = item.get("remedies_hi") or []
                if rems_en and rems_hi and len(rems_en) == len(rems_hi):
                    rems_html = "<br/>".join([f"• {en} <span class='hi-sub'>({to_marathi(hi)})</span>" for en, hi in zip(rems_en, rems_hi)])
                else:
                    rems_html = "<br/>".join([f"• {to_marathi(r)}" for r in rems_source]) if rems_source else "• नियमित कुलदेवता उपासना करावी."
                title_disp = f"{item.get('title_en', '')} / {to_marathi(item.get('title_hi', ''))}"
            else:
                rems_html = "<br/>".join([f"• {r}" for r in rems_source]) if rems_source else "• Worship family deity and practice satvik karmas."
                title_disp = item.get("title_en") or item.get("title_hi") or ""

            body_formatted_en = item["body_en"].replace("\n", "<br/>")
            lk_top_badge = ""
            if item.get("planet_en") == "Sun":
                lk_pic = get_image_base64("opt_lalkitab.jpg")
                if lk_pic:
                    lk_top_badge = f'<div style="display:flex; align-items:center; gap:10px; margin-bottom:8px; padding:6px 10px; background:#FEF3C7; border:1px solid #FDE68A; border-radius:8px;"><img src="{lk_pic}" style="width:48px; height:auto; border-radius:4px; box-shadow:0 1px 4px rgba(0,0,0,0.15);"><div style="font-size:10px; color:#78350F; font-weight:700;">📖 <strong>लाल किताब १९५२ फर्मानानुसार अचूक तोडगे:</strong> पक्के घर, दृष्टि संबंध आणि सात्त्विक उपायांचे परिपूर्ण शास्त्रीय संकलन.</div></div>'

            lk_blocks.append(f"""
            {lk_top_badge}
            <div class="prose-section lk-card">
              <h3>{title_disp}</h3>
              <div class="lk-body">{P(body_formatted_en, item['body_hi'])}</div>
              <div class="lk-remedies">
                <strong>{T("Remedial Measures (Lal Kitab Upay / Totke):", "लाल किताब के प्रामाणिक उपाय (टोटके):")}</strong><br/>
                {rems_html}
              </div>
            </div>
            """)
        pages.append(_page_wrapper(p_num, meta, brand, "Lal Kitab Prediction", "लाल किताब फलादेश एवं अचूक उपाय", f"<div class='prose-block'>{''.join(lk_blocks)}</div>", lang))

    # =========================================================================
    # PAGE 34: LAL KITAB CALCULATION, TEVA CHART & 35-YEAR DASHA
    # =========================================================================
    svg_lk = render_north_indian_svg(1, lk["chart"]["house_planets"], lang=svg_lang, size=230)
    lk_p_rows = "".join(
        f"<tr><td>{L(r['planet_en'], r['planet_hi'])}</td><td>{r['sign_hi'] if is_hi else r['sign_en']}</td><td class='c'>{r['positions']}</td><td class='c'>{L(r['soya_en'], r['soya_hi'])}</td><td class='c'>{L(r['kismat_en'], r['kismat_hi'])}</td><td class='c'>{L(r['status_en'], r['status_hi'])}</td></tr>"
        for r in lk["planet_rows"]
    )
    lk_d_boxes = []
    for db in lk["dasha_blocks"]:
        sr = "".join(f"<tr><td>{L(r['planet_en'], r['planet_hi'])}</td><td>{r['end_str']}</td></tr>" for r in db["rows"])
        lk_d_boxes.append(f"""
        <div class="mini-dasha-box">
          <div class="mini-dasha-head">{L(db['header_en'], db['header_hi'])}</div>
          <table class="mini-table">
            <tr class="sub-hd"><td>From</td><td>{db['from_str']}</td></tr>
            <tr class="sub-hd"><td>To</td><td>{db['to_str']}</td></tr>
            {sr}
          </table>
        </div>
        """)

    p34_inner = f"""
    <table class="top-summary-strip">
      <tr>
        <td><b>Name:</b> {meta["name"]} ({meta["sex"]})</td>
        <td><b>Date:</b> {meta["dob_dot"]} ({meta["day_en"]})</td>
        <td><b>Sunrise:</b> {meta["sunrise"]} | <b>Sunset:</b> {meta["sunset"]}</td>
        <td><b>Dasa Balance:</b> {vim["balance_upper"]}</td>
      </tr>
      <tr>
        <td><b>Time:</b> {meta["tob_dot"]} | <b>SID:</b> {meta["sidereal_time"]}</td>
        <td><b>Place:</b> {meta["place"]} ({meta["lat_short"]}, {meta["lon_short"]})</td>
        <td><b>Lagna:</b> {meta["lagna_en"]} ({meta["lagna_lord_short"]}) | <b>Rashi:</b> {meta["rasi_en"]} ({meta["rasi_lord_short"]})</td>
        <td><b>Nakshatra:</b> {meta["nakshatra_pada_dash"]} ({meta["nakshatra_lord_short"]})</td>
      </tr>
    </table>

    <div class="two-col-grid mt-6">
      <div>
        <div class="box-heading">{T("Planetary Degree And Their Positions (Lal Kitab Teva)", "लाल किताब ग्रह स्थिति, सोया ग्रह एवं नेक/बद विचार")}</div>
        <table class="data-table ultra-compact">
          <thead><tr><th>Planets</th><th>Sign (House)</th><th>Positions</th><th>Soya</th><th>Kismat Jaganewala</th><th>Benefic / Malefic</th></tr></thead>
          <tbody>{lk_p_rows}</tbody>
        </table>
      </div>
      <div class="chart-col">
        <div class="chart-title">{T("Lal Kitab Lagna Chart (Fixed Aries = House 1)", "लाल किताब टेवा कुंडली (खाना नंबर 1 = मेष)")}</div>
        {svg_lk}
      </div>
    </div>

    <div class="box-heading center mt-6">{T("Lal Kitab 35-Year Dasha Cycle", "लाल किताब 35-वर्षीय दशा चक्र")}</div>
    <div class="six-col-grid">{"".join(lk_d_boxes)}</div>
    """
    pages.append(_page_wrapper(34, meta, brand, "Lal Kitab Calculation", "लाल किताब गणित, टेवा एवं दशा चक्र", p34_inner, lang))

    # =========================================================================
    # PAGES 35, 36, 37, 38, 39: PLANET CONSIDERATION IN ASTROLOGY
    # =========================================================================
    pc = wrt["planet_considerations"]
    pc_slices = [
        (35, pc[0:2]),  # Sun, Moon
        (36, pc[2:4]),  # Mars, Mercury
        (37, pc[4:6]),  # Jupiter, Venus
        (38, pc[6:8]),  # Saturn, Rahu
        (39, pc[8:9]),  # Ketu (+ Chamatkari Sutras & Career Rules from 167329767-Lal-Kitab-Hindi.txt!)
    ]
    for p_num, pc_sl in pc_slices:
        pc_html = "".join(
            f"<div class='prose-section'><h3>{L(item['title_en'], item['title_hi'])}</h3><p class='intro-highlight'>{P(item['intro_en'], item['intro_hi'])}</p><p>{P(item['body_en'], item['body_hi'])}</p></div>"
            for item in pc_sl
        )
        extra_p39 = ""
        if p_num == 39:
            sutras_data = wrt["lal_kitab_sutras"]
            sutra_items = "".join(
                f"<li>{P(s['sutra_en'], s['sutra_hi'])}</li>"
                for s in sutras_data["matched_sutras"]
            )
            jp = sutras_data["job_promotion"]
            jp_list = "".join(
                f"<li>{P(en_i, hi_i)}</li>"
                for en_i, hi_i in zip(jp["job_dashas_en"], jp["job_dashas_hi"])
            )
            rins_html = "".join(
                f"<div class='yoga-card'><h4>✦ {L(r['name_en'], r['name_hi'])}</h4><p><b>{T('Cause:', 'कारण:')}</b> {P(r['cause_en'], r['cause_hi'])}<br/><b>{T('Remedy:', 'उपाय:')}</b> {P(r['remedy_en'], r['remedy_hi'])}</p></div>"
                for r in lk["rins"]
            )
            extra_p39 = f"""
            <div class="box-heading mt-10">{T("Lal Kitab Pitra Rin (Ancestral Debts) & Chamatkari Phaladesh Sutras", "लाल किताब पैतृक ऋण एवं चमत्कारी फलादेश सूत्र")}</div>
            {rins_html}
            <div class="prose-section mt-8">
              <h4>{T("Active Chamatkari Sutras in Your Horoscope:", "आपकी कुंडली पर लागू होने वाले चमत्कारी ज्योतिष सूत्र:")}</h4>
              <ul class="remedy-list">{sutra_items}</ul>
              <h4>{T("Job & Promotion Favourable Dasha Rules:", "नौकरी एवं पदोन्नति प्रदान करने वाली दशाएं व गोचर नियम:")}</h4>
              <ul class="remedy-list">{jp_list}</ul>
              <p><em>{P(jp['transit_rule_en'], jp['transit_rule_hi'])}</em></p>
            </div>
            """
        pages.append(_page_wrapper(p_num, meta, brand, "Planet Consideration in Astrology", "नवग्रह फलादेश एवं विशेष सूत्र विचार", f"<div class='prose-block'>{pc_html}{extra_p39}</div>", lang))

    # =========================================================================
    # PAGE 40: SHODASHVARGA TABLE & SHODASHVARGA BHAV TABLE
    # =========================================================================
    col_keys = ["ASC", "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu", "Uranus", "Neptune", "Pluto"]
    col_headers = ["Lagna", "Sun", "Moon", "Mars", "Mer", "Jup", "Ven", "Sat", "Rah", "Ket", "Ure", "Nep", "Plu"]

    sv_sign_rows_html = "".join(
        f"<tr><td class='c'>{r['sn']}</td><td>{L(r['name_en'], r['name_hi'])}</td>"
        + "".join(f"<td class='c'>{r['values'][k]}</td>" for k in col_keys) + "</tr>"
        for r in sv["sign_rows"]
    )
    sv_bhav_rows_html = "".join(
        f"<tr><td class='c'>{r['sn']}</td><td>{L(r['name_en'], r['name_hi'])}</td>"
        + "".join(f"<td class='c {'red-cell' if r['values'][k] in (6,8,12) else ''}'>{r['values'][k]}</td>" for k in col_keys) + "</tr>"
        for r in sv["bhav_rows"]
    )
    p40_inner = f"""
    <div class="box-heading center">{T("Shodashvarga Rashi Table (16 Divisional Charts)", "षोडशवर्ग राशि तालिका")}</div>
    <table class="data-table ultra-compact">
      <thead><tr><th class="c">S.N.</th><th>Shodashvarga</th>{"".join(f"<th class='c'>{h}</th>" for h in col_headers)}</tr></thead>
      <tbody>{sv_sign_rows_html}</tbody>
    </table>

    <div class="box-heading center mt-12">{T("Shodashvarga Bhav Table", "षोडशवर्ग भाव तालिका")}</div>
    <table class="data-table ultra-compact">
      <thead><tr><th class="c">S.N.</th><th>Shodashvarga</th>{"".join(f"<th class='c'>{h}</th>" for h in col_headers)}</tr></thead>
      <tbody>{sv_bhav_rows_html}</tbody>
    </table>
    """
    pages.append(_page_wrapper(40, meta, brand, "Shodashvarga Table", "षोडशवर्ग राशि एवं भाव तालिका", p40_inner, lang))

    # =========================================================================
    # PAGES 41, 42, 43: SHODASHVARGA 16 DIVISIONAL CHARTS
    # =========================================================================
    varga_pages = [
        (41, ["D1", "D2", "D3", "D4", "D7", "D9"]),
        (42, ["D10", "D12", "D16", "D20", "D24", "D27"]),
        (43, ["D30", "D40", "D45", "D60"]),
    ]
    for p_num, codes in varga_pages:
        chart_cells = []
        for vc in codes:
            c_info = sv["charts"][vc]
            svg_c = render_north_indian_svg(c_info["lagna_sign"], c_info["house_planets"], lang=svg_lang, size=220)
            c_title = L(c_info["chart_title_en"], f"{c_info['name_hi']} ({vc})")
            chart_cells.append(f"<div class='chart-col'><div class='chart-title'>{c_title}</div>{svg_c}</div>")

        extra_p43 = ""
        if p_num == 43:
            # On Page 43 bottom (where AstroSage put a shop ad!), we put the authentic Gurukulam Vedic Gemstone, Rudraksha & Mantra Table!
            gem_rows = "".join(
                f"<tr><td><b>{L(g['role_en'], g['role_hi'])}</b></td><td>{L(g['planet_en'], g['planet_hi'])}</td><td><b>{L(g['gem_en'], g['gem_hi'])}</b></td><td>{L(g['metal_en'], g['metal_hi'])} ({L(g['finger_en'], g['finger_hi'])})</td><td>{L(g['rudra_en'], g['rudra_hi'])}</td><td><small>{g['mantra']}</small></td></tr>"
                for g in gems
            )
            extra_p43 = f"""
            <div class="box-heading mt-10">{T("Shivansh Astro-Vastu Vedic Ratna, Rudraksha & Beej Mantra Prescription", "शिवांश ॲस्ट्रो-वास्तू वैदिक रत्न, रुद्राक्ष व बीज मंत्र सल्ला")}</div>
            <table class="data-table ultra-compact">
              <thead><tr><th>Trikona Role</th><th>Planet</th><th>Recommended Gemstone</th><th>Metal &amp; Finger</th><th>Rudraksha</th><th>Vedic Beej Mantra</th></tr></thead>
              <tbody>{gem_rows}</tbody>
            </table>
            """
        pages.append(_page_wrapper(p_num, meta, brand, "Shodashvarga Charts", "षोडशवर्ग कुंडली चक्र", f"<div class='two-col-grid'>{''.join(chart_cells)}</div>{extra_p43}", lang))

    # =========================================================================
    # PAGE 44: KP SYSTEM / NAKSHATRA NADI
    # =========================================================================
    svg_kp = render_north_indian_svg(meta["lagna_sign_num"], kp["kp_chart_houses"], lang=svg_lang, size=250, is_kp=True)
    cusp_rows = "".join(
        f"<tr><td class='c'>{c['cusp']}</td><td class='c'>{c['dms']}</td><td class='c'>{c['rasi']}</td><td class='c'>{c['nak']}</td><td class='c'>{c['sub']}</td><td class='c'>{c['ss']}</td></tr>"
        for c in kp["cuspal_positions"]
    )
    kp_p_rows = "".join(
        f"<tr><td>{p['planet_en']}</td><td class='c'>{p['dms']}</td><td class='c'>{p['rasi']}</td><td class='c'>{p['nak']}</td><td class='c'>{p['sub']}</td><td class='c'>{p['ss']}</td></tr>"
        for p in kp["planetary_positions"]
    )
    h_sig_rows = "".join(
        f"<tr><td class='c'>{r['house']}</td><td>{r['planets_str']}</td></tr>"
        for r in kp["house_significators"]
    )
    p_sig_rows = "".join(
        f"<tr><td>{r['planet_en']}</td><td>{r['houses_str']}</td></tr>"
        for r in kp["planet_signification"]
    )
    kp_vim_boxes = []
    for md in kp["kp_vimshottari"]["mahadashas"]:
        ad_lines = "".join(f"<tr><td>{ad['code']}</td><td>{ad['end_str']}</td></tr>" for ad in md["antardashas"])
        kp_vim_boxes.append(f"""
        <div class="mini-dasha-box">
          <div class="mini-dasha-head">{md['header_en']}<br/><span>{md['range_str']}</span></div>
          <table class="mini-table">{ad_lines}</table>
        </div>
        """)

    rp = kp["ruling_planets"]
    p44_inner = f"""
    <table class="top-summary-strip">
      <tr>
        <td><b>Name:</b> {meta["name"]} ({meta["sex"]})</td>
        <td><b>Date:</b> {meta["dob_dot"]} ({meta["day_en"]}) | <b>Time:</b> {meta["tob_dot"]}</td>
        <td><b>Ayan Type:</b> K. P. New ({meta["kp_ayanamsa_dms"]})</td>
        <td><b>Dasa Balance:</b> {kp["kp_vimshottari"]["balance_upper"]}</td>
      </tr>
    </table>

    <div class="two-col-grid mt-6">
      <div>
        <div class="chart-col">{svg_kp}</div>
        <div class="three-col-grid mt-6">{"".join(kp_vim_boxes)}</div>
      </div>
      <div>
        <div class="box-heading">{T("Ruling Planet", "शासक ग्रह (Ruling Planets)")}</div>
        <table class="data-table ultra-compact">
          <thead><tr><th>{T("Planet", "ग्रह")}</th><th>{T("Rasi Lord", "राशी स्वामी")}</th><th>{T("Nak Lord", "नक्षत्र स्वामी")}</th><th>{T("Sub Lord", "उपस्वामी")}</th></tr></thead>
          <tbody>
            <tr><td>Lagna</td><td>{rp['lagna']['rasi']}</td><td>{rp['lagna']['nak']}</td><td>{rp['lagna']['sub']}</td></tr>
            <tr><td>Moon</td><td>{rp['moon']['rasi']}</td><td>{rp['moon']['nak']}</td><td>{rp['moon']['sub']}</td></tr>
            <tr><td>Day Lord</td><td colspan="3"><b>{rp['day_lord']}</b></td></tr>
          </tbody>
        </table>

        <div class="box-heading mt-4">{T("Cuspal Positions (Placidus)", "भाव संधि स्पष्ट (Cusps)")}</div>
        <table class="data-table ultra-compact">
          <thead><tr><th>{T("Cusp", "भाव संधि")}</th><th>{T("Degree", "अंश/कला")}</th><th>{T("Sign Lord", "राशी स्वामी")}</th><th>{T("Star Lord", "नक्षत्र स्वामी")}</th><th>{T("Sub Lord", "उपस्वामी")}</th><th>{T("Sub-Sub Lord", "उप-उपस्वामी")}</th></tr></thead>
          <tbody>{cusp_rows}</tbody>
        </table>

        <div class="box-heading mt-4">{T("Planetary Positions (KP)", "ग्रह स्पष्ट (KP)")}</div>
        <table class="data-table ultra-compact">
          <thead><tr><th>{T("Planet", "ग्रह")}</th><th>{T("Degree", "अंश/कला")}</th><th>{T("Sign Lord", "राशी स्वामी")}</th><th>{T("Star Lord", "नक्षत्र स्वामी")}</th><th>{T("Sub Lord", "उपस्वामी")}</th><th>{T("Sub-Sub Lord", "उप-उपस्वामी")}</th></tr></thead>
          <tbody>{kp_p_rows}</tbody>
        </table>

        <div class="two-col-grid mt-4">
          <div>
            <div class="box-heading">{T("Significators of Houses", "भाव कारक ग्रह")}</div>
            <table class="data-table ultra-compact">
              <thead><tr><th>House</th><th>Planet</th></tr></thead>
              <tbody>{h_sig_rows}</tbody>
            </table>
          </div>
          <div>
            <div class="box-heading">{T("Planet Signification", "ग्रहों के कारक भाव")}</div>
            <table class="data-table ultra-compact">
              <thead><tr><th>Planet</th><th>House</th></tr></thead>
              <tbody>{p_sig_rows}</tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
    """
    pages.append(_page_wrapper(44, meta, brand, "KP System / Nakshatra Nadi", "कृष्णमूर्ति पद्धति (KP System / नक्षत्र नाड़ी)", p44_inner, lang))

    # =========================================================================
    # PAGES 45, 46, 47, 48: VIMSHOTTARI DASHA - PRATYANTAR (15 blocks per page in 5x3 grid)
    # =========================================================================
    pd_blocks = kp["kp_vimshottari"]["pratyantar_blocks"]
    for p_idx, p_num in enumerate([45, 46, 47, 48]):
        sl = pd_blocks[p_idx * 15:(p_idx + 1) * 15]
        boxes = []
        for b in sl:
            r_html = "".join(f"<tr><td>{r['code']}</td><td>{r['end_str']}</td></tr>" for r in b["rows"])
            boxes.append(f"""
            <div class="mini-dasha-box">
              <div class="mini-dasha-head">{b['title']}<br/><span>From {b['from_str']} - To {b['to_str']}</span></div>
              <table class="mini-table">{r_html}</table>
            </div>
            """)
        pages.append(_page_wrapper(p_num, meta, brand, "Vimshottari Dasha - Pratyantar", "विंशोत्तरी प्रत्यंतर दशा तालिका", f"<div class='five-col-grid'>{''.join(boxes)}</div>", lang))

    # =========================================================================
    # PAGE 49: FRIENDSHIP TABLE (PERMANENT, TEMPORAL, FIVE-FOLD)
    # =========================================================================
    f_keys = fr["keys"]

    def _render_friend_grid(matrix_dict):
        rows = []
        for k1 in f_keys:
            cells = "".join(f"<td class='c'>{to_marathi(fr['hi_map'][matrix_dict[k1][k2]]) if is_mr else (fr['hi_map'][matrix_dict[k1][k2]] if is_hi else matrix_dict[k1][k2])}</td>" for k2 in f_keys)
            rows.append(f"<tr><td class='c'><b>{k1}</b></td>{cells}</tr>")
        return f"""
        <table class="data-table compact">
          <thead><tr><th></th>{"".join(f"<th class='c'>{k}</th>" for k in f_keys)}</tr></thead>
          <tbody>{"".join(rows)}</tbody>
        </table>
        """

    p49_inner = f"""
    <div class="box-heading">{T("Permanent Friendship (Naisargika Maitri)", "नैसर्गिक (स्थायी) मैत्री चक्र")}</div>
    {_render_friend_grid(fr["permanent"])}
    <div class="box-heading mt-12">{T("Temporal Friendship (Tatkalika Maitri)", "तात्कालिक मैत्री चक्र")}</div>
    {_render_friend_grid(fr["temporal"])}
    <div class="box-heading mt-12">{T("Five-fold Friendship (Panchadha Maitri)", "पंचधा मैत्री चक्र")}</div>
    {_render_friend_grid(fr["five_fold"])}
    """
    pages.append(_page_wrapper(49, meta, brand, "Friendship Table", "ग्रह मैत्री चक्र (नैसर्गिक, तात्कालिक एवं पंचधा)", p49_inner, lang))

    # =========================================================================
    # PAGE 50: SHADBALA AND BHAVABALA - STRENGTH CALCULATIONS
    # =========================================================================
    sb_p_keys = shad["planets"]
    sb_rows_html = "".join(
        f"<tr class='{'tot-row' if 'Total' in en_lbl or 'Rupas' in en_lbl or 'Rank' in en_lbl else ''}'><td><b>{L(en_lbl, hi_lbl)}</b></td>"
        + "".join(f"<td class='c'>{vals[k]}</td>" for k in sb_p_keys) + "</tr>"
        for en_lbl, hi_lbl, vals in shad["rows"]
    )
    bb_rows_html = "".join(
        f"<tr class='{'tot-row' if 'Total' in en_lbl or 'Rank' in en_lbl else ''}'><td><b>{L(en_lbl, hi_lbl)}</b></td>"
        + "".join(f"<td class='c'>{v}</td>" for v in vals) + "</tr>"
        for en_lbl, hi_lbl, vals in shad["bhav_rows"]
    )
    p50_inner = f"""
    <p class="small-intro">{P(
      "Shadbala is a foundational mathematical method in Vedic astrology that calculates the six-fold strength of planets (Sthana, Dig, Kala, Chesta, Naisargika, and Drik Bala) and the 12 Bhavas.",
      "षड्बल वैदिक ज्योतिष की वह गणितीय पद्धति है जिसके द्वारा सप्त ग्रहों के छह प्रकार के बलों (स्थान बल, दिग्बल, काल बल, चेष्टा बल, नैसर्गिक बल और दृक् बल) तथा द्वादश भावों के बल का सूक्ष्म आकलन किया जाता है।"
    )}</p>
    <div class="box-heading">{T("ShadBala Table", "षड्बल तालिका")}</div>
    <table class="data-table ultra-compact">
      <thead><tr><th>{T("Strength Source", "षड्बल घटक")}</th><th>{T("SUN", "रवी")}</th><th>{T("MOON", "चंद्र")}</th><th>{T("MARS", "मंगळ")}</th><th>{T("MER", "बुध")}</th><th>{T("JUP", "गुरू")}</th><th>{T("VEN", "शुक्र")}</th><th>{T("SAT", "शनि")}</th></tr></thead>
      <tbody>{sb_rows_html}</tbody>
    </table>

    <div class="box-heading mt-8">{T("BhavBala Table", "भावबल तालिका")}</div>
    <table class="data-table ultra-compact">
      <thead><tr><th>{T("Bhav Strength", "भाव सामर्थ्य")}</th>{"".join(f"<th class='c'>{i}</th>" for i in range(1,13))}</tr></thead>
      <tbody>{bb_rows_html}</tbody>
    </table>
    """
    pages.append(_page_wrapper(50, meta, brand, "Shadbala and Bhavabala – Strength Calculations", "षड्बल एवं भावबल — ग्रह एवं भाव शक्ति गणना", p50_inner, lang))

    # =========================================================================
    # PAGES 51, 52, 53: PLANETARY ASPECTS (WESTERN, BHAV MADHYA, KP CUSP)
    # =========================================================================
    aspect_legend = """
    <div class="box-heading mt-8">Note : Aspect Orbs &amp; Weights</div>
    <table class="data-table ultra-compact">
      <thead><tr><th>{T("Abbr-Aspect", "दृष्टी प्रकार")}</th><th>{T("Degree", "अंश")}</th><th>{T("Orb", "कक्षा")}</th><th>{T("Weight", "भार")}</th><th>{T("Abbr-Aspect", "दृष्टी प्रकार")}</th><th>{T("Degree", "अंश")}</th><th>{T("Orb", "कक्षा")}</th><th>{T("Weight", "भार")}</th></tr></thead>
      <tbody>
        <tr><td>CONJ-CONJUNCTION</td><td>0</td><td>15</td><td>10</td><td>OPPN-OPPOSITION</td><td>180</td><td>15</td><td>10</td></tr>
        <tr><td>TRIN-TRINE</td><td>120</td><td>6</td><td>3</td><td>SQUR-SQUARE</td><td>90</td><td>6</td><td>3</td></tr>
        <tr><td>SEXT-SEXTILE</td><td>60</td><td>6</td><td>3</td><td>SSQU-SEMI SQUARE</td><td>45</td><td>1</td><td>1</td></tr>
        <tr><td>NONL-NONILE</td><td>40</td><td>1</td><td>1</td><td>QUIN-QUINLILE</td><td>72</td><td>1</td><td>1</td></tr>
        <tr><td>SQQD-SESQUIQUA..</td><td>135</td><td>1</td><td>1</td><td>QCUN-QUINCUNC</td><td>150</td><td>1</td><td>1</td></tr>
      </tbody>
    </table>
    """

    # Page 51: Planet-to-Planet
    p51_th = "".join(f"<th class='c'>{h['label']}<br/><small>{h['deg_str']}<br/>{h['min_str']}</small></th>" for h in asp["planet_headers"])
    p51_tr = "".join(
        f"<tr><td><b>{r['header']['label']}</b><br/><small>{r['header']['row_str']}</small></td>"
        + "".join(f"<td class='c tiny-cell'>{c.replace(chr(10), '<br/>')}</td>" for c in r["cells"]) + "</tr>"
        for r in asp["planet_matrix"]
    )
    pages.append(_page_wrapper(51, meta, brand, "Planetary Aspects (Western)", "पाश्चात्य ग्रह दृष्टि चक्र", f"<table class='data-table ultra-compact'><thead><tr><th></th>{p51_th}</tr></thead><tbody>{p51_tr}</tbody></table>{aspect_legend}", lang))

    # Page 52: Aspects on Bhav Madhya
    p52_th = "".join(f"<th class='c'>{h['num']}<br/><small>{h['deg_str']}<br/>{h['min_str']}</small></th>" for h in asp["bhav_headers"])
    p52_tr = "".join(
        f"<tr><td><b>{r['header']['label']}</b><br/><small>{r['header']['row_str']}</small></td>"
        + "".join(f"<td class='c tiny-cell'>{c.replace(chr(10), '<br/>')}</td>" for c in r["cells"]) + "</tr>"
        for r in asp["bhav_matrix"]
    )
    pages.append(_page_wrapper(52, meta, brand, "Aspects On Bhav Madhya", "भाव मध्य पर ग्रह दृष्टि", f"<table class='data-table ultra-compact'><thead><tr><th></th>{p52_th}</tr></thead><tbody>{p52_tr}</tbody></table>{aspect_legend}", lang))

    # Page 53: Aspects on KP Cusp
    p53_th = "".join(f"<th class='c'>{h['num']}<br/><small>{h['deg_str']}<br/>{h['min_str']}</small></th>" for h in asp["kp_headers"])
    p53_tr = "".join(
        f"<tr><td><b>{r['header']['label']}</b><br/><small>{r['header']['row_str']}</small></td>"
        + "".join(f"<td class='c tiny-cell'>{c.replace(chr(10), '<br/>')}</td>" for c in r["cells"]) + "</tr>"
        for r in asp["kp_matrix"]
    )
    pages.append(_page_wrapper(53, meta, brand, "Aspects On KP Cusp", "के.पी. भाव संधि पर ग्रह दृष्टि", f"<table class='data-table ultra-compact'><thead><tr><th></th>{p53_th}</tr></thead><tbody>{p53_tr}</tbody></table>{aspect_legend}", lang))

    # =========================================================================
    # PAGE 54: ASHTAKVARGA TABLE & ASHTAKVARGA CHART
    # =========================================================================
    svg_av = render_ashtakavarga_svg(ash["chart_houses"], size=310)
    av_full_rows = "".join(
        f"<tr><td><b>{L(r['name_4'], r['name_hi'])}</b></td>" + "".join(f"<td class='c'>{v}</td>" for v in r["values"]) + "</tr>"
        for r in ash["bhinna_rows"]
    )
    p54_inner = f"""
    <table class="data-table compact">
      <thead><tr><th>Rashi No.</th>{"".join(f"<th class='c'>{i}</th>" for i in range(1,13))}</tr></thead>
      <tbody>{av_full_rows}{av_tot_html}</tbody>
    </table>
    <div class="chart-col mt-16">
      <div class="chart-title">{T("Sarvashtakvarga Chart:", "सर्वाष्टकवर्ग कुंडली चक्र:")}</div>
      {svg_av}
    </div>
    """
    pages.append(_page_wrapper(54, meta, brand, "Ashtakvarga Table", "अष्टकवर्ग तालिका एवं सर्वाष्टकवर्ग चक्र", p54_inner, lang))

    # =========================================================================
    # PAGE 55: PRASTHARASHTAKVARGA TABLES
    # =========================================================================
    r_hdrs = ["Ar", "Ta", "Ge", "Ca", "Le", "Vi", "Li", "Sc", "Sa", "Ca", "Aq", "Pi", "ToT"]
    prasthara_boxes = []
    for pid in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
        pt = ash["prasthara_tables"][pid]
        p_rows = "".join(
            f"<tr><td><b>{r['contributor']}</b></td>" + "".join(f"<td class='c'>{v}</td>" for v in r["values"]) + f"<td class='c'><b>{r['total']}</b></td></tr>"
            for r in pt["rows"]
        )
        t_row = "<tr class='tot-row'><td><b>Total</b></td>" + "".join(f"<td class='c'>{v}</td>" for v in pt["totals"]) + f"<td class='c'>{pt['grand_total']}</td></tr>"
        prasthara_boxes.append(f"""
        <div>
          <div class="box-heading">{L(pt['planet_en'], pt['planet_hi'])}</div>
          <table class="data-table ultra-compact">
            <thead><tr><th></th>{"".join(f"<th class='c'>{h}</th>" for h in r_hdrs)}</tr></thead>
            <tbody>{p_rows}{t_row}</tbody>
          </table>
        </div>
        """)
    pages.append(_page_wrapper(55, meta, brand, "Prastharashtakvarga Tables", "प्रस्ताराष्टकवर्ग तालिकाएं", f"<div class='two-col-grid'>{''.join(prasthara_boxes)}</div>", lang))

    # =========================================================================
    # PAGE 56: EASY PERSONAL RASHI & IDENTITY GUIDE — SUPERPOWERS, LUCKY FACTORS & LIFE PATH
    # (आपकी राशि का सम्पूर्ण परिचय — श्रेष्ठ गुण, शुभ कारक व जीवन मार्गदर्शन)
    # =========================================================================
    moon_p_obj = next((p for p in data["planets"] if p["id"] == "Moon"), None)
    rasi_idx = moon_p_obj["sign_idx"] if moon_p_obj else (meta.get("rasi_sign_num", 1) - 1) % 12
    r_guide = RASHI_GUIDE_DATA.get(rasi_idx, RASHI_GUIDE_DATA[0])

    p_rashi_inner = f"""
    <div class="prose-block">
      <div class="highlight-banner" style="font-size:12px; border-left:4px solid #B45309;">
        <strong>{T(f"Your Moon Sign (Janma Rashi) is {meta['rasi_en']} &amp; Ascendant is {meta['lagna_en']}", f"आपकी जन्म राशि {meta['rasi_hi']} एवं जन्म लग्न {meta['lagna_hi']} है")}</strong><br/>
        <span style="font-size:10px; color:#78350F;">{T("Understand your core superpowers, lucky elements, mindset, and career strengths in crystal clear simple words.", "अपनी जन्म राशि के सबसे श्रेष्ठ गुण, शुभ कारक, स्वभाव, आंतरिक शक्ति व सावधानियों का सरल मार्गदर्शन।")}</span>
      </div>

      <div class="two-col-grid mt-6">
        <div class="lk-card">
          <h4 style="color:#7C2D12; font-size:11.5px;">🌟 {T("1. Lagna vs Moon Rashi (लग्न और राशि का सरल अर्थ)", "लग्न और जन्म राशि में क्या अंतर है?")}</h4>
          <p style="margin:4px 0;"><strong>• {T("Ascendant (Lagna):", "जन्म लग्न:")}</strong> {L(meta['lagna_en'], meta['lagna_hi'])} ({T('Lord: ' + meta['lagna_lord_en'], 'स्वामी: ' + meta['lagna_lord_hi'])})<br/>
          <small style="color:#57534E;">{T("Represents your physical body, vitality, health, and how the outside world perceives you.", "आपके शरीर, स्वास्थ्य, जीवन शक्ति और समाज में आपकी पहचान व प्रतिष्ठा का प्रतिनिधित्व करता है।")}</small></p>

          <p style="margin:4px 0;"><strong>• {T("Moon Sign (Rashi):", "जन्म राशि:")}</strong> {L(meta['rasi_en'], meta['rasi_hi'])} ({T('Lord: ' + meta['rasi_lord_en'], 'स्वामी: ' + meta['rasi_lord_hi'])})<br/>
          <small style="color:#57534E;">{T("Represents your subconscious mind, emotional core, inner peace, and natural instincts.", "आपके मन, आंतरिक भावनाओं, विचारों, मानसिक शांति व स्वाभाविक प्रवृत्तियों का दर्पण है।")}</small></p>

          <p style="margin:4px 0;"><strong>• {T("Birth Nakshatra:", "जन्म नक्षत्र:")}</strong> {L(meta['nakshatra_pada_en'], meta['nakshatra_pada_hi'])}<br/>
          <small style="color:#57534E;">{T("The cosmic frequency that shapes your life impulses and karmic blueprint.", "वह सूक्ष्म खगोलीय नक्षत्र जो आपके प्रारब्ध कर्मों और स्वाभाविक प्रतिभा को दिशा देता है।")}</small></p>
        </div>

        <div class="lk-card">
          <h4 style="color:#991B1B; font-size:11.5px;">⚡ {T("2. Core Superpowers of Your Rashi (आपकी राशि के श्रेष्ठ गुण)", "आपकी राशि के सबसे श्रेष्ठ गुण एवं अद्भुत विशेषताएं")}</h4>
          <div style="background:rgba(254, 243, 199, 0.7); padding:5px 8px; border-radius:6px; font-weight:700; color:#7C2D12; margin-bottom:5px; font-size:10.5px;">
            {L(r_guide['superpower_en'], r_guide['superpower_hi'])}
          </div>
          <p style="margin:0; font-size:10.4px;">
            <strong>{T("Mindset & Temperament:", "स्वभाव व कार्यशैली:")}</strong><br/>
            {L(r_guide['mindset_en'], r_guide['mindset_hi'])}
          </p>
        </div>
      </div>

      <div class="box-heading mt-6">{T("Complete Lucky Factors & Affinity Matrix (सम्पूर्ण शुभ कारक एवं अनुकूलता चक्र)", "आपकी राशि के सम्पूर्ण शुभ कारक एवं अनुकूलता चक्र")}</div>
      <table class="data-table compact">
        <thead>
          <tr>
            <th style="width:25%;">{T("Auspicious Attribute", "शुभ कारक / तत्व")}</th>
            <th style="width:35%;">{T("Favourable Values for You", "आपके लिए शुभ मान")}</th>
            <th>{T("Astrological Significance & Practical Guidance", "ज्योतिषीय महत्व व दैनिक जीवन में प्रयोग")}</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><b>{T("Element & Direction", "तत्व एवं शुभ दिशा")}</b></td>
            <td><strong style="color:#7C2D12;">{L(r_guide['element_en'], r_guide['element_hi'])}</strong> • {L(r_guide['direction_en'], r_guide['direction_hi'])}</td>
            <td>{T("Face this direction during study, worship, or important negotiations for enhanced clarity.", "अध्ययन, पूजा अथवा महत्वपूर्ण वार्ता के समय इस दिशा की ओर मुख करना अत्यंत शुभकारी होता है।")}</td>
          </tr>
          <tr>
            <td><b>{T("Lucky Gemstone & Metal", "भाग्य रत्न एवं धातु")}</b></td>
            <td><strong>{fav.get('stone', 'रत्न')}</strong> • {fav.get('metal', 'धातू')}</td>
            <td>{T("Strengthens your ruling planet, boosts immunity, aura radiance, and protection from evil eyes.", "लग्न व राशि स्वामी को बल प्रदान कर शारीरिक आभा मंडल, आत्मविश्वास व आत्मरक्षा को सुदृढ़ करता है।")}</td>
          </tr>
          <tr>
            <td><b>{T("Lucky Numbers", "शुभ व भाग्यशाली अंक")}</b></td>
            <td><span class="red-cell">{fav.get('lucky_num', '1')}</span> (मित्र अंक: {fav.get('good_nums', '1, 3, 9')})</td>
            <td>{T("Use these digits for crucial contracts, vehicle numbers, bank account dates, and house keys.", "महत्वपूर्ण अनुबंधों, नवीन कार्यों, वाहन संख्या एवं तिथि निर्धारण में इन अंकों को प्राथमिकता दें।")}</td>
          </tr>
          <tr>
            <td><b>{T("Lucky Days & Friends", "शुभ वार एवं मित्र राशियां")}</b></td>
            <td><strong>{fav.get('days', 'वार')}</strong> • {fav.get('signs', 'मित्र राशियां')}</td>
            <td>{T("Best weekdays for launching new ventures; native persons of friendly signs provide lifelong trust.", "नए व्यवसाय या शुभ कार्य के आरंभ हेतु सर्वोत्तम दिन; मित्र राशि वाले लोग विश्वसनीय सहयोगी बनते हैं।")}</td>
          </tr>
          <tr>
            <td><b>{T("Ideal Wealth Careers", "अनुकूल आजीविका क्षेत्र")}</b></td>
            <td colspan="2"><strong>{L(r_guide['careers_en'], r_guide['careers_hi'])}</strong></td>
          </tr>
        </tbody>
      </table>

      <div class="yoga-card mt-6" style="border:1.2px solid #F59E0B; background:rgba(255, 251, 235, 0.95); padding:8px 12px;">
        <h4 style="color:#9A3412; font-size:11px; margin:0 0 3px 0;">⚠️ {T("Pitfalls & Weaknesses to Guard Against (सावधानियां एवं कमजोरियों से बचाव):", "किन सावधानियों व कमजोरियों से सतर्क रहें:")}</h4>
        <p style="margin:0; font-size:10.2px; line-height:1.5;">
          {L(r_guide['pitfalls_en'], r_guide['pitfalls_hi'])} {T("Practicing daily mindfulness, calm breathing, and avoiding hasty emotional reactions will transform these inclinations into remarkable inner strengths.", "दैनिक प्राणायाम, धैर्यपूर्ण चिंतन और बिना सोचे-समझे प्रतिक्रिया न देने से ये कमजोरियां स्थायी शक्ति में बदल जाती हैं।")}
        </p>
      </div>
    </div>
    """
    pages.append(_page_wrapper(56, meta, brand, "Your Rashi & Identity Guide — Superpowers, Lucky Factors & Life Guidance", "आपकी राशि का सम्पूर्ण परिचय — श्रेष्ठ गुण, शुभ कारक व जीवन मार्गदर्शन", p_rashi_inner, lang))

    # =========================================================================
    # PAGE 57: DEDICATED MARRIAGE PROSPECTS & KUNDLI MILAN GUIDE (36 GUNA MILAN)
    # (विवाह एवं वैवाहिक सुख सम्पूर्ण विश्लेषण — 36 गुण मिलान, मांगलिक विचार व जीवनसाथी)
    # =========================================================================
    d1_houses = sv["charts"]["D1"]["house_planets"]
    p_in_7 = d1_houses.get(7, [])
    p_in_7_names = []
    for p in p_in_7:
        if isinstance(p, dict):
            pid = p.get("id", "")
            p_lbl = L((pid or p.get("short_en")), (p.get("short_hi") or pid))
        else:
            p_lbl = str(p)
        p_in_7_names.append(p_lbl)
    p_in_7_str = ", ".join(p_in_7_names) if p_in_7_names else T("No malefic occupying (शुद्ध भाव)", "कोई क्रूर ग्रह स्थित नहीं (शुद्ध भाव)")
    lagna_sign_idx = sv["charts"]["D1"]["lagna_sign"] - 1
    seventh_sign_idx = (lagna_sign_idx + 6) % 12
    seventh_sign_en = RASHI_NAMES_EN[seventh_sign_idx]
    seventh_sign_hi = RASHI_NAMES_HI[seventh_sign_idx]
    seventh_lord_en = RASHI_LORDS_EN[seventh_sign_idx]
    seventh_lord_hi = RASHI_LORDS_HI[seventh_sign_idx]
    is_manglik = mang.get("is_manglik", False)
    manglik_status = T("Active (मांगलिक प्रभाव)", "मांगलिक प्रभाव विद्यमान") if is_manglik else T("Free (दोष मुक्त)", "मांगलिक दोष नहीं है")

    p_marriage_inner = f"""
    <div class="prose-block">
      <div class="highlight-banner" style="font-size:12px; border-left:4px solid #B45309;">
        <strong>{T("Comprehensive Marriage &amp; Partner Compatibility Guide (विवाह एवं दांपत्य सुख सम्पूर्ण विश्लेषण)", "विवाह एवं दांपत्य सुख सम्पूर्ण विश्लेषण — वर-कन्या कुंडली मिलान गाइड")}</strong><br/>
        <span style="font-size:10px; color:#78350F;">{T("How to check boy and girl horoscopes, 7th house marital happiness, Manglik dosha cancellation, and Ashtakoot 36-Guna matching.", "सप्तम भाव व सप्तमेश विश्लेषण, मांगलिक दोष व परिहार के नियम, तथा वर-कन्या अष्टकूट 36 गुण मिलान का संपूर्ण रहस्य।")}</span>
      </div>

      <div class="two-col-grid mt-6">
        <div class="lk-card">
          <h4 style="color:#7C2D12; font-size:11.5px;">💍 {T("1. 7th House & Marital Significations (सप्तम भाव व जीवनसाथी)", "सप्तम भाव एवं जीवनसाथी का स्वरूप")}</h4>
          <p style="margin:3px 0;"><strong>• {T("7th House Rashi & Lord:", "सप्तम भाव राशि व स्वामी:")}</strong> {L(seventh_sign_en, seventh_sign_hi)} ({T('Lord: ' + seventh_lord_en, 'सप्तमेश: ' + seventh_lord_hi)})</p>
          <p style="margin:3px 0;"><strong>• {T("Planets in 7th House:", "सप्तम भाव में स्थित ग्रह:")}</strong> {p_in_7_str}</p>
          <p style="margin:3px 0;"><strong>• {T("Natural Karakas:", "विवाह के नैसर्गिक कारक:")}</strong> {T("Jupiter (Husband) & Venus (Wife)", "गुरु (पति सुख कारक) एवं शुक्र (पत्नी व दांपत्य सुख कारक)")}</p>
          <p style="margin:3px 0; font-size:10px; color:#57534E;">{T(
            f"The 7th lord ({seventh_lord_en}) governs partner temperament and domestic tranquility. Auspicious Jupiter/Venus influences ensure an educated, loyal, and supportive life partner.",
            f"सप्तमेश ({seventh_lord_hi}) जीवनसाथी के स्वभाव व पारिवारिक तालमेल को दर्शाता है। शुभ गुरु व शुक्र का अनुकूल प्रभाव सुसंस्कृत, निष्ठावान व सहयोगी जीवनसाथी प्रदान करता है।"
          )}</p>
        </div>

        <div class="lk-card">
          <h4 style="color:#991B1B; font-size:11.5px;">🔥 {T("2. Manglik Dosha & Complete Parihara (मांगलिक विचार व परिहार)", "मांगलिक विचार एवं सम्पूर्ण परिहार (काट) के नियम")}</h4>
          <p style="margin:3px 0;"><strong>• {T("Native's Status:", "आपकी मांगलिक स्थिति:")}</strong> <span class="{'red-cell' if mang.get('is_manglik') else ''}"><strong>{manglik_status}</strong></span></p>
          <p style="margin:3px 0; font-size:10px;"><strong>• {T("Checked Houses:", "जांचे गए भाव:")}</strong> 1st (Lagna), 4th (Domestic Bliss), 7th (Spouse), 8th (Longevity), 12th (Expenses)</p>
          <div style="background:rgba(254, 243, 199, 0.7); padding:4px 8px; border-radius:6px; font-size:9.8px; margin-top:4px;">
            <strong>{T("Classical Cancellation Exceptions (परिहार नियम):", "शास्त्रसम्मत परिहार (काट) नियम:")}</strong><br/>
            1. {T("Dosh Samya: Partner also having Mars or Saturn/Rahu in 1, 4, 7, 8, 12 completely balances the dosha.", "दोष साम्य: यदि जीवनसाथी की कुंडली में भी 1, 4, 7, 8, 12वें भाव में मंगल/शनि/राहु हो तो दोष पूर्णतः समाप्त हो जाता है।")}<br/>
            2. {T("Mars in own sign (Aries/Scorpio) or exalted sign (Capricorn) loses malefic hostility.", "मंगल स्वराशि (मेष/वृश्चिक) या उच्च राशि (मकर) में हो तो मांगलिक दोष का अनिष्ट प्रभाव निष्प्रभावी हो जाता है।")}<br/>
            3. {T("Aspect of benefic Jupiter on Mars nullifies friction and protects marital longevity.", "शुभ बृहस्पति की मंगल पर दृष्टि होने से अमंगलकारी प्रभाव शांत हो जाता है।")}
          </div>
        </div>
      </div>

      <div class="box-heading mt-6">{T("Ashtakoot 36-Guna Milan Comprehensive Matrix (वर-कन्या अष्टकूट 36 गुण मिलान तालिका)", "वर-कन्या अष्टकूट 36 गुण मिलान सम्पूर्ण तालिका")}</div>
      <table class="data-table compact">
        <thead>
          <tr>
            <th style="width:14%;">{T("Koot Name", "कूट का नाम")}</th>
            <th style="width:9%;" class="c">{T("Max Pts", "अधिकतम")}</th>
            <th style="width:25%;">{T("Governing Domain", "क्षेत्र व प्रभाव")}</th>
            <th>{T("Astrological Significance for Boy & Girl Compatibility", "वर-कन्या मिलान में महत्व एवं फलादेश")}</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><b>1. {T("Varna", "वर्ण")}</b></td><td class="c"><b>1</b></td>
            <td>{T("Ego & Work Tendency", "कार्य प्रवृत्ति व आध्यात्मिक स्तर")}</td>
            <td>{T("Ensures intellectual compatibility and mutual ego alignment between boy and girl.", "वर और कन्या के बीच बौद्धिक स्तर, कर्तव्य भावना और अहंकार का सहज सामंजस्य सुनिश्चित करता है।")}</td>
          </tr>
          <tr>
            <td><b>2. {T("Vasya", "वश्य")}</b></td><td class="c"><b>2</b></td>
            <td>{T("Mutual Attraction & Control", "परस्पर आकर्षण व समर्पण")}</td>
            <td>{T("Evaluates emotional pull, domestic loyalty, and natural willingness to cooperate.", "दांपत्य जीवन में परस्पर आकर्षण, स्नेह, वफादारी तथा एक-दूसरे के प्रति सहयोग की भावना परखता है।")}</td>
          </tr>
          <tr>
            <td><b>3. {T("Tara", "तारा")}</b></td><td class="c"><b>3</b></td>
            <td>{T("Destiny & Lifespan Health", "भाग्य, स्वास्थ्य व आयु")}</td>
            <td>{T("Calculates birth-star cosmic affinity across 9 Taras for prosperity, luck, and vitality.", "जन्म नक्षत्रों के आधार पर संपत, विपत, क्षेम आदि 9 तारों द्वारा स्वास्थ्य, दीर्घायु व भाग्य का विचार करता है।")}</td>
          </tr>
          <tr>
            <td><b>4. {T("Yoni", "योनि")}</b></td><td class="c"><b>4</b></td>
            <td>{T("Physical & Biological Bliss", "जैविक व शारीरिक अनुकूलता")}</td>
            <td>{T("Evaluates intimacy temperament and physical attraction via 14 animal archetypes.", "14 पशु योनियों के माध्यम से दांपत्य सुख, शारीरिक आकर्षण और जैविक सामंजस्य का निर्धारण करता है।")}</td>
          </tr>
          <tr>
            <td><b>5. {T("Graha Maitri", "ग्रहमैत्री")}</b></td><td class="c"><b>5</b></td>
            <td>{T("Mental Friendship & Outlook", "मानसिक मित्रता व वैचारिक तालमेल")}</td>
            <td>{T("Moon sign lords' friendship guarantees deep psychological bonding, peace, and harmony.", "चंद्र राशि स्वामियों की मित्रता जातक व जीवनसाथी के बीच वैचारिक समानता व आजीवन मानसिक शांति देती है।")}</td>
          </tr>
          <tr>
            <td><b>6. {T("Gana", "गण")}</b></td><td class="c"><b>6</b></td>
            <td>{T("Temperament & Social Behavior", "स्वभाव, आचरण व जीवनशैली")}</td>
            <td>{T("Harmonizes Deva, Manushya, and Rakshasa temperaments for peaceful daily coexistence.", "देव, मनुष्य व राक्षस गणों के माध्यम से स्वभाव, सहिष्णुता, सामाजिक व्यवहार व दिनचर्या का मिलान होता है।")}</td>
          </tr>
          <tr>
            <td><b>7. {T("Bhakoot", "भकूट")}</b></td><td class="c"><b>7</b></td>
            <td>{T("Family Growth & Prosperity", "वंश वृद्धि, प्रेम व समृद्धि")}</td>
            <td>{T("Prevents 6/8, 9/5, 2/12 doshas; secures financial abundance, mutual love, and progeny welfare.", "षडाष्टक, नवपंचम व द्विर्द्वादश दोष से रक्षा कर वंश वृद्धि, दीर्घायु, प्रेम व आर्थिक संपन्नता प्रदान करता है।")}</td>
          </tr>
          <tr>
            <td><b>8. {T("Nadi", "नाड़ी")}</b></td><td class="c"><b>8</b></td>
            <td>{T("Genetics, Progeny & Vitality", "आनुवंशिकी, रक्त समूह व संतान सुख")}</td>
            <td>{T("Adi, Madhya, and Antya Nadi compatibility guarantees healthy genetic lineage and robust child health.", "आदि, मध्य व अंत्य नाड़ी का मिलान संतान सुख, शारीरिक आरोग्यता, रक्त समूह व आनुवंशिक रक्षा करता है।")}</td>
          </tr>
          <tr class="tot-row">
            <td><b>{T("Total Score", "कुल प्राप्तांक")}</b></td><td class="c"><b>36</b></td>
            <td colspan="2">{T("Above 18 points is acceptable; 25 to 32 is highly auspicious (Uttam); 33 to 36 is supreme soulmate bond.", "18 से अधिक गुण ग्राह्य; 25 से 32 गुण अत्यंत शुभ (उत्तम मिलान); 33 से 36 गुण सर्वोत्तम आत्मिक मिलन है।")}</td>
          </tr>
        </tbody>
      </table>

      <div class="two-col-grid mt-4">
        <div class="note-box" style="margin-top:0; font-size:9.5px; padding:6px 10px;">
          <strong>⚖️ {T("Papa Samya Check (पाप साम्य विचार):", "पाप साम्य विचार (संतुलन):")}</strong><br/>
          {T(
            "In Vedic matching, Papa Samya balances malefic points of Saturn, Mars, Sun, and Rahu in 1st, 2nd, 4th, 7th, 8th, and 12th houses for both boy and girl, ensuring mutual marital longevity.",
            "अष्टकूट गुण मिलान के साथ वर-कन्या के 1, 2, 4, 7, 8, 12वें भाव में क्रूर ग्रहों (शनि, मंगल, सूर्य, राहु) के पाप अंकों का साम्य किया जाता है ताकि दांपत्य में आयु व स्वास्थ्य का संतुलन रहे।"
          )}
        </div>
        <div class="note-box" style="margin-top:0; font-size:9.5px; padding:6px 10px;">
          <strong>⏳ {T("Dasha Sandhi Check (दशा संधि विचार):", "दशा संधि विचार (दशा मिलान):")}</strong><br/>
          {T(
            "Verifies that both prospective spouses do not undergo critical major dasha transitions (such as concluding Saturn, Rahu, or Ketu mahadashas) at the exact same juncture.",
            "यह जांचा जाता है कि वर व कन्या दोनों की कुंडली में एक ही समय पर किसी मुख्य महादशा का समापन (दशा संधि) न हो रहा हो, जिससे किसी भी आकस्मिक पारिवारिक संकट से पूर्ण सुरक्षा मिले।"
          )}
        </div>
      </div>
    </div>
    """
    pages.append(_page_wrapper(57, meta, brand, "Marriage Prospects & Kundli Milan Guide — 7th House, Manglik & Ashtakoot Guna", "विवाह एवं दांपत्य जीवन सम्पूर्ण विश्लेषण — 36 गुण मिलान, मांगलिक विचार व जीवनसाथी", p_marriage_inner, lang))

    # =========================================================================
    # PAGE 58: DEDICATED VEDIC PANCHANG PREDICTIONS & HOROSCOPE ESSENTIALS
    # (वैदिक पंचांग फलादेश, जन्म पत्रिका ज्ञान व राहु-केतु विश्लेषण)
    # =========================================================================
    p_panchang_inner = f"""
    <div class="prose-block">
      <div class="highlight-banner" style="font-size:12px; border-left:4px solid #B45309;">
        <strong>{T("Vedic Panchang Predictions &amp; Horoscope Foundations", "वैदिक पंचांग फलादेश, जन्म पत्रिका ज्ञान व राहु-केतु विश्लेषण")}</strong><br/>
        <span style="font-size:10px; color:#78350F;">{T("Ancient secrets of the Five Cosmic Pillars of Panchang, high-precision astronomical computation, and Rahu-Ketu karmic mastery.", "पंचांग के पांच दिव्य अंग, जन्म कुंडली का वास्तविक स्वरूप, आधुनिक खगोलीय गणित की प्रामाणिकता व राहु-केतु शांति सूत्र।")}</span>
      </div>

      <div class="two-col-grid mt-6">
        <div class="lk-card">
          <h4 style="color:#7C2D12; font-size:11.5px;">📜 {T("1. What is Janam Kundli? (जन्म कुंडली क्या है?)", "जन्म कुंडली क्या है? — दिव्य खगोलीय मानचित्र")}</h4>
          <p style="margin:0 0 4px 0; font-size:10.2px;">
            {T(
              "The word 'Horoscope' derives from ancient Greek 'Hora' (Hour/Time) and 'Scopos' (Observer). In Sanskrit Vedic Jyotish, 'Janam Kundali' is the celestial blueprint depicting the exact mathematical coordinates of the 12 Bhavas, 12 Rashis, 27 Nakshatras, and Navagrahas at the exact second and latitude/longitude of birth.",
              "अंग्रेजी शब्द 'Horoscope' संस्कृत 'होरा' (काल/समय) और 'स्कोपो' (दर्शक/मानचित्र) से बना है। वैदिक ज्योतिष में जन्म कुंडली जातक के जन्म के सटीक क्षण एवं अक्षांश-देशांतर पर आकाश मंडल में स्थित 12 भावों, 12 राशियों, 27 नक्षत्रों एवं नवग्रहों का प्रामाणिक खगोलीय एवं कर्मफल मानचित्र है।"
            )}
          </p>
          <p style="margin:0; font-size:10.2px;">
            {T(
              "It reveals past karmic tendencies (Prarabdha), biological constitution, character strengths, career avenues, and the unfolding timing of life events via Mahadashas.",
              "यह जातक के पूर्व संचित कर्मों (प्रारब्ध), शारीरिक संरचना, मानसिक क्षमताओं, आजीविका के अवसरों और जीवन की महत्वपूर्ण घटनाओं के समय का प्रामाणिक दिग्दर्शन कराती है।"
            )}
          </p>
        </div>

        <div class="lk-card">
          <h4 style="color:#991B1B; font-size:11.5px;">🪐 {T("2. Precision Algorithm vs Manual Panchang (सटीक खगोलीय गणित)", "सटीक खगोलीय गणना बनाम पारंपरिक पंचांग")}</h4>
          <p style="margin:0 0 4px 0; font-size:10.2px;">
            {T(
              "Traditional manual panchang calculations frequently suffer from human observational errors, imprecise sunrise timings, and uncalibrated ayanamsa variations.",
              "पारंपरिक हस्तलिखित पंचांगों में कई बार स्थानीय समय सुधार (LMT), देशांतर अंतर तथा सूर्योदय के सूक्ष्म अंतर के कारण लग्न व भाव संधि में त्रुटि की संभावना रहती है।"
            )}
          </p>
          <p style="margin:0; font-size:10.2px;">
            {T(
              "Shivansh Astro-Vastu computes planetary positions using high-precision astronomical algorithms (Swiss Ephemeris / Lahiri Chitrapaksha Ayanamsa) down to fractions of an arc-second. This eliminates all manual calculation defects, guaranteeing 100% authentic, tamper-proof ephemeris charts.",
              "शिवांश ॲस्ट्रो-वास्तू (Shivansh Astro-Vastu) आधुनिक खगोलीय गणित व प्रामाणिक लाहिड़ी अयनांश के आधार पर सेकंड के सूक्ष्म भाग तक ग्रह स्थितियों की गणना करता है, जिससे मानवीय गणना की सभी त्रुटियां समाप्त हो जाती हैं और शत-प्रतिशत प्रामाणिक चक्र निर्मित होते हैं।"
            )}
          </p>
        </div>
      </div>

      <div class="box-heading mt-6">{T("Your Five Panchang Pillars & Astrological Significations (आपके पंचांग के पंचतत्व एवं फलादेश)", "आपके पंचांग के पंचतत्व एवं विशेष फलादेश")}</div>
      <table class="data-table compact">
        <thead>
          <tr>
            <th style="width:16%;">{T("Pillar", "पंचांग अंग")}</th>
            <th style="width:22%;">{T("Your Birth Factor", "आपका जन्म मान")}</th>
            <th style="width:22%;">{T("Governing Domain", "कारकात्व व प्रभाव")}</th>
            <th>{T("Astrological Prediction & Impact on Destiny", "ज्योतिषीय फलादेश व जीवन प्रभाव")}</th>
          </tr>
        </thead>
        <tbody>
          <tr>
            <td><b>1. {T("Vaar (Weekday)", "वार (दिन)")}</b></td>
            <td><strong>{L(meta['day_en'], meta['day_hi'])}</strong></td>
            <td>{T("Physical Vitality & Drive", "शारीरिक बल, ऊर्जा व आरोग्यता")}</td>
            <td>{T("Governs your active physical stamina, willpower, and immune recovery rate.", "जातक के शारीरिक स्वास्थ्य, सक्रियता, पुरुषार्थ और रोगों से लड़ने की प्रतिरोधक क्षमता का निर्धारण करता है।")}</td>
          </tr>
          <tr>
            <td><b>2. {T("Tithi (Lunar Day)", "तिथि")}</b></td>
            <td><strong>{L(meta['tithi_en'], meta['tithi_hi'])}</strong></td>
            <td>{T("Emotional Core & Wealth", "मानसिक सुख, भाव व लक्ष्मी कृपा")}</td>
            <td>{T("Dictates inner contentment, psychological stability, and relationship with material wealth.", "जातक की मानसिक शांति, पारिवारिक सुख, आंतरिक संतोष और धन संचय की स्वाभाविक प्रवृत्ति को दर्शाता है।")}</td>
          </tr>
          <tr>
            <td><b>3. {T("Nakshatra", "नक्षत्र")}</b></td>
            <td><strong>{L(meta['nakshatra_pada_en'], meta['nakshatra_pada_hi'])}</strong></td>
            <td>{T("Karmic Instincts & Skills", "प्रारब्ध संस्कार, प्रतिभा व स्वभाव")}</td>
            <td>{T("The foundational cosmic imprint shaping your innate talents, mindset, and lifetime dasha sequence.", "जातक की अंतर्निहित प्रतिभा, सोचने के तरीके और जीवन में महादशाओं के आरंभिक क्रम का आधार है।")}</td>
          </tr>
          <tr>
            <td><b>4. {T("Yoga (Nithya)", "नित्य योग")}</b></td>
            <td><strong>{L(meta['yoga_en'], meta['yoga_hi'])}</strong></td>
            <td>{T("Virtue, Character & Dik-Bala", "चरित्र शुद्धि, सामाजिक प्रतिष्ठा व यश")}</td>
            <td>{T("Fosters noble virtues, righteousness, ethical reputation, and social goodwill.", "जातक के आचरण, नैतिक मूल्यों, समाज में मान-सम्मान और धर्मपरायणता को दिशा प्रदान करता है।")}</td>
          </tr>
          <tr>
            <td><b>5. {T("Karana", "करण (आधा तिथि)")}</b></td>
            <td><strong>{L(meta.get('karana_en', ''), meta.get('karana_hi', ''))}</strong></td>
            <td>{T("Work Stamina & Execution", "कार्यकुशलता, व्यापार व सफलता")}</td>
            <td>{T("Determines professional tenacity, practical execution skills, and tangible career achievements.", "जातक की कार्यकुशलता, व्यावसायिक क्षमता और किसी भी योजना को पूर्ण सफलता तक पहुंचाने की शक्ति तय करता है।")}</td>
          </tr>
        </tbody>
      </table>

      <div class="yoga-card mt-6" style="border:1.2px solid #D97706; background:rgba(254, 243, 199, 0.7); padding:8px 12px;">
        <h4 style="color:#7C2D12; font-size:11px; margin:0 0 3px 0;">🐍 {T("Rahu and Ketu Karmic Nodes Mastery (राहु-केतु कर्म चक्र एवं विशेष शांति सूत्र):", "राहु-केतु कर्म चक्र एवं विशेष शांति सूत्र:")}</h4>
        <p style="margin:0; font-size:10.2px; line-height:1.5;">
          {T(
            "Rahu represents material ambitions, unconventional intelligence, and futuristic expansion, while Ketu signifies past-life mastery, detachment, intuition, and spiritual liberation. To maintain auspicious harmony: keep the residence roof and toilets immaculate, never hoard unserviceable electronic items, respect maternal and paternal grandparents, and feed dogs and birds regularly.",
            "राहु सांसारिक महत्वाकांक्षा, तकनीकी सोच व आकस्मिक उन्नति का प्रतीक है; जबकि केतु पूर्वजन्म के संचित ज्ञान, वैराग्य, मोक्ष व अंतर्ज्ञान का कारक है। राहु-केतु को शुभ रखने हेतु घर की छत व शौचालय अत्यंत स्वच्छ रखें, बंद घड़ियां या कबाड़ न रखें, ननिहाल व ससुराल पक्ष का सम्मान करें तथा नियमित रूप से पक्षियों व श्वानों को भोजन दें।"
          )}
        </p>
      </div>
    </div>
    """
    pages.append(_page_wrapper(58, meta, brand, "Vedic Panchang Predictions & Planetary Fundamentals", "वैदिक पंचांग फलादेश, जन्म पत्रिका ज्ञान व राहु-केतु विश्लेषण", p_panchang_inner, lang))

    # =========================================================================
    # PAGE 59: SPECIAL GURUKULAM TEACHER — EASILY UNDERSTAND YOUR KUNDLI & DOSHA DECODER
    # (कुंडली सरल मार्गदर्शन — क्या दोष हैं, जीवन कैसे बीतेगा, लाल किताब जीवन सूत्र)
    # =========================================================================
    kalsarpa_status = L(kals.get("result_en", "No Kalsarpa Dosha"), kals.get("result_hi", "कालसर्प दोष नाही"))
    
    # Check Sade Sati for Year 2026
    sadesati_phase = T("Peaceful Phase (वर्तमान में कोई तीव्र साढ़े साती नहीं)", "वर्तमान में कोई तीव्र साढ़े साती नहीं है")
    if isinstance(sade, list):
        for s_row in sade:
            if "2026" in str(s_row.get("start_date_en", "")) or "2026" in str(s_row.get("end_date_en", "")):
                p_hi = s_row.get("phase_hi", "प्रभावित")
                p_en = s_row.get("phase_en", "Active Phase")
                sadesati_phase = L(p_en, p_hi)
                break

    p56_inner = f"""
    <div class="prose-block">
      <div class="highlight-banner" style="font-size:12.5px; border-left:4px solid #B45309;">
        <strong>{T("Special Shivansh Master Guide: Understand Your Life & Kundli In Simple Words", "विशेष गुरुकुलम् मार्गदर्शिका: अपनी कुंडली को आसान भाषा में समझें")}</strong><br/>
        <span style="font-size:10px; color:#78350F;">{T("A practical, easy-to-understand breakdown of major doshas, life roadmap, and real Lal Kitab wisdom for daily living.", "कुंडली में कौन-से मुख्य दोष हैं, जीवन का भविष्य कैसा रहेगा और लाल किताब अनुसार क्या करना चाहिए।")}</span>
      </div>

      <div class="two-col-grid mt-6">
        <div class="lk-card">
          <h4 style="color:#991B1B; font-size:11.8px;">1. {T("Major Doshas Analysis (मुख्य दोषों की सरल स्थिति)", "कुंडली के मुख्य दोषों की सरल स्थिति")}</h4>
          <p style="margin:4px 0;"><strong>• {T("Manglik Dosha:", "मांगलिक स्थिति:")}</strong> {manglik_status}<br/>
          <small style="color:#57534E;">{T("Determines temperamental compatibility in marriage and partnerships.", "वैवाहिक जीवन व साझेदारी में सामंजस्य का निर्धारण करता है।")}</small></p>
          
          <p style="margin:4px 0;"><strong>• {T("Kalsarpa Influence:", "कालसर्प योग:")}</strong> {kalsarpa_status}<br/>
          <small style="color:#57534E;">{T("Signifies karmic turning points and initial struggle before rapid mid-life rise.", "आरंभिक संघर्ष के बाद 36वें वर्ष से स्थायी उत्थान का संकेत देता है।")}</small></p>

          <p style="margin:4px 0;"><strong>• {T("Shani Sade Sati Status:", "शनि साढ़ेसाती / ढैया:")}</strong> {sadesati_phase}<br/>
          <small style="color:#57534E;">{T("Disciplines patience, hard work, and rewards sustained ethical efforts.", "धैर्य, कठोर परिश्रम और न्यायप्रिय आचरण का शुभ फल प्रदान करता है।")}</small></p>
        </div>

        <div class="lk-card">
          <h4 style="color:#7C2D12; font-size:11.8px;">2. {T("How Your Life Will Progress (जीवन की दिशा व भविष्य)", "जीवन की दिशा एवं भविष्य कैसा रहेगा?")}</h4>
          <p>{P(
            f"Your birth lagna is <strong>{meta['lagna_en']}</strong> and Moon sign is <strong>{meta['rasi_en']}</strong> ({meta['nakshatra_pada_en']}). This configuration creates an ambitious, self-made personality. The first phase of life demands foundation building; mid-life brings career authority and public respect; the mature phase brings spiritual stability and solid assets.",
            f"आपका जन्म लग्न <strong>{meta['lagna_hi']}</strong> तथा जन्म राशि <strong>{meta['rasi_hi']}</strong> ({meta['nakshatra_pada_hi']}) है। यह योग स्वाभिमानी, पुरुषार्थी और स्व-निर्मित व्यक्तित्व का निर्माण करता है। जीवन का प्रथम पड़ाव परिश्रम व आधार निर्माण का होता है; मध्य आयु में पद-प्रतिष्ठा व अधिकार प्राप्त होते हैं; और परिपक्व अवस्था में स्थायी संपत्ति व मानसिक संतोष प्राप्त होता है।"
          )}</p>
        </div>
      </div>

      <div class="box-heading mt-6">{T("Authentic Lal Kitab 5 Life Secrets (लाल किताब के 5 गुप्त जीवन सूत्र)", "लाल किताब के 5 गुप्त जीवन सूत्र — जीवन कैसे सफल होगा?")}</div>
      <table class="data-table compact">
        <thead><tr><th style="width:25%;">{T("Lal Kitab Principle", "लाल किताब सूत्र")}</th><th>{T("Practical Meaning & Effect", "सरल अर्थ एवं प्रभाव")}</th><th style="width:30%;">{T("Actionable Direction", "जीवन में क्या करें")}</th></tr></thead>
        <tbody>
          <tr>
            <td><b>1. {T("Nek vs Mandi Halat", "नेक बनाम मंदी हालत")}</b></td>
            <td>{T("Planets act benefic (Nek) when pure conduct is kept; foul language turns even Jupiter/Venus malefic (Mandi).", "जातक का आचरण शुद्ध रहे तो ग्रह नेक फल देते हैं; मिथ्या भाषण या कटुता से शुभ ग्रह भी मंदी हालत में चले जाते हैं।")}</td>
            <td>{T("Maintain clean tongue, respect elders, avoid debt on Tuesday/Saturday.", "वाणी में मधुरता रखें, बुजुर्गों का आदर करें, मंगलवार/शनिवार को कर्ज न लें।")}</td>
          </tr>
          <tr>
            <td><b>2. {T("Dharmi Teva Rule", "धर्मी तेवा का नियम")}</b></td>
            <td>{T("When Jupiter or Saturn bless Kendra/Trikona, the native is protected from catastrophic downfalls.", "जब बृहस्पति या शनि की कृपा दृष्टि शुभ भावों पर हो, तो अदृश्य दैवीय शक्ति संकटों से बचाती है।")}</td>
            <td>{T("Visit religious places unconditionally; donate yellow items or saffron mark on forehead.", "बिना शर्त धार्मिक स्थलों पर माथा टेकें, मस्तक पर केसर/हल्दी का तिलक लगाएं।")}</td>
          </tr>
          <tr>
            <td><b>3. {T("Pitri Rin (Ancestral Debt)", "पितृ ऋण से मुक्ति")}</b></td>
            <td>{T("Obstacles in progeny or recurring property disputes occur when family ancestors are neglected.", "वंश वृद्धि में विलंब या पैतृक संपत्ति में अड़चनें पूर्वजों के प्रति अनदेखी से उत्पन्न होती हैं।")}</td>
            <td>{T("Feed birds, provide water to trees (Peepal/Banyan), respect living father & paternal figures.", "पक्षियों को दाना डालें, पीपल में जल दें, जीवित पिता व बुजुर्गों का चरण स्पर्श करें।")}</td>
          </tr>
          <tr>
            <td><b>4. {T("Rahu & Ketu Management", "राहु-केतु नियंत्रण")}</b></td>
            <td>{T("Sudden mental anxiety, insomnia, or deceptive partnerships arise when Rahu is agitated in house.", "अचानक मानसिक तनाव, अनिद्रा अथवा धोखे का कारण घर में राहु की अशुद्धि (कबाड़/इलेक्ट्रॉनिक खराबी) है।")}</td>
            <td>{T("Keep terrace & toilets spotlessly clean; do not keep non-working electronic watches/clocks at home.", "छत और शौचालय अत्यंत स्वच्छ रखें; बंद घड़ियां व खराब इलेक्ट्रॉनिक सामान तुरंत हटाएं।")}</td>
          </tr>
          <tr>
            <td><b>5. {T("Bhavan & Money Flow", "धन प्रवाह एवं बरकत")}</b></td>
            <td>{T("Mercury-driven loose expenses or unnecessary lending drains liquidity and wealth accumulation.", "अकारण उधार देने अथवा कागजी लापरवाही से लक्ष्मी का अपव्यय होता है।")}</td>
            <td>{T("Keep solid silver square piece in pocket/vault; avoid free gifts or unauthorized guarantees.", "चांदी का चौकोर ठोस टुकड़ा तिजोरी/जेब में रखें; मुफ्त की वस्तुएं व अनाधिकृत जमानत से बचें।")}</td>
          </tr>
        </tbody>
      </table>
    </div>
    """
    pages.append(_page_wrapper(59, meta, brand, "Easily Understand Your Kundli — Lal Kitab Teacher", "कुंडली सरल मार्गदर्शन — दोष, भविष्य एवं लाल किताब सूत्र", p56_inner, lang))

    # =========================================================================
    # PAGE 60: SHIVANSH ASTRO-VASTU — WHAT TO DO & WHAT NOT TO DO (KARMA CODE)
    # (वैदिक एवं लाल किताब जीवन आचरण संहिता — क्या अवश्य करें एवं क्या न करें)
    # =========================================================================
    p57_inner = f"""
    <div class="prose-block">
      <div class="intro-highlight" style="font-size:11px; margin-bottom:10px;">
        {T(
          "Shivansh Astro-Vastu presents the sacred behavioral and karmic roadmap derived from Maharishi Parashara and Lal Kitab Farman. Practicing noble karma mitigates malefic planetary vibrations, while violating karmic codes severely triggers Rahu, Ketu, and Saturn doshas.",
          "शिवांश ॲस्ट्रो-वास्तू (Shivansh Astro-Vastu) द्वारा प्रस्तुत महर्षि पराशर एवं लाल किताब पर आधारित आचरण संहिता। सात्विक कर्म एवं अनुशासित आचरण से अशुभ ग्रहों का दुष्प्रभाव शांत होता है, जबकि वर्जित कार्यों से शनि, राहु एवं केतु के तीव्र दोष उत्पन्न होते हैं।"
        )}
      </div>

      <div class="two-col-grid" style="gap:12px;">
        <div class="yoga-card" style="border:1.5px solid #16A34A; background:rgba(240, 253, 244, 0.9); padding:10px 14px;">
          <h4 style="color:#15803D; font-size:12.5px; border-bottom:1.5px solid #86EFAC; padding-bottom:4px; margin-bottom:8px;">
            ✅ {T("WHAT TO DO (जीवन में क्या अवश्य करें - शुभ आचरण)", "जीवन में क्या अवश्य करें (शुभ आचरण)")}
          </h4>
          <ul class="remedy-list" style="color:#14532D; font-size:10.2px; line-height:1.6;">
            <li><strong>{T("Daily Solar Arghya:", "दैनिक सूर्य अर्घ्य:")}</strong> {T("Offer fresh water to Lord Surya in a copper vessel with kumkum/saffron within 1 hour of sunrise.", "प्रातः सूर्योदय के 1 घंटे के भीतर तांबे के पात्र से कुमकुम/रोली मिश्रित जल भगवान सूर्य को अर्पित करें।")}</li>
            <li><strong>{T("Work & Investment:", "कार्यक्षेत्र एवं धन:")}</strong> {T("Maintain clean, transparent accounts. Consult trusted mentors before taking speculative financial leverage.", "वित्तीय लेन-देन में पूर्ण पारदर्शिता रखें; सट्टेबाजी अथवा जोखिम भरे ऋण से पूर्व गुरुजनों से परामर्श लें।")}</li>
            <li><strong>{T("Living Routine (Dincharya):", "स्वास्थ्य व दिनचर्या:")}</strong> {T("Wake up before sunrise, walk barefoot on dew-laden grass, and practice sattvic vegetarian eating habits.", "सूर्योदय पूर्व उठें, हरी घास पर नंगे पैर घूमें और सात्विक, ताजा व पौष्टिक आहार अपनाएं।")}</li>
            <li><strong>{T("Selfless Seva (Charity):", "गौ व श्वान सेवा:")}</strong> {T("Feed green fodder/jaggery to indigenous cows and bread/milk to stray dogs on Saturdays.", "प्रतिदिन गौमाता को प्रथम रोटी व हरा चारा दें तथा शनिवार को काले श्वान को भोजन कराएं।")}</li>
            <li><strong>{T("Mantra Armor (Kavach):", "मंत्र कवच:")}</strong> {T("Recite Gayatri Mantra, Mahamrityunjaya Mantra, or Hanuman Chalisa 11 times with devotional focus daily.", "प्रतिदिन 11 बार गायत्री मंत्र, महामृत्युंजय मंत्र अथवा हनुमान चालीसा का श्रद्धापूर्वक पाठ करें।")}</li>
            <li><strong>{T("Elders' Blessings:", "माता-पिता का आशीष:")}</strong> {T("Touch the feet of parents, elders, and teachers daily to attract Jupiter and Sun auspicious blessings.", "प्रतिदिन माता-पिता व गुरुजनों के चरण स्पर्श कर आशीर्वाद लें, इससे गुरु व सूर्य देव प्रसन्न होते हैं।")}</li>
          </ul>
        </div>

        <div class="yoga-card" style="border:1.5px solid #DC2626; background:rgba(254, 242, 242, 0.9); padding:10px 14px;">
          <h4 style="color:#991B1B; font-size:12.5px; border-bottom:1.5px solid #FCA5A5; padding-bottom:4px; margin-bottom:8px;">
            ❌ {T("WHAT NOT TO DO (किन कार्यों से बचें - सख्त वर्जनाएं)", "किन कार्यों से बचें (सख्त वर्जनाएं)")}
          </h4>
          <ul class="remedy-list" style="color:#7F1D1D; font-size:10.2px; line-height:1.6;">
            <li><strong>{T("Intoxicants & Gambling:", "नशा व सट्टेबाजी:")}</strong> {T("Never consume alcohol, non-vegetarian meat, or indulge in lottery, betting, or speculative gambling.", "शराब, मांसाहार, जुआ एवं सट्टेबाजी से पूर्णतः दूर रहें; यह शनि-राहु को अत्यंत क्रूर बनाता है।")}</li>
            <li><strong>{T("Clutter & Negative Vastu:", "घर में कबाड़ व बंद वस्तुएं:")}</strong> {T("Never accumulate non-working clocks, broken mirrors, rusted iron, or junk on your house roof.", "छत पर जंग लगा लोहा, कबाड़, बंद घड़ियां अथवा चटके हुए दर्पण कभी न रखें; यह राहु को बिगाड़ता है।")}</li>
            <li><strong>{T("Relations & Ethics:", "संबंध एवं नैतिक मर्यादा:")}</strong> {T("Never disrespect sisters, daughters, aunts, or domestic helpers. Never cheat commercial partners.", "बहन, बेटी, बुआ व श्रमिकों का कभी अनादर न करें; व्यापारिक साझीदारों के साथ कभी कपट न करें।")}</li>
            <li><strong>{T("Sunset Money Lending:", "सूर्यास्त पश्चात धन लेन-देन:")}</strong> {T("Do not lend hard cash or precious valuables after sunset, and never stand unauthorized guarantees.", "सूर्यास्त के बाद धन उधार न दें और अंधविश्वास में किसी की जमानत अथवा गारंटर न बनें।")}</li>
            <li><strong>{T("Unverified Occult Tantra:", "अंधविश्वास व गलत रत्न:")}</strong> {T("Never wear cracked, dull gemstones or perform unverified cemetery/tamasic tantric rituals.", "बिना जांचा हुआ या टूटा रत्न न पहनें और भ्रामक तांत्रिक क्रियाओं अथवा अंधविश्वास से बचें।")}</li>
            <li><strong>{T("Cruelty & False Guarantees:", "जीव हिंसा व झूठी गवाही:")}</strong> {T("Never hurt animals, commit perjury, or usurp ancestral or orphan properties.", "किसी निर्दोष जीव को न सताएं, झूठी गवाही न दें और कभी किसी का हक या संपत्ति न हड़पें।")}</li>
          </ul>
        </div>
      </div>

      <div class="highlight-banner" style="margin-top:12px; font-size:11.2px; line-height:1.55;">
        <strong>{T("Shivansh Astro-Vastu Principle:", "शिवांश ॲस्ट्रो-वास्तू कर्म सिद्धांत:")}</strong>
        {T(
          '"Yadrisham Kriyate Karma Tadrisham Bhujyate Phalam" — Planetary transits only deliver the harvest of your seeds. When noble conduct, righteous livelihood, and charity are practiced, even debilitated planets convert into protective shields.', 
          '"यादृशं क्रियते कर्म तादृशं भुज्यते फलम्" — ग्रह केवल आपके द्वारा बोए गए बीजों का फल प्रदान करते हैं। जब आचरण सात्विक, आजीविका धर्मसम्मत और सेवा निःस्वार्थ होती है, तो नीच ग्रह भी जीवन रक्षक कवच बन जाते हैं।', 
        )}
      </div>
    </div>
    """
    pages.append(_page_wrapper(60, meta, brand, "Karma Code — What To Do & What To Avoid", "जीवन आचरण संहिता — क्या अवश्य करें एवं क्या न करें", p57_inner, lang))

    # =========================================================================
    # ULTRA-VIP HIGH-TICKET REMEDIES & AUTHENTIC KP DOSSIER (PAGES 61-75+)
    # Trained from Prof. K. S. Krishnamurti (Reader III) & KP Cuspal Event Groupings
    # =========================================================================
    try:
        vip_remedy_pages = generate_vip_remedy_pages(data, T, P)
        for vrp in vip_remedy_pages:
            pages.append(_page_wrapper(
                len(pages) + 1, meta, brand,
                vrp["title_en"], vrp["title_hi"],
                vrp["html"], lang
            ))
    except Exception as e_rem:
        print("Warning: Could not append VIP remedy pages:", e_rem)

    # =========================================================================
    # PAGE 61: EXCLUSIVE DEDICATED MASTER LEGAL DISCLAIMER & COPYRIGHT STATEMENT
    # (सम्पूर्ण वैधानिक कानूनी उद्घोषणा, प्राचीन विद्या प्रकटीकरण एवं सर्वाधिकार सुरक्षित)
    # =========================================================================
    p58_inner = f"""
    <div class="prose-block" style="font-size:9.4px; line-height:1.52; color:#1E293B;">
      <div style="text-align:center; margin-bottom:8px; padding-bottom:6px; border-bottom:1.5px solid #D97706;">
        <div style="font-size:13.5px; font-weight:900; color:#7C2D12; letter-spacing:1px; font-family:'Cinzel', serif;">
          SHIVANSH ASTRO-VASTU — LEGAL PROTOCOL &amp; STATUTORY COPYRIGHT
        </div>
        <div style="font-size:11px; font-weight:700; color:#B45309; margin-top:2px;">
          ॥ वैधानिक कानूनी उद्घोषणा, प्राचीन विद्या प्रकटीकरण एवं सर्वाधिकार सुरक्षित ॥
        </div>
      </div>

      <div class="disclaimer-card" style="background:rgba(255, 255, 255, 0.95); border:1.2px solid #CBD5E1; padding:9px 13px; margin-bottom:8px;">
        <h4 style="color:#7C2D12; font-size:10.5px; margin:0 0 3px 0;">
          ⚖️ {T("1. Nature of Ancient Observational Science (प्राचीन विद्या प्रकटीकरण):", "1. प्राचीन विद्या का स्वरूप एवं गैर-निश्चयात्मक परामर्श:")}
        </h4>
        <p style="margin:0 0 4px 0;">
          {T(
            "This Brihat Janma Patrika and astrological report is formulated strictly in accordance with traditional tenets of ancient Indian Vedic Astrology (Brihat Parashara Hora Shastra, Jaimini Upadesha Sutras), Krishnamurti Paddhati (KP System), and Lal Kitab Samhita using modern high-precision astronomical ephemerides. Vedic Astrology is an ancient observational, philosophical, and traditional study of celestial alignments and karmic probabilities. It is NOT an empirical, physical, or exact laboratory science, nor does it claim infallible mathematical certainty.",
            "यह जन्म पत्रिका एवं भविष्य कथन विश्लेषण प्राचीन भारतीय वैदिक ज्योतिष (बृहत् पराशर होरा शास्त्र, जैमिनी सूत्र), कृष्णमूर्ति पद्धति (के.पी.) एवं लाल किताब के पारंपरिक सिद्धांतों व खगोलीय गणनाओं पर आधारित है। वैदिक ज्योतिष आकाशीय खगोलीय संकेतों एवं पूर्वजन्म के कर्मों की संभावनाओं पर आधारित एक प्राचीन दार्शनिक एवं पारंपरिक अध्ययन है। यह कोई प्रयोगशाला-सिद्ध भौतिक विज्ञान नहीं है और न ही यह किसी अचूक या अनिवार्य भविष्य का दावा करता है।"
          )}
        </p>
      </div>

      <div class="disclaimer-card" style="background:rgba(255, 255, 255, 0.95); border:1.2px solid #CBD5E1; padding:9px 13px; margin-bottom:8px;">
        <h4 style="color:#7C2D12; font-size:10.5px; margin:0 0 3px 0;">
          ⚡ {T("2. No Confirmation of Future Events & Primacy of Free Will (अनिश्चित भविष्य एवं मानवीय पुरुषार्थ):", "2. अनिश्चित भविष्य एवं मानवीय कर्म/पुरुषार्थ की प्रधानता:")}
        </h4>
        <p style="margin:0 0 4px 0;">
          {T(
            "No calculation, dasha timeline, yogic combination, or prediction in this report confirms or guarantees that any future event will unquestionably occur. Human life is governed by dynamic free will (Purushartha), moral actions (Kriyamana Karma), environmental conditions, and personal effort. Planetary horoscopes solely illustrate potential cosmic weather and energetic inclinations. The outcome of any venture, marriage, business, or health phase remains entirely dependent on individual choices, karmic effort, and divine will. No prediction can be treated as a confirmed outcome.",
            "इस प्रतिवेदन में दी गई कोई भी गणना, दशा चक्र अथवा भविष्यवाणी यह प्रमाणित या पुष्टि (Confirm) नहीं करती कि कोई घटना अनिवार्य रूप से घटित ही होगी। मानव जीवन व्यक्तिगत पुरुषार्थ, स्वतंत्र इच्छाशक्ति (Free Will), नैतिक कर्म, सामाजिक परिवेश एवं मानवीय निर्णयों द्वारा संचालित होता है। जन्म कुंडली केवल आकाशीय प्रवृत्तियों एवं संभावनाओं को दर्शाती है। किसी भी कार्य, विवाह, व्यवसाय अथवा स्वास्थ्य का अंतिम परिणाम जातक के व्यक्तिगत कर्मों एवं ईश्वर की इच्छा पर निर्भर है।"
          )}
        </p>
      </div>

      <div class="disclaimer-card" style="background:rgba(255, 255, 255, 0.95); border:1.2px solid #CBD5E1; padding:9px 13px; margin-bottom:8px;">
        <h4 style="color:#7C2D12; font-size:10.5px; margin:0 0 3px 0;">
          🛡️ {T("3. Absolute Limitation of Liability & Zero Blame Clause (कानूनी देयता से पूर्ण मुक्ति एवं शून्य अभियोग):", "3. कानूनी देयता से पूर्ण मुक्ति एवं शून्य अभियोग की शर्त:")}
        </h4>
        <p style="margin:0 0 4px 0;">
          {T(
            "Under no circumstances shall Shivansh Astro-Vastu, its computational algorithm creators, developers, publishers, consulting astrologers, authors, or corporate distributors be blamed, held liable, or legally answerable for any direct, indirect, consequential, punitive, or financial losses, mental distress, domestic disputes, business failures, or personal consequences arising out of the interpretation, belief, or application of this document. Possession or reading of this report constitutes an absolute, irrevocable agreement to hold Shivansh Astro-Vastu completely harmless from all legal actions, police complaints, civil claims, or consumer litigations worldwide.",
            "किसी भी परिस्थिति में 'शिवांश ॲस्ट्रो-वास्तू (Shivansh Astro-Vastu)' (Shivansh Astro-Vastu), इसके सॉफ्टवेयर डेवलपर, प्रकाशक, परामर्शदाता ज्योतिषी अथवा संबंधित संस्थाओं को इस प्रतिवेदन में उल्लिखित किसी भी गणना, फलादेश अथवा उपाय के कारण उत्पन्न किसी भी आर्थिक हानि, मानसिक तनाव, पारिवारिक विवाद, व्यापारिक घाटे अथवा निर्णय के लिए उत्तरदायी या जिम्मेदार (Blame) नहीं ठहराया जा सकेगा। इस दस्तावेज को प्राप्त करना इस बात की बिना शर्त कानूनी सहमति है कि इसके आधार पर किसी भी न्यायालय, उपभोक्ता मंच या पुलिस प्राधिकरण में कोई दावा अथवा अभियोग स्वीकार्य नहीं होगा।"
          )}
        </p>
      </div>

      <div class="disclaimer-card" style="background:rgba(255, 255, 255, 0.95); border:1.2px solid #CBD5E1; padding:9px 13px; margin-bottom:8px;">
        <h4 style="color:#7C2D12; font-size:10.5px; margin:0 0 3px 0;">
          🩺 {T("4. Statutory Non-Substitute Notice & Remedy Discretion (चिकित्सा, कानूनी एवं वित्तीय गैर-विकल्प उद्घोषणा):", "4. चिकित्सा, विधिक एवं वित्तीय गैर-विकल्प सूचना तथा उपाय विवेक:")}
        </h4>
        <p style="margin:0 0 4px 0;">
          {T(
            "This report is strictly for cultural, advisory, and spiritual guidance. It is NEVER a substitute for licensed medical diagnosis or surgery, psychiatric evaluation, qualified legal advocacy, or certified financial investment planning. Consult registered doctors for medical ailments and certified attorneys for legal issues. Furthermore, all Lal Kitab totkas, remedies, fasts, donations, and gemstones mentioned herein are traditional cultural practices; adopting any remedy is entirely at the recipient's voluntary risk, discretion, and faith.",
            "यह प्रतिवेदन केवल आध्यात्मिक, सांस्कृतिक एवं परामर्श प्रयोजन हेतु है। यह किसी भी प्रकार से योग्य चिकित्सक, मनोरोग विशेषज्ञ, प्रमाणित अधिवक्ता अथवा पंजीकृत वित्तीय सलाहकार के पेशेवर परामर्श का विकल्प नहीं है। गंभीर स्वास्थ्य समस्याओं के लिए डॉक्टर तथा कानूनी विवादों के लिए वकील से संपर्क करना अनिवार्य है। इसके अतिरिक्त, इस प्रतिवेदन में दिए गए लाल किताब उपाय, दान, व्रत एवं रत्न पारंपरिक आस्था पर आधारित हैं; इनका पालन करना पूरी तरह से जातक के स्वैच्छिक विवेक, विश्वास एवं उत्तरदायित्व पर निर्भर है।"
          )}
        </p>
      </div>

      <div class="disclaimer-card" style="background:linear-gradient(135deg, rgba(254, 243, 199, 0.8) 0%, rgba(254, 249, 195, 0.7) 100%); border:1.5px solid #D97706; padding:9px 13px;">
        <h4 style="color:#7C2D12; font-size:10.5px; margin:0 0 3px 0;">
          ©️ {T("5. Proprietary Copyright & Jurisdiction Notice (कॉपीराइट, बौद्धिक संपदा एवं विधिक क्षेत्राधिकार):", "5. सर्वाधिकार सुरक्षित, कॉपीराइट एवं विधिक क्षेत्राधिकार:")}
        </h4>
        <p style="margin:0 0 4px 0;">
          {T(
            "© 2026 Shivansh Astro-Vastu. All Rights Reserved. The layout, astrological logic synthesis, report architecture, and algorithmic design of this publication are protected under the Indian Copyright Act 1957, International Berne Convention, and universal Intellectual Property Treaties. Unauthorized reproduction, digital copying, automated extraction, commercial syndication, reselling, or reverse engineering of this software or PDF report without prior written consent is strictly prohibited by law. Any dispute or arbitration shall be strictly and exclusively subject to the courts of local jurisdiction at the publisher's registered city.",
            "© 2026 शिवांश ॲस्ट्रो-वास्तू (Shivansh Astro-Vastu) (Shivansh Astro-Vastu) — सर्वाधिकार सुरक्षित। इस प्रतिवेदन का प्रारूप, ज्योतिषीय एल्गोरिदम, संरचना एवं विश्लेषणात्मक प्रस्तुति भारतीय कॉपीराइट अधिनियम 1957 एवं अंतरराष्ट्रीय बौद्धिक संपदा संधियों के तहत सुरक्षित है। प्रकाशक की पूर्व लिखित अनुमति के बिना इस दस्तावेज अथवा इसके अंशों की प्रतिलिपि बनाना, पुनः प्रकाशन, डिजिटल पुनर्विक्रय अथवा व्यावसायिक उपयोग विधि विरुद्ध है। किसी भी कानूनी विवाद की स्थिति में न्यायिक क्षेत्राधिकार केवल प्रकाशक के पंजीकृत स्थानीय न्यायालय तक सीमित रहेगा।"
          )}
        </p>
      </div>

      <div style="text-align:center; margin-top:8px; font-weight:800; color:#7C2D12; font-size:10.5px; letter-spacing:0.5px;">
        {T(
          "॥ Dharmo Rakshati Rakshitah — Righteous Karma Is The Supreme Shield & True Destiny ॥",
          "॥ धर्मो रक्षति रक्षितः — धर्म व सत्कर्म ही जीवन का सर्वोच्च कवच एवं परम भाग्य हैं ॥"
        )}
      </div>
      <div style="text-align:center; margin-top:2px; font-size:9px; color:#64748B;">
        Verified Authentic Astrological Document • Shivansh Astro-Vastu • 100% Offline Edition
      </div>
    </div>
    """
    pages.append(_page_wrapper(61, meta, brand, "Statutory Legal Disclaimer & Copyright Protocol", "वैधानिक कानूनी उद्घोषणा एवं सर्वाधिकार सुरक्षित", p58_inner, lang))


    # Assemble complete HTML with Modern Royal Vedic Glassmorphism Theme
    css = """
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700;900&family=Plus+Jakarta+Sans:wght@400;500;600;700&family=Noto+Sans+Devanagari:wght@400;500;600;700;800&family=Rasa:wght@500;600;700&display=swap');

    @page {
      size: A4 portrait;
      margin: 6mm;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      padding: 0;
      background: radial-gradient(circle at 10% 20%, #F5EFEB 0%, #E8DFD8 90%);
      color: #1F1B16;
      font-family: 'Plus Jakarta Sans', 'Noto Sans Devanagari', 'Rasa', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Mangal', 'Kokila', sans-serif;
      font-size: 10.6px;
      line-height: 1.48;
      -webkit-font-smoothing: antialiased;
    }
    .kundli-page {
      width: 198mm;
      min-height: 284mm;
      max-height: 284mm;
      margin: 12px auto;
      background: rgba(255, 253, 249, 0.88);
      backdrop-filter: blur(16px);
      -webkit-backdrop-filter: blur(16px);
      border: 1.5px solid rgba(194, 65, 12, 0.28);
      border-radius: 14px;
      box-shadow: 
        0 12px 34px -8px rgba(124, 45, 18, 0.12),
        0 4px 16px -2px rgba(180, 83, 9, 0.08),
        inset 0 0 0 1px rgba(255, 255, 255, 0.7);
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      padding: 12px 16px;
      page-break-after: always;
      break-after: page;
      overflow: hidden;
      position: relative;
    }
    @media print {
      body { background: #FFFFFF; }
      .kundli-page {
        margin: 0 auto;
        box-shadow: none;
        border-radius: 0;
        border: 1px solid #7C2D12;
        background: #FFFFFF;
        height: 284mm;
      }
      .no-print { display: none !important; }
    }
    @media screen and (max-width: 800px) {
      body {
        padding: 4px 2px !important;
        background: #F5EFEB !important;
        overflow-x: hidden !important;
      }
      .kundli-page {
        width: 100% !important;
        max-width: 100% !important;
        min-height: auto !important;
        max-height: none !important;
        margin: 8px 0 !important;
        padding: 8px 6px !important;
        box-sizing: border-box !important;
        border-radius: 10px !important;
        overflow: hidden !important;
        word-wrap: break-word !important;
      }
      .kundli-page * {
        box-sizing: border-box !important;
        max-width: 100% !important;
      }
      .cover-brand-title {
        font-size: 20px !important;
        letter-spacing: 2px !important;
        line-height: 1.2 !important;
      }
      .cover-brand-hindi {
        font-size: 15px !important;
      }
      .cover-border-outer, .cover-border-inner {
        padding: 6px !important;
        height: auto !important;
      }
      .cover-client-card {
        padding: 8px !important;
        margin: 8px 0 !important;
      }
      .cover-emblem svg {
        max-width: 200px !important;
        height: auto !important;
      }
      svg {
        max-width: 100% !important;
        height: auto !important;
      }
      table {
        width: 100% !important;
        max-width: 100% !important;
        display: block !important;
        overflow-x: auto !important;
        -webkit-overflow-scrolling: touch !important;
      }
      [style*="display:grid"], [style*="display: grid"] {
        display: flex !important;
        flex-direction: column !important;
        gap: 10px !important;
        max-width: 100% !important;
      }
    }
    .page-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      background: rgba(254, 243, 199, 0.55);
      border: 1px solid rgba(217, 119, 6, 0.25);
      border-radius: 8px;
      padding: 4px 12px;
      margin-bottom: 7px;
      color: #7C2D12;
      font-size: 11.5px;
      font-weight: 700;
      box-shadow: 0 2px 6px rgba(180, 83, 9, 0.04);
    }
    .header-name {
      display: flex;
      align-items: center;
      gap: 6px;
      letter-spacing: 0.3px;
    }
    .header-brand {
      color: #9A3412;
      font-size: 11px;
      font-family: 'Cinzel', serif;
      letter-spacing: 0.5px;
    }
    .page-body { flex: 1; overflow: hidden; }
    .page-footer {
      border-top: 1px solid rgba(217, 119, 6, 0.25);
      background: rgba(255, 251, 235, 0.65);
      border-radius: 6px;
      padding: 3px 10px;
      margin-top: 6px;
      display: flex;
      justify-content: space-between;
      font-size: 9px;
      color: #78716C;
    }
    .section-title {
      text-align: center;
      font-size: 14.5px;
      font-weight: 800;
      color: #7C2D12;
      background: linear-gradient(135deg, rgba(254, 243, 199, 0.95) 0%, rgba(253, 230, 138, 0.75) 50%, rgba(254, 243, 199, 0.95) 100%);
      border: 1px solid rgba(217, 119, 6, 0.35);
      padding: 5px 14px;
      margin-bottom: 8px;
      border-radius: 8px;
      letter-spacing: 0.5px;
      box-shadow: 0 4px 12px rgba(180, 83, 9, 0.06);
    }
    .box-heading {
      font-size: 11.2px;
      font-weight: 700;
      color: #7C2D12;
      background: rgba(254, 243, 199, 0.7);
      border-left: 3.5px solid #C2410C;
      border-radius: 0 6px 6px 0;
      padding: 3px 8px;
      margin-bottom: 5px;
      letter-spacing: 0.2px;
    }
    .box-heading.center { text-align: center; border-left: none; border-bottom: 1.5px solid #D97706; border-radius: 6px; }
    .two-col-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; align-items: start; }
    .three-col-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 6px; }
    .four-col-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 6px; }
    .five-col-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 4px; }
    .six-col-grid { display: grid; grid-template-columns: repeat(6, 1fr); gap: 4px; }
    
    /* Modern Glassmorphic Data Tables */
    .data-table {
      width: 100%;
      border-collapse: separate;
      border-spacing: 0;
      background: rgba(255, 255, 255, 0.75);
      backdrop-filter: blur(8px);
      border: 1px solid rgba(217, 119, 6, 0.22);
      border-radius: 8px;
      overflow: hidden;
      box-shadow: 0 3px 10px rgba(120, 113, 108, 0.05);
    }
    .data-table th, .data-table td {
      border-bottom: 1px solid rgba(231, 229, 228, 0.85);
      border-right: 1px solid rgba(231, 229, 228, 0.85);
      padding: 3.2px 6px;
      text-align: left;
    }
    .data-table th:last-child, .data-table td:last-child {
      border-right: none;
    }
    .data-table tr:last-child td {
      border-bottom: none;
    }
    .data-table th {
      background: linear-gradient(135deg, #7C2D12 0%, #9A3412 100%);
      color: #FFFBEB;
      font-weight: 700;
      font-size: 9.8px;
      letter-spacing: 0.3px;
      text-shadow: 0 1px 2px rgba(0,0,0,0.25);
    }
    .data-table.compact td { padding: 2.4px 5px; font-size: 9.8px; }
    .data-table.ultra-compact th, .data-table.ultra-compact td { padding: 1.8px 3px; font-size: 8.8px; }
    .data-table tr:nth-child(even) td { background: rgba(254, 243, 199, 0.22); }
    .data-table tr.tot-row td { background: rgba(253, 230, 138, 0.65); font-weight: 800; color: #7C2D12; }
    .red-cell { color: #DC2626; font-weight: bold; }
    .tiny-cell { font-size: 7.5px !important; line-height: 1.1; }
    .c { text-align: center !important; }
    .mt-4 { margin-top: 4px; }
    .mt-6 { margin-top: 6px; }
    .mt-8 { margin-top: 8px; }
    .mt-10 { margin-top: 10px; }
    .mt-12 { margin-top: 12px; }
    .mt-14 { margin-top: 14px; }
    .mt-16 { margin-top: 16px; }
    .mb-10 { margin-bottom: 10px; }

    .top-summary-strip {
      width: 100%;
      border-collapse: separate;
      border-spacing: 0;
      background: rgba(255, 251, 235, 0.85);
      border: 1px solid rgba(217, 119, 6, 0.35);
      border-radius: 8px;
      overflow: hidden;
      font-size: 9.6px;
      box-shadow: 0 3px 8px rgba(180, 83, 9, 0.05);
    }
    .top-summary-strip td { padding: 3px 7px; border-bottom: 1px solid rgba(231, 229, 228, 0.7); border-right: 1px solid rgba(231, 229, 228, 0.7); }
    .chart-col { text-align: center; }
    .chart-title {
      font-weight: 700;
      color: #7C2D12;
      font-size: 11.2px;
      margin-bottom: 4px;
      letter-spacing: 0.2px;
    }
    .mini-dasha-box {
      border: 1px solid rgba(217, 119, 6, 0.28);
      background: rgba(255, 255, 255, 0.82);
      border-radius: 6px;
      overflow: hidden;
      font-size: 8.3px;
      box-shadow: 0 2px 5px rgba(0,0,0,0.03);
    }
    .mini-dasha-head {
      background: linear-gradient(135deg, rgba(254, 243, 199, 0.9) 0%, rgba(253, 230, 138, 0.7) 100%);
      color: #7C2D12;
      font-weight: 700;
      text-align: center;
      padding: 2.5px;
      border-bottom: 1px solid rgba(217, 119, 6, 0.25);
      font-size: 8.2px;
      line-height: 1.15;
    }
    .mini-dasha-head span { font-weight: normal; font-size: 7.5px; color: #44403C; }
    .mini-table { width: 100%; border-collapse: collapse; }
    .mini-table td { border-bottom: 1px solid rgba(231, 229, 228, 0.6); padding: 1.2px 3.5px; font-size: 7.9px; }
    .mini-table tr.sub-hd td { background: rgba(254, 243, 199, 0.4); font-weight: 700; }

    /* Modern Luxury Vedic Glass Cover Page */
    .cover-page {
      background: 
        radial-gradient(circle at 50% 15%, rgba(254, 240, 138, 0.6) 0%, rgba(255, 251, 235, 0.3) 50%, transparent 80%),
        radial-gradient(circle at 80% 85%, rgba(251, 146, 60, 0.25) 0%, transparent 60%),
        radial-gradient(circle at 15% 75%, rgba(217, 119, 6, 0.2) 0%, transparent 60%),
        linear-gradient(135deg, #FFFDF9 0%, #FEF9EE 100%);
      padding: 12px;
      border: 1.5px solid rgba(217, 119, 6, 0.35);
      border-radius: 16px;
      box-shadow: 0 16px 40px -10px rgba(124, 45, 18, 0.15);
    }
    .cover-border-outer {
      border: 2px solid rgba(194, 65, 12, 0.4);
      border-radius: 12px;
      height: 100%;
      padding: 6px;
      background: rgba(255, 255, 255, 0.3);
      backdrop-filter: blur(10px);
    }
    .cover-border-inner {
      border: 1px dashed rgba(217, 119, 6, 0.5);
      border-radius: 10px;
      height: 100%;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: space-between;
      padding: 16px 20px;
      text-align: center;
    }
    .cover-shloka { 
      font-size: 14.5px; 
      font-weight: 800; 
      color: #991B1B; 
      letter-spacing: 1px;
      text-shadow: 0 1px 3px rgba(153, 27, 27, 0.15);
    }
    .cover-sanskrit-verse { 
      font-size: 11px; 
      color: #7C2D12; 
      font-style: italic; 
      line-height: 1.55; 
      max-width: 90%;
    }
    .cover-brand-title {
      font-family: 'Cinzel', serif;
      font-size: 44px;
      font-weight: 900;
      letter-spacing: 8px;
      color: #7C2D12;
      text-shadow: 0 2px 4px rgba(124, 45, 18, 0.2), 0 0 20px rgba(245, 158, 11, 0.3);
      margin-top: 2px;
    }
    .cover-brand-hindi { 
      font-size: 17.5px; 
      font-weight: 800; 
      color: #B45309; 
      margin-top: -6px; 
      letter-spacing: 0.5px;
    }
    .cover-tagline {
      background: linear-gradient(135deg, #7C2D12 0%, #9A3412 100%);
      color: #FEF08A;
      padding: 5px 22px;
      border-radius: 30px;
      font-size: 10.5px;
      font-weight: 700;
      letter-spacing: 0.8px;
      box-shadow: 0 4px 14px rgba(124, 45, 18, 0.25);
    }
    .cover-client-card {
      width: 94%;
      background: rgba(255, 255, 255, 0.82);
      backdrop-filter: blur(14px);
      -webkit-backdrop-filter: blur(14px);
      border: 1.5px solid rgba(217, 119, 6, 0.35);
      border-radius: 12px;
      overflow: hidden;
      box-shadow: 0 8px 24px -4px rgba(124, 45, 18, 0.12), inset 0 0 0 1px rgba(255,255,255,0.8);
    }
    .cover-client-header {
      background: linear-gradient(135deg, #7C2D12 0%, #9A3412 100%);
      color: #FEF3C7;
      font-weight: 800;
      padding: 6px;
      font-size: 13px;
      letter-spacing: 1.2px;
      text-shadow: 0 1px 2px rgba(0,0,0,0.3);
    }
    .cover-table { width: 100%; border-collapse: collapse; }
    .cover-table td { border-bottom: 1px solid rgba(231, 229, 228, 0.7); border-right: 1px solid rgba(231, 229, 228, 0.7); padding: 5px 9px; text-align: left; font-size: 10.8px; }
    .cover-table td.lbl { background: rgba(254, 243, 199, 0.45); color: #7C2D12; font-weight: 700; width: 22%; }
    .cover-table td.val { width: 28%; color: #1C1917; font-weight: 500; }
    .cover-footer-stamp { 
      font-size: 10.5px; 
      color: #7C2D12; 
      font-weight: 700; 
      background: rgba(254, 243, 199, 0.6); 
      padding: 4px 16px; 
      border-radius: 20px; 
      border: 1px solid rgba(217, 119, 6, 0.3);
    }

    /* Enhanced Luxury Glass Prose & Prediction Badges */
    .prose-block { font-size: 11px; line-height: 1.58; text-align: justify; }
    .prose-block h3 {
      color: #7C2D12;
      border-bottom: 2px solid rgba(217, 119, 6, 0.45);
      padding-bottom: 3px;
      margin: 11px 0 6px 0;
      font-size: 13px;
      font-weight: 800;
      letter-spacing: 0.3px;
      display: flex;
      align-items: center;
      gap: 6px;
    }
    .prose-block h3::before {
      content: "✦";
      color: #D97706;
      font-size: 12px;
    }
    .prose-block h4 {
      color: #7C2D12;
      margin: 9px 0 4px 0;
      font-size: 11.8px;
      font-weight: 700;
    }
    .prose-block h4 span { color: #B45309; font-size: 10.8px; font-weight: normal; }
    .prose-block p { margin: 0 0 8px 0; }
    .highlight-banner {
      background: linear-gradient(135deg, rgba(254, 243, 199, 0.85) 0%, rgba(253, 230, 138, 0.6) 100%);
      backdrop-filter: blur(10px);
      border: 1px solid rgba(217, 119, 6, 0.35);
      border-left: 4.5px solid #7C2D12;
      border-radius: 0 10px 10px 0;
      padding: 7px 14px;
      margin: 8px 0;
      font-size: 12px;
      color: #7C2D12;
      box-shadow: 0 3px 10px rgba(180, 83, 9, 0.08);
    }
    .intro-highlight {
      background: rgba(255, 251, 235, 0.85);
      border-left: 3.5px solid #D97706;
      border-radius: 0 8px 8px 0;
      padding: 5px 10px;
      font-weight: 600;
      color: #44403C;
      margin-bottom: 6px;
    }
    .lk-card {
      background: rgba(255, 255, 255, 0.9);
      backdrop-filter: blur(10px);
      border: 1px solid rgba(217, 119, 6, 0.25);
      border-left: 4.5px solid #991B1B;
      padding: 8px 13px;
      margin-bottom: 9px;
      border-radius: 0 10px 10px 0;
      box-shadow: 0 4px 12px rgba(124, 45, 18, 0.06);
    }
    .lk-body { font-size: 10.8px; line-height: 1.55; }
    .lk-remedies {
      margin-top: 7px;
      background: linear-gradient(135deg, rgba(254, 243, 199, 0.85) 0%, rgba(254, 249, 195, 0.9) 100%);
      border: 1px solid rgba(217, 119, 6, 0.3);
      padding: 7px 12px;
      border-radius: 8px;
      font-size: 10.6px;
      color: #7C2D12;
      box-shadow: inset 0 1px 3px rgba(217, 119, 6, 0.1);
    }
    .yoga-card {
      background: rgba(255, 251, 235, 0.9);
      backdrop-filter: blur(10px);
      border: 1px solid rgba(245, 158, 11, 0.4);
      border-radius: 9px;
      padding: 7px 12px;
      margin-bottom: 7px;
      box-shadow: 0 3px 8px rgba(245, 158, 11, 0.08);
    }
    .yoga-card h4 { margin: 0 0 3px 0; color: #991B1B; font-size: 11.5px; font-weight: 700; }
    .yoga-card p { margin: 0; font-size: 10.3px; }
    .note-box, .disclaimer-card {
      background: rgba(254, 243, 199, 0.85);
      backdrop-filter: blur(10px);
      border: 1px solid rgba(217, 119, 6, 0.4);
      padding: 9px 14px;
      border-radius: 10px;
      font-size: 9.8px;
      margin-top: 8px;
      box-shadow: 0 3px 10px rgba(180, 83, 9, 0.07);
    }
    .remedy-list { margin: 5px 0 9px 18px; padding: 0; }
    .remedy-list li { margin-bottom: 4px; line-height: 1.48; }
    .para-en { margin-bottom: 4px; }
    .para-hi { color: #7C2D12; font-size: 10.5px; background: rgba(255, 251, 235, 0.8); padding: 4px 8px; border-left: 2.5px solid #D97706; border-radius: 0 6px 6px 0; margin-top: 3px; }
    .hi-sub { color: #9A3412; font-size: 0.92em; font-weight: 600; }
    """

    # Modular report package filtering
    if package == "laghu":
        # 4 Core Pages: Cover, Avkahada & Favourable, Lagna/Navamsha/Dasha overview, Planetary Positions & Chalit
        pages = pages[:4]
    elif package == "varshaphal":
        # 10 Selected Pages: Core charts + Varshaphal Annual Predictions + Lal Kitab
        varsha_pages = [p for p in pages[4:] if "varshaphal" in p.lower() or "lal kitab" in p.lower() or "transit" in p.lower()]
        pages = [pages[0], pages[1], pages[2], pages[3]] + varsha_pages[:6]
    elif package == "kp_remedies":
        # Focused 7-Page Dossier: Cover + Table of Contents + Dedicated 5 Authentic KP Remedial Pages
        kp_rems = [p for p in pages if ("4-fold" in p.lower() or "४-स्तरीय" in p or "उपस्वामी घटना" in p or "zero-damage" in p.lower() or "रोग निदान" in p or "ऋण मुक्ती" in p or "significator" in p.lower())]
        pages = [pages[0], pages[1]] + [p for p in kp_rems if p != pages[0] and p != pages[1]][:5]

    # Number pages dynamically so no numbers are duplicated or skipped
    total_pages = len(pages)
    final_pages = []
    for idx, p in enumerate(pages, start=1):
        final_pages.append(
            p.replace("__PAGE_NUM__", str(idx)).replace("__TOTAL_PAGES__", str(total_pages))
        )

    full_html = f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=3.0, user-scalable=yes"/>
  <title>Shivansh Astro-Vastu - {meta["name"]}</title>
  <style>{css}</style>
</head>
<body>
  {"".join(final_pages)}
</body>
</html>
"""
    if is_mr:
        full_html = to_marathi(full_html)
    return full_html


def export_html_to_pdf(html_content: str, output_pdf_path: str, split_single_pages: bool = True) -> dict:
    """
    Convert the 55-page Gurukulam HTML report (with inline SVG charts and Unicode Devanagari)
    into a high-resolution vector PDF using Microsoft Edge or Google Chrome headless engine.
    If `split_single_pages` is True, it also extracts all individual pages into a subfolder:
    e.g., reports/{basename}_single_pages/Page_01.pdf ... Page_55.pdf
    """
    os.makedirs(os.path.dirname(os.path.abspath(output_pdf_path)), exist_ok=True)
    with tempfile.NamedTemporaryFile("w", suffix=".html", encoding="utf-8", delete=False) as tf:
        tf.write(html_content)
        temp_html_path = tf.name

    import shutil
    raw_candidates = [
        shutil.which("google-chrome"),
        shutil.which("google-chrome-stable"),
        shutil.which("chromium"),
        shutil.which("chromium-browser"),
        "/usr/bin/google-chrome",
        "/usr/bin/google-chrome-stable",
        "/usr/bin/chromium",
        "/usr/bin/chromium-browser",
        "/snap/bin/chromium",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    ]
    browser_candidates = [b for b in raw_candidates if b and os.path.exists(b)]
    browser_exe = browser_candidates[0] if browser_candidates else None

    result = {"success": False, "pdf_path": output_pdf_path, "single_pages_dir": None, "page_count": 0}
    user_data_dir = tempfile.mkdtemp(prefix="vedas_edge_")

    try:
        if os.path.exists(output_pdf_path):
            try:
                os.remove(output_pdf_path)
            except Exception:
                pass

        if browser_exe:
            cmd = [
                browser_exe,
                "--headless=new",
                "--no-sandbox",
                "--disable-gpu",
                "--disable-dev-shm-usage",
                "--no-pdf-header-footer",
                f"--user-data-dir={user_data_dir}",
                "--virtual-time-budget=2000",
                f"--print-to-pdf={os.path.abspath(output_pdf_path)}",
                f"file:///{temp_html_path.replace(os.sep, '/')}",
            ]
            try:
                flags = 0x08000000 if sys.platform == "win32" else 0
                run_res = subprocess.run(
                    cmd,
                    timeout=90,
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    creationflags=flags
                )
                if run_res.returncode != 0:
                    result["error"] = run_res.stderr.decode(errors='replace')
            except Exception as be:
                result["error"] = str(be)

            if os.path.exists(output_pdf_path) and os.path.getsize(output_pdf_path) > 1000:
                result["success"] = True
                
                # Split into individual single page PDFs
                if split_single_pages:
                    try:
                        import pypdf
                        reader = pypdf.PdfReader(output_pdf_path)
                        total_p = len(reader.pages)
                        result["page_count"] = total_p
                        
                        base_stem = os.path.splitext(os.path.basename(output_pdf_path))[0]
                        single_dir = os.path.join(os.path.dirname(output_pdf_path), f"{base_stem}_pages")
                        os.makedirs(single_dir, exist_ok=True)
                        result["single_pages_dir"] = single_dir
                        
                        for idx, page in enumerate(reader.pages, start=1):
                            writer = pypdf.PdfWriter()
                            writer.add_page(page)
                            out_p = os.path.join(single_dir, f"Page_{idx:02d}.pdf")
                            with open(out_p, "wb") as pf:
                                writer.write(pf)
                    except Exception as pe:
                        print("Warning: Could not split individual pages:", pe)

        if not (os.path.exists(output_pdf_path) and os.path.getsize(output_pdf_path) > 1000):
            # If headless browser is absent on container, notify caller for instant client dynamic print
            result["success"] = False
            result["headless_absent"] = True
    finally:
        try:
            os.remove(temp_html_path)
        except OSError:
            pass
        try:
            import shutil
            shutil.rmtree(user_data_dir, ignore_errors=True)
        except Exception:
            pass
    return result

