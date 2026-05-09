"""AfidnaTTS Backend - Arabic Diacritics Engine (CAMeL)"""
from backend.core.logging import get_logger
from backend.core.config import DEFAULT_DIACRITICS_LEVEL
import os

logger = get_logger("diacritics")

class DiacriticsEngine:
    def __init__(self):
        self.model = None
        self._initialized = False

    def _initialize(self):
        if self._initialized: return
        try:
            from camel_tools.utils.dediac import dediac_ar
            from camel_tools.disambig.bert import BERTUnfactoredDisambiguator
            from camel_tools.tokenizers.word import simple_word_tokenize
            
            # This requires camel-tools data to be downloaded
            self.disambiguator = BERTUnfactoredDisambiguator.pretrained('msa')
            self._initialized = True
            logger.info("CAMeL Tools diacritizer initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize CAMeL Tools: {e}")
            logger.warning("Falling back to simple diacritization (none)")

    def process(self, text: str, level: str = DEFAULT_DIACRITICS_LEVEL) -> str:
        """
        Diacritizes Arabic text using CAMeL Tools.
        If initialization fails, returns the original text.
        """
        if not text: return ""
        if level == "none": return text
        
        self._initialize()
        if not self._initialized:
            return text
            
        try:
            from camel_tools.tokenizers.word import simple_word_tokenize
            
            tokens = simple_word_tokenize(text)
            disambig_results = self.disambiguator.disambiguate(tokens)
            
            diacritized_tokens = []
            for i, result in enumerate(disambig_results):
                # Get the top diacritized form
                diacritized = result.analyses[0].analysis['diac']
                diacritized_tokens.append(diacritized)
            
            return " ".join(diacritized_tokens)
        except Exception as e:
            logger.error(f"Diacritization failed: {e}")
            return text

diacritics_engine = DiacriticsEngine()
