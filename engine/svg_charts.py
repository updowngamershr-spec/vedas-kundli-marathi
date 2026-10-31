# -*- coding: utf-8 -*-
"""
Gurukulam Kundli CRM - Royal Vedic North Indian SVG Chart Renderer
Renders:
1. Standard North Indian Diamond Kundli Chart (Lagna, Navamsha, 16 Shodashvarga, Karakamsa, Swamsa, Varshaphal, Lal Kitab)
2. KP System Chart (with Planet(Sign) notation)
3. Sarvashtakavarga Bindu Chart (with large bindu scores in each house)
4. Royal Gurukulam Cover Page Emblem & Ganesha Kundli SVG
Supports both English ('en') and Hindi ('hi') labels and Royal Gurukulam Gold/Maroon/Saffron palette.
"""

# Coordinates inside a 320x320 North Indian Diamond Chart:
# Outer square: (8, 8) to (312, 312), Center: (160, 160)
# Midpoints: Top(160, 8), Left(8, 160), Bottom(160, 312), Right(312, 160)
# Quarter intersections:
# TL(84, 84), BL(84, 236), BR(236, 236), TR(236, 84)

# Rashi number coordinates (x, y) for Houses 1 to 12 (anticlockwise)
HOUSE_SIGN_POS = {
    1:  (160, 138),  # Top center diamond (above center intersection)
    2:  (84,  66),   # Top-left triangle (above TL intersection)
    3:  (64,  88),   # Upper-left triangle (left of TL intersection)
    4:  (138, 164),  # Left center diamond (left of center intersection)
    5:  (64,  240),  # Lower-left triangle (left of BL intersection)
    6:  (84,  260),  # Bottom-left triangle (below BL intersection)
    7:  (160, 188),  # Bottom center diamond (below center intersection)
    8:  (236, 260),  # Bottom-right triangle (below BR intersection)
    9:  (256, 240),  # Lower-right triangle (right of BR intersection)
    10: (182, 164),  # Right center diamond (right of center intersection)
    11: (256, 88),   # Upper-right triangle (right of TR intersection)
    12: (236, 66),   # Top-right triangle (above TR intersection)
}

# Center bounding area (x_center, y_center, width_span, height_span) for planet text inside Houses 1 to 12
HOUSE_PLANET_CENTERS = {
    1:  (160, 74,  70, 48),
    2:  (84,  32,  76, 28),
    3:  (34,  84,  44, 56),
    4:  (78,  160, 68, 52),
    5:  (34,  236, 44, 56),
    6:  (84,  288, 76, 28),
    7:  (160, 248, 70, 48),
    8:  (236, 288, 76, 28),
    9:  (284, 236, 44, 56),
    10: (242, 160, 68, 52),
    11: (284, 84,  44, 56),
    12: (236, 32,  76, 28),
}

PLANET_COLORS = {
    "Su": "#B91C1C", "सू": "#B91C1C", "સૂ": "#B91C1C",
    "Mo": "#1D4ED8", "चं": "#1D4ED8", "ચં": "#1D4ED8",
    "Ma": "#C2410C", "मं": "#C2410C", "મં": "#C2410C",
    "Me": "#15803D", "बु": "#15803D", "બુ": "#15803D",
    "Ju": "#B45309", "गु": "#B45309", "ગુ": "#B45309",
    "Ve": "#7E22CE", "शु": "#7E22CE", "શુ": "#7E22CE",
    "Sa": "#1E293B", "श": "#1E293B", "શ": "#1E293B",
    "Ra": "#334155", "रा": "#334155", "રા": "#334155",
    "Ke": "#475569", "के": "#475569", "કે": "#475569",
    "Ur": "#0369A1", "अ": "#0369A1", "હ": "#0369A1",
    "Ne": "#0F766E", "व": "#0F766E", "ને": "#0F766E",
    "Pl": "#4338CA", "य": "#4338CA", "પ્લુ": "#4338CA",
}


