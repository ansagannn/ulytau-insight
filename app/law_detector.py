# app/law_detector.py
from typing import List
from app.rss_sources import LAW_KEYWORDS, CONSTITUTION_KEYWORDS

class LawDetector:
    """
    Detector for identifying legislative content (laws, decrees, orders).
    """

    def __init__(self):
        self.law_keywords = [k.lower() for k in LAW_KEYWORDS]
        self.const_keywords = [k.lower() for k in CONSTITUTION_KEYWORDS]

    def is_law(self, text: str) -> bool:
        """Check if the text contains any law-related keywords."""
        if not text: return False
        text_lower = text.lower()
        return any(k in text_lower for k in self.law_keywords)

    def is_constitutional(self, text: str) -> bool:
        """Check if the text mentions constitutional changes."""
        if not text: return False
        text_lower = text.lower()
        return any(k in text_lower for k in self.const_keywords)

    def get_category(self, text: str) -> str:
        """
        Return category 'constitution', 'law' or 'news' based on content.
        """
        if self.is_constitutional(text):
            return "constitution"
        if self.is_law(text):
            return "law"
        return "news"
