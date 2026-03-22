# SiYuan API 中文参考

本文档整理自 SiYuan 官方中文 API 文档：https://github.com/siyuan-note/siyuan/blob/master/API_zh_CN.md

## 规范

- 端点：http://127.0.0.1:6806
- 均是 POST 方法
- 需要带参的接口，参数为 JSON 字符串，放置到 body 里，标头 Content-Type 为 application/json
- 返回值
```json
{
 "code": 0,
 "msg": "",
 "data": {}
}
```
  - `code`：非 0 为异常情况
  - `msg`：正常情况下是空字符串，异常情况下会返回错误文案
  - `data`：可能为 `{}`、`[]` 或者 `NULL`，根据不同接口而不同

## 鉴权

在 设置 - 关于 里查看 API token，请求标头：`Authorization: token xxx`

## 笔记本

### 列出笔记本
`POST /api/notebook/lsNotebooks`

不带参。

返回值：
```json
{
 "code": 0,
 "msg": "",
 "data": {
  "notebooks": [
   {
    "id": "20210817205410-2kvfpfn",
    "name": "测试笔记本",
    "icon": "1f41b",
    "sort": 0,
    "closed": false
   },
   {
    "id": "20210808180117-czj9bvb",
    "name": "思源笔记用户指南",
    "icon": "1f4d4",
    "sort": 1,
    "closed": false
   }
  ]
 }
}
```

### 打开笔记本
`POST /api/notebook/openNotebook`

参数：
```json
{
 "notebook": "20210831090520-7dvbdv0"
}
```

### 关闭笔记本
`POST /api/notebook/closeNotebook`

参数：
```json
{
 "notebook": "20210831090520-7dvbdv0"
}
```

### 重命名笔记本
`POST /api/notebook/renameNotebook`

参数：
```json
{
 "notebook": "20210831090520-7dvbdv0",
 "name": "笔记本的新名称"
}
```

### 创建笔记本
`POST /api/notebook/createNotebook`

参数：
```json
{
 "name": "笔记本的名称"
}
```

### 删除笔记本
`POST /api/notebook/removeNotebook`

参数：
```json
{
 "notebook": "20210831090520-7dvbdv0"
}
```

### 获取笔记本配置
`POST /api/notebook/getNotebookConf`

参数：
```json
{
 "notebook": "20210817205410-2kvfpfn"
}
```

### 保存笔记本配置
`POST /api/notebook/setNotebookConf`

参数：
```json
{
 "notebook": "20210817205410-2kvfpfn",
 "conf": {
  "name": "测试笔记本",
  "closed": false,
  "refCreateSavePath": "",
  "createDocNameTemplate": "",
  "dailyNoteSavePath": "/daily note/{{now | date \"2006/01\"}}/{{now | date \"2006-01-02\"}}",
  "dailyNoteTemplatePath": ""
 }
}
```

## 文档

### 通过 Markdown 创建文档
`POST /api/filetree/createDocWithMd`

参数：
```json
{
 "notebook": "20210817205410-2kvfpfn",
 "path": "/foo/bar",
 "markdown": ""
}
```
- `notebook`：笔记本 ID
- `path`：文档路径，需要以 `/` 开头，中间使用 `/` 分隔层级（对应数据库 hpath 字段）
- `markdown`：GFM Markdown 内容

返回：创建好的文档 ID 在 `data`。

**注意**：如果使用同一个 path 重复调用该接口，不会覆盖已有文档。

### 重命名文档
`POST /api/filetree/renameDoc`

参数：
```json
{
 "notebook": "20210831090520-7dvbdv0",
 "path": "/20210902210113-0avi12f.sy",
 "title": "文档新标题"
}
```

### 重命名文档（通过 ID）
`POST /api/filetree/renameDocByID`

参数：
```json
{
 "id": "20210902210113-0avi12f",
 "title": "文档新标题"
}
```

### 删除文档
`POST /api/filetree/removeDoc`

参数：
```json
{
 "notebook": "20210831090520-7dvbdv0",
 "path": "/20210902210113-0avi12f.sy"
}
```

