"""Curated study practice and a transparent rule-based study companion."""

import random
import re
import json
import os
import base64
import time
from urllib.error import HTTPError, URLError
from urllib.parse import quote_plus
from urllib.request import Request, urlopen

from medlineplus import search_medlineplus

GREETINGS = [
    "Hi again, future clinician! What are we learning today?",
    "Welcome back! Ready to make a tricky topic feel simpler?",
    "Hey there, study buddy. What would you like to explore?",
    "Good to see you! Shall we practice, review, or unpack a question?",
]

EXAM_GUIDES = {
    "neet": (
        "NEET-UG preparation usually focuses on Biology, Chemistry, and Physics. "
        "For an exact current syllabus and exam rules, check the official NTA "
        "information bulletin. I can offer introductory practice and study prompts."
    ),
    "mcat": (
        "The MCAT has sections on biological and biochemical foundations, chemical "
        "and physical foundations, psychological and social foundations, and "
        "critical analysis and reasoning skills. Check the AAMC website for the "
        "current official content outline and policies."
    ),
    "aamc": (
        "AAMC offers official MCAT preparation resources, practice materials, and "
        "exam information. Check aamc.org for current materials and policies. I "
        "can help with original introductory practice, not reproduce official papers."
    ),
}
EXAM_SOURCES = {
    "neet": ("National Testing Agency — NEET", "https://exams.nta.ac.in/NEET/"),
    "mcat": ("AAMC — Prepare for the MCAT", "https://students-residents.aamc.org/prepare-mcat-exam"),
    "aamc": ("AAMC — MCAT exam resources", "https://students-residents.aamc.org/prepare-mcat-exam"),
}
SEARCH_FILLER_WORDS = {
    "a", "an", "and", "are", "about", "biology", "can", "describe", "does",
    "exam", "explain", "for", "give", "help", "how", "is", "me", "of", "on",
    "please", "study", "symptom", "symptoms", "tell", "the", "this", "to",
    "what", "with", "would",
}
VITAMIN_OVERVIEW_TRIGGERS = (
    "all vitamin", "every vitamin", "all the vitamins",
    "vitamins and their sources", "sources of all vitamins",
    "vitamin deficiency diseases", "vitamin deficiencies",
    "all vitamins deficiency", "all vitamin sources",
)
VITAMIN_OVERVIEW = """Here is a study overview of all 13 essential vitamins. Deficiency effects vary with severity, duration, diet, absorption, and health; these are common associations, not a way to diagnose yourself.

| Vitamin | Common deficiency condition or findings | Dietary sources |
|---|---|---|
| A (retinol/carotenoids) | Night blindness and, when severe, xerophthalmia | Liver, eggs, dairy; orange and dark-green vegetables |
| B1 (thiamin) | Beriberi; Wernicke-Korsakoff syndrome in at-risk people | Whole/enriched grains, pork, legumes, nuts |
| B2 (riboflavin) | Ariboflavinosis: cracked lips, sore mouth, and skin findings | Dairy, eggs, meat, enriched grains, almonds |
| B3 (niacin) | Pellagra: classically dermatitis, diarrhea, and cognitive changes | Poultry, fish, peanuts, legumes, enriched grains |
| B5 (pantothenic acid) | Deficiency is rare; fatigue and tingling may occur | Widespread in foods, including poultry, eggs, whole grains, legumes |
| B6 (pyridoxine) | Anemia, dermatitis, or neurologic findings | Fish, poultry, potatoes, chickpeas, bananas |
| B7 (biotin) | Rare; dermatitis and hair loss can occur | Cooked eggs, nuts, seeds, legumes, fish |
| B9 (folate) | Megaloblastic anemia; inadequate folate in pregnancy increases neural-tube-defect risk | Leafy greens, legumes, citrus, fortified grains |
| B12 (cobalamin) | Megaloblastic anemia and possible nerve damage; pernicious anemia is one cause of B12 deficiency | Meat, fish, eggs, dairy, fortified foods |
| C (ascorbic acid) | Scurvy: poor wound healing, gum changes, and bruising | Citrus, berries, peppers, tomatoes, broccoli |
| D (calciferol) | Rickets in children; osteomalacia in adults | Fatty fish, egg yolk, fortified milk/alternatives |
| E (tocopherol) | Rare; nerve or muscle problems, especially with fat-malabsorption disorders | Nuts, seeds, vegetable oils, leafy greens |
| K (phylloquinone/menaquinones) | Easy bruising or bleeding from impaired clotting | Leafy greens, broccoli, some fermented foods |

This is general study information, not personal medical advice. If you suspect a deficiency, a clinician can assess causes and appropriate testing. Do not start high-dose supplements on this basis; some vitamins can be harmful in excess or interact with medicines. Dietary sources and fortification vary by country."""
VITAMIN_OVERVIEW += "\nLINK:NIH Office of Dietary Supplements fact sheets|https://ods.od.nih.gov/factsheets/list-all/"

