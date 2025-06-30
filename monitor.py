import pandas as pd
import requests
from io import StringIO
from telegram import Bot
import os
import json

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
CSV_URL = os.getenv('CSV_EXPORT_URL')

cells_to_monitor = {
    'C57': (56, 2, 'Strawberry Kiwi'),
    'C59': (58, 2, 'Tie Guan Yin'),
    'C60': (59, 2, 'Watermelon'),
}

status_emojis = {
    'AVAILABLE': '🟢',
    'LOW': '🟡',
    'OUT OF STOCK': '🔴'
}

# Load last known values from status.json
status_file = 'status.json'
if os.path.exists(status_file):
    with open(status_file, 'r') as f:
        last_values = json.load(f)
else:
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

            if current_value != last_values.get(cell):
                updates.append(
                    f"🔔 *Status change for {product_name}*\n"
                    f"Previous: `{last_values.get(cell)}`\n"
                    f"Now: {emoji} *{current_value}*"
                )
                last_values[cell] = current_value

        # ✅ Always save the status file (even if no updates)
        with open(status_file, 'w') as f:
            json.dump(last_values, f, indent=2)

        # Only send alert if there were changes
        if updates:
            bot.send_message(chat_id=TELEGRAM_CHAT_ID, text="\n\n".join(updates), parse_mode='Markdown')

    except Exception as e:
        print(f"Error fetching sheet: {e}")

if __name__ == "__main__":
    from time import strftime
    print(f"📡 Checking for status changes at {strftime('%Y-%m-%d %H:%M:%S')}")
    check_sheet()
