import os
import google.generativeai as genai
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
        
        genai.configure(api_key=self.api_key)
        self.model_name = "gemini-1.5-flash"

    async def generate_response(self, persona_instruction: str, history: list, user_input: str) -> str:
        """
        Generates a response from a specific AI persona.
        
        Args:
            persona_instruction (str): The 'System Instruction' defining the bot's character.
            history (list): List of previous messages in the meeting (Context).
            user_input (str): The specific prompt or trigger for this turn.
            
        Returns:
            str: The AI's response text.
        """
        try:
            # Create a model instance with the specific system instruction for this persona
            # Note: In the new library versions, system_instruction can be passed to GenerativeModel
            model = genai.GenerativeModel(
                model_name=self.model_name,
                system_instruction=persona_instruction
            )

            # Convert database/internal history format to Gemini format if needed
            # For simplicity, we can feed history as a string in the prompt or use chat session
            # using chat session is better for context
            
            chat = model.start_chat(history=self._format_history_for_gemini(history))
            
            response = chat.send_message(user_input)
            return response.text
        
        except Exception as e:
            logger.error(f"Gemini API Error: {e}")
            return "Beyinlerim yandı... (API Error)"

    def _format_history_for_gemini(self, history: list) -> list:
        """
        Converts internal history list to Gemini's expected format.
        Expected internal history: [{'role': 'user'|'model', 'parts': ['message']}]
        
        Gemini expects:
        Content(role="user", parts=[Part(text="...")])
        """
        formatted_history = []
        for msg in history:
            # Simple mapping, assuming history comes in compatible structure or simple dicts
            role = "user" if msg.get("is_user", False) else "model"
            
            # If the previous message was from another bot, treating it as 'user' for relevant context 
            # might be better for the current bot to "respond" to it.
            # However, standard practice is User/Model. 
            # For a multi-bot chat, "everyone else" is effectively the "user" from the perspective of the current bot.
            
            formatted_history.append({
                "role": "user", # Treat all past context as 'user' input so the model reacts to it
                "parts": [f"[{msg['bot_name']}]: {msg['content']}"]
            })
            
            # If we want to strictly differentiate, we would need to know which message came from THIS specific bot instance
            # which is complex in a round-robin. 
            # Strategy: Feed everything as "User says: [CTO]: bla bla" so the model sees the flow.
            
        return formatted_history
