#!/usr/bin/env node
/**
 * recall_brain.cjs - 应用层召回记忆（带 embedding 语义搜索）
 * 用法: node recall_brain.cjs "查询内容" [limit]
 */

const path = require('path');

const HOME = process.env.HOME || '/root';
const SKILL_DIR = path.join(HOME, '.openclaw/workspace/skills/cognitive-brain');

async function main() {
  const query = process.argv[2];
  const limit = parseInt(process.argv[3]) || 5;
  
  if (!query) {
    console.log('Usage: node recall_brain.cjs "query" [limit]');
    process.exit(1);
  }
  
  try {
    // 加载 CognitiveBrain 应用层
    const { CognitiveBrain } = require(path.join(SKILL_DIR, 'src/index.js'));
    const brain = new CognitiveBrain();
    
    console.error('[recall_brain] Initializing brain...');
    
    // 召回记忆
    const memories = await brain.recall(query, { limit });
    
    if (!memories || memories.length === 0) {
      console.log('[]');
      return;
    }
    
    // 输出 JSON
    const result = memories.map(m => ({
      summary: m.summary || m.content?.substring(0, 100),
      role: m.role || 'unknown',
      time: m.createdAt ? new Date(m.createdAt).toISOString().replace('T', ' ').substring(0, 16) : 'unknown'
    }));
    
    console.log(JSON.stringify(result, null, 2));
    
    if (brain.close) await brain.close();
  } catch (e) {
    console.error('Error:', e.message);
    process.exit(1);
  }
}

main();
