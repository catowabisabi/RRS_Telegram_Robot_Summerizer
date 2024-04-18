import os
from dotenv import load_dotenv
from pymongo import MongoClient
from datetime import datetime, timedelta
from class_db_handler import DatabaseHandler
from class_state import state, state_manager
import json
import asyncio

from class_logging import logger
from class_news_summarizer import NewsSummarizer
from class_telegram_bot import TelegramBot

# 載入.env檔案
load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

class PureDataCollector:
    def __init__(self):
        self.database_handler = DatabaseHandler()
        self.news_summerizer= NewsSummarizer(openai_api_key=OPENAI_API_KEY)
        self.single_news_count_for_summarization= state_manager.get_state('Single_News_Count_For_summarization')
        #self.telegram_bot = TelegramBot(bot_token=bot_token, chat_id=chat_id, openai_api_key=openai_api_key)
    

    async def process_save_new_article(self, source, link, title, article_content):
        catagory = state_manager.get_state("News_Catagory")
        last_article_id = self.database_handler.save_to_database(source, link, title, article_content, catagory)
        
        if last_article_id and last_article_id % state['Single_News_Count_For_summarization'] == 0 and not last_article_id == 0:
            try:
                articles_str = await self.collect_articles_segment(last_article_id)

                # sent gpt - try to get json result
                state_manager.set_state('Model', "gpt-3.5-turbo")
                json_result_gpt3    = self.news_summerizer.get_gpt_json_response(articles_str)
                if json_result_gpt3:

                #state_manager.set_state('Model', "gpt-4-1106-preview")
                #json_result_gpt4    = self.news_summerizer.get_gpt_json_response(articles_str)

                #logger.info(f"\n\nGPT3 :\n{json_result_gpt3}\n\nGPT4 :\n{json_result_gpt4}")
                #print (f"\n\nGPT3 :\n{json_result_gpt3}\n\nGPT4 :\n{json_result_gpt4}")
                # save gpt ans

                #new_ans_id, ans = self.database_handler.save_gpt_ans_to_database(json_result_gpt3)
                    new_ans_id, tg_msg  = self.database_handler.save_gpt_ans_to_database2(json_result_gpt3)
                    return new_ans_id, tg_msg
                else:
                    return None, None

                # send tg
                #last_send_time = await self.telegram_bot.send_news_to_telegram_async(tg_msg = tg_msg, last_send_time= last_send_time, second_msg = en_content, send_full_content = send_full_content)
                # sleep 1
            except Exception as e:
                logger.critical(f"try process_save_new_article ... ERROR: {e}")
                print(f"try process_save_new_article ... ERROR: {e}")
                return None,None
        else:
            return None,None

    
    async def collect_articles_segment(self, last_article_id):
        end_id = last_article_id # 最近id
        news_counter = state_manager.get_state("Single_News_Count_For_summarization")

        if last_article_id % news_counter == 0 :# 最新id係倍數
            start_id = max(1, last_article_id - news_counter + 1) #如果最新id係26, 咁start id就係1, 如果係52, start_id 就係27
            articles = list(self.database_handler.collection.find({"article_id": {"$gte": start_id, "$lte": end_id}})) # 拎晒咁多返黎
        else:
            logger.info("沒有到達用戶所定位的新聞倍數...")
            return
        
        if articles:
            articles_json = json.dumps(articles, default=str)
            # 將文章轉換成字串格式
            articles_str = ""

            for article in articles:
                article_str = f"文章 ID: {article['article_id']}\n"
                article_str += f"來源: {article['source']}\n"
                article_str += f"URL: {article['url']}\n"
                article_str += f"題目: {article['title']}\n"
                article_str += f"新聞內文: {article['article_content']}\n"
                article_str += f"分類: {article['catagory']}\n"
                article_str += f"時間: {article['created_at']}\n\n"
                articles_str += article_str

            # 在這裡將articles_str發送到ChatGPT進行處理
            logger.info(f"已將文章ID從{start_id}到{end_id}的文章發送到ChatGPT。字數為: {len(articles_str)}")
            logger.info("Articles String (頭300字):")
            logger.info(articles_str[0:300])
            
            return articles_str
            # 在這裡實現將文章發送到ChatGPT的邏輯
            #logging.info(f"已將{len(articles)}篇文章發送到ChatGPT")
        else:
            logger.info (f"沒有找到文章")
            return None
    

#pd = PureDataCollector()
#pd.send_articles_to_chatgpt(26) 

