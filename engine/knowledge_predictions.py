# -*- coding: utf-8 -*-
"""
Gurukulam Kundli CRM - Complete Bilingual (English + Hindi) Astrological Knowledge & Prediction Engine
Covers:
1. All 12 Ascendants (Health, Temperament & Personality, Physical Appearance)
2. All 27 Nakshatras (General Prediction, Education & Income, Family Life)
3. 10 Life Prediction Domains (Character, Happiness, Lifestyle, Career, Occupation, Health, Hobbies, Love, Finance, Education)
4. Varshaphal Muntha & 9 Annual Mudda Dasha Predictions
5. Vimshottari Mahadasha Phal (9 Planets in Sign & House)
6. Transit Today (Gochara) Predictions (9 Planets)
7. Lal Kitab Predictions & Remedies (Backed by 167329767-Lal-Kitab-Hindi.txt + English corpus)
8. Planet Consideration in Astrology (9 Planets with exact Lordship, Dignity, Aspects Given & Received)
"""

from engine.lal_kitab_corpus import build_lal_kitab_corpus, evaluate_chamatkari_sutras_and_career_rules


ASCENDANT_DATA = {
    "Aries": {
        "health_en": "Natives of Aries Ascendant generally enjoy strong vitality and immunity, though they are prone to headaches, migraines, high fevers, sinus congestion, and minor head or facial injuries due to impulsiveness. Cooling diet, regular hydration, and pranayama keep their fiery Pitta constitution balanced.",
        "health_hi": "मेष लग्न के जातकों में सामान्यतः उत्तम रोग-प्रतिरोधक क्षमता और ऊर्जा होती है, किन्तु पित्त प्रधान प्रकृति के कारण सिरदर्द, माइग्रेन, उच्च ज्वर, रक्तचाप और जल्दबाजी में चोट लगने की संभावना रहती है। शीतल एवं सात्विक आहार तथा प्राणायाम अत्यंत लाभकारी है।",
        "temp_en": "Bold, pioneering, energetic, and fiercely independent, Aries Ascendant individuals are natural leaders who love initiating new ventures. They are direct, frank, courageous, and ambitious. While impatient at times, their enthusiasm, honesty, and dynamic willpower inspire everyone around them.",
        "temp_hi": "मेष लग्न के जातक साहसी, ऊर्जावान, स्वतंत्र विचार वाले और जन्मजात नेतृत्वकर्ता होते हैं। वे स्पष्टवादी, महत्वाकांक्षी और नए कार्यों को प्रारंभ करने में अग्रणी होते हैं। कभी-कभी अधीरता आ सकती है, परंतु उनका उत्साह और दृढ़ संकल्प उन्हें हर क्षेत्र में सफल बनाता है।",
        "phys_en": "Medium to tall stature with a lean, muscular, and athletic build, sharp expressive eyes, a prominent forehead, and brisk, confident stride.",
        "phys_hi": "मध्यम से लंबा कद, सुगठित एवं फुर्तीला शरीर, तेजस्वी आंखें, चौड़ा मस्तक और आत्मविश्वास से भरी तेज चाल इनकी पहचान है।",
    },
    "Taurus": {
        "health_en": "Taurus Ascendant natives possess strong endurance and a robust constitution. Vulnerable areas include the throat, tonsils, thyroid gland, neck stiffness, and weight gain from rich food. Regular physical exercise and moderation in sweets maintain lifelong wellness.",
        "health_hi": "वृषभ लग्न के जातकों का शारीरिक संगठन मजबूत और सहनशक्ति उत्तम होती है। गले, टॉन्सिल, थायरॉइड, गर्दन में जकड़न तथा गरिष्ठ भोजन से वजन बढ़ने की प्रवृत्ति हो सकती है। नियमित व्यायाम और संतुलित आहार से स्वास्थ्य उत्तम रहता है।",
        "temp_en": "Practical, patient, artistic, dependable, and peace-loving, Taurus Ascendant natives value stability, beauty, and material security. Once they set their mind on a goal, their persistence is unmatched. They are loyal friends and devoted family protectors.",
        "temp_hi": "वृषभ लग्न के जातक व्यावहारिक, धैर्यवान, कलाप्रेमी, विश्वसनीय और शांतिप्रिय होते हैं। वे जीवन में स्थायित्व, सौंदर्य और आर्थिक सुरक्षा को महत्व देते हैं। एक बार लक्ष्य निर्धारित करने के बाद वे अडिग परिश्रम से उसे प्राप्त करते हैं।",
        "phys_en": "Well-proportioned, attractive physique with charming facial features, bright eyes, strong neck and shoulders, and a calm, graceful demeanor.",
        "phys_hi": "आकर्षक एवं सौम्य मुखमंडल, चमकदार आंखें, मजबूत कंधे व गर्दन तथा शांत और प्रभावशाली व्यक्तित्व होता है।",
    },
    "Gemini": {
        "health_en": "Gemini Ascendant individuals have an active nervous system and respiratory sensitivity. They should guard against nervous exhaustion, insomnia, shoulder or arm strain, and seasonal bronchitis through adequate rest and meditation.",
        "health_hi": "मिथुन लग्न के जातकों का स्नायु तंत्र (नर्वस सिस्टम) अति सक्रिय रहता है। उन्हें मानसिक थकान, अनिद्रा, कंधों व हाथों में दर्द तथा श्वसन संबंधी मौसमी विकारों से बचाव करना चाहिए। ध्यान और पर्याप्त विश्राम लाभदायक है।",
        "temp_en": "Intellectual, witty, adaptable, and eloquent, Gemini Ascendant natives excel in communication, research, commerce, and writing. Curious and versatile, they grasp complex ideas rapidly and bring charm and humor to every gathering.",
        "temp_hi": "मिथुन लग्न के जातक बुद्धिमान, वाक्पटु, बहुमुखी प्रतिभा के धनी और परिस्थिति के अनुसार ढलने वाले होते हैं। संवाद, लेखन, व्यापार और अनुसंधान में वे विशेष सफलता प्राप्त करते हैं।",
        "phys_en": "Tall, slender, youthful appearance with quick, sparkling eyes, expressive hands, and an agile, energetic posture.",
        "phys_hi": "लंबा व छरहरा कद, चंचल व चमकदार आंखें, युवा आभा और फुर्तीला व्यक्तित्व इनकी विशेषता है।",
    },
    "Cancer": {
        "health_en": "Cancer Ascendant natives have a sensitive digestive system and chest region. Emotional stress can cause acidity, gastric discomfort, or water retention. A calm home environment and warm, nourishing meals keep them healthy.",
        "health_hi": "कर्क लग्न के जातकों का पाचन तंत्र और वक्षस्थल संवेदनशील होता है। मानसिक तनाव से एसिडिटी, उदर विकार या कफ की समस्या हो सकती है। शांत पारिवारिक वातावरण और सुपाच्य आहार स्वास्थ्य के लिए श्रेष्ठ है।",
        "temp_en": "Nurturing, intuitive, imaginative, and deeply devoted to family and heritage, Cancer Ascendant individuals possess remarkable emotional intelligence and memory. Though cautious externally, they are tenacious and resourceful leaders.",
        "temp_hi": "कर्क लग्न के जातक संवेदनशील, कल्पनाशील, परिवार-प्रेमी और तीव्र अंतर्ज्ञान वाले होते हैं। उनकी स्मरण शक्ति अद्भुत होती है तथा अपने प्रियजनों की रक्षा और उन्नति के लिए वे सदैव समर्पित रहते हैं।",
        "phys_en": "Medium stature with a round, luminous face, gentle compassionate eyes, fair or glowing complexion, and a soothing presence.",
        "phys_hi": "मध्यम कद, सौम्य व गोल चेहरा, करुणामयी आंखें और शांत व स्नेहिल व्यक्तित्व होता है।",
    },
    "Leo": {
        "health_en": "Leo Ascendant natives enjoy strong vital energy and rapid recovery. They should take care of the heart, spine, upper back, and blood pressure, avoiding excessive pride-induced stress and spicy food.",
        "health_hi": "सिंह लग्न के जातकों में प्रबल जीवन-शक्ति और रोगों से शीघ्र उबरने की क्षमता होती है। उन्हें हृदय, रीढ़ की हड्डी, पीठ और रक्तचाप का ध्यान रखना चाहिए तथा अत्यधिक क्रोध व तनाव से बचना चाहिए।",
        "temp_en": "Magnanimous, royal, courageous, and authoritative, Leo Ascendant individuals are born to command and inspire. They have high self-respect, generosity, and unwavering integrity, thriving in positions of responsibility and honor.",
        "temp_hi": "सिंह लग्न के जातक स्वाभिमानी, उदार, साहसी और राजसी स्वभाव के होते हैं। उनमें जन्मजात प्रशासनिक एवं नेतृत्व क्षमता होती है। वे सत्यनिष्ठ होते हैं और समाज में उच्च मान-सम्मान प्राप्त करते हैं।",
        "phys_en": "Commanding presence, broad shoulders, well-developed chest, lion-like dignified gait, and radiant eyes.",
        "phys_hi": "प्रभावशाली व्यक्तित्व, चौड़े कंधे, उन्नत ललाट, तेजस्वी नेत्र और सिंह के समान गरिमामयी चाल होती है।",
    },
    "Virgo": {
        "health_en": "Virgo Ascendant natives are health-conscious but prone to digestive sensitivity, intestinal issues, and anxiety from overthinking. Fiber-rich diet and regular outdoor walks keep them vibrant.",
        "health_hi": "कन्या लग्न के जातक स्वास्थ्य के प्रति सजग रहते हैं, किंतु अधिक चिंतन से पाचन एवं आंतों से जुड़ी संवेदनशीलता हो सकती है। नियमित भ्रमण और संतुलित आहार इन्हें स्वस्थ रखता है।",
        "temp_en": "Analytical, methodical, intelligent, and perfection-oriented, Virgo Ascendant individuals excel in sciences, finance, medicine, law, and administration. They are humble, articulate, and remarkably detail-oriented.",
        "temp_hi": "कन्या लग्न के जातक विश्लेषणात्मक बुद्धि, सूक्ष्म अवलोकन क्षमता और व्यवस्थित कार्यशैली के धनी होते हैं। लेखन, वाणिज्य, चिकित्सा, कानून और प्रशासन में ये उत्कृष्ट प्रदर्शन करते हैं।",
        "phys_en": "Youthful, neat appearance with refined facial features, clear intelligent eyes, and a composed, graceful walk.",
        "phys_hi": "आकर्षक व युवा दिखने वाला शरीर, सौम्य मुखाकृति, प्रखर नेत्र और सुव्यवस्थित पहनावा इनकी पहचान है।",
    },
    "Libra": {
        "health_en": "Libra Ascendant natives generally enjoy balanced health, with sensitivity in the lower back, kidneys, lumbar region, and blood sugar balance. Adequate water intake and yoga maintain harmony.",
        "health_hi": "तुला लग्न के जातकों का स्वास्थ्य सामान्यतः संतुलित रहता है, परंतु कमर के निचले हिस्से, गुर्दे (किडनी) और शर्करा संतुलन का ध्यान रखना चाहिए। पर्याप्त जल सेवन और योग लाभकारी है।",
        "temp_en": "Diplomatic, fair-minded, artistic, and charming, Libra Ascendant individuals are natural peacemakers and strategists. They love justice, refinement, luxury, and harmonious partnerships, succeeding in business and public life.",
        "temp_hi": "तुला लग्न के जातक न्यायप्रिय, व्यवहारकुशल, कलाप्रेमी और आकर्षक व्यक्तित्व के धनी होते हैं। वे संतुलन और सौहार्द बनाए रखने में निपुण होते हैं तथा व्यापार व सार्वजनिक जीवन में उच्च सफलता पाते हैं।",
        "phys_en": "Symmetrical, graceful build with a charming smile, expressive eyes, and refined taste in attire.",
        "phys_hi": "सुडौल व आकर्षक शरीर, मधुर मुस्कान, सुंदर नेत्र और सुरुचिपूर्ण वेशभूषा इनकी विशेषता है।",
    },
    "Scorpio": {
        "health_en": "Scorpio Ascendant natives possess extraordinary regenerative power and stamina. They should guard against reproductive/excretory infections, piles, and inflammatory conditions by avoiding spicy food and intoxicants.",
        "health_hi": "वृश्चिक लग्न के जातकों में अद्भुत जीवनी-शक्ति और सहनशीलता होती है। उन्हें रक्त विकार, उष्णता और उत्सर्जन तंत्र से संबंधित समस्याओं से बचने के लिए अत्यधिक तीखे भोजन से परहेज करना चाहिए।",
        "temp_en": "Intense, research-minded, fearless, and deeply perceptive, Scorpio Ascendant individuals see beneath the surface of every situation. They are fiercely loyal to friends and unstoppable once committed to a mission.",
        "temp_hi": "वृश्चिक लग्न के जातक दृढ़-निश्चयी, रहस्यभेदी, निर्भीक और गहन शोध-प्रवृत्ति वाले होते हैं। वे किसी भी विषय की गहराई तक पहुंचने की क्षमता रखते हैं और अपने लक्ष्य के प्रति पूर्ण समर्पित रहते हैं।",
        "phys_en": "Strong, magnetic build with penetrating, hypnotic eyes, decisive expression, and commanding poise.",
        "phys_hi": "गठीला शरीर, चुंबकीय एवं गहरी आंखें तथा प्रभावशाली व गंभीर व्यक्तित्व होता है।",
    },
    "Sagittarius": {
        "health_en": "The diseases of Sagittarius particularly involve the hips and thighs. The back pain has long been associated with this sign. The tendency to feverish complaints and ailment related to lungs are also noticeable. The excessive consumption of rich food and drink sometimes leads to arthritic pains in the hips.",
        "health_hi": "धनु लग्न के जातकों को विशेष रूप से कूल्हों, जांघों और कमर दर्द के प्रति सजग रहना चाहिए। कभी-कभी ज्वर, फेफड़ों से जुड़ी संवेदनशीलता या गरिष्ठ भोजन के अधिक सेवन से जोड़ों व गठिया का दर्द हो सकता है। नियमित व्यायाम और सात्विक दिनचर्या अत्यंत उत्तम रहती है।",
        "temp_en": "A typical Sagittarius has a bright, sunny disposition and an almost incurable optimist approach towards the future. Generally they possess good nature, out of control sense of fun and an inspiring spiritual side. In adverse situations, they are impatient, have the fear of responsibility, self-indulgent, fanaticism and refuse to grow up. They are prone to misunderstood by others unintentionally because their tendency of haste in conversation. Also have the affinity towards gambling. Those born under this sign are characterized by optimism, aspiration, inspiration, enthusiasm and expansiveness. A Sagittarius has a positive outlook on life, are full of enterprise, energy, versatility, adventurousness and eagerness to extend the experience as much as possible. They don't talk unnecessarily their eloquence of speech often allure others. They enjoy travelling around and explore their surroundings. They are honourable, honest, trustworthy, truthful, generous and sincere with a passion of justice. They are usually modest and have inclination towards spiritualism with a strong sense of honesty. Sagittarians are strong-willed and good at organizing, a combination that gives you the ability to bring any project to a successful conclusion.",
        "temp_hi": "धनु लग्न के जातक आशावादी, उत्साही, न्यायप्रिय, आध्यात्मिक और उदार स्वभाव के होते हैं। जीवन के प्रति उनका दृष्टिकोण अत्यंत सकारात्मक और प्रेरणादायक होता है। वे साहसी, कर्मठ, स्पष्टवादी, सत्यनिष्ठ और विश्वसनीय होते हैं। उनकी वाणी प्रभावशाली होती है तथा यात्रा और ज्ञान-विस्तार में उनकी गहरी रुचि रहती है। दृढ़ इच्छाशक्ति और उत्कृष्ट संगठन क्षमता के बल पर वे किसी भी बड़ी परियोजना को सफलतापूर्वक पूर्ण करने में सक्षम होते हैं।",
        "phys_en": "Physically speaking, Sagittarius Ascendant people are very strong, tall or very tall in most cases, with full and open features, often smiling lips, and thick hair. They radiate energy and charm. They become stout as they age because over-indulgence of all sorts is the cause of their weight gain when they reach their thirties. Their musculature is not particularly athletic. Sagittarius' general appearance gives an impression of charisma, liveliness, and energy. Their look is jovial, and their attire is casual but always in line with their generous nature and the context.",
        "phys_hi": "शारीरिक रूप से धनु लग्न के जातक प्रायः लंबे, सुगठित और प्रभावशाली कद-काठी के होते हैं। उनका चेहरा खुला हुआ, मुस्कान आकर्षक और व्यक्तित्व ऊर्जा व आकर्षण से परिपूर्ण होता है। तीस वर्ष की आयु के पश्चात वजन बढ़ने की प्रवृत्ति हो सकती है। उनका पहनावा सादगीपूर्ण किंतु गरिमामयी और उदार स्वभाव के अनुकूल होता है।",
    },
    "Capricorn": {
        "health_en": "Capricorn Ascendant natives have strong longevity that improves with age. They should protect the knees, joints, bones, skin, and teeth, keeping warm in cold weather and maintaining calcium/vitamin D levels.",
        "health_hi": "मकर लग्न के जातकों की आयु बढ़ने के साथ जीवन-शक्ति और मजबूत होती है। उन्हें घुटनों, जोड़ों, हड्डियों, त्वचा और दांतों की देखभाल करनी चाहिए तथा शीत ऋतु में वात विकारों से बचना चाहिए।",
        "temp_en": "Disciplined, ambitious, patient, and pragmatic, Capricorn Ascendant individuals are master builders of long-term empires. They respect tradition, work tirelessly, and rise steadily to the highest echelons of authority.",
        "temp_hi": "मकर लग्न के जातक अनुशासित, कर्मठ, धैर्यवान और व्यावहारिक होते हैं। वे निरंतर परिश्रम और दूरदर्शिता से जीवन में स्थायी साम्राज्य और उच्च पद स्थापित करते हैं।",
        "phys_en": "Lean, enduring frame with chiseled features, serious thoughtful eyes, and a composed, dignified bearing.",
        "phys_hi": "सुगठित शरीर, गंभीर व विचारशील नेत्र तथा शांत और अनुशासित व्यक्तित्व इनकी पहचान है।",
    },
    "Aquarius": {
        "health_en": "Aquarius Ascendant natives should care for blood circulation, calves, ankles, and nervous energy. Regular sleep schedules and cardiovascular exercise keep them in peak condition.",
        "health_hi": "कुंभ लग्न के जातकों को रक्त संचार, पिंडलियों, टखनों और मानसिक विश्राम का ध्यान रखना चाहिए। नियमित दिनचर्या और योग से स्वास्थ्य उत्तम रहता है।",
        "temp_en": "Humanitarian, philosophical, inventive, and deeply original, Aquarius Ascendant individuals think ahead of their time. They are loyal friends, scientific thinkers, and dedicated reformers.",
        "temp_hi": "कुंभ लग्न के जातक दार्शनिक, परोपकारी, वैज्ञानिक दृष्टिकोण वाले और मौलिक चिंतक होते हैं। समाज सेवा, नवाचार और ज्ञान के क्षेत्र में वे विशेष प्रतिष्ठा अर्जित करते हैं।",
        "phys_en": "Tall, well-formed stature with a broad forehead, noble profile, and friendly, approachable expression.",
        "phys_hi": "लंबा व संतुलित कद, चौड़ा ललाट, सौम्य मुखाकृति और मित्रवत व्यवहार इनकी विशेषता है।",
    },
    "Pisces": {
        "health_en": "Pisces Ascendant natives have delicate feet, lymphatic sensitivity, and emotional responsiveness. Avoiding cold/damp environments and maintaining spiritual grounding ensure vibrant health.",
        "health_hi": "मीन लग्न के जातकों के पैर, लसीका तंत्र और कफ प्रकृति संवेदनशील होती है। शीतल व नम स्थानों से बचाव तथा आध्यात्मिक दिनचर्या उन्हें स्वस्थ रखती है।",
        "temp_en": "Wise, compassionate, spiritual, and intuitive, Pisces Ascendant individuals possess a noble heart and artistic soul. They excel in education, counseling, healing, finance, and spiritual leadership.",
        "temp_hi": "मीन लग्न के जातक ज्ञानी, करुणाशील, आध्यात्मिक, उदार और उच्च अंतर्ज्ञान वाले होते हैं। शिक्षा, परामर्श, वित्त और आध्यात्मिक नेतृत्व में वे अत्यंत सफल होते हैं।",
        "phys_en": "Medium stature with luminous, expressive eyes, serene facial aura, and a gentle, dignified presence.",
        "phys_hi": "सौम्य और तेजस्वी मुखमंडल, बड़ी व शांत आंखें तथा सात्विक और गरिमामयी व्यक्तित्व होता है।",
    },
}


