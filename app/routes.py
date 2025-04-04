#後端程式碼（Flask路由）

from flask import render_template, jsonify, request
from app import app, socketio
from app.models.ai_model import BaccaratAIModel
from app.models.shoe_manager import ShoeManager
from app.models.formula_calculator import FormulaCalculator
from datetime import datetime

# 建立例項
ai_model = BaccaratAIModel()
shoe_manager = ShoeManager()
formula_calculator = FormulaCalculator()
game_history = []

@app.route('/')
def index():
    """首頁"""
    return render_template('index.html')

@app.route('/api/predict', methods=['POST'])
def predict_next():
    """預測下一局結果"""
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
   
    # 算牌公式預測
    formula_result = "無法預測"
    formula_confidence = 0
   
    if len(history) >= 5:
        try:
            formula_result, formula_confidence = formula_calculator.predict(history)
        except Exception as e:
            print(f"公式預測錯誤: {str(e)}")
            formula_result = "預測錯誤"
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

@app.route('/api/predict/ai', methods=['POST'])
def predict_ai():
    """AI預測下一局結果"""
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
   
    return jsonify({
        'success': True,
        'prediction': ai_result,
        'confidence': ai_confidence
    })

@app.route('/api/train', methods=['POST'])
def train():
    """訓練AI模型"""
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
            'message': '訓練失敗，請檢查歷史資料'
        })

@app.route('/api/shoe', methods=['GET'])
def get_shoe_status():
    """獲取牌靴狀態"""
    return jsonify({
        'cards_remaining': shoe_manager.get_remaining_cards(),
        'banker_probability': shoe_manager.calculate_banker_probability(),
        'player_probability': shoe_manager.calculate_player_probability(),
        'tie_probability': shoe_manager.calculate_tie_probability()
    })

@app.route('/api/shoe/reset', methods=['POST'])
def reset_shoe():
    """重置牌靴"""
    data = request.json
    num_decks = data.get('num_decks', 8)
    shoe_manager.reset(num_decks)
    return jsonify({'success': True, 'message': f'已重置牌靴，使用 {num_decks} 副牌'})

@app.route('/api/shoe/draw', methods=['POST'])
def draw_cards():
    """從牌靴中抽牌"""
    data = request.json
    banker_cards = data.get('banker_cards', [])
    player_cards = data.get('player_cards', [])
   
    # 從牌靴中移除這些牌
    for card in banker_cards + player_cards:
        shoe_manager.remove_card(card)
   
    return jsonify({
        'success': True,
        'cards_remaining': shoe_manager.get_remaining_cards()
    })

@app.route('/api/history', methods=['GET'])
def get_history():
    """獲取歷史記錄"""
    return jsonify({'history': game_history})

@app.route('/api/history/add', methods=['POST'])
def add_result():
    """新增遊戲結果"""
    global game_history
    data = request.json
    result = data.get('result')
   
    if not result:
        return jsonify({'success': False, 'message': '結果不能為空'})
   
    # 獲取當前時間
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
   
    # 獲取當前局數
    round_number = len(game_history) + 1
   
    # 獲取預測結果
    history_results = [record['result'] for record in game_history]
   
    # AI預測
    ai_prediction = "無法預測"
    if ai_model.is_trained and len(history_results) >= 10:
        ai_prediction, _ = ai_model.predict(history_results)
   
    # 算牌公式預測
    formula_prediction = "無法預測"
    if len(history_results) >= 5:
        formula_prediction, _ = formula_calculator.predict(history_results)
   
    # 建立記錄
    record = {
        'round': round_number,
        'result': result,
        'time': current_time,
        'ai_prediction': ai_prediction,
        'formula_prediction': formula_prediction
    }
   
    # 新增到歷史記錄
    game_history.append(record)
   
    # 計算統計資料
    statistics = calculate_statistics()
   
    return jsonify({
        'success': True,
        'record': record,
        'statistics': statistics
    })

@app.route('/api/history/undo', methods=['POST'])
def undo_last():
    """撤銷上一局結果"""
    global game_history
    if not game_history:
        return jsonify({'success': False, 'message': '沒有可撤銷的記錄'})
   
    game_history.pop()
    statistics = calculate_statistics()
   
    return jsonify({
        'success': True,
        'history': game_history,
        'statistics': statistics
    })

@app.route('/api/history/clear', methods=['POST'])
def clear_history():
    """清空所有記錄"""
    global game_history
    game_history = []
   
    return jsonify({
        'success': True,
        'message': '已清空所有記錄'
    })

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    """獲取統計資料"""
    return jsonify(calculate_statistics())

