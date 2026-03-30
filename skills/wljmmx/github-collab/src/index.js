/**
 * GitHub Collaborative Development System - 主入口
 * 统一配置管理，支持环境变量和配置文件
 */

const config = require('./config');
const { initDatabase } = require('./db/init');
const { getDatabaseManager } = require('./db/database-manager');
const logger = require('./logger');

/**
 * 应用初始化
 */
async function initialize() {
  console.log('🚀 GitHub Collaborative Development System');
  console.log('='.repeat(50));
  console.log(`📁 项目根目录：${config.PROJECT_ROOT}`);
  console.log(`📊 数据库类型：${config.database.type}`);
  console.log(`📝 数据库名称：${config.database.name}`);
  console.log(`📁 数据库路径：${config.database.path}`);
  console.log('='.repeat(50));

  try {
    // 初始化数据库
    console.log('\n📦 初始化数据库...');
    const dbSuccess = await initDatabase();

    if (!dbSuccess) {
      console.error('❌ 数据库初始化失败');
      process.exit(1);
    }

    // 连接数据库
    console.log('\n🔌 连接数据库...');
    const dbManager = getDatabaseManager();
    const connected = dbManager.init();

    if (!connected) {
      console.error('❌ 数据库连接失败');
      process.exit(1);
    }

    console.log('✅ 系统初始化完成');

    // 启动主控制器
    console.log('\n🎮 启动主控制器...');
    // await startMainController();

    return true;
  } catch (error) {
    console.error('❌ 系统初始化失败:', error.message);
    logger.error('初始化失败:', error);
    return false;
  }
}

/**
 * 启动主控制器
 */
async function startMainController() {
  // TODO: 实现主控制器启动逻辑
  console.log('🎮 主控制器启动中...');
}

/**
 * 优雅关闭
 */
async function shutdown() {
  console.log('\n🛑 系统关闭中...');

  // 关闭数据库连接
  const dbManager = getDatabaseManager();
  dbManager.close();

  console.log('✅ 系统已关闭');
  process.exit(0);
}

// 处理关闭信号
process.on('SIGINT', shutdown);
process.on('SIGTERM', shutdown);

// 启动应用
if (require.main === module) {
  initialize().then((success) => {
    if (!success) {
      process.exit(1);
    }
  });
}

module.exports = {
  initialize,
  shutdown,
  config
};
