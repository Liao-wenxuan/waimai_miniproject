"""应用配置"""
import os


class Config:
    # MySQL 数据库连接
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'mysql+pymysql://root:213546@localhost:3306/food_delivery?charset=utf8mb4'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'connect_args': {'charset': 'utf8mb4'}
    }

    # JWT 密钥
    SECRET_KEY = os.environ.get('SECRET_KEY', 'food-delivery-secret-key-2024')

    # SocketIO 配置
    SOCKETIO_MESSAGE_QUEUE = None

    # 高德地图 API Key（前端也需配置）
    AMAP_KEY = os.environ.get('AMAP_KEY', 'b088bfacf1f1d34edb868779d2075a54')

    # 上传配置
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static/uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
