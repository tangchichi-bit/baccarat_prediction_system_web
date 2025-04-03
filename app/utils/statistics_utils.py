def calculate_statistics(game_history):
    """計算遊戲統計資料"""
    # 初始化統計資料
    stats = {
        "total_rounds": 0,
        "banker_count": 0,
        "player_count": 0,
        "tie_count": 0,
        "banker_percentage": 0,
        "player_percentage": 0,
        "tie_percentage": 0,
        "ai_correct": 0,
        "formula_correct": 0,
        "ai_accuracy": 0,
        "formula_accuracy": 0,
        "match_count": 0,
        "match_rate": 0
    }
    
    # 如果沒有歷史記錄，返回預設統計資料
    if not game_history:
        return stats
    
    # 計算總局數
    stats["total_rounds"] = len(game_history)
    
    # 計算各結果數量
    for record in game_history:
        result = record.get("result", "")
        ai_prediction = record.get("ai_prediction", "無")
        formula_prediction = record.get("formula_prediction", "無")
        
        if result == "莊家":
            stats["banker_count"] += 1
        elif result == "閒家":
            stats["player_count"] += 1
        elif result == "和局":
            stats["tie_count"] += 1
        
        # 計算預測正確數
        if ai_prediction == result:
            stats["ai_correct"] += 1
        
        if formula_prediction == result:
            stats["formula_correct"] += 1
        
        # 計算AI與公式匹配數
        if ai_prediction == formula_prediction and ai_prediction != "無":
            stats["match_count"] += 1
    
    # 計算百分比
    total = stats["total_rounds"]
    if total > 0:
        stats["banker_percentage"] = (stats["banker_count"] / total) * 100
        stats["player_percentage"] = (stats["player_count"] / total) * 100
        stats["tie_percentage"] = (stats["tie_count"] / total) * 100
        stats["ai_accuracy"] = (stats["ai_correct"] / total) * 100
        stats["formula_accuracy"] = (stats["formula_correct"] / total) * 100
    
    # 計算匹配率
    valid_predictions = sum(1 for record in game_history if record.get("ai_prediction", "無") != "無")
    if valid_predictions > 0:
        stats["match_rate"] = (stats["match_count"] / valid_predictions) * 100
    
    return stats
