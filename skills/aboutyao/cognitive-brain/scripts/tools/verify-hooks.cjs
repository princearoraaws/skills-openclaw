#!/usr/bin/env node
/**
 * Cognitive Brain - Hook 健康验证
 * 验证 Gateway 是否正确加载 hooks
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const HOME = process.env.HOME || '/root';
const SKILL_DIR = path.join(__dirname, "..", "..");
const OPENCLAW_CONFIG = path.join(HOME, '.openclaw', 'openclaw.json');

console.log('\n🔍 Cognitive Brain Hook 健康验证\n');
console.log('='.repeat(50));

let hasError = false;

// 1. 检查配置文件
console.log('\n📋 检查 Gateway 配置...');
if (!fs.existsSync(OPENCLAW_CONFIG)) {
  console.log('  ❌ 未找到 OpenClaw 配置文件');
  console.log('     请确保 OpenClaw 已正确安装');
  hasError = true;
} else {
  try {
    const config = JSON.parse(fs.readFileSync(OPENCLAW_CONFIG, 'utf8'));
    
    // 检查 hooks.internal.enabled
    if (!config.hooks?.internal?.enabled) {
      console.log('  ❌ hooks.internal.enabled 未启用');
      hasError = true;
    } else {
      console.log('  ✅ hooks.internal.enabled = true');
    }
    
    // 检查 extraDirs
    const skillHooksDir = path.join(SKILL_DIR, 'hooks');
    const extraDirs = config.hooks?.internal?.load?.extraDirs || [];
    
    if (extraDirs.includes(skillHooksDir)) {
      console.log(`  ✅ hooks.internal.load.extraDirs 包含: ${skillHooksDir}`);
    } else {
      console.log('  ❌ hooks.internal.load.extraDirs 未包含 skill hooks 目录');
      console.log(`     期望: ${skillHooksDir}`);
      console.log(`     实际: ${JSON.stringify(extraDirs)}`);
      hasError = true;
    }
  } catch (e) {
    console.log(`  ❌ 配置文件解析失败: ${e.message}`);
    hasError = true;
  }
}

// 2. 检查 hooks 目录
console.log('\n📁 检查 hooks 目录...');
const hooksDir = path.join(SKILL_DIR, 'hooks', 'cognitive-recall');
if (!fs.existsSync(hooksDir)) {
  console.log('  ❌ hooks 目录不存在');
  console.log(`     路径: ${hooksDir}`);
  hasError = true;
} else {
  console.log(`  ✅ hooks 目录存在: ${hooksDir}`);
  
  // 检查必需文件
  const requiredFiles = ['HOOK.md', 'handler.js'];
  for (const file of requiredFiles) {
    const filePath = path.join(hooksDir, file);
    if (fs.existsSync(filePath)) {
      console.log(`  ✅ ${file} 存在`);
    } else {
      console.log(`  ❌ ${file} 不存在`);
      hasError = true;
    }
  }
  
  // 检查 handler.js 语法
  console.log('\n🔧 检查 handler.js 语法...');
  try {
    require(path.join(hooksDir, 'handler.js'));
    console.log('  ✅ handler.js 语法正确');
  } catch (e) {
    if (e.code === 'MODULE_NOT_FOUND') {
      // 这是正常的，因为依赖可能未加载
      console.log('  ⚠️  handler.js 有未解析的依赖（正常，运行时会解析）');
    } else {
      console.log(`  ❌ handler.js 语法错误: ${e.message}`);
      hasError = true;
    }
  }
}

// 3. 检查依赖
console.log('\n📦 检查依赖...');
const nodeModulesPath = path.join(SKILL_DIR, 'node_modules');
if (!fs.existsSync(nodeModulesPath)) {
  console.log('  ❌ node_modules 不存在，请运行 npm install');
  hasError = true;
} else {
  const pgPath = path.join(nodeModulesPath, 'pg');
  const redisPath = path.join(nodeModulesPath, 'redis');
  
  if (fs.existsSync(pgPath)) {
    console.log('  ✅ pg 依赖已安装');
  } else {
    console.log('  ❌ pg 依赖未安装');
    hasError = true;
  }
  
  if (fs.existsSync(redisPath)) {
    console.log('  ✅ redis 依赖已安装');
  } else {
    console.log('  ❌ redis 依赖未安装');
    hasError = true;
  }
}

// 4. 检查 Gateway 日志
console.log('\n📜 检查 Gateway 日志...');
try {
  const logDir = '/tmp/openclaw';
  const logFiles = fs.readdirSync(logDir)
    .filter(f => f.startsWith('openclaw-') && f.endsWith('.log'))
    .sort()
    .reverse();
  
  if (logFiles.length > 0) {
    const latestLog = path.join(logDir, logFiles[0]);
    const logContent = fs.readFileSync(latestLog, 'utf8');
    
    // 检查 hook 注册记录
    if (logContent.includes('Registered hook: cognitive-recall')) {
      console.log('  ✅ Gateway 日志显示 cognitive-recall hook 已注册');
    } else if (logContent.includes('Failed to load hook cognitive-recall')) {
      console.log('  ❌ Gateway 日志显示 hook 加载失败');
      const errorLines = logContent.split('\n')
        .filter(l => l.includes('cognitive-recall'))
        .slice(-5);
      console.log('     最近错误:');
      errorLines.forEach(l => {
        const match = l.match(/"message":"([^"]+)"/);
        if (match) console.log(`     ${match[1]}`);
      });
      hasError = true;
    } else {
      console.log('  ⚠️  Gateway 日志中未找到 hook 注册记录');
      console.log('     可能需要重启 Gateway: systemctl --user restart openclaw-gateway');
    }
  }
} catch (e) {
  console.log('  ⚠️  无法读取 Gateway 日志');
}

// 5. 检查数据库连接
console.log('\n🗄️  检查数据库连接...');
const configPath = path.join(SKILL_DIR, 'config.json');
if (fs.existsSync(configPath)) {
  try {
    const config = JSON.parse(fs.readFileSync(configPath, 'utf8'));
    const { Pool } = require('pg');
    const pool = new Pool({
      host: config.storage.primary.host,
      port: config.storage.primary.port,
      database: config.storage.primary.database,
      user: config.storage.primary.user,
      password: config.storage.primary.password || undefined,
      connectionTimeoutMillis: 3000
    });
    
    pool.query('SELECT 1')
      .then(() => {
        console.log('  ✅ PostgreSQL 连接正常');
        pool.end();
      })
      .catch(e => {
        console.log(`  ❌ PostgreSQL 连接失败: ${e.message}`);
        pool.end();
      });
  } catch (e) {
    console.log(`  ⚠️  无法测试数据库连接: ${e.message}`);
  }
} else {
  console.log('  ⚠️  config.json 不存在，跳过数据库检查');
}

// 总结
console.log('\n' + '='.repeat(50));
if (hasError) {
  console.log('\n❌ 发现问题，请根据上述提示修复\n');
  console.log('修复建议:');
  console.log('  1. 重新运行安装: npm run setup');
  console.log('  2. 重启 Gateway: systemctl --user restart openclaw-gateway');
  console.log('  3. 查看日志: tail -f /tmp/openclaw/openclaw-*.log | grep cognitive\n');
  process.exit(1);
} else {
  console.log('\n✅ Hook 健康检查通过!\n');
  process.exit(0);
}
