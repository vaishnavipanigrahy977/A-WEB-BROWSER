import unittest
from io import BytesIO
import base64
import json
import os
import re
from urllib.error import HTTPError
from unittest.mock import patch
from urllib.parse import quote_plus

import app as wellnote_app
import body_verse
from app import COOKIE_NAME, LANGUAGE_COOKIE_NAME, TEXTBOOK_COOKIE_NAME, application
from medlineplus import search_medlineplus
import openstax
from study import EXAM_GUIDES, QUESTIONS, ai_provider_configured, generate_ai_response, make_response, next_question_id
import translations
import textbooks


def request(path="/", method="GET", query="", cookie="", form="", host="localhost:8000", forwarded_proto=""):
    result = {}

    def start_response(status, headers):
        result["status"] = status
        result["headers"] = dict(headers)

    body = application({
        "REQUEST_METHOD": method, "PATH_INFO": path, "QUERY_STRING": query,
        "HTTP_COOKIE": cookie, "HTTP_HOST": host,
        "HTTP_X_FORWARDED_PROTO": forwarded_proto,
        "CONTENT_LENGTH": str(len(form.encode())),
        "wsgi.input": BytesIO(form.encode()),
    }, start_response)
    result["body_bytes"] = b"".join(body)
    result["body"] = result["body_bytes"].decode("utf-8", "replace")
    return result


