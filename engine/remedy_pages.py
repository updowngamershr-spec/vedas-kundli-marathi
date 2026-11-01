# -*- coding: utf-8 -*-
"""
Vedas Kundli Predictions - Ultra-VIP High-Ticket Remedies & KP Dossier Module
Contains 15 dedicated, sellable pages directly formulated from:
1. Prof. K. S. Krishnamurti - 'Predictive Stellar Astrology' (KP Reader III)
2. Astrologer Gautam Verma - 'KP Astrology House Groupings'
3. Authentic Parashari, Ayurveda & Lal Kitab 1952 Samhita
Formatted in Royal Gurukulam Gold/Maroon luxury cards with 100% Marathi Primary & Hindi Subtitles.
"""

def generate_vip_remedy_pages(data: dict, T, P) -> list[dict]:
    meta = data["meta"]
    planets = data["planets"]
    four_fold = data.get("kp_four_fold", {})
    kp_gems = data.get("kp_gems", {"approved": [], "rejected": []})
    kp_debts = data.get("kp_debts", {})
    kp_disease = data.get("kp_disease", {})
    kp_events = data.get("kp_event_rules", {})
    
    pages = []

    # -------------------------------------------------------------------------
    # PAGE 1: KP 4-FOLD SIGNIFICATORS MATRIX (READER III)
    # -------------------------------------------------------------------------
    p1_html = f"""
    <div class="prose-block" style="font-size:10px; line-height:1.55;">
      <div style="background:linear-gradient(135deg, #FEF3C7 0%, #FFFBEB 100%); border:1.5px solid #D97706; padding:10px; border-radius:8px; margin-bottom:12px;">
        <h3 style="color:#7C2D12; margin:0 0 4px 0; font-size:13px; font-family:'Noto Sans Devanagari', sans-serif;">
          कृष्णमूर्ती पद्धती: ४-स्तरीय ग्रह कार्येश मॅट्रिक्स (4-Fold Significators Matrix — Levels A, B, C, D)
        </h3>
        <p style="margin:0; font-size:10.5px; color:#574032;">
          {P(
            "Prof. K.S. Krishnamurti Reader III Rule: Level A (planets in constellation of occupants) is the strongest significator, followed by Level B (occupants), Level C (planets in star of cusp lord), and Level D (sign ruler).",
            "प्रो. के. एस. कृष्णमूर्ति रीडर ३ चा अचूक नियम: स्तर 'अ' (भावात बसलेल्या ग्रहाच्या नक्षत्रातील ग्रह) सर्वात बलवान असतो, त्यानंतर स्तर 'ब' (भावात स्थित ग्रह), स्तर 'क' (भावेशाच्या नक्षत्रातील ग्रह) आणि स्तर 'ड' (राशी स्वामी)."
          )}
        </p>
      </div>

      <table class="data-table" style="width:100%; font-size:9.5px; border-collapse:collapse; margin-bottom:12px;">
        <thead>
          <tr style="background:#7C2D12; color:#FFF; text-align:center;">
            <th style="padding:5px; border:1px solid #D97706;">भाव (House)</th>
            <th style="padding:5px; border:1px solid #D97706;">स्तर अ (Level A - Strongest)</th>
            <th style="padding:5px; border:1px solid #D97706;">स्तर ब (Level B - Occupant)</th>
            <th style="padding:5px; border:1px solid #D97706;">स्तर क (Level C - Star of Lord)</th>
            <th style="padding:5px; border:1px solid #D97706;">स्तर ड (Level D - Lord)</th>
          </tr>
        </thead>
        <tbody>
    """
    h_sigs = four_fold.get("house_significators", {})
    for h in range(1, 13):
        hs = h_sigs.get(h, {"Level_A": [], "Level_B": [], "Level_C": [], "Level_D": []})
        p1_html += f"""
          <tr style="background:{'#FFF' if h%2!=0 else '#FEF9C3'}; text-align:center;">
            <td style="font-weight:700; color:#7C2D12; border:1px solid #E2E8F0; padding:4px;">भाव {h}</td>
            <td style="border:1px solid #E2E8F0; padding:4px; font-weight:700; color:#166534;">{', '.join(hs['Level_A']) or '—'}</td>
            <td style="border:1px solid #E2E8F0; padding:4px; color:#B45309;">{', '.join(hs['Level_B']) or '—'}</td>
            <td style="border:1px solid #E2E8F0; padding:4px; color:#1E40AF;">{', '.join(hs['Level_C']) or '—'}</td>
            <td style="border:1px solid #E2E8F0; padding:4px; color:#475569;">{', '.join(hs['Level_D']) or '—'}</td>
          </tr>
        """
    p1_html += f"""
        </tbody>
      </table>
      <div style="background:#F8FAFC; border:1px dashed #CBD5E1; padding:8px; border-radius:6px; font-size:9.5px; color:#334155;">
        <strong>के.पी. सिद्धांत (Golden Axiom):</strong> ग्रह घटना सुचवतो (Planet proposes), नक्षत्र निकाल ठरवतो (Star disposes) आणि उपस्वामी (Sub-Lord) ती घटना जीवनात प्रत्यक्ष घडेल की नाही याचा अंतिम निर्णय देतो.
      </div>
    </div>
    """
    pages.append({
        "title_en": "KP 4-Fold Significators Matrix (Levels A, B, C, D)",
        "title_hi": "कृष्णमूर्ती पद्धती ४-स्तरीय ग्रह कार्येश मॅट्रिक्स",
        "html": p1_html
    })

    # -------------------------------------------------------------------------
    # PAGE 2: KP CUSPAL SUB-LORD LIFE EVENT GROUPINGS (GAUTAM VERMA)
    # -------------------------------------------------------------------------
    p2_html = f"""
    <div class="prose-block" style="font-size:10px; line-height:1.52;">
      <div style="background:#FFFBEB; border:1.5px solid #B45309; padding:8px 12px; border-radius:6px; margin-bottom:10px;">
        <h4 style="margin:0 0 3px 0; color:#7C2D12; font-size:12px;">
          १२ भाव उपस्वामी व अचूक घटना विश्लेषण (KP Cuspal Sub-Lord Event Groupings)
        </h4>
        <p style="margin:0; font-size:10px; color:#78350F;">
          गौतम वर्मा यांच्या 'KP Astrology House Groupings' ग्रंथानुसार प्रत्येक भावाचा उपस्वामी कोणत्या भाव समूहाला जोडला आहे यावरून निश्चित होणारे फलादेश:
        </p>
      </div>

      <div style="display:grid; grid-template-columns:1fr 1fr; gap:8px;">
    """
    for h in range(1, 13):
        rules = kp_events.get(h, [])
        p2_html += f"""
        <div style="background:#FFFFFF; border:1.2px solid #E2E8F0; padding:6px 8px; border-radius:6px; box-shadow:0 1px 2px rgba(0,0,0,0.03);">
          <div style="font-weight:800; color:#7C2D12; border-bottom:1px solid #FED7AA; padding-bottom:2px; margin-bottom:4px; font-size:10.5px;">
            भाव {h} विश्लेषण (House {h} CSL)
          </div>
        """
        for r in rules[:2]:
            icon = "✅" if r.get("fav") else "⚠️"
            color = "#166534" if r.get("fav") else "#B91C1C"
            p2_html += f"""
            <div style="margin-bottom:3px; font-size:9.5px;">
              <span style="color:{color}; font-weight:700;">{icon} {r['event_mr']}:</span>
              <span style="background:#FEF3C7; padding:1px 4px; border-radius:3px; font-weight:800; color:#7C2D12;">{'-'.join(map(str, r['houses']))}</span>
              <div style="color:#64748B; font-size:8.8px; margin-top:1px;">{r['desc_mr']}</div>
            </div>
            """
        p2_html += "</div>"

    p2_html += """
      </div>
    </div>
    """
    pages.append({
        "title_en": "KP Cuspal Sub-Lord Event Formulas (Houses 1-12)",
        "title_hi": "के.पी. १२ भाव उपस्वामी घटना सूत्रे व फलादेश",
        "html": p2_html
    })

    # -------------------------------------------------------------------------
    # PAGE 3: KP READER III MATHEMATICAL GEMSTONE PROTOCOL (ZERO DAMAGE RULE)
    # -------------------------------------------------------------------------
    approved = kp_gems.get("approved", [])
    rejected = kp_gems.get("rejected", [])
    p3_html = f"""
    <div class="prose-block" style="font-size:10px; line-height:1.55;">
      <div style="background:#FEF2F2; border:1.5px solid #EF4444; padding:9px 12px; border-radius:6px; margin-bottom:10px;">
        <h4 style="margin:0 0 3px 0; color:#991B1B; font-size:12px;">
          ⚠️ प्रो. के. एस. कृष्णमूर्ति रत्न निवड व वर्ज्य नियम (KP Zero Damage Gemstone Rule — Reader III, p. 414)
        </h4>
        <p style="margin:0; font-size:9.8px; color:#7F1D1D;">
          "१ल्या (लग्न) आणि ११व्या भावाचा उपस्वामी तपासा. जर तो ६, ८ किंवा १२ शी जोडलेला असेल, तर त्याचा रत्न घालणे <strong>पूर्णतः वर्ज्य</strong> करा, अन्यथा गंभीर रोग, कर्ज किंवा हानी संभवते. केवळ ६, ८, १२ पासून मुक्त असणारा ग्रहच रत्न म्हणून वापरावा."
        </p>
      </div>

      <h4 style="color:#166534; font-size:11.5px; margin:6px 0 4px 0;">✅ कुंडलीनुसार पूर्णतः स्वीकृत व कल्याणकारी रत्न (Scientifically Approved):</h4>
    """
    for ag in approved:
        p3_html += f"""
        <div style="background:#F0FDF4; border:1.3px solid #86EFAC; padding:8px 12px; border-radius:6px; margin-bottom:8px;">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">
            <span style="font-size:12px; font-weight:800; color:#14532D;">💎 {ag['gem_mr']} ({ag['gem_en']})</span>
            <span style="background:#DCFCE7; color:#15803D; padding:2px 8px; border-radius:12px; font-weight:700; font-size:9.5px;">{ag['source']}</span>
          </div>
          <div style="font-size:9.5px; color:#166534; line-height:1.45;">
            <strong>धातू:</strong> {ag['metal_mr']} | <strong>बोट:</strong> {ag['finger_mr']} | <strong>वजन:</strong> {ag['carat']} कॅरेट | <strong>रंग:</strong> {ag['color_mr']}
          </div>
          <div style="font-size:9px; color:#15803D; margin-top:3px;">
            <strong>मंत्र:</strong> {ag['mantra_mr']}
          </div>
          <div style="font-size:9.2px; color:#374151; margin-top:3px; background:#FFFFFF; padding:4px; border-radius:4px; border:1px solid #BBF7D0;">
            <strong>के.पी. वैज्ञानिक निष्कर्ष:</strong> {ag['reason_mr']}
          </div>
        </div>
        """

    if rejected:
        p3_html += f"""<h4 style="color:#B91C1C; font-size:11.5px; margin:8px 0 4px 0;">❌ कडक वर्ज्य व धोकादायक रत्न (Strictly Denied by KP Science):</h4>"""
        for rg in rejected:
            p3_html += f"""
            <div style="background:#FFF1F2; border:1.2px solid #FDA4AF; padding:8px 12px; border-radius:6px; margin-bottom:6px;">
              <div style="font-weight:700; color:#9F1239; font-size:11px;">
                🚫 {rg['gem_mr']} — {rg['source']}
              </div>
              <div style="font-size:9.2px; color:#BE123C; margin-top:2px;">
                <strong>धोका कारण:</strong> {rg['reason_mr']} (कार्येश भाव: {', '.join(map(str, rg['signified_houses']))})
              </div>
            </div>
            """
    p3_html += "</div>"
    pages.append({
        "title_en": "KP Reader III Gemstone Protocol & Strict Warnings",
        "title_hi": "के.पी. वैज्ञानिक रत्न निवड व वर्ज्य रत्न इशारा",
        "html": p3_html
    })

    # -------------------------------------------------------------------------
    # PAGE 4: KP MEDICAL ASTROLOGY: DISEASE & CURE (READER III)
    # -------------------------------------------------------------------------
    p4_html = f"""
    <div class="prose-block" style="font-size:10px; line-height:1.55;">
      <div style="background:#FFFBEB; border:1.5px solid #D97706; padding:10px; border-radius:8px; margin-bottom:12px;">
        <h3 style="color:#7C2D12; margin:0 0 4px 0; font-size:12.5px;">
          वैद्यकीय ज्योतिष: रोग निदान व शीघ्र रोगमुक्ती (KP Medical Astrology & Cure Window)
        </h3>
        <p style="margin:0; font-size:10px; color:#574032;">
          प्रो. कृष्णमूर्ति रीडर ३ (पृष्ठ २७८-२९५) नुसार १ल्या आणि ६व्या भावाचे कार्येश आजारपण आणतात, तर ५व्या (६व्यापासून १२वा - रोगनाशक) व ११व्या (६व्यापासून ६वा - आरोग्य पुनर्प्राप्ती) भावाचे कार्येश आजाराचे कायमस्वरूपी उच्चाटन करतात.
        </p>
      </div>

      <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px; margin-bottom:10px;">
        <div style="background:#FEF2F2; border:1.2px solid #FCA5A5; padding:8px 10px; border-radius:6px;">
          <h4 style="color:#991B1B; margin:0 0 4px 0; font-size:11px;">⚠️ रोगसूचक ग्रह (Disease Significators):</h4>
          <p style="font-size:9.5px; color:#7F1D1D; margin:0 0 4px 0;">
            १ व ६ व्या भावाशी संबंधित ग्रह: <strong>{', '.join(kp_disease.get('disease_significators', [])) or 'कोणताही तीव्र दोष नाही'}</strong>
          </p>
          <div style="font-size:9px; color:#991B1B;">
            या ग्रहांच्या अंतर्दशेत प्रकृती अस्वास्थ्य, थकवा किंवा संसर्ग संभवतो. वेळेवर वैद्यकीय तपासणी करावी.
          </div>
        </div>

        <div style="background:#F0FDF4; border:1.2px solid #86EFAC; padding:8px 10px; border-radius:6px;">
          <h4 style="color:#166534; margin:0 0 4px 0; font-size:11px;">🌿 रोगमुक्ती व आरोग्यदायी ग्रह (Cure Significators):</h4>
          <p style="font-size:9.5px; color:#14532D; margin:0 0 4px 0;">
            ५ व ११ व्या भावाशी संबंधित ग्रह: <strong>{', '.join(kp_disease.get('cure_significators', [])) or 'नैसर्गिक गुरु व शुक्र'}</strong>
          </p>
          <div style="font-size:9px; color:#15803D;">
            या ग्रहांच्या काळात योग्य औषधोपचार, शस्त्रक्रिया यश आणि उत्कृष्ट रोगप्रतिकारक शक्ती लाभते.
          </div>
        </div>
      </div>

      <div style="background:#F8FAFC; border:1px solid #CBD5E1; padding:8px 12px; border-radius:6px;">
        <div style="font-weight:700; color:#334155; margin-bottom:3px; font-size:10.5px;">आरोग्य संरक्षण वैदिक उपाय:</div>
        <ul style="margin:0; padding-left:18px; font-size:9.5px; color:#475569;">
          <li>दररोज सकाळी सूर्योदयावेळी १ तांब्या पाणी तांब्याच्या पात्रातून अर्घ्य देऊन <strong>आदित्य हृदय स्तोत्र</strong> म्हणावे.</li>
          <li>६व्या भावाच्या उपशमनासाठी महामृत्युंजय मंत्राचा १ माळ (१०८ जप) रुद्राक्ष माळेवर करावा.</li>
          <li>औषधे नेहमी अमृत वेळेत किंवा शुक्ल पक्षाच्या शुभ नक्षत्रात सुरू करावीत.</li>
        </ul>
      </div>
    </div>
    """
    pages.append({
        "title_en": "KP Medical Astrology: Disease Diagnosis & Cure Window",
        "title_hi": "के.पी. वैद्यकीय ज्योतिष: रोग निदान व शीघ्र मुक्ती",
        "html": p4_html
    })

    # -------------------------------------------------------------------------
    # PAGE 5: KP DEBTS, LOANS & REPAYMENT (READER III)
    # -------------------------------------------------------------------------
    p5_html = f"""
    <div class="prose-block" style="font-size:10px; line-height:1.55;">
      <div style="background:#EFF6FF; border:1.5px solid #3B82F6; padding:10px; border-radius:8px; margin-bottom:12px;">
        <h3 style="color:#1E40AF; margin:0 0 4px 0; font-size:12.5px;">
          कर्ज मुक्ती व वित्तीय स्वातंत्र्य (KP Debts Borrowing vs Repayment Analysis)
        </h3>
        <p style="margin:0; font-size:10px; color:#1E3A8A;">
          प्रो. कृष्णमूर्ति रीडर ३ (पृष्ठ २७६-२८९) चे सूत्र: २, ६, १०, ११ भाव एकत्र आल्यास कर्ज घेणे किंवा भांडवल उभारणी होते; तर ४, ५, ८, १२ भाव सक्रिय झाल्यास कर्जाची परतफेड होते.
        </p>
      </div>

      <div style="background:#FFFFFF; border:1.2px solid #E2E8F0; padding:10px; border-radius:6px; margin-bottom:10px;">
        <div style="font-size:11px; font-weight:800; color:#7C2D12; margin-bottom:6px;">
          📊 कुंडलीतील कर्ज व देणी गणितीय स्थिती:
        </div>
        <p style="font-size:10px; color:#334155; margin:0 0 6px 0;">
          <strong>कर्ज मुक्ती निष्कर्ष:</strong> {kp_debts.get('verdict_mr', 'कर्ज फेडण्याचे योग अनुकूल आहेत.')}
        </p>
        <p style="font-size:9.5px; color:#475569; margin:0 0 6px 0;">
          <strong>कर्ज परतफेड अनुकूल ग्रह:</strong> {', '.join(kp_debts.get('repay_planets', [])) or 'गुरु व चंद्र'}
        </p>
        <div style="background:#FEF3C7; padding:6px 10px; border-radius:4px; font-size:9.5px; color:#78350F;">
          <strong>शनि देव कर्ज परतफेड नियम:</strong> शनि ग्रहाचा प्रभाव असल्यास कर्ज एकाच वेळी न फिटता टप्प्याटप्प्याने (हप्त्यांमध्ये) फिटते. कर्ज फेडताना पहिली रक्कम मंगळवारी किंवा शनिवारी देणे टाळावे, नेहमी बुधवारी किंवा गुरुवारी द्यावी.
        </div>
      </div>

      <div style="background:#F0FDF4; border:1.2px solid #86EFAC; padding:9px 12px; border-radius:6px;">
        <div style="font-weight:800; color:#166534; font-size:10.5px; margin-bottom:4px;">ऋण मुक्तीसाठी विशेष शास्त्रीय तोडगे:</div>
        <ol style="margin:0; padding-left:18px; font-size:9.5px; color:#14532D; line-height:1.5;">
          <li>दर मंगळवारी <strong>ऋणमोचक मंगल स्तोत्र</strong> चे पठण करावे व हनुमानजींना गुळ-हरभऱ्याचा नैवेद्य दाखवावा.</li>
          <li>कर्जाचा पहिला हप्ता नेहमी शुक्ल पक्षाच्या मंगळवारी फेडण्यास सुरुवात करावी, यामुळे कर्ज लवकर संपुष्टात येते.</li>
          <li>घराच्या उत्तर-पूर्व (ईशान्य) दिशेत कोणतीही जड अडगळ किंवा कचरा ठेवू नये, तेथे पाण्याचे भांडे ठेवावे.</li>
        </ol>
      </div>
    </div>
    """
    pages.append({
        "title_en": "KP Debts & Loans Clearance Protocol (Reader III)",
        "title_hi": "के.पी. ऋण मुक्ती व कर्ज परतफेड शास्त्रीय विधान",
        "html": p5_html
    })

    # -------------------------------------------------------------------------
    # PAGE 6: 1 TO 14 MUKHI RUDRAKSHA THERAPY & KAVACH
    # -------------------------------------------------------------------------
    p6_html = f"""
    <div class="prose-block" style="font-size:10px; line-height:1.55;">
      <div style="background:#FFFBEB; border:1.5px solid #D97706; padding:10px; border-radius:8px; margin-bottom:12px;">
        <h3 style="color:#7C2D12; margin:0 0 4px 0; font-size:12.5px;">
          दिव्य रुद्राक्ष थेरपी व शिव कवच (1 to 14 Mukhi Rudraksha Selection)
        </h3>
        <p style="margin:0; font-size:10px; color:#574032;">
          रुद्राक्ष हे भगवान शंकराचे साक्षात अश्रू मानले जातात. हे धारण केल्याने रक्तदाब, मानसिक ताण आणि ग्रहांचे अनिष्ट प्रारब्ध शांत होते.
        </p>
      </div>

      <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px; margin-bottom:10px;">
        <div style="background:#FFF; border:1.2px solid #FED7AA; padding:8px 10px; border-radius:6px;">
          <div style="font-weight:800; color:#9A3412; font-size:11px; margin-bottom:3px;">
            📿 जातकासाठी मुख्य शिफारस रुद्राक्ष:
          </div>
          <div style="font-size:10px; color:#7C2D12; font-weight:700;">
            पंचमुखी (५ मुखी) व सातमुखी (७ मुखी) रुद्राक्ष कवच
          </div>
          <div style="font-size:9.2px; color:#475569; margin-top:3px;">
            पंचमुखी रुद्राक्ष बृहस्पतीचे (ज्ञान, संतती, धन) रक्षण करतो, तर सातमुखी रुद्राक्ष महालक्ष्मीचे प्रतीक असून आर्थिक संकटे दूर करतो.
          </div>
        </div>

        <div style="background:#FFF; border:1.2px solid #FED7AA; padding:8px 10px; border-radius:6px;">
          <div style="font-weight:800; color:#9A3412; font-size:11px; margin-bottom:3px;">
            🛡️ प्राण प्रतिष्ठा व धारण विधी:
          </div>
          <div style="font-size:9.2px; color:#475569; line-height:1.45;">
            सोमवारी सकाळी रुद्राक्ष कच्च्या दुधात व गंगाजलात धुवून <strong>"ॐ नमः शिवाय"</strong> या मंत्राचा १०८ वेळा जप करून लाल किंवा पिवळ्या धाग्यात, चांदीच्या तारेत गुंफून गळ्यात किंवा उजव्या मनगटावर धारण करावा.
          </div>
        </div>
      </div>

      <table class="data-table" style="width:100%; font-size:9px; border-collapse:collapse;">
        <thead>
          <tr style="background:#7C2D12; color:#FFF; text-align:center;">
            <th style="padding:4px; border:1px solid #D97706;">मुख</th>
            <th style="padding:4px; border:1px solid #D97706;">स्वामी ग्रह</th>
            <th style="padding:4px; border:1px solid #D97706;">देवता</th>
            <th style="padding:4px; border:1px solid #D97706;">विशेष फळ</th>
          </tr>
        </thead>
        <tbody>
          <tr><td style="font-weight:700; padding:3px; text-align:center;">१ मुखी</td><td>सूर्य</td><td>शिव</td><td>आत्मज्ञान, नेतृत्व, उच्च पद प्रतिष्ठा</td></tr>
          <tr style="background:#FEF9C3;"><td style="font-weight:700; padding:3px; text-align:center;">२ मुखी</td><td>चंद्र</td><td>अर्दधनारिश्वर</td><td>मानसिक शांती, वैवाहिक सौख्य</td></tr>
          <tr><td style="font-weight:700; padding:3px; text-align:center;">३ मुखी</td><td>मंगळ</td><td>अग्नी</td><td>आत्मविश्वास, आळस नाश, रक्त विकार मुक्ती</td></tr>
          <tr style="background:#FEF9C3;"><td style="font-weight:700; padding:3px; text-align:center;">४ मुखी</td><td>बुध</td><td>ब्रह्मा</td><td>बुद्धिमत्ता, शिक्षण, वक्तृत्व सिद्धी</td></tr>
          <tr><td style="font-weight:700; padding:3px; text-align:center;">५ मुखी</td><td>गुरु</td><td>कालाग्नी रुद्र</td><td>आरोग्य, दीर्घायुष्य, पापांचे क्षालन</td></tr>
          <tr style="background:#FEF9C3;"><td style="font-weight:700; padding:3px; text-align:center;">६ मुखी</td><td>शुक्र</td><td>कार्तिकेय</td><td>आकर्षण, कला, वाहन सुख, विजय</td></tr>
          <tr><td style="font-weight:700; padding:3px; text-align:center;">७ मुखी</td><td>शनि</td><td>महालक्ष्मी</td><td>दरिद्रता नाश, उद्योग-व्यवसायात यश</td></tr>
          <tr style="background:#FEF9C3;"><td style="font-weight:700; padding:3px; text-align:center;">८ मुखी</td><td>राहू</td><td>गणेश</td><td>विघ्नहर्ता, आकस्मिक संकटांपासून संरक्षण</td></tr>
        </tbody>
      </table>
    </div>
    """
    pages.append({
        "title_en": "Authentic Rudraksha Therapy & Kavach Prescription",
        "title_hi": "दिव्य रुद्राक्ष थेरपी व शिव कवच धारण विधी",
        "html": p6_html
    })

    # -------------------------------------------------------------------------
    # PAGE 7: SIDDHA YANTRA STHAPANA & WORSHIP
    # -------------------------------------------------------------------------
    p7_html = f"""
    <div class="prose-block" style="font-size:10px; line-height:1.55;">
      <div style="background:#FFFBEB; border:1.5px solid #D97706; padding:10px; border-radius:8px; margin-bottom:12px;">
        <h3 style="color:#7C2D12; margin:0 0 4px 0; font-size:12.5px;">
          सिद्ध यंत्र स्थापना, ऊर्जा समीकरण व नित्य पूजा (Siddha Yantra Science)
        </h3>
        <p style="margin:0; font-size:10px; color:#574032;">
          यंत्र हे देवतेचे दृश्य शरीर (Geometric Energy Grid) मानले जाते. कुंडलीतील कमजोर भावांना ताकद देण्यासाठी सिद्ध यंत्रांची स्थापना घरात किंवा देव्हाऱ्यात केली जाते.
        </p>
      </div>

      <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px; margin-bottom:10px;">
        <div style="background:#FFF; border:1.2px solid #E2E8F0; padding:8px 10px; border-radius:6px;">
          <h4 style="color:#7C2D12; margin:0 0 3px 0; font-size:11px;">⚜️ श्री संपूर्ण महालक्ष्मी यंत्र:</h4>
          <p style="font-size:9.2px; color:#475569; margin:0 0 4px 0;">
            स्थापना: शुक्रवार, शुक्ल पक्ष, देव्हाऱ्यात उत्तर किंवा पूर्व दिशेस तोंड करून ठेवावे. दररोज कमळाचे फूल किंवा अत्तर अर्पण करावे.
          </p>
          <div style="font-size:9px; color:#B45309; font-weight:700;">मंत्र: ॐ श्रीं ह्रीं श्रीं कमले कमलालये प्रसीद प्रसीद श्रीं ह्रीं श्रीं ॐ महालक्ष्म्यै नमः</div>
        </div>

        <div style="background:#FFF; border:1.2px solid #E2E8F0; padding:8px 10px; border-radius:6px;">
          <h4 style="color:#7C2D12; margin:0 0 3px 0; font-size:11px;">🪙 श्री कुबेर धनप्राप्ती यंत्र:</h4>
          <p style="font-size:9.2px; color:#475569; margin:0 0 4px 0;">
            स्थापना: उत्तर दिशेच्या भिंतीवर किंवा तिजोरीत/कॅश बॉक्समध्ये ठेवावे. व्यापार वाढीसाठी व अडकलेले पैसे मिळवण्यासाठी अत्यंत प्रभावी.
          </p>
          <div style="font-size:9px; color:#B45309; font-weight:700;">मंत्र: ॐ यक्षाय कुबेराय वैश्रवणाय धनधान्याधिपतये धनधान्यसमृद्धिं मे देहि दापय स्वाहा</div>
        </div>
      </div>

      <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px;">
        <div style="background:#FFF; border:1.2px solid #E2E8F0; padding:8px 10px; border-radius:6px;">
          <h4 style="color:#7C2D12; margin:0 0 3px 0; font-size:11px;">🛡️ श्री महामृत्युंजय आरोग्य यंत्र:</h4>
          <p style="font-size:9.2px; color:#475569; margin:0 0 4px 0;">
            दीर्घ आजार, भीती, अपघात आणि अकाल मृत्यूच्या धोक्यापासून रक्षण करते. सोमवारी दुधाने अभिषेक करावा.
          </p>
        </div>

        <div style="background:#FFF; border:1.2px solid #E2E8F0; padding:8px 10px; border-radius:6px;">
          <h4 style="color:#7C2D12; margin:0 0 3px 0; font-size:11px;">🪐 श्री नवग्रह शांती यंत्र:</h4>
          <p style="font-size:9.2px; color:#475569; margin:0 0 4px 0;">
            सर्व नऊ ग्रहांचे संतुलन साधते आणि घरात वास्तुदोष असल्यास सकारात्मक लहरींचा संचार करते.
          </p>
        </div>
      </div>
    </div>
    """
    pages.append({
        "title_en": "Siddha Yantra Science & Energization Guide",
        "title_hi": "सिद्ध यंत्र स्थापना, ऊर्जा समीकरण व नित्य पूजा",
        "html": p7_html
    })

    # -------------------------------------------------------------------------
    # PAGE 8: AYURVEDIC OSHADHI SNANA (HERBAL BATH)
    # -------------------------------------------------------------------------
    p8_html = f"""
    <div class="prose-block" style="font-size:10px; line-height:1.55;">
      <div style="background:#F0FDF4; border:1.5px solid #22C55E; padding:10px; border-radius:8px; margin-bottom:12px;">
        <h3 style="color:#15803D; margin:0 0 4px 0; font-size:12.5px;">
          नवग्रह औषधी स्नान चिकित्सा (Ayurvedic Planetary Herbal Bath Therapy)
        </h3>
        <p style="margin:0; font-size:10px; color:#14532D;">
          आयुर्वेद आणि पराशर संहितेनुसार शरीरावरील आभा (Aura) शुद्ध करण्यासाठी विशिष्ट वनस्पती व औषधीयुक्त पाण्याने स्नान केल्यास ग्रहांची नकारात्मक ऊर्जा त्वरित नष्ट होते.
        </p>
      </div>

      <table class="data-table" style="width:100%; font-size:9.2px; border-collapse:collapse; margin-bottom:10px;">
        <thead>
          <tr style="background:#15803D; color:#FFF; text-align:center;">
            <th style="padding:4px; border:1px solid #86EFAC;">ग्रह</th>
            <th style="padding:4px; border:1px solid #86EFAC;">स्नान वार</th>
            <th style="padding:4px; border:1px solid #86EFAC;">औषधी वनस्पती साहित्य</th>
            <th style="padding:4px; border:1px solid #86EFAC;">आरोग्य लाभ</th>
          </tr>
        </thead>
        <tbody>
          <tr><td style="font-weight:700; padding:4px;">सूर्य</td><td>रविवार</td><td>केशर, रक्तचंदन, खस, विलायची आणि कमळाचे पान</td><td>तेज, आत्मविश्वास, हाडांचे आरोग्य</td></tr>
          <tr style="background:#F0FDF4;"><td style="font-weight:700; padding:4px;">चंद्र</td><td>सोमवार</td><td>कच्च्या गायीचे दूध, पांढरे चंदन, शंखजल</td><td>मानसिक शांती, निद्रानाश मुक्ती</td></tr>
          <tr><td style="font-weight:700; padding:4px;">मंगळ</td><td>मंगळवार</td><td>लाल चंदन, बेलपत्र, जटामांसी आणि हिंगूळ</td><td>रक्तशुद्धी, धैर्य, भूमी लाभ</td></tr>
          <tr style="background:#F0FDF4;"><td style="font-weight:700; padding:4px;">बुध</td><td>बुधवार</td><td>गोरोचन, मध, आवळा पावडर, दूर्वा</td><td>त्वचा विकार मुक्ती, बुद्धी तीक्ष्णता</td></tr>
          <tr><td style="font-weight:700; padding:4px;">गुरु</td><td>गुरुवार</td><td>हळद, पिवळी मोहरी, मध आणि मुलेठी</td><td>भाग्य वृद्धी, ज्ञान, यकृत स्वास्थ्य</td></tr>
          <tr style="background:#F0FDF4;"><td style="font-weight:700; padding:4px;">शुक्र</td><td>शुक्रवार</td><td>वेलची, पांढरे फूल, जायफळ आणि कापूर</td><td>सौंदर्य, आकर्षण, वैवाहिक सुख</td></tr>
          <tr><td style="font-weight:700; padding:4px;">शनि</td><td>शनिवार</td><td>काळे तीळ, सुरमा, लोध्र, खस आणि शतावरी</td><td>वात रोग निवारण, दीर्घायुष्य</td></tr>
          <tr style="background:#F0FDF4;"><td style="font-weight:700; padding:4px;">राहू/केतू</td><td>शनि/मंगळ</td><td>नागरमोथा, लोबान, दर्भाचे पाणी, चंदन</td><td>भय मुक्ती, नजरदोष उच्चाटन</td></tr>
        </tbody>
      </table>

      <div style="background:#FFF; border:1px dashed #22C55E; padding:8px 10px; border-radius:6px; font-size:9.2px; color:#166534;">
        <strong>वापर विधी:</strong> वरील वनस्पतींचे चूर्ण आदल्या रात्री एका तांब्याच्या किंवा मातीच्या पात्रात भिजवून ठेवावे. दुसऱ्या दिवशी सकाळी ते गाळून स्नानाच्या पाण्यात मिसळावे आणि कुलदेवतेचे स्मरण करत स्नान करावे.
      </div>
    </div>
    """
    pages.append({
        "title_en": "Navagraha Ayurvedic Oshadhi Snana (Herbal Bath)",
        "title_hi": "नवग्रह औषधी स्नान चिकित्सा व आभा शुद्धी",
        "html": p8_html
    })

    # -------------------------------------------------------------------------
    # PAGE 9: LAL KITAB 1952 FARMAN TOTKE
    # -------------------------------------------------------------------------
    p9_html = f"""
    <div class="prose-block" style="font-size:10px; line-height:1.55;">
      <div style="background:#FFFBEB; border:1.5px solid #D97706; padding:10px; border-radius:8px; margin-bottom:12px;">
        <h3 style="color:#7C2D12; margin:0 0 4px 0; font-size:12.5px;">
          लाल किताब १९५२ फर्मान: अचूक व सात्विक तोडगे (Lal Kitab Remedial Farman)
        </h3>
        <p style="margin:0; font-size:10px; color:#574032;">
          लाल किताब ही कर्म-सुधारणेवर आधारित अत्यंत गतिमान विद्या आहे. यामध्ये कोणत्याही तांत्रिक किंवा घातक विधींऐवजी निसर्गाशी व प्राण्यांशी जोडलेले सात्विक उपाय सांगितले आहेत.
        </p>
      </div>

      <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px; margin-bottom:10px;">
        <div style="background:#FFF; border:1.2px solid #E2E8F0; padding:8px 10px; border-radius:6px;">
          <h4 style="color:#7C2D12; margin:0 0 3px 0; font-size:11px;">🕊️ पक्षी व प्राण्यांची सेवा:</h4>
          <ul style="margin:0; padding-left:16px; font-size:9.2px; color:#475569;">
            <li>दररोज सकाळी कावळ्यांना व मुंग्यांना गोड पोळी किंवा साखरेचे पीठ द्यावे (शनि व राहू शांती).</li>
            <li>गायीला दररोज पहिली पोळी गुळ किंवा हिरवे गवत घालून खाऊ घालावी (शुक्र व गुरु बळकट).</li>
            <li>माशांना कणकेचे गोळे नद्या किंवा तलावात टाकावेत (चंद्र व केतू प्रसन्न).</li>
          </ul>
        </div>

        <div style="background:#FFF; border:1.2px solid #E2E8F0; padding:8px 10px; border-radius:6px;">
          <h4 style="color:#7C2D12; margin:0 0 3px 0; font-size:11px;">🌊 जल प्रवाह विधी:</h4>
          <ul style="margin:0; padding-left:16px; font-size:9.2px; color:#475569;">
            <li>वाहत्या स्वच्छ पाण्यात जव किंवा गूळ प्रवाहित केल्याने अनिष्ट ग्रह शांत होतात.</li>
            <li>खोबऱ्याची वाटी (नारळ) वाहत्या पाण्यात सोडल्याने आकस्मिक संकटांचा नाश होतो.</li>
            <li>स्मशानातील पाणी किंवा तांब्याचे नाणे घरात ठेवण्याचे तोडगे तज्ज्ञ मार्गदर्शनाखालीच करावेत.</li>
          </ul>
        </div>
      </div>

      <div style="background:#FEF3C7; border:1px solid #D97706; padding:8px 10px; border-radius:6px; font-size:9.2px; color:#78350F;">
        <strong>लाल किताब सुवर्ण नियम:</strong> कोणतेही उपाय एका वेळी एकाच ग्रहासाठी करावेत. उपाय भर दुपारी सूर्य मावळण्यापूर्वी करावेत; रात्रीच्या वेळी लाल किताबचे उपाय वर्ज्य मानले आहेत.
      </div>
    </div>
    """
    pages.append({
        "title_en": "Lal Kitab 1952 Authentic Satvik Totke & Upay",
        "title_hi": "लाल किताब १९५२ फर्मान: अचूक व सात्विक तोडगे",
        "html": p9_html
    })

    # -------------------------------------------------------------------------
    # PAGE 10: RIN MUKTI TEVA (ANCESTRAL KARMIC DEBTS)
    # -------------------------------------------------------------------------
    p10_html = f"""
    <div class="prose-block" style="font-size:10px; line-height:1.55;">
      <div style="background:#FEF2F2; border:1.5px solid #EF4444; padding:10px; border-radius:8px; margin-bottom:12px;">
        <h3 style="color:#991B1B; margin:0 0 4px 0; font-size:12.5px;">
          ऋण मुक्ती टेवा: पूर्वजन्म संचित पितृ व कौटुंबिक ऋण (Ancestral Debt Clearance)
        </h3>
        <p style="margin:0; font-size:10px; color:#7F1D1D;">
          लाल किताब संहितेनुसार कुंडलीत पूर्वजांचे ऋण असल्यास संपूर्ण कुटुंबाच्या प्रगतीमध्ये अचानक खिळ बसते. हे ऋण ओळखून त्याचे निवारण करणे अनिवार्य असते.
        </p>
      </div>

      <table class="data-table" style="width:100%; font-size:9.2px; border-collapse:collapse; margin-bottom:10px;">
        <thead>
          <tr style="background:#991B1B; color:#FFF; text-align:center;">
            <th style="padding:4px; border:1px solid #F87171;">ऋण प्रकार</th>
            <th style="padding:4px; border:1px solid #F87171;">कारणीभूत ग्रह</th>
            <th style="padding:4px; border:1px solid #F87171;">जीवनावरील लक्षणे</th>
            <th style="padding:4px; border:1px solid #F87171;">शास्त्रीय प्रायश्चित्त उपाय</th>
          </tr>
        </thead>
        <tbody>
          <tr><td style="font-weight:700; padding:4px;">पितृ ऋण (Father's Debt)</td><td>बृहस्पती (गुरु)</td><td>केस गळणे, सोन्याची चोरी, मंदिरात अपमान</td><td>कुटुंबातील सर्वांकडून समप्रमाणात पैसे गोळा करून मंदिरात दान करावे.</td></tr>
          <tr style="background:#FFF1F2;"><td style="font-weight:700; padding:4px;">मातृ ऋण (Mother's Debt)</td><td>चंद्र</td><td>मानसिक अशांती, विहिरीचे पाणी सुकणे</td><td>नदीकाठी चांदीचे नाणे दान करावे व वृद्ध महिलांचे चरणस्पर्श करावे.</td></tr>
          <tr><td style="font-weight:700; padding:4px;">स्त्री ऋण (Spouse Debt)</td><td>शुक्र</td><td>घरात सतत भांडणे, संतती अडथळा</td><td>गाईला १०० दिवस सतत चारा घालावा व लक्ष्मी स्तोत्र म्हणावे.</td></tr>
          <tr style="background:#FFF1F2;"><td style="font-weight:700; padding:4px;">बंधू ऋण (Brother's Debt)</td><td>मंगळ</td><td>भावांमध्ये वैर, जमिनीचे वाद</td><td>गोरगरिबांना गोड भात किंवा लाडू वाटावेत.</td></tr>
        </tbody>
      </table>

      <div style="background:#FFFFFF; border:1px solid #CBD5E1; padding:8px 10px; border-radius:6px; font-size:9.2px; color:#334155;">
        <strong>पितृ शांती संकल्प:</strong> दर अमावस्येला काळे तीळ पाण्यात टाकून पितरांना तर्पण द्यावे व पिंपळाच्या झाडाला प्रदक्षिणा घालून दिवा लावावा.
      </div>
    </div>
    """
    pages.append({
        "title_en": "Ancestral Karmic Debt Clearance (Rin Mukti Teva)",
        "title_hi": "ऋण मुक्ती टेवा: पितृ व कौटुंबिक ऋण निवारण",
        "html": p10_html
    })

    # -------------------------------------------------------------------------
    # PAGE 11: NAVAGRAHA DAAN SAMAGRI & MUHURAT
    # -------------------------------------------------------------------------
    p11_html = f"""
    <div class="prose-block" style="font-size:10px; line-height:1.55;">
      <div style="background:#FFFBEB; border:1.5px solid #D97706; padding:10px; border-radius:8px; margin-bottom:12px;">
        <h3 style="color:#7C2D12; margin:0 0 4px 0; font-size:12.5px;">
          नवग्रह दान सामग्री, शुभ मुहूर्त व सत्पात्र व्यक्ती (Navagraha Daan Samagri)
        </h3>
        <p style="margin:0; font-size:10px; color:#574032;">
          दान नेहमी योग्य मुहूर्तावर आणि योग्य व्यक्तीला दिल्यासच त्याचे १००% पुण्य प्राप्त होते. ज्या ग्रहाचे दान केले जाते, त्या ग्रहाची नकारात्मक ऊर्जा शरीराबाहेर पडते.
        </p>
      </div>

      <table class="data-table" style="width:100%; font-size:9.2px; border-collapse:collapse; margin-bottom:10px;">
        <thead>
          <tr style="background:#7C2D12; color:#FFF; text-align:center;">
            <th style="padding:4px; border:1px solid #D97706;">ग्रह</th>
            <th style="padding:4px; border:1px solid #D97706;">दान सामग्री (वस्तू)</th>
            <th style="padding:4px; border:1px solid #D97706;">शुभ वार व वेळ</th>
            <th style="padding:4px; border:1px solid #D97706;">सत्पात्र व्यक्ती (Recipient)</th>
          </tr>
        </thead>
        <tbody>
          <tr><td style="font-weight:700; padding:4px;">सूर्य</td><td>गहू, गूळ, तांब्याचे भांडे, लाल वस्त्र, केशर</td><td>रविवार (दुपारी १२ पूर्वी)</td><td>विद्वान ब्राह्मण, गरजू वृद्ध व्यक्ती</td></tr>
          <tr style="background:#FEF9C3;"><td style="font-weight:700; padding:4px;">चंद्र</td><td>तांदूळ, दूध, पांढरे वस्त्र, शंख, चांदी</td><td>सोमवार (सायंकाळी)</td><td>माता, वृद्ध महिला, तीर्थस्थानी भिक्षुक</td></tr>
          <tr><td style="font-weight:700; padding:4px;">मंगळ</td><td>मसूर डाळ, लाल चंदन, गूळ, तांबे</td><td>मंगळवार (दुपारी)</td><td>ब्रह्मचारी, सैनिक, पोलीस, आचारी</td></tr>
          <tr style="background:#FEF9C3;"><td style="font-weight:700; padding:4px;">बुध</td><td>मूग डाळ, हिरवे वस्त्र, कास्य भांडे, पुस्तके</td><td>बुधवार (सकाळी)</td><td>विद्यार्थी, लहान कन्या, किन्नर</td></tr>
          <tr><td style="font-weight:700; padding:4px;">गुरु</td><td>हरभरा डाळ, हळद, पिवळे वस्त्र, पिवळी फळे</td><td>गुरुवार (सकाळी)</td><td>शिक्षक, पुरोहित, साधू-संत</td></tr>
          <tr style="background:#FEF9C3;"><td style="font-weight:700; padding:4px;">शुक्र</td><td>तूप, साखर, पांढरी फुले, कापूर, दही</td><td>शुक्रवार (सकाळी)</td><td>सुवासिनी महिला, दृष्टिहीन व्यक्ती</td></tr>
          <tr><td style="font-weight:700; padding:4px;">शनि</td><td>काळे उडीद, मोहरीचे तेल, लोखंड, काळे घोंगडे</td><td>शनिवार (संध्याकाळी)</td><td>कष्टकरी मजूर, अपंग व्यक्ती</td></tr>
        </tbody>
      </table>

      <div style="background:#F8FAFC; border:1px solid #CBD5E1; padding:8px 10px; border-radius:6px; font-size:9.2px; color:#475569;">
        <strong>दान संकल्प नियम:</strong> दानाची वस्तू उजव्या हातात पाणी घेऊन संकल्प सोडून अर्पण करावी आणि दानानंतर कोणताही अहंकार मनात ठेवू नये.
      </div>
    </div>
    """
    pages.append({
        "title_en": "Navagraha Charity & Donation Guidelines (Daan Samagri)",
        "title_hi": "नवग्रह दान सामग्री, शुभ मुहूर्त व सत्पात्र व्यक्ती",
        "html": p11_html
    })

    # -------------------------------------------------------------------------
    # PAGE 12: VEDIC & TANTRIK BEEJ MANTRAS
    # -------------------------------------------------------------------------
    p12_html = f"""
    <div class="prose-block" style="font-size:10px; line-height:1.55;">
      <div style="background:#FFFBEB; border:1.5px solid #D97706; padding:10px; border-radius:8px; margin-bottom:12px;">
        <h3 style="color:#7C2D12; margin:0 0 4px 0; font-size:12.5px;">
          वैदिक व तांत्रिक बीज मंत्र साधन (Vedic & Tantrik Planetary Mantras)
        </h3>
        <p style="margin:0; font-size:10px; color:#574032;">
          मंत्रांची स्पंदने थेट मेंदूतील चेतातंतूंना व ग्रहांच्या किरणांना संतुलित करतात. अचूक जप संख्या आणि योग्य माळेचा वापर केल्यासच मंत्र सिद्ध होतो.
        </p>
      </div>

      <table class="data-table" style="width:100%; font-size:9.2px; border-collapse:collapse; margin-bottom:10px;">
        <thead>
          <tr style="background:#7C2D12; color:#FFF; text-align:center;">
            <th style="padding:4px; border:1px solid #D97706;">ग्रह</th>
            <th style="padding:4px; border:1px solid #D97706;">तांत्रिक बीज मंत्र</th>
            <th style="padding:4px; border:1px solid #D97706;">एकूण जप संख्या</th>
            <th style="padding:4px; border:1px solid #D97706;">वापरण्याची माळ</th>
          </tr>
        </thead>
        <tbody>
          <tr><td style="font-weight:700; padding:4px;">सूर्य</td><td>ॐ ह्रां ह्रीं ह्रौं सः सूर्याय नमः</td><td>७,००० जप</td><td>रुद्राक्ष किंवा लाल चंदन</td></tr>
          <tr style="background:#FEF9C3;"><td style="font-weight:700; padding:4px;">चंद्र</td><td>ॐ श्रां श्रीं श्रौं सः चंद्राय नमः</td><td>११,००० जप</td><td>स्फटिक किंवा मोती माळ</td></tr>
          <tr><td style="font-weight:700; padding:4px;">मंगळ</td><td>ॐ क्रां क्रीं क्रौं सः भौमाय नमः</td><td>१०,००० जप</td><td>रक्तचंदन किंवा रुद्राक्ष</td></tr>
          <tr style="background:#FEF9C3;"><td style="font-weight:700; padding:4px;">बुध</td><td>ॐ ब्रां ब्रीं ब्रौं सः बुधाय नमः</td><td>९,००० जप</td><td>तुळशीची माळ</td></tr>
          <tr><td style="font-weight:700; padding:4px;">गुरु</td><td>ॐ ग्रां ग्रीं ग्रौं सः गुरवे नमः</td><td>१९,००० जप</td><td>हळदीची किंवा पिवळ्या चंदनाची माळ</td></tr>
          <tr style="background:#FEF9C3;"><td style="font-weight:700; padding:4px;">शुक्र</td><td>ॐ द्रां द्रीं द्रौं सः शुक्राय नमः</td><td>१६,००० जप</td><td>स्फटिक किंवा पांढऱ्या चंदनाची माळ</td></tr>
          <tr><td style="font-weight:700; padding:4px;">शनि</td><td>ॐ प्रां प्रीं प्रौं सः शनैश्चराय नमः</td><td>२३,००० जप</td><td>रुद्राक्ष किंवा निळी माळ</td></tr>
          <tr style="background:#FEF9C3;"><td style="font-weight:700; padding:4px;">राहू</td><td>ॐ भ्रां भ्रीं भ्रौं सः राहवे नमः</td><td>१८,००० जप</td><td>अष्टधातू किंवा चंदन माळ</td></tr>
          <tr><td style="font-weight:700; padding:4px;">केतू</td><td>ॐ स्त्रां स्त्रीं स्त्रौं सः केतवे नमः</td><td>१७,००० जप</td><td>अश्वत्थ किंवा रुद्राक्ष</td></tr>
        </tbody>
      </table>

      <div style="background:#F0FDF4; border:1px solid #86EFAC; padding:8px 10px; border-radius:6px; font-size:9.2px; color:#14532D;">
        <strong>जप विधी:</strong> दररोज पूर्व किंवा उत्तर दिशेला तोंड करून, शुद्ध लोकरीच्या किंवा कुशाच्या आसनावर बसून जप करावा. जप पूर्ण झाल्यावर दशांश हवन किंवा तर्पण करावे.
      </div>
    </div>
    """
    pages.append({
        "title_en": "Vedic & Tantrik Planetary Beej Mantras",
        "title_hi": "वैदिक व तांत्रिक बीज मंत्र साधन व जप विधी",
        "html": p12_html
    })

    # -------------------------------------------------------------------------
    # PAGE 13: SANKAT NASHAK STOTRA KAVACH
    # -------------------------------------------------------------------------
    p13_html = f"""
    <div class="prose-block" style="font-size:10px; line-height:1.55;">
      <div style="background:#FFFBEB; border:1.5px solid #D97706; padding:10px; border-radius:8px; margin-bottom:12px;">
        <h3 style="color:#7C2D12; margin:0 0 4px 0; font-size:12.5px;">
          नित्य पठण व संकट नाशक स्तोत्र कवच (Nitya Path & Protective Stotras)
        </h3>
        <p style="margin:0; font-size:10px; color:#574032;">
          स्तोत्रांचे गायन हे साक्षात देवाशी संवाद साधण्याचे माध्यम आहे. नियमित पठणाने घरात सकारात्मक लहरींचे अभेद्य कवच निर्माण होते.
        </p>
      </div>

      <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px; margin-bottom:10px;">
        <div style="background:#FFF; border:1.2px solid #E2E8F0; padding:8px 10px; border-radius:6px;">
          <h4 style="color:#7C2D12; margin:0 0 3px 0; font-size:11px;">☀️ श्री आदित्य हृदय स्तोत्र:</h4>
          <p style="font-size:9.2px; color:#475569; margin:0;">
            अगस्त्य ऋषींनी भगवान श्रीरामांना रावणावर विजय मिळवण्यासाठी हे स्तोत्र दिले होते. सरकारी नोकरी, उच्च पद आणि कोर्ट कचेरीच्या विजयासाठी दररोज पठण करावे.
          </p>
        </div>

        <div style="background:#FFF; border:1.2px solid #E2E8F0; padding:8px 10px; border-radius:6px;">
          <h4 style="color:#7C2D12; margin:0 0 3px 0; font-size:11px;">🔱 श्री संकट मोचन हनुमानाष्टक:</h4>
          <p style="font-size:9.2px; color:#475569; margin:0;">
            जीवनातील सर्व प्रकारच्या आकस्मिक संकटांवर, भीतीवर आणि शत्रूंच्या त्रासावर रामबाण उपाय. मंगळवारी आणि शनिवारी तीन वेळा म्हणावे.
          </p>
        </div>
      </div>

      <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px;">
        <div style="background:#FFF; border:1.2px solid #E2E8F0; padding:8px 10px; border-radius:6px;">
          <h4 style="color:#7C2D12; margin:0 0 3px 0; font-size:11px;">🪷 श्री कनकधारा व सूक्तम:</h4>
          <p style="font-size:9.2px; color:#475569; margin:0;">
            आदि शंकराचार्यांनी रचलेले कनकधारा स्तोत्र गरिबीचे समूळ उच्चाटन करून सोन्यासारखी समृद्धी आणि ऐश्वर्य खेचून आणते.
          </p>
        </div>

        <div style="background:#FFF; border:1.2px solid #E2E8F0; padding:8px 10px; border-radius:6px;">
          <h4 style="color:#7C2D12; margin:0 0 3px 0; font-size:11px;">🛡️ श्री विष्णु सहस्रनाम:</h4>
          <p style="font-size:9.2px; color:#475569; margin:0;">
            भगवान विष्णूंच्या १००० दिव्य नावांचे पठण कुंडलीतील सर्व ग्रहांचे दोष शांत करते आणि मनाला परमोच्च शांतता प्रदान करते.
          </p>
        </div>
      </div>
    </div>
    """
    pages.append({
        "title_en": "Nitya Path & Protective Stotra Kavach",
        "title_hi": "नित्य पठण व संकट नाशक स्तोत्र कवच",
        "html": p13_html
    })

    # -------------------------------------------------------------------------
    # PAGE 14: VASTU & DIRECTIONAL ENERGY BALANCING
    # -------------------------------------------------------------------------
    p14_html = f"""
    <div class="prose-block" style="font-size:10px; line-height:1.55;">
      <div style="background:#FFFBEB; border:1.5px solid #D97706; padding:10px; border-radius:8px; margin-bottom:12px;">
        <h3 style="color:#7C2D12; margin:0 0 4px 0; font-size:12.5px;">
          वास्तु शास्त्र व दिशा ऊर्जा संतुलन (Vastu & Directional Energy Balancing)
        </h3>
        <p style="margin:0; font-size:10px; color:#574032;">
          कुंडलीतील १२ भाव आणि घरातील ८ दिशा यांचा थेट संबंध असतो. घराची ऊर्जा संतुलित केल्यास कुंडलीतील कमजोर ग्रह आपोआप बळकट होतात.
        </p>
      </div>

      <table class="data-table" style="width:100%; font-size:9.2px; border-collapse:collapse; margin-bottom:10px;">
        <thead>
          <tr style="background:#7C2D12; color:#FFF; text-align:center;">
            <th style="padding:4px; border:1px solid #D97706;">दिशा (Direction)</th>
            <th style="padding:4px; border:1px solid #D97706;">दिशा स्वामी</th>
            <th style="padding:4px; border:1px solid #D97706;">घरातील आदर्श स्थान</th>
            <th style="padding:4px; border:1px solid #D97706;">वास्तुदोष निवारण तोडगा</th>
          </tr>
        </thead>
        <tbody>
          <tr><td style="font-weight:700; padding:4px;">ईशान्य (North-East)</td><td>बृहस्पती (गुरु)</td><td>देवघर, ध्यान कक्ष, पाण्याचे स्थान</td><td>येथे पिवळा दिवा लावावा, कचरा अजिबात ठेवू नये.</td></tr>
          <tr style="background:#FEF9C3;"><td style="font-weight:700; padding:4px;">पूर्व (East)</td><td>सूर्य देव</td><td>मुख्य प्रवेशद्वार, खिडक्या, लिव्हिंग रूम</td><td>तांब्याचा सूर्य लावावा, सकाळी सूर्यप्रकाश येऊ द्यावा.</td></tr>
          <tr><td style="font-weight:700; padding:4px;">आग्नेय (South-East)</td><td>शुक्र देव</td><td>स्वयंपाकघर (किचन), विद्युत उपकरणे</td><td>लाल रंगाचा दिवा लावावा, पाणी आणि अग्नी एकत्र ठेवू नये.</td></tr>
          <tr style="background:#FEF9C3;"><td style="font-weight:700; padding:4px;">दक्षिण (South)</td><td>मंगळ देव</td><td>बेडरूम, अवजड साहित्य</td><td>येथे लाल किंवा तपकिरी रंग वापरावा.</td></tr>
          <tr><td style="font-weight:700; padding:4px;">नैऋत्य (South-West)</td><td>राहू / पृथ्वी</td><td>मास्टर बेडरूम, तिजोरी</td><td>हे स्थान सर्वात उंच व जड असावे, येथे खड्डा नसावा.</td></tr>
          <tr style="background:#FEF9C3;"><td style="font-weight:700; padding:4px;">पश्चिम (West)</td><td>शनि देव</td><td>डायनिंग रूम, मुलांची खोली</td><td>येथे शनि यंत्र किंवा काळे घोड्याचे नाल लावावे.</td></tr>
          <tr><td style="font-weight:700; padding:4px;">वायव्य (North-West)</td><td>चंद्र देव</td><td>अतिथी कक्ष, धान्याचे कोठार</td><td>पांढरा रंग वापरावा, चांदीचे चौकोनी तुकडे ठेवावेत.</td></tr>
          <tr style="background:#FEF9C3;"><td style="font-weight:700; padding:4px;">उत्तर (North)</td><td>बुध / कुबेर</td><td>तिजोरी, कॅश बॉक्स, अभ्यास कक्ष</td><td>येथे हिरवी झाडे लावावीत व कुबेर यंत्र स्थापन करावे.</td></tr>
        </tbody>
      </table>

      <div style="background:#F0FDF4; border:1px solid #86EFAC; padding:8px 10px; border-radius:6px; font-size:9.2px; color:#14532D;">
        <strong>ब्रह्मस्थान सुरक्षा:</strong> घराचा मध्यभाग (Center) नेहमी मोकळा, स्वच्छ आणि प्रकाशमय असावा. येथे कोणताही खांब किंवा जड अडथळा नसावा.
      </div>
    </div>
    """
    pages.append({
        "title_en": "Vastu Shastra & Directional Energy Alignment",
        "title_hi": "वास्तु शास्त्र व दिशा ऊर्जा संतुलन विधान",
        "html": p14_html
    })

    # -------------------------------------------------------------------------
    # PAGE 15: VRATA (FASTING) & DIETARY CODES
    # -------------------------------------------------------------------------
    p15_html = f"""
    <div class="prose-block" style="font-size:10px; line-height:1.55;">
      <div style="background:#FFFBEB; border:1.5px solid #D97706; padding:10px; border-radius:8px; margin-bottom:12px;">
        <h3 style="color:#7C2D12; margin:0 0 4px 0; font-size:12.5px;">
          व्रत, उपवास संहिता व अन्न संस्कार (Vrata & Dietary Planetary Codes)
        </h3>
        <p style="margin:0; font-size:10px; color:#574032;">
          "जसे अन्न तसे मन" — उपवास केवळ पोटासाठी नसून ग्रहांच्या किरणोत्सर्गाला सात्विकरीत्या पचवण्याचे शारीरिक साधन आहे.
        </p>
      </div>

      <div style="display:grid; grid-template-columns:1fr 1fr; gap:10px; margin-bottom:10px;">
        <div style="background:#FFF; border:1.2px solid #E2E8F0; padding:8px 10px; border-radius:6px;">
          <h4 style="color:#7C2D12; margin:0 0 3px 0; font-size:11px;">🍛 जातकासाठी अनुकूल अन्नपदार्थ:</h4>
          <ul style="margin:0; padding-left:16px; font-size:9.2px; color:#475569;">
            <li>ताज्या अन्नाचा वापर करावा, शिळे अन्न राहू-शनिचा दोष वाढवते.</li>
            <li>भोजनात हळद, केशर आणि गायीच्या तुपाचा नियमित समावेश करावा (बृहस्पती पुष्टी).</li>
            <li>तांब्याच्या पात्रात साठवलेले पाणी पिणे सूर्याचे तेज वाढवते.</li>
          </ul>
        </div>

        <div style="background:#FFF; border:1.2px solid #E2E8F0; padding:8px 10px; border-radius:6px;">
          <h4 style="color:#7C2D12; margin:0 0 3px 0; font-size:11px;">🚫 वर्ज्य अन्नपदार्थ (Dietary Restrictions):</h4>
          <ul style="margin:0; padding-left:16px; font-size:9.2px; color:#475569;">
            <li>मद्यपान, मांसाहार आणि तंबाखूचे सेवन पूर्णतः टाळावे; यामुळे राहू व शनि तीव्र कुपित होतात.</li>
            <li>शनिवारी मीठ किंवा तेलाचे पदार्थ जास्त प्रमाणात खाणे टाळावे.</li>
            <li>अति आंबट किंवा जळजळीत पदार्थ मंगळाची उग्रता वाढवतात.</li>
          </ul>
        </div>
      </div>

      <div style="background:#FEF3C7; border:1px solid #D97706; padding:8px 10px; border-radius:6px; font-size:9.2px; color:#78350F;">
        <strong>एकादशी व्रत महत्त्व:</strong> महिन्यातील दोन्ही एकादशीचे व्रत केल्याने सर्व ग्रहांचे पाप शांत होते आणि शरीरातील विषारी घटक (Toxins) बाहेर पडून दीर्घायुष्य लाभते.
      </div>
    </div>
    """
    pages.append({
        "title_en": "Planetary Vrata, Fasting & Dietary Codes",
        "title_hi": "व्रत, उपवास संहिता व अन्न संस्कार विधान",
        "html": p15_html
    })

    return pages
