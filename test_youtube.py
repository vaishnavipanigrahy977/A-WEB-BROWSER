import json
import unittest
from unittest.mock import patch

import youtube


class FakeResponse:
    def __init__(self, content):
        self.content = content

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def read(self, limit=-1):
        return self.content[:limit]


class YouTubeSearchTests(unittest.TestCase):
    def tearDown(self):
        youtube.search_youtube_video.cache_clear()

    def test_returns_a_topic_search_result_only_after_oembed_verification(self):
        video_id = "A1B2C3D4E5F"
        shorts_id = "SHORTS12345"
        search_page = (
            f'"shortsLockupViewModel":{{"videoId":"{shorts_id}"}}'
            f'"videoRenderer":{{"videoId":"{video_id}"}}'
        ).encode()
        metadata = json.dumps({
            "title": "Malaria animation",
            "author_name": "Health Learning",
            "html": f'<iframe src="https://www.youtube.com/embed/{video_id}"></iframe>',
        }).encode()
        with patch("youtube.urlopen", side_effect=[
            FakeResponse(search_page),
            FakeResponse(metadata),
        ]) as open_url:
            result, error = youtube.search_youtube_video("malaria")

        self.assertIsNone(error)
        self.assertEqual(result, {
            "video_id": video_id,
            "title": "Malaria animation",
            "channel": "Health Learning",
        })
        self.assertEqual(open_url.call_count, 2)

    def test_returns_empty_result_when_youtube_has_no_video_candidates(self):
        with patch("youtube.urlopen", return_value=FakeResponse(b"<html>no videos</html>")):
            result, error = youtube.search_youtube_video("unknown condition")

        self.assertIsNone(result)
        self.assertIsNone(error)


if __name__ == "__main__":
    unittest.main()
