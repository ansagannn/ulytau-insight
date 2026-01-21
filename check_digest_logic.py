
import asyncio
from datetime import datetime, timedelta
# Mock structures to simulate bot logic
class MockItem(dict):
    pass

items = [
    # Mock Data: 
    # High score (5), Law
    {"title": "Important Law Update", "type": "law", "score": 5, "link": "http://law.com", "summary": "Big change."},
    # High score (4), News
    {"title": "Major Event in Ulytau", "type": "news", "score": 4, "link": "http://news.com/1", "summary": "Something big happened."},
    # Low score (2), News
    {"title": "Small event", "type": "news", "score": 2, "link": "http://news.com/2", "summary": "Minor detail."},
    # High score (5), News
    {"title": "Another Major Event", "type": "news", "score": 5, "link": "http://news.com/3", "summary": "Another big thing."},
    # Excluded (simulated filtered out upstream, but here we assume items are result of filtered fetch)
]

# Simulate Logic from bot
now = datetime.now()
week_ago = now - timedelta(days=7)

digest_items = items # In real bot, we trust API filtered list.

digest_items.sort(key=lambda x: x.get('score', 0), reverse=True)

top_events = []
laws = []

for item in digest_items:
    # If Law/Constitution -> Add to laws
    if item.get('type') in ['law', 'constitution']:
        if len(laws) < 5:
            laws.append(item)
    else:
        # Regular news
        if item.get('score', 0) >= 4 and len(top_events) < 5:
            top_events.append(item)

# If no high score news, take just top 3 regular
if not top_events and not laws:
    top_events = digest_items[:3]

start_date = week_ago.strftime("%d.%m")
end_date = now.strftime("%d.%m")

msg_lines = [f"📅 <b>Главное за неделю ({start_date} - {end_date})</b>\n"]

if top_events:
    msg_lines.append("🏆 <b>Топ событий:</b>")
    for i, item in enumerate(top_events, 1):
        title = item.get('title', 'No Title')
        msg_lines.append(f"{i}. <a href='{item['link']}'>{title}</a>")
    msg_lines.append("")

if laws:
    msg_lines.append("⚖️ <b>Законы и решения:</b>")
    for item in laws:
        title = item.get('title', 'No Title')
        msg_lines.append(f"• <a href='{item['link']}'>{title}</a>")
    msg_lines.append("")
    
text = "\n".join(msg_lines)
print(text)
