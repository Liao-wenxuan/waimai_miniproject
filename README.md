# 🍔 外卖平台 - 全栈 Demo

一个功能完整的外卖系统，包含用户端、商家端、骑手端和管理后台，支持 WebSocket 实时订单推送和高德地图骑手轨迹展示。

## 技术栈

| 层级 | 技术 |
|------|------|
| 后端框架 | Flask 3.0 + Flask-SocketIO |
| 数据库 | MySQL 8.0 + SQLAlchemy |
| 认证 | PyJWT |
| 前端框架 | Vue 3 (Composition API) |
| UI 组件库 | Vant 4 |
| 实时通信 | Socket.IO Client |
| 地图 | 高德地图 JavaScript API v2.0 |
| 构建工具 | Vite 5 |

## 目录结构

```
外卖平台/
├── backend/                  # 后端 Flask 应用
│   ├── app.py                # Flask 主入口 + SocketIO
│   ├── models.py             # SQLAlchemy 数据模型
│   ├── auth.py               # JWT 认证
│   ├── config.py             # 配置（数据库、密钥）
│   ├── utils.py              # 工具函数
│   ├── socket_events.py      # WebSocket 事件处理
│   ├── requirements.txt      # Python 依赖
│   └── routes/               # API 路由
│       ├── user.py           # 用户端 API
│       ├── merchant.py       # 商家端 API
│       ├── rider.py          # 骑手端 API
│       └── admin.py          # 管理后台 API
├── frontend/                 # 前端 Vue 3 应用
│   ├── index.html            # 入口 HTML（含高德地图 SDK）
│   ├── package.json          # 前端依赖
│   ├── vite.config.js        # Vite 配置
│   └── src/
│       ├── main.js           # Vue 入口
│       ├── App.vue           # 根组件
│       ├── router.js         # 路由配置
│       ├── stores/index.js   # Pinia 状态管理 + WebSocket
│       ├── views/            # 页面组件
│       │   ├── Login.vue     # 登录页（用户/商家/骑手）
│       │   ├── Home.vue      # 首页（商家列表）
│       │   ├── Merchant.vue  # 商家详情/菜单
│       │   ├── Cart.vue      # 确认订单
│       │   ├── OrderList.vue # 订单列表
│       │   ├── OrderDetail.vue # 订单详情 + 地图
│       │   ├── Profile.vue   # 个人中心
│       │   ├── MerchantOrder.vue # 商家端订单管理
│       │   └── RiderOrder.vue    # 骑手端接单/配送
│       └── components/       # 可复用组件
│           ├── ProductCard.vue
│           ├── CartSidebar.vue
│           └── RiderMap.vue
├── init.sql                  # 数据库初始化脚本
└── README.md                 # 本文件
```

## 快速开始

### 环境要求

- Python 3.9+
- Node.js 18+
- MySQL 8.0+
- 高德地图 API Key（已内置测试 Key，建议替换为你自己的）

### 1. 初始化数据库

```bash
# 登录 MySQL
mysql -u root -p

# 执行初始化脚本
source init.sql
```

> **注意**：数据库连接配置在 `backend/config.py` 中，默认使用：
> - 用户名：`root`
> - 密码：`213546`（根据你的 MySQL 密码修改）
> - 数据库名：`food_delivery`

### 2. 启动后端

```bash
cd backend

# 创建虚拟环境（推荐）
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 启动后端服务（默认端口 5000）
python app.py
```

