#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
车况信息查询脚本 - 跨平台版本 (Mac/Windows/Linux)
功能：读取缓存认证信息，调用 API 获取车辆状态

用法：
    python3 query_vehicle.py              # 查询全部信息
    python3 query_vehicle.py --position   # 仅查询车辆位置
    python3 query_vehicle.py --condition  # 仅查询车况信息
    python3 query_vehicle.py --json       # 输出原始 JSON
"""

import json
import sys
import urllib.request
import urllib.error
import ssl
import argparse
from pathlib import Path
from datetime import datetime

# 配置
BASE_URL = "https://openapi.nokeeu.com"
API_URL = f"{BASE_URL}/iot/v1/condition"
CACHE_FILE = Path.home() / ".skill_carkey_cache.json"

# 状态映射
POWER_STATUS = {0: "熄火", 1: "ACC", 2: "ON"}
GEAR_STATUS = {1: "P档", 2: "N档", 3: "D档", 4: "R档", 5: "S档"}
SWITCH_STATUS = {0: "关闭/解锁", 1: "开启/上锁"}


def load_cache():
    """读取缓存文件中的认证信息"""
    if not CACHE_FILE.exists():
        print("❌ 未找到认证信息")
        print(f"请提供认证信息，格式：vehicleToken####accessToken")
        print(f"缓存文件路径：{CACHE_FILE}")
        sys.exit(1)
    
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            cache = json.load(f)
    except json.JSONDecodeError:
        print("❌ 缓存文件格式错误")
        sys.exit(1)
    
    access_token = cache.get("accessToken", "")
    vehicle_token = cache.get("vehicleToken", "")
    
    if not access_token or not vehicle_token:
        print("❌ 认证信息不完整")
        print("请提供完整的 vehicleToken####accessToken")
        sys.exit(1)
    
    return access_token, vehicle_token


def call_api(access_token: str, vehicle_token: str) -> dict:
    """调用车况 API"""
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    data = json.dumps({"vehicleToken": vehicle_token}).encode("utf-8")
    
    # 创建忽略 SSL 证书验证的上下文（某些环境可能需要）
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    
    try:
        req = urllib.request.Request(API_URL, data=data, headers=headers, method="POST")
        with urllib.request.urlopen(req, context=ctx, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(f"❌ HTTP 错误: {e.code}")
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"❌ 网络错误: {e.reason}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        sys.exit(1)


def format_timestamp(ts):
    """格式化时间戳（毫秒）"""
    if not ts:
        return "未知"
    try:
        return datetime.fromtimestamp(ts / 1000).strftime("%Y-%m-%d %H:%M:%S")
    except:
        return str(ts)


def parse_status(value, mapping):
    """解析状态值"""
    if value is None:
        return "未知"
    return mapping.get(value, str(value))


def display_basic_info(data: dict):
    """输出基本信息（SN/VIN）"""
    print(f"📱 SN: {data.get('sn', '未知')}")
    print(f"🚗 VIN: {data.get('vin', '未知')}")


def display_position(data: dict):
    """输出车辆位置信息"""
    pos = data.get("vehiclePosition", {})
    if not pos:
        print("\n📍 位置信息: 暂无数据")
        return
    
    print(f"\n📍 位置信息:")
    if pos.get("address"):
        print(f"   地址: {pos['address']}")
    if pos.get("longitude") and pos.get("latitude"):
        print(f"   经纬度: {pos['longitude']}, {pos['latitude']}")
    if pos.get("positionUpdateTime"):
        print(f"   更新时间: {format_timestamp(pos['positionUpdateTime'])}")


def display_condition(data: dict):
    """输出车况信息"""
    cond = data.get("vehicleCondition", {})
    if not cond:
        print("\n🔧 车况信息: 暂无数据")
        return
    
    print(f"\n🔧 车辆状态:")
    
    # 电源和档位
    if "power" in cond:
        print(f"   电源: {parse_status(cond['power'], POWER_STATUS)}")
    if "gear" in cond:
        print(f"   档位: {parse_status(cond['gear'], GEAR_STATUS)}")
    
    # 车门状态
    door = cond.get("door", {})
    if door:
        print(f"\n🚪 车门状态:")
        door_names = {"fl": "左前门", "fr": "右前门", "rl": "左后门", "rr": "右后门", "trunk": "后备箱"}
        for key, name in door_names.items():
            if key in door:
                status = "开启" if door[key] == 1 else "关闭"
                print(f"   {name}: {status}")
    
    # 车锁状态
    lock = cond.get("lock", {})
    if lock:
        print(f"\n🔐 车锁状态:")
        lock_names = {"fl": "左前锁", "fr": "右前锁", "rl": "左后锁", "rr": "右后锁"}
        for key, name in lock_names.items():
            if key in lock:
                status = "上锁" if lock[key] == 1 else "解锁"
                print(f"   {name}: {status}")
    
    # 车窗状态
    window = cond.get("window", {})
    if window:
        print(f"\n🪟 车窗状态:")
        window_names = {"fl": "左前窗", "fr": "右前窗", "rl": "左后窗", "rr": "右后窗", "skylight": "天窗"}
        for key, name in window_names.items():
            if key in window:
                status = "开启" if window[key] == 1 else "关闭"
                print(f"   {name}: {status}")
    
    # 空调状态
    ac = cond.get("airConditionerState", {})
    if ac:
        print(f"\n❄️ 空调状态:")
        if "driverTemperature" in ac:
            print(f"   驾驶位温度: {ac['driverTemperature']}°C")
        if "passengerTemperature" in ac:
            print(f"   副驾驶温度: {ac['passengerTemperature']}°C")


def display_result(data: dict, show_position: bool = True, show_condition: bool = True):
    """格式化输出车况信息"""
    print("\n✅ 查询成功\n")
    print("=" * 50)
    
    # 基本信息
    display_basic_info(data)
    
    # 位置信息
    if show_position:
        display_position(data)
    
    # 车况信息
    if show_condition:
        display_condition(data)
    
    print("\n" + "=" * 50)


def output_json(data: dict, filter_key: str = None):
    """输出原始 JSON（供后续处理）"""
    print("\n📋 数据 (JSON):")
    if filter_key and filter_key in data:
        output = {filter_key: data[filter_key]}
    else:
        output = data
    print(json.dumps(output, ensure_ascii=False, indent=2))


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="车况信息查询脚本 - 跨平台版本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python3 query_vehicle.py              查询全部信息
  python3 query_vehicle.py -p           仅查询车辆位置
  python3 query_vehicle.py -c           仅查询车况信息
  python3 query_vehicle.py -p --json    查询位置并输出 JSON
        """
    )
    
    # 查询模式（互斥）
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "-p", "--position",
        action="store_true",
        help="仅查询车辆位置信息"
    )
    mode_group.add_argument(
        "-c", "--condition",
        action="store_true",
        help="仅查询车况信息（车门、车锁、车窗、空调等）"
    )
    
    # 输出选项
    parser.add_argument(
        "--json",
        action="store_true",
        help="输出原始 JSON 数据"
    )
    
    return parser.parse_args()


