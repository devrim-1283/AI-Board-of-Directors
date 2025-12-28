import os
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
        
        # Gemini 3 uses genai.Client() with API key
        self.client = genai.Client(api_key=self.api_key)
        self.model_name = "gemini-3-flash-preview"

    async def generate_response(self, persona_instruction: str, history: list, user_input: str) -> str:
        """
        Generates a response from a specific AI persona using Gemini 3.
        
        Args:
            persona_instruction (str): The 'System Instruction' defining the bot's character.
            history (list): List of previous messages in the meeting (Context).
            user_input (str): The specific prompt or trigger for this turn.
            
        Returns:
            str: The AI's response text.
        """
        try:
            # Build context from history
            context_text = self._build_context(history)
            
            # Combine context + user input into contents
            full_prompt = f"""
--- TOPLANTI GEÇMİŞİ ---
{context_text}

--- ŞİMDİKİ GÖREV ---
{user_input}
"""
            
            # Gemini 3 API format with system_instruction in config
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=full_prompt,
                config=types.GenerateContentConfig(
                    system_instruction=persona_instruction,
                    thinking_config=types.ThinkingConfig(thinking_level="low")  # Fast responses for chat
                )
            )
            
            return response.text
        
        except Exception as e:
            logger.error(f"Gemini API Error: {e}")
            return "Beyinlerim yandı... (API Error)"

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
