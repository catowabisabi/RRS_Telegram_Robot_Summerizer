
# 原始數據



class KeyMap:
    @staticmethod
    def translated_gpt_json(data):

        # 中英對照表
        key_mapping = {
            '投資': 'Investment',
            'symbols': 'Symbols',  # 如果鍵名相同，可以直接複製或省略
            'sentiment': 'Sentiment',  # 同上
            'links': 'Links',  # 同上
            'analysis': 'Analysis'  # 同上
        }

        # 使用字典推導式轉換鍵
        translated_data = {key_mapping.get(k, k): v for k, v in data.items()}

        investment = translated_data['Investment']
        symbols = translated_data['Symbols']
        sentiment = translated_data['Sentiment']
        links = translated_data['Links']
        analysis = translated_data['Analysis']
        print(f'\n{investment}\n{symbols}\n{sentiment}\n{links}\n{analysis}')
        return investment,  symbols, sentiment, links, analysis



""" data1 = {'Investment': '比特幣', 'Symbols': 'BTC', 'Sentiment': '正面', 'Links': ['https://www.coindesk.com/markets/2024/04/08/bitcoin-tops-71k-ordinals-bets-rise-ahead-of-halving/'], 'Analysis': '比特幣在亞洲交易時段突破了71,000美元，預期4月20日的獎勵減半，為Ordinal和BRC-20生態系的投注提供提振，儘管整個加密市場仍然保持著微弱的變化。BTC在過去24小時上漲2％，達到4月1日以來的最高水平。 CoinGecko的數據顯示，廣泛的CoinDesk 20指數，這是一個排除穩定幣的最流動代幣的指數，上漲了0.43％。當減半發生時，挖礦交易的獎勵將減少50％，降低新幣創建的速度，從而降低可用的新供應量。這在過去通常是比特幣牛市的前兆。目前的區塊獎勵是6.25 BTC，將在減半後降至3.125 BTC。 BTC跟踪期貨的持倉量在幾周內保持在超過250億美元的歷史高位，表明對更多預期的價格波動的槓桿投注。一些比特幣生態系代幣和項目上升，因為交易員預計比特幣在減半事件後會上漲。這樣的投注是一種在不使用期貨產品或槓桿的情況下獲得比特幣漲幅代理曝光的方式。數據顯示，過去一周，Ordinal的交易量高於通常的領導者以太坊和Solana，由NodeMonkes和Pups領導。在同一時期，跨所有網絡的NFT買賣活動下降了95％，表明Ordinal出現了孤立的上升。 BRC-20類型的代幣在過去24小時內增加了近6％。基礎設施代幣Multibit（MULTI）上漲22％，而模因幣pepe（PEPE）、alex（ALEX）和pizza（PIZA）最多上漲了60％。PUPS，Pups Ordinal的代幣，在周末上漲了500％後，損失了22％，交易員在獲利後進行了盈利了結。Ordinal是一種通過將數字藝術的引用銘刻到基於比特幣的小型交易中的方式，將數據嵌入比特幣區塊鏈。 BRC-20標準（BRC代表比特幣建議評論）去年推出，使用戶首次可以直接通過網絡發行可轉讓代幣。'}
data2 = {'投資': '比特幣', 'symbols': 'BTC', 'sentiment': '正面', 'links': ['https://www.coindesk.com/markets/2024/04/08/bitcoin-tops-71k-ordinals-bets-rise-ahead-of-halving/?utm_medium=referral&utm_source=rss&utm_campaign=headlines'], 'analysis': '比特幣在亞洲交易時段超過71,000美元，預期4月20日的獎勵減半活動帶來了一些Ordinal和BRC-20生態系的投注提振，即使整體加密貨幣市場仍然保持不變。BTC過去24小時上漲2%，創下自4月1日以來的最高水平。CoinGecko數據顯示，CoinDesk 20指數，即排除穩定幣外最流動代幣的指數，上漲了0.43%。當減半發生時，挖礦交易的獎勵將減少50%，降低創建新幣的速率，從而降低可用的新供應。這在歷史上預示著該代幣的牛市。當前的區塊獎勵是6.25 BTC，將在減半後降至3.125 BTC。BTC跟蹤期貨的未平倉量在過去幾周保持在超過250億美元的記錄高水平，表明人們對預期價格波動的杠杆投注。一些比特幣生態系代幣和項目上涨，交易者預期BTC將在減半事件後出現上漲。這些投注是一種在不使用期貨產品或杠杆的情況下獲得比特幣上漲的替代方式。數據顯示，過去一周Ordinals的成交量高於通常領先者以太坊和Solana，主要由NodeMonkes和Pups領先。在同一時期，跨所有網絡的非同質化代幣（NFT）的買賣活動下降了95%，表明Ordinals的上漲是孤立的。過去24小時，BRC-20類別的代幣上漲了近6％。基礎設施代幣Multibit（MULTI）上漲22％，而模因代幣pepe（PEPE）、alex（ALEX）和pizza（PIZA）上漲了多達60％。PUPS，Pups Ordinal的代幣，在周末上漲了500％後，交易者獲利了22％。Ordinals是一種通過在小比特幣交易中鐫刻數字藝術參考來將數據嵌入比特幣區塊鏈的方式。去年推出了BRC-20標準（BRC代表比特幣請求評論），允許用戶首次直接通過網絡發行可轉讓代幣。'}

KeyMap.translated_gpt_json(data1)

KeyMap.translated_gpt_json(data2) """