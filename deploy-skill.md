# 外卖平台部署 Skill

## 触发条件
用户说"部署"、"上线"、"deploy"、"发布到服务器" 等关键词时激活。

## 部署工作流

### 前置条件
- 服务器 IP + root 密码
- 本地 Node.js 已安装（用于前端构建）
- 服务器为 Ubuntu/CentOS（阿里云/腾讯云等）

### 标准流程（5 步）

```
1. 本地构建前端     → cd frontend && npm run build
2. 打包项目文件     → tar czf (排除 node_modules/__pycache__/.git)
3. 上传到服务器     → scp 到 /root/
4. 服务器端解压配置  → 写 .env + 前端 Dockerfile(纯静态) + Docker镜像源
5. docker compose up → 启动 MySQL + Flask + Nginx
```

### 关键踩坑记录

| 问题 | 原因 | 解决 |
|------|------|------|
| Docker 镜像拉不下来 | 国内墙 Docker Hub | 配置 daemon.json registry-mirrors |
| 前端白屏/MIME type错误 | index.html 和 assets 哈希不匹配 | 必须在同一次构建中生成，不同构建产物混用会导致404 |
| 前端 Dockerfile | 不要在 Dockerfile 里 COPY index.html 覆盖 dist/index.html | Dockerfile 只需 `COPY dist /usr/share/nginx/html` |
| heredoc 换行符截断 | SSH 终端粘贴多行时 `<<'EOF'` 容易卡住 | 用 `printf` 或逐行 `echo` 写文件 |
| 旧容器冲突 | 容器名已被占用 | 先 `docker rm -f` 再启动 |
| daemon.json 换行 | JSON 内含 `\n` 导致 Docker 启动失败 | 用 `printf` 写单行 JSON |
| 服务器 npm build 权限错误 | node_modules 通过 tar 解压后权限异常 | 本地构建好 dist，服务器直接 COPY dist |
| 阿里云安全组 | 80/5000 端口未开放 | 控制台 → 安全组 → 添加入站规则 |

### 服务器环境初始化（仅首次）

```bash
# 安装 Docker（如果没装）
curl -fsSL https://get.docker.com | sh

# 配置国内镜像源
printf '{"registry-mirrors":["https://docker.1ms.run","https://docker.xuanyuan.me"]}\n' > /etc/docker/daemon.json
systemctl restart docker
```

### 前端 Dockerfile（最终版）

```dockerfile
FROM nginx:alpine
COPY dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
```

**不要**额外 `COPY index.html` —— dist 里已经有了 Vite 构建好的 index.html。

### 验证部署

```bash
# 容器状态
docker compose ps

# API 健康检查
curl http://localhost:5000/api/health

# 前端首页
curl -s http://localhost:80 | head -5
```

### 一键脚本

项目根目录下的 `deploy.sh`：
```bash
bash deploy.sh <IP地址> <密码>
```
