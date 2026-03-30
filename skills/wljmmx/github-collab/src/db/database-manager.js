const Database = require('better-sqlite3');
const path = require('path');
const { getDatabaseConfig } = require('../config');

/**
 * 数据库管理 - 统一数据库连接
 * 支持配置化：数据库类型、名称、路径、连接池等
 */
class DatabaseManager {
  /**
   * 构造函数
   * @param {string} dbPath - 可选，覆盖配置中的数据库路径
   */
  constructor(dbPath = null) {
    // 从配置文件读取数据库路径
    const dbConfig = getDatabaseConfig();
    this.dbPath = dbPath || dbConfig.path;
    this.db = null;
    this.config = {
      type: dbConfig.type,
      poolSize: dbConfig.poolSize,
      timeout: dbConfig.timeout,
      name: dbConfig.name,
      dir: dbConfig.dir
    };
  }

  /**
   * 初始化数据库连接
   */
  init() {
    try {
      this.db = new Database(this.dbPath);
      this.db.pragma('journal_mode = WAL');
      console.log(`✅ 数据库已连接：${this.dbPath}`);
      console.log(`   类型：${this.config.type}`);
      console.log(`   名称：${this.config.name}`);
      return true;
    } catch (error) {
      console.error('❌ 数据库连接失败:', error.message);
      return false;
    }
  }

  /**
   * 执行 SQL 查询
   */
  query(sql, params = []) {
    if (!this.db) {
      throw new Error('数据库未初始化');
    }
    return this.db.prepare(sql).run(...params);
  }

  /**
   * 执行 SQL 查询并获取结果
   */
  getAll(sql, params = []) {
    if (!this.db) {
      throw new Error('数据库未初始化');
    }
    return this.db.prepare(sql).all(...params);
  }

  /**
   * 执行 SQL 查询并获取单条结果
   */
  get(sql, params = []) {
    if (!this.db) {
      throw new Error('数据库未初始化');
    }
    return this.db.prepare(sql).get(...params);
  }

  /**
   * 执行事务
   */
  transaction(fn) {
    if (!this.db) {
      throw new Error('数据库未初始化');
    }
    const transactionFn = this.db.transaction(fn);
    return transactionFn;
  }

  /**
   * 获取数据库实例
   */
  getDatabase() {
    return this.db;
  }

  /**
   * 关闭数据库连接
   */
  close() {
    if (this.db) {
      this.db.close();
      this.db = null;
      console.log('✅ 数据库已关闭');
    }
  }

  /**
   * 获取数据库配置
   */
  getConfig() {
    return this.config;
  }

  /**
   * 获取数据库路径
   */
  getDbPath() {
    return this.dbPath;
  }
}

// 导出单例
let instance = null;

function getDatabaseManager(customPath = null) {
  if (!instance) {
    instance = new DatabaseManager(customPath);
  }
  return instance;
}

module.exports = {
  DatabaseManager,
  getDatabaseManager
};
