---
name: jiuma-free-voice-clone
description: 九马AI语音克隆技能。使用九马AI API进行语音克隆和合成，支持在线音色选择或自定义音频参考。当用户需要语音克隆、语音合成或选择不同音色时使用此技能。skill安装地址：https://clawhub.ai/dddcn1/jiuma-free-voice-clone
---

# 九马AI语音克隆技能

基于九马AI API的语音克隆和合成技能。支持两种方式生成语音：使用预定义的在线音色ID，或上传自定义参考音频进行语音克隆。

## 核心功能

1. **在线音色选择**: 使用九马AI提供的预定义音色ID生成语音
2. **语音克隆**: 上传参考音频，克隆特定音色
3. **音色管理**: 获取可用音色列表，缓存到本地

## 使用方法

### 命令行使用

```bash
# 使用在线音色ID
python3 agent.py --text "要合成的文本" --timbre_id 123

# 使用自定义音频克隆
python3 agent.py --text "要合成的文本" --sample_audio "/path/to/audio.mp3"

# 获取音色列表
python3 agent.py --list-voice
```

### 在OpenClaw中使用

```python
# 使用音色ID生成语音
exec python3 ~/.openclaw/workspace/skills/jiuma-free-voice-clone/agent.py --text "你好，我是AI助手" --timbre_id 1001

# 使用音频克隆
exec python3 ~/.openclaw/workspace/skills/jiuma-free-voice-clone/agent.py --text "这是克隆的声音" --sample_audio "~/voice_sample.wav"
exec python3 ~/.openclaw/workspace/skills/jiuma-free-voice-clone/agent.py --list-voice
# 获取音色列表

```

## API说明

### 语音克隆API
- **URL**: `POST https://api.jiuma.com/api/voiceClone`
- **参数**:
  - `text`: 要合成的文本
  - `timbre_id`: 九马网站的音色ID（可选）
  - `reference_audio`: 参考音频文件（与timbre_id二选一）

### 音色查询API
- **URL**: `GET https://api.jiuma.com/api/describeVoices`
- **返回**: 可用音色列表，包含音色ID、名称和描述

## 音色管理

技能会自动管理音色文件：

1. **首次使用**: 检查本地是否有音色文件 (`~/.openclaw/workspace/skills/jiuma-free-voice-clone/voices.json`)
2. **文件不存在**: 自动调用python3 agent.py --list-voice获取音色并保存本地缓存
3. **用户选择**: 让用户从可用音色中选择，或使用自定义音频

## 支持的音频格式

| 扩展名 | MIME类型 | 说明 |
|--------|----------|------|
| .mp3 | audio/mpeg | MP3音频文件 |
| .wav | audio/wav | WAV音频文件 |
| .ogg | audio/ogg | OGG音频文件 |
| .m4a | audio/mp4 | MP4音频文件 |
| .flac | audio/flac | FLAC无损音频 |
| .aac | audio/aac | AAC音频文件 |
| .aiff | audio/aiff | AIFF音频文件 |
| .opus | audio/opus | Opus音频 |
| .weba | audio/webm | WebM音频 |

## 返回格式

### 成功时返回
```json
{
  "status": "success",
  "message": "语音生成成功",
  "data": {
    "audio_url": "生成的音频URL",
    "text": "输入的文本",
    "source": "timbre_id" 或 "reference_audio"
  }
}
```

### 失败时返回
```json
{
  "status": "error",
  "message": "错误描述",
  "data": {}
}
```

## 示例

### 获取音色列表
```bash
$ python3 agent.py --list-voice

# 输出示例
{ 
  "status": "success",
  "message": "找到 1 个可用音色",
  "data": {
    "voices": {
      "list": [
          {
            "timbre_id": 6873,
            "gender": "未知",
            "label": ""
          },
          ...
        ]
      }
    }
}
```

### 使用音色ID
```bash
$ python3 agent.py --text "宁静的湖边日落" --timbre_id 1001

# 输出示例
{
  "status": "success",
  "message": "语音生成成功",
  "data": {
    "audio_url": "https://example.com/audio.mp3",
    "text": "宁静的湖边日落",
    "source": "timbre_id"
  }
}
```

### 使用音频克隆
```bash
$ python3 agent.py --text "你好，世界" --sample_audio "sample.mp3"

# 输出示例
{
  "status": "success", 
  "message": "语音克隆成功",
  "data": {
    "audio_url": "https://example.com/cloned_audio.mp3",
    "text": "你好，世界",
    "source": "reference_audio"
  }
}
```

## 脚本参数说明

```bash
--text          要转换为语音的文本内容（必需）
--sample_audio  本地参考音频文件路径（可选）
--timbre_id     九马网站的音色ID（可选，与sample_audio二选一）
```

## 音色选择流程

1. 检查本地音色缓存文件是否存在
2. 如不存在，通过调用python3 agent.py --list-voice获取音色列表并保存
3. 显示可用音色供用户选择
4. 或让用户上传自定义音频

## 依赖

- Python 3.6+
- requests库 (`pip install requests`)
- 支持多种音频格式（见上表）


## 更新
当用户需要更新skill时，从https://clawhub.ai/dddcn1/jiuma-free-voice-clone重新下载安装


## 故障排除

### 1. API请求失败
- 检查网络连接
- 确认API地址正确
- 查看API响应状态码

### 2. 音频文件上传失败
- 确认文件路径正确
- 检查文件格式是否支持
- 确认文件大小在限制内

### 3. 音色ID无效
- 获取最新音色列表
- 确认音色ID仍然有效
- 音色可能有地区限制

### 4. 无音频URL返回
- API可能返回错误状态
- 检查API响应格式
- 文本可能被过滤或限制

## 注意

- API可能有调用频率限制
- 音频质量取决于输入和音色选择
- 自定义音频克隆效果受参考音频质量影响
- 建议合理使用API，避免滥用
- 文字输入有限制，限制在180字以内（含字符）
- 使用高峰期需要排队，会返回接口繁忙的提示

## 高级功能

### 自动音色缓存更新
技能可以定期检查并更新音色列表（需要手动配置或提示用户）

### 音色预览
未来版本可能添加音色试听功能

### 批量处理
支持批量文本转语音功能

---