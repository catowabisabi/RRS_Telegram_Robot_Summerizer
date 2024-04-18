import aiohttp
from bs4 import BeautifulSoup
import asyncio
import re
from class_logging import logger

class ArticleExtractor_old:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
            'Accept': 'application/json',
            'Connection': 'keep-alive',
            'Accept-Language': 'en-US,en;q=0.9'
        }

    async def fetch_article_async(self, url, tab_type="div", div_class_name=""):
        try:
            if "coindesk.com" in url:
                return await self._handle_coindesk_async(url)
            elif "ambcrypto.com" in url:
                return await self._handle_ambcrypto_async(url)
            elif "money.cnn.com" in url:
                return await self._handle_cnn_money_async(url)
            elif "news.bitcoin.com" in url:
                return await self._handle_news_bitcoin_com_async(url)
            elif "cn.cointelegraph.com" in url:
                return await self._handle_cointelegraph_async(url)
            elif "https://www.cnbc.com/" in url:
                return await self._handle_cnbc_async(url)
            elif "investing.com" in url:
                return await self._handle_general_async_by_id(url, tab_type="div", div_id_name="article")
            else:
                return await self._handle_general_async(url, tab_type, div_class_name)
        except Exception as e:
            logger.error (f"fetch_article_async Error: {e}")
            return None
        

    async def _handle_coindesk_async(self, url):
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(url) as response:
                html_content = await response.text()
                soup = BeautifulSoup(html_content, "lxml")
                paragraphs = soup.find_all("div", class_="typography__StyledTypography-sc-owin6q-0 eycWal at-text")
                article_text = " ".join([p.get_text(strip=True) for p in paragraphs])
                await asyncio.sleep(3)
                return article_text

    async def _handle_ambcrypto_async(self, url):
        #logger.debug("_handle_ambcrypto")
        try:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.get(url) as response:
                    html_content = await response.text()
                    soup = BeautifulSoup(html_content, 'html.parser')
                    content_div = soup.find('div', class_='single-post-main-middle')
                    if content_div:
                        article_text = content_div.get_text(separator='\n', strip=True)
                        await asyncio.sleep(1)
                        return article_text
        except Exception as e:
            logger.error(f"_handle_ambcrypto Error:{e}")
            return None

    async def _handle_cnn_money_async(self, url):
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(url) as response:
                html_content = await response.text()
                soup = BeautifulSoup(html_content, "lxml")

                paragraphs = soup.select("#storycontent p")

                article_text = " ".join([p.get_text(strip=True) for p in paragraphs])
                await asyncio.sleep(3)
                return article_text

    async def _handle_news_bitcoin_com_async(self, url):
        try:
            slug = url.rstrip('/').split('/')[-1]
            api_url = f"https://api.news.bitcoin.com/wp-json/bcn/v1/post?slug={slug}"
            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.get(api_url) as response:
                    data = await response.json()

                    html_content = data['content']
                    soup = BeautifulSoup(html_content, 'html.parser')

                    text_content = soup.get_text(separator='\n', strip=True)
                    article_text = re.sub(r'\s+', ' ', text_content).strip()
                    await asyncio.sleep(3)
                    return article_text
        except Exception as e:
            logger.error(f"_handle_news_bitcoin_com Error:{e}")
            return None

    async def _handle_cointelegraph_async(self, url):
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(url) as response:
                html_content = await response.text()
                soup = BeautifulSoup(html_content, "lxml")
                paragraphs = soup.find_all("div", class_="post-content relative post-content_asia")
                article_text = " ".join([p.get_text(strip=True) for p in paragraphs])
                await asyncio.sleep(3)
                return article_text

    async def _handle_cnbc_async(self, url):
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(url) as response:
                html_content = await response.text()
                soup = BeautifulSoup(html_content, "lxml")
                paragraphs = soup.find_all("div", class_="ArticleBody-articleBody")
                article_text = " ".join([p.get_text(strip=True) for p in paragraphs])
                await asyncio.sleep(3)
                return article_text
    
    async def _handle_general_async(self, url, tab_type, div_class_name):
        #logger.info(f"使用_handle_general_async, class name = '{div_class_name}'")
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(url) as response:
                html_content = await response.text()
                soup = BeautifulSoup(html_content, "lxml")
                paragraphs = soup.find_all(tab_type, class_= div_class_name)
                article_text = " ".join([p.get_text(strip=True) for p in paragraphs])
                await asyncio.sleep(3)
                return article_text
    
    async def _handle_general_async_by_id(self, url, tab_type, div_id_name):
        #logger.info(f"_handle_general_async_by_id, id name = '{div_id_name}'")
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(url) as response:
                html_content = await response.text()
                soup = BeautifulSoup(html_content, "lxml")
                paragraphs = soup.find_all(tab_type, id= div_id_name)
                article_text = " ".join([p.get_text(strip=True) for p in paragraphs])
                await asyncio.sleep(3)
                #logger.info((f"_handle_general_async_by_id, article_text = '{article_text}'"))
                return article_text

