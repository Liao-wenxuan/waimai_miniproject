"""管理后台 API — 完整 CRUD + 增强统计"""
import datetime
import logging
from flask import Blueprint, request, jsonify, g
from models import db, Admin, User, Merchant, Order, OrderItem, Product, Rider, UserAddress, UserFavoriteMerchant
from auth import generate_token, role_required
from utils import hash_password, success, error, format_datetime

logger = logging.getLogger(__name__)
admin_bp = Blueprint('admin', __name__)


# ============================================================
#  登录
# ============================================================

@admin_bp.route('/api/admin/login', methods=['POST'])
def login():
    """管理员登录 — Demo 账号 + 数据库密码验证"""
    try:
        data = request.get_json(silent=True) or {}
        username = (data.get('username') or '').strip()
        password = (data.get('password') or '').strip()

        if not username or not password:
            return error('请输入账号和密码')

        # ---------- Demo 测试账号 ----------
        if username == 'admin' and password == 'admin':
            admin = Admin.query.filter_by(username='admin').first()
            if not admin:
                admin = Admin(username='admin', password_hash=hash_password('admin'))
                db.session.add(admin)
                db.session.commit()
            token = generate_token(admin.id, 'admin')
            return success({
                'token': token,
                'admin': {'id': admin.id, 'username': admin.username}
            }, '登录成功（Demo）')

        # ---------- 真实密码验证 ----------
        admin = Admin.query.filter_by(username=username).first()
        if not admin:
            return error('账号或密码错误')
        if not admin.password_hash or admin.password_hash != hash_password(password):
            return error('账号或密码错误')

        token = generate_token(admin.id, 'admin')
        return success({
            'token': token,
            'admin': {'id': admin.id, 'username': admin.username}
        }, '登录成功')

    except Exception as e:
        logger.error(f'Admin login error: {e}', exc_info=True)
        return error(f'服务器内部错误: {str(e)}', 500)


# ============================================================
#  订单管理
# ============================================================

@admin_bp.route('/api/admin/orders', methods=['GET'])
@role_required('admin')
def get_all_orders():
    """查看所有订单（支持状态筛选、关键词搜索）"""
    status = request.args.get('status', type=int)
    keyword = request.args.get('keyword', '').strip()

    query = Order.query
    if status is not None:
        query = query.filter_by(status=status)
    if keyword:
        # 按订单号或用户名搜索
        query = query.join(User, Order.user_id == User.id, isouter=True) \
                     .filter(
                         (Order.id == keyword if keyword.isdigit() else False) |
                         (User.nickname.like(f'%{keyword}%')) |
                         (User.phone.like(f'%{keyword}%'))
                     )

    orders = query.order_by(Order.create_time.desc()).limit(200).all()

    result = []
    for o in orders:
        user = User.query.get(o.user_id)
        merchant = Merchant.query.get(o.merchant_id)
        rider = Rider.query.get(o.rider_id) if o.rider_id else None
        result.append(_order_to_dict(o, user, merchant, rider))
    return success(result)


@admin_bp.route('/api/admin/orders/<int:order_id>', methods=['GET'])
@role_required('admin')
def get_order_detail(order_id):
    """获取订单详情（含商品项）"""
    order = Order.query.get(order_id)
    if not order:
        return error('订单不存在', 404)

    user = User.query.get(order.user_id)
    merchant = Merchant.query.get(order.merchant_id)
    rider = Rider.query.get(order.rider_id) if order.rider_id else None
    items = OrderItem.query.filter_by(order_id=order.id).all()

    detail = _order_to_dict(order, user, merchant, rider)
    detail['items'] = [{
        'id': i.id,
        'product_name': i.product_name,
        'quantity': i.quantity,
        'price': float(i.price)
    } for i in items]
    detail['remark'] = order.remark
    detail['address_lng'] = float(order.address_lng)
    detail['address_lat'] = float(order.address_lat)
    detail['pay_time'] = format_datetime(order.pay_time)
    detail['accept_time'] = format_datetime(order.accept_time)
    detail['rider_grab_time'] = format_datetime(order.rider_grab_time)
    detail['finish_time'] = format_datetime(order.finish_time)

    return success(detail)


