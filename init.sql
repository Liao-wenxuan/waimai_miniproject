-- ========================================
-- 外卖平台数据库初始化脚本
-- MySQL 8.0+
-- ========================================
SET GLOBAL sql_mode = 'NO_ENGINE_SUBSTITUTION';
SET SESSION sql_mode = 'NO_ENGINE_SUBSTITUTION';
SET NAMES utf8mb4;
CREATE DATABASE IF NOT EXISTS food_delivery DEFAULT CHARSET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE food_delivery;
-- ----------------------------
-- 用户表
-- ----------------------------
DROP TABLE IF EXISTS user_favorite_merchant;
DROP TABLE IF EXISTS user_address;
DROP TABLE IF EXISTS order_item;
DROP TABLE IF EXISTS `order`;
DROP TABLE IF EXISTS product;
DROP TABLE IF EXISTS merchant;
DROP TABLE IF EXISTS rider;
DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS admin;
CREATE TABLE `user` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `phone` VARCHAR(20) NOT NULL UNIQUE,
  `nickname` VARCHAR(64) DEFAULT '用户',
  `avatar` VARCHAR(256) DEFAULT '',
  `balance` DECIMAL(10, 2) DEFAULT 0.00,
  `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP,
  INDEX idx_phone (`phone`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;
-- ----------------------------
-- 用户地址表
-- ----------------------------
CREATE TABLE `user_address` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `user_id` INT NOT NULL,
  `name` VARCHAR(32) NOT NULL DEFAULT '',
  `phone` VARCHAR(20) NOT NULL DEFAULT '',
  `address` VARCHAR(256) NOT NULL DEFAULT '',
  `lng` DECIMAL(10, 6) DEFAULT 0.0,
  `lat` DECIMAL(10, 6) DEFAULT 0.0,
  `tag` VARCHAR(16) DEFAULT '',
  `is_default` SMALLINT DEFAULT 0,
  `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (`user_id`) REFERENCES `user`(`id`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;
-- ----------------------------
-- 商家表
-- ----------------------------
CREATE TABLE `merchant` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `name` VARCHAR(128) NOT NULL,
  `address` VARCHAR(256) DEFAULT '',
  `phone` VARCHAR(20) DEFAULT '',
  `lng` DECIMAL(10, 6) DEFAULT 0.0,
  `lat` DECIMAL(10, 6) DEFAULT 0.0,
  `logo` VARCHAR(256) DEFAULT '',
  `rating` DECIMAL(2, 1) DEFAULT 5.0,
  `monthly_sales` INT DEFAULT 0,
  `delivery_fee` DECIMAL(6, 2) DEFAULT 0.00,
  `min_price` DECIMAL(6, 2) DEFAULT 0.00,
  `status` SMALLINT DEFAULT 1,
  `password_hash` VARCHAR(128) DEFAULT '',
  `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;
-- ----------------------------
-- 商品表
-- ----------------------------
CREATE TABLE `product` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `merchant_id` INT NOT NULL,
  `name` VARCHAR(128) NOT NULL,
  `price` DECIMAL(8, 2) NOT NULL,
  `image` VARCHAR(256) DEFAULT '',
  `description` VARCHAR(512) DEFAULT '',
  `sales` INT DEFAULT 0,
  `category` VARCHAR(64) DEFAULT NULL,
  `is_available` SMALLINT DEFAULT 1,
  FOREIGN KEY (`merchant_id`) REFERENCES `merchant`(`id`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;
-- ----------------------------
-- 骑手表
-- ----------------------------
CREATE TABLE `rider` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `name` VARCHAR(64) NOT NULL,
  `phone` VARCHAR(20) NOT NULL UNIQUE,
  `lng` DECIMAL(10, 6) DEFAULT 0.0,
  `lat` DECIMAL(10, 6) DEFAULT 0.0,
  `status` SMALLINT DEFAULT 0,
  `password_hash` VARCHAR(128) DEFAULT '',
  `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;
-- ----------------------------
-- 订单表
-- ----------------------------
CREATE TABLE `order` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `user_id` INT NOT NULL,
  `merchant_id` INT NOT NULL,
  `rider_id` INT DEFAULT NULL,
  `total_amount` DECIMAL(8, 2) NOT NULL,
  `status` SMALLINT DEFAULT 0,
  `address` VARCHAR(256) DEFAULT '',
  `address_lng` DECIMAL(10, 6) DEFAULT 0.0,
  `address_lat` DECIMAL(10, 6) DEFAULT 0.0,
  `remark` VARCHAR(256) DEFAULT '',
  `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP,
  `pay_time` DATETIME DEFAULT NULL,
  `accept_time` DATETIME DEFAULT NULL,
  `finish_time` DATETIME DEFAULT NULL,
  `rider_grab_time` DATETIME DEFAULT NULL,
  FOREIGN KEY (`user_id`) REFERENCES `user`(`id`),
  FOREIGN KEY (`merchant_id`) REFERENCES `merchant`(`id`),
  FOREIGN KEY (`rider_id`) REFERENCES `rider`(`id`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;
-- ----------------------------
-- 订单商品表
-- ----------------------------
CREATE TABLE `order_item` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `order_id` INT NOT NULL,
  `product_id` INT NOT NULL,
  `product_name` VARCHAR(128) DEFAULT '',
  `quantity` INT NOT NULL DEFAULT 1,
  `price` DECIMAL(8, 2) NOT NULL,
  FOREIGN KEY (`order_id`) REFERENCES `order`(`id`),
  FOREIGN KEY (`product_id`) REFERENCES `product`(`id`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;
-- ----------------------------
-- 管理员表
-- ----------------------------
CREATE TABLE `admin` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `username` VARCHAR(64) NOT NULL UNIQUE,
  `password_hash` VARCHAR(128) DEFAULT ''
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;
-- ----------------------------
-- 用户收藏商家表
-- ----------------------------
CREATE TABLE `user_favorite_merchant` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `user_id` INT NOT NULL,
  `merchant_id` INT NOT NULL,
  `create_time` DATETIME DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY `uq_user_merchant` (`user_id`, `merchant_id`),
  FOREIGN KEY (`user_id`) REFERENCES `user`(`id`),
  FOREIGN KEY (`merchant_id`) REFERENCES `merchant`(`id`)
) ENGINE = InnoDB DEFAULT CHARSET = utf8mb4;
-- ========================================
-- 测试数据
-- ========================================
-- 测试用户
INSERT INTO `user` (`phone`, `nickname`, `avatar`, `balance`)
VALUES ('13800138000', '张三', '', 500.00),
  ('13900139000', '李四', '', 300.00);
-- 管理员
INSERT INTO `admin` (`username`, `password_hash`)
VALUES ('admin', SHA2('admin', 256));
-- 骑手
INSERT INTO `rider` (
    `name`,
    `phone`,
    `lng`,
    `lat`,
    `status`,
    `password_hash`
  )
VALUES (
    '张骑手',
    '13300000001',
    103.0010,
    29.9780,
    0,
    SHA2('123456', 256)
  ),
  (
    '李骑手',
    '13300000002',
    103.0100,
    29.9800,
    0,
    SHA2('123456', 256)
  ),
  (
    '王骑手',
    '13300000003',
    102.9900,
    29.9700,
    0,
    SHA2('123456', 256)
  );
-- 商家 (四川雅安雨城区为主，周边补充)
INSERT INTO `merchant` (
    `name`,
    `address`,
    `phone`,
    `lng`,
    `lat`,
    `logo`,
    `rating`,
    `monthly_sales`,
    `delivery_fee`,
    `min_price`,
    `status`,
    `password_hash`
  )
VALUES (
    '蜜雪冰城（四川农业大学雅安校区）',
    '四川省雅安市雨城区新康路46号四川农业大学雅安校区内',
    '0835-2882001',
    103.001,
    29.978,
    'https://img.yzcdn.cn/vant/cat.jpeg',
    4.8,
    3560,
    2.00,
    6.00,
    1,
    SHA2('123456', 256)
  ),
  (
    '书亦烧仙草(雅安万达店)',
    '四川省雅安市雨城区熊猫大道66号万达广场3楼',
    '0835-2882002',
    103.020,
    29.990,
    'https://img.yzcdn.cn/vant/cat.jpeg',
    4.6,
    2100,
    3.00,
    10.00,
    1,
    SHA2('123456', 256)
  ),
  (
    '华莱士(雅安川农店)',
    '四川省雅安市雨城区人民路128号',
    '0835-2882003',
    103.008,
    29.982,
    'https://img.yzcdn.cn/vant/cat.jpeg',
    4.5,
    1850,
    2.00,
    10.00,
    1,
    SHA2('123456', 256)
  ),
  (
    '正新鸡排(雅安店)',
    '四川省雅安市雨城区中大街55号',
    '0835-2882004',
    103.005,
    29.985,
    'https://img.yzcdn.cn/vant/cat.jpeg',
    4.3,
    3200,
    1.00,
    8.00,
    1,
    SHA2('123456', 256)
  ),
  (
    '一只酸奶牛(川农店)',
    '四川省雅安市雨城区新康路48号四川农业大学商业街',
    '0835-2882005',
    103.002,
    29.977,
    'https://img.yzcdn.cn/vant/cat.jpeg',
    4.7,
    1500,
    1.00,
    5.00,
    1,
    SHA2('123456', 256)
  ),
  (
    '茶百道(川农大店)',
    '四川省雅安市雨城区新康路52号',
    '0835-2882006',
    103.003,
    29.976,
    'https://img.yzcdn.cn/vant/cat.jpeg',
    4.7,
    2800,
    2.00,
    8.00,
    1,
    SHA2('123456', 256)
  ),
  (
    '绝味鸭脖(雅安旗舰店)',
    '四川省雅安市雨城区人民路89号',
    '0835-2882007',
    103.012,
    29.983,
    'https://img.yzcdn.cn/vant/cat.jpeg',
    4.4,
    4200,
    2.00,
    15.00,
    1,
    SHA2('123456', 256)
  ),
  (
    '张亮麻辣烫(川农店)',
    '四川省雅安市雨城区新康路50号',
    '0835-2882008',
    103.001,
    29.979,
    'https://img.yzcdn.cn/vant/cat.jpeg',
    4.2,
    1800,
    3.00,
    12.00,
    1,
    SHA2('123456', 256)
  );
-- 蜜雪冰城菜品 (merchant_id=1)
INSERT INTO `product` (
    `merchant_id`,
    `name`,
    `price`,
    `image`,
    `description`,
    `sales`,
    `category`
  )
VALUES (1, '柠檬水(大杯)', 5.00, '', '新鲜柠檬现榨，清爽解渴', 3500, '畅销爆款'),
  (1, '草莓摇摇奶昔', 8.00, '', '草莓+冰淇淋+茶底', 2800, '畅销爆款'),
  (1, '蜜桃四季春', 7.00, '', '蜜桃果肉+四季春茶', 2200, '果茶系列'),
  (1, '满杯百香果', 8.00, '', '百香果+椰果+茉莉茶', 1800, '果茶系列'),
  (1, '冰鲜柠檬水', 4.00, '', '冰鲜柠檬现调', 4200, '畅销爆款'),
  (1, '黑糖珍珠圣代', 8.00, '', '黑糖珍珠+冰淇淋', 1600, '冰淇淋'),
  (1, '摩天脆脆', 3.00, '', '香脆蛋筒+鲜奶冰淇淋', 3000, '冰淇淋'),
  (1, '棒打鲜橙', 7.00, '', '鲜橙现捣+茉莉绿茶', 1500, '果茶系列');
-- 书亦烧仙草菜品 (merchant_id=2)
INSERT INTO `product` (
    `merchant_id`,
    `name`,
    `price`,
    `image`,
    `description`,
    `sales`,
    `category`
  )
VALUES (2, '招牌烧仙草', 12.00, '', '仙草冻+花生+葡萄干+奶茶', 1800, '招牌'),
  (2, '杨枝甘露烧仙草', 15.00, '', '芒果+西柚+椰奶+仙草', 1200, '招牌'),
  (2, '葡萄芋圆冻冻', 13.00, '', '葡萄汁+芋圆+果冻', 950, '鲜果'),
  (2, '西瓜啵啵', 10.00, '', '西瓜+脆啵啵+绿茶', 1500, '鲜果'),
  (2, '黑糖珍珠奶茶', 11.00, '', '黑糖珍珠+鲜奶+红茶', 1100, '奶茶');
-- 华莱士菜品 (merchant_id=3)
INSERT INTO `product` (
    `merchant_id`,
    `name`,
    `price`,
    `image`,
    `description`,
    `sales`,
    `category`
  )
VALUES (3, '香辣鸡腿堡', 12.00, '', '实惠好吃的鸡腿堡', 2300, '热销'),
  (3, '奥尔良烤鸡腿堡', 14.00, '', '烤制风味', 1800, '热销'),
  (3, '鸡米花', 8.00, '', '一口一个美味', 3000, '小食'),
  (3, '薯条(中)', 7.00, '', '金黄香脆', 2800, '小食'),
  (3, '冰可乐(中)', 5.00, '', '爽口可乐', 3500, '饮品');
-- 正新鸡排菜品 (merchant_id=4)
INSERT INTO `product` (
    `merchant_id`,
    `name`,
    `price`,
    `image`,
    `description`,
    `sales`,
    `category`
  )
VALUES (4, '招牌大鸡排', 15.00, '', '外酥里嫩超大鸡排', 2800, '热销'),
  (4, '香辣鸡排', 16.00, '', '秘制香辣调料', 1900, '热销'),
  (4, '火爆大鱿鱼', 18.00, '', '整只鱿鱼铁板烤制', 1500, '招牌'),
  (4, '烤肉串(10串)', 12.00, '', '秘制酱料烤肉串', 2200, '烤串'),
  (4, '甘梅地瓜条', 8.00, '', '甜糯红薯条', 1800, '小食');
-- 一只酸奶牛菜品 (merchant_id=5)
INSERT INTO `product` (
    `merchant_id`,
    `name`,
    `price`,
    `image`,
    `description`,
    `sales`,
    `category`
  )
VALUES (5, '原味酸奶紫米露', 10.00, '', '酸奶+紫米+冰沙', 1600, '招牌'),
  (5, '草莓酸奶紫米露', 12.00, '', '草莓+酸奶+紫米', 1300, '招牌'),
  (5, '芒果酸奶刨冰', 13.00, '', '鲜芒果+酸奶刨冰', 980, '刨冰'),
  (5, '鲜果酸奶杯', 15.00, '', '当季鲜果+浓稠酸奶', 850, '鲜果'),
  (5, '原味酸奶(杯)', 8.00, '', '浓稠发酵鲜酸奶', 1100, '经典');
-- 茶百道菜品 (merchant_id=6)
INSERT INTO `product` (`merchant_id`, `name`, `price`, `image`, `description`, `sales`, `category`)
VALUES (6, '杨枝甘露', 16.00, '', '芒果+西柚+椰奶+西米', 1800, '招牌'),
  (6, '茉莉奶绿', 12.00, '', '茉莉花茶+鲜奶', 1500, '奶茶'),
  (6, '豆乳玉麒麟', 15.00, '', '豆乳+玉麒麟茶底', 1200, '招牌'),
  (6, '超级杯水果茶', 18.00, '', '多种鲜果+绿茶', 950, '果茶'),
  (6, '芋圆奶茶', 13.00, '', 'Q弹芋圆+红茶', 1100, '奶茶');
-- 绝味鸭脖菜品 (merchant_id=7)
INSERT INTO `product` (`merchant_id`, `name`, `price`, `image`, `description`, `sales`, `category`)
VALUES (7, '招牌鸭脖(中)', 20.00, '', '秘制卤料鲜辣入味', 2200, '招牌'),
  (7, '鸭锁骨(份)', 18.00, '', '酱香浓郁有嚼劲', 1500, '鸭货'),
  (7, '毛豆(份)', 10.00, '', '鲜香入味下酒菜', 1800, '素菜'),
  (7, '藕片(份)', 8.00, '', '脆爽藕片麻辣味', 1400, '素菜'),
  (7, '鸡爪(5只)', 15.00, '', '软糯脱骨卤鸡爪', 1100, '招牌');
-- 张亮麻辣烫菜品 (merchant_id=8)
INSERT INTO `product` (`merchant_id`, `name`, `price`, `image`, `description`, `sales`, `category`)
VALUES (8, '麻辣烫(自选)', 18.00, '', '自选食材麻辣汤底', 1600, '招牌'),
  (8, '麻辣拌(自选)', 18.00, '', '自选食材麻酱干拌', 1200, '招牌'),
  (8, '酸辣粉', 12.00, '', '红薯粉酸辣开胃', 900, '粉面'),
  (8, '牛肉面', 15.00, '', '大块牛肉手工面', 800, '粉面'),
  (8, '冰粉', 8.00, '', '手搓冰粉清凉解辣', 1300, '甜品');