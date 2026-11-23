"""English and Hindi labels and reviewed local guide translations."""

import copy
from html import escape, unescape
from html.parser import HTMLParser

from diseases import DISEASES_BY_SLUG


LANGUAGES = {
    "en": "English",
    "hi": "हिन्दी",
    "hinglish": "Hinglish",
}

LANGUAGE_HTML_CODES = {
    "en": "en",
    "hi": "hi",
    "hinglish": "hi-Latn",
}


UI_TRANSLATIONS = {
    "Explore": "खोजें",
    "Study room": "अध्ययन कक्ष",
    "Saved": "सहेजे गए",
    "A calmer way to learn": "सीखने का सहज तरीका",
    "Clearer health learning, one topic at a time.": "हर विषय के साथ स्वास्थ्य को बेहतर समझें।",
    "For education only · Not a substitute for professional medical advice": "केवल शैक्षिक जानकारी · पेशेवर चिकित्सकीय सलाह का विकल्प नहीं",
    "YOUR PERSONAL HEALTH LIBRARY": "आपकी निजी स्वास्थ्य लाइब्रेरी",
    "Understand health.": "स्वास्थ्य को समझें।",
    "Feel more prepared.": "बेहतर तैयारी करें।",
    "Clear, thoughtful guides to health topics—made for learning, not self-diagnosis.": "स्वास्थ्य विषयों पर स्पष्ट जानकारी—सीखने के लिए, स्वयं निदान के लिए नहीं।",
    "Search health topics": "स्वास्थ्य विषय खोजें",
    "Search a disease or condition": "किसी बीमारी या स्थिति को खोजें",
    "Try “asthma”, “diabetes”, or “flu”": "उदाहरण: “asthma”, “diabetes” या “flu”",
    "Search": "खोजें",
    "THE LIBRARY": "स्वास्थ्य लाइब्रेरी",
    "Search results": "खोज के परिणाम",
    "Explore health topics": "स्वास्थ्य विषय देखें",
    "Explore topic": "विषय देखें",
    "Start with a topic, follow your curiosity.": "किसी विषय से शुरुआत करें और अपनी जिज्ञासा के अनुसार आगे बढ़ें।",
    "External lookup": "बाहरी खोज",
    "topics": "विषय",
    "references": "संदर्भ",
    "MAKE IT STICK": "सीखी बातों को याद रखें",
    "Curiosity, meet your study room.": "जिज्ञासा का स्वागत है आपके अध्ययन कक्ष में।",
    "Review health topics, ask the study buddy, and practice original questions.": "स्वास्थ्य विषय दोहराएँ, स्टडी बडी से पूछें और अभ्यास प्रश्न हल करें।",
    "Visit study room": "अध्ययन कक्ष खोलें",
    "A note on health information": "स्वास्थ्य जानकारी के बारे में",
    "Knowledge is care": "ज्ञान से बेहतर देखभाल",
    "Learn at your own pace": "अपनी गति से सीखें",
    "A little more clarity,": "थोड़ी और स्पष्टता,",
    "a little less overwhelm.": "थोड़ा कम तनाव।",
    "These guides are educational, not medical advice. They cover a small set of common topics, not every disease. Always talk with a qualified health professional about personal symptoms or care.": "ये गाइड शैक्षिक जानकारी हैं, चिकित्सकीय सलाह नहीं। इनमें कुछ सामान्य विषय हैं, सभी बीमारियाँ नहीं। अपने लक्षणों या देखभाल के लिए योग्य स्वास्थ्यकर्मी से बात करें।",
    "All topics": "सभी विषय",
    "← All topics": "← सभी विषय",
    "EXTERNAL HEALTH REFERENCE": "बाहरी स्वास्थ्य संदर्भ",
    "This condition is not in Wellnote’s small, reviewed starter library.": "यह स्थिति Wellnote की सीमित, समीक्षित शुरुआती लाइब्रेरी में शामिल नहीं है।",
    "For education, not diagnosis.": "शिक्षा के लिए, निदान के लिए नहीं।",
    "Online references cannot assess your personal health. For symptoms or care, talk with a qualified health professional; for a possible emergency, contact local emergency services.": "ऑनलाइन संदर्भ आपकी व्यक्तिगत सेहत का आकलन नहीं कर सकते। लक्षणों या देखभाल के लिए योग्य स्वास्थ्यकर्मी से बात करें; आपात स्थिति में स्थानीय आपात सेवाओं से संपर्क करें।",
    "THE OVERVIEW": "संक्षिप्त परिचय",
    "What it is": "यह क्या है",
    "WHAT TO LOOK FOR": "किन बातों पर ध्यान दें",
    "Common symptoms": "सामान्य लक्षण",
    "Symptoms can vary. This list cannot tell you what is causing your symptoms.": "लक्षण अलग-अलग हो सकते हैं। यह सूची आपके लक्षणों का कारण नहीं बता सकती।",
    "EVERYDAY WELLBEING": "रोज़मर्रा की सेहत",
    "Prevention &amp; risk reduction": "रोकथाम और जोखिम में कमी",
    "CARE &amp; TREATMENT": "देखभाल और उपचार",
    "Can it be treated?": "क्या इसका उपचार संभव है?",
    "Care is personal. A licensed health professional can help you understand your options and what is right for you.": "देखभाल हर व्यक्ति के लिए अलग होती है। योग्य स्वास्थ्यकर्मी आपके विकल्प समझने में मदद कर सकते हैं।",
    "Learn more from": "और जानकारी:",
    "QUICK REVIEW": "झटपट दोहराएँ",
    "Key takeaways": "मुख्य बातें",
    "Study this topic": "इस विषय का अध्ययन करें",
    "Study this topic →": "इस विषय का अध्ययन करें →",
    "Need medical help?": "चिकित्सकीय मदद चाहिए?",
    "If you think you may have a medical emergency, contact your local emergency services now.": "यदि आपको लगता है कि यह चिकित्सकीय आपात स्थिति हो सकती है, तो तुरंत स्थानीय आपात सेवाओं से संपर्क करें।",
    "Learning, not diagnosis.": "सीखने के लिए, निदान के लिए नहीं।",
    "This overview is general education and is not a substitute for a clinician’s assessment, diagnosis, or treatment advice.": "यह सामान्य शैक्षिक जानकारी है और चिकित्सक के आकलन, निदान या उपचार संबंधी सलाह का विकल्प नहीं है।",
    "YOUR PERSONAL LIBRARY": "आपकी निजी लाइब्रेरी",
    "Saved topics": "सहेजे गए विषय",
    "Pick up where your curiosity left off.": "जहाँ जिज्ञासा रुकी थी, वहीं से आगे बढ़ें।",
    "BOOKMARKS": "बुकमार्क",
    "Your reading list": "आपकी पढ़ने की सूची",
    "saved": "सहेजे गए",
    "Your library is ready": "आपकी लाइब्रेरी तैयार है",
    "Save a health topic to keep it close for your next study session.": "अगले अध्ययन सत्र के लिए स्वास्थ्य विषय सहेजें।",
    "Save for later": "बाद के लिए सहेजें",
    "＋ Save for later": "＋ बाद के लिए सहेजें",
    "♥ Saved to your library": "♥ आपकी लाइब्रेरी में सहेजा गया",
    "Save to library": "लाइब्रेरी में सहेजें",
    "Remove from library": "लाइब्रेरी से हटाएँ",
    "MedlinePlus reference": "MedlinePlus संदर्भ",
    "Saved health topic. Open it to view the current source summary.": "सहेजा गया स्वास्थ्य विषय। वर्तमान संदर्भ देखने के लिए खोलें।",
    "Reading list is full": "आपकी पठन सूची भर गई है",
    "This browser’s reading-list storage is full. Remove a saved topic before adding another.": "ब्राउज़र की पठन सूची में जगह नहीं है। नया विषय जोड़ने से पहले कोई सहेजा हुआ विषय हटाएँ।",
    "A GENTLER WAY TO LEARN": "सीखने का सहज तरीका",
    "Welcome to your": "आपके",
    "study room.": "अध्ययन कक्ष में स्वागत है।",
    "Short reviews, original practice, and a small study companion—no pressure, just a little more understanding.": "छोटी पुनरावृत्ति, मौलिक अभ्यास और आपका अध्ययन साथी—बिना दबाव, थोड़ी और समझ।",
    "Try a practice question": "अभ्यास प्रश्न हल करें",
    "Try a practice question →": "अभ्यास प्रश्न हल करें →",
    "Generate a mind map": "माइंड मैप बनाएँ",
    "Smart flashcards": "स्मार्ट फ्लैशकार्ड",
    "Compare diseases": "बीमारियों की तुलना करें",
    "YOUR TOPICS": "आपके विषय",
    "Choose what to review": "दोहराने के लिए विषय चुनें",
    "Essentials from each health guide.": "हर स्वास्थ्य गाइड की ज़रूरी बातें।",
    "EXAM STARTERS": "परीक्षा की तैयारी",
    "Preparing for an exam?": "क्या आप परीक्षा की तैयारी कर रहे हैं?",
    "Ask the study buddy about NEET, MCAT, or AAMC. For current exam details and syllabi, check the official provider.": "NEET, MCAT या AAMC के बारे में स्टडी बडी से पूछें। परीक्षा और पाठ्यक्रम की नवीनतम जानकारी आधिकारिक स्रोत से जाँचें।",
    "Study, not a substitute.": "अध्ययन सामग्री, विकल्प नहीं।",
    "Study buddy replies are for education, not personal diagnosis or treatment. For your own symptoms or care, consult a qualified health professional.": "स्टडी बडी के जवाब शिक्षा के लिए हैं, व्यक्तिगत निदान या उपचार के लिए नहीं। अपने लक्षणों या देखभाल के लिए योग्य स्वास्थ्यकर्मी से सलाह लें।",
    "Your study buddy": "आपका स्टडी बडी",
    "Ready when you are": "जब चाहें, पूछें",
    "Ask a study question": "अध्ययन से जुड़ा सवाल पूछें",
    "Ask a study question…": "अध्ययन से जुड़ा सवाल पूछें…",
    "Send": "भेजें",
    "Read answer aloud": "जवाब सुनें",
    "Stop audio": "आवाज़ रोकें",
    "Select Read answer aloud to hear the study buddy response.": "स्टडी बडी का जवाब सुनने के लिए ‘जवाब सुनें’ चुनें।",
    "VISUAL STUDY TOOL": "दृश्य अध्ययन टूल",
    "Mind map generator": "माइंड मैप जनरेटर",
    "Enter any health topic. Wellnote uses its reviewed guide or searches MedlinePlus for a reference.": "कोई भी स्वास्थ्य विषय लिखें। Wellnote अपनी समीक्षित गाइड या MedlinePlus संदर्भ खोजेगा।",
    "Enter any disease or health topic": "किसी भी बीमारी या स्वास्थ्य विषय का नाम लिखें",
    "Generate map": "मैप बनाएँ",
    "ACTIVE RECALL": "सक्रिय पुनरावृत्ति",
    "Choose any disease or health topic": "कोई भी बीमारी या स्वास्थ्य विषय चुनें",
    "Build deck": "कार्ड बनाएँ",
    "Reveal answer": "जवाब देखें",
    "Compare for learning, not diagnosis.": "सीखने के लिए तुलना करें, निदान के लिए नहीं।",
    "First health topic": "पहला स्वास्थ्य विषय",
    "Second health topic": "दूसरा स्वास्थ्य विषय",
    "Compare topics": "विषयों की तुलना करें",
    "SIDE-BY-SIDE REVIEW": "आमने-सामने तुलना",
    "Disease comparison": "बीमारियों की तुलना",
    "Compare two health topics using reviewed Wellnote guides or linked MedlinePlus references.": "Wellnote की समीक्षित गाइड या MedlinePlus संदर्भों से दो स्वास्थ्य विषयों की तुलना करें।",
    "Overview": "परिचय",
    "Symptoms": "लक्षण",
    "Prevention": "रोकथाम",
    "Treatment &amp; care": "उपचार और देखभाल",
    "Sources": "स्रोत",
    "Compare": "तुलना",
    "For example: asthma": "उदाहरण: अस्थमा",
    "For example: seasonal flu": "उदाहरण: मौसमी फ्लू",
    "OOPS": "क्षमा करें",
    "Back to explore": "विषय सूची पर लौटें",
    "Correct!": "सही जवाब!",
    "Not quite—review the explanation.": "सही नहीं—व्याख्या दोबारा देखें।",
    "Check answer": "जवाब जाँचें",
    "Next question": "अगला सवाल",
    "Language switcher": "भाषा चुनें",
    "Some references and study content may still be in English.": "कुछ संदर्भ और अध्ययन सामग्री अभी भी अंग्रेज़ी में हो सकती है।",
}

