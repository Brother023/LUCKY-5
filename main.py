import os
import logging
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, ContextTypes,
    CallbackQueryHandler
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# In-memory storage (resets when bot restarts)
boards = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome! I track scores for games, sports, and challenges.\n\n"
        "• /newboard — Create a scoreboard\n"
        "• /add — Add players\n"
        "• /score — Record points\n"
        "• /scores — View standings\n"
        "• /help — Instructions"
    )

async def newboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    boards[user_id] = {"players": {}, "name": "My Board"}
    await update.message.reply_text(
        "✅ Scoreboard created!\n\n"
        "Now use /add to add players (e.g., /add Alice)"
    )

async def add_player(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in boards:
        await update.message.reply_text("❌ No scoreboard yet. Use /newboard first.")
        return

    if not context.args:
        await update.message.reply_text("Usage: /add PlayerName")
        return

    name = " ".join(context.args)
    boards[user_id]["players"][name] = 0
    await update.message.reply_text(f"✅ Added **{name}** with 0 points.", parse_mode="Markdown")

async def score(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in boards or not boards[user_id]["players"]:
        await update.message.reply_text("❌ No players yet. Use /newboard then /add.")
        return

    if len(context.args) < 2:
        await update.message.reply_text("Usage: /score PlayerName 10")
        return

    name = " ".join(context.args[:-1])
    try:
        points = int(context.args[-1])
    except ValueError:
        await update.message.reply_text("❌ Points must be a number.")
        return

    if name not in boards[user_id]["players"]:
        await update.message.reply_text(f"❌ Player '{name}' not found. Use /add {name} first.")
        return

    boards[user_id]["players"][name] += points
    total = boards[user_id]["players"][name]
    await update.message.reply_text(f"✅ **{name}** now has **{total}** points.", parse_mode="Markdown")

async def view_scores(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in boards or not boards[user_id]["players"]:
        await update.message.reply_text("❌ No scoreboard found. Use /newboard then /add.")
        return

    players = boards[user_id]["players"]
    sorted_players = sorted(players.items(), key=lambda x: x[1], reverse=True)

    text = "🏆 **Scoreboard**\n\n"
    for i, (name, pts) in enumerate(sorted_players, 1):
        text += f"{i}. {name}: **{pts}** pts\n"

    await update.message.reply_text(text, parse_mode="Markdown")

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in boards or not boards[user_id]["players"]:
        await update.message.reply_text("❌ No scores to reset.")
        return

    for name in boards[user_id]["players"]:
        boards[user_id]["players"][name] = 0
    await update.message.reply_text("🔄 All scores reset to 0.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "**How to use the Score Bot:**\n\n"
        "1️⃣ /newboard — Start a fresh scoreboard\n"
        "2️⃣ /add Alice — Add a player\n"
        "3️⃣ /score Alice 5 — Give Alice 5 points\n"
        "4️⃣ /scores — See the ranking\n"
        "5️⃣ /reset — Clear all points\n\n"
        "Use negative points to subtract: `/score Alice -3`",
        parse_mode="Markdown"
    )

def main():
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not token:
        raise ValueError("TELEGRAM_BOT_TOKEN environment variable not set")

    app = Application.builder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("newboard", newboard))
    app.add_handler(CommandHandler("add", add_player))
    app.add_handler(CommandHandler("score", score))
    app.add_handler(CommandHandler("scores", view_scores))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(CommandHandler("help", help_command))

    app.run_polling()

if __name__ == "__main__":
    main()
