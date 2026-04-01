/**
 * 配置管理模块
 * 负责配置的加载、保存、验证和迁移
 */

const fs = require('fs-extra');
const path = require('path');
const os = require('os');

// 配置文件路径
const CONFIG_DIR = path.join(os.homedir(), '.openclaw', 'workspace', 'Auto-Backup-Openclaw-User-Data');
const CONFIG_FILE = path.join(CONFIG_DIR, 'config.json');
const LOG_FILE = path.join(CONFIG_DIR, 'backup.log');
const BACKUPS_DIR = path.join(CONFIG_DIR, 'backups');

// OpenClaw 配置文件路径
const OPENCLAW_CONFIG_FILE = path.join(os.homedir(), '.openclaw', 'openclaw.json');

// 默认配置
const DEFAULT_CONFIG = {
  version: "1.0.2",
  createdAt: new Date().toISOString(),
  updatedAt: new Date().toISOString(),
  
  backup: {
    mode: "full",
    targets: ["workspace", "workspace-1", "workspace-2", "workspace-2", "memory",……],
    exclude: ["logs", "cache", "tmp", "node_modules"],
    excludePatterns: ["*.log", "*.tmp", ".DS_Store", "Thumbs.db"]
  },
  
  schedule: {
    enabled: true,
    cron: "0 3 * * *",
    timezone: "Asia/Shanghai",
    lastRun: null
  },
  
  output: {
    path: BACKUPS_DIR,
    naming: {
      prefix: "auto-backup-openclaw-user-data",
      includeVersion: true,
      includeSequence: true
    }
  },
  
  retention: {
    enabled: true,
    mode: "count",
    days: 30,
    count: 10
  },
  
  notification: {
    enabled: true,
    channels: ["feishu"],
    targets: {},
    onSuccess: true,
    onFailure: true
  },
  
  logging: {
    enabled: true,
    level: "info",
    maxSize: "10MB",
    maxFiles: 5
  }
};

/**
 * 确保配置目录存在
 */
async function ensureConfigDir() {
  await fs.ensureDir(CONFIG_DIR);
  await fs.ensureDir(BACKUPS_DIR);
}

/**
 * 检查配置文件是否存在
 */
async function configExists() {
  return fs.pathExists(CONFIG_FILE);
}

/**
 * 加载配置
 */
async function loadConfig() {
  try {
    await ensureConfigDir();
    
    if (!(await configExists())) {
      // 配置不存在，创建默认配置
      await saveConfig(DEFAULT_CONFIG);
      return { ...DEFAULT_CONFIG };
    }
    
    const config = await fs.readJson(CONFIG_FILE);
    
    // 配置迁移（检查并补全新字段）
    const migratedConfig = migrateConfig(config);
    
    return migratedConfig;
  } catch (error) {
    console.error(`[Config] 加载配置失败: ${error.message}`);
    // 返回默认配置
    return { ...DEFAULT_CONFIG };
  }
}

/**
 * 保存配置
 */
async function saveConfig(config) {
  try {
    await ensureConfigDir();
    
    config.updatedAt = new Date().toISOString();
    
    // 验证配置
    const validation = validateConfig(config);
    if (!validation.valid) {
      throw new Error(`配置验证失败: ${validation.errors.join(', ')}`);
    }
    
    await fs.writeJson(CONFIG_FILE, config, { spaces: 2 });
    return true;
  } catch (error) {
    console.error(`[Config] 保存配置失败: ${error.message}`);
    return false;
  }
}

/**
 * 验证配置
 */
function validateConfig(config) {
  const errors = [];
  
  // 验证 version
  if (!config.version || typeof config.version !== 'string') {
    errors.push('version 必须是字符串');
  }
  
  // 验证 backup.mode
  if (config.backup && !['full', 'partial'].includes(config.backup.mode)) {
    errors.push('backup.mode 必须是 "full" 或 "partial"');
  }
  
  // 验证 schedule.cron
  if (config.schedule && config.schedule.cron) {
    const cronPattern = /^[\d*\/,-]+\s+[\d*\/,-]+\s+[\d*\/,-]+\s+[\d*\/,-]+\s+[\d*\/,-]+$/;
    if (!cronPattern.test(config.schedule.cron)) {
      errors.push('schedule.cron 格式无效');
    }
  }
  
  // 验证 retention.mode
  if (config.retention && !['days', 'count'].includes(config.retention.mode)) {
    errors.push('retention.mode 必须是 "days" 或 "count"');
  }
  
  // 验证 retention.days
  if (config.retention && config.retention.mode === 'days') {
    if (typeof config.retention.days !== 'number' || config.retention.days < 1) {
      errors.push('retention.days 必须是大于 0 的数字');
    }
  }
  
  // 验证 retention.count
  if (config.retention && config.retention.mode === 'count') {
    if (typeof config.retention.count !== 'number' || config.retention.count < 1) {
      errors.push('retention.count 必须是大于 0 的数字');
    }
  }
  
  return {
    valid: errors.length === 0,
    errors
  };
}

/**
 * 配置迁移
 */
