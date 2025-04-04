import eventlet
eventlet.monkey_patch()

from app import app, socketio

if __name__ == '__main__':
    print("服务器启动在 http://localhost:5000")
    print("注册的路由:")
    for rule in app.url_map.iter_rules():
        print(f"{rule.endpoint}: {rule.rule}")
   
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
