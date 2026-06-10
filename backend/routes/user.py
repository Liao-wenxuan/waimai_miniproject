"""用户端 API"""
import datetime
import logging
from flask import Blueprint, request, jsonify, g
from models import db, User, Merchant, Product, Order, OrderItem, Rider
from auth import generate_token, login_required
from utils import hash_password, calc_distance, success, error, format_datetime

logger = logging.getLogger(__name__)
user_bp = Blueprint('user', __name__)


def _user_to_dict(u):
    """序列化用户信息"""
    return {
        'id': u.id,
        'phone': u.phone,
        'nickname': u.nickname,
        'avatar': u.avatar,
        'balance': float(u.balance)
    }


@user_bp.route('/api/user/login', methods=['POST'])
def login():
    """用户登录（手机号+验证码，验证码写死 123456）"""
    try:
        data = request.get_json(silent=True) or {}
        phone = (data.get('phone') or '').strip()
        code = (data.get('code') or '').strip()

        if not phone or len(phone) != 11:
            return error('请输入正确的手机号')

        if code != '123456':
            return error('验证码错误')

        user = User.query.filter_by(phone=phone).first()
        if not user:
            user = User(phone=phone, nickname=f'用户{phone[-4:]}')
            db.session.add(user)
            db.session.commit()

        token = generate_token(user.id, 'user')
        return success({
            'token': token,
            'user': _user_to_dict(user)
        }, '登录成功')

    except Exception as e:
        logger.error(f'User login error: {e}', exc_info=True)
        return error(f'服务器内部错误: {str(e)}', 500)


@user_bp.route('/api/user/profile', methods=['GET'])
@login_required
def get_profile():
    """获取用户信息"""
    user = User.query.get(g.user_id)
    if not user:
        return error('用户不存在')
    return success({
        'id': user.id,
        'phone': user.phone,
        'nickname': user.nickname,
        'avatar': user.avatar,
        'balance': float(user.balance)
    })


@user_bp.route('/api/user/profile', methods=['PUT'])
@login_required
def update_profile():
    """更新用户信息"""
    user = User.query.get(g.user_id)
    data = request.get_json()
    if data.get('nickname'):
        user.nickname = data['nickname']
    if data.get('avatar'):
        user.avatar = data['avatar']
    db.session.commit()
    return success(msg='更新成功')


@user_bp.route('/api/merchants', methods=['GET'])
@login_required
def get_merchants():
    """获取商家列表（按距离排序，支持搜索和范围过滤）"""
    lat = request.args.get('lat', 0, type=float)
    lng = request.args.get('lng', 0, type=float)
    keyword = request.args.get('keyword', '').strip()
    range_km = request.args.get('range', type=float)  # 可选范围过滤（公里）

    # 坐标无效时（0或超出合理范围），跳过距离过滤，返回所有商家
    coords_valid = (-90 <= lat <= 90 and -180 <= lng <= 180 and not (lat == 0 and lng == 0))

    merchants = Merchant.query.filter_by(status=1)

    if keyword:
        merchants = merchants.filter(
            (Merchant.name.like(f'%{keyword}%')) |
            (Merchant.id.in_(
                db.session.query(Product.merchant_id)
                .filter(Product.name.like(f'%{keyword}%'))
            ))
        )

    merchants = merchants.all()

    result = []
    for m in merchants:
        if coords_valid:
            distance = calc_distance(lat, lng, float(m.lat), float(m.lng))
        else:
            distance = 0  # 无有效坐标时不计算距离
        
        # 范围过滤（坐标无效时跳过过滤，显示全部商家）
        if coords_valid and range_km and distance > range_km:
            continue
            
        result.append({
            'id': m.id,
            'name': m.name,
            'address': m.address,
            'lng': float(m.lng),
            'lat': float(m.lat),
            'logo': m.logo,
            'rating': float(m.rating),
            'monthly_sales': m.monthly_sales,
            'delivery_fee': float(m.delivery_fee),
            'min_price': float(m.min_price),
            'distance': distance
        })

    result.sort(key=lambda x: x['distance'])

    return success(result)


