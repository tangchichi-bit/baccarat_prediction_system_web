#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
百家樂 AI 預測模型實現
"""

import random
import numpy as np
import time
import threading
import traceback  # 新增這一行
from sklearn.ensemble import RandomForestClassifier
import tkinter as tk
from tkinter import ttk, Toplevel, StringVar


class BaccaratAIModel:
    """百家樂 AI 預測模型類別"""
   
    def __init__(self):
        """初始化 AI 模型"""
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.is_trained = False
   
    def _prepare_features(self, history):
        """準備特徵資料"""
        features = []
        labels = []
       
        # 使用過去 10 局作為特徵，預測下一局
        window_size = 10
       
        # 列印除錯資訊
        print(f"準備特徵，歷史記錄長度={len(history)}")
        print(f"歷史記錄樣本: {history[:min(5, len(history))]}")
       
        for i in range(len(history) - window_size):
            window = history[i:i+window_size]
           
            # 將結果轉換為數值特徵
            feature = []
            for result in window:
                # 確保處理字串結果
                if isinstance(result, str):
                    if "莊" in result:
                        feature.append(1)
                    elif "閒" in result:
                        feature.append(2)
                    else:  # 和局
                        feature.append(0)
                else:
                    # 如果結果不是字串，嘗試直接使用
                    feature.append(result)
           
            features.append(feature)
           
            # 下一局結果作為標籤
            next_result = history[i+window_size]
            if isinstance(next_result, str):
                if "莊" in next_result:
                    labels.append(1)
                elif "閒" in next_result:
                    labels.append(2)
                else:  # 和局
                    labels.append(0)
            else:
                # 如果結果不是字串，嘗試直接使用
                labels.append(next_result)
       
        # 列印除錯資訊
        if features:
            print(f"特徵樣本: {features[0]}")
            print(f"標籤樣本: {labels[0]}")
       
        return np.array(features), np.array(labels)

    def train(self, history):
        """訓練模型"""
        if len(history) <= 10:
            print("歷史記錄不足，無法訓練")
            return False
       
        try:
            X, y = self._prepare_features(history)
           
            if len(X) == 0:
                print("無法準備特徵，無法訓練")
                return False
           
            print(f"訓練資料: X形狀={X.shape}, y形狀={len(y)}")
            print(f"訓練資料樣本: X[0]={X[0]}, y[0]={y[0]}")
           
            # 訓練模型
            self.model.fit(X, y)
            self.is_trained = True
           
            # 列印模型資訊
            print(f"模型已訓練，類別={self.model.classes_}")
           
            return True
        except Exception as e:
            print(f"訓練出錯: {str(e)}")
            traceback.print_exc()  # 列印完整錯誤堆疊
            return False

    def predict(self, history):
        """預測下一局結果"""
        if not self.is_trained or len(history) < 10:
            return "無法預測", 0
       
        try:
            # 取最近 10 局作為特徵
            recent = history[-10:]
           
            # 將結果轉換為數值特徵
            feature = []
            for result in recent:
                # 統一處理各種可能的結果格式
                if isinstance(result, str):
                    if "莊" in result:
                        feature.append(1)
                    elif "閒" in result:
                        feature.append(2)
                    else:  # 和局
                        feature.append(0)
                else:
                    # 如果結果不是字串，嘗試直接使用
                    feature.append(result)
           
            # 進行預測
            prediction = self.model.predict([feature])[0]
            probabilities = self.model.predict_proba([feature])[0]
           
            # 列印除錯資訊
            print(f"預測結果: {prediction}")
            print(f"機率分佈: {probabilities}")
            print(f"機率分佈大小: {len(probabilities)}")
            print(f"模型類別: {self.model.classes_}")
           
            # 轉換預測結果
            result = "無法預測"
            confidence = 0
            
            # 根據預測值確定結果
            if prediction == 1:
                result = "莊家"
            elif prediction == 2:
                result = "閒家"
            else:
                result = "和局"
                
            # 查詢對應類別的機率
            for i, cls in enumerate(self.model.classes_):
                if cls == prediction:
                    confidence = probabilities[i] * 100
                    break
           
            # 如果無法確定信心度，使用最高機率
            if confidence == 0:
                confidence = max(probabilities) * 100
           
            return result, confidence
        except Exception as e:
            print(f"預測出錯: {str(e)}")
            traceback.print_exc()  # 列印完整錯誤堆疊
            return "預測錯誤", 0
   
    def simple_predict(self, player_points, banker_points):
        """簡單預測方法，用於與算牌公式比較"""
        # 這是一個簡化的預測方法，實際應用中應該使用更複雜的模型
        # 這裡僅作為示例
       
        # 計算點數總和
        player_sum = sum(player_points)
        banker_sum = sum(banker_points)
       
        # 簡單規則：點數總和較大的一方獲勝機率較高
        if player_sum > banker_sum:
            return "閒"
        else:
            return "莊"


# 注意：這些類別應該在 BaccaratAIModel 類別外部定義
class AITrainingManager:
    """AI 模型訓練管理器"""
   
    def __init__(self, ai_model, history_data, accuracy_threshold=0.7):
        """初始化訓練管理器
       
        Args:
            ai_model: AI 模型例項
            history_data: 歷史資料提供者（通常是 AIModeFrame 例項）
            accuracy_threshold: 觸發訓練的準確率閾值
        """
        self.ai_model = ai_model
        self.history_data = history_data
        self.accuracy_threshold = accuracy_threshold
        self.last_user_action_time = time.time()
        self.is_training = False
        self.training_scheduled = False
       
    def update_user_action_time(self):
        """更新使用者最後操作時間"""
        self.last_user_action_time = time.time()
       
    def check_accuracy(self):
        """檢查最近預測準確率"""
        # 獲取最近的預測記錄
        recent_predictions = self._get_recent_predictions(20)
        if not recent_predictions or len(recent_predictions) < 10:
            return True  # 資料不足，不觸發訓練
           
        correct_count = sum(1 for pred in recent_predictions if pred["correct"])
        accuracy = correct_count / len(recent_predictions)
       
        return accuracy >= self.accuracy_threshold
   
    def _get_recent_predictions(self, count):
        """獲取最近的預測記錄
       
        這個方法需要根據實際的歷史資料結構來實現
        """
        if hasattr(self.history_data, 'get_recent_predictions'):
            return self.history_data.get_recent_predictions(count)
       
        # 如果歷史資料提供者沒有提供專門的方法，則嘗試從 local_history 獲取
        if hasattr(self.history_data, 'local_history'):
            recent = self.history_data.local_history[-count:] if len(self.history_data.local_history) > count else self.history_data.local_history
            return [{"prediction": item.get("ai_prediction", ""),
                    "result": item.get("result", ""),
                    "correct": item.get("ai_prediction") == item.get("result")}
                    for item in recent]
       
        # 如果都無法獲取，返回空列表
        return []
       
    def should_start_training(self):
        """判斷是否應該開始訓練"""
        # 如果已經在訓練或已排程訓練，則不重複觸發
        if self.is_training or self.training_scheduled:
            return False
           
        # 檢查準確率是否低於閾值
        if not self.check_accuracy():
            # 檢查使用者是否處於非活動狀態（30秒無操作）
            if time.time() - self.last_user_action_time > 30:
                return True
               
        return False
       
    def schedule_training(self, parent_widget):
        """排程訓練任務"""
        self.training_scheduled = True
       
        # 顯示訓練通知
        notification = TrainingNotification(parent_widget,
                                        cancel_callback=self.cancel_training)
       
        # 5秒後如果未取消則開始訓練
        parent_widget.after(5000, self.start_training_if_scheduled)
       
    def cancel_training(self):
        """取消排程的訓練"""
        self.training_scheduled = False
       
    def start_training_if_scheduled(self):
        """如果訓練仍在排程中則開始訓練"""
        if self.training_scheduled:
            self.start_training()
           
    def start_training(self):
        """開始模型訓練"""
        self.is_training = True
        self.training_scheduled = False
       
        # 在背景執行緒中訓練模型
        threading.Thread(target=self._train_model_thread, daemon=True).start()
       
    def _train_model_thread(self):
        """模型訓練執行緒"""
        try:
            # 獲取訓練資料
            if hasattr(self.history_data, 'history'):
                training_data = self.history_data.history
            else:
                training_data = []
               
            # 執行模型訓練
            if training_data:
                training_success = self.ai_model.train(training_data)
               
                # 訓練完成後的回撥
                if hasattr(self.history_data, 'after') and hasattr(self.history_data, '_update_after_training'):
                    self.history_data.after(0, lambda: self.history_data._update_after_training(training_success))
        except Exception as e:
            print(f"訓練過程中發生錯誤: {str(e)}")
            traceback.print_exc()  # 新增這一行
        finally:
            self.is_training = False


class TrainingNotification(Toplevel):
    """訓練通知對話方塊"""
   
    def __init__(self, parent, cancel_callback=None):
        """初始化通知對話方塊"""
        super().__init__(parent)
        self.title("AI訓練通知")
        self.geometry("300x150")
        self.resizable(False, False)
        self.transient(parent)
       
        self.cancel_callback = cancel_callback
       
        # 設定UI元件
        ttk.Label(self, text="AI模型準確率下降",
                font=("微軟正黑體", 12, "bold")).pack(pady=10)
        ttk.Label(self, text="系統將在5秒後自動開始訓練模型").pack(pady=5)
       
        self.countdown_var = StringVar(value="5")
        ttk.Label(self, textvariable=self.countdown_var).pack(pady=5)
       
        ttk.Button(self, text="取消", command=self._cancel).pack(pady=10)
       
        # 開始倒數
        self._countdown(5)
   
    def _countdown(self, count):
        """倒數計時"""
        if count > 0:
            self.countdown_var.set(str(count))
            self.after(1000, lambda: self._countdown(count-1))
        else:
            self.destroy()
   
    def _cancel(self):
        """取消訓練"""
        if self.cancel_callback:
            self.cancel_callback()
        self.destroy()
