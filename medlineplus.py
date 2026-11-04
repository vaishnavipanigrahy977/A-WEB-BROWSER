"""Small client for the National Library of Medicine's MedlinePlus search API."""

from html.parser import HTMLParser
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET


API_URL = "https://wsearch.nlm.nih.gov/ws/query"
SITE_ROOT = "https://medlineplus.gov/"
MAX_RESULTS = 3
MAX_RESPONSE_BYTES = 1_000_000
TIMEOUT_SECONDS = 4


class _TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []

    def handle_data(self, data):
        self.parts.append(data)


def _plain_text(markup):
    parser = _TextExtractor()
    parser.feed(markup)
    parser.close()
    return " ".join(" ".join(parser.parts).split())


def search_medlineplus(term):
    """Return sanitized, linked MedlinePlus health-topic summaries and an error.

    The remote API is an optional extension to the small curated local catalog.
    No medical facts are generated here; result text comes directly from
    MedlinePlus and links are restricted to its HTTPS host.
    """
    params = urlencode({"db": "healthTopics", "term": term, "retmax": MAX_RESULTS})
    request = Request(
        f"{API_URL}?{params}",
        headers={"Accept": "application/xml", "User-Agent": "WellnoteHealthLearning/1.0"},
    )
    try:
        with urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            payload = response.read(MAX_RESPONSE_BYTES + 1)
        if len(payload) > MAX_RESPONSE_BYTES:
            return [], "The reference response was too large to process."
        root = ET.fromstring(payload)
    except (URLError, TimeoutError, OSError) as exc:
        return [], f"MedlinePlus could not be reached right now ({exc})."
    except ET.ParseError:
        return [], "MedlinePlus returned a response that could not be read."

    results = []
    for document in root.findall(".//document")[:MAX_RESULTS]:
        url = document.get("url", "")
        if not url.startswith("https://medlineplus.gov/"):
            continue
        fields = {}
        for content in document.findall("content"):
            fields.setdefault(content.get("name", ""), []).append(content.text or "")
        title = _plain_text(" ".join(fields.get("title", [])))
        summary = _plain_text(" ".join(fields.get("FullSummary", [])) or " ".join(fields.get("snippet", [])))
        if title:
            results.append({
                "title": title,
                "summary": summary[:1000],
                "url": url,
            })
    return results, None