@user_bp.route('/api/merchants/<int:merchant_id>', methods=['GET'])
@login_required
def get_merchant_detail(merchant_id):
    """获取商家详情和菜单"""
    merchant = Merchant.query.get(merchant_id)
    if not merchant:
        return error('商家不存在')

    products = Product.query.filter_by(merchant_id=merchant_id, is_available=1).all()
    # 按分类分组
    categories = {}
    for p in products:
        cat = p.category or '其他'
        if cat not in categories:
            categories[cat] = []
        categories[cat].append({
            'id': p.id,
            'name': p.name,
            'price': float(p.price),
            'image': p.image,
            'description': p.description,
            'sales': p.sales,
            'category': p.category
        })

    return success({
        'merchant': {
            'id': merchant.id,
            'name': merchant.name,
            'address': merchant.address,
            'lng': float(merchant.lng),
            'lat': float(merchant.lat),
            'logo': merchant.logo,
            'rating': float(merchant.rating),
            'monthly_sales': merchant.monthly_sales,
            'delivery_fee': float(merchant.delivery_fee),
            'min_price': float(merchant.min_price),
            'status': merchant.status
        },
        'products': categories
    })


@user_bp.route('/api/orders', methods=['POST'])
@login_required
def create_order():
    """创建订单"""
    data = request.get_json()
    merchant_id = data.get('merchant_id')
    items = data.get('items', [])  # [{product_id, quantity}]
    address = data.get('address', '')
    address_lng = data.get('address_lng', 0)
    address_lat = data.get('address_lat', 0)
    remark = data.get('remark', '')

    if not merchant_id or not items:
        return error('参数不完整')

    merchant = Merchant.query.get(merchant_id)
    if not merchant:
        return error('商家不存在')

    # 计算总价
    total = 0
    order_items = []
    for item in items:
        product = Product.query.get(item['product_id'])
        if not product or product.merchant_id != merchant_id:
            return error(f'商品 {item.get("product_id")} 不存在')
        qty = item.get('quantity', 1)
        subtotal = float(product.price) * qty
        total += subtotal
        order_items.append({
            'product': product,
            'qty': qty,
            'price': float(product.price)
        })

    total += float(merchant.delivery_fee)  # 加配送费

    order = Order(
        user_id=g.user_id,
        merchant_id=merchant_id,
        total_amount=total,
        status=0,  # 待支付
        address=address,
        address_lng=address_lng,
        address_lat=address_lat,
        remark=remark,
        create_time=datetime.datetime.now()
    )
    db.session.add(order)
    db.session.flush()

    for oi in order_items:
        order_item = OrderItem(
            order_id=order.id,
            product_id=oi['product'].id,
            product_name=oi['product'].name,
            quantity=oi['qty'],
            price=oi['price']
        )
        db.session.add(order_item)

    db.session.commit()

    return success({'order_id': order.id, 'total_amount': float(order.total_amount)}, '下单成功')


@user_bp.route('/api/orders/<int:order_id>/pay', methods=['POST'])
@login_required
def pay_order(order_id):
    """模拟支付"""
    order = Order.query.get(order_id)
    if not order or order.user_id != g.user_id:
        return error('订单不存在')
    if order.status != 0:
        return error('订单状态不正确')

    order.status = 1  # 待接单
    order.pay_time = datetime.datetime.now()
    db.session.commit()

    # WebSocket 通知商家有新订单
    from socket_events import notify_merchant_new_order
    items_data = [{
        'name': i.product_name, 'qty': i.quantity, 'price': float(i.price)
    } for i in OrderItem.query.filter_by(order_id=order.id).all()]
    notify_merchant_new_order(order.merchant_id, {
        'id': order.id,
        'user_name': User.query.get(g.user_id).nickname if User.query.get(g.user_id) else '',
        'total_amount': float(order.total_amount),
        'status': order.status,
        'address': order.address,
        'create_time': order.create_time.strftime('%Y-%m-%d %H:%M:%S'),
        'items': items_data
    })

    return success({'status': order.status}, '支付成功')


