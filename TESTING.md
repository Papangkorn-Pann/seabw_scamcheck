# 🧪 SCAMCHECK Testing Guide

This guide helps you test SCAMCHECK without setting up a real Telegram bot.

---

## ✅ Unit Testing the Detector

### Test the Core Detection Logic

Create `test_detector.py` in the `backend/` folder:

```python
"""Test SCAMCHECK detector without Telegram."""
import os
import sys
from transformers import pipeline

# Load model
print("Loading SCAMCHECK model...")
classifier = pipeline(
    "text-classification",
    model="./scam_detector_bert_final",
    device=-1  # Use CPU
)

# Test messages
test_messages = [
    "Congratulations! You've won 1 million baht! Click here: bit.ly/freemoney",
    "Hi, this is your bank. We need to verify your account. Please reply with your password.",
    "Your package is ready for delivery. Track here: tracking.example.com",
    "This is an official message from the government. You owe taxes. Send money now!",
    "Hi Mom, I'm running late. See you at 6pm.",
    "Urgent! Your account has suspicious activity. Confirm your identity immediately.",
]

print("\n" + "="*60)
print("Testing SCAMCHECK Detector")
print("="*60 + "\n")

LABEL_NAMES = {
    0: "General",
    1: "Official",
    2: "Scam",
    3: "Unknown",
    4: "Verification Call",
}

EMOJI_MAP = {
    0: "✅",
    1: "✅",
    2: "🚨",
    3: "❓",
    4: "📞",
}

for i, message in enumerate(test_messages, 1):
    result = classifier(message[:512])
    prediction = result[0]
    
    label_id = int(prediction['label'].split('_')[1])
    confidence = prediction['score']
    label_name = LABEL_NAMES.get(label_id, "Unknown")
    emoji = EMOJI_MAP.get(label_id, "❓")
    
    print(f"Test {i}:")
    print(f"Message: {message[:50]}...")
    print(f"{emoji} Verdict: {label_name} ({confidence:.1%})")
    print()
```

### Run the Test

```bash
cd backend
python test_detector.py
```

Expected output:
```
Test 1:
Message: Congratulations! You've won 1 million baht!...
🚨 Verdict: Scam (98%)

Test 2:
Message: Hi, this is your bank. We need to verify...
🚨 Verdict: Scam (95%)
...
```

---

## 🗄️ Database Testing

### Test Cache Functionality

Create `test_database.py` in the `backend/` folder:

```python
"""Test SCAMCHECK database caching."""
import sys
sys.path.insert(0, '.')
from main import hash_message, check_cache, save_to_cache, get_cache_stats

print("Testing SCAMCHECK Database Caching\n")

# Test message
test_msg = "You've won 1 million baht! Click here: bit.ly/free"
msg_hash = hash_message(test_msg)

print(f"1. Testing message hashing:")
print(f"   Original: {test_msg}")
print(f"   Hash: {msg_hash[:16]}...")

# Save to cache
print(f"\n2. Saving to cache...")
save_to_cache(test_msg, msg_hash, 2, "Scam", 0.98)

# Check cache
print(f"\n3. Checking cache (should be found):")
result = check_cache(msg_hash)
if result:
    print(f"   ✅ Found in cache!")
    print(f"   Label: {result['label']}")
    print(f"   Confidence: {result['confidence']:.1%}")
    print(f"   Report count: {result['report_count']}")
else:
    print(f"   ❌ Not found in cache")

# Test duplicate
print(f"\n4. Testing duplicate report:")
save_to_cache(test_msg, msg_hash, 2, "Scam", 0.98)
result = check_cache(msg_hash)
print(f"   Report count: {result['report_count']} (should be 2)")

# Stats
print(f"\n5. Database stats:")
stats = get_cache_stats()
print(f"   Unique scams: {stats['total_unique']}")
print(f"   Total reports: {stats['total_reports']}")

print(f"\n✅ Database testing complete!")
```

### Run the Test

```bash
cd backend
python test_database.py
```

---

## 🤖 Manual Bot Testing (Without Telegram)

### Test Bot Logic

Create `test_bot_logic.py` in the `backend/` folder:

