"""骑手端 API"""
import datetime
import logging
from flask import Blueprint, request, jsonify, g
from models import db, Rider, Order, OrderItem, Merchant, User
from auth import generate_token, role_required
from utils import hash_password, calc_distance, success, error, format_datetime

logger = logging.getLogger(__name__)
rider_bp = Blueprint('rider', __name__)


def _rider_to_dict(r):
    """序列化骑手信息"""
    return {
        'id': r.id,
        'name': r.name,
        'phone': r.phone,
        'lng': float(r.lng),
        'lat': float(r.lat),
        'status': r.status
    }


@rider_bp.route('/api/rider/login', methods=['POST'])
def login():
    """骑手登录 — 支持 Demo 账号和真实密码验证"""
    try:
        data = request.get_json(silent=True) or {}
        username = (data.get('username') or '').strip()
        password = (data.get('password') or '').strip()

        if not username or not password:
            return error('请输入账号和密码')

        # ---------- Demo 测试账号 ----------
        if username == 'rider' and password == '123456':
            rider = Rider.query.first()
            if not rider:
                return error('暂无骑手数据，请先初始化数据库或运行 seed')
            token = generate_token(rider.id, 'rider')
            return success({'token': token, 'rider': _rider_to_dict(rider)}, '登录成功（Demo）')

        # ---------- 真实密码验证：用骑手姓名 / 手机号作为登录账号 ----------
        rider = Rider.query.filter(
            (Rider.name == username) | (Rider.phone == username)
        ).first()
        if not rider:
            return error('账号或密码错误')
        if not rider.password_hash:
            return error('该骑手未设置密码，请联系管理员')
        if rider.password_hash != hash_password(password):
            return error('账号或密码错误')

        token = generate_token(rider.id, 'rider')
        return success({'token': token, 'rider': _rider_to_dict(rider)}, '登录成功')

    except Exception as e:
        logger.error(f'Rider login error: {e}', exc_info=True)
        return error(f'服务器内部错误: {str(e)}', 500)


@rider_bp.route('/api/rider/profile', methods=['GET'])
@role_required('rider')
def get_profile():
    """获取骑手信息"""
    rider = Rider.query.get(g.user_id)
    if not rider:
        return error('骑手不存在')
    return success({
        'id': rider.id,
        'name': rider.name,
        'phone': rider.phone,
        'lng': float(rider.lng),
        'lat': float(rider.lat),
        'status': rider.status
    })


@rider_bp.route('/api/rider/profile', methods=['PUT'])
@role_required('rider')
def update_profile():
    """更新骑手信息"""
    rider = Rider.query.get(g.user_id)
    if not rider:
        return error('骑手不存在')

    data = request.get_json()
    if data.get('name') is not None:
        rider.name = data['name']
    if data.get('phone') is not None:
        rider.phone = data['phone']

    db.session.commit()
    return success({
        'id': rider.id,
        'name': rider.name,
        'phone': rider.phone,
        'lng': float(rider.lng),
        'lat': float(rider.lat),
        'status': rider.status
    }, '骑手信息已更新')


@rider_bp.route('/api/rider/available-orders', methods=['GET'])
@role_required('rider')
def get_available_orders():
    """获取可抢订单列表（待接单状态的订单，按距离排序）"""
    rider = Rider.query.get(g.user_id)
    if not rider:
        return error('骑手不存在')

    # 获取所有待接单订单
    orders = Order.query.filter_by(status=1).all()
    result = []
    for o in orders:
        merchant = Merchant.query.get(o.merchant_id)
        user = User.query.get(o.user_id)
        if not merchant:
            continue

        # 计算骑手到商家的距离
        dist = calc_distance(float(rider.lat), float(rider.lng), float(merchant.lat), float(merchant.lng))
        items = OrderItem.query.filter_by(order_id=o.id).all()

        result.append({
            'id': o.id,
            'merchant_name': merchant.name,
            'merchant_address': merchant.address,
            'merchant_lng': float(merchant.lng),
            'merchant_lat': float(merchant.lat),
            'user_address': o.address,
            'user_lng': float(o.address_lng),
            'user_lat': float(o.address_lat),
            'total_amount': float(o.total_amount),
            'distance_to_merchant': dist,
            'create_time': format_datetime(o.create_time),
            'items': [{'name': i.product_name, 'qty': i.quantity} for i in items]
        })

    result.sort(key=lambda x: x['distance_to_merchant'])
    return success(result)


