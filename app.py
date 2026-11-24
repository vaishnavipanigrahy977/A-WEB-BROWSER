"""Python-led, server-rendered health-learning app."""

from http import cookies
from http import HTTPStatus
import base64
import json
import os
from pathlib import Path
import re
from urllib.parse import parse_qs, unquote, urlsplit
from wsgiref.simple_server import make_server

import diseases
from medlineplus import search_medlineplus
import study
import templates
import translations
from youtube import search_youtube_video

ROOT = Path(__file__).resolve().parent
COOKIE_NAME = "wellnote_saved"
LANGUAGE_COOKIE_NAME = "wellnote_language"
COOKIE_MAX_AGE = 60 * 60 * 24 * 30
MAX_SAVED_COOKIE_LENGTH = 3800


def external_saved_token(topic):
    encoded = base64.urlsafe_b64encode(topic.encode("utf-8")).decode("ascii").rstrip("=")
    return f"x-{encoded}"


def decode_external_saved_token(token):
    if not token.startswith("x-") or not re.fullmatch(r"[A-Za-z0-9_-]+", token[2:]):
        return None
    try:
        encoded = token[2:]
        topic = base64.urlsafe_b64decode(encoded + "=" * (-len(encoded) % 4)).decode("utf-8")
    except (ValueError, UnicodeDecodeError):
        return None
    if not topic or len(topic) > 120 or external_saved_token(topic) != token:
        return None
    return topic


def saved_tokens(environ):
    jar = cookies.SimpleCookie()
    try:
        jar.load(environ.get("HTTP_COOKIE", ""))
    except cookies.CookieError:
        return []
    item = jar.get(COOKIE_NAME)
    tokens = []
    for token in item.value.split(",") if item else []:
        if token in diseases.DISEASES_BY_SLUG or decode_external_saved_token(token):
            if token not in tokens:
                tokens.append(token)
    return tokens


def saved_topic_names(tokens):
    return [
        topic for token in tokens
        if (topic := decode_external_saved_token(token)) is not None
    ]


def saved_page_items(tokens):
    items = []
    for token in tokens:
        disease = diseases.DISEASES_BY_SLUG.get(token)
        if disease:
            items.append(disease)
            continue
        topic = decode_external_saved_token(token)
        if topic:
            items.append({
                "external": True,
                "external_topic": topic,
                "name": topic,
                "category": "MedlinePlus reference",
                "summary": (
                    "Saved health topic. Open it to view the current source summary."
                ),
            })
    return items


def request_origin(environ):
    host = environ.get("HTTP_HOST", "localhost:8000").strip()
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9.-]*(?::[0-9]{1,5})?", host):
        host = "localhost:8000"
    forwarded_proto = environ.get("HTTP_X_FORWARDED_PROTO", "").split(",", 1)[0].strip().lower()
    scheme = forwarded_proto if forwarded_proto in ("http", "https") else environ.get("wsgi.url_scheme", "http")
    if scheme not in ("http", "https"):
        scheme = "http"
    return f"{scheme}://{host}"


def preferred_language(environ):
    jar = cookies.SimpleCookie()
    try:
        jar.load(environ.get("HTTP_COOKIE", ""))
    except cookies.CookieError:
        return "en"
    item = jar.get(LANGUAGE_COOKIE_NAME)
    language = item.value if item else "en"
    return language if language in translations.LANGUAGES else "en"


def find_local_disease(topic):
    normalized_topic = topic.casefold()
    return next((
        item for item in diseases.DISEASES
        if normalized_topic in (
            item["name"].casefold(),
            item["slug"].casefold(),
            item["slug"].replace("-", " ").casefold(),
        ) or any(
            normalized_topic in (
                translations.localize_disease(item, locale)["name"].casefold(),
                translations.localize_disease(item, locale)["category"].casefold(),
            )
            for locale in ("hi", "hinglish")
        )
    ), None)


def respond(start_response, status, body, extra_headers=None, content_type="text/html; charset=utf-8"):
    payload = body if isinstance(body, bytes) else body.encode("utf-8")
    headers = [
        ("Content-Type", content_type),
        ("Content-Length", str(len(payload))),
        ("X-Content-Type-Options", "nosniff"),
        ("X-Frame-Options", "DENY"),
        ("Referrer-Policy", "strict-origin-when-cross-origin"),
    ]
    headers.extend(extra_headers or [])
    start_response(f"{status.value} {status.phrase}" if isinstance(status, HTTPStatus) else status, headers)
    return [payload]


