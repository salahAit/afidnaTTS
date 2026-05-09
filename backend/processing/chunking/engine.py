"""AfidnaTTS Backend - Smart Chunking Engine"""
import re
from typing import List
from backend.core.config import MAX_CHUNK_CHARS
from backend.core.logging import get_logger

logger = get_logger("chunking")

class ChunkingEngine:
    def split_text(self, text: str) -> List[str]:
        """
        Splits text into chunks based on paragraphs and punctuation.
        Targeting 10-35 seconds per chunk (approx 200-700 characters).
        """
        if not text: return []
        
        # 1. Initial split by paragraphs
        paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
        
        final_chunks = []
        
        # Target character count (20 chars/sec * 25 sec = 500 chars)
        TARGET_CHARS = 500
        MIN_CHARS = 200
        MAX_CHARS = 700

        for para in paragraphs:
            if len(para) <= MAX_CHARS:
                final_chunks.append(para)
            else:
                # Split long paragraphs by sentences/punctuation
                # Using Arabic and Latin punctuation
                sentences = re.split(r'([.?!؛?،,])', para)
                
                current_chunk = ""
                for i in range(0, len(sentences), 2):
                    sentence = sentences[i]
                    punc = sentences[i+1] if i+1 < len(sentences) else ""
                    full_sentence = (sentence + punc).strip()
                    
                    # If adding this sentence stays within MAX_CHARS
                    if len(current_chunk) + len(full_sentence) + 1 <= MAX_CHARS:
                        current_chunk += (" " if current_chunk else "") + full_sentence
                        
                        # If we reached the TARGET_CHARS, close the chunk if it's "long enough"
                        if len(current_chunk) >= TARGET_CHARS:
                            final_chunks.append(current_chunk)
                            current_chunk = ""
                    else:
                        # Adding this sentence would exceed MAX_CHARS
                        if current_chunk:
                            # If current_chunk is too short, we might have to combine anyway or split sentence
                            if len(current_chunk) < MIN_CHARS and len(full_sentence) < MAX_CHARS:
                                # This is a tricky case, for now just push what we have
                                pass
                            final_chunks.append(current_chunk)
                        
                        # If the single sentence is longer than MAX_CHARS, we must force split it
                        if len(full_sentence) > MAX_CHARS:
                            # Force split by words
                            words = full_sentence.split(' ')
                            sub_chunk = ""
                            for word in words:
                                if len(sub_chunk) + len(word) + 1 <= MAX_CHARS:
                                    sub_chunk += (" " if sub_chunk else "") + word
                                else:
                                    final_chunks.append(sub_chunk)
                                    sub_chunk = word
                            current_chunk = sub_chunk
                        else:
                            current_chunk = full_sentence
                
                if current_chunk:
                    final_chunks.append(current_chunk)
        
        # Final pass: merge very short chunks if possible
        optimized_chunks = []
        temp_chunk = ""
        for chunk in final_chunks:
            if not temp_chunk:
                temp_chunk = chunk
            elif len(temp_chunk) + len(chunk) + 1 <= MAX_CHARS:
                temp_chunk += " " + chunk
            else:
                optimized_chunks.append(temp_chunk)
                temp_chunk = chunk
        if temp_chunk:
            optimized_chunks.append(temp_chunk)

        logger.info(f"Text split into {len(optimized_chunks)} optimized chunks")
        return optimized_chunks

chunking_engine = ChunkingEngine()
