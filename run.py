from dotenv import load_dotenv
import os
import nltk
from threading import Thread, Event
import asyncio
import logging

from class_news_fetcher import NewsFetcher
from class_telegram_bot import TelegramBot
from class_logging import AppLogger
# 初始化日誌配置
applogger = AppLogger()
applogger.setup_logging()

# 現在你可以在主程序中使用日誌了
logging.info('應用程序啟動')

from my_var import rss_feed_crypto, rss_feed_stock


# 首次使用需要下载punkt
nltk.download('punkt')
from class_state import state, state_manager

load_dotenv()


rss_feed = rss_feed_stock

if rss_feed == rss_feed_crypto:
    TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
    state_manager.set_state("News_Catagory", "Crypto")
else:
    TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN_STOCK')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY_STOCK')
    TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID_STOCK')
    state_manager.set_state("News_Catagory", "Stock")

# 我地會使用呢一個json
    
os.makedirs("market_news", exist_ok=True)

new_fetcher = NewsFetcher(rss_feeds=rss_feed, 
                          bot_token=TELEGRAM_TOKEN, 
                          chat_id=TELEGRAM_CHAT_ID,
                          openai_api_key=OPENAI_API_KEY, turn_on_bot_reference=False)

#new_fetcher.fetch_news()
async def run_fetcher():
    await new_fetcher.fetch_news()

telegram_bot = TelegramBot(TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, OPENAI_API_KEY)
telegram_bot.set_callback(run_fetcher)
asyncio.run(telegram_bot.main())

# 改為database
# 可改msg
# 分開問問題model