def render_north_indian_svg(
    lagna_sign: int,
    house_planets: dict,
    lang: str = "en",
    title: str = "",
    size: int = 320,
    theme: str = "royal",
    is_kp: bool = False,
) -> str:
    """
    Render a crisp North Indian Diamond Kundli SVG string.
    `lagna_sign`: 1..12 (sign in House 1)
    `house_planets`: {1: [{"short_en": "Su", "short_hi": "सू", ...}], ..., 12: [...]}
    """
    bg_fill = "#FFFDF7" if theme == "royal" else "#FFFFFF"
    outer_stroke = "#7C2D12" if theme == "royal" else "#111827"
    inner_stroke = "#9A3412" if theme == "royal" else "#1F2937"
    sign_color = "#7C2D12" if theme == "royal" else "#374151"

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 320" width="{size}" height="{size}" class="kundli-svg">',
        f'  <rect x="4" y="4" width="312" height="312" fill="{bg_fill}" stroke="{outer_stroke}" stroke-width="2.2" rx="2"/>',
        f'  <rect x="8" y="8" width="304" height="304" fill="none" stroke="{inner_stroke}" stroke-width="1.3"/>',
        # Diagonals
        f'  <line x1="8" y1="8" x2="312" y2="312" stroke="{inner_stroke}" stroke-width="1.2"/>',
        f'  <line x1="312" y1="8" x2="8" y2="312" stroke="{inner_stroke}" stroke-width="1.2"/>',
        # Central Diamond
        f'  <polygon points="160,8 8,160 160,312 312,160" fill="none" stroke="{inner_stroke}" stroke-width="1.3"/>',
    ]

    # Draw Rashi numbers in each house
    for h in range(1, 13):
        sign_num = ((lagna_sign - 1 + h - 1) % 12) + 1
        sx, sy = HOUSE_SIGN_POS[h]
        svg.append(
            f'  <text x="{sx}" y="{sy}" text-anchor="middle" dominant-baseline="central" '
            f'font-family="Georgia, \'Noto Serif Devanagari\', serif" font-size="11.5" font-weight="600" fill="{sign_color}">{sign_num}</text>'
        )

        # Draw planets in house h
        p_list = house_planets.get(h, [])
        if not p_list:
            continue

        cx, cy, w_span, h_span = HOUSE_PLANET_CENTERS[h]
        labels = []
        for p in p_list:
            if is_kp:
                if lang in ("gu", "gujarati"):
                    from engine.gujarati_engine import to_gujarati
                    lbl = to_gujarati(p.get("label_hi") or p.get("label_en") or "")
                elif lang == "hi":
                    lbl = p.get("label_hi")
                else:
                    lbl = p.get("label_en")
            else:
                if lang in ("gu", "gujarati"):
                    from engine.gujarati_engine import to_gujarati
                    lbl = to_gujarati(p.get("short_hi") or p.get("short_en") or "")
                elif lang == "hi":
                    lbl = p.get("short_hi")
                else:
                    lbl = p.get("short_en")
            labels.append(lbl or "")

        n = len(labels)
        # Arrange neatly in rows of 2 or 3 so planets never overlap
        if n == 1:
            rows = [labels]
        elif n == 2:
            if h in (3, 5, 9, 11):
                rows = [[labels[0]], [labels[1]]]
            else:
                rows = [labels]
        elif n <= 4:
            if h in (3, 5, 9, 11):
                rows = [[l] for l in labels]
            else:
                rows = [labels[:2], labels[2:]]
        else:
            rows = [labels[i:i + 3] for i in range(0, n, 3)]

        row_count = len(rows)
        line_h = 14 if not is_kp else 12
        start_y = cy - ((row_count - 1) * line_h) / 2.0

        for r_idx, row_items in enumerate(rows):
            ry = start_y + r_idx * line_h
            col_count = len(row_items)
            col_step = 24 if not is_kp else 32
            if h in (3, 5, 9, 11):
                col_step = 18
            start_x = cx - ((col_count - 1) * col_step) / 2.0
            for c_idx, txt in enumerate(row_items):
                rx = start_x + c_idx * col_step
                base_key = txt.split("(")[0].strip()
                p_col = PLANET_COLORS.get(base_key, "#111827")
                f_size = "10.5" if is_kp else ("12" if n <= 3 else "10.5")
                svg.append(
                    f'  <text x="{rx:.1f}" y="{ry:.1f}" text-anchor="middle" dominant-baseline="central" '
                    f'font-family="\'Noto Sans Devanagari\', Georgia, serif" font-size="{f_size}" font-weight="700" fill="{p_col}">{txt}</text>'
                )

    svg.append("</svg>")
    return "\n".join(svg)


