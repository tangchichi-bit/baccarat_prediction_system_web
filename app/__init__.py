from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS

# 建立Flask應用
app = Flask(__name__)
app.config['SECRET_KEY'] = 'baccarat-prediction-system'
socketio = SocketIO(app)
CORS(app)  # 啟用CORS支援

# 匯入路由
from app import routes
