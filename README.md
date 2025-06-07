# 信用卡管理系统 💳

一个智能化的信用卡管理系统，帮助用户更好地管理信用卡使用、优化消费策略并及时提醒还款。

## 🌟 项目特色

- 📱 **移动端优先**：基于 uni-app 开发，支持多端运行
- 🤖 **智能推荐**：自动计算并推荐最优信用卡使用方案
- 📊 **数据分析**：全面的信用卡使用数据统计和分析
- ⏰ **智能提醒**：自动还款提醒，避免逾期风险
- 💰 **年费管理**：统一管理各信用卡年费信息

## 🛠️ 技术栈

### 前端
- **框架**：[UniBest](https://github.com/codercup/unibest) - 基于 uni-app 的最佳实践模板
- **构建工具**：Vite
- **语言**：TypeScript
- **UI框架**：Wot Design Uni

### 后端
- **框架**：FastAPI (Python)
- **数据库**：PostgreSQL
- **ORM**：SQLAlchemy
- **认证**：JWT

## 📋 主要功能

### 1. 信用卡管理 💳
- 添加、编辑、删除信用卡信息
- 信用卡基本信息管理（卡号、银行、额度等）
- 信用卡状态跟踪

### 2. 智能推荐 🎯
- 基于消费场景自动推荐最优信用卡
- 积分/里程优化建议
- 费率对比分析

### 3. 年费管理 📅
- 年费到期提醒
- 年费豁免条件跟踪
- 年费成本分析

### 4. 还款提醒 ⏰
- 智能还款日期提醒
- 最低还款额计算
- 还款记录管理

## 📁 项目结构

```
credit-card-manage/
├── mobile/                 # 前端项目 (UniBest)
│   ├── src/
│   │   ├── api/           # API 接口
│   │   ├── components/    # 公共组件
│   │   ├── pages/         # 页面文件
│   │   ├── store/         # 状态管理
│   │   └── utils/         # 工具函数
│   ├── package.json
│   └── vite.config.ts
├── backend/               # 后端项目 (FastAPI)
│   ├── app/
│   │   ├── api/          # API 路由
│   │   ├── core/         # 核心配置
│   │   ├── models/       # 数据库模型
│   │   ├── schemas/      # Pydantic 模型
│   │   └── services/     # 业务逻辑
│   ├── requirements.txt
│   └── main.py
└── README.md
```

## 🚀 快速开始

### 环境要求

- Node.js >= 16.0.0
- Python >= 3.8
- PostgreSQL >= 12.0

### 前端安装运行

```bash
# 进入前端目录
cd mobile

# 安装依赖
pnpm install

# 启动开发服务器
pnpm dev

# 构建生产版本
pnpm build
```

### 后端安装运行

```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 启动开发服务器
uvicorn main:app --reload
```

### 数据库配置

1. 创建 PostgreSQL 数据库
2. 配置环境变量或修改配置文件
3. 运行数据库迁移

```bash
# 数据库迁移
alembic upgrade head
```

## 📱 支持平台

- 📱 **移动端**：iOS、Android
- 🌐 **Web端**：现代浏览器
- 🖥️ **桌面端**：Electron (计划中)

## 🔧 开发说明

### 前端开发
- 使用 UniBest 模板，集成了最佳实践
- 支持 TypeScript，提供类型安全
- 使用 UnoCSS 进行样式开发
- 支持多端编译和发布

### 后端开发
- 遵循 RESTful API 设计规范
- 使用 FastAPI 自动生成 API 文档
- 数据库操作使用 SQLAlchemy ORM
- 支持异步操作，提升性能

### 数据安全
- 敏感信息加密存储
- API 接口权限控制
- 数据传输 HTTPS 加密

## 📄 许可证

MIT License

## 👥 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开起 Pull Request

## 📞 联系方式

- 作者：Leo
- 邮箱：leoyfm@gmail.com
- GitHub：[leoyfm](https://github.com/leoyfm)

## 🙏 致谢

感谢以下开源项目的支持：
- [UniBest](https://github.com/codercup/unibest) - 优秀的 uni-app 开发模板
- [FastAPI](https://fastapi.tiangolo.com/) - 现代化的 Python Web 框架
- [PostgreSQL](https://www.postgresql.org/) - 强大的开源数据库

---

⭐ 如果这个项目对您有帮助，请给一个 Star 支持一下！ 