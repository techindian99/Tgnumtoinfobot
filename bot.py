import requests
import json
import time


import os
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
EXTERNAL_API_URL = "https://rtf-api-server.onrender.com/api?types=num&key=demo2&spell=8815695989"

BASE_URL = "https://api.telegram.org/bot" + BOT_TOKEN


def send_message(chat_id, text, reply_markup=None):
    url = BASE_URL + "/sendMessage"

    data = {
        "chat_id": chat_id,
        "text": text
    }

    if reply_markup is not None:
        data["reply_markup"] = json.dumps(reply_markup)

    try:
        requests.post(url, data=data, timeout=15)
    except requests.RequestException:
        pass


def get_updates(offset=None):
    url = BASE_URL + "/getUpdates"

    params = {
        "timeout": 30
    }

    if offset is not None:
        params["offset"] = offset

    try:
        response = requests.get(url, params=params, timeout=35)
        response.raise_for_status()
        return response.json()
    except (requests.RequestException, ValueError):
        return None


def phone_lookup(phone_number):
    if EXTERNAL_API_URL == "https://rtf-api-server.onrender.com/api?types=num&key=demo2&spell=8815695989":
        return {
            "status": "error",
            "message": "External API URL is not configured."
        }

    try:
        response = requests.get(
            EXTERNAL_API_URL,
            params={"phone": phone_number},
            timeout=15
        )

        response.raise_for_status()

        return response.json()

    except requests.RequestException as error:
        return {
            "status": "error",
            "message": "External API request failed.",
            "details": str(error)
        }

    except ValueError:
        return {
            "status": "error",
            "message": "External API did not return valid JSON."
        }


def main():
    if not BOT_TOKEN:
    print("ERROR: Please add your Telegram BOT_TOKEN.")
        return

    keyboard = {
        "keyboard": [
            [
                {
                    "text": "📱 Phone Lookup"
                }
            ]
        ],
        "resize_keyboard": True,
        "one_time_keyboard": False
    }

    offset = None

    print("Bot started...")

    while True:
        updates = get_updates(offset)

        if updates is None:
            time.sleep(3)
            continue

        if not updates.get("ok"):
            time.sleep(3)
            continue

        for update in updates.get("result", []):
            offset = update["update_id"] + 1

            message = update.get("message")

            if not message:
                continue

            chat = message.get("chat")

            if not chat:
                continue

            chat_id = chat.get("id")
            text = message.get("text", "").strip()

            # /start command
            if text == "/start":
                welcome = (
                    "👋 Welcome!\n\n"
                    "Choose an option from the keyboard below."
                )

                send_message(
                    chat_id,
                    welcome,
                    keyboard
                )

            # Phone Lookup button
            elif text == "📱 Phone Lookup":
                send_message(
                    chat_id,
                    "📞 Send 10 digit mobile number:"
                )

            # 10-digit number
            elif text.isdigit() and len(text) == 10:
                send_message(
                    chat_id,
                    "⏳ Processing..."
                )

                result = phone_lookup(text)

                formatted_json = json.dumps(
                    result,
                    indent=2,
                    ensure_ascii=False
                )

                # Telegram HTML message
                output = "<pre>" + formatted_json + "</pre>"

                send_message(
                    chat_id,
                    output
                )

            # Invalid input
            else:
                error_message = (
                    "❌ Invalid input.\n\n"
                    "Please send a valid 10-digit numeric mobile number."
                )

                send_message(
                    chat_id,
                    error_message
                )


if __name__ == "__main__":
    main()
