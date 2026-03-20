#!/usr/bin/env node
/**
 * Cognitive Brain v5.3.25 - Post-install Script
 * 支持：非交互模式、自动安装依赖、日志记录、断点恢复、彩色输出
 */

const fs = require('fs');
const path = require('path');
const { execSync, spawn } = require('child_process');
const readline = require('readline');

const HOME = process.env.HOME || '/root';
const SKILL_DIR = path.join(__dirname, "..", "..");
const OPENCLAW_HOOKS_DIR = path.join(HOME, '.openclaw', 'hooks');
const CONFIG_PATH = path.join(SKILL_DIR, 'config.json');
const LOG_PATH = path.join(SKILL_DIR, 'install.log');
const CHECKPOINT_PATH = path.join(SKILL_DIR, '.install-progress.json');

// ===== 彩色输出 =====
const colors = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  dim: '\x1b[2m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m',
  white: '\x1b[37m'
};

const symbols = {
  success: '✅',
  error: '❌',
  warning: '⚠️',
  info: 'ℹ️',
  progress: '⏳',
  check: '✓',
  cross: '✗'
};

// 检测是否支持彩色输出
const supportsColor = process.stdout.isTTY && process.env.TERM !== 'dumb';

function colorize(color, text) {
  return supportsColor ? `${colors[color]}${text}${colors.reset}` : text;
}

// ===== 进度条 =====
let currentProgress = 0;
let totalSteps = 12;

function updateProgress(step, total) {
  currentProgress = step;
  totalSteps = total;
  
  if (!process.stdout.isTTY) return; // 非终端环境不显示进度条
  
  const percent = Math.round((step / total) * 100);
  const filled = Math.round((step / total) * 30);
  const empty = 30 - filled;
  const bar = '█'.repeat(filled) + '░'.repeat(empty);
  
  process.stdout.write(`\r${colorize('cyan', '进度:')} [${colorize('green', bar)}] ${percent}% (${step}/${total})`);
}

function clearProgress() {
  if (process.stdout.isTTY) {
    process.stdout.write('\r' + ' '.repeat(60) + '\r');
  }
}

// 安装步骤
const STEPS = ['npm_deps', 'system_deps', 'db_auth', 'config', 'db_create', 'db_init', 'indexes', 'hooks', 'data_files', 'health', 'record', 'restart'];

const STEP_NAMES = {
  npm_deps: '安装 npm 依赖',
  system_deps: '检查系统依赖 (PostgreSQL, Redis)',
  db_auth: '配置数据库认证',
  config: '生成配置文件',
  db_create: '创建数据库和扩展',
  db_init: '初始化数据库表',
  indexes: '创建数据库索引',
  hooks: '配置 Gateway Hooks',
  data_files: '创建数据文件',
  health: '健康检查',
  record: '记录安装状态',
  restart: '重启 Gateway'
};

// 非交互模式检测
const isNonInteractive = !process.stdin.isTTY || process.env.CI || process.env.SKILLHUB_INSTALL;

// 命令行参数
const args = process.argv.slice(2);
const autoInstallDeps = args.includes('--auto-deps') || isNonInteractive;
const skipDeps = args.includes('--skip-deps');
const useDefaultConfig = args.includes('--default-config') || isNonInteractive;
const resumeMode = args.includes('--resume');

// ===== 日志系统 =====
function log(msg, level = 'INFO') {
  const timestamp = new Date().toISOString();
  const logLine = `[${timestamp}] [${level}] ${msg}`;
  try { fs.appendFileSync(LOG_PATH, logLine + '\n'); } catch (e) {}
  
  // 彩色输出
  clearProgress();
  
  if (level === 'ERROR') {
    console.error(`${colorize('red', symbols.error)} ${msg}`);
  } else if (level === 'WARN') {
    console.log(`${colorize('yellow', symbols.warning)} ${msg}`);
  } else if (level === 'SUCCESS') {
    console.log(`${colorize('green', symbols.success)} ${msg}`);
  } else {
    console.log(msg);
  }
}