HINGLISH_UI_TRANSLATIONS = {
    "Explore": "Dekhein",
    "Study room": "Study room",
    "Saved": "Save kiye gaye",
    "A calmer way to learn": "Seekhne ka aasan tareeka",
    "Clearer health learning, one topic at a time.": "Har topic ke saath health ko behtar samjhein.",
    "For education only · Not a substitute for professional medical advice": "Sirf jaankari ke liye · Doctor ki salah ka badal nahi",
    "YOUR PERSONAL HEALTH LIBRARY": "Aapki personal health library",
    "Understand health.": "Health ko samjhein.",
    "Feel more prepared.": "Behtar taiyaari karein.",
    "Clear, thoughtful guides to health topics—made for learning, not self-diagnosis.": "Health topics par saaf jaankari—seekhne ke liye, khud diagnosis karne ke liye nahi.",
    "Search health topics": "Health topics search karein",
    "Search a disease or condition": "Koi bimari ya condition search karein",
    "Try “asthma”, “diabetes”, or “flu”": "Jaise: “asthma”, “diabetes” ya “flu”",
    "Search": "Search karein",
    "THE LIBRARY": "Health library",
    "Search results": "Search ke results",
    "Explore health topics": "Health topics dekhein",
    "Start with a topic, follow your curiosity.": "Kisi topic se shuru karein aur apni curiosity ko follow karein.",
    "External lookup": "External search",
    "topics": "topics",
    "references": "references",
    "MAKE IT STICK": "Seekhi hui baat yaad rakhein",
    "Curiosity, meet your study room.": "Aapki curiosity ka study room mein swagat hai.",
    "Review health topics, ask the study buddy, and practice original questions.": "Health topics revise karein, study buddy se poochhein, aur original questions practice karein.",
    "Visit study room": "Study room kholein",
    "A note on health information": "Health information ke baare mein",
    "Knowledge is care": "Jaankari se behtar care",
    "Learn at your own pace": "Apni speed se seekhein",
    "A little more clarity,": "Thodi aur clarity,",
    "a little less overwhelm.": "thoda kam stress.",
    "These guides are educational, not medical advice. They cover a small set of common topics, not every disease. Always talk with a qualified health professional about personal symptoms or care.": "Yeh guides sirf jaankari ke liye hain, medical advice nahi. Inmein kuch common topics hain, har bimari nahi. Apne symptoms ya care ke liye qualified health professional se baat karein.",
    "All topics": "Saare topics",
    "← All topics": "← Saare topics",
    "EXTERNAL HEALTH REFERENCE": "External health reference",
    "This condition is not in Wellnote’s small, reviewed starter library.": "Yeh condition Wellnote ki chhoti, reviewed starter library mein nahi hai.",
    "For education, not diagnosis.": "Jaankari ke liye, diagnosis ke liye nahi.",
    "Online references cannot assess your personal health. For symptoms or care, talk with a qualified health professional; for a possible emergency, contact local emergency services.": "Online references aapki personal health check nahi kar sakte. Symptoms ya care ke liye qualified health professional se baat karein; emergency mein local emergency services ko contact karein.",
    "THE OVERVIEW": "Overview",
    "What it is": "Yeh kya hai",
    "WHAT TO LOOK FOR": "Kin baaton par dhyaan dein",
    "Common symptoms": "Aam symptoms",
    "Symptoms can vary. This list cannot tell you what is causing your symptoms.": "Symptoms alag ho sakte hain. Yeh list aapke symptoms ka kaaran nahi bata sakti.",
    "EVERYDAY WELLBEING": "Rozmarra ki sehat",
    "Prevention &amp; risk reduction": "Bachaav aur risk kam karna",
    "CARE &amp; TREATMENT": "Care aur treatment",
    "Can it be treated?": "Kya iska treatment ho sakta hai?",
    "Care is personal. A licensed health professional can help you understand your options and what is right for you.": "Har vyakti ki care alag hoti hai. Qualified health professional aapke options samajhne mein madad kar sakte hain.",
    "Learn more from": "Aur jaankari:",
    "QUICK REVIEW": "Quick review",
    "Key takeaways": "Zaroori baatein",
    "Study this topic": "Is topic ko padhein",
    "Study this topic →": "Is topic ko padhein →",
    "Need medical help?": "Medical help chahiye?",
    "If you think you may have a medical emergency, contact your local emergency services now.": "Agar aapko lagta hai ki medical emergency ho sakti hai, turant local emergency services ko contact karein.",
    "Learning, not diagnosis.": "Seekhne ke liye, diagnosis ke liye nahi.",
    "This overview is general education and is not a substitute for a clinician’s assessment, diagnosis, or treatment advice.": "Yeh general jaankari hai aur clinician ke assessment, diagnosis, ya treatment advice ka badal nahi hai.",
    "YOUR PERSONAL LIBRARY": "Aapki personal library",
    "Saved topics": "Save kiye gaye topics",
    "Pick up where your curiosity left off.": "Jahaan curiosity ruki thi, wahin se shuru karein.",
    "BOOKMARKS": "Bookmarks",
    "Your reading list": "Aapki reading list",
    "saved": "save kiye gaye",
    "Your library is ready": "Aapki library taiyaar hai",
    "Save a health topic to keep it close for your next study session.": "Agli study session ke liye health topic save karein.",
    "Explore topic": "Topic dekhein",
    "Save for later": "Baad ke liye save karein",
    "＋ Save for later": "＋ Baad ke liye save karein",
    "♥ Saved to your library": "♥ Aapki library mein save hai",
    "Save to library": "Library mein save karein",
    "Remove from library": "Library se hataayein",
    "MedlinePlus reference": "MedlinePlus reference",
    "Saved health topic. Open it to view the current source summary.": "Saved health topic. Current source summary dekhne ke liye kholein.",
    "Reading list is full": "Aapki reading list bhar gayi hai",
    "This browser’s reading-list storage is full. Remove a saved topic before adding another.": "Browser ki reading list mein jagah nahi hai. Naya topic jodne se pehle koi saved topic hataayein.",
    "A GENTLER WAY TO LEARN": "Seekhne ka aasan tareeka",
    "Welcome to your": "Aapke",
    "study room.": "study room mein swagat hai.",
    "Short reviews, original practice, and a small study companion—no pressure, just a little more understanding.": "Short revision, original practice aur aapka study buddy—bina pressure, thodi aur samajh.",
    "Try a practice question": "Practice question karein",
    "Try a practice question →": "Practice question karein →",
    "Generate a mind map": "Mind map banaayein",
    "Smart flashcards": "Smart flashcards",
    "Compare diseases": "Diseases compare karein",
    "YOUR TOPICS": "Aapke topics",
    "Choose what to review": "Review ke liye chunein",
    "Essentials from each health guide.": "Har health guide ki zaroori baatein.",
    "EXAM STARTERS": "Exam ki taiyaari",
    "Preparing for an exam?": "Kya aap exam ki taiyaari kar rahe hain?",
    "Ask the study buddy about NEET, MCAT, or AAMC. For current exam details and syllabi, check the official provider.": "NEET, MCAT ya AAMC ke baare mein study buddy se poochhein. Exam details aur syllabus ke liye official provider ko check karein.",
    "Study, not a substitute.": "Study ke liye, professional care ka badal nahi.",
    "Study buddy replies are for education, not personal diagnosis or treatment. For your own symptoms or care, consult a qualified health professional.": "Study buddy ke jawab jaankari ke liye hain, personal diagnosis ya treatment ke liye nahi. Apne symptoms ya care ke liye qualified health professional se salah lein.",
    "Your study buddy": "Aapka study buddy",
    "Ready when you are": "Jab chahein, poochhein",
    "Ask a study question": "Study se juda sawaal poochhein",
    "Ask a study question…": "Study se juda sawaal poochhein…",
    "Send": "Bhejein",
    "Read answer aloud": "Jawaab sunein",
    "Stop audio": "Audio rokein",
    "Select Read answer aloud to hear the study buddy response.": "Study buddy ka jawaab sunne ke liye ‘Jawaab sunein’ chunein.",
    "VISUAL STUDY TOOL": "Visual study tool",
    "Mind map generator": "Mind map generator",
    "Enter any health topic. Wellnote uses its reviewed guide or searches MedlinePlus for a reference.": "Koi bhi health topic likhein. Wellnote apni reviewed guide ya MedlinePlus reference dhoondhega.",
    "Enter any disease or health topic": "Kisi bhi bimari ya health topic ka naam likhein",
    "Generate map": "Map banaayein",
    "ACTIVE RECALL": "Active recall",
    "Choose any disease or health topic": "Koi bhi bimari ya health topic chunein",
    "Build deck": "Cards banaayein",
    "Reveal answer": "Jawaab dekhein",
    "Compare for learning, not diagnosis.": "Seekhne ke liye compare karein, diagnosis ke liye nahi.",
    "First health topic": "Pehla health topic",
    "Second health topic": "Doosra health topic",
    "Compare topics": "Topics compare karein",
    "SIDE-BY-SIDE REVIEW": "Saath-saath review",
    "Disease comparison": "Bimariyon ki tulna",
    "Compare two health topics using reviewed Wellnote guides or linked MedlinePlus references.": "Wellnote ki reviewed guides ya MedlinePlus references se do health topics compare karein.",
    "Overview": "Overview",
    "Symptoms": "Symptoms",
    "Prevention": "Bachaav",
    "Treatment &amp; care": "Treatment aur care",
    "Sources": "Sources",
    "Compare": "Compare",
    "For example: asthma": "Jaise: asthma",
    "For example: seasonal flu": "Jaise: seasonal flu",
    "OOPS": "Oops",
    "Back to explore": "Topics par waapas jaayein",
    "Correct!": "Sahi jawaab!",
    "Not quite—review the explanation.": "Abhi sahi nahi—explanation phir se dekhein.",
    "Check answer": "Jawaab check karein",
    "Next question": "Agla sawaal",
    "Language switcher": "Language chunein",
    "Some references and study content may still be in English.": "Kuch references aur study content abhi English mein ho sakte hain.",
}


