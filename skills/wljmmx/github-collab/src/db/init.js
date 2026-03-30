const { getDatabaseManager } = require('./database-manager');
const { getDatabaseConfig } = require('../config');

/**
 * 创建所有表
 */
function createTables(db) {
  if (!db) {
    console.error('❌ 数据库连接未初始化');
    return;
  }

  console.log('📋 创建表结构...');

  // Agents 表
  db.exec(`
        CREATE TABLE IF NOT EXISTS agents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            type TEXT NOT NULL,
            status TEXT DEFAULT 'idle',
            address TEXT,
            current_task_id INTEGER,
            max_concurrent_tasks INTEGER DEFAULT 1,
            skills TEXT,
            last_heartbeat DATETIME,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    `);
  console.log('  ✓ agents');

  // Agent Configs 表
  db.exec(`
        CREATE TABLE IF NOT EXISTS agent_configs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_id INTEGER NOT NULL,
            config_key TEXT NOT NULL,
            config_value TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (agent_id) REFERENCES agents(id)
        )
    `);
  console.log('  ✓ agent_configs');

  // Message Logs 表
  db.exec(`
        CREATE TABLE IF NOT EXISTS message_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_id INTEGER,
            message_type TEXT NOT NULL,
            content TEXT,
            status TEXT DEFAULT 'pending',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (agent_id) REFERENCES agents(id)
        )
    `);
  console.log('  ✓ message_logs');

  // Tasks 表
  db.exec(`
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'pending',
            priority INTEGER DEFAULT 2,
            assigned_agent_id INTEGER,
            parent_task_id INTEGER,
            project_id INTEGER,
            estimated_hours REAL,
            actual_hours REAL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            started_at DATETIME,
            completed_at DATETIME,
            FOREIGN KEY (assigned_agent_id) REFERENCES agents(id),
            FOREIGN KEY (parent_task_id) REFERENCES tasks(id),
            FOREIGN KEY (project_id) REFERENCES projects(id)
        )
    `);
  console.log('  ✓ tasks');

  // Task Assignments 表
  db.exec(`
        CREATE TABLE IF NOT EXISTS task_assignments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER NOT NULL,
            agent_id INTEGER NOT NULL,
            assigned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            completed_at DATETIME,
            FOREIGN KEY (task_id) REFERENCES tasks(id),
            FOREIGN KEY (agent_id) REFERENCES agents(id)
        )
    `);
  console.log('  ✓ task_assignments');

  // Task History 表
  db.exec(`
        CREATE TABLE IF NOT EXISTS task_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER NOT NULL,
            old_status TEXT,
            new_status TEXT,
            changed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (task_id) REFERENCES tasks(id)
        )
    `);
  console.log('  ✓ task_history');

  // Configs 表
  db.exec(`
        CREATE TABLE IF NOT EXISTS configs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT UNIQUE NOT NULL,
            value TEXT,
            description TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    `);
  console.log('  ✓ configs');

  // Config 表（兼容旧版本）
  db.exec(`
        CREATE TABLE IF NOT EXISTS config (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT UNIQUE NOT NULL,
            value TEXT,
            description TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    `);
  console.log('  ✓ config');

  // Task Dependencies 表
  db.exec(`
        CREATE TABLE IF NOT EXISTS task_dependencies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_id INTEGER NOT NULL,
            depends_on_task_id INTEGER NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (task_id) REFERENCES tasks(id),
            FOREIGN KEY (depends_on_task_id) REFERENCES tasks(id)
        )
    `);
  console.log('  ✓ task_dependencies');

  // Projects 表
  db.exec(`
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'active',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    `);
  console.log('  ✓ projects');

  // Performance Metrics 表
  db.exec(`
        CREATE TABLE IF NOT EXISTS performance_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            metric_name TEXT NOT NULL,
            metric_value REAL NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            context TEXT
        )
    `);
  console.log('  ✓ performance_metrics');

  // Sessions 表
  db.exec(`
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT UNIQUE NOT NULL,
            user_id TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            expires_at DATETIME,
            is_valid INTEGER DEFAULT 1
        )
    `);
  console.log('  ✓ sessions');

  // Users 表
  db.exec(`
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            status TEXT DEFAULT 'active',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    `);
  console.log('  ✓ users');
}

/**
 * 创建索引
 */