### 删除文档（通过 ID）
`POST /api/filetree/removeDocByID`

参数：
```json
{
 "id": "20210902210113-0avi12f"
}
```

### 移动文档
`POST /api/filetree/moveDocs`

参数：
```json
{
 "fromPaths": ["/20210917220056-yxtyl7i.sy"],
 "toNotebook": "20210817205410-2kvfpfn",
 "toPath": "/"
}
```

### 移动文档（通过 ID）
`POST /api/filetree/moveDocsByID`

参数：
```json
{
 "fromIDs": ["20210917220056-yxtyl7i"],
 "toID": "20210817205410-2kvfpfn"
}
```

### 根据路径获取人类可读路径
`POST /api/filetree/getHPathByPath`

参数：
```json
{
 "notebook": "20210831090520-7dvbdv0",
 "path": "/20210917220500-sz588nq/20210917220056-yxtyl7i.sy"
}
```

### 根据 ID 获取人类可读路径
`POST /api/filetree/getHPathByID`

参数：
```json
{
 "id": "20210917220056-yxtyl7i"
}
```

### 根据 ID 获取存储路径
`POST /api/filetree/getPathByID`

参数：
```json
{
 "id": "20210808180320-fqgskfj"
}
```

### 根据人类可读路径获取 IDs
`POST /api/filetree/getIDsByHPath`

参数：
```json
{
 "path": "/foo/bar",
 "notebook": "20210808180117-czj9bvb"
}
```

## 资源文件

### 上传资源文件
`POST /api/asset/upload`，参数为 HTTP Multipart 表单

- `assetsDirPath`：资源文件存放的文件夹路径，以 data 文件夹作为根路径，例如：
  - `"/assets/"`：工作空间/data/assets/ 文件夹（推荐）
  - `"/assets/sub/"`：工作空间/data/assets/sub/ 文件夹
- `file[]`：上传的文件列表

## 块

### 插入块
`POST /api/block/insertBlock`

参数：
```json
{
 "dataType": "markdown",
 "data": "foo**bar**{: style=\"color: var(--b3-font-color8);\"}baz",
 "nextID": "",
 "previousID": "20211229114650-vrek5x6",
 "parentID": ""
}
```
- `dataType`：待插入数据类型，值可选择 `markdown` 或者 `dom`
- 至少一个位置 ID 必须有值：`nextID`/`previousID`/`parentID`，优先级：nextID > previousID > parentID

### 插入前置子块
`POST /api/block/prependBlock`

参数：
```json
{
 "data": "foo**bar**{: style=\"color: var(--b3-font-color8);\"}baz",
 "dataType": "markdown",
 "parentID": "20220107173950-7f9m1nb"
}
```

### 插入后置子块
`POST /api/block/appendBlock`

参数：
```json
{
 "data": "foo**bar**{: style=\"color: var(--b3-font-color8);\"}baz",
 "dataType": "markdown",
 "parentID": "20220107173950-7f9m1nb"
}
```

### 更新块
`POST /api/block/updateBlock`

参数：
```json
{
 "dataType": "markdown",
 "data": "foobarbaz",
 "id": "20211230161520-querkps"
}
```

### 删除块
`POST /api/block/deleteBlock`

参数：
```json
{
 "id": "20211230161520-querkps"
}
```

### 移动块
`POST /api/block/moveBlock`

参数：
```json
{
 "id": "20230406180530-3o1rqkc",
 "previousID": "20230406152734-if5kyx6",
 "parentID": "20230404183855-woe52ko"
}
```

### 折叠块
`POST /api/block/foldBlock`

参数：
```json
{
 "id": "20231224160424-2f5680o"
}
```

### 展开块
`POST /api/block/unfoldBlock`

参数：
```json
{
 "id": "20231224160424-2f5680o"
}
```

### 获取块 kramdown 源码
`POST /api/block/getBlockKramdown`

参数：
```json
{
 "id": "20201225220955-l154bn4"
}
```

### 获取子块
`POST /api/block/getChildBlocks`

