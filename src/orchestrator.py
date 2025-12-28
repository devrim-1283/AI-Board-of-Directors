import asyncio
import logging
from datetime import datetime
from src.db import AsyncSessionLocal
from src.models import Meeting, Message
from src.ai_engine import GeminiClient
from sqlalchemy import select, update
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

class Orchestrator:
    def __init__(self, bot_manager, gemini_client):
        self.bot_manager = bot_manager
        self.gemini_client = gemini_client
        self.turn_order = ["CTO", "CFO", "Growth", "Product", "Devil"] 
        self.rounds = 2
        self.active_meetings = {}  # chat_id -> {'meeting_id': int, 'stopped': bool}

    async def stop_meeting(self, chat_id):
        """Stops the active meeting for a chat."""
        if chat_id in self.active_meetings:
            self.active_meetings[chat_id]['stopped'] = True
            meeting_id = self.active_meetings[chat_id].get('meeting_id')
            if meeting_id:
                async with AsyncSessionLocal() as session:
                    stmt = update(Meeting).where(Meeting.id == meeting_id).values(status="stopped")
                    await session.execute(stmt)
                    await session.commit()
            return True
        return False

    async def force_summary(self, chat_id):
        """Forces summary of the active meeting."""
        if chat_id in self.active_meetings:
            meeting_data = self.active_meetings[chat_id]
            meeting_id = meeting_data.get('meeting_id')
            topic = meeting_data.get('topic', 'Belirtilmemiş')
            if meeting_id:
                self.active_meetings[chat_id]['stopped'] = True
                await self.summarize_meeting(chat_id, meeting_id, topic)
                return True
        return False 

    async def start_new_meeting(self, chat_id, topic, user_id):
        """Initiates a new meeting."""
        
        # 1. Create DB Record
        async with AsyncSessionLocal() as session:
            new_meeting = Meeting(topic=topic, status="active")
            session.add(new_meeting)
            await session.commit()
            await session.refresh(new_meeting)
            meeting_id = new_meeting.id

        logger.info(f"Starting meeting {meeting_id} on '{topic}'")
        
        # Register active meeting
        self.active_meetings[chat_id] = {
            'meeting_id': meeting_id,
            'topic': topic,
            'stopped': False
        }

        # 2. Chairman Opening
        chairman_intro = f"🔔 **Yönetim Kurulu Toplantısı Başladı**\n\n📋 **Gündem:** {topic}\n\nToplantıyı açıyorum. Söz sırası: Teknoloji Lideri (CTO) ile başlıyoruz."
        sent_msg = await self.bot_manager.send_message("Chairman", chat_id, chairman_intro)

        # 3. Log Chairman Message
        await self.log_message(meeting_id, "Chairman", chairman_intro, 0, sent_msg.message_id if sent_msg else None)

        # 4. Start Orchestration Loop
        asyncio.create_task(self.run_meeting_loop(chat_id, meeting_id, topic))

    async def run_meeting_loop(self, chat_id, meeting_id, topic):
        """Main loop that iterates through 3 rounds with different prompts."""
        
        # Small delay before starting
        await asyncio.sleep(2)
        
        # Round definitions with specific purposes
        round_configs = [
            {
                "round": 1,
                "name": "İLK GÖRÜŞLER",
                "prompt": f"'{topic}' konusu hakkında ilk değerlendirmeni yap. Kendi uzmanlık alanından (rolünden) bakarak kısa ve net bir görüş bildir. Henüz tartışma yok, sadece kendi fikrini söyle."
            },
            {
                "round": 2,
                "name": "TARTIŞMA",
                "prompt": f"Diğer üyelerin '{topic}' hakkındaki görüşlerini duydun. Şimdi onların söylediklerine yanıt ver, eleştir veya destekle. Özellikle sana zıt görüşlere cevap ver. Tartışmacı ol ama profesyonel kal."
            },
            {
                "round": 3,
                "name": "SON SÖZLER",
                "prompt": f"Tartışma bitti. '{topic}' hakkındaki SON fikrini söyle. Lehte mi aleyhte mi olduğunu net belirt. Tek cümlelik kesin bir yargı ver."
            }
        ]

        for config in round_configs:
            # Check if meeting was stopped
            if self.active_meetings.get(chat_id, {}).get('stopped', False):
                logger.info(f"Meeting {meeting_id} was stopped by user.")
                return
            
            current_round = config["round"]
            round_name = config["name"]
            round_prompt = config["prompt"]
            
            logger.info(f"Meeting {meeting_id} - Round {current_round}: {round_name}")
            
            # Announce Round
            await self.bot_manager.send_message("Chairman", chat_id, f"📢 **{round_name}** (Tur {current_round}/3)")
            await asyncio.sleep(1)

            for persona_key in self.turn_order:
                # Check if meeting was stopped
                if self.active_meetings.get(chat_id, {}).get('stopped', False):
                    logger.info(f"Meeting {meeting_id} was stopped by user.")
                    return
                    
                await self.play_turn(chat_id, meeting_id, topic, persona_key, current_round, round_prompt)
                await asyncio.sleep(4)  # Wait between speakers for realism
            
            await asyncio.sleep(2)  # Pause between rounds

        # End of Rounds - Summary
        await self.summarize_meeting(chat_id, meeting_id, topic)
        
        # Cleanup
        if chat_id in self.active_meetings:
            del self.active_meetings[chat_id]

    async def play_turn(self, chat_id, meeting_id, topic, persona_key, round_num, round_prompt):
        """Executes a single turn for a bot."""
        
        # 1. Fetch History (Context)
        history = await self.get_meeting_history(meeting_id)
        
        # Determine Reply Target
        reply_to_id = None
        if history:
            async with AsyncSessionLocal() as session:
                stmt = select(Message).where(Message.meeting_id == meeting_id).order_by(Message.id.desc()).limit(1)
                result = await session.execute(stmt)
                last_msg = result.scalar_one_or_none()
                if last_msg:
                    reply_to_id = last_msg.telegram_message_id

        # 2. Prepare System Prompt & Input
        persona = self.bot_manager.bot_info.get(persona_key)
        system_instruction = persona.get('system_instruction', '')
        
        # Use the round-specific prompt
        user_input_prompt = f"""
TOPLANTI KONUSU: {topic}
TUR: {round_num}/3

{round_prompt}

ÖNEMLİ: 
- Maksimum 4-5 cümle yaz
- Rolüne uygun konuş
- Gereksiz emoji kullanma
"""

        # 3. Generate AI Response
        try:
            await self.bot_manager.get_bot_app(persona_key).bot.send_chat_action(chat_id=chat_id, action="typing")
        except Exception as e:
            logger.warning(f"Could not send typing action: {e}")
        
        # Simulate thinking time
        await asyncio.sleep(2) 
        response_text = await self.gemini_client.generate_response(system_instruction, history, user_input_prompt)

        # 4. Clean Response (Optional: Remove markdown code blocks if raw json comes)
        
        # 5. Send Message to Telegram
        sent_msg = await self.bot_manager.send_message(persona_key, chat_id, response_text, reply_to_message_id=reply_to_id)
        
        # 6. Log to DB
        msg_id_to_save = sent_msg.message_id if sent_msg else None
        await self.log_message(meeting_id, persona_key, response_text, round_num, msg_id_to_save)

    async def summarize_meeting(self, chat_id, meeting_id, topic):
        """Chairman summarizes and closes the meeting."""
        
        history = await self.get_meeting_history(meeting_id)
        persona = self.bot_manager.bot_info.get("Chairman")
        
        prompt = f"""
        Toplantı bitti. Konu: '{topic}'.
        Tüm konuşmaları analiz et.
        1. Ortak Karar (Konsensüs) var mı?
        2. En büyük risk nedir?
        3. Sonuç: Yapalım mı, yapmayalım mı?
        4. Oylama Sonucu (Sanal bir oylama uydur, örn: 3 Evet, 2 Hayır).
        
        Lider gibi konuş ve toplantıyı resmi olarak kapat.
        """
        
        try:
            await self.bot_manager.get_bot_app("Chairman").bot.send_chat_action(chat_id=chat_id, action="typing")
        except Exception as e:
            logger.warning(f"Could not send typing action: {e}")
        
        await asyncio.sleep(2)
        summary_text = await self.gemini_client.generate_response(persona['system_instruction'], history, prompt)

        sent_msg = await self.bot_manager.send_message("Chairman", chat_id, summary_text)
        await self.log_message(meeting_id, "Chairman", summary_text, 99, sent_msg.message_id if sent_msg else None)
        
        # Close Meeting in DB
        async with AsyncSessionLocal() as session:
            stmt = update(Meeting).where(Meeting.id == meeting_id).values(status="completed", is_processed=True)
            await session.execute(stmt)
            await session.commit()

    async def log_message(self, meeting_id, bot_name, content, round_num, telegram_message_id=None):
        async with AsyncSessionLocal() as session:
            msg = Message(
                meeting_id=meeting_id, 
                bot_name=bot_name, 
                content=content, 
                round_number=round_num,
                telegram_message_id=telegram_message_id
            )
            session.add(msg)
            await session.commit()

    async def introduce_team(self, chat_id):
        """Bots introduce themselves sequentially."""
        
        introduction_order = ["Chairman"] + self.turn_order
        
        for persona_key in introduction_order:
            persona = self.bot_manager.bot_info.get(persona_key)
            
            # Simple static introduction or dynamic
            # Let's use a dynamic one using Gemini for flavor, or static for speed.
            # Using prompt for flavor:
            prompt = f"Kısaca kendini tanıt. Kimsin, ne iş yaparsın ve tarzın ne? Tek bir cümle ile söyle. Merhaba diyerek başla."
            
            try:
                await self.bot_manager.get_bot_app(persona_key).bot.send_chat_action(chat_id=chat_id, action="typing")
            except Exception as e:
                logger.warning(f"Could not send typing action: {e}")
            
            # Fast response
            intro_text = await self.gemini_client.generate_response(persona['system_instruction'], [], prompt)
            
            await self.bot_manager.send_message(persona_key, chat_id, intro_text)
            await asyncio.sleep(1.5) # Short pause between introductions

    async def get_meeting_history(self, meeting_id):
        async with AsyncSessionLocal() as session:
            # Fetch last 30 messages to fit in context
            stmt = select(Message).where(Message.meeting_id == meeting_id).order_by(Message.id.asc())
            result = await session.execute(stmt)
            messages = result.scalars().all()
            
            history_data = []
            for m in messages:
                history_data.append({
                    "bot_name": m.bot_name,
                    "content": m.content,
                    "is_user": False # All db logs are treated as 'context'
                })
            return history_data