```python
"""Test bot response logic without Telegram."""
import sys
sys.path.insert(0, '.')
from transformers import pipeline

classifier = pipeline(
    "text-classification",
    model="./scam_detector_bert_final",
    device=-1
)

LABEL_NAMES = {
    0: "General",
    1: "Official", 
    2: "Scam",
    3: "Unknown",
    4: "Verification Call",
}

EMOJI_MAP = {
    0: "✅",
    1: "✅",
    2: "🚨",
    3: "❓",
    4: "📞",
}

def analyze_message(user_message):
    """Simulate bot analysis (without caching)."""
    if not user_message or len(user_message.strip()) < 3:
        return "⚠️ Please send me a message to check."
    
    result = classifier(user_message[:512])
    prediction = result[0]
    
    label_id = int(prediction['label'].split('_')[1])
    confidence = prediction['score']
    
    is_scam = label_id == 2
    emoji = EMOJI_MAP.get(label_id, "❓")
    label_name = LABEL_NAMES.get(label_id, "Unknown")
    
    response = f"""
{emoji} **Analysis Result:**

**VERDICT:** {'🚨 SCAM' if is_scam else '✅ SAFE' if label_id in [0, 1, 4] else '⚠️ SUSPICIOUS'}

**Type:** {label_name}
**Confidence:** {confidence:.1%}

**What to do:**
"""
    
    if is_scam:
        response += """
1. ❌ Do NOT click any links
2. ❌ Do NOT reply to the message
3. 🚨 Report this message to the platform
"""
    else:
        response += "✅ This message appears to be safe."
    
    return response

# Test messages
print("="*60)
print("Bot Logic Testing")
print("="*60)

test_cases = [
    "Congratulations! You've won 1 million baht!",
    "Hi, how are you?",
    "Your bank account needs verification. Click here.",
    "",  # Test short message
]

for msg in test_cases:
    print(f"\nUser: {msg if msg else '(empty message)'}")
    print(analyze_message(msg))
```

### Run the Test

```bash
cd backend
python test_bot_logic.py
```

---

## 🧪 Telegram Bot Testing (Real)

### Step 1: Create a Test Bot

1. Go to Telegram and search for [@BotFather](https://t.me/botfather)
2. Send `/newbot`
3. Follow the prompts to create a test bot
4. Copy the bot token

### Step 2: Run the Bot

```bash
export TELEGRAM_BOT_TOKEN="your-test-bot-token"
python main.py
```

### Step 3: Test with Your Bot

1. Search for your bot on Telegram (name you gave it)
2. Send `/start` to see welcome message
3. Send `/help` for safety tips
4. Send `/stats` to see database stats
5. Send various test messages:
   - "You've won 1 million baht! Click: bit.ly/free" → Should be 🚨 SCAM
   - "Hi, how are you?" → Should be ✅ SAFE
   - "Your bank needs to verify your account" → Should be 🚨 SCAM

---

## ✅ Automated Testing Script

Create `run_all_tests.py`:

```bash
#!/bin/bash
cd backend

echo "Running SCAMCHECK Tests..."
echo "=========================="

echo -e "\n1. Testing Detector..."
python test_detector.py

echo -e "\n2. Testing Database..."
python test_database.py

echo -e "\n3. Testing Bot Logic..."
python test_bot_logic.py

echo -e "\n=========================="
echo "✅ All tests complete!"
```

Run:
```bash
chmod +x run_all_tests.py
./run_all_tests.py
```

---

## 📊 Testing Checklist

- [ ] Model loads without errors
- [ ] Detector identifies known scams correctly
- [ ] Database caching works (duplicate messages counted)
- [ ] Bot responds to `/start`, `/help`, `/stats` commands
- [ ] Bot analyzes test messages correctly
- [ ] Short messages rejected (<3 chars)
- [ ] Long messages truncated to 512 chars before analysis
- [ ] Error handling works (bad messages, missing model)

---

## 🐛 Debugging Tips

### Enable Verbose Logging

Add to `main.py`:
```python
logging.basicConfig(level=logging.DEBUG)  # More verbose output
```

### Check Model Loading

```python
from transformers import pipeline
classifier = pipeline("text-classification", model="./scam_detector_bert_final")
print(classifier("test message"))  # Quick test
```

### Inspect Database

```bash
sqlite3 ../database/scam_reports.db
SELECT * FROM scam_reports;
```

---

## 📞 Support

If tests fail:
1. Check that dependencies are installed: `pip list`
2. Verify model file exists: `ls -la scam_detector_bert_final/`
3. Check database directory exists: `ls -la ../database/`
4. Review error logs in console output
