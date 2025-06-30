# Telegram Sheet Monitor Bot

This Python bot monitors specific cells in a public Google Sheet and sends Telegram alerts when product statuses change (e.g., `AVAILABLE`, `LOW`, `OUT OF STOCK`).

## ✨ Features

- 📄 Monitors a live Google Sheet via CSV export (no Google API required)
- 🔔 Sends alerts to Telegram on **status changes**
- 💬 Emoji-based status display (🟢 AVAILABLE, 🟡 LOW, 🔴 OUT OF STOCK)
- 🕒 Automatically runs every 5 minutes using **GitHub Actions**
- 🔐 Telegram token and chat ID are managed securely via GitHub Secrets

## 🚀 Setup & Usage (Local)

1. **Clone the repo**
   ```bash
   git clone https://github.com/IndominusD/telegram-sheet-monitor.git
   cd telegram-sheet-monitor
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set your secrets (locally for testing)**
   - Add the following environment variables:
     ```
     TELEGRAM_BOT_TOKEN=your-token
     TELEGRAM_CHAT_ID=your-chat-id
     CSV_EXPORT_URL=your_sheet_url
     ```

4. **Run the script**
   ```bash
   python monitor.py
   ```

## 🤖 Automated Deployment via GitHub Actions

This project runs **automatically every 5 minutes** with GitHub Actions!

### 🔧 Setup:

1. Fork or clone this repo

2. Add GitHub Secrets:
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`
   - `CSV_EXPORT_URL`

   Go to: `Settings → Secrets and variables → Actions → New repository secret`

3. Ensure this workflow file exists:
   - `.github/workflows/monitor.yml`

4. That's it! GitHub Actions will handle the rest.

## 📝 License

MIT
