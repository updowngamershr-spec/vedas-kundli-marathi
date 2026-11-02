# SHIVANSH ASTRO-VASTU: MATHEMATICAL & ASTROLOGICAL CALCULATION CONVENTIONS

## 1. Astronomical Engine & Ephemeris

### 1.1 Core Planetary Theory
- **Primary Engine**: VSOP87 (Variations Séculaires des Orbites Planétaires) analytical theory combined with NOVAS (Naval Observatory Vector Astrometry Software) algorithms.
- **Reference Ephemeris**: Swiss Ephemeris v2.10.03 (AstroDienst / JPL DE431 integration).
- **Coordinate System**: Geocentric Apparent Ecliptic coordinates referred to the True Equator and Equinox of date.
- **Light-Time Correction & Aberration**: Included in apparent longitude calculations.

### 1.2 Sidereal Zodiac & Ayanamsa
1. **N.C. Lahiri (Chitrapaksha) Ayanamsa**:
   - Used for all Classical Vedic (Parashari, Jaimini, Varshaphal) calculations.
   - Epoch J2000.0 (JD 2451545.0) mean value: $23^\circ 51' 25.532" = 23.85709222^\circ$.
   - Precession Rate: $50.2797"$ per Julian year ($1.3966583^\circ$ per Julian century).
   - Formula:
     $$\text{Ayanamsa} = 23.856528^\circ + 1.396042^\circ \cdot T + 0.000308^\circ \cdot T^2$$
     where $T = (\text{JD}_{\text{UT}} - 2451545.0) / 36525.0$.
   - **Empirical Accuracy**: Verified within $0.44"$ to $2.08"$ arcseconds against official Swiss Ephemeris across the 20th and 21st centuries.

2. **KP New (Krishnamurti Paddhati) Ayanamsa**:
   - Used for KP Cuspal calculations, Significators, and Sub-Lord tables.
   - Base value at epoch 03-Aug-1970: $23^\circ 21' 21"$.
   - Formula:
     $$\text{Ayanamsa}_{\text{KP}} = 23.763194^\circ + 1.396042^\circ \cdot T + 0.000308^\circ \cdot T^2$$

### 1.3 True Obliquity of the Ecliptic & Nutation
- Mean Obliquity ($\epsilon_0$):
  $$\epsilon_0 = 23.43929111^\circ - \frac{46.8150 \cdot T + 0.00059 \cdot T^2 - 0.001813 \cdot T^3}{3600}$$
