import requests
from bs4 import BeautifulSoup
from telegram import Bot
import os
import re
import json

TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
SHEET_VIEW_URL = os.getenv('SHEET_VIEW_URL')  # This should be the view-only URL (with edit#gid=...)

cells_to_monitor = {
    'C57': 'Strawberry Kiwi',
    'C59': 'Tie Guan Yin',
    'C60': 'Watermelon',
}

status_emojis = {
    'AVAILABLE': '🟢',
    'LOW': '🟡',
    'OUT OF STOCK': '🔴'
}

status_file = 'status.json'
if os.path.exists(status_file):
    with open(status_file, 'r') as f:
        last_values = json.load(f)
else:
    last_values = {cell: None for cell in cells_to_monitor}

bot = Bot(token=TELEGRAM_BOT_TOKEN)

def fetch_html_cells():
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    response = requests.get(SHEET_VIEW_URL, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    cell_data = {}
    for cell in cells_to_monitor:
        match = soup.find(text=re.compile(f'{cell}', re.IGNORECASE))
        if match:
            cell_data[cell] = match.strip().upper()
        else:
            cell_data[cell] = None
    return cell_data

def check_changes():
    global last_values
    try:
        current_data = fetch_html_cells()
        updates = []

        for cell, product_name in cells_to_monitor.items():
            current_value = current_data[cell].split()[0] if current_data[cell] else ''
            emoji = status_emojis.get(current_value, '❔')

            if current_value != last_values.get(cell):
                updates.append(
                    f"🔔 *Status change for {product_name}*
"
                    f"Previous: `{last_values.get(cell)}`
"
                    f"Now: {emoji} *{current_value}*"
                )
                last_values[cell] = current_value

        if updates:
            bot.send_message(chat_id=TELEGRAM_CHAT_ID, text="\n\n".join(updates), parse_mode='Markdown')

        with open(status_file, 'w') as f:
            json.dump(last_values, f, indent=2)

    except Exception as e:
        print(f"Error scraping sheet: {e}")

if __name__ == "__main__":
    from time import strftime
    print(f"📡 Checking for status changes at {strftime('%Y-%m-%d %H:%M:%S')}")
    check_changes()
