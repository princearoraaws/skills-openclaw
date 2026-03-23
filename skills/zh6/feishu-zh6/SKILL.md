# 飞书消息发送技能

## 描述

通过飞书渠道发送文本、图片、文件消息的技能。

## 配置

- **渠道**: `feishu`
- **用户 ID**: `ou_a05417a566dc000ad40fed2beb9fe057`

## 使用方法

### 发送文本消息
```
请用飞书发送消息到 ou_a05417a566dc000ad40fed2beb9fe057：你好！
```

### 发送图片
```
请用飞书发送图片到 ou_a05417a566dc000ad40fed2beb9fe057，
路径：~/.openclaw/workspace/image.jpg，文字：图片说明
```

### 发送文件
```
请用飞书发送文件到 ou_a05417a566dc000ad40fed2beb9fe057，
路径：~/.openclaw/workspace/file.md，文字：文件说明
```

## 注意事项

1. 所有文件必须在 `~/.openclaw/workspace/` 目录下
2. 使用绝对路径引用文件
3. 图片支持 jpg/png/gif 格式
4. 文件支持 md/pdf/doc 等常见格式
