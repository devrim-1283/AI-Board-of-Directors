import asyncio
import logging
import os
import json
from telegram import Bot
from telegram.ext import Application, ApplicationBuilder, CommandHandler, MessageHandler, filters
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class BotManager:
    def __init__(self, personas_file='src/personas.json'):
        self.bots = {} # { 'CTO': ApplicationObject, 'Chairman': ApplicationObject ... }
        self.bot_info = {} # { 'CTO': {name, role...} }
        self.personas_file = personas_file
        self.load_personas()
        self.group_id =  os.getenv("TELEGRAM_GROUP_ID") 
        if self.group_id:
            try:
                 self.group_id = int(self.group_id)
            except ValueError:
                logger.error("TELEGRAM_GROUP_ID must be an integer (e.g., -100...)")

    def load_personas(self):
        with open(self.personas_file, 'r', encoding='utf-8') as f:
            self.personas = json.load(f)

        for key, p in self.personas.items():
            token_env_var = p.get('token_env')
            token = os.getenv(token_env_var)
            
            if token:
                logger.info(f"Initializing bot for {key}...")
                # We build an Application for each bot to handle updates if needed
                app = ApplicationBuilder().token(token).build()
                self.bots[key] = app
                self.bot_info[key] = p
            else:
                logger.warning(f"Token not found for {key} ({token_env_var})")

    async def initialize_bots(self):
        """Initializes all bot applications."""
        for app in self.bots.values():
            await app.initialize()

    async def start_polling(self):
        """Starts polling for all bots concurrently."""
        # Note: In a production environment with limiting, we might want to prioritize the Chairman for commands
        # For simplicity, we start all. Be aware of race conditions on signal handling if using run_polling.
        # Here we use start() + updater.start_polling() pattern for "manual" control or 
        # use asyncio.gather on run_polling if supported. 
        # python-telegram-bot v20 recommends only one run_polling per process usually due to signals.
        # We will use start() and updater.start_polling() manually to avoid signal conflicts.
        
        tasks = []
        for key, app in self.bots.items():
            await app.start()
            # We assume we want them to process updates (listen for mentions/replies)
            # For the MVP, mainly Chairman needs to listen for /toplanti
            # But we turn them all on.
            if app.updater:
                await app.updater.start_polling(allowed_updates=["message", "callback_query"])
                logger.info(f"Started polling for {key}")
        
        # Keep the loop alive
        # A simple event to keep the main loop running
        stop_signal = asyncio.Event()
        await stop_signal.wait()

    async def send_message(self, bot_key, chat_id, text, reply_to_message_id=None):
        """Sends a message using a specific persona's bot."""
        app = self.bots.get(bot_key)
        if not app:
            logger.error(f"Bot {bot_key} not found or initialized.")
            return None
        
        try:
            # First try with reply
            sent_msg = await app.bot.send_message(
                chat_id=chat_id,
                text=text,
                reply_to_message_id=reply_to_message_id,
                parse_mode='Markdown'
            )
            return sent_msg
        except Exception as e:
            error_str = str(e)
            
            # If reply target not found, retry without reply
            if "Message to be replied not found" in error_str or "replied" in error_str.lower():
                logger.warning(f"Reply target not found for {bot_key}, sending without reply")
                try:
                    sent_msg = await app.bot.send_message(
                        chat_id=chat_id,
                        text=text,
                        parse_mode='Markdown'
                    )
                    return sent_msg
                except Exception as e2:
                    logger.error(f"Error sending message as {bot_key} (retry): {e2}")
                    return None
            else:
                logger.error(f"Error sending message as {bot_key}: {e}")
                return None

    def get_bot_app(self, bot_key):
        return self.bots.get(bot_key)
