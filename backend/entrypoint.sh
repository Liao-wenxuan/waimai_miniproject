#!/bin/bash
# ============================================
# Backend 启动脚本 - 等待 MySQL 就绪后启动
# ============================================
set -e

echo "⏳ 等待 MySQL 就绪..."
while ! python3 -c "import pymysql; pymysql.connect(host='mysql', user='root', password='${MYSQL_ROOT_PASSWORD:-213546}', database='${MYSQL_DATABASE:-food_delivery}')" 2>/dev/null; do
  sleep 2
done

echo "✅ MySQL 已就绪"

# 初始化数据表（幂等，如果 init.sql 已执行则跳过）
python3 -c "
from app import app, db
with app.app_context():
    db.create_all()
    try:
        from seed import seed_data
        seed_data()
        print('🌱 种子数据已加载')
    except Exception as e:
        print(f'⚠️ 种子数据跳过: {e}')
"

echo "🚀 启动 Gunicorn..."
exec gunicorn -k geventwebsocket.gunicorn.workers.GeventWebSocketWorker \
     -w 1 --bind 0.0.0.0:5000 app:app
