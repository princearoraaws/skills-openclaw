#!/usr/bin/env node
/**
 * process.js - 处理滴滴打车截图
 * 
 * Usage: node process.js <image1> [image2] ...
 * 
 * 功能:
 * 1. Tesseract OCR 识别文字+坐标
 * 2. 检测目的地文字并马赛克脱敏（保留首尾字）
 * 3. 按月生成报销 Excel
 * 4. 自动去重
 */

const fs = require('fs');
const path = require('path');

// === CWD 修复：tesseract.js 需要从 /tmp 运行 ===
process.chdir('/tmp');

// === 路径配置 ===
const SKILL_DIR = path.resolve(__dirname, '..');
const DEPS_DIR = path.join(SKILL_DIR, 'deps');
const TESSDATA_DIR = path.join(SKILL_DIR, 'tessdata');
const WORKSPACE = process.env.HOME + '/.openclaw/workspace';
const BASE_DIR = path.join(WORKSPACE, 'taxi_expense');
const SCREEN_DIR = path.join(BASE_DIR, 'screenshots');
const DATA_FILE = path.join(BASE_DIR, 'taxi_data.json');

// === 马赛克参数 ===
const PIXEL_SIZE = 8;
const CARD_TOP_OFFSET = 160;   // 目的地文字上方保留的像素
const CARD_BOT_OFFSET = 200;   // 目的地文字下方保留的像素
const MOSAIC_PADDING = 3;      // 首尾字保护边距

// === 加载依赖 ===
let Tesseract, sharp, ExcelJS;
try {
  Tesseract = require(path.join(DEPS_DIR, 'node_modules', 'tesseract.js'));
  sharp = require(path.join(DEPS_DIR, 'node_modules', 'sharp'));
  ExcelJS = require(path.join(DEPS_DIR, 'node_modules', 'exceljs'));
} catch (e) {
  console.error('❌ 依赖未安装，请先运行: bash scripts/setup.sh');
  process.exit(1);
}

// === 目录初始化 ===
fs.mkdirSync(SCREEN_DIR, { recursive: true });

function maskDestination(text) {
  if (!text || text.length <= 2) return text;
  return text[0] + '*'.repeat(text.length - 2) + text[text.length - 1];
}

// === 去重：基于日期+金额 ===
function loadExisting() {
  if (fs.existsSync(DATA_FILE)) return JSON.parse(fs.readFileSync(DATA_FILE, 'utf8'));
  return [];
}

function isDuplicate(orders, date, amount) {
  return orders.some(o => o.date === date && o.amount === amount);
}

// === OCR 识别 ===
async function ocrImage(imagePath) {
  const worker = await Tesseract.createWorker({ langPath: TESSDATA_DIR, logger: () => {} });
  await worker.loadLanguage('chi_sim+eng');
  await worker.initialize('chi_sim+eng');
  const { data } = await worker.recognize(imagePath);
  await worker.terminate();
  return data;
}

// === 提取订单 ===
function extractOrders(data) {
  const orders = [];

  // 找目的地行
  const destLines = data.lines.filter(l => l.text.replace(/\s/g, '').match(/终[点炭]/));
  // 找日期行
  const dateLines = data.lines.filter(l => l.text.match(/20\d{2}/) && l.text.match(/月.*日/));
  // 找金额行
  const amountLines = data.lines.filter(l => l.text.includes('¥') || l.text.includes('￥'));

  for (const dl of destLines) {
    // 匹配最近的日期和金额
    const dateLine = dateLines.reduce((best, cur) => {
      if (!best || Math.abs(cur.bbox.y0 - dl.bbox.y0) < Math.abs(best.bbox.y0 - dl.bbox.y0)) return cur;
      return best;
    }, null);

    const amountLine = amountLines.reduce((best, cur) => {
      if (!best || Math.abs(cur.bbox.y0 - dl.bbox.y0) < Math.abs(best.bbox.y0 - dl.bbox.y0)) return cur;
      return best;
    }, null);

    if (!dateLine || !amountLine) continue;

    // 解析日期
    const dateMatch = dateLine.text.match(/(\d{4})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日\s*(\d{1,2})[.:：](\d{2})/);
    if (!dateMatch) continue;

    const [, y, m, d, hh, mm] = dateMatch;
    const date = `${y}-${m.padStart(2,'0')}-${d.padStart(2,'0')}`;
    const time = `${hh.padStart(2,'0')}:${mm}`;

    // 解析金额
    const amountMatch = amountLine.text.match(/[¥￥]\s*([\d.]+)/);
    if (!amountMatch) continue;
    const amount = parseFloat(amountMatch[1]);

    // 解析目的地
    const destText = dl.text.replace(/\s/g, '').replace(/终[点炭][:：]?\s*/, '');
    const startText = amountLine.text.replace(/\s/g, '').replace(/.*起点[:：]?\s*/, '').replace(/[¥￥][\d.]+.*/, '');

    orders.push({
      date, time, amount,
      start: startText || '未知',
      end: destText || '未知',
      destBbox: dl.bbox,
      qualified: isQualified(date, time)
    });
  }

  return orders;
}

