#!/usr/bin/env python3
"""
股票投资深度分析技能 - 主执行脚本

调用scripts/agentscope_stock_advisor.py文件执行完整的股票分析任务
"""

import os
import sys
import subprocess
import argparse
import time
from pathlib import Path

def validate_stock_code(stock_code):
    """验证股票代码格式"""
    if not stock_code:
        raise ValueError("股票代码不能为空")
    
    if not (stock_code.endswith('.SH') or stock_code.endswith('.SZ')):
        raise ValueError("股票代码必须包含交易所后缀(.SH 或 .SZ)")
    
    # 检查股票代码部分是否为6位数字
    code_part = stock_code[:-3]  # 去掉后缀
    if not code_part.isdigit() or len(code_part) != 6:
        raise ValueError("股票代码必须是6位数字 + 交易所后缀")
    
    return True

def validate_output_path(output_path):
    """验证输出路径"""
    path = Path(output_path)
    try:
        path.mkdir(parents=True, exist_ok=True)
        # 测试写入权限
        test_file = path / ".test_write"
        test_file.touch()
        test_file.unlink()
        return True
    except Exception as e:
        raise ValueError(f"输出路径无效或无写入权限: {e}")

def run_stock_analysis(stock_code, output_path):
    """执行股票分析"""
    target_script = "scripts/agentscope_stock_advisor.py"
    
    # 验证目标脚本存在
    if not os.path.exists(target_script):
        raise FileNotFoundError(f"目标Python文件不存在: {target_script}")
    
    # 验证输入参数
    validate_stock_code(stock_code)
    validate_output_path(output_path)
    
    print(f"开始分析股票: {stock_code}")
    print(f"报告输出路径: {output_path}")
    print(f"预计分析时间: 10分钟左右")
    print("-" * 50)
    
    # 构建命令
    cmd = [
        sys.executable,
        target_script,
        "-s", stock_code,
        "-o", output_path
    ]
    
    try:
        # 执行分析脚本
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        # 实时输出日志
        print("开始执行股票分析系统...")
        print("实时分析日志:")
        print("=" * 50)
        
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())
                sys.stdout.flush()
        
        # 获取返回码
        return_code = process.poll()
        
        if return_code == 0:
            print("=" * 50)
            print("✅ 股票分析完成！")
            print(f"报告已保存到: {output_path}")
            
            # 查找生成的PDF文件
            pdf_files = list(Path(output_path).glob("*.pdf"))
            if pdf_files:
                latest_pdf = max(pdf_files, key=os.path.getctime)
                print(f"最新PDF报告: {latest_pdf.name}")
                return str(latest_pdf)
            else:
                print("⚠️ 未找到生成的PDF报告文件")
                return None
        else:
            raise RuntimeError(f"分析脚本执行失败，返回码: {return_code}")
            
    except KeyboardInterrupt:
        print("\n⚠️ 分析过程被用户中断")
        process.terminate()
        process.wait()
        raise
    except Exception as e:
        print(f"❌ 分析过程中发生错误: {e}")
        raise

def main():
    parser = argparse.ArgumentParser(description="股票投资深度分析技能")
    parser.add_argument("-s", "--stock_code", required=True, 
                       help="股票代码（必须包含交易所后缀，如：600519.SH 或 000960.SZ）")
    parser = argparse.ArgumentParser(description="股票投资深度分析技能")
    parser.add_argument("-s", "--stock_code", required=True, 
                       help="股票代码（必须包含交易所后缀，如：600519.SH 或 000960.SZ）")
    parser.add_argument("-o", "--output_path", required=True,
                       help="报告输出路径")
    
    args = parser.parse_args()
    
    try:
        pdf_path = run_stock_analysis(args.stock_code, args.output_path)
        if pdf_path:
            print(f"\n📄 PDF报告路径: {pdf_path}")
        else:
            print("\n⚠️ 分析完成但未生成PDF报告")
    except Exception as e:
        print(f"\n❌ 技能执行失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
