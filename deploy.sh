#!/bin/bash
#=============================================
# 外卖平台 — 一键部署脚本
# 用法: bash deploy.sh <服务器IP> <密码>
# 示例: bash deploy.sh 8.137.206.218 Lwx20070513@
#=============================================
set -e

SERVER="${1:?请提供服务器IP}"
PASSWORD="${2:?请提供root密码}"

REMOTE_USER="root"
REMOTE_DIR="/root/waimai"
TARBALL="waimai-deploy.tar.gz"

echo "🚀 外卖平台部署开始"
echo "   目标: $REMOTE_USER@$SERVER"
echo ""

# ---- 1. 本地构建前端 ----
echo "[1/5] 本地构建前端..."
cd "$(dirname "$0")/frontend"
rm -rf dist
npm install --silent 2>/dev/null
npm run build 2>&1 | tail -3
cd ..
echo "   ✅ 前端构建完成"

# ---- 2. 打包项目 ----
echo "[2/5] 打包项目..."
tar czf $TARBALL \
  --exclude='node_modules' --exclude='__pycache__' --exclude='dist' \
  --exclude='.git'       --exclude='.claude'        --exclude='*.pyc' \
  --exclude='taste-skill' --exclude='.agents' --exclude='deploy.sh' \
  backend docker-compose.yml init.sql frontend .dockerignore
echo "   ✅ 打包完成 ($(du -h $TARBALL | cut -f1))"

# ---- 3. 上传 ----
echo "[3/5] 上传到服务器..."
export SSHPASS="$PASSWORD"
sshpass -e scp -o StrictHostKeyChecking=no $TARBALL $REMOTE_USER@$SERVER:/root/
rm -f $TARBALL
echo "   ✅ 上传完成"

# ---- 4. 服务器部署 ----
echo "[4/5] 服务器端部署..."
sshpass -e ssh -o StrictHostKeyChecking=no $REMOTE_USER@$SERVER "
set -e

# 解压项目
rm -rf $REMOTE_DIR
mkdir -p $REMOTE_DIR
tar xzf /root/$TARBALL -C $REMOTE_DIR
rm -f /root/$TARBALL

# 写 .env
cat > $REMOTE_DIR/.env << 'ENVEOF'
MYSQL_ROOT_PASSWORD=213546
MYSQL_DATABASE=food_delivery
DATABASE_URL=mysql+pymysql://root:213546@mysql:3306/food_delivery
SECRET_KEY=food-delivery-secret-key-2024
AMAP_KEY=b088bfacf1f1d34edb868779d2075a54
ENVEOF

# 前端 Dockerfile (纯静态, 不在服务器上构建)
cat > $REMOTE_DIR/frontend/Dockerfile << 'DOCKEREOF'
FROM nginx:alpine
COPY dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
DOCKEREOF

# 配置 Docker 国内镜像源
mkdir -p /etc/docker
printf '{\"registry-mirrors\":[\"https://docker.1ms.run\",\"https://docker.xuanyuan.me\"]}\n' > /etc/docker/daemon.json
systemctl restart docker 2>/dev/null || true

# 安装 Docker (如果没有)
which docker >/dev/null 2>&1 || curl -fsSL https://get.docker.com | sh

# 启动
cd $REMOTE_DIR
docker rm -f food-backend food-mysql food-frontend 2>/dev/null || true
docker compose up -d --build

# 等待就绪
sleep 12
docker compose ps
"

echo "   ✅ 部署完成"

# ---- 5. 验证 ----
echo ""
echo "[5/5] 验证服务..."
sleep 3
HEALTH=$(sshpass -e ssh -o StrictHostKeyChecking=no $REMOTE_USER@$SERVER "curl -s http://localhost:5000/api/health")
echo "   API健康: $HEALTH"

echo ""
echo "=============================="
echo "  🎉 部署成功！"
echo "  前端:    http://$SERVER"
echo "  管理后台: http://$SERVER/#/admin/login"
echo "  管理员:   admin / admin"
echo "=============================="