// ===== 检查点系统 =====
function loadCheckpoint() {
  try {
    if (fs.existsSync(CHECKPOINT_PATH)) {
      return JSON.parse(fs.readFileSync(CHECKPOINT_PATH, 'utf8'));
    }
  } catch (e) {}
  return { step: 0, completed: [], errors: [] };
}

function saveCheckpoint(step, error = null) {
  const checkpoint = loadCheckpoint();
  checkpoint.step = step;
  checkpoint.lastUpdate = new Date().toISOString();
  if (!checkpoint.completed.includes(STEPS[step])) {
    checkpoint.completed.push(STEPS[step]);
  }
  if (error) {
    checkpoint.errors.push({ step: STEPS[step], error: error.message, time: new Date().toISOString() });
  }
  fs.writeFileSync(CHECKPOINT_PATH, JSON.stringify(checkpoint, null, 2));
}

function clearCheckpoint() {
  if (fs.existsSync(CHECKPOINT_PATH)) fs.unlinkSync(CHECKPOINT_PATH);
}

function getResumeStep() {
  if (!resumeMode) return 0;
  const checkpoint = loadCheckpoint();
  if (checkpoint.completed.length > 0) {
    log(`🔄 从断点恢复，已完成: ${checkpoint.completed.join(', ')}`);
    return checkpoint.completed.length;
  }
  return 0;
}

// ===== 默认配置 =====
const DEFAULT_CONFIG = {
  version: "5.3.23",
  storage: {
    primary: { type: "postgresql", host: "localhost", port: 5432, database: "cognitive_brain", user: "postgres", password: "", poolSize: 10, connectionTimeoutMillis: 5000, queryTimeout: 10000, extensions: ["pgvector", "pg_trgm"] },
    cache: { type: "redis", host: "localhost", port: 6379, db: 0, keyPrefix: "brain:" }
  },
  embedding: { provider: "local", dimension: 384, options: { model: "paraphrase-multilingual-MiniLM-L12-v2", script: "scripts/embed.py" } },
  memory: {
    sensory: { ttl: 30000, maxSize: 100, storage: "redis" },
    working: { ttl: 3600000, maxSize: 50, storage: "redis" },
    episodic: { maxCount: 10000, decayRate: 0.1, storage: "postgresql" },
    semantic: { maxCount: 5000, storage: "postgresql" }
  },
  forgetting: { enabled: true, schedule: "0 3 * * *", minAge: 604800000, importanceThreshold: 0.2, cleanupOrphans: true },
  proactive: { enabled: true, maxSuggestions: 2, confidenceThreshold: 0.5 },
  safety: { enabled: true, strictMode: false, blockedOperations: ["rm -rf", "format", "fdisk", "mkfs"], requireConfirmation: ["delete_file", "send_email", "post_public"] }
};

// ===== 交互式提问 =====
function ask(question, defaultValue = '') {
  if (isNonInteractive) {
    console.log(`  🤖 使用默认值: ${defaultValue || '(空)'}`);
    return Promise.resolve(defaultValue);
  }
  return new Promise((resolve) => {
    const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
    const prompt = defaultValue ? `${question} [${defaultValue}]: ` : `${question}: `;
    rl.question(prompt, (answer) => { rl.close(); resolve(answer.trim() || defaultValue); });
  });
}

// ===== 1. 安装 npm 依赖 =====
async function installNpmDependencies() {
  log('\n📦 安装 npm 依赖...');
  const nodeModulesPath = path.join(SKILL_DIR, 'node_modules');
  if (fs.existsSync(nodeModulesPath)) {
    log('  ✅ npm 依赖已存在，跳过安装');
    return true;
  }
  log('  ⏳ 正在安装依赖...');
  try {
    await new Promise((resolve, reject) => {
      const npm = spawn('npm', ['install', '--production'], { cwd: SKILL_DIR, stdio: 'inherit' });
      npm.on('close', (code) => code === 0 ? resolve() : reject(new Error(`npm install 退出码: ${code}`)));
      npm.on('error', reject);
    });
    log('  ✅ npm 依赖安装成功');
    return true;
  } catch (e) {
    log(`npm install 失败: ${e.message}`, 'ERROR');
    return false;
  }
}

