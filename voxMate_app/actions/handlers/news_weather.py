import feedparser
import re
from typing import Optional, Tuple


from utils.logging import logger
from services.ai import AIService
from services.audio import AudioProcessor


def format_for_tts(news_list: str) -> str:
    formatted_items = []
    for i, item in enumerate(news_list, start=1):
        # Expand common abbreviations
        text = re.sub(r"\bUK\b", "United Kingdom", item)
        text = re.sub(r"\bUS\b", "United States", text)

        # Ensure a pause at the end
        text = text.strip()
        if not text.endswith("."):
            text += "."

        # Add story number for spoken clarity
        formatted_items.append(f"Story {i}. {text}")

    # Add pauses between stories
    return "  \n\n".join(formatted_items)


def get_rss_feed() -> str:
    # Parse BBC News RSS feed
    rss_url = "https://feeds.bbci.co.uk/news/rss.xml"
    feed = feedparser.parse(rss_url)

    if feed.entries:
        news_list = []
        for entry in feed.entries[:5]:  # First 5 headlines
            headline = entry.title
            summary = entry.summary if "summary" in entry else ""
            news_list.append(f"{headline}. {summary}")

        # Format for TTS
        formatted_news = (
            "Here is the latest news bulletin.  \n\n"
            + format_for_tts(news_list)
            + "  \n\nThat’s the end of your news update."
        )

        return formatted_news


def play_news() -> Tuple[bool, Optional[str]]:

    try:
        formatted_news = get_rss_feed()
        AIService.text_to_speech(formatted_news)
        AudioProcessor.play_sound()
        return True, None
    except Exception as e:
        logger.warning(f"Error playing the news {e}")
        return False, "There was an error playing the news"
