"""Small YouTube search client for disease-topic video previews."""

from functools import lru_cache
from html import unescape
import json
import re
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


SEARCH_URL = "https://www.youtube.com/results"
OEMBED_URL = "https://www.youtube.com/oembed"
MAX_RESPONSE_BYTES = 2_000_000
TIMEOUT_SECONDS = 2
MAX_CANDIDATES = 3
VIDEO_ID_PATTERN = re.compile(
    r'"videoRenderer"\s*:\s*\{"videoId"\s*:\s*"([A-Za-z0-9_-]{11})"'
)


@lru_cache(maxsize=128)
def search_youtube_video(topic):
    """Find a topic-matched, embeddable YouTube result or return an error."""
    search_request = Request(
        f"{SEARCH_URL}?{urlencode({'search_query': topic + ' animated medical explanation'})}",
        headers={
            "Accept": "text/html",
            "User-Agent": "Mozilla/5.0 (compatible; WellNoteHealthLearning/1.0)",
        },
    )
    try:
        with urlopen(search_request, timeout=TIMEOUT_SECONDS) as response:
            page = response.read(MAX_RESPONSE_BYTES + 1)
    except (URLError, TimeoutError, OSError):
        return None, "YouTube could not be reached right now."
    if len(page) > MAX_RESPONSE_BYTES:
        return None, "YouTube returned a response that was too large to process."

    candidate_ids = list(dict.fromkeys(
        VIDEO_ID_PATTERN.findall(page.decode("utf-8", "replace"))
    ))[:MAX_CANDIDATES]
    if not candidate_ids:
        return None, None

    for video_id in candidate_ids:
        params = urlencode({
            "url": f"https://www.youtube.com/watch?v={video_id}",
            "format": "json",
        })
        request = Request(
            f"{OEMBED_URL}?{params}",
            headers={"Accept": "application/json"},
        )
        try:
            with urlopen(request, timeout=TIMEOUT_SECONDS) as response:
                payload = response.read(64_001)
            if len(payload) > 64_000:
                continue
            metadata = json.loads(payload)
        except (URLError, TimeoutError, OSError, json.JSONDecodeError):
            continue

        if not isinstance(metadata, dict):
            continue
        title = unescape(str(metadata.get("title", ""))).strip()
        channel = unescape(str(metadata.get("author_name", ""))).strip()
        embed_markup = metadata.get("html", "")
        if (
            title
            and channel
            and isinstance(embed_markup, str)
            and f"/embed/{video_id}" in embed_markup
        ):
            return {
                "video_id": video_id,
                "title": title,
                "channel": channel,
            }, None

    return None, None
