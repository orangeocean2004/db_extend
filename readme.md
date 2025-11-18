# 学生信息管理系统

前后端分离：

- backend：FastAPI + SQLAlchemy
- frontend：Vue 3 + Vite

API 文档：启动后访问 <http://127.0.0.1:8000/docs>

初始管理员账号见 backend/app/init_db.py 中的注释或执行时的控制台输出。

## 环境要求

- Windows 10/11
- Python 3.10+
- Node.js 18+（LTS）与 npm
- 可选：Git、Docker

## 一键启动（开发模式）

### 1) 启动后端

```powershell
cd backend

# 建议使用虚拟环境
python -m venv .venv
.\.venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 初始化数据库（会创建表与初始数据）
python -m app.init_db

# 启动服务（默认 8000 端口）
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2) 启动前端

```powershell
cd frontend
npm install
npm run dev
```

默认开发端口为 5173，浏览器打开：

- 前端：<http://127.0.0.1:5173>
- 后端：<http://127.0.0.1:8000>

前端请求统一以 `/api` 开头，开发环境通过 Vite 代理到后端。
如需自配代理（若项目未内置），示例 vite.config.ts：

```ts
server: {
  proxy: {
    '/api': { target: 'http://127.0.0.1:8000', changeOrigin: true }
  }
}
```

## 生产构建

- 前端打包

```powershell
cd frontend
npm run build
```

- 后端运行（示例）

```powershell
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 可选：Docker（仅后端）

仓库已提供 backend/Dockerfile：

```powershell
# 在仓库根目录执行
docker build -t simms-backend ./backend
docker run -p 8000:8000 simms-backend
```

## 常见问题

- 404 /api/...：检查 Vite 代理是否将 /api 转发到 <http://127.0.0.1:8000。>
- 修改密码接口：POST /api/auth/change-password，需携带登录后的认证凭证（Bearer Token）。
- 端口被占用：更换前端端口（--port）或后端端口（--port 8001），并同步更新代理目标地址。
