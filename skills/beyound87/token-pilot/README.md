# token-pilot

## 这是什么
`token-pilot` 是一个用于降低 OpenClaw 日常 token 消耗的优化技能。

它的核心不是"替你自动改一切配置",而是提供三类能力:
1. **会话内自动生效的行为规则**
2. **对相关技能的协同节流建议**
3. **用于审计和优化的脚本**

## 当前准确定位
提供三类能力:
1. **会话内自动生效的行为规则**
2. **对相关技能的协同节流建议**
3. **用于审计和优化的脚本**

## 核心能力

### 1. 自动生效规则
会话加载后,自动遵循以下方向:
- 先小读再全读
- 压缩长工具输出
- 简答问题尽量短答
- 不重复读取同一文件
- 合并独立工具调用
- 小改优先 `edit`
- 按角色重量控制工具使用范围

### 2. 角色感知型工具经济
基于自身 `SOUL.md` 内容判定当前角色是:
- 重型角色
- 中型角色
- 轻型角色

再决定默认工具使用强度。

### 3. 技能协同建议
#### 与 `coding-lead`
- 大上下文写磁盘 context 文件
- ACP prompt 只放最小必要头部

#### 与 `smart-agent-memory`
- 先查历史,后做调查
- 解决后及时记录 lesson / fact,减少重复探索

#### 与多 agent 团队结构
- 轻任务使用轻上下文
- 模板和职责说明尽量放到 references,不塞进主 prompt
- 如果检测到共享 inbox / dashboard / product manifest / role SOUL 等结构,先读最小协调文件,再读任务文件

## 初始化
本技能**无需初始化**。
安装后,在后续会话里加载技能即可按规则生效。

## 使用方法

### 1. 作为行为规则直接使用
如果技能已加载,规则会自动生效,不需要额外命令。

### 2. 使用审计脚本
```bash
node {baseDir}/scripts/audit.js --all
node {baseDir}/scripts/audit.js --config
node {baseDir}/scripts/audit.js --synergy
```
适合检查当前工作区、配置与技能协同情况。

### 3. 使用优化脚本
```bash
node {baseDir}/scripts/optimize.js
node {baseDir}/scripts/optimize.js --apply
node {baseDir}/scripts/optimize.js --cron
node {baseDir}/scripts/optimize.js --agents
node {baseDir}/scripts/optimize.js --template
```

### 4. 生成技能目录索引
```bash
node {baseDir}/scripts/catalog.js [--output path]
```

## 配置说明
本技能本身没有独立配置文件,但 README 层面的推荐配置应以**"建议"**而不是**"自动已启用"**理解。

### 推荐的 openclaw.json 方向
- `bootstrapMaxChars`
- `bootstrapTotalMaxChars`
- `compaction.memoryFlush`
- `contextPruning`
- `heartbeat`

这些只是**建议你审计并手动合并**,不是 token-pilot 自动替你写入。

### 工具白名单建议
可按角色配置 `tools.allow`,但应结合实际工具集,不要把 README 写成对所有环境都完全适用的固定结论。

## 适用场景
- 工作区太大、read 过多
- cron 太多、上下文太重
- 多 agent 团队 token 消耗偏高
- 单 agent 长会话上下文膨胀
- 编码任务 prompt 过胖
- 经常重复调查同一问题

## 不适用 / 边界
- 不替代具体业务技能
- 不直接保证固定节省比例
- 不自动重写你的全部配置
- 不应把 README 里的推荐项当作已经落地的事实

## 相关文件
- `SKILL.md`
- `scripts/audit.js`
- `scripts/optimize.js`
- `scripts/catalog.js`
- `references/workspace-patterns.md`
- `references/cron-optimization.md`

## 最近一次修改（中文）
- **v1.2.0 / 2026-03-29**
- 多 agent 团队检测改为识别多 agent 协作结构特征（shared inbox/dashboard/manifest/role SOUL），去除 team-builder 唯一来源绑定
- 补充"单 agent 长会话上下文膨胀"为适用场景
- 将配置项定位为建议，而非自动落地事实
