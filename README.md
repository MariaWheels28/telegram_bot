# Homework Status Telegram Bot

This bot automatically checks the status of your homework submissions on the **Practicum API** and notifies you via Telegram.  
It also logs all key events and errors, helping you track both successful updates and issues.

---

## Features

- Polls the **Practicum API** every 10 minutes to check homework status.
- Sends a notification to Telegram if the status of a homework has been updated.
- Logs all operations, including errors and debug information.
- Notifies the user in Telegram about critical errors (when possible).

---

## Functions Overview

- **`main()`**  
  The core logic of the bot:  
  1. Make an API request.  
  2. Validate the response.  
  3. If there are updates — parse the status and send a Telegram notification.  
  4. Wait for the next cycle.  

- **`check_tokens()`**  
  Checks availability of required environment variables (`PRACTICUM_TOKEN`, `TELEGRAM_TOKEN`, `TELEGRAM_CHAT_ID`).  
  If any are missing, the bot stops with a **CRITICAL** log.

- **`get_api_answer(timestamp)`**  
  Sends a request to the Practicum API with a timestamp parameter.  
  Returns a Python dictionary with the parsed JSON response.

- **`check_response(response)`**  
  Validates the API response format against documentation.  
  Ensures required keys and expected types are present.

- **`parse_status(homework)`**  
  Extracts the homework status and returns a human-readable verdict from `HOMEWORK_VERDICTS`.

- **`send_message(bot, message)`**  
  Sends a message to a Telegram chat using the bot instance and the provided text.  
  Logs success (**DEBUG**) or failure (**ERROR**).

---

## Logging

The bot logs all important events with the following format:

YYYY-MM-DD HH:MM:SS,MS [LEVEL] Message

markdown
Copy code

### Examples
- `2021-10-09 15:34:45,150 [ERROR] API endpoint https://practicum.yandex.ru/api/user_api/homework_statuses/ unavailable. Response code: 404`
- `2021-10-09 16:19:13,149 [CRITICAL] Missing required environment variable: 'TELEGRAM_CHAT_ID'. Program terminated.`

### Logged Events
- Missing required environment variables (**CRITICAL**)  
- Successful Telegram message sending (**DEBUG**)  
- Message sending failure (**ERROR**)  
- API endpoint unavailable (**ERROR**)  
- Unexpected or missing keys in API response (**ERROR**)  
- Unknown homework status (**ERROR**)  
- No new homework statuses (**DEBUG**)  

Errors are not only logged but also sent to Telegram (when technically possible).  
If an error repeats in each cycle, it is logged every time but only one Telegram notification is sent.

---

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/homework-status-bot.git
   cd homework-status-bot
   
2. Create and activate a virtual environment:
  ```bash
  python3 -m venv venv
  source venv/bin/activate

3. Install dependencies:
  ```bash
  pip install -r requirements.txt

4. Create a .env file with your tokens:
  ```env
  PRACTICUM_TOKEN=your_practicum_api_token
  TELEGRAM_TOKEN=your_telegram_bot_token
  TELEGRAM_CHAT_ID=your_chat_id

5. Run the bot:
  ```bash
  python homework.py
  Technologies Used
  Python 3.x

requests — for API calls
python-telegram-bot (or telebot) — for Telegram integration
logging — for error and debug logging
dotenv — for managing environment variables
