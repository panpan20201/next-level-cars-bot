import os
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

BOT_TOKEN = os.getenv('BOT_TOKEN')
CHANNEL_ID = os.getenv('CHANNEL_ID')
SOCKS5_PROXY = os.getenv('SOCKS5_PROXY')

# Личный chat_id администратора для оповещений о сбоях (не канал).
# Узнать свой chat_id можно у бота @userinfobot.
ADMIN_CHAT_ID = os.getenv('ADMIN_CHAT_ID')