def redirect(start_response, location, slugs):
    jar = cookies.SimpleCookie()
    jar[COOKIE_NAME] = ",".join(slugs)
    item = jar[COOKIE_NAME]
    item["path"] = "/"
    item["max-age"] = COOKIE_MAX_AGE
    item["httponly"] = True
    item["samesite"] = "Lax"
    return respond(start_response, HTTPStatus.SEE_OTHER, b"", [("Location", location), ("Set-Cookie", item.OutputString())])


def application(environ, start_response):
    method = environ.get("REQUEST_METHOD", "GET").upper()
    path = unquote(environ.get("PATH_INFO", "/"))
    query_string = environ.get("QUERY_STRING", "")
    current_url = path + (f"?{query_string}" if query_string else "")
    origin = request_origin(environ)
    language = preferred_language(environ)
    saved = saved_tokens(environ)

    static_assets = {
        "/static/style.css": ("style.css", "text/css; charset=utf-8"),
        "/static/language.css": ("language.css", "text/css; charset=utf-8"),
        "/static/voice-tutor.js": ("voice-tutor.js", "text/javascript; charset=utf-8"),
        "/static/body-verse.css": ("body-verse.css", "text/css; charset=utf-8"),
        "/static/body-verse.js": ("body-verse.js", "text/javascript; charset=utf-8"),
    }
    if method == "GET" and path in static_assets:
        filename, content_type = static_assets[path]
        return respond(
            start_response, HTTPStatus.OK,
            (ROOT / "static" / filename).read_bytes(),
            content_type=content_type,
        )

    if method == "POST":
        if path == "/study/speak":
            content_length = int(environ.get("CONTENT_LENGTH") or "0")
            if content_length > 12_000:
                return respond(
                    start_response, HTTPStatus.REQUEST_ENTITY_TOO_LARGE,
                    "Speech text is too long.",
                )
            try:
                request_data = json.loads(
                    environ.get("wsgi.input").read(content_length).decode("utf-8")
                )
            except (UnicodeDecodeError, ValueError):
                return respond(
                    start_response, HTTPStatus.BAD_REQUEST,
                    "A valid JSON speech request is required.",
                )
            if not isinstance(request_data, dict):
                return respond(
                    start_response, HTTPStatus.BAD_REQUEST,
                    "A valid JSON speech request is required.",
                )
            text = request_data.get("text")
            speech_language = request_data.get("language", language)
            if not isinstance(text, str) or not text.strip() or len(text) > 5000:
                return respond(
                    start_response, HTTPStatus.BAD_REQUEST,
                    "Speech text must contain 1 to 5000 characters.",
                )
            if speech_language not in ("en", "hi", "hinglish"):
                return respond(
                    start_response, HTTPStatus.BAD_REQUEST,
                    "Unsupported speech language.",
                )
            try:
                audio = study.generate_gemini_speech(text, speech_language)
            except study.GeminiSpeechError as exc:
                return respond(
                    start_response, HTTPStatus.BAD_GATEWAY, str(exc),
                )
            if audio is None:
                return respond(
                    start_response, HTTPStatus.SERVICE_UNAVAILABLE,
                    "Gemini speech is not configured.",
                )
            return respond(
                start_response,
                HTTPStatus.OK,
                audio,
                [("Cache-Control", "no-store")],
                content_type="audio/wav",
            )
        form = parse_qs(environ.get("wsgi.input").read(int(environ.get("CONTENT_LENGTH") or "0")).decode("utf-8", "replace"))
        if path in ("/study/ask", "/study/ask-again"):
            prompt = form.get("prompt", [""])[0]
            return respond(start_response, HTTPStatus.OK, templates.study_page(
                diseases.DISEASES,
                study.greeting(),
                study.make_response(prompt, language),
                prompt=prompt,
                language=language,
                current_url=current_url,
            ))
        if path.startswith("/study/answer/"):
            question = next((q for q in study.QUESTIONS if q["id"] == path.rsplit("/", 1)[-1]), None)
            if question is None:
                status, body = templates.error_page(
                    "Question not found", "Choose another practice question.",
                    language=language, current_url=current_url,
                )
                return respond(start_response, status, body)
            answer = form.get("answer", [""])[0]
            try:
                result = int(answer)
            except ValueError:
                result = -1
            if not 0 <= result < len(question["options"]):
                result = -1
            return respond(start_response, HTTPStatus.OK, templates.study_page(
                diseases.DISEASES, study.greeting(), question=question, result=result,
                language=language, current_url=current_url,
            ))
        if path.startswith("/saved/"):
            parts = path.strip("/").split("/")
            if len(parts) == 2 and parts[1] in ("add-topic", "remove-topic"):
                topic = form.get("topic", [""])[0].strip()[:120]
                if not topic:
                    return respond(
                        start_response, HTTPStatus.BAD_REQUEST,
                        translations.translate("A health topic is required", language),
                    )
                local = find_local_disease(topic)
                matching_external_token = next(
                    (
                        entry for entry in saved
                        if (saved_topic := decode_external_saved_token(entry))
                        and saved_topic.casefold() == topic.casefold()
                    ),
                    None,
                )
                token = local["slug"] if local else (
                    matching_external_token or external_saved_token(topic)
                )
                if parts[1] == "add-topic":
                    updated_saved = saved if token in saved else saved + [token]
                    if len(f"{COOKIE_NAME}={','.join(updated_saved)}") > MAX_SAVED_COOKIE_LENGTH:
                        status, body = templates.error_page(
                            "Reading list is full",
                            "This browser’s reading-list storage is full. Remove a saved topic before adding another.",
                            status="400 Bad Request",
                            language=language,
                            current_url=current_url,
                        )
                        return respond(start_response, status, body)
                    if token not in saved:
                        saved.append(token)
                else:
                    saved = [
                        entry for entry in saved
                        if entry != token and (
                            decode_external_saved_token(entry) or ""
                        ).casefold() != topic.casefold()
                    ]
                return redirect(start_response, "/saved", saved)
            if len(parts) == 3 and parts[1] in ("add", "remove"):
                slug = parts[2]
                if slug not in diseases.DISEASES_BY_SLUG:
                    return respond(
                        start_response, HTTPStatus.NOT_FOUND,
                        translations.translate("Topic not found", language),
                    )
                if parts[1] == "add" and slug not in saved:
                    saved.append(slug)
                elif parts[1] == "remove":
                    saved = [entry for entry in saved if entry != slug]
                return redirect(start_response, "/saved", saved)
        return respond(
            start_response, HTTPStatus.NOT_FOUND,
            translations.translate("Page not found", language),
        )

    if method != "GET":
        return respond(
            start_response, HTTPStatus.METHOD_NOT_ALLOWED,
            translations.translate("Method not allowed", language),
        )

    if path == "/language":
        params = parse_qs(query_string)
        requested_language = params.get("lang", [""])[0]
        if requested_language not in translations.LANGUAGES:
            return respond(
                start_response, HTTPStatus.BAD_REQUEST,
                translations.translate("Unsupported language", language),
            )
        destination = params.get("next", ["/"])[0]
        parsed_destination = urlsplit(destination)
        if (
            not destination.startswith("/")
            or destination.startswith("//")
            or parsed_destination.scheme
            or parsed_destination.netloc
            or "\\" in destination
            or any(ord(character) < 32 or ord(character) == 127 for character in destination)
        ):
            destination = "/"
        jar = cookies.SimpleCookie()
        jar[LANGUAGE_COOKIE_NAME] = requested_language
        item = jar[LANGUAGE_COOKIE_NAME]
        item["path"] = "/"
        item["max-age"] = 60 * 60 * 24 * 365
        item["httponly"] = True
        item["samesite"] = "Lax"
        return respond(
            start_response, HTTPStatus.SEE_OTHER, b"",
            [("Location", destination), ("Set-Cookie", item.OutputString())],
        )

    if path == "/":
        query = parse_qs(query_string).get("q", [""])[0].strip()[:120]
        matches = [
            item for item in diseases.DISEASES
            if not query or query.casefold() in " ".join(
                (item["name"], item["category"], item["summary"], item["description"])
            ).casefold() or any(
                query.casefold() in " ".join(
                    str(value) for value in translations.localize_disease(item, locale).values()
                    if isinstance(value, (str, list))
                ).casefold()
                for locale in ("hi", "hinglish")
            )
        ]
        external_results, external_error = search_medlineplus(query) if query and not matches else ([], None)
        return respond(start_response, HTTPStatus.OK, templates.home_page(
            matches, query, external_results, external_error,
            language=language, current_url=current_url,
            saved_topics=saved_topic_names(saved),
        ))
    if path == "/saved":
        return respond(start_response, HTTPStatus.OK, templates.saved_page(
            saved_page_items(saved),
            language=language, current_url=current_url,
        ))
    if path == "/study/body-verse":
        return respond(start_response, HTTPStatus.OK, templates.body_verse_page(
            language=language, current_url=current_url,
        ))
    if path == "/study/mind-map":
        topic = parse_qs(query_string).get("topic", [""])[0].strip()[:120]
        selected = find_local_disease(topic)
        selected = translations.localize_disease(selected, language) if selected else None
        reference = None
        reference_error = None
        if topic and not selected:
            results, reference_error = search_medlineplus(topic)
            reference = results[0] if results else None
        return respond(start_response, HTTPStatus.OK, templates.mind_map_page(
            diseases.DISEASES, topic, selected, reference, reference_error,
            language=language, current_url=current_url,
            saved_topics=saved_topic_names(saved),
        ))
    if path == "/study/flashcards":
        topic = parse_qs(query_string).get("topic", [""])[0].strip()[:120]
        selected = find_local_disease(topic)
        selected = translations.localize_disease(selected, language) if selected else None
        reference = None
        reference_error = None
        if topic and not selected:
            results, reference_error = search_medlineplus(topic)
            reference = results[0] if results else None
        cards = (
            study.create_flashcards(selected)
            if selected else
            study.create_reference_flashcards(topic, reference, language)
            if reference else
            []
        )
        try:
            card_index = int(parse_qs(query_string).get("card", ["0"])[0])
        except ValueError:
            card_index = 0
        if not 0 <= card_index < len(cards):
            card_index = 0
        return respond(start_response, HTTPStatus.OK, templates.flashcards_page(
            topic, selected, reference, cards, card_index, reference_error,
            language=language, current_url=current_url,
            saved_topics=saved_topic_names(saved),
        ))
    if path == "/study/compare":
        params = parse_qs(query_string)
        first = params.get("first", [""])[0].strip()[:120]
        second = params.get("second", [""])[0].strip()[:120]
        left = right = None
        error = None
        if first and second:
            left_local = find_local_disease(first)
            right_local = find_local_disease(second)
            if first.casefold() == second.casefold() or (
                left_local and right_local and left_local["slug"] == right_local["slug"]
            ):
                error = "Enter two different diseases or health topics to compare."
            else:
                left_reference = right_reference = None
                left_error = right_error = None
                if not left_local:
                    results, left_error = search_medlineplus(first)
                    left_reference = results[0] if results else None
                if not right_local:
                    results, right_error = search_medlineplus(second)
                    right_reference = results[0] if results else None
                left = study.compare_health_topic(
                    first, left_local, left_reference, left_error
                )
                right = study.compare_health_topic(
                    second, right_local, right_reference, right_error
                )
        return respond(start_response, HTTPStatus.OK, templates.disease_comparison_page(
            first, second, left, right, error,
            language=language, current_url=current_url,
        ))
    if path in ("/study", "/study/question"):
        question = None
        if path.endswith("/question"):
            after = parse_qs(query_string).get("after", [""])[0]
            question_id = study.next_question_id(after)
            question = next(item for item in study.QUESTIONS if item["id"] == question_id)
        return respond(start_response, HTTPStatus.OK, templates.study_page(
            diseases.DISEASES, study.greeting(), question=question,
            language=language, current_url=current_url,
        ))
    if path.startswith("/study/"):
        selected = diseases.DISEASES_BY_SLUG.get(path.removeprefix("/study/"))
        if selected:
            return respond(start_response, HTTPStatus.OK, templates.study_page(
                diseases.DISEASES, study.greeting(), selected=selected,
                language=language, current_url=current_url,
            ))
    if path.startswith("/disease/"):
        selected = diseases.DISEASES_BY_SLUG.get(path.removeprefix("/disease/"))
        if selected:
            video = None
            video_error = None
            if not selected.get("video_id"):
                video, video_error = search_youtube_video(selected["name"])
            return respond(start_response, HTTPStatus.OK, templates.disease_page(
                selected, selected["slug"] in saved,
                language=language, current_url=current_url,
                video=video, video_error=video_error,
                origin=origin,
            ))
        topic = path.removeprefix("/disease/").replace("-", " ").strip()[:120]
        if topic:
            results, error = search_medlineplus(topic)
            video, video_error = search_youtube_video(topic)
            return respond(start_response, HTTPStatus.OK, templates.external_topic_page(
                topic, results, error, language=language, current_url=current_url,
                saved_topics=saved_topic_names(saved),
                video=video, video_error=video_error,
                origin=origin,
            ))
    status, body = templates.error_page(
        "Page not found", "The page may have moved or the topic is not in this starter library.",
        language=language, current_url=current_url,
    )
    return respond(start_response, status, body)


def serve():
    host = "0.0.0.0"
    port = int(os.environ.get("PORT", "8000"))
    print(f"WellNote is running at http://127.0.0.1:{port}")
    make_server(host, port, application).serve_forever()


if __name__ == "__main__":
    serve()
