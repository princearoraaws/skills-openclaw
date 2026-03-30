#!/usr/bin/env node
/**
 * Initialize Database
 * 初始化数据库脚本
 */

const path = require('path');
const { initDatabase } = require('../db/init');

console.log('🚀 初始化数据库...\n');

initDatabase().then((success) => {
  if (success) {
    console.log('\n✅ 数据库初始化完成！');
    process.exit(0);
  } else {
    console.error('\n❌ 数据库初始化失败');
    process.exit(1);
  }
});
