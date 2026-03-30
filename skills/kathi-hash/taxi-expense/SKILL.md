---
name: taxi_expense
description: 识别滴滴打车订单截图，OCR识别文字+坐标，马赛克脱敏目的地，按月生成报销Excel
---

When user sends taxi order screenshots:

## Setup (first time only)
```bash
bash ~/.openclaw/workspace/skills/taxi_expense/scripts/setup.sh
```

## Process Screenshots
```bash
node ~/.openclaw/workspace/skills/taxi_expense/scripts/process.js <image1> [image2] ...
```

The script will:
1. OCR each image with Tesseract.js v4 (uses coordinates to detect text positions)
2. Filter: only weekday evening rides (after 18:00) qualify for reimbursement
3. Mosaic the destination address (keeps first and last character visible)
4. Save screenshots to `~/.openclaw/workspace/taxi_expense/screenshots/`
5. Update `~/.openclaw/workspace/taxi_expense/taxi_data.json` (auto-dedup)
6. Generate monthly Excel: `~/.openclaw/workspace/taxi_expense/YYYY-MM-taxi_expense.xlsx`

## Output
Tell user:
- How many new orders were added
- Monthly totals
- Any skipped orders and why

## Send Preview (only if user asks)
The script saves mosaiced screenshots to the `screenshots/` directory. Send them manually when requested.

## Configuration
Edit `scripts/process.js` to change:
- `PIXEL_SIZE`: mosaic pixel block size (default: 8)
- `CARD_TOP_OFFSET` / `CARD_BOT_OFFSET`: crop area around destination text
- `MOSAIC_PADDING`: padding around first/last visible character

## Known Issues
- Tesseract Chinese quality is imperfect ("点"→"炭", "轻享"→"轻亭")
- Uses regex `/终[点炭]/` for tolerant matching
- Amount recognition: ¥ may be misread as other characters
- Source images must be the ORIGINAL screenshots (not previously processed/cropped)