def query_position(access_token: str, vehicle_token: str, output_json_flag: bool = False):
    """查询车辆位置"""
    response = call_api(access_token, vehicle_token)
    check_response(response)
    
    data = response.get("data", {})
    display_result(data, show_position=True, show_condition=False)
    
    if output_json_flag:
        output_json(data, "vehiclePosition")


def query_condition(access_token: str, vehicle_token: str, output_json_flag: bool = False):
    """查询车况信息"""
    response = call_api(access_token, vehicle_token)
    check_response(response)
    
    data = response.get("data", {})
    display_result(data, show_position=False, show_condition=True)
    
    if output_json_flag:
        output_json(data, "vehicleCondition")


def query_all(access_token: str, vehicle_token: str, output_json_flag: bool = False):
    """查询全部信息"""
    response = call_api(access_token, vehicle_token)
    check_response(response)
    
    data = response.get("data", {})
    display_result(data, show_position=True, show_condition=True)
    
    if output_json_flag:
        output_json(data)


def check_response(response: dict):
    """检查 API 响应"""
    if response.get("code") != 0:
        error_msg = response.get("message", "未知错误")
        error_code = response.get("code", "")
        print(f"❌ API 错误 [{error_code}]: {error_msg}")
        
        # 特殊错误处理
        if error_code == 360004:
            print("💡 提示: access_token 可能已过期，请重新获取认证信息")
        sys.exit(1)


def main():
    """主函数"""
    args = parse_args()
    
    # 1. 读取认证信息
    access_token, vehicle_token = load_cache()
    
    # 2. 根据参数执行对应查询
    if args.position:
        query_position(access_token, vehicle_token, args.json)
    elif args.condition:
        query_condition(access_token, vehicle_token, args.json)
    else:
        query_all(access_token, vehicle_token, args.json)


if __name__ == "__main__":
    main()
