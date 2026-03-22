# SiYuan API Reference

Based on https://github.com/siyuan-note/siyuan/blob/master/API.md

## Base Specification

- Endpoint: `http://127.0.0.1:6806`
- All requests are POST methods
- Parameters are JSON in request body, `Content-Type: application/json`
- Response format:
```json
{
  "code": 0,
  "msg": "",
  "data": {}
}
```
  - `code`: non-zero for exceptions
  - `msg`: error message, empty on success
  - `data`: response data, varies by endpoint

## Authentication

Get API token in SiYuan → Settings → About. Send token in request header:
```
Authorization: Token {{token}}
```

## API Endpoints

### Notebooks

#### List notebooks
`GET /api/notebook/lsNotebooks`

No parameters.

Returns:
```json
{
  "code": 0,
  "msg": "",
  "data": {
    "notebooks": [
      {
        "id": "20210817205410-2kvfpfn",
        "name": "Test Notebook",
        "icon": "1f41b",
        "sort": 0,
        "closed": false
      }
    ]
  }
}
```

#### Open a notebook
`POST /api/notebook/openNotebook`

Parameters:
```json
{
  "notebook": "20210831090520-7dvbdv0"
}
```

#### Close a notebook
`POST /api/notebook/closeNotebook`

Parameters:
```json
{
  "notebook": "20210831090520-7dvbdv0"
}
```

#### Rename a notebook
`POST /api/notebook/renameNotebook`

Parameters:
```json
{
  "notebook": "20210831090520-7dvbdv0",
  "name": "New name"
}
```

#### Create a notebook
`POST /api/notebook/createNotebook`

Parameters:
```json
{
  "name": "Notebook name"
}
```

Returns:
```json
{
  "code": 0,
  "msg": "",
  "data": {
    "notebook": {
      "id": "20220126215949-r1wvoch",
      "name": "Notebook name",
      "icon": "",
      "sort": 0,
      "closed": false
    }
  }
}
```

#### Remove a notebook
`POST /api/notebook/removeNotebook`

Parameters:
```json
{
  "notebook": "20210831090520-7dvbdv0"
}
```

#### Get notebook configuration
`POST /api/notebook/getNotebookConf`

Parameters:
```json
{
  "notebook": "20210817205410-2kvfpfn"
}
```

#### Save notebook configuration
`POST /api/notebook/setNotebookConf`

Parameters:
```json
{
  "notebook": "20210817205410-2kvfpfn",
  "conf": {
    "name": "Test Notebook",
    "closed": false,
    "refCreateSavePath": "",
    "createDocNameTemplate": "",
    "dailyNoteSavePath": "/daily note/{{now | date \"2006/01\"}}/{{now | date \"2006-01-02\"}}",
    "dailyNoteTemplatePath": ""
  }
}
```

### Documents

#### Create a document with Markdown
`POST /api/filetree/createDocWithMd`

Parameters:
```json
{
  "notebook": "20210817205410-2kvfpfn",
  "path": "/foo/bar",
  "markdown": ""
}
```
- `path`: Must start with `/`, uses `/` as separator
- Repeated calls with same path do **not** overwrite existing documents

Returns: Created document ID in `data`.

#### Rename a document
`POST /api/filetree/renameDoc`

Parameters:
```json
{
  "notebook": "20210831090520-7dvbdv0",
  "path": "/20210902210113-0avi12f.sy",
  "title": "New document title"
}
```

#### Rename a document by ID
`POST /api/filetree/renameDocByID`

Parameters:
```json
{
  "id": "20210902210113-0avi12f",
  "title": "New document title"
}
```

#### Remove a document
`POST /api/filetree/removeDoc`

Parameters:
```json
{
  "notebook": "20210831090520-7dvbdv0",
  "path": "/20210902210113-0avi12f.sy"
}
```

#### Remove a document by ID
`POST /api/filetree/removeDocByID`