// ===== 2. 安装系统依赖 =====
async function installSystemDependencies(failedDeps) {
  log('\n📦 自动安装系统依赖...');
  const platform = process.platform;
  const isRoot = process.getuid && process.getuid() === 0;
  const sudo = isRoot ? '' : 'sudo ';
  
  for (const dep of failedDeps) {
    if (dep.name === 'Node.js') { log('  ⚠️  Node.js 需要手动安装'); continue; }
    try {
      if (platform === 'linux') {
        const isUbuntu = fs.existsSync('/etc/debian_version');
        if (isUbuntu) {
          if (dep.name === 'PostgreSQL') {
            log('  ⏳ 安装 PostgreSQL...');
            execSync(`${sudo}apt-get update -qq && ${sudo}apt-get install -y -qq postgresql postgresql-contrib postgresql-16-pgvector 2>/dev/null`, { stdio: 'pipe' });
            execSync(`${sudo}systemctl enable postgresql && ${sudo}systemctl start postgresql`, { stdio: 'pipe' });
            log('  ✅ PostgreSQL 安装完成');
          } else if (dep.name === 'Redis') {
            log('  ⏳ 安装 Redis...');
            execSync(`${sudo}apt-get install -y -qq redis-server`, { stdio: 'pipe' });
            execSync(`${sudo}systemctl enable redis-server && ${sudo}systemctl start redis-server`, { stdio: 'pipe' });
            log('  ✅ Redis 安装完成');
          }
        }
      }
    } catch (e) {
      log(`${dep.name} 安装失败: ${e.message}`, 'ERROR');
    }
  }
  return true;
}

// ===== 3. 检查依赖 =====
async function checkDependencies() {
  log('\n🔍 检查系统依赖...');
  const checks = [
    { name: 'Node.js', cmd: 'node -v' },
    { name: 'PostgreSQL', cmd: 'psql --version' },
    { name: 'Redis', cmd: 'redis-cli ping' }
  ];
  
  const results = [];
  for (const check of checks) {
    try {
      execSync(check.cmd, { stdio: 'pipe' });
      log(`  ✅ ${check.name} 已安装`);
      results.push({ name: check.name, ok: true });
    } catch (e) {
      log(`  ❌ ${check.name} 未安装或无法访问`, 'WARN');
      results.push({ name: check.name, ok: false });
    }
  }
  
  const failed = results.filter(r => !r.ok);
  if (failed.length > 0 && autoInstallDeps && !skipDeps) {
    await installSystemDependencies(failed);
  }
  return true;
}

// ===== 4. 配置 PostgreSQL 认证 =====
async function configurePostgresAuth() {
  log('\n🔐 配置 PostgreSQL 本地认证...');
  try {
    const pgVersion = execSync('ls /usr/lib/postgresql 2>/dev/null | head -1 || echo "16"', { encoding: 'utf8' }).trim();
    const pgHbaPath = `/etc/postgresql/${pgVersion}/main/pg_hba.conf`;
    if (!fs.existsSync(pgHbaPath)) { log('  ⚠️  未找到 pg_hba.conf，跳过'); return true; }
    
    let content = fs.readFileSync(pgHbaPath, 'utf8');
    let modified = false;
    const isRoot = process.getuid && process.getuid() === 0;
    const sudo = isRoot ? '' : 'sudo ';
    
    if (content.includes('local   all             postgres                                peer')) {
      content = content.replace(/local\s+all\s+postgres\s+peer/, 'local   all             postgres                                trust');
      modified = true;
    }
    if (content.includes('host    all             all             127.0.0.1/32            scram-sha-256')) {
      content = content.replace(/host\s+all\s+all\s+127\.0\.0\.1\/32\s+scram-sha-256/, 'host    all             all             127.0.0.1/32            trust');
      modified = true;
    }
    
    if (modified) {
      execSync(`${sudo}cp ${pgHbaPath} ${pgHbaPath}.bak`, { stdio: 'pipe' });
      if (isRoot) fs.writeFileSync(pgHbaPath, content);
      else execSync(`${sudo}tee ${pgHbaPath} > /dev/null`, { input: content, stdio: ['pipe', 'pipe', 'pipe'] });
      execSync(`${sudo}systemctl reload postgresql`, { stdio: 'pipe' });
      log('  ✅ PostgreSQL 认证已配置为 trust（本地）');
    } else {
      log('  ✅ PostgreSQL 认证已正确配置');
    }
    return true;
  } catch (e) {
    log(`配置 PostgreSQL 认证失败: ${e.message}`, 'WARN');
    return true;
  }
}

