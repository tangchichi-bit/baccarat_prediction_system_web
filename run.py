from app import app, socketio

if __name__ == '__main__':
    print("啟動百家樂 AI 預測與算牌系統...")
    print("請在瀏覽器中訪問: http://localhost:5000/")
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)

