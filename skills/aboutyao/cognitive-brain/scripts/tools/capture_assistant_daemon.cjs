#!/usr/bin/env node
/**
 * AI 回复捕获器 - 独立后台进程
 * 每 10 秒扫描会话文件，捕获 AI 回复并编码到数据库
 */

const fs = require('fs');
const path = require('path');
const { getPool } = require('./scripts/core/db.cjs');

const SESSIONS_DIR = '/root/.openclaw/agents/main/sessions';
const CHECK_INTERVAL = 10000; // 10 秒
const PROCESSED_MARKER = '.processed-ai-replies';

// 记录已处理的位置
let processedPositions = {};

// 加载已处理位置
function loadProcessedPositions() {
  try {
    const markerPath = path.join(SESSIONS_DIR, PROCESSED_MARKER);
    if (fs.existsSync(markerPath)) {
      processedPositions = JSON.parse(fs.readFileSync(markerPath, 'utf8'));
    }
  } catch (e) {}
}

// 保存已处理位置
function saveProcessedPositions() {
  try {
    const markerPath = path.join(SESSIONS_DIR, PROCESSED_MARKER);
    fs.writeFileSync(markerPath, JSON.stringify(processedPositions, null, 2));
  } catch (e) {}
}

// 编码 AI 回复到数据库
async function encodeAssistantReply(content, metadata) {
  const pool = getPool();
  
  try {
    // 检查是否已存在（去重）
    const existing = await pool.query(
      'SELECT id FROM episodes WHERE content = $1 AND role = $2 LIMIT 1',
      [content, 'assistant']
    );
    if (existing.rows.length > 0) return null;
    
    // 插入新记录
    const result = await pool.query(`
      INSERT INTO episodes (content, summary, type, role, source_channel, importance, created_at)
      VALUES ($1, $2, $3, $4, $5, $6, NOW())
      RETURNING id
    `, [
      content,
      content.slice(0, 200),
      metadata.type || 'episodic',
      'assistant',
      metadata.channel || 'unknown',
      0.5 // AI 回复默认重要性
    ]);
    
    return result.rows[0].id;
  } catch (err) {
    console.error('[AI Capture] Encode error:', err.message);
    return null;
  }
}

// 扫描单个会话文件
async function scanSessionFile(filename) {
  const filepath = path.join(SESSIONS_DIR, filename);
  const sessionId = filename.replace('.jsonl', '');
  
  try {
    const stats = fs.statSync(filepath);
    const lastSize = processedPositions[sessionId] || 0;
    
    // 文件没有增长，跳过
    if (stats.size <= lastSize) return 0;
    
    // 读取新增内容
    const fd = fs.openSync(filepath, 'r');
    const buffer = Buffer.alloc(stats.size - lastSize);
    fs.readSync(fd, buffer, 0, buffer.length, lastSize);
    fs.closeSync(fd);
    
    const newContent = buffer.toString('utf8');
    const lines = newContent.split('\n').filter(l => l.trim());
    
    let capturedCount = 0;
    
    for (const line of lines) {
      try {
        const msg = JSON.parse(line);
        
        // 只处理 assistant 消息
        if (msg.type === 'message' && msg.message?.role === 'assistant') {
          const content = typeof msg.message.content === 'string'
            ? msg.message.content
            : msg.message.content?.map(c => c.text || '').join('');
          
          if (content && content.length > 10) {
            const id = await encodeAssistantReply(content, {
              type: 'episodic',
              channel: 'unknown'
            });
            if (id) {
              console.log('[AI Capture] Captured reply:', id, 'from session:', sessionId.slice(0, 8));
              capturedCount++;
            }
          }
        }
      } catch (e) {}
    }
    
    // 更新处理位置
    processedPositions[sessionId] = stats.size;
    return capturedCount;
    
  } catch (err) {
    console.error('[AI Capture] Scan error:', err.message);
    return 0;
  }
}

// 主循环
async function main() {
  console.log('[AI Capture] Starting assistant reply capture daemon...');
  console.log('[AI Capture] Check interval:', CHECK_INTERVAL, 'ms');
  
  loadProcessedPositions();
  
  while (true) {
    try {
      // 获取所有会话文件
      const files = fs.readdirSync(SESSIONS_DIR)
        .filter(f => f.endsWith('.jsonl'));
      
      let totalCaptured = 0;
      
      for (const file of files) {
        const count = await scanSessionFile(file);
        totalCaptured += count;
      }
      
      if (totalCaptured > 0) {
        console.log('[AI Capture] Total captured this round:', totalCaptured);
        saveProcessedPositions();
      }
      
    } catch (err) {
      console.error('[AI Capture] Main loop error:', err.message);
    }
    
    // 等待下一轮
    await new Promise(resolve => setTimeout(resolve, CHECK_INTERVAL));
  }
}

// 启动
main().catch(err => {
  console.error('[AI Capture] Fatal error:', err);
  process.exit(1);
});

