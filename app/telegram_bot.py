# Trigger Deploy
import logging
import os
import json
import requests
import asyncio
from typing import Set, List, Dict, Optional
from datetime import datetime, timedelta
from dotenv import load_dotenv

from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.constants import ParseMode
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    CallbackQueryHandler,
)

try:
    from app.persistence import Persistence
except ImportError:
    from persistence import Persistence

# 1) Load .env
load_dotenv()
# 2) Config
BOT_TOKEN = os.getenv("BOT_TOKEN")
API_URL = os.getenv("API_URL", "https://ulytau-insight.onrender.com")
BOT_LIMIT = int(os.getenv("BOT_LIMIT", "5"))
POST_INTERVAL_MIN = int(os.getenv("POST_INTERVAL_MIN", "15"))
DISABLE_PREVIEW = os.getenv("DISABLE_PREVIEW", "true").lower() == "true"

# Initialize Persistence
db = Persistence()

# 3) Configure Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- Helper Functions ---

def fetch_news(limit: int = 40) -> List[Dict]:
    """
    Fetches news from the local API.
    """
    try:
        url = f"{API_URL}/news"
        response = requests.get(url, timeout=60)
        response.raise_for_status()
        payload = response.json()
        return payload.get("data", [])[:limit]
    except Exception as e:
        logger.error(f"Error in fetch_news: {e}")
        return []

async def send_news_item(update: Update, item: Dict):
    """Helper to send a formatted news item to a specific update context."""
    emoji = "⚖️" if item.get('type') == 'law' else "📰"
    title = item.get('title', 'No Title').replace("<", "&lt;").replace(">", "&gt;")
    summary = item.get('summary', '').replace("<", "&lt;").replace(">", "&gt;")
    link = item.get('link', '')
    source = item.get('source', 'Unknown')
    score = item.get('score', 1)
    
    stars = "⭐" * score
    text = (
        f"{emoji} <b>{title}</b>\n"
        f"Важность: {stars}\n\n"
        f"{summary}\n\n"
        f"<i>Источник: {source}</i>"
    )
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Читать полностью 🔗", url=link)]
    ])
    
    try:
        if update.message:
            await update.message.reply_html(
                text=text,
                reply_markup=keyboard,
                disable_web_page_preview=DISABLE_PREVIEW
            )
    except Exception as e:
        logger.error(f"Error sending message: {e}")

# --- Command Handlers ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    db.add_subscriber(chat_id)
    
    msg = (
        "👋 Добро пожаловать в <b>Ulytau Inside</b> — ваш персональный агрегатор новостей Улытауской области!\n\n"
        "🚀 <b>Преимущества:</b>\n"
        "• <b>Мгновенно</b>: Узнавайте о новостях первыми благодаря автоматическим пуш-уведомлениям.\n"
        "• <b>Важно</b>: Особый приоритет законам и изменениям в Конституции РК.\n"
        "• <b>Удобно</b>: Умная сортировка и только проверенные источники.\n\n"
        "📍 <i>Вы автоматически подписаны на уведомления.</i>\n\n"
        "🤖 <b>Команды:</b>\n"
        "• /latest — Свежие новости региона\n"
        "• /subscribe — Включить уведомления\n"
        "• /unsubscribe — Выключить уведомления\n"
        "• /status — Проверить работу системы\n"
        "• /help — Помощь"
    )
    await update.message.reply_html(msg)

async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if db.add_subscriber(chat_id):
        await update.message.reply_text("✅ Вы подписаны на уведомления о свежих новостях!")
    else:
        await update.message.reply_text("ℹ️ Вы уже подписаны.")

async def unsubscribe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if db.remove_subscriber(chat_id):
        await update.message.reply_text("🔕 Уведомления отключены. Вы всегда можете подписаться снова через /subscribe.")
    else:
        await update.message.reply_text("ℹ️ Вы не были подписаны.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    commands = (
        "/latest - Последние новости\n"
        "/subscribe - Включить пуш-уведомления\n"
        "/unsubscribe - Выключить пуш-уведомления\n"
        "/week - Дайджест за неделю\n"
        "/status - Диагностика API"
    )
    await update.message.reply_text(f"📋 *Доступные команды:*\n\n{commands}", parse_mode=ParseMode.MARKDOWN)

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔄 Проверяю API...", parse_mode=ParseMode.MARKDOWN)
    
    def api_health():
        r = requests.get(f"{API_URL}/health", timeout=10)
        r.raise_for_status()
        return r.json() if "application/json" in r.headers.get("content-type","") else r.text

    try:
        # User requested logic
        payload = await asyncio.to_thread(api_health)
        
        # If payload is dict (expected)
        if isinstance(payload, dict):
             sub_count = len(db.get_subscribers())
             msg = (
                f"✅ *API STATUS*\n"
                f"Service: `{payload.get('service', 'OK')}`\n"
                f"Version: `{payload.get('version', '?')}`\n"
                f"Подписчиков: `{sub_count}`"
            )
        else:
            # Fallback if raw text
             msg = f"✅ *API STATUS*\nResponse: `{str(payload)[:200]}`"

        await update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        await update.message.reply_text(f"❌ *API Error*:\nError: `{e}`", parse_mode=ParseMode.MARKDOWN)