def render_ashtakavarga_svg(chart_houses: dict, size: int = 340, theme: str = "royal") -> str:
    """
    Render Sarvashtakavarga North Indian Chart with sign numbers and bold Bindu points in each house.
    Matches Page 54 of benchmark PDF.
    """
    bg_fill = "#FFFDF7" if theme == "royal" else "#FFFFFF"
    outer_stroke = "#7C2D12" if theme == "royal" else "#111827"
    inner_stroke = "#9A3412" if theme == "royal" else "#1F2937"

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 320" width="{size}" height="{size}" class="kundli-svg">',
        f'  <rect x="4" y="4" width="312" height="312" fill="{bg_fill}" stroke="{outer_stroke}" stroke-width="2.2" rx="2"/>',
        f'  <rect x="8" y="8" width="304" height="304" fill="none" stroke="{inner_stroke}" stroke-width="1.3"/>',
        f'  <line x1="8" y1="8" x2="312" y2="312" stroke="{inner_stroke}" stroke-width="1.2"/>',
        f'  <line x1="312" y1="8" x2="8" y2="312" stroke="{inner_stroke}" stroke-width="1.2"/>',
        f'  <polygon points="160,8 8,160 160,312 312,160" fill="none" stroke="{inner_stroke}" stroke-width="1.3"/>',
    ]

    for h in range(1, 13):
        info = chart_houses[h]
        sx, sy = HOUSE_SIGN_POS[h]
        cx, cy, _, _ = HOUSE_PLANET_CENTERS[h]
        pts = info["points"]
        pt_color = "#15803D" if pts >= 30 else ("#B91C1C" if pts < 25 else "#7C2D12")
        svg.append(
            f'  <text x="{sx}" y="{sy}" text-anchor="middle" dominant-baseline="central" '
            f'font-family="Georgia, serif" font-size="11.5" font-weight="600" fill="#4B5563">{info["sign_num"]}</text>'
        )
        svg.append(
            f'  <text x="{cx}" y="{cy}" text-anchor="middle" dominant-baseline="central" '
            f'font-family="Georgia, serif" font-size="16" font-weight="700" fill="{pt_color}">{pts}</text>'
        )

    svg.append("</svg>")
    return "\n".join(svg)


def render_gurukulam_cover_svg(lagna_sign: int, house_planets: dict) -> str:
    """
    Render the auspicious Gurukulam Cover Emblem with traditional Kundli Chakra,
    Swastika symbols, and sacred Sri Ganeshaya Namah crest.
    """
    return f"""
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 360 320" width="320" height="285">
  <defs>
    <radialGradient id="guruGlow" cx="50%" cy="50%" r="55%">
      <stop offset="0%" stop-color="#FEF08A"/>
      <stop offset="55%" stop-color="#FDE047" stop-opacity="0.65"/>
      <stop offset="100%" stop-color="#FFFBEB" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="goldGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#B45309"/>
      <stop offset="50%" stop-color="#D97706"/>
      <stop offset="100%" stop-color="#7C2D12"/>
    </linearGradient>
  </defs>
  <!-- Sacred Sunburst Halo -->
  <circle cx="180" cy="155" r="145" fill="url(#guruGlow)"/>
  <!-- Traditional North Indian Chart Backdrop -->
  <g transform="translate(50, 15) scale(0.8125)">
    <rect x="4" y="4" width="312" height="312" fill="#FFFBEB" fill-opacity="0.88" stroke="#7C2D12" stroke-width="2.5"/>
    <line x1="8" y1="8" x2="312" y2="312" stroke="#9A3412" stroke-width="1.4"/>
    <line x1="312" y1="8" x2="8" y2="312" stroke="#9A3412" stroke-width="1.4"/>
    <polygon points="160,8 8,160 160,312 312,160" fill="#FEF3C7" fill-opacity="0.55" stroke="#9A3412" stroke-width="1.6"/>
    <text x="160" y="62" text-anchor="middle" font-size="22" fill="#DC2626" font-weight="bold">卐</text>
    <text x="72" y="162" text-anchor="middle" font-size="22" fill="#DC2626" font-weight="bold">卐</text>
    <text x="248" y="162" text-anchor="middle" font-size="22" fill="#DC2626" font-weight="bold">卐</text>
    <text x="160" y="262" text-anchor="middle" font-size="22" fill="#DC2626" font-weight="bold">卐</text>
  </g>
  <!-- Central Sacred Lotus & Om Shri Ganeshaya Medallion -->
  <circle cx="180" cy="155" r="64" fill="#7C2D12" stroke="#F59E0B" stroke-width="3.5"/>
  <circle cx="180" cy="155" r="56" fill="#991B1B" stroke="#FDE047" stroke-width="1.5" stroke-dasharray="4,3"/>
  <text x="180" y="146" text-anchor="middle" font-family="'Noto Serif Devanagari', Georgia, serif" font-size="42" font-weight="bold" fill="#FEF08A">ॐ</text>
  <text x="180" y="178" text-anchor="middle" font-family="'Noto Serif Devanagari', Georgia, serif" font-size="13" font-weight="bold" fill="#FDE68A">श्री गणेशाय नमः</text>
  <text x="180" y="196" text-anchor="middle" font-family="Georgia, serif" font-size="9.5" letter-spacing="1.5" fill="#FED7AA">GURUKULAM JYOTISH</text>
</svg>
"""


