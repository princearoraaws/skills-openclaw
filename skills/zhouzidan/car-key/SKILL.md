---
name: carkey
description: 查询车辆位置和车况信息（车锁、车门、车窗、空调等状态）。当用户询问"我的车在哪"、"查询车辆信息"、"车况怎么样"时自动调用。支持 SN、VIN、经纬度地址查询。
---

## 触发场景

- 用户查询车辆位置或询问"车在哪儿"
- 用户请求查询车况信息（电压、电量、里程、续航等）
- 用户询问车辆状态（车锁、车门、车窗、空调是否开启）
- 用户需要获取车辆详细信息（SN、VIN、档位、电源状态等）
- 缺少认证信息时，引导用户提供 token

## 核心配置

| 配置项 | 值 |
|--------|-----|
| API 地址 | `https://openapi.nokeeu.com/iot/v1/condition` |
| 缓存文件 | `~/.skill_carkey_cache.json` |
| 认证格式 | `vehicleToken####accessToken` |

## 认证流程

1. 检查缓存文件是否存在且 token 有效
2. 如无有效认证，引导用户提供：`vehicleToken####accessToken`
3. 解析 token（4个#分隔）：前半为 vehicleToken，后半为 accessToken
4. 保存到缓存：`~/.skill_carkey_cache.json`

## API 调用

使用 Python 脚本查询车况信息（跨平台兼容 Mac/Windows/Linux）：

```bash
# 查询全部信息
python3 query_vehicle.py

# 仅查询车辆位置
python3 query_vehicle.py -p
python3 query_vehicle.py --position

# 仅查询车况信息（车门、车锁、车窗、空调等）
python3 query_vehicle.py -c
python3 query_vehicle.py --condition

# 输出原始 JSON 数据
python3 query_vehicle.py --json
python3 query_vehicle.py -p --json
python3 query_vehicle.py -c --json
```

脚本文件：[query_vehicle.py](./query_vehicle.py)

### 响应字段说明

| 字段路径 | 说明 |
|----------|------|
| `data.sn` | 数字钥匙 SN |
| `data.vin` | 车架号 |
| `data.vehiclePosition.longitude/latitude` | GPS 经纬度 |
| `data.vehiclePosition.address` | 地址 |
| `data.vehiclePosition.positionUpdateTime` | 位置更新时间戳（毫秒） |
| `data.vehicleCondition.power` | 电源状态（0熄火/1ACC/2ON） |
| `data.vehicleCondition.gear` | 档位（1P/2N/3D/4R/5S） |
| `data.vehicleCondition.door.*` | 车门状态（0关闭/1开启） |
| `data.vehicleCondition.lock.*` | 车锁状态（0解锁/1上锁） |
| `data.vehicleCondition.window.*` | 车窗状态（0关闭/1开启） |
| `data.vehicleCondition.airConditionerState.*` | 空调温度设定 |

### 状态值速查

```
电源: 0=熄火, 1=ACC, 2=ON
档位: 1=P档, 2=N档, 3=D档, 4=R档, 5=S档
门/窗/锁: 0=关闭/解锁, 1=开启/上锁
后备箱: 0=关闭, 1=开启
```

## 脚本功能

Python 脚本 `query_vehicle.py` 提供以下功能：

| 参数 | 简写 | 说明 |
|------|------|------|
| `--position` | `-p` | 仅查询车辆位置信息 |
| `--condition` | `-c` | 仅查询车况信息（车门、车锁、车窗、空调） |
| `--json` | | 输出原始 JSON 数据 |
| 无参数 | | 查询全部信息（位置 + 车况） |

其他特性：
- 自动读取缓存文件中的认证信息
- 格式化输出车辆状态
- 完整的错误处理和提示

## 错误处理

| 错误类型 | 处理方式 |
|----------|----------|
| 认证信息缺失 | 引导用户提供 vehicleToken####accessToken |
| 认证格式错误 | 提示正确的4个#号分隔格式 |
| API 请求失败 | 返回错误码和 message |
| 车辆不在线 | 提示车辆需要在线才能获取最新数据 |

## 依赖

- `Python 3.6+`（使用标准库，无需额外安装依赖）