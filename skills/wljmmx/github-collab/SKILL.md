# GitHub Collaboration Skill Documentation

GitHub 项目协作开发技能 - 多 Agent 协同编程系统

## 📋 概述

GitHub Collaboration Skill 是一个基于多 Agent 架构的 GitHub 项目协作开发系统。该系统支持 DevAgent、TestAgent、ReviewAgent 等多种 Agent 协同工作，实现任务的自动分配、执行、审查和测试。

### 核心特性

- **多 Agent 协同**: 支持多种 Agent 类型分工协作
- **任务管理**: 完整的任务生命周期管理
- **项目管理**: 项目创建、任务规划、进度跟踪
- **配置化**: 所有配置可通过环境变量调整
- **性能优化**: 查询缓存、批量操作、N+1 优化
- **自动恢复**: Agent 崩溃自动恢复机制

## 🏗️ 架构设计

### 系统架构

```
┌─────────────────────────────────────────────────┐
│              Main Controller                     │
│  (主控制器：任务调度、Agent 管理、并行控制)          │
└─────────────────────────────────────────────────┘
                    │
        ┌───────────┼───────────┐
        ▼           ▼           ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│  DevAgent   │ │ TestAgent   │ │ ReviewAgent │
│ (开发 Agent) │ │ (测试 Agent) │ │ (审查 Agent) │
└─────────────┘ └─────────────┘ └─────────────┘
        │           │           │
        └───────────┼───────────┘
                    ▼
        ┌─────────────────────────┐
        │   Task Manager          │
        │   (任务管理：分配、跟踪)    │
        └─────────────────────────┘
                    │
        ┌───────────┼───────────┐
        ▼           ▼           ▼
┌─────────────┐ ┌─────────────┐ ┌─────────────┐
│   Projects  │ │   Tasks     │ │   Agents    │
│  (项目数据)  │ │  (任务数据)  │ │ (Agent 数据) │
└─────────────┘ └─────────────┘ └─────────────┘
                    │
        ┌───────────┴───────────┐
        ▼                       ▼
┌─────────────────┐ ┌─────────────────┐
│  Database       │ │  Performance    │
│  (统一数据库)    │ │  Monitoring     │
└─────────────────┘ └─────────────────┘
```

### 模块结构

#### 核心模块 (src/core/)

1. **main-controller.js** - 主控制器
   - Agent 启动/停止
   - 任务调度
   - 并行数量控制
   - 自动恢复

2. **dev-agent.js** - 开发 Agent
   - 代码生成
   - 任务执行
   - 代码审查

3. **test-agent.js** - 测试 Agent
   - 测试用例生成
   - 测试执行
   - 结果报告

4. **task-manager-enhanced.js** - 增强任务管理器
   - 任务分配
   - 依赖管理
   - 优先级调度

#### 数据库模块 (src/db/)

1. **database-manager.js** - 数据库管理器
   - 统一数据库连接管理
   - 配置化路径
   - 性能监控

2. **agent-manager.js** - Agent 管理
   - Agent 增删改查
   - Agent 状态管理

3. **task-manager.js** - 任务管理
   - 任务增删改查
   - 任务状态管理

4. **config-manager.js** - 配置管理
   - 系统配置管理
   - 配置持久化

5. **project-manager.js** - 项目管理
   - 项目增删改查
   - 项目进度跟踪

6. **task-dependency-manager.js** - 任务依赖管理
   - 依赖关系管理
   - 依赖解析

7. **task-distribution-manager.js** - 任务分发管理
   - 任务分配策略
   - 负载均衡

#### CLI 脚本 (src/scripts/)

1. **cli-commands.js** - 通用命令系统
2. **task-cli.js** - 任务管理 CLI
3. **project-manager.js** - 项目管理 CLI
4. **agent-assign.js** - Agent 分配 CLI
5. **agent-queue.js** - Agent 队列 CLI
6. **config-cli.js** - 配置管理 CLI

## 🗄️ 数据库架构

### 统一数据库

**文件名**: `github-collab.db`  
**位置**: `./src/db/` (可配置)  
**类型**: SQLite 3  
**大小**: 92KB