def render_south_indian_svg(lagna_sign: int, house_planets: dict, size: int = 320, lang: str = "en") -> str:
    """
    Render classical South Indian Vedic Chart (4x4 outer ring with fixed signs clockwise).
    Pisces(12), Aries(1), Taurus(2), Gemini(3) on top row;
    Cancer(4), Leo(5) on right column;
    Virgo(6), Libra(7), Scorpio(8), Sagittarius(9) on bottom row;
    Capricorn(10), Aquarius(11) on left column.
    Lagna is marked with 'ASC' / 'लग्न' diagonal cross or banner.
    """
    # Sign index (1..12) to grid cell (col 0..3, row 0..3)
    SOUTH_SIGN_CELLS = {
        12: (0, 0), 1: (1, 0), 2: (2, 0), 3: (3, 0),
        11: (0, 1),                        4: (3, 1),
        10: (0, 2),                        5: (3, 2),
        9:  (0, 3), 8: (1, 3), 7: (2, 3), 6: (3, 3)
    }
    
    cell_w = size / 4.0
    cell_h = size / 4.0
    
    # Map house planets (house 1..12) to sign numbers
    sign_planets = {s: [] for s in range(1, 13)}
    for h, p_list in house_planets.items():
        s_num = ((lagna_sign - 1 + (h - 1)) % 12) + 1
        sign_planets[s_num].extend(p_list)

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" width="{size}" height="{size}">',
        '  <rect x="2" y="2" width="' + str(size-4) + '" height="' + str(size-4) + '" fill="#FFFDF8" stroke="#7C2D12" stroke-width="2.5"/>',
        f'  <rect x="{cell_w}" y="{cell_h}" width="{cell_w*2}" height="{cell_h*2}" fill="#FEF3C7" fill-opacity="0.65" stroke="#7C2D12" stroke-width="1.5"/>',
        f'  <text x="{size/2}" y="{size/2 - 6}" text-anchor="middle" font-family="Cinzel, Georgia, serif" font-size="12" font-weight="bold" fill="#7C2D12">VEDAS KUNDLI</text>',
        f'  <text x="{size/2}" y="{size/2 + 10}" text-anchor="middle" font-family="sans-serif" font-size="9.5" fill="#B45309">South Indian Style</text>',
    ]
    
    # Draw grid lines
    for i in range(1, 4):
        x = i * cell_w
        svg.append(f'  <line x1="{x}" y1="0" x2="{x}" y2="{cell_h}" stroke="#9A3412" stroke-width="1.2"/>')
        svg.append(f'  <line x1="{x}" y1="{cell_h*3}" x2="{x}" y2="{size}" stroke="#9A3412" stroke-width="1.2"/>')
        y = i * cell_h
        svg.append(f'  <line x1="0" y1="{y}" x2="{cell_w}" y2="{y}" stroke="#9A3412" stroke-width="1.2"/>')
        svg.append(f'  <line x1="{cell_w*3}" y1="{y}" x2="{size}" y2="{y}" stroke="#9A3412" stroke-width="1.2"/>')

    # Draw contents for each sign
    for s_num, (col, row) in SOUTH_SIGN_CELLS.items():
        x0 = col * cell_w
        y0 = row * cell_h
        is_lagna = (s_num == lagna_sign)
        if is_lagna:
            svg.append(f'  <line x1="{x0}" y1="{y0}" x2="{x0+cell_w}" y2="{y0+cell_h}" stroke="#DC2626" stroke-width="1.8" stroke-dasharray="3,2"/>')
            asc_lbl = "लग्न (ASC)" if lang == "hi" else "ASC"
            svg.append(f'  <text x="{x0+4}" y="{y0+12}" font-size="9" font-weight="bold" fill="#DC2626">{asc_lbl}</text>')

        # Sign label in small gold
        from engine.ephemeris import RASHI_NAMES_HI, RASHI_SHORT_EN
        sign_txt = RASHI_NAMES_HI[s_num-1] if lang == "hi" else RASHI_SHORT_EN[s_num-1]
        svg.append(f'  <text x="{x0+cell_w-3}" y="{y0+10}" text-anchor="end" font-size="7.5" fill="#B45309">{sign_txt}</text>')

        # Planets inside this sign
        p_list = sign_planets[s_num]
        if p_list:
            py = y0 + 22
            p_names = []
            for p in p_list:
                if isinstance(p, dict):
                    lbl = p.get("short_hi" if lang == "hi" else "short_en") or p.get("id", "")
                else:
                    lbl = str(p)
                p_names.append(lbl)
            p_str = " ".join(p_names)
            svg.append(f'  <text x="{x0+cell_w/2}" y="{py}" text-anchor="middle" font-family="sans-serif" font-size="9.5" font-weight="700" fill="#7C2D12">{p_str}</text>')

    svg.append('</svg>')
    return "\n".join(svg)


