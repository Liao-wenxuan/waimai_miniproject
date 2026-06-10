"""商家端 API"""
import datetime
import logging
from flask import Blueprint, request, jsonify, g, current_app
from models import db, Merchant, Order, OrderItem, Product
from auth import generate_token, role_required
from utils import hash_password, success, error, format_datetime

logger = logging.getLogger(__name__)
merchant_bp = Blueprint('merchant', __name__)


def _merchant_to_dict(m):
    """序列化商家信息"""
    return {
        'id': m.id,
        'name': m.name,
        'address': m.address,
        'phone': m.phone,
        'lng': float(m.lng),
        'lat': float(m.lat),
        'logo': m.logo,
        'rating': float(m.rating),
        'monthly_sales': m.monthly_sales,
        'delivery_fee': float(m.delivery_fee),
        'min_price': float(m.min_price),
        'status': m.status
    }


@merchant_bp.route('/api/merchant/login', methods=['POST'])
def login():
    """商家登录 — 支持 Demo 账号和真实密码验证"""
    try:
        data = request.get_json(silent=True) or {}
        username = (data.get('username') or '').strip()
        password = (data.get('password') or '').strip()

        if not username or not password:
            return error('请输入账号和密码')

        # ---------- Demo 测试账号 ----------
        if username == 'merchant' and password == '123456':
            merchant = Merchant.query.first()
            if not merchant:
                return error('暂无商家数据，请先初始化数据库或运行 seed')
            token = generate_token(merchant.id, 'merchant')
            return success({'token': token, 'merchant': _merchant_to_dict(merchant)}, '登录成功（Demo）')

        # ---------- 真实密码验证：用商家名称作为登录账号 ----------
        merchant = Merchant.query.filter_by(name=username).first()
        if not merchant:
            return error('账号或密码错误')
        if not merchant.password_hash:
            return error('该商家未设置密码，请联系管理员')
        if merchant.password_hash != hash_password(password):
            return error('账号或密码错误')

        token = generate_token(merchant.id, 'merchant')
        return success({'token': token, 'merchant': _merchant_to_dict(merchant)}, '登录成功')

    except Exception as e:
        logger.error(f'Merchant login error: {e}', exc_info=True)
        return error(f'服务器内部错误: {str(e)}', 500)


@merchant_bp.route('/api/merchant/orders', methods=['GET'])
@role_required('merchant')
def get_orders():
    """获取本店订单"""
    status = request.args.get('status', type=int)
    merchant = Merchant.query.get(g.user_id)
    if not merchant:
        return error('商家不存在')

    query = Order.query.filter_by(merchant_id=merchant.id)
    if status is not None:
        query = query.filter_by(status=status)
    orders = query.order_by(Order.create_time.desc()).all()

    result = []
    for o in orders:
        items = OrderItem.query.filter_by(order_id=o.id).all()
        # 获取用户名
        from models import User
        user = User.query.get(o.user_id)
        result.append({
            'id': o.id,
            'user_name': user.nickname if user else '未知用户',
            'user_phone': user.phone if user else '',
            'total_amount': float(o.total_amount),
            'status': o.status,
            'address': o.address,
            'address_lng': float(o.address_lng),
            'address_lat': float(o.address_lat),
            'remark': o.remark,
            'create_time': format_datetime(o.create_time),
            'items': [{'name': i.product_name, 'qty': i.quantity, 'price': float(i.price)} for i in items]
        })

    return success(result)


@merchant_bp.route('/api/merchant/orders/<int:order_id>/accept', methods=['POST'])
@role_required('merchant')
def accept_order(order_id):
    """接单"""
    order = Order.query.get(order_id)
    if not order or order.merchant_id != g.user_id:
        return error('订单不存在')
    if order.status != 1:
        return error('订单状态不正确，只能接待接单的订单')

    order.status = 2  # 已接单/待取餐
    order.accept_time = datetime.datetime.now()
    db.session.commit()

    # WebSocket 通知用户商家已接单
    from socket_events import notify_user_order_update
    notify_user_order_update(order.user_id, {
        'order_id': order.id,
        'status': order.status,
        'msg': '商家已接单，正在准备餐品'
    })

    return success({'order_id': order.id, 'status': order.status}, '接单成功')


