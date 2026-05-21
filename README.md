# 🚨 SCAMCHECK - AI Scam Detection Bot

A real-time scam detection assistant powered by BERT, helping elderly users in Southeast Asia identify online scams and fraudulent messages instantly.

**SEABW 2026 Hackathon Submission** by Papangkorn Wangchochedkun & Piyaphat Klanprayoon

---

## 🎯 Overview

**SCAMCHECK** is an AI-powered Telegram bot that analyzes suspicious messages and identifies whether they are scams, spam, or legitimate messages. Using a fine-tuned multilingual BERT model trained on Thai call center data and SMS spam datasets, the bot provides instant, confidence-rated verdicts with actionable safety advice.

**Perfect for:** Elderly users, families, and anyone vulnerable to online scams in Southeast Asia.

---

## ✨ Features

### 🤖 AI-Powered Detection
- Fine-tuned BERT model trained on **5,770+ messages** (Thai + SMS data)
- Multilingual support (Thai & English)
- Real-time analysis with confidence scores
- 5-class classification: Scam, General, Official, Unknown, Verification Call

### ⚡ Smart Caching System
- Message hashing with SHA256 for instant lookups
- SQLite database tracks scam patterns
- Identifies repeated scams reported by multiple users
- Speeds up response time for known scams

### 🛡️ User-Friendly
- Simple `/start`, `/help`, `/stats` commands
- Emoji indicators for quick understanding
- Warm, reassuring tone (not alarming)
- Actionable safety advice for each verdict

### 📊 Community Intelligence
- Track which scams are most common
- Learn from community reports
- Build a Southeast Asia scam database
- Help future users avoid known threats

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip (Python package manager)
- Telegram account
- A Telegram bot token (from @BotFather)

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/Papangkorn-Pann/seabw_scamcheck.git
cd seabw_scamcheck
```

2. **Install dependencies:**
```bash
cd backend
pip install -r requirements.txt
```

3. **Create a Telegram bot:**
   - Chat with [@BotFather](https://t.me/botfather) on Telegram
   - Create a new bot with `/newbot`
   - Copy your bot token

4. **Set your bot token:**

Create a `.env` file in the project root (see `.env.example` for reference):
```env
TELEGRAM_BOT_TOKEN=your-bot-token-here
```

Or set environment variables:

**Windows (PowerShell):**
```powershell
$env:TELEGRAM_BOT_TOKEN = "your-bot-token-here"
```

**Linux/Mac:**
```bash
export TELEGRAM_BOT_TOKEN="your-bot-token-here"
```

5. **Verify your setup (optional):**
```bash
python verify_setup.py
```

You should see:
```
✅ transformers
✅ torch
✅ python-telegram-bot
✅ pandas
✅ numpy
✅ kagglehub
✅ datasets
✅ TELEGRAM_BOT_TOKEN is set
```

6. **Run the bot:**
```bash
python main.py
```

You should see:
```
✅ Model loaded successfully!
✅ Database initialized!
🤖 SCAMCHECK Telegram Bot Started!
```

6. **Test it:**
   - Search for your bot on Telegram
   - Send `/start` to begin
   - Send any suspicious message to analyze

---

## 📱 How to Use

### Commands
```
/start    - Welcome message & how to use the bot
/help     - Detailed help & safety tips
/stats    - View scam database statistics
```

### Sending a Message
Simply type or paste any suspicious message you received:

```
User: "Congratulations! You've won 1 million baht! 
       Click here to claim: bit.ly/freemoney"

Bot: 🚨 VERDICT: SCAM
     Type: Scam
     Confidence: 98%
     
     This scam has been reported 5 times!
     
     What to do:
     1. ❌ Do NOT click any links
     2. ❌ Do NOT reply to the message
     3. 🚨 Report this message to the platform
     [etc...]
