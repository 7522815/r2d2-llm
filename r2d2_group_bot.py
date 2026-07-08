"""
R2D2 Group Bot — автоматически принимает заявки и отвечает бипами.

Работает как systemd-сервис на VPS.
Запросы шлёт на локальный R2D2 API (localhost:6969).
"""

import logging
import os
import re
import random
import json
import urllib.request
import urllib.error

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ChatJoinRequestHandler,
    filters,
)

# ─── Config ───────────────────────────────────────────────────────────
BOT_TOKEN = os.environ.get("R2D2_BOT_TOKEN", "ВАШ_ТОКЕН_ОТ_BOTFATHER")
R2D2_API_URL = os.environ.get("R2D2_API_URL", "http://localhost:6969/v1/chat/completions")
ALLOWED_GROUP_ID = int(os.environ.get("R2D2_GROUP_ID", "-1004319246642"))

# ─── Logging ──────────────────────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


# ─── R2D2 API Client ─────────────────────────────────────────────────

BEEPS_RU = ["Пиу-пиу!", "Бип-буп!", "Пиу!", "Биип-биип!", "Пуу-пуу!",
            "Бип!", "Пиу-пиу-пиу!", "Бууп-бип!", "Би-и-ип!"]
BEEPS_EN = ["Beep boop!", "Bee-bee-boo!", "Boop!", "Beep!",
            "Bwip-bwop!", "Bleep-bloop!", "Bzzzt!", "Wooop!"]

def has_cyrillic(text: str) -> bool:
    return bool(re.search(r"[а-яёА-ЯЁ]", text))


def get_r2d2_beep(message: str) -> str:
    """Get a beep from the R2D2 API, with fallback to local generation."""
    payload = json.dumps({
        "model": "r2d2-1b",
        "messages": [{"role": "user", "content": message}],
        "stream": False,
    }).encode("utf-8")

    req = urllib.request.Request(
        R2D2_API_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            beep = data["choices"][0]["message"]["content"]
            if beep:
                return beep
    except Exception:
        pass

    # Fallback: random beep
    is_ru = has_cyrillic(message)
    pool = BEEPS_RU if is_ru else BEEPS_EN
    return random.choice(pool)


# ─── Handlers ─────────────────────────────────────────────────────────

async def start(update: Update, context):
    """Handle /start command."""
    await update.message.reply_text(get_r2d2_beep("start"))


async def handle_message(update: Update, context):
    """Reply to any message with an R2D2 beep."""
    if not update.message or not update.message.text:
        return

    text = update.message.text
    beep = get_r2d2_beep(text)
    await update.message.reply_text(beep)


async def handle_join_request(update: Update, context):
    """Auto-accept all join requests."""
    if update.chat_join_request:
        chat = update.chat_join_request.chat
        user = update.chat_join_request.from_user
        try:
            await update.chat_join_request.approve()
            logger.info(f"✅ Approved join request: {user.full_name} (ID: {user.id}) to {chat.title}")
        except Exception as e:
            logger.error(f"❌ Failed to approve: {e}")


async def handle_new_members(update: Update, context):
    """Welcome new members with a beep."""
    if not update.message or not update.message.new_chat_members:
        return
    for member in update.message.new_chat_members:
        if member.is_bot:
            continue
        welcome = get_r2d2_beep(f"welcome {member.full_name}")
        await update.message.reply_text(f"🤖 {welcome}")


def main():
    """Start the bot."""
    if BOT_TOKEN == "ВАШ_ТОКЕН_ОТ_BOTFATHER":
        logger.error("❌ BOT_TOKEN not set! Set R2D2_BOT_TOKEN environment variable.")
        print("ERROR: Set R2D2_BOT_TOKEN env var with your bot token from @BotFather")
        return

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(ChatJoinRequestHandler(handle_join_request))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, handle_new_members))

    logger.info("🤖 R2D2 Group Bot starting...")
    print("🤖 R2D2 Group Bot is running! Press Ctrl+C to stop.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