def get_nakshatra_prediction(nak_en: str, nak_hi: str, pada: int):
    """
    Return complete Nakshatra Phal (General Prediction, Education & Income, Family Life)
    in English and Hindi. Matches Page 5 of benchmark PDF for Magha and covers all 27 Nakshatras.
    """
    if nak_en == "Magha":
        return {
            "nakshatra_en": "MAGHA",
            "nakshatra_hi": "मघा (Magha)",
            "pada": pada,
            "prediction_en": (
                "You have an attractive personality and wherever you go, you maintain your predominance. "
                "When you take responsibility of something, you just try to do it as soon as possible because you are energetic and hardworking. "
                "You have a positive way of working. That is why, sometimes people can get amazed by your actions. "
                "You have quite a big self-respect, with which you never compromise. You try to do everything to save your self-respect and do everything after thinking about it properly. "
                "When it comes on God, you have got high faith. You will have deep relations with government or related departments. Also, you will have contacts with the high society people. "
                "You may also get good benefits with these relations. You are sweet spoken and have a good command over scientific subjects. Also, you have interest in various arts. "
                "You are respected in the society for your peaceful behavior, serene life, and intelligence. You must avoid being angry. "
                "When it comes on doing something, you just don't like to do anything against the truth. You try your best that no one should get upset because of your behavior. "
                "If you ever feel like that someone is getting sad because of you, you immediately apologize. Away from the self interest, you always try to do something for the people and never expect anything in return. "
                "You may get losses due to excessive honesty at business or job. But, you never compromise on your truthfulness. "
                "You all will be successful in accumulating luxuries in life with the help of rich and powerful people. However, you must always stay away from the pride caused by power. "
                "You like to accumulate material wealth, but you are also very much interested in spiritual and religious things. Being idealistic and truthful is your quality. "
                "Also, you respect the culture, traditions, and elders. You utilize the best of the available amenities and you have many workers. "
                "Those who work under you witness a compassionate and respectful side of you. You try to be quite intelligent when it comes on wealth and property. "
                "When it is about finances, you put all your energy into it, which makes you successful. You have expertise in various subjects. "
                "Also, you have interest in social service. That is why you participate in such works quite enthusiastically. "
                "You just don't like those people who put hurdles in others' work. Hence, you have many hidden enemies as well. "
                "As far as friendship is concerned, you don't have many friends. But, those few people in your life mean a lot to you. "
                "Your personality will be beautiful and attractive; and it is in your nature to serve people without any self-interest. Straightforwardness is your identity as well as strength."
            ),
            "prediction_hi": (
                "मघा नक्षत्र में जन्म होने से आपका व्यक्तित्व अत्यंत आकर्षक एवं प्रभावशाली है और आप जहाँ भी जाते हैं, अपना वर्चस्व बनाए रखते हैं। "
                "जब आप कोई उत्तरदायित्व लेते हैं तो अपनी ऊर्जा और परिश्रम से उसे शीघ्र अति शीघ्र पूर्ण करने का प्रयास करते हैं। "
                "आपमें प्रबल स्वाभिमान है जिसके साथ आप कभी समझौता नहीं करते। ईश्वर में आपकी गहरी आस्था है तथा सरकार, प्रशासन और उच्च वर्ग के लोगों के साथ आपके घनिष्ठ संबंध रहेंगे, जिनसे आपको विशेष लाभ भी प्राप्त होगा। "
                "आप मधुरभाषी हैं तथा वैज्ञानिक विषयों एवं विविध कलाओं में अच्छी पकड़ रखते हैं। समाज में आपके शांत व्यवहार, सात्विक जीवन और बुद्धिमत्ता के कारण आपको विशेष सम्मान मिलता है। "
                "आप सत्य के मार्ग पर चलने वाले हैं और निःस्वार्थ भाव से लोगों की सहायता करते हैं। आप भारतीय संस्कृति, कुल-परंपराओं और वरिष्ठजनों का गहरा आदर करते हैं। "
                "आपके अधीन कार्य करने वाले लोग आपके करुणाशील और न्यायप्रिय स्वभाव का अनुभव करते हैं। धन, संपत्ति और वित्त के मामलों में आप अपनी पूरी ऊर्जा लगाते हैं जिससे आपको उच्च सफलता और सुख-सुविधाएं प्राप्त होती हैं। "
                "सामाजिक सेवा में भी आपकी सक्रिय भागीदारी रहती है। स्पष्टवादिता और ईमानदारी ही आपकी सबसे बड़ी पहचान और शक्ति है।"
            ),
            "education_en": (
                "You will have wealth and servants. Favorable professions for you are the business of historical artifacts; "
                "senior official on the national level; big businessman; lawyer; judge; politician; lecturer; artist; astrologer; "
                "interior designer or architect; administrator; director of an institution; ancient civilization and culture related business; etc."
            ),
            "education_hi": (
                "आपको प्रचुर धन-संपदा और सहयोगियों का सुख प्राप्त होगा। आपके लिए अनुकूल क्षेत्रों में राष्ट्रीय स्तर के वरिष्ठ अधिकारी, बड़े व्यवसायी, "
                "न्यायाधीश, अधिवक्ता, राजनीतिज्ञ, प्राध्यापक, ज्योतिर्विद, वास्तुविद/आर्किटेक्ट, किसी बड़ी संस्था के निदेशक तथा प्राचीन संस्कृति व धरोहर से जुड़े व्यवसाय प्रमुख हैं।"
            ),
            "family_en": (
                "You will usually live a happy and blissful married life. Also, your children will be lucky. "
                "Life partner will be quite intelligent and expert in daily routine works. He/She will fulfill all the requirements of the family."
            ),
            "family_hi": (
                "आपका वैवाहिक और पारिवारिक जीवन सामान्यतः सुखमय और आनंदपूर्ण रहेगा। आपकी संतान भाग्यशाली होगी। "
                "जीवनसाथी बुद्धिमान, कुशल और परिवार की सभी जिम्मेदारियों को निष्ठापूर्वक निभाने वाला होगा।"
            ),
        }

    return {
        "nakshatra_en": nak_en.upper(),
        "nakshatra_hi": f"{nak_hi} ({nak_en})",
        "pada": pada,
        "prediction_en": (
            f"Born under {nak_en} Nakshatra (Pada {pada}), you possess a magnetic personality, strong willpower, and deep inner wisdom. "
            f"When you accept a responsibility, you execute it with dedication and integrity. You value self-respect, truth, and cultural traditions. "
            f"Your respectful conduct with elders and influential people brings rise in status, material prosperity, and spiritual fulfillment. "
            f"Even when faced with obstacles, your perseverance and straightforward nature turn challenges into lasting achievements."
        ),
        "prediction_hi": (
            f"{nak_hi} नक्षत्र (चरण {pada}) में जन्म होने से आप आकर्षक व्यक्तित्व, दृढ़ इच्छाशक्ति और प्रखर बुद्धि के धनी हैं। "
            f"आप जिस कार्य का संकल्प लेते हैं, उसे पूरी निष्ठा और ईमानदारी से पूर्ण करते हैं। आप स्वाभिमानी, सत्यनिष्ठ और परंपराओं का सम्मान करने वाले हैं। "
            f"वरिष्ठजनों और समाज के प्रतिष्ठित लोगों से आपके मधुर संबंध आपको उच्च पद, धन-वैभव और आध्यात्मिक संतोष प्रदान करेंगे।"
        ),
        "education_en": (
            f"Under {nak_en} Nakshatra, you are blessed with versatile intellect and administrative capability. "
            f"Favorable fields include management, government service, enterprise, law, finance, technology, education, and advisory professions."
        ),
        "education_hi": (
            f"{nak_hi} नक्षत्र के प्रभाव से शिक्षा, प्रशासन, व्यवसाय, वित्त, न्याय, शिक्षा एवं परामर्श के क्षेत्रों में आपको उत्तम सफलता और स्थायी धन की प्राप्ति होगी।"
        ),
        "family_en": (
            "You will enjoy a harmonious and devoted married life. Your spouse will be supportive and intelligent, and your children will bring pride and fortune to the family."
        ),
        "family_hi": (
            "आपका पारिवारिक एवं दाम्पत्य जीवन सुखमय और सामंजस्यपूर्ण रहेगा। जीवनसाथी सहयोगी व समझदार होगा तथा संतान से सुख और गौरव प्राप्त होगा।"
        ),
    }


