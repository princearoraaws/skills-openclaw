\# API 数据获取技能



\## 技能名称

API 数据获取



\## 技能描述

通过 HTTP/HTTPS 调用第三方 API 接口，支持 GET/POST 请求，自动解析 JSON 数据，返回标准化结果，可用于数据拉取、接口测试、外部数据对接等场景。



\## 支持请求方式

\- GET

\- POST



\## 入参说明

| 参数名 | 类型 | 必填 | 说明 |

|--------|------|------|------|

| url | string | 是 | API 地址 |

| method | string | 否 | 请求方法，默认 GET |

| headers | object | 否 | 请求头 |

| params | object | 否 | URL 查询参数 |

| data | object | 否 | POST 请求体（JSON） |

| timeout | number | 否 | 超时时间，默认 10s |



\## 出参说明

| 字段 | 类型 | 说明 |

|------|------|------|

| status | string | success / fail |

| data | any | 返回数据 |

| error | string | 错误信息 |



\## 使用示例

\### GET 示例

```json

{

&#x20; "url": "https://jsonplaceholder.typicode.com/todos/1"

}