参数：
```json
{
 "id": "20230506212712-vt9ajwj"
}
```

### 转移块引用
`POST /api/block/transferBlockRef`

参数：
```json
{
 "fromID": "20230612160235-mv6rrh1",
 "toID": "20230613093045-uwcomng",
 "refIDs": ["20230613092230-cpyimmd"]
}
```

## 属性

### 设置块属性
`POST /api/attr/setBlockAttrs`

参数：
```json
{
 "id": "20210912214605-uhi5gco",
 "attrs": {
  "custom-attr1": "line1\nline2"
 }
}
```
- 自定义属性必须以 `custom-` 作为前缀

### 获取块属性
`POST /api/attr/getBlockAttrs`

参数：
```json
{
 "id": "20210912214605-uhi5gco"
}
```

## SQL

### 执行 SQL 查询
`POST /api/query/sql`

参数：
```json
{
 "stmt": "SELECT * FROM blocks WHERE content LIKE '%content%' LIMIT 7"
}
```
注意：发布模式下除非公开所有文档读写权限，否则会禁止访问该接口。

### 提交事务
`POST /api/sqlite/flushTransaction`

不带参。

## 模板

### 渲染模板
`POST /api/template/render`

参数：
```json
{
 "id": "20220724223548-j6g0o87",
 "path": "/absolute/path/to/template.md"
}
```

### 渲染 Sprig
`POST /api/template/renderSprig`

参数：
```json
{
 "template": "/daily note/{{now | date \"2006/01\"}}/{{now | date \"2006-01-02\"}}"
}
```

## 文件

### 获取文件
`POST /api/file/getFile`

参数：
```json
{
 "path": "/data/20210808180117-6v0mkxr/20200923234011-ieuun1p.sy"
}
```
- `path`：工作空间路径下的文件路径

### 写入文件
`POST /api/file/putFile`，参数为 HTTP Multipart 表单

- `path`：工作空间路径下的文件路径
- `isDir`：是否为创建文件夹，为 true 时仅创建文件夹，忽略 file
- `modTime`：最近访问和修改时间，Unix time
- `file`：上传的文件

### 删除文件
`POST /api/file/removeFile`

参数：
```json
{
 "path": "/data/20210808180117-6v0mkxr/20200923234011-ieuun1p.sy"
}
```

### 重命名文件
`POST /api/file/renameFile`

参数：
```json
{
 "path": "/data/assets/image-20230523085812-k3o9t32.png",
 "newPath": "/data/assets/test-20230523085812-k3o9t32.png"
}
```

### 列出文件
`POST /api/file/readDir`

参数：
```json
{
 "path": "/data/20210808180117-6v0mkxr"
}
```

## 导出

### 导出 Markdown 文本
`POST /api/export/exportMdContent`

参数：
```json
{
 "id": "doc-block-id"
}
```

### 导出文件与目录
`POST /api/export/exportResources`

参数：
```json
{
 "paths": ["/conf/appearance/boot", "/conf/appearance/langs"],
 "name": "zip-file-name"
}
```

## 转换

### Pandoc
`POST /api/convert/pandoc`

- 工作目录：执行调用 pandoc 命令时工作目录会被设置在 `工作空间/temp/convert/pandoc/${dir}` 下
- 可先通过 API [写入文件](#写入文件) 将待转换文件写入该目录
- 然后再调用该 API 进行转换，转换后的文件也会被写入该目录
- 最后调用 API [获取文件](#获取文件) 获取转换后的文件内容

参数：
```json
{
 "dir": "test",
 "args": [
  "--to", "markdown_strict-raw_html",
  "foo.epub",
  "-o", "foo.md"
 ]
}
```

## 通知

### 推送消息
`POST /api/notification/pushMsg`

参数：
```json
{
 "msg": "test",
 "timeout": 7000
}
```
- `timeout`：消息持续显示时间，单位为毫秒，可以不传入，默认为 7000 毫秒

### 推送报错消息
`POST /api/notification/pushErrMsg`

参数：
```json
{
 "msg": "test",
 "timeout": 7000
}
```

## 网络