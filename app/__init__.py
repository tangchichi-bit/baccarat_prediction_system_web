from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS

# 创建Flask应用
app = Flask(__name__)
app.config['SECRET_KEY'] = 'baccarat-prediction-system'
socketio = SocketIO(app)
CORS(app)  # 启用CORS支持

# 导入路由
from app import routes
