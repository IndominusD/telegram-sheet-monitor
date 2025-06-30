import asyncio
import json
import os
from telegram import Bot
from playwright.async_api import async_playwright

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
SHEET_VIEW_URL = os.getenv("SHEET_VIEW_URL")

cells_to_monitor = {
    "C57": "Strawberry Kiwi",
    "C59": "Tie Guan Yin",
    "C60": "Watermelon",
}

status_emojis = {
    "AVAILABLE": "🟢",
    "LOW": "🟡",
    "OUT": "🔴",
    "OUT OF STOCK": "🔴"
}

status_file = "status.json"
if os.path.exists(status_file):
    with open(status_file, "r") as f:
        last_values = json.load(f)
else:
    last_values = {cell: None for cell in cells_to_monitor}

bot = Bot(token=TELEGRAM_BOT_TOKEN)

async def fetch_statuses():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            await page.goto(SHEET_VIEW_URL, wait_until="domcontentloaded", timeout=60000)
            await page.wait_for_timeout(5000)  # Let sheet fully render after DOM load
        except Exception as e:
            print(f"❌ Failed to load sheet: {e}")
            await browser.close()
            return {cell: None for cell in cells_to_monitor}


        content = await page.content()

        found = {}
        for cell, product in cells_to_monitor.items():
            if product.upper() in content.upper():
                snippet = content.upper().split(product.upper(), 1)[-1][:80]
                for status in status_emojis:
                    if status in snippet:
                        found[cell] = f"{status}"
                        break
                else:
                    found[cell] = None
            else:
                found[cell] = None

        await browser.close()
        return found

async def check_changes():
    global last_values
    print("📡 Launching headless browser...")
    try:
        current_data = await fetch_statuses()

        print("📋 Current visible statuses:")
        for cell, raw in current_data.items():
            print(f"  {cell} ({cells_to_monitor[cell]}): {raw if raw else '❌ Not found'}")

        updates = []

        for cell, product_name in cells_to_monitor.items():
            current_value = current_data[cell]
            emoji = status_emojis.get(current_value, "❔")

            if last_values.get(cell) is None or current_value != last_values.get(cell):
                updates.append(
                    f"🔔 *Status change for {product_name}*\n"
                    f"Previous: `{last_values.get(cell)}`\n"
                    f"Now: {emoji} *{current_value or 'UNKNOWN'}*"
                )
                last_values[cell] = current_value

        if updates:
            bot.send_message(chat_id=TELEGRAM_CHAT_ID, text="\n\n".join(updates), parse_mode="Markdown")

        with open(status_file, "w") as f:
            json.dump(last_values, f, indent=2)

    except Exception as e:
        print(f"❌ Error in check_changes: {e}")

if __name__ == "__main__":
    from time import strftime
    print(f"📡 Checking for status changes at {strftime('%Y-%m-%d %H:%M:%S')}")
    asyncio.run(check_changes())
