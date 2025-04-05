# 百家樂預測系統

一個基於Flask的百家樂AI預測與算牌系統，提供Web介面訪問。

## 功能特點

- AI預測模式：使用機器學習演演算法分析歷史資料，預測下一局結果
- 算牌公式模式：使用傳統百家樂算牌公式，根據當前牌點預測結果
- 歷史記錄管理：記錄遊戲結果，支援匯入匯出
- 路單顯示：直觀展示遊戲走勢
- 統計分析：計算預測準確率和結果分佈
- 實時更新：使用WebSocket技術實現實時資料更新

## 安裝與執行

### 使用Python直接執行

1. 克隆倉庫
   ```bash
   git clone https://github.com/yourusername/baccarat-prediction-system.git
   cd baccarat-prediction-system
   ```

2. 建立虛擬環境並安裝依賴
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. 執行應用
   ```bash
   python run.py
   ```

4. 在瀏覽器中訪問 http://localhost:5000

### 使用Docker執行

1. 構建Docker映象
   ```bash
   docker build -t baccarat-prediction-system .
   ```

2. 執行Docker容器
   ```bash
   docker run -p 5000:5000 baccarat-prediction-system
   ```

3. 在瀏覽器中訪問 http://localhost:5000

## 使用說明

### AI預測模式

1. 新增遊戲結果（莊家/閒家/和局）
2. 積累足夠的歷史記錄後，點選"訓練模型"
3. 訓練完成後，點選"預測下一局"獲取AI預測結果

### 算牌公式模式

1. 輸入當前局的莊家和閒家點數
2. 點選"計算"獲取頻率和預測結果
3. 根據預測結果和實際情況新增遊戲結果

## 技術棧

- 後端：Flask, Flask-SocketIO, scikit-learn
- 前端：HTML, CSS, JavaScript, Bootstrap, Chart.js
- 資料儲存：JSON檔案（可擴充套件為資料庫）

## 許可證

MIT