QUESTIONS = [
    {
        "id": "cell",
        "subject": "Biology",
        "question": "Which organelle is the main site of ATP production during aerobic respiration?",
        "options": ["Ribosome", "Mitochondrion", "Golgi apparatus", "Lysosome"],
        "answer": 1,
        "explanation": "Mitochondria carry out much of aerobic cellular respiration and produce ATP through oxidative phosphorylation.",
    },
    {
        "id": "genetics",
        "subject": "Biology",
        "question": "If a heterozygous dominant parent (Aa) is crossed with aa, what fraction of offspring are expected to be Aa?",
        "options": ["0%", "25%", "50%", "100%"],
        "answer": 2,
        "explanation": "The Aa parent can pass A or a; the aa parent can only pass a. Half of the expected combinations are Aa.",
    },
    {
        "id": "chemistry",
        "subject": "Chemistry",
        "question": "At 25 °C, a neutral aqueous solution has a pH closest to:",
        "options": ["2", "5", "7", "12"],
        "answer": 2,
        "explanation": "At 25 °C, a neutral solution has equal hydrogen and hydroxide ion concentrations, corresponding to pH 7.",
    },
    {
        "id": "physics",
        "subject": "Physics",
        "question": "A 2 kg object accelerates at 3 m/s². What is the net force?",
        "options": ["1.5 N", "5 N", "6 N", "9 N"],
        "answer": 2,
        "explanation": "Newton's second law gives F = ma = 2 kg × 3 m/s² = 6 N.",
    },
    {
        "id": "heart",
        "subject": "Anatomy",
        "question": "Which chamber of the heart pumps oxygenated blood into the aorta?",
        "options": ["Right atrium", "Right ventricle", "Left atrium", "Left ventricle"],
        "answer": 3,
        "explanation": "The left ventricle pumps oxygenated blood through the aortic valve into the aorta and systemic circulation.",
    },
    {
        "id": "kidney",
        "subject": "Physiology",
        "question": "What is the functional filtering unit of the kidney?",
        "options": ["Alveolus", "Neuron", "Nephron", "Osteon"],
        "answer": 2,
        "explanation": "Nephrons filter blood and process the filtrate to form urine.",
    },
    {
        "id": "blood",
        "subject": "Biology",
        "question": "Which blood component primarily transports oxygen using hemoglobin?",
        "options": ["Platelets", "Red blood cells", "Plasma proteins", "White blood cells"],
        "answer": 1,
        "explanation": "Hemoglobin in red blood cells binds and transports most oxygen in the blood.",
    },
    {
        "id": "immunity",
        "subject": "Immunology",
        "question": "Which cells can produce antibodies as part of the adaptive immune response?",
        "options": ["Plasma cells", "Red blood cells", "Platelets", "Osteocytes"],
        "answer": 0,
        "explanation": "Activated B lymphocytes can differentiate into plasma cells, which secrete antibodies.",
    },
    {
        "id": "lungs",
        "subject": "Physiology",
        "question": "Where does most gas exchange between air and blood occur in the lungs?",
        "options": ["Trachea", "Bronchi", "Alveoli", "Larynx"],
        "answer": 2,
        "explanation": "Alveoli provide thin-walled surfaces closely associated with capillaries for oxygen and carbon-dioxide exchange.",
    },
    {
        "id": "dna",
        "subject": "Genetics",
        "question": "Which nitrogenous base pairs with adenine in DNA?",
        "options": ["Cytosine", "Guanine", "Thymine", "Uracil"],
        "answer": 2,
        "explanation": "In DNA, adenine pairs with thymine; in RNA, adenine pairs with uracil.",
    },
    {
        "id": "insulin",
        "subject": "Endocrinology",
        "question": "Which organ produces insulin?",
        "options": ["Thyroid", "Pancreas", "Adrenal gland", "Spleen"],
        "answer": 1,
        "explanation": "Beta cells in the pancreatic islets produce insulin, a hormone that helps regulate blood glucose.",
    },
]