@admin_bp.route('/api/admin/orders/<int:order_id>', methods=['PUT'])
@role_required('admin')
def update_order_status(order_id):
    """修改订单状态"""
    order = Order.query.get(order_id)
    if not order:
        return error('订单不存在', 404)

    data = request.get_json(silent=True) or {}
    new_status = data.get('status')

    if new_status is None:
        return error('请提供新状态')

    valid_statuses = [-1, 0, 1, 2, 3, 4]
    if new_status not in valid_statuses:
        return error(f'无效状态值，有效值: {valid_statuses}')

    order.status = new_status

    # 根据状态自动更新对应时间戳
    now = datetime.datetime.now()
    if new_status == 1:
        order.pay_time = order.pay_time or now
    if new_status == 2:
        order.accept_time = now
    if new_status in (3, 4):
        if new_status == 3 and not order.rider_grab_time:
            order.rider_grab_time = now
        if new_status == 4:
            order.finish_time = now
            # 骑手恢复空闲
            if order.rider_id:
                rider = Rider.query.get(order.rider_id)
                if rider and rider.status == 1:
                    rider.status = 0

    db.session.commit()

    logger.info(f'Admin updated order #{order_id} status to {new_status}')
    return success({'order_id': order.id, 'status': order.status}, '订单状态已更新')


@admin_bp.route('/api/admin/orders/<int:order_id>', methods=['DELETE'])
@role_required('admin')
def delete_order(order_id):
    """删除订单"""
    order = Order.query.get(order_id)
    if not order:
        return error('订单不存在', 404)

    # 级联删除订单项
    OrderItem.query.filter_by(order_id=order.id).delete()
    db.session.delete(order)
    db.session.commit()

    logger.info(f'Admin deleted order #{order_id}')
    return success(msg=f'订单 #{order_id} 已删除')


def _order_to_dict(o, user, merchant, rider):
    """序列化订单基础信息"""
    return {
        'id': o.id,
        'user_id': o.user_id,
        'user_name': user.nickname if user else '',
        'user_phone': user.phone if user else '',
        'merchant_id': o.merchant_id,
        'merchant_name': merchant.name if merchant else '',
        'rider_id': o.rider_id,
        'rider_name': rider.name if rider else '',
        'rider_phone': rider.phone if rider else '',
        'total_amount': float(o.total_amount),
        'status': o.status,
        'address': o.address,
        'create_time': format_datetime(o.create_time)
    }


# ============================================================
#  商家管理 CRUD
# ============================================================

@admin_bp.route('/api/admin/merchants', methods=['GET'])
@role_required('admin')
def get_merchants():
    """查看所有商家"""
    keyword = request.args.get('keyword', '').strip()
    query = Merchant.query
    if keyword:
        query = query.filter(
            (Merchant.name.like(f'%{keyword}%')) |
            (Merchant.phone.like(f'%{keyword}%'))
        )
    merchants = query.order_by(Merchant.id.asc()).all()
    result = [_merchant_to_dict(m) for m in merchants]
    return success(result)


@admin_bp.route('/api/admin/merchants/<int:merchant_id>', methods=['GET'])
@role_required('admin')
def get_merchant_detail(merchant_id):
    """获取商家详情"""
    merchant = Merchant.query.get(merchant_id)
    if not merchant:
        return error('商家不存在', 404)

    products = Product.query.filter_by(merchant_id=merchant_id).all()
    detail = _merchant_to_dict(merchant)
    detail['products'] = [{
        'id': p.id,
        'name': p.name,
        'price': float(p.price),
        'category': p.category,
        'sales': p.sales,
        'is_available': p.is_available
    } for p in products]

    return success(detail)


@admin_bp.route('/api/admin/merchants', methods=['POST'])
@role_required('admin')
def create_merchant():
    """创建商家"""
    data = request.get_json(silent=True) or {}
    name = (data.get('name') or '').strip()
    if not name:
        return error('商家名称不能为空')

    merchant = Merchant(
        name=name,
        address=data.get('address', ''),
        phone=data.get('phone', ''),
        lng=data.get('lng', 0),
        lat=data.get('lat', 0),
        logo=data.get('logo', ''),
        rating=data.get('rating', 5.0),
        monthly_sales=data.get('monthly_sales', 0),
        delivery_fee=data.get('delivery_fee', 0),
        min_price=data.get('min_price', 0),
        status=data.get('status', 1),
        password_hash=hash_password(data.get('password', '123456'))
    )
    db.session.add(merchant)
    db.session.commit()

    logger.info(f'Admin created merchant: {merchant.name} (id={merchant.id})')
    return success(_merchant_to_dict(merchant), '商家创建成功')


@admin_bp.route('/api/admin/merchants/<int:merchant_id>', methods=['PUT'])
@role_required('admin')
def update_merchant(merchant_id):
    """更新商家信息"""
    merchant = Merchant.query.get(merchant_id)
    if not merchant:
        return error('商家不存在', 404)

    data = request.get_json(silent=True) or {}
    _update_model_fields(merchant, data, [
        'name', 'address', 'phone', 'lng', 'lat', 'logo',
        'rating', 'monthly_sales', 'delivery_fee', 'min_price', 'status'
    ])

    # 单独处理密码
    if data.get('password'):
        merchant.password_hash = hash_password(data['password'])

    db.session.commit()
    logger.info(f'Admin updated merchant #{merchant_id}')
    return success(_merchant_to_dict(merchant), '商家信息已更新')


@admin_bp.route('/api/admin/merchants/<int:merchant_id>', methods=['DELETE'])
@role_required('admin')
def delete_merchant(merchant_id):
    """删除商家（级联删除关联商品和订单）"""
    merchant = Merchant.query.get(merchant_id)
    if not merchant:
        return error('商家不存在', 404)

    # 级联删除：订单项 → 订单 → 商品 → 收藏 → 商家
    orders = Order.query.filter_by(merchant_id=merchant_id).all()
    for order in orders:
        OrderItem.query.filter_by(order_id=order.id).delete()
        db.session.delete(order)
    Product.query.filter_by(merchant_id=merchant_id).delete()
    UserFavoriteMerchant.query.filter_by(merchant_id=merchant_id).delete()
    db.session.delete(merchant)
    db.session.commit()

    logger.info(f'Admin deleted merchant #{merchant_id} (cascade)')
    return success(msg=f'商家已删除')


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
        'status': m.status,
        'password_hash': m.password_hash or ''
    }


# ============================================================
#  骑手管理 CRUD
# ============================================================

@admin_bp.route('/api/admin/riders', methods=['GET'])
@role_required('admin')
def get_riders():
    """查看所有骑手"""
    keyword = request.args.get('keyword', '').strip()
    query = Rider.query
    if keyword:
        query = query.filter(
            (Rider.name.like(f'%{keyword}%')) |
            (Rider.phone.like(f'%{keyword}%'))
        )
    riders = query.order_by(Rider.id.asc()).all()
    result = [_rider_to_dict(r) for r in riders]
    return success(result)


@admin_bp.route('/api/admin/riders', methods=['POST'])
@role_required('admin')
def create_rider():
    """创建骑手"""
    data = request.get_json(silent=True) or {}
    name = (data.get('name') or '').strip()
    phone = (data.get('phone') or '').strip()

    if not name:
        return error('骑手姓名不能为空')
    if not phone:
        return error('骑手电话不能为空')

    # 检查手机号唯一
    if Rider.query.filter_by(phone=phone).first():
        return error('该手机号已被使用')

    rider = Rider(
        name=name,
        phone=phone,
        lng=data.get('lng', 0),
        lat=data.get('lat', 0),
        status=data.get('status', 0),
        password_hash=hash_password(data.get('password', '123456'))
    )
    db.session.add(rider)
    db.session.commit()

    logger.info(f'Admin created rider: {rider.name} (id={rider.id})')
    return success(_rider_to_dict(rider), '骑手创建成功')


@admin_bp.route('/api/admin/riders/<int:rider_id>', methods=['PUT'])
@role_required('admin')
def update_rider(rider_id):
    """更新骑手信息"""
    rider = Rider.query.get(rider_id)
    if not rider:
        return error('骑手不存在', 404)

    data = request.get_json(silent=True) or {}
    _update_model_fields(rider, data, ['name', 'phone', 'lng', 'lat', 'status'])

    if data.get('password'):
        rider.password_hash = hash_password(data['password'])

    db.session.commit()
    logger.info(f'Admin updated rider #{rider_id}')
    return success(_rider_to_dict(rider), '骑手信息已更新')


@admin_bp.route('/api/admin/riders/<int:rider_id>', methods=['DELETE'])
@role_required('admin')
def delete_rider(rider_id):
    """删除骑手（将其名下订单的骑手字段置空）"""
    rider = Rider.query.get(rider_id)
    if not rider:
        return error('骑手不存在', 404)

    # 将该骑手的订单置空骑手字段
    Order.query.filter_by(rider_id=rider_id).update({'rider_id': None})
    db.session.delete(rider)
    db.session.commit()

    logger.info(f'Admin deleted rider #{rider_id}')
    return success(msg=f'骑手已删除')


def _rider_to_dict(r):
    """序列化骑手信息"""
    return {
        'id': r.id,
        'name': r.name,
        'phone': r.phone,
        'lng': float(r.lng),
        'lat': float(r.lat),
        'status': r.status,
        'password_hash': r.password_hash or ''
    }


# ============================================================
#  用户管理
# ============================================================

@admin_bp.route('/api/admin/users', methods=['GET'])
@role_required('admin')
def get_users():
    """查看所有用户（支持搜索）"""
    keyword = request.args.get('keyword', '').strip()
    query = User.query
    if keyword:
        query = query.filter(
            (User.nickname.like(f'%{keyword}%')) |
            (User.phone.like(f'%{keyword}%'))
        )
    users = query.order_by(User.create_time.desc()).limit(200).all()
    result = [_user_to_dict(u) for u in users]
    return success(result)


@admin_bp.route('/api/admin/users/<int:user_id>', methods=['PUT'])
@role_required('admin')
def update_user(user_id):
    """更新用户信息"""
    user = User.query.get(user_id)
    if not user:
        return error('用户不存在', 404)

    data = request.get_json(silent=True) or {}
    if data.get('nickname') is not None:
        user.nickname = data['nickname']
    if data.get('phone') is not None:
        user.phone = data['phone']
    if data.get('balance') is not None:
        user.balance = data['balance']

    db.session.commit()
    logger.info(f'Admin updated user #{user_id}')
    return success(_user_to_dict(user), '用户信息已更新')


@admin_bp.route('/api/admin/users/<int:user_id>', methods=['DELETE'])
@role_required('admin')
def delete_user(user_id):
    """删除用户（级联删除订单、地址、收藏）"""
    user = User.query.get(user_id)
    if not user:
        return error('用户不存在', 404)

    # 级联删除
    orders = Order.query.filter_by(user_id=user_id).all()
    for order in orders:
        OrderItem.query.filter_by(order_id=order.id).delete()
        db.session.delete(order)
    UserAddress.query.filter_by(user_id=user_id).delete()
    UserFavoriteMerchant.query.filter_by(user_id=user_id).delete()
    db.session.delete(user)
    db.session.commit()

    logger.info(f'Admin deleted user #{user_id} (cascade)')
    return success(msg=f'用户已删除')


def _user_to_dict(u):
    """序列化用户信息"""
    return {
        'id': u.id,
        'phone': u.phone,
        'nickname': u.nickname,
        'avatar': u.avatar,
        'balance': float(u.balance),
        'create_time': format_datetime(u.create_time)
    }


# ============================================================
#  商品管理
# ============================================================

@admin_bp.route('/api/admin/products', methods=['GET'])
@role_required('admin')
def get_products():
    """查看全部商品（支持按商家筛选和关键词搜索）"""
    merchant_id = request.args.get('merchant_id', type=int)
    keyword = request.args.get('keyword', '').strip()

    query = Product.query
    if merchant_id:
        query = query.filter_by(merchant_id=merchant_id)
    if keyword:
        query = query.filter(Product.name.like(f'%{keyword}%'))

    products = query.order_by(Product.merchant_id.asc(), Product.id.asc()).limit(500).all()

    result = []
    for p in products:
        merchant = Merchant.query.get(p.merchant_id)
        result.append({
            'id': p.id,
            'merchant_id': p.merchant_id,
            'merchant_name': merchant.name if merchant else '',
            'name': p.name,
            'price': float(p.price),
            'image': p.image,
            'description': p.description,
            'sales': p.sales,
            'category': p.category,
            'is_available': p.is_available
        })
    return success(result)


@admin_bp.route('/api/admin/products', methods=['POST'])
@role_required('admin')
def create_product():
    """创建商品"""
    data = request.get_json(silent=True) or {}
    merchant_id = data.get('merchant_id')
    name = (data.get('name') or '').strip()

    if not merchant_id:
        return error('请选择所属商家')
    if not name:
        return error('商品名称不能为空')

    merchant = Merchant.query.get(merchant_id)
    if not merchant:
        return error('商家不存在')

    product = Product(
        merchant_id=merchant_id,
        name=name,
        price=data.get('price', 0),
        image=data.get('image', ''),
        description=data.get('description', ''),
        sales=data.get('sales', 0),
        category=data.get('category', '其他'),
        is_available=data.get('is_available', 1)
    )
    db.session.add(product)
    db.session.commit()

    logger.info(f'Admin created product: {product.name} for merchant #{merchant_id}')
    return success({
        'id': product.id,
        'merchant_id': product.merchant_id,
        'merchant_name': merchant.name,
        'name': product.name,
        'price': float(product.price),
        'category': product.category,
        'is_available': product.is_available
    }, '商品创建成功')


@admin_bp.route('/api/admin/products/<int:product_id>', methods=['PUT'])
@role_required('admin')
def update_product(product_id):
    """更新商品"""
    product = Product.query.get(product_id)
    if not product:
        return error('商品不存在', 404)

    data = request.get_json(silent=True) or {}
    _update_model_fields(product, data, [
        'merchant_id', 'name', 'price', 'image', 'description',
        'sales', 'category', 'is_available'
    ])
    db.session.commit()

    merchant = Merchant.query.get(product.merchant_id)
    logger.info(f'Admin updated product #{product_id}')
    return success({
        'id': product.id,
        'merchant_id': product.merchant_id,
        'merchant_name': merchant.name if merchant else '',
        'name': product.name,
        'price': float(product.price),
        'category': product.category,
        'is_available': product.is_available
    }, '商品已更新')


@admin_bp.route('/api/admin/products/<int:product_id>', methods=['DELETE'])
@role_required('admin')
def delete_product(product_id):
    """删除商品（级联删除关联订单项）"""
    product = Product.query.get(product_id)
    if not product:
        return error('商品不存在', 404)

    OrderItem.query.filter_by(product_id=product_id).delete()
    db.session.delete(product)
    db.session.commit()

    logger.info(f'Admin deleted product #{product_id}')
    return success(msg=f'商品已删除')


# ============================================================
#  增强统计
# ============================================================

@admin_bp.route('/api/admin/statistics', methods=['GET'])
@role_required('admin')
def get_statistics():
    """数据统计（含近7天趋势、状态分布、热销榜）"""
    today = datetime.datetime.now().date()
    today_start = datetime.datetime.combine(today, datetime.time.min)
    today_end = datetime.datetime.combine(today, datetime.time.max)

    # ---------- 基础统计 ----------
    today_orders = Order.query.filter(
        Order.create_time >= today_start,
        Order.create_time <= today_end
    ).count()

    today_amount = db.session.query(db.func.sum(Order.total_amount)).filter(
        Order.create_time >= today_start,
        Order.create_time <= today_end,
        Order.status.in_([1, 2, 3, 4])
    ).scalar() or 0

    total_orders = Order.query.count()
    total_users = User.query.count()
    total_merchants = Merchant.query.count()
    total_riders = Rider.query.count()
    total_products = Product.query.count()

    # ---------- 近7天趋势 ----------
    week_orders = []
    week_amount = []
    for i in range(6, -1, -1):
        day = today - datetime.timedelta(days=i)
        day_start = datetime.datetime.combine(day, datetime.time.min)
        day_end = datetime.datetime.combine(day, datetime.time.max)

        count = Order.query.filter(
            Order.create_time >= day_start,
            Order.create_time <= day_end
        ).count()

        amount = db.session.query(db.func.sum(Order.total_amount)).filter(
            Order.create_time >= day_start,
            Order.create_time <= day_end,
            Order.status.in_([1, 2, 3, 4])
        ).scalar() or 0

        week_orders.append({'date': day.strftime('%m-%d'), 'count': count})
        week_amount.append({'date': day.strftime('%m-%d'), 'amount': round(float(amount), 2)})

    # ---------- 订单状态分布 ----------
    status_names = {-1: '已取消', 0: '待支付', 1: '待接单', 2: '已接单', 3: '配送中', 4: '已完成'}
    status_breakdown = []
    for s, label in status_names.items():
        cnt = Order.query.filter_by(status=s).count()
        if cnt > 0:
            status_breakdown.append({'status': s, 'label': label, 'count': cnt})

    # ---------- Top 5 商家（按订单数） ----------
    top_merchants_raw = db.session.query(
        Order.merchant_id,
        db.func.count(Order.id).label('order_count'),
        db.func.sum(Order.total_amount).label('total_revenue')
    ).filter(
        Order.status.in_([1, 2, 3, 4])
    ).group_by(Order.merchant_id).order_by(
        db.func.count(Order.id).desc()
    ).limit(5).all()

    top_merchants = []
    for m_id, cnt, rev in top_merchants_raw:
        merchant = Merchant.query.get(m_id)
        if merchant:
            top_merchants.append({
                'id': merchant.id,
                'name': merchant.name,
                'order_count': cnt,
                'total_revenue': round(float(rev or 0), 2)
            })

    return success({
        'today_orders': today_orders,
        'today_amount': round(float(today_amount), 2),
        'total_orders': total_orders,
        'total_users': total_users,
        'total_merchants': total_merchants,
        'total_riders': total_riders,
        'total_products': total_products,
        'week_orders': week_orders,
        'week_amount': week_amount,
        'status_breakdown': status_breakdown,
        'top_merchants': top_merchants
    })


# ============================================================
#  工具函数
# ============================================================

def _update_model_fields(model, data, fields):
    """批量更新 Model 字段（仅更新 data 中存在的 key）"""
    for field in fields:
        if field in data and data[field] is not None:
            setattr(model, field, data[field])
