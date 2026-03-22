---
name: siyuan-api
description: 轻量化思源笔记原生API集成，无需额外依赖，支持笔记本、文档、块、资源全操作，可通过SQL搜索笔记。Lightweight direct API integration for SiYuan note-taking, no extra dependencies. Supports all core operations: notebooks, documents, blocks, assets, SQL search.
metadata:
  openclaw:
    requires:
      env:
        SIYUAN_API_TOKEN:
          description: SiYuan API token from Settings → About
          required: true
        SIYUAN_API_URL:
          description: SiYuan API endpoint, default: http://127.0.0.1:6806
          required: false
---

# **SiYuan 思源笔记技能**  
集成思源笔记本地 API，支持管理笔记本、文档、块、资源，执行 SQL 搜索。

  
## **特点**  
• **轻量化**：无需安装 Node.js 依赖，不捆绑 CLI 包装  
• **原生直接调用**：Agent 直接调用官方 API，灵活组合操作  
• **简洁**：只提供 API 规范和常用示例，保持最小体积  
• **安全**：不在技能包存储任何凭据，Token 由用户本地环境配置  
• 本技能仅和用户本地运行的 SiYuan API 通信，不会将数据发送到第三方服务器  
• 本技能提供完整的读写能力，操作你的 SiYuan 笔记，请确认在信任环境使用  

  
## **配置要求**  
• 思源笔记本地运行，默认地址 `http://127.0.0.1:6806`  
• API Token 在思源 → 设置 → 关于 中获取  
• Token 通过环境变量 `SIYUAN_API_TOKEN` 提供  

  
## **使用场景**  
• 创建 / 重命名 / 删除笔记本  
• Markdown 创建新文档  
• 插入 / 追加 / 更新 / 删除块  
• 上传资源文件  
• SQL 搜索笔记  
• 导出文档为 Markdown  
• 读写思源工作区文件  

  
## **API 参考**  
完整 API 文档分语言提供，需要详细端点规范时读取对应文件：  
• [references/api-zh.md](references/api-zh.md) - 中文  
• [references/api.md](references/api.md) - 英文  

  
## **常用示例**

### **列出所有笔记本**  
```javascript
fetch('http://127.0.0.1:6806/api/notebook/lsNotebooks', {
  method: 'POST',
  headers: {
    'Authorization': 'token ' + token,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({})
})
```

  
### **创建新文档**  
```javascript
fetch('http://127.0.0.1:6806/api/filetree/createDocWithMd', {
  method: 'POST',
  headers: {
    'Authorization': 'token ' + token,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    notebook: '笔记本ID',
    path: '/文档路径',
    markdown: '# 文档标题\n\n正文内容...'
  })
})
```

  
### **在文档末尾追加块**  
```javascript
fetch('http://127.0.0.1:6806/api/block/appendBlock', {
  method: 'POST',
  headers: {
    'Authorization': 'token ' + token,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    parentID: '父块ID',
    dataType: 'markdown',
    data: '追加的内容'
  })
})
```

  
### **SQL 搜索笔记**  
```javascript
fetch('http://127.0.0.1:6806/api/query/sql', {
  method: 'POST',
  headers: {
    'Authorization': 'token ' + token,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    stmt: 'SELECT id, content FROM blocks WHERE content LIKE "%关键词%" LIMIT 10'
  })
})
```

  
## **注意事项**  
• 重复调用 `createDocWithMd` 同一路径**不会**覆盖已有文档  
• 自定义块属性必须以 `custom-` 为前缀  
• 所有接口都使用 POST 方法，返回统一格式 `{code, msg, data}`  
• Authorization 头部格式：`token <你的token>` —— "token" 必须为小写  