# 新增的公式計算路由
@app.route('/api/formula/calculate', methods=['POST'])
def calculate_formula():
    """計算公式"""
    try:
        data = request.json
        print(f"接收到的原始數據: {data}")  # 調試信息
        
        # 獲取輸入數據
        banker_cards_input = data.get('banker_cards', '')
        player_cards_input = data.get('player_cards', '')
        
        # 檢查輸入是否為空
        if not banker_cards_input or not player_cards_input:
            return jsonify({
                'success': False,
                'message': '請輸入莊家和閒家的牌型'
            })
        
        # 處理不同類型的輸入
        banker_cards = []
        player_cards = []
        
        # 處理banker_cards_input
        if isinstance(banker_cards_input, list):
            # 如果已經是列表，嘗試將每個元素轉換為整數
            try:
                banker_cards = [int(card) for card in banker_cards_input if card != '']
            except (ValueError, TypeError):
                return jsonify({
                    'success': False,
                    'message': '莊家牌值必須是數字 (0-9)'
                })
        elif isinstance(banker_cards_input, str):
            # 如果是字符串，移除所有空格並逐個字符轉換
            banker_cards_input = banker_cards_input.replace(" ", "")
            try:
                banker_cards = [int(card) for card in banker_cards_input]
            except ValueError:
                return jsonify({
                    'success': False,
                    'message': '莊家牌值必須是數字 (0-9)'
                })
        else:
            # 其他類型，嘗試轉換為字符串後處理
            try:
                banker_cards_input = str(banker_cards_input).replace(" ", "")
                banker_cards = [int(card) for card in banker_cards_input]
            except ValueError:
                return jsonify({
                    'success': False,
                    'message': '莊家牌值必須是數字 (0-9)'
                })
        
        # 處理player_cards_input
        if isinstance(player_cards_input, list):
            try:
                player_cards = [int(card) for card in player_cards_input if card != '']
            except (ValueError, TypeError):
                return jsonify({
                    'success': False,
                    'message': '閒家牌值必須是數字 (0-9)'
                })
        elif isinstance(player_cards_input, str):
            player_cards_input = player_cards_input.replace(" ", "")
            try:
                player_cards = [int(card) for card in player_cards_input]
            except ValueError:
                return jsonify({
                    'success': False,
                    'message': '閒家牌值必須是數字 (0-9)'
                })
        else:
            try:
                player_cards_input = str(player_cards_input).replace(" ", "")
                player_cards = [int(card) for card in player_cards_input]
            except ValueError:
                return jsonify({
                    'success': False,
                    'message': '閒家牌值必須是數字 (0-9)'
                })
        
        # 驗證牌值範圍 (百家樂中只有0-9的牌值)
        for card in banker_cards + player_cards:
            if card < 0 or card > 9:
                return jsonify({
                    'success': False,
                    'message': '牌值必須在0-9範圍內 (10/J/Q/K輸入為0)'
                })
        
        # 列印處理後的數據，用於除錯
        print(f"處理後 - 莊家牌: {banker_cards}, 閒家牌: {player_cards}")
        
        # 計算百家樂點數
        banker_points = sum(banker_cards) % 10
        player_points = sum(player_cards) % 10
        
        # 呼叫公式計算邏輯
        banker_frequency = formula_calculator.calculate_banker_frequency(banker_cards)
        player_frequency = formula_calculator.calculate_player_frequency(player_cards)
        
        # 確定預測結果
        prediction = '無預測'  # 預設值
        
        if banker_frequency > player_frequency:
            prediction = '莊家'
        elif player_frequency > banker_frequency:
            prediction = '閒家'
        else:
            # 如果頻率相同，比較優勢值
            banker_advantage = formula_calculator.calculate_advantage_value(banker_cards)
            player_advantage = formula_calculator.calculate_advantage_value(player_cards)
            
            if banker_advantage > player_advantage:
                prediction = '莊家'
            elif player_advantage > banker_advantage:
                prediction = '閒家'
            else:
                prediction = '和局'
        
        return jsonify({
            'success': True,
            'banker_points': banker_points,
            'player_points': player_points,
            'banker_frequency': banker_frequency,
            'player_frequency': player_frequency,
            'formula_result': prediction,  # 修改為前端期望的字段名
            'formula_confidence': 80  # 添加一個置信度值
        })
    except Exception as e:
        import traceback
        print(f"計算公式時出錯: {str(e)}")
        traceback.print_exc()  # 列印詳細錯誤資訊
        return jsonify({'success': False, 'message': f'計算公式結果失敗: {str(e)}'})


