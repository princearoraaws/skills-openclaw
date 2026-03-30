# GitHub Collaboration Skill

GitHub 项目协作开发技能 - 支持多 Agent 协同编程、任务分配、代码审查

## 🚀 功能特性

### 核心功能
- **多 Agent 协同**: DevAgent、TestAgent、ReviewAgent 分工协作
- **任务管理**: 任务分解、分配、跟踪、依赖管理
- **项目管理**: 项目创建、任务规划、进度跟踪
- **配置管理**: 集中化配置，支持环境变量覆盖
- **性能监控**: 实时性能指标、查询优化、缓存机制

### 技术亮点
- **统一数据库**: 单一 SQLite 数据库，包含所有业务数据
- **配置化**: 所有配置可通过环境变量调整
- **查询优化**: 缓存、批量查询、N+1 优化
- **自动恢复**: Agent 崩溃自动恢复、任务自动重试
- **优先级调度**: 基于优先级的任务调度系统

## 📁 项目结构

```
github-collab/
├── src/
│   ├── core/                    # 核心模块
│   │   ├── main-controller.js   # 主控制器
│   │   ├── dev-agent.js         # 开发 Agent
│   │   ├── test-agent.js        # 测试 Agent
│   │   └── task-manager-enhanced.js  # 增强任务管理器
│   ├── db/                      # 数据库模块
│   │   ├── database-manager.js  # 数据库管理器
│   │   ├── agent-manager.js     # Agent 管理
│   │   ├── task-manager.js      # 任务管理
│   │   ├── config-manager.js    # 配置管理
│   │   ├── project-manager.js   # 项目管理
│   │   ├── task-dependency-manager.js  # 任务依赖
│   │   └── task-distribution-manager.js  # 任务分发
│   ├── scripts/                 # CLI 脚本
│   │   ├── cli-commands.js      # 通用命令
│   │   ├── task-cli.js          # 任务 CLI
│   │   ├── project-manager.js   # 项目 CLI
│   │   ├── agent-assign.js      # Agent 分配
│   │   ├── agent-queue.js       # Agent 队列
│   │   └── config-cli.js        # 配置 CLI
│   ├── config.js                # 配置管理
│   ├── db.js                    # 数据库封装
│   ├── db-optimized.js          # 优化版数据库
│   └── index.js                 # 主入口
├── test/                        # 测试文件
├── docs/                        # 文档
├── .github-collab-config.json   # 配置文件
├── SKILL.md                     # Skill 文档
├── PROJECT_STRUCTURE.md         # 项目结构文档
├── DATABASE_MERGED.md           # 数据库合并记录
└── CONFIG_UPDATE_REPORT.md      # 配置更新报告
```

## 🛠️ 安装配置

### 1. 安装依赖

```bash
npm install better-sqlite3 commander chalk
```

### 2. 配置环境变量

创建 `.env` 文件或设置环境变量：

```bash
# 数据库配置
DATABASE_TYPE=sqlite3
DATABASE_NAME=github-collab
DATABASE_DIR=./src/db
DATABASE_PATH=/path/to/database.db  # 优先级最高

# 性能配置
DATABASE_POOL_SIZE=10
DATABASE_TIMEOUT=5000
CACHE_TTL=300

# Agent 配置
MAX_PARALLEL_AGENTS=3
AUTO_RECOVERY=true
PRIORITY_THRESHOLD=5
```

### 3. 初始化数据库

```bash
node src/scripts/init-db.js
```

## 📖 使用指南

### 基础使用

#### 1. 创建项目

```bash
# 使用 CLI 创建项目
node src/scripts/project-manager.js create --name "My Project" --description "Project description"
```

#### 2. 添加任务

```bash
# 添加任务
node src/scripts/task-cli.js add --title "Task Title" --priority 5 --projectId 1
```

#### 3. 分配任务给 Agent

```bash
# 分配任务
node src/scripts/agent-assign.js assign --taskId 1 --agentId 1
```

#### 4. 查看任务状态

```bash
# 查看所有任务
node src/scripts/task-cli.js list

# 查看任务详情
node src/scripts/task-cli.js show --id 1
```

### 高级使用

#### 配置化数据库路径

```bash
# 使用默认配置
node src/scripts/init.js

# 自定义数据库名称
DATABASE_NAME=my-custom-db node src/scripts/init.js

# 自定义数据库目录
DATABASE_DIR=/path/to/db DATABASE_NAME=my-db node src/scripts/init.js

# 指定完整路径（优先级最高）
DATABASE_PATH=/full/path/to/database.db node src/scripts/init.js
```

