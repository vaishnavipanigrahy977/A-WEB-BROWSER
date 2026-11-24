"""Search OpenStax's live book catalog for medical-foundation subjects."""

import json
import re
from http.client import HTTPException
from urllib.error import URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen


CATALOG_URL = "https://openstax.org/apps/cms/api/books/?format=json"
OPENSTAX_ROOT = "https://openstax.org/"
MAX_RESPONSE_BYTES = 2_000_000
TIMEOUT_SECONDS = 5
MAX_RESULTS = 60

FIELD_CATEGORIES = {
    "Physics": {"physics"},
    "Chemistry": {"chemistry"},
    "Biology": {"biology"},
    "Others": {"anatomy and physiology"},
}
FIELD_URLS = {
    "Physics": "https://openstax.org/subjects/science#Physics",
    "Chemistry": "https://openstax.org/subjects/science#Chemistry",
    "Biology": "https://openstax.org/subjects/science#Biology",
    "Others": "https://openstax.org/subjects/science#Anatomy%20and%20Physiology",
}
ALLOWED_FIELDS = tuple(FIELD_CATEGORIES)
MEDICAL_INTENT_TERMS = {
    "medical", "medicine", "doctor", "doctors", "premed", "pre-med",
    "entrance", "neet", "mcat", "aamc",
}


def _record_field(book):
    categories = book.get("subject_categories")
    if not isinstance(categories, list):
        categories = []
    normalized_categories = {
        value.strip().casefold()
        for value in categories
        if isinstance(value, str)
    }
    for field, names in FIELD_CATEGORIES.items():
        if normalized_categories.intersection(names):
            return field

    title = book.get("title", "")
    if not isinstance(title, str):
        return None
    title = title.casefold()
    if any(term in title for term in ("biology", "microbiology")):
        return "Biology"
    if "anatomy" in title or "physiology" in title:
        return "Others"
    if "chemistry" in title:
        return "Chemistry"
    if "physics" in title:
        return "Physics"
    return None


def _catalog_records(payload):
    catalog = json.loads(payload)
    books = catalog.get("books") if isinstance(catalog, dict) else None
    if not isinstance(books, list):
        raise ValueError("OpenStax catalog did not contain a book list.")

    records = []
    seen = set()
    for book in books:
        if not isinstance(book, dict) or book.get("book_state") != "live":
            continue
        title = book.get("title")
        slug = book.get("slug")
        field = _record_field(book)
        if (
            not isinstance(title, str)
            or not title.strip()
            or not isinstance(slug, str)
            or not re.fullmatch(r"books/[a-z0-9][a-z0-9-]*", slug)
            or field not in FIELD_CATEGORIES
            or slug in seen
        ):
            continue
        seen.add(slug)
        records.append({
            "title": title.strip(),
            "field": field,
            "url": urljoin(OPENSTAX_ROOT, slug),
            "subject_url": FIELD_URLS[field],
            "slug": slug,
            "categories": book.get("subject_categories", []),
            "tags": book.get("promote_tags", []),
            "description": book.get("promote_snippet", ""),
        })
    return records


def _load_catalog():
    request = Request(
        CATALOG_URL,
        headers={
            "Accept": "application/json",
            "User-Agent": "WellNoteHealthLearning/1.0",
        },
    )
    with urlopen(request, timeout=TIMEOUT_SECONDS) as response:
        payload = response.read(MAX_RESPONSE_BYTES + 1)
    if len(payload) > MAX_RESPONSE_BYTES:
        raise ValueError("OpenStax catalog response was too large.")
    return _catalog_records(payload)


def search_openstax_books(term, field=""):
    """Return matching live OpenStax book links in the allowed medical fields."""
    term = term.strip()[:120]
    if not term:
        return [], None
    if field not in ("", *ALLOWED_FIELDS):
        field = ""

    try:
        records = _load_catalog()
    except (URLError, HTTPException, TimeoutError, OSError):
        return [], "The OpenStax catalog could not be reached right now."
    except (ValueError, json.JSONDecodeError):
        return [], "OpenStax returned a catalog response that could not be read."

    words = re.findall(r"[a-z0-9]+", term.casefold())
    content_words = [word for word in words if word not in MEDICAL_INTENT_TERMS]
    broad_medical_search = bool(words) and not content_words
    matches = []
    for record in records:
        if field and record["field"] != field:
            continue
        if not broad_medical_search:
            categories = record["categories"]
            if not isinstance(categories, list):
                categories = []
            tags = record["tags"]
            if not isinstance(tags, list):
                tags = []
            description = record["description"]
            searchable = " ".join(
                [record["title"], record["field"]]
                + [value for value in categories + tags if isinstance(value, str)]
                + ([description] if isinstance(description, str) else [])
            ).casefold()
            if not all(word in searchable for word in content_words):
                continue
        matches.append({
            "title": record["title"],
            "field": record["field"],
            "url": record["url"],
            "subject_url": record["subject_url"],
        })
        if len(matches) >= MAX_RESULTS:
            break
    return matches, None
