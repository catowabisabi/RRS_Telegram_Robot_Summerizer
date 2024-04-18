import csv
from datetime import datetime, timedelta
import os
from class_logging import logger

from class_state import state_manager



class NewsCSVExtractor:
    def __init__(self):
        self.base_path = "./market_news"
        self.output_path = "./selected_news_csv"
        # 創建輸出文件夾（如果不存在）
        os.makedirs(self.output_path, exist_ok=True)
        self.fields = ['英文標題', '發佈時間', '中文內容', '建議']

    def extract_data(self, date):
        file_path = os.path.join(self.base_path, f"{date}_news.csv")
        logger.debug(file_path)

        if not os.path.exists(file_path):
            logger.info(f"找不到 {date} 的資料文件。")
            return None

        extracted_data = []

        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                data = {field: row[field] for field in self.fields}
                extracted_data.append(data)

        return extracted_data

    def save_data(self, date, data):
        max_size = state_manager.get_state('CSV_Size')
    # 计算需要分割的文件数量
        num_files = (len(data) + max_size - 1) // max_size

        for i in range(num_files):
            start = i * max_size
            end = start + max_size
            subset = data[start:end]

            output_file = os.path.join(self.output_path, f"{date}_{i+1:02d}_news.csv")
            with open(output_file, 'w', encoding='utf-8', newline='') as file:
                writer = csv.DictWriter(file, fieldnames=self.fields)
                writer.writeheader()
                writer.writerows(subset)

    def save_csv_data_in_one_day(self, days_ago="0"):
        try:
            days_ago = int(days_ago)
        except ValueError:
            days_ago = 0

        day = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
        data = self.extract_data(day)
        if data:
            self.save_data(day, data)
            return day
        else:
            return None





