
from class_newsfetcher_investing_com import GetRRSNews
import requests
import feedparser
from class_parse_entries import ParseEntries
from class_logging import logger


class NewsFetcherHelper:
    def __init__(self) -> None:
        self.parse_entries = ParseEntries()
        self.headers  = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    

    def get_all_news(self, url):
        if "cointelegraph" in url:
            headers = self.headers
            url = "https://cn.cointelegraph.com/rss"
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                feed_data = feedparser.parse(response.content)
            else:
                logger.debug(response)
                feed_data = None
        else:   
            feed_data = feedparser.parse(url)
        return feed_data
    
    def get_readable_news(self, source, url):
        if "investing.com" in url:
            grn = GetRRSNews()
            all_news = grn.get_all_rss_news(url)
            readable_news = grn.get_all_readable_news(all_news)
        else:
            feed_data      = self.get_all_news(url)#json in a list
            readable_news  = self.align_data(url=url, source=source, feed_data=feed_data)#json in a list 
        return readable_news

    
    def align_data(self, url, source, feed_data):  
        readable_news = None      
        if source == "Coindesk":
            readable_news = self.parse_entries.parse_coindesk_rss_entries(feed_data.entries)
        elif source == "AMBCrypto":
            readable_news = self.parse_entries.parse_ambcrypto_rss_entries(feed_data.entries)
        elif source == "Bitcoin.com":
            readable_news =self.parse_entries.parse_bitcoin_com_rss_entries(feed_data.entries)
        elif source == "CNN Money":
            readable_news = self.parse_entries.parse_cnn_money_rss_entries(feed_data.entries)
        elif "cointelegraph" in url:
            logger.debug ("cointelegraph in url1")
            readable_news = self.parse_entries.parse_cointelegraph_rss_entries(feed_data.entries)
        else:
            logger.info (f"正在提取 {source} 的新聞...")
            readable_news = self.parse_entries.parse_general_rss_entries(feed_data.entries, source)

        return readable_news
    
    def get_title_summary_link(self, news):
        title = news.get('標題', 'No Title')
        summary = news.get('摘要', '')
        news_link = news.get('連結', '') # 拎到條link
        return title, summary, news_link
    
    def check_not_duplicated_news(self, title, existing_news, link):
        return (title not in [n['英文標題'] for n in existing_news]) and (link not in [n['連結'] for n in existing_news]) and (title not in [n['中文標題'] for n in existing_news])