DISEASE_TRANSLATIONS = {
    "asthma": {
        "name": "अस्थमा (दमा)",
        "category": "श्वसन स्वास्थ्य",
        "summary": "एक दीर्घकालिक स्थिति जिसमें वायुमार्ग में सूजन और संकुचन हो सकता है।",
        "description": (
            "अस्थमा उन वायुमार्गों को प्रभावित करता है जिनसे हवा फेफड़ों तक आती-जाती है। "
            "सूजन और वायुमार्ग का सिकुड़ना ऐसे लक्षण पैदा कर सकता है जो समय के साथ बदलते हैं। "
            "हर व्यक्ति के ट्रिगर अलग हो सकते हैं; व्यक्तिगत देखभाल योजना बिगड़ते लक्षणों को "
            "पहचानने और संभालने में मदद कर सकती है।"
        ),
        "symptoms": ["साँस में घरघराहट", "खाँसी, अक्सर रात या सुबह जल्दी", "साँस फूलना", "छाती में जकड़न"],
        "prevention": [
            "व्यक्तिगत ट्रिगर पहचानने के लिए चिकित्सक के साथ काम करें।",
            "लिखित अस्थमा एक्शन प्लान और निर्धारित उपचार का पालन करें।",
            "तंबाकू के धुएँ से बचें और ज्ञात उत्तेजकों के संपर्क को कम करें।",
            "अनुशंसित टीकाकरण समय पर करवाएँ।",
        ],
        "treatment": (
            "अस्थमा दीर्घकालिक स्थिति है और इसका वर्तमान में स्थायी इलाज नहीं है, लेकिन "
            "निर्धारित दवाएँ और एक्शन प्लान लक्षणों को नियंत्रित करने में मदद कर सकते हैं। "
            "उपचार में साँस के साथ ली जाने वाली दवाएँ शामिल हो सकती हैं; सही योजना हर व्यक्ति "
            "के लिए अलग होती है।"
        ),
        "study_points": [
            "अस्थमा वायुमार्गों को प्रभावित करता है और इसके लक्षण आते-जाते रह सकते हैं।",
            "आम लक्षणों में घरघराहट, खाँसी, साँस फूलना और छाती में जकड़न शामिल हैं।",
            "चिकित्सक की मदद से बनाई गई योजना लक्षण बढ़ने पर संभालने में मदद कर सकती है।",
        ],
    },
    "type-2-diabetes": {
        "name": "टाइप 2 मधुमेह",
        "category": "चयापचय स्वास्थ्य",
        "summary": "एक ऐसी स्थिति जिसमें समय के साथ रक्त शर्करा बहुत अधिक हो सकती है।",
        "description": (
            "टाइप 2 मधुमेह में शरीर इंसुलिन का प्रभावी ढंग से उपयोग नहीं कर पाता और समय के साथ "
            "स्वस्थ सीमा में रक्त शर्करा बनाए रखने के लिए पर्याप्त इंसुलिन नहीं बना पाता। जोखिम "
            "और अनुभव हर व्यक्ति में अलग होते हैं। स्वास्थ्यकर्मी लक्षणों और जाँचों का आकलन कर "
            "उपयुक्त योजना पर चर्चा कर सकते हैं।"
        ),
        "symptoms": ["प्यास या पेशाब अधिक लगना", "सामान्य से अधिक थकान", "धुँधला दिखना", "कुछ लोगों को स्पष्ट लक्षण नहीं होते"],
        "prevention": [
            "स्वस्थ आदतें जोखिम कम कर सकती हैं, लेकिन हर मामले को रोक नहीं सकतीं।",
            "व्यक्तिगत जोखिम और जाँच के बारे में स्वास्थ्यकर्मी से चर्चा करें।",
            "नियमित शारीरिक गतिविधि और संतुलित भोजन समग्र स्वास्थ्य में मदद कर सकते हैं।",
            "जोखिम कई बातों से प्रभावित होता है; स्वयं को दोष न दें।",
        ],
        "treatment": (
            "टाइप 2 मधुमेह दीर्घकालिक स्थिति है। देखभाल योजना में पोषण और गतिविधि में बदलाव, "
            "निगरानी और दवाएँ शामिल हो सकती हैं। कुछ लोगों में रोग की छूट (रिमिशन) संभव है, "
            "लेकिन इसकी गारंटी नहीं होती और यह स्थायी इलाज के समान नहीं है; नियमित देखभाल "
            "फिर भी महत्वपूर्ण है।"
        ),
        "study_points": [
            "यह स्थिति शरीर में इंसुलिन के उपयोग और रक्त शर्करा के नियंत्रण को प्रभावित करती है।",
            "लक्षणों में प्यास, बार-बार पेशाब, थकान या धुँधला दिखना शामिल हो सकता है।",
            "जाँच और व्यक्तिगत देखभाल योजना पर चिकित्सक से चर्चा करनी चाहिए।",
        ],
    },
    "seasonal-influenza": {
        "name": "मौसमी इन्फ्लुएंज़ा (फ्लू)",
        "category": "संक्रामक रोग",
        "summary": "इन्फ्लुएंज़ा वायरस से होने वाला एक संक्रामक श्वसन रोग।",
        "description": (
            "मौसमी इन्फ्लुएंज़ा नाक, गले और कभी-कभी फेफड़ों का संक्रमण है। यह हल्का या गंभीर "
            "हो सकता है और कुछ लोगों में जटिलताओं का जोखिम अधिक होता है। इसके लक्षण अन्य "
            "बीमारियों से मिल सकते हैं, इसलिए यह जानकारी किसी व्यक्ति की बीमारी का कारण "
            "निर्धारित नहीं कर सकती।"
        ),
        "symptoms": ["बुखार या ठंड लगना", "खाँसी और गले में दर्द", "मांसपेशियों में दर्द और सिरदर्द", "थकान; कुछ लोगों को नाक भी बह सकती है"],
        "prevention": [
            "अपने लिए अनुशंसित मौसमी फ्लू का टीका लगवाएँ।",
            "हाथ धोएँ और खाँसते या छींकते समय मुँह ढकें।",
            "संभव हो तो बीमार होने पर घर पर रहें और स्थानीय स्वास्थ्य सलाह मानें।",
            "यदि आपको अधिक जोखिम है तो देखभाल के लिए जल्दी चिकित्सक से पूछें।",
        ],
        "treatment": (
            "कई लोग आराम और सहायक देखभाल से ठीक हो जाते हैं, लेकिन इन्फ्लुएंज़ा गंभीर बीमारी "
            "भी पैदा कर सकता है। पर्चे पर मिलने वाली एंटीवायरल दवाएँ कुछ लोगों की मदद कर सकती "
            "हैं, खासकर जल्दी शुरू करने पर। उपचार के लिए चिकित्सक सलाह दे सकते हैं; हर व्यक्ति "
            "के ठीक होने का तरीका समान नहीं होता।"
        ),
        "study_points": [
            "इन्फ्लुएंज़ा फ्लू वायरस से होने वाला संक्रामक श्वसन रोग है।",
            "बुखार, खाँसी, गले में दर्द, बदन दर्द और थकान आम लक्षण हैं।",
            "टीकाकरण और रोज़मर्रा की स्वच्छता जोखिम कम करते हैं; अधिक जोखिम वाले लोगों को जल्दी सलाह लेनी चाहिए।",
        ],
    },
}

