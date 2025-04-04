#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
百家樂 AI 預測與算牌系統後端 API
"""

# 匯入必要的模組
import sys
import os
import time
import random

# 新增專案根目錄到Python路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Flask相關匯入
from flask import Flask, Blueprint, request, jsonify, render_template
from flask_socketio import SocketIO
from flask_cors import CORS

# 匯入自定義模組
from models.ai_model import BaccaratAIModel
from models.shoe_manager import ShoeManager
from models.card_formula import BaccaratCardFormula

# 初始化Flask應用
app = Flask(__name__)
app.config['SECRET_KEY'] = 'baccarat-prediction-system'
socketio = SocketIO(app)
CORS(app)  # 啟用CORS支援

# 初始化模型和管理器
ai_model = BaccaratAIModel()
card_formula = BaccaratCardFormula()
shoe_manager = ShoeManager(auto_detect=True, warmup_size=15)

# 遊戲歷史記錄
game_history = []

@app.route('/')
def index():
    """首頁"""
    return render_template('index.html')

@app.route('/api/shoe', methods=['GET'])
def get_shoe_status():
    """獲取牌靴資訊"""
    return jsonify({
        'shoe_id': shoe_manager.get_current_shoe_id(),
        'cards_remaining': shoe_manager.get_remaining_cards_count(),
        'cards_used': shoe_manager.get_used_cards_count(),
        'is_in_warmup': shoe_manager.is_in_warmup_period(),
        'warmup_progress': shoe_manager.get_warmup_progress(),
        'statistics': shoe_manager.get_shoe_statistics()
    })

@app.route('/api/shoe/new', methods=['POST'])
def new_shoe():
    """開始新牌靴"""
    shoe_id = shoe_manager.manually_start_new_shoe()
   
    return jsonify({
        'success': True,
        'message': f'已開始新牌靴 #{shoe_id}',
        'shoe_id': shoe_id
    })

@app.route('/api/shoe/reset', methods=['POST'])
def reset_shoe():
    """重置當前牌靴"""
    shoe_id = shoe_manager.reset_current_shoe()
   
    return jsonify({
        'success': True,
        'message': f'已重置牌靴 #{shoe_id}',
        'shoe_id': shoe_id
    })

@app.route('/api/shoe/settings', methods=['POST'])
def update_shoe_settings():
    """更新牌靴設定"""
    data = request.json
    auto_detect = data.get('auto_detect', True)
    warmup_size = data.get('warmup_size', 15)
   
    shoe_manager.set_auto_detect(auto_detect)
    shoe_manager.warmup_size = warmup_size
   
    return jsonify({
        'success': True,
        'message': '已更新牌靴設定',
        'settings': {
            'auto_detect': auto_detect,
            'warmup_size': warmup_size
        }
    })

@app.route('/api/train', methods=['POST'])
def train():
    """訓練模型"""
    data = request.json
    history = data.get('history', [])
   
    if len(history) < 10:
        return jsonify({
            'success': False,
            'message': '歷史記錄太少，請至少輸入 10 筆資料'
        })
   
    success = ai_model.train(history)
   
    if success:
        return jsonify({
            'success': True,
            'message': f'已成功訓練模型，使用 {len(history)} 筆歷史資料'
        })
    else:
        return jsonify({
            'success': False,
            'message': '訓練模型失敗'
        })

@app.route('/api/predict/ai', methods=['POST'])
def predict_ai():
    """AI預測下一局結果"""
    try:
        data = request.json
        print(f"收到AI預測請求: {data}")
       
        if not data:
            print("請求資料為空")
            return jsonify({
                'success': False,
                'message': '請求資料為空'
            }), 400
           
        history = data.get('history', [])
        print(f"歷史記錄: {history}")
       
        # AI預測
        ai_result = "無法預測"
        ai_confidence = 0
       
        if ai_model.is_trained and len(history) >= 10:
            try:
                ai_result, ai_confidence = ai_model.predict(history)
                print(f"AI預測結果: {ai_result}, 信心度: {ai_confidence}")
            except Exception as e:
                print(f"AI預測錯誤: {str(e)}")
                import traceback
                traceback.print_exc()
                ai_result = "預測錯誤"
                ai_confidence = 0
       
        return jsonify({
            'success': True,
            'prediction': ai_result,
            'confidence': ai_confidence
        })
    except Exception as e:
        print(f"處理AI預測請求時出錯: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'處理請求時出錯: {str(e)}'
        }), 500

# 算牌公式預測API
@app.route('/api/predict/formula', methods=['POST'])
def predict_formula():
    """算牌公式預測下一局結果"""
    try:
        data = request.json
        print(f"收到公式預測請求: {data}")
       
        banker_cards = data.get('banker_cards', [])
        player_cards = data.get('player_cards', [])
       
        if not banker_cards or not player_cards:
            return jsonify({
                'success': False,
                'message': '請提供莊家和閒家的牌'
            })
       
        # 計算頻率
        banker_frequency = card_formula.calculate_banker_frequency(banker_cards)
        player_frequency = card_formula.calculate_player_frequency(player_cards)
       
        # 計算優勢值
        banker_advantage = card_formula.calculate_advantage_value(banker_cards)
        player_advantage = card_formula.calculate_advantage_value(player_cards)
       
        # 簡單預測
        if banker_frequency > player_frequency:
            prediction = "莊家"
            confidence = min(100, abs(banker_frequency - player_frequency) * 10)
        elif player_frequency > banker_frequency:
            prediction = "閒家"
            confidence = min(100, abs(player_frequency - banker_frequency) * 10)
        else:
            # 如果頻率相同，使用優勢值決定
            if banker_advantage > player_advantage:
                prediction = "莊家"
                confidence = min(100, abs(banker_advantage - player_advantage) * 5)
            elif player_advantage > banker_advantage:
                prediction = "閒家"
                confidence = min(100, abs(player_advantage - banker_advantage) * 5)
            else:
                prediction = "和局"
                confidence = 50
       
        print(f"公式預測結果: {prediction}, 信心度: {confidence}")
       
        return jsonify({
            'success': True,
            'prediction': prediction,
            'confidence': confidence,
            'banker_frequency': banker_frequency,
            'player_frequency': player_frequency,
            'banker_advantage': banker_advantage,
            'player_advantage': player_advantage
        })
    except Exception as e:
        print(f"公式預測錯誤: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'公式預測失敗: {str(e)}'
        }), 500

# 保留原來的組合預測API，但在前端不使用它
@app.route('/api/predict', methods=['POST'])
def predict_next():
    """預測下一局結果(組合)"""
    data = request.json
    history = data.get('history', [])
   
    # AI預測
    ai_result = "無法預測"
    ai_confidence = 0
   
    if ai_model.is_trained and len(history) >= 10:
        try:
            ai_result, ai_confidence = ai_model.predict(history)
        except Exception as e:
            print(f"AI預測錯誤: {str(e)}")
            ai_result = "預測錯誤"
            ai_confidence = 0
   
    # 算牌公式預測 - 這裡需要修改，因為我們現在需要牌型資料
    formula_result = "無法預測"
    formula_confidence = 0
   
    return jsonify({
        'success': True,
        'ai_prediction': {
            'result': ai_result,
            'confidence': ai_confidence
        },
        'formula_prediction': {
            'result': formula_result,
            'confidence': formula_confidence
        }
    })

@app.route('/api/history/add', methods=['POST'])
def add_result():
    """新增遊戲結果"""
    global game_history
   
    data = request.json
    result = data.get('result')
   
    if not result:
        return jsonify({
            'success': False,
            'message': '結果不能為空'
        })
   
    # 獲取當前時間
    current_time = time.strftime("%Y-%m-%d %H:%M:%S")
   
    # 獲取當前局數
    round_number = len(game_history) + 1
   
    # 獲取預測結果
    ai_prediction = "無"
    formula_prediction = "無"
   
    # 如果有足夠的歷史記錄，進行AI預測
    if ai_model.is_trained and len(game_history) >= 10:
        history = [record['result'] for record in game_history]
        ai_prediction, _ = ai_model.predict(history)
   
    # 建立遊戲記錄
    game_record = {
        "round": round_number,
        "result": result,
        "time": current_time,
        "ai_prediction": ai_prediction,
        "formula_prediction": formula_prediction
    }
   
    # 新增到歷史記錄
    game_history.append(game_record)
   
    # 更新牌靴
    is_new_shoe = shoe_manager.add_result(result)
   
    # 計算統計資料
    statistics = calculate_statistics()
   
    return jsonify({
        'success': True,
        'record': game_record,
        'statistics': statistics,
        'is_new_shoe': is_new_shoe,
        'shoe_info': {
            'shoe_id': shoe_manager.get_current_shoe_id(),
            'cards_remaining': shoe_manager.get_remaining_cards_count(),
            'cards_used': shoe_manager.get_used_cards_count(),
            'is_in_warmup': shoe_manager.is_in_warmup_period(),
            'warmup_progress': shoe_manager.get_warmup_progress(),
            'statistics': shoe_manager.get_shoe_statistics()
        }
    })

@app.route('/api/history/undo', methods=['POST'])
def undo_last():
    """撤銷上一局結果"""
    global game_history
   
    if not game_history:
        return jsonify({
            'success': False,
            'message': '沒有可撤銷的記錄'
        })
   
    # 從歷史記錄中移除最後一條
    game_history.pop()
   
    # 從牌靴中撤銷最後一局
    shoe_manager.undo_last_result()
   
    return jsonify({
        'success': True,
        'message': '已撤銷上一局結果',
        'history': game_history,
        'shoe_info': {
            'shoe_id': shoe_manager.get_current_shoe_id(),
            'cards_remaining': shoe_manager.get_remaining_cards_count(),
            'cards_used': shoe_manager.get_used_cards_count(),
            'is_in_warmup': shoe_manager.is_in_warmup_period(),
            'warmup_progress': shoe_manager.get_warmup_progress(),
            'statistics': shoe_manager.get_shoe_statistics()
        }
    })

@app.route('/api/history/clear', methods=['POST'])
def clear_history():
    """清空所有記錄"""
    global game_history
   
    game_history = []
   
    # 重置牌靴
    shoe_manager.reset_all()
   
    return jsonify({
        'success': True,
        'message': '已清空所有記錄'
    })

def calculate_statistics():
    """計算統計資料"""
    total_rounds = len(game_history)
   
    if total_rounds == 0:
        return {
            'total_rounds': 0,
            'ai_accuracy': 0,
            'formula_accuracy': 0,
            'match_rate': 0
        }
   
    # 計算 AI 預測準確率
    ai_correct = 0
    formula_correct = 0
    match_count = 0
    valid_predictions = 0
   
    for record in game_history:
        result = record.get("result", "")
        ai_prediction = record.get("ai_prediction", "無")
        formula_prediction = record.get("formula_prediction", "無")
       
        if ai_prediction != "無":
            valid_predictions += 1
           
            if ai_prediction == result:
                ai_correct += 1
           
            if formula_prediction != "無" and formula_prediction == result:
                formula_correct += 1
           
            if formula_prediction != "無" and ai_prediction == formula_prediction:
                match_count += 1
   
    # 計算準確率和匹配率
    ai_accuracy = (ai_correct / valid_predictions) * 100 if valid_predictions > 0 else 0
    formula_accuracy = (formula_correct / valid_predictions) * 100 if valid_predictions > 0 else 0
    match_rate = (match_count / valid_predictions) * 100 if valid_predictions > 0 else 0
   
    return {
        'total_rounds': total_rounds,
                'ai_accuracy': ai_accuracy,
        'formula_accuracy': formula_accuracy,
        'match_rate': match_rate
    }

@app.route('/api/formula/analyze', methods=['POST'])
def analyze_formula():
    """分析公式"""
    try:
        data = request.json
        print(f"接收到的原始數據: {data}")
       
        # 處理連續輸入的字串
        banker_cards_input = data.get('banker_cards', '')
        player_cards_input = data.get('player_cards', '')
       
        # 將輸入轉換為數字列表
        banker_cards = []
        player_cards = []
       
        # 處理莊家牌
        if isinstance(banker_cards_input, str):
            # 先嘗試按空格分割
            if ' ' in banker_cards_input:
                try:
                    banker_cards = [int(num) for num in banker_cards_input.split()]
                    # 驗證數字範圍
                    for num in banker_cards:
                        if not 0 <= num <= 9:
                            return jsonify({'success': False, 'message': f'莊家牌值必須在0-9之間，發現無效值: {num}'})
                except ValueError:
                    banker_cards = []  # 重置，使用下面的字元解析方法
           
            # 如果空格分割失敗或沒有空格，嘗試將每個字元轉換為數字
            if not banker_cards:
                for char in banker_cards_input:
                    try:
                        num = int(char)
                        if 0 <= num <= 9:  # 確保牌值在有效範圍內
                            banker_cards.append(num)
                        else:
                            return jsonify({'success': False, 'message': f'莊家牌值必須在0-9之間，發現無效值: {num}'})
                    except ValueError:
                        # 忽略非數字字元
                        pass
        elif isinstance(banker_cards_input, list):
            # 如果已經是列表，直接使用
            banker_cards = banker_cards_input
       
        # 處理閒家牌
        if isinstance(player_cards_input, str):
            # 先嘗試按空格分割
            if ' ' in player_cards_input:
                try:
                    player_cards = [int(num) for num in player_cards_input.split()]
                    # 驗證數字範圍
                    for num in player_cards:
                        if not 0 <= num <= 9:
                            return jsonify({'success': False, 'message': f'閒家牌值必須在0-9之間，發現無效值: {num}'})
                except ValueError:
                    player_cards = []  # 重置，使用下面的字元解析方法
           
            # 如果空格分割失敗或沒有空格，嘗試將每個字元轉換為數字
            if not player_cards:
                for char in player_cards_input:
                    try:
                        num = int(char)
                        if 0 <= num <= 9:  # 確保牌值在有效範圍內
                            player_cards.append(num)
                        else:
                            return jsonify({'success': False, 'message': f'閒家牌值必須在0-9之間，發現無效值: {num}'})
                    except ValueError:
                        # 忽略非數字字元
                        pass
        elif isinstance(player_cards_input, list):
            # 如果已經是列表，直接使用
            player_cards = player_cards_input
       
        print(f"處理後 - 莊家牌: {banker_cards}, 閒家牌: {player_cards}")
       
        # 確保有牌可分析
        if not banker_cards or not player_cards:
            return jsonify({'success': False, 'message': '請輸入有效的牌值'})
       
        # 呼叫公式計算邏輯
        banker_frequency = card_formula.calculate_banker_frequency(banker_cards)
        player_frequency = card_formula.calculate_player_frequency(player_cards)
       
        # 計算優勢牌值
        banker_advantage = card_formula.calculate_advantage_value(banker_cards)
        player_advantage = card_formula.calculate_advantage_value(player_cards)
       
        # 確定赫茲結果
        hertz_result = '無預測'  # 預設值
       
        if banker_frequency > player_frequency:
            hertz_result = '莊家'
        elif player_frequency > banker_frequency:
            hertz_result = '閒家'
        else:
            # 如果頻率相同，比較優勢值
            if banker_advantage > player_advantage:
                hertz_result = '莊家'
            elif player_advantage > banker_advantage:
                hertz_result = '閒家'
            else:
                hertz_result = '和局'
       
        # 計算和局頻率 (如果您的公式支援)
        tie_frequency = 0  # 預設值，根據您的邏輯可能需要調整
       
        return jsonify({
            'success': True,
            'banker_frequency': banker_frequency,
            'player_frequency': player_frequency,
            'tie_frequency': tie_frequency,
            'banker_advantage': banker_advantage,
            'player_advantage': player_advantage,
            'hertz_result': hertz_result
        })
    except Exception as e:
        import traceback
        print(f"分析公式時出錯: {str(e)}")
        traceback.print_exc()  # 列印詳細錯誤資訊
        return jsonify({'success': False, 'message': f'計算公式結果失敗: {str(e)}'})

@app.route('/api/formula/calculate', methods=['POST'])
def calculate_formula():
    """计算公式"""
    try:
        data = request.json
        print(f"接收到的原始数据: {data}")
       
        # 处理连续输入的字符串
        banker_cards_input = data.get('banker_cards', '')
        player_cards_input = data.get('player_cards', '')
       
        # 将输入转换为数字列表
        banker_cards = []
        player_cards = []
       
        # 处理庄家牌
        if isinstance(banker_cards_input, str):
            # 先尝试按空格分割
            if ' ' in banker_cards_input:
                try:
                    banker_cards = [int(num) for num in banker_cards_input.split()]
                    # 验证数字范围
                    for num in banker_cards:
                        if not 0 <= num <= 9:
                            return jsonify({'success': False, 'message': f'庄家牌值必须在0-9之间，发现无效值: {num}'})
                except ValueError:
                    banker_cards = []  # 重置，使用下面的字符解析方法
           
            # 如果空格分割失败或没有空格，尝试将每个字符转换为数字
            if not banker_cards:
                for char in banker_cards_input:
                    try:
                        num = int(char)
                        if 0 <= num <= 9:  # 确保牌值在有效范围内
                            banker_cards.append(num)
                        else:
                            return jsonify({'success': False, 'message': f'庄家牌值必须在0-9之间，发现无效值: {num}'})
                    except ValueError:
                        # 忽略非数字字符
                        pass
       
        # 处理闲家牌 (同样的逻辑)
        if isinstance(player_cards_input, str):
            # 先尝试按空格分割
            if ' ' in player_cards_input:
                try:
                    player_cards = [int(num) for num in player_cards_input.split()]
                    # 验证数字范围
                    for num in player_cards:
                        if not 0 <= num <= 9:
                            return jsonify({'success': False, 'message': f'闲家牌值必须在0-9之间，发现无效值: {num}'})
                except ValueError:
                    player_cards = []  # 重置，使用下面的字符解析方法
           
            # 如果空格分割失败或没有空格，尝试将每个字符转换为数字
            if not player_cards:
                for char in player_cards_input:
                    try:
                        num = int(char)
                        if 0 <= num <= 9:  # 确保牌值在有效范围内
                            player_cards.append(num)
                        else:
                            return jsonify({'success': False, 'message': f'闲家牌值必须在0-9之间，发现无效值: {num}'})
                    except ValueError:
                        # 忽略非数字字符
                        pass
       
        print(f"处理后 - 庄家牌: {banker_cards}, 闲家牌: {player_cards}")
       
        # 确保有牌可分析
        if not banker_cards or not player_cards:
            return jsonify({'success': False, 'message': '请输入有效的牌值'})
       
        # 計算百家樂點數
        banker_points = sum(banker_cards) % 10
        player_points = sum(player_cards) % 10
       
        # 呼叫公式計算邏輯
        banker_frequency = card_formula.calculate_banker_frequency(banker_cards)
        player_frequency = card_formula.calculate_player_frequency(player_cards)
        
        # 計算優勢值
        banker_advantage = card_formula.calculate_advantage_value(banker_cards)
        player_advantage = card_formula.calculate_advantage_value(player_cards)
       
        # 確定預測結果
        if banker_frequency > player_frequency:
            prediction = '莊家'
            confidence = min(100, abs(banker_frequency - player_frequency) * 10)
        elif player_frequency > banker_frequency:
            prediction = '閒家'
            confidence = min(100, abs(player_frequency - banker_frequency) * 10)
        else:
            # 如果頻率相同，比較優勢值
            if banker_advantage > player_advantage:
                prediction = '莊家'
                confidence = min(100, abs(banker_advantage - player_advantage) * 5)
            elif player_advantage > banker_advantage:
                prediction = '閒家'
                confidence = min(100, abs(player_advantage - banker_advantage) * 5)
            else:
                prediction = '和局'
                confidence = 50
       
        # 在返回的JSON中包含所有计算结果
        return jsonify({
            'success': True,
            'banker_points': banker_points,
            'player_points': player_points,
            'banker_frequency': banker_frequency,
            'player_frequency': player_frequency,
            'banker_advantage': banker_advantage,
            'player_advantage': player_advantage,
            'prediction': prediction,
            'confidence': confidence
        })
    except Exception as e:
        import traceback
        print(f"計算公式時出錯: {str(e)}")
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'計算公式結果失敗: {str(e)}'})

@app.route('/api/history/add_with_cards', methods=['POST'])
def add_result_with_cards():
    """新增遊戲結果（含牌型）"""
    global game_history
   
    data = request.json
    result = data.get('result')
    banker_cards = data.get('banker_cards', [])
    player_cards = data.get('player_cards', [])
   
    if not result:
        return jsonify({
            'success': False,
            'message': '結果不能為空'
        })
   
    # 獲取當前時間
    current_time = time.strftime("%Y-%m-%d %H:%M:%S")
   
    # 獲取當前局數
    round_number = len(game_history) + 1
   
    # 獲取預測結果
    ai_prediction = "無"
    formula_prediction = "無"
   
    # 如果有足夠的歷史記錄，進行AI預測
    if ai_model.is_trained and len(game_history) >= 10:
        history = [record['result'] for record in game_history]
        ai_prediction, _ = ai_model.predict(history)
   
    # 使用牌型進行公式預測
    try:
        # 計算頻率
        banker_frequency = card_formula.calculate_banker_frequency(banker_cards)
        player_frequency = card_formula.calculate_player_frequency(player_cards)
       
        # 計算優劣勢牌值
        banker_advantage = card_formula.calculate_advantage_value(banker_cards)
        player_advantage = card_formula.calculate_advantage_value(player_cards)
       
        # 公式結果
        if banker_frequency > player_frequency:
            formula_prediction = "莊"
        elif player_frequency > banker_frequency:
            formula_prediction = "閒"
        else:
            # 如果頻率相同，使用優勢值決定
            if banker_advantage > player_advantage:
                formula_prediction = "莊"
            elif player_advantage > banker_advantage:
                formula_prediction = "閒"
            else:
                formula_prediction = "和"
    except:
        formula_prediction = "無"
   
    # 建立遊戲記錄
    game_record = {
        "round": round_number,
        "result": result,
        "time": current_time,
        "ai_prediction": ai_prediction,
        "formula_prediction": formula_prediction,
        "banker_cards": banker_cards,
        "player_cards": player_cards
    }
   
    # 新增到歷史記錄
    game_history.append(game_record)
   
    # 更新牌靴
    is_new_shoe = shoe_manager.add_result(result)
   
    # 計算統計資料
    statistics = calculate_statistics()
   
    return jsonify({
        'success': True,
        'record': game_record,
        'statistics': statistics,
        'is_new_shoe': is_new_shoe,
        'shoe_info': {
            'shoe_id': shoe_manager.get_current_shoe_id(),
            'cards_remaining': shoe_manager.get_remaining_cards_count(),
            'cards_used': shoe_manager.get_used_cards_count(),
                        'is_in_warmup': shoe_manager.is_in_warmup_period(),
            'warmup_progress': shoe_manager.get_warmup_progress(),
            'statistics': shoe_manager.get_shoe_statistics()
        }
    })

@app.route('/api/history/get', methods=['GET'])
def get_history():
    """獲取遊戲歷史記錄"""
    return jsonify({
        'success': True,
        'history': game_history
    })

@app.route('/api/history/import', methods=['POST'])
def import_history():
    """匯入遊戲歷史記錄"""
    global game_history
   
    data = request.json
    history = data.get('history', [])
   
    if not history:
        return jsonify({
            'success': False,
            'message': '歷史記錄不能為空'
        })
   
    # 更新歷史記錄
    game_history = history
   
    # 重置牌靴並新增所有結果
    shoe_manager.reset_all()
    for record in history:
        shoe_manager.add_result(record.get('result', ''))
   
    return jsonify({
        'success': True,
        'message': f'已匯入 {len(history)} 筆歷史記錄',
        'shoe_info': {
            'shoe_id': shoe_manager.get_current_shoe_id(),
            'cards_remaining': shoe_manager.get_remaining_cards_count(),
            'cards_used': shoe_manager.get_used_cards_count(),
            'is_in_warmup': shoe_manager.is_in_warmup_period(),
            'warmup_progress': shoe_manager.get_warmup_progress(),
            'statistics': shoe_manager.get_shoe_statistics()
        }
    })

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)


