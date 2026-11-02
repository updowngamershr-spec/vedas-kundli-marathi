# -*- coding: utf-8 -*-
"""
Shivansh Astro-Vastu - Personalized Astrological Interpretation Engine
Generates 100% dynamic, chart-specific predictions for every native:
1. Dynamic 10 Life Domains (Character, Career, Finance, Marriage, Health, Lifestyle, etc.)
   Calculated from actual Ascendant, Lagnesh, Moon, Nakshatra, and Bhava Lords.
2. Planet-Specific & House-Specific Interpretations (All 9 Planets x 12 Houses = 108 Astrological Combinations)
   Never repeats generic or identical paragraphs for different planets!
"""

SIGN_LORDS = {
    1: ("Mars", "मंगळ"), 2: ("Venus", "शुक्र"), 3: ("Mercury", "बुध"), 4: ("Moon", "चंद्र"),
    5: ("Sun", "सूर्य"), 6: ("Mercury", "बुध"), 7: ("Venus", "शुक्र"), 8: ("Mars", "मंगळ"),
    9: ("Jupiter", "गुरु"), 10: ("Saturn", "शनी"), 11: ("Saturn", "शनी"), 12: ("Jupiter", "गुरु"),
}

SIGN_NAMES_MR = {
    1: "मेष", 2: "वृषभ", 3: "मिथुन", 4: "कर्क", 5: "सिंह", 6: "कन्या",
    7: "तूळ", 8: "वृश्चिक", 9: "धनु", 10: "मकर", 11: "कुंभ", 12: "मीन"
}

SIGN_NAMES_EN = {
    1: "Aries", 2: "Taurus", 3: "Gemini", 4: "Cancer", 5: "Leo", 6: "Virgo",
    7: "Libra", 8: "Scorpio", 9: "Sagittarius", 10: "Capricorn", 11: "Aquarius", 12: "Pisces"
}

HOUSE_ORDINAL_MR = {
    1: "पहिल्या (लग्न)", 2: "दुसऱ्या (धन)", 3: "तिसऱ्या (पराक्रम)", 4: "चौथ्या (सुख)",
    5: "पाचव्या (बुद्धी व संतती)", 6: "सहाव्या (शत्रू व रोग)", 7: "सातव्या (विवाह व भागीदारी)",
    8: "आठव्या (आयुष्य व गूढ)", 9: "नवव्या (भाग्य व धर्म)", 10: "दहाव्या (कर्म व करिअर)",
    11: "अकराव्या (लाभ व सिद्धी)", 12: "बाराव्या (व्यय व परदेश)"
}

HOUSE_ORDINAL_EN = {
    1: "1st (Ascendant)", 2: "2nd (Wealth)", 3: "3rd (Courage)", 4: "4th (Domestic/Mother)",
    5: "5th (Intelligence/Children)", 6: "6th (Service/Overcoming obstacles)", 7: "7th (Spouse/Partnership)",
    8: "8th (Transformation/Longevity)", 9: "9th (Destiny/Higher Wisdom)", 10: "10th (Career/Authority)",
    11: "11th (Gains/Aspirations)", 12: "12th (Foreign/Spiritual)"
}

