
from typing import List, Dict
import requests
import feedparser
from bs4 import BeautifulSoup
import html2text
from class_logging import logger

class GetRRSNews:

    def __init__(self) -> None:
        self.headers  = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        self.html_parser = html2text.HTML2Text()
        self.html_parser.ignore_links = True  # 忽略摘要中的連結
        self.html_parser.ignore_images = True  # 忽略摘要中的圖片

    def get_all_rss_news(self, rrs_url) -> List[Dict]:
        if "cointelegraph" in rrs_url:
            headers = self.headers
            url = "https://cn.cointelegraph.com/rss"
            response = requests.get(url, headers=headers)
            feed_data = feedparser.parse(response.content)
        else:
            feed_data = feedparser.parse(rrs_url)

        self.news = feed_data.entries
        #logging.info(f"\n\n第一條新聞的資料:\n{self.news[0]}\n\n")
        return self.news


    def get_all_rrs_news_with_headers(self, rrs_url):
        response = requests.get(rrs_url, headers=self.headers)
        if response.status_code == 200:
            feed_data = feedparser.parse(response.content)
        else:
            logger.debug(response)
            feed_data = None
        return feed_data
    
    def clean_html_summary(self, summary):
        """將HTML摘要轉換為純文字，並去除多餘的空格和換行符。"""
        text_summary = self.html_parser.handle(summary)
        return text_summary.replace("\n", " ").strip()
    
    def get_all_readable_news(self, all_news, title_tab = "title", summary_tab = "summary", author_tab = "author", published_tab = "published", link_tab = "link"):
        all_readable_news = []
        for news in all_news:
            single_readable_news = {
                "標題":         news.get(title_tab,     "無標題"),
                "摘要":         self.clean_html_summary(news.get(summary_tab) or news.get('description', '無摘要')),
                "作者":         news.get(author_tab,    "無作者"),
                "發佈時間":     news.get(published_tab, "未知時間"),
                "連結":         news.get(link_tab,      "#"),
            }
            all_readable_news.append(single_readable_news)
            #logging.info(f"\n\n第一條新聞(可讀)的資料:\n{all_readable_news[0]}\n\n")
        return all_readable_news

    def get_single_article(self, article_url, class_name):
        response = requests.get(article_url)
        soup = BeautifulSoup(response.text, "lxml")
        paragraphs = soup.find_all("div", class_=class_name)
        article_text = " ".join([p.get_text(strip=True) for p in paragraphs])
        return article_text
    


    

    def get_readable_news(self,  url):
        all_news = self.get_all_rss_news(url)
        readable_news = self.get_all_readable_news(all_news)
        return readable_news

    def check_not_duplicated_news(self, title, existing_news, link):
        return (title not in [n['英文標題'] for n in existing_news]) and (link not in [n['連結'] for n in existing_news]) and (title not in [n['中文標題'] for n in existing_news])


    def get_title_summary_link(self, news):
        title = news.get('標題', 'No Title')
        summary = news.get('摘要', '')
        news_link = news.get('連結', '') # 拎到條link
        return title, summary, news_link
    