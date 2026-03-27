#!/usr/bin/env node

/**
 * ChatGPT/Claude 分享链接抓取脚本
 * 使用 Chrome CDP (Chrome DevTools Protocol) 抓取页面内容
 * 
 * 用法:
 *   node capture-cdp.js <URL> [OUTPUT_DIR]
 * 
 * 环境变量:
 *   CHROME_DEBUG_PORT - Chrome 调试端口 (默认: 60184)
 */

const WebSocket = require('ws');
const fs = require('fs');
const http = require('http');
const path = require('path');

const DEBUG_PORT = process.env.CHROME_DEBUG_PORT || 60184;
const TARGET_URL = process.argv[2] || process.env.TARGET_URL;
const OUTPUT_DIR = process.argv[3] || process.env.OUTPUT_DIR || '/tmp';

/**
 * 获取 Chrome 已打开的页面列表
 */
async function getChromeTargets() {
  return new Promise((resolve, reject) => {
    const req = http.get(`http://127.0.0.1:${DEBUG_PORT}/json/list`, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        try {
          resolve(JSON.parse(data));
        } catch (e) {
          reject(e);
        }
      });
    });
    req.on('error', reject);
    req.setTimeout(5000, () => {
      req.destroy();
      reject(new Error('Connection timeout'));
    });
  });
}

/**
 * 创建新标签页
 */
async function createNewPage(targetUrl) {
  return new Promise((resolve, reject) => {
    const req = http.get(
      `http://127.0.0.1:${DEBUG_PORT}/json/new?${encodeURIComponent(targetUrl)}`,
      (res) => {
        let data = '';
        res.on('data', chunk => data += chunk);
        res.on('end', () => {
          try {
            resolve(JSON.parse(data));
          } catch (e) {
            reject(e);
          }
        });
      }
    );
    req.on('error', reject);
  });
}

/**
 * 通过 CDP 抓取页面 HTML
 */
async function capturePage(pageId) {
  return new Promise((resolve, reject) => {
    const ws = new WebSocket(`ws://127.0.0.1:${DEBUG_PORT}/devtools/page/${pageId}`);
    let messageId = 0;
    let resolved = false;

    const cleanup = () => {
      if (!resolved) {
        resolved = true;
        try { ws.close(); } catch (e) {}
      }
    };

    ws.on('open', () => {
      // 启用 Page domain
      sendCommand('Page.enable');
      // 等待页面稳定后抓取
      setTimeout(() => {
        sendCommand('Runtime.evaluate', {
          expression: 'document.documentElement.outerHTML',
          returnByValue: true
        });
      }, 2000);
    });

    ws.on('message', (data) => {
      const msg = JSON.parse(data.toString());
      if (msg.result?.result?.value) {
        resolved = true;
        resolve(msg.result.result.value);
        ws.close();
      }
    });

    ws.on('error', (err) => {
      cleanup();
      reject(err);
    });

    ws.on('close', () => {
      if (!resolved) {
        cleanup();
        reject(new Error('Connection closed'));
      }
    });

    function sendCommand(method, params = {}) {
      messageId++;
      ws.send(JSON.stringify({ id: messageId, method, params }));
    }

    // 超时 30 秒
    setTimeout(() => {
      cleanup();
      reject(new Error('Timeout'));
    }, 30000);
  });
}

/**
 * 主函数
 */
async function main() {
  if (!TARGET_URL) {
    console.error('用法: node capture-cdp.js <URL> [OUTPUT_DIR]');
    console.error('或设置环境变量: TARGET_URL OUTPUT_DIR CHROME_DEBUG_PORT');
    process.exit(1);
  }

  console.log(`🔍 连接 Chrome 端口 ${DEBUG_PORT}...`);
  console.log(`🎯 目标: ${TARGET_URL}`);

  // 获取已打开的页面
  let targets;
  try {
    targets = await getChromeTargets();
  } catch (err) {
    console.error('❌ 无法连接 Chrome 调试端口:', err.message);
    console.log('请确保 Chrome 已启动并带有 --remote-debugging-port 参数');
    process.exit(1);
  }

  // 查找目标页面
  let pageTarget = targets.find(t => t.url.includes(TARGET_URL) || t.type === 'page');

  if (!pageTarget) {
    console.log('📑 创建新标签页...');
    pageTarget = await createNewPage(TARGET_URL);
    console.log(`⏳ 等待页面加载...`);
    await new Promise(r => setTimeout(r, 8000));
  }

  console.log(`📄 抓取页面：${pageTarget.title}`);

  const html = await capturePage(pageTarget.id);

  // 生成文件名
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
  const slug = (pageTarget.title || 'untitled')
    .replace(/[^a-zA-Z0-9\u4e00-\u9fa5]/g, '-')
    .slice(0, 50);
  
  // 确定输出目录
  const isClaude = TARGET_URL.includes('claude.ai');
  const homeDir = process.env.HOME || process.env.USERPROFILE || '~';
  const dateStr = new Date().toISOString().slice(0, 10);
  const outputBase = OUTPUT_DIR || `${homeDir}/LookBack/${dateStr}/${isClaude ? 'Claude' : 'ChatGPT'}`;
  
  // 创建目录
  if (!fs.existsSync(outputBase)) {
    fs.mkdirSync(outputBase, { recursive: true });
  }

  const htmlPath = path.join(outputBase, `${timestamp}-${slug}-captured.html`);
  fs.writeFileSync(htmlPath, html);
  console.log(`✅ HTML 已保存：${htmlPath}`);

  // 提取元数据
  const titleMatch = html.match(/<meta property="og:title" content="([^"]+)"/);
  const title = titleMatch 
    ? titleMatch[1].replace('ChatGPT - ', '').replace('Claude - ', '')
    : slug;
  const descMatch = html.match(/<meta property="og:description" content="([^"]+)"/);

  // 保存元数据
  const metaPath = path.join(outputBase, '.metadata.json');
  const metadata = {
    title,
    description: descMatch?.[1] || '',
    source: TARGET_URL,
    htmlPath,
    timestamp,
    slug,
    outputBase
  };
  fs.writeFileSync(metaPath, JSON.stringify(metadata, null, 2));
  
  console.log(`✅ 元数据已保存：${metaPath}`);
  console.log(`📋 标题: ${title}`);
  
  return metadata;
}

main()
  .then(meta => {
    console.log('\n🎉 抓取完成！');
    process.exit(0);
  })
  .catch(err => {
    console.error('❌ 错误:', err.message);
    process.exit(1);
  });