@app.route('/api/formula/analyze', methods=['POST'])
def analyze_formula():
    """分析公式"""
    try:
        data = request.json
        print(f"接收到的原始數據: {data}")  # 調試信息
        
        # 獲取輸入數據
        banker_cards_input = data.get('banker_cards', '')
        player_cards_input = data.get('player_cards', '')
        
        # 檢查輸入是否為空
        if not banker_cards_input or not player_cards_input:
            return jsonify({
                'success': False,
                'message': '請輸入莊家和閒家的牌型'
            })
        
        # 處理不同類型的輸入
        banker_cards = []
        player_cards = []
        
        # 處理banker_cards_input
        if isinstance(banker_cards_input, list):
            try:
                banker_cards = [int(card) for card in banker_cards_input if card != '']
            except (ValueError, TypeError):
                return jsonify({
                    'success': False,
                    'message': '莊家牌值必須是數字 (0-9)'
                })
        elif isinstance(banker_cards_input, str):
            banker_cards_input = banker_cards_input.replace(" ", "")
            try:
                banker_cards = [int(card) for card in banker_cards_input]
            except ValueError:
                return jsonify({
                    'success': False,
                    'message': '莊家牌值必須是數字 (0-9)'
                })
        else:
            try:
                banker_cards_input = str(banker_cards_input).replace(" ", "")
                banker_cards = [int(card) for card in banker_cards_input]
            except ValueError:
                return jsonify({
                    'success': False,
                    'message': '莊家牌值必須是數字 (0-9)'
                })
        
        # 處理player_cards_input
        if isinstance(player_cards_input, list):
            try:
                player_cards = [int(card) for card in player_cards_input if card != '']
            except (ValueError, TypeError):
                return jsonify({
                    'success': False,
                    'message': '閒家牌值必須是數字 (0-9)'
                })
        elif isinstance(player_cards_input, str):
            player_cards_input = player_cards_input.replace(" ", "")
            try:
                player_cards = [int(card) for card in player_cards_input]
            except ValueError:
                return jsonify({
                    'success': False,
                    'message': '閒家牌值必須是數字 (0-9)'
                })
        else:
            try:
                player_cards_input = str(player_cards_input).replace(" ", "")
                player_cards = [int(card) for card in player_cards_input]
            except ValueError:
                return jsonify({
                    'success': False,
                    'message': '閒家牌值必須是數字 (0-9)'
                })
        
        # 驗證牌值範圍
        for card in banker_cards + player_cards:
            if card < 0 or card > 9:
                return jsonify({
                    'success': False,
                    'message': '牌值必須在0-9範圍內 (10/J/Q/K輸入為0)'
                })
        
        # 列印處理後的數據
        print(f"處理後 - 莊家牌: {banker_cards}, 閒家牌: {player_cards}")
        
        # 呼叫公式計算邏輯
        banker_frequency = formula_calculator.calculate_banker_frequency(banker_cards)
        player_frequency = formula_calculator.calculate_player_frequency(player_cards)
        
        # 計算優勢牌值
        banker_advantage = formula_calculator.calculate_advantage_value(banker_cards)
        player_advantage = formula_calculator.calculate_advantage_value(player_cards)
        
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
        
        # 計算和局頻率
        tie_frequency = 0  # 預設值
        
        return jsonify({
            'success': True,
            'banker_frequency': banker_frequency,
            'player_frequency': player_frequency,
            'tie_frequency': tie_frequency,
            'banker_advantage': banker_advantage,
            'player_advantage': player_advantage,
            'prediction': hertz_result  # 修改為統一的字段名
        })
    except Exception as e:
        import traceback
        print(f"分析公式時出錯: {str(e)}")
        traceback.print_exc()
        return jsonify({'success': False, 'message': f'計算公式結果失敗: {str(e)}'})


def calculate_statistics():
    """計算統計資料"""
    total_rounds = len(game_history)
    banker_count = sum(1 for record in game_history if record['result'] == '莊家')
    player_count = sum(1 for record in game_history if record['result'] == '閒家')
    tie_count = sum(1 for record in game_history if record['result'] == '和局')
   
    # 計算AI預測準確率
    ai_correct = 0
    ai_predictions = 0
   
    # 計算公式預測準確率
    formula_correct = 0
    formula_predictions = 0
   
    # 計算匹配率
    match_count = 0
    valid_predictions = 0
   
    for record in game_history:
        ai_pred = record.get('ai_prediction')
        formula_pred = record.get('formula_prediction')
        result = record.get('result')
       
        if ai_pred and ai_pred != '無法預測':
            ai_predictions += 1
            if ai_pred == result:
                ai_correct += 1
       
        if formula_pred and formula_pred != '無法預測':
            formula_predictions += 1
            if formula_pred == result:
                formula_correct += 1
       
        if ai_pred and formula_pred and ai_pred != '無法預測' and formula_pred != '無法預測':
            valid_predictions += 1
            if ai_pred == formula_pred:
                match_count += 1
   
    ai_accuracy = (ai_correct / ai_predictions * 100) if ai_predictions > 0 else 0
    formula_accuracy = (formula_correct / formula_predictions * 100) if formula_predictions > 0 else 0
    match_rate = (match_count / valid_predictions * 100) if valid_predictions > 0 else 0
   
    return {
        'total_rounds': total_rounds,
        'banker_count': banker_count,
        'player_count': player_count,
        'tie_count': tie_count,
        'ai_accuracy': ai_accuracy,
        'formula_accuracy': formula_accuracy,
        'match_rate': match_rate
    }