#### 在代码中使用

```javascript
const { getDatabaseManager } = require('./src/db/database-manager');
const AgentManager = require('./src/db/agent-manager');
const TaskManager = require('./src/db/task-manager');

// 获取数据库管理器
const dbManager = getDatabaseManager();

// 初始化数据库
dbManager.init();

// 使用 Agent 管理器
const agentManager = new AgentManager();
const agents = agentManager.getAllAgents();

// 使用任务管理器
const taskManager = new TaskManager();
const tasks = taskManager.getAllTasks();

// 关闭连接
dbManager.close();
```

## 🗄️ 数据库架构

### 统一数据库

所有数据存储在单个 SQLite 数据库文件中：

**默认位置**: `./src/db/github-collab.db`

**包含的表**:
1. **agents** - Agent 信息（4 条记录）
2. **agent_configs** - Agent 配置
3. **message_logs** - 消息日志
4. **tasks** - 任务信息
5. **task_assignments** - 任务分配
6. **task_history** - 任务历史
7. **configs** - 系统配置（1 条记录）
8. **config** - 配置表（备用）
9. **task_dependencies** - 任务依赖
10. **projects** - 项目信息
11. **performance_metrics** - 性能指标
12. **sessions** - 会话管理

### 数据库迁移

从 4 个独立数据库合并为 1 个统一数据库：

**迁移前**:
- agents.db
- config.db
- github-collab.db
- tasks.db

**迁移后**:
- github-collab.db（统一数据库）

**数据完整性**: ✅ 所有数据已完整迁移，无数据丢失

## 🔧 配置说明

### 配置优先级

1. **DATABASE_PATH** (最高优先级) - 指定完整路径
2. **DATABASE_DIR + DATABASE_NAME** - 组合路径
3. **默认配置** (最低优先级) - `./src/db/github-collab.db`

### 配置项

| 配置项 | 默认值 | 环境变量 | 说明 |
|--------|--------|---------|------|
| DATABASE_TYPE | sqlite3 | DATABASE_TYPE | 数据库类型 |
| DATABASE_NAME | github-collab | DATABASE_NAME | 数据库文件名 |
| DATABASE_DIR | ./src/db | DATABASE_DIR | 数据库目录 |
| DATABASE_PATH | (自动生成) | DATABASE_PATH | 完整路径 |
| DATABASE_POOL_SIZE | 10 | DATABASE_POOL_SIZE | 连接池大小 |
| DATABASE_TIMEOUT | 5000 | DATABASE_TIMEOUT | 查询超时（毫秒） |
| CACHE_TTL | 300 | CACHE_TTL | 缓存过期时间（秒） |
| MAX_PARALLEL_AGENTS | 3 | MAX_PARALLEL_AGENTS | 最大并行 Agent 数 |
| AUTO_RECOVERY | true | AUTO_RECOVERY | 自动恢复 |
| PRIORITY_THRESHOLD | 5 | PRIORITY_THRESHOLD | 优先级阈值 |

## 📊 性能优化

### 查询优化

- **缓存机制**: 查询结果缓存，减少数据库压力
- **批量查询**: 合并多个查询为一次批量查询
- **N+1 优化**: 避免 N+1 查询问题
- **索引优化**: 关键查询字段建立索引
- **WAL 模式**: 启用 Write-Ahead Logging 提高并发性能

### 性能指标

- 初始化时间：< 100ms
- 查询响应时间：< 10ms
- 缓存命中率：> 80%
- 内存占用：< 50MB

## 🧪 测试

### 运行测试

```bash
# 配置测试
node test-config.js

# 数据库配置测试
node test-database-config.js

# 完整功能测试
node test-full.js

# 集成测试
node test-integration.js
```

### 测试结果

```
✅ 配置系统：成功
✅ 数据库管理器：成功
✅ Agent 管理器：成功
✅ 任务管理器：成功
✅ 配置管理器：成功
✅ 数据库查询：成功
✅ 环境变量覆盖：成功
✅ 自定义路径：成功
```

## 📝 文档

- [SKILL.md](./SKILL.md) - Skill 详细文档
- [PROJECT_STRUCTURE.md](./PROJECT_STRUCTURE.md) - 项目结构
- [DATABASE_MERGED.md](./DATABASE_MERGED.md) - 数据库合并记录
- [CONFIG_UPDATE_REPORT.md](./CONFIG_UPDATE_REPORT.md) - 配置更新报告

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 License

MIT License

---

**版本**: 1.0.0  
**更新日期**: 2026-03-27  
**状态**: ✅ 配置化完成，测试通过
