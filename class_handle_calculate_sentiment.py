from datetime import datetime
from pymongo import MongoClient
import os
from class_state import state
from class_telegram_bot import TG

collection_name ="daily_sentiment_stock"
""" print (collection_name)
if state["News_Catagory"] == "Crypto":
    collection_name = "daily_sentiment"
print (collection_name) """



class SentimentCalculator:
    def __init__(self, db_name="cato_trading", collection_name=collection_name):
        self.client = MongoClient(os.getenv("MONGODB_CONNECTION_STRING"))
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    def put_sentiment(self, symbol, sentiment):
        today = datetime.now().strftime("%Y-%m-%d")
        doc = self.collection.find_one({"date": today})

        if doc:
            sentiment_list = doc["sentiment"]
            found = False
            for item in sentiment_list:
                if symbol in item:
                    item[symbol] += 1 if sentiment == "正面" else -1 if sentiment == "負面" else 0
                    found = True
                    break
            if not found:
                sentiment_list.append({symbol: 1 if sentiment == "正面" else -1 if sentiment == "負面" else 0})
            self.collection.update_one({"date": today}, {"$set": {"sentiment": sentiment_list}})
        else:
            sentiment_list = [{symbol: 1 if sentiment == "正面" else -1 if sentiment == "負面" else 0}]
            self.collection.insert_one({"date": today, "sentiment": sentiment_list})

    def get_daily_sentiment(self):
        today = datetime.now().strftime("%Y-%m-%d")
        doc = self.collection.find_one({"date": today})
        if doc:
            sentiment_list = doc["sentiment"]
            sentiment_items = [(symbol, score) for item in sentiment_list for symbol, score in item.items()]
            sorted_items = sorted(sentiment_items, key=lambda x: x[1], reverse=True)
            tg_msg = f"日期: {today}\n\n新聞情緒:\n\n\n"
            tg_msg += "\n".join(f"{score:4d} {symbol}" for symbol, score in sorted_items)
            tg_msg += "\n\n\n\n\n\n\n\n."
            return tg_msg
        else:
            return "No sentiment data found for today."        
        

    def send_tg(self, tg_msg):
        response = TG.send(tg_msg)
        print(response)
        
""" sc = SentimentCalculator()
sc.put_sentiment('DOGE', "正面")

tg_msg = sc.get_daily_sentiment()
sc.send_tg(tg_msg) """