Parameters:
```json
{
  "id": "20210902210113-0avi12f"
}
```

#### Move documents
`POST /api/filetree/moveDocs`

Parameters:
```json
{
  "fromPaths": ["/20210917220056-yxtyl7i.sy"],
  "toNotebook": "20210817205410-2kvfpfn",
  "toPath": "/"
}
```

#### Move documents by ID
`POST /api/filetree/moveDocsByID`

Parameters:
```json
{
  "fromIDs": ["20210917220056-yxtyl7i"],
  "toID": "20210817205410-2kvfpfn"
}
```

#### Get human-readable path by path
`POST /api/filetree/getHPathByPath`

Parameters:
```json
{
  "notebook": "20210831090520-7dvbdv0",
  "path": "/20210917220500-sz588nq/20210917220056-yxtyl7i.sy"
}
```

Returns: Human-readable path in `data`.

#### Get human-readable path by ID
`POST /api/filetree/getHPathByID`

Parameters:
```json
{
  "id": "20210917220056-yxtyl7i"
}
```

Returns: Human-readable path in `data`.

#### Get storage path by ID
`POST /api/filetree/getPathByID`

Parameters:
```json
{
  "id": "20210808180320-fqgskfj"
}
```

Returns:
```json
{
  "code": 0,
  "msg": "",
  "data": {
    "notebook": "20210808180117-czj9bvb",
    "path": "/20200812220555-lj3enxa/20210808180320-fqgskfj.sy"
  }
}
```

#### Get IDs by human-readable path
`POST /api/filetree/getIDsByHPath`

Parameters:
```json
{
  "path": "/foo/bar",
  "notebook": "20210808180117-czj9bvb"
}
```

Returns: Array of IDs in `data`.

### Assets

#### Upload assets
`POST /api/asset/upload` (multipart form)

Parameters:
- `assetsDirPath`: Storage folder, root is data folder:
  - `"/assets/"`: `workspace/data/assets/` (recommended)
  - `"/assets/sub/"`: `workspace/data/assets/sub/`
- `file[]`: List of files to upload

Returns:
```json
{
  "code": 0,
  "msg": "",
  "data": {
    "errFiles": [""],
    "succMap": {
      "foo.png": "assets/foo-20210719092549-9j5y79r.png"
    }
  }
}
```

### Blocks

#### Insert blocks
`POST /api/block/insertBlock`

Parameters:
```json
{
  "dataType": "markdown",
  "data": "foo**bar**baz",
  "nextID": "",
  "previousID": "20211229114650-vrek5x6",
  "parentID": ""
}
```
- `dataType`: `markdown` or `dom`
- At least one of `nextID`, `previousID`, `parentID` is required (priority: nextID > previousID > parentID)

#### Prepend blocks
`POST /api/block/prependBlock`

Parameters:
```json
{
  "dataType": "markdown",
  "data": "foo**bar**baz",
  "parentID": "20220107173950-7f9m1nb"
}
```

#### Append blocks
`POST /api/block/appendBlock`

Parameters:
```json
{
  "dataType": "markdown",
  "data": "foo**bar**baz",
  "parentID": "20220107173950-7f9m1nb"
}
```

#### Update a block
`POST /api/block/updateBlock`

Parameters:
```json
{
  "dataType": "markdown",
  "data": "foobarbaz",
  "id": "20211230161520-querkps"
}
```

#### Delete a block
`POST /api/block/deleteBlock`

Parameters:
```json
{
  "id": "20211230161520-querkps"
}
```

#### Move a block
`POST /api/block/moveBlock`

Parameters:
```json
{
  "id": "20230406180530-3o1rqkc",
  "previousID": "20230406152734-if5kyx6",
  "parentID": "20230404183855-woe52ko"
}
```

#### Fold a block
`POST /api/block/foldBlock`

Parameters:
```json
{
  "id": "20231224160424-2f5680o"
}
```

#### Unfold a block
`POST /api/block/unfoldBlock`