class MedicalAppTests(unittest.TestCase):
    def test_server_uses_default_and_environment_port(self):
        server = unittest.mock.Mock()
        with patch.dict(os.environ, {}, clear=True), patch("app.make_server", return_value=server) as make_server:
            wellnote_app.serve()
        make_server.assert_called_once_with("0.0.0.0", 8000, application)
        server.serve_forever.assert_called_once_with()

        server.reset_mock()
        with patch.dict(os.environ, {"PORT": "4321"}), patch("app.make_server", return_value=server) as make_server:
            wellnote_app.serve()
        make_server.assert_called_once_with("0.0.0.0", 4321, application)
        server.serve_forever.assert_called_once_with()

    def test_home_and_search(self):
        self.assertIn("Asthma", request()["body"])
        self.assertIn("not medical advice", request()["body"])
        result = request(query="q=ASTHMA")
        self.assertIn("Asthma", result["body"])
        self.assertNotIn("Type 2 diabetes</h3>", result["body"])
        self.assertIn("&lt;script&gt;", request(query="q=%3Cscript%3E")["body"])

    def test_study_room_links_curated_textbook_library(self):
        body = request("/study")["body"]
        self.assertIn('href="/study/textbooks">Open textbook library', body)

        library = request("/study/textbooks")
        self.assertTrue(library["status"].startswith("200"))
        for expected in (
            "A library for learning",
            "Anatomy and Physiology 2e",
            "Microbiology",
            "Introductory college",
            "CC BY-NC-SA 4.0",
            "Official source",
            "Educational use only.",
        ):
            self.assertIn(expected, library["body"])

    def test_research_decoder_routes_and_assets_are_removed(self):
        self.assertNotIn("research-decoder", request("/study")["body"])
        for path in (
            "/study/research-decoder",
            "/static/research-decoder.css",
            "/static/research-decoder.js",
        ):
            self.assertTrue(request(path)["status"].startswith("404"))
        post = request(
            "/study/research-decoder",
            method="POST",
            form="action=decode&abstract=example",
        )
        self.assertTrue(post["status"].startswith("404"))

    def test_textbook_detail_has_source_attribution_and_searchable_chapters(self):
        detail = request("/study/textbooks/anatomy-and-physiology-2e")
        for expected in (
            "J. Gordon Betts",
            "OpenStax, Rice University",
            "CC BY-NC-SA 4.0",
            "https://openstax.org/books/anatomy-and-physiology-2e",
            "Chapter 1: An Introduction to the Human Body",
            "Chapter 3: The Cellular Level of Organization",
            "A link-out reader, not a copy.",
        ):
            self.assertIn(expected, detail["body"])
        self.assertIn("https://openstax.org/books/anatomy-and-physiology-2e/pages/3-the-cellular-level-of-organization", detail["body"])

        searched = request(
            "/study/textbooks/anatomy-and-physiology-2e",
            query="q=lymphocyte",
        )["body"]
        self.assertIn("The Lymphatic System and Immunity", searched)
        self.assertNotIn("An Introduction to the Human Body", searched)

        filtered = request("/study/textbooks", query="subject=Microbiology+%26+infection")
        self.assertIn("Microbiology</a>", filtered["body"])
        self.assertNotIn("Anatomy and Physiology 2e</a>", filtered["body"])
        self.assertIn("&lt;script&gt;", request("/study/textbooks", query="q=%3Cscript%3E")["body"])

    def test_textbook_reader_controls_search_and_original_study_aids(self):
        reader = request(
            "/study/textbooks/microbiology/antimicrobial-drugs",
            query="font=large",
        )
        for expected in (
            'class="textbook-reading-pane large"',
            "font-controls",
            "GLOSSARY",
            "Selective toxicity",
            "REVIEW QUESTIONS",
            "Reveal a sample answer",
            "original WellNote learning aids",
            "Read full chapter at OpenStax",
            "https://openstax.org/books/microbiology/pages/14-antimicrobial-drugs",
            "CC BY-NC-SA 4.0",
        ):
            self.assertIn(expected, reader["body"])
        search_results = request(
            "/study/textbooks/microbiology/antimicrobial-drugs",
            query="q=incidence",
        )["body"]
        self.assertIn("Search results for “incidence”", search_results)
        self.assertIn("Chapter 16: Disease and Epidemiology", search_results)

        invalid_font = request(
            "/study/textbooks/microbiology/antimicrobial-drugs",
            query="font=huge",
        )["body"]
        self.assertIn('class="textbook-reading-pane medium"', invalid_font)
        self.assertTrue(request("/study/textbooks/no-such-book")["status"].startswith("404"))
        self.assertTrue(request("/study/textbooks/microbiology/no-such-chapter")["status"].startswith("404"))
        self.assertIn(".textbook-reader-layout", request("/static/textbooks.css")["body"])

    def test_textbook_bookmarks_and_completion_progress_persist_in_cookie(self):
        first = request(
            "/study/textbooks/state",
            method="POST",
            form="action=bookmark&book=anatomy-and-physiology-2e&chapter=cellular-level",
        )
        self.assertTrue(first["status"].startswith("303"))
        self.assertEqual(
            first["headers"]["Location"],
            "/study/textbooks/anatomy-and-physiology-2e/cellular-level",
        )
        cookie = first["headers"]["Set-Cookie"].split(";", 1)[0]
        self.assertIn(TEXTBOOK_COOKIE_NAME, cookie)
        reader = request(
            "/study/textbooks/anatomy-and-physiology-2e/cellular-level",
            cookie=cookie,
        )["body"]
        self.assertIn("Remove bookmark", reader)

        completed = request(
            "/study/textbooks/state",
            method="POST",
            cookie=cookie,
            form="action=complete&book=anatomy-and-physiology-2e&chapter=cellular-level",
        )
        updated_cookie = completed["headers"]["Set-Cookie"].split(";", 1)[0]
        reader = request(
            "/study/textbooks/anatomy-and-physiology-2e/cellular-level",
            cookie=updated_cookie,
        )["body"]
        self.assertIn("Mark as unread", reader)
        self.assertIn("1/4 selected chapters · 25%", reader)
        library = request("/study/textbooks", cookie=updated_cookie)["body"]
        self.assertIn("YOUR BOOKMARKS", library)
        self.assertIn("Chapter 3: The Cellular Level of Organization", library)

        invalid = request(
            "/study/textbooks/state",
            method="POST",
            form="action=bookmark&book=unknown&chapter=bad",
        )
        self.assertTrue(invalid["status"].startswith("400"))

    def test_openstax_catalog_search_only_returns_live_allowed_subjects(self):
        catalog = {
            "books": [
                {"title": "Anatomy and Physiology 2e", "slug": "books/anatomy-and-physiology-2e",
                 "book_state": "live", "subject_categories": ["Anatomy and Physiology"]},
                {"title": "Microbiology", "slug": "books/microbiology",
                 "book_state": "live", "subject_categories": ["Biology"]},
                {"title": "Chemistry 2e", "slug": "books/chemistry-2e",
                 "book_state": "live", "subject_categories": ["Chemistry"]},
                {"title": "College Physics 2e", "slug": "books/college-physics-2e",
                 "book_state": "live", "subject_categories": ["Physics"]},
                {"title": "Medical-Surgical Nursing", "slug": "books/medical-surgical-nursing",
                 "book_state": "live", "subject_categories": ["Medical-Surgical Nursing"]},
                {"title": "Biology Draft", "slug": "books/biology-draft",
                 "book_state": "draft", "subject_categories": ["Biology"]},
                {"title": "Unsafe link", "slug": "https://example.com/book",
                 "book_state": "live", "subject_categories": ["Biology"]},
            ]
        }
        payload = json.dumps(catalog).encode()
        with patch("openstax.urlopen", return_value=BytesIO(payload)):
            results, error = openstax.search_openstax_books("medical")
        self.assertIsNone(error)
        self.assertEqual(len(results), 4)
        self.assertEqual(
            {item["field"] for item in results},
            {"Biology", "Chemistry", "Physics", "Others"},
        )
        self.assertNotIn("Medical-Surgical Nursing", {item["title"] for item in results})
        self.assertTrue(all(item["url"].startswith("https://openstax.org/books/") for item in results))
        anatomy = next(item for item in results if item["title"] == "Anatomy and Physiology 2e")
        self.assertEqual(anatomy["field"], "Others")
        self.assertEqual(
            anatomy["subject_url"],
            "https://openstax.org/subjects/science#Anatomy%20and%20Physiology",
        )

        with patch("openstax.urlopen", return_value=BytesIO(payload)):
            chemistry, error = openstax.search_openstax_books("chemistry")
        self.assertIsNone(error)
        self.assertEqual([item["title"] for item in chemistry], ["Chemistry 2e"])

        with patch("openstax.urlopen", return_value=BytesIO(payload)):
            wrong_field, error = openstax.search_openstax_books("chemistry", "Physics")
        self.assertIsNone(error)
        self.assertEqual(wrong_field, [])

        with patch("openstax.urlopen", return_value=BytesIO(payload)):
            anatomy_only, error = openstax.search_openstax_books("medical", "Others")
        self.assertIsNone(error)
        self.assertEqual([item["title"] for item in anatomy_only], ["Anatomy and Physiology 2e"])

    def test_openstax_search_page_shows_not_found_and_catalog_errors(self):
        catalog = {"books": [
            {"title": "Biology 2e", "slug": "books/biology-2e",
             "book_state": "live", "subject_categories": ["Biology"]}
        ]}
        with patch("openstax.urlopen", return_value=BytesIO(json.dumps(catalog).encode())):
            found = request("/study/textbooks/search", query="q=biology")
        self.assertIn("LIVE OPENSTAX CATALOG", found["body"])
        self.assertIn("Biology 2e", found["body"])
        self.assertIn('href="https://openstax.org/books/biology-2e"', found["body"])
        self.assertIn('href="https://openstax.org/subjects/science#Biology"', found["body"])
        self.assertIn('value="Others">Others · Anatomy and Physiology', found["body"])

        with patch("openstax.urlopen", return_value=BytesIO(json.dumps(catalog).encode())):
            absent = request("/study/textbooks/search", query="q=rare+anatomy+book")
        self.assertIn("No such content available.", absent["body"])
        self.assertIn(
            "medical-related Physics, Chemistry, Biology, or Anatomy and Physiology",
            absent["body"],
        )
        for source_url in openstax.FIELD_URLS.values():
            self.assertIn(f'href="{source_url}"', found["body"])

        with patch("openstax.urlopen", side_effect=TimeoutError):
            unavailable = request("/study/textbooks/search", query="q=biology")
        self.assertIn("OpenStax search is unavailable.", unavailable["body"])
        self.assertNotIn("No such content available.", unavailable["body"])

    def test_hindi_language_switcher_localizes_guides_and_remembers_choice(self):
        english = request("/disease/asthma")
        self.assertIn('href="/language?lang=hi&amp;next=%2Fdisease%2Fasthma"', english["body"])

        switched = request(
            "/language",
            query="lang=hi&next=%2Fdisease%2Fasthma",
        )
        self.assertTrue(switched["status"].startswith("303"))
        self.assertEqual(switched["headers"]["Location"], "/disease/asthma")
        language_cookie = switched["headers"]["Set-Cookie"]
        self.assertIn(f"{LANGUAGE_COOKIE_NAME}=hi", language_cookie)

        hindi = request("/disease/asthma", cookie=f"{LANGUAGE_COOKIE_NAME}=hi")
        for expected in ('<html lang="hi">', "अस्थमा (दमा)", "सामान्य लक्षण",
                         "साँस में घरघराहट", "रोकथाम और जोखिम में कमी",
                         "चिकित्सकीय सलाह का विकल्प नहीं", "अंग्रेज़ी",
                         "WellNote", "मुख्य नेविगेशन"):
            self.assertIn(expected, hindi["body"])
        self.assertIn("National Heart, Lung, and Blood Institute", hindi["body"])
        hindi_diabetes = request(
            "/disease/type-2-diabetes", cookie=f"{LANGUAGE_COOKIE_NAME}=hi"
        )["body"]
        self.assertIn("Centers for Disease Control and Prevention", hindi_diabetes)
        self.assertNotIn("Centers for Disease Control and रोकथाम", hindi_diabetes)

        hindi_search = request(query="q=टाइप+2+मधुमेह", cookie=f"{LANGUAGE_COOKIE_NAME}=hi")
        self.assertIn("टाइप 2 मधुमेह", hindi_search["body"])

    def test_language_switcher_rejects_unsupported_and_external_redirects(self):
        unsupported = request("/language", query="lang=fr")
        self.assertTrue(unsupported["status"].startswith("400"))

        switched = request(
            "/language",
            query="lang=hi&next=https%3A%2F%2Fexample.com",
        )
        self.assertEqual(switched["headers"]["Location"], "/")
        back_to_english = request(
            "/language",
            query="lang=en&next=%2Fdisease%2Fasthma",
        )
        self.assertIn(f"{LANGUAGE_COOKIE_NAME}=en", back_to_english["headers"]["Set-Cookie"])

    def test_hindi_switch_applies_to_study_tools_and_comparison(self):
        language_cookie = f"{LANGUAGE_COOKIE_NAME}=hi"
        study_home = request("/study", cookie=language_cookie)["body"]
        self.assertIn("अध्ययन कक्ष", study_home)
        self.assertIn("अभ्यास प्रश्न हल करें", study_home)

        mind_map = request(
            "/study/mind-map", query="topic=asthma", cookie=language_cookie
        )["body"]
        self.assertIn("माइंड मैप जनरेटर", mind_map)
        self.assertIn("साँस में घरघराहट", mind_map)

        flashcards = request(
            "/study/flashcards", query="topic=asthma", cookie=language_cookie
        )["body"]
        self.assertIn("स्मार्ट फ्लैशकार्ड", flashcards)
        self.assertIn("अस्थमा (दमा)", flashcards)

        compared = request(
            "/study/compare",
            query="first=asthma&second=type-2-diabetes",
            cookie=language_cookie,
        )["body"]
        self.assertIn("बीमारियों की तुलना", compared)
        self.assertIn("एक दीर्घकालिक स्थिति", compared)
        self.assertIn("टाइप 2 मधुमेह", compared)

    def test_body_verse_has_real_3d_system_models_and_selectable_details(self):
        page = request("/study/body-verse")
        self.assertTrue(page["status"].startswith("200"))
        for expected in (
            "Body Verse",
            "Explore the human body",
            'class="body-verse-side-panel"',
            "Drag to rotate · Scroll to zoom",
            "What it does",
            'data-detail-fact',
            'href="/static/body-verse.css"',
            'type="importmap"',
            'type="module" src="/static/body-verse.js?v=20261124-original-sketchfab-ui"',
            "OrbitControls",
            "FBXLoader",
            "Raycaster",
            "Z-Anatomy",
            "BodyParts3D",
            "CC BY-SA 4.0",
            "0caae8f894cc40b69f3f78adf14b9665",
            "fe69d7b1ed6f46a3bd0b6933b796092e",
        ):
            if expected in (
                "OrbitControls", "FBXLoader", "Raycaster",
                "whole-body.avif", "organs.jpg",
                "nervous-system.jpg", "lymphatic-system.jpg",
            ):
                self.assertIn(expected, request("/static/body-verse.js")["body"])
            else:
                self.assertIn(expected, page["body"])
        self.assertIn('href="/study/body-verse"', request("/study")["body"])
        rendered_systems = re.findall(
            r'<button[^>]+data-system-card="([^"]+)"',
            page["body"],
        )
        self.assertEqual(rendered_systems, list(body_verse.SYSTEMS))
        for system in body_verse.SYSTEMS.values():
            with self.subTest(system=system["model"]):
                self.assertIn(system["model"], page["body"])
        self.assertNotIn("<svg", page["body"])
        self.assertNotIn("body-zoom-tools", page["body"])
        self.assertNotIn('data-camera=', page["body"])
        self.assertNotIn("Reset view", page["body"])

        script = request("/static/body-verse.js")
        self.assertTrue(script["status"].startswith("200"))
        self.assertIn("pointerup", script["body"])
        self.assertIn("loader.load", script["body"])
        self.assertIn('imageViewport.addEventListener("wheel"', script["body"])
        self.assertNotIn("data-camera", script["body"])
        self.assertIn("data-structure-search", page["body"])
        self.assertIn("data-detail-function", page["body"])
        self.assertTrue(request("/static/body-verse.css")["status"].startswith("200"))

    def test_body_verse_localizes_layer_details_in_hindi_and_hinglish(self):
        cases = (
            ("hi", "मानव शरीर को जानें", "महाधमनी", "फुफ्फुसीय शिराएँ",
             "हृदय एक मांसपेशीय पंप है"),
            ("hinglish", "Insaani body ko explore karein", "Aorta",
             "Pulmonary veins", "Heart ek muscular pump hai"),
        )
        for language, title, artery, vein, heart_function in cases:
            with self.subTest(language=language):
                page = request(
                    "/study/body-verse",
                    cookie=f"{LANGUAGE_COOKIE_NAME}={language}",
                )["body"]
                self.assertIn(title, page)
                self.assertIn(artery, page)
                self.assertIn(vein, page)
                self.assertIn(heart_function, page)

    def test_hindi_and_hinglish_localize_quiz_and_flashcards(self):
        cases = (
            ("hi", "वायवीय श्वसन के दौरान ATP उत्पादन", "माइटोकॉन्ड्रियन",
             "कार्ड 1 / 7", "एक दीर्घकालिक स्थिति"),
            ("hinglish", "Aerobic respiration ke dauraan ATP", "Mitochondrion",
             "Card 1 / 7", "Ek lambe samay tak rehne wali condition"),
        )
        for language, question_text, option_text, progress, summary in cases:
            with self.subTest(language=language):
                cookie = f"{LANGUAGE_COOKIE_NAME}={language}"
                quiz = request("/study/question", cookie=cookie)["body"]
                self.assertIn(question_text, quiz)
                self.assertIn(option_text, quiz)
                self.assertNotIn(
                    "Which organelle is the main site of ATP production",
                    quiz,
                )
                self.assertIn("WellNote", quiz)

                flashcards = request(
                    "/study/flashcards",
                    query="topic=asthma",
                    cookie=cookie,
                )["body"]
                self.assertIn(progress, flashcards)
                self.assertIn(summary, flashcards)
                self.assertNotIn(
                    "A long-term condition that can make the airways inflamed",
                    flashcards,
                )

    def test_every_practice_question_has_hindi_and_hinglish_copy(self):
        for language in ("hi", "hinglish"):
            for question in QUESTIONS:
                localized = translations.localize_question(question, language)
                with self.subTest(language=language, question=question["id"]):
                    self.assertNotEqual(localized["question"], question["question"])
                    self.assertEqual(len(localized["options"]), len(question["options"]))
                    self.assertNotEqual(localized["explanation"], question["explanation"])

    def test_external_reference_chrome_and_study_prompts_follow_selected_language(self):
        language_cookie = f"{LANGUAGE_COOKIE_NAME}=hi"
        source = [{
            "title": "Zika virus",
            "summary": "Zika is a virus spread by mosquitoes.",
            "url": "https://medlineplus.gov/zika.html",
        }]
        with patch("app.search_medlineplus", return_value=(source, None)):
            search = request(query="q=zika", cookie=language_cookie)["body"]
        self.assertIn("विश्वसनीय स्वास्थ्य संदर्भ", search)
        self.assertIn("“zika” के लिए जानकारी", search)
        self.assertIn("Zika is a virus spread by mosquitoes.", search)
        self.assertIn("मूल भाषा में दिख सकते हैं", search)
        self.assertIn("WellNote", search)

        with patch("app.search_medlineplus", return_value=([], None)):
            mind_map = request(
                "/study/mind-map",
                query="topic=dyslexia",
                cookie=language_cookie,
            )["body"]
        self.assertIn("dyslexia के लक्षणों की जानकारी नहीं थी", mind_map)
        self.assertIn("विश्वसनीय स्रोत क्या कहता है", mind_map)
        self.assertNotIn("Symptom details for dyslexia", mind_map)

    def test_save_and_remove_topic_work_from_hindi_interface(self):
        language_cookie = f"{LANGUAGE_COOKIE_NAME}=hi"
        detail = request(
            "/disease/type-2-diabetes", cookie=language_cookie
        )["body"]
        self.assertIn("＋ बाद के लिए सहेजें", detail)

        saved = request(
            "/saved/add/type-2-diabetes",
            method="POST",
            cookie=language_cookie,
        )
        self.assertTrue(saved["status"].startswith("303"))
        self.assertEqual(saved["headers"]["Location"], "/saved")
        self.assertIn(f"{COOKIE_NAME}=type-2-diabetes", saved["headers"]["Set-Cookie"])

        saved_page = request(
            "/saved",
            cookie=f"{language_cookie}; {COOKIE_NAME}=type-2-diabetes",
        )["body"]
        self.assertIn("टाइप 2 मधुमेह", saved_page)
        self.assertIn("सहेजे गए विषय", saved_page)

        removed = request(
            "/saved/remove/type-2-diabetes",
            method="POST",
            cookie=f"{language_cookie}; {COOKIE_NAME}=type-2-diabetes",
        )
        self.assertTrue(removed["status"].startswith("303"))
        self.assertIn(f"{COOKIE_NAME}=", removed["headers"]["Set-Cookie"])

    def test_topic_card_plus_adds_to_reading_list_in_hindi_and_hinglish(self):
        for language, translated_name in (
            ("en", "Asthma"),
            ("hi", "अस्थमा (दमा)"),
            ("hinglish", "Asthma (Dama)"),
        ):
            language_cookie = f"{LANGUAGE_COOKIE_NAME}={language}"
            home = request("/", cookie=language_cookie)["body"]
            self.assertIn(f'action="/saved/add/asthma" method="post"', home)
            self.assertIn("Save to library" if language == "en" else (
                "लाइब्रेरी में सहेजें" if language == "hi" else "Library mein save karein"
            ), home)

            added = request(
                "/saved/add/asthma",
                method="POST",
                cookie=language_cookie,
            )
            self.assertTrue(added["status"].startswith("303"))
            self.assertEqual(added["headers"]["Location"], "/saved")
            saved_page = request(
                "/saved",
                cookie=f"{language_cookie}; {COOKIE_NAME}=asthma",
            )["body"]
            self.assertIn(translated_name, saved_page)
            self.assertIn("♥", saved_page)

    def test_hinglish_switcher_uses_roman_script_and_finds_local_guides(self):
        switched = request(
            "/language",
            query="lang=hinglish&next=%2Fdisease%2Fasthma",
        )
        self.assertIn(f"{LANGUAGE_COOKIE_NAME}=hinglish", switched["headers"]["Set-Cookie"])

        page = request(
            "/disease/asthma",
            cookie=f"{LANGUAGE_COOKIE_NAME}=hinglish",
        )["body"]
        self.assertIn('<html lang="hi-Latn">', page)
        self.assertIn("Asthma (Dama)", page)
        self.assertIn("Baad ke liye save karein", page)
        self.assertIn("Saans mein ghargharahat", page)
        self.assertNotIn("साँस में घरघराहट", page)

        local_topic = request(
            "/study/flashcards",
            query="topic=Asthma+%28Dama%29&card=1",
            cookie=f"{LANGUAGE_COOKIE_NAME}=hinglish",
        )
        self.assertIn("Saans mein ghargharahat", local_topic["body"])

    def test_unknown_disease_search_and_detail_link_to_medlineplus(self):
        medlineplus_result = [{
            "title": "Malaria",
            "summary": "Malaria is a disease caused by parasites.",
            "url": "https://medlineplus.gov/malaria.html",
        }]
        with patch("app.search_medlineplus", return_value=(medlineplus_result, None)):
            result = request(query="q=malaria")
        self.assertTrue(result["status"].startswith("200"))
        self.assertIn("Information for “malaria”", result["body"])
        self.assertIn("Malaria is a disease caused by parasites.", result["body"])
        self.assertIn("https://medlineplus.gov/malaria.html", result["body"])
        video = {
            "video_id": "Qwerty12345",
            "title": "Malaria animation",
            "channel": "Health Learning",
        }
        with patch("app.search_medlineplus", return_value=(medlineplus_result, None)), \
                patch("app.search_youtube_video", return_value=(video, None)):
            detail = request("/disease/malaria")
        self.assertTrue(detail["status"].startswith("200"))
        self.assertIn("This condition is not in WellNote", detail["body"])
        self.assertNotIn("Common symptoms", detail["body"])
        self.assertIn("youtube-nocookie.com/embed/Qwerty12345", detail["body"])
        self.assertIn("Malaria animation", detail["body"])
        self.assertIn("external-topic-layout", detail["body"])

    def test_external_disease_detail_shows_youtube_fallback_when_lookup_fails(self):
        with patch("app.search_medlineplus", return_value=([], None)), \
                patch("app.search_youtube_video", return_value=(None, "YouTube could not be reached right now.")):
            detail = request("/disease/rare-condition")
        self.assertIn("Video preview unavailable", detail["body"])
        self.assertIn("YouTube could not be reached just now.", detail["body"])
        self.assertIn(
            "youtube.com/results?search_query=rare+condition+animated+medical+explanation",
            detail["body"],
        )

    def test_external_disease_search_can_be_saved_and_removed_from_reading_list(self):
        malaria = {
            "title": "Malaria",
            "summary": "Malaria is caused by parasites.",
            "url": "https://medlineplus.gov/malaria.html",
        }
        with patch("app.search_medlineplus", return_value=([malaria], None)):
            search = request(query="q=malaria", cookie=f"{LANGUAGE_COOKIE_NAME}=hi")
        self.assertIn('action="/saved/add-topic" method="post"', search["body"])
        self.assertIn('name="topic" value="Malaria"', search["body"])
        header_position = search["body"].index('class="reference-intro-header"')
        save_control_position = search["body"].index('action="/saved/add-topic"', header_position)
        self.assertLess(
            save_control_position,
            search["body"].index("Malaria is caused by parasites."),
        )

        added = request(
            "/saved/add-topic",
            method="POST",
            cookie=f"{LANGUAGE_COOKIE_NAME}=hi",
            form="topic=Malaria",
        )
        self.assertTrue(added["status"].startswith("303"))
        self.assertEqual(added["headers"]["Location"], "/saved")
        token = wellnote_app.external_saved_token("Malaria")
        with patch("app.search_medlineplus", return_value=([malaria], None)):
            already_saved = request(
                query="q=malaria",
                cookie=f"{LANGUAGE_COOKIE_NAME}=hi; {COOKIE_NAME}={token}",
            )
        intro = already_saved["body"].index('class="reference-intro-header"')
        remove_position = already_saved["body"].index('action="/saved/remove-topic"', intro)
        self.assertLess(remove_position, already_saved["body"].index("Malaria is caused by parasites."))
        saved_page = request(
            "/saved",
            cookie=f"{LANGUAGE_COOKIE_NAME}=hi; {COOKIE_NAME}={token}",
        )["body"]
        self.assertIn("Malaria", saved_page)
        self.assertIn("सहेजा गया स्वास्थ्य विषय", saved_page)
        self.assertIn('/saved/remove-topic', saved_page)

        removed = request(
            "/saved/remove-topic",
            method="POST",
            cookie=f"{LANGUAGE_COOKIE_NAME}=hi; {COOKIE_NAME}={token}",
            form="topic=Malaria",
        )
        self.assertTrue(removed["status"].startswith("303"))
        empty_page = request(
            "/saved",
            cookie=f"{LANGUAGE_COOKIE_NAME}=hi; {COOKIE_NAME}=",
        )["body"]
        self.assertIn("आपकी लाइब्रेरी तैयार है", empty_page)

    def test_external_mind_map_and_flashcard_topics_can_be_saved(self):
        article = {
            "title": "Dyslexia",
            "summary": "Dyslexia can affect reading and writing.",
            "url": "https://medlineplus.gov/learningdisabilities.html",
        }
        with patch("app.search_medlineplus", return_value=([article], None)):
            mind_map = request("/study/mind-map", query="topic=dyslexia")
            flashcards = request("/study/flashcards", query="topic=dyslexia")
        for result in (mind_map, flashcards):
            self.assertIn('action="/saved/add-topic" method="post"', result["body"])
            self.assertIn('name="topic" value="Dyslexia"', result["body"])

    def test_medlineplus_parser_strips_markup_and_rejects_untrusted_links(self):
        payload = b"""<?xml version="1.0"?>
        <nlmSearchResult><list><document url="https://medlineplus.gov/malaria.html">
        <content name="title">&lt;span&gt;Malaria&lt;/span&gt;</content>
        <content name="FullSummary">&lt;p&gt;Malaria is caused by parasites.&lt;/p&gt;</content>
        </document><document url="https://example.com/fake">
        <content name="title">Fake source</content><content name="snippet">Do not trust</content>
        </document></list></nlmSearchResult>"""

        class FakeResponse:
            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return None

            def read(self, _limit):
                return payload

        with patch("medlineplus.urlopen", return_value=FakeResponse()):
            results, error = search_medlineplus("malaria & fever")
        self.assertIsNone(error)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["title"], "Malaria")
        self.assertEqual(results[0]["summary"], "Malaria is caused by parasites.")
        self.assertEqual(results[0]["url"], "https://medlineplus.gov/malaria.html")

    def test_disease_detail_has_safety_and_source(self):
        body = request("/disease/asthma")["body"]
        for expected in ("Common symptoms", "Prevention &amp; risk reduction",
                         "does not currently have a cure", "nhlbi.nih.gov",
                         "not a substitute for a clinician",
                         "youtube-nocookie.com/embed/PzfLDi-sL3w",
                         "origin=http%3A%2F%2Flocalhost%3A8000",
                         'referrerpolicy="origin"',
                         "How does asthma work?",
                         "TED-Ed"):
            self.assertIn(expected, body)

    def test_disease_video_uses_forwarded_railway_origin(self):
        body = request(
            "/disease/asthma",
            host="a-web-browser-production.up.railway.app",
            forwarded_proto="https",
        )["body"]
        self.assertIn(
            "origin=https%3A%2F%2Fa-web-browser-production.up.railway.app",
            body,
        )

    def test_video_origin_rejects_malformed_host(self):
        body = request(
            "/disease/asthma",
            host='example.com" onclick="alert(1)',
            forwarded_proto="https",
        )["body"]
        self.assertIn("origin=https%3A%2F%2Flocalhost%3A8000", body)
        self.assertNotIn('example.com&quot;', body)

    def test_disease_video_previews_match_each_curated_topic(self):
        cases = (
            ("/disease/type-2-diabetes", "JAjZv41iUJU", "Common symptoms"),
            ("/disease/seasonal-influenza", "oXzwtGFyBik", "Prevention &amp; risk reduction"),
        )
        for path, video_id, existing_detail in cases:
            with self.subTest(path=path):
                body = request(path)["body"]
                self.assertIn(f"youtube-nocookie.com/embed/{video_id}", body)
                self.assertIn(existing_detail, body)
                self.assertIn("Supplementary educational content", body)

    def test_study_greeting_tutor_and_exam_information(self):
        self.assertIn("MCAT", request("/study")["body"])
        study_home = request("/study")["body"]
        self.assertNotIn("limited, introductory guidance", study_home)
        self.assertNotIn("maxlength=", study_home)
        self.assertNotIn("unrestricted AI", study_home)
        self.assertIn("No AI model is configured", study_home)
        self.assertIn("THREE THINGS TO REMEMBER", request("/study/asthma")["body"])
        result = request("/study/ask", method="POST", form="prompt=Help+me+with+NEET")
        self.assertIn(EXAM_GUIDES["neet"], result["body"])
        self.assertIn("Your study buddy", result["body"])
        self.assertTrue(make_response("AAMC") == EXAM_GUIDES["aamc"])

    def test_voice_tutor_speaks_typed_prompt_answers(self):
        study_home = request("/study")["body"]
        self.assertIn("Read answer aloud", study_home)
        self.assertIn("Stop audio", study_home)
        self.assertIn("Select Read answer aloud", study_home)
        self.assertNotIn("Ask by voice", study_home)
        self.assertIn('/static/voice-tutor.js', study_home)

        script = request("/static/voice-tutor.js")
        self.assertTrue(script["status"].startswith("200"))
        self.assertIn("SpeechSynthesisUtterance", script["body"])
        self.assertIn('"hi-Latn": ["hi-IN", "hi", "en-IN"]', script["body"])
        self.assertIn("utterance.voice = voice", script["body"])
        self.assertIn("matchingVoice(await availableVoices())", script["body"])
        self.assertIn('fetch("/study/speak"', script["body"])
        self.assertIn("if (!browserSpeechAvailable)", script["body"])
        self.assertIn("voiceGeminiEnabled", script["body"])
        self.assertIn('samjhayein: "समझाएँ"', script["body"])
        self.assertNotIn("SpeechRecognition", script["body"])

        result = request(
            "/study/ask", method="POST",
            form="prompt=What+is+the+powerhouse+of+the+cell%3F",
        )
        self.assertIn("mitochondrion", result["body"].casefold())
        self.assertIn("step by step", make_response("Help me with homework"))
        self.assertIn("personal symptoms", make_response("I have a symptom"))

    def test_voice_status_explains_when_a_matching_localized_voice_is_missing(self):
        for language, phrase in (
            ("hi", "इस डिवाइस में"),
            ("hinglish", "Is device par"),
        ):
            body = request(
                "/study",
                cookie=f"{LANGUAGE_COOKIE_NAME}={language}",
            )["body"]
            with self.subTest(language=language):
                self.assertIn("data-voice-missing=", body)
                self.assertIn(phrase, body)
                self.assertIn("data-voice-hindi-name=", body)

    def test_mind_map_picker_and_reviewed_topic_map(self):
        picker = request("/study/mind-map")
        self.assertIn("Enter any disease or health topic", picker["body"])
        self.assertIn("Generate map", picker["body"])
        self.assertIn("asthma", picker["body"])
        self.assertNotIn("<select", picker["body"])

        generated = request("/study/mind-map", query="topic=asthma")
        for expected in (
            "Mind map for Asthma", "Common symptoms",
            "Prevention &amp; risk reduction", "Treatment &amp; care",
            "Study takeaways", "National Heart, Lung, and Blood Institute",
        ):
            self.assertIn(expected, generated["body"])
        self.assertIn("Make a mind map", request("/study/asthma")["body"])

    def test_mind_map_uses_external_reference_for_unlisted_disease(self):
        source = {
            "title": "Malaria",
            "summary": (
                "Malaria is a disease caused by parasites. "
                "Symptoms include fever and chills. Malaria can be prevented. "
                "Treatment includes antimalarial medicines."
            ),
            "url": "https://medlineplus.gov/malaria.html",
        }
        with patch("app.search_medlineplus", return_value=([source], None)) as lookup:
            generated = request("/study/mind-map", query="topic=malaria")
        lookup.assert_called_once_with("malaria")
        for expected in (
            "Mind map for malaria", "Malaria is a disease caused by parasites.",
            "Symptoms", "Symptoms include fever and chills.",
            "Prevention", "Malaria can be prevented.",
            "Treatment &amp; care", "Treatment includes antimalarial medicines.",
            "Study questions", "Open the full article for details ↗",
            "https://medlineplus.gov/malaria.html",
        ):
            self.assertIn(expected, generated["body"])
        self.assertEqual(generated["body"].count('class="mind-map-detail-link"'), 5)

    def test_mind_map_keeps_unavailable_branches_with_source_links(self):
        source = {
            "title": "Learning Disabilities",
            "summary": (
                "Learning disabilities are conditions that affect the ability to learn. "
                "They can cause problems with reading and writing."
            ),
            "url": "https://medlineplus.gov/learningdisabilities.html",
        }
        with patch("app.search_medlineplus", return_value=([source], None)):
            generated = request("/study/mind-map", query="topic=dyslexia")
        self.assertIn('<h2>dyslexia</h2>', generated["body"])
        self.assertIn("Learning disabilities are conditions that affect", generated["body"])
        self.assertIn("Overview", generated["body"])
        self.assertIn("Symptoms</h3>", generated["body"])
        self.assertIn("Symptom details for dyslexia were not included", generated["body"])
        self.assertIn("Prevention</h3>", generated["body"])
        self.assertIn("Treatment &amp; care</h3>", generated["body"])
        symptoms_card = generated["body"].split('<section class="mind-map-branch"><h3>Symptoms</h3>', 1)[1]
        self.assertIn("Open the full article for details ↗", symptoms_card.split("</section>", 1)[0])

    def test_mind_map_still_renders_research_outline_without_reference(self):
        with patch("app.search_medlineplus", return_value=([], None)) as lookup:
            generated = request("/study/mind-map", query="topic=rare+condition")
        lookup.assert_called_once_with("rare condition")
        self.assertTrue(generated["status"].startswith("200"))
        self.assertIn("Mind map for rare condition", generated["body"])
        self.assertIn("No MedlinePlus article was found", generated["body"])
        self.assertIn("Symptoms</h3>", generated["body"])
        self.assertIn("Search MedlinePlus for details", generated["body"])
        self.assertEqual(generated["body"].count('class="mind-map-detail-link"'), 5)

    def test_smart_flashcards_reveal_and_navigate_local_deck(self):
        picker = request("/study/flashcards")
        self.assertIn("Choose any disease or health topic", picker["body"])
        self.assertIn("Build deck", picker["body"])

        first = request("/study/flashcards", query="topic=asthma")
        self.assertIn("CARD 1 OF 7", first["body"])
        self.assertIn("What is Asthma?", first["body"])
        self.assertIn("<details class=\"flashcard-reveal\">", first["body"])
        self.assertIn("<summary>Reveal answer</summary>", first["body"])
        self.assertIn("https://www.nhlbi.nih.gov/health/asthma", first["body"])
        self.assertIn("topic=asthma&amp;card=1", first["body"])
        self.assertIn("Study with flashcards", request("/study/asthma")["body"])

        second = request("/study/flashcards", query="topic=asthma&card=1")
        self.assertIn("What are common symptoms of Asthma?", second["body"])
        self.assertIn("CARD 2 OF 7", second["body"])
        self.assertIn("topic=asthma&amp;card=0", second["body"])
        last = request("/study/flashcards", query="topic=asthma&card=6")
        self.assertIn("topic=asthma&amp;card=0", last["body"])
        invalid = request("/study/flashcards", query="topic=asthma&card=bogus")
        self.assertIn("CARD 1 OF 7", invalid["body"])

    def test_external_flashcards_are_sourced_and_empty_search_is_clear(self):
        source = {
            "title": "Malaria",
            "summary": (
                "Malaria is a disease caused by parasites. "
                "Symptoms include fever and chills. Malaria can be prevented. "
                "Treatment includes antimalarial medicines."
            ),
            "url": "https://medlineplus.gov/malaria.html",
        }
        with patch("app.search_medlineplus", return_value=([source], None)) as lookup:
            deck = request("/study/flashcards", query="topic=malaria")
        lookup.assert_called_once_with("malaria")
        self.assertIn("What does the MedlinePlus article say about overview for malaria?", deck["body"])
        self.assertIn("Symptoms include fever and chills.", deck["body"])
        self.assertIn("Read the MedlinePlus article", deck["body"])

        with patch("app.search_medlineplus", return_value=([], None)):
            unavailable = request("/study/flashcards", query="topic=unknown")
        self.assertIn("No reviewed flashcards available", unavailable["body"])
        self.assertIn("No factual flashcards were generated.", unavailable["body"])
        self.assertNotIn("<details class=\"flashcard-reveal\">", unavailable["body"])

    def test_disease_comparison_form_and_local_topics(self):
        picker = request("/study/compare")
        self.assertIn("First health topic", picker["body"])
        self.assertIn("Second health topic", picker["body"])

        with patch("app.search_medlineplus") as lookup:
            compared = request(
                "/study/compare",
                query="first=asthma&second=type-2-diabetes",
            )
        lookup.assert_not_called()
        for expected in (
            "Disease comparison", "Asthma", "Type 2 diabetes",
            "Symptoms", "Prevention", "Treatment &amp; care",
            "Wheezing", "blood glucose", "National Heart, Lung, and Blood Institute",
        ):
            self.assertIn(expected, compared["body"])
        self.assertIn("Compare with another topic", request("/study/asthma")["body"])

        duplicate = request("/study/compare", query="first=asthma&second=ASTHMA")
        self.assertIn("Enter two different diseases or health topics", duplicate["body"])

    def test_disease_comparison_uses_external_sources_and_marks_missing_details(self):
        malaria = {
            "title": "Malaria",
            "summary": (
                "Malaria is caused by parasites. Symptoms include fever and chills. "
                "It can be prevented. Treatment includes antimalarial medicines."
            ),
            "url": "https://medlineplus.gov/malaria.html",
        }
        dyslexia = {
            "title": "Learning Disabilities",
            "summary": "Learning disabilities can cause problems with reading and writing.",
            "url": "https://medlineplus.gov/learningdisabilities.html",
        }
        with patch("app.search_medlineplus", side_effect=[([malaria], None), ([dyslexia], None)]) as lookup:
            compared = request(
                "/study/compare",
                query="first=malaria&second=dyslexia",
            )
        self.assertEqual(lookup.call_count, 2)
        self.assertIn("Symptoms include fever and chills.", compared["body"])
        self.assertIn("Symptom details for dyslexia were not included in this search summary.", compared["body"])
        self.assertIn("https://medlineplus.gov/malaria.html", compared["body"])
        self.assertIn("https://medlineplus.gov/learningdisabilities.html", compared["body"])

        with patch("app.search_medlineplus", return_value=([], None)):
            unavailable = request("/study/compare", query="first=unknown&second=rare")
        self.assertIn("No reviewed MedlinePlus details were found for unknown.", unavailable["body"])
        self.assertIn("Search MedlinePlus ↗", unavailable["body"])

    def test_study_intent_answers_medical_symptom_question_educationally(self):
        source = {
            "title": "Malaria",
            "summary": "Malaria symptoms can include fever and chills.",
            "url": "https://medlineplus.gov/malaria.html",
        }
        with patch("study.search_medlineplus", return_value=([source], None)) as lookup:
            result = request(
                "/study/ask",
                method="POST",
                form="prompt=Explain+malaria+symptoms+for+a+biology+exam",
            )
        lookup.assert_called_once_with("malaria")
        self.assertIn("MedlinePlus reference, Malaria", result["body"])
        self.assertIn("You asked", result["body"])
        self.assertIn("Explain malaria symptoms for a biology exam", result["body"])
        self.assertIn("Malaria symptoms can include fever and chills.", result["body"])
        self.assertNotIn("I can’t assess personal symptoms", result["body"])
        self.assertIn("Read the MedlinePlus article", result["body"])
        self.assertLess(
            result["body"].index("Malaria symptoms can include fever and chills."),
            result["body"].index('<textarea id="study-prompt"'),
        )

    def test_study_prompt_categories_and_repeated_unlimited_posts(self):
        first = request(
            "/study/ask", method="POST",
            form="prompt=Tell+me+some+funny+jokes",
        )
        self.assertIn("brought the ATP", first["body"])
        business = request(
            "/study/ask", method="POST",
            form="prompt=How+do+I+start+a+healthcare+business",
        )
        self.assertIn("regulations, licensing, privacy", business["body"])
        hospital = request(
            "/study/ask", method="POST",
            form="prompt=Find+a+hospital+near+Boston",
        )
        self.assertIn("maps/search", hospital["body"])
        self.assertIn("Boston", hospital["body"])

        long_prompt = "biology " * 250
        captured = []
        with patch(
            "app.study.make_response",
            side_effect=lambda text, language="en": captured.append(text) or "Let’s study biology.",
        ):
            result = request(
                "/study/ask",
                method="POST",
                form="prompt=" + quote_plus(long_prompt),
            )
        self.assertEqual(captured, [long_prompt])
        self.assertIn("Let’s study biology.", result["body"])

    def test_powerhouse_cell_question_and_variants(self):
        prompts = [
            "Help me with this question What is the power house of a cell organelle??",
            "What is the powerhouse of the cell?",
            "Which organelle is called the powerhouse of a cell?",
            "Tell me about mitochondria and why they are the cell's powerhouse.",
        ]
        for prompt in prompts:
            with self.subTest(prompt=prompt):
                answer = make_response(prompt)
                self.assertIn("mitochondrion", answer.casefold())
                self.assertIn("mitochondria", answer.casefold())
                self.assertIn("ATP", answer)
                self.assertIn("cellular respiration", answer)
                self.assertNotIn("couldn’t find", answer)

        with patch("app.study.search_medlineplus") as search:
            result = request(
                "/study/ask",
                method="POST",
                form="prompt=" + quote_plus(prompts[0]),
            )
        self.assertIn("mitochondrion", result["body"].casefold())
        self.assertIn("powerhouse of the cell", result["body"])
        self.assertIn("You asked", result["body"])
        search.assert_not_called()

    def test_all_vitamins_question_returns_thirteen_vitamin_overview(self):
        prompt = "What are the vitamin deficiency diseases for all the vitamins and their sources of all vitamins"
        with patch("study.search_medlineplus") as medlineplus:
            answer = make_response(prompt)
        vitamin_names = (
            "A (retinol", "B1 (thiamin", "B2 (riboflavin", "B3 (niacin",
            "B5 (pantothenic", "B6 (pyridoxine", "B7 (biotin", "B9 (folate",
            "B12 (cobalamin", "C (ascorbic", "D (calciferol",
            "E (tocopherol", "K (phylloquinone",
        )
        for vitamin in vitamin_names:
            with self.subTest(vitamin=vitamin):
                self.assertIn(vitamin, answer)
        for condition in ("scurvy", "rickets", "beriberi", "pellagra", "megaloblastic anemia"):
            self.assertIn(condition, answer.casefold())
        for source in ("citrus", "fortified grains", "leafy greens", "fatty fish"):
            self.assertIn(source, answer.casefold())
        self.assertIn("Do not start high-dose supplements", answer)
        self.assertIn("NIH Office of Dietary Supplements", answer)
        medlineplus.assert_not_called()

        with patch("app.study.search_medlineplus") as medlineplus:
            rendered = request(
                "/study/ask", method="POST",
                form="prompt=" + quote_plus(prompt),
            )
        self.assertTrue(rendered["status"].startswith("200"))
        self.assertIn("<th>Vitamin</th>", rendered["body"])
        self.assertIn("<td>A (retinol/carotenoids)</td>", rendered["body"])
        self.assertIn("<td>B12 (cobalamin)</td>", rendered["body"])
        self.assertIn("<td>K (phylloquinone/menaquinones)</td>", rendered["body"])
        self.assertIn("<table", rendered["body"])
        self.assertIn("Pellagra", rendered["body"])
        self.assertIn("https://ods.od.nih.gov/factsheets/list-all/", rendered["body"])
        self.assertNotIn("MedlinePlus reference, Vitamin D", rendered["body"])
        medlineplus.assert_not_called()

    def test_single_vitamin_question_still_uses_targeted_reference(self):
        vitamin_d = [{
            "title": "Vitamin D",
            "summary": "Vitamin D helps the body absorb calcium.",
            "url": "https://medlineplus.gov/vitamind.html",
        }]
        with patch("study.search_medlineplus", return_value=(vitamin_d, None)) as medlineplus:
            answer = make_response("What are vitamin D sources?")
        medlineplus.assert_called_once_with("vitamin D sources")
        self.assertIn("Vitamin D", answer)
        self.assertNotIn("Vitamin A", answer)

    def test_ai_provider_sends_general_prompt_and_safety_instructions(self):
        response_body = json.dumps({
            "choices": [{"message": {"content": "Here is a friendly joke about cells."}}]
        }).encode()

        class FakeResponse:
            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return None

            def read(self, _limit):
                return response_body

        captured = {}

        def fake_urlopen(request, timeout):
            captured["url"] = request.full_url
            captured["headers"] = request.headers
            captured["payload"] = json.loads(request.data.decode())
            captured["timeout"] = timeout
            return FakeResponse()

        config = {
            "WELLNOTE_AI_API_KEY": "test-key-not-a-real-secret",
            "WELLNOTE_AI_MODEL": "test-model",
            "WELLNOTE_AI_BASE_URL": "https://example.test/v1",
        }
        with patch.dict(os.environ, config, clear=True):
            self.assertTrue(ai_provider_configured())
            with patch("study.urlopen", side_effect=fake_urlopen):
                result = request(
                    "/study/ask", method="POST",
                    form="prompt=" + quote_plus("Tell me a funny joke"),
                )
        self.assertIn("Here is a friendly joke about cells.", result["body"])
        self.assertIn("Tell me a funny joke", result["body"])
        self.assertEqual(captured["url"], "https://example.test/v1/chat/completions")
        self.assertEqual(captured["payload"]["model"], "test-model")
        self.assertEqual(captured["payload"]["messages"][1]["content"], "Tell me a funny joke")
        self.assertIn("never diagnose", captured["payload"]["messages"][0]["content"])
        self.assertEqual(captured["headers"]["Authorization"], "Bearer test-key-not-a-real-secret")

        hindi_payload = {}

        def capture_hindi_request(request, timeout):
            hindi_payload["messages"] = json.loads(request.data.decode())["messages"]
            return FakeResponse()

        with patch.dict(os.environ, config, clear=True):
            with patch("study.urlopen", side_effect=capture_hindi_request):
                generate_ai_response("Explain a biology topic", "hi")
        self.assertIn(
            "Hindi written in Devanagari",
            hindi_payload["messages"][0]["content"],
        )

    def test_gemini_api_key_configures_native_gemini_chat_endpoint(self):
        response_body = json.dumps({
            "choices": [{"message": {"content": "Gemini study answer"}}]
        }).encode()

        class FakeResponse:
            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return None

            def read(self, _limit):
                return response_body

        captured = {}

        def fake_urlopen(request, timeout):
            captured["url"] = request.full_url
            captured["headers"] = request.headers
            captured["payload"] = json.loads(request.data.decode())
            return FakeResponse()

        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-gemini-key"}, clear=True):
            self.assertTrue(ai_provider_configured())
            with patch("study.urlopen", side_effect=fake_urlopen):
                answer = generate_ai_response("Explain photosynthesis")

        self.assertEqual(answer, "Gemini study answer")
        self.assertEqual(
            captured["url"],
            "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
        )
        self.assertEqual(captured["payload"]["model"], "gemini-3.5-flash-lite")
        self.assertEqual(
            captured["headers"]["Authorization"],
            "Bearer test-gemini-key",
        )

    def test_gemini_speech_returns_wav_and_uses_the_requested_language_style(self):
        response_body = json.dumps({
            "output_audio": {"data": base64.b64encode(b"RIFF-test-audio").decode()},
        }).encode()

        class FakeResponse:
            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return None

            def read(self, _limit):
                return response_body

        captured = {}

        def fake_urlopen(request, timeout):
            captured["url"] = request.full_url
            captured["headers"] = request.headers
            captured["payload"] = json.loads(request.data.decode())
            return FakeResponse()

        with patch.dict(
            os.environ,
            {"GEMINI_API_KEY": "test-gemini-key"},
            clear=True,
        ):
            with patch("study.urlopen", side_effect=fake_urlopen):
                audio = wellnote_app.study.generate_gemini_speech(
                    "नमस्ते, जवाब सुनें।",
                    "hi",
                )

        self.assertEqual(audio, b"RIFF-test-audio")
        self.assertEqual(
            captured["url"],
            "https://generativelanguage.googleapis.com/v1beta/interactions",
        )
        self.assertEqual(captured["headers"]["X-goog-api-key"], "test-gemini-key")
        self.assertEqual(captured["payload"]["model"], "gemini-3.8-flash-tts")
        self.assertIn(
            "Hindi (India) accent",
            captured["payload"]["input"][0]["content"][0]["annotations"][0]["style"],
        )

    def test_gemini_speech_endpoint_returns_audio_and_validates_requests(self):
        with patch(
            "app.study.generate_gemini_speech",
            return_value=b"RIFF-test-audio",
        ) as generate:
            response = request(
                "/study/speak",
                method="POST",
                form=json.dumps({"text": "namaste", "language": "hinglish"}),
            )
        self.assertTrue(response["status"].startswith("200"))
        self.assertEqual(response["headers"]["Content-Type"], "audio/wav")
        self.assertEqual(response["body"], "RIFF-test-audio")
        generate.assert_called_once_with("namaste", "hinglish")

        too_long = request(
            "/study/speak",
            method="POST",
            form=json.dumps({"text": "x" * 5001, "language": "hi"}),
        )
        self.assertTrue(too_long["status"].startswith("400"))

    def test_gemini_speech_endpoint_requires_a_gemini_api_key(self):
        with patch.dict(os.environ, {}, clear=True):
            response = request(
                "/study/speak",
                method="POST",
                form=json.dumps({"text": "namaste", "language": "hi"}),
            )
        self.assertTrue(response["status"].startswith("503"))
        self.assertIn("Gemini speech is not configured", response["body"])

    def test_gemini_key_enables_transparently_disclosed_speech_fallback(self):
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}, clear=True):
            page = request(
                "/study",
                cookie=f"{LANGUAGE_COOKIE_NAME}=hi",
            )["body"]
        self.assertIn('data-voice-gemini-enabled="true"', page)
        self.assertIn("जवाब का पाठ ऑडियो बनाने के लिए Google Gemini को भेजा जाएगा", page)
        self.assertNotIn("इस ऐप में AI मॉडल सेट नहीं है", page)

    def test_ai_provider_missing_configuration_uses_safe_local_fallback(self):
        with patch.dict(os.environ, {}, clear=True):
            with patch("study.urlopen") as provider:
                self.assertIn("mitochondrion", make_response("What is the powerhouse of the cell?").casefold())
                answer = generate_ai_response("Tell me a joke")
            with patch("study.search_medlineplus", return_value=([], None)):
                general_answer = make_response("What is the capital of France?")
        self.assertIsNone(answer)
        provider.assert_not_called()
        self.assertIn("general AI provider is not configured", general_answer)
        self.assertIn("ATP", make_response("Tell me a joke"))
        with patch.dict(os.environ, {}, clear=True):
            page = request("/study")["body"]
        self.assertIn("No AI model is configured", page)
        self.assertFalse(ai_provider_configured())
        with patch.dict(os.environ, {"WELLNOTE_AI_MODEL": "model-only"}, clear=True):
            message = generate_ai_response("Hello")
        self.assertIn("not fully configured", message)

    def test_ai_provider_http_errors_are_clear_and_do_not_leak_secrets(self):
        error = HTTPError(
            "https://example.test/v1/chat/completions", 401, "Unauthorized",
            {}, BytesIO(b"secret provider response"),
        )
        config = {"WELLNOTE_AI_API_KEY": "private-key", "WELLNOTE_AI_MODEL": "model"}
        with patch.dict(os.environ, config, clear=True):
            with patch("study.urlopen", side_effect=error):
                answer = generate_ai_response("What is a cell?")
        self.assertIn("rejected its credentials", answer)
        self.assertNotIn("private-key", answer)
        self.assertNotIn("secret provider response", answer)
        server_error = HTTPError(
            "https://example.test/v1/chat/completions", 503, "Unavailable",
            {}, BytesIO(b"provider internals"),
        )
        with patch.dict(os.environ, config, clear=True):
            with patch("study.urlopen", side_effect=server_error) as provider:
                with patch("study.time.sleep"):
                    answer = generate_ai_response("A general prompt")
        self.assertEqual(provider.call_count, 3)
        self.assertIn("HTTP 503", answer)
        self.assertIn("retried automatically", answer)
        self.assertNotIn("provider internals", answer)

        missing_model = HTTPError(
            "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions",
            404, "Not Found", {}, BytesIO(b"model details"),
        )
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}, clear=True):
            with patch("study.urlopen", side_effect=missing_model):
                answer = generate_ai_response("A research prompt")
        self.assertIn("GEMINI_MODEL", answer)
        self.assertIn("gemini-3.5-flash-lite", answer)
        self.assertNotIn("model details", answer)

    def test_ai_provider_retries_transient_503_and_recovers(self):
        response_body = json.dumps({
            "choices": [{"message": {"content": "Recovered answer"}}]
        }).encode()

        class FakeResponse:
            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return None

            def read(self, _limit):
                return response_body

        attempts = 0

        def fail_then_succeed(_request, timeout):
            nonlocal attempts
            attempts += 1
            if attempts < 3:
                raise HTTPError(
                    "https://example.test/v1/chat/completions",
                    503,
                    "Unavailable",
                    {},
                    BytesIO(b"temporary provider failure"),
                )
            return FakeResponse()

        config = {"WELLNOTE_AI_API_KEY": "private-key", "WELLNOTE_AI_MODEL": "model"}
        with patch.dict(os.environ, config, clear=True):
            with patch("study.urlopen", side_effect=fail_then_succeed):
                with patch("study.time.sleep") as sleep:
                    answer = generate_ai_response("A general prompt")

        self.assertEqual(answer, "Recovered answer")
        self.assertEqual(attempts, 3)
        self.assertEqual(sleep.call_count, 2)

    def test_gemini_switches_models_after_transient_retries_are_exhausted(self):
        response_body = json.dumps({
            "choices": [{"message": {"content": "Recovered with Gemini fallback"}}]
        }).encode()

        class FakeResponse:
            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return None

            def read(self, _limit):
                return response_body

        models_used = []

        def fail_primary_then_succeed(request, timeout):
            models_used.append(json.loads(request.data)["model"])
            if len(models_used) <= 3:
                raise HTTPError(
                    request.full_url, 503, "Unavailable", {}, BytesIO(b"temporary")
                )
            return FakeResponse()

        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}, clear=True):
            with patch("study.urlopen", side_effect=fail_primary_then_succeed):
                with patch("study.time.sleep"):
                    answer = generate_ai_response("Explain this study topic")

        self.assertEqual(answer, "Recovered with Gemini fallback")
        self.assertEqual(
            models_used,
            [
                "gemini-3.5-flash-lite",
                "gemini-3.5-flash-lite",
                "gemini-3.5-flash-lite",
                "gemini-3.8-flash",
            ],
        )

    def test_gemini_reports_outage_after_all_fallback_models_fail(self):
        models_used = []

        def fail_every_model(request, timeout):
            models_used.append(json.loads(request.data)["model"])
            raise HTTPError(
                request.full_url, 503, "Unavailable", {}, BytesIO(b"temporary")
            )

        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}, clear=True):
            with patch("study.urlopen", side_effect=fail_every_model):
                with patch("study.time.sleep"):
                    answer = generate_ai_response("Explain this study topic")

        self.assertEqual(
            models_used,
            [
                "gemini-3.5-flash-lite",
                "gemini-3.5-flash-lite",
                "gemini-3.5-flash-lite",
                "gemini-3.8-flash",
                "gemini-3.1-flash-lite",
            ],
        )
        self.assertIn("HTTP 503", answer)
        self.assertIn("alternate Gemini model", answer)

    def test_practice_question_checks_answer(self):
        body = request("/study/question")["body"]
        self.assertIn(QUESTIONS[0]["question"], body)
        self.assertIn("Next question", body)
        next_body = request("/study/question", query="after=cell")["body"]
        self.assertIn(QUESTIONS[1]["question"], next_body)
        self.assertNotIn(QUESTIONS[0]["question"], next_body)
        result = request("/study/answer/cell", method="POST", form="answer=1")
        self.assertIn("Correct!", result["body"])
        result = request("/study/answer/cell", method="POST", form="answer=0")
        self.assertIn("Not quite", result["body"])

    def test_next_question_cycles_through_varied_questions_then_wraps(self):
        self.assertGreaterEqual(len(QUESTIONS), 8)
        question_ids = [item["id"] for item in QUESTIONS]
        self.assertEqual(len(question_ids), len(set(question_ids)))
        for index, question in enumerate(QUESTIONS):
            expected = QUESTIONS[(index + 1) % len(QUESTIONS)]
            self.assertEqual(next_question_id(question["id"]), expected["id"])
            result = request(
                "/study/question",
                query="after=" + quote_plus(question["id"]),
            )
            self.assertIn(expected["question"], result["body"])
            self.assertNotIn(question["question"], result["body"])
        self.assertEqual(next_question_id("unknown"), QUESTIONS[0]["id"])

    def test_saved_topics_and_invalid_routes(self):
        result = request("/saved/add/asthma", method="POST")
        self.assertTrue(result["status"].startswith("303"))
        cookie = result["headers"]["Set-Cookie"].split(";", 1)[0]
        self.assertIn(COOKIE_NAME, cookie)
        self.assertIn("Asthma", request("/saved", cookie=cookie)["body"])
        with patch("app.search_medlineplus", return_value=([], "Reference service unavailable")), \
                patch("app.search_youtube_video", return_value=(None, "YouTube unavailable")):
            unknown = request("/disease/nope")
        self.assertTrue(unknown["status"].startswith("200"))
        self.assertIn("Reference service unavailable", unknown["body"])
        self.assertTrue(request("/", method="DELETE")["status"].startswith("405"))


if __name__ == "__main__":
    unittest.main()