def next_question_id(after=None):
    """Return a deterministic next ID without shared mutable quiz state."""
    ids = [question["id"] for question in QUESTIONS]
    try:
        index = ids.index(after)
    except ValueError:
        index = -1
    return ids[(index + 1) % len(ids)]


def create_mind_map(disease):
    return [
        {"title": "Overview", "points": [disease["summary"], disease["description"]]},
        {"title": "Common symptoms", "points": disease["symptoms"]},
        {"title": "Prevention & risk reduction", "points": disease["prevention"]},
        {"title": "Treatment & care", "points": [disease["treatment"]]},
        {"title": "Study takeaways", "points": disease["study_points"]},
    ]


def create_reference_mind_map(topic, reference=None):
    summary = reference.get("summary", "").strip() if reference else ""
    sentences = [
        sentence.strip()
        for sentence in re.split(r"(?<=[.!?])\s+", summary)
        if sentence.strip()
    ]
    branches = [{
        "title": "Overview",
        "points": [summary] if summary else ["No reviewed overview was found in the search result."],
    }]
    categories = (
        (
            "Symptoms",
            r"\b(?:symptoms?|signs?(?: and symptoms?)?)\b",
            f"Symptom details for {topic} were not included in this search summary.",
        ),
        (
            "Prevention",
            r"\b(?:prevent\w*|prevention|risk reduction|reduce the risk|lower the risk|protect\w*|avoid\w*)\b",
            f"Prevention details for {topic} were not included in this search summary.",
        ),
        (
            "Treatment & care",
            r"\b(?:treat\w*|medications?|medicines?|drugs?|therap(?:y|ies)|cur(?:e|able)|manage\w*)\b",
            f"Treatment details for {topic} were not included in this search summary.",
        ),
    )
    for title, pattern, fallback in categories:
        points = [sentence for sentence in sentences if re.search(pattern, sentence, re.IGNORECASE)]
        branches.append({"title": title, "points": points or [fallback]})
    branches.append({
        "title": "Study questions",
        "points": [
            f"What does a trusted source say about the causes of {topic}?",
            f"What details about {topic} should be confirmed in the full article?",
        ],
    })
    return branches


def create_flashcards(disease):
    cards = [
        {
            "category": "OVERVIEW",
            "question": f"What is {disease['name']}?",
            "answer": [disease["summary"], disease["description"]],
        },
        {
            "category": "SYMPTOMS",
            "question": f"What are common symptoms of {disease['name']}?",
            "answer": disease["symptoms"],
        },
        {
            "category": "PREVENTION",
            "question": f"What can help prevent or reduce risk from {disease['name']}?",
            "answer": disease["prevention"],
        },
        {
            "category": "TREATMENT",
            "question": f"What should you know about treatment for {disease['name']}?",
            "answer": [disease["treatment"]],
        },
    ]
    cards.extend(
        {
            "category": "QUICK REVIEW",
            "question": f"What is a key study point about {disease['name']}?",
            "answer": [point],
        }
        for point in disease["study_points"]
    )
    return cards


def create_reference_flashcards(topic, reference, language="en"):
    import translations

    branches = translations.localize_reference_branches(
        create_reference_mind_map(topic, reference),
        topic,
        language,
    )
    return [
        {
            "category": branch["title"].upper(),
            "question": f"What does the MedlinePlus article say about {branch['title'].lower()} for {topic}?",
            "answer": branch["points"],
        }
        for branch in branches
        if branch["title"] != translations.translate("Study questions", language)
    ]


