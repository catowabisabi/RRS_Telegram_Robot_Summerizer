rss_feed_crypto = {
    "Coindesk": "https://www.coindesk.com/arc/outboundfeeds/rss/",
    "AMBCrypto": "https://ambcrypto.com/feed/", 
    "Bitcoin.com": "https://news.bitcoin.com/feed/",
    "CNN Money": "http://rss.cnn.com/rss/money_topstories.rss",
    "Cointelegraph": "https://cn.cointelegraph.com/rss"
}
rss_feed_stock = {
    "CNBC-Finance":"https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=10000664",
    "CNBC-Economy":"https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=20910258",

    "Investing-Stock":"https://ca.investing.com/rss/news_25.rss",
    "Investing-Popular":"https://ca.investing.com/rss/news_285.rss",
    "Investing-Crypto":"https://ca.investing.com/rss/news_301.rss",
    "Investing-Crypto-Analysis":"https://ca.investing.com/rss/302.rss"

}

introduction_text = """
歡迎使用我們的Telegram機械人！以下是可用的命令列表：
/start                  - 顯示歡迎信息
/help                   - 顯示此功能清單
/test                   - 測試
/s                      - 總結文本
/e                      - 解釋事件
/l                      - 列出持份者與資產
/t                      - 說明技術與科技
/start_bot              - 開始提取新聞
/stop_bot               - 停止提取新聞
/model 3/4              - 改變GPT 模型
/ask_model 3/4          - 改變GPT ASK模型
/set_prompts            - 設定GPT Prompts
/set_systems_prompts    - 設定GPT System Prompts
/show_prompts           - 顯示 Prompts
/show_models            - 顯示 GPT 模型
/csv_size               - 設定 Selected CSV 行數
/show_csv_size          - 顯示 Selected CSV 行數
/save_csv"              - 保存指定的CSV
/list_csv               - 顯示已保存的CSV
/get_csv"               - 提取指定的CSV
/csv_keep_45            - 保持 Market News 中的CSV 數量為45天
/clear_s_csv            - 清空 Selected CSV
    """