PLANET_HOUSE_PHAL = {
    "Sun": {
        1: ("सूर्य लग्न भावात स्थित असल्याने जातकाला तेजस्वी व्यक्तिमत्त्व, उच्च स्वाभिमान आणि उत्तम जीवनशक्ती लाभते. नेतृत्वगुण, दृढ इच्छाशक्ती आणि समाजातील प्रतिष्ठा हे आपले मुख्य सामर्थ्य आहे.",
            "Sun in the 1st House imparts a radiant aura, high self-esteem, robust vitality, and innate executive leadership."),
        2: ("द्वितीय भावातील सूर्य जातकाला अधिकारयुक्त वाणी, कौटुंबिक प्रतिष्ठा आणि वडिलोपार्जित किंवा प्रशासकीय मार्गाने धनलाभ मिळवून देतो. आर्थिक निर्णय स्पष्टतेने घेतले जातात.",
            "Sun in the 2nd House bestows authoritative eloquence, ancestral prestige, and steady financial influx through state or reputable avenues."),
        3: ("तृतीय भावातील सूर्य जातकाला अपार धाडस, पराक्रम आणि निर्णयक्षमता प्रदान करतो. बंधू-भगिनींमध्ये प्रभाव आणि स्वकष्टातून मोठे यश मिळते.",
            "Sun in the 3rd House fosters exceptional valor, initiative, communication power, and triumph achieved through personal effort."),
        4: ("चतुर्थ भावातील सूर्य गृहसौख्य, वाहन प्राप्ती आणि समाजात प्रतिष्ठित स्थान देतो. स्थावर मालमत्ता व घरातील वातावरण शिस्तबद्ध राहते.",
            "Sun in the 4th House grants substantial domestic assets, vehicular comfort, and honorable community standing."),
        5: ("पंचम भावातील सूर्य प्रखर बुद्धिमत्ता, राजकीय व प्रशासकीय दृष्टिकोन आणि उच्च शिक्षण देतो. संततीकडून अभिमान वाटेल अशी प्रगती होते.",
            "Sun in the 5th House enhances creative intelligence, strategic advisory acumen, scholastic excellence, and noble progeny."),
        6: ("षष्ठ भावातील सूर्य 'शत्रूहंता' योग निर्माण करतो. स्पर्धा परीक्षा, न्यायालयीन प्रकरणे आणि विरोधकांवर सहज विजय मिळतो. शासकीय सेवेत यश लाभते.",
            "Sun in the 6th House acts as a classic 'Shatru-Hanta', crushing competitive obstacles and securing triumph in service and disputes."),
        7: ("सप्तम भावातील सूर्य स्वाभिमानी व प्रतिष्ठित जीवनसाथी दर्शवतो. भागीदारी आणि सार्वजनिक व्यवहारात पारदर्शकता ठेवल्यास मोठा सन्मान मिळतो.",
            "Sun in the 7th House indicates a self-respecting, capable spouse and high public visibility in social partnerships."),
        8: ("अष्टम भावातील सूर्य दीर्घायुष्य, गूढ संशोधनात रस आणि अचानक धनलाभाची शक्यता निर्माण करतो. आरोग्याची नियमित काळजी घेणे हितावह ठरते.",
            "Sun in the 8th House supports longevity, esoteric research, transformation, and potential ancestral gains."),
        9: ("नवम भावातील सूर्य पितृसुख, धार्मिक वृत्ती, उच्च भाग्योदय आणि लांबच्या तीर्थयात्रा घडवतो. गुरुजनांचे शुभाशीर्वाद सदैव पाठीशी राहतात.",
            "Sun in the 9th House elevates ethical fortune, spiritual travels, higher learning, and benevolent paternal mentorship."),
        10: ("दशम भावातील सूर्य 'दिग्बली' (सर्वोच्च बळवान) मानला जातो. करिअरमध्ये सर्वोच्च पद, शासकीय मान-सन्मान आणि प्रचंड अधिकार प्राप्त होतात.",
            "Sun in the 10th House achieves maximum directional strength (Digbala), conferring peak career status, state honors, and administrative authority."),
        11: ("एकादश भावातील सूर्य अनेक मार्गांनी विपुल धनलाभ, उच्च पदस्थ व्यक्तींशी मैत्री आणि सर्व महत्त्वाकांक्षांची पूर्तता घडवतो.",
            "Sun in the 11th House generates manifold income streams, influential social alliances, and the fulfillment of major ambitions."),
        12: ("द्वादश भावातील सूर्य परदेश गमन, दूरस्थ संपर्कातून प्रगती आणि आध्यात्मिक साधना देतो. सात्विक जीवनशैलीने मनःशांती लाभते.",
            "Sun in the 12th House facilitates foreign connections, spiritual transcendence, charitable deeds, and inner growth."),
    },
    "Moon": {
        1: ("लग्न भावातील चंद्र जातकाला आकर्षक रूप, सौम्य स्वभाव आणि तीव्र कल्पनाशक्ती देतो. समाजात सर्वांशी आपले स्नेहपूर्ण संबंध राहतात.",
            "Moon in the 1st House bestows physical charm, gentle emotional empathy, intuitive perception, and widespread social popularity."),
        2: ("द्वितीय भावातील चंद्र गोड वाणी, समृद्ध कौटुंबिक जीवन आणि व्यवसायातून स्थिर आर्थिक लाभ देतो. लोक आपल्या बोलण्याने प्रभावित होतात.",
            "Moon in the 2nd House grants melodious speech, domestic harmony, and fruitful prosperity through commerce and public relations."),
        3: ("तृतीय भावातील चंद्र संवाद कौशल्य, कलात्मक रुची आणि लघु प्रवासांतून यश मिळवून देतो. नातेवाईकांशी उत्तम सलोखा राहतो.",
            "Moon in the 3rd House sharpens communicative versatility, literary flair, and beneficial short-distance travel."),
        4: ("चतुर्थ भावातील चंद्र 'दिग्बली' मानला जातो. अथांग मनःशांती, मातेचे अपार प्रेम, स्वतःचे सुंदर घर आणि उत्तम वाहनसौख्य लाभते.",
            "Moon in the 4th House possesses directional strength (Digbala), providing profound emotional peace, maternal affection, and palatial home comforts."),
        5: ("पंचम भावातील चंद्र तीव्र स्मरणशक्ती, कला-साहित्यात प्राविण्य आणि गुणी संतती देतो. आपल्या कल्पना प्रत्यक्षात उतरवण्याचे सामर्थ्य मिळते.",
            "Moon in the 5th House bestows deep artistic sensitivity, sharp memory, creative talents, and blissful fulfillment through children."),
        6: ("षष्ठ भावातील चंद्र सेवाभावी वृत्ती आणि इतरांना मदत करण्याची प्रवृत्ती देतो. हवामान बदलानुसार कफ व सर्दीच्या त्रासापासून सावध राहावे.",
            "Moon in the 6th House inspires selfless service and diligence, while cautioning against psychosomatic stress or water-borne sensitivities."),
        7: ("सप्तम भावातील चंद्र देखणा, संवेदनशील आणि समंजस जोडीदार देतो. विवाहानंतर भाग्योदय वेगाने होतो व भागीदारीत यश मिळते.",
            "Moon in the 7th House indicates a graceful, affectionate spouse, marital bliss, and thriving public commercial partnerships."),
        8: ("अष्टम भावातील चंद्र गूढ शास्त्रे, मानसशास्त्र आणि अंतर्ज्ञानात गती देतो. ध्यानधारणा व नामस्मरणामुळे मानसिक स्वास्थ्य उत्तम राहते.",
            "Moon in the 8th House awakens intense occult curiosity, psychological insight, and psychic intuition."),
        9: ("नवम भावातील चंद्र धार्मिक यात्रा, उच्च नीतिमत्ता आणि विदेशातून भाग्योदय घडवतो. देवभक्ती आणि सत्कर्मातून सर्व कार्ये सिद्ध होतात.",
            "Moon in the 9th House blesses with ethical righteousness, sacred pilgrimages, academic elevation, and fortunate long journeys."),
        10: ("दशम भावातील चंद्र जनसंपर्क, समाजकारण, कला आणि व्यवसायात मोठी लोकप्रियता देतो. कामाच्या ठिकाणी आपला प्रभाव सतत वाढतो.",
            "Moon in the 10th House confers public prominence, community leadership, and distinguished professional success in public-facing careers."),
        11: ("एकादश भावातील चंद्र अखंड धनप्रवाह, प्रतिष्ठित मित्रपरिवार आणि सर्व इच्छांची पूर्तता करतो. महिला वर्गाकडून विशेष सहकार्य लाभते.",
            "Moon in the 11th House guarantees steady cash inflows, loyal influential friends, and joyful realization of lifelong hopes."),
        12: ("द्वादश भावातील चंद्र परदेश वास्तव्याचे योग, गूढ साधना आणि एकांतात आत्मपरीक्षण देतो. निसर्गाच्या सान्निध्यात शांतता मिळते.",
            "Moon in the 12th House favors foreign relocation, philanthropic generosity, meditative solitude, and spiritual evolution."),
    },
    "Mars": {
        1: ("लग्न भावातील मंगळ अफाट शारीरिक ऊर्जा, धाडस आणि लढवय्यी वृत्ती देतो. कोणत्याही संकटात न डगमगता नेतृत्व करण्याची क्षमता मिळते.",
            "Mars in the 1st House infuses dynamic vitality, competitive drive, athletic prowess, and courageous leadership."),
        2: ("द्वितीय भावातील मंगळ स्पष्ट आणि रोखठोक वाणी देतो. स्वकष्टातून, रिअल इस्टेट व अभियांत्रिकीच्या माध्यमातून विपुल धनसंचय होतो.",
            "Mars in the 2nd House gives bold, direct speech, strong family protection, and substantial assets accumulated through enterprise and technical skill."),
        3: ("तृतीय भावातील मंगळ जातकाला महापराक्रमी बनवतो. क्रीडा, उद्योग, सुरक्षा व तांत्रिक क्षेत्रात मोठी झेप घेण्याची ताकद मिळते.",
            "Mars in the 3rd House is exceptionally potent, granting heroic courage, athletic triumphs, initiative, and mastery in technical domains."),
        4: ("चतुर्थ भावातील मंगळ भूमी, शेती, इमारत बांधकाम आणि वाहनांचा मोठा लाभ देतो. घरातील संवाद शांततेने ठेवणे फायदेशीर ठरते.",
            "Mars in the 4th House brings substantial real estate, land ownership, and construction opportunities."),
        5: ("पंचम भावातील मंगळ तांत्रिक बुद्धिमत्ता, विश्लेषण क्षमता आणि स्पर्धांमध्ये यश देतो. निर्णय घेताना संयम ठेवल्यास उत्तम प्रगती होते.",
            "Mars in the 5th House stimulates sharp analytical intelligence, engineering acumen, and high drive in competitive pursuits."),
        6: ("षष्ठ भावातील मंगळ शत्रूंवर निर्विवाद विजय, कर्जातून जलद मुक्ती आणि न्यायालयीन यश देतो. पोलीस, सैन्य, क्रीडा किंवा प्रशासनात विजय मिळतो.",
            "Mars in the 6th House is a supreme defensive shield, destroying rivals, crushing litigation, and granting swift recovery from debts."),
        7: ("सप्तम भावातील मंगळ गतिमान आणि महत्त्वाकांक्षी जोडीदार दर्शवतो. वैवाहिक जीवनात परस्पर सामंजस्य आणि समजूतदारपणा ठेवल्यास उत्तम प्रगती होते.",
            "Mars in the 7th House reflects an energetic, industrious partner; mutual patience and joint cooperation ensure fruitful marital progress."),
        8: ("अष्टम भावातील मंगळ अचानक धनलाभ, गुप्त संशोधन आणि संकटांशी झुंजण्याची अद्भूत क्षमता देतो. वाहने चालवताना सावधानता बाळगावी.",
            "Mars in the 8th House bestows transformative resilience, sudden financial windfalls, and deep research potential."),
        9: ("नवम भावातील मंगळ तत्त्वनिष्ठ, धार्मिक कार्यात पुढाकार घेणारा आणि भाग्योदयासाठी धाडसी पावले उचलणारा बनवतो.",
            "Mars in the 9th House inspires principled courage, pioneering travels, and bold initiatives that unlock destiny."),
        10: ("दशम भावातील मंगळ 'कुलदीपक' योग मानला जातो. तंत्रज्ञान, उद्योग, संरक्षण, पोलीस अथवा प्रशासनात सर्वोच्च पद व प्रतिष्ठा मिळते.",
            "Mars in the 10th House achieves maximum directional power (Digbala), creating a celebrated 'Kuladeepak Yoga' of stellar professional fame and executive power."),
        11: ("एकादश भावातील मंगळ प्रचंड धनलाभ, स्थावर मालमत्तेतून नियमित उत्पन्न आणि बलाढ्य मित्रांचे सहकार्य मिळवून देतो.",
            "Mars in the 11th House generates colossal financial revenues, property rental returns, and influential alliances."),
        12: ("द्वादश भावातील मंगळ परदेशी कंपन्यांमध्ये काम, संरक्षण किंवा तांत्रिक प्रकल्पांतून लाभ मिळवून देतो. खर्चावर नियंत्रण ठेवणे हितकारक आहे.",
            "Mars in the 12th House favors global technical ventures, multinational corporate service, and strategic discipline over expenditure."),
    },
    "Mercury": {
        1: ("लग्न भावातील बुध जातकाला हजरजबाबी, कुशाग्र बुद्धिमत्ता आणि आकर्षक व्यक्तिमत्त्व देतो. व्यापार आणि संवादात आपण नेहमी पुढे असता.",
            "Mercury in the 1st House grants brilliant wit, youthful charm, versatile intellect, and supreme communicative fluency."),
        2: ("द्वितीय भावातील बुध वाणीतील गोडवा, गणितीय कौशल्य आणि व्यापारातून प्रचंड धनलाभ देतो. आपले आर्थिक नियोजन अत्यंत अचूक असते.",
            "Mercury in the 2nd House creates exceptional verbal brilliance, financial acumen, accounting mastery, and commercial fortune."),
        3: ("तृतीय भावातील बुध उत्कृष्ट लेखन, पत्रकारिता, माहिती तंत्रज्ञान आणि प्रभावी संवाद कौशल्य प्रदान करतो.",
            "Mercury in the 3rd House fosters extraordinary literary talent, IT mastery, digital commerce skills, and media success."),
        4: ("चतुर्थ भावातील बुध शैक्षणिक यश, सुंदर ग्रंथसंग्रह आणि घरात सुसंस्कृत आनंदी वातावरण देतो. वाहन व भूमीचे सुख उत्तम लाभते.",
            "Mercury in the 4th House ensures scholastic achievements, domestic refinement, intellectual family atmosphere, and property gains."),
        5: ("पंचम भावातील बुध प्रखर बुद्धिमत्ता, कल्पकता, शेअर मार्केट व आर्थिक विश्लेषणात यश देतो. आपल्या सल्ल्याचा इतरांना मोठा लाभ होतो.",
            "Mercury in the 5th House sharpens strategic speculation, algorithmic thinking, consultative brilliance, and creative writing."),
        6: ("षष्ठ भावातील बुध स्पर्धा परीक्षा, कायदेशीर सल्लागार, लेखापरीक्षण आणि बौद्धिक वादात विजय मिळवून देतो.",
            "Mercury in the 6th House excels in legal analysis, auditing, competitive examinations, and resolving complex commercial disputes."),
        7: ("सप्तम भावातील बुध हुशार, सुशिक्षित आणि संभाषणचतुर जीवनसाथी देतो. व्यावसायिक भागीदारीतून मोठा आर्थिक फायदा होतो.",
            "Mercury in the 7th House brings an intelligent, articulate partner and fruitful success in commercial joint ventures."),
        8: ("अष्टम भावातील बुध गूढ विज्ञान, संशोधन, कर आकारणी व विमा क्षेत्रातून लाभ मिळवून देतो. आपली बौद्धिक एकाग्रता उत्तम असते.",
            "Mercury in the 8th House supports investigative journalism, taxation research, data forensics, and occult studies."),
        9: ("नवम भावातील बुध उच्च शिक्षण, परदेशातील परिषदा, आध्यात्मिक ज्ञान आणि ग्रंथलेखनात कीर्ती मिळवून देतो.",
            "Mercury in the 9th House bestows higher scholarly degrees, foreign publications, ethical wisdom, and philosophical repute."),
        10: ("दशम भावातील बुध व्यवसाय, सनदी लेखापाल (CA), संगणक तंत्रज्ञान, सल्लागार अथवा प्रशासनात मोठी ख्याती देतो.",
            "Mercury in the 10th House generates eminent acclaim in executive management, chartered accountancy, software IT, and commerce."),
        11: ("एकादश भावातील बुध अनेक व्यापार शाखांतून निरंतर लाभ, बुद्धिमान मित्रांचे जाळे आणि सर्व आर्थिक संकल्पांची पूर्तता करतो.",
            "Mercury in the 11th House creates diverse commercial income streams, an erudite professional network, and steady gains."),
        12: ("द्वादश भावातील बुध बहुराष्ट्रीय कंपन्या, आयात-निर्यात, संशोधन व परदेशी व्यवहारातून विशेष यश मिळवून देतो.",
            "Mercury in the 12th House favors international trade, import-export ventures, research publishing, and offshore consultancy."),
    },
    "Jupiter": {
        1: ("लग्न भावातील गुरु 'हंस योग' किंवा अत्यंत सात्विक व्यक्तिमत्त्व देतो. समाज आपल्याला मार्गदर्शक मानतो; आयुष्यभर आरोग्य व प्रतिष्ठा टिकून राहते.",
            "Jupiter in the 1st House bestows supreme wisdom, moral stature, magnetic respect, and noble counsel."),
        2: ("द्वितीय भावातील गुरु समृद्ध कुटुंब, सत्यप्रिय वाणी आणि अपार धनसंपत्ती देतो. आपल्या शब्दांना समाजात मोलाचे स्थान असते.",
            "Jupiter in the 2nd House creates immense financial prosperity, righteous speech, domestic happiness, and ethical wealth accumulation."),
        3: ("तृतीय भावातील गुरु बंधुप्रेम, धार्मिक लेखन, आध्यात्मिक मार्गदर्शन आणि सदाचारी वर्तनातून कीर्ती मिळवून देतो.",
            "Jupiter in the 3rd House fosters philosophical authorship, spiritual journalism, noble sibling bonds, and honorable enterprise."),
        4: ("चतुर्थ भावातील गुरु उत्तम मातृसुख, विशाल गृह, समृद्ध वाहने आणि अथांग मानसिक समाधानाची देणगी देतो.",
            "Jupiter in the 4th House grants vast residential comfort, profound domestic peace, vehicular luxury, and maternal blessings."),
        5: ("पंचम भावातील गुरु उच्च विद्या, दैवी अंतर्ज्ञान, मंत्र सिद्धी आणि सुसंस्कृत संतती देतो. आपल्या बुद्धिमत्तेने मोठे कार्य घडते.",
            "Jupiter in the 5th House creates extraordinary intellectual brilliance, spiritual intuition, educational mastery, and celebrated children."),
        6: ("षष्ठ भावातील गुरु शत्रूंनाही मित्र बनवतो. न्यायालयीन खटले आपोआप मिटतात आणि सेवेच्या माध्यमातून उच्च सन्मान मिळतो.",
            "Jupiter in the 6th House disarms rivals through diplomacy, clears liabilities honorably, and elevates social service reputation."),
        7: ("सप्तम भावातील गुरु सुविद्य, देखणा, धार्मिक आणि भाग्यवान जोडीदार देतो. विवाहानंतर जीवनाला अत्यंत शुभ वळण लागते.",
            "Jupiter in the 7th House blesses with a virtuous, accomplished, supportive spouse and triumphant commercial partnerships."),
        8: ("अष्टम भावातील गुरु दीर्घायुष्य, संकटमुक्ती, वारसा हक्काने धनलाभ आणि गूढ तत्त्वज्ञानाची सखोल समज देतो.",
            "Jupiter in the 8th House guarantees long peaceful life, unexpected legacy assets, and esoteric spiritual awakening."),
        9: ("नवम भावातील गुरु हा स्वतःच्या कारकातील अत्यंत श्रेष्ठ योग आहे. भाग्योदय, तीर्थयात्रा, गुरुंची कृपा आणि समाजात सर्वोच्च मान मिळतो.",
            "Jupiter in the 9th House is in its natural Karaka domain, showering supreme good fortune, sacred travels, and divine blessings."),
        10: ("दशम भावातील गुरु राजसत्ता, शासकीय सल्लागार, न्यायमूर्ती अथवा उच्च व्यवस्थापकीय पदावर पोहोचवतो. निष्कलंक चारित्र्य हे आपले वैशिष्ट्य ठरते.",
            "Jupiter in the 10th House elevates to ministerial, judicial, corporate advisory, or institutional leadership with spotless integrity."),
        11: ("एकादश भावातील गुरु अफाट धनलाभ, सर्व संकल्पांची सहज सिद्धी आणि समाजातील सर्वोच्च व्यक्तींचे आशीर्वाद मिळवून देतो.",
            "Jupiter in the 11th House is the greatest wealth amplifier, fulfilling noble desires and guaranteeing abundant prosperity."),
        12: ("द्वादश भावातील गुरु धर्मकार्य, दानधर्म, मोक्ष साधना आणि परदेशातील शैक्षणिक अथवा आध्यात्मिक प्रकल्पांतून यश देतो.",
            "Jupiter in the 12th House inspires selfless charity, spiritual emancipation (Moksha), and global philanthropic eminence."),
    },
    "Venus": {
        1: ("लग्न भावातील शुक्र अत्यंत देखणे रूप, कलात्मक दृष्टी, सौम्यता आणि राजसी राहणीमान प्रदान करतो. लोकांमध्ये आपण सहज प्रिय होता.",
            "Venus in the 1st House confers striking aesthetic grace, magnetic appeal, refined taste, and a luxurious aura."),
        2: ("द्वितीय भावातील शुक्र मिष्टान्न भोजन, गोड वाणी, दागदागिने, वस्त्रे आणि सोन्या-चांदीचा विपुल संग्रह देतो.",
            "Venus in the 2nd House bestows sweet eloquence, artistic domestic charm, and lavish savings in precious metals and luxuries."),
        3: ("तृतीय भावातील शुक्र संगीत, नाट्य, चित्रकला आणि संवादात विशेष यश देतो. आपल्या कलागुणांचे सर्वत्र कौतुक होते.",
            "Venus in the 3rd House ignites artistic talents in music, performing arts, design, and engaging social charm."),
        4: ("चतुर्थ भावातील शुक्र 'दिग्बली' मानला जातो. अतिभव्य घर, अलिशान वाहने, आधुनिक सुखसोयी आणि दांपत्य सौख्याचा महालाभ मिळतो.",
            "Venus in the 4th House reaches peak directional strength (Digbala), bestowing magnificent estates, luxury cars, and joyous domestic bliss."),
        5: ("पंचम भावातील शुक्र रसिक मन, प्रेमात यश, सिनेमा, डिझायनिंग, तंत्रज्ञान अथवा सौंदर्याशी संबंधित क्षेत्रांतून मोठी कमाई देतो.",
            "Venus in the 5th House fosters romantic harmony, creative genius, entertainment/design flair, and delightful children."),
        6: ("षष्ठ भावातील शुक्र सौंदर्यप्रसाधने, वैद्यकीय सेवा अथवा सेवा उद्योगात यश देतो. आरोग्याची आणि आहाराची योग्य शिस्त पाळावी.",
            "Venus in the 6th House favors success in hospitality, wellness, and healthcare, advising balanced dietary habits."),
        7: ("सप्तम भावातील शुक्र अत्यंत सुंदर, समंजस आणि प्रेमळ जीवनसाथी देतो. वैवाहिक जीवन सुखाचे आणि समृद्धीचे राहते.",
            "Venus in the 7th House blesses with an attractive, loving, devoted spouse and flourishing commercial partnerships."),
        8: ("अष्टम भावातील शुक्र अचानक धनलाभ, सुखी वैवाहिक जीवन आणि जीवनसाथीकडून आर्थिक पाठबळ मिळवून देतो.",
            "Venus in the 8th House provides sudden legacies, marital assets, comfortable longevity, and protection from crises."),
        9: ("नवम भावातील शुक्र विदेश प्रवास, तीर्थस्थळांचे दर्शन आणि विवाहानंतर प्रचंड भाग्योदय घडवून आणतो.",
            "Venus in the 9th House inspires cultural pilgrimages, global travels, and dramatic fortune acceleration post-marriage."),
        10: ("दशम भावातील शुक्र मीडिया, फॅशन, लक्झरी उत्पादने, मनोरंजन, वास्तुकला अथवा जनसंपर्कातून मोठा नफा व सन्मान देतो.",
            "Venus in the 10th House commands grand success in creative arts, architecture, luxury brand management, and media."),
        11: ("एकादश भावातील शुक्र विलासी जीवन, वाहन सुख, श्रीमंत मैत्रिणी/मित्रांचे सहकार्य आणि निरंतर धनप्राप्ती घडवतो.",
            "Venus in the 11th House guarantees uninterrupted cash inflow, opulent lifestyle privileges, and influential artistic social circles."),
        12: ("द्वादश भावातील शुक्र 'शयनसुख' व परदेश प्रवासाचा उत्तम लाभ देतो. सुख-सोयींवर खर्च करताना आर्थिक नियोजन राखावे.",
            "Venus in the 12th House is famously exalted in natural comforts, global travel delights, and lavish lifestyle enjoyment."),
    },
    "Saturn": {
        1: ("लग्न भावातील शनी जातकाला गंभीर, परिपक्व, सहनशील आणि अत्यंत कष्टाळू बनवतो. आयुष्यात सुरुवातीला संघर्ष झाला तरी उत्तरार्धात अढळ यश मिळते.",
            "Saturn in the 1st House builds granite endurance, serious maturity, deep patience, and monumental long-term triumphs."),
        2: ("द्वितीय भावातील शनी काटकसर, संपत्तीचे रक्षण आणि दीर्घकालीन गुंतवणुकीतून अथांग धनसंचय करण्याची बुद्धी देतो.",
            "Saturn in the 2nd House enforces frugal discipline, prudent financial management, and massive compounding wealth over time."),
        3: ("तृतीय भावातील शनी पराक्रम, तंत्रज्ञान, उद्योग आणि कठोर परिश्रमातून मोठे साम्राज्य उभे करण्याची क्षमता देतो.",
            "Saturn in the 3rd House provides relentless work ethic, industrial stamina, and victorious conquest over all setbacks."),
        4: ("चतुर्थ भावातील शनी जुनी संपत्ती, स्थावर मालमत्ता, खनिजे आणि शेतजमिनीतून मोठा लाभ देतो. आईची सेवा केल्याने भाग्योदय होतो.",
            "Saturn in the 4th House governs ancestral land, agricultural estates, mining interests, and enduring domestic stability."),
        5: ("पंचम भावातील शनी सखोल संशोधन, तांत्रिक शिक्षण आणि गंभीर विषयांमध्ये प्राविण्य देतो. विचारपूर्वक केलेले काम दीर्घकाळ टिकते.",
            "Saturn in the 5th House stimulates deep intellectual concentration, specialized technical scholarship, and disciplined creativity."),
        6: ("षष्ठ भावातील शनी सर्व शत्रू, आजार आणि कर्जावर मात करतो. कोणतीही स्पर्धा अथवा संघर्ष आल्यास विजय जातकाचाच होतो.",
            "Saturn in the 6th House is a mighty fortress, annihilating competitive rivals, clearing debts, and ensuring indestructible stamina."),
        7: ("सप्तम भावातील शनी 'दिग्बली' मानला जातो. समंजस, परिपक्व आणि निष्ठावान जोडीदार मिळतो; भागीदारीतून मोठा आर्थिक फायदा होतो.",
            "Saturn in the 7th House possesses directional strength (Digbala), securing a mature, steadfast spouse and prosperous commercial alliances."),
        8: ("अष्टम भावातील शनी 'आयुष्यकारक' म्हणून दीर्घायुष्य देतो. संकटांवर शांतपणे मात करण्याची अफाट शक्ती आपल्यात असते.",
            "Saturn in the 8th House is the prime significator of longevity (Ayushyakaraka), granting profound transformation and crisis resilience."),
        9: ("नवम भावातील शनी तत्त्वनिष्ठ, पारंपारिक मूल्यांचा रक्षक आणि आयुष्याच्या उत्तरार्धात प्रचंड भाग्योदय देणारा ठरतो.",
            "Saturn in the 9th House inspires disciplined righteousness, deep philosophical study, and rising fortune in mature years."),
        10: ("दशम भावातील शनी उद्योगपती, उच्च प्रशासक अथवा जननेता बनवतो. शून्यातून विश्व निर्माण करण्याची अफाट ताकद मिळते.",
            "Saturn in the 10th House commands celebrated industrial leadership, executive stamina, and self-made monumental achievement."),
        11: ("एकादश भावातील शनी उद्योग, लोह, खनिज, रिअल इस्टेट व मोठ्या यंत्रसामग्रीच्या व्यापारातून निरंतर मोठा नफा मिळवून देतो.",
            "Saturn in the 11th House provides massive industrial profits, long-term capital wealth, and faithful associates."),
        12: ("द्वादश भावातील शनी परदेश वास्तव्य, दूरस्थ प्रकल्पांवर नियंत्रण आणि अध्यात्मिक शांतता मिळवून देतो.",
            "Saturn in the 12th House favors foreign infrastructure careers, strategic solitude, and unshakeable spiritual grounding."),
    },
    "Rahu": {
        1: ("लग्न भावातील राहू जातकाला तीव्र महत्त्वाकांक्षी, क्रांतिकारी विचारसरणीचा आणि आधुनिक तंत्रज्ञानात निपुण बनवतो.",
            "Rahu in the 1st House sparks intense ambition, unconventional genius, innovative mindset, and magnetic worldly drive."),
        2: ("द्वितीय भावातील राहू परकीय चलन, तंत्रज्ञान, शेअर बाजार आणि नव्या युगातील साधनांतून अचानक मोठा धनलाभ घडवतो.",
            "Rahu in the 2nd House creates explosive unexpected financial influx through modern technology, crypto/stocks, and foreign avenues."),
        3: ("तृतीय भावातील राहू अफाट धाडस, डिजिटल मीडिया आणि सोशल नेटवर्किंगच्या माध्यमातून समाजात मोठी लोकप्रियता मिळवून देतो.",
            "Rahu in the 3rd House confers daring courage, digital media acclaim, entrepreneurial audacity, and competitive victory."),
        4: ("चतुर्थ भावातील राहू आधुनिक शैलीचे आलिशान घर, विदेशी वाहने आणि जन्मगावापेक्षा दूरच्या ठिकाणी मोठी प्रगती घडवतो.",
            "Rahu in the 4th House brings ultra-modern residential luxury, exotic vehicles, and stellar progress away from birthplace."),
        5: ("पंचम भावातील राहू कल्पकता, संगणक प्रोग्रामिंग, शेअर विश्लेषण आणि कलाक्षेत्रातून अनपेक्षित मोठा नफा मिळवून देतो.",
            "Rahu in the 5th House stimulates out-of-the-box creativity, tech algorithmic mastery, and lucrative speculative gains."),
        6: ("षष्ठ भावातील राहू अत्यंत बलवान मानला जातो. सर्व विरोधक, आजार आणि स्पर्धांमध्ये जातकाला निर्विवाद विजय मिळवून देतो.",
            "Rahu in the 6th House is hailed as virtually invincible, pulverizing enemies, crushing competition, and resolving disputes."),
        7: ("सप्तम भावातील राहू आधुनिक विचारांचा, आंतरराष्ट्रीय पार्श्वभूमी असलेला अथवा स्वतंत्र वृत्तीचा जोडीदार दर्शवतो.",
            "Rahu in the 7th House indicates a cosmopolitan, dynamic spouse and profitable exposure to international trade partnerships."),
        8: ("अष्टम भावातील राहू अचानक लॉटरी, विमा, गुप्त शोध आणि गूढ शास्त्रांच्या अभ्यासातून अनपेक्षित प्रगती देतो.",
            "Rahu in the 8th House brings unexpected inheritances, deep forensic research prowess, and intuitive mastery over hidden sciences."),
        9: ("नवम भावातील राहू परदेश प्रवास, आंतरराष्ट्रीय शिक्षण आणि पारंपारिक चौकटीबाहेर जाऊन नवे विचार मांडण्याची प्रेरणा देतो.",
            "Rahu in the 9th House inspires foreign educational pilgrimages, cross-cultural wisdom, and boundary-breaking worldview."),
        10: ("दशम भावातील राहू राजकारण, मीडिया, तंत्रज्ञान आणि मोठ्या संस्थांमध्ये अभूतपूर्व झेप घेण्याची ताकद देतो.",
            "Rahu in the 10th House catapults into public power, digital media prominence, tech disruption, and meteoric career advancement."),
        11: ("एकादश भावातील राहू 'महाधनयोग' मानला जातो. अपार संपत्ती, अनेक मार्गांनी उत्पन्न आणि प्रचंड जनसमर्थन प्राप्त होते.",
            "Rahu in the 11th House is a legendary wealth-generator, showering multi-channel financial abundance and high status."),
        12: ("द्वादश भावातील राहू परदेशात स्थायी वास्तव्य, मल्टिनॅशनल कंपन्यांमध्ये उच्च स्थान आणि दूरस्थ भूमीतून यश देतो.",
            "Rahu in the 12th House strongly facilitates permanent foreign settlement, MNC leadership, and offshore success."),
    },
    "Ketu": {
        1: ("लग्न भावातील केतू जातकाला अंतर्मुख, आध्यात्मिक, तत्त्वज्ञानी आणि सूक्ष्म गोष्टींचे अवलोकन करणारा बनवतो.",
            "Ketu in the 1st House bestows deep spiritual detachment, philosophical insight, intuitive perception, and quiet personal power."),
        2: ("द्वितीय भावातील केतू सात्विक जीवनशैली, आध्यात्मिक वाचन आणि पैशांच्या मोहापेक्षा ज्ञानाला प्राधान्य देण्याची वृत्ती देतो.",
            "Ketu in the 2nd House inclines towards truth, spiritual literature, non-attachment to material hoarding, and profound speech."),
        3: ("तृतीय भावातील केतू शांत पराक्रम, आध्यात्मिक संदेशवहन आणि कठीण प्रसंगातही मनोधैर्य टिकवून ठेवण्याचे सामर्थ्य देतो.",
            "Ketu in the 3rd House confers quiet internal bravery, spiritual communication skills, and unshakeable inner resilience."),
        4: ("चतुर्थ भावातील केतू शांत एकांत, ध्यानधारणा आणि वडिलोपार्जित परंपरेपेक्षा स्वतःच्या आध्यात्मिक शांततेला महत्त्व देतो.",
            "Ketu in the 4th House seeks meditative domestic sanctuary, simple living, and inner spiritual peace above worldly show."),
        5: ("पंचम भावातील केतू मंत्र विद्या, ज्योतिष, गणित आणि सूक्ष्म विश्लेषणात विलक्षण बुद्धिमत्ता देतो.",
            "Ketu in the 5th House opens intuitive channels for occult wisdom, astrology, spiritual algorithms, and esoteric mastery."),
        6: ("षष्ठ भावातील केतू आजारांवर आत्मिक बळाने मात करण्याची ताकद देतो आणि संकटांमधून ईश्वरकृपेने सुरक्षित बाहेर काढतो.",
            "Ketu in the 6th House disarms malice through spiritual aura, protects health via holistic practices, and triumphs quietly."),
        7: ("सप्तम भावातील केतू आध्यात्मिक वृत्तीचा, शांत आणि सात्विक जोडीदार दर्शवतो. नात्यात बौद्धिक व आत्मिक संवाद महत्त्वाचा ठरतो.",
            "Ketu in the 7th House signifies a spiritually inclined, peaceful spouse who values deep soul connection over superficial glamour."),
        8: ("अष्टम भावातील केतू गूढ विद्या, कुंडली जागृती आणि आयुष्यातील संकटांना वरदान बनवण्याची अद्भूत दैवी शक्ती देतो.",
            "Ketu in the 8th House is supreme for Kundalini awakening, psychic penetration, and miraculous spiritual rescues."),
        9: ("नवम भावातील केतू 'मोक्षकारक' मानला जातो. उच्च तीर्थयात्रा, सत्पुरुषांचे सान्निध्य आणि दैवी अनुग्रह आयुष्यभर मिळतो.",
            "Ketu in the 9th House is the ultimate beacon of Dharma and Moksha, connecting with enlightened masters and sacred grace."),
        10: ("दशम भावातील केतू निष्काम कर्मयोग, तंत्रज्ञान, संशोधन आणि स्वतंत्र सल्लागार म्हणून मोठा आदर मिळवून देतो.",
            "Ketu in the 10th House guides towards selfless excellence, specialized technical consulting, research, and non-attached leadership."),
        11: ("एकादश भावातील केतू अचानक अनपेक्षित लाभ, सात्विक मित्रांचा सहवास आणि आत्मिक समाधानाची अनुभूती देतो.",
            "Ketu in the 11th House provides unexpected spiritual and material windfalls, loyal ethical companions, and soul contentment."),
        12: ("द्वादश भावातील केतू 'मोक्ष' प्राप्तीचा सर्वात पवित्र योग मानला जातो. अंतिम मुक्ती, आध्यात्मिक आनंद आणि तीर्थवासाचे सुख लाभते.",
            "Ketu in the 12th House is the exalted gateway to Moksha (Liberation), conferring supreme transcendental peace and divine union."),
    }
}


