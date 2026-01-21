# app/rss_parser.py
import feedparser
import logging
import os
import requests
import time
import certifi
import re
import concurrent.futures
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime, timedelta, timezone
from dateutil import parser as date_parser

# Import configuration and helpers
from app.rss_sources import SOURCES, REGION_KEYWORDS, EXCLUDE_KEYWORDS
from app.law_detector import LawDetector
from app.summarizer import NewsSummarizer
from app.circuit_breaker import CircuitBreaker

logger = logging.getLogger(__name__)

class RSSParser:
    def __init__(self):
        self.sources = SOURCES
        self.region_keywords = [k.lower() for k in REGION_KEYWORDS]
        self.exclude_keywords = [k.lower() for k in EXCLUDE_KEYWORDS]
        
        self.law_detector = LawDetector()
        self.summarizer = NewsSummarizer()
        
        # Circuit Breaker Registry: { source_url: CircuitBreakerInstance }
        self.breakers = {
            src["url"]: CircuitBreaker(failure_threshold=3, recovery_timeout=1800) 
            for src in self.sources
        }
        
        # State storage for debug endpoint
        self.source_statuses = {} 

    def clean_text(self, text: str) -> str:
        """Clean HTML and remove unwanted urls/spaces."""
        if not text: return ""
        soup = BeautifulSoup(text, "html.parser")
        text = soup.get_text(separator=" ", strip=True)
        text = re.sub(r'https?://\S+\.(?:jpg|jpeg|png|webp|gif)\S*', '', text, flags=re.IGNORECASE)
        text = re.sub(r'https?://img\S+', '', text, flags=re.IGNORECASE)
        text = ' '.join(text.split())
        return text

    def is_relevant(self, text: str) -> bool:
        """Strict filtering: Text MUST contain at least one region keyword."""
        text_lower = text.lower()
        return any(k in text_lower for k in self.region_keywords)

    def calculate_importance(self, title: str, summary: str, content_type: str, published_str: str) -> int:
        """
        Calculates news score (1 to 5).
        +5: Constitution (Auto-Max)
        +2: Keyword in title
        +2: Is a Law/Act
        +1: >3 mentions of region in text
        +1: Fresh news (< 24 hours)
        """
        if content_type == "constitution":
            return 5
            
        score = 1 # Base score
        full_text = f"{title} {summary}"
        full_text_lower = full_text.lower()
        
        # 1. Keyword in Title (+2)
        title_lower = title.lower()
        if any(k in title_lower for k in self.region_keywords):
            score += 2
            
        # 2. Is Law (+2 boost for laws, as they are high priority)
        if content_type == "law":
            score += 2
            
        # 3. Multiple mentions (+1)
        mentions = sum(full_text_lower.count(k) for k in self.region_keywords)
        if mentions > 3:
            score += 1
            
        # 4. Freshness (+1 if < 24 hours)
        try:
            if published_str:
                pub_date = date_parser.parse(published_str)
                if pub_date.tzinfo is None:
                    pub_date = pub_date.replace(tzinfo=timezone.utc)
                
                now = datetime.now(timezone.utc)
                if now - pub_date < timedelta(hours=24):
                    score += 1
            # REMOVED: Automatic +1 for HTML news without dates.
            # If no date is found, we don't grant freshness bonus to be safe.
        except:
            pass
            
        return min(score, 5)

    def fetch_source(self, source: Dict) -> List[Dict]:
        """Fetch a single source with Circuit Breaker protection."""
        start_t = time.time()
        source_name = source.get("name", "Unknown")
        source_url = source.get("url")
        source_type = source.get("type", "rss")
        
        breaker = self.breakers.get(source_url)
        
        result_status = {
            "name": source_name,
            "url": source_url,
            "type": source_type,
            "ok": False,
            "entries_count": 0,
            "error": None,
            "elapsed_ms": 0,
            "circuit": breaker.state.value if breaker else "N/A"
        }
        
        # Check Circuit Breaker
        if breaker and not breaker.allow_request():
            logger.info(f"CircuitBreaker: Skipping {source_name} (State: OPEN)")
            result_status["error"] = "Circuit Breaker OPEN"
            self.source_statuses[source_url] = result_status
            return []

        entries = []
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }

        try:
            # Fetch logic...
            if source_type in ["rss", "google_rss"]:
                response = requests.get(source_url, headers=headers, timeout=6, verify=certifi.where())
                response.raise_for_status()
                feed = feedparser.parse(response.content)
                for entry in feed.entries:
                    entries.append({
                        "title": entry.get("title", ""),
                        "link": entry.get("link", ""),
                        "summary": entry.get("summary", entry.get("description", "")),
                        "published": entry.get("published", ""),
                        "source_name": source_name
                    })

            elif source_type == "html_list":
                response = requests.get(source_url, headers=headers, timeout=5, verify=certifi.where())
                response.raise_for_status()
                soup = BeautifulSoup(response.content, "html.parser")
                links = soup.find_all('a', href=True)
                valid_count = 0
                for a in links:
                    if valid_count >= 10: break # More candidates, but filter strictly
                    t = self.clean_text(a.get_text())
                    if len(t) < 25: continue
                    link = a['href']
                    if "gov.kz" in source_url and "/press/news/" not in link: continue
                    if link.startswith("/"):
                        link = ("https://www.gov.kz" if "gov.kz" in source_url else "https://news20.kz") + link
                    
                    # --- IMPROVED HTML Date Extraction ---
                    pub_date = ""
                    # Search up to 4 parents for metadata container
                    parent = a
                    for _ in range(4):
                        parent = parent.parent
                        if not parent: break
                        
                        # 1. Look for <time> tag
                        time_tag = parent.find("time")
                        if time_tag:
                            pub_date = time_tag.get("datetime") or time_tag.get_text()
                            break
                        
                        # 2. Look for common date classes
                        date_el = parent.find(class_=re.compile(r"date|time|bi_date_pub", re.I))
                        if date_el:
                            pub_date = date_el.get_text()
                            break
                            
                        # 3. Fallback: Regex in parent text
                        date_match = re.search(r'(\d{2}\.\d{2}\.\d{4})', parent.get_text())
                        if date_match:
                            pub_date = date_match.group(1)
                            break
                    
                    entries.append({
                        "title": t, 
                        "link": link, 
                        "summary": t, 
                        "published": pub_date, 
                        "source_name": source_name
                    })
                    valid_count += 1

            elif source_type == "telegram":
                response = requests.get(source_url, headers=headers, timeout=6, verify=certifi.where())
                response.raise_for_status()
                soup = BeautifulSoup(response.content, "html.parser")
                
                # Telegram Web wraps messages in tgme_widget_message_wrap
                msgs = soup.find_all("div", class_="tgme_widget_message_wrap")
                
                for wrap in msgs:
                    msg_div = wrap.find("div", class_="tgme_widget_message")
                    if not msg_div: continue
                    
                    # Text content
                    text_div = msg_div.find("div", class_="tgme_widget_message_text")
                    if not text_div:
                        # Maybe it is a photo-only post or album without caption?
                        # Using text detection from any part if main text block missing?
                        # For now, skip empty text posts as they lack context for filtering
                        continue
                        
                    raw_text = text_div.get_text(separator=" ", strip=True)
                    if len(raw_text) < 10: continue # Skip very short/empty messages
                    
                    cleaned_text = self.clean_text(raw_text)
                    
                    # Link
                    link_node = msg_div.find("a", class_="tgme_widget_message_date")
                    link = link_node["href"] if link_node else ""
                    
                    # Date
                    time_node = msg_div.find("time", class_="time")
                    pub_date = ""
                    if time_node and time_node.has_attr("datetime"):
                        pub_date = time_node["datetime"]
                    
                    entries.append({
                        "title": cleaned_text[:100] + "..." if len(cleaned_text) > 100 else cleaned_text,
                        "link": link,
                        "summary": cleaned_text,
                        "published": pub_date,
                        "source_name": source_name
                    })

            result_status["ok"] = True
            result_status["entries_count"] = len(entries)
            if breaker: breaker.record_success()

        except Exception as e:
            result_status["error"] = str(e)
            if breaker: breaker.record_failure()
            logger.warning(f"Source {source_name} failed: {e}")
            
        result_status["elapsed_ms"] = int((time.time() - start_t) * 1000)
        self.source_statuses[source_url] = result_status
        return entries

    def fetch_news(self) -> List[Dict[str, Any]]:
        """Fetch, filter, and score news. Sorted by importance."""
        all_raw_entries = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            future_to_source = {executor.submit(self.fetch_source, src): src for src in self.sources}
            done, not_done = concurrent.futures.wait(future_to_source.keys(), timeout=10)
            for future in done:
                try:
                    all_raw_entries.extend(future.result())
                except: pass
            for future in not_done: future.cancel()

        processed_news = []
        seen_links = set()
        
        now = datetime.now(timezone.utc)
        seven_days_ago = now - timedelta(days=7)
        
        for entry in all_raw_entries:
            link = entry.get("link", "")
            if not link or link in seen_links: continue
            seen_links.add(link)
            
            # --- TIME FILTERING ---
            pub_date_str = entry.get("published", "")
            
            # DEFAULT: If no date found in HTML source, treat as EXPIRED (very old)
            # to prevent leaks. RSS usually has dates or is live anyway.
            # We use 1970 as a safe 'old' date.
            pub_date_obj = datetime(1970, 1, 1, tzinfo=timezone.utc)
            is_fresh = True
            
            if pub_date_str:
                try:
                    # Use dateutil for robust parsing
                    parsed_dt = date_parser.parse(pub_date_str)
                    if parsed_dt.tzinfo is None:
                        parsed_dt = parsed_dt.replace(tzinfo=timezone.utc)
                    
                    pub_date_obj = parsed_dt
                except Exception as e:
                    logger.debug(f"Date parsing failed for {pub_date_str}: {e}")
            
            # Final 7-day check
            if pub_date_obj < seven_days_ago:
                is_fresh = False
                
            if not is_fresh:
                continue

            title = entry.get("title", "")
            summary = self.clean_text(entry.get("summary", ""))
            if not summary: summary = title
            
            # --- NEGATIVE FILTERING ---
            # Exclude news about other major cities if they don't explicitly mention Ulytau.
            full_text_lower = f"{title} {summary}".lower()
            has_exclude = any(k in full_text_lower for k in self.exclude_keywords)
            has_include = self.is_relevant(f"{title} {summary}")
            
            if has_exclude and not has_include:
                 # It mentions another city (e.g. Shymkent) AND NOT Ulytau -> SKIP
                 # This overrides Law/Constitution checks to avoid spam.
                 continue

            # --- CATEGORY DETECTION ---
            ctype = self.law_detector.get_category(f"{title} {summary}")
            
            # --- BYPASS FILTER FOR CONSTITUTION ONLY ---
            # User requested strict filtering. General laws are now hidden unless they mention Ulytau.
            # Only Constitutional changes (major events) bypass the region check.
            if ctype != "constitution" and not self.is_relevant(f"{title} {summary}"):
                continue
            
            score = self.calculate_importance(title, summary, ctype, pub_date_str)
            
            processed_news.append({
                "title": title,
                "summary": summary[:350] + "..." if len(summary) > 350 else summary,
                "type": ctype,
                "source": entry.get("source_name"),
                "link": link,
                "score": score,
                "pub_date_obj": pub_date_obj # Store for sorting
            })

        # --- MULTI-LEVEL SORTING ---
        # 1. By Score (Highest first)
        # 2. By Date (Newest first)
        processed_news.sort(key=lambda x: (x["score"], x["pub_date_obj"]), reverse=True)
        
        # Clean up objects before returning to API (JSON can't handle datetime)
        for item in processed_news:
            if "pub_date_obj" in item:
                del item["pub_date_obj"]

        return processed_news

    def get_sources_status(self) -> List[Dict]:
        return list(self.source_statuses.values())
