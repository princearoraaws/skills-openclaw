---
name: duhui-all-to-pdf
description: Use this skill when converting a single local document to PDF through 度慧文档转换 on Alibaba Cloud Market. Trigger for requests mentioning 度慧, 文档转PDF, doc to pdf, 文档转换, 格式转换, 文档格式转换, PDF转换 or when one local Office/WPS/OFD/image/text/web/any file must be converted to PDF through the async API.
---

# 度慧文档转PDF

## Overview

用这个 skill 处理“单个本地文件转单个 PDF”的度慧异步转换任务。
标准链路是：本地文件 -> 阿里云 OSS 临时上传 -> 把 OSS 对象直链放进 `input` -> `v2/convert_async` -> 轮询查询 -> 下载本地 PDF -> 删除 OSS 临时文件。

## When To Use

- 用户明确提到度慧、文档转 PDF、文档转换、格式转换、PDF 转换、压缩pdf，PDF水印
- 用户要把单个本地 `doc/docx/ppt/pptx/xls/xlsx/ofd/img/txt/html/...` 文件转成 PDF
- 任务需要走度慧的异步接口，而不是本地 LibreOffice 或其他转换器

## Do Not Use

- 直接 URL 输入
- Base64 输入
- 回调 URL

## Workflow

1. 只检查环境变量 `DUHUI_DOC_TO_PDF_APPCODE`。
   - 如果环境变量已经存在，直接运行转换脚本；不要要求用户重复输入 AppCode，也不要再推荐一次性 `DUHUI_DOC_TO_PDF_APPCODE='<appcode>' python3 ...` 这种临时注入方式。
   - 如果环境变量不存在，明确告诉用户先去阿里云市场商品页获取 AppCode：`https://market.aliyun.com/detail/cmapi00044564`。不要只笼统地说“请提供 AppCode”。
   - 如果用户已经在当前对话里提供了 AppCode，先持久化保存，再继续执行。默认命令是：

```bash
python3 scripts/persist_duhui_appcode.py '<appcode>'
```

   - 持久化完成后，按脚本输出里的 `source_command` 执行一次 `source`，或让用户开启新的 shell 会话；之后再运行转换脚本。
2. 默认优先运行脚本，不要手写 OSS 上传或 HTTP 调用逻辑：

```bash
python3 scripts/duhui_doc_to_pdf.py ./input.docx
```

3. 用户指定输出路径时，加 `--output`：

```bash
python3 scripts/duhui_doc_to_pdf.py ./input.docx --output ./output.pdf
```

4. 默认会覆盖同名输出 PDF；如果用户要保留旧结果，显式指定另一个 `--output` 路径。
5. 只有在文件后缀缺失、错误、或需要强制覆盖源类型时才传 `--type`。
6. 需要 vendor `v2` 可选参数时，用 `--extra-params '<json>'` 透传，例如：

```bash
python3 scripts/duhui_doc_to_pdf.py ./input.docx --extra-params '{"pagesize":2,"compress":1}'
```

7. 绝不在聊天、日志或最终答复里回显 AppCode 或脚本内置的 OSS 凭证；持久化时也只用占位符或用户已提供的值，不要把秘密再次展示出来。
8. 当需要确认支持格式、把用户的细化要求映射成更多 `v2` 参数、查看 vendor 参数细节、或排查 vendor 返回字段时，读取 [references/doc_to_pdf_ali.md](references/doc_to_pdf_ali.md)。

## Output Contract

- 进度信息只写到 `stderr`
- `stdout` 只输出一个 JSON
- 成功 JSON 包含：`status`, `token`, `output_path`, `pdf_url`, `page_count`, `filesize`, `source_object_key`
- 失败 JSON 包含：`status`, `stage`, `token`, `reason`

## Notes

- 脚本始终只处理一个本地输入文件
- 脚本只使用 Python 标准库，不依赖额外 Python 包
- OSS 对象名固定为 `up/<uuid4><原扩展名>`
- 上传后直接把 OSS 对象 URL 传给 vendor，不生成签名 URL
- 查询接口不带认证，固定每 2 秒轮询一次，最长等待 60 分钟
- 转换结束后会尝试删除 OSS 临时源文件；删除失败只记 warning，不覆盖主错误