async def week(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generates a weekly digest."""
    await update.message.reply_text("📅 Готовлю дайджест за неделю...")
    
    try:
        # Fetch plenty of news to ensure we cover the week
        items = fetch_news(100)
        if not items:
            await update.message.reply_text("📭 За эту неделю новостей не найдено.")
            return

        # 1. Date Range Filter (Last 7 days)
        # Note: API usually returns sorted by importance/date, but strict check is good.
        # We accept naive dates assuming API returns UTC or similar.
        now = datetime.now()
        week_ago = now - timedelta(days=7)
        
        digest_items = []
        for item in items:
            # We don't have raw date object here easily unless we parse string again 
            # or trust the API order. API returns 'processed_news' which has string date.
            # Let's trust the API returned 'fresh' news (logic in rss_parser ensures 7 days).
            # So we take all items.
            digest_items.append(item)

        if not digest_items:
             await update.message.reply_text("📭 За эту неделю новостей не найдено.")
             return

        # 2. Sort by Score (Desc)
        digest_items.sort(key=lambda x: x.get('score', 0), reverse=True)

        # 3. Categorize
        top_events = []
        laws = []
        
        # Take Top 5 High Score items for "Top Events"
        # Take All "Law" items (max 5)
        
        for item in digest_items:
            # If Law/Constitution -> Add to laws
            if item.get('type') in ['law', 'constitution']:
                if len(laws) < 5:
                    laws.append(item)
            else:
                # Regular news
                if item.get('score', 0) >= 4 and len(top_events) < 5:
                    top_events.append(item)
        
        # If no high score news, take just top 3 regular
        if not top_events and not laws:
            top_events = digest_items[:3]

        # 4. Format Message
        start_date = week_ago.strftime("%d.%m")
        end_date = now.strftime("%d.%m")
        
        msg_lines = [f"📅 <b>Главное за неделю ({start_date} - {end_date})</b>\n"]
        
        if top_events:
            msg_lines.append("🏆 <b>Топ событий:</b>")
            for i, item in enumerate(top_events, 1):
                title = item.get('title', 'No Title').replace("<", "&lt;").replace(">", "&gt;")
                link = item.get('link', '')
                msg_lines.append(f"{i}. <a href='{link}'>{title}</a>")
            msg_lines.append("") # Spacer

        if laws:
            msg_lines.append("⚖️ <b>Законы и решения:</b>")
            for item in laws:
                title = item.get('title', 'No Title').replace("<", "&lt;").replace(">", "&gt;")
                link = item.get('link', '')
                msg_lines.append(f"• <a href='{link}'>{title}</a>")
            msg_lines.append("") # Spacer
            
        msg_lines.append("<i>Нажмите /latest, чтобы увидеть ленту полностью.</i>")
        
        text = "\n".join(msg_lines)
        
        await update.message.reply_html(text, disable_web_page_preview=True)

    except Exception as e:
        logger.error(f"Week digest error: {e}")
        await update.message.reply_text("⚠️ Ошибка при создании дайджеста.")

async def latest(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.first_name
    await update.message.reply_text(f"🔍 {user}, ищу свежие новости...")
    
    try:
        items = fetch_news(40)
        if items:
            page_size = 10
            to_send = items[:page_size]
            remaining = items[page_size:]
            context.user_data['remaining_news'] = remaining
            
            for item in to_send:
                await send_news_item(update, item)
            
            if remaining:
                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton(f"Показать ещё ⬇️ ({len(remaining)})", callback_data="load_more")]
                ])
                await update.message.reply_text("Хотите прочитать ещё?", reply_markup=keyboard)
        else:
            await update.message.reply_text("📭 Новостей пока нет.")
    except Exception as e:
        logger.error(f"Latest cmd error: {e}")
        await update.message.reply_text("⚠️ Ошибка при получении новостей.")

async def load_more_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    remaining = context.user_data.get('remaining_news', [])
    if not remaining:
        await query.edit_message_text("Больше новостей нет.")
        return
        
    page_size = 10
    to_send = remaining[:page_size]
    new_remaining = remaining[page_size:]
    context.user_data['remaining_news'] = new_remaining
    
    for item in to_send:
        await send_news_item_direct(query.message.chat_id, context, item)
        
    if new_remaining:
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"Показать ещё ⬇️ ({len(new_remaining)})", callback_data="load_more")]
        ])
        await query.message.reply_text("Продолжить чтение?", reply_markup=keyboard)
    else:
        await query.message.reply_text("✅ Вы просмотрели все найденные новости.")

async def send_news_item_direct(chat_id: int, context: ContextTypes.DEFAULT_TYPE, item: Dict):
    """Universal helper to send news to a specific chat_id."""
    emoji = "⚖️" if item.get('type') == 'law' else "📰"
    title = item.get('title', 'No Title').replace("<", "&lt;").replace(">", "&gt;")
    summary = item.get('summary', '').replace("<", "&lt;").replace(">", "&gt;")
    link = item.get('link', '')
    source = item.get('source', 'Unknown')
    score = item.get('score', 1)
    stars = "⭐" * score
    
    text = (
        f"{emoji} <b>{title}</b>\n"
        f"Важность: {stars}\n\n"
        f"{summary}\n\n"
        f"<i>Источник: {source}</i>"
    )
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Читать полностью 🔗", url=link)]
    ])
    
    try:
        await context.bot.send_message(
            chat_id=chat_id,
            text=text,
            parse_mode=ParseMode.HTML,
            reply_markup=keyboard,
            disable_web_page_preview=DISABLE_PREVIEW
        )
    except Exception as e:
        logger.error(f"Error sending direct message to {chat_id}: {e}")

# --- Smart Notifications Job ---

async def monitor_news_job(context: ContextTypes.DEFAULT_TYPE):
    """ Background job to push new articles to subscribers. """
    logger.info("Smart Monitor: Checking for fresh news...")
    items = fetch_news(50)
    if not items:
        return

    subscribers = db.get_subscribers()
    if not subscribers:
        return

    count = 0
    MAX_PER_CHECK = 3 # Anti-spam: limit news items per burst
    
    for item in reversed(items): # Process oldest to newest so they appear in order
        if count >= MAX_PER_CHECK:
            # Mark remaining as seen to not spam later, or just wait?
            # Better: stop and wait for next check to send more, or skip.
            # For "first to know", we shouldn't skip, but we slow down.
            break

        link = item.get('link')
        if not link or db.is_seen(link):
            continue
        
        # New article found! Notify all subscribers
        for chat_id in subscribers:
            await send_news_item_direct(chat_id, context, item)
            await asyncio.sleep(0.1) # Brief pause to avoid flood
            
        db.add_seen(link)
        count += 1
        
    if count > 0:
        logger.info(f"Smart Monitor: Sent {count} new articles to {len(subscribers)} subscribers.")

async def run_scheduler_fallback(application, interval_sec):
    """Fallback loop if JobQueue is missing."""
    logger.info("Starting Fallback Scheduler Loop...")
    
    # Wait a bit before first run
    await asyncio.sleep(10)
    
    while True:
        try:
            # Create a mock context if needed, or just pass application.
            # monitor_news_job expects 'context' with 'bot'. 
            # In PTB v20+, Context is complex, but we can try to mimic it or refactor monitor_news_job.
            # Actually, context.bot is the main requirement.
            
            # Simple wrapper class to mimic Context
            class MockContext:
                def __init__(self, app):
                    self.bot = app.bot
                    self.job = None
                    self.application = app
                    self.user_data = {}
            
            mock_ctx = MockContext(application)
            
            await monitor_news_job(mock_ctx)
            
        except Exception as e:
            logger.error(f"Fallback Scheduler Error: {e}")
        
        await asyncio.sleep(interval_sec)

# --- Main ---

async def main():
    if not BOT_TOKEN:
        logger.error("❌ BOT_TOKEN не установлен!")
        return

    # Check for JobQueue dependency
    job_queue_available = True
    try:
        from telegram.ext import JobQueue
    except ImportError:
        job_queue_available = False

    logger.info(f"🤖 Запуск бота... Подписчиков в базе: {len(db.get_subscribers())}")
    
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("subscribe", subscribe))
    application.add_handler(CommandHandler("unsubscribe", unsubscribe))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("latest", latest))
    application.add_handler(CommandHandler("week", week))
    application.add_handler(CommandHandler("status", status))
    application.add_handler(CallbackQueryHandler(load_more_callback, pattern="^load_more$"))
    
    # Background Job (Interval: every X minutes)
    job_queue = application.job_queue
    interval_sec = POST_INTERVAL_MIN * 60
    
    if job_queue:
        logger.info(f"✅ JobQueue доступен. Запускаем периодическую задачу (интервал {interval_sec}с).")
        job_queue.run_repeating(monitor_news_job, interval=interval_sec, first=10)
    else:
        logger.error("⚠️ JobQueue НЕ доступен! Установите 'python-telegram-bot[job-queue]'.")
        logger.info(f"🔄 Включаю Fallback: asyncio loop scheduler (интервал {interval_sec}с).")
        # Start fallback task
        asyncio.create_task(run_scheduler_fallback(application, interval_sec))
    
    # Run
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    
    logger.info("Бот запущен и мониторит новости.")
    
    try:
        while True:
            await asyncio.sleep(3600)
    except (KeyboardInterrupt, SystemExit, asyncio.CancelledError):
        await application.stop()
        await application.shutdown()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