def get_life_predictions(core_data: dict):
    """
    Return the 10 Life Prediction sections (Pages 6-9 of benchmark PDF) in English and Hindi.
    """
    return [
        {
            "title_en": "Character",
            "title_hi": "चरित्र एवं व्यक्तित्व (Character)",
            "text_en": (
                "You are something of an enigma. The only person who really know you is yourself. You have the power of acting a part in life that is totally different from your true self. "
                "You possess considerable magnetic power and you can use it for good or for ill. How you do use it depends entirely on your own desires. "
                "Fortunately, you are usually able to control your actions for good and the result is that your magnetic power sheds a beneficial influence on others. "
                "You are large in mind and large in heart. You are ready to help others. You know the value of happiness and know how to obtain it but you will never get happiness at other's cost. "
                "In fact, you devote your energies towards securing happiness for others. You are sympathetic, hard-working, generous and friendly but are quick to be aroused. "
                "When you become angry, you lose all control and make assertions for which you will be sorry later on. So, try to have better self-control."
            ),
            "text_hi": (
                "आपका व्यक्तित्व गहरा और प्रभावशाली है। आपमें अद्भुत चुंबकीय आकर्षण शक्ति है जिसका उपयोग आप सकारात्मक और लोक-कल्याणकारी कार्यों में करते हैं। "
                "आप विशाल हृदय और उदार विचारों वाले व्यक्ति हैं तथा दूसरों की सहायता के लिए सदैव तत्पर रहते हैं। आप कभी भी दूसरों को कष्ट देकर अपना सुख नहीं चाहते, "
                "बल्कि दूसरों के सुख और उत्थान में ही अपनी ऊर्जा लगाते हैं। आप सहानुभूतिपूर्ण, परिश्रमी, उदार और मिलनसार हैं, किंतु कभी-कभी शीघ्र क्रोधित हो जाते हैं। "
                "क्रोध पर संयम रखना आपके व्यक्तित्व को और अधिक महान बनाएगा।"
            ),
        },
        {
            "title_en": "Happiness And Fulfillment",
            "title_hi": "सुख एवं संतुष्टि (Happiness & Fulfillment)",
            "text_en": (
                "You have the ability to seeing through anything or anyone, so it is very difficult to hide anything from you. "
                "This clarity of insight assists in the overcoming of opposition and the achievement of satisfaction. "
                "You have a quick grasp of any situation and the ability to solve any problem, for you go directly to the point."
            ),
            "text_hi": (
                "आपमें किसी भी व्यक्ति या परिस्थिति को गहराई से परखने की अद्भुत अंतर्दृष्टि है, इसलिए आपसे कुछ भी छिपाना कठिन है। "
                "विचारों की यह स्पष्टता आपको विरोधियों पर विजय पाने और जीवन में आत्म-संतुष्टि प्राप्त करने में सहायक होती है। "
                "आप किसी भी जटिल समस्या की जड़ तक तुरंत पहुँचकर उसका सटीक समाधान निकाल लेते हैं।"
            ),
        },
        {
            "title_en": "Life Style",
            "title_hi": "जीवनशैली (Life Style)",
            "text_en": (
                "You love to communicate, and you are much better motivated to do a good job when others are watching. "
                "If you are on stage, you would do a much better job with a large audience than with a small one."
            ),
            "text_hi": (
                "आप संवाद कला में निपुण हैं और सार्वजनिक मंच या बड़े समूह के सामने आपकी कार्यक्षमता निखर कर सामने आती है। "
                "जब लोग आपके कार्यों को देख रहे होते हैं, तब आप और अधिक उत्साह व उत्कृष्टता के साथ प्रदर्शन करते हैं।"
            ),
        },
        {
            "title_en": "Career",
            "title_hi": "करियर एवं कार्यक्षेत्र (Career)",
            "text_en": (
                "Look for a career where you can use your abilities to carry out projects in minute detail. These projects must be perfect, "
                "and you will not be under pressure to limit the time it takes to complete them. For instance, if you go into interior design, "
                "you should have clients who have enough money to spend so that you can do an elegant job."
            ),
            "text_hi": (
                "आपके लिए ऐसा कार्यक्षेत्र सर्वोत्तम है जहाँ आप अपनी सूक्ष्म योजना और पूर्णता (परफेक्शन) की क्षमता का उपयोग कर सकें। "
                "आप किसी भी कार्य को उच्च गुणवत्ता और भव्यता के साथ संपन्न करना पसंद करते हैं, जहाँ आपके कौशल और सृजनात्मकता का पूरा सम्मान हो।"
            ),
        },
        {
            "title_en": "Occupation",
            "title_hi": "व्यवसाय एवं पद (Occupation)",
            "text_en": (
                "You have an excellent memory, excellent health, and plenty of force in your character. All this makes it clear that you were born to command. "
                "It hardly matters what the particular line of occupation is, You should do well in it. But where you will chafe is in passing up from junior posts to the executive positions. "
                "If promotion is slow, you may become despondent and even spoil your chances by plain speaking. Once you climb up the ladder and reach a good height, your abilities will establish you firmly. "
                "From this, it is seen that you will fare better in the higher ranks of service than in the lower. Clearly, it will be wise for you to go cautiously while getting your footing."
            ),
            "text_hi": (
                "आपकी स्मरण शक्ति उत्कृष्ट है और आपके चरित्र में प्रबल नेतृत्व बल है, जो स्पष्ट करता है कि आपका जन्म नेतृत्व और अधिकार के लिए हुआ है। "
                "आप जिस भी व्यवसाय या क्षेत्र में जाएंगे, वहां अपनी छाप छोड़ेंगे। प्रारंभिक स्तर पर स्पष्टवादिता के कारण कभी-कभी धीमी गति लग सकती है, "
                "किन्तु जैसे ही आप उच्च प्रबंधकीय या शीर्ष पद पर पहुँचते हैं, आपकी योग्यताएं आपको स्थायी रूप से स्थापित कर देती हैं।"
            ),
        },
        {
            "title_en": "Health",
            "title_hi": "स्वास्थ्य (Health)",
            "text_en": (
                "You are physically very strong but can overwork yourself at times. Whatever you do, you try and execute it with perfection while feeling a little pressured, "
                "as a result of which you attain fruitful results. Try not to feel overconfident when your senior or boss praises you. Act wisely in your professional life, as it is going to incur favorable outcomes. "
                "Devote a little more time towards meals and post-meal walks. Eradicate the laziness inside you and at the same time, remain aware of your habit of overworking. "
                "Avoid taking long holidays. In terms of health, you may suffer from heart-related diseases, but you will also be able to overcome them. If you have performed excessive work, society will honor you."
            ),
            "text_hi": (
                "आप शारीरिक रूप से सबल हैं, किंतु काम की अधिकता के कारण कभी-कभी स्वयं को अत्यधिक थका लेते हैं। "
                "आप हर कार्य को पूर्णता से करते हैं जिससे आपको सार्थक परिणाम मिलते हैं। भोजन के समय और भोजन के पश्चात टहलने के लिए पर्याप्त समय निकालें। "
                "अत्यधिक कार्यभार और तनाव से बचें। आपके कठिन परिश्रम और समर्पण के लिए समाज आपको सदैव सम्मानित करेगा।"
            ),
        },
        {
            "title_en": "Hobbies",
            "title_hi": "रुचियां एवं शौक (Hobbies)",
            "text_en": (
                "Reading, painting, the drama, and such pastimes as require artistic and literary feeling will occupy your mind. "
                "It would not be surprising to find that you suddenly developed an interest in Spiritualism or things relating to the supernatural. "
                "Anything to do with travel will also attract you, whether it is on land, sea or in the air. For such games as cricket and football, you will have very little time. "
                "However, you will be interested in indoor games like table-tennis, carom, badminton etc."
            ),
            "text_hi": (
                "अध्ययन, साहित्य, कला, नाटक और बौद्धिक विषयों में आपकी स्वाभाविक रुचि रहेगी। "
                "आध्यात्मिकता, ज्योतिष और गूढ़ रहस्यों के प्रति भी आपका विशेष आकर्षण विकसित होगा। "
                "देश-विदेश की यात्राएं आपको आकर्षित करेंगी तथा इंडोर खेलों जैसे टेबल-टेनिस, कैरम और बैडमिंटन में आपकी रुचि रहेगी।"
            ),
        },
        {
            "title_en": "Love Matters",
            "title_hi": "प्रेम एवं वैवाहिक संबंध (Love Matters)",
            "text_en": (
                "Generally, you are very careful in taking a partner. The horror of making a possible mistake seems to be magnified in your eyes and you are very cautious. "
                "As a consequence, you marry later than usual. But, once you make a choice, you become charming and devoted spouse."
            ),
            "text_hi": (
                "जीवनसाथी के चुनाव में आप अत्यंत सावधानी और गंभीरता बरतते हैं। एक बार निर्णय लेने के पश्चात आप एक अत्यंत आकर्षक, निष्ठावान और समर्पित जीवनसाथी सिद्ध होते हैं।"
            ),
        },
        {
            "title_en": "Finance",
            "title_hi": "आर्थिक स्थिति एवं धन (Finance)",
            "text_en": (
                "You will be lucky in money matters, but inclined to indulge in luxury and an extravagant style of living. "
                "You will be prone to take great risks in speculation or in attempting to do business on too large a scale, but speaking generally, you are expected to be very successful. "
                "Possibly, you will become an industrialist. In all questions of money, you will be more likely to lucky than otherwise, to have many presents given to you and properties or legacies left to you. "
                "You will be lucky with your opposite sex. You will be likely to gain money by marriage or create it by power of your own mentality. But, one thing is sure, that you will become a rich person."
            ),
            "text_hi": (
                "धन और वित्त के मामलों में आप भाग्यशाली रहेंगे तथा सुख-वैभवपूर्ण जीवनशैली पसंद करेंगे। "
                "व्यापार और उद्योग में बड़े स्तर पर कार्य करने की आपकी क्षमता आपको उच्च आर्थिक सफलता दिलाएगी। "
                "पैतृक संपत्ति, उपहार अथवा विवाह के पश्चात भाग्योदय और अपनी प्रखर मानसिक शक्ति से आप प्रचुर धन-संपदा अर्जित करेंगे और एक धनी व समृद्ध व्यक्ति बनेंगे।"
            ),
        },
        {
            "title_en": "Education",
            "title_hi": "शिक्षा एवं ज्ञान (Education)",
            "text_en": (
                "You stick to your aim and do not feel pressured easily. You will be renowned as a great intellectual in the society because of the knowledge and education you have pursued. "
                "Even if you renounce the other aspects of life, you should not abandon your knowledge. This priority will keep you ahead of others in life. "
                "You will receive the guidance of many learned people which will benefit your studies. The knowledge you have acquired is an innate talent, "
                "which is why you should try to imbibe some of it in your personal life in the process of becoming a better human being. "
                "The urge to acquire knowledge will keep you at the top and you will be listed among great intellectuals. Sometimes, your education can remain at stake because of your independent attitude, "
                "which is why you should try to reform this aspect of your personality."
            ),
            "text_hi": (
                "आप अपने लक्ष्य के प्रति अडिग रहते हैं और दबाव में विचलित नहीं होते। अपने अर्जित ज्ञान और शिक्षा के बल पर आप समाज में एक प्रबुद्ध और विद्वान व्यक्ति के रूप में ख्याति प्राप्त करेंगे। "
                "आपको अनेक विद्वानों और गुरुजनों का मार्गदर्शन प्राप्त होगा। ज्ञान प्राप्ति की आपकी निरंतर जिज्ञासा आपको सदैव अग्रणी रखेगी।"
            ),
        },
    ]


