import logging


class AppLogger:
    @staticmethod
    def setup_logging():
        """
        為不同級別的日誌設置專門的文件處理器，終端僅顯示CRITICAL級別的日誌。
        """
        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)  # 設定最低捕獲級別

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # DEBUG級別的文件處理器
        debug_handler = logging.FileHandler('zlog_debug.log', encoding='utf-8')
        debug_handler.setLevel(logging.DEBUG)
        debug_handler.setFormatter(formatter)
        debug_handler.propagate = False
        logger.addHandler(debug_handler)


        # ERROR級別的文件處理器
        error_handler = logging.FileHandler('zlog_error.log', encoding='utf-8')
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        error_handler.propagate = False
        logger.addHandler(error_handler)


        # INFO級別的文件處理器
        info_handler = logging.FileHandler('zlog_info.log', encoding='utf-8')
        info_handler.setLevel(logging.INFO)
        info_handler.setFormatter(formatter)
        info_handler.propagate = False
        logger.addHandler(info_handler)


        critical_handler = logging.FileHandler('zlog_critical.log', encoding='utf-8')
        critical_handler.setLevel(logging.CRITICAL)
        critical_handler.setFormatter(formatter)
        critical_handler.propagate = False
        logger.addHandler(critical_handler)

        critical_handler = logging.FileHandler('zlog_warming.log', encoding='utf-8')
        warming_handler = logging.StreamHandler()
        warming_handler.setLevel(logging.WARNING)
        warming_handler.setFormatter(formatter)
        warming_handler.propagate = False
        logger.addHandler(warming_handler)


        # 終端處理器，設置為僅顯示CRITICAL級別的日誌
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.ERROR)
        console_handler.setFormatter(formatter)
        console_handler.propagate = False
        logger.addHandler(console_handler)

        warming_handler = logging.StreamHandler()
        warming_handler.setLevel(logging.WARNING)
        warming_handler.setFormatter(formatter)
        warming_handler.propagate = False
        logger.addHandler(warming_handler)
    
    @staticmethod
    def log_and_print_state_info(bot_is_on, fetching_news, this_model):
        message = f"\nCLASS_TG_BOT 機器人開啓狀態: {bot_is_on}\n提取狀態: {fetching_news}\n模型: {this_model}\n"
        logger.info(message)
        print(message)
    
    @staticmethod
    def log_and_print_error(msg):
        message = msg
        logger.error(message)
        print(message)
    
    @staticmethod
    def log_and_print_info(msg, to_log=True, to_print=True):
        if to_log:
            logger.info(msg)
        if to_print:
            print(msg)



AppLogger.setup_logging()
logger = logging.getLogger()
