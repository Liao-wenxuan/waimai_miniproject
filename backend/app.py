"""Flask 主入口"""
import logging
from flask import Flask, jsonify
from flask_socketio import SocketIO
from flask_cors import CORS
from config import Config
from models import db

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# 创建应用
app = Flask(__name__)
app.config.from_object(Config)

# 初始化扩展
db.init_app(app)
CORS(app, supports_credentials=True)
socketio = SocketIO(app, cors_allowed_origins='*', async_mode='threading')

# 将 socketio 实例注入到 socket_events 模块（避免循环导入）
import socket_events
socket_events.socketio = socketio

# 注册 WebSocket 事件
socket_events.register_socket_events(socketio)

# 注册路由蓝图
from routes.user import user_bp
from routes.merchant import merchant_bp
from routes.rider import rider_bp
from routes.admin import admin_bp

app.register_blueprint(user_bp)
app.register_blueprint(merchant_bp)
app.register_blueprint(rider_bp)
app.register_blueprint(admin_bp)


# ---------- 全局错误处理（确保返回 JSON，不是 HTML） ----------
@app.errorhandler(400)
def bad_request(e):
    return jsonify({'code': 400, 'data': None, 'msg': '请求参数错误'}), 400


@app.errorhandler(401)
def unauthorized(e):
    return jsonify({'code': 401, 'data': None, 'msg': '未授权，请先登录'}), 401


@app.errorhandler(403)
def forbidden(e):
    return jsonify({'code': 403, 'data': None, 'msg': '权限不足'}), 403


@app.errorhandler(404)
def not_found(e):
    return jsonify({'code': 404, 'data': None, 'msg': '接口不存在'}), 404


@app.errorhandler(500)
def internal_error(e):
    logger.error(f'500 Internal Server Error: {e}', exc_info=True)
    return jsonify({'code': 500, 'data': None, 'msg': '服务器内部错误，请查看后端日志'}), 500


@app.route('/api/health')
def health():
    """健康检查 + 数据库连通性"""
    try:
        db.session.execute(db.text('SELECT 1'))
        db_ok = True
    except Exception as e:
        db_ok = False
        logger.error(f'Database health check failed: {e}')

    return {
        'code': 200,
        'msg': 'ok' if db_ok else 'database unreachable',
        'data': {'database': 'connected' if db_ok else 'disconnected'}
    }


if __name__ == '__main__':
    logger.info('Starting Food Delivery backend...')
    with app.app_context():
        logger.info('Creating database tables...')
        db.create_all()
        from seed import seed_data
        seed_data()
    logger.info('Backend running on http://0.0.0.0:5000')
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
