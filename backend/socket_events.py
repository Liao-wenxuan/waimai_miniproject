"""WebSocket 事件处理"""
from flask import request
from flask_socketio import emit, join_room, leave_room
from models import db, Order, Rider

# 由 app.py 在初始化时注入
socketio = None


def register_socket_events(sio):
    """注册 WebSocket 事件"""

    @sio.on('connect')
    def handle_connect():
        """客户端连接"""
        from auth import decode_token
        token = request.args.get('token', '')
        payload = decode_token(token)
        if not payload:
            return False
        user_id = payload['user_id']
        role = payload['role']

        if role == 'user':
            join_room(f'user_{user_id}')
        elif role == 'merchant':
            join_room(f'merchant_{user_id}')
        elif role == 'rider':
            join_room(f'rider_{user_id}')

        emit('connected', {'status': 'ok', 'role': role})

    @sio.on('disconnect')
    def handle_disconnect():
        pass

    @sio.on('rider_location_update')
    def handle_rider_location(data):
        """骑手位置实时更新"""
        from auth import decode_token
        token = request.args.get('token', '')
        payload = decode_token(token)
        if not payload or payload['role'] != 'rider':
            return

        rider_id = payload['user_id']
        lng = data.get('lng')
        lat = data.get('lat')

        rider = Rider.query.get(rider_id)
        if rider:
            rider.lng = lng
            rider.lat = lat
            db.session.commit()

        order = Order.query.filter_by(rider_id=rider_id).filter(
            Order.status == 3
        ).first()

        if order and socketio:
            socketio.emit('location_changed', {
                'rider_id': rider_id,
                'rider_name': rider.name if rider else '',
                'lng': lng,
                'lat': lat,
                'order_id': order.id
            }, room=f'user_{order.user_id}')


def notify_merchant_new_order(merchant_id, order_data):
    """通知商家有新订单"""
    if socketio:
        socketio.emit('new_order', order_data, room=f'merchant_{merchant_id}')


def notify_user_order_update(user_id, order_data):
    """通知用户订单状态更新"""
    if socketio:
        socketio.emit('order_status_changed', order_data, room=f'user_{user_id}')