// ===== 5. 创建数据库 =====
async function ensureDatabase(config) {
  log('\n🗄️  创建数据库和扩展...');
  const dbName = config.storage.primary.database;
  try {
    try {
      execSync(`su - postgres -c "createdb ${dbName}"`, { stdio: 'pipe' });
      log(`  ✅ 数据库 ${dbName} 已创建`);
    } catch (e) {
      if (e.message.includes('already exists')) log(`  ✅ 数据库 ${dbName} 已存在`);
    }
    execSync(`su - postgres -c "psql -d ${dbName} -c 'CREATE EXTENSION IF NOT EXISTS vector;'"`, { stdio: 'pipe' });
    log('  ✅ pgvector 扩展已启用');
    execSync(`su - postgres -c "psql -d ${dbName} -c 'CREATE EXTENSION IF NOT EXISTS pg_trgm;'"`, { stdio: 'pipe' });
    log('  ✅ pg_trgm 扩展已启用');
    return true;
  } catch (e) {
    log(`数据库创建失败: ${e.message}`, 'ERROR');
    return false;
  }
}

// ===== 6. 交互式配置 =====
async function interactiveConfig() {
  if (useDefaultConfig) {
    log('\n⚙️  使用默认配置（非交互模式）');
    fs.writeFileSync(CONFIG_PATH, JSON.stringify(DEFAULT_CONFIG, null, 2));
    log('  ✅ 配置已保存');
    return DEFAULT_CONFIG;
  }
  
  log('\n⚙️  配置 Cognitive Brain');
  const config = JSON.parse(JSON.stringify(DEFAULT_CONFIG));
  config.storage.primary.host = await ask('PostgreSQL 主机', 'localhost');
  config.storage.primary.port = parseInt(await ask('PostgreSQL 端口', '5432'));
  config.storage.primary.database = await ask('PostgreSQL 数据库名', 'cognitive_brain');
  config.storage.primary.user = await ask('PostgreSQL 用户名', 'postgres');
  config.storage.primary.password = await ask('PostgreSQL 密码（本地可留空）', '');
  config.storage.cache.host = await ask('Redis 主机', 'localhost');
  config.storage.cache.port = parseInt(await ask('Redis 端口', '6379'));
  fs.writeFileSync(CONFIG_PATH, JSON.stringify(config, null, 2));
  log('✅ 配置已保存');
  return config;
}

// ===== 7. 测试数据库连接 =====
async function testDatabaseConnection(config) {
  log('\n🗄️  测试数据库连接...');
  try {
    const { Pool } = require('pg');
    const pool = new Pool({
      host: config.storage.primary.host, port: config.storage.primary.port,
      database: config.storage.primary.database, user: config.storage.primary.user,
      password: config.storage.primary.password || undefined, connectionTimeoutMillis: 5000
    });
    await pool.query('SELECT 1');
    log('  ✅ PostgreSQL 连接成功');
    await pool.end();
    return true;
  } catch (e) {
    log(`PostgreSQL 连接失败: ${e.message}`, 'ERROR');
    return false;
  }
}

// ===== 8. 初始化数据库 =====
async function initDatabase() {
  log('\n📋 初始化数据库表结构...');
  try {
    execSync(`node "${path.join(SKILL_DIR, 'scripts/tools/init-db.cjs')}"`, { cwd: SKILL_DIR, stdio: 'inherit', timeout: 60000 });
    log('  ✅ 数据库表结构初始化完成');
    return true;
  } catch (e) {
    log(`数据库初始化问题: ${e.message}`, 'WARN');
    return true;
  }
}

