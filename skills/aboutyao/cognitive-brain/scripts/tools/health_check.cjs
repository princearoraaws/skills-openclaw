#!/usr/bin/env node
/**
 * 健康检查脚本
 * 检查数据库、Redis 和系统状态
 */

const { getPool } = require('../core/db.cjs');
const { initRedis } = require('../core/cache.cjs');

async function healthCheck() {
  const checks = {
    database: false,
    redis: false,
    timestamp: new Date().toISOString()
  };

  console.log('🏥 Cognitive Brain 健康检查\n');

  // 1. 检查数据库
  try {
    const pool = getPool();
    if (pool) {
      const result = await pool.query('SELECT 1 as health');
      if (result.rows[0].health === 1) {
        checks.database = true;
        console.log('  ✅ PostgreSQL 连接正常');
      }
    }
  } catch (e) {
    console.error('  ❌ PostgreSQL 连接失败:', e.message);
  }

  // 2. 检查 Redis
  try {
    const redisOk = await initRedis();
    if (redisOk) {
      checks.redis = true;
      console.log('  ✅ Redis 连接正常');
    } else {
      console.log('  ⚠️  Redis 未启用或连接失败');
    }
  } catch (e) {
    console.log('  ⚠️  Redis 未启用或连接失败');
  }

  // 3. 检查表存在
  if (checks.database) {
    try {
      const pool = getPool();
      const tables = await pool.query(`
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name IN ('episodes', 'concepts', 'associations')
      `);
      const tableNames = tables.rows.map(r => r.table_name);
      console.log(`  ✅ 数据表检查: ${tableNames.join(', ')}`);
    } catch (e) {
      console.error('  ❌ 数据表检查失败:', e.message);
    }
  }

  console.log('');
  if (checks.database) {
    console.log('✅ 系统健康');
    process.exit(0);
  } else {
    console.log('❌ 系统异常');
    process.exit(1);
  }
}

healthCheck().catch(console.error);

