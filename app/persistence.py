# app/persistence.py
import json
import os
import logging

logger = logging.getLogger(__name__)

class Persistence:
    """Handles JSON-based storage for bot state."""
    
    def __init__(self, storage_path="bot_data.json"):
        self.storage_path = storage_path
        self.data = {
            "subscribers": [],
            "seen_links": []
        }
        self.load()

    def load(self):
        """Load data from file."""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    file_content = f.read()
                    if file_content.strip():
                        self.data = json.loads(file_content)
                logger.info(f"Persistence: Loaded data from {self.storage_path}")
            except Exception as e:
                logger.error(f"Persistence: Failed to load data: {e}")

    def save(self):
        """Save data to file."""
        try:
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Persistence: Failed to save data: {e}")

    # Subscriber Management
    def add_subscriber(self, chat_id: int):
        if chat_id not in self.data["subscribers"]:
            self.data["subscribers"].append(chat_id)
            self.save()
            return True
        return False

    def remove_subscriber(self, chat_id: int):
        if chat_id in self.data["subscribers"]:
            self.data["subscribers"].remove(chat_id)
            self.save()
            return True
        return False

    def get_subscribers(self):
        return self.data["subscribers"]

    # Deduplication Logic
    def is_seen(self, link: str):
        return link in self.data["seen_links"]

    def add_seen(self, link: str):
        if link not in self.data["seen_links"]:
            self.data["seen_links"].append(link)
            # Keep only last 500 links to manage file size
            if len(self.data["seen_links"]) > 500:
                self.data["seen_links"] = self.data["seen_links"][-500:]
            self.save()
            return True
        return False
