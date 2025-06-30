import pandas as pd
import requests
from io import StringIO
from telegram import Bot
import os

# Telegram setup
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# CSV export link for public sheet
CSV_URL = os.getenv('CSV_EXPORT_URL')

# Cells to monitor: cell -> (row, col, product name)
cells_to_monitor = {
    'C57': (56, 2, 'Strawberry Kiwi'),
    'C59': (58, 2, 'Tie Guan Yin'),
    'C60': (59, 2, 'Watermelon'),
}

# Emojis per status
status_emojis = {
    'AVAILABLE': '🟢',
    'LOW': '🟡',
    'OUT OF STOCK': '🔴'
}

# Track last known values
last_values = {cell: None for cell in cells_to_monitor}
bot = Bot(token=TELEGRAM_BOT_TOKEN)

def check_sheet():
    global last_values
    try:
        response = requests.get(CSV_URL)
        data = pd.read_csv(StringIO(response.text), header=None)

        updates = []

        for cell, (row, col, product_name) in cells_to_monitor.items():
            raw_value = str(data.iloc[row, col]).strip().upper()
            current_value = raw_value.split()[0] if raw_value else ''
            emoji = status_emojis.get(current_value, '❔')

            if current_value != last_values[cell]:
                updates.append(
                    f"🔔 *Status change for {product_name}*\n"
                    f"Previous: `{last_values[cell]}`\n"
                    f"Now: {emoji} *{current_value}*"
                )
                last_values[cell] = current_value

        if updates:
            bot.send_message(chat_id=TELEGRAM_CHAT_ID, text="\n\n".join(updates), parse_mode='Markdown')

    except Exception as e:
        print(f"Error fetching sheet: {e}")

if __name__ == "__main__":
    print("📡 Checking for status changes...")
    check_sheet()