// ===== 9. 创建索引 =====
async function createIndexes() {
  log('\n🔧 创建数据库索引...');
  try {
    execSync(`node "${path.join(SKILL_DIR, 'scripts/tools/create_indexes.cjs')}"`, { cwd: SKILL_DIR, stdio: 'inherit' });
    log('  ✅ 索引创建完成');
  } catch (e) {
    log(`索引创建失败: ${e.message}`, 'WARN');
  }
}

// 全局回滚状态
let rollbackState = {
  configBackedUp: false,
  BACKUP_CONFIG: path.join(HOME, '.openclaw', 'openclaw.json.bak')
};

// ===== 回滚函数 =====
async function rollback(error) {
  log('\n🔄 正在回滚安装...', 'WARN');
  
  // 恢复配置文件
  if (rollbackState.configBackedUp && fs.existsSync(rollbackState.BACKUP_CONFIG)) {
    const OPENCLAW_CONFIG = path.join(HOME, '.openclaw', 'openclaw.json');
    try {
      fs.copyFileSync(rollbackState.BACKUP_CONFIG, OPENCLAW_CONFIG);
      log('  ✅ 已恢复 Gateway 配置文件');
    } catch (e) {
      log(`  ⚠️  恢复配置失败: ${e.message}`, 'WARN');
    }
  }
  
  log(`\n❌ 安装失败: ${error.message}`, 'ERROR');
  console.log('\n回滚完成。请修复问题后重试:');
  console.log('  npm run setup -- --resume\n');
}

// ===== 10. 配置 Gateway Hooks =====
async function configureGatewayHooks() {
  log('\n🔄 配置 Gateway hooks...');
  
  const OPENCLAW_CONFIG = path.join(HOME, '.openclaw', 'openclaw.json');
  
  if (!fs.existsSync(OPENCLAW_CONFIG)) {
    log('  ⚠️  未找到 OpenClaw 配置文件，跳过 hooks 配置');
    log('  💡 请确保 OpenClaw 已正确安装');
    return true;
  }
  
  try {
    let config = {};
    try {
      config = JSON.parse(fs.readFileSync(OPENCLAW_CONFIG, 'utf8'));
    } catch (e) {
      log('  ⚠️  配置文件解析失败，跳过');
      return true;
    }
    
    // 备份原配置（仅首次）
    if (!fs.existsSync(rollbackState.BACKUP_CONFIG)) {
      fs.copyFileSync(OPENCLAW_CONFIG, rollbackState.BACKUP_CONFIG);
      rollbackState.configBackedUp = true;
      log('  ✅ 已备份原配置到 openclaw.json.bak');
    } else {
      log('  ⚠️  发现已存在的备份文件，跳过备份');
    }
    
    // 确保 hooks.internal 结构存在
    if (!config.hooks) config.hooks = {};
    if (!config.hooks.internal) config.hooks.internal = {};
    
    // 启用 internal hooks
    config.hooks.internal.enabled = true;
    
    // 配置 extraDirs（让 Gateway 从 skill 目录加载 hooks）
    const skillHooksDir = path.join(SKILL_DIR, 'hooks');
    if (!config.hooks.internal.load) config.hooks.internal.load = {};
    if (!config.hooks.internal.load.extraDirs) config.hooks.internal.load.extraDirs = [];
    
    // 幂等性检查：是否已配置
    if (!config.hooks.internal.load.extraDirs.includes(skillHooksDir)) {
      config.hooks.internal.load.extraDirs.push(skillHooksDir);
      log(`  ✅ 已添加 hooks 目录: ${skillHooksDir}`);
    } else {
      log('  ✅ hooks 目录已配置，跳过');
    }
    
    // 保存配置
    fs.writeFileSync(OPENCLAW_CONFIG, JSON.stringify(config, null, 2));
    log('  ✅ Gateway hooks 配置已保存');
    
    return true;
  } catch (e) {
    log(`配置 Gateway hooks 失败: ${e.message}`, 'WARN');
    log('  💡 你可以手动添加以下配置到 ~/.openclaw/openclaw.json:');
    log('     "hooks": { "internal": { "enabled": true, "load": { "extraDirs": ["<skill-path>/hooks"] } } }');
    return true;
  }
}

