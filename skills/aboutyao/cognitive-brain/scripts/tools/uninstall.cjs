#!/usr/bin/env node
/**
 * Cognitive Brain - 卸载脚本
 * 清理数据库、hooks、配置文件
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

const HOME = process.env.HOME || '/root';
const SKILL_DIR = path.join(__dirname, "..", "..");
const OPENCLAW_HOOKS_DIR = path.join(HOME, '.openclaw', 'hooks');
const CONFIG_PATH = path.join(SKILL_DIR, 'config.json');

const args = process.argv.slice(2);
const keepDb = args.includes('--keep-db');
const keepConfig = args.includes('--keep-config');
const force = args.includes('--force');

async function uninstall() {
  console.log('\n🗑️  Cognitive Brain 卸载程序\n');
  console.log('='.repeat(50));
  
  // 确认
  if (!force) {
    console.log('\n将删除:');
    console.log('  - Hooks 文件');
    console.log('  - 数据文件 (.user-model.json 等)');
    if (!keepDb) console.log('  - 数据库表和数据');
    if (!keepConfig) console.log('  - 配置文件');
    console.log('');
    
    // 非交互模式直接继续
    if (!process.stdin.isTTY) {
      console.log('🤖 非交互模式，自动继续...\n');
    } else {
      const rl = require('readline').createInterface({
        input: process.stdin,
        output: process.stdout
      });
      
      const answer = await new Promise(resolve => {
        rl.question('确认卸载? [y/N]: ', resolve);
      });
      rl.close();
      
      if (answer.toLowerCase() !== 'y') {
        console.log('已取消');
        process.exit(0);
      }
    }
  }
  
  // 1. 清理 Gateway hooks 配置
  console.log('\n🔄 清理 Gateway hooks 配置...');
  const OPENCLAW_CONFIG = path.join(HOME, '.openclaw', 'openclaw.json');
  if (fs.existsSync(OPENCLAW_CONFIG)) {
    try {
      const config = JSON.parse(fs.readFileSync(OPENCLAW_CONFIG, 'utf8'));
      const skillHooksDir = path.join(SKILL_DIR, 'hooks');
      
      if (config.hooks?.internal?.load?.extraDirs) {
        const idx = config.hooks.internal.load.extraDirs.indexOf(skillHooksDir);
        if (idx !== -1) {
          config.hooks.internal.load.extraDirs.splice(idx, 1);
          fs.writeFileSync(OPENCLAW_CONFIG, JSON.stringify(config, null, 2));
          console.log('  ✅ 已从 Gateway 配置中移除 hooks 目录');
        } else {
          console.log('  ⚠️  Gateway 配置中未找到 hooks 目录');
        }
      }
    } catch (e) {
      console.log(`  ⚠️  清理 Gateway 配置失败: ${e.message}`);
    }
  }
  
  // 删除旧的 hooks 目录（如果存在）
  const hooksDir = path.join(OPENCLAW_HOOKS_DIR, 'cognitive-recall');
  if (fs.existsSync(hooksDir)) {
    fs.rmSync(hooksDir, { recursive: true });
    console.log('  ✅ 已删除旧的 hooks 目录');
  }
  
  // 2. 删除数据文件
  console.log('\n🗑️  删除数据文件...');
  const dataFiles = [
    '.user-model.json',
    '.working-memory.json',
    '.prediction-cache.json',
    '.safety-log.json'
  ];
  
  for (const file of dataFiles) {
    const filePath = path.join(SKILL_DIR, file);
    if (fs.existsSync(filePath)) {
      fs.unlinkSync(filePath);
      console.log(`  ✅ 删除 ${file}`);
    }
  }
  
  // 3. 删除配置
  if (!keepConfig) {
    console.log('\n🗑️  删除配置文件...');
    if (fs.existsSync(CONFIG_PATH)) {
      fs.unlinkSync(CONFIG_PATH);
      console.log('  ✅ config.json 已删除');
    }
  }
  
  // 4. 清理数据库
  if (!keepDb) {
    console.log('\n🗄️  清理数据库...');
    try {
      // 读取配置（如果还存在）
      let dbConfig = {
        host: 'localhost',
        port: 5432,
        database: 'cognitive_brain',
        user: 'postgres'
      };
      
      if (fs.existsSync(CONFIG_PATH)) {
        const config = JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf8'));
        dbConfig = { ...dbConfig, ...config.storage.primary };
      }
      
      const { Pool } = require('pg');
      const pool = new Pool(dbConfig);
      
      // 删除所有表
      const tables = ['episodes', 'concepts', 'associations', 'reflections', 
                      'user_profiles', 'self_awareness', 'subagent_logs'];
      
      for (const table of tables) {
        try {
          await pool.query(`DROP TABLE IF EXISTS ${table} CASCADE`);
          console.log(`  ✅ 删除表 ${table}`);
        } catch (e) {
          console.log(`  ⚠️  删除表 ${table} 失败: ${e.message}`);
        }
      }
      
      // 删除函数
      const functions = ['spread_activation', 'memory_retention', 'find_similar_episodes'];
      for (const fn of functions) {
        try {
          await pool.query(`DROP FUNCTION IF EXISTS ${fn} CASCADE`);
        } catch (e) {}
      }
      
      await pool.end();
      console.log('  ✅ 数据库已清理');
      
    } catch (e) {
      console.log(`  ⚠️  数据库清理失败: ${e.message}`);
    }
  }
  
  // 5. 删除 node_modules
  console.log('\n🗑️  删除 node_modules...');
  const nodeModulesPath = path.join(SKILL_DIR, 'node_modules');
  if (fs.existsSync(nodeModulesPath)) {
    fs.rmSync(nodeModulesPath, { recursive: true });
    console.log('  ✅ node_modules 已删除');
  }
  
  console.log('\n' + '='.repeat(50));
  console.log('\n✨ Cognitive Brain 已卸载!\n');
  console.log('如需重新安装:');
  console.log('  clawhub install cognitive-brain');
  console.log('  npm run setup\n');
}

uninstall().catch(e => {
  console.error('\n❌ 卸载失败:', e.message);
  process.exit(1);
});