HINGLISH_DISEASE_TRANSLATIONS = {
    "asthma": {
        "name": "Asthma (Dama)",
        "category": "Saans ki sehat",
        "summary": "Ek lambe samay tak rehne wali condition jismein saans ki naliyon mein sujan aur sikudav ho sakta hai.",
        "description": (
            "Asthma un saans ki naliyon ko affect karta hai jinse hawa lungs tak aati-jaati hai. "
            "Sujan aur naliyon ka sikudna aise symptoms la sakta hai jo samay ke saath badalte hain. "
            "Har vyakti ke triggers alag ho sakte hain; personal care plan se badhte symptoms ko "
            "pehchaanne aur manage karne mein madad mil sakti hai."
        ),
        "symptoms": ["Saans mein ghargharahat", "Khansi, aksar raat ya subah jaldi", "Saans phoolna", "Seene mein jakadan"],
        "prevention": [
            "Apne triggers pehchaanne ke liye clinician ke saath kaam karein.",
            "Likhe hue asthma action plan aur prescribed treatment ko follow karein.",
            "Tobacco ke dhuen se bachein aur jaane-pehchaane irritants se door rahein.",
            "Recommended vaccinations samay par lagwaayein.",
        ],
        "treatment": (
            "Asthma ek long-term condition hai aur iska abhi permanent cure nahi hai, lekin prescribed "
            "medicines aur action plan symptoms ko control karne mein madad kar sakte hain. Treatment "
            "mein inhaled medicines ho sakti hain; sahi plan har vyakti ke liye alag hota hai."
        ),
        "study_points": [
            "Asthma saans ki naliyon ko affect karta hai aur symptoms aate-jaate reh sakte hain.",
            "Aam symptoms mein ghargharahat, khansi, saans phoolna aur seene mein jakadan shamil hain.",
            "Clinician ki madad se bana action plan flare-ups manage karne mein madad karta hai.",
        ],
    },
    "type-2-diabetes": {
        "name": "Type 2 Diabetes",
        "category": "Metabolic health",
        "summary": "Ek condition jismein samay ke saath blood sugar zyada ho sakti hai.",
        "description": (
            "Type 2 diabetes tab hoti hai jab sharir insulin ka sahi tarah use nahi kar pata aur waqt ke "
            "saath healthy blood sugar level ke liye kaafi insulin nahi bana pata. Risk aur har vyakti "
            "ka experience alag hota hai. Health professional symptoms aur tests ka assessment karke "
            "sahi plan par baat kar sakte hain."
        ),
        "symptoms": ["Zyada pyaas lagna ya baar-baar peshab aana", "Aam se zyada thakaan", "Dhundhla dikhna", "Kuch logon ko koi saaf symptom nahi hota"],
        "prevention": [
            "Healthy aadatein risk kam kar sakti hain, par har case ko rok nahi sakti.",
            "Apne risk aur screening ke baare mein health professional se baat karein.",
            "Regular physical activity aur balanced khana overall health mein madad kar sakte hain.",
            "Risk kai cheezon se juda hota hai; khud ko dosh na dein.",
        ],
        "treatment": (
            "Type 2 diabetes ek long-term condition hai. Care plan mein khane aur activity mein badlav, "
            "monitoring aur medicines shamil ho sakti hain. Kuch log remission tak pahunchte hain, "
            "lekin iski guarantee nahi hoti aur yeh cure ke barabar nahi hai; regular follow-up zaroori hai."
        ),
        "study_points": [
            "Yeh condition insulin ke use aur blood sugar manage karne ke tareeke ko affect karti hai.",
            "Symptoms mein pyaas, baar-baar peshab, thakaan ya dhundhla dikhna shamil ho sakta hai.",
            "Tests aur personal care plan ke baare mein clinician se baat karein.",
        ],
    },
    "seasonal-influenza": {
        "name": "Seasonal Influenza (Flu)",
        "category": "Infectious disease",
        "summary": "Influenza viruses ki wajah se hone wali contagious respiratory illness.",
        "description": (
            "Seasonal influenza naak, gale aur kabhi-kabhi lungs ka infection hai. Yeh halka ya serious "
            "ho sakta hai, aur kuch logon mein complications ka risk zyada hota hai. Iske symptoms "
            "doosri illnesses jaise ho sakte hain, isliye yeh overview kisi vyakti ki illness ka kaaran "
            "nahi bata sakta."
        ),
        "symptoms": ["Bukhar ya thand lagna", "Khansi aur gale mein dard", "Manspeshiyon mein dard aur sir dard", "Thakaan; kuch logon ki naak bhi beh sakti hai"],
        "prevention": [
            "Aapke liye recommended seasonal flu vaccine lagwaayein.",
            "Haath dhoyein aur khansne ya chheenkne par munh dhakein.",
            "Mumkin ho to beemar hone par ghar par rahein aur local health guidance follow karein.",
            "Agar aapko zyada risk hai to care ke liye jaldi clinician se poochhein.",
        ],
        "treatment": (
            "Kai log aaram aur supportive care se theek ho jaate hain, lekin influenza serious illness "
            "bhi kar sakta hai. Prescription antivirals kuch logon ki madad kar sakte hain, khaas kar "
            "jab jaldi shuru kiye jaayein. Treatment ke liye clinician salah de sakte hain; recovery "
            "har vyakti mein ek jaisi nahi hoti."
        ),
        "study_points": [
            "Influenza flu viruses ki wajah se hone wali contagious respiratory illness hai.",
            "Bukhar, khansi, gale mein dard, badan dard aur thakaan aam symptoms hain.",
            "Vaccination aur rozmarra ki safai risk kam karti hai; zyada risk wale log jaldi salah lein.",
        ],
    },
}