def compare_health_topic(topic, disease=None, reference=None, reference_error=None):
    if disease:
        return {
            "name": disease["name"],
            "slug": disease["slug"],
            "overview": [disease["summary"], disease["description"]],
            "symptoms": disease["symptoms"],
            "prevention": disease["prevention"],
            "treatment": [disease["treatment"]],
            "source_name": disease["source_name"],
            "source_url": disease["source_url"],
        }

    branches = {
        branch["title"]: branch["points"]
        for branch in create_reference_mind_map(topic, reference)
    }
    if reference:
        return {
            "name": topic,
            "overview": branches.get("Overview", ["No overview details in the search result."]),
            "symptoms": branches.get("Symptoms", ["No symptom details in the search summary."]),
            "prevention": branches.get("Prevention", ["No prevention details in the search summary."]),
            "treatment": branches.get("Treatment & care", ["No treatment details in the search summary."]),
            "source_name": reference["title"],
            "source_url": reference["url"],
        }

    unavailable = [
        f"MedlinePlus lookup failed: {reference_error}"
        if reference_error
        else f"No reviewed MedlinePlus details were found for {topic}."
    ]
    return {
        "name": topic,
        "overview": unavailable,
        "symptoms": unavailable,
        "prevention": unavailable,
        "treatment": unavailable,
        "source_name": "Search MedlinePlus",
        "source_url": "https://medlineplus.gov/",
    }


AI_SYSTEM_PROMPT = (
    "You are WellNote's friendly study and general-purpose assistant. Answer the "
    "user's actual question clearly and helpfully, including general knowledge, "
    "medical education, exam study, business, practical questions, or harmless "
    "humor when asked. Explain uncertainty; do not claim perfect or exhaustive "
    "knowledge and do not invent facts or citations. For medical questions, "
    "provide general educational information, never diagnose or prescribe "
    "personal treatment, and advise consulting a qualified clinician for "
    "personal concerns. For emergencies, direct the user to local emergency "
    "services. Keep answers useful, respectful, and appropriately concise."
)
AI_TIMEOUT_SECONDS = 45
GEMINI_TRANSIENT_FALLBACK_MODELS = (
    "gemini-3.8-flash",
    "gemini-3.1-flash-lite",
)


def ai_provider_configured():
    return all(_ai_configuration())


class GeminiSpeechError(Exception):
    """A safe, user-facing failure from Gemini text-to-speech."""


def gemini_speech_configured():
    return bool(os.environ.get("GEMINI_API_KEY", "").strip())


