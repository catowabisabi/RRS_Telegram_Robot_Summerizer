import os
from dotenv import load_dotenv
from pymongo import MongoClient
from datetime import datetime, timedelta
import asyncio
from class_logging import logger
from class_key_map import KeyMap
from class_handle_calculate_sentiment import SentimentCalculator

# 載入.env檔案
load_dotenv()



class DatabaseHandler:
    def __init__(self, database_name = "cato_trading", db = "trading_news"):
        # 從.env檔案中獲取MongoDB的連接字串
        self.connection_string = os.getenv("MONGODB_CONNECTION_STRING")
        
        # 建立MongoDB客戶端
        self.client = MongoClient(self.connection_string)
        
        # 選擇要使用的資料庫和集合
        self.db = self.client[f"{database_name}"]
        self.collection = self.db[f"{db}"]
        
    def existing_article(self, url, title):
        existing_article = self.collection.find_one({"url": url}) or self.collection.find_one({"title": title})
        if existing_article:
            logger.info("\n文章已存在於資料庫中,不需要重複儲存\n\n")
            return True
        return False

    #保存用
    def save_to_database(self, source="", url="", title="", article_content="", catagory=""):
        if self.existing_article(url, title): return False

        try:
            last_article_id = self.get_last_article_id()
            new_article_id = last_article_id + 1
            document = {
                "article_id": new_article_id,
                "source": source,
                "url": url,
                "title": title,
                "article_content": article_content,
                "catagory": catagory, 
                "created_at": datetime.now()
            }
            
            # 將文件插入到集合中
            response = self.collection.insert_one(document)
            logger.info("文章已成功保存到資料庫")
            return last_article_id
        except Exception as e:
            logger.error(f"DatabaseHandler.save_to_database: 文章保存到資料庫失敗...Error: ({e})")
            return None
        
    def save_gpt_ans_to_database(self, data):
        collection_gpt = self.db[f"gpt_ans"]
        investment,  symbols, sentiment, links, analysis = KeyMap.translated_gpt_json(data)

        last_ans = collection_gpt.find_one(sort=[("article_id", -1)])
        if last_ans and "article_id" in last_ans:
            last_ans_id =  last_ans["article_id"]
        else:
            last_ans_id =  0

        try:
            new_ans_id = last_ans_id + 1
            ans={}
            # 将数据插入到集合中
            ans["id"] = new_ans_id
            ans["investment"] = investment
            ans["symbols"] = symbols
            ans["sentiment"] = sentiment
            ans["links"] = links
            ans["analysis"] = analysis
            ans["created_at"] = datetime.now()
            response = self.collection.insert_one(ans)
            
            logger.info("GPT回應已成功保存到資料庫")
            print ("GPT回應已成功保存到資料庫")
            return new_ans_id, ans
        except Exception as e:
            logger.error(f"DatabaseHandler.save_gpt_ans_to_database: GPT回應保存到資料庫失敗...Error: ({e})")
            print (f"DatabaseHandler.save_gpt_ans_to_database: GPT回應保存到資料庫失敗...Error: ({e})")
            return None, None
    
    def save_gpt_ans_to_database2(self, data):
        collection_gpt = self.db[f"gpt_ans"]
        #investment,  symbols, sentiment, links, analysis = KeyMap.translated_gpt_json(data)

        last_ans = collection_gpt.find_one(sort=[("ans_id", -1)])
        if last_ans and "ans_id" in last_ans:
            last_ans_id =  last_ans["ans_id"]
        else:
            last_ans_id =  0

        try:
            new_ans_id = last_ans_id + 1
            ans={}
            # 将数据插入到集合中
            ans["ans_id"] = new_ans_id
            ans["gpt"] = data
            ans["created_at"] = datetime.now()
            response = collection_gpt.insert_one(ans)

            # 格式化文本消息
            investments = data.get("Investment", [])
            links = data.get("Links", [])
            analysis = data.get("Analysis", "")

            logger.info("GPT回應已成功保存到資料庫")
            print ("GPT回應已成功保存到資料庫")
            
            unique_investments = {}
            tg_msg = "投資標的:\n"
            for inv in investments:
                asset = inv.get("Asset", "N/A")
                symbol = inv.get("Symbol", "N/A")
                sentiment = inv.get("Sentiment", "N/A")
                
                if symbol not in unique_investments:
                    unique_investments[symbol] = inv
                    tg_msg += f"資產: {asset}, 代碼: {symbol}, 情緒: {sentiment}\n"
                    
                    if symbol and sentiment:
                        if not symbol == "N/A" and not  sentiment == "N/A":
                            sc = SentimentCalculator()
                            sc.put_sentiment(symbol, sentiment)

            tg_msg += f"\n\n分析:\n{analysis}\n\n"
            
            tg_msg += "\n鏈接:\n"
            for link in links:
                tg_msg += f"{link}\n"
            
            sc = SentimentCalculator()
            sentiment_msg = sc.get_daily_sentiment()
            tg_msg += f"\n\n\n{sentiment_msg}"
        
            
            
            return new_ans_id, tg_msg
        except Exception as e:
            logger.error(f"DatabaseHandler.save_gpt_ans_to_database: GPT回應保存到資料庫失敗...Error: ({e})")
            print (f"DatabaseHandler.save_gpt_ans_to_database: GPT回應保存到資料庫失敗...Error: ({e})")
            return None, None
        
        
    def get_article_count(self):
        # 獲取資料庫中的文章數量
        return self.collection.count_documents({})
    
    def get_last_article_id(self):
        last_article = self.collection.find_one(sort=[("article_id", -1)])
        if last_article and "article_id" in last_article:
            return last_article["article_id"]
        else:
            return 0
    
    def remove_old_articles(self, day_ago = 45):
        # 計算45天前的日期
        
        forty_five_days_ago = datetime.now() - timedelta(days=day_ago)
        
        # 刪除45天以前的文章
        result = self.collection.delete_many({"created_at": {"$lt": forty_five_days_ago}})
        print(f"已刪除 {result.deleted_count} 篇({day_ago})天以前的文章")
        logger.info(f"已刪除 {result.deleted_count} 篇({day_ago})天以前的文章")
        
    async def daily_cleanup(self):
        while True:
            now = datetime.now()
            if now.hour == 12 and now.minute == 0:
                # 每天中午12點進行清理
                await self.remove_old_articles()
            await asyncio.sleep(60)  # 每分鐘檢查一次時間



def main():
    dbhandler = DatabaseHandler()

    #number = 4
    #for number in range(1, 10):
    #    dbhandler.save_to_database( title = f"title {number}", source = f"test source {number}", url = f"testurl {number}", article_content = f"testarticle {number}", catagory="Crypto")
   
    #dbhandler.remove_old_articles(0)
    #dbhandler.get_last_article_id()
    return None

if __name__ == "__main__":
    main()