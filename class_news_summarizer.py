import json
import openai
from class_text_cleaner import TextCleaner
import asyncio

from class_state import state, state_manager
from class_logging import AppLogger

class NewsSummarizer:
    def __init__(self, openai_api_key):
        openai.api_key = openai_api_key
        self.text_cleaner = TextCleaner()
        self.model = state['Model']
    
    def try_parse_json(self, maybe_json_str):
        maybe_json_str = self.text_cleaner.clean(maybe_json_str)
        try:
            # 尝试解析 JSON
            return json.loads(maybe_json_str), True
        except json.JSONDecodeError:
            # 如果解析失败，返回原始字符串
            return maybe_json_str, False

    def generate_completion(self, user_prompts, model = None, system_prompts="請使用繁體中文回答使用者問題", temperature=0.7):
        if not model:
            self.model = state['Model']
        completion = openai.ChatCompletion.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompts},
                {"role": "user", "content": user_prompts}
            ],
            temperature=temperature
        )
        return completion.choices[0].message.content.strip()
    


    def send_GPT_news_OPENAI(self, news):
        try:
            model = state['Model']
            
            prompts, system_prompts = self.collect_prompts(news)
            result = self.generate_completion( model = model, user_prompts=prompts, system_prompts=system_prompts)
            parsed_result, is_json = self.try_parse_json(result)
            if is_json:
                result = parsed_result
            return result
        except Exception as e:
            AppLogger.log_and_print_error(f'send_GPT_news Error: {e}')
            return None
    
    #claude
    def send_GPT_news(self, news):
        try:
            model = state['Model']
            
            prompts, system_prompts = self.collect_prompts(news)
            result = self.generate_completion( model = model, user_prompts=prompts, system_prompts=system_prompts)
            parsed_result, is_json = self.try_parse_json(result)
            if is_json:
                result = parsed_result
            return result
        except Exception as e:
            AppLogger.log_and_print_error(f'send_GPT_news Error: {e}')
            return None
    


    def ask_GPT_news(self, news):
        prompts, system_prompts = self.collect_prompts(news)
        model = state['Ask_Model']
        result = self.generate_completion( model = model, user_prompts=prompts, system_prompts=system_prompts)
        return result


    def collect_prompts(self, news):
        system_prompts = state['System_Prompts']
        prompts = f"{state['Prompts']} + 以下是新聞內容: \n\'{news}\'"
        return prompts, system_prompts
    


