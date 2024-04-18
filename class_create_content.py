from class_state import state_manager
from opencc import OpenCC
from class_text_cleaner import TextCleaner
from class_news_summarizer import NewsSummarizer
from class_translator import EnglishToChineseTranslator
from class_logging import logger



class ContentCreator:
    def __init__(self, openai_api_key) -> None:
        self.cc = OpenCC('s2t')
        self.text_cleaner = TextCleaner()
        self.news_summerizer = NewsSummarizer(openai_api_key=openai_api_key)
        self.translator = EnglishToChineseTranslator()
        
    async def create_content(self, url, source, news, title, summary, article_content):
        if "cointelegraph" in url:
            cn_title, cn_summary, cn_content, en_title, en_summary,  en_content, analysis, cn_suggestion, model = await self.handle_cn_content(title, summary, article_content)
            tg_msg = f"資料來源: {source}\n\n{news.get('發佈時間', '')}\n\n<<{cn_title}>>\n======\n\nAI分析 ({model}): \n{cn_suggestion}\n\n連結: {news.get('連結', '')}"
            send_full_content = False
        else:
            cn_title, cn_summary, cn_content, en_title, en_summary,  en_content, analysis, cn_suggestion, model = await self.handle_en_content(title, summary, article_content)
            tg_msg = f"資料來源: {source}\n\n{news.get('發佈時間', '')}\n\n<<{cn_title}>>\n\n({en_title})>>\n======\n\nAI分析 ({model}): \n{cn_suggestion}\n\n連結: {news.get('連結', '')}"
            send_full_content = True
        return  cn_title, cn_summary, cn_content, en_title, en_summary,  en_content, analysis, cn_suggestion, model, tg_msg, send_full_content


    async def handle_cn_content(self, title, summary, article_content):
        model           = state_manager.get_state("Model")
        cn_title        = self.cc.convert(title)
        cn_summary      = self.text_cleaner.remove_html_tags(self.cc.convert(summary))
        cn_content      = self.cc.convert(article_content)
        en_title        = cn_title
        en_summary      = ""
        en_content      = ""
        analysis        = self.news_summerizer.send_GPT_news(cn_content)
        cn_suggestion   = analysis
        return cn_title, cn_summary, cn_content, en_title, en_summary,  en_content, analysis, cn_suggestion, model
    
    async def handle_en_content(self, title, summary, article_content):
        model           = state_manager.get_state("Model")
        cn_title        = ""
        cn_summary      = ""
        cn_content      = ""
        analysis        = ""
        cn_suggestion   = ""

        try:
            en_title    = title
            en_summary  = summary
            en_content  = article_content
            cn_title    = self.translator.translate(title)
            #analysis   = self.news_summerizer.summarize_financial_impact(en_content, model=model)
            analysis    = self.news_summerizer.send_GPT_news(en_content)
            cn_summary  = self.translator.translate(en_summary)
            
            
            if isinstance(analysis, str):
                cn_suggestion = analysis
            elif isinstance(analysis, dict):
                cn_content = analysis.get('cn_summary', '')
                cn_suggestion = analysis.get('cn_summary', '') + "\n\n\n" + analysis.get('suggestion', '')
            else:
                logger.error(f"Unexpected type for analysis: {type(analysis)}")
        except Exception as e:
            logger.error (f"handle_en_content Error: {e}")
        return cn_title, cn_summary, cn_content, en_title, en_summary,  en_content, analysis, cn_suggestion, model