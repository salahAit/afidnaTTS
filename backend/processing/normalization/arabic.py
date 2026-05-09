"""AfidnaTTS Backend - Arabic Text Normalization"""
import re
from backend.core.logging import get_logger

logger = get_logger("normalization")

class ArabicNormalizer:
    def __init__(self):
        # Basic Arabic symbol to word mapping
        self.replacements = {
            "ﷺ": "صلى الله عليه وسلم",
            "📖": "صفحة",
            "؟": "?",
            "؛": ",",
            "٪": "بالمائة",
        }
        
        self.abbreviations = {
            "د.": "دكتور",
            "أ.": "أستاذ",
            "ص.ب": "صندوق بريد",
            "هـ": "هجري",
            "م": "ميلادي",
        }

    def normalize(self, text: str) -> str:
        if not text: return ""
        
        # 1. Replace symbols
        for sym, word in self.replacements.items():
            text = text.replace(sym, f" {word} ")
            
        # 2. Replace abbreviations
        for abbr, full in self.abbreviations.items():
            text = text.replace(abbr, f" {full} ")

        # 3. Handle Numbers using num2words
        def replace_numbers(match):
            from num2words import num2words
            try:
                num = match.group()
                return " " + num2words(num, lang='ar') + " "
            except:
                return match.group()
        
        text = re.sub(r'\d+', replace_numbers, text)

        # 4. Handle units
        text = text.replace("kg", " كيلوغرام ")
        text = text.replace("km", " كيلومتر ")
        text = text.replace("$", " دولار ")
        
        # 5. Clean up extra spaces
        text = re.sub(r'\s+', ' ', text).strip()
        
        logger.debug("Text normalized successfully")
        return text

    def clean_arabic(self, text: str) -> str:
        """Removes excessive repetitions and handles non-supported characters."""
        # Remove repeated punctuations like !!! or ???
        text = re.sub(r'([!?])\1+', r'\1', text)
        # Remove non-arabic/non-latin characters if they disturb the model
        # (Keeping it simple for now)
        return text

arabic_normalizer = ArabicNormalizer()
