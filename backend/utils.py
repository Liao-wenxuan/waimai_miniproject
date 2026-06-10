"""工具函数"""
import math
import hashlib


def hash_password(password):
    """密码哈希"""
    return hashlib.sha256(password.encode()).hexdigest()


def calc_distance(lat1, lng1, lat2, lng2):
    """
    计算两点间的直线距离（Haversine 公式）
    返回单位：公里
    """
    lat1, lng1 = float(lat1), float(lng1)
    lat2, lng2 = float(lat2), float(lng2)
    R = 6371.0  # 地球半径(km)
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlng / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 3)


def format_datetime(dt):
    """格式化日期时间"""
    if dt is None:
        return None
    return dt.strftime('%Y-%m-%d %H:%M:%S')


def success(data=None, msg='success'):
    """统一成功响应"""
    return {'code': 200, 'data': data, 'msg': msg}


def error(msg='error', code=400):
    """统一错误响应"""
    return {'code': code, 'data': None, 'msg': msg}
