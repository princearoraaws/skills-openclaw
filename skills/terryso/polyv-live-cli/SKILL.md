---
name: polyv-live-cli
description: 管理保利威直播服务，包括频道管理、推流操作、商品管理、优惠券、回放、文档和统计数据。当用户需要管理直播频道、配置推流设置、管理商品、处理优惠券、查看直播数据或管理回放录像时使用。
allowed-tools: Bash(npx polyv-live-cli@latest:*)
---

# 保利威直播 CLI

## 执行前验证

在执行任何 CLI 命令之前，必须先验证账号认证状态。

### 1. 检测认证状态

```bash
npx polyv-live-cli@latest account list
```

### 2. 配置认证（如需要）

如果用户未配置认证，引导用户提供 AppID 和 AppSecret：

```
请提供你的保利威 AppID 和 AppSecret：
- 访问 https://www.polyv.net/ 后台获取
- 路径：云直播 -> 设置 -> 开发者信息
```

然后用用户提供的凭据配置：

```bash
npx polyv-live-cli@latest account add <名称> --app-id <appId> --app-secret <appSecret>
npx polyv-live-cli@latest account set-default <名称>
```

### 3. 验证配置成功

```bash
npx polyv-live-cli@latest channel list
```

## 快速开始

```bash
# 添加账号凭证
npx polyv-live-cli@latest account add myaccount --app-id <id> --app-secret <secret>

# 切换账号
npx polyv-live-cli@latest use myaccount

# 创建频道
npx polyv-live-cli@latest channel create -n "我的直播"

# 获取推流密钥（用于OBS）
npx polyv-live-cli@latest stream get-key -c <channelId>

# 开始直播
npx polyv-live-cli@latest stream start -c <channelId>

# 监控直播状态
npx polyv-live-cli@latest stream status -c <channelId> -w
```

## 身份认证

```bash
# 账号管理
npx polyv-live-cli@latest account add <名称> --app-id <id> --app-secret <secret>
npx polyv-live-cli@latest account list
npx polyv-live-cli@latest account set-default <名称>
npx polyv-live-cli@latest account delete <名称>

# 切换当前会话账号
npx polyv-live-cli@latest use <名称>

# 或使用内联凭证
npx polyv-live-cli@latest channel list --appId <id> --appSecret <secret>
npx polyv-live-cli@latest channel list -a <账号名称>
```

## 频道命令

```bash
# 增删改查操作
npx polyv-live-cli@latest channel create -n <名称> [-d <描述>] [--scene <场景类型>]
npx polyv-live-cli@latest channel list [-P <页码>] [-l <数量>] [--keyword <关键词>]
npx polyv-live-cli@latest channel get -c <频道ID>
npx polyv-live-cli@latest channel update -c <频道ID> [-n <名称>] [-d <描述>]
npx polyv-live-cli@latest channel delete -c <频道ID> [-f]
npx polyv-live-cli@latest channel batch-delete --channelIds <id1> <id2> ...

# 场景类型: topclass（三分屏）, cloudclass（云课堂）, telecast（纯视频）, akt（活动直播）
# 模板: ppt（PPT模板）, video（视频模板）
```

## 推流命令

```bash
# 推流操作
npx polyv-live-cli@latest stream get-key -c <频道ID>        # 获取RTMP地址和推流密钥
npx polyv-live-cli@latest stream start -c <频道ID>          # 开始直播
npx polyv-live-cli@latest stream stop -c <频道ID>           # 结束直播
npx polyv-live-cli@latest stream status -c <频道ID> [-w]    # 查看状态（-w持续监控）
npx polyv-live-cli@latest stream push -c <频道ID> -f <文件> # 推送视频文件
npx polyv-live-cli@latest stream verify -c <频道ID> [-d 60] # 直播质量验证
npx polyv-live-cli@latest stream monitor -c <频道ID> [-r 5] # 实时监控面板
```

## 商品命令

```bash
# 商品管理
npx polyv-live-cli@latest product list -c <频道ID>
npx polyv-live-cli@latest product add -c <频道ID> --name <名称> --price <价格>
npx polyv-live-cli@latest product get -c <频道ID> -p <商品ID>
npx polyv-live-cli@latest product update -c <频道ID> -p <商品ID> [--name <名称>]
npx polyv-live-cli@latest product delete -c <频道ID> -p <商品ID>
```

## 优惠券命令

```bash
# 优惠券操作
npx polyv-live-cli@latest coupon create -c <频道ID> -n <名称> --discount <金额>
npx polyv-live-cli@latest coupon list -c <频道ID>
npx polyv-live-cli@latest coupon get -c <频道ID> --couponId <优惠券ID>
npx polyv-live-cli@latest coupon delete -c <频道ID> --couponId <优惠券ID>
```

## 回放命令

```bash
# 回放管理
npx polyv-live-cli@latest playback list -c <频道ID>
npx polyv-live-cli@latest playback get -c <频道ID> --videoId <回放ID>
npx polyv-live-cli@latest playback delete -c <频道ID> --videoId <回放ID>
npx polyv-live-cli@latest playback merge -c <频道ID> --videoIds <id1> <id2>
```

## 场次命令

```bash
# 场次管理
npx polyv-live-cli@latest session list [-c <频道ID>] [--page <页码>] [--page-size <数量>]
npx polyv-live-cli@latest session get -c <频道ID> --session-id <场次ID>

# 状态值: unStart(未开始), live(直播中), end(已结束), playback(回放中), expired(已过期)
```

## 文档命令

```bash
# 文档管理
npx polyv-live-cli@latest document list -c <频道ID> [--status <状态>] [--page <页码>] [--page-size <数量>]
npx polyv-live-cli@latest document upload -c <频道ID> --url <文件URL> [--type common|animate] [--doc-name <名称>]
npx polyv-live-cli@latest document delete -c <频道ID> --file-id <文档ID> [--type old|new] [--force]
npx polyv-live-cli@latest document status -c <频道ID> --file-id <文档ID>

# 状态值: normal, waitUpload, failUpload, waitConvert, failConvert
# 类型: common(普通转换), animate(动效转换)
```

## 统计命令

```bash
# 数据分析
npx polyv-live-cli@latest statistics overview -c <频道ID>
npx polyv-live-cli@latest statistics viewdata -c <频道ID> [--start-date <日期>]
npx polyv-live-cli@latest statistics summary -c <频道ID>
npx polyv-live-cli@latest statistics export -c <频道ID> -f csv -o report.csv
```

## 播放器命令

```bash
# 播放器配置
npx polyv-live-cli@latest player get -c <频道ID>
npx polyv-live-cli@latest player update -c <频道ID> [--autoplay] [--logo <url>]
```

## 场景初始化

```bash
# 预设场景
npx polyv-live-cli@latest setup --list                    # 列出可用场景
npx polyv-live-cli@latest setup e-commerce                # 电商直播场景
npx polyv-live-cli@latest setup education                 # 在线教育场景
```

## 监控命令

```bash
# 直播监控面板
npx polyv-live-cli@latest monitor start -c <频道ID>
npx polyv-live-cli@latest monitor stop
```

## 输出格式

大多数命令支持 `-o table`（默认表格格式）或 `-o json`（JSON格式，便于程序化处理）。

```bash
npx polyv-live-cli@latest channel list -o json
npx polyv-live-cli@latest stream status -c <频道ID> -o json
```

## 全局选项

```bash
--appId <id>           # 保利威应用ID
--appSecret <secret>   # 保利威应用密钥
--userId <id>          # 保利威用户ID（可选）
-a, --account <名称>   # 使用指定账号
--verbose              # 显示详细信息
--debug                # 启用调试模式
--timeout <毫秒>       # API超时时间（默认30000毫秒）
```

## 常用工作流程

### 创建并开始直播

```bash
npx polyv-live-cli@latest use myaccount
npx polyv-live-cli@latest channel create -n "新品发布会" -d "新品展示直播"
# 记住输出的频道ID
npx polyv-live-cli@latest stream get-key -c 3151318
# 在OBS中使用RTMP地址和推流密钥
npx polyv-live-cli@latest stream start -c 3151318
npx polyv-live-cli@latest stream status -c 3151318 -w
```

### 初始化电商直播场景

```bash
npx polyv-live-cli@latest setup e-commerce
# 自动创建带商品预配置的频道
```

### 监控直播质量

```bash
npx polyv-live-cli@latest stream verify -c 3151318 -d 120 -i 5
npx polyv-live-cli@latest stream monitor -c 3151318 -r 3 --alerts
```

## 详细文档

* **身份认证配置** [references/authentication.md](references/authentication.md)
* **频道管理** [references/channel-management.md](references/channel-management.md)
* **推流操作** [references/streaming.md](references/streaming.md)
* **商品管理** [references/products.md](references/products.md)
* **优惠券管理** [references/coupons.md](references/coupons.md)
* **回放管理** [references/playback.md](references/playback.md)
* **场次管理** [references/session-management.md](references/session-management.md)
* **文档管理** [references/documents.md](references/documents.md)
* **统计分析** [references/statistics.md](references/statistics.md)
* **场景初始化** [references/scene-setup.md](references/scene-setup.md)

## 联系方式

- 邮箱: support@polyv.net
- 官网: https://www.polyv.net/
- 保利威直播 API 文档: https://help.polyv.net/#/live/api/
- 技术支持: 400-993-9533