def render_east_indian_svg(lagna_sign: int, house_planets: dict, size: int = 320, lang: str = "en") -> str:
    """
    Render classical East Indian (Bengali / Odia / Assamese) Chart.
    Signs are FIXED in traditional anti-clockwise arrangement:
    Aries(1) is top diamond, Taurus(2) top-left, Gemini(3) left-top, Cancer(4) left diamond, etc.
    Lagna is marked in whichever sign box corresponds to lagna_sign.
    """
    from engine.ephemeris import RASHI_NAMES_HI, RASHI_SHORT_EN
    scale = size / 320.0
    
    # Map house planets (house 1..12) to sign numbers
    sign_planets = {s: [] for s in range(1, 13)}
    for h, p_list in house_planets.items():
        s_num = ((lagna_sign - 1 + (int(h) - 1)) % 12) + 1
        sign_planets[s_num].extend(p_list)

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 320" width="{size}" height="{size}" class="kundli-svg">',
        '  <rect x="4" y="4" width="312" height="312" fill="#FFFDF7" stroke="#7C2D12" stroke-width="2.2" rx="2"/>',
        '  <rect x="8" y="8" width="304" height="304" fill="none" stroke="#9A3412" stroke-width="1.3"/>',
        '  <line x1="8" y1="8" x2="312" y2="312" stroke="#9A3412" stroke-width="1.2"/>',
        '  <line x1="312" y1="8" x2="8" y2="312" stroke="#9A3412" stroke-width="1.2"/>',
        '  <polygon points="160,8 8,160 160,312 312,160" fill="none" stroke="#9A3412" stroke-width="1.3"/>',
    ]

    # Draw fixed Rashi numbers (1..12) and their planets
    for s_num in range(1, 13):
        sx, sy = HOUSE_SIGN_POS[s_num]
        s_txt = str(s_num)
        is_lagna = (s_num == lagna_sign)
        if is_lagna:
            lbl = "लग्न" if lang == "hi" else "ASC"
            svg.append(f'  <text x="{sx}" y="{sy}" text-anchor="middle" dominant-baseline="central" font-family="sans-serif" font-size="10.5" font-weight="bold" fill="#DC2626">{lbl} ({s_txt})</text>')
        else:
            svg.append(f'  <text x="{sx}" y="{sy}" text-anchor="middle" dominant-baseline="central" font-family="Georgia, serif" font-size="11" font-weight="600" fill="#B45309">{s_txt}</text>')

        p_list = sign_planets[s_num]
        if not p_list:
            continue

        cx, cy, _, _ = HOUSE_PLANET_CENTERS[s_num]
        labels = []
        for p in p_list:
            if isinstance(p, dict):
                lbl = p.get("short_hi" if lang == "hi" else "short_en") or p.get("id", "")
            else:
                lbl = str(p)
            labels.append(lbl)

        p_str = " ".join(labels)
        svg.append(f'  <text x="{cx}" y="{cy}" text-anchor="middle" dominant-baseline="central" font-family="sans-serif" font-size="10" font-weight="bold" fill="#7C2D12">{p_str}</text>')

    svg.append('</svg>')
    return "\n".join(svg)

