# 🤖 Homework Status Telegram Bot  

This is my Telegram bot that automatically checks the status of my homework submissions on the **Practicum API** and notifies me via Telegram.  
I also added logging for all key events and errors, so I can track both successful updates and issues.  

---

### ✨ What it does  

- Polls the **Practicum API** every 10 minutes to check the homework status.  
- Sends me a notification in Telegram whenever the status of a homework is updated.  
- Logs all operations, including errors and debug information.  
- Notifies me in Telegram about critical errors (when possible).  

---

### 🛠️ How I built it  

- **`main()`** — the core logic of the bot:  
  1. Make an API request.  
  2. Validate the response.  
  3. If there are updates, parse the status and send a Telegram notification.  
  4. Wait for the next cycle.  

- **`check_tokens()`** — verifies that all required environment variables are available (`PRACTICUM_TOKEN`, `TELEGRAM_TOKEN`, `TELEGRAM_CHAT_ID`). If any are missing, the bot stops with a **CRITICAL** log.  

- **`get_api_answer(timestamp)`** — sends a request to the Practicum API with a timestamp and returns a Python dictionary with the JSON response.  

- **`check_response(response)`** — validates the API response format against the documentation.  

- **`parse_status(homework)`** — extracts the homework status and returns a human-readable message from `HOMEWORK_VERDICTS`.  

- **`send_message(bot, message)`** — sends a message to a Telegram chat. Logs success (**DEBUG**) or failure (**ERROR**).  

---

### Logging  

I added logging to track all important events with the following format:  

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

requests — for API calls
python-telegram-bot (or telebot) — for Telegram integration
logging — for error and debug logging
dotenv — for managing environment variables
