from urllib.parse import urlparse, parse_qs
from youtube_transcript_api import YouTubeTranscriptApi


def extract_video_id(url):
    parsed = urlparse(url)

    if parsed.hostname == "youtu.be":
        return parsed.path[1:]

    if parsed.hostname in ("www.youtube.com", "youtube.com"):
        return parse_qs(parsed.query)["v"][0]

    return None

def get_youtube_video_trasncript(url):
    video_id = extract_video_id(url)
    if not video_id:
        return None
    
    transcript = YouTubeTranscriptApi().fetch(video_id)
    full_text = " ".join([snippet.text for snippet in transcript])
    return full_text
