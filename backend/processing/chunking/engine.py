"""AfidnaTTS Backend - Smart Chunking Engine"""
import re
from typing import List
from backend.core.config import MAX_CHUNK_CHARS
from backend.core.logging import get_logger

logger = get_logger("chunking")

class ChunkingEngine:
    def split_text(self, text: str) -> List[str]:
        """Splits text into chunks based on paragraphs and punctuation."""
        if not text: return []
        
        # 1. Initial split by paragraphs
        paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
        
        final_chunks = []
        for para in paragraphs:
            if len(para) <= MAX_CHUNK_CHARS:
                final_chunks.append(para)
            else:
                # 2. Split long paragraphs by sentences
                sentences = re.split(r'([.?!؛])', para)
                current_chunk = ""
                
                for i in range(0, len(sentences), 2):
                    sentence = sentences[i]
                    punc = sentences[i+1] if i+1 < len(sentences) else ""
                    full_sentence = (sentence + punc).strip()
                    
                    if len(current_chunk) + len(full_sentence) <= MAX_CHUNK_CHARS:
                        current_chunk += (" " if current_chunk else "") + full_sentence
                    else:
                        if current_chunk: final_chunks.append(current_chunk)
                        current_chunk = full_sentence
                
                if current_chunk:
                    final_chunks.append(current_chunk)
        
        logger.info(f"Text split into {len(final_chunks)} chunks")
        return final_chunks

chunking_engine = ChunkingEngine()
