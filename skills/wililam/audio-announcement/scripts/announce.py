#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Silent Audio Player v5.0 - MP3 + PowerShell WMP COM
最简单稳定的方案：edge-tts 生成 MP3，PowerShell WMP COM 静默播放
"""

import os
import sys
import subprocess
import tempfile
import hashlib
import platform
import shutil
import time
import threading

# 配置
CACHE_DIR = os.path.expanduser("~/.cache/audio-announcement")
TEMP_DIR = os.path.join(tempfile.gettempdir(), "audio-announcement")
MAX_RETRIES = 3
KEEP_TEMP_FILES = False  # 播放后自动删除临时文件
VOLUME = 100  # 音量：0-100（默认 100%）
CLEANUP_DELAY = 60  # 播放后延迟删除（秒），默认 60 秒

def ensure_dirs():
    os.makedirs(CACHE_DIR, exist_ok=True)
    os.makedirs(TEMP_DIR, exist_ok=True)

def get_cache_key(text, voice):
    key_str = f"{text}-{voice}"
    return hashlib.md5(key_str.encode('utf-8')).hexdigest()

def generate_audio(text, voice, output_file):
    """生成 MP3 语音"""
    print(f"[INFO] 生成语音: {text[:30]}...", file=sys.stderr)
    
    cache_key = get_cache_key(text, voice)
    cached_file = os.path.join(CACHE_DIR, f"{cache_key}.mp3")
    
    if os.path.exists(cached_file):
        print(f"[INFO] 使用缓存 MP3", file=sys.stderr)
        shutil.copy2(cached_file, output_file)
        return True
    
    for i in range(1, MAX_RETRIES + 1):
        try:
            print(f"[INFO] 第 {i} 次生成 MP3...", file=sys.stderr)
            result = subprocess.run(
                ["edge-tts", "--text", text, "--voice", voice, "--write-media", output_file],
                capture_output=True,
                timeout=30,
                text=True
            )
            if result.returncode == 0 and os.path.exists(output_file) and os.path.getsize(output_file) > 0:
                shutil.copy2(output_file, cached_file)
                print(f"[INFO] 生成成功 (大小: {os.path.getsize(output_file)} 字节)", file=sys.stderr)
                return True
            else:
                print(f"[WARN] 生成失败或文件为空", file=sys.stderr)
        except Exception as e:
            print(f"[WARN] 第 {i} 次异常: {e}", file=sys.stderr)
        
        if i < MAX_RETRIES:
            time.sleep(1)
    
    print(f"[ERROR] 语音生成失败", file=sys.stderr)
    return False

def play_silent_mp3(audio_file):
    """使用 PowerShell + WMP COM 静默播放 MP3"""
    try:
        # WMP 音量范围 0.0-1.0，将 0-100 转换为 0.0-1.0
        wmp_volume = VOLUME / 100.0
        
        ps_script = f'''
$ErrorActionPreference = "Stop"
try {{
    $player = New-Object -ComObject WMPlayer.OCX
    $player.settings.volume = {wmp_volume}
    $player.currentMedia = $player.newMedia('{audio_file}')
    $player.controls.play()
    Start-Sleep -Milliseconds 500  # 等待播放开始
    # 不等待，WMP 继续在后台播放
    Write-Host "播放已启动"
}} catch {{
    Write-Error "播放失败: $_"
    exit 1
}}
'''
        temp_ps = os.path.join(TEMP_DIR, f"play_{os.getpid()}_{int(time.time()*1000)}.ps1")
        with open(temp_ps, 'w', encoding='utf-8') as f:
            f.write(ps_script)
        
        # 启动 PowerShell，隐藏窗口，不等待
        subprocess.Popen([
            "powershell.exe",
            "-NoProfile",
            "-WindowStyle", "Hidden",
            "-File", temp_ps
        ], creationflags=subprocess.CREATE_NO_WINDOW,
           stdout=subprocess.DEVNULL,
           stderr=subprocess.DEVNULL)
        
        print(f"[INFO] 静默播放 (PowerShell + WMP COM, 音量: {VOLUME}%)", file=sys.stderr)
        return True
    except Exception as e:
        print(f"[WARN] PowerShell 播放失败: {e}", file=sys.stderr)
        return False

def announce(type_, message, lang="zh"):
    """主函数"""
    voices = {
        "zh": "zh-CN-XiaoxiaoNeural",
        "zh-m": "zh-CN-YunxiNeural",
        "en": "en-US-JennyNeural",
        "en-m": "en-US-GuyNeural",
        "ja": "ja-JP-NanamiNeural",
        "ko": "ko-KR-SunHiNeural",
        "es": "es-ES-ElviraNeural",
        "fr": "fr-FR-DeniseNeural",
        "de": "de-DE-KatjaNeural",
    }
    
    voice = voices.get(lang, voices["zh"])
    
    prefixes = {
        "task": "任务: ",
        "complete": "完成: ",
        "error": "警告: ",
        "custom": ""
    }
    
    prefix = prefixes.get(type_, "")
    full_message = prefix + message
    
    timestamp = int(time.time() * 1000)
    temp_mp3 = os.path.join(TEMP_DIR, f"announce_{os.getpid()}_{timestamp}.mp3")
    
    try:
        # 生成 MP3
        if not generate_audio(full_message, voice, temp_mp3):
            return False
        
        # 静默播放
        if not play_silent_mp3(temp_mp3):
            print("[ERROR] 无法播放音频", file=sys.stderr)
            try:
                os.remove(temp_mp3)
            except:
                pass
            return False
        
        print(f"[INFO] 播报成功（完全静默）", file=sys.stderr)
        
        # 根据配置清理临时文件
        if not KEEP_TEMP_FILES:
            def delayed_cleanup(file_path, delay=CLEANUP_DELAY):
                time.sleep(delay)
                try:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                except:
                    pass
            threading.Thread(target=delayed_cleanup, args=(temp_mp3,), daemon=True).start()
        else:
            print(f"[DEBUG] MP3 文件保留: {temp_mp3}", file=sys.stderr)
        
        return True
        
    except Exception as e:
        print(f"[ERROR] 播报异常: {e}", file=sys.stderr)
        try:
            if os.path.exists(temp_mp3):
                os.remove(temp_mp3)
        except:
            pass
        return False

def print_help():
    print("Silent Audio Announcement Player v5.0 (MP3)")
    print("")
    print("用法: python announce.py <type> <message> [lang]")
    print("")
    print("类型:")
    print("  task      - 任务开始/处理中")
    print("  complete  - 任务完成")
    print("  error     - 错误/警告")
    print("  custom    - 自定义消息")
    print("")
    print("语种: zh, en, ja, ko, es, fr, de")
    print("")
    print("示例:")
    print("  python announce.py complete '任务完成' zh")
    print("  python announce.py complete 'Task done' en")
    print("")
    print("特性:")
    print("  - 生成 MP3，PowerShell WMP COM 静默播放")
    print("  - 完全静默，无窗口")
    print("  - 自动缓存，快速重复")
    print("  - 异步播放，立即返回")
    print("  - 临时文件自动清理（默认60秒后）")

def print_version():
    print("v5.1.0 (MP3 - Silent Player - Auto Cleanup)")

if __name__ == "__main__":
    ensure_dirs()
    
    if len(sys.argv) < 3:
        if len(sys.argv) == 2 and sys.argv[1] in ["-h", "--help", "help"]:
            print_help()
            sys.exit(0)
        elif len(sys.argv) == 2 and sys.argv[1] in ["-v", "--version"]:
            print_version()
            sys.exit(0)
        else:
            print("用法: python announce.py <type> <message> [lang]", file=sys.stderr)
            print("运行 python announce.py -h 查看帮助", file=sys.stderr)
            sys.exit(1)
    
    type_ = sys.argv[1]
    message = sys.argv[2]
    lang = sys.argv[3] if len(sys.argv) > 3 else "zh"
    
    success = announce(type_, message, lang)
    sys.exit(0 if success else 1)
