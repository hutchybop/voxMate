# Required python imports
import feedparser

# Required local imports
from services.audio import AudioProcessor
from utils.logging import logger


def get_news():

    # For BBC
    news_url = "https://podcasts.files.bbci.co.uk/p02nq0gn.rss"

    try:
        feed = feedparser.parse(news_url)
        news_audio =  feed.entries[0].enclosures[0].href  # MP3 link
        AudioProcessor.play_sound(news_audio)
        return True, None
    except Exception as e:
        logger.error(f"Error getting the news: {e}")
        return False, "Could not get the news"


