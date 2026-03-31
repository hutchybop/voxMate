# Required python imports
import feedparser
import os


# def get_news():

#     # Choose a short news RSS feed
#     # RSS_URL = "https://podcasts.files.bbci.co.uk/p02nq0gn.rss"
#     # RSS_URL = "http://feeds.bbci.co.uk/news/rss.xml?edition=uk"
#     # RSS_URL = "https://www.npr.org/rss/podcast.php?id=500005"
#     # RSS_URL = "https://podcasts.files.bbci.co.uk/news/sixminnews/rss.xml"
#     # RSS_URL = "https://feeds.skynews.com/feeds/rss/uk.xmlhttps://podcasts.files.bbci.co.uk/p02q5bq4.rss"
#     # RSS_URL = "https://podcasts.files.bbci.co.uk/p02nq0gn.rss"
#     RSS_URL = "https://feeds.a.dj.com/rss/RSSWSJD.xml"

#     try:
#         feed = feedparser.parse(RSS_URL)
#         print(feed)

#         # Get the first entry with a valid audio enclosure
#         for entry in feed.entries:
#             enclosures = entry.get("enclosures", [])
#             if enclosures:
#                 audio_url = enclosures[0].get("href")
#                 if audio_url:
#                     print(f"Now playing: {entry.title}")
#                     print(f"From: {feed.feed.title}")
#                     print(f"URL: {audio_url}")

#                     # Play the audio using afplay
#                     os.system(f'mpv "{audio_url}"')
#                     return

#         print("No audio enclosures found in the RSS feed.")

#     except Exception as e:
#         print(f"Error getting the news: {e}")

# get_news()

rss_url = "https://feeds.bbci.co.uk/news/rss.xml"

# Parse the RSS feed
feed = feedparser.parse(rss_url)

if feed.entries:
    news_text = []
    for entry in feed.entries[:5]:  # Limit to first 5 headlines
        headline = entry.title
        summary = entry.summary if 'summary' in entry else ''
        news_text.append(f"{headline}. {summary}")

    # Join into one block of plain text
    plain_text_news = "\n\n".join(news_text)

    print(plain_text_news)
else:
    print("No entries found in the feed.")


