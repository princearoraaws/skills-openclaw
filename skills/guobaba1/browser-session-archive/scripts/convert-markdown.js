#!/usr/bin/env node

/**
 * HTML 转 Markdown 转换脚本
 * 读取抓取的 HTML 文件，转换为结构化 Markdown
 * 
 * 用法:
 *   node convert-markdown.js <HTML_PATH>
 *   或
 *   bun run convert-markdown.js <HTML_PATH>
 */

const fs = require('fs');
const path = require('path');

/**
 * 清理 HTML 标签，提取纯文本
 */
function cleanHtml(html) {
  let content = html;

  // 提取 main 区域
  const mainMatch = content.match(/<main[^>]*>([\s\S]*?)<\/main>/i);
  if (mainMatch) {
    content = mainMatch[1];
  }

  // 移除脚本、样式、SVG
  content = content
    .replace(/<script[^>]*>[\s\S]*?<\/script>/gi, '')
    .replace(/<style[^>]*>[\s\S]*?<\/style>/gi, '')
    .replace(/<svg[^>]*>[\s\S]*?<\/svg>/gi, '')
    .replace(/<nav[^>]*>[\s\S]*?<\/nav>/gi, '')
    .replace(/<footer[^>]*>[\s\S]*?<\/footer>/gi, '')
    .replace(/<header[^>]*>[\s\S]*?<\/header>/gi, '');

  // 移除所有 HTML 标签
  content = content.replace(/<[^>]+>/g, '');

  // 转换 HTML 实体
  content = content
    .replace(/&nbsp;/g, ' ')
    .replace(/&lt;/g, '<')
    .replace(/&gt;/g, '>')
    .replace(/&amp;/g, '&')
    .replace(/&#x27;/g, "'")
    .replace(/&#x2F;/g, '/')
    .replace(/&quot;/g, '"')
    .replace(/&nbsp;/g, ' ');

  // 清理多余空白
  content = content.replace(/\n\s*\n/g, '\n\n').trim();

  return content;
}

/**
 * 生成 Markdown 文件
 */
function generateMarkdown(metadata, html) {
  const content = cleanHtml(html);
  const now = new Date().toISOString();
  const isClaude = metadata.source.includes('claude.ai');
  
  const markdown = `---
title: "${metadata.title}"
source: "${metadata.source}"
source_type: "${isClaude ? 'claude' : 'chatgpt'}"
date: ${now}
captured_at: ${metadata.timestamp}
---

# ${metadata.title}

${metadata.description || ''}

---

## 对话内容

${content}
`;

  return markdown;
}

/**
 * 主函数
 */
async function main() {
  const htmlPath = process.argv[2] || process.argv[3];
  
  if (!htmlPath) {
    console.error('用法: node convert-markdown.js <HTML_PATH>');
    console.error('或: bun run convert-markdown.js <HTML_PATH>');
    console.error('\n从元数据文件读取: node convert-markdown.js --metadata <METADATA_JSON>');
    process.exit(1);
  }

  // 检查是否是元数据模式
  if (htmlPath === '--metadata' || htmlPath === '-m') {
    const metaPath = process.argv[3];
    if (!metaPath) {
      console.error('错误: 需要提供元数据文件路径');
      process.exit(1);
    }
    
    const metaStr = fs.readFileSync(metaPath, 'utf8');
    const metadata = JSON.parse(metaStr);
    const html = fs.readFileSync(metadata.htmlPath, 'utf8');
    
    const markdown = generateMarkdown(metadata, html);
    const mdPath = metadata.htmlPath.replace('-captured.html', '.md');
    fs.writeFileSync(mdPath, markdown);
    
    console.log(`✅ Markdown 已保存: ${mdPath}`);
    return;
  }

  // 普通模式：直接处理 HTML 文件
  if (!fs.existsSync(htmlPath)) {
    console.error(`错误: 文件不存在: ${htmlPath}`);
    process.exit(1);
  }

  const html = fs.readFileSync(htmlPath, 'utf8');
  
  // 尝试从同目录读取元数据
  const dir = path.dirname(htmlPath);
  const metaPath = path.join(dir, '.metadata.json');
  
  let metadata;
  if (fs.existsSync(metaPath)) {
    metadata = JSON.parse(fs.readFileSync(metaPath, 'utf8'));
  } else {
    // 从 HTML 中提取基本信息
    const titleMatch = html.match(/<title>([^<]+)<\/title>/i);
    const ogTitleMatch = html.match(/<meta property="og:title" content="([^"]+)"/);
    
    metadata = {
      title: ogTitleMatch ? ogTitleMatch[1] : (titleMatch ? titleMatch[1] : 'Untitled'),
      source: '',
      timestamp: new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5)
    };
  }

  const markdown = generateMarkdown(metadata, html);
  const mdPath = htmlPath.replace('.html', '.md').replace('-captured', '');
  
  fs.writeFileSync(mdPath, markdown);
  
  console.log(`✅ Markdown 已保存: ${mdPath}`);
  
  // 输出文件大小
  const htmlSize = (fs.statSync(htmlPath).size / 1024).toFixed(1);
  const mdSize = (fs.statSync(mdPath).size / 1024).toFixed(1);
  console.log(`📊 大小: ${mdSize}KB (Markdown) + ${htmlSize}KB (HTML)`);
}

main().catch(err => {
  console.error('错误:', err.message);
  process.exit(1);
});