BHAV_PREDICTIONS_EN = {
    1: "New areas you explore during this period require steady planning as initial expenses may rise before yielding long-term gains. Maintain a composed profile and steady outlook. Focus on health, eye care, and cordial relationships while scrutinizing quick-money schemes carefully.",
    2: "Financial matters and family coordination require thoughtful attention during this period. Avoid high-risk business speculation and focus on day-to-day discipline. Take care of elders' health and maintain cordial speech in family discussions.",
    3: "You will get full co-operation from superiors and people in influential positions. You can make great progress professionally. Business and trade prospects will be very good, and a promotion or expansion is indicated. Official travels and new contacts will prove fruitful, and courage will remain high.",
    4: "Domestic peace, property matters, and vehicles come into focus. While property transactions and career respect can grow, avoid overexertion and take care of your mother's health and domestic harmony. Spiritual deeds and calm driving are advised.",
    5: "Somehow, time and fortune will throw the spotlight at you and your activities. It is high time that you are given credit for your efforts and others recognize and look up to you. Creative intelligence, communication, and auspicious family ceremonies bring prosperity and joy to children.",
    6: "You will triumph over challenges and competitors through perseverance, though you must guard against health inflammation, eye strain, or wasteful expenditure on luxuries. Legal matters and service promotions turn in your favor when you avoid rash arguments.",
    7: "Business partnerships, public dealings, and marital harmony require balanced judgment. Avoid unnecessary conflicts with dear ones or impulsive risk-taking in joint ventures. Patience and mutual respect preserve honor and domestic peace.",
    8: "You should learn to relax to avoid unnecessary mental stress when things seem to be stagnating at the professional front. Resist the urge to change jobs on an impulse. Health and safety require attention against minor injuries or seasonal ailments; steady spiritual practice brings protection.",
    9: "This is a highly auspicious period for fortune, dharma, higher knowledge, and long-distance journeys. Family harmony flourishes, auspicious ceremonies take place, and guidance from respected and learned people brings land, prosperity, and success to children.",
    10: "You will come up with innovative ideas for dealing with challenges. Professional dealings and transactions work out smoothly as you score over competitors. Multiple sources of income, higher status, luxury acquisitions, and strong support from superiors make this a rewarding period.",
    11: "Time and fortune strongly favor your ambitions and financial gains. Your social circle expands with influential allies, personal relations get a boost, children bring happiness, and rare/valuable acquisitions crown your efforts with success.",
    12: "Charitable deeds, spiritual contemplation, and foreign connections are highlighted. Keep a check on rising expenses and avoid lending money without security. Meditation and ethical conduct turn challenges into inner peace.",
}

