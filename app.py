"""Python-only server-rendered health-learning MVP (no JavaScript application code)."""

from http import cookies
from http import HTTPStatus
from pathlib import Path
from urllib.parse import parse_qs, unquote
from wsgiref.simple_server import make_server

import diseases
from medlineplus import search_medlineplus
import study
import templates

ROOT = Path(__file__).resolve().parent
COOKIE_NAME = "wellnote_saved"
COOKIE_MAX_AGE = 60 * 60 * 24 * 30


def saved_slugs(environ):
    jar = cookies.SimpleCookie()
    try:
        jar.load(environ.get("HTTP_COOKIE", ""))
    except cookies.CookieError:
        return []
    item = jar.get(COOKIE_NAME)
    return list(dict.fromkeys(
        slug for slug in (item.value.split(",") if item else [])
        if slug in diseases.DISEASES_BY_SLUG
    ))


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
    saved = saved_slugs(environ)

    if method == "GET" and path == "/static/style.css":
        return respond(start_response, HTTPStatus.OK, (ROOT / "static" / "style.css").read_bytes(), content_type="text/css; charset=utf-8")

    if method == "POST":
        form = parse_qs(environ.get("wsgi.input").read(int(environ.get("CONTENT_LENGTH") or "0")).decode("utf-8", "replace"))
        if path in ("/study/ask", "/study/ask-again"):
            prompt = form.get("prompt", [""])[0]
            return respond(start_response, HTTPStatus.OK, templates.study_page(
                diseases.DISEASES,
                study.greeting(),
                study.make_response(prompt),
                prompt=prompt,
            ))
        if path.startswith("/study/answer/"):
            question = next((q for q in study.QUESTIONS if q["id"] == path.rsplit("/", 1)[-1]), None)
            if question is None:
                status, body = templates.error_page("Question not found", "Choose another practice question.")
                return respond(start_response, status, body)
            answer = form.get("answer", [""])[0]
            try:
                result = int(answer)
            except ValueError:
                result = -1
            if not 0 <= result < len(question["options"]):
                result = -1
            return respond(start_response, HTTPStatus.OK, templates.study_page(diseases.DISEASES, study.greeting(), question=question, result=result))
        if path.startswith("/saved/"):
            parts = path.strip("/").split("/")
            if len(parts) == 3 and parts[1] in ("add", "remove"):
                slug = parts[2]
                if slug not in diseases.DISEASES_BY_SLUG:
                    return respond(start_response, HTTPStatus.NOT_FOUND, "Topic not found")
                if parts[1] == "add" and slug not in saved:
                    saved.append(slug)
                elif parts[1] == "remove":
                    saved = [entry for entry in saved if entry != slug]
                return redirect(start_response, "/saved", saved)
        return respond(start_response, HTTPStatus.NOT_FOUND, "Page not found")

    if method != "GET":
        return respond(start_response, HTTPStatus.METHOD_NOT_ALLOWED, "Method not allowed")

    if path == "/":
        query = parse_qs(environ.get("QUERY_STRING", "")).get("q", [""])[0].strip()[:120]
        matches = [
            item for item in diseases.DISEASES
            if not query or query.casefold() in " ".join(
                (item["name"], item["category"], item["summary"], item["description"])
            ).casefold()
        ]
        external_results, external_error = search_medlineplus(query) if query and not matches else ([], None)
        return respond(start_response, HTTPStatus.OK, templates.home_page(
            matches, query, external_results, external_error
        ))
    if path == "/saved":
        return respond(start_response, HTTPStatus.OK, templates.saved_page(
            [diseases.DISEASES_BY_SLUG[slug] for slug in saved]
        ))
    if path in ("/study", "/study/question"):
        question = None
        if path.endswith("/question"):
            after = parse_qs(environ.get("QUERY_STRING", "")).get("after", [""])[0]
            question_id = study.next_question_id(after)
            question = next(item for item in study.QUESTIONS if item["id"] == question_id)
        return respond(start_response, HTTPStatus.OK, templates.study_page(
            diseases.DISEASES, study.greeting(), question=question
        ))
    if path.startswith("/study/"):
        selected = diseases.DISEASES_BY_SLUG.get(path.removeprefix("/study/"))
        if selected:
            return respond(start_response, HTTPStatus.OK, templates.study_page(
                diseases.DISEASES, study.greeting(), selected=selected
            ))
    if path.startswith("/disease/"):
        selected = diseases.DISEASES_BY_SLUG.get(path.removeprefix("/disease/"))
        if selected:
            return respond(start_response, HTTPStatus.OK, templates.disease_page(
                selected, selected["slug"] in saved
            ))
        topic = path.removeprefix("/disease/").replace("-", " ").strip()[:120]
        if topic:
            results, error = search_medlineplus(topic)
            return respond(start_response, HTTPStatus.OK, templates.external_topic_page(topic, results, error))
    status, body = templates.error_page("Page not found", "The page may have moved or the topic is not in this starter library.")
    return respond(start_response, status, body)


if __name__ == "__main__":
    print("Wellnote is running at http://127.0.0.1:8000")
    make_server("127.0.0.1", 8000, application).serve_forever()