### 数据表结构

#### 1. agents (Agent 信息)

```sql
CREATE TABLE agents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    status TEXT DEFAULT 'idle',
    capabilities TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### 2. tasks (任务信息)

```sql
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    priority INTEGER DEFAULT 5,
    status TEXT DEFAULT 'pending',
    project_id INTEGER,
    assigned_to INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(id),
    FOREIGN KEY (assigned_to) REFERENCES agents(id)
);
```

#### 3. projects (项目信息)

```sql
CREATE TABLE projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'active',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### 4. task_assignments (任务分配)

```sql
CREATE TABLE task_assignments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL,
    agent_id INTEGER NOT NULL,
    assigned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME,
    FOREIGN KEY (task_id) REFERENCES tasks(id),
    FOREIGN KEY (agent_id) REFERENCES agents(id)
);
```

#### 5. task_dependencies (任务依赖)

```sql
CREATE TABLE task_dependencies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL,
    depends_on INTEGER NOT NULL,
    dependency_type TEXT DEFAULT 'blocks',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES tasks(id),
    FOREIGN KEY (depends_on) REFERENCES tasks(id)
);
```

#### 6. configs (系统配置)

```sql
CREATE TABLE configs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT UNIQUE NOT NULL,
    value TEXT,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### 7. performance_metrics (性能指标)

```sql
CREATE TABLE performance_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    metric_type TEXT NOT NULL,
    metric_name TEXT NOT NULL,
    value REAL NOT NULL,
    unit TEXT,
    recorded_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### 8. message_logs (消息日志)

```sql
CREATE TABLE message_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_id INTEGER,
    message TEXT NOT NULL,
    level TEXT DEFAULT 'info',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (agent_id) REFERENCES agents(id)
);
```

#### 9. task_history (任务历史)

```sql
CREATE TABLE task_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL,
    old_status TEXT,
    new_status TEXT,
    changed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES tasks(id)
);
```

#### 10. sessions (会话管理)

```sql
CREATE TABLE sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT UNIQUE NOT NULL,
    agent_id INTEGER,
    task_id INTEGER,
    status TEXT DEFAULT 'active',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    ended_at DATETIME,
    FOREIGN KEY (agent_id) REFERENCES agents(id),
    FOREIGN KEY (task_id) REFERENCES tasks(id)
);
```

#### 11. agent_configs (Agent 配置)

```sql
CREATE TABLE agent_configs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_id INTEGER NOT NULL,
    config_key TEXT NOT NULL,
    config_value TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (agent_id) REFERENCES agents(id)
);
```

#### 12. config (配置表 - 备用)

```sql
CREATE TABLE config (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    key TEXT UNIQUE NOT NULL,
    value TEXT
);
```

## ⚙️ 配置系统

### 配置优先级

1. **环境变量** (最高优先级)
2. **配置文件** (.github-collab-config.json)
3. **默认配置** (最低优先级)

### 配置项

#### 数据库配置

| 配置项 | 默认值 | 环境变量 | 说明 |
|--------|--------|---------|------|
| DATABASE_TYPE | sqlite3 | DATABASE_TYPE | 数据库类型 |
| DATABASE_NAME | github-collab | DATABASE_NAME | 数据库文件名 |
| DATABASE_DIR | ./src/db | DATABASE_DIR | 数据库目录 |
| DATABASE_PATH | (自动生成) | DATABASE_PATH | 完整路径 |
| DATABASE_POOL_SIZE | 10 | DATABASE_POOL_SIZE | 连接池大小 |
| DATABASE_TIMEOUT | 5000 | DATABASE_TIMEOUT | 查询超时（毫秒） |

#### 性能配置

| 配置项 | 默认值 | 环境变量 | 说明 |
|--------|--------|---------|------|
| CACHE_TTL | 300 | CACHE_TTL | 缓存过期时间（秒） |
| CACHE_MAX_SIZE | 500 | CACHE_MAX_SIZE | 缓存最大条目数 |

#### Agent 配置

