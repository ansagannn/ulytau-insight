
import logging
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.rss_parser import RSSParser

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

parser = RSSParser()

print(f"{'Source Name':<40} | {'Type':<10} | {'Entries':<7} | {'Status'}")
print("-" * 90)

for source in parser.sources:
    try:
        entries = parser.fetch_source(source)
        status_info = parser.source_statuses.get(source["url"], {})
        
        status_str = "OK" if status_info.get("ok") else f"ERR: {status_info.get('error')}"
        count = len(entries)
        
        print(f"{source['name']:<40} | {source.get('type'):<10} | {count:<7} | {status_str}")
        
        # Print first entry title for verification if it's a telegram source
        if source.get("type") == "telegram" and count > 0:
             print(f"   [Latest]: {entries[0]['title'][:80]}...")
             print(f"   [Date]: {entries[0]['published']}")
             print("-" * 40)

    except Exception as e:
        print(f"{source['name']:<40} | {source.get('type'):<10} | {0:<7} | EXC: {e}")
