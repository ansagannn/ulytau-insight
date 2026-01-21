# app/summarizer.py
import logging
from transformers import pipeline
import warnings

# Suppress warnings for clean output
warnings.filterwarnings("ignore")

logger = logging.getLogger(__name__)

class NewsSummarizer:
    """
    AI Summarizer using HuggingFace Transformers.
    """
    def __init__(self):
        logger.info("AI Summarizer: ML model loading DISABLED for performance stability.")
        self.active = False
        # try:
        #     self.summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")
        #     self.active = True
        # except Exception as e:
        #     logger.error(f"Failed to load ML model: {e}")
        #     self.active = False

    def summarize(self, text: str, max_length: int = 200, min_length: int = 50) -> str:
        """
        Generate a summary of the provided text.
        
        Args:
            text (str): Text to summarize.
            max_length (int): Max token length.
            min_length (int): Min token length.
        
        Returns:
            str: Summarized text or original text if summarization fails/is too short.
        """
        if not self.active or not text or len(text) < 100:
            return text[:max_length] + "..." if text and len(text) > max_length else text

        try:
            # Truncate input text to avoid model limits
            input_text = text[:1024] 
            
            summary_output = self.summarizer(input_text, max_length=max_length, min_length=min_length, do_sample=False)
            if summary_output and len(summary_output) > 0:
                summary_text = summary_output[0].get('summary_text', '')
                return summary_text.strip()
        except Exception as e:
            logger.error(f"Summarization error: {e}")
            
        return text[:max_length] + "..."
