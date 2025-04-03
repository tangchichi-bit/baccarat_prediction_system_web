#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
百家樂算牌公式計算器
"""

class FormulaCalculator:
    """百家樂算牌公式計算器類別"""
    
    def __init__(self):
        """初始化計算器"""
        pass
    
    def predict(self, history):
        """使用算牌公式預測下一局結果"""
        if len(history) < 5:
            return "無法預測", 0
        
        # 獲取最近的結果
        recent = history[-5:]
        
        # 計算莊閒出現次數
        banker_count = sum(1 for result in recent if result == "莊家")
        player_count = sum(1 for result in recent if result == "閒家")
        
        # 計算趨勢
        trend = []
        for i in range(1, len(recent)):
            if recent[i] == recent[i-1]:
                trend.append("連續")
            else:
                trend.append("交替")
        
        # 計算連續和交替的次數
        consecutive_count = trend.count("連續")
        alternating_count = trend.count("交替")
        
        # 判斷是否有明顯趨勢
        if consecutive_count >= 3:
            # 連續趨勢，預測與最後一個結果相同
            prediction = recent[-1]
            confidence = 60 + consecutive_count * 5  # 基礎信心度60%，每多一次連續+5%
        elif alternating_count >= 3:
            # 交替趨勢，預測與最後一個結果相反
            prediction = "閒家" if recent[-1] == "莊家" else "莊家"
            confidence = 60 + alternating_count * 5  # 基礎信心度60%，每多一次交替+5%
        else:
            # 無明顯趨勢，根據出現次數預測
            if banker_count > player_count + 1:
                prediction = "閒家"  # 莊家出現次數明顯多，預測下一局是閒家（回歸均值）
                confidence = 55
            elif player_count > banker_count + 1:
                prediction = "莊家"  # 閒家出現次數明顯多，預測下一局是莊家（回歸均值）
                confidence = 55
            else:
                # 出現次數相近，預測最後一局的結果
                prediction = recent[-1]
                confidence = 50
        
        # 確保信心度不超過100%
        confidence = min(confidence, 100)
        
        return prediction, confidence
    
    def predict_with_cards(self, banker_cards, player_cards):
        """根據牌型預測結果"""
        # 計算百家樂點數
        banker_points = sum(banker_cards) % 10
        player_points = sum(player_cards) % 10
        
        # 計算頻率
        banker_frequency = self.calculate_banker_frequency(banker_cards)
        player_frequency = self.calculate_player_frequency(player_cards)
        
        # 計算優劣勢牌值
        banker_advantage = self.calculate_advantage_value(banker_cards)
        player_advantage = self.calculate_advantage_value(player_cards)
        
        # 綜合評分
        banker_score = banker_frequency + banker_advantage
        player_score = player_frequency + player_advantage
        
        # 和局評分
        tie_score = 0
        if banker_points == player_points:
            tie_score = 5
        
        # 根據分數預測結果
        scores = {
            "莊家": banker_score,
            "閒家": player_score,
            "和局": tie_score
        }
        
        # 找出分數最高的結果
        max_score = max(scores.values())
        max_results = [k for k, v in scores.items() if v == max_score]
        
        # 如果有多個最高分，隨機選擇一個
        if len(max_results) > 1:
            result = random.choice(max_results)
        else:
            result = max_results[0]
        
        # 計算信心度
        total_abs = abs(banker_score) + abs(player_score) + abs(tie_score)
        if total_abs == 0:
            confidence = 33.33  # 平均機率
        else:
            if result == "莊家":
                confidence = (abs(banker_score) / total_abs) * 100
            elif result == "閒家":
                confidence = (abs(player_score) / total_abs) * 100
            else:
                confidence = (abs(tie_score) / total_abs) * 100
        
        # 限制和局的信心度
        if result == "和局" and confidence > 25:
            confidence = 25
        
        return result, confidence

    
    def calculate_player_frequency(self, points):
        """計算閒家頻率"""
        # 計算點數總和並對 10 取餘數
        point_sum = sum(points) % 10
        
        # 根據點數轉換頻率
        if point_sum in [7, 8, 9]:
            return 2
        elif point_sum in [0, 1, 3, 4]:
            return 1
        elif point_sum in [2, 5, 6]:
            return -5
        else:
            return 0
    
    def calculate_banker_frequency(self, points):
        """計算莊家頻率"""
        # 計算點數總和並對 10 取餘數
        point_sum = sum(points) % 10
        
        # 根據點數轉換頻率
        if point_sum in [7, 8, 9]:
            return 3
        elif point_sum in [0, 1, 3, 4, 6]:
            return 2
        elif point_sum in [2, 5]:
            return -5
        else:
            return 0
    
    def calculate_advantage_value(self, points):
        """計算優勢牌值"""
        advantage = 0
        
        for point in points:
            if point in [1, 4, 5, 7, 8]:
                advantage += 2
            elif point in [2, 3]:
                advantage -= 3
            elif point in [6, 9]:
                advantage -= 5
        
        return advantage
