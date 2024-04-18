# state_manager.py

# 初始化狀態
class StateManager:
    def __init__(self) -> None:
        
        self.state = {
            'Bot is ON': False,
            'Fetching News': False,
            'Model': "gpt-3.5-turbo", 
            'Ask_Model':"gpt-4-1106-preview",
            'Prompts':f"""幫我把以下的文字以簡單都容易明白的方式解釋。詳細列出並解釋新聞中的不同機構或法人之間的關係, 事件的發生, 事件的對投資者的影響, 事件對投資者的的機會, 事件對投資者的的風險, 事件中主要機構或法人的潛在的對手, 其他對投資者的有可能受到影響的地方。並列出可能與新聞有關的資產, 或巿場, 並分析新聞中所記述的事件對每一個列出的資產和巿場的正面或負面影響""",
            'System_Prompts':"請使用繁體中文回答使用者問題",
            "CSV_Size":300,
            "Single_News_Count_For_summarization":5,
            "Over_All_Analysis": True,
            "News_Catagory":"Crypto",
            "Save_Only": True

        }
        self.last_bot_is_on = False
        self.last_fetching_news = False

    def get_state(self, key):
        return self.state.get(key)

    def set_state(self, key, value):
        self.state[key] = value
        print(f"狀態已更新：{key} = {value}")

    def update_state(self, new_state):
        self.state.update(new_state)
    
    def check_state(self):
        bot_is_on = self.get_state('Bot is ON')
        fetching_news = self.get_state('Fetching News')
        self.last_bot_is_on = bot_is_on
        self.last_fetching_news = fetching_news
        return bot_is_on, fetching_news
    
    def bot_is_on(self):
        bot_is_on, fetching_news = self.check_state()
        if bot_is_on:
            if fetching_news != self.last_fetching_news:
                self.set_state("Fetching News", True)
                self.last_fetching_news = fetching_news

        if bot_is_on != self.last_bot_is_on:
            print(f"機器人開啓狀態:{bot_is_on}\n")
            self.last_bot_is_on = bot_is_on
        return bot_is_on

    def fetching_news(self):
        bot_is_on, fetching_news = self.check_state()
        if fetching_news != self.last_fetching_news:
            print(f"提取新聞狀態:{fetching_news}\n")
            self.last_fetching_news = fetching_news
        return fetching_news

state_manager = StateManager()
state = state_manager.state