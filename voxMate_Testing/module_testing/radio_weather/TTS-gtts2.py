from gtts import gTTS
import feedparser
import re
import time


def text_to_speech(message):
    start_total = time.time()

    # Clean up any markdown-like formatting
    clean_message = re.sub(r"\*\*(.*?)\*\*", r"\1", message)
    clean_message = re.sub(r"[_*~]", "", clean_message)

    tts = gTTS(text=clean_message, lang='en')
    tts.save("py_test.mp3")

    stop_total = time.time()
    print(f"Total Time to create audio: {stop_total - start_total:.2f} seconds")


def format_for_tts(news_list):
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


# Parse BBC News RSS feed
rss_url = "https://feeds.bbci.co.uk/news/rss.xml"
feed = feedparser.parse(rss_url)

if feed.entries:
    news_list = []
    for entry in feed.entries[:5]:  # First 5 headlines
        headline = entry.title
        summary = entry.summary if 'summary' in entry else ''
        news_list.append(f"{headline}. {summary}")

    # Format for TTS
    formatted_news = (
        "Here is the latest news bulletin.  \n\n"
        + format_for_tts(news_list)
        + "  \n\nThat’s the end of your news update."
    )

    print(formatted_news)  # Debug print
    text_to_speech(formatted_news)

else:
    print("No entries found in the feed.")