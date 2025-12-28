import os
import time
from google import genai
from google.genai import types
from dotenv import load_dotenv
import logging

load_dotenv()

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GeminiClient:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY is missing in .env")
        
        # Gemini uses genai.Client() with API key
        self.client = genai.Client(api_key=self.api_key)
        # Gemini 3 Flash - latest and most capable model
        self.model_name = "gemini-3-flash-preview"
        self.max_retries = 5
        self.retry_delay = 25  # 25 seconds for rate limit recovery

    async def generate_response(self, persona_instruction: str, history: list, user_input: str) -> str:
        """
        Generates a response from a specific AI persona using Gemini.
        Includes retry logic for rate limit errors.
        """
        
        # Build context from history
        context_text = self._build_context(history)
        
        # Combine context + user input into contents
        full_prompt = f"""
--- TOPLANTI GEÇMİŞİ ---
{context_text}

--- ŞİMDİKİ GÖREV ---
{user_input}
"""
        
        for attempt in range(self.max_retries):
            try:
                # Gemini API format with system_instruction in config
                response = self.client.models.generate_content(
                    model=self.model_name,
                    contents=full_prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=persona_instruction
                    )
                )
                
                return response.text
            
            except Exception as e:
                error_str = str(e)
                
                # Check if it's a rate limit error (429)
                if "429" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                    wait_time = self.retry_delay * (attempt + 1)  # Exponential backoff
                    logger.warning(f"Rate limit hit. Waiting {wait_time}s before retry {attempt + 1}/{self.max_retries}")
                    time.sleep(wait_time)
                    continue
                else:
                    logger.error(f"Gemini API Error: {e}")
                    return "Beyinlerim yandı... (API Error)"
        
        logger.error("Max retries exceeded for Gemini API")
        return "Beyinlerim yandı... (Rate Limit)"

    def _build_context(self, history: list) -> str:
        """
        Converts internal history list to a readable context string.
        """
        if not history:
            return "(Henüz konuşma yok)"
        
        context_lines = []
        for msg in history:
            bot_name = msg.get('bot_name', 'Bilinmeyen')
            content = msg.get('content', '')
            context_lines.append(f"[{bot_name}]: {content}")
        
        return "\n".join(context_lines)