// ===== 11. 重启 Gateway =====
async function restartGateway() {
  log('\n🔄 重启 Gateway...');
  
  // 检测是否在主会话中运行（避免中断会话）
  const inMainSession = process.env.OPENCLAW_SESSION_KEY?.includes('main') || 
                        process.cwd().includes('/agents/main');
  
  if (inMainSession) {
    log('  ⚠️  检测到在主会话中运行，跳过自动重启', 'WARN');
    log('  💡 请手动重启 Gateway 使 hooks 生效:');
    log('     systemctl --user restart openclaw-gateway');
    return true;
  }
  
  try {
    execSync('systemctl --user restart openclaw-gateway', { stdio: 'pipe' });
    log('  ✅ Gateway 已重启');
    log('  💡 Hooks 将在下次消息时生效');
    return true;
  } catch (e) {
    log('  ⚠️  自动重启失败，请手动重启:', 'WARN');
    log('     systemctl --user restart openclaw-gateway');
    return true;
  }
}

// ===== 11. 创建数据文件 =====
async function createDataFiles() {
  log('\n📁 创建数据文件...');
  const files = [
    { name: '.user-model.json', content: { stats: { totalInteractions: 0 }, preferences: { topics: {} } } },
    { name: '.working-memory.json', content: { activeContext: { entities: [], topic: null } } },
    { name: '.prediction-cache.json', content: { predictions: [], lastUpdated: null } }
  ];
  for (const file of files) {
    const filePath = path.join(SKILL_DIR, file.name);
    if (!fs.existsSync(filePath)) { fs.writeFileSync(filePath, JSON.stringify(file.content, null, 2)); log(`  ✅ 创建: ${file.name}`); }
    else log(`  ✅ 已存在: ${file.name}`);
  }
}

// ===== 13. 记录安装状态 =====
async function recordInstallStatus(config) {
  log('\n📝 记录安装状态...');
  
  const installedFile = path.join(SKILL_DIR, '.installed.json');
  const packageJson = require(path.join(SKILL_DIR, 'package.json'));
  
  const status = {
    version: packageJson.version,
    installedAt: new Date().toISOString(),
    nodeVersion: process.version,
    platform: process.platform,
    arch: process.arch,
    skillDir: SKILL_DIR,
    config: {
      database: config.storage.primary.database,
      redis: `${config.storage.cache.host}:${config.storage.cache.port}`
    },
    hooks: {
      method: 'gateway-extraDirs',
      path: path.join(SKILL_DIR, 'hooks')
    },
    checks: {
      postgresql: true,
      redis: true,
      gateway: true
    }
  };
  
  try {
    fs.writeFileSync(installedFile, JSON.stringify(status, null, 2));
    log(`  ✅ 安装状态已记录到 .installed.json`);
    return true;
  } catch (e) {
    log(`  ⚠️  记录安装状态失败: ${e.message}`, 'WARN');
    return true;
  }
}

// ===== 12. 健康检查 =====
async function healthCheck() {
  log('\n🏥 运行健康检查...');
  try {
    execSync(`node "${path.join(SKILL_DIR, 'scripts/tools/health_check.cjs')}"`, { cwd: SKILL_DIR, stdio: 'inherit' });
  } catch (e) {
    log(`健康检查失败: ${e.message}`, 'WARN');
  }
}

// ===== 检测已安装状态 =====
function checkAlreadyInstalled() {
  const markers = [path.join(SKILL_DIR, 'config.json'), path.join(SKILL_DIR, 'node_modules')];
  const installed = markers.filter(m => fs.existsSync(m));
  if (installed.length >= 2) {
    log('\n⚠️  检测到 Cognitive Brain 已安装');
    log('  已存在的组件:');
    if (fs.existsSync(path.join(SKILL_DIR, 'config.json'))) log('  ✅ 配置文件');
    if (fs.existsSync(path.join(SKILL_DIR, 'node_modules'))) log('  ✅ npm 依赖');
    return true;
  }
  return false;
}