| 配置项 | 默认值 | 环境变量 | 说明 |
|--------|--------|---------|------|
| MAX_PARALLEL_AGENTS | 3 | MAX_PARALLEL_AGENTS | 最大并行 Agent 数 |
| AUTO_RECOVERY | true | AUTO_RECOVERY | 自动恢复 |
| PRIORITY_THRESHOLD | 5 | PRIORITY_THRESHOLD | 优先级阈值 |

### 配置示例

#### 环境变量配置

```bash
# 数据库配置
export DATABASE_TYPE=sqlite3
export DATABASE_NAME=my-custom-db
export DATABASE_DIR=/path/to/db
export DATABASE_PATH=/full/path/to/database.db

# 性能配置
export DATABASE_POOL_SIZE=20
export DATABASE_TIMEOUT=10000
export CACHE_TTL=600

# Agent 配置
export MAX_PARALLEL_AGENTS=5
export AUTO_RECOVERY=true
export PRIORITY_THRESHOLD=3
```

#### 配置文件 (.github-collab-config.json)

```json
{
  "database": {
    "type": "sqlite3",
    "name": "github-collab",
    "path": "./src/db/github-collab.db",
    "poolSize": 10,
    "timeout": 5000
  },
  "cache": {
    "ttl": 300,
    "maxSize": 500
  },
  "agent": {
    "maxParallel": 3,
    "autoRecovery": true,
    "priorityThreshold": 5
  }
}
```

## 🚀 使用指南

### 初始化

```bash
# 安装依赖
npm install

# 初始化数据库
node src/scripts/init-db.js

# 运行主程序
node src/index.js
```

### CLI 命令

#### 项目管理

```bash
# 创建项目
node src/scripts/project-manager.js create --name "My Project" --description "Description"

# 列出项目
node src/scripts/project-manager.js list

# 查看项目详情
node src/scripts/project-manager.js show --id 1
```

#### 任务管理

```bash
# 添加任务
node src/scripts/task-cli.js add --title "Task Title" --priority 5 --projectId 1

# 列出任务
node src/scripts/task-cli.js list

# 查看任务详情
node src/scripts/task-cli.js show --id 1

# 更新任务状态
node src/scripts/task-cli.js update --id 1 --status "in_progress"
```

#### Agent 管理

```bash
# 分配任务给 Agent
node src/scripts/agent-assign.js assign --taskId 1 --agentId 1

# 查看 Agent 队列
node src/scripts/agent-queue.js list
```

#### 配置管理

```bash
# 查看配置
node src/scripts/config-cli.js get --key "database.type"

# 设置配置
node src/scripts/config-cli.js set --key "database.type" --value "sqlite3"
```

### 代码集成

```javascript
const { getDatabaseManager } = require('./src/db/database-manager');
const AgentManager = require('./src/db/agent-manager');
const TaskManager = require('./src/db/task-manager');

// 初始化
const dbManager = getDatabaseManager();
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

## 📊 性能优化

### 查询优化策略

1. **缓存机制**
   - 查询结果缓存
   - 缓存过期时间可配置
   - LRU 淘汰策略

2. **批量查询**
   - 合并多个查询为一次批量查询
   - 减少数据库往返次数

3. **N+1 优化**
   - 批量加载关联数据
   - 避免循环查询

4. **索引优化**
   - 关键查询字段建立索引
   - 定期分析查询性能

5. **WAL 模式**
   - 启用 Write-Ahead Logging
   - 提高并发性能

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

### 测试覆盖

- ✅ 配置系统测试
- ✅ 数据库管理器测试
- ✅ Agent 管理器测试
- ✅ 任务管理器测试
- ✅ 配置管理器测试
- ✅ 数据库查询测试
- ✅ 环境变量覆盖测试
- ✅ 自定义路径测试

## 📝 更新日志

### v1.0.0 (2026-03-27)

- ✅ 完成数据库合并（4 个 → 1 个）
- ✅ 完成配置化重构
- ✅ 完成性能优化
- ✅ 完成测试验证
- ✅ 完成文档更新

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 License

MIT License

---

**版本**: 1.0.0  
**更新日期**: 2026-03-27  
**状态**: ✅ 配置化完成，测试通过  
**维护者**: 小码