BHAV_PREDICTIONS_HI = {
    1: "इस अवधि में नए क्षेत्रों में कदम रखते समय धैर्य और दूरगामी योजना बनाएं। खर्चों पर नियंत्रण रखें तथा स्वास्थ्य व नेत्रों का ध्यान रखें। शांत और स्थिर दृष्टिकोण से कार्य करने पर स्थायी लाभ मिलेगा।",
    2: "आर्थिक मामलों और पारिवारिक सामंजस्य पर विशेष ध्यान देने का समय है। व्यापार में बड़े जोखिम से बचें और दैनिक कार्यों में अनुशासन बनाए रखें। माता-पिता के स्वास्थ्य का ध्यान रखें एवं वाणी में मधुरता रखें।",
    3: "वरिष्ठ अधिकारियों और प्रभावशाली व्यक्तियों का पूर्ण सहयोग प्राप्त होगा। व्यावसायिक और कार्यक्षेत्र में बड़ी उन्नति व पदोन्नति के योग हैं। कार्य से जुड़ी यात्राएं और नए संपर्क लाभकारी सिद्ध होंगे तथा पराक्रम में वृद्धि होगी।",
    4: "भूमि, भवन, वाहन और पारिवारिक सुख के मामलों में सक्रियता रहेगी। संपत्ति से जुड़े कार्यों और मान-सम्मान में वृद्धि होगी। माता के स्वास्थ्य का ध्यान रखें और वाहन सावधानीपूर्वक चलाएं।",
    5: "समय और भाग्य आपके कार्यों व प्रतिभा को नई पहचान दिलाएंगे। आपके परिश्रम की सराहना होगी और समाज में मान-सम्मान बढ़ेगा। परिवार में मांगलिक कार्य संपन्न होंगे तथा संतान पक्ष से प्रसन्नता और समृद्धि प्राप्त होगी।",
    6: "आप अपने परिश्रम से विरोधियों और चुनौतियों पर विजय प्राप्त करेंगे। कोर्ट-कचहरी और प्रतियोगी कार्यों में सफलता मिलेगी। स्वास्थ्य, नेत्र और अनावश्यक विलासितापूर्ण खर्चों के प्रति सजग रहें।",
    7: "व्यापारिक साझेदारी और दाम्पत्य जीवन में धैर्य व समझदारी से काम लें। प्रियजनों से अनावश्यक वाद-विवाद से बचें तथा जोखिम भरे निवेश में सावधानी बरतें।",
    8: "कार्यक्षेत्र में धैर्य बनाए रखें और आवेश में आकर नौकरी या व्यवसाय बदलने से बचें। मानसिक तनाव से दूर रहें तथा स्वास्थ्य व वाहन सुरक्षा का विशेष ध्यान रखें। आध्यात्मिक साधना से रक्षा होगी।",
    9: "यह भाग्यवृद्धि, धर्म, ज्ञान-विस्तार और शुभ यात्राओं का अत्यंत श्रेष्ठ समय है। परिवार में सुख-शांति और मांगलिक उत्सव होंगे। विद्वानों व वरिष्ठों के आशीर्वाद से भूमि, धन और संतान सुख में वृद्धि होगी।",
    10: "कार्यक्षेत्र में आपके नए विचार और योजनाएं अत्यंत सफल रहेंगी। व्यापारिक लेन-देन सुगम होगा और आप प्रतिस्पर्धियों से आगे निकलेंगे। एक से अधिक स्रोतों से आय, सुख-साधनों की प्राप्ति और उच्च पद-प्रतिष्ठा का योग है।",
    11: "आपकी महत्वाकांक्षाओं की पूर्ति और विशेष आर्थिक लाभ का समय है। उच्च पदस्थ मित्रों का सहयोग मिलेगा, संतान से सुख प्राप्त होगा और बहुमूल्य संपत्ति व दुर्लभ उपलब्धि हासिल होगी।",
    12: "धार्मिक एवं परोपकारी कार्यों तथा दूरस्थ/विदेशी संपर्कों से लाभ होगा। बढ़ते खर्चों पर नियंत्रण रखें और सोच-समझकर वित्तीय निर्णय लें।",
}


