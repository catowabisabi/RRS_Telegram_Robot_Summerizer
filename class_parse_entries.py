import html2text
#己經無用
class ParseEntries:
    def __init__(self):
        self.html_parser = html2text.HTML2Text()
        self.html_parser.ignore_links = True  # 忽略摘要中的連結
        self.html_parser.ignore_images = True  # 忽略摘要中的圖片

    def clean_html_summary(self, summary):
        """將HTML摘要轉換為純文字，並去除多餘的空格和換行符。"""
        text_summary = self.html_parser.handle(summary)
        return text_summary.replace("\n", " ").strip()



    def parse_entries(self, entries, source="generic"):
        """通用的解析RSS條目列表的方法，根據不同的源提取有用信息。"""
        parsed_entries = []
        for entry in entries:
            if source in ["coindesk", "ambcrypto", "bitcoin_com", "cnn_money"]:
                summary = self.clean_html_summary(entry.get("summary", "無摘要"))
            else:  # 對於其他源，如 cointelegraph
                summary = entry.get("description", "無摘要")

            parsed_entry = {
                "標題": entry.get("title", "無標題"), ######################有分中英文
                "摘要": summary,
                "作者": entry.get("author", source),  # 如果沒有作者信息，則使用源名稱
                "發佈時間": entry.get("published", "未知時間"),
                "連結": entry.get("link", "#"),
            }
            parsed_entries.append(parsed_entry)
        return parsed_entries



    def parse_coindesk_rss_entries(self, entries):
        return self.parse_entries(entries, "coindesk")
    


    def parse_ambcrypto_rss_entries(self, entries):
        return self.parse_entries(entries, "ambcrypto")

    def parse_bitcoin_com_rss_entries(self, entries):
        return self.parse_entries(entries, "bitcoin_com")

    def parse_cnn_money_rss_entries(self, entries):
        return self.parse_entries(entries, "cnn_money")

    def parse_cointelegraph_rss_entries(self, entries):
        return self.parse_entries(entries, "cointelegraph")
    
    def parse_general_rss_entries(self, entries, source):
        return self.parse_entries(entries, source)