class ArticleExtractor:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
            'Accept': 'application/json',
            'Connection': 'keep-alive',
            'Accept-Language': 'en-US,en;q=0.9'
        }
    

    async def get_article(self, url, tab_type = "div", select_type = "class", selector_value = ""):
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(url) as response:

                html_content = await response.text()

                soup = BeautifulSoup(html_content, "lxml")
                if select_type == "class":
                    paragraphs = soup.find_all(tab_type, class_= selector_value)
                elif select_type == "id":
                    paragraphs = soup.find_all(tab_type, id= selector_value)
                article_text = " ".join([p.get_text(strip=True) for p in paragraphs])
                await asyncio.sleep(1)
                #logger.info((f"_handle_general_async_by_id, article_text = '{article_text}'"))
                return article_text


    async def fetch_article_async(self, url, tab_type="div", select_type="class", selector_value=""):
        try:
            if "coindesk.com" in url:
                return await self.get_article(url, tab_type= "div", select_type="class", selector_value="typography__StyledTypography-sc-owin6q-0 eycWal at-text")
            elif "ambcrypto.com" in url:
                return await self.get_article(url, tab_type= "div", select_type="class", selector_value="single-post-main-middle")
            elif "cn.cointelegraph.com" in url:
                return await self.get_article(url, tab_type= "div", select_type="class", selector_value="post-content relative post-content_asia")
            elif "https://www.cnbc.com/" in url:
                return await self.get_article(url, tab_type= "div", select_type="class", selector_value="ArticleBody-articleBody")
            elif "investing.com" in url:
                return await self.get_article(url, tab_type= "div", select_type="id", selector_value="article")
            elif "money.cnn.com" in url:
                return await self._handle_cnn_money_async(url)
            elif "news.bitcoin.com" in url:
                return await self._handle_news_bitcoin_com_async(url)
            else:
                return await self.get_article(url, tab_type= tab_type, select_type=select_type, selector_value=selector_value)

        except Exception as e:
            logger.error (f"fetch_article_async Error: {e}")
            return {"msg":f"fetch_article_async Error: {e}"}
        
    
    async def _handle_cnn_money_async(self, url):
        async with aiohttp.ClientSession(headers=self.headers) as session:
            async with session.get(url) as response:
                html_content = await response.text()
                soup = BeautifulSoup(html_content, "lxml")

                paragraphs = soup.select("#storycontent p")
                
                article_text = " ".join([p.get_text(strip=True) for p in paragraphs])
                await asyncio.sleep(3)
                return article_text

    async def _handle_news_bitcoin_com_async(self, url):
        try:
            slug = url.rstrip('/').split('/')[-1]
            api_url = f"https://api.news.bitcoin.com/wp-json/bcn/v1/post?slug={slug}"
            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.get(api_url) as response:
                    data = await response.json()

                    html_content = data['content']
                    soup = BeautifulSoup(html_content, 'html.parser')

                    text_content = soup.get_text(separator='\n', strip=True)
                    article_text = re.sub(r'\s+', ' ', text_content).strip()
                    await asyncio.sleep(3)
                    return article_text
        except Exception as e:
            logger.error(f"_handle_news_bitcoin_com Error:{e}")
            return None