# 板材费用统计 Skill

## 功能

从激光切割 PDF（Bystronic ByWork job list）提取板材数据，自动生成艾威格式 Excel。

**核心能力：**
- 从 PDF 文件名识别板厚和材质
- 从 PDF 提取 Sheet dimension（长×宽）、Cycles（数量）、Waste（废料率）
- 从价格表自动匹配当月采购单价
- 提取后自动核对 Material data（检查有无遗漏）
- 生成带公式的完整 Excel

## 使用方法

```bash
python3 calculator.py <PDF文件夹> [输出文件] [废料单价] [价格表] [月份]
```

**示例：**
```bash
# 基础用法
python3 calculator.py /tmp/0642_processing

# 带价格表
python3 calculator.py /tmp/0642_processing /tmp/0642_Board_material_cost_statistics.xlsx 0 /tmp/价格表.xlsx 3
```

**输出命名：** `{文件夹名}_Board material cost statistics.xlsx`

## 文件名解析

| 文件名 | 厚度 | 材质 |
|--------|------|------|
| `3mm.pdf` | 3mm | Q235 |
| `1.5mm.pdf` | 1.5mm | Q235 冷板（≤2mm） |
| `3Mn.pdf` | 3mm | Q345 |
| `sus-1mm.pdf` | 1mm | SUS |
| `dxb-1.5mm.pdf` | 1.5mm | 镀锌板 |
| `nm-8mm.pdf` | 8mm | 耐磨板 |

## 厚度映射（负公差）

| PDF 厚度 | 实际厚度 |
|----------|----------|
| 3mm | 2.75mm |
| 4mm | 3.75mm |
| 5mm | 4.75mm |
| 6mm | 5.75mm |
| 8mm | 7.75mm |
| 10mm | 9.75mm |
| 12mm | 11.75mm |

## 排序规则

1. **Q235冷板 + Q235 + Q345**：按厚度从小到大，同厚度按材质排
2. **SUS → 镀锌板 → 耐磨板**：排在后面

## Excel 结构

| 列 | 内容 | 说明 |
|----|------|------|
| A | 序号 | 自动编号 |
| D | 材质 | Q235冷板/Q235/Q345/SUS/镀锌板/耐磨板 |
| E | 长（mm） | 从 PDF 提取 |
| F | 宽（mm） | 从 PDF 提取 |
| G | 厚（mm） | 负公差映射后 |
| H | 数量 | Cycles |
| I | 单重（Kg） | 公式：长×宽×厚/10⁶×密度 |
| J | 合计重量 | 公式：I×H |
| K | 利用率 | 公式：1-废料率 |
| L | 废料重量 | 公式：J×(1-K)×0.85 |
| M | 单价（Kg） | 从价格表自动填充 |
| N | 板材价格 | 公式：J×M |
| O | 废料率 | 从 PDF 提取 |

**密度：** SUS=7.95，其他=7.85

## 价格表格式

震源板材价格 Excel：
- 工作表名含 "X月份板材价格"
- F 列：厚度，C 列：材质名称
- 动态匹配 "X月采购价格" 列

## 核对功能

提取完自动核对 Material data（第一页）：
- 检查 Used > 0 的板材是否都提取到了
- 检查提取数量和 Used 是否一致
- Used=0 的不管

## 文件结构

```
切割费用计算/
├── calculator.py       # 主脚本
├── requirements.txt    # 依赖
├── README.md           # 详细文档
└── SKILL.md            # 本文件
```

## 版本

- **v3.4** (2026-03-25) - 修复 Material data 提取 bug，核对逻辑优化
- **v3.3** (2026-03-25) - 添加 Material data 核对功能
- **v3.2** (2026-03-25) - SUS 密度 7.95，表头自动换行，支持镀锌板/耐磨板，排序调整
- **v3.1** (2026-03-25) - 合计行 A-K 合并居中、两位小数、不加粗
- **v3.0** (2026-03-25) - 价格表自动填充
- **v2.0** (2026-03-23) - 无模板独立生成版
- **v1.0** (2026-03-21) - 初始版本
