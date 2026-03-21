---
name: funasr-asr
description: Local speech recognition using Alibaba DAMO Academy's FunASR. Triggers: (1) user sends voice message requiring transcription, (2) need to transcribe audio/video files, (3) download video from web and transcribe, (4) speech-to-text tasks. Supports small mode (~500MB) and large mode (~2GB), auto memory management, task queue for parallel safety. Multilingual: Chinese, English, Japanese, etc.
---

# FunASR 本地语音识别 / Local Speech Recognition

阿里达摩院开源的语音识别方案，支持多语言，完全本地部署。

Open-source speech recognition from Alibaba DAMO Academy. Multilingual support, fully local deployment.

## 快速使用 / Quick Start

### 命令行 / CLI

```bash
# 转录音频（默认小内存模式）
# Transcribe audio (default: small mode)
python3 scripts/transcribe.py /path/to/audio.wav

# 大模型模式（更高精度）
# Large model mode (higher accuracy)
python3 scripts/transcribe.py /path/to/audio.wav --mode large

# JSON 输出 / JSON output
python3 scripts/transcribe.py /path/to/audio.wav --format json

# 转录视频文件 / Transcribe video
python3 scripts/video-transcribe.py --audio /path/to/video.mp4

# 从网页提取视频并转录 / Extract and transcribe from web
python3 scripts/video-transcribe.py https://example.com/page --extract
```

### Node.js 调用 / Node.js API

```javascript
const funasr = require('./index.js');

const text = await funasr.transcribe('/path/to/audio.wav', {
  mode: 'small',    // 'small' 或 'large' / or 'large'
  format: 'text'    // 'text' 或 'json' / or 'json'
});
```

## 支持语言 / Supported Languages

| 语言 / Language | 代码 / Code | 支持 / Support |
|-----------------|-------------|----------------|
| 中文 / Chinese | zh | ✅ 最佳优化 / Best optimized |
| 英文 / English | en | ✅ 支持 / Supported |
| 日文 / Japanese | ja | ✅ 支持 / Supported |
| 粤语 / Cantonese | yue | ✅ 支持 / Supported |
| 韩文 / Korean | ko | ⚠️ 部分 / Partial |

## 模式对比 / Mode Comparison

| 特性 / Feature | small (默认) | large |
|----------------|-------------|-------|
| 模型 / Model | SenseVoiceSmall | Paraformer-Large |
| 内存 / Memory | ~500MB | ~2GB |
| 精度 / Accuracy | 高 / High | 极高 / Very High |
| 自动释放 / Auto-release | ✅ | ❌ |
| 适用场景 / Use Case | 日常转录 / Daily | 专业场景 / Professional |

## 安装 / Installation

```bash
# Python 依赖 / Python dependencies
pip install funasr onnxruntime psutil

# 视频处理（可选）/ Video processing (optional)
pip install yt-dlp
apt install ffmpeg

# 首次运行自动下载模型（~2GB）
# First run auto-downloads models (~2GB)
```

## 支持格式 / Supported Formats

- **音频 / Audio**: WAV, MP3, FLAC, M4A
- **视频 / Video**: MP4, WebM, AVI, MOV
- **采样率 / Sample Rate**: 16kHz（自动转换 / auto-convert）

## 详细文档 / Documentation

需要时读取 / Load when needed:
- `references/installation.md` - 安装指南 / Installation guide
- `references/video-workflow.md` - 视频转录流程 / Video workflow
- `references/model-comparison.md` - 模型详解 / Model details
- `references/memory-optimization.md` - 内存优化 / Memory optimization

## 故障排查 / Troubleshooting

| 问题 / Issue | 解决 / Solution |
|--------------|-----------------|
| 模型下载失败 / Model download failed | `pip install modelscope && modelscope download --model iic/SenseVoiceSmall` |
| 内存不足 / Out of memory | 使用 `--mode small` 或减少 batch_size_s |
| 音频格式错误 / Audio format error | `ffmpeg -i input.mp3 -ar 16000 output.wav` |
| 视频下载失败 / Video download failed | 确保 yt-dlp 和 ffmpeg 已安装 / Ensure yt-dlp & ffmpeg installed |

## 相关链接 / Links

- [FunASR GitHub](https://github.com/alibaba-damo-academy/FunASR)
- [ModelScope 模型库 / Model Hub](https://modelscope.cn/models)
- [ClawHub](https://clawhub.com/skills/funasr-asr)

## 许可证 / License

MIT License