// === 报销判定 ===
function isQualified(date, time) {
  const d = new Date(date);
  const dow = d.getDay(); // 0=Sun, 6=Sat
  if (dow === 0 || dow === 6) return false;
  const [hh] = time.split(':').map(Number);
  return hh >= 18;
}

// === 马赛克处理 ===
async function processMosaic(imagePath, order, data, outputName) {
  const metadata = await sharp(imagePath).metadata();
  const w = metadata.width;
  const h = metadata.height;

  // 找目的地行的所有字
  const dl = data.lines.find(l =>
    l.text.replace(/\s/g, '').match(/终[点炭]/) &&
    Math.abs(l.bbox.y0 - order.destBbox.y0) < 30
  );
  if (!dl) return null;

  const lineWords = data.words.filter(w =>
    w.bbox.y0 >= dl.bbox.y0 - 5 && w.bbox.y1 <= dl.bbox.y1 + 5 &&
    w.bbox.x0 >= dl.bbox.x0
  ).sort((a, b) => a.bbox.x0 - b.bbox.x0);

  // 过滤掉标签字
  const addrWords = lineWords.filter(w => {
    const t = w.text.replace(/\s/g, '');
    return t.length > 0 && !['终', '点', '炭', ':', '：'].includes(t);
  });

  if (addrWords.length < 2) return null;

  const firstWord = addrWords[0];
  const lastWord = addrWords[addrWords.length - 1];

  // 裁剪订单卡片
  const cardTop = Math.max(0, dl.bbox.y0 - CARD_TOP_OFFSET);
  const cardBot = Math.min(h, dl.bbox.y1 + CARD_BOT_OFFSET);
  const cardH = cardBot - cardTop;

  // 马赛克区域
  const mX = firstWord.bbox.x1 + MOSAIC_PADDING;
  const mW = lastWord.bbox.x0 - mX - MOSAIC_PADDING;
  const mY = dl.bbox.y0 - cardTop;
  const mH = dl.bbox.y1 - dl.bbox.y0;

  if (mW <= 0) return null;

  // 裁剪 + 马赛克
  await sharp(imagePath).extract({ left: 0, top: cardTop, width: w, height: cardH }).toFile('/tmp/_card.png');
  await sharp('/tmp/_card.png').extract({ left: mX, top: mY, width: mW, height: mH }).toFile('/tmp/_cs.png');
  await sharp('/tmp/_cs.png')
    .resize(Math.ceil(mW / PIXEL_SIZE), Math.ceil(mH / PIXEL_SIZE), { kernel: 'nearest', fit: 'fill' })
    .toFile('/tmp/_csm.png');
  await sharp('/tmp/_csm.png')
    .resize(mW, mH, { kernel: 'nearest', fit: 'fill' })
    .toFile('/tmp/_ct.png');

  // 合成
  const { data: origData } = await sharp('/tmp/_card.png').raw().toBuffer({ resolveWithObject: true });
  const { data: tileData } = await sharp('/tmp/_ct.png').raw().toBuffer({ resolveWithObject: true });

  const result = Buffer.from(origData);
  for (let y = 0; y < mH; y++)
    for (let x = 0; x < mW; x++) {
      const di = ((y + mY) * w + (x + mX)) * 3;
      const si = (y * mW + x) * 3;
      result[di] = tileData[si];
      result[di + 1] = tileData[si + 1];
      result[di + 2] = tileData[si + 2];
    }

  const outPath = path.join(SCREEN_DIR, outputName);
  await sharp(result, { raw: { width: w, height: cardH, channels: 3 } }).png().toFile(outPath);
  return outPath;
}

