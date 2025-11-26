import os
import logging
from collections import defaultdict
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from profanity_filter import ProfanityFilter

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuration
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
THRESHOLD = float(os.getenv("PROFANITY_THRESHOLD", 0.8))
MODEL_PATH = os.getenv("MODEL_PATH", "Anvesh18/zeroshot-profanity-filter")

# Initialize Profanity Filter
print("Initializing Profanity Filter... This might take a moment.")
pf = ProfanityFilter(model_path=MODEL_PATH, threshold=THRESHOLD)
print("Profanity Filter initialized.")

# Track user strikes
# Format: {user_id: strike_count}
user_strikes = defaultdict(int)
MAX_STRIKES = 3

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle incoming text messages.
    Check for profanity, censor if necessary, and manage strikes.
    """
    if not update.message or not update.message.text:
        return

    user = update.message.from_user
    text = update.message.text
    chat_id = update.message.chat_id
    
    # Check for profanity
    result = pf.is_profane(text)
    
    if result["is_profane"]:
        # Increment strikes
        user_strikes[user.id] += 1
        current_strikes = user_strikes[user.id]
        
        logger.info(f"Profanity detected from user {user.id} ({user.first_name}). Strike {current_strikes}/{MAX_STRIKES}. Text: {text}")
        
        # Delete the profane message
        try:
            await update.message.delete()
        except Exception as e:
            logger.error(f"Failed to delete message: {e}")
            # If we can't delete, we might not have permissions, but we continue logic
        
        # Check if user should be kicked
        if current_strikes >= MAX_STRIKES:
            try:
                await context.bot.ban_chat_member(chat_id, user.id)
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=f"🚫 User {user.first_name} has been kicked for repeated profanity."
                )
                # Reset strikes after kicking (optional, depending on if they can rejoin)
                del user_strikes[user.id]
            except Exception as e:
                logger.error(f"Failed to kick user: {e}")
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=f"⚠️ User {user.first_name} reached {MAX_STRIKES} strikes but I couldn't kick them. Please check my admin permissions."
                )
        else:
            # Warn the user
            censored_text = pf.censor_text(text)
            warning_msg = (
                f"⚠️ {user.mention_html()}, your message was removed due to profanity.\n"
                f"Strike {current_strikes}/{MAX_STRIKES}.\n"
                f"Censored content: {censored_text}"
            )
            await context.bot.send_message(
                chat_id=chat_id,
                text=warning_msg,
                parse_mode='HTML'
            )

if __name__ == '__main__':
    if not TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN not found in environment variables.")
        print("Please create a .env file with your bot token.")
        exit(1)

    application = ApplicationBuilder().token(TOKEN).build()
    
    # Add handler for text messages
    # filters.TEXT & (~filters.COMMAND) ensures we don't catch commands as regular text if we had any
    echo_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message)
    application.add_handler(echo_handler)
    
    print("Bot is running...")
    application.run_polling()