function migrateConfig(config) {
  let needsSave = false;
  
  // v1.0.0 -> v1.0.1: 新增 notification.targets 字段
  if (!config.notification) {
    config.notification = { ...DEFAULT_CONFIG.notification };
    needsSave = true;
  }
  
  if (!config.notification.targets) {
    config.notification.targets = {};
    needsSave = true;
  }
  
  // 更新版本号
  if (config.version !== DEFAULT_CONFIG.version) {
    config.version = DEFAULT_CONFIG.version;
    needsSave = true;
  }
  
  // 如果有变更，保存配置
  if (needsSave) {
    saveConfig(config).catch(err => {
      console.error(`[Config] 配置迁移保存失败: ${err.message}`);
    });
  }
  
  return config;
}

/**
 * 重置配置为默认值
 */
async function resetConfig() {
  const newConfig = {
    ...DEFAULT_CONFIG,
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  };
  
  await saveConfig(newConfig);
  return newConfig;
}

/**
 * 获取配置路径信息
 */
function getConfigPaths() {
  return {
    configDir: CONFIG_DIR,
    configFile: CONFIG_FILE,
    logFile: LOG_FILE,
    backupsDir: BACKUPS_DIR
  };
}

/**
 * 更新部分配置
 */
async function updateConfig(updates) {
  const config = await loadConfig();
  const newConfig = deepMerge(config, updates);
  await saveConfig(newConfig);
  return newConfig;
}

/**
 * 深度合并对象
 */
function deepMerge(target, source) {
  const result = { ...target };
  
  for (const key in source) {
    if (source[key] && typeof source[key] === 'object' && !Array.isArray(source[key])) {
      result[key] = deepMerge(result[key] || {}, source[key]);
    } else {
      result[key] = source[key];
    }
  }
  
  return result;
}

/**
 * 加载 OpenClaw 配置
 * 从 ~/.openclaw/openclaw.json 读取渠道配置和绑定信息
 */
async function loadOpenClawConfig() {
  try {
    if (!(await fs.pathExists(OPENCLAW_CONFIG_FILE))) {
      return { channels: {}, bindings: [], availableTargets: {} };
    }
    
    const config = await fs.readJson(OPENCLAW_CONFIG_FILE);
    
    const result = {
      channels: {},
      bindings: config.bindings || [],
      availableTargets: {}
    };
    
    // 解析渠道配置
    if (config.channels) {
      // Feishu
      if (config.channels.feishu && config.channels.feishu.enabled) {
        result.channels.feishu = {
          enabled: true,
          appId: config.channels.feishu.appId
        };
        result.availableTargets.feishu = [];
      }
      
      // Telegram
      if (config.channels.telegram && config.channels.telegram.enabled) {
        result.channels.telegram = {
          enabled: true,
          groups: config.channels.telegram.groups || {}
        };
        result.availableTargets.telegram = [];
      }
      
      // Discord
      if (config.channels.discord && config.channels.discord.enabled) {
        result.channels.discord = {
          enabled: true
        };
        result.availableTargets.discord = [];
      }
      
      // Slack
      if (config.channels.slack && config.channels.slack.enabled) {
        result.channels.slack = {
          enabled: true
        };
        result.availableTargets.slack = [];
      }
    }
    
    // 从 bindings 解析可用的推送目标
    if (config.bindings && Array.isArray(config.bindings)) {
      for (const binding of config.bindings) {
        if (binding.match && binding.match.channel && binding.match.peer) {
          const channel = binding.match.channel;
          const peer = binding.match.peer;
          
          if (!result.availableTargets[channel]) {
            result.availableTargets[channel] = [];
          }
          
          // 添加到可用目标列表
          result.availableTargets[channel].push({
            type: peer.kind, // 'group' or 'user'
            id: peer.id,
            name: binding.agentId ? `${binding.agentId} Agent` : peer.id,
            agentId: binding.agentId
          });
        }
      }
    }
    
    // 从 Telegram groups 配置解析
    if (config.channels?.telegram?.groups) {
      const tgGroups = config.channels.telegram.groups;
      for (const groupId in tgGroups) {
        if (tgGroups[groupId].enabled) {
          if (!result.availableTargets.telegram) {
            result.availableTargets.telegram = [];
          }
          result.availableTargets.telegram.push({
            type: 'group',
            id: groupId,
            name: `Telegram群组 ${groupId}`
          });
        }
      }
    }
    
    return result;
  } catch (error) {
    console.error(`[Config] 加载 OpenClaw 配置失败: ${error.message}`);
    return { channels: {}, bindings: [], availableTargets: {} };
  }
}

/**
 * 检测渠道是否已配置
 */
function isChannelConfigured(channel, openclawConfig) {
  return openclawConfig.channels[channel]?.enabled === true;
}

/**
 * 获取渠道可用的推送目标
 */
function getChannelTargets(channel, openclawConfig) {
  return openclawConfig.availableTargets[channel] || [];
}

module.exports = {
  loadConfig,
  saveConfig,
  validateConfig,
  resetConfig,
  updateConfig,
  configExists,
  ensureConfigDir,
  getConfigPaths,
  loadOpenClawConfig,
  isChannelConfigured,
  getChannelTargets,
  DEFAULT_CONFIG,
  CONFIG_DIR,
  CONFIG_FILE,
  LOG_FILE,
  BACKUPS_DIR
};