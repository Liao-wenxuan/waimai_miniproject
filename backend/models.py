"""SQLAlchemy 数据模型"""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    phone = db.Column(db.String(20), unique=True, nullable=False, index=True)
    nickname = db.Column(db.String(64), default='用户')
    avatar = db.Column(db.String(256), default='')
    balance = db.Column(db.Numeric(10, 2), default=0.00)
    create_time = db.Column(db.DateTime, default=datetime.now)

    orders = db.relationship('Order', backref='user', lazy='dynamic')


class Merchant(db.Model):
    __tablename__ = 'merchant'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(128), nullable=False)
    address = db.Column(db.String(256), default='')
    phone = db.Column(db.String(20), default='')
    lng = db.Column(db.Numeric(10, 6), default=0.0)  # 经度
    lat = db.Column(db.Numeric(10, 6), default=0.0)  # 纬度
    logo = db.Column(db.String(256), default='')
    rating = db.Column(db.Numeric(2, 1), default=5.0)
    monthly_sales = db.Column(db.Integer, default=0)
    delivery_fee = db.Column(db.Numeric(6, 2), default=0.00)
    min_price = db.Column(db.Numeric(6, 2), default=0.00)
    status = db.Column(db.SmallInteger, default=1)  # 1=营业, 0=休息
    password_hash = db.Column(db.String(128), default='')
    create_time = db.Column(db.DateTime, default=datetime.now)

    products = db.relationship('Product', backref='merchant', lazy='dynamic')
    orders = db.relationship('Order', backref='merchant', lazy='dynamic')


class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    merchant_id = db.Column(db.Integer, db.ForeignKey('merchant.id'), nullable=False)
    name = db.Column(db.String(128), nullable=False)
    price = db.Column(db.Numeric(8, 2), nullable=False)
    image = db.Column(db.String(256), default='')
    description = db.Column(db.String(512), default='')
    sales = db.Column(db.Integer, default=0)
    category = db.Column(db.String(64), default='热销')
    is_available = db.Column(db.SmallInteger, default=1)


class Order(db.Model):
    __tablename__ = 'order'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    merchant_id = db.Column(db.Integer, db.ForeignKey('merchant.id'), nullable=False)
    rider_id = db.Column(db.Integer, db.ForeignKey('rider.id'), nullable=True)
    total_amount = db.Column(db.Numeric(8, 2), nullable=False)
    status = db.Column(db.SmallInteger, default=0)
    # 0=待支付, 1=待接单, 2=已接单/待取餐, 3=配送中, 4=已完成, -1=已取消
    address = db.Column(db.String(256), default='')
    address_lng = db.Column(db.Numeric(10, 6), default=0.0)
    address_lat = db.Column(db.Numeric(10, 6), default=0.0)
    remark = db.Column(db.String(256), default='')
    create_time = db.Column(db.DateTime, default=datetime.now)
    pay_time = db.Column(db.DateTime, nullable=True)
    accept_time = db.Column(db.DateTime, nullable=True)
    finish_time = db.Column(db.DateTime, nullable=True)
    rider_grab_time = db.Column(db.DateTime, nullable=True)

    items = db.relationship('OrderItem', backref='order', lazy='dynamic')


class OrderItem(db.Model):
    __tablename__ = 'order_item'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    product_name = db.Column(db.String(128), default='')
    quantity = db.Column(db.Integer, nullable=False, default=1)
    price = db.Column(db.Numeric(8, 2), nullable=False)


class Rider(db.Model):
    __tablename__ = 'rider'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(64), nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    lng = db.Column(db.Numeric(10, 6), default=0.0)
    lat = db.Column(db.Numeric(10, 6), default=0.0)
    status = db.Column(db.SmallInteger, default=0)  # 0=空闲, 1=配送中
    password_hash = db.Column(db.String(128), default='')
    create_time = db.Column(db.DateTime, default=datetime.now)


class Admin(db.Model):
    __tablename__ = 'admin'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), default='')


class UserAddress(db.Model):
    __tablename__ = 'user_address'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(32), nullable=False, default='')       # 收件人姓名
    phone = db.Column(db.String(20), nullable=False, default='')      # 收件人电话
    address = db.Column(db.String(256), nullable=False, default='')   # 详细地址文字
    lng = db.Column(db.Numeric(10, 6), default=0.0)                  # 经度
    lat = db.Column(db.Numeric(10, 6), default=0.0)                  # 纬度
    tag = db.Column(db.String(16), default='')                       # 标签：家/公司/学校
    is_default = db.Column(db.SmallInteger, default=0)                # 1=默认地址
    create_time = db.Column(db.DateTime, default=datetime.now)

    user = db.relationship('User', backref='addresses')


class UserFavoriteMerchant(db.Model):
    """用户收藏商家"""
    __tablename__ = 'user_favorite_merchant'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    merchant_id = db.Column(db.Integer, db.ForeignKey('merchant.id'), nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.now)
    __table_args__ = (db.UniqueConstraint('user_id', 'merchant_id', name='uq_user_merchant'),)
