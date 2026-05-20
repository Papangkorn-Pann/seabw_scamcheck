import os
import logging
import sqlite3
import hashlib
from datetime import datetime
from transformers import pipeline
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Database setup
DB_PATH = '../database/scam_reports.db'

def init_database():
    """Initialize SQLite database for caching scam messages."""
    # Ensure database directory exists
    db_dir = os.path.dirname(DB_PATH)
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
        print(f"✅ Created database directory: {db_dir}")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scam_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message_hash TEXT UNIQUE NOT NULL,
            original_message TEXT NOT NULL,
            prediction INTEGER NOT NULL,
            prediction_label TEXT NOT NULL,
            confidence REAL NOT NULL,
            report_count INTEGER DEFAULT 1,
            first_reported TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_reported TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Create index on message_hash for faster searching
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_message_hash ON scam_reports(message_hash)
    ''')

    conn.commit()
    conn.close()
    print("✅ Database initialized!")

def hash_message(message: str) -> str:
    """Hash a message using SHA256 for fast searching."""
    return hashlib.sha256(message.lower().strip().encode()).hexdigest()

def check_cache(message_hash: str) -> dict or None:
    """Check if message hash exists in database."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute('''
            SELECT prediction, prediction_label, confidence, report_count, original_message
            FROM scam_reports WHERE message_hash = ?
        ''', (message_hash,))

        result = cursor.fetchone()
        conn.close()

        if result:
            return {
                'prediction': result[0],
                'label': result[1],
                'confidence': result[2],
                'report_count': result[3],
                'original_message': result[4],
                'cached': True
            }
        return None
    except Exception as e:
        logger.error(f"Error checking cache: {e}")
        return None

def save_to_cache(message: str, message_hash: str, prediction: int, label: str, confidence: float):
    """Save message analysis to database."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Try to insert new record
        try:
            cursor.execute('''
                INSERT INTO scam_reports (message_hash, original_message, prediction, prediction_label, confidence)
                VALUES (?, ?, ?, ?, ?)
            ''', (message_hash, message, prediction, label, confidence))
        except sqlite3.IntegrityError:
            # If hash already exists, increment count and update last_reported
            cursor.execute('''
                UPDATE scam_reports
                SET report_count = report_count + 1, last_reported = CURRENT_TIMESTAMP
                WHERE message_hash = ?
            ''', (message_hash,))

        conn.commit()
        conn.close()
    except Exception as e:
        logger.error(f"Error saving to cache: {e}")

def get_cache_stats() -> dict:
    """Get statistics about cached messages."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute('SELECT COUNT(*) FROM scam_reports')
        total = cursor.fetchone()[0]

        cursor.execute('SELECT SUM(report_count) FROM scam_reports')
        total_reports = cursor.fetchone()[0] or 0

        conn.close()

        return {
            'total_unique': total,
            'total_reports': total_reports
        }
    except Exception as e:
        logger.error(f"Error getting cache stats: {e}")
        return {'total_unique': 0, 'total_reports': 0}

# Load the trained BERT model
print("Loading trained SCAMCHECK model...")
try:
    classifier = pipeline(
        "text-classification",
        model="./scam_detector_bert_final",
        device=-1  # Use CPU (-1), change to 0 for GPU
    )
    print("✅ Model loaded successfully!")
except Exception as e:
    print(f"❌ Error loading model: {e}")
    classifier = None

# Label mappings
LABEL_NAMES = {
    0: "General",
    1: "Official",
    2: "Scam",
    3: "Unknown",
    4: "Verification Call",
    # SMS dataset labels
    "ham": "Safe Message",
    "spam": "Spam/Scam"
}

# Emoji indicators
EMOJI_MAP = {
    0: "✅",  # General
    1: "✅",  # Official
    2: "🚨",  # Scam
    3: "❓",  # Unknown
    4: "📞",  # Verification Call
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    welcome_message = """
👋 Welcome to **SCAMCHECK** - Your Scam Detection Assistant!

I help elderly users in Southeast Asia identify online scams and fraudulent messages.

**How to use:**
1. Paste a suspicious message or message content
2. I'll analyze it and tell you if it's safe or a scam
3. I'll explain what red flags I spotted
4. I'll suggest what to do

**Simply send me any suspicious message you'd like me to check!**

🔒 Your privacy is protected - messages are only used for analysis.
    """
    await update.message.reply_text(welcome_message)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    help_text = """
**SCAMCHECK Help**

📌 **What I can detect:**
- Phone scams (impersonating banks, officials)
- SMS/Spam messages
- Phishing attempts
- Fake prize/reward schemes
- OTP/password requests
- Suspicious links

📝 **How to check a message:**
Just send me the suspicious message content and I'll analyze it!

⚠️ **Important:**
- Be careful with messages asking for:
  • Your password or PIN
  • OTP codes
  • Bank details
  • Personal ID numbers
  • Money transfers

🆘 **If you find a scam:**
1. Don't click any links
2. Don't reply to the message
3. Report it to the platform
4. Tell your bank if it involves money

📊 **Check statistics:** /stats
    """
    await update.message.reply_text(help_text)

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show database statistics."""
    stats = get_cache_stats()

    stats_text = f"""
📊 **SCAMCHECK Statistics**

🔍 **Scam Database:**
- Unique scams detected: {stats['total_unique']}
- Total times reported: {stats['total_reports']}

⚡ **Smart Caching:**
- Messages are hashed for instant lookups
- Repeated scams identified immediately
- Database grows with each report

💡 **This data helps us:**
- Identify scam trends in Southeast Asia
- Improve detection accuracy
- Protect more users
    """
    await update.message.reply_text(stats_text)

async def analyze_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Analyze a message for scams with caching."""

    user_message = update.message.text

    if not user_message or len(user_message.strip()) < 3:
        await update.message.reply_text(
            "⚠️ Please send me a message to check. It should be at least 3 characters long."
        )
        return

    if classifier is None:
        await update.message.reply_text(
            "❌ Error: The model is not loaded. Please try again later."
        )
        return

    # Show "thinking" indicator
    await update.message.chat.send_action("typing")

    try:
        # Hash the message for fast cache lookup
        message_hash = hash_message(user_message)

        # Check if message was already analyzed
        cached_result = check_cache(message_hash)

        if cached_result:
            # Use cached result
            logger.info(f"Cache hit! Message: {user_message[:50]}...")
            label_id = cached_result['prediction']
            confidence = cached_result['confidence']
            report_count = cached_result['report_count']
            is_cached = True
        else:
            # Get new prediction from model
            logger.info(f"Cache miss! Analyzing new message: {user_message[:50]}...")
            result = classifier(user_message[:512])  # Limit to 512 chars for model
            prediction = result[0]

            label_id = int(prediction['label'].split('_')[1])
            confidence = prediction['score']
            report_count = 1
            is_cached = False

            # Save to cache
            label_name = LABEL_NAMES.get(label_id, "Unknown")
            save_to_cache(user_message, message_hash, label_id, label_name, confidence)

        # Determine if it's a scam
        is_scam = label_id == 2  # Label 2 is "Scam"

        # Build response
        emoji = EMOJI_MAP.get(label_id, "❓")
        label_name = LABEL_NAMES.get(label_id, "Unknown")

        # Add cache indicator
        cache_indicator = "⚡ (Fast answer - Already checked!)" if is_cached else ""

        response = f"""
{emoji} **Analysis Result:** {cache_indicator}

**VERDICT:** {'🚨 SCAM' if is_scam else '✅ SAFE' if label_id in [0, 1, 4] else '⚠️ SUSPICIOUS'}

**Type:** {label_name}
**Confidence:** {confidence:.1%}

**This scam type has been reported {report_count} {'time' if report_count == 1 else 'times'} by other users!**

**What to do:**
"""

        if is_scam:
            response += """
1. ❌ Do NOT click any links
2. ❌ Do NOT reply to the message
3. ❌ Do NOT share any personal information
4. 📞 If it's about your bank, call your bank directly
5. 🚨 Report this message to the platform
6. 👨‍👩‍👧‍👦 Tell family members about this scam type
"""
        elif label_id == 4:  # Verification call
            response += """
1. ⚠️ Be cautious - verify caller's identity
2. 📞 Call your bank/official number directly
3. ❌ Never give OTP or passwords over phone
4. 🔍 Check with official sources first
"""
        else:
            response += "✅ This message appears to be safe. But always stay cautious!"

        await update.message.reply_text(response)

    except Exception as e:
        logger.error(f"Error analyzing message: {e}")
        await update.message.reply_text(
            f"⚠️ Error analyzing message: {str(e)}\n\nPlease try again or send a different message."
        )

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and send a telegram message to notify the developer."""
    logger.error(msg="Exception while handling an update:", exc_info=context.error)

    if isinstance(update, Update) and update.effective_message:
        await update.effective_message.reply_text(
            "❌ An error occurred. Please try again later."
        )

def main() -> None:
    """Start the bot."""
    # Initialize database
    init_database()

    # Get token from environment variable
    token = os.getenv('TELEGRAM_BOT_TOKEN')

    if not token:
        print("❌ Error: TELEGRAM_BOT_TOKEN environment variable not set!")
        print("Set it with: export TELEGRAM_BOT_TOKEN='your-token-here'")
        return

    # Create the Application
    application = Application.builder().token(token).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("stats", stats_command))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, analyze_message))

    # log all errors
    application.add_error_handler(error_handler)

    # Run the bot
    print("🤖 SCAMCHECK Telegram Bot Started!")
    print("📊 Database: scam_reports.db")
    print("Press Ctrl+C to stop")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