// === 生成 Excel ===
async function generateExcel(orders) {
  const months = [...new Set(orders.map(o => o.date.substring(0, 7)))].sort();
  const results = [];

  for (const month of months) {
    const mo = orders.filter(o => o.date.startsWith(month)).sort((a, b) => a.date.localeCompare(b.date));
    if (mo.length === 0) continue;

    const wb = new ExcelJS.Workbook();
    const ws = wb.addWorksheet('打车报销');

    // 表头
    ws.columns = [
      { header: '序号', key: 'no', width: 6 },
      { header: '日期', key: 'date', width: 15 },
      { header: '时间', key: 'time', width: 10 },
      { header: '起点', key: 'start', width: 30 },
      { header: '终点', key: 'end', width: 20 },
      { header: '金额', key: 'amount', width: 10 },
      { header: '备注', key: 'note', width: 12 }
    ];
    ws.getRow(1).font = { bold: true };
    ws.getRow(1).alignment = { horizontal: 'center' };

    mo.forEach((o, i) => ws.addRow({
      no: i + 1, date: o.date, time: o.time,
      start: o.start, end: o.end, amount: o.amount,
      note: o.note || '加班打车'
    }));

    ws.getColumn('amount').numFmt = '¥#,##0.00';

    const totalRow = ws.addRow([
      '', '', '', '', '合计',
      { formula: `SUM(F2:F${mo.length + 1})` }, ''
    ]);
    totalRow.font = { bold: true };
    totalRow.getCell('amount').numFmt = '¥#,##0.00';

    // 截图 Sheet
    const imgSheet = wb.addWorksheet('订单截图');
    imgSheet.getColumn(1).width = 25;
    let curRow = 1;

    for (const o of mo) {
      if (!o.file) continue;
      const imgPath = path.join(SCREEN_DIR, o.file);
      if (!fs.existsSync(imgPath)) continue;

      imgSheet.getRow(curRow).getCell(1).value = `📅 ${o.date}  💰 ¥${o.amount.toFixed(2)}`;
      imgSheet.getRow(curRow).getCell(1).font = { bold: true, size: 11 };
      imgSheet.getRow(curRow).height = 18;
      curRow++;

      const imgBuf = fs.readFileSync(imgPath);
      const imgId = wb.addImage({ buffer: imgBuf, extension: 'png' });
      imgSheet.addImage(imgId, {
        tl: { col: 0, row: curRow },
        ext: { width: 500, height: 150 }
      });
      imgSheet.getRow(curRow).height = 112;
      curRow++;
      imgSheet.getRow(curRow).height = 2;
      curRow++;
    }

    const outPath = path.join(BASE_DIR, `${month}-taxi_expense.xlsx`);
    await wb.xlsx.writeFile(outPath);

    const total = mo.reduce((s, o) => s + o.amount, 0);
    results.push({ month, count: mo.length, total, path: outPath });
  }

  return results;
}

// === 主流程 ===
async function main() {
  const args = process.argv.slice(2);
  if (args.length === 0) {
    console.log('Usage: node process.js <image1> [image2] ...');
    process.exit(1);
  }

  const existingOrders = loadExisting();
  let newOrders = [];
  const allOcrData = {};

  for (const imagePath of args) {
    if (!fs.existsSync(imagePath)) {
      console.log(`⚠️  文件不存在: ${imagePath}`);
      continue;
    }

    console.log(`\n🔍 OCR: ${path.basename(imagePath)}`);
    const data = await ocrImage(imagePath);
    allOcrData[imagePath] = data;

    const orders = extractOrders(data);
    console.log(`   找到 ${orders.length} 笔订单`);

    for (const o of orders) {
      if (isDuplicate(existingOrders, o.date, o.amount)) {
        console.log(`   ⏭️  ${o.date} ¥${o.amount} (已存在，跳过)`);
        continue;
      }

      if (!o.qualified) {
        console.log(`   ❌ ${o.date} ${o.time} ¥${o.amount} (非工作日加班，跳过)`);
        continue;
      }

      // 马赛克
      const fileName = `order_${o.date}.png`;
      console.log(`   ✅ ${o.date} ${o.time} ¥${o.amount} → 马赛克...`);
      await processMosaic(imagePath, o, data, fileName);

      existingOrders.push({
        date: o.date, time: o.time,
        start: o.start, end: maskDestination(o.end),
        amount: o.amount, note: '加班打车',
        file: fileName
      });
      newOrders.push(o);
    }
  }

  // 保存数据
  fs.writeFileSync(DATA_FILE, JSON.stringify(existingOrders, null, 2));

  // 生成所有月份的 Excel
  const results = await generateExcel(existingOrders);

  // 输出结果
  console.log('\n📊 处理结果:');
  console.log(`   新增: ${newOrders.length} 笔`);
  for (const r of results) {
    console.log(`   ${r.month}: ${r.count} 笔, ¥${r.total.toFixed(2)}`);
  }
  console.log(`   数据文件: ${DATA_FILE}`);
  console.log(`   截图目录: ${SCREEN_DIR}`);

  // 清理临时文件
  ['/tmp/_card.png', '/tmp/_cs.png', '/tmp/_csm.png', '/tmp/_ct.png'].forEach(f => {
    try { fs.unlinkSync(f); } catch (e) {}
  });
}

main().catch(e => { console.error(e); process.exit(1); });