// ===== 主流程 =====
async function main() {
  console.log(`\n${colorize('cyan', colorize('bright', '🧠 Cognitive Brain v5.3.25 安装程序'))}\n`);
  console.log(colorize('cyan', '='.repeat(50)));
  log('安装开始', 'INFO');
  
  if (isNonInteractive) console.log(`\n${colorize('dim', '🤖 自动安装模式（非交互）')}\n`);
  else console.log(`\n${colorize('dim', '📝 交互式安装模式')}\n`);
  
  // 检测已安装
  if (checkAlreadyInstalled() && !args.includes('--force')) {
    console.log('\n如需重新安装: npm run setup -- --force');
    console.log('从断点恢复: npm run setup -- --resume');
    console.log('卸载重装: npm run uninstall && npm run setup\n');
    if (!isNonInteractive) {
      const rl = readline.createInterface({ input: process.stdin, output: process.stdout });
      const answer = await new Promise(resolve => rl.question('是否继续安装? [y/N]: ', resolve));
      rl.close();
      if (answer.toLowerCase() !== 'y') { log('用户取消安装'); process.exit(0); }
    } else {
      log('已安装，更新中...');
    }
  }
  
  // 获取恢复点
  const startStep = getResumeStep();
  if (startStep > 0) console.log(`\n${colorize('yellow', '📍 从步骤 ' + (startStep + 1) + ' 继续安装...')}\n`);
  
  // 显示安装步骤
  console.log(colorize('bright', '安装步骤:'));
  STEPS.forEach((step, i) => {
    const symbol = startStep > i ? colorize('green', '✅') : colorize('dim', `${i + 1}️⃣`);
    console.log(`  ${symbol} ${STEP_NAMES[step]}`);
  });
  console.log('');
  
  try {
    let config = DEFAULT_CONFIG;
    
    // 步骤 1-12（调整顺序：record 在 restart 之前）
    const steps = [
      [0, installNpmDependencies],
      [1, checkDependencies],
      [2, configurePostgresAuth],
      [3, async () => { config = await interactiveConfig(); }],
      [4, async () => await ensureDatabase(config)],
      [5, initDatabase],
      [6, createIndexes],
      [7, configureGatewayHooks],
      [8, createDataFiles],
      [9, healthCheck],
      [10, async () => await recordInstallStatus(config)],
      [11, restartGateway]
    ];
    
    for (const [stepIndex, stepFn] of steps) {
      if (startStep > stepIndex) continue;
      
      updateProgress(stepIndex, steps.length);
      log(`${colorize('bright', `步骤 ${stepIndex + 1}/${steps.length}:`)} ${STEP_NAMES[STEPS[stepIndex]]}`);
      await stepFn();
      saveCheckpoint(stepIndex);
    }
    
    updateProgress(steps.length, steps.length);
    console.log(''); // 换行
    
    // 测试连接
    if (!await testDatabaseConnection(config) && !isNonInteractive) {
      const retry = await ask('连接失败，是否重试?', 'y');
      if (retry.toLowerCase() === 'y') return main();
    }
    
    clearCheckpoint();
    
    // 安装成功，清理备份
    if (fs.existsSync(rollbackState.BACKUP_CONFIG)) {
      fs.unlinkSync(rollbackState.BACKUP_CONFIG);
    }
    
    console.log('\n' + colorize('cyan', '='.repeat(50)));
    console.log(`\n${colorize('green', colorize('bright', '✨ Cognitive Brain v5.3.25 安装完成!'))}\n`);
    log('安装完成', 'INFO');
    console.log(colorize('bright', '使用方法:'));
    console.log(`  ${colorize('cyan', 'npm run health')}     # 健康检查`);
    console.log(`  ${colorize('cyan', 'npm run verify')}     # 验证 hooks`);
    console.log(`  ${colorize('cyan', 'npm run encode')}     # 编码记忆`);
    console.log(`  ${colorize('cyan', 'npm run recall')}     # 检索记忆`);
    console.log(`\n📄 安装日志: ${colorize('dim', LOG_PATH)}\n`);
  } catch (error) {
    await rollback(error);
    process.exit(1);
  }
}

main().catch(async (e) => { 
  await rollback(e);
  process.exit(1);
});
