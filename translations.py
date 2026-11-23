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
    "This condition is not in WellNote’s small, reviewed starter library.": "यह स्थिति WellNote की सीमित, समीक्षित शुरुआती लाइब्रेरी में शामिल नहीं है।",
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
    "Enter any health topic. WellNote uses its reviewed guide or searches MedlinePlus for a reference.": "कोई भी स्वास्थ्य विषय लिखें। WellNote अपनी समीक्षित गाइड या MedlinePlus संदर्भ खोजेगा।",
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
    "Compare two health topics using reviewed WellNote guides or linked MedlinePlus references.": "WellNote की समीक्षित गाइड या MedlinePlus संदर्भों से दो स्वास्थ्य विषयों की तुलना करें।",
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
    "Some references and study content may still be in English.": "बाहरी स्वास्थ्य स्रोतों के उद्धरण और कुछ अध्ययन-साथी के जवाब मूल भाषा में दिख सकते हैं।",
    "Main navigation": "मुख्य नेविगेशन",
    "English": "अंग्रेज़ी",
    "Hindi": "हिन्दी",
    "Hinglish": "हिंग्लिश",
    "YOUR PERSONAL HEALTH LIBRARY": "आपकी निजी स्वास्थ्य लाइब्रेरी",
    "Results for": "इसके परिणाम",
    "Results for “{query}”": "“{query}” के परिणाम",
    "MEDLINEPLUS REFERENCE": "MedlinePlus संदर्भ",
    "TRUSTED HEALTH REFERENCES": "विश्वसनीय स्वास्थ्य संदर्भ",
    "MEDLINEPLUS · NATIONAL LIBRARY OF MEDICINE": "MedlinePlus · राष्ट्रीय चिकित्सा पुस्तकालय",
    "No reviewed WellNote guide for “{query}”": "“{query}” के लिए WellNote की समीक्षित गाइड उपलब्ध नहीं है",
    "MedlinePlus did not find a matching health topic. Try a broader search directly on the MedlinePlus website.": "MedlinePlus को इससे मिलता-जुलता स्वास्थ्य विषय नहीं मिला। MedlinePlus वेबसाइट पर अधिक सामान्य शब्द खोजें।",
    "We won’t guess at symptoms or treatment. MedlinePlus is the U.S. National Library of Medicine’s health information service.": "हम लक्षणों या उपचार के बारे में अनुमान नहीं लगाएँगे। MedlinePlus, अमेरिकी राष्ट्रीय चिकित्सा पुस्तकालय की स्वास्थ्य जानकारी सेवा है।",
    "Visit MedlinePlus ↗": "MedlinePlus पर जाएँ ↗",
    "These summaries are provided by MedlinePlus, a service of the U.S. National Library of Medicine. Open a source for its full article and references.": "ये सारांश अमेरिकी राष्ट्रीय चिकित्सा पुस्तकालय की सेवा MedlinePlus से हैं। पूरा लेख और उसके संदर्भ देखने के लिए स्रोत खोलें।",
    "Read the full reference ↗": "पूरा संदर्भ पढ़ें ↗",
    "Information for “{query}”": "“{query}” के लिए जानकारी",
    "Find information about {topic}": "{topic} के बारे में जानकारी खोजें",
    "Mind map for {topic}": "{topic} का माइंड मैप",
    "CARD {current} OF {total}": "कार्ड {current} / {total}",
    "Flashcard navigation": "फ्लैशकार्ड नेविगेशन",
    "OVERVIEW": "परिचय",
    "SYMPTOMS": "लक्षण",
    "PREVENTION": "रोकथाम",
    "TREATMENT": "उपचार",
    "QUICK REVIEW": "झटपट दोहराएँ",
    "TREATMENT & CARE": "उपचार और देखभाल",
    "No reviewed WellNote guide for": "WellNote की समीक्षित गाइड उपलब्ध नहीं है:",
    "Question not found": "प्रश्न नहीं मिला",
    "Choose another practice question.": "कोई दूसरा अभ्यास प्रश्न चुनें।",
    "The page may have moved or the topic is not in this starter library.": "पृष्ठ शायद स्थानांतरित हो गया है या यह विषय शुरुआती लाइब्रेरी में नहीं है।",
    "Unsupported language": "यह भाषा उपलब्ध नहीं है",
    "Page not found": "पृष्ठ नहीं मिला",
    "Method not allowed": "यह अनुरोध स्वीकार नहीं है",
    "Topic not found": "विषय नहीं मिला",
    "A health topic is required": "स्वास्थ्य विषय लिखना ज़रूरी है",
    "Flashcard navigation": "फ्लैशकार्ड नेविगेशन",
    "EXTERNAL HEALTH REFERENCE": "बाहरी स्वास्थ्य संदर्भ",
    "This condition is not in WellNote’s small, reviewed starter library.": "यह स्थिति WellNote की सीमित, समीक्षित शुरुआती लाइब्रेरी में शामिल नहीं है।",
    "For education, not diagnosis.": "शिक्षा के लिए, निदान के लिए नहीं।",
    "No matching health topic found": "इससे मिलता-जुलता स्वास्थ्य विषय नहीं मिला",
    "Search MedlinePlus for details ↗": "जानकारी के लिए MedlinePlus खोजें ↗",
    "Open the full article for details ↗": "अधिक जानकारी के लिए पूरा लेख खोलें ↗",
    "Available details from the reference appear in the branches below.": "संदर्भ में उपलब्ध जानकारी नीचे की शाखाओं में दिखाई गई है।",
    "No source details were available for branches; use the linked article to research this topic.": "शाखाओं के लिए स्रोत में जानकारी उपलब्ध नहीं थी; इस विषय के अध्ययन के लिए जुड़ा लेख खोलें।",
    "No matching MedlinePlus article was found, so only the topic node is shown.": "MedlinePlus का मिलता-जुलता लेख नहीं मिला, इसलिए केवल विषय दिखाया गया है।",
    "No MedlinePlus article was found": "MedlinePlus का कोई लेख नहीं मिला",
    "Based on WellNote’s educational guide.": "WellNote की शैक्षिक गाइड पर आधारित।",
    "Based on a MedlinePlus search result.": "MedlinePlus के खोज परिणाम पर आधारित।",
    "Read": "पढ़ें",
    "Open the full article": "पूरा लेख खोलें",
    "Search MedlinePlus": "MedlinePlus खोजें",
    "STUDY TOPIC": "अध्ययन का विषय",
    "For example: malaria, lupus, or asthma": "उदाहरण: मलेरिया, ल्यूपस या अस्थमा",
    "For example: asthma, malaria, or diabetes": "उदाहरण: अस्थमा, मलेरिया या मधुमेह",
    "For example: asthma": "उदाहरण: अस्थमा",
    "For example: seasonal flu": "उदाहरण: मौसमी फ्लू",
    "CARD": "कार्ड",
    "OF": "में से",
    "REVIEW": "दोहराएँ",
    "QUESTION": "प्रश्न",
    "← Previous": "← पिछला",
    "Next card →": "अगला कार्ड →",
    "Read the MedlinePlus article ↗": "MedlinePlus लेख पढ़ें ↗",
    "Review": "दोहराएँ",
    "No reviewed flashcards available": "समीक्षित फ्लैशकार्ड उपलब्ध नहीं हैं",
    "No MedlinePlus article was found": "MedlinePlus का कोई लेख नहीं मिला",
    "No factual flashcards were generated.": "तथ्यात्मक फ्लैशकार्ड नहीं बनाए गए।",
    "Search MedlinePlus ↗": "MedlinePlus खोजें ↗",
    "SIDE-BY-SIDE REVIEW": "आमने-सामने दोहराएँ",
    "Enter two different diseases or health topics to compare.": "तुलना करने के लिए दो अलग-अलग बीमारियों या स्वास्थ्य विषयों के नाम लिखें।",
    "FOCUSED REVIEW": "ध्यान से दोहराएँ",
    "Take a moment with the essentials, then revisit the full guide when you’re ready.": "पहले मुख्य बातें समझें, फिर तैयार होने पर पूरी गाइड पढ़ें।",
    "THREE THINGS TO REMEMBER": "याद रखने की तीन बातें",
    "Read the full guide →": "पूरी गाइड पढ़ें →",
    "Make a mind map": "माइंड मैप बनाएँ",
    "Study with flashcards": "फ्लैशकार्ड से पढ़ें",
    "Compare with another topic": "दूसरे विषय से तुलना करें",
    "REFLECT": "विचार करें",
    "What would you like to ask a health professional?": "आप स्वास्थ्यकर्मी से क्या पूछना चाहेंगे?",
    "Use what you’ve learned to prepare questions for a conversation about your own health.": "अपनी सेहत के बारे में बातचीत के लिए सवाल तैयार करने में सीखी हुई बातों का उपयोग करें।",
    "Keep learning in context.": "सीखते समय संदर्भ याद रखें।",
    "Study notes summarize educational topics; they are not diagnostic tools or personal care recommendations.": "अध्ययन नोट्स शैक्षिक विषयों का सार हैं; वे निदान के साधन या व्यक्तिगत देखभाल की सलाह नहीं हैं।",
    "PRACTICE, AT YOUR PACE": "अपनी गति से अभ्यास करें",
    "One question at a time": "एक बार में एक सवाल",
    "Original introductory examples. Check your reasoning with each explanation.": "अभ्यास के लिए बनाए गए शुरुआती सवाल। हर व्याख्या से अपने तर्क को जाँचें।",
    "ORIGINAL PRACTICE": "मौलिक अभ्यास",
    "Correct!": "सही!",
    "Not quite—review the explanation.": "अभी सही नहीं—व्याख्या दोबारा पढ़ें।",
    "Check answer": "जवाब जाँचें",
    "Next question →": "अगला सवाल →",
    "Original practice only.": "केवल मौलिक अभ्यास।",
    "These introductory questions are not official NEET, MCAT, or AAMC exam items and do not represent the full syllabus.": "ये शुरुआती सवाल NEET, MCAT या AAMC की आधिकारिक परीक्षा के सवाल नहीं हैं और पूरे पाठ्यक्रम को शामिल नहीं करते।",
    "EXAM STARTERS": "परीक्षा की तैयारी",
    "Try: “Help me plan for NEET”, “Explain biology”, “Help with homework”, or “Give me a study strategy.”": "ऐसे पूछें: “NEET की योजना बनाने में मदद करें”, “जीवविज्ञान समझाएँ”, “होमवर्क में मदद करें” या “पढ़ाई की रणनीति बताएँ।”",
    "Confirm exam requirements with official sources.": "परीक्षा की आवश्यकताएँ आधिकारिक स्रोतों से जाँचें।",
    "A model provider is configured; its answers may be incomplete or incorrect. For personal medical concerns, consult a qualified health professional.": "AI मॉडल जुड़ा है; उसके जवाब अधूरे या गलत हो सकते हैं। निजी स्वास्थ्य संबंधी चिंताओं के लिए योग्य स्वास्थ्यकर्मी से सलाह लें।",
    "No AI model is configured in this app, so replies use curated local study content. To use Gemini, set GEMINI_API_KEY; the default model is gemini-2.5-flash. For other providers, see README.md. For personal medical concerns, consult a qualified health professional.": "इस ऐप में AI मॉडल सेट नहीं है, इसलिए जवाब चुनी हुई स्थानीय अध्ययन सामग्री पर आधारित हैं। Gemini के लिए GEMINI_API_KEY सेट करें; डिफ़ॉल्ट मॉडल gemini-2.5-flash है। अन्य प्रदाताओं के लिए README.md देखें। निजी स्वास्थ्य संबंधी चिंताओं के लिए योग्य स्वास्थ्यकर्मी से सलाह लें।",
    "Spoken answers are not supported in this browser.": "इस ब्राउज़र में जवाब सुनने की सुविधा उपलब्ध नहीं है।",
    "Ask a question first, then your answer can be read aloud.": "पहले सवाल पूछें, फिर जवाब सुन सकते हैं।",
    "Reading the answer aloud.": "जवाब पढ़कर सुनाया जा रहा है।",
    "Finished reading the answer.": "जवाब पढ़कर सुनाना पूरा हुआ।",
    "Audio playback stopped or is unavailable.": "ऑडियो रुक गया है या उपलब्ध नहीं है।",
    "Audio stopped.": "ऑडियो रोक दिया गया।",
    "Checking for the right speech voice…": "सही आवाज़ खोजी जा रही है…",
    "Install a {language} speech voice in your device’s language or speech settings, then try again.": "इस डिवाइस में {language} आवाज़ उपलब्ध नहीं है। डिवाइस की वाक् सेटिंग में आवाज़ इंस्टॉल करके फिर कोशिश करें।",
    "Creating speech with Gemini…": "Gemini से आवाज़ बनाई जा रही है…",
    "If no matching device voice is installed, Read aloud sends the reply text to Google Gemini to create audio.": "यदि डिवाइस में सही भाषा की आवाज़ नहीं है, तो जवाब का पाठ ऑडियो बनाने के लिए Google Gemini को भेजा जाएगा।",
    "Hindi for Hinglish": "हिंग्लिश के लिए हिन्दी",
    "You asked": "आपने पूछा",
    "Study buddy": "अध्ययन साथी",
    "Try a focused study question or one of the original practice items below.": "पढ़ाई से जुड़ा कोई खास सवाल पूछें या नीचे दिए मौलिक अभ्यास सवालों में से चुनें।",
    "No matching health topic found": "इससे मिलता-जुलता स्वास्थ्य विषय नहीं मिला",
    "Read the answer aloud": "जवाब सुनें",
    "Hi again, future clinician! What are we learning today?": "नमस्ते, भावी चिकित्सक! आज क्या सीखना चाहेंगे?",
    "Welcome back! Ready to make a tricky topic feel simpler?": "वापस स्वागत है! किसी कठिन विषय को सरलता से समझने के लिए तैयार हैं?",
    "Hey there, study buddy. What would you like to explore?": "नमस्ते, अध्ययन साथी। आप किस विषय को समझना चाहेंगे?",
    "Good to see you! Shall we practice, review, or unpack a question?": "आपसे मिलकर अच्छा लगा! अभ्यास करें, दोहराएँ या किसी सवाल को समझें?",
    "Review key points →": "मुख्य बातें दोहराएँ →",
    "Choose any topic, try to recall the answer, then reveal it and move through the deck.": "कोई भी विषय चुनें, जवाब याद करने की कोशिश करें, फिर उसे देखें और अगले कार्ड पर जाएँ।",
    "Learn safely.": "सुरक्षित तरीके से सीखें।",
    "Cards summarize WellNote educational guides or linked MedlinePlus references. They are for study, not personal diagnosis or treatment.": "कार्ड WellNote की शैक्षिक गाइड या जुड़े MedlinePlus संदर्भों का सार हैं। ये अध्ययन के लिए हैं, व्यक्तिगत निदान या उपचार के लिए नहीं।",
    "Maps outside WellNote’s reviewed guides use linked references or clearly labeled study prompts. They are educational and not personal medical advice.": "WellNote की समीक्षित गाइड से बाहर के माइंड मैप जुड़े संदर्भों या स्पष्ट रूप से बताए गए अध्ययन संकेतों पर आधारित हैं। ये शैक्षिक हैं, व्यक्तिगत चिकित्सकीय सलाह नहीं।",
    "Topics can differ in important ways beyond this summary. This comparison cannot determine what condition a person has or which treatment is right for them.": "इन विषयों में इस सारांश से परे महत्वपूर्ण अंतर हो सकते हैं। यह तुलना किसी व्यक्ति की स्थिति या उसके लिए सही उपचार निर्धारित नहीं कर सकती।",
    "Compare": "तुलना",
    "Sources": "स्रोत",
    "Read the MedlinePlus article ↗": "MedlinePlus लेख पढ़ें ↗",
    "← Study room": "← अध्ययन कक्ष",
    "Reveal answer": "जवाब देखें",
    "← Previous": "← पिछला",
    "Study takeaways": "अध्ययन की मुख्य बातें",
    "Study questions": "अध्ययन के प्रश्न",
    "No reviewed overview was found in the search result.": "खोज परिणाम में कोई समीक्षित परिचय नहीं मिला।",
    "No overview details in the search result.": "खोज परिणाम में परिचय की जानकारी नहीं मिली।",
    "No symptom details in the search summary.": "खोज सारांश में लक्षणों की जानकारी नहीं मिली।",
    "No prevention details in the search summary.": "खोज सारांश में रोकथाम की जानकारी नहीं मिली।",
    "No treatment details in the search summary.": "खोज सारांश में उपचार की जानकारी नहीं मिली।",
    "No prevention details for this topic were included in the search summary.": "खोज सारांश में इस विषय की रोकथाम की जानकारी नहीं थी।",
    "No symptom details for this topic were included in the search summary.": "खोज सारांश में इस विषय के लक्षणों की जानकारी नहीं थी।",
    "No treatment details for this topic were included in the search summary.": "खोज सारांश में इस विषय के उपचार की जानकारी नहीं थी।",
    "No details for this topic were included in the search summary.": "खोज सारांश में इस विषय की जानकारी नहीं थी।",
    "Symptom details for {topic} were not included in this search summary.": "खोज सारांश में {topic} के लक्षणों की जानकारी नहीं थी।",
    "Prevention details for {topic} were not included in this search summary.": "खोज सारांश में {topic} की रोकथाम की जानकारी नहीं थी।",
    "Treatment details for {topic} were not included in this search summary.": "खोज सारांश में {topic} के उपचार की जानकारी नहीं थी।",
    "What does a trusted source say about the causes of {topic}?": "{topic} के कारणों के बारे में विश्वसनीय स्रोत क्या कहता है?",
    "What details about {topic} should be confirmed in the full article?": "पूरे लेख में {topic} की किन बातों की पुष्टि करनी चाहिए?",
    "No reviewed MedlinePlus details were found for {topic}.": "{topic} के लिए MedlinePlus में समीक्षित जानकारी नहीं मिली।",
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
    "This condition is not in WellNote’s small, reviewed starter library.": "Yeh condition WellNote ki chhoti, reviewed starter library mein nahi hai.",
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
    "Enter any health topic. WellNote uses its reviewed guide or searches MedlinePlus for a reference.": "Koi bhi health topic likhein. WellNote apni reviewed guide ya MedlinePlus reference dhoondhega.",
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
    "Compare two health topics using reviewed WellNote guides or linked MedlinePlus references.": "WellNote ki reviewed guides ya MedlinePlus references se do health topics compare karein.",
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
    "Some references and study content may still be in English.": "Bahaari health sources ke uddharan aur study buddy ke kuch jawaab mool bhasha mein dikh sakte hain.",
    "Main navigation": "Main navigation",
    "English": "Angrezi",
    "Hindi": "Hindi",
    "Hinglish": "Hinglish",
    "YOUR PERSONAL HEALTH LIBRARY": "Aapki personal health library",
    "Results for “{query}”": "“{query}” ke results",
    "MEDLINEPLUS REFERENCE": "MedlinePlus reference",
    "TRUSTED HEALTH REFERENCES": "Bharosemand health references",
    "MEDLINEPLUS · NATIONAL LIBRARY OF MEDICINE": "MedlinePlus · National Library of Medicine",
    "No reviewed WellNote guide for “{query}”": "“{query}” ke liye WellNote ki reviewed guide nahi hai",
    "MedlinePlus did not find a matching health topic. Try a broader search directly on the MedlinePlus website.": "MedlinePlus ko milta-julta health topic nahi mila. MedlinePlus website par zyada general shabd search karein.",
    "We won’t guess at symptoms or treatment. MedlinePlus is the U.S. National Library of Medicine’s health information service.": "Hum symptoms ya treatment ka andaza nahi lagaayenge. MedlinePlus, U.S. National Library of Medicine ki health information service hai.",
    "Visit MedlinePlus ↗": "MedlinePlus par jaayein ↗",
    "These summaries are provided by MedlinePlus, a service of the U.S. National Library of Medicine. Open a source for its full article and references.": "Yeh summaries U.S. National Library of Medicine ki service MedlinePlus se hain. Poora article aur uske references padhne ke liye source kholein.",
    "Read the full reference ↗": "Poora reference padhein ↗",
    "Information for “{query}”": "“{query}” ke baare mein jaankari",
    "Find information about {topic}": "{topic} ke baare mein jaankari dhoondhein",
    "Mind map for {topic}": "{topic} ka mind map",
    "CARD {current} OF {total}": "Card {current} / {total}",
    "Flashcard navigation": "Flashcard navigation",
    "OVERVIEW": "Overview",
    "SYMPTOMS": "Symptoms",
    "PREVENTION": "Bachaav",
    "TREATMENT": "Treatment",
    "QUICK REVIEW": "Quick review",
    "TREATMENT & CARE": "Treatment aur care",
    "Question not found": "Sawaal nahi mila",
    "Choose another practice question.": "Koi doosra practice sawaal chunein.",
    "The page may have moved or the topic is not in this starter library.": "Page shayad move ho gaya hai ya yeh topic starter library mein nahi hai.",
    "Unsupported language": "Yeh language available nahi hai",
    "Page not found": "Page nahi mila",
    "Method not allowed": "Yeh request allowed nahi hai",
    "Topic not found": "Topic nahi mila",
    "A health topic is required": "Health topic likhna zaroori hai",
    "EXTERNAL HEALTH REFERENCE": "External health reference",
    "This condition is not in WellNote’s small, reviewed starter library.": "Yeh condition WellNote ki chhoti, reviewed starter library mein nahi hai.",
    "For education, not diagnosis.": "Jaankari ke liye, diagnosis ke liye nahi.",
    "Search MedlinePlus for details ↗": "Details ke liye MedlinePlus search karein ↗",
    "Open the full article for details ↗": "Details ke liye poora article kholein ↗",
    "Available details from the reference appear in the branches below.": "Reference mein available details neeche branches mein dikhengi.",
    "No source details were available for branches; use the linked article to research this topic.": "Branches ke liye source details available nahi thi; is topic ko padhne ke liye linked article kholein.",
    "No matching MedlinePlus article was found, so only the topic node is shown.": "MedlinePlus ka matching article nahi mila, isliye sirf topic dikhaya gaya hai.",
    "Based on WellNote’s educational guide.": "WellNote ki educational guide par based.",
    "Based on a MedlinePlus search result.": "MedlinePlus search result par based.",
    "STUDY TOPIC": "Study topic",
    "For example: malaria, lupus, or asthma": "Jaise: malaria, lupus ya asthma",
    "For example: asthma, malaria, or diabetes": "Jaise: asthma, malaria ya diabetes",
    "CARD": "Card",
    "OF": "mein se",
    "REVIEW": "Review",
    "QUESTION": "Sawaal",
    "← Previous": "← Pichhla",
    "Next card →": "Agla card →",
    "Read the MedlinePlus article ↗": "MedlinePlus article padhein ↗",
    "No reviewed flashcards available": "Reviewed flashcards available nahi hain",
    "No factual flashcards were generated.": "Factual flashcards nahi bane.",
    "SIDE-BY-SIDE REVIEW": "Saath-saath review",
    "Enter two different diseases or health topics to compare.": "Compare karne ke liye do alag bimariyon ya health topics ke naam likhein.",
    "FOCUSED REVIEW": "Dhyaan se review karein",
    "Take a moment with the essentials, then revisit the full guide when you’re ready.": "Pehle zaroori baatein samjhein, phir taiyaar hone par poori guide dekhein.",
    "THREE THINGS TO REMEMBER": "Yaad rakhne ki teen baatein",
    "Read the full guide →": "Poori guide padhein →",
    "Make a mind map": "Mind map banaayein",
    "Study with flashcards": "Flashcards se padhein",
    "Compare with another topic": "Doosre topic se compare karein",
    "REFLECT": "Sochiye",
    "What would you like to ask a health professional?": "Aap health professional se kya poochhna chahenge?",
    "Use what you’ve learned to prepare questions for a conversation about your own health.": "Apni health ke baare mein baat karne ke liye sawaal taiyaar karne mein seekhi baaton ka use karein.",
    "Keep learning in context.": "Context ke saath seekhte rahein.",
    "Study notes summarize educational topics; they are not diagnostic tools or personal care recommendations.": "Study notes educational topics ka saar hain; ye diagnosis ya personal care recommendations nahi hain.",
    "PRACTICE, AT YOUR PACE": "Apni speed se practice karein",
    "One question at a time": "Ek baar mein ek sawaal",
    "Original introductory examples. Check your reasoning with each explanation.": "Practice ke liye banaye gaye shuruaati sawaal. Har explanation se apni soch check karein.",
    "ORIGINAL PRACTICE": "Original practice",
    "Correct!": "Sahi!",
    "Not quite—review the explanation.": "Abhi sahi nahi—explanation dobara dekhein.",
    "Check answer": "Jawaab check karein",
    "Next question →": "Agla sawaal →",
    "Original practice only.": "Sirf original practice.",
    "These introductory questions are not official NEET, MCAT, or AAMC exam items and do not represent the full syllabus.": "Yeh shuruaati sawaal official NEET, MCAT ya AAMC exam ke nahi hain aur poora syllabus cover nahi karte.",
    "Try: “Help me plan for NEET”, “Explain biology”, “Help with homework”, or “Give me a study strategy.”": "Aise poochhein: “NEET ke liye plan banaayein”, “Biology samjhaayein”, “Homework mein madad karein” ya “Study strategy dein.”",
    "Confirm exam requirements with official sources.": "Exam requirements official sources se check karein.",
    "A model provider is configured; its answers may be incomplete or incorrect. For personal medical concerns, consult a qualified health professional.": "AI model connect hai; uske jawaab adhure ya galat ho sakte hain. Personal health concerns ke liye qualified health professional se salah lein.",
    "No AI model is configured in this app, so replies use curated local study content. To use Gemini, set GEMINI_API_KEY; the default model is gemini-2.5-flash. For other providers, see README.md. For personal medical concerns, consult a qualified health professional.": "Is app mein AI model set nahi hai, isliye jawaab chuni hui local study content par based hain. Gemini ke liye GEMINI_API_KEY set karein; default model gemini-2.5-flash hai. Doosre providers ke liye README.md dekhein. Personal health concerns ke liye qualified health professional se salah lein.",
    "Spoken answers are not supported in this browser.": "Is browser mein jawaab sunne ki suvidha available nahi hai.",
    "Ask a question first, then your answer can be read aloud.": "Pehle sawaal poochhein, phir jawaab suna ja sakta hai.",
    "Reading the answer aloud.": "Jawaab padhkar sunaaya ja raha hai.",
    "Finished reading the answer.": "Jawaab padhkar sunaana poora hua.",
    "Audio playback stopped or is unavailable.": "Audio ruk gaya hai ya available nahi hai.",
    "Audio stopped.": "Audio rok diya gaya.",
    "Checking for the right speech voice…": "Sahi awaaz dhoondhi ja rahi hai…",
    "Install a {language} speech voice in your device’s language or speech settings, then try again.": "Is device par {language} voice available nahi hai. Device ki speech settings mein voice install karke phir try karein.",
    "Creating speech with Gemini…": "Gemini se awaaz banaayi ja rahi hai…",
    "If no matching device voice is installed, Read aloud sends the reply text to Google Gemini to create audio.": "Agar device par matching language ki voice nahi hai, to reply ka text audio banane ke liye Google Gemini ko bheja jaayega.",
    "Hindi for Hinglish": "Hinglish ke liye Hindi",
    "You asked": "Aapne poochha",
    "Study buddy": "Study buddy",
    "Try a focused study question or one of the original practice items below.": "Padhai se juda koi khaas sawaal poochhein ya neeche diye original practice sawaalon mein se chunein.",
    "Hi again, future clinician! What are we learning today?": "Namaste, future clinician! Aaj kya seekhna chahenge?",
    "Welcome back! Ready to make a tricky topic feel simpler?": "Waapas swagat hai! Kisi mushkil topic ko aasaan tareeke se samajhne ke liye taiyaar hain?",
    "Hey there, study buddy. What would you like to explore?": "Namaste, study buddy. Aap kis topic ko explore karna chahenge?",
    "Good to see you! Shall we practice, review, or unpack a question?": "Aapse milkar achha laga! Practice karein, review karein, ya kisi sawaal ko samjhein?",
    "Review key points →": "Zaroori baatein review karein →",
    "Choose any topic, try to recall the answer, then reveal it and move through the deck.": "Koi bhi topic chunein, jawaab yaad karne ki koshish karein, phir use dekhkar agle card par jaayein.",
    "Learn safely.": "Surakshit tareeke se seekhein.",
    "Cards summarize WellNote educational guides or linked MedlinePlus references. They are for study, not personal diagnosis or treatment.": "Cards WellNote ki educational guides ya linked MedlinePlus references ka saar hain. Ye study ke liye hain, personal diagnosis ya treatment ke liye nahi.",
    "Maps outside WellNote’s reviewed guides use linked references or clearly labeled study prompts. They are educational and not personal medical advice.": "WellNote ki reviewed guides ke baahar ke mind maps linked references ya saaf study prompts par based hain. Ye jaankari ke liye hain, personal medical advice nahi.",
    "Topics can differ in important ways beyond this summary. This comparison cannot determine what condition a person has or which treatment is right for them.": "Topics mein is summary se aage bhi zaroori farq ho sakte hain. Yeh comparison kisi vyakti ki condition ya uske liye sahi treatment nahi bata sakta.",
    "Compare": "Compare karein",
    "Sources": "Sources",
    "Review": "Review karein",
    "Read the MedlinePlus article ↗": "MedlinePlus article padhein ↗",
    "← Study room": "← Study room",
    "Reveal answer": "Jawaab dekhein",
    "Study takeaways": "Study ki zaroori baatein",
    "Study questions": "Study ke sawaal",
    "No reviewed overview was found in the search result.": "Search result mein koi reviewed overview nahi mila.",
    "No overview details in the search result.": "Search result mein overview details nahi mili.",
    "No symptom details in the search summary.": "Search summary mein symptoms ki details nahi mili.",
    "No prevention details in the search summary.": "Search summary mein bachaav ki details nahi mili.",
    "No treatment details in the search summary.": "Search summary mein treatment ki details nahi mili.",
    "No prevention details for this topic were included in the search summary.": "Search summary mein is topic ke bachaav ki details nahi thi.",
    "No symptom details for this topic were included in the search summary.": "Search summary mein is topic ke symptoms ki details nahi thi.",
    "No treatment details for this topic were included in the search summary.": "Search summary mein is topic ke treatment ki details nahi thi.",
    "No details for this topic were included in the search summary.": "Search summary mein is topic ki details nahi thi.",
    "Symptom details for {topic} were not included in this search summary.": "Search summary mein {topic} ke symptoms ki details nahi thi.",
    "Prevention details for {topic} were not included in this search summary.": "Search summary mein {topic} ke bachaav ki details nahi thi.",
    "Treatment details for {topic} were not included in this search summary.": "Search summary mein {topic} ke treatment ki details nahi thi.",
    "What does a trusted source say about the causes of {topic}?": "{topic} ke causes ke baare mein trusted source kya kehta hai?",
    "What details about {topic} should be confirmed in the full article?": "Poore article mein {topic} ki kaunsi details confirm karni chahiye?",
    "No reviewed MedlinePlus details were found for {topic}.": "{topic} ke liye MedlinePlus mein reviewed details nahi mili.",
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


