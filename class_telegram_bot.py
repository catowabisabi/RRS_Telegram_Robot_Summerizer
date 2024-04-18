import requests
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.error import NetworkError
import openai
import json
import time
import threading
import asyncio
import os
from datetime import datetime, timedelta
import shutil
from dotenv import load_dotenv

from class_logging import logger, AppLogger

from class_state import state, state_manager
from class_CSV_reader import NewsCSVExtractor

from my_var import introduction_text

load_dotenv()

USERID =int(os.getenv('USER_ID'))



prompts_1 = f"""幫我把以下的文字或以簡單都容易明白的方式解釋。詳細列出並解釋中的不同機構或法人之間的關係, 事件的發生, 事件的對投資者的影響, 事件對投資者的的機會, 事件對投資者的的風險, 事件中主要機構或法人的潛在的對手, 其他對投資者的有可能受到影響的地方。並列出可能與有關的資產, 或巿場, 並分析中所記述的事件對每一個列出的資產和巿場的正面或負面影響"""
prompts_2 = f"""幫我把以下的文字或以清單方式作出總結和分析, 最後指出該中的事件可能對金融巿場, 加密貨幣巿場等的影響和投資建議。以JSON型式回應我。\nJSON的格式如下:{{"cn_summary":"{{文章的中文總結}}","suggestion":"{{該中的事件可能對金融巿場, 加密貨幣巿場等的影響和投資建議}}"}}本回應回直接作為PYTHON應用的輸入, 請只以單一JSON格式回應, 不需要使用自然語言, 以便應用能直接讀取。"""
prompts_3 = f"""幫我把以下的文字或總結摘要。"""

lock = threading.Lock()

if state["News_Catagory"] == "Crypto":
    TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
else:
    TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN_STOCK')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY_STOCK')
    TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID_STOCK')

class TG:
    @staticmethod
    def send(message):
        base_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        data = {
            'chat_id': TELEGRAM_CHAT_ID,
            'text': message
        }
        try:
            response = requests.post(base_url, json=data, timeout=10)
            response.raise_for_status()  # 對4xx或5xx的狀態碼引發異常
            logger.info ("Telegram Msg is sent")
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"發送消息時出錯: {e}")
            return None