@merchant_bp.route('/api/merchant/orders/<int:order_id>/reject', methods=['POST'])
@role_required('merchant')
def reject_order(order_id):
    """拒单"""
    order = Order.query.get(order_id)
    if not order or order.merchant_id != g.user_id:
        return error('订单不存在')
    if order.status != 1:
        return error('订单状态不正确')

    order.status = -1  # 已取消
    db.session.commit()

    return success(msg='已拒绝该订单')


@merchant_bp.route('/api/merchant/orders/<int:order_id>/complete', methods=['POST'])
@role_required('merchant')
def complete_order(order_id):
    """完成订单"""
    order = Order.query.get(order_id)
    if not order or order.merchant_id != g.user_id:
        return error('订单不存在')
    # 配送中或已接单状态都可以完成
    if order.status not in (2, 3):
        return error('订单状态不正确')

    order.status = 4  # 已完成
    order.finish_time = datetime.datetime.now()
    db.session.commit()

    return success({'order_id': order.id, 'status': order.status}, '订单已完成')


@merchant_bp.route('/api/merchant/products', methods=['GET'])
@role_required('merchant')
def get_products():
    """获取本店商品"""
    products = Product.query.filter_by(merchant_id=g.user_id).all()
    result = [{
        'id': p.id,
        'name': p.name,
        'price': float(p.price),
        'image': p.image,
        'description': p.description,
        'sales': p.sales,
        'category': p.category,
        'is_available': p.is_available
    } for p in products]
    return success(result)


@merchant_bp.route('/api/merchant/profile', methods=['GET'])
@role_required('merchant')
def get_profile():
    """获取商家信息"""
    merchant = Merchant.query.get(g.user_id)
    if not merchant:
        return error('商家不存在')
    return success({
        'id': merchant.id,
        'name': merchant.name,
        'address': merchant.address,
        'phone': merchant.phone,
        'lng': float(merchant.lng),
        'lat': float(merchant.lat),
        'logo': merchant.logo,
        'rating': float(merchant.rating),
        'monthly_sales': merchant.monthly_sales,
        'delivery_fee': float(merchant.delivery_fee),
        'min_price': float(merchant.min_price),
        'status': merchant.status
    })


@merchant_bp.route('/api/merchant/profile', methods=['PUT'])
@role_required('merchant')
def update_profile():
    """更新商家信息"""
    merchant = Merchant.query.get(g.user_id)
    if not merchant:
        return error('商家不存在')

    data = request.get_json()
    if data.get('name') is not None:
        merchant.name = data['name']
    if data.get('address') is not None:
        merchant.address = data['address']
    if data.get('phone') is not None:
        merchant.phone = data['phone']
    if data.get('lng') is not None:
        merchant.lng = data['lng']
    if data.get('lat') is not None:
        merchant.lat = data['lat']
    if data.get('logo') is not None:
        merchant.logo = data['logo']
    if data.get('delivery_fee') is not None:
        merchant.delivery_fee = data['delivery_fee']
    if data.get('min_price') is not None:
        merchant.min_price = data['min_price']
    if data.get('status') is not None:
        merchant.status = data['status']

    db.session.commit()
    return success({
        'id': merchant.id,
        'name': merchant.name,
        'address': merchant.address,
        'phone': merchant.phone,
        'lng': float(merchant.lng),
        'lat': float(merchant.lat),
        'logo': merchant.logo,
        'rating': float(merchant.rating),
        'monthly_sales': merchant.monthly_sales,
        'delivery_fee': float(merchant.delivery_fee),
        'min_price': float(merchant.min_price),
        'status': merchant.status
    }, '商家信息已更新')