@user_bp.route('/api/orders/<int:order_id>/cancel', methods=['POST'])
@login_required
def cancel_order(order_id):
    """用户取消订单"""
    order = Order.query.get(order_id)
    if not order or order.user_id != g.user_id:
        return error('订单不存在')
    if order.status not in (0, 1):
        return error('当前状态不支持取消')

    order.status = -1  # 已取消
    db.session.commit()

    return success({'order_id': order.id, 'status': order.status}, '订单已取消')


@user_bp.route('/api/orders', methods=['GET'])
@login_required
def get_orders():
    """获取用户订单列表"""
    status = request.args.get('status', type=int)  # None=全部
    query = Order.query.filter_by(user_id=g.user_id)
    if status is not None:
        query = query.filter_by(status=status)
    orders = query.order_by(Order.create_time.desc()).all()

    result = []
    for o in orders:
        merchant = Merchant.query.get(o.merchant_id)
        items = OrderItem.query.filter_by(order_id=o.id).all()
        rider_info = None
        if o.rider_id:
            rider = Rider.query.get(o.rider_id)
            if rider:
                rider_info = {
                    'id': rider.id,
                    'name': rider.name,
                    'phone': rider.phone,
                    'lng': float(rider.lng),
                    'lat': float(rider.lat)
                }
        result.append({
            'id': o.id,
            'merchant_name': merchant.name if merchant else '',
            'merchant_logo': merchant.logo if merchant else '',
            'total_amount': float(o.total_amount),
            'status': o.status,
            'address': o.address,
            'remark': o.remark,
            'create_time': format_datetime(o.create_time),
            'items': [{'name': i.product_name, 'qty': i.quantity, 'price': float(i.price)} for i in items],
            'rider': rider_info
        })

    return success(result)


@user_bp.route('/api/orders/<int:order_id>', methods=['GET'])
@login_required
def get_order_detail(order_id):
    """获取订单详情"""
    order = Order.query.get(order_id)
    if not order or order.user_id != g.user_id:
        return error('订单不存在')

    merchant = Merchant.query.get(order.merchant_id)
    items = OrderItem.query.filter_by(order_id=order.id).all()
    rider_info = None
    if order.rider_id:
        rider = Rider.query.get(order.rider_id)
        if rider:
            rider_info = {
                'id': rider.id,
                'name': rider.name,
                'phone': rider.phone,
                'lng': float(rider.lng),
                'lat': float(rider.lat)
            }

    return success({
        'id': order.id,
        'merchant': {
            'id': merchant.id,
            'name': merchant.name,
            'address': merchant.address,
            'lng': float(merchant.lng),
            'lat': float(merchant.lat)
        } if merchant else None,
        'total_amount': float(order.total_amount),
        'status': order.status,
        'address': order.address,
        'address_lng': float(order.address_lng),
        'address_lat': float(order.address_lat),
        'remark': order.remark,
        'create_time': format_datetime(order.create_time),
        'pay_time': format_datetime(order.pay_time),
        'accept_time': format_datetime(order.accept_time),
        'finish_time': format_datetime(order.finish_time),
        'items': [{
            'id': i.id,
            'product_name': i.product_name,
            'quantity': i.quantity,
            'price': float(i.price)
        } for i in items],
        'rider': rider_info
    })


# ========== 地址管理 ==========

@user_bp.route('/api/user/addresses', methods=['GET'])
@login_required
def get_addresses():
    """获取用户地址列表"""
    from models import UserAddress
    addresses = UserAddress.query.filter_by(user_id=g.user_id).order_by(
        UserAddress.is_default.desc(),
        UserAddress.create_time.desc()
    ).all()
    result = [{
        'id': a.id,
        'name': a.name,
        'phone': a.phone,
        'address': a.address,
        'lng': float(a.lng),
        'lat': float(a.lat),
        'tag': a.tag,
        'is_default': a.is_default
    } for a in addresses]
    return success(result)