Parameters:
```json
{
  "id": "20231224160424-2f5680o"
}
```

#### Get block kramdown
`POST /api/block/getBlockKramdown`

Parameters:
```json
{
  "id": "20201225220954-dlgzk1o"
}
```

Returns:
```json
{
  "code": 0,
  "msg": "",
  "data": {
    "id": "20201225220954-dlgzk1o",
    "kramdown": "* {...}Create a new notebook..."
  }
}
```

#### Get child blocks
`POST /api/block/getChildBlocks`

Parameters:
```json
{
  "id": "20230506212712-vt9ajwj"
}
```

Returns: Array of child blocks in `data`.

#### Transfer block ref
`POST /api/block/transferBlockRef`

Parameters:
```json
{
  "fromID": "20230612160235-mv6rrh1",
  "toID": "20230613093045-uwcomng",
  "refIDs": ["20230613092230-cpyimmd"]
}
```

### Attributes

#### Set block attributes
`POST /api/attr/setBlockAttrs`

Parameters:
```json
{
  "id": "20210912214605-uhi5gco",
  "attrs": {
    "custom-attr1": "line1\nline2"
  }
}
```
- Custom attributes must be prefixed with `custom-`

#### Get block attributes
`POST /api/attr/getBlockAttrs`

Parameters:
```json
{
  "id": "20210912214605-uhi5gco"
}
```

Returns: Attributes in `data`.

### SQL

#### Execute SQL query
`POST /api/query/sql`

Parameters:
```json
{
  "stmt": "SELECT * FROM blocks WHERE content LIKE '%content%' LIMIT 7"
}
```

Returns: Query results in `data`.

Note: In publish mode, this endpoint is prohibited unless all read permissions are public.

#### Flush transaction
`POST /api/sqlite/flushTransaction`

No parameters.

### Templates

#### Render a template
`POST /api/template/render`

Parameters:
```json
{
  "id": "20220724223548-j6g0o87",
  "path": "/absolute/path/to/template.md"
}
```

Returns: Rendered content in `data.content`.

#### Render Sprig template
`POST /api/template/renderSprig`

Parameters:
```json
{
  "template": "/daily note/{{now | date \"2006/01\"}}/{{now | date \"2006-01-02\"}}"
}
```

Returns: Rendered path in `data`.

### File

#### Get file
`POST /api/file/getFile`

Parameters:
```json
{
  "path": "/data/20210808180117-6v0mkxr/20200923234011-ieuun1p.sy"
}
```
- `path`: File path under workspace

Returns: File content as raw response.

#### Put file
`POST /api/file/putFile` (multipart form)

Parameters:
- `path`: File path under workspace
- `isDir`: Whether to create a folder only
- `modTime`: Last access/modification time (Unix time)
- `file`: Uploaded file

#### Remove file
`POST /api/file/removeFile`

Parameters:
```json
{
  "path": "/data/20210808180117-6v0mkxr/20200923234011-ieuun1p.sy"
}
```

#### Rename file
`POST /api/file/renameFile`

Parameters:
```json
{
  "path": "/data/assets/image-20230523085812-k3o9t32.png",
  "newPath": "/data/assets/test-20230523085812-k3o9t32.png"
}
```

#### List files
`POST /api/file/readDir`

Parameters:
```json
{
  "path": "/data/20210808180117-6v0mkxr"
}
```

Returns: Directory listing in `data`.

### Export

#### Export Markdown content
`POST /api/export/exportMdContent`

Parameters:
```json
{
  "id": "doc-block-id"
}
```

Returns:
```json
{
  "code": 0,
  "msg": "",
  "data": {
    "hPath": "/document/path",
    "content": "## Markdown content here..."
  }
}
```

#### Export files and folders
`POST /api/export/exportResources`

Parameters:
```json
{
  "paths": ["/conf/appearance/boot", "/conf/appearance/langs"],
  "name": "