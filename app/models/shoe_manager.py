#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
百家樂牌靴管理器
"""

import random

class ShoeManager:
    """百家樂牌靴管理器類別"""
    
    def __init__(self, num_decks=8):
        """初始化牌靴"""
        self.num_decks = num_decks
        self.reset(num_decks)
    
    def reset(self, num_decks=None):
        """重置牌靴"""
        if num_decks is not None:
            self.num_decks = num_decks
        
        # 建立牌靴
        self.shoe = []
        suits = ['♠', '♥', '♦', '♣']
        ranks = ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']
        
        for _ in range(self.num_decks):
            for suit in suits:
                for rank in ranks:
                    self.shoe.append(f"{rank}{suit}")
        
        # 洗牌
        random.shuffle(self.shoe)
    
    def get_remaining_cards(self):
        """獲取剩餘牌數"""
        return len(self.shoe)
    
    def draw_card(self):
        """抽一張牌"""
        if not self.shoe:
            return None
        return self.shoe.pop()
    
    def remove_card(self, card):
        """從牌靴中移除指定的牌"""
        if card in self.shoe:
            self.shoe.remove(card)
            return True
        return False
    
    def calculate_banker_probability(self):
        """計算莊家獲勝機率"""
        # 簡化的計算方法，實際應用中應該使用更複雜的模型
        high_cards = sum(1 for card in self.shoe if card[0] in ['10', 'J', 'Q', 'K'])
        low_cards = sum(1 for card in self.shoe if card[0] in ['A', '2', '3', '4', '5', '6'])
        
        total_cards = len(self.shoe)
        if total_cards == 0:
            return 0.5
        
        # 低牌比例高時，莊家獲勝機率增加
        banker_prob = 0.5 + (low_cards - high_cards) / (2 * total_cards)
        
        # 確保機率在合理範圍內
        return max(0.4, min(0.6, banker_prob))
    
    def calculate_player_probability(self):
        """計算閒家獲勝機率"""
        banker_prob = self.calculate_banker_probability()
        tie_prob = self.calculate_tie_probability()
        
        # 閒家機率 = 1 - 莊家機率 - 和局機率
        return 1 - banker_prob - tie_prob
    
    def calculate_tie_probability(self):
        """計算和局機率"""
        # 和局的基本機率約為 9.6%
        return 0.096
