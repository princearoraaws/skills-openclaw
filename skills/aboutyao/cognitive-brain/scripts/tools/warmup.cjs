#!/usr/bin/env node
/**
 * warmup.cjs - 预热 embedding 服务
 * 在 Gateway 启动时自动运行，避免首次召回延迟
 */

const path = require('path');
const { spawn } = require('child_process');

const HOME = process.env.HOME || '/root';
const SKILL_DIR = path.join(HOME, '.openclaw/workspace/skills/cognitive-brain');

async function warmup() {
  console.log('[warmup] Warming up embedding service...');
  
  try {
    // 启动 embedding 服务（后台）
    const embedScript = path.join(SKILL_DIR, 'scripts/embed.py');
    const proc = spawn('python3', [embedScript, '--serve'], {
      stdio: ['pipe', 'pipe', 'pipe'],
      detached: true
    });
    
    // 发送一个测试请求
    proc.stdin.write(JSON.stringify({ request_id: 1, text: 'warmup' }) + '\n');
    
    // 等待响应
    return new Promise((resolve) => {
      proc.stdout.on('data', (data) => {
        const line = data.toString();
        if (line.includes('embedding')) {
          console.log('[warmup] ✅ Embedding service ready');
          proc.disconnect();
          resolve(true);
        }
      });
      
      // 最多等待 60 秒
      setTimeout(() => {
        console.log('[warmup] ⚠️ Warmup timeout, continuing anyway');
        proc.disconnect();
        resolve(false);
      }, 60000);
    });
  } catch (e) {
    console.error('[warmup] Error:', e.message);
    return false;
  }
}

// 作为独立进程运行
if (require.main === module) {
  warmup().then(() => process.exit(0));
}

module.exports = { warmup };