class TelegramBot:
    def __init__(self, bot_token, chat_id, openai_api_key):
        """
        :param bot_token: Telegram機器人的Token。
        :param chat_id: 消息接收者的聊天ID。
        """
        self.introduction_text = introduction_text
        self.bot_token = bot_token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        openai.api_key = openai_api_key
        self.telegram_token = bot_token
        self.callback_function = None
        self.extractor = NewsCSVExtractor()
        self.bot_is_on, self.fetching_news = self.check_state()
        self.this_model = ""
        

    
    def main(self):
        application = Application.builder().token(self.telegram_token).build()
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CommandHandler("help", self.help))
        application.add_handler(CommandHandler("test", self.test))
        application.add_handler(CommandHandler("s", self.summarize))
        application.add_handler(CommandHandler("e", self.explain_to_kids))
        application.add_handler(CommandHandler("l", self.list_out_parties_and_coin))
        application.add_handler(CommandHandler("t", self.explain_technologies))
        application.add_handler(CommandHandler("start_bot", self.start_bot))
        application.add_handler(CommandHandler("stop_bot", self.stop_bot))
        application.add_handler(CommandHandler("model", self.set_model))
        application.add_handler(CommandHandler("set_prompts", self.set_prompts))
        application.add_handler(CommandHandler("set_systems_prompts", self.set_systems_prompts))
        application.add_handler(CommandHandler("show_prompts", self.show_prompts))
        application.add_handler(CommandHandler("ask_model", self.set_ask_model))
        application.add_handler(CommandHandler("show_models", self.show_models))
        application.add_handler(CommandHandler("csv_size", self.change_selected_csv_max_size))
        application.add_handler(CommandHandler("show_csv_size", self.show_selected_csv_max_size))
        application.add_handler(CommandHandler("save_csv", self.save_single_csv))
        application.add_handler(CommandHandler("list_csv", self.list_csv_files_in_selected_folder))
        application.add_handler(CommandHandler("get_csv", self.push_csv_to_tg))
        application.add_handler(CommandHandler("csv_keep_45", self.remove_old_csv_files))
        application.add_handler(CommandHandler("clear_s_csv", self.clear_selected_news_csv_folder))



        # 同時運行Fetching News
        asyncio.ensure_future(self.run_callback())
        application.run_polling()


    

    ########################################################################################################## Function
    def remove_special_markers(self, text, start_marker='```json', end_marker='```'):
        if text.startswith(start_marker):
            text = text[len(start_marker):]
        if text.endswith(end_marker):
            text = text[:-len(end_marker)]
        return text.strip()
    ##########################################################################################################



    ###########################################################################################################
    # 設定要同時運行的程序 (Fetching News)
    def set_callback(self, callback):
        self.callback_function = callback

    # 返回機器人的運行狀態
    def check_state(self):
        bot_is_on = state_manager.get_state('Bot is ON')
        fetching_news = state_manager.get_state('Fetching News')
        return bot_is_on, fetching_news
    
    async def run_callback(self):
        self.this_model = state_manager.get_state("Model") 
        AppLogger.log_and_print_state_info(self.bot_is_on, self.fetching_news, self.this_model)
        
        while True:
            this_model = state_manager.get_state("Model") 
            bot_is_on, fetching_news = self.check_state()
            if this_model != self.this_model or bot_is_on != self.bot_is_on or this_model !=self.this_model:
                AppLogger.log_and_print_state_info(bot_is_on, fetching_news, this_model)
                self.this_model = this_model
                self.bot_is_on = bot_is_on
                self.fetching_news = fetching_news
            
            if bot_is_on and self.callback_function:
                if not fetching_news:
                    state_manager.set_state("Fetching News", True)
                    asyncio.create_task(self.callback_function())
            await asyncio.sleep(5)
    ###########################################################################################################




    ###########################################################################################################
    async def start_bot(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_id = update.effective_user.id
        if user_id != USERID:
            return
        logger.info('Bot is turned on.')
        state_manager.set_state("Bot is ON", True)
        await update.message.reply_text('Bot is turned on.')

    async def stop_bot(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_id = update.effective_user.id
        if user_id != USERID:
            return
        logger.info('Bot is turned off.')
        state_manager.set_state("Bot is ON", False)
        state_manager.set_state("Fetching News", False)
        await update.message.reply_text('Bot is turned off.')
    
    ###########################################################################################################
        

    ########################################################################################################### CSV
    def send_document(self, document_path):
        bot = Bot(self.bot_token)
        try:
            bot.send_document(chat_id=self.chat_id, document=open(document_path, 'rb'))
        except (NetworkError) as e:
            logger.error(e)


    async def save_single_csv(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_id = update.effective_user.id
        if user_id != USERID:
            return
        user_message = ' '.join(context.args)
        day = self.extractor.save_csv_data_in_one_day(user_message)
        await update.message.reply_text(f"已改保存了 {day} 當天的到\'Selected_News_CSV\'文件夾。")

    async def list_csv_files_in_selected_folder(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_id = update.effective_user.id
        if user_id != USERID:
            return
        tg_msg = []
        output_path = "./selected_news_csv"
        
        # 获取文件夹内所有文件的名称
        file_names = [f for f in os.listdir(output_path) if os.path.isfile(os.path.join(output_path, f)) and f.endswith('.csv')]

        for file_name in file_names:
            tg_msg.append(file_name)

        tg_msg = f"所有在'Selected_News_CSV'文件夾中的文件名稱是: \n{str(tg_msg)}"
        await update.message.reply_text(tg_msg)


    async def push_csv_to_tg(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_id = update.effective_user.id
        if user_id != USERID:
            return
        user_message = ' '.join(context.args)
        output_path = "./selected_news_csv"

        try:
            # 尝试将用户输入解析为日期
            date = datetime.strptime(user_message, "%Y-%m-%d").date()
            date_str = date.strftime("%Y-%m-%d")

            # 获取该日期对应的所有CSV文件
            file_paths = [os.path.join(output_path, f) for f in os.listdir(output_path) if f.startswith(date_str) and f.endswith(".csv")]

            if file_paths:
                for file_path in file_paths:
                    try:
                        with open(file_path, 'rb') as file:
                            await context.bot.send_document(chat_id=update.effective_chat.id, document=file)
                    except Exception as e:
                        logger.info(f"發送 CSV 文件時出错: {e}")
                        await update.message.reply_text("发送 CSV 失败")
            else:
                await update.message.reply_text(f"沒有找到 {date_str} 的 CSV 文件")

        except ValueError:
            await update.message.reply_text("無效的日期格式,請使用 YYYY-MM-DD 格式")

    async def clear_selected_news_csv_folder(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_id = update.effective_user.id
        if user_id != USERID:
            return
        output_path = "./selected_news_csv"
        
        # 检查文件夹是否存在
        if os.path.exists(output_path):
            # 获取文件夹内所有文件和子文件夹
            entries = os.listdir(output_path)
            
            for entry in entries:
                entry_path = os.path.join(output_path, entry)
                
                # 如果是文件,就删除它
                if os.path.isfile(entry_path):
                    os.remove(entry_path)
                # 如果是子文件夹,就递归删除它
                elif os.path.isdir(entry_path):
                    shutil.rmtree(entry_path)
            
            logger.info(f"已清空 '{output_path}' 文件夾")
            await update.message.reply_text(f"已清空 '{output_path}' 文件夾")
        else:
            logger.info(f"'{output_path}' 文件夾不存在")
            await update.message.reply_text(f"'{output_path}' 文件夾不存在")
            

    async def remove_old_csv_files(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_id = update.effective_user.id
        if user_id != USERID:
            return
        """
        删除指定目录中超过指定天数的CSV文件。
        """
        directory = "./market_news"
        days_to_keep = 45
        now = datetime.now()
        cutoff_date = now - timedelta(days=days_to_keep)

        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            if os.path.isfile(file_path) and filename.endswith('.csv'):
                try:
                    file_date = datetime.strptime(filename.split('_')[0], '%Y-%m-%d').date()  # 将 file_date 转换为 date 对象
                    if file_date < cutoff_date.date():
                        os.remove(file_path)
                        logger.info(f"已删除文件: {file_path}")
                        await update.message.reply_text("45天以前的csv被刪除了!")
                except ValueError:
                    # 如果文件名格式不正确,忽略该文件
                    await update.message.reply_text("刪除45天以前的csv: Error!")
                    continue
    
    async def change_selected_csv_max_size(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_id = update.effective_user.id
        if user_id != USERID:
            return
        user_message = ' '.join(context.args)
        try:
            new_size = int(user_message)
            state_manager.set_state('CSV_Size', new_size)
            msg = f"已更改 CSV 文件最大大小為 {new_size} 行"
            logger.debug(msg)
            await update.message.reply_text(msg)
        except ValueError:
            current_size = state_manager.get_state('CSV_Size')
            msg = f"無效的輸入,當前 CSV 文件最大大小為 {current_size} 行"
            logger.debug(msg)
            await update.message.reply_text(msg)
    
    async def show_selected_csv_max_size(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_id = update.effective_user.id
        if user_id != USERID:
            return
        user_message = ' '.join(context.args)
        current_size = state_manager.get_state('CSV_Size')
        msg = f"當前 CSV 文件最大大小為 {current_size} 行"
        logger.info(msg)
        await update.message.reply_text(msg)
   


    ########################################################################################################### CSV       





    ########################################################################################################### STATE
    async def set_model(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_id = update.effective_user.id
        if user_id != USERID:
            return
        user_message = ' '.join(context.args)
        if user_message == "3":
            state_manager.set_state('Model', "gpt-3.5-turbo")
            logger.info("已改為使用ChatGPT 3.5 Turbo 作為分析模型。")
            await update.message.reply_text("已改為使用ChatGPT 3.5 Turbo 作為分析模型。")
        elif user_message == "4":
            state_manager.set_state('Model', "gpt-4-1106-preview")
            logger.info("已改為使用ChatGPT 4.5 Turbo 作為分析模型。")
            await update.message.reply_text("已改為使用ChatGPT 4.5 Turbo 作為分析模型。")
        else: 
            this_model = state_manager.get_state("Model")
            logger.info(f"沒有改變分析用語言模型, 現時模型為{this_model}。")
            await update.message.reply_text(f"沒有改變分析用語言模型, 現時模型為{this_model}。")
    
    async def set_ask_model(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_id = update.effective_user.id
        if user_id != USERID:
            return
        user_message = ' '.join(context.args)
        if user_message == "3":
            state_manager.set_state('Ask_Model', "gpt-3.5-turbo")
            logger.info("Ask_Model已改為使用ChatGPT 3.5 Turbo 作為分析模型。")
            await update.message.reply_text("Ask_Model已改為使用ChatGPT 3.5 Turbo 作為分析模型。")
        elif user_message == "4":
            state_manager.set_state('Ask_Model', "gpt-4-1106-preview")
            logger.info("Ask_Model已改為使用ChatGPT 4.5 Turbo 作為分析模型。")
            await update.message.reply_text("Ask_Model已改為使用ChatGPT 4.5 Turbo 作為分析模型。")
        else: 
            this_model = state_manager.get_state("Ask_Model")
            logger.info(f"Ask_Model沒有改變分析用語言模型, Ask_Model現時模型為{this_model}。")
            await update.message.reply_text(f"Ask_Model沒有改變分析用語言模型, Ask_Model現時模型為{this_model}。")
        
    async def show_models(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_id = update.effective_user.id
        if user_id != USERID:
            return
        model = state_manager.get_state('Model')
        ask_model = state_manager.get_state('Ask_Model')
        
        logger.debug(f"Model: {model}\n\nAsk_Model: {ask_model}")
        await update.message.reply_text(f"Model: {model}\n\nAsk_Model: {ask_model}")
    ########################################################################################################### STATE        





    ########################################################################################################### STATE

    async def set_prompts(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_id = update.effective_user.id
        if user_id != USERID:
            return
        user_message = ' '.join(context.args)
        if user_message == "1":
            user_message = prompts_1
        
        if user_message == "2":
            user_message = prompts_2

        if user_message == "3":
            user_message = prompts_3

        state_manager.set_state('Prompts', user_message)
        logger.info(f"已更改分析Prompts: {user_message}")
        await update.message.reply_text(f"已更改分析問題: {user_message}")
    
    async def set_systems_prompts(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_id = update.effective_user.id
        if user_id != USERID:
            return
        user_message = ' '.join(context.args)
        state_manager.set_state('System_Prompts', user_message)
        logger.info(f"已更改分析System_Prompts: {user_message}")
        await update.message.reply_text(f"已更改分析System_Prompts: {user_message}")
    
    async def show_prompts(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_id = update.effective_user.id
        if user_id != USERID:
            return
        promtps = state_manager.get_state('Prompts')
        systems_prompts = state_manager.get_state('System_Prompts')
        logger.debug(f"promtps: {promtps}\n\nSystem_Prompts: {systems_prompts}")
        await update.message.reply_text(f"promtps: {promtps}\n\nSystem_Prompts: {systems_prompts}")
    ########################################################################################################### STATE




    ########################################################################################################### GPT
    # ChatGPT
    def dial_chatGPT(self, prompt, system_prompts="請使用繁體中文回答使用者問題"):
        
        model = state_manager.get_state("Ask_Model")
        
        completion = openai.ChatCompletion.create(
            messages=[
                {"role": "system", "content": system_prompts},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            model=model,
        )
        result = completion.choices[0].message.content.strip()
        return result

    # 向Channel發送Msg
    def send_message(self, message):
        data = {
            'chat_id': self.chat_id,
            'text': message
        }
        try:
            response = requests.post(self.base_url, json=data, timeout=10)
            response.raise_for_status()  # 對4xx或5xx的狀態碼引發異常
            logger.info ("Telegram Msg is sent")
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"發送消息時出錯: {e}")
            return None
    ########################################################################################################### GPT








    ########################################################################################################### 普通野
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_id = update.effective_user.id
        if user_id != USERID:
            return
        introduction_text  = self.introduction_text
        await update.message.reply_text(introduction_text)

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_id = update.effective_user.id
        if user_id != USERID:
            return
        help_message  = self.introduction_text
        await update.message.reply_text(help_message)

    async def test(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_id = update.effective_user.id
        if user_id != USERID:
            return
        user_message = ' '.join(context.args)
        test_message = self.introduction_text
        logger.info(user_message)
        await update.message.reply_text(test_message)
    ########################################################################################################### 普通野





    ########################################################################################################### 問野

    #async def summarize(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    #    ask_model = state_manager.get_state('Ask_Model')
    #    user_message = ' '.join(context.args)
    #    #logger.info(f"正在進行總結與分析... :\n\n{'='*30}\n\n{user_message}\n\n{'='*30}\n\n\n\n")
    #    instruction = "你是一個API終端, 你的回應會直接作為PYTHON應用的輸入, 請只以JSON格式回應, 不需要使用自然語言, 以便應用能直接讀取。"
    #    prompt = f"""幫我把以下< >的文字以清單方式作出總結和分析, 最後指出該中的事件可能對金融巿場, 加密貨幣巿場等的影響和投資建議。以JSON型式回應我:內容如下:<{user_message}>JSON的格式如下:{{"cn_summary":"{{文章的中文總結}}","suggestion":"{{該中的事件可能對金融巿場, 加密貨幣巿場等的影響和投資建議}}"}}本回應回直接作為PYTHON應用的輸入, 請只以JSON格式回應, 不需要使用自然語言, 以便應用能直接讀取。"""
    #    result = self.dial_chatGPT(prompt, instruction)
    #    result = self.remove_special_markers(result)
    #    result = json.loads(result)
    #    #logger.info(f"總結與分析-- 結果返回:\n\n{'='*30}\n\n{result}\n\n{'='*30}\n\n\n\n")
    #    summary = result["cn_summary"]
    #    suggestion = result["suggestion"]
    #    msg = f"Ask_Model:{ask_model}\n文章總結:\n{'='*30}\n{summary}\n\n分析或建議:\n{'='*30}\n\n{suggestion}"
    #    await update.message.reply_text(msg)

    #async def explain_to_kids(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    #    ask_model = state_manager.get_state('Ask_Model')
    #    user_message = ' '.join(context.args)
    #    #logger.info(f"正在進行解釋... :\n\n{'='*30}\n\n{user_message}\n\n{'='*30}\n\n\n\n")
    #    prompt = f"""幫我把以下< >的文字以小學生都能明白的方式解釋。內容如下:<{user_message}>。解釋中的不同機構或法人之間的關係, 事件的發生, 事件的影響, 事件的機會, 事件的風險, 潛在的對手, 其他有可能受到影響的地方"""
    #    result = self.dial_chatGPT(prompt)
    #    #logger.info(f"解釋-- 結果返回:\n\n{'='*30}\n\n{result}\n\n{'='*30}\n\n\n\n")
    #    msg = f"Ask_Model:{ask_model}\n解釋:\n{'='*30}\n{result}\n\n"
    #    await update.message.reply_text(msg)

    #async def list_out_parties_and_coin(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    #    ask_model = state_manager.get_state('Ask_Model')
    #    user_message = ' '.join(context.args)
    #    #logger.info(f"清單幫緊你幫緊你... :\n\n{'='*30}\n\n{user_message}\n\n{'='*30}\n\n\n\n")
    #    prompt = f"""幫我把以下< >的文字以內的不同持份者與不同資産或貨幣列出, 並說明文本中的對他們的影響, 說是是正面還是負面。內容如下:<{user_message}>。"""
    #    result = self.dial_chatGPT(prompt)
    #    #logger.info(f"清單幫緊你幫緊你-- 結果返回:\n\n{'='*30}\n\n{result}\n\n{'='*30}\n\n\n\n")
    #    msg = f"Ask_Model:{ask_model}\n不同持份者與不同資産或貨幣:\n{'='*30}\n{result}\n\n"
    #    await update.message.reply_text(msg)

    #async def explain_technologies(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    #    ask_model = state_manager.get_state('Ask_Model')
    #    user_message = ' '.join(context.args)
    #    #logger.info(f"技術與科技... :\n\n{'='*30}\n\n{user_message}\n\n{'='*30}\n\n\n\n")
    #    prompt = f"""幫我把以下< >的文字中所提及的技術或科技以小學生都能明白的方式解釋。內容如下:<{user_message}>。說明技術的原理, 背後理念, 突破, 成功指標, 風險等等。"""
    #    result = self.dial_chatGPT(prompt)
    #    #logger.info(f"技術與科技-- 結果返回:\n\n{'='*30}\n\n{result}\n\n{'='*30}\n\n\n\n")
    #    msg = f"Ask_Model:{ask_model}\n技術與科技:\n{'='*30}\n{result}\n\n"
     #   await update.message.reply_text(msg)

    ########################################################################################################### 普通野

    async def handle_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE, prompt_template: str, processing_function=None):
        user_id = update.effective_user.id
        if user_id != USERID:
            return
        ask_model = state_manager.get_state('Ask_Model')
        user_message = ' '.join(context.args)
        prompt = prompt_template.format(user_message=user_message)
        result = self.dial_chatGPT(prompt)

        if processing_function:
            result = processing_function(result)

        msg = f"Ask_Model:{ask_model}\n{result}\n"
        await update.message.reply_text(msg)

    async def summarize(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_id = update.effective_user.id
        if user_id != USERID:
            return
        prompt_template = "幫我把以下< >的文字以清單方式作出總結和分析, 最後指出該中的事件可能對金融巿場, 加密貨幣巿場等的影響和投資建議。以JSON型式回應我:內容如下:<{user_message}>"
        await self.handle_command(update, context, prompt_template, self.process_summarize)

    async def explain_to_kids(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_id = update.effective_user.id
        if user_id != USERID:
            return
        prompt_template = "幫我把以下< >的文字以小學生都能明白的方式解釋。內容如下:<{user_message}>。"
        await self.handle_command(update, context, prompt_template)

    async def list_out_parties_and_coin(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_id = update.effective_user.id
        if user_id != USERID:
            return
        prompt_template = "幫我把以下< >的文字以內的不同持份者與不同資産或貨幣列出, 並說明文本中的對他們的影響, 說是是正面還是負面。內容如下:<{user_message}>。"
        await self.handle_command(update, context, prompt_template)

    async def explain_technologies(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        user_id = update.effective_user.id
        if user_id != USERID:
            return
        prompt_template = "幫我把以下< >的文字中所提及的技術或科技以小學生都能明白的方式解釋。內容如下:<{user_message}>。"
        await self.handle_command(update, context, prompt_template)

    def process_summarize(self, result):
        result = self.remove_special_markers(result)
        result = json.loads(result)
        summary = result["cn_summary"]
        suggestion = result["suggestion"]
        result = f"文章總結:\n{'='*30}\n{summary}\n\n分析或建議:\n{'='*30}\n\n{suggestion}"
        return result




    async def send_news_to_telegram_async(self, tg_msg, last_send_time, second_msg = "No Msg", send_full_content = False): 
        
        min_send_interval = 5  # 發送消息的最小間隔（秒）
        current_time = time.time()
        try:
            if current_time - last_send_time >= min_send_interval:
                self.send_message(tg_msg)
                if send_full_content:
                    time.sleep(5)
                    self.send_message(second_msg)
                last_send_time = current_time
                return last_send_time
        except Exception as e:
            logger.error(f"send_news_to_telegram_async error: ({e})")





