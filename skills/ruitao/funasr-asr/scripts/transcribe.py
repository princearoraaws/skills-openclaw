#!/usr/bin/env python3
"""
FunASR 语音转录脚本（优化版）
- 支持小内存模式
- 任务队列防止并行运行
- 自动内存管理
"""

import sys
import os
import json
import argparse
import fcntl
import psutil
from pathlib import Path
from datetime import datetime

try:
    from funasr import AutoModel
except ImportError:
    print("❌ 未安装 FunASR，请运行: pip install funasr onnxruntime")
    sys.exit(1)

# ==================== 配置 ====================
# 锁文件位置
LOCK_DIR = Path("/tmp/funasr_locks")
LOCK_DIR.mkdir(exist_ok=True)

# 模型配置
MODEL_CONFIG = {
    "small": {
        "model": "iic/SenseVoiceSmall",
        "vad_model": "iic/speech_fsmn_vad_zh-cn-16k-common-pytorch",
        "punc_model": "iic/punc_ct-transformer_zh-cn-common-vocab272727-pytorch",
        "memory_mb": 500,
        "batch_size_s": 300,
    },
    "large": {
        "model": "iic/speech_paraformer-large_asr_nat-zh-cn-16k-common-vocab8404-pytorch",
        "vad_model": "iic/speech_fsmn_vad_zh-cn-16k-common-pytorch",
        "punc_model": "iic/punc_ct-transformer_zh-cn-common-vocab272727-pytorch",
        "memory_mb": 2000,
        "batch_size_s": 300,
    }
}

# ==================== 工具函数 ====================
def get_memory_usage():
    """获取当前进程内存使用"""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024  # MB

def check_available_memory(required_mb):
    """检查是否有足够可用内存"""
    available = psutil.virtual_memory().available / 1024 / 1024
    return available >= required_mb

def acquire_lock(audio_path, timeout=3600):
    """
    获取任务锁，防止同一音频被并行处理
    返回: (lock_file, acquired)
    """
    audio_name = Path(audio_path).stem
    lock_file = LOCK_DIR / f"{audio_name}.lock"

    try:
        fd = os.open(lock_file, os.O_CREAT | os.O_WRONLY)
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return fd, True
    except IOError:
        # 锁已被占用
        return None, False

def release_lock(lock_fd):
    """释放任务锁"""
    if lock_fd:
        fcntl.flock(lock_fd, fcntl.LOCK_UN)
        os.close(lock_fd)

# ==================== 模型管理 ====================
class ModelManager:
    """模型管理器 - 支持内存优化"""

    def __init__(self, mode="small"):
        self.mode = mode
        self.config = MODEL_CONFIG[mode]
        self.model = None
        self.loaded = False

    def load_model(self):
        """加载模型（小内存优化）"""
        if self.loaded:
            return self.model

        required_memory = self.config["memory_mb"]

        # 小内存模式：检查可用内存
        if self.mode == "small":
            print(f"🔧 小内存模式: 需要约 {required_memory}MB 内存")

            if not check_available_memory(required_memory):
                print(f"❌ 内存不足，需要至少 {required_memory}MB 可用内存")
                print("💡 建议：")
                print("   1. 关闭其他程序")
                print("   2. 等待其他转录任务完成")
                print("   3. 增加系统交换空间")
                sys.exit(1)

        print("📦 正在加载 FunASR 模型...")
        print(f"   模型: {self.config['model'].split('/')[-1]}")
        print("⚠️  首次运行会自动下载模型，请耐心等待...")

        try:
            self.model = AutoModel(
                model=self.config["model"],
                vad_model=self.config["vad_model"],
                punc_model=self.config["punc_model"],
                disable_update=True,  # 禁用更新检查
                disable_log=False,    # 启用日志
            )
            self.loaded = True
            print("✅ 模型加载完成")

            # 显示实际内存使用
            memory_used = get_memory_usage()
            print(f"💾 当前内存使用: {memory_used:.1f} MB")

            return self.model

        except Exception as e:
            print(f"❌ 模型加载失败: {e}")
            sys.exit(1)

    def unload_model(self):
        """卸载模型释放内存"""
        if self.model:
            del self.model
            self.model = None
            self.loaded = False
            print("♻️  模型已卸载，内存已释放")