def generate_gemini_speech(text, language="en"):
    """Return Gemini's generated WAV bytes, or None when no Gemini key is set."""
    api_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not api_key:
        return None
    text = text.strip()
    if not text or len(text) > 5000:
        raise GeminiSpeechError("Speech text must contain 1 to 5000 characters.")

    speech_styles = {
        "en": "Speak clearly in a warm, friendly English tutor voice.",
        "hi": "Speak clearly in natural Hindi with a Hindi (India) accent.",
        "hinglish": "Speak naturally in conversational Hinglish with a clear Indian accent. Pronounce Hindi words naturally and English terms clearly.",
    }
    payload = json.dumps({
        "model": os.environ.get("GEMINI_TTS_MODEL", "gemini-3.8-flash-tts").strip(),
        "input": [{
            "type": "user_input",
            "content": [{
                "type": "text",
                "text": text,
                "annotations": [{
                    "type": "speech_metadata",
                    "style": speech_styles.get(language, speech_styles["en"]),
                }],
            }],
        }],
        "response_format": {"type": "audio"},
        "generation_config": {
            "speech_config": [{"voice": "Kore"}],
        },
    }).encode("utf-8")
    request = Request(
        "https://generativelanguage.googleapis.com/v1beta/interactions",
        data=payload,
        headers={
            "x-goog-api-key": api_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="POST",
    )
    try:
        with urlopen(request, timeout=AI_TIMEOUT_SECONDS) as response:
            data = json.loads(response.read(15_000_001).decode("utf-8"))
        output_audio = data.get("output_audio")
        audio_data = output_audio.get("data") if isinstance(output_audio, dict) else None
        if not audio_data:
            audio_data = next(
                (
                    content.get("data")
                    for step in reversed(data.get("steps", []))
                    if step.get("type") == "model_output"
                    for content in reversed(step.get("content", []))
                    if content.get("type") == "audio" and content.get("data")
                ),
                None,
            )
        if not audio_data:
            raise GeminiSpeechError("Gemini did not return speech audio.")
        audio = base64.b64decode(audio_data, validate=True)
        if len(audio) > 15_000_000 or not audio.startswith(b"RIFF"):
            raise GeminiSpeechError("Gemini returned audio in an unsupported format.")
        return audio
    except HTTPError as exc:
        status = exc.code
        exc.close()
        if status in (401, 403):
            raise GeminiSpeechError(
                "Gemini rejected the API key or does not allow this speech model."
            ) from None
        if status == 429:
            raise GeminiSpeechError(
                "Gemini is rate-limiting speech requests. Please try again later."
            ) from None
        raise GeminiSpeechError(
            f"Gemini speech returned an HTTP {status} error."
        ) from None
    except (URLError, TimeoutError, OSError):
        raise GeminiSpeechError(
            "Gemini speech could not be reached. Check the connection and try again."
        ) from None
    except (AttributeError, KeyError, TypeError, ValueError, UnicodeDecodeError):
        raise GeminiSpeechError(
            "Gemini returned an unreadable speech response."
        ) from None


def _ai_configuration():
    wellnote_key = os.environ.get("WELLNOTE_AI_API_KEY", "").strip()
    gemini_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if wellnote_key:
        return (
            wellnote_key,
            os.environ.get("WELLNOTE_AI_MODEL", "").strip(),
            os.environ.get("WELLNOTE_AI_BASE_URL", "https://api.openai.com/v1").strip(),
        )
    if gemini_key:
        return (
            gemini_key,
            os.environ.get(
                "GEMINI_MODEL",
                os.environ.get("WELLNOTE_AI_MODEL", "gemini-3.5-flash-lite"),
            ).strip(),
            "https://generativelanguage.googleapis.com/v1beta/openai",
        )
    return (
        "",
        os.environ.get("WELLNOTE_AI_MODEL", "").strip(),
        os.environ.get("WELLNOTE_AI_BASE_URL", "https://api.openai.com/v1").strip(),
    )


def _ai_endpoint(base_url):
    base = base_url.rstrip("/")
    if base.endswith("/chat/completions"):
        return base
    if base.endswith("/openai"):
        return base + "/chat/completions"
    if base.endswith("/v1"):
        return base + "/chat/completions"
    return base + "/v1/chat/completions"


def generate_ai_response(prompt, language="en"):
    """Call a configured OpenAI-compatible chat-completions service.

    Returns None only when no AI provider configuration is present. Provider
    failures return an explicit user-facing message rather than silently
    pretending that a local canned answer came from a model.
    """
    api_key, model, base_url = _ai_configuration()
    if not api_key and not model:
        return None
    if not api_key or not model or not base_url:
        return (
            "The AI assistant is not fully configured. Set "
            "WELLNOTE_AI_API_KEY and WELLNOTE_AI_MODEL, and optionally "
            "WELLNOTE_AI_BASE_URL, then restart the app."
        )

    language_instructions = {
        "hi": "Respond in clear, natural Hindi written in Devanagari. Preserve WellNote and official names as written.",
        "hinglish": "Respond in conversational Hinglish using Roman script. Preserve WellNote and official names as written.",
    }
    system_prompt = AI_SYSTEM_PROMPT
    if language in language_instructions:
        system_prompt += " " + language_instructions[language]
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt},
    ]
    gemini_key = os.environ.get("GEMINI_API_KEY", "").strip()
    uses_gemini_directly = (
        bool(gemini_key)
        and not os.environ.get("WELLNOTE_AI_API_KEY", "").strip()
        and base_url.rstrip("/")
        == "https://generativelanguage.googleapis.com/v1beta/openai"
    )
    models = [model]
    if uses_gemini_directly:
        models.extend(
            candidate
            for candidate in GEMINI_TRANSIENT_FALLBACK_MODELS
            if candidate != model
        )
    data = None
    last_transient_status = None
    for model_index, candidate_model in enumerate(models):
        payload = json.dumps({
            "model": candidate_model,
            "messages": messages,
        }).encode("utf-8")
        request = Request(
            _ai_endpoint(base_url),
            data=payload,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            method="POST",
        )
        retry_count = 3 if model_index == 0 else 1
        for attempt in range(retry_count):
            try:
                with urlopen(request, timeout=AI_TIMEOUT_SECONDS) as response:
                    data = json.loads(response.read(2_000_000).decode("utf-8"))
                break
            except HTTPError as exc:
                status = exc.code
                exc.close()
                if status in (408, 500, 502, 503, 504):
                    last_transient_status = status
                    if attempt < retry_count - 1:
                        base_delay = 2 ** attempt
                        time.sleep(random.uniform(base_delay * 0.5, base_delay * 1.5))
                        continue
                    if model_index < len(models) - 1:
                        break
                    retry_note = (
                        "The app retried and tried an alternate Gemini model; "
                        if uses_gemini_directly
                        else "The app retried automatically; "
                    )
                    return (
                        f"The AI provider is temporarily unavailable (HTTP {status}). "
                        f"{retry_note}please wait a moment and try again."
                    )
                if status in (401, 403):
                    return (
                        "The AI provider rejected its credentials. Check the configured "
                        "API key and provider access, then try again."
                    )
                if status == 404:
                    return (
                        "The AI provider could not find the configured model or endpoint "
                        "(HTTP 404). For Gemini, check GEMINI_MODEL and model access; "
                        "the default is gemini-3.5-flash-lite."
                    )
                if status == 429:
                    return "The AI provider is rate-limiting requests. Please wait a moment and try again."
                return f"The AI provider returned an HTTP {status} error. Please try again later."
            except (URLError, TimeoutError, OSError):
                return "The AI provider could not be reached. Check the connection and provider URL, then try again."
            except (KeyError, IndexError, TypeError, ValueError, UnicodeDecodeError):
                return "The AI provider returned an unreadable response. Please check the provider configuration and try again."
        if data is not None:
            break
    if data is None and last_transient_status is not None:
        return (
            f"The AI provider is temporarily unavailable (HTTP {last_transient_status}). "
            "The app retried and tried alternate Gemini models; "
            "please wait a moment and try again."
        )
    try:
        answer = data["choices"][0]["message"]["content"]
        if not isinstance(answer, str) or not answer.strip():
            return "The AI provider returned an empty answer. Please try again."
        return answer.strip()
    except (KeyError, IndexError, TypeError, ValueError, UnicodeDecodeError):
        return "The AI provider returned an unreadable response. Please check the provider configuration and try again."


