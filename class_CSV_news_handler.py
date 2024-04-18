import csv
import os
from datetime import datetime, timedelta
from class_logging import logger

class CSVNewsHandler:
    def __init__(self, base_dir="market_news"):
        """
        初始化CSV新聞處理器。
        :param base_dir: 存放CSV文件的基本目錄。
        """
        self.base_dir = base_dir

    def read_csv_files(self, file_paths):
        """
        讀取多個CSV文件中的新聞數據。
        :param file_paths: CSV文件路徑列表。
        :return: 包含所有讀取數據的列表。
        """
        news_data = []
        for file_path in file_paths:
            if os.path.isfile(file_path):
                with open(file_path, mode='r', newline='', encoding='utf-8') as file:
                    reader = csv.DictReader(file)
                    for row in reader:
                        news_data.append(row)
        return news_data

    def get_csv_file_paths(self, num_days):
        """
        獲取當天和之前指定天數的CSV文件路徑。
        :param num_days: 指定的天數。
        :return: CSV文件路徑的列表。
        """
        current_date = datetime.now().date()
        file_paths = []
        for i in range(num_days):
            date = current_date - timedelta(days=i)
            file_path = f"{self.base_dir}/{date}_news.csv"
            file_paths.append(file_path)
        return file_paths

    def write_to_csv(self, news_data, file_path):
        """
        將新聞數據寫入CSV文件。
        :param news_data: 新聞數據。
        :param file_path: CSV文件的路徑。
        """
        fieldnames = ["英文標題", "中文標題", "英文摘要", "中文摘要", "英文內容", "中文內容", "作者", "發佈時間", "連結", "中文總結", "建議"]
        file_exists = os.path.isfile(file_path)
        
        with open(file_path, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerow(news_data)

    def read_csv(self, file_path):
        """
        讀取CSV文件中的新聞數據。
        :param file_path: CSV文件的路徑。
        :return: 包含讀取數據的列表。
        """
        news_data = []
        if os.path.isfile(file_path):
            with open(file_path, mode='r', newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    news_data.append(row)
        return news_data
    
    def get_existing_news(self): 
        # 拎當天和之前30天的CSV文件路徑
        csv_file_paths = self.get_csv_file_paths(30)
        existing_news = self.read_csv_files(csv_file_paths)
        return existing_news

    def save_csv(self, news, title, cn_title, cn_summary, cn_content, en_title, en_summary,  en_content, analysis, cn_suggestion, existing_news):
        try:
            news_data = {
                "英文標題": en_title,
                "中文標題": cn_title,
                "英文摘要": en_summary,
                "中文摘要": cn_summary,  
                "英文內容": en_content,
                "中文內容": cn_content,
                "作者": news.get('作者', '') if '作者' in news else '',
                "發佈時間": news.get('發佈時間', '') if '發佈時間' in news else '',
                "連結": news.get('連結', '') if '連結' in news else '',
                "中文總結": cn_summary,
                "建議": cn_suggestion
            }

            #logging.info (f"\n\n-=---------------------------------------\n{news_data}\n-=---------------------------------------\n\n\n")

            current_date = datetime.now().strftime("%Y-%m-%d")
            csv_file_path = f"market_news/{current_date}_news.csv"
            self.write_to_csv(news_data, csv_file_path)
            existing_news.append(news_data)
            logger.info(f"\nsave_csv - 標題: {title}")
            logger.info(f"save_csv - 連結: {news.get('連結', '') if '連結' in news else ''}")
            logger.info("-" * 30)
            return existing_news
        except Exception as e:
            logger.error (f"save_csv error: ({e})")