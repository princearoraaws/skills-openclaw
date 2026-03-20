#!/usr/bin/env node
/**
 * 数据库索引优化脚本
 * 添加必要的索引以提高查询性能
 */

const { getPool } = require('../core/db.cjs');

const INDEXES = [
  {
    name: 'idx_episodes_type_importance',
    sql: `CREATE INDEX IF NOT EXISTS idx_episodes_type_importance 
          ON episodes(type, importance DESC)`
  },
  {
    name: 'idx_episodes_created_at',
    sql: `CREATE INDEX IF NOT EXISTS idx_episodes_created_at 
          ON episodes(created_at DESC)`
  },
  {
    name: 'idx_episodes_source_channel',
    sql: `CREATE INDEX IF NOT EXISTS idx_episodes_source_channel 
          ON episodes(source_channel)`
  },
  {
    name: 'idx_episodes_access_count',
    sql: `CREATE INDEX IF NOT EXISTS idx_episodes_access_count 
          ON episodes(access_count DESC)`
  },
  {
    name: 'idx_concepts_name',
    sql: `CREATE INDEX IF NOT EXISTS idx_concepts_name 
          ON concepts(name)`
  },
  {
    name: 'idx_concepts_activation',
    sql: `CREATE INDEX IF NOT EXISTS idx_concepts_activation 
          ON concepts(activation DESC)`
  },
  {
    name: 'idx_associations_from_id',
    sql: `CREATE INDEX IF NOT EXISTS idx_associations_from_id 
          ON associations(from_id)`
  },
  {
    name: 'idx_associations_weight',
    sql: `CREATE INDEX IF NOT EXISTS idx_associations_weight 
          ON associations(weight DESC)`
  }
];

async function createIndexes() {
  const pool = getPool();
  if (!pool) {
    console.error('❌ 数据库连接失败');
    process.exit(1);
  }

  console.log('🔧 创建数据库索引...\n');

  for (const index of INDEXES) {
    try {
      await pool.query(index.sql);
      console.log(`  ✅ ${index.name}`);
    } catch (e) {
      console.error(`  ❌ ${index.name}: ${e.message}`);
    }
  }

  console.log('\n✅ 索引创建完成');
  await pool.end();
}

createIndexes().catch(console.error);