# ==================== 转录函数 ====================
def transcribe_audio(model_manager, audio_path, output_format="text"):
    """转录音频文件"""
    if not os.path.exists(audio_path):
        print(f"❌ 音频文件不存在: {audio_path}")
        return None

    print(f"🎙️  正在转录: {audio_path}")
    start_time = datetime.now()

    try:
        # 确保模型已加载
        model = model_manager.load_model()

        # 转录
        result = model.generate(
            input=audio_path,
            batch_size_s=model_manager.config["batch_size_s"]
        )

        if not result or not result[0]:
            print("❌ 转录失败: 无结果")
            return None

        # 提取文本
        text = result[0]["text"]

        # 计算耗时
        elapsed = (datetime.now() - start_time).total_seconds()

        print(f"✅ 转录完成！耗时: {elapsed:.1f}秒")

        if output_format == "json":
            output = {
                "text": text,
                "timestamp": result[0].get("timestamp", []),
                "duration": result[0].get("duration", 0),
                "elapsed_seconds": elapsed,
                "memory_mb": get_memory_usage()
            }
            print(json.dumps(output, ensure_ascii=False, indent=2))
        else:
            print(f"\n{'='*60}")
            print("转录结果：")
            print(f"{'='*60}")
            print(text)
            print(f"{'='*60}\n")

        return text

    except Exception as e:
        print(f"❌ 转录失败: {e}")
        import traceback
        traceback.print_exc()
        return None

# ==================== 主函数 ====================
def main():
    parser = argparse.ArgumentParser(
        description="FunASR 语音转录（优化版）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 小内存模式（默认）
  %(prog)s audio.wav

  # 大模型模式
  %(prog)s audio.wav --mode large

  # JSON 输出
  %(prog)s audio.wav --format json

  # 显示详细信息
  %(prog)s audio.wav --verbose
        """
    )

    parser.add_argument("audio", nargs="?", help="音频文件路径")
    parser.add_argument("--mode", "-m", default="small",
                       choices=["small", "large"],
                       help="模型模式: small(500MB) / large(2GB)")
    parser.add_argument("--format", "-f", default="text",
                       choices=["text", "json"],
                       help="输出格式")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="显示详细信息")
    parser.add_argument("--live", "-l", action="store_true",
                       help="实时转录模式（未实现）")
    parser.add_argument("--no-wait", action="store_true",
                       help="不等待其他任务完成，立即退出")

    args = parser.parse_args()

    # 显示版本信息
    if args.verbose:
        print(f"🔧 FunASR 转录脚本 (优化版)")
        print(f"   模式: {args.mode}")
        print(f"   可用内存: {psutil.virtual_memory().available / 1024 / 1024:.0f} MB")
        print()

    # 实时模式（未实现）
    if args.live:
        print("❌ 实时转录模式暂未实现")
        print("💡 请使用文件模式")
        return

    # 文件模式
    if not args.audio:
        parser.print_help()
        return

    # 任务锁：防止并行处理同一文件
    lock_fd, acquired = acquire_lock(args.audio)

    if not acquired:
        print(f"⏳ 该音频正在被其他任务处理...")
        print(f"   文件: {args.audio}")

        if args.no_wait:
            print("   使用 --no-wait 跳过等待")
            sys.exit(1)
        else:
            print("   等待中... (按 Ctrl+C 退出)")

            # 等待锁释放
            lock_fd, acquired = acquire_lock(args.audio, timeout=None)
            if not acquired:
                print("❌ 获取锁失败")
                sys.exit(1)

    try:
        # 创建模型管理器
        model_manager = ModelManager(mode=args.mode)

        # 执行转录
        result = transcribe_audio(model_manager, args.audio, args.format)

        # 小内存模式：转录完成后卸载模型
        if args.mode == "small":
            model_manager.unload_model()

        # 返回状态
        sys.exit(0 if result else 1)

    finally:
        # 释放锁
        release_lock(lock_fd)

if __name__ == "__main__":
    main()
