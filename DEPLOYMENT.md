# 🚀 SCAMCHECK Deployment Guide

This guide covers deploying SCAMCHECK to free/low-cost cloud hosting platforms.

---

## 📋 Prerequisites

- Git installed and repository pushed to GitHub
- Telegram bot token from [@BotFather](https://t.me/botfather)
- Account on your chosen hosting platform

---

## 🔧 Option 1: Railway (Recommended - Free Tier)

### Step 1: Prepare your repository

Ensure `.gitignore` includes:
```
scam_detector_bert_final/
scam_detector_bert/
database/
*.db
```

Commit and push to GitHub.

### Step 2: Connect to Railway

1. Go to [railway.app](https://railway.app)
2. Sign in with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your `seabw_scamcheck` repository
5. Railway will auto-detect the Python project

### Step 3: Set Environment Variables

1. In Railway dashboard, go to your project
2. Click "Variables"
3. Add: `TELEGRAM_BOT_TOKEN=your-token-here`
4. Save

### Step 4: Configure Procfile

Create `Procfile` in your project root:
```
worker: cd backend && python main.py
```

### Step 5: Deploy

Railway will automatically deploy on every push to main. Check logs in the Railway dashboard.

**Cost:** Free tier includes 5GB storage and 500 execution hours/month

---

## 🔧 Option 2: Render

### Step 1: Create Background Worker

1. Go to [render.com](https://render.com)
2. Sign in with GitHub
3. Click "New +" → "Background Worker"
4. Connect your GitHub repository
5. Fill in:
   - **Name:** scamcheck-bot
   - **Runtime:** Python 3.9
   - **Build Command:** `pip install -r backend/requirements.txt`
   - **Start Command:** `cd backend && python main.py`

### Step 2: Add Environment Variables

1. Click "Environment" tab
2. Add: `TELEGRAM_BOT_TOKEN=your-token-here`
3. Save

### Step 3: Deploy

Click "Create Web Service". Render will deploy automatically.

**Cost:** Free tier (limited to one service at a time)

---

## 🔧 Option 3: PythonAnywhere

### Step 1: Create Account

1. Go to [pythonanywhere.com](https://pythonanywhere.com)
2. Create free account

### Step 2: Upload Files

1. Go to "Files" tab
2. Upload your `backend/` folder and `database/` folder

### Step 3: Create Web App

1. Go to "Web" tab
2. Click "Add a new web app"
3. Choose "Python 3.8" → "Manual configuration"

### Step 4: Set Up Python Environment

In "Consoles" tab, start a Bash console:
```bash
mkvirtualenv --python=/usr/bin/python3.8 scamcheck
pip install -r backend/requirements.txt
```

### Step 5: Configure Task

1. Go to "Tasks" tab
2. Create "Always-on" task
3. Command: `/home/yourusername/.virtualenvs/scamcheck/bin/python /home/yourusername/backend/main.py`
4. Start the task

**Cost:** Free tier with limitations

---

## 🔧 Option 4: DigitalOcean ($4/month - Most Reliable)

### Step 1: Create Droplet

1. Go to [digitalocean.com](https://digitalocean.com)
2. Create "Droplet" (Basic, 512MB RAM, $4/month)
3. Choose Ubuntu 22.04

### Step 2: SSH into Server

```bash
ssh root@your_droplet_ip
```

### Step 3: Install Dependencies

```bash
apt update && apt upgrade -y
apt install -y python3 python3-pip git
```

### Step 4: Clone Repository

```bash
git clone https://github.com/yourusername/seabw_scamcheck.git
cd seabw_scamcheck/backend
pip install -r requirements.txt
```

### Step 5: Set Environment Variable

```bash
export TELEGRAM_BOT_TOKEN="your-token-here"
```

### Step 6: Run Bot with Supervisor (Keep it Running)

Install supervisor:
```bash
apt install -y supervisor
```

Create `/etc/supervisor/conf.d/scamcheck.conf`:
```ini
[program:scamcheck]
directory=/root/seabw_scamcheck/backend
command=/usr/bin/python3 main.py
autostart=true
autorestart=true
environment=TELEGRAM_BOT_TOKEN=your-token-here
```

Start supervisor:
```bash
supervisorctl reread
supervisorctl update
supervisorctl start scamcheck
```

Check status:
```bash
supervisorctl status scamcheck
```

**Cost:** $4/month, most reliable

---

## 🔄 Comparison Table

| Platform     | Cost      | Setup   | Reliability | Recommendation                |
| ------------ | --------- | ------- | ----------- | ----------------------------- |
| Railway      | Free      | Easy    | Very Good   | **Best for quick demo**       |
| Render       | Free      | Easy    | Good        | Good for testing              |
| PythonAnywhere | Free    | Medium  | Good        | Good if you prefer web UI     |
| DigitalOcean | $4/month  | Hard    | Excellent   | **Best for production**       |

---

## 📊 Monitoring

### Check Logs

**Railway:**
```
Dashboard → Logs tab
```

**Render:**
```
Dashboard → Logs tab
```

**DigitalOcean:**
```
ssh root@droplet_ip
supervisorctl tail scamcheck
```

### Common Issues

**"Model not found"**
- The fine-tuned model isn't in the repository
- Download it locally and add to `.gitignore` during dev only
- For production, consider: fine-tuning in deployment, or loading from Hugging Face Hub

**"Database permission denied"**
- Ensure `database/` folder exists and is writable
- On cloud: use `/tmp/` or a cloud database

**"Memory exceeded"**
- Model + inference uses ~1.5GB RAM
- Minimum 2GB RAM required (Railway/Render free tiers may struggle)
- Upgrade to paid tier if needed

---

## 🔐 Security Checklist

- [ ] Bot token is in environment variables, NOT in code
- [ ] `.gitignore` excludes `.env` and sensitive files
- [ ] Repository is private or sensitive data is removed
- [ ] Database file is gitignored
- [ ] Model file is gitignored

---

## 📞 Support

- **Railway Support:** [railway.app/docs](https://railway.app/docs)
- **Render Support:** [render.com/docs](https://render.com/docs)
- **DigitalOcean:** [digitalocean.com/docs](https://digitalocean.com/docs)
