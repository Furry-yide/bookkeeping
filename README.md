# 🐱 小猫的账本 (Cat Ledger)

一个面向个人 / 家庭用户的轻量级记账 Web 应用：支持记账、分类统计、预算管控，以及多支付源（微信 / 支付宝 / 银行卡等）管理与余额统计。

> 前端 Vue3 + Vite，后端 FastAPI + SQLite，零额外付费组件，适合部署在轻量云服务器。

---

## ✨ 功能特性

- **记账**：记录每一笔收入 / 支出，支持选择分类（使用方向）与支付源（微信支付 / 支付宝 / 银行卡 / 现金 …）
- **统计**：月度收入 / 支出 / 结余概览，按分类的支出占比环形图，数据可导出 CSV
- **预算**：设置月度支出预算，实时查看执行进度与超支提醒
- **支付源余额**：按每个支付源汇总收入 / 支出 / 余额
- **后台管理**：自定义分类（使用方向）与支付源（增 / 删 / 改）
- **登录保护（JWT）**：
  - 未登录可**只读**浏览所有页面
  - 登录后才能**增删改**（记账、预算、管理）
  - 默认账户：`Furry-yide` / `Dede200822`
- **数据迁移**：登录后可一键**导出 / 导入** JSON 全量备份（含流水、支付源、分类、预算、月度统计等）

---

## 🧱 技术架构

| 层 | 技术 |
|----|------|
| 前端 | Vue 3 + Vite + vue-router + axios |
| 后端 | FastAPI + SQLAlchemy 2.0 |
| 数据库 | SQLite（`cat_ledger.db`，零配置） |
| 鉴权 | JWT（PyJWT），密码使用 PBKDF2 哈希存储 |
| 部署 | 轻量云服务器（已内置一键脚本） |

---

## 📁 目录结构

```
bookkeeping/
├── Backend/                # 后端 (FastAPI)
│   ├── app/
│   │   ├── main.py         # 入口、路由注册、默认数据初始化
│   │   ├── database.py     # 引擎 / Session / 建表
│   │   ├── models.py       # ORM 模型
│   │   ├── schemas.py      # Pydantic 模型
│   │   ├── security.py     # 密码哈希 + JWT
│   │   └── routers/        # 各模块接口
│   ├── requirements.txt
│   └── cat_ledger.db       # 运行后自动生成
├── Frontend/               # 前端 (Vue3)
│   ├── src/
│   │   ├── api/            # axios 实例 + 拦截器
│   │   ├── auth.js         # 登录态
│   │   ├── store.js        # 全局响应式状态
│   │   ├── views/          # 记账 / 统计 / 预算 / 管理
│   │   └── components/     # 登录弹窗 / 导入导出 等
│   ├── package.json
│   └── vite.config.js
├── start.sh                # 启动前后端
├── stop.sh                 # 停止
├── status.sh               # 查看运行状态
├── install.sh              # 自动配置环境（Python venv + Node 依赖）
└── README.md
```

---

## 🚀 快速开始（开发 / 单机）

### 方式一：一键脚本（推荐）

```bash
# 1. 自动配置环境（创建 Python venv、安装后端/前端依赖）
./install.sh

# 2. 启动服务
./start.sh

# 3. 查看状态
./status.sh

# 4. 停止服务
./stop.sh
```

启动后访问：
- 前端：http://localhost:5173
- 后端 API：http://localhost:8123

> `install.sh` 在裸 Linux 服务器上也能用：会自动安装 `git` / `Python` / `Node.js 18+`（Debian 走 NodeSource 安装 Node 20），再进行依赖安装。
> 如需从 GitHub 拉取代码，把脚本顶部的 `GITHUB_REPO` 填成你的仓库地址即可。

### 方式二：手动运行

后端：
```bash
cd Backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --port 8123 --reload
```

前端（开发模式，自带 `/api` 代理到 8123）：
```bash
cd Frontend
npm install
npm run dev          # http://localhost:5173
```

---

## 🔐 登录与权限

- 默认账户：**Furry-yide** / **Dede200822**
- 未登录：所有页面**只读**，编辑按钮禁用并提示登录
- 登录后：可进行记账 / 预算 / 管理操作；JWT 令牌存于浏览器 `localStorage`，7 天有效
- 令牌失效或退出后自动回到只读模式

> ⚠️ **生产部署务必修改默认账户密码**，并设置一个强随机的 JWT 密钥：
> ```bash
> export CAT_LEDGER_SECRET="你的强随机密钥"
> ```
> 密钥写在 `Backend/app/security.py` 的 `SECRET_KEY`，未设置时使用内置默认值（不安全）。

---

## 💾 数据备份与迁移

登录后，点击右上角「⬇️ 导出 / ⬆️ 导入」：

- **导出**：下载 `小猫的账本_备份_YYYY-MM-DD.json`，包含
  - 全部资金流水记录
  - 支付源记录
  - 支付类型（分类）记录
  - 月度预算记录
  - 每月统计记录、各支付源余额
- **导入**：上传 JSON 文件，**全量覆盖**当前数据（导入前会二次确认）

---

## 🌐 部署到轻量云（要点）

1. 服务器放行安全组端口 `5173`、`8123`（或改用 80/443 + Nginx 反代）
2. `git clone` 仓库后执行 `./install.sh` → `./start.sh`
3. 设置 `CAT_LEDGER_SECRET` 环境变量后再启动后端
4. 数据文件为 `Backend/cat_ledger.db`，备份时直接拷贝该文件即可
5. （可选）用 systemd / pm2 / supervisor 托管进程，实现开机自启与崩溃重启

---

## 📝 主要 API 速览

| 方法 | 路径 | 说明 | 需登录 |
|------|------|------|--------|
| POST | `/api/auth/login` | 登录获取 JWT | 否 |
| GET | `/api/categories` | 分类列表 | 否 |
| POST/PUT/DELETE | `/api/categories` | 分类增改删 | 是 |
| GET | `/api/payment-sources` | 支付源列表 | 否 |
| POST/PUT/DELETE | `/api/payment-sources` | 支付源增改删 | 是 |
| GET/POST/DELETE | `/api/transactions` | 流水查询 / 新增 / 删除 | 查询否，写是 |
| GET/POST/PUT/DELETE | `/api/budgets` | 预算 | 查询否，写是 |
| GET | `/api/stats/summary` | 月度统计 | 否 |
| GET | `/api/stats/source-balances` | 支付源余额 | 否 |
| GET/POST | `/api/backup/export` `/import` | 全量备份导出 / 导入 | 是 |

---

## 📄 License

个人 / 学习用途，MIT。