LAL_KITAB_EN_OVERRIDES = {
    ("Sun", 8): {
        "benefic": [
            "(1) Government favours will accrue from the 22nd year of life.",
            "(2) Here the Sun makes the native truthful, saintly and king-like. Nobody would be able to harm him.",
        ],
        "malefic": [
            "(1) Mercury in the 2nd house will create economic crisis.",
            "(2) Native will be short tempered, impatient and will have ill health.",
        ],
        "remedies": [
            "(1) Never keep a white cloth in the house.",
            "(2) Never live in the house facing south.",
            "(3) Always eat something sweet and drink water before starting any new work.",
            "(4) Throw copper coins in a burning pyre (Chita) whenever possible.",
            "(5) Throw Gur (jaggery) in running water.",
        ],
    },
    ("Moon", 9): {
        "body": (
            "The 9th house belongs to Jupiter, who is a great friend of the Moon. Hence the native will imbibe the traits and features "
            "of both these planets - good conduct, soft heartedness, religious bent of mind and love for virtuous acts and pilgrimage. "
            "Native will live upto 75 years. A friendly planet in the 5th house will augment comforts and pleasures from the son and develops "
            "intense interest in religious deeds. A friendly planet in the 3rd house ensures great increase in money and wealth."
        ),
        "remedies": [
            "(1) Install the things associated with the Moon within the house, e.g., place a square piece of silver in the almirah.",
            "(2) Serve the labourers with milk.",
            "(3) Offer milk to snakes and rice to fish.",
        ],
    },
    ("Mars", 8): {
        "body": (
            "The 8th house belongs to Mars and Saturn, who jointly influence the properties of this house. No planet is considered good in this house. "
            "Mars here affects very adversely the younger brothers of the native. The native sticks to commitments made by him without caring for profit or loss."
        ),
        "remedies": [
            "(1) Obtain blessings of widows and wear a silver chain.",
            "(2) Offer sweet loaves of bread prepared on Tandoor to dogs.",
            "(3) Take your meals in the kitchen.",
            "(4) Build a small dark room at the end of your house and do not allow sun light to enter it.",
            "(5) Offer rice, jaggery and gram pulse at religious places of worship.",
            "(6) Fill an earthen pot with 'Deshi Khand' and bury it near a cremation ground.",
        ],
    },
    ("Mercury", 9): {
        "body": (
            "Mercury provides very bad results in the 9th house also, because this house belongs to Jupiter and Mercury remains inimical to it. "
            "It causes continuous mental restlessness and defamation of various types. If Moon, Ketu and Jupiter are placed in 1, 3, 6, 7, 9 and 11th houses, "
            "Mercury does not give very advantageous results."
        ),
        "remedies": [
            "(1) Avoid the use of green colour.",
            "(2) Get your nose pricked.",
            "(3) Offer mushroom filled in an earthen pot to a religious place.",
            "(4) Do not accept any tabeez from any sadhu or faqir.",
        ],
    },
    ("Jupiter", 11): {
        "body": (
            "Jupiter in this house affects the things and relatives of enemies Mercury, Venus and Rahu very adversely. "
            "Consequently, the spouse of the native will remain miserable. Similarly, sisters, daughters and father's sisters will also remain unhappy. "
            "The native will be a debtor even if Mercury is well placed. The native will be comfortable only as long as father lives with him in a joint family along with brothers, sisters and mother."
        ),
        "remedies": [
            "(1) Always keep gold on your body.",
            "(2) Put on a copper bangle.",
            "(3) Watering a pipal tree would prove beneficial.",
        ],
    },
    ("Venus", 10): {
        "body": (
            "Venus in this house makes native greedy, suspicious and interested in handicraft. The native would act under the control and guidance of his spouse. "
            "As long as the spouse is with the native all sorts of troubles will remain warded off. If in a motor car no accident will take place or even if it takes place "
            "the native cannot be harmed in any manner. The business and things associated with Saturn will prove advantageous."
        ),
        "remedies": [
            "(1) Washing private parts with curd.",
            "(2) Western wall of the house should be of mud.",
            "(3) Abstinence from wine and non vegetarian food.",
            "(4) At the time of illness, the native should donate a black cow.",
        ],
    },
    ("Saturn", 5): {
        "body": (
            "This house belongs to Sun, which is inimical to Saturn. The native will be proud. He/she should not construct a house till 48 years, otherwise his/her child will suffer. "
            "He/she should live in the house bought or constructed by children. He/She should keep articles of Jupiter and Mars in ancestral house for welfare of children."
        ),
        "remedies": [
            "(1) Distribute salty things while celebrating child's birthday.",
            "(2) Offering almonds in the temple and bringing and keeping half of it in the house.",
        ],
    },
    ("Rahu", 3): {
        "body": (
            "It is the 'Pukka Ghar' of Rahu. 3rd house belongs to Mercury and is influenced by Mars. When Rahu is benefic the native will enjoy great wealth and a long life. "
            "He/She will be fearless and a loyal friend and would be a clairvoyant for seeing future in dreams. He/She will never be issueless, will be victorious over enemies; "
            "can never be a debtor. Native would leave behind property. 22nd year of life would be of progress. However if Rahu is malefic in 3rd house then brothers and relatives would waste money. "
            "Money once borrowed would never be returned. He/She would have defective speech and would be an atheist. If Sun and Mercury are also there (in 3rd house) with Rahu then sister would become a widow in 22nd or 32nd year of life."
        ),
        "remedies": [
            "(1) Never keep ivory or things of ivory in the house.",
        ],
    },
    ("Ketu", 9): {
        "body": (
            "9th house belongs to Jupiter, which favours Ketu. Ketu in 9th house is considered to be exalted. Such a native is obedient and lucky. "
            "It increases one's wealth. If Ketu is benefic then one earns wealth through one's own labour. There will be progress but no transfer. "
            "If one keeps gold brick in his house then wealth comes. The son of such a native is able to guess the future. One spends a big part of his life in foreign land. "
            "One has at least three sons and if 2nd house is auspicious then Ketu gives excellent results. If Moon is auspicious then the native helps his mother's family. "
            "If Ketu in 9th house is malefic then the native suffers from urinary problems, pain in back, problem in legs."
        ),
        "remedies": [
            "(1) Keep a dog.",
            "(2) Establish a rectangular piece of gold anywhere in the house.",
            "(3) Wear gold in the ear.",
            "(4) Respect elders, specially father-in-law.",
        ],
    },
}