function createIndexes(db) {
  console.log('🔍 创建索引...');

  db.exec(`CREATE INDEX IF NOT EXISTS idx_agents_status ON agents(status)`);
  console.log('  ✓ idx_agents_status');

  db.exec(`CREATE INDEX IF NOT EXISTS idx_agents_type ON agents(type)`);
  console.log('  ✓ idx_agents_type');

  db.exec(`CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status)`);
  console.log('  ✓ idx_tasks_status');

  db.exec(`CREATE INDEX IF NOT EXISTS idx_tasks_priority ON tasks(priority)`);
  console.log('  ✓ idx_tasks_priority');

  db.exec(`CREATE INDEX IF NOT EXISTS idx_tasks_assigned_agent ON tasks(assigned_agent_id)`);
  console.log('  ✓ idx_tasks_assigned_agent');

  db.exec(`CREATE INDEX IF NOT EXISTS idx_tasks_project ON tasks(project_id)`);
  console.log('  ✓ idx_tasks_project');

  db.exec(`CREATE INDEX IF NOT EXISTS idx_task_dependencies_task ON task_dependencies(task_id)`);
  console.log('  ✓ idx_task_dependencies_task');

  db.exec(
    `CREATE INDEX IF NOT EXISTS idx_task_dependencies_depends ON task_dependencies(depends_on_task_id)`
  );
  console.log('  ✓ idx_task_dependencies_depends');

  db.exec(`CREATE INDEX IF NOT EXISTS idx_message_logs_agent ON message_logs(agent_id)`);
  console.log('  ✓ idx_message_logs_agent');

  db.exec(`CREATE INDEX IF NOT EXISTS idx_message_logs_status ON message_logs(status)`);
  console.log('  ✓ idx_message_logs_status');
}

/**
 * 插入默认数据
 */
function insertDefaultData(db) {
  console.log('📝 插入默认数据...');

  // 插入默认配置
  const defaultConfigs = [
    { key: 'SYSTEM_VERSION', value: '1.0.0', description: '系统版本' },
    {
      key: 'SYSTEM_NAME',
      value: 'GitHub Collaborative Development System',
      description: '系统名称'
    },
    { key: 'MAX_PARALLEL_AGENTS', value: '3', description: '最大并行 Agent 数量' },
    { key: 'DEFAULT_PRIORITY', value: '2', description: '默认任务优先级' }
  ];

  defaultConfigs.forEach((cfg) => {
    db.prepare(`INSERT OR IGNORE INTO configs (key, value, description) VALUES (?, ?, ?)`).run(
      cfg.key,
      cfg.value,
      cfg.description
    );
  });
  console.log(`  ✓ 插入 ${defaultConfigs.length} 条默认配置`);

  // 插入默认项目
  const defaultProjects = [{ name: 'Default Project', description: '默认项目', status: 'active' }];

  defaultProjects.forEach((proj) => {
    db.prepare(`INSERT OR IGNORE INTO projects (name, description, status) VALUES (?, ?, ?)`).run(
      proj.name,
      proj.description,
      proj.status
    );
  });
  console.log(`  ✓ 插入 ${defaultProjects.length} 个默认项目`);
}

/**
 * 数据库初始化脚本
 * 自动创建所有必要的表和索引
 */
async function initDatabase() {
  const dbConfig = getDatabaseConfig();
  console.log('🚀 开始初始化数据库...');
  console.log(`📁 数据库路径：${dbConfig.path}`);
  console.log(`📊 数据库类型：${dbConfig.type}`);
  console.log(`📝 数据库名称：${dbConfig.name}`);

  const dbManager = getDatabaseManager();

  if (!dbManager.init()) {
    console.error('❌ 数据库初始化失败');
    return false;
  }

  const db = dbManager.getDatabase();

  try {
    // 创建所有表
    createTables(db);

    // 创建索引
    createIndexes(db);

    // 插入默认数据
    insertDefaultData(db);

    console.log('✅ 数据库初始化完成');
    return true;
  } catch (error) {
    console.error('❌ 数据库初始化失败:', error.message);
    return false;
  } finally {
    dbManager.close();
  }
}

// 如果直接运行此脚本
if (require.main === module) {
  initDatabase().then((success) => {
    if (success) {
      console.log('✅ 数据库初始化成功');
      process.exit(0);
    } else {
      console.error('❌ 数据库初始化失败');
      process.exit(1);
    }
  });
}

module.exports = { initDatabase, createTables, createIndexes, insertDefaultData };
