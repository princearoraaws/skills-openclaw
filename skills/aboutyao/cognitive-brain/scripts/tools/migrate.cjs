#!/usr/bin/env node
/**
 * Cognitive Brain - 升级迁移脚本
 * 从旧版本迁移到新版本（自动清理旧的 hooks 目录）
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const HOME = process.env.HOME || '/root';
const SKILL_DIR = path.join(__dirname, "..", "..");
const OPENCLAW_CONFIG = path.join(HOME, '.openclaw', 'openclaw.json');
const OLD_HOOKS_DIR = path.join(HOME, '.openclaw', 'hooks', 'cognitive-recall');

console.log('\n🔄 Cognitive Brain 升级迁移工具\n');
console.log('='.repeat(50));

let changes = [];

// 1. 检测旧版本 hooks 目录
console.log('\n🔍 检测旧版本安装...');
if (fs.existsSync(OLD_HOOKS_DIR)) {
  console.log('  ⚠️  发现旧版本 hooks 目录');
  console.log(`     路径: ${OLD_HOOKS_DIR}`);
  changes.push('删除旧 hooks 目录');
} else {
  console.log('  ✅ 未发现旧版本 hooks 目录');
}

// 2. 检查配置中的旧路径
console.log('\n🔍 检查 Gateway 配置...');
let config = {};
let configChanged = false;

if (fs.existsSync(OPENCLAW_CONFIG)) {
  try {
    config = JSON.parse(fs.readFileSync(OPENCLAW_CONFIG, 'utf8'));
    
    // 检查是否有旧的配置
    if (config.hooks?.internal?.handlers) {
      const oldHandlers = config.hooks.internal.handlers.filter(h => 
        h.module && h.module.includes('.openclaw/hooks/cognitive-recall')
      );
      
      if (oldHandlers.length > 0) {
        console.log('  ⚠️  发现旧的 handlers 配置');
        changes.push('清理旧的 handlers 配置');
      }
    }
    
    // 检查 extraDirs
    const skillHooksDir = path.join(SKILL_DIR, 'hooks');
    const extraDirs = config.hooks?.internal?.load?.extraDirs || [];
    
    if (!extraDirs.includes(skillHooksDir)) {
      console.log('  ⚠️  需要添加新的 hooks 目录');
      changes.push('添加新的 hooks 目录到配置');
    } else {
      console.log('  ✅ hooks 目录配置正确');
    }
    
  } catch (e) {
    console.log(`  ❌ 配置文件解析失败: ${e.message}`);
  }
} else {
  console.log('  ⚠️  OpenClaw 配置文件不存在');
}

// 3. 显示迁移计划
if (changes.length === 0) {
  console.log('\n✅ 无需迁移，已是最新版本!\n');
  process.exit(0);
}

console.log('\n📋 迁移计划:');
changes.forEach((change, i) => console.log(`  ${i + 1}. ${change}`));

// 4. 执行迁移
console.log('\n🔧 执行迁移...\n');

// 删除旧 hooks 目录
if (fs.existsSync(OLD_HOOKS_DIR)) {
  console.log('  🗑️  删除旧 hooks 目录...');
  fs.rmSync(OLD_HOOKS_DIR, { recursive: true });
  console.log('  ✅ 已删除');
}

// 更新配置
if (fs.existsSync(OPENCLAW_CONFIG)) {
  console.log('  📝 更新 Gateway 配置...');
  
  try {
    // 备份
    const backup = OPENCLAW_CONFIG + '.migrate.bak';
    fs.copyFileSync(OPENCLAW_CONFIG, backup);
    console.log('  ✅ 已备份配置');
    
    // 清理旧的 handlers
    if (config.hooks?.internal?.handlers) {
      config.hooks.internal.handlers = config.hooks.internal.handlers.filter(h => 
        !h.module?.includes('.openclaw/hooks/cognitive-recall')
      );
    }
    
    // 确保 hooks.internal 结构正确
    if (!config.hooks) config.hooks = {};
    if (!config.hooks.internal) config.hooks.internal = {};
    config.hooks.internal.enabled = true;
    
    if (!config.hooks.internal.load) config.hooks.internal.load = {};
    if (!config.hooks.internal.load.extraDirs) config.hooks.internal.load.extraDirs = [];
    
    // 添加新的路径
    const skillHooksDir = path.join(SKILL_DIR, 'hooks');
    if (!config.hooks.internal.load.extraDirs.includes(skillHooksDir)) {
      config.hooks.internal.load.extraDirs.push(skillHooksDir);
    }
    
    // 保存
    fs.writeFileSync(OPENCLAW_CONFIG, JSON.stringify(config, null, 2));
    console.log('  ✅ 配置已更新');
    
  } catch (e) {
    console.log(`  ❌ 配置更新失败: ${e.message}`);
    process.exit(1);
  }
}

// 5. 重启 Gateway（检测主会话）
const inMainSession = process.env.OPENCLAW_SESSION_KEY?.includes('main') || 
                      process.cwd().includes('/agents/main');

console.log('\n🔄 重启 Gateway...');
if (inMainSession) {
  console.log('  ⚠️  检测到在主会话中运行，跳过自动重启');
  console.log('  💡 请手动重启 Gateway 使配置生效:');
  console.log('     systemctl --user restart openclaw-gateway');
} else {
  try {
    execSync('systemctl --user restart openclaw-gateway', { stdio: 'pipe' });
    console.log('  ✅ Gateway 已重启');
  } catch (e) {
    console.log('  ⚠️  自动重启失败，请手动重启:');
    console.log('     systemctl --user restart openclaw-gateway');
  }
}

console.log('\n' + '='.repeat(50));
console.log('\n✅ 迁移完成!\n');
console.log('验证安装:');
console.log('  npm run verify\n');