def translate(value, language="en"):
    if language != "hi":
        if language != "hinglish":
            return value
        ui_translations = HINGLISH_UI_TRANSLATIONS
        disease_translations = HINGLISH_DISEASE_TRANSLATIONS
    else:
        ui_translations = UI_TRANSLATIONS
        disease_translations = DISEASE_TRANSLATIONS
    if value in ui_translations:
        return ui_translations[value]
    for slug, guide in disease_translations.items():
        if value == DISEASES_BY_SLUG[slug]["name"]:
            return guide["name"]
    return value


def translate_markup(markup, language="en"):
    if language not in ("hi", "hinglish"):
        return markup
    ui_translations = UI_TRANSLATIONS if language == "hi" else HINGLISH_UI_TRANSLATIONS
    localized_text = {unescape(key): value for key, value in ui_translations.items()}

    class LocalizedMarkup(HTMLParser):
        def __init__(self):
            super().__init__(convert_charrefs=True)
            self.parts = []

        def handle_starttag(self, tag, attrs):
            rendered_attrs = []
            for name, value in attrs:
                if value is not None and name in ("aria-label", "alt", "placeholder", "title"):
                    value = localized_text.get(value, value)
                rendered_attrs.append(
                    f' {name}="{escape(value, quote=True)}"' if value is not None else f" {name}"
                )
            self.parts.append(f"<{tag}{''.join(rendered_attrs)}>")

        def handle_startendtag(self, tag, attrs):
            self.handle_starttag(tag, attrs)
            self.parts[-1] = self.parts[-1][:-1] + " />"

        def handle_endtag(self, tag):
            self.parts.append(f"</{tag}>")

        def handle_data(self, data):
            leading = data[:len(data) - len(data.lstrip())]
            trailing = data[len(data.rstrip()):]
            text = data.strip()
            self.parts.append(escape(leading + localized_text.get(text, text) + trailing, quote=False))

        def handle_comment(self, data):
            self.parts.append(f"<!--{data}-->")

        def handle_decl(self, decl):
            self.parts.append(f"<!{decl}>")

    parser = LocalizedMarkup()
    parser.feed(markup)
    return "".join(parser.parts)


def localize_disease(disease, language="en"):
    if language not in ("hi", "hinglish"):
        return disease
    localized = copy.copy(disease)
    disease_translations = (
        DISEASE_TRANSLATIONS if language == "hi" else HINGLISH_DISEASE_TRANSLATIONS
    )
    localized.update(disease_translations.get(disease.get("slug"), {}))
    return localized


def localize_comparison(topic, language="en"):
    if language not in ("hi", "hinglish") or not topic:
        return topic
    disease_translations = (
        DISEASE_TRANSLATIONS if language == "hi" else HINGLISH_DISEASE_TRANSLATIONS
    ).get(topic.get("slug"))
    if not disease_translations:
        return topic
    localized = copy.copy(topic)
    localized.update({
        "name": disease_translations["name"],
        "overview": [disease_translations["summary"], disease_translations["description"]],
        "symptoms": disease_translations["symptoms"],
        "prevention": disease_translations["prevention"],
        "treatment": [disease_translations["treatment"]],
    })
    return localized