def make_response(prompt, language="en"):
    """Provide an educational response or a relevant trusted reference."""
    text = prompt.strip()
    lowered = text.casefold()
    if not text:
        return "Tell me a topic, exam, or question and we’ll take it one step at a time."
    ai_response = generate_ai_response(text, language)
    if ai_response is not None:
        return ai_response
    study_intent = any(
        term in lowered
        for term in ("study", "exam", "homework", "assignment", "textbook", "biology", "chemistry", "physics", "for a test", "for neet", "for mcat")
    )
    normalized_question = re.sub(r"[^a-z0-9]+", " ", lowered).strip()
    asks_all_vitamins = any(trigger in lowered for trigger in VITAMIN_OVERVIEW_TRIGGERS)
    if "vitamin" in normalized_question and (
        asks_all_vitamins
        or (
            any(term in normalized_question for term in ("all", "every", "each"))
            and any(term in normalized_question for term in ("source", "deficien", "vitamin"))
        )
    ):
        return VITAMIN_OVERVIEW
    if not study_intent and any(term in lowered for term in ("my symptom", "my symptoms", "i have a symptom", "i have symptoms", "diagnos", "my pain", "my cough", "treatment for me", "i have a fever", "i have pain")):
        return (
            "I can explain medical concepts for study, but I can’t assess personal "
            "symptoms or diagnose you. Please speak with a qualified health "
            "professional. If this may be an emergency, contact local emergency services."
        )
    if any(word in lowered for word in ("hospital", "clinic", "doctor", "physician")) and any(
        word in lowered for word in ("find", "near", "nearest", "location", "where", "search")
    ):
        location = text
        for marker in ("near me", "nearest", "near", "in "):
            position = lowered.find(marker)
            if position >= 0:
                location = text[position + len(marker):].strip(" ?.,")
                if location:
                    break
        if not location or location.casefold() == "me":
            location = "hospitals near me"
        maps_url = "https://www.google.com/maps/search/?api=1&query=" + quote_plus(
            "hospitals " + location
        )
        return (
            "I can help you find options. Open this map search to see hospitals "
            "and clinics near the location you entered. Check services, current "
            "hours, and contact details directly with the facility. For an "
            "emergency, contact your local emergency services."
            f"\nLINK:Find hospitals and clinics|{maps_url}"
        )
    if "homework" in lowered or "assignment" in lowered:
        return (
            "I can help you study through an assignment step by step. Share one "
            "specific question and what you have tried, and I’ll offer a "
            "learning-focused explanation. Please verify important work with "
            "your course materials or instructor."
        )
    if any(word in lowered for word in ("business", "business plan", "startup", "start a business", "entrepreneur")):
        return (
            "For a healthcare business idea, start with the problem and people "
            "served, then research local needs, regulations, licensing, privacy, "
            "staffing, costs, and a sustainable revenue model. Avoid collecting "
            "patient information until you understand the applicable privacy "
            "requirements. Tell me the business type and country and I can help "
            "you make a learning-focused checklist."
        )
    if any(word in lowered for word in ("joke", "funny", "tell me a joke")):
        return (
            "Why did the mitochondrion get invited to every study group? It always "
            "brought the ATP!"
        )
    if (
        "powerhouse" in normalized_question
        or "power house" in normalized_question
    ) and any(term in normalized_question for term in ("cell", "organelle", "mitochondri")):
        return (
            "The mitochondrion (plural: mitochondria) is commonly called the "
            "“powerhouse of the cell.” It produces most of the cell’s ATP through "
            "cellular respiration, especially oxidative phosphorylation in its "
            "inner membrane. ATP is a major usable energy source for cellular "
            "processes."
        )
    for exam, guide in EXAM_GUIDES.items():
        if exam in lowered:
            return guide
    concepts = {
        "photosynthesis": "Photosynthesis converts light energy into chemical energy. In plants, chlorophyll captures light; the light-dependent reactions make ATP and NADPH, which the Calvin cycle uses to fix carbon dioxide into sugars.",
        "mitochondri": "Mitochondria make much of a cell’s ATP during aerobic respiration. Glycolysis happens in the cytoplasm; the citric acid cycle and oxidative phosphorylation are associated with mitochondria in eukaryotic cells.",
        "osmosis": "Osmosis is the net movement of water across a selectively permeable membrane toward the side with a higher effective solute concentration. The exact outcome depends on membrane permeability and solution conditions.",
        "neuron": "A neuron receives and transmits information. Dendrites and the cell body integrate many signals; an action potential travels along the axon, and synapses communicate with target cells.",
        "blood pressure": "Blood pressure is the force of circulating blood against artery walls, usually recorded as systolic over diastolic pressure. Interpretation depends on measurement and individual context; personal readings should be discussed with a clinician.",
        "antibiotic resistance": "Antimicrobial resistance can emerge when microbes survive medicines that once worked against them. Appropriate prescribing, infection prevention, and taking medicines exactly as directed help address the problem; do not start or stop a prescription without clinical advice.",
        "study plan": "Try a weekly cycle: list exam topics, break them into small sessions, use active recall and spaced review, alternate practice questions with checking explanations, and reserve time to revisit mistakes. Share your exam date and subjects for a tailored timetable.",
        "study strategy": "A useful routine is active recall followed by spaced review: close your notes, retrieve the key ideas, check gaps, and revisit them after increasing intervals. Mix practice questions with short explanations of mistakes.",
    }
    for concept, answer in concepts.items():
        if concept in lowered:
            return answer
    subjects = {
        "biology": "I can help with cell biology, genetics, physiology, or another biology topic. Ask a focused question or try one of the original practice questions below.",
        "chemistry": "I can help review foundational chemistry, such as pH, bonding, or reactions. Ask a focused question or try an original practice question below.",
        "physics": "I can help review foundational physics, such as mechanics or units. Ask a focused question or try an original practice question below.",
    }
    for subject, response in subjects.items():
        if subject in lowered and len(text.split()) <= 3:
            return response
    search_terms = [
        word.strip("?!.,:;()") for word in text.split()
        if word.casefold().strip("?!.,:;()") not in SEARCH_FILLER_WORDS
    ]
    results, error = search_medlineplus(" ".join(search_terms) or text)
    if results:
        return (
            f"For study and general learning — MedlinePlus reference, {results[0]['title']}: {results[0]['summary']} "
            "This information is not a diagnosis or personal treatment advice. "
            f"\nLINK:Read the MedlinePlus article|{results[0]['url']}"
        )
    detail = f" The reference lookup is temporarily unavailable: {error}" if error else ""
    return (
        "I couldn’t find a specific reviewed article for that wording. Try "
        "the main topic or a more specific medical term in MedlinePlus. A "
        "general AI provider is not configured, so I can’t reliably answer "
        "open-ended questions yet. Configure WELLNOTE_AI_API_KEY and "
        "WELLNOTE_AI_MODEL (see README.md) to enable general conversation."
        + detail
        + "\nLINK:Search MedlinePlus|https://medlineplus.gov/"
    )


def greeting():
    return random.choice(GREETINGS)