def compute_all_written_reports(core_data: dict, vim_data: dict, varsha_data: dict):
    """
    Assemble all written prediction sections in both English and Pure Hindi.
    """
    meta = core_data["meta"]
    p_map = core_data["planet_by_id"]

    asc_en = meta["lagna_en"]
    asc_info = ASCENDANT_DATA.get(asc_en, ASCENDANT_DATA["Sagittarius"])
    nak_report = get_nakshatra_prediction(meta["nakshatra_en"], meta["nakshatra_hi"], meta["nakshatra_pada"])
    life_preds = get_life_predictions(core_data)

    m_bhav = varsha_data["muntha_bhav"]
    muntha_pred_en = (
        "It would be advisable to maintain cordial relations with relatives. A health check is necessary. "
        "A prolonged illness is speculated. Your enemies will leave no stone unturned to harm you, so better to keep safe distance from them. "
        "Family members health may disturb your peace of mind. Financial condition may not be good and you may get into debt. "
        "There can be expenditure and loss due to thieves and disputes. There will be disputes and disagreements with the authorities."
        if m_bhav == 6
        else BHAV_PREDICTIONS_EN.get(m_bhav, BHAV_PREDICTIONS_EN[1])
    )
    muntha_pred_hi = (
        "वर्ष कुंडली में मुंथा छठे भाव में होने से रिश्तेदारों के साथ मधुर संबंध बनाए रखना हितकर रहेगा। स्वास्थ्य की नियमित जांच कराएं तथा विरोधियों से सतर्क रहें। "
        "परिवार के सदस्यों के स्वास्थ्य और अनावश्यक खर्च या ऋण से बचाव करें। अधिकारियों के साथ वाद-विवाद से दूर रहें।"
        if m_bhav == 6
        else BHAV_PREDICTIONS_HI.get(m_bhav, BHAV_PREDICTIONS_HI[1])
    )

    varsha_dasha_preds = []
    for vd in varsha_data["varsha_dashas"]:
        b = vd["bhav"]
        varsha_dasha_preds.append({
            **vd,
            "text_en": BHAV_PREDICTIONS_EN.get(b, BHAV_PREDICTIONS_EN[1]),
            "text_hi": BHAV_PREDICTIONS_HI.get(b, BHAV_PREDICTIONS_HI[1]),
        })

    vim_maha_preds = []
    for md in vim_data["mahadashas"]:
        p_en = md["name_en"]
        p_obj = p_map[p_en]
        h = p_obj["house"]
        h_suf = "st" if h == 1 else "nd" if h == 2 else "rd" if h == 3 else "th"
        vim_maha_preds.append({
            "header_en": f"{p_en} Mahadasha Phal ({md['start_full']} - {md['end_full']})",
            "sub_en": f"{p_en} is in {p_obj['sign_en']} in your {h}{h_suf} house",
            "header_hi": f"{md['name_hi']} महादशा फल ({md['start_full']} से {md['end_full']})",
            "sub_hi": f"{md['name_hi']} आपकी कुंडली के {h}वें भाव ({p_obj['sign_hi']} राशि) में स्थित है",
            "text_en": BHAV_PREDICTIONS_EN.get(h, BHAV_PREDICTIONS_EN[1]),
            "text_hi": BHAV_PREDICTIONS_HI.get(h, BHAV_PREDICTIONS_HI[1]),
        })

    transit_preds = []
    for tp in varsha_data["transit_planets"]:
        h = tp["house"]
        transit_preds.append({
            **tp,
            "text_en": BHAV_PREDICTIONS_EN.get(h, BHAV_PREDICTIONS_EN[1]),
            "text_hi": BHAV_PREDICTIONS_HI.get(h, BHAV_PREDICTIONS_HI[1]),
        })

    lk_corpus_data = build_lal_kitab_corpus()
    lk_corpus = lk_corpus_data["planet_house_predictions"]
    lk_sutras = evaluate_chamatkari_sutras_and_career_rules(core_data)

    lk_written = []
    for pid in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]:
        p_obj = p_map[pid]
        h = p_obj["house"]
        h_suf = "st" if h == 1 else "nd" if h == 2 else "rd" if h == 3 else "th"
        c_entry = lk_corpus.get(f"{pid}_{h}", {})
        en_over = LAL_KITAB_EN_OVERRIDES.get((pid, h))

        if en_over:
            if "benefic" in en_over:
                body_en = "If benefic\n" + "\n".join(en_over["benefic"]) + "\n\nIf malefic\n" + "\n".join(en_over["malefic"])
            else:
                body_en = en_over["body"]
            rems_en = en_over["remedies"]
        else:
            body_en = (
                f"According to Lal Kitab, {pid} placed in the {h}{h_suf} house (Khana No. {h}) influences the affairs of this house "
                f"based on its Pakka Ghar and mutual planetary relationships. When benefic (Nek), it bestows prosperity, protection, and family rise; "
                f"when afflicted, following the traditional Lal Kitab precautions and remedies restores harmony."
            )
            rems_en = [f"({i+1}) {r}" for i, r in enumerate(c_entry.get("remedies_hi", []))]

        lk_written.append({
            "planet_en": pid,
            "planet_hi": p_obj["base_hi"],
            "house": h,
            "title_en": f"{pid} in your {h}{h_suf} house:",
            "title_hi": c_entry.get("title_hi", f"लाल किताब के अनुसार {p_obj['base_hi']} का {h}वें भाव में फल"),
            "body_en": body_en,
            "body_hi": c_entry.get("prediction_hi", ""),
            "remedies_en": rems_en,
            "remedies_hi": [f"({i+1}) {r}" for i, r in enumerate(c_entry.get("remedies_hi", []))],
        })

    lagna_idx = meta["lagna_sign_num"] - 1
    sign_lords = ["Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter"]
    nine_ids = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]

    vedic_aspect_offsets = {
        "Sun": [6],
        "Moon": [6],
        "Mars": [3, 6, 7],
        "Mercury": [6],
        "Jupiter": [4, 6, 8],
        "Venus": [6],
        "Saturn": [2, 6, 9],
        "Rahu": [4, 6, 8],
        "Ketu": [4, 6, 8],
    }

    exalted_s = {"Sun": 1, "Moon": 2, "Mars": 10, "Mercury": 6, "Jupiter": 4, "Venus": 12, "Saturn": 7, "Rahu": 2, "Ketu": 8}
    deb_s = {"Sun": 7, "Moon": 8, "Mars": 4, "Mercury": 12, "Jupiter": 10, "Venus": 6, "Saturn": 1, "Rahu": 8, "Ketu": 2}
    friendly_s = {
        "Sun": {1, 4, 5, 8, 9, 12},
        "Moon": {2, 3, 4, 5, 6},
        "Mars": {1, 5, 8, 9, 12},
        "Mercury": {2, 3, 5, 6, 7},
        "Jupiter": {1, 4, 5, 8, 9, 12},
        "Venus": {2, 3, 7, 10, 11},
        "Saturn": {2, 3, 6, 7, 10, 11},
        "Rahu": {2, 3, 6, 7, 10, 11},
        "Ketu": {1, 5, 8, 9, 12},
    }

    planet_considerations = []
    for pid in nine_ids:
        p_obj = p_map[pid]
        s_num = p_obj["sign_num"]
        h_num = p_obj["house"]
        h_suf = "st" if h_num == 1 else "nd" if h_num == 2 else "rd" if h_num == 3 else "th"

        if s_num == exalted_s[pid]:
            dig_en, dig_hi = "Exalted", "उच्च (Exalted)"
        elif s_num == deb_s[pid]:
            dig_en, dig_hi = "Debilitated", "नीच (Debilitated)"
        elif s_num in friendly_s[pid]:
            dig_en, dig_hi = "Friendly", "मित्र (Friendly)"
        else:
            dig_en, dig_hi = "Enemy", "शत्रु (Enemy)"

        owned_h = [
            f"{i+1}{'st' if i+1==1 else 'nd' if i+1==2 else 'rd' if i+1==3 else 'th'}"
            for i in range(12) if sign_lords[(lagna_idx + i) % 12] == pid
        ]
        if pid == "Rahu":
            owned_str_en = "11th (Co-lord of Aquarius)"
            owned_str_hi = "एकादश (कुंभ का सह-स्वामी)"
        elif pid == "Ketu":
            owned_str_en = "8th (Co-lord of Scorpio)"
            owned_str_hi = "अष्टम (वृश्चिक का सह-स्वामी)"
        else:
            owned_str_en = ", ".join(owned_h)
            owned_str_hi = ", ".join(str(i + 1) + "वें" for i in range(12) if sign_lords[(lagna_idx + i) % 12] == pid)

        asp_given = [((h_num - 1 + off) % 12) + 1 for off in vedic_aspect_offsets[pid]]
        asp_given_str = ", ".join(f"{ah}{'st' if ah==1 else 'nd' if ah==2 else 'rd' if ah==3 else 'th'}" for ah in asp_given)
        asp_given_hi = ", ".join(f"{ah}वें" for ah in asp_given)

        asp_received_en = []
        asp_received_hi = []
        for other_id in nine_ids:
            if other_id == pid:
                continue
            oh = p_map[other_id]["house"]
            other_targets = [((oh - 1 + off) % 12) + 1 for off in vedic_aspect_offsets[other_id]]
            if h_num in other_targets:
                asp_received_en.append(other_id)
                asp_received_hi.append(p_map[other_id]["base_hi"])

        asp_rec_str_en = ", ".join(asp_received_en) if asp_received_en else "no planet (un-aspected)"
        asp_rec_str_hi = ", ".join(asp_received_hi) if asp_received_hi else "किसी भी ग्रह द्वारा नहीं (दृष्टि रहित)"

        intro_en = (
            f"Your {pid} is in {p_obj['sign_en']} sign which is a {dig_en} sign for {pid}. "
            f"{pid} is lord of {owned_str_en} house and situated in {h_num}{h_suf} house. "
            f"{pid} aspects {asp_given_str} house and is aspected by {asp_rec_str_en}."
        )
        intro_hi = (
            f"आपकी कुंडली में {p_obj['base_hi']} {p_obj['sign_hi']} राशि में स्थित है जो इसके लिए {dig_hi} राशि है। "
            f"{p_obj['base_hi']} {owned_str_hi} भाव का स्वामी होकर {h_num}वें भाव में विराजमान है। "
            f"{p_obj['base_hi']} की दृष्टि {asp_given_hi} भाव पर है तथा यह {asp_rec_str_hi} से दृष्ट है।"
        )

        planet_considerations.append({
            "id": pid,
            "title_en": f"{pid} Consideration",
            "title_hi": f"{p_obj['base_hi']} विचार ({pid} Consideration)",
            "intro_en": intro_en,
            "intro_hi": intro_hi,
            "body_en": BHAV_PREDICTIONS_EN.get(h_num, BHAV_PREDICTIONS_EN[1]),
            "body_hi": BHAV_PREDICTIONS_HI.get(h_num, BHAV_PREDICTIONS_HI[1]),
            "dignity_en": dig_en,
            "dignity_hi": dig_hi,
        })

    return {
        "ascendant_report": asc_info,
        "nakshatra_report": nak_report,
        "life_predictions": life_preds,
        "muntha_pred_en": muntha_pred_en,
        "muntha_pred_hi": muntha_pred_hi,
        "varsha_dasha_preds": varsha_dasha_preds,
        "vim_maha_preds": vim_maha_preds,
        "transit_preds": transit_preds,
        "lal_kitab_written": lk_written,
        "lal_kitab_sutras": lk_sutras,
        "planet_considerations": planet_considerations,
    }
