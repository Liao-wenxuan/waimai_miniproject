"""JWT 认证相关"""
import jwt
import datetime
from functools import wraps
from flask import request, jsonify, g
from config import Config


def generate_token(user_id, role='user'):
    """生成 JWT token"""
    payload = {
        'user_id': user_id,
        'role': role,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=7),
        'iat': datetime.datetime.utcnow()
    }
    return jwt.encode(payload, Config.SECRET_KEY, algorithm='HS256')


def decode_token(token):
    """解析 JWT token"""
    try:
        payload = jwt.decode(token, Config.SECRET_KEY, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def login_required(f):
    """登录验证装饰器"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return jsonify({'code': 401, 'msg': '请先登录', 'data': None})
        payload = decode_token(token)
        if not payload:
            return jsonify({'code': 401, 'msg': '登录已过期，请重新登录', 'data': None})
        g.user_id = payload['user_id']
        g.role = payload['role']
        return f(*args, **kwargs)
    return decorated


def role_required(role):
    """角色验证装饰器"""
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = request.headers.get('Authorization', '').replace('Bearer ', '')
            if not token:
                return jsonify({'code': 401, 'msg': '请先登录', 'data': None})
            payload = decode_token(token)
            if not payload:
                return jsonify({'code': 401, 'msg': '登录已过期', 'data': None})
            if payload.get('role') != role:
                return jsonify({'code': 403, 'msg': '权限不足', 'data': None})
            g.user_id = payload['user_id']
            g.role = payload['role']
            return f(*args, **kwargs)
        return decorated
    return decorator