@user_bp.route('/api/user/addresses', methods=['POST'])
@login_required
def add_address():
    """添加地址"""
    from models import UserAddress
    data = request.get_json()
    name = data.get('name', '')
    phone = data.get('phone', '')
    address = data.get('address', '')
    lng = data.get('lng', 0)
    lat = data.get('lat', 0)
    tag = data.get('tag', '')
    is_default = data.get('is_default', 0)

    if not name or not address:
        return error('请填写完整地址信息')

    # 如果设为默认，先取消其他默认
    if is_default:
        UserAddress.query.filter_by(user_id=g.user_id, is_default=1).update({'is_default': 0})

    addr = UserAddress(
        user_id=g.user_id,
        name=name,
        phone=phone,
        address=address,
        lng=lng,
        lat=lat,
        tag=tag,
        is_default=is_default
    )
    db.session.add(addr)
    db.session.commit()

    return success({'id': addr.id}, '地址添加成功')


@user_bp.route('/api/user/addresses/<int:addr_id>', methods=['PUT'])
@login_required
def update_address(addr_id):
    """更新地址"""
    from models import UserAddress
    addr = UserAddress.query.get(addr_id)
    if not addr or addr.user_id != g.user_id:
        return error('地址不存在')

    data = request.get_json()
    if data.get('name') is not None:
        addr.name = data['name']
    if data.get('phone') is not None:
        addr.phone = data['phone']
    if data.get('address') is not None:
        addr.address = data['address']
    if data.get('lng') is not None:
        addr.lng = data['lng']
    if data.get('lat') is not None:
        addr.lat = data['lat']
    if data.get('tag') is not None:
        addr.tag = data['tag']
    if data.get('is_default') is not None:
        # 如果设为默认，先取消其他默认
        if data['is_default']:
            UserAddress.query.filter_by(user_id=g.user_id, is_default=1).update({'is_default': 0})
        addr.is_default = data['is_default']

    db.session.commit()
    return success(msg='地址更新成功')


@user_bp.route('/api/user/addresses/<int:addr_id>', methods=['DELETE'])
@login_required
def delete_address(addr_id):
    """删除地址"""
    from models import UserAddress
    addr = UserAddress.query.get(addr_id)
    if not addr or addr.user_id != g.user_id:
        return error('地址不存在')

    db.session.delete(addr)
    db.session.commit()
    return success(msg='地址已删除')


# ========== 收藏商家 ==========

@user_bp.route('/api/user/favorites', methods=['GET'])
@login_required
def get_favorites():
    """获取用户收藏的商家列表"""
    from models import UserFavoriteMerchant
    favs = UserFavoriteMerchant.query.filter_by(user_id=g.user_id).all()
    merchant_ids = [f.merchant_id for f in favs]
    merchants = Merchant.query.filter(Merchant.id.in_(merchant_ids)).all() if merchant_ids else []
    result = []
    for m in merchants:
        result.append({
            'id': m.id,
            'name': m.name,
            'address': m.address,
            'logo': m.logo,
            'rating': float(m.rating),
            'monthly_sales': m.monthly_sales,
            'delivery_fee': float(m.delivery_fee),
            'min_price': float(m.min_price)
        })
    return success(result)


@user_bp.route('/api/user/favorites/<int:merchant_id>', methods=['POST'])
@login_required
def add_favorite(merchant_id):
    """收藏商家"""
    from models import UserFavoriteMerchant
    exist = UserFavoriteMerchant.query.filter_by(user_id=g.user_id, merchant_id=merchant_id).first()
    if exist:
        return error('已收藏')
    fav = UserFavoriteMerchant(user_id=g.user_id, merchant_id=merchant_id)
    db.session.add(fav)
    db.session.commit()
    return success(msg='已收藏')


@user_bp.route('/api/user/favorites/<int:merchant_id>', methods=['DELETE'])
@login_required
def remove_favorite(merchant_id):
    """取消收藏"""
    from models import UserFavoriteMerchant
    fav = UserFavoriteMerchant.query.filter_by(user_id=g.user_id, merchant_id=merchant_id).first()
    if not fav:
        return error('未收藏')
    db.session.delete(fav)
    db.session.commit()
    return success(msg='已取消收藏')
