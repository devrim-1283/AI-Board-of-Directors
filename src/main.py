import asyncio
import logging
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler

from src.db import init_db
from src.bot_manager import BotManager
from src.ai_engine import GeminiClient
from src.orchestrator import Orchestrator

# Setup Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

load_dotenv()

# Global Objects
bot_manager = None
orchestrator = None

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Merhaba! Ben Yönetim Kurulu Başkanı'yım.\n\nBir fikri tartışmak için:\n`/toplanti [Fikir/Konu]`\nkomutunu kullanabilirsin.")

async def toplanti_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Lütfen bir konu belirtin.\nÖrnek: `/toplanti Yeni mobil uygulama fikri`")
        return

    topic = " ".join(context.args)
    user = update.effective_user
    chat_id = update.effective_chat.id

async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    info_text = """
ℹ️ **AI Yönetim Kurulu Bilgilendirme**

Bu sistem, 5 farklı yapay zeka karakterinin fikirlerinizi tartıştığı bir simülasyondur.

🤖 **Botlar:**
1. **Yönetim Kurulu Başkanı (Chairman):** Toplantıyı yönetir, özetler ve oylatır.
2. **CTO:** Teknik, altyapı ve güvenlik odaklı inceleme yapar.
3. **CFO:** Maliyet, bütçe ve finansal riskleri analiz eder.
4. **Growth Hacker:** Pazarlama, büyüme ve viral yayılma odaklıdır.
5. **Product Owner:** Kullanıcı deneyimi (UX) ve müşteri memnuniyetini savunur.
6. **Devil's Advocate:** En kötü senaryoları düşünür, riskleri bulur.

🛠 **Komutlar:**
- `/toplanti [Konu]`: Belirtilen konuda yeni bir toplantı başlatır.
- `/tanis`: Tüm botlar sırayla kendilerini tanıtır.
- `/ozet`: Mevcut toplantıyı özetleyip kapatır.
- `/sus`: Aktif toplantıyı acil olarak durdurur.
- `/info`: Bu bilgi mesajını gösterir.
- `/start`: Botu selamlar.

💡 **Nasıl Çalışır?**
Bir konu atıldığında botlar sırayla (2 Tur) konuşur, birbirlerinin fikirlerine cevap verirler ve en sonunda Başkan ortak bir karar metni çıkarır.
    """
    await update.message.reply_text(info_text, parse_mode='Markdown')

async def toplanti_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Lütfen bir konu belirtin.\nÖrnek: `/toplanti Yeni mobil uygulama fikri`")
        return

    topic = " ".join(context.args)
    user = update.effective_user
    chat_id = update.effective_chat.id

    # Admin ID kontrolü kaldırıldı - Herkes toplantı başlatabilir.

    await update.message.reply_text(f"📁 Konu alındı: **{topic}**\nKurul toplanıyor, lütfen bekleyin...")
    
    # Start the async meeting flow
    # logic is handled in orchestrator, completely detached from this handler to avoid timeout
    asyncio.create_task(orchestrator.start_new_meeting(chat_id, topic, user.id))

async def tanis_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if orchestrator:
        await update.message.reply_text("📢 **Yönetim Kurulu Üyeleri Takdim Ediliyor...**")
        asyncio.create_task(orchestrator.introduce_team(chat_id))

async def sus_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if orchestrator:
        stopped = await orchestrator.stop_meeting(chat_id)
        if stopped:
            await update.message.reply_text("🛑 **Toplantı Durduruldu!** Tüm botlar susturuldu.")
        else:
            await update.message.reply_text("ℹ️ Şu an aktif bir toplantı yok.")

async def ozet_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if orchestrator:
        summarized = await orchestrator.force_summary(chat_id)
        if not summarized:
            await update.message.reply_text("ℹ️ Özetlenecek aktif bir toplantı bulunamadı.")

async def main():
    global bot_manager, orchestrator

    # 1. Database Init
    logger.info("Initializing Database...")
    await init_db()

    # 2. Components Init
    logger.info("Initializing Components...")
    bot_manager = BotManager()
    gemini_client = GeminiClient()
    orchestrator = Orchestrator(bot_manager, gemini_client)

    # 3. Initialize Bots
    await bot_manager.initialize_bots()

    # 4. Attach Handlers to Chairman Bot
    # Only Chairman listens for commands to avoid duplicate replies if all bots are in group
    chairman_app = bot_manager.get_bot_app("Chairman")
    if chairman_app:
        chairman_app.add_handler(CommandHandler("start", start_command))
        chairman_app.add_handler(CommandHandler("toplanti", toplanti_command))
        chairman_app.add_handler(CommandHandler("info", info_command))
        chairman_app.add_handler(CommandHandler("tanis", tanis_command))
        chairman_app.add_handler(CommandHandler("sus", sus_command))
        chairman_app.add_handler(CommandHandler("ozet", ozet_command))
        logger.info("Handlers attached to Chairman.")
    else:
        logger.error("Chairman bot not found! Check personas.json and .env")

    # 5. Start EVERYTHING
    logger.info("Starting Bot Symphony...")
    await bot_manager.start_polling()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