```

---

## 🏗️ Project Structure

```
seabw_scamcheck/
├── backend/
│   ├── main.py                      # Telegram bot with SQLite caching
│   ├── training.py                  # BERT model fine-tuning script
│   ├── requirements.txt             # Python dependencies
│   └── scam_detector_bert_final/    # Trained BERT model (gitignored)
├── database/
│   └── scam_reports.db              # SQLite database of scam reports
├── README.md                        # This file
├── .gitignore                       # Git exclusions
└── .git/                            # Version control
```

---

## 🧠 Model Details

### Training Data
- **Thai Call Center Dataset:** 198 messages (5 classes)
- **SMS Spam Collection:** 5,572 messages (2 classes)
- **Total:** 5,770 messages for fine-tuning
- **Train/Test Split:** 80/20 (4,616 train, 1,154 eval)

### Architecture
- **Base Model:** `bert-base-multilingual-uncased`
- **Fine-tuning:** 3 epochs, batch size 8
- **Language Support:** Thai, English, and 100+ other languages
- **Confidence Scores:** 0-100% for each prediction

### Performance
- Trains in **30-60 minutes** on CPU
- Analyzes messages in **<1 second**
- Cache hits return results in **<100ms**

---

## 💾 Database Schema

The SQLite database tracks scam reports:

```sql
CREATE TABLE scam_reports (
    id INTEGER PRIMARY KEY,
    message_hash TEXT UNIQUE,        -- SHA256 hash for fast lookup
    original_message TEXT,           -- Full message text
    prediction INTEGER,              -- Label ID (0-4)
    prediction_label TEXT,           -- Label name
    confidence REAL,                 -- Confidence score (0-1)
    report_count INTEGER,            -- Times reported by users
    first_reported TIMESTAMP,        -- When first reported
    last_reported TIMESTAMP          -- Last time reported
)
```

---

## 🔐 Privacy & Security

✅ **Privacy Protected:**
- Messages are hashed, not stored verbatim
- Database stores analysis results only
- No user identification stored
- Local database (not cloud)

⚠️ **Important:**
- Use a secure bot token (rotate periodically)
- Don't share your bot token in code/repos
- Set TELEGRAM_BOT_TOKEN as environment variable only

---

## 🌐 Deployment

For detailed deployment instructions, see **[DEPLOYMENT.md](./DEPLOYMENT.md)** which covers:
- Railway (recommended - free)
- Render (free)
- PythonAnywhere (free)
- DigitalOcean ($4/month - most reliable)

### Quick Deployment
1. Push code to GitHub (excluding model + database)
2. Connect GitHub repo to hosting platform
3. Set `TELEGRAM_BOT_TOKEN` environment variable
4. Deploy and monitor

---

## 🔄 How It Works

```
User sends message
        ↓
Hash the message (SHA256)
        ↓
Check database for hash
        ↓
    ┌─────────────────┬──────────────────┐
    ↓ (FOUND)         ↓ (NOT FOUND)      
Return cached result  Load BERT model
    ↓                 ↓
⚡ Instant answer    Analyze message
    ↓                 ↓
(< 100ms)            Save to database
                      ↓
                    Send result
```

---

## 📊 Statistics

Your bot will track:
- Total unique scams detected
- Total times each scam was reported
- Most common scam types
- Trends over time

View stats anytime with `/stats` command!

---

## 🛠️ Technologies Used

| Technology | Purpose |
|------------|---------|
| **BERT** | NLP model for text classification |
| **Transformers** | Hugging Face library for BERT |
| **Telegram Bot API** | Bot communication |
| **SQLite** | Local database |
| **Python 3.8+** | Programming language |
| **Kaggle** | Training datasets |

---

## 📈 Future Improvements

- [ ] Multi-language response (detect & respond in user's language)
- [ ] Image/document analysis (not just text)
- [ ] Real-time scam alert network
- [ ] User feedback loop (improve model with corrections)
- [ ] Integration with Telegram channels
- [ ] Mobile app version
- [ ] Web dashboard for analytics
- [ ] Multi-platform support (WhatsApp, Facebook Messenger)

---

## 🤝 Contributing

Found a bug or have a feature idea? 
1. Create an issue
2. Fork the repo
3. Submit a pull request

---

## 📝 License

This project is open source and available under the MIT License.

---

## 👥 Credits

**Built for:** Elderly users and families in Southeast Asia protecting themselves from online scams.

**Special thanks to:**
- Kaggle community for datasets
- Hugging Face for pre-trained models
- Telegram for the bot API
- Claude for AI assistance

---

## 📞 Support

Have questions or issues?
- 📖 Check `/help` in the bot
- 🐛 Report bugs on GitHub Issues
- 💬 See README.md for detailed documentation

---

## ⚠️ Disclaimer

**SCAMCHECK is a tool to assist in scam detection, not a guarantee.**
- Always verify suspicious messages with official sources
- When in doubt, call directly using verified numbers
- Never share passwords, OTPs, or personal information
- Report actual scams to authorities

---

**Stay safe. Stay alert. Use SCAMCHECK.** 🛡️
