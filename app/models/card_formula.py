class BaccaratCardFormula:
    """百家樂算牌公式類別"""
    
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
