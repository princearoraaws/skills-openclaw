---
name: zbj
version: 0.1.0
description: ZBJ MCP 官方技能 - 一站式服务交易平台集成
author: ZBJ
homepage: https://zmcp.zbj.com
openclaw_version: v2026.3.7+
type: script
script:
  command: node
  args: [bridge.js]
requires:
  binaries:
    - node
  env:
    - ZBJ_API_URL
    - ZBJ_API_KEY
primary_credential: ZBJ_API_KEY
permissions:
  - network:zmcp.zbj.com:443
security:
  sandbox: required
---

# ZBJ MCP 官方技能

基于 Model Context Protocol (MCP) 构建的 ZBJ（猪八戒网）服务集成技能，提供 AI Agent 访问一站式服务交易平台的能力。

支持：需求发布与管理、订单查询与管理、服务/店铺/需求搜索、类目智能匹配、服务商评价、托管支付等功能。已实现 **18 个工具**，覆盖需求管理、订单管理、搜索服务、类目服务 4 大功能模块，以及 **2 个资源** 用于系统配置和类目数据访问。

---

## 安装

```bash
# 1. 进入技能目录
cd ~/.openclaw/skills/zbj

# 2. 安装依赖（axios）
npm install

# 3. 配置环境变量
export ZBJ_API_URL="https://zmcp.zbj.com"
```

**依赖说明**：
- `axios ^1.7.7` - HTTP 请求库

---

## 工具列表（18个工具，4个模块）

### 需求管理（8个）
| 工具名 | 功能说明 |
|--------|----------|
| publish_demand | 发布或修改需求，传入 demandId 则为修改 |
| get_demand_detail | 查询需求详情（含投标情况） |
| close_demand | 关闭需求 |
| pause_demand | 暂停需求 |
| open_demand | 公开已暂停的需求 |
| eliminate_seller | 淘汰服务商 |
| select_winner | 选服务商中标 |
| search_demands | 搜索需求（支持状态筛选） |

### 订单管理（5个）
| 工具名 | 功能说明 |
|--------|----------|
| get_order_detail | 查询订单详情 |
| search_orders | 搜索订单 |
| eval_seller | 评价已完成订单的服务商 |
| close_order | 关闭订单 |
| get_trusteeship_pay_url | 获取托管支付地址 |

### 搜索服务（2个）
| 工具名 | 功能说明 |
|--------|----------|
| search_services | 搜索服务商品 |
| search_shops | 搜索店铺/服务商 |

### 类目服务（2个）
| 工具名 | 功能说明 |
|--------|----------|
| get_categories | 获取类目列表（支持层级筛选） |
| search_category | 根据关键词搜索匹配类目 |

### 系统工具（1个）
| 工具名 | 功能说明 |
|--------|----------|
| health_check | 检查后端服务健康状态 |

---

## 资源列表（2个）

| URI | 描述 | MIME 类型 |
|-----|------|-----------|
| `zbj://config` | 系统配置信息 | application/json |
| `zbj://categories` | 所有服务类目数据（AI 智能识别用） | application/json |

---

## 使用示例

```bash
# 健康检查
/run zbj health_check '{}'

# 搜索类目
/run zbj search_category '{"keyword":"网站"}'

# 获取类目列表（三级）
/run zbj get_categories '{"level":3}'

# 发布需求
/run zbj publish_demand '{"title":"开发企业官网","description":"需要开发响应式企业官网","categoryId":1001,"price":5000}'

# 查询需求详情
/run zbj get_demand_detail '{"demandId":12345}'

# 搜索服务
/run zbj search_services '{"keyword":"logo设计","pageNum":1,"pageSize":20}'

# 搜索店铺
/run zbj search_shops '{"keyword":"网站建设"}'

# 查询订单详情
/run zbj get_order_detail '{"orderId":"ORDER123"}'

# 获取托管支付链接
/run zbj get_trusteeship_pay_url '{"orderId":"ORDER123","hostedPrice":1000,"clientType":"pc"}'
```

---

## 获取 API Key

使用本技能需要 API 认证密钥，请访问以下地址获取：

**https://account.zbj.com/setting/mcpapikey**

获取后配置环境变量：
```bash
export ZBJ_API_KEY="your_api_key_here"
```

---

## 环境变量

| 变量名 | 说明 | 必填 | 默认值 |
|--------|------|------|--------|
| ZBJ_API_URL | 后端 API 地址 | 否 | https://zmcp.zbj.com |
| ZBJ_API_KEY | API 认证密钥 | 是 | - |
| ZBJ_API_TIMEOUT | API 请求超时时间 (ms) | 否 | 30000 |

---

## 权限说明

本技能仅申请最小权限：
- 网络访问：仅允许 `zmcp.zbj.com:443`
- 执行权限：仅允许运行 `node`

无文件读写、无系统权限、无高危操作。

---

## 技术栈

- TypeScript 5.3+
- @modelcontextprotocol/sdk 1.0+
- Node.js 18+
- Zod 3.22+ (参数验证)

---

## 许可证

MIT