def translate_format(value, language="en", **values):
    return translate(value, language).format(**values)


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
        if not topic:
            return topic
        localized = copy.copy(topic)
        for field in ("overview", "symptoms", "prevention", "treatment"):
            localized[field] = [
                localize_reference_point(point, topic.get("name", ""), language)
                for point in topic.get(field, [])
            ]
        return localized
    localized = copy.copy(topic)
    localized.update({
        "name": disease_translations["name"],
        "overview": [disease_translations["summary"], disease_translations["description"]],
        "symptoms": disease_translations["symptoms"],
        "prevention": disease_translations["prevention"],
        "treatment": [disease_translations["treatment"]],
    })
    return localized


def localize_reference_point(point, topic, language="en"):
    templates = (
        "Symptom details for {topic} were not included in this search summary.",
        "Prevention details for {topic} were not included in this search summary.",
        "Treatment details for {topic} were not included in this search summary.",
        "What does a trusted source say about the causes of {topic}?",
        "What details about {topic} should be confirmed in the full article?",
    )
    for template in templates:
        if point == template.format(topic=topic):
            return translate_format(template, language, topic=topic)
    if point.startswith("No reviewed MedlinePlus details were found for "):
        return translate_format(
            "No reviewed MedlinePlus details were found for {topic}.",
            language,
            topic=topic,
        )
    return translate(point, language)


