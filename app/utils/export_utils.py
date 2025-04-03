import csv
import io
import json
from datetime import datetime

def export_to_csv(game_history):
    """匯出歷史記錄為CSV格式"""
    output = io.StringIO()
    writer = csv.writer(output)
    
    # 寫入標題行
    writer.writerow(["局數", "結果", "時間", "AI預測", "公式預測", "AI預測正確", "公式預測正確"])
    
    # 寫入資料行
    for record in game_history:
        round_number = record.get("round", "")
        result = record.get("result", "")
        time_str = record.get("time", "")
        ai_prediction = record.get("ai_prediction", "無")
        formula_prediction = record.get("formula_prediction", "無")
        
        ai_correct = "是" if ai_prediction == result else "否"
        formula_correct = "是" if formula_prediction == result else "否"
        
        writer.writerow([
            round_number, 
            result, 
            time_str, 
            ai_prediction, 
            formula_prediction, 
            ai_correct, 
            formula_correct
        ])
    
    return output.getvalue()

def export_to_json(game_history):
    """匯出歷史記錄為JSON格式"""
    return json.dumps(game_history, ensure_ascii=False, indent=4)

def generate_filename(prefix, extension):
    """生成帶有時間戳的檔名"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{timestamp}.{extension}"

