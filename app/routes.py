from flask import render_template, jsonify, request
from app import app, socketio
from app.models.ai_model import BaccaratAIModel
from app.models.shoe_manager import ShoeManager  # 新增牌靴管理器
from app.models.formula_calculator import FormulaCalculator  # 新增算牌公式計算器

# 建立例項
ai_model = BaccaratAIModel()
shoe_manager = ShoeManager()
formula_calculator = FormulaCalculator()
game_history = []

@app.route('/')
def index():
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


@app.route('/api/train', methods=['POST'])
def train():
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
    return jsonify({
        'cards_remaining': shoe_manager.get_remaining_cards(),
        'banker_probability': shoe_manager.calculate_banker_probability(),
        'player_probability': shoe_manager.calculate_player_probability(),
        'tie_probability': shoe_manager.calculate_tie_probability()
    })

@app.route('/api/shoe/reset', methods=['POST'])
def reset_shoe():
    data = request.json
    num_decks = data.get('num_decks', 8)
    shoe_manager.reset(num_decks)
    return jsonify({'success': True, 'message': f'已重置牌靴，使用 {num_decks} 副牌'})

@app.route('/api/shoe/draw', methods=['POST'])
def draw_cards():
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
    return jsonify({'history': game_history})

@app.route('/api/history/add', methods=['POST'])
def add_result():
    global game_history
    data = request.json
    result = data.get('result')
    
    if not result:
        return jsonify({'success': False, 'message': '結果不能為空'})
    
    # 獲取當前時間
    from datetime import datetime
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
    global game_history
    game_history = []
    
    return jsonify({
        'success': True,
        'message': '已清空所有記錄'
    })

@app.route('/api/statistics', methods=['GET'])
def get_statistics():
    return jsonify(calculate_statistics())

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