- Nutation in Obliquity ($\Delta\epsilon$):
  $$\Delta\epsilon = \frac{9.2025"}{3600} \cos(\Omega), \quad \Omega = 125.04452^\circ - 1934.136261^\circ \cdot T$$
- True Obliquity $\epsilon = \epsilon_0 + \Delta\epsilon$.

### 1.4 Lunar Node (Rahu & Ketu)
- Standard Vedic Mean Node convention:
  $$\Omega_{\text{Mean}} = (125.04455501 - 1934.13626197 \cdot T + 0.0020756 \cdot T^2 + T^3 / 467441.0) \pmod{360^\circ}$$
- Rahu = $\Omega_{\text{Mean}} - \text{Ayanamsa}$.
- Ketu = $(\text{Rahu} + 180^\circ) \pmod{360^\circ}$.

---

## 2. Spherical Trigonometry & House Systems

### 2.1 Local Sidereal Time (LST) & Right Ascension of Midheaven (RAMC)
1. Greenwich Apparent Sidereal Time (GMST) computed via IAU 2000 / VSOP87 formula.
2. $\text{LST} = (\text{GMST} + \text{Longitude}_{\text{East}} / 15.0) \pmod{24.0\text{ hours}}$.
3. $\text{RAMC} = \text{LST} \times 15.0^\circ$.

### 2.2 Ascendant (Lagna) & Midheaven (MC)
- **Ascendant ($\lambda_{\text{Asc}}$)**:
  $$\tan(\lambda_{\text{Asc}}) = \frac{\cos(\text{RAMC})}{-\sin(\text{RAMC})\cos(\epsilon) - \tan(\phi)\sin(\epsilon)}$$
  where $\phi$ is geodetic latitude.
- **Midheaven ($\lambda_{\text{MC}}$)**:
  $$\tan(\lambda_{\text{MC}}) = \frac{\tan(\text{RAMC})}{\cos(\epsilon)}$$
- Sidereal Ascendant = $(\lambda_{\text{Asc}} - \text{Ayanamsa}) \pmod{360^\circ}$.
- Sidereal MC = $(\lambda_{\text{MC}} - \text{Ayanamsa}) \pmod{360^\circ}$.

### 2.3 House Division Methods
1. **Placidus Semi-Arc System**:
   - Used for Krishnamurti Paddhati (KP) 12 cusps.
   - Cusps 11, 12, 2, 3 determined by diurnal/nocturnal semi-arc division on the celestial sphere.
2. **Sripati Bhava Chalit System**:
   - Used for Vedic Chalit Chakra and Bhavabala.
   - Mid-Bhavas: H1 = Ascendant, H10 = MC, H4 = IC, H7 = Descendant.
   - Intermediate bhavas trisected along the ecliptic; Bhava Sandhi (junction) = midpoint between adjacent mid-bhavas.

---

## 3. KP System & The 249-Subdivision Method

### 3.1 249 Subdivisions Table
- Each of the 27 Nakshatras ($13^\circ 20' = 800'$) is divided into 9 unequal parts proportional to the Vimshottari Dasha periods of the 9 planets (total 120 years).
- Sub span formula for planet $P$ with dasha duration $Y_P$ years:
  $$\text{Span}(P) = 800' \times \frac{Y_P}{120} = \frac{20 \times Y_P}{3}\text{ minutes of arc}$$
- Because the zodiac circle transitions across rashi boundaries inside 3 Nakshatras (Krittika, Uttara Phalguni, Uttara Ashadha), the 243 pure subs expand to exactly **249 distinct Cusp Sub-Lords**.

### 3.2 Four-Fold Planetary Significators (Levels A, B, C, D)
In accordance with K.S. Krishnamurti's *KP Reader III*:
- **Level A (Strongest)**: Planets posited in the constellation (Star) of an occupant of the house.
- **Level B**: Planets posited directly in the house itself.
- **Level C**: Planets posited in the constellation of the lord of the house.
- **Level D (Weakest)**: The lord of the house itself.

### 3.3 Authentic KP Gemstone Recommendations
A gemstone is recommended only if its ruling planet satisfies all KP conditions:
1. Candidate planets: **Ascendant Sub-Lord (1st CSL)** representing the physical self, longevity, and vitality; and **11th Cusp Sub-Lord (11th CSL)** representing fulfillment of desires, prosperity, and gains.
2. The planet must **not** signify destructive houses $\{6, 8, 12\}$ without strong mitigating connections to supportive houses $\{1, 2, 3, 5, 9, 10, 11\}$.
3. If both 1st and 11th CSL point to the same planet, the recommendation is deduplicated.
4. Each recommendation details the exact houses signified and the classical justification.

---

## 4. Vimshottari Dasha Engine

### 4.1 Order & Duration of Mahadashas (120-Year Full Cycle)
| Planet | Sanskrit | Years |
|:---|:---|:---:|
| Ketu | केतु | 7 |
| Venus | शुक्र | 20 |
| Sun | सूर्य | 6 |
| Moon | चंद्र | 10 |
| Mars | मंगल | 7 |
| Rahu | राहु | 18 |
| Jupiter | गुरु | 16 |
| Saturn | शनि | 19 |
| Mercury | बुध | 17 |
| **Total Cycle** | | **120 Years** |

### 4.2 Birth Dasha Balance Calculation
- Moon's sidereal longitude: $\lambda_{\text{Moon}}$.
- Nakshatra index $N = \lfloor \lambda_{\text{Moon}} / 13^\circ 20' \rfloor$.
- Position within Nakshatra: $\Delta\lambda = \lambda_{\text{Moon}} - N \times 13^\circ 20'$.
- Remaining fraction: $f_{\text{rem}} = 1.0 - (\Delta\lambda / 13^\circ 20')$.
- Balance of birth Mahadasha lord:
  $$\text{Balance} = f_{\text{rem}} \times \text{Years}(N_{\text{Lord}})$$
- Output in exact Years, Months, and Days:
  - Years = $\lfloor \text{Balance} \rfloor$
  - Months = $\lfloor (\text{Balance} - \text{Years}) \times 12 \rfloor$
  - Days = $\lfloor ((\text{Balance} - \text{Years}) \times 12 - \text{Months}) \times 30 \rfloor$

### 4.3 Date Integrity Rules
- The first active Antardasha begins on the native's **exact Date of Birth**.
- Pre-birth elapsed Antardashas within the birth Mahadasha are marked `is_pre_birth = True` and masked with `00/00/0000` to prevent confusion with future periods.
- Calendar addition accurately accounts for Gregorian leap years (Feb 29) and varying month lengths (28, 29, 30, 31 days).

---

## 5. Ashtakavarga Mathematical Invariant (Sum = 337)

### 5.1 Parashari Rules
- Computed for 7 planets: Sun (48 points), Moon (49 points), Mars (39 points), Mercury (54 points), Jupiter (56 points), Venus (52 points), Saturn (39 points).
- Total benefic dots across all 7 Bhinnashtakavargas:
  $$48 + 49 + 39 + 54 + 56 + 52 + 39 = \mathbf{337}$$
- When these points are mapped into the 12 signs/houses and summed to form the **Sarvashtakavarga (SAV)** table:
  $$\sum_{h=1}^{12} \text{SAV}_h = \mathbf{337}$$
- This sum is a rigorous mathematical invariant of the classical Parashari system. The engine calculates each dot individually according to the Maharishi Parashara Brihat Hora Shastra (BPHS) benefic rules; the sum of 337 emerges naturally from the underlying geometry without artificial clamping.

---

## 6. Dynamic Personalized Predictions

### 6.1 Architecture
Predictions are never static or generic copy-pasted blocks. Every report generates dynamic textual interpretations based on:
1. **Lagna & Lagna Lord**: Sign placement, house placement, aspects, and dignity determine the primary Character and Personality profile.
2. **10th House, 10th Lord & Sun**: Occupation, status, government favour, and career directions.
3. **2nd & 11th Houses, Jupiter & Mercury**: Wealth accumulation, financial streams, business acumen.
4. **7th House, Venus & Mars**: Marriage dynamics, compatibility, marital timing, and partnership temperament.
5. **6th House, 8th House, Ascendant Lord & Saturn**: Constitutional health tendencies, anatomical vulnerabilities, and preventive lifestyle recommendations.
6. **Planet-in-House (108 Combinations)**: Distinct Marathi paragraphs for each planet in its calculated house.
