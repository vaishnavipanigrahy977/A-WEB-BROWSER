import unittest
from io import BytesIO
import json
import os
from urllib.error import HTTPError
from unittest.mock import patch
from urllib.parse import quote_plus

import app as wellnote_app
from app import COOKIE_NAME, application
from medlineplus import search_medlineplus
from study import EXAM_GUIDES, QUESTIONS, ai_provider_configured, generate_ai_response, make_response, next_question_id


def request(path="/", method="GET", query="", cookie="", form=""):
    result = {}

    def start_response(status, headers):
        result["status"] = status
        result["headers"] = dict(headers)

    body = application({
        "REQUEST_METHOD": method, "PATH_INFO": path, "QUERY_STRING": query,
        "HTTP_COOKIE": cookie, "CONTENT_LENGTH": str(len(form.encode())),
        "wsgi.input": BytesIO(form.encode()),
    }, start_response)
    result["body"] = b"".join(body).decode()
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
        with patch("app.search_medlineplus", return_value=(medlineplus_result, None)):
            detail = request("/disease/malaria")
        self.assertTrue(detail["status"].startswith("200"))
        self.assertIn("This condition is not in Wellnote", detail["body"])
        self.assertNotIn("Common symptoms", detail["body"])

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
                         "not a substitute for a clinician"):
            self.assertIn(expected, body)

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
        self.assertIn("step by step", make_response("Help me with homework"))
        self.assertIn("personal symptoms", make_response("I have a symptom"))

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
        with patch("app.study.make_response", side_effect=lambda text: captured.append(text) or "Let’s study biology."):
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
            with patch("study.urlopen", side_effect=server_error):
                answer = generate_ai_response("A general prompt")
        self.assertIn("HTTP 503", answer)
        self.assertNotIn("provider internals", answer)

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
        with patch("app.search_medlineplus", return_value=([], "Reference service unavailable")):
            unknown = request("/disease/nope")
        self.assertTrue(unknown["status"].startswith("200"))
        self.assertIn("Reference service unavailable", unknown["body"])
        self.assertTrue(request("/", method="DELETE")["status"].startswith("405"))


if __name__ == "__main__":
    unittest.main()