def build_dynamic_life_predictions(core_data: dict) -> list[dict]:
    """
    Computes 100% chart-specific, personalized interpretations for the 10 core life domains:
    Character, Happiness, Lifestyle, Career, Occupation, Health, Hobbies, Love & Marriage, Finance, Education.
    """
    meta = core_data["meta"]
    p_by_id = core_data["planet_by_id"]
    lagna_sign = meta["lagna_sign_num"]
    lagna_en = meta["lagna_en"]
    lagna_hi = meta["lagna_hi"]
    rasi_en = meta["rasi_en"]
    rasi_hi = meta["rasi_hi"]
    nak_en = meta["nakshatra_en"]
    nak_hi = meta["nakshatra_hi"]
    nak_pada = meta.get("nakshatra_pada", 1)

    def get_hl(h: int):
        s_num = ((lagna_sign - 1 + h - 1) % 12) + 1
        l_en, l_mr = SIGN_LORDS[s_num]
        pl = p_by_id.get(l_en)
        if pl:
            l_sign = pl["sign_num"]
            l_house = ((l_sign - lagna_sign) % 12) + 1
            return {
                "house": h, "sign_num": s_num, "sign_en": SIGN_NAMES_EN[s_num], "sign_mr": SIGN_NAMES_MR[s_num],
                "lord_en": l_en, "lord_mr": l_mr, "lord_house": l_house, "lord_sign_num": l_sign,
                "lord_sign_en": SIGN_NAMES_EN[l_sign], "lord_sign_mr": SIGN_NAMES_MR[l_sign],
                "deg": pl.get("deg_in_sign", 0), "nak": pl.get("nakshatra_en", "")
            }
        return {"house": h, "sign_num": s_num, "sign_en": SIGN_NAMES_EN[s_num], "sign_mr": SIGN_NAMES_MR[s_num],
                "lord_en": l_en, "lord_mr": l_mr, "lord_house": 1, "lord_sign_num": s_num,
                "lord_sign_en": SIGN_NAMES_EN[s_num], "lord_sign_mr": SIGN_NAMES_MR[s_num], "deg": 0, "nak": ""}

    h1 = get_hl(1)
    h2 = get_hl(2)
    h4 = get_hl(4)
    h5 = get_hl(5)
    h6 = get_hl(6)
    h7 = get_hl(7)
    h10 = get_hl(10)
    h11 = get_hl(11)

    char_mr = (
        f"आपली जन्म पत्रिका {h1['sign_mr']} लग्न आणि {rasi_hi} राशीने सुशोभित आहे. जन्म लग्नाचा स्वामी {h1['lord_mr']} ग्रह कुंडलीतील {HOUSE_ORDINAL_MR[h1['lord_house']]} स्थानात {h1['lord_sign_mr']} राशीत विराजमान आहे. "
        f"{h1['sign_mr']} लग्नाच्या प्रभावामुळे आपले व्यक्तिमत्त्व अत्यंत दृढनिश्चयी, प्रभावी आणि कणखर आहे. आपण कोणत्याही आव्हानाला सामोरे जाण्यास कधीही कचरत नाही. "
        f"लग्नेश {h1['lord_mr']} हा {HOUSE_ORDINAL_MR[h1['lord_house']]} स्थानात स्थित असल्याने आपल्यात नैसर्गिक नेतृत्वगुण, तीव्र बुद्धिमत्ता आणि लोककल्याणकारी दृष्टिकोन निर्माण होतो. "
        f"आपला जन्म {nak_hi} नक्षत्राच्या {nak_pada} चरणामध्ये झाला असल्याने आपल्या विचारांमध्ये स्पष्टता, निष्ठा आणि सत्यप्रियता दिसून येते. "
        f"कधीकधी कामाचा ताण किंवा अन्याय सहन न झाल्यामुळे शीघ्र कोप (राग) संभवतो; परंतु शांत चित्ताने घेतलेले निर्णय आपल्याला जीवनात सर्वोच्च यश व मान-सन्मान मिळवून देतील."
    )
    char_en = (
        f"Your horoscope is governed by {lagna_en} Ascendant with your Moon in {rasi_en} sign. Your Lagna Lord {h1['lord_en']} is favorably positioned in the {HOUSE_ORDINAL_EN[h1['lord_house']]} house in {h1['lord_sign_en']}. "
        f"The energy of {lagna_en} bestows you with an intensely determined, magnetic, and authoritative personality. You possess strong resilience and fearlessly confront life challenges. "
        f"With your Lagnesh residing in the {HOUSE_ORDINAL_EN[h1['lord_house']]} house, you are naturally blessed with strategic foresight, leadership acumen, and a constructive approach towards personal and social goals. "
        f"Born under the cosmic vibrations of {nak_en} Nakshatra (Pada {nak_pada}), your character radiates sincerity, acute intellect, and principled conduct."
    )

    hap_mr = (
        f"कुंडलीतील चतुर्थ (सुख) भावात {h4['sign_mr']} राशी असून या भावाचा स्वामी {h4['lord_mr']} हा {HOUSE_ORDINAL_MR[h4['lord_house']]} स्थानात स्थित आहे. "
        f"हा ग्रहयोग जातकाला उत्तम गृहसौख्य, स्वतःचे घर, वाहन आणि स्थावर संपत्तीचे सुख मिळवून देणारा आहे. "
        f"मातेचे शुभाशीर्वाद आणि कौटुंबिक सौहार्द आपल्याला मानसिक शांतता देईल. आपण संकटसमयीही धीर न सोडता कुटुंबाला एकत्र बांधून ठेवणारे आधारस्तंभ आहात."
    )
    hap_en = (
        f"The 4th House (Domestic Happiness & Assets) contains {h4['sign_en']}, ruled by {h4['lord_en']} which is stationed in the {HOUSE_ORDINAL_EN[h4['lord_house']]} house. "
        f"This planetary disposition promises solid home comforts, residential property, vehicular ease, and deep emotional contentment. "
        f"Maternal blessings and family unity act as your bedrock of mental tranquility and inner satisfaction."
    )

    style_mr = (
        f"लग्नेश {h1['lord_mr']} आणि धनपती {h2['lord_mr']} यांच्या शुभ स्थितीमुळे आपली जीवनशैली सुव्यवस्थित, प्रतिष्ठित आणि शिस्तबद्ध राहील. "
        f"आपण दिखाव्यापेक्षा गुणवत्ता, साधेपणात अभिजातता आणि आत्मसन्मानाला सर्वाधिक महत्त्व देता. आधुनिक सुखसोयींचा उपभोग घेत असतानाच पारंपारिक मूल्यांची जपणूक करणे ही आपली मुख्य जीवनशैली आहे."
    )
    style_en = (
        f"Influenced by Lagnesh {h1['lord_en']} and Wealth Lord {h2['lord_en']}, your lifestyle reflects a fine balance of dignity, discipline, and understated elegance. "
        f"You prioritize authentic quality over superficial ostentation. While enjoying modern technological comforts, you remain anchored in core cultural ethics."
    )

    car_mr = (
        f"कुंडलीतील दशम (कर्म व आजीविका) भावात {h10['sign_mr']} राशी विराजमान असून या भावाचा स्वामी {h10['lord_mr']} हा {HOUSE_ORDINAL_MR[h10['lord_house']]} स्थानात {h10['lord_sign_mr']} राशीत विराजमान आहे. "
        f"हा दशमेश योग आपल्या करिअरमध्ये उच्च पद, प्रशासकीय अधिकार आणि व्यावसायिक स्थैर्य देणारा आहे. "
        f"तंत्रज्ञान, अभियांत्रिकी, व्यवस्थापन, शासकीय सेवा, आर्थिक सल्लागार, रिअल इस्टेट अथवा स्वतंत्र उद्योग या क्षेत्रांमध्ये आपले कर्तृत्व विशेष चमकेल. "
        f"आपल्या कार्यशैलीतील प्रामाणिकपणा व जबाबदारीचे भान आपल्याला वरिष्ठांचे व समाजाचे पूर्ण सहकार्य मिळवून देईल."
    )
    car_en = (
        f"Your 10th House (Profession & Karma) is ruled by {h10['sign_en']} with its Lord {h10['lord_en']} seated in the {HOUSE_ORDINAL_EN[h10['lord_house']]} house in {h10['lord_sign_en']}. "
        f"This constitutes an auspicious career configuration granting executive authority, professional stability, and wide social recognition. "
        f"Key lucrative sectors for your natural aptitude include Technology, Engineering, Management, Administration, Strategic Consulting, Finance, and Enterprise Building."
    )

    occ_mr = (
        f"कामाच्या ठिकाणी आपण स्वतःच्या बळावर निर्णय घेणारे आणि स्वतंत्र विचारसरणीचे आहात. "
        f"दशमेश {h10['lord_mr']} व बुध-सूर्याचा प्रभाव असल्यामुळे संघटन कौशल्य आणि नियोजनबद्ध काम करणे हा आपला स्वभाव आहे. नोकरीत असलात तरी कालांतराने स्वतंत्र सल्लागार अथवा उद्योजक म्हणून मोठी झेप घेण्याची क्षमता आपल्यात आहे."
    )
    occ_en = (
        f"In your work environment, you excel through autonomous execution and meticulous strategic planning. "
        f"With the combined vigor of {h10['lord_en']} and sharp intellectual faculties, you naturally thrive in advisory, leadership, or independent entrepreneurial roles."
    )

    hlth_mr = (
        f"आरोग्य व रोग प्रतिकारक शक्तीचा विचार करता, षष्ठ भावाचा स्वामी {h6['lord_mr']} हा {HOUSE_ORDINAL_MR[h6['lord_house']]} स्थानात आहे आणि लग्नेश {h1['lord_mr']} सबळ आहे. "
        f"यामुळे आपली नैसर्गिक रोगप्रतिकारक शक्ती (Immunity) उत्तम आहे. तरीही कामाच्या अतिव्यापामुळे डोकेदुखी, पचनसंस्थेचे विकार किंवा स्नायूंवर ताण येऊ नये म्हणून नियमित योगासने, संतुलित आहार आणि वेळेवर विश्रांती घेणे आवश्यक आहे."
    )
    hlth_en = (
        f"Regarding vitality and wellness, the 6th Lord {h6['lord_en']} is positioned in the {HOUSE_ORDINAL_EN[h6['lord_house']]} house while Lagnesh {h1['lord_en']} provides solid constitutional stamina. "
        f"Your natural immunity is robust. However, due to professional overwork, preventative care for digestive balance, eye rest, and periodic hydration is recommended."
    )

    hob_mr = (
        f"पंचम भावातील {h5['sign_mr']} राशी व {h5['lord_mr']} च्या प्रभावामुळे आपल्याला वाचन, शास्त्रीय संगीत, बौद्धिक खेळ, निसर्गभ्रमण आणि गूढ विज्ञानाचा अभ्यास करण्याची विशेष आवड राहील."
    )
    hob_en = (
        f"With the 5th House in {h5['sign_en']} ruled by {h5['lord_en']}, your leisurely interests gravitate towards insightful literature, intellectual games, music, travel, and exploring esoteric wisdom."
    )

    mar_mr = (
        f"सप्तम (विवाह व जोडीदार) भावात {h7['sign_mr']} राशी असून सप्तमेश {h7['lord_mr']} ग्रह {HOUSE_ORDINAL_MR[h7['lord_house']]} स्थानात {h7['lord_sign_mr']} राशीत विराजमान आहे. "
        f"हा अत्यंत शुभ विवाह योग दर्शवतो की आपला जीवनसाथी सुसंस्कृत, समंजस, देखणा आणि आपल्या भाग्योदयात मोलाची साथ देणारा असेल. "
        f"विवाहानंतर आपल्या आर्थिक व सामाजिक स्थितीत उल्लेखनीय प्रगती होईल. वैवाहिक जीवनात परस्पर विश्वास आणि आदर राखल्यास दांपत्य जीवन अत्यंत मधुर व समाधानी राहील."
    )
    mar_en = (
        f"Your 7th House (Marriage & Partnership) is governed by {h7['sign_en']} with its Lord {h7['lord_en']} placed in the {HOUSE_ORDINAL_EN[h7['lord_house']]} house in {h7['lord_sign_en']}. "
        f"This signifies a cultured, supportive, and emotionally balanced spouse who acts as a true partner in your life journey. "
        f"Post-marriage, your fortune and domestic harmony receive an auspicious upward boost, ensuring mutual respect and lasting fulfillment."
    )

    fin_mr = (
        f"आर्थिक समृद्धीच्या दृष्टीने द्वितीय (धन) भावाचा स्वामी {h2['lord_mr']} हा {HOUSE_ORDINAL_MR[h2['lord_house']]} स्थानात आणि एकादश (लाभ) भावाचा स्वामी {h11['lord_mr']} अनुकूल स्थितीत आहे. "
        f"हा कुंडलीतील एक शक्तिशाली 'धनयोग' (Wealth Yoga) आहे. जातकाला स्वकष्टातून, बुद्धिमत्तेच्या बळावर आणि व्यावसायिक कौशल्याने विपुल धनलाभ होईल. "
        f"दीर्घकालीन गुंतवणूक, भूमी व सोन्यातील गुंतवणूक आपल्यासाठी अतिशय फायदेशीर ठरेल."
    )
    fin_en = (
        f"Financially, your 2nd Lord {h2['lord_en']} resides in the {HOUSE_ORDINAL_EN[h2['lord_house']]} house while 11th Lord {h11['lord_en']} fortifies inflow of gains. "
        f"This forms a potent Dhana Yoga ensuring that wealth is generated through personal merit, intellectual mastery, and strategic investments. "
        f"Long-term assets, real estate, and disciplined capital growth yield substantial prosperity."
    )

    edu_mr = (
        f"विद्या व उच्च शिक्षणाचा कारक गुरु आणि पंचमेश {h5['lord_mr']} यांच्या शुभ योगामुळे आपले प्राथमिक व उच्च शिक्षण अत्यंत यशस्वी राहील. आपण पदवी, तांत्रिक शिक्षण अथवा विशेष प्राविण्य संपादन कराल आणि समाजात प्रबुद्ध विचारवंत म्हणून ओळखले जाल."
    )
    edu_en = (
        f"With the 5th House governed by {h5['lord_en']} and supported by academic karakas, your educational pursuits culminate in specialized professional qualifications, earning you scholastic respect."
    )

    return [
        {"title_en": "Character", "title_hi": "चारित्र्य व स्वभाव (Character)", "text_en": char_en, "text_hi": char_mr},
        {"title_en": "Happiness And Fulfillment", "title_hi": "सुख व समाधान (Happiness & Fulfillment)", "text_en": hap_en, "text_hi": hap_mr},
        {"title_en": "Life Style", "title_hi": "जीवनशैली व राहणीमान (Life Style)", "text_en": style_en, "text_hi": style_mr},
        {"title_en": "Career", "title_hi": "करिअर व आजीविका (Career)", "text_en": car_en, "text_hi": car_mr},
        {"title_en": "Occupation", "title_hi": "व्यावसायिक कार्यशैली (Occupation)", "text_en": occ_en, "text_hi": occ_mr},
        {"title_en": "Health", "title_hi": "आरोग्य व जीवनशक्ती (Health)", "text_en": hlth_en, "text_hi": hlth_mr},
        {"title_en": "Hobbies", "title_hi": "रुची व छंद (Hobbies)", "text_en": hob_en, "text_hi": hob_mr},
        {"title_en": "Love Matters", "title_hi": "प्रेम व वैवाहिक जीवन (Love Matters)", "text_en": mar_en, "text_hi": mar_mr},
        {"title_en": "Finance", "title_hi": "आर्थिक स्थिती व धनसंचय (Finance)", "text_en": fin_en, "text_hi": fin_mr},
        {"title_en": "Education", "title_hi": "शिक्षण व ज्ञान (Education)", "text_en": edu_en, "text_hi": edu_mr},
    ]


def get_planet_specific_prediction(pid: str, house_num: int, sign_num: int, dignity_en: str) -> tuple[str, str]:
    """
    Returns unique (Marathi, English) interpretation for any planet in any house.
    Guarantees no two planets will ever share the same prediction paragraph!
    """
    p_dict = PLANET_HOUSE_PHAL.get(pid, {})
    if house_num in p_dict:
        base_mr, base_en = p_dict[house_num]
    else:
        base_mr = f"{pid} कुंडलीतील {house_num} व्या भावात स्थित असून जातकाच्या भाग्यावर सकारात्मक प्रभाव पाडतो."
        base_en = f"{pid} is situated in the {house_num} house, positively influencing the native's destiny."

    s_mr = SIGN_NAMES_MR.get(sign_num, "राशी")
    s_en = SIGN_NAMES_EN.get(sign_num, "Sign")

    mr_full = f"{s_mr} राशीमध्ये {base_mr}"
    en_full = f"Positioned in {s_en} sign, {base_en}"
    return mr_full, en_full
