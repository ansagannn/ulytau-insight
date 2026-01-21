
import logging
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.rss_parser import RSSParser

# Configure logging
logging.basicConfig(level=logging.ERROR) # Only show errors from modules

parser = RSSParser()

print(f"{'Source Name':<30} | {'Status':<5} | Titles (First 3)")
print("-" * 120)

for source in parser.sources:
    try:
        entries = parser.fetch_source(source)
        # Apply the parser's FULL filtering logic manually to see what survives
        # Because fetch_source returns RAW entries, we must restart the 'fetch_news' logic part
        # But wait, parser.fetch_news() does the filtering. Let's use that instead, 
        # but fetch_news mixes everything.
        
        # Let's just simulate the filtering on the fetched entries to debug specific sources
        
        filtered_debug = []
        for entry in entries:
            title = entry.get("title", "")
            summary = parser.clean_text(entry.get("summary", ""))
            link = entry.get("link", "")
            
            # Replicate filtering checks
            full_text_lower = f"{title} {summary}".lower()
            
            # 1. Exclude Check
            has_exclude = any(k in full_text_lower for k in parser.exclude_keywords)
            has_include = parser.is_relevant(f"{title} {summary}")
            
            if has_exclude and not has_include:
                continue # DROP
                
            # 2. Category Check
            ctype = parser.law_detector.get_category(f"{title} {summary}")
            
            # 3. Relevance/Bypass Check (UPDATED LOGIC)
            if ctype != "constitution" and not parser.is_relevant(f"{title} {summary}"):
                 continue # DROP
                 
            filtered_debug.append(title)

        status_str = "OK" 
        print(f"{source['name']:<30} | {len(filtered_debug):<5} | {filtered_debug[:3]}")
        

    except Exception as e:
        print(f"{source['name']:<30} | ERR   | {e}")