@rider_bp.route('/api/rider/orders/<int:order_id>/grab', methods=['POST'])
@role_required('rider')
def grab_order(order_id):
    """抢单"""
    rider = Rider.query.get(g.user_id)
    if not rider:
        return error('骑手不存在')
    if rider.status != 0:
        return error('您当前有订单在进行中')

    order = Order.query.get(order_id)
    if not order:
        return error('订单不存在')
    if order.status != 1:
        return error('订单已被其他骑手接走')

    order.rider_id = rider.id
    order.status = 3  # 配送中
    order.rider_grab_time = datetime.datetime.now()
    rider.status = 1  # 骑手配送中
    db.session.commit()

    # WebSocket 通知用户骑手已接单
    from socket_events import notify_user_order_update
    notify_user_order_update(order.user_id, {
        'order_id': order.id,
        'status': order.status,
        'rider_name': rider.name,
        'rider_phone': rider.phone,
        'rider_lng': float(rider.lng),
        'rider_lat': float(rider.lat),
        'msg': f'骑手{rider.name}已接单，正在赶来'
    })

    return success({'order_id': order.id, 'status': order.status}, '抢单成功')


@rider_bp.route('/api/rider/location', methods=['POST'])
@role_required('rider')
def update_location():
    """骑手上报位置"""
    data = request.get_json()
    lng = data.get('lng')
    lat = data.get('lat')

    if lng is None or lat is None:
        return error('请提供经纬度')

    rider = Rider.query.get(g.user_id)
    rider.lng = lng
    rider.lat = lat
    db.session.commit()

    return success({'lng': float(rider.lng), 'lat': float(rider.lat)}, '位置已更新')


@rider_bp.route('/api/rider/my-order', methods=['GET'])
@role_required('rider')
def my_order():
    """获取骑手当前订单"""
    rider = Rider.query.get(g.user_id)
    if not rider:
        return error('骑手不存在')

    order = Order.query.filter_by(rider_id=rider.id).filter(
        Order.status.in_([3])  # 配送中
    ).first()

    if not order:
        return success(None, '暂无进行中的订单')

    merchant = Merchant.query.get(order.merchant_id)
    user = User.query.get(order.user_id)
    items = OrderItem.query.filter_by(order_id=order.id).all()

    return success({
        'id': order.id,
        'merchant': {
            'id': merchant.id,
            'name': merchant.name,
            'address': merchant.address,
            'lng': float(merchant.lng),
            'lat': float(merchant.lat)
        } if merchant else None,
        'user': {
            'id': user.id,
            'name': user.nickname,
            'phone': user.phone,
            'address': order.address,
            'lng': float(order.address_lng),
            'lat': float(order.address_lat)
        } if user else None,
        'total_amount': float(order.total_amount),
        'status': order.status,
        'remark': order.remark,
        'items': [{'name': i.product_name, 'qty': i.quantity} for i in items]
    })


@rider_bp.route('/api/rider/orders/<int:order_id>/complete', methods=['POST'])
@role_required('rider')
def complete_delivery(order_id):
    """完成配送"""
    order = Order.query.get(order_id)
    if not order or order.rider_id != g.user_id:
        return error('订单不存在')
    if order.status != 3:
        return error('订单状态不正确')

    order.status = 4  # 已完成
    order.finish_time = datetime.datetime.now()

    rider = Rider.query.get(g.user_id)
    rider.status = 0  # 骑手恢复空闲
    db.session.commit()

    return success({'order_id': order.id, 'status': order.status}, '配送完成')
