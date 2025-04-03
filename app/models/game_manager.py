import json
import time
from datetime import datetime

class GameManager:
    def __init__(self):
        self.game_history = []
        self.current_round = 0
    
    def add_result(self, result, ai_prediction="無", formula_prediction="無"):
        """新增遊戲結果"""
        self.current_round += 1
        
        # 建立記錄
        record = {
            "round": self.current_round,
            "result": result,
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "ai_prediction": ai_prediction,
            "formula_prediction": formula_prediction
        }
        
        # 新增到歷史記錄
        self.game_history.append(record)
        return record
    
    def undo_last_result(self):
        """撤銷上一局結果"""
        if not self.game_history:
            return False
        
        last_record = self.game_history.pop()
        self.current_round -= 1
        return last_record
    
    def get_history(self):
        """獲取歷史記錄"""
        return self.game_history
    
    def clear_history(self):
        """清空歷史記錄"""
        self.game_history = []
        self.current_round = 0
        return True
    
    def save_history(self, filename):
        """儲存歷史記錄到檔案"""
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(self.game_history, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"儲存歷史記錄時出錯: {str(e)}")
            return False
    
    def load_history(self, filename):
        """從檔案載入歷史記錄"""
        try:
            with open(filename, "r", encoding="utf-8") as f:
                self.game_history = json.load(f)
            
            # 更新當前局數
            if self.game_history:
                self.current_round = max([record.get("round", 0) for record in self.game_history])
            else:
                self.current_round = 0
                
            return True
        except Exception as e:
            print(f"載入歷史記錄時出錯: {str(e)}")
            return False
    
    def get_statistics(self):
        """獲取統計資料"""
        if not self.game_history:
            return {
                "total_rounds": 0,
                "banker_count": 0,
                "player_count": 0,
                "tie_count": 0,
                "banker_percentage": 0,
                "player_percentage": 0,
                "tie_percentage": 0,
                "ai_accuracy": 0,
                "formula_accuracy": 0,
                "match_rate": 0
            }
        
        total_rounds = len(self.game_history)
        banker_count = sum(1 for r in self.game_history if r.get("result") == "莊家")
        player_count = sum(1 for r in self.game_history if r.get("result") == "閒家")
        tie_count = sum(1 for r in self.game_history if r.get("result") == "和局")
        
        # 計算AI和公式預測準確率
        ai_correct = 0
        formula_correct = 0
        match_count = 0
        
        for record in self.game_history:
            result = record.get("result", "")
            ai_prediction = record.get("ai_prediction", "無")
            formula_prediction = record.get("formula_prediction", "無")
            
            if ai_prediction == result:
                ai_correct += 1
            
            if formula_prediction == result:
                formula_correct += 1
            
            if ai_prediction == formula_prediction and ai_prediction != "無":
                match_count += 1
        
        # 計算百分比
        banker_percentage = (banker_count / total_rounds) * 100 if total_rounds > 0 else 0
        player_percentage = (player_count / total_rounds) * 100 if total_rounds > 0 else 0
        tie_percentage = (tie_count / total_rounds) * 100 if total_rounds > 0 else 0
        
        ai_accuracy = (ai_correct / total_rounds) * 100 if total_rounds > 0 else 0
        formula_accuracy = (formula_correct / total_rounds) * 100 if total_rounds > 0 else 0
        
        # 避免除以零
        valid_predictions = sum(1 for record in self.game_history if record.get("ai_prediction", "無") != "無")
        match_rate = (match_count / valid_predictions) * 100 if valid_predictions > 0 else 0
        
        return {
            "total_rounds": total_rounds,
            "banker_count": banker_count,
            "player_count": player_count,
            "tie_count": tie_count,
            "banker_percentage": banker_percentage,
            "player_percentage": player_percentage,
            "tie_percentage": tie_percentage,
            "ai_accuracy": ai_accuracy,
            "formula_accuracy": formula_accuracy,
            "match_rate": match_rate
        }
