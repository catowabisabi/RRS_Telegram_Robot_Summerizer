import csv
import os
import requests
import feedparser
import time
import json
from datetime import datetime, timedelta
from opencc import OpenCC  
from class_logging import logger

from class_article_extractor import ArticleExtractor
from class_translator import EnglishToChineseTranslator
from class_CSV_news_handler import CSVNewsHandler
from class_telegram_bot import TelegramBot
from class_newsfetcher_investing_com import GetRRSNews
from class_display_info import InfoDisplay
#from class_news_fetcher_helper import NewsFetcherHelper
from class_create_content import ContentCreator
from class_newsfetcher_investing_com import GetRRSNews
from class_db_handler import DatabaseHandler
from class_data_collector import PureDataCollector


import asyncio

from class_state import state, state_manager, StateManager


class NewsFetcher:
    def __init__(self, rss_feeds, bot_token, chat_id, openai_api_key, turn_on_bot_reference):
        self.rss_feeds_urls = rss_feeds
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.article_extractor = ArticleExtractor()
        self.translator = EnglishToChineseTranslator()
        self.csv_news_handler = CSVNewsHandler()
        self.telegram_bot = TelegramBot(bot_token=bot_token, chat_id=chat_id, openai_api_key=openai_api_key)
        self.display_info = InfoDisplay()
        self.state_manager = StateManager()
        self.get_RRS_news = GetRRSNews()
        self.content_creator = ContentCreator(openai_api_key=openai_api_key)
        self.dbh = DatabaseHandler()
        self.pdc = PureDataCollector()
        self.base_dir = "market_news"
        self.headers  = {
                            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
                        }
    
    async def fetch_news(self):
        last_send_time = 0
        logger.info ("新聞機器人開始提取新開...\n")
        while True:
            new_news_count = 0
            for source, url in self.rss_feeds_urls.items():
                if not state_manager.bot_is_on():
                    logger.info ("機器人關閉...")
                    state_manager.set_state("Fetching News", False)
                    break
                try:
                    readable_news = self.get_RRS_news.get_readable_news( url)
                    existing_news = self.csv_news_handler.get_existing_news()#json in a list

                    tasks = []
                    #每一個news
                    for news in readable_news:
                        bot_is_on = state['Bot is ON']
                        if not bot_is_on:
                            break
                        tasks.append(asyncio.ensure_future(self.process_news(news, url, existing_news, source, last_send_time))) #<------------------------------------------------------
                    
                    
                    if tasks:
                        results = await asyncio.gather(*tasks)
                        if results:
                            existing_news = results[-1][0] if results else existing_news
                            new_news_count += sum([count for _, count, _ in results])
                            last_send_time = results[-1][2] if results else last_send_time

                except Exception as e:
                    logger.error(f"處理源'{source}'時發生錯誤: {str(e)}，URL: {url}")  # 修改了這行

            self.display_info.show_news_court(new_news_count)

            await asyncio.sleep(60)





############################################

#######################################################
    
    async def process_news(self, news, url, existing_news, source, last_send_time):
        if not state_manager.bot_is_on():
            state_manager.set_state("Fetching News", False)
            return existing_news, 0, last_send_time

        title, summary, link = self.get_RRS_news.get_title_summary_link(news)
        summarizer = state_manager.get_state("Save_Only")

        if summarizer:
            #existing_news=[]
            #last_send_time=""

            if not self.dbh.existing_article(url=link, title=title):
                logger.info(f'這是新的文章... : {title}')
                try:
                    article_content = await self.article_extractor.fetch_article_async(news.get('連結', ''))
                    new_ans_id, tg_msg = await self.pdc.process_save_new_article(source, link, title, article_content)
                    if tg_msg:
                        model = state['Model']
                        tg_msg = f"資料來源: {source}\n\nAI分析 ({model}):\n\n{tg_msg}\n\n時間: {datetime.now()}"
                    #tg_msg = f"資料來源: {source}\n\nAI分析 ({model}):\n\n目標: {ans["Investment"]}\n\nSymbols: {ans["symbols"]}\n\n情緒: {ans["sentiment"]}\n\n連結: {ans["links"]}\n\n分析: {ans["analysis"]}\n\n時間: {datetime.now()}"
                        
                        last_send_time = await self.telegram_bot.send_news_to_telegram_async(tg_msg = tg_msg, last_send_time= last_send_time, second_msg = "", send_full_content = False)

                    await asyncio.sleep(1)
                    return existing_news, 1, last_send_time
                except Exception as e:
                    logger.error(f"summarizer...Error:{e}")
            else:
                logger.info(f"文章已存在: {title}")
                print(f"文章已存在: {title}")
                await asyncio.sleep(3)
                return existing_news, 0, last_send_time

        else:   
            if self.get_RRS_news.check_not_duplicated_news(title, existing_news, link) and state_manager.bot_is_on():
                
                logger.info(f'這是新的文章... : {title}')
                try:
                    article_content = await self.article_extractor.fetch_article_async(news.get('連結', ''))
                    time.sleep (1)
                    if article_content:
                        cn_title, cn_summary, cn_content, en_title, en_summary,  en_content, analysis, cn_suggestion, model, tg_msg, send_full_content = await self.content_creator.create_content(url, source, news, title, summary, article_content)
                        last_send_time = await self.telegram_bot.send_news_to_telegram_async(tg_msg = tg_msg, last_send_time= last_send_time, second_msg = en_content, send_full_content = send_full_content)
                        existing_news = self.csv_news_handler.save_csv(news, title, cn_title, cn_summary, cn_content, en_title, en_summary,  en_content, analysis, cn_suggestion, existing_news)
                        await asyncio.sleep(1)
                        return existing_news, 1, last_send_time
                    else:
                        logger.info(f"無法獲取文章內容: {news.get('連結', '')}")
                except Exception as e:
                    logger.error(f" #拎content Error fetching article content: {e}")
            else:
                logger.info(f"文章已存在: {title}")
                print(f"文章已存在: {title}")
                await asyncio.sleep(3)
                return existing_news, 0, last_send_time
    

    