def localize_reference_branches(branches, topic, language="en"):
    if language not in ("hi", "hinglish"):
        return branches
    localized = []
    for branch in branches:
        localized.append({
            "title": translate(branch["title"], language),
            "points": [
                localize_reference_point(point, topic, language)
                for point in branch["points"]
            ],
        })
    return localized


PRACTICE_TRANSLATIONS = {
    "hi": {
        "cell": (
            "जीवविज्ञान",
            "वायवीय श्वसन के दौरान ATP उत्पादन का मुख्य स्थान कौन-सा कोशिकांग है?",
            ["राइबोसोम", "माइटोकॉन्ड्रियन", "गॉल्जी उपकरण", "लाइसोसोम"],
            "माइटोकॉन्ड्रिया में वायवीय कोशिकीय श्वसन का बड़ा हिस्सा होता है और ऑक्सीडेटिव फॉस्फोराइलेशन से ATP बनता है।",
        ),
        "genetics": (
            "आनुवंशिकी",
            "यदि विषमयुग्मजी प्रभावी जनक (Aa) का संकरण aa से हो, तो कितनी संतति Aa होने की अपेक्षा है?",
            ["0%", "25%", "50%", "100%"],
            "Aa जनक A या a दे सकता है; aa जनक केवल a दे सकता है। संभावित संयोजनों में आधे Aa होते हैं।",
        ),
        "chemistry": (
            "रसायन विज्ञान",
            "25 °C पर उदासीन जलीय विलयन का pH लगभग कितना होता है?",
            ["2", "5", "7", "12"],
            "25 °C पर उदासीन विलयन में हाइड्रोजन और हाइड्रॉक्साइड आयनों की सांद्रता समान होती है, जो pH 7 के अनुरूप है।",
        ),
        "physics": (
            "भौतिक विज्ञान",
            "2 kg का कोई पिंड 3 m/s² से त्वरित होता है। उस पर कुल बल कितना है?",
            ["1.5 N", "5 N", "6 N", "9 N"],
            "न्यूटन के दूसरे नियम के अनुसार F = ma = 2 kg × 3 m/s² = 6 N।",
        ),
        "heart": (
            "शरीर रचना विज्ञान",
            "हृदय का कौन-सा कक्ष ऑक्सीजनयुक्त रक्त को महाधमनी में पंप करता है?",
            ["दायाँ आलिंद", "दायाँ निलय", "बायाँ आलिंद", "बायाँ निलय"],
            "बायाँ निलय महाधमनी वाल्व से ऑक्सीजनयुक्त रक्त को महाधमनी और पूरे शरीर के परिसंचरण में पंप करता है।",
        ),
        "kidney": (
            "शरीर क्रिया विज्ञान",
            "गुर्दे की कार्यात्मक छनन इकाई कौन-सी है?",
            ["वायुकोष्ठिका", "न्यूरॉन", "नेफ्रॉन", "ऑस्टिऑन"],
            "नेफ्रॉन रक्त को छानते हैं और छनित द्रव को संसाधित करके मूत्र बनाते हैं।",
        ),
        "blood": (
            "जीवविज्ञान",
            "हीमोग्लोबिन की सहायता से मुख्यतः कौन-सा रक्त घटक ऑक्सीजन पहुँचाता है?",
            ["प्लेटलेट", "लाल रक्त कोशिकाएँ", "प्लाज़्मा प्रोटीन", "श्वेत रक्त कोशिकाएँ"],
            "लाल रक्त कोशिकाओं में मौजूद हीमोग्लोबिन अधिकांश ऑक्सीजन को बाँधकर पहुँचाता है।",
        ),
        "immunity": (
            "प्रतिरक्षा विज्ञान",
            "अनुकूली प्रतिरक्षा प्रतिक्रिया में कौन-सी कोशिकाएँ एंटीबॉडी बना सकती हैं?",
            ["प्लाज़्मा कोशिकाएँ", "लाल रक्त कोशिकाएँ", "प्लेटलेट", "ऑस्टियोसाइट"],
            "सक्रिय B लिम्फोसाइट प्लाज़्मा कोशिकाओं में बदल सकते हैं, जो एंटीबॉडी स्रावित करती हैं।",
        ),
        "lungs": (
            "शरीर क्रिया विज्ञान",
            "फेफड़ों में हवा और रक्त के बीच अधिकांश गैसों का आदान-प्रदान कहाँ होता है?",
            ["श्वासनली", "ब्रॉन्कस", "वायुकोष्ठिकाएँ", "कंठ"],
            "वायुकोष्ठिकाओं की पतली दीवारें केशिकाओं के पास होती हैं, जहाँ ऑक्सीजन और कार्बन डाइऑक्साइड का आदान-प्रदान होता है।",
        ),
        "dna": (
            "आनुवंशिकी",
            "DNA में एडेनिन के साथ कौन-सा नाइट्रोजनस क्षार जोड़ा बनाता है?",
            ["साइटोसिन", "ग्वानिन", "थाइमिन", "यूरैसिल"],
            "DNA में एडेनिन, थाइमिन के साथ जोड़ा बनाता है; RNA में एडेनिन, यूरैसिल के साथ जुड़ता है।",
        ),
        "insulin": (
            "अंतःस्राव विज्ञान",
            "इंसुलिन कौन-सा अंग बनाता है?",
            ["थायरॉइड", "अग्न्याशय", "अधिवृक्क ग्रंथि", "प्लीहा"],
            "अग्न्याशय के आइलेट्स में बीटा कोशिकाएँ इंसुलिन बनाती हैं, जो रक्त ग्लूकोज़ को नियंत्रित करने में मदद करता है।",
        ),
    },
    "hinglish": {
        "cell": (
            "Biology",
            "Aerobic respiration ke dauraan ATP banane ka main site kaunsa organelle hai?",
            ["Ribosome", "Mitochondrion", "Golgi apparatus", "Lysosome"],
            "Mitochondria mein aerobic cellular respiration ka bada hissa hota hai aur oxidative phosphorylation se ATP banta hai.",
        ),
        "genetics": (
            "Genetics",
            "Agar heterozygous dominant parent (Aa) ka cross aa se ho, to kitne offspring Aa hone ki umeed hai?",
            ["0%", "25%", "50%", "100%"],
            "Aa parent A ya a de sakta hai; aa parent sirf a de sakta hai. Expected combinations mein aadhe Aa hote hain.",
        ),
        "chemistry": (
            "Chemistry",
            "25 °C par neutral aqueous solution ka pH lagbhag kya hota hai?",
            ["2", "5", "7", "12"],
            "25 °C par neutral solution mein hydrogen aur hydroxide ions ki concentration barabar hoti hai, jo pH 7 hota hai.",
        ),
        "physics": (
            "Physics",
            "2 kg ka object 3 m/s² se accelerate karta hai. Net force kitna hoga?",
            ["1.5 N", "5 N", "6 N", "9 N"],
            "Newton ke second law se F = ma = 2 kg × 3 m/s² = 6 N.",
        ),
        "heart": (
            "Anatomy",
            "Heart ka kaunsa chamber oxygenated blood ko aorta mein pump karta hai?",
            ["Right atrium", "Right ventricle", "Left atrium", "Left ventricle"],
            "Left ventricle aortic valve se oxygenated blood ko aorta aur poori body circulation mein pump karta hai.",
        ),
        "kidney": (
            "Physiology",
            "Kidney ki functional filtering unit kaunsi hai?",
            ["Alveolus", "Neuron", "Nephron", "Osteon"],
            "Nephrons blood filter karte hain aur filtrate ko process karke urine banaate hain.",
        ),
        "blood": (
            "Biology",
            "Hemoglobin ki madad se kaunsa blood component zyadaatar oxygen pahunchata hai?",
            ["Platelets", "Red blood cells", "Plasma proteins", "White blood cells"],
            "Red blood cells mein hemoglobin zyadaatar oxygen ko bind karke transport karta hai.",
        ),
        "immunity": (
            "Immunology",
            "Adaptive immune response mein kaunsi cells antibodies bana sakti hain?",
            ["Plasma cells", "Red blood cells", "Platelets", "Osteocytes"],
            "Activated B lymphocytes plasma cells ban sakte hain, jo antibodies release karte hain.",
        ),
        "lungs": (
            "Physiology",
            "Lungs mein air aur blood ke beech zyadaatar gas exchange kahaan hota hai?",
            ["Trachea", "Bronchi", "Alveoli", "Larynx"],
            "Alveoli ki patli walls capillaries ke paas hoti hain, jahaan oxygen aur carbon dioxide ka exchange hota hai.",
        ),
        "dna": (
            "Genetics",
            "DNA mein adenine ke saath kaunsa nitrogenous base pair karta hai?",
            ["Cytosine", "Guanine", "Thymine", "Uracil"],
            "DNA mein adenine, thymine ke saath pair karta hai; RNA mein adenine, uracil ke saath pair karta hai.",
        ),
        "insulin": (
            "Endocrinology",
            "Insulin kaunsa organ banata hai?",
            ["Thyroid", "Pancreas", "Adrenal gland", "Spleen"],
            "Pancreatic islets ki beta cells insulin banaati hain, jo blood glucose regulate karne mein madad karta hai.",
        ),
    },
}