### 3. 启动前端

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器（默认端口 3000）
npm run dev
```

### 4. 访问应用

打开浏览器访问：**http://localhost:3000**

## 测试账号

| 角色 | 账号 | 密码/验证码 | 说明 |
|------|------|------------|------|
| 用户 | 任意11位手机号 | 验证码 `123456` | 自动注册+登录 |
| 商家 | `merchant` | `123456` | 管理本店订单 |
| 骑手 | `rider` | `123456` | 接单/配送 |
| 管理员 | `admin` | `admin` | 后台管理 |

## 核心功能说明

### 用户端
1. 手机号验证码登录（验证码写死 123456）
2. 查看附近商家列表（按距离排序）
3. 查看商家菜单，加购商品
4. 购物车实时计算总价
5. 下单 + 模拟支付（点击即支付）
6. 订单列表（按状态 Tab 分类）
7. 订单详情 + 骑手位置地图
8. 个人中心

### 商家端
1. 登录（merchant / 123456）
2. 实时弹窗提醒新订单（WebSocket 推送）
3. 接单 / 拒单
4. 确认完成订单

### 骑手端
1. 登录（rider / 123456）
2. 查看可抢订单（按距离排序）
3. 抢单
4. 每 3 秒自动上报位置（通过 WebSocket 广播给用户）
5. 完成配送

### WebSocket 实时通知
- 用户支付后 → 商家端自动弹出"新订单"通知
- 商家接单后 → 用户端订单状态自动更新
- 骑手上报位置 → 用户端地图骑手图标实时移动

### 高德地图
- 用户端订单详情页展示：商家 → 骑手 → 收货地址的标记点
- 骑手位置实时更新

## 高德地图 API Key 配置

### 内置 Key
代码中已内置测试 Key：`05c9a16f1ed97ea0222817e690e1ca62`

### 替换为自己的 Key
1. 前往 [高德开放平台](https://lbs.amap.com/) 注册并创建应用
2. 获取 Web端(JS API) 的 Key
3. 修改以下两个文件：
   - `backend/config.py` 中的 `AMAP_KEY`
   - `frontend/index.html` 中高德地图 script 标签的 `key` 参数

## API 接口文档

### 通用格式
```json
{
  "code": 200,
  "data": {},
  "msg": "success"
}
```

### 用户端
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/user/login` | 用户登录 |
| GET | `/api/user/profile` | 获取用户信息 |
| PUT | `/api/user/profile` | 更新用户信息 |
| GET | `/api/merchants` | 商家列表 |
| GET | `/api/merchants/:id` | 商家详情+菜单 |
| POST | `/api/orders` | 创建订单 |
| POST | `/api/orders/:id/pay` | 模拟支付 |
| GET | `/api/orders` | 订单列表 |
| GET | `/api/orders/:id` | 订单详情 |

### 商家端
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/merchant/login` | 商家登录 |
| GET | `/api/merchant/orders` | 本店订单列表 |
| POST | `/api/merchant/orders/:id/accept` | 接单 |
| POST | `/api/merchant/orders/:id/reject` | 拒单 |
| POST | `/api/merchant/orders/:id/complete` | 完成订单 |

### 骑手端
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/rider/login` | 骑手登录 |
| GET | `/api/rider/available-orders` | 可抢订单 |
| POST | `/api/rider/orders/:id/grab` | 抢单 |
| POST | `/api/rider/location` | 上报位置 |
| GET | `/api/rider/my-order` | 当前配送订单 |
| POST | `/api/rider/orders/:id/complete` | 完成配送 |

### 管理端
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/admin/login` | 管理员登录 |
| GET | `/api/admin/orders` | 所有订单 |
| GET | `/api/admin/merchants` | 所有商家 |
| GET | `/api/admin/riders` | 所有骑手 |
| GET | `/api/admin/statistics` | 数据统计 |

## 常见问题

**Q: 后端启动报错 `ModuleNotFoundError`？**
A: 确保已激活虚拟环境并执行 `pip install -r requirements.txt`

**Q: 前端连接不到后端？**
A: 检查 `vite.config.js` 中的 proxy 配置，确保后端运行在 5000 端口

**Q: 地图不显示？**
A: 检查高德地图 API Key 是否有效，以及是否在 JS API 安全域名中配置了 `localhost`

**Q: WebSocket 没反应？**
A: 确保使用 `pip install gevent gevent-websocket`，Windows 下可能需要额外配置
