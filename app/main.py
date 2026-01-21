from fastapi import FastAPI
from app.rss_parser import RSSParser
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Ulytau Inside AI Agent",
    description="AI-powered news monitoring agent for Ulytau region",
    version="1.0.0"
)

# Initialize Parser
rss_parser = RSSParser()

@app.get("/")
def read_root():
    return {"message": "Ulytau Inside AI Agent is running. Go to /news to see latest updates."}

@app.get("/news")
def get_news():
    """
    Get latest news. 
    Strict filtering is now Enforced by default in the parser.
    """
    # We remove query params logic to simplify: filtering is hardcoded in parser now.
    news_items = rss_parser.fetch_news()
    return {
        "count": len(news_items),
        "data": news_items
    }

@app.get("/debug/sources")
def debug_sources():
    """
    Check status of all configured sources.
    """
    return {
        "sources": rss_parser.get_sources_status()
    }

@app.get("/health")
def health_check():
    """
    Lightweight health check endpoint.
    """
    return {
        "ok": True,
        "service": "ulytau-insight",
        "version": "1.0.0"
    }

@app.get("/debug/feeds")
def debug_feeds():
    """
    Debug endpoint to check status of RSS feeds.
    """
    results = []
    for feed_url in rss_parser.feeds:
        try:
            feed_data, error = rss_parser.parse_feed(feed_url)
            entry_count = len(feed_data.entries) if feed_data else 0
            results.append({
                "url": feed_url,
                "entries": entry_count,
                "ok": feed_data is not None,
                "error": str(error) if error else None
            })
        except Exception as e:
            results.append({
                "url": feed_url,
                "entries": 0,
                "ok": False,
                "error": str(e)
            })
    return results

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
