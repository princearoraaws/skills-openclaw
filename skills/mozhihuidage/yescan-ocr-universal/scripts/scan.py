#!/usr/bin/env python3
"""
Quark OCR - 夸克扫描王 OCR识别服务（仅返回结果，不保存文件）
支持通过 --scene 参数指定场景，自动获取对应配置
"""
import sys
import argparse
from pathlib import Path

# 导入公共模块 - 同级目录（发布版本）
SCRIPTS_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPTS_DIR))

from common import (
    OCRResult,
    CredentialManager,
    QuarkOCRClient,
    get_scene_config,
    list_scenes,
)


def main():
    """主函数 - 仅调用 API 并返回结果，不保存文件"""
    parser = argparse.ArgumentParser(
        description="Quark OCR - 支持图片 URL、本地路径、BASE64 字符串",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
可用场景（--scene 参数值）:
  {', '.join(list_scenes())}

示例:
  # 通用 OCR
  python3 scripts/scan.py --scene general-ocr --url "https://example.com/image.jpg"
  
  # 身份证识别
  python3 scripts/scan.py --scene idcard-ocr --path "/path/to/idcard.jpg"
        """
    )
    
    # 场景参数（必填）
    parser.add_argument("--scene", "-s", required=True, help="场景名称（如 general-ocr, idcard-ocr 等）")
    
    # 图片输入参数（三选一）
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--url", "-u", help="图片 URL")
    group.add_argument("--path", "-p", help="本地图片文件路径")
    group.add_argument("--base64", "-b", help="BASE64 字符串")
    
    args = parser.parse_args()
    
    # 获取场景配置
    try:
        config = get_scene_config(args.scene)
    except ValueError as e:
        print(OCRResult(code="INVALID_SCENE", message=str(e), data=None).to_json())
        sys.exit(1)
    
    try:
        api_key = CredentialManager.load()
        with QuarkOCRClient(
            api_key=api_key,
            service_option=config["service_option"],
            input_configs=config["input_configs"],
            output_configs=config["output_configs"],
            data_type=config["data_type"]
        ) as client:
            if args.base64:
                result = client.recognize(base64_data=args.base64)
            elif args.url:
                result = client.recognize(image_url=args.url)
            else:
                result = client.recognize(image_path=args.path)
        
        # 直接输出结果，不保存文件
        print(result.to_json())
        
    except ValueError as e:
        print(OCRResult(code="A0100", message=str(e), data=None).to_json())
        sys.exit(1)
    except Exception as e:
        print(OCRResult(code="UNKNOWN_ERROR", message=f"Unexpected error: {str(e)}", data=None).to_json())
        sys.exit(1)


if __name__ == "__main__":
    main()