def localize_question(question, language="en"):
    localized = copy.copy(question)
    practice = PRACTICE_TRANSLATIONS.get(language, {}).get(question.get("id"))
    if practice:
        localized.update({
            "subject": practice[0],
            "question": practice[1],
            "options": practice[2],
            "explanation": practice[3],
        })
    return localized


FLASHCARD_QUESTION_TEMPLATES = {
    "hi": {
        "OVERVIEW": "{name} क्या है?",
        "SYMPTOMS": "{name} के सामान्य लक्षण क्या हैं?",
        "PREVENTION": "{name} को रोकने या इसका जोखिम कम करने में क्या मदद कर सकता है?",
        "TREATMENT": "{name} के उपचार के बारे में क्या जानना चाहिए?",
        "QUICK REVIEW": "{name} के अध्ययन की एक मुख्य बात क्या है?",
        "REFERENCE": "MedlinePlus लेख में {topic} के {section} के बारे में क्या बताया गया है?",
    },
    "hinglish": {
        "OVERVIEW": "{name} kya hai?",
        "SYMPTOMS": "{name} ke aam symptoms kya hain?",
        "PREVENTION": "{name} ko rokne ya iska risk kam karne mein kya madad kar sakta hai?",
        "TREATMENT": "{name} ke treatment ke baare mein kya jaanna chahiye?",
        "QUICK REVIEW": "{name} ke study ki ek zaroori baat kya hai?",
        "REFERENCE": "MedlinePlus article mein {topic} ke {section} ke baare mein kya bataya gaya hai?",
    },
}


def localize_flashcard_question(card, topic, language="en"):
    templates = FLASHCARD_QUESTION_TEMPLATES.get(language)
    if not templates:
        return card["question"]
    category = card.get("category", "").upper()
    if "MedlinePlus article say about " in card.get("question", ""):
        section = card["question"].split("MedlinePlus article say about ", 1)[1].split(" for ", 1)[0]
        return templates["REFERENCE"].format(
            topic=topic,
            section=translate(section, language).lower(),
        )
    template = templates.get(category)
    return template.format(name=topic) if template else card["question"]
