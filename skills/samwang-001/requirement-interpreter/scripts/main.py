#!/usr/bin/env python3
"""
需求解读技能入口文件
提供命令行界面和API接口
"""

import sys
import json
from pathlib import Path

# 添加脚本目录到路径
script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))

from optimized_interpreter import OptimizedRequirementInterpreter
from optimized_classifier import RequirementClassifier


def main():
    """主入口函数"""
    if len(sys.argv) < 2:
        print("用法: python main.py <需求描述>")
        print("示例: python main.py \"请帮我设计一个蛋糕促销海报\"")
        sys.exit(1)
    
    requirement_text = sys.argv[1]
    
    # 初始化解读器
    case_library_path = script_dir / "case_library.json"
    interpreter = OptimizedRequirementInterpreter(str(case_library_path))
    
    # 解读需求
    result = interpreter.interpret_requirement(requirement_text)
    
    # 输出结果
    print("\n=== 需求解读结果 ===\n")
    print(f"需求类型: {result['classification'].primary_type.value}")
    print(f"二级分类: {result['classification'].secondary_type}")
    print(f"置信度: {result['classification'].confidence:.2%}")
    print(f"行业背景: {result['classification'].context.industry}")
    print(f"紧急程度: {result['classification'].context.urgency.value}")
    print(f"复杂度: {result['classification'].context.complexity.value}")
    
    print(f"\n推荐思考维度 ({len(result['dimensions'])}):")
    for dim in result['dimensions'][:5]:
        print(f"  - {dim}")
    
    print(f"\n相似案例 ({len(result['similar_cases'])}):")
    for case in result['similar_cases'][:3]:
        print(f"  - {case.title}")
    
    print(f"\n建议访谈问题 ({len(result['interview_plan']['questions'])}):")
    for q in result['interview_plan']['questions'][:3]:
        print(f"  - {q}")
    
    print()


if __name__ == "__main__":
    main()
