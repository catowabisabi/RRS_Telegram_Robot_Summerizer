import re

class TextCleaner:
    #移除HTML標籤後的文本
    def remove_html_tags(self, text):
        clean_text = re.sub('<[^<]+?>', '', text)
        return clean_text

    def fix_json_brackets(self, json_str):
        stack = []
        for i, char in enumerate(json_str):
            if char == '{':
                stack.append(i)
            elif char == '}':
                if stack:
                    stack.pop()
                else:
                    json_str = json_str[:i] + '{' + json_str[i:]
                    stack.append(i)
        
        while stack:
            index = stack.pop()
            json_str = json_str[:index+1] + '}' + json_str[index+1:]
        
        return json_str

    def remove_special_markers(self, text, start_marker='```json', end_marker='```'):
        """
        從文本的開始和結束處移除特殊標記或模式。
        :param start_marker: 從文本開始處移除的標記或模式。
        :param end_marker: 從文本結束處移除的標記或模式。
        """
        if text.startswith(start_marker):
            text = text[len(start_marker):]  # 移除開始標記
        if text.endswith(end_marker):
            text = text[:-len(end_marker)]  # 移除結束標記
        return text.strip()  # 從文本的開始和結束處修剪空白
    
    def clean(self,text):
        text = self.remove_html_tags(text=text)
        text = self.fix_json_brackets(json_str=text)
        text = self.remove_special_markers(text=text)
        return text