#====================以下是舊的代碼

    def summarize_financial_impact(self, context, system_prompt="請使用繁體中文回答使用者問題"):
        prompts = f"""幫我把以下的新聞以清單方式作出總結和分析, 最後指出該新聞中的事件可能對金融巿場, 加密貨幣巿場等的影響和投資建議。以JSON型式回應我。\nJSON的格式如下:{{"cn_summary":"{{文章的中文總結}}","suggestion":"{{該新聞中的事件可能對金融巿場, 加密貨幣巿場等的影響和投資建議}}"}}本回應回直接作為PYTHON應用的輸入, 請只以單一JSON格式回應, 不需要使用自然語言, 以便應用能直接讀取。"""
        state_manager.set_state("Prompts", prompts)
        state_manager.set_state("System_Prompts", system_prompt)
        self.send_GPT_news(context)
        #logging.info(f"正在進行總結與分析... :\n\n{'='*30}\n\n{context}\n\n{'='*30}\n\n\n\n")
        result = self.send_GPT_news(context)
        #logging.info(f"總結結果:\n\n{'='*30}\n\n{result[:30]}\n\n{'='*30}\n\n\n\n")
        result = self.text_cleaner.clean(result)
        #logging.info(f"cleaned總結結果:\n\n{'='*30}\n\n{result[:30]}\n\n{'='*30}\n\n\n\n")
        return json.loads(result)

    def explain_to_children(self, context,  system_prompt="請使用繁體中文回答使用者問題"):
        #logging.info(f"正在以兒童的角度進行總結與分析... :\n\n{'='*30}\n{context[:150]}\n{'='*30}\n\n")
        prompts = f"""幫我把以下的新聞以小學生都能明白的方式解釋。詳細列出並解釋新聞中的不同機構或法人之間的關係, 事件的發生, 事件的對投資者的影響, 事件對投資者的的機會, 事件對投資者的的風險, 事件中主要機構或法人的潛在的對手, 其他對投資者的有可能受到影響的地方。並列出可能與新聞有關的資產, 或巿場, 並分析新聞中所記述的事件對每一個列出的資產和巿場的正面或負面影響"""
        state_manager.set_state("Prompts", prompts)
        state_manager.set_state("System_Prompts", system_prompt)
        result = self.send_GPT_news(context)
        #result = self.generate_completion(user_prompt=prompt, system_prompt=system_prompt)
        #logging.info(f"兒童角度總結結果:\n\n{'='*30}\n{result[:30]}\n{'='*150}\n\n")
        return result
    
    def summarize_text(self, context, system_prompt="請使用繁體中文回答使用者問題"):
        prompts = f"""幫我把以下的-新聞總結摘要。"""
        state_manager.set_state("Prompts", prompts)
        state_manager.set_state("System_Prompts", system_prompt)
        result = self.send_GPT_news(context)
        return result
    
    def get_gpt_json_response(self, context, system_prompt='You are an assistant that only speaks JSON. Do not write normal text for response. Please use ENGLISH keys, e.g. \"Investment\",\"Links\" and \"Analysis\". Please use Traditional Chinese for the VALUES execpt for the Symbol or Links. The value type of \"Investment\" is List of Dict[{...},{...}], the value type of  , the value type of  \"Links\" is List [url, url, ...] and the value type of \"Analysis\" is str"'):
        try:
            prompts = f"""總結以下所有新聞, 列出相對有投資資訊價值的, 與Daytrade有關的新聞, 新聞內的提及的貨幣, 股票, 項目等標的物, 如果有Symbol請標示Symbol。\n\n每個標的物請給與\"正面\"或\"負面\"的標籤, 忽略所有中性的新聞和沒有明顯投資方向或價值的新聞。\n\n然後把資訊以以下的JSON FORMAT回應, Values \"Investment\",\"Symbols\",\"Sentiment\" 內的值依次序一一對應, 例如新聞中的比特幣是負面而以太幣是正面, \n\n而\"Links\"不需要包括中性或沒有投資方向的新聞連結。 \n\n可以如下表示: {{\n    \"Investment\": [ {{\"Asset\":\"比特幣\",\"Symbol\" : \"BTC\", \"Sentiment\":\"負面\"}},\n                    {{\"Asset\":\"以太幣\",\"Symbol\" : \"ETH\", \"Sentiment\":\"正面\"}},\n                    {{\"Asset\":\"阿根廷股市\",\"Symbol\" : \"N/A\", \"Sentiment\":\"負面\"}}],\n    \"Links\": [\n      \"http://example.com/news/bitcoin-drop\",\n      \"http://example.com/news/ethereum-rise\",\n      \"http://example.com/news/argentina-stock-crash\"\n    ],\n    \"Analysis\": \"近期比特幣價格下跌，交易價格約為6.6萬美元，市場對其前景持保留態度。與此同時，以太幣在技術升級後表現強勁，多數分析師看好其市場表現。阿根廷股市因政府新政影響，總統Milei的政策使投資者感到不安，股市急跌。\"\n  }}\n\n以下是這次要分析的新聞: """
            state_manager.set_state("Prompts", prompts)
            state_manager.set_state("System_Prompts", system_prompt)
            result = self.send_GPT_news(context)
            print("\n\n成功 get_gpt_json_response, RESULT:\n")
            print(result)
            print ("\n")
            return result
        except Exception as e:
            AppLogger.log_and_print_error(f'get_gpt_json_response Error: {e}')
            return None
    
    