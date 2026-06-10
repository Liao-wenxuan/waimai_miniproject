"""种子数据 — 首次启动时自动插入测试商家、商品、订单"""
from datetime import datetime, timedelta
from models import db, Merchant, Product, Rider, Order, OrderItem, User
from utils import hash_password


def seed_data():
    """如果数据库为空，插入种子数据"""
    need_merchants = not Merchant.query.first()
    need_orders = not Order.query.first()

    if not need_merchants and not need_orders:
        return

    if need_merchants:
        print('[Seed] 正在初始化商家和商品...')
        _seed_merchants()

    if need_orders:
        print('[Seed] 正在初始化测试订单...')
        _seed_orders()


def _seed_merchants():

    merchants_data = [
        {
            'name': '蜜雪冰城（四川农业大学雅安校区）',
            'address': '新康路46号川农大校内',
            'phone': '0835-2882001', 'lng': 103.0009, 'lat': 29.9782,
            'rating': 4.8, 'monthly_sales': 3560, 'delivery_fee': 2.0, 'min_price': 6.0,
        },
        {
            'name': '书亦烧仙草(雅安万达店)',
            'address': '熊猫大道66号万达广场3楼',
            'phone': '0835-2882002', 'lng': 103.0150, 'lat': 29.9890,
            'rating': 4.6, 'monthly_sales': 2100, 'delivery_fee': 3.0, 'min_price': 10.0,
        },
        {
            'name': '华莱士(雅安川农店)',
            'address': '人民路128号川农侧门',
            'phone': '0835-2882003', 'lng': 103.0030, 'lat': 29.9810,
            'rating': 4.5, 'monthly_sales': 1850, 'delivery_fee': 2.0, 'min_price': 10.0,
        },
        {
            'name': '正新鸡排(雅安店)',
            'address': '中大街55号步行街口',
            'phone': '0835-2882004', 'lng': 102.9980, 'lat': 29.9750,
            'rating': 4.3, 'monthly_sales': 3200, 'delivery_fee': 1.0, 'min_price': 8.0,
        },
        {
            'name': '一只酸奶牛(川农店)',
            'address': '新康路48号川农商业街',
            'phone': '0835-2882005', 'lng': 103.0015, 'lat': 29.9770,
            'rating': 4.7, 'monthly_sales': 1500, 'delivery_fee': 1.0, 'min_price': 5.0,
        },
        {
            'name': '茶百道(川农大店)',
            'address': '新康路52号川农正门对面',
            'phone': '0835-2882006', 'lng': 103.0025, 'lat': 29.9760,
            'rating': 4.7, 'monthly_sales': 2800, 'delivery_fee': 2.0, 'min_price': 8.0,
        },
        {
            'name': '绝味鸭脖(雅安旗舰店)',
            'address': '人民路89号大北街口',
            'phone': '0835-2882007', 'lng': 102.9950, 'lat': 29.9800,
            'rating': 4.4, 'monthly_sales': 4200, 'delivery_fee': 2.0, 'min_price': 15.0,
        },
        {
            'name': '张亮麻辣烫(川农店)',
            'address': '新康路50号川农美食街',
            'phone': '0835-2882008', 'lng': 103.0010, 'lat': 29.9790,
            'rating': 4.2, 'monthly_sales': 1800, 'delivery_fee': 3.0, 'min_price': 12.0,
        },
    ]

    products_data = {
        '蜜雪冰城': [
            ('柠檬水(大杯)', 5, '新鲜柠檬现榨，清爽解渴', 3500, '畅销爆款'),
            ('草莓摇摇奶昔', 8, '草莓+冰淇淋+茶底', 2800, '畅销爆款'),
            ('蜜桃四季春', 7, '蜜桃果肉+四季春茶', 2200, '果茶系列'),
            ('满杯百香果', 8, '百香果+椰果+茉莉茶', 1800, '果茶系列'),
            ('冰鲜柠檬水', 4, '冰鲜柠檬现调', 4200, '畅销爆款'),
            ('黑糖珍珠圣代', 8, '黑糖珍珠+冰淇淋', 1600, '冰淇淋'),
            ('摩天脆脆', 3, '香脆蛋筒+鲜奶冰淇淋', 3000, '冰淇淋'),
            ('棒打鲜橙', 7, '鲜橙现捣+茉莉绿茶', 1500, '果茶系列'),
        ],
        '书亦烧仙草': [
            ('招牌烧仙草', 12, '仙草冻+花生+葡萄干+奶茶', 1800, '招牌'),
            ('杨枝甘露烧仙草', 15, '芒果+西柚+椰奶+仙草', 1200, '招牌'),
            ('葡萄芋圆冻冻', 13, '葡萄汁+芋圆+果冻', 950, '鲜果'),
            ('西瓜啵啵', 10, '西瓜+脆啵啵+绿茶', 1500, '鲜果'),
            ('黑糖珍珠奶茶', 11, '黑糖珍珠+鲜奶+红茶', 1100, '奶茶'),
        ],
        '华莱士': [
            ('香辣鸡腿堡', 12, '实惠好吃的鸡腿堡', 2300, '热销'),
            ('奥尔良烤鸡腿堡', 14, '烤制风味', 1800, '热销'),
            ('鸡米花', 8, '一口一个美味', 3000, '小食'),
            ('薯条(中)', 7, '金黄香脆', 2800, '小食'),
            ('冰可乐(中)', 5, '爽口可乐', 3500, '饮品'),
        ],
        '正新鸡排': [
            ('招牌大鸡排', 15, '外酥里嫩超大鸡排', 2800, '热销'),
            ('香辣鸡排', 16, '秘制香辣调料', 1900, '热销'),
            ('火爆大鱿鱼', 18, '整只鱿鱼铁板烤制', 1500, '招牌'),
            ('烤肉串(10串)', 12, '秘制酱料烤肉串', 2200, '烤串'),
            ('甘梅地瓜条', 8, '甜糯红薯条', 1800, '小食'),
        ],
        '一只酸奶牛': [
            ('原味酸奶紫米露', 10, '酸奶+紫米+冰沙', 1600, '招牌'),
            ('草莓酸奶紫米露', 12, '草莓+酸奶+紫米', 1300, '招牌'),
            ('芒果酸奶刨冰', 13, '鲜芒果+酸奶刨冰', 980, '刨冰'),
            ('鲜果酸奶杯', 15, '当季鲜果+浓稠酸奶', 850, '鲜果'),
            ('原味酸奶(杯)', 8, '浓稠发酵鲜酸奶', 1100, '经典'),
        ],
        '茶百道': [
            ('杨枝甘露', 16, '芒果+西柚+椰奶+西米', 1800, '招牌'),
            ('茉莉奶绿', 12, '茉莉花茶+鲜奶', 1500, '奶茶'),
            ('豆乳玉麒麟', 15, '豆乳+玉麒麟茶底', 1200, '招牌'),
            ('超级杯水果茶', 18, '多种鲜果+绿茶', 950, '果茶'),
            ('芋圆奶茶', 13, 'Q弹芋圆+红茶', 1100, '奶茶'),
        ],
        '绝味鸭脖': [
            ('招牌鸭脖(中)', 20, '秘制卤料鲜辣入味', 2200, '招牌'),
            ('鸭锁骨(份)', 18, '酱香浓郁有嚼劲', 1500, '鸭货'),
            ('毛豆(份)', 10, '鲜香入味下酒菜', 1800, '素菜'),
            ('藕片(份)', 8, '脆爽藕片麻辣味', 1400, '素菜'),
            ('鸡爪(5只)', 15, '软糯脱骨卤鸡爪', 1100, '招牌'),
        ],
        '张亮麻辣烫': [
            ('麻辣烫(自选)', 18, '自选食材麻辣汤底', 1600, '招牌'),
            ('麻辣拌(自选)', 18, '自选食材麻酱干拌', 1200, '招牌'),
            ('酸辣粉', 12, '红薯粉酸辣开胃', 900, '粉面'),
            ('牛肉面', 15, '大块牛肉手工面', 800, '粉面'),
            ('冰粉', 8, '手搓冰粉清凉解辣', 1300, '甜品'),
        ],
    }

    rider_data = [
        {'name': '张骑手', 'phone': '13300000001', 'lng': 103.001, 'lat': 29.978},
        {'name': '李骑手', 'phone': '13300000002', 'lng': 103.010, 'lat': 29.980},
        {'name': '王骑手', 'phone': '13300000003', 'lng': 102.990, 'lat': 29.970},
    ]

    for r in rider_data:
        rider = Rider(name=r['name'], phone=r['phone'], lng=r['lng'], lat=r['lat'],
                      password_hash=hash_password('123456'))
        db.session.add(rider)

    for md in merchants_data:
        m = Merchant(
            name=md['name'], address=md['address'], phone=md['phone'],
            lng=md['lng'], lat=md['lat'], rating=md['rating'],
            monthly_sales=md['monthly_sales'], delivery_fee=md['delivery_fee'],
            min_price=md['min_price'], status=1,
            password_hash=hash_password('123456')
        )
        db.session.add(m)
        db.session.flush()

        # 匹配商品
        for key, prods in products_data.items():
            if key in md['name']:
                for p_name, p_price, p_desc, p_sales, p_cat in prods:
                    p = Product(
                        merchant_id=m.id, name=p_name, price=p_price,
                        description=p_desc, sales=p_sales, category=p_cat, is_available=1
                    )
                    db.session.add(p)
                break

    db.session.commit()
    print(f'[Seed] 完成！已插入 {len(merchants_data)} 个商家、{len(rider_data)} 个骑手')


def _seed_orders():
    merchant = Merchant.query.first()
    if not merchant: return

    users = User.query.all()
    riders = Rider.query.all()
    if not users or not riders: return

    # 查找真实产品ID
    products = Product.query.filter_by(merchant_id=merchant.id).all()
    prod_map = {p.name: p.id for p in products}

    now = datetime.now()
    test_orders = [
        {'status': 1, 'user': 0, 'total': 28.00, 'addr': '川农大第二教学区', 'remark': '少冰', 'ago': 5,
         'items': [('柠檬水(大杯)', 2, 5), ('摩天脆脆', 3, 3), ('草莓摇摇奶昔', 1, 8)]},
        {'status': 1, 'user': 1, 'total': 42.00, 'addr': '川农大图书馆', 'remark': '', 'ago': 12,
         'items': [('满杯百香果', 2, 8), ('蜜桃四季春', 2, 7), ('黑糖珍珠圣代', 1, 8), ('冰鲜柠檬水', 1, 4)]},
        {'status': 2, 'user': 0, 'total': 15.00, 'addr': '川农大体育馆', 'remark': '加糖', 'ago': 30,
         'items': [('棒打鲜橙', 1, 7), ('摩天脆脆', 2, 3), ('冰鲜柠檬水', 1, 4)]},
        {'status': 3, 'user': 1, 'total': 35.00, 'addr': '川农大逸夫楼', 'remark': '门牌号302', 'ago': 60,
         'items': [('草莓摇摇奶昔', 2, 8), ('满杯百香果', 1, 8), ('蜜桃四季春', 1, 7), ('柠檬水(大杯)', 1, 5)]},
        {'status': 4, 'user': 0, 'total': 21.00, 'addr': '川农大第十教学楼', 'remark': '', 'ago': 120,
         'items': [('冰鲜柠檬水', 3, 4), ('摩天脆脆', 3, 3)]},
        {'status': 4, 'user': 1, 'total': 52.00, 'addr': '川农大学生宿舍1号楼', 'remark': '快点送', 'ago': 180,
         'items': [('满杯百香果', 2, 8), ('草莓摇摇奶昔', 1, 8), ('蜜桃四季春', 2, 7), ('黑糖珍珠圣代', 2, 8)]},
    ]

    for od in test_orders:
        user = users[od['user'] % len(users)]
        order = Order(
            user_id=user.id, merchant_id=merchant.id,
            total_amount=od['total'], status=od['status'],
            address=od['addr'], remark=od['remark'],
            create_time=now - timedelta(minutes=od['ago']),
            pay_time=now - timedelta(minutes=od['ago']),
        )
        if od['status'] >= 2:
            order.accept_time = now - timedelta(minutes=od['ago'] - 2)
        if od['status'] >= 3:
            order.rider_id = riders[0].id
            order.rider_grab_time = now - timedelta(minutes=od['ago'] - 5)
        if od['status'] >= 4:
            order.finish_time = now - timedelta(minutes=0)

        db.session.add(order)
        db.session.flush()

        for item_name, qty, price in od['items']:
            pid = prod_map.get(item_name, products[0].id if products else 1)
            oi = OrderItem(order_id=order.id, product_id=pid, product_name=item_name, quantity=qty, price=price)
            db.session.add(oi)

    db.session.commit()
    print(f'[Seed] 完成！已插入 {len(test_orders)} 个测试订单')
