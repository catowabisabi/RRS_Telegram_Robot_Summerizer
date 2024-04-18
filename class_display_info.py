from class_logging import logger

class InfoDisplay:
    def __init__(self):
        pass

    def show_news_court(self,new_news_count):
        if new_news_count == 0:
                logger.info("沒有新的新聞")
        else:
            logger.info(f"發現 {new_news_count} 條新的新聞")
        logger.info("=" * 30)