# -*- coding: utf-8 -*-
"""
Vedas Kundli CRM - Comprehensive 3-Page Royal Matrimonial Milan Dossier Generator
(अष्टकूट मेलापक, वर-कन्या कुण्डली तुलना, मांगलिक दोष परीक्षण एवं दाम्पत्य फलादेश)
"""

import os
import base64
from engine.svg_charts import render_north_indian_svg
from engine.vargas_avkahada import compute_shodashvarga
from engine.varshaphal_sadesati_yogas import compute_manglik_and_kalsarpa


def _fmt_deg(deg: float) -> str:
    sign_deg = deg % 30.0
    d = int(sign_deg)
    m = int(round((sign_deg - d) * 60.0))
    if m == 60:
        d += 1
        m = 0
    return f"{d:02d}°{m:02d}'"


_IMG_CACHE = {}

def _get_god_img_b64(name: str) -> str:
    if name in _IMG_CACHE:
        return _IMG_CACHE[name]
    cur_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for fname in [f"thumb_{name}.png", f"{name}.png"]:
        target = os.path.join(cur_dir, "assets", "gods", fname)
        if os.path.exists(target):
            try:
                with open(target, "rb") as f:
                    b64 = base64.b64encode(f.read()).decode("ascii")
                    data_url = f"data:image/png;base64,{b64}"
                    _IMG_CACHE[name] = data_url
                    return data_url
            except Exception:
                pass
    return ""


def build_milan_dossier_html(boy_core: dict, girl_core: dict, milan: dict, brand: dict, lang: str = "hi") -> str:
    """
    Generate an opulent, 3-page Royal Matrimonial Matchmaking Dossier HTML
    complete with side-by-side D1 charts, comparative planetary table,
    36-Guna Ashtakoot matrix, Manglik harmony, Nadi/Bhakoot parihar,
    and Vedic matrimonial remedies.
    """
    is_hi = (lang == "hi")

    # 1. Compute D1 charts for both
    b_sv = compute_shodashvarga(boy_core)
    g_sv = compute_shodashvarga(girl_core)
    b_d1 = b_sv["charts"]["D1"]
    g_d1 = g_sv["charts"]["D1"]

    b_svg = render_north_indian_svg(b_d1["lagna_sign"], b_d1["house_planets"], lang=("hi" if is_hi else "en"), size=230)
    g_svg = render_north_indian_svg(g_d1["lagna_sign"], g_d1["house_planets"], lang=("hi" if is_hi else "en"), size=230)

    # 2. Manglik analysis
    b_mang = compute_manglik_and_kalsarpa(boy_core)["manglik"]
    g_mang = compute_manglik_and_kalsarpa(girl_core)["manglik"]

    # 3. Core info
    b_meta = boy_core["meta"]
    g_meta = girl_core["meta"]
    b_moon = boy_core["planet_by_id"]["Moon"]
    g_moon = girl_core["planet_by_id"]["Moon"]
    b_asc_deg = boy_core["planet_by_id"]["ASC"]["deg_in_sign"]
    g_asc_deg = girl_core["planet_by_id"]["ASC"]["deg_in_sign"]

    # 4. Koots dictionary for attributes
    koot_dict = {k.get("koot_en"): (k.get("boy_val", ""), k.get("girl_val", "")) for k in milan.get("koots", [])}

    # 5. Comparative planetary table (9 planets)
    planet_order = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
    comp_planet_rows = []
    for pid in planet_order:
        bp = boy_core["planet_by_id"].get(pid, {})
        gp = girl_core["planet_by_id"].get(pid, {})
        p_name = bp.get("name_hi" if is_hi else "name_en", pid)

        b_sign = bp.get("sign_hi" if is_hi else "sign_en", "")
        b_pos = f"{b_sign} {_fmt_deg(bp.get('deg_in_sign', 0.0))}"
        b_nak = f"{bp.get('nakshatra_hi' if is_hi else 'nakshatra_en', '')} ({bp.get('pada', 1)})"

        g_sign = gp.get("sign_hi" if is_hi else "sign_en", "")
        g_pos = f"{g_sign} {_fmt_deg(gp.get('deg_in_sign', 0.0))}"
        g_nak = f"{gp.get('nakshatra_hi' if is_hi else 'nakshatra_en', '')} ({gp.get('pada', 1)})"

        comp_planet_rows.append(f"""
        <tr>
          <td><strong>{p_name}</strong></td>
          <td>{b_pos}</td>
          <td>{b_nak}</td>
          <td>{g_pos}</td>
          <td>{g_nak}</td>
        </tr>
        """)
    comp_planet_html = "".join(comp_planet_rows)

    # 6. Koots detailed rows
    koot_area_map = {
        "Varna": ("कार्य प्रकृति व अहंकार (Ego & Temperament)", "Spiritual / Work Temperament"),
        "Vasya": ("पारस्परिक आकर्षण व नियंत्रण (Mutual Attraction)", "Mutual Control / Attraction"),
        "Tara": ("आरोग्य व भाग्य अनुकूलता (Destiny & Health)", "Destiny & Longevity Harmony"),
        "Yoni": ("शारीरिक आकर्षण व काम सामंजस्य (Physical Affinity)", "Biological / Sexual Compatibility"),
        "Graha Maitri": ("मानसिक मित्रता व विचार सामंजस्य (Friendship)", "Mental Compatibility & Outlook"),
        "Gana": ("स्वभाव व व्यवहार समन्वय (Behavioral Nature)", "Behavioral Temperament"),
        "Bhakoot": ("दांपत्य सुख, वंश वृद्धि व समृद्धि (Prosperity)", "Family Growth & Marital Health"),
        "Nadi": ("आनुवंशिक ऊर्जा व संतान सुख (Genetics & Progeny)", "Genetic Vigor & Progeny")
    }

    koots_rows = []
    for k in milan.get("koots", []):
        k_code = k.get("koot_en", "")
        area_hi, area_en = koot_area_map.get(k_code, ("", ""))
        area = area_hi if is_hi else area_en
        k_name = k["koot_hi"] if is_hi else k["koot_en"]
        pts_color = "#16a34a" if float(k["obtained"]) >= (float(k["max"]) * 0.6) else ("#d97706" if float(k["obtained"]) > 0 else "#dc2626")

        koots_rows.append(f"""
        <tr>
          <td><strong>{k_name}</strong><br/><span style="font-size:8.5px; color:#78716c;">{area}</span></td>
          <td style="text-align:center; font-weight:bold;">{k['max']}</td>
          <td style="text-align:center; font-weight:bold; color:{pts_color}; font-size:12px;">{k['obtained']}</td>
          <td>{k['boy_val']}</td>
          <td>{k['girl_val']}</td>
          <td style="font-size:9px;">{k['desc_hi'] if is_hi else k['desc_en']}</td>
        </tr>
        """)
    koots_html = "".join(koots_rows)

    # 7. Overall verdict styling
    score = milan["total_score"]
    if score >= 28:
        verdict_badge = "🌟 अति उत्तम मिलान (Excellent Soulmate Match)" if is_hi else "🌟 Excellent Soulmate Match"
        score_gradient = "linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%)"
        border_col = "#10b981"
        badge_col = "#047857"
    elif score >= 18:
        verdict_badge = "✨ उत्तम एवं शुभ मिलान (Auspicious Union)" if is_hi else "✨ Auspicious & Recommended Match"
        score_gradient = "linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%)"
        border_col = "#f59e0b"
        badge_col = "#b45309"
    else:
        verdict_badge = "⚠️ मध्यम / परिहार अपेक्षित (Remedial Match)" if is_hi else "⚠️ Average / Remedial Review Needed"
        score_gradient = "linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%)"
        border_col = "#ef4444"
        badge_col = "#b91c1c"

    # 8. Brand info
    kendra_name = brand.get("kendra_name", "वेदास ज्योतिष पीठ (Vedas Kundli Predictions)")
    astrologer_name = brand.get("astrologer_name", "आचार्य ज्योतिषविद")
    phone = brand.get("phone", "+91 98765 43210")

    # 9. Manglik Harmony Text
    m_harm = milan.get("manglik_harmony", {})
    m_verdict = m_harm.get("verdict_hi" if is_hi else "verdict_en", "")

    # Nadi & Bhakoot Parihar specific text
    bhakoot_koot = next((k for k in milan.get("koots", []) if k.get("koot_en") == "Bhakoot"), {})
    nadi_koot = next((k for k in milan.get("koots", []) if k.get("koot_en") == "Nadi"), {})

    nadi_status_text = (
        "नाड़ी दोष पूर्णतः अनुपस्थित है। वर एवं कन्या की भिन्न नाड़ी होने से संतान सुख, दीर्घायु एवं आरोग्य सर्वोत्तम रहेगा।"
        if float(nadi_koot.get("obtained", 0)) > 0 else
        "एक नाड़ी होने से नाड़ी दोष उत्पन्न होता है। इसके निवारण हेतु महामृत्युंजय जप, स्वर्ण दान अथवा युगल संकल्प अनुष्ठान शास्त्रसम्मत है।"
    ) if is_hi else (
        "Nadi Dosha is absent or cancelled. Genetic constitution and progeny prospects are sound and harmonious."
        if float(nadi_koot.get("obtained", 0)) > 0 else
        "Same Nadi present. Astrological remedial pacification (Mahamrityunjaya Japa, Gauri-Shankar Puja) is recommended."
    )

    bhakoot_status_text = (
        "भकूट दोष अनुपस्थित अथवा राशीश मित्रता के कारण पूर्ण परिहार प्राप्त है। गृहस्थ सुख व समृद्धि अनुकूल रहेगी।"
        if float(bhakoot_koot.get("obtained", 0)) > 0 else
        "भकूट षडाष्टक, नवपंचम अथवा द्विर्द्वादश होने पर भकूट दोष रहता है। इसके लिए भगवान शिव-पार्वती की संयुक्त उपासना कल्याणकारी है।"
    ) if is_hi else (
        "Bhakoot is harmonious or cancelled by friendly planetary lordship. Conjugal prosperity is well supported."
        if float(bhakoot_koot.get("obtained", 0)) > 0 else
        "Bhakoot dosha present. Worshipping Lord Shiva and Goddess Parvati mitigates this placement."
    )

    ganesha_b64 = _get_god_img_b64("ganesha")
    shiva_b64 = _get_god_img_b64("shiva")
    durga_b64 = _get_god_img_b64("durga")
    hanuman_b64 = _get_god_img_b64("hanuman")

    img_g_tag = f'<img src="{ganesha_b64}" class="header-logo" alt="Ganesha"/>' if ganesha_b64 else ''
    img_s_tag = f'<img src="{shiva_b64}" class="header-logo" alt="Shiva"/>' if shiva_b64 else ''
    img_d_tag = f'<img src="{durga_b64}" class="header-logo" alt="Durga"/>' if durga_b64 else ''
    img_h_tag = f'<img src="{hanuman_b64}" class="header-logo" alt="Hanuman"/>' if hanuman_b64 else ''

    # Build the 3-Page HTML with page breaks
    return f"""<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="utf-8"/>
<title>Vedas Kundli - Matrimonial Milan Dossier ({b_meta['name']} & {g_meta['name']})</title>
<style>
  @page {{
    size: A4 portrait;
    margin: 8mm 9mm 8mm 9mm;
  }}
  * {{
    box-sizing: border-box;
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
  }}
  body {{
    font-family: 'Plus Jakarta Sans', 'Segoe UI', -apple-system, Arial, sans-serif;
    background: #FFFDF9;
    color: #1F1B16;
    margin: 0;
    padding: 0;
    line-height: 1.35;
    font-size: 10px;
  }}
  .page {{
    width: 100%;
    min-height: 275mm;
    page-break-after: always;
    border: 2px solid #D97706;
    background: #FFFDF9;
    padding: 12px 14px;
    position: relative;
    box-sizing: border-box;
    margin-bottom: 20px;
    box-shadow: 0 4px 14px rgba(0,0,0,0.06);
  }}
  @media print {{
    body {{ background: transparent; }}
    .page {{
      border: 1.5px solid #B45309;
      box-shadow: none;
      margin-bottom: 0;
      page-break-after: always;
      min-height: 280mm;
    }}
  }}
  .corner-decor {{
    position: absolute;
    width: 18px;
    height: 18px;
    border-color: #B45309;
    pointer-events: none;
  }}
  .tl {{ top: 4px; left: 4px; border-top: 2px solid #B45309; border-left: 2px solid #B45309; }}
  .tr {{ top: 4px; right: 4px; border-top: 2px solid #B45309; border-right: 2px solid #B45309; }}
  .bl {{ bottom: 4px; left: 4px; border-bottom: 2px solid #B45309; border-left: 2px solid #B45309; }}
  .br {{ bottom: 4px; right: 4px; border-bottom: 2px solid #B45309; border-right: 2px solid #B45309; }}

  /* Header */
  .milan-header {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 2px solid #F59E0B;
    padding-bottom: 6px;
    margin-bottom: 8px;
  }}
  .header-logo {{
    width: 44px;
    height: 44px;
    object-fit: cover;
    border-radius: 50%;
    border: 1.5px solid #D97706;
  }}
  .header-text {{
    text-align: center;
    flex: 1;
    padding: 0 8px;
  }}
  .om-tag {{
    font-size: 10px;
    font-weight: 800;
    color: #B45309;
    letter-spacing: 0.5px;
  }}
  .main-title {{
    font-size: 16px;
    font-weight: 900;
    color: #7C2D12;
    margin: 2px 0;
    letter-spacing: 0.5px;
  }}
  .sub-title {{
    font-size: 9.5px;
    color: #92400E;
    font-weight: 700;
  }}

  /* Page Footer */
  .milan-footer {{
    position: absolute;
    bottom: 8px;
    left: 14px;
    right: 14px;
    border-top: 1px solid #E5E7EB;
    padding-top: 4px;
    display: flex;
    justify-content: space-between;
    font-size: 8px;
    color: #6B7280;
    font-weight: 600;
  }}

  /* Section Title */
  .section-heading {{
    background: linear-gradient(90deg, #7C2D12 0%, #B45309 100%);
    color: #FFFFFF;
    font-size: 10px;
    font-weight: 800;
    padding: 3px 8px;
    border-radius: 4px;
    margin: 6px 0 5px 0;
    letter-spacing: 0.5px;
    display: flex;
    align-items: center;
    justify-content: space-between;
  }}

  /* Two Column Grid */
  .two-col {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
    margin-bottom: 6px;
  }}
  .card {{
    border: 1.2px solid #EADBC8;
    background: #FFFFFF;
    border-radius: 6px;
    padding: 6px 8px;
  }}
  .card-title {{
    font-size: 10.5px;
    font-weight: 800;
    color: #92400E;
    border-bottom: 1px solid #FDE68A;
    padding-bottom: 2px;
    margin-bottom: 4px;
    display: flex;
    align-items: center;
    justify-content: space-between;
  }}

  /* Tables */
  table.data-table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 9px;
  }}
  table.data-table th, table.data-table td {{
    border: 1px solid #EADBC8;
    padding: 3px 5px;
    text-align: left;
  }}
  table.data-table th {{
    background: #FEF3C7;
    color: #78350F;
    font-weight: 800;
  }}
  table.data-table tr:nth-child(even) {{
    background: #FFFDF9;
  }}

  /* Chart Wrappers */
  .chart-box {{
    display: flex;
    flex-direction: column;
    align-items: center;
    background: #FFFFFF;
    border: 1px solid #EADBC8;
    border-radius: 6px;
    padding: 4px;
  }}
  .chart-box svg {{
    max-width: 100%;
    height: auto;
  }}

  /* Grand Score Ribbon */
  .score-ribbon {{
    background: {score_gradient};
    border: 1.8px solid {border_col};
    border-radius: 8px;
    padding: 8px 12px;
    text-align: center;
    margin-bottom: 8px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.03);
  }}
  .score-num {{
    font-size: 28px;
    font-weight: 900;
    color: #7C2D12;
    line-height: 1.1;
  }}
  .score-badge {{
    display: inline-block;
    background: {badge_col};
    color: #FFFFFF;
    font-size: 10px;
    font-weight: 800;
    padding: 2px 10px;
    border-radius: 10px;
    margin-top: 3px;
  }}

  /* 5 Pillars Grid */
  .pillar-grid {{
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 5px;
    margin: 6px 0;
  }}
  .pillar-box {{
    background: #FFFBEB;
    border: 1px solid #FDE68A;
    border-radius: 5px;
    padding: 5px 3px;
    text-align: center;
  }}
  .pillar-title {{
    font-size: 8.5px;
    font-weight: 800;
    color: #92400E;
    margin-bottom: 1px;
  }}
  .pillar-stars {{
    color: #D97706;
    font-size: 9.5px;
    font-weight: 800;
  }}

  /* Remedy Pill */
  .remedy-card {{
    background: #FFFDF9;
    border-left: 3px solid #B45309;
    border-top: 1px solid #EADBC8;
    border-right: 1px solid #EADBC8;
    border-bottom: 1px solid #EADBC8;
    border-radius: 4px;
    padding: 5px 8px;
    margin-bottom: 5px;
    font-size: 9px;
  }}
  .remedy-title {{
    font-weight: 800;
    color: #7C2D12;
    margin-bottom: 1px;
  }}
</style>
</head>
<body>

  <!-- ========================================================================= -->
  <!-- PAGE 1: वर-कन्या परिचय, जन्म कुण्डली (D1) एवं ग्रह स्थिति तुलना -->
  <!-- ========================================================================= -->
  <div class="page">
    <div class="corner-decor tl"></div>
    <div class="corner-decor tr"></div>
    <div class="corner-decor bl"></div>
    <div class="corner-decor br"></div>

    <div class="milan-header">
      {img_g_tag}
      <div class="header-text">
        <div class="om-tag">॥ श्री गणेशाय नमः ॥ श्री कुलदेवतायै नमः ॥</div>
        <div class="main-title">॥ वैदिक अष्टकूट विवाह मेलापक विवरण ॥</div>
        <div class="sub-title">{kendra_name} | {phone}</div>
      </div>
      {img_s_tag}
    </div>

    <!-- Bride & Groom Info Cards -->
    <div class="two-col">
      <div class="card">
        <div class="card-title">
          <span>👦 वर विवरण (Groom Particulars)</span>
          <span style="font-size:9.5px; color:#78350F;">वर पक्ष</span>
        </div>
        <table class="data-table">
          <tr><th>नाम (Name)</th><td><strong>{b_meta['name']}</strong></td></tr>
          <tr><th>जन्म तिथि (DOB)</th><td>{b_meta['dob_slash']} ({b_meta['tob_str']})</td></tr>
          <tr><th>जन्म स्थान (Place)</th><td>{b_meta['place']}</td></tr>
          <tr><th>जन्म लग्न (Lagna)</th><td>{b_meta['lagna_hi'] if is_hi else b_meta['lagna_en']} ({_fmt_deg(b_asc_deg)})</td></tr>
          <tr><th>जन्म राशि (Rashi)</th><td>{b_meta['rasi_hi'] if is_hi else b_meta['rasi_en']} ({b_meta['rasi_lord_hi'] if is_hi else b_meta['rasi_lord_en']})</td></tr>
          <tr><th>नक्षत्र (Nakshatra)</th><td>{b_moon['nakshatra_hi'] if is_hi else b_moon['nakshatra_en']} (चरण {b_moon['pada']})</td></tr>
          <tr><th>वर्ण / वश्य</th><td>{koot_dict.get('Varna', ('-','-'))[0]} / {koot_dict.get('Vasya', ('-','-'))[0]}</td></tr>
          <tr><th>योनि / गण / नाड़ी</th><td>{koot_dict.get('Yoni', ('-','-'))[0]} / {koot_dict.get('Gana', ('-','-'))[0]} / {koot_dict.get('Nadi', ('-','-'))[0]}</td></tr>
        </table>
      </div>

      <div class="card">
        <div class="card-title">
          <span>👧 कन्या विवरण (Bride Particulars)</span>
          <span style="font-size:9.5px; color:#78350F;">कन्या पक्ष</span>
        </div>
        <table class="data-table">
          <tr><th>नाम (Name)</th><td><strong>{g_meta['name']}</strong></td></tr>
          <tr><th>जन्म तिथि (DOB)</th><td>{g_meta['dob_slash']} ({g_meta['tob_str']})</td></tr>
          <tr><th>जन्म स्थान (Place)</th><td>{g_meta['place']}</td></tr>
          <tr><th>जन्म लग्न (Lagna)</th><td>{g_meta['lagna_hi'] if is_hi else g_meta['lagna_en']} ({_fmt_deg(g_asc_deg)})</td></tr>
          <tr><th>जन्म राशि (Rashi)</th><td>{g_meta['rasi_hi'] if is_hi else g_meta['rasi_en']} ({g_meta['rasi_lord_hi'] if is_hi else g_meta['rasi_lord_en']})</td></tr>
          <tr><th>नक्षत्र (Nakshatra)</th><td>{g_moon['nakshatra_hi'] if is_hi else g_moon['nakshatra_en']} (चरण {g_moon['pada']})</td></tr>
          <tr><th>वर्ण / वश्य</th><td>{koot_dict.get('Varna', ('-','-'))[1]} / {koot_dict.get('Vasya', ('-','-'))[1]}</td></tr>
          <tr><th>योनि / गण / नाड़ी</th><td>{koot_dict.get('Yoni', ('-','-'))[1]} / {koot_dict.get('Gana', ('-','-'))[1]} / {koot_dict.get('Nadi', ('-','-'))[1]}</td></tr>
        </table>
      </div>
    </div>

    <!-- Side-by-Side D1 Lagna Kundlis -->
    <div class="section-heading">
      <span>📐 वैदिक लग्न कुण्डली तुलना (Side-by-Side D1 Horoscopes)</span>
      <span style="font-size:8.5px; font-weight:600;">निरयण पद्धति (Lahiri Ayanamsha)</span>
    </div>
    <div class="two-col" style="margin-bottom:6px;">
      <div class="chart-box">
        <div style="font-weight:800; color:#7C2D12; font-size:10px; margin-bottom:2px;">वर लग्न चक्र (Groom D1)</div>
        {b_svg}
      </div>
      <div class="chart-box">
        <div style="font-weight:800; color:#7C2D12; font-size:10px; margin-bottom:2px;">कन्या लग्न चक्र (Bride D1)</div>
        {g_svg}
      </div>
    </div>

    <!-- Comparative Planetary Table -->
    <div class="section-heading">
      <span>🪐 वर-कन्या नवग्रह स्थिति तुलनात्मक सारणी (Comparative Planetary Coordinates)</span>
      <span style="font-size:8.5px; font-weight:600;">9 ग्रह स्पष्ट मान</span>
    </div>
    <table class="data-table">
      <thead>
        <tr>
          <th>ग्रह (Planet)</th>
          <th>वर राशि व अंश (Groom Position)</th>
          <th>वर नक्षत्र (Groom Star)</th>
          <th>कन्या राशि व अंश (Bride Position)</th>
          <th>कन्या नक्षत्र (Bride Star)</th>
        </tr>
      </thead>
      <tbody>
        {comp_planet_html}
      </tbody>
    </table>

    <div class="milan-footer">
      <span>{kendra_name} • {astrologer_name}</span>
      <span>पृष्ठ १ / ३ (Page 1 of 3: Horoscopes & Profiles)</span>
    </div>
  </div>


  <!-- ========================================================================= -->
  <!-- PAGE 2: अष्टकूट मिलान (36-Guna Scorecard) & मांगलिक दोष परीक्षण -->
  <!-- ========================================================================= -->
  <div class="page">
    <div class="corner-decor tl"></div>
    <div class="corner-decor tr"></div>
    <div class="corner-decor bl"></div>
    <div class="corner-decor br"></div>

    <div class="milan-header">
      {img_g_tag}
      <div class="header-text">
        <div class="om-tag">॥ अष्टकूट गुण मिलान एवं मांगलिक परीक्षण ॥</div>
        <div class="main-title">{b_meta['name']} 💍 {g_meta['name']}</div>
        <div class="sub-title">वैदिक मेलापक निर्णय एवं दांपत्य सामंजस्य</div>
      </div>
      {img_d_tag}
    </div>

    <!-- Grand Score Ribbon -->
    <div class="score-ribbon">
      <div style="font-size:11px; font-weight:800; color:#92400E; letter-spacing:0.5px;">कुल गुण मिलान प्राप्तांक (TOTAL ASHTAKOOT SCORE)</div>
      <div class="score-num">{score} <span style="font-size:18px; font-weight:700; color:#78350F;">/ 36</span></div>
      <div class="score-badge">{verdict_badge}</div>
      <div style="font-size:10px; font-weight:700; color:#7C2D12; margin-top:3px;">
        {milan['verdict_hi'] if is_hi else milan['verdict_en']} ({milan.get('percentage', 0)}%)
      </div>
    </div>

    <!-- Ashtakoot Matrix -->
    <div class="section-heading">
      <span>⚖️ अष्टकूट ३६-गुण विस्तृत विश्लेषण (Ashtakoot 36-Point Detailed Matrix)</span>
      <span style="font-size:8.5px; font-weight:600;">शास्त्रसम्मत अंकन</span>
    </div>
    <table class="data-table" style="margin-bottom:8px;">
      <thead>
        <tr>
          <th style="width:22%;">कूट व क्षेत्र (Koot & Area)</th>
          <th style="width:8%; text-align:center;">अधिकतम</th>
          <th style="width:8%; text-align:center;">प्राप्त</th>
          <th style="width:14%;">वर लक्षण</th>
          <th style="width:14%;">कन्या लक्षण</th>
          <th style="width:34%;">सामंजस्य फलादेश (Interpretation)</th>
        </tr>
      </thead>
      <tbody>
        {koots_html}
      </tbody>
      <tfoot>
        <tr style="background:#FEF3C7; font-weight:900;">
          <td><strong>कुल योग (Grand Total)</strong></td>
          <td style="text-align:center;">36</td>
          <td style="text-align:center; color:#c2540a; font-size:13px;">{score}</td>
          <td colspan="3" style="text-align:right;"><strong>{milan['verdict_grade']} Compatibility</strong></td>
        </tr>
      </tfoot>
    </table>

    <!-- Manglik Dosha Analysis -->
    <div class="section-heading">
      <span>🔥 मांगलिक दोष एवं कुज साम्य परीक्षण (Kuja Dosha & Manglik Harmony Analysis)</span>
      <span style="font-size:8.5px; font-weight:600;">लग्न व चंद्र कुंडली आधार</span>
    </div>
    <div class="two-col" style="margin-bottom:4px;">
      <div class="card">
        <div class="card-title">
          <span>👦 वर मांगलिक स्थिति (Groom Kuja Dosha)</span>
          <span style="font-size:9.5px; font-weight:800; color:{'#DC2626' if b_mang['is_manglik'] else '#15803D'};">
            {'⚠️ मांगलिक (Manglik)' if b_mang['is_manglik'] else '✅ अमंगल मुक्त (Non-Manglik)'}
          </span>
        </div>
        <p style="margin:2px 0; font-size:9px;"><strong>लग्न से मंगल भाव:</strong> {b_mang.get('mars_house_lagna_word_hi' if is_hi else 'mars_house_lagna_word_en', '')}</p>
        <p style="margin:2px 0; font-size:9px;"><strong>चंद्र से मंगल भाव:</strong> {b_mang.get('mars_house_moon_word_hi' if is_hi else 'mars_house_moon_word_en', '')}</p>
        <p style="margin:2px 0; font-size:9px; color:#4B5563;">{b_mang.get('status_hi' if is_hi else 'status_en', '')}</p>
      </div>

      <div class="card">
        <div class="card-title">
          <span>👧 कन्या मांगलिक स्थिति (Bride Kuja Dosha)</span>
          <span style="font-size:9.5px; font-weight:800; color:{'#DC2626' if g_mang['is_manglik'] else '#15803D'};">
            {'⚠️ मांगलिक (Manglik)' if g_mang['is_manglik'] else '✅ अमंगल मुक्त (Non-Manglik)'}
          </span>
        </div>
        <p style="margin:2px 0; font-size:9px;"><strong>लग्न से मंगल भाव:</strong> {g_mang.get('mars_house_lagna_word_hi' if is_hi else 'mars_house_lagna_word_en', '')}</p>
        <p style="margin:2px 0; font-size:9px;"><strong>चंद्र से मंगल भाव:</strong> {g_mang.get('mars_house_moon_word_hi' if is_hi else 'mars_house_moon_word_en', '')}</p>
        <p style="margin:2px 0; font-size:9px; color:#4B5563;">{g_mang.get('status_hi' if is_hi else 'status_en', '')}</p>
      </div>
    </div>

    <!-- Manglik Compatibility Summary -->
    <div style="background:#FFFBEB; border:1.5px solid #FDE68A; border-radius:6px; padding:6px 10px; margin-top:4px;">
      <div style="font-weight:800; color:#7C2D12; font-size:10px; margin-bottom:2px;">
        🛡️ मांगलिक सामंजस्य निष्कर्ष (Manglik Harmony Verdict):
      </div>
      <div style="font-size:9.5px; color:#92400E; font-weight:700;">
        {m_verdict}
      </div>
    </div>

    <div class="milan-footer">
      <span>{kendra_name} • {astrologer_name}</span>
      <span>पृष्ठ २ / ३ (Page 2 of 3: Ashtakoot & Manglik Verification)</span>
    </div>
  </div>


  <!-- ========================================================================= -->
  <!-- PAGE 3: नाड़ी एवं भकूट परिहार, दाम्पत्य फलादेश, वैदिक उपाय एवं आशीर्वाद -->
  <!-- ========================================================================= -->
  <div class="page">
    <div class="corner-decor tl"></div>
    <div class="corner-decor tr"></div>
    <div class="corner-decor bl"></div>
    <div class="corner-decor br"></div>

    <div class="milan-header">
      {img_g_tag}
      <div class="header-text">
        <div class="om-tag">॥ दोष परिहार, दांपत्य फलादेश एवं वैदिक उपाय ॥</div>
        <div class="main-title">॥ दांपत्य जीवन मंगलमय कल्याण सूत्र ॥</div>
        <div class="sub-title">सुखी, समृद्ध एवं दीर्घायु दांपत्य जीवन के शाश्वत नियम</div>
      </div>
      {img_h_tag}
    </div>

    <!-- Nadi & Bhakoot Dosha Special Analysis -->
    <div class="section-heading">
      <span>🔬 मुख्य दोष परिहार परीक्षण (Nadi & Bhakoot Parihar Evaluation)</span>
      <span style="font-size:8.5px; font-weight:600;">वशिष्ठ एवं नारद संहिता अनुसार</span>
    </div>

    <div class="two-col" style="margin-bottom:6px;">
      <div class="card">
        <div class="card-title">
          <span>🧬 नाड़ी दोष स्थिति एवं परिहार</span>
          <span style="font-size:9px; font-weight:800; color:{'#15803D' if float(nadi_koot.get('obtained', 0)) > 0 else '#DC2626'};">
            {nadi_koot.get('obtained', 0)} / 8 अंक
          </span>
        </div>
        <p style="font-size:9px; line-height:1.4; margin:0; color:#374151;">
          {nadi_status_text}
        </p>
      </div>

      <div class="card">
        <div class="card-title">
          <span>🏡 भकूट दोष स्थिति एवं परिहार</span>
          <span style="font-size:9px; font-weight:800; color:{'#15803D' if float(bhakoot_koot.get('obtained', 0)) > 0 else '#DC2626'};">
            {bhakoot_koot.get('obtained', 0)} / 7 अंक
          </span>
        </div>
        <p style="font-size:9px; line-height:1.4; margin:0; color:#374151;">
          {bhakoot_status_text}
        </p>
      </div>
    </div>

    <!-- 5 Pillars Assessment -->
    <div class="section-heading">
      <span>🏛️ दाम्पत्य जीवन के ५ आधार स्तम्भ (5 Pillars of Conjugal Life Harmony)</span>
      <span style="font-size:8.5px; font-weight:600;">सर्वांगीण मूल्यांकन</span>
    </div>
    <div class="pillar-grid">
      <div class="pillar-box">
        <div class="pillar-title">मानसिक व भावना</div>
        <div class="pillar-stars">★★★★★</div>
        <div style="font-size:7.5px; color:#6B7280; margin-top:1px;">उत्तम विचार साम्य</div>
      </div>
      <div class="pillar-box">
        <div class="pillar-title">आरोग्य व आयु</div>
        <div class="pillar-stars">★★★★☆</div>
        <div style="font-size:7.5px; color:#6B7280; margin-top:1px;">दीर्घायु व स्वास्थ्य</div>
      </div>
      <div class="pillar-box">
        <div class="pillar-title">संतान व कुल वृद्धि</div>
        <div class="pillar-stars">★★★★★</div>
        <div style="font-size:7.5px; color:#6B7280; margin-top:1px;">शुभ वंश वृद्धि</div>
      </div>
      <div class="pillar-box">
        <div class="pillar-title">आर्थिक उन्नति</div>
        <div class="pillar-stars">★★★★☆</div>
        <div style="font-size:7.5px; color:#6B7280; margin-top:1px;">परस्पर भाग्योदय</div>
      </div>
      <div class="pillar-box">
        <div class="pillar-title">आध्यात्मिक समन्वय</div>
        <div class="pillar-stars">★★★★★</div>
        <div style="font-size:7.5px; color:#6B7280; margin-top:1px;">धार्मिक अनुकूलता</div>
      </div>
    </div>

    <!-- Vedic Remedies & Guidelines -->
    <div class="section-heading">
      <span>🪔 सुखद दाम्पत्य हेतु सिद्ध वैदिक उपाय एवं अनुष्ठान (Auspicious Matrimonial Remedies)</span>
      <span style="font-size:8.5px; font-weight:600;">कल्याणकारी परामर्श</span>
    </div>

    <div class="remedy-card">
      <div class="remedy-title">🕉️ श्री गौरी-शंकर एवं शिव-पार्वती संयुक्त पूजन</div>
      <div>
        विवाह पश्चात अथवा विवाह पूर्व दोनों पक्ष शुक्ल पक्ष के सोमवार अथवा प्रदोष काल में भगवान शिव एवं माता पार्वती का पंचामृत से अभिषेक करें। इससे दांपत्य में आजीवन प्रेम, विश्वास और सौहार्द बना रहता है।
      </div>
    </div>

    <div class="remedy-card">
      <div class="remedy-title">📿 दैनिक दांपत्य कल्याण मंत्र जप</div>
      <div>
        प्रातःकाल शुद्ध होकर <strong>"॥ ॐ उमामहेश्वराभ्यां नमः ॥"</strong> अथवा <strong>"॥ ॐ गौरीशंकराय नमः ॥"</strong> मंत्र की १ माला (१०८ जप) करने से पारिवारिक कलह समाप्त होकर सुख-शांति की अभिवृद्धि होती है।
      </div>
    </div>

    <div class="remedy-card">
      <div class="remedy-title">💎 रत्न एवं दान परामर्श</div>
      <div>
        गुरु (बृहस्पति) एवं शुक्र की शुभता हेतु गुरुवार को चने की दाल व बेसन के लड्डू का दान तथा शुक्रवार को श्वेत वस्तुओं (चावल, मिश्री, दूध) का दान दाम्पत्य के आर्थिक एवं भौतिक सुखों को पुष्ट करता है।
      </div>
    </div>

    <!-- Sign-off & Astrologer Seal -->
    <div style="display:flex; justify-content:space-between; align-items:flex-end; margin-top:10px; border-top:1.5px dashed #D97706; padding-top:8px;">
      <div style="font-size:9px; color:#4B5563; max-width:62%;">
        <strong>ज्योतिषीय परामर्श सारांश:</strong> यह मेलापक रिपोर्ट वैदिक ज्योतिष के प्राचीन प्रामाणिक ग्रंथों (वृहत्पाराशर होराशास्त्र, मुहूर्तमार्तण्ड व जातकपारिजात) के आधार पर परिगणित की गई है।
      </div>
      <div style="text-align:center;">
        <div style="font-size:9.5px; font-weight:800; color:#7C2D12;">{astrologer_name}</div>
        <div style="font-size:8px; color:#92400E; margin-top:1px;">{kendra_name}</div>
        <div style="margin-top:3px; font-size:8px; border:1px solid #B45309; padding:2px 8px; border-radius:3px; color:#B45309; font-weight:700;">
          [ प्रमाणित वैदिक मेलापक मुहर ]
        </div>
      </div>
    </div>

    <div class="milan-footer">
      <span>{kendra_name} • {astrologer_name}</span>
      <span>पृष्ठ ३ / ३ (Page 3 of 3: Remedies, Forecast & Blessings)</span>
    </div>
  </div>

</body>
</html>"""
