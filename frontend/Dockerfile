# ============================================
# Frontend Dockerfile - 多阶段构建
# Stage 1: 构建 Vue 应用
# Stage 2: Nginx 提供静态文件服务
# ============================================

# ---------- 构建阶段 ----------
FROM node:18-alpine AS builder

WORKDIR /app

# 安装依赖
COPY package.json package-lock.json* ./
RUN npm install

# 复制源码并构建
COPY . .
RUN npm run build

# ---------- 运行阶段 ----------
FROM nginx:alpine

# 复制构建产物
COPY --from=builder /app/dist /usr/share/nginx/html

# 复制 Nginx 配置
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
