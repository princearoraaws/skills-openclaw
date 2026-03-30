#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
鐪犲皬鍏旂潯鐪犲仴搴锋妧鑳?- OpenClaw闆嗘垚 (鐪熷疄鍔熻兘鐗?
鎵€鏈夊姛鑳介兘鏄湡瀹炵殑锛岀粷涓嶆ā鎷燂紒
绗﹀悎OpenClaw鎶€鑳借鑼?v1.0.5
"""

import os
import sys
import json
import argparse
import statistics
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import shutil
import csv


class EnvironmentCapability(Enum):
    """鐜鑳藉姏绾у埆"""
    BASIC = "basic"      # 浠呮爣鍑嗗簱锛屾彁渚涚湡瀹炲熀纭€鍔熻兘
    ADVANCED = "advanced"  # 鏈塎NE绛夌瀛﹀簱锛屾彁渚涘畬鏁碋DF鍒嗘瀽
    FULL = "full"        # 瀹屾暣AISleepGen鐜锛屾墍鏈夐珮绾у姛鑳?

class FileType(Enum):
    """鏂囦欢绫诲瀷"""
    EDF = "edf"          # EDF鐫＄湢鏁版嵁
    CSV = "csv"          # CSV鏁版嵁鏂囦欢
    TXT = "txt"          # 鏂囨湰鏁版嵁
    UNKNOWN = "unknown"  # 鏈煡绫诲瀷


@dataclass
class FileAnalysis:
    """鏂囦欢鍒嗘瀽缁撴灉"""
    exists: bool
    file_type: FileType
    size_mb: float
    extension: str
    is_readable: bool
    line_count: Optional[int] = None
    encoding: Optional[str] = None


@dataclass
class HeartRateAnalysis:
    """蹇冪巼鍒嗘瀽缁撴灉"""
    samples: int
    average_bpm: float
    min_bpm: float
    max_bpm: float
    std_dev: float
    variability_score: float
    assessment: str
    recommendations: List[str]


class SleepRabbitSkill:
    """鐪犲皬鍏旂潯鐪犲仴搴锋妧鑳?- 鎵€鏈夊姛鑳介兘鏄湡瀹炵殑"""
    
    def __init__(self):
        self.name = "鐪犲皬鍏旂潯鐪犲仴搴?
        self.version = "1.0.5"
        self.description = "涓撲笟鐨勭潯鐪犲垎鏋愩€佸帇鍔涜瘎浼板拰鍐ユ兂鎸囧绯荤粺锛堢湡瀹炲姛鑳斤級"
        
        # 妫€娴嬬幆澧冭兘鍔?        self.capability = self._detect_capability()
        print(f"[INFO] 鐜鑳藉姏: {self.capability.value}")
    
    def _detect_capability(self) -> EnvironmentCapability:
        """妫€娴嬬幆澧冭兘鍔?""
        # 妫€鏌NE
        try:
            import mne
            import numpy
            import scipy
            # 妫€鏌ュ畬鏁寸幆澧?            try:
                from plugin_manager import PluginManager
                return EnvironmentCapability.FULL
            except ImportError:
                return EnvironmentCapability.ADVANCED
        except ImportError:
            return EnvironmentCapability.BASIC
    
    def setup(self, context: Dict[str, Any]) -> None:
        """璁剧疆鏂规硶"""
        print(f"[INFO] {self.name} v{self.version} 璁剧疆瀹屾垚")
        print(f"[INFO] 妯″紡: {self.capability.value}")
        print(f"[INFO] 鍘熷垯: 鎵€鏈夊姛鑳介兘鏄湡瀹炵殑锛岀粷涓嶆ā鎷?)
        
        if self.capability == EnvironmentCapability.BASIC:
            print(f"[INFO] 褰撳墠鍔熻兘: 鏂囦欢楠岃瘉銆佸績鐜囧垎鏋愩€佸啣鎯虫寚瀵?)
            print(f"[INFO] 瀹夎MNE鍙幏寰桬DF鍒嗘瀽: pip install mne numpy scipy")
    
    def handle(self, command: str, args: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """澶勭悊鍛戒护"""
        print(f"[INFO] 澶勭悊鍛戒护: {command}")
        
        if command == "sleep-analyze":
            return self._handle_sleep_analyze_real(args)
        elif command == "stress-check":
            return self._handle_stress_check_real(args)
        elif command == "meditation-guide":
            return self._handle_meditation_guide_real(args)
        elif command == "file-info":
            return self._handle_file_info(args)
        elif command == "hr-analyze":
            return self._handle_hr_analyze(args)
        elif command == "skill-info":
            return self._handle_skill_info(args)
        elif command == "env-check":
            return self._handle_env_check(args)
        else:
            return {
                "error": f"鏈煡鍛戒护: {command}",
                "available_commands": self._get_available_commands()
            }
    
    def _handle_sleep_analyze_real(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """鐪熷疄鐨勭潯鐪犲垎鏋?""
        edf_file = args.get("edf_file", "")
        
        if not edf_file:
            return {
                "success": False,
                "error": "璇锋彁渚汦DF鏂囦欢璺緞",
                "usage": "/sleep-analyze <edf鏂囦欢璺緞>",
                "example": "/sleep-analyze data/sleep.edf"
            }
        
        # 1. 棣栧厛杩涜鐪熷疄鐨勬枃浠舵鏌?        file_analysis = self._analyze_file(edf_file)
        
        if not file_analysis.exists:
            return {
                "success": False,
                "error": f"鏂囦欢涓嶅瓨鍦? {edf_file}",
                "suggestion": "璇锋鏌ユ枃浠惰矾寰勬槸鍚︽纭?
            }
        
        if file_analysis.file_type != FileType.EDF:
            return {
                "success": False,
                "error": f"鏂囦欢涓嶆槸EDF鏍煎紡: {file_analysis.extension}",
                "file_info": self._format_file_analysis(file_analysis),
                "requirement": "鐫＄湢鍒嗘瀽闇€瑕佹爣鍑嗙殑EDF鏍煎紡鏂囦欢"
            }
        
        # 2. 鏍规嵁鐜鑳藉姏鎻愪緵鐪熷疄鍒嗘瀽
        if self.capability in [EnvironmentCapability.ADVANCED, EnvironmentCapability.FULL]:
            # 浣跨敤MNE杩涜鐪熷疄EDF鍒嗘瀽
            return self._analyze_edf_with_mne(edf_file, file_analysis)
        else:
            # 鍩虹鐜锛氭彁渚涚湡瀹炵殑鏂囦欢淇℃伅鍜屾槑纭殑鍗囩骇鎸囧
            return {
                "success": True,
                "command": "sleep-analyze",
                "capability": "basic",
                "data": {
                    "file_analysis": self._format_file_analysis(file_analysis),
                    "analysis_status": "鏂囦欢楠岃瘉閫氳繃锛岀瓑寰匛DF鍒嗘瀽",
                    "requirements": {
                        "current": "鏍囧噯Python鐜",
                        "required": "MNE-Python搴?,
                        "purpose": "瑙ｆ瀽鍜屽垎鏋怑DF鐫＄湢鏁版嵁鏂囦欢"
                    },
                    "next_steps": [
                        f"1. 鏂囦欢 '{Path(edf_file).name}' 宸查獙璇佷负EDF鏍煎紡",
                        f"2. 鏂囦欢澶у皬: {file_analysis.size_mb:.2f} MB",
                        "3. 闇€瑕佸畨瑁匨NE搴撹繘琛岀潯鐪犳暟鎹垎鏋?,
                        "4. 瀹夎鍛戒护: pip install mne numpy scipy",
                        "5. 瀹夎鍚庨噸鏂拌繍琛屾鍛戒护"
                    ]
                },
                "note": "EDF鏂囦欢宸查獙璇侊紝瀹夎MNE鍚庡嵆鍙繘琛屽畬鏁寸潯鐪犲垎鏋?,
                "installation_guide": self._get_mne_installation_guide()
            }
    
    def _analyze_edf_with_mne(self, edf_file: str, file_analysis: FileAnalysis) -> Dict[str, Any]:
        """浣跨敤MNE杩涜鐪熷疄鐨凟DF鍒嗘瀽"""
        try:
            import mne
            import numpy as np
            
            print(f"[INFO] 浣跨敤MNE鍒嗘瀽EDF鏂囦欢: {edf_file}")
            
            # 璇诲彇EDF鏂囦欢
            raw = mne.io.read_raw_edf(edf_file, preload=False)
            
            # 鎻愬彇鐪熷疄淇℃伅
            info = {
                "channels": len(raw.ch_names),
                "channel_names": raw.ch_names[:10],  # 鍙樉绀哄墠10涓?                "sampling_frequency": float(raw.info['sfreq']),
                "duration_seconds": float(raw.times[-1]),
                "duration_formatted": self._format_duration(raw.times[-1]),
                "measurement_date": str(raw.info['meas_date']) if raw.info['meas_date'] else "鏈煡"
            }
            
            # 鑾峰彇閮ㄥ垎鏁版嵁杩涜鍒嗘瀽锛堥伩鍏嶅唴瀛橀棶棰橈級
            if raw.times[-1] > 30:  # 濡傛灉鏃堕暱瓒呰繃30绉掞紝鍙垎鏋愬墠30绉?                duration = 30
            else:
                duration = raw.times[-1]
            
            data, times = raw[:, :int(duration * raw.info['sfreq'])]
            
            # 鐪熷疄鐨勬暟鎹垎鏋?            if len(data) > 0:
                # 璁＄畻EEG閫氶亾鐨勫姛鐜?                eeg_indices = [i for i, name in enumerate(raw.ch_names) if 'EEG' in name.upper()]
                if eeg_indices:
                    eeg_data = data[eeg_indices]
                    mean_amplitude = np.mean(np.abs(eeg_data))
                    amplitude_std = np.std(eeg_data)
                    
                    # 鍩轰簬鐪熷疄鏁版嵁鐨勭畝鍗曡川閲忚瘎浼?                    if amplitude_std > 20 and mean_amplitude > 10:
                        signal_quality = "鑹ソ"
                        quality_score = 75
                    elif amplitude_std > 10:
                        signal_quality = "涓€鑸?
                        quality_score = 60
                    else:
                        signal_quality = "杈冨樊"
                        quality_score = 40
                else:
                    signal_quality = "鏃燛EG淇″彿"
                    quality_score = 0
                    mean_amplitude = 0
                    amplitude_std = 0
            else:
                signal_quality = "鏃犳暟鎹?
                quality_score = 0
                mean_amplitude = 0
                amplitude_std = 0
            
            return {
                "success": True,
                "command": "sleep-analyze",
                "capability": "advanced",
                "data": {
                    "file_info": self._format_file_analysis(file_analysis),
                    "edf_info": info,
                    "signal_analysis": {
                        "signal_quality": signal_quality,
                        "quality_score": quality_score,
                        "mean_amplitude": float(mean_amplitude),
                        "amplitude_std": float(amplitude_std),
                        "analyzed_duration": f"{duration}绉?,
                        "data_points": data.shape[1]
                    },
                    "recommendations": [
                        "EDF鏂囦欢瑙ｆ瀽鎴愬姛",
                        f"淇″彿璐ㄩ噺: {signal_quality}",
                        "寤鸿杩涜瀹屾暣鐨勭潯鐪犲垎鏈熷垎鏋? if quality_score > 50 else "寤鸿妫€鏌ヤ俊鍙疯川閲?
                    ]
                },
                "note": "浣跨敤MNE-Python杩涜鐪熷疄鐨凟DF鏂囦欢鍒嗘瀽",
                "analysis_method": "MNE搴撶湡瀹炲垎鏋?
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"EDF鍒嗘瀽澶辫触: {str(e)}",
                "file_info": self._format_file_analysis(file_analysis),
                "suggestion": "璇锋鏌DF鏂囦欢鏍煎紡鏄惁姝ｇ‘锛屾垨灏濊瘯鍏朵粬鏂囦欢"
            }
    
    def _handle_stress_check_real(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """鐪熷疄鐨勫帇鍔涜瘎浼?""
        heart_rate_data = args.get("heart_rate_data", "")
        
        if not heart_rate_data:
            return {
                "success": False,
                "error": "璇锋彁渚涘績鐜囨暟鎹?,
                "usage": "/stress-check <蹇冪巼鏁版嵁>",
                "example": "/stress-check 70,72,75,68,80,78,76",
                "data_format": "閫楀彿鍒嗛殧鐨勬暟瀛楋紝濡? 70,72,75,68,80"
            }
        
        # 瑙ｆ瀽蹇冪巼鏁版嵁
        try:
            if isinstance(heart_rate_data, str):
                hr_values = [float(x.strip()) for x in heart_rate_data.split(",")]
            elif isinstance(heart_rate_data, list):
                hr_values = [float(x) for x in heart_rate_data]
            else:
                return {"error": "蹇冪巼鏁版嵁鏍煎紡涓嶆纭?}
        except ValueError as e:
            return {
                "success": False,
                "error": f"蹇冪巼鏁版嵁瑙ｆ瀽澶辫触: {str(e)}",
                "suggestion": "璇风‘淇濇暟鎹槸閫楀彿鍒嗛殧鐨勬暟瀛楋紝濡? 70,72,75,68,80"
            }
        
        if len(hr_values) < 5:
            return {
                "success": False,
                "error": f"鏁版嵁鐐逛笉瓒? {len(hr_values)} 涓紝闇€瑕佽嚦灏?涓暟鎹偣",
                "suggestion": "璇锋彁渚涙洿澶氬績鐜囨暟鎹偣"
            }
        
        # 杩涜鐪熷疄鐨勫績鐜囧垎鏋?        analysis = self._analyze_heart_rate(hr_values)
        
        return {
            "success": True,
            "command": "stress-check",
            "data": {
                "heart_rate_data": {
                    "samples": analysis.samples,
                    "values": hr_values[:10] if len(hr_values) > 10 else hr_values,
                    "total_points": len(hr_values)
                },
                "analysis": {
                    "average_bpm": analysis.average_bpm,
                    "range": f"{analysis.min_bpm}-{analysis.max_bpm} BPM",
                    "variability": f"{analysis.variability_score:.2f}",
                    "assessment": analysis.assessment
                },
                "recommendations": analysis.recommendations,
                "analysis_method": "鐪熷疄缁熻璁＄畻"
            },
            "note": f"鍩轰簬 {len(hr_values)} 涓湡瀹炲績鐜囨暟鎹偣鐨勫垎鏋?
        }
    
    def _analyze_heart_rate(self, hr_values: List[float]) -> HeartRateAnalysis:
        """鍒嗘瀽蹇冪巼鏁版嵁"""
        samples = len(hr_values)
        average_bpm = statistics.mean(hr_values)
        min_bpm = min(hr_values)
        max_bpm = max(hr_values)
        
        # 璁＄畻鏍囧噯宸?        if samples > 1:
            std_dev = statistics.stdev(hr_values)
        else:
            std_dev = 0
        
        # 璁＄畻鍙樺紓鎬ц瘎鍒嗭紙绠€鍗曠畻娉曪級
        range_bpm = max_bpm - min_bpm
        variability_score = min(1.0, range_bpm / 40)  # 40 BPM鑼冨洿瀵瑰簲鏈€楂樺垎
        
        # 璇勪及
        if average_bpm < 60:
            assessment = "蹇冪巼鍋忎綆"
            recommendations = ["蹇冪巼鍋忎綆锛屽缓璁挩璇㈠尰鐢?, "閫傚綋澧炲姞鏈夋哀杩愬姩"]
        elif average_bpm > 100:
            assessment = "蹇冪巼鍋忛珮"
            recommendations = ["蹇冪巼鍋忛珮锛屽缓璁斁鏉句紤鎭?, "閬垮厤鍓х儓杩愬姩", "鑰冭檻鍜ㄨ鍖荤敓"]
        elif variability_score < 0.3:
            assessment = "蹇冪巼鍙樺紓鎬ц緝浣?
            recommendations = ["蹇冪巼鍙樺紓鎬ц緝浣庯紝寤鸿鏀炬澗缁冧範", "灏濊瘯娣卞懠鍚哥粌涔?]
        elif variability_score > 0.7:
            assessment = "蹇冪巼鍙樺紓鎬ц壇濂?
            recommendations = ["蹇冪巼鍙樺紓鎬ц壇濂斤紝蹇冭绠″仴搴?, "缁х画淇濇寔褰撳墠鐢熸椿涔犳儻"]
        else:
            assessment = "蹇冪巼姝ｅ父"
            recommendations = ["蹇冪巼鍦ㄦ甯歌寖鍥?, "淇濇寔鍋ュ悍鐢熸椿涔犳儻"]
        
        return HeartRateAnalysis(
            samples=samples,
            average_bpm=round(average_bpm, 1),
            min_bpm=min_bpm,
            max_bpm=max_bpm,
            std_dev=round(std_dev, 1),
            variability_score=round(variability_score, 2),
            assessment=assessment,
            recommendations=recommendations
        )
    
    def _handle_meditation_guide_real(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """鐪熷疄鐨勫啣鎯虫寚瀵?""
        meditation_type = args.get("type", "relaxation")
        duration = args.get("duration", 10)
        
        # 楠岃瘉鍙傛暟
        if duration < 1 or duration > 60:
            return {
                "success": False,
                "error": f"鏃堕暱鏃犳晥: {duration}鍒嗛挓",
                "valid_range": "1-60鍒嗛挓",
                "suggestion": "璇锋彁渚?-60鍒嗛挓涔嬮棿鐨勬椂闀?
            }
        
        # 鐪熷疄鐨勫啣鎯虫寚瀵煎唴瀹?        guides = {
            "relaxation": {
                "name": "鏀炬澗鍐ユ兂",
                "purpose": "缂撹В鍘嬪姏锛屾斁鏉捐韩蹇?,
                "preparation": [
                    "鎵句竴涓畨闈欒垝閫傜殑鍦版柟",
                    "鍏抽棴鎵嬫満鍜屽共鎵版簮",
                    "绌跨潃瀹芥澗鑸掗€傜殑琛ｆ湇",
                    "鍑嗗涓€涓鏃跺櫒"
                ],
                "steps": [
                    {"time": "0-1鍒嗛挓", "action": "鑸掗€傚潗涓嬶紝闂笂鐪肩潧"},
                    {"time": "1-3鍒嗛挓", "action": "娣卞懠鍚?娆★紝鎰熷彈姘旀伅杩涘嚭"},
                    {"time": "3-8鍒嗛挓", "action": "鎵弿韬綋锛屾斁鏉炬瘡涓儴浣?},
                    {"time": "8-10鍒嗛挓", "action": "鎯宠薄鍘嬪姏鍍忎簯涓€鏍烽璧?},
                    {"time": "10鍒嗛挓", "action": "鎱㈡參鐫佸紑鐪肩潧锛屾劅鍙楁斁鏉?}
                ],
                "tips": [
                    "濡傛灉鎬濈华椋樿蛋锛屾俯鏌斿湴甯﹀洖鍛煎惛",
                    "涓嶈璇勫垽鑷繁鐨勮〃鐜?,
                    "姣忓ぉ缁冧範鏁堟灉鏇翠匠"
                ]
            },
            "focus": {
                "name": "涓撴敞鍐ユ兂",
                "purpose": "鎻愰珮娉ㄦ剰鍔涘拰涓撴敞鍔?,
                "preparation": [
                    "閫夋嫨涓€涓笓娉ㄥ璞★紙鍛煎惛銆佺儧鍏夈€佸０闊筹級",
                    "纭繚鐜鐩稿瀹夐潤",
                    "璁惧畾鏄庣‘鐨勬椂闂寸洰鏍?
                ],
                "steps": [
                    {"time": "0-2鍒嗛挓", "action": "璋冩暣濮垮娍锛岃剨鏌辨尯鐩?},
                    {"time": "2-5鍒嗛挓", "action": "灏嗘敞鎰忓姏闆嗕腑鍦ㄥ璞′笂"},
                    {"time": "5-12鍒嗛挓", "action": "淇濇寔涓撴敞锛屽綋鍒嗗績鏃舵俯鏌斿甫鍥?},
                    {"time": "12-15鍒嗛挓", "action": "閫愭笎鎵╁ぇ娉ㄦ剰鍔涜寖鍥?},
                    {"time": "15鍒嗛挓", "action": "缁撴潫鍐ユ兂锛屾劅鍙椾笓娉ㄧ姸鎬?}
                ],
                "tips": [
                    "浠庣煭鏃堕棿寮€濮嬶紝閫愭笎寤堕暱",
                    "宸ヤ綔瀛︿範鍓嶈繘琛屾晥鏋滄渶浣?,
                    "璁板綍姣忔鐨勪笓娉ㄦ椂闂?
                ]
            },
            "sleep": {
                "name": "鍔╃湢鍐ユ兂",
                "purpose": "鏀瑰杽鐫＄湢璐ㄩ噺锛屽府鍔╁叆鐫?,
                "preparation": [
                    "鍦ㄥ簥涓婃垨鑸掗€傜殑鍦版柟韬轰笅",
                    "璋冩殫鐏厜锛屼繚鎸佸畨闈?,
                    "鍏抽棴鐢靛瓙璁惧"
                ],
                "steps": [
                    {"time": "0-3鍒嗛挓", "action": "鏀炬澗鍏ㄨ韩锛屼粠鑴氬埌澶存壂鎻?},
                    {"time": "3-8鍒嗛挓", "action": "缂撴參娣卞懠鍚革紝璁℃暟鍛煎惛"},
                    {"time": "8-12鍒嗛挓", "action": "鎯宠薄鍦ㄨ垝閫傜殑鍦版柟婕"},
                    {"time": "12-15鍒嗛挓", "action": "璁╂€濈华鑷劧椋樻暎锛屼笉寮鸿揩"},
                    {"time": "15鍒嗛挓", "action": "鑷劧杩涘叆鐫＄湢鐘舵€?}
                ],
                "tips": [
                    "鐫″墠30-60鍒嗛挓杩涜",
                    "淇濇寔瑙勫緥鐨勫啣鎯虫椂闂?,
                    "濡傛灉涓€旂潯鐫€涔熸病鍏崇郴"
                ]
            }
        }
        
        guide = guides.get(meditation_type, guides["relaxation"])
        
        # 璋冩暣姝ラ鏃堕棿
        adjusted_steps = []
        total_steps = len(guide["steps"])
        for i, step in enumerate(guide["steps"]):
            # 鎸夋瘮渚嬭皟鏁存椂闂?            time_ratio = (i + 1) / total_steps
            adjusted_time = int(duration * time_ratio)
            adjusted_steps.append({
                "time": f"绾adjusted_time}鍒嗛挓",
                "action": step["action"]
            })
        
        return {
            "success": True,
            "command": "meditation-guide",
            "data": {
                "type": guide["name"],
                "purpose": guide["purpose"],
                "duration": f"{duration}鍒嗛挓",
                "preparation": guide["preparation"],
                "steps": adjusted_steps,
                "tips": guide["tips"],
                "total_time": f"鎬昏 {duration} 鍒嗛挓"
            },
            "note": "鍩轰簬蹇冪悊瀛︾爺绌剁殑鍐ユ兂鎸囧鏂规硶"
        }
    
    def _handle_file_info(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """鐪熷疄鐨勬枃浠朵俊鎭垎鏋?""
        file_path = args.get("file_path", "")
        
        if not file_path:
            return {
                "success": False,
                "error": "璇锋彁渚涙枃浠惰矾寰?,
                "usage": "/file-info <鏂囦欢璺緞>"
            }
        
        analysis = self._analyze_file(file_path)
        
        return {
            "success": True,
            "command": "file-info",
            "data": self._format_file_analysis(analysis),
            "note": "鐪熷疄鐨勬枃浠剁郴缁熷垎鏋?
        }
    
    def _handle_hr_analyze(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """蹇冪巼鏁版嵁鍒嗘瀽锛堜粠鏂囦欢锛?""
        file_path = args.get("file_path", "")
        
        if not file_path:
            return {
                "success": False,
                "error": "璇锋彁渚涘績鐜囨暟鎹枃浠惰矾寰?,
                "supported_formats": ["CSV", "TXT锛堟瘡琛屼竴涓暟瀛楋級"]
            }
        
        # 鍒嗘瀽鏂囦欢
        file_analysis = self._analyze_file(file_path)
        
        if not file_analysis.exists:
            return {
                "success": False,
                "error": f"鏂囦欢涓嶅瓨鍦? {file_path}",
                "suggestion": "璇锋鏌ユ枃浠惰矾寰?
            }
        
        if not file_analysis.is_readable:
            return {
                "success": False,
                "error": f"鏂囦欢涓嶅彲璇? {file_path}",
                "file_info": self._format_file_analysis(file_analysis)
            }
        
        # 璇诲彇蹇冪巼鏁版嵁
        try:
            hr_values = []
            if file_analysis.file_type == FileType.CSV:
                with open(file_path, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    for row in reader:
                        for cell in row:
                            try:
                                hr_values.append(float(cell.strip()))
                            except ValueError:
                                continue
            else:  # TXT鎴栧叾浠栨枃鏈枃浠?                with open(file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            try:
                                hr_values.append(float(line))
                            except ValueError:
                                continue
            
            if not hr_values:
                return {
                    "success": False,
                    "error": "鏂囦欢涓湭鎵惧埌鏈夋晥鐨勫績鐜囨暟鎹?,
                    "file_info": self._format_file_analysis(file_analysis),
                    "requirement": "鏂囦欢搴斿寘鍚暟瀛楁牸寮忕殑蹇冪巼鍊?
                }
            
            # 鍒嗘瀽蹇冪巼鏁版嵁
            analysis = self._analyze_heart_rate(hr_values)
            
            return {
                "success": True,
                "command": "hr-analyze",
                "data": {
                    "file_info": self._format_file_analysis(file_analysis),
                    "heart_rate_analysis": {
                        "data_points": analysis.samples,
                        "average_bpm": analysis.average_bpm,
                        "range": f"{analysis.min_bpm}-{analysis.max_bpm} BPM",
                        "variability": analysis.variability_score,
                        "assessment": analysis.assessment
                    },
                    "recommendations": analysis.recommendations
                },
                "note": f"浠庢枃浠惰鍙?{len(hr_values)} 涓湡瀹炲績鐜囨暟鎹偣杩涜鍒嗘瀽"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"鏂囦欢璇诲彇澶辫触: {str(e)}",
                "file_info": self._format_file_analysis(file_analysis),
                "suggestion": "璇风‘淇濇枃浠舵牸寮忔纭笖鍙"
            }
    
    def _handle_skill_info(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """鎶€鑳戒俊鎭?""
        return {
            "success": True,
            "command": "skill-info",
            "data": {
                "name": self.name,
                "version": self.version,
                "description": self.description,
                "principle": "鎵€鏈夊姛鑳介兘鏄湡瀹炵殑锛岀粷涓嶆ā鎷?,
                "capability": self.capability.value,
                "real_functions": self._get_real_functions(),
                "available_commands": self._get_available_commands(),
                "requirements": self._get_requirements()
            }
        }
    
    def _handle_env_check(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """鐜妫€鏌?""
        checks = []
        
        # Python妫€鏌?        python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        checks.append({
            "check": "Python鐗堟湰",
            "status": "OK",
            "message": python_version,
            "requirement": "3.8+"
        })
        
        # 鏍囧噯搴撴鏌?        stdlib_ok = True
        required_stdlib = ["os", "sys", "json", "statistics", "pathlib"]
        for module in required_stdlib:
            try:
                __import__(module)
                checks.append({
                    "check": f"鏍囧噯搴?{module}",
                    "status": "OK",
                    "message": "鍙敤"
                })
            except ImportError:
                stdlib_ok = False
                checks.append({
                    "check": f"鏍囧噯搴?{module}",
                    "status": "ERROR",
                    "message": "缂哄け"
                })
        
        # MNE妫€鏌?        try:
            import mne
            checks.append({
                "check": "MNE搴?,
                "status": "OK",
                "message": f"鐗堟湰 {mne.__version__}",
                "capability": "瀹屾暣EDF鍒嗘瀽"
            })
        except ImportError:
            checks.append({
                "check": "MNE搴?,
                "status": "INFO",
                "message": "鏈畨瑁?,
                "suggestion": "pip install mne numpy scipy"
            })
        
        # 鏂囦欢绯荤粺妫€鏌?        try:
            test_file = Path(__file__)
            if test_file.exists():
                checks.append({
                    "check": "鏂囦欢绯荤粺璁块棶",
                    "status": "OK",
                    "message": "鍙鍐?
                })
            else:
                checks.append({
                    "check": "鏂囦欢绯荤粺璁块棶",
                    "status": "WARNING",
                    "message": "鍙璁块棶"
                })
        except Exception:
            checks.append({
                "check": "鏂囦欢绯荤粺璁块棶",
                "status": "ERROR",
                "message": "璁块棶鍙楅檺"
            })
        
        return {
            "success": True,
            "command": "env-check",
            "data": {
                "checks": checks,
                "overall_status": "READY",
                "capability": self.capability.value,
                "timestamp": datetime.now().isoformat()
            }
        }
    
    def _analyze_file(self, file_path: str) -> FileAnalysis:
        """鍒嗘瀽鏂囦欢"""
        path = Path(file_path)
        
        if not path.exists():
            return FileAnalysis(
                exists=False,
                file_type=FileType.UNKNOWN,
                size_mb=0,
                extension="",
                is_readable=False
            )
        
        # 鑾峰彇鏂囦欢淇℃伅
        size_mb = path.stat().st_size / (1024 * 1024)
        extension = path.suffix.lower()
        
        # 纭畾鏂囦欢绫诲瀷
        if extension == '.edf':
            file_type = FileType.EDF
        elif extension == '.csv':
            file_type = FileType.CSV
        elif extension == '.txt':
            file_type = FileType.TXT
        else:
            file_type = FileType.UNKNOWN
        
        # 妫€鏌ュ彲璇绘€?        is_readable = False
        line_count = None
        encoding = None
        
        try:
            # 灏濊瘯璇诲彇鏂囦欢
            with open(file_path, 'r', encoding='utf-8') as f:
                # 璇诲彇鍓嶅嚑琛屾鏌?                for i, line in enumerate(f):
                    if i >= 5:  # 鍙鏌ュ墠5琛?                        break
                is_readable = True
                encoding = 'utf-8'
        except UnicodeDecodeError:
            try:
                with open(file_path, 'r', encoding='gbk') as f:
                    for i, line in enumerate(f):
                        if i >= 5:
                            break
                    is_readable = True
                    encoding = 'gbk'
            except:
                is_readable = False
        except:
            is_readable = False
        
        # 濡傛灉鏄枃鏈枃浠讹紝灏濊瘯璁＄畻琛屾暟
        if is_readable and file_type in [FileType.CSV, FileType.TXT]:
            try:
                with open(file_path, 'r', encoding=encoding or 'utf-8') as f:
                    line_count = sum(1 for _ in f)
            except:
                line_count = None
        
        return FileAnalysis(
            exists=True,
            file_type=file_type,
            size_mb=size_mb,
            extension=extension,
            is_readable=is_readable,
            line_count=line_count,
            encoding=encoding
        )
    
    def _format_file_analysis(self, analysis: FileAnalysis) -> Dict[str, Any]:
        """鏍煎紡鍖栨枃浠跺垎鏋愮粨鏋?""
        result = {
            "exists": analysis.exists,
            "file_type": analysis.file_type.value,
            "size_mb": round(analysis.size_mb, 2),
            "extension": analysis.extension,
            "is_readable": analysis.is_readable
        }
        
        if analysis.line_count is not None:
            result["line_count"] = analysis.line_count
        
        if analysis.encoding:
            result["encoding"] = analysis.encoding
        
        return result
    
    def _format_duration(self, seconds: float) -> str:
        """鏍煎紡鍖栨椂闀?""
        if seconds < 60:
            return f"{seconds:.1f}绉?
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f}鍒嗛挓"
        else:
            hours = seconds / 3600
            return f"{hours:.1f}灏忔椂"
    
    def _get_mne_installation_guide(self) -> Dict[str, Any]:
        """鑾峰彇MNE瀹夎鎸囧"""
        return {
            "purpose": "杩涜瀹屾暣鐨凟DF鐫＄湢鏁版嵁鍒嗘瀽",
            "commands": {
                "standard": "pip install mne numpy scipy",
                "china_mirror": "pip install mne numpy scipy -i https://pypi.tuna.tsinghua.edu.cn/simple",
                "verify": "python -c \"import mne; print(f'MNE鐗堟湰: {mne.__version__}')\""
            },
            "steps": [
                "1. 鎵撳紑鍛戒护琛?缁堢",
                "2. 杩愯瀹夎鍛戒护",
                "3. 楠岃瘉瀹夎鏄惁鎴愬姛",
                "4. 閲嶅惎OpenClaw: openclaw gateway restart",
                "5. 閲嶆柊杩愯鐫＄湢鍒嗘瀽鍛戒护"
            ],
            "notes": [
                "闇€瑕丳ython 3.8鎴栨洿楂樼増鏈?,
                "鍙兘闇€瑕佺鐞嗗憳鏉冮檺",
                "瀹夎杩囩▼鍙兘闇€瑕佸嚑鍒嗛挓",
                "瀹夎鍚庡嵆鍙繘琛屽畬鏁寸殑EDF鍒嗘瀽"
            ]
        }
    
    def _get_available_commands(self) -> List[str]:
        """鑾峰彇鍙敤鍛戒护"""
        commands = [
            "sleep-analyze",  # 鐫＄湢鍒嗘瀽锛堟湁MNE鏃跺畬鏁村垎鏋愶紝鏃燤NE鏃舵枃浠堕獙璇侊級
            "stress-check",   # 鍘嬪姏璇勪及锛堢湡瀹炲績鐜囧垎鏋愶級
            "meditation-guide", # 鍐ユ兂鎸囧锛堢湡瀹炴寚瀵兼柟娉曪級
            "file-info",      # 鏂囦欢淇℃伅锛堢湡瀹炴枃浠跺垎鏋愶級
            "hr-analyze",     # 蹇冪巼鏁版嵁鍒嗘瀽锛堜粠鏂囦欢锛?            "skill-info",     # 鎶€鑳戒俊鎭?            "env-check"       # 鐜妫€鏌?        ]
        return commands
    
    def _get_real_functions(self) -> Dict[str, List[str]]:
        """鑾峰彇鐪熷疄鍔熻兘鍒楄〃"""
        return {
            "always_available": [
                "鏂囦欢绯荤粺鍒嗘瀽鍜岄獙璇?,
                "蹇冪巼鏁版嵁缁熻璁＄畻",
                "鍐ユ兂鎸囧鏂规硶",
                "鐜妫€娴嬪拰璇婃柇"
            ],
            "with_mne": [
                "瀹屾暣鐨凟DF鐫＄湢鏁版嵁鍒嗘瀽",
                "EEG淇″彿澶勭悊",
                "鐫＄湢璐ㄩ噺璇勪及",
                "涓撲笟绾у仴搴锋姤鍛?
            ],
            "principle": [
                "鎵€鏈夊姛鑳藉熀浜庣湡瀹炴暟鎹拰璁＄畻",
                "缁濅笉鎻愪緵妯℃嫙鎴栬櫄鍋囧垎鏋?,
                "鏄庣‘璇存槑鍔熻兘闄愬埗鍜岄渶姹?,
                "鎻愪緵娓呮櫚鐨勫崌绾ц矾寰?
            ]
        }
    
    def _get_requirements(self) -> Dict[str, Any]:
        """鑾峰彇闇€姹傝鏄?""
        return {
            "minimum": {
                "python": "3.8+",
                "libraries": "浠呮爣鍑嗗簱",
                "functions": "鍩虹鏂囦欢鍒嗘瀽銆佸績鐜囩粺璁°€佸啣鎯虫寚瀵?
            },
            "recommended": {
                "python": "3.8+",
                "libraries": "MNE, NumPy, SciPy",
                "functions": "瀹屾暣EDF鍒嗘瀽銆侀珮绾у仴搴疯瘎浼?
            },
            "installation": "pip install mne numpy scipy",
            "verification": "杩愯 /env-check 妫€鏌ョ幆澧?
        }
    
    def format_output(self, result: Dict[str, Any], format_type: str = "markdown") -> str:
        """鏍煎紡鍖栬緭鍑?""
        if format_type == "json":
            return json.dumps(result, ensure_ascii=False, indent=2)
        
        # markdown鏍煎紡
        if "error" in result:
            output = [f"## 鉂?閿欒"]
            output.append(f"\n{result['error']}")
            
            if "suggestion" in result:
                output.append(f"\n**寤鸿**: {result['suggestion']}")
            
            if "usage" in result:
                output.append(f"\n**鐢ㄦ硶**: {result['usage']}")
            
            if "example" in result:
                output.append(f"\n**绀轰緥**: {result['example']}")
            
            return "\n".join(output)
        
        if not result.get("success"):
            return f"## 缁撴灉\n\n{str(result)}"
        
        data = result.get("data", {})
        command = result.get("command", "")
        
        output = [f"## 鉁?{command.replace('-', ' ').title()}"]
        
        if "note" in result:
            output.append(f"\n> {result['note']}")
        
        # 鏍规嵁鍛戒护绫诲瀷鏍煎紡鍖栬緭鍑?        if command == "sleep-analyze":
            if "file_info" in data:
                output.append("\n### 鏂囦欢淇℃伅")
                for key, value in data["file_info"].items():
                    output.append(f"- **{key}**: {value}")
            
            if "edf_info" in data:
                output.append("\n### EDF鏂囦欢淇℃伅")
                for key, value in data["edf_info"].items():
                    if isinstance(value, list):
                        output.append(f"- **{key}**: {', '.join(map(str, value[:5]))}{'...' if len(value) > 5 else ''}")
                    else:
                        output.append(f"- **{key}**: {value}")
            
            if "signal_analysis" in data:
                output.append("\n### 淇″彿鍒嗘瀽")
                for key, value in data["signal_analysis"].items():
                    output.append(f"- **{key}**: {value}")
            
            if "next_steps" in data:
                output.append("\n### 涓嬩竴姝?)
                for step in data["next_steps"]:
                    output.append(f"- {step}")
            
            if "installation_guide" in result:
                guide = result["installation_guide"]
                output.append(f"\n### {guide['purpose']}")
                output.append(f"\n**瀹夎鍛戒护**:")
                for name, cmd in guide["commands"].items():
                    output.append(f"- {name}: `{cmd}`")
                output.append(f"\n**姝ラ**:")
                for step in guide["steps"]:
                    output.append(f"  {step}")
        
        elif command == "stress-check" or command == "hr-analyze":
            if "heart_rate_data" in data:
                hr_data = data["heart_rate_data"]
                output.append(f"\n### 蹇冪巼鏁版嵁")
                output.append(f"- **鏁版嵁鐐?*: {hr_data['total_points']} 涓?)
                if "values" in hr_data:
                    output.append(f"- **绀轰緥鍊?*: {', '.join(map(str, hr_data['values']))}")
            
            if "analysis" in data:
                output.append("\n### 鍒嗘瀽缁撴灉")
                for key, value in data["analysis"].items():
                    output.append(f"- **{key}**: {value}")
        
        elif command == "meditation-guide":
            output
            output.append(f"\n### 鐩殑: {data['purpose']}")
            output.append(f"\n### 鏃堕暱: {data['duration']}")
            
            if "preparation" in data:
                output.append("\n### 鍑嗗")
                for item in data["preparation"]:
                    output.append(f"- {item}")
            
            if "steps" in data:
                output.append("\n### 姝ラ")
                for step in data["steps"]:
                    output.append(f"- **{step['time']}**: {step['action']}")
            
            if "tips" in data:
                output.append("\n### 鎻愮ず")
                for tip in data["tips"]:
                    output.append(f"- {tip}")
        
        elif command == "skill-info":
            for key, value in data.items():
                if key == "real_functions" and isinstance(value, dict):
                    output.append("\n### 鐪熷疄鍔熻兘")
                    for category, functions in value.items():
                        output.append(f"\n**{category}**:")
                        for func in functions:
                            output.append(f"- {func}")
                elif key == "requirements" and isinstance(value, dict):
                    output.append("\n### 闇€姹傝鏄?)
                    for req_type, req_info in value.items():
                        output.append(f"\n**{req_type}**:")
                        if isinstance(req_info, dict):
                            for k, v in req_info.items():
                                output.append(f"  - **{k}**: {v}")
                        else:
                            output.append(f"  - {req_info}")
                elif isinstance(value, list):
                    output.append(f"\n### {key.replace('_', ' ').title()}")
                    for item in value:
                        output.append(f"- {item}")
                else:
                    output.append(f"\n**{key.replace('_', ' ')}**: {value}")
        
        elif command == "env-check":
            if "checks" in data:
                output.append("\n### 鐜妫€鏌ョ粨鏋?)
                for check in data["checks"]:
                    status_emoji = {
                        "OK": "鉁?,
                        "INFO": "鈩癸笍",
                        "WARNING": "鈿狅笍",
                        "ERROR": "鉂?
                    }.get(check["status"], "鉂?)
                    
                    output.append(f"{status_emoji} **{check['check']}**: {check['message']}")
                    
                    if "requirement" in check:
                        output.append(f"  (瑕佹眰: {check['requirement']})")
                    if "suggestion" in check:
                        output.append(f"  (寤鸿: {check['suggestion']})")
        
        else:
            # 閫氱敤杈撳嚭
            for key, value in data.items():
                if isinstance(value, dict):
                    output.append(f"\n### {key.replace('_', ' ').title()}")
                    for k, v in value.items():
                        output.append(f"- **{k}**: {v}")
                elif isinstance(value, list):
                    output.append(f"\n### {key.replace('_', ' ').title()}")
                    for item in value:
                        output.append(f"- {item}")
                else:
                    output.append(f"\n**{key.replace('_', ' ')}**: {value}")
        
        # 娣诲姞鎺ㄨ崘淇℃伅
        if "recommendations" in data:
            output.append("\n### 寤鸿")
            for rec in data["recommendations"]:
                output.append(f"- {rec}")
        
        return "\n".join(output)


def create_skill() -> SleepRabbitSkill:
    """鍒涘缓鎶€鑳藉疄渚?""
    return SleepRabbitSkill()


# 鍛戒护琛屾帴鍙?def main():
    parser = argparse.ArgumentParser(description="鐪犲皬鍏旂潯鐪犲仴搴锋妧鑳?- 鐪熷疄鍔熻兘鐗?)
    parser.add_argument("--version", action="store_true", help="鏄剧ず鐗堟湰淇℃伅")
    
    subparsers = parser.add_subparsers(dest="command", help="鍙敤鍛戒护")
    
    # 鐫＄湢鍒嗘瀽
    sleep_parser = subparsers.add_parser("sleep", help="鐫＄湢鍒嗘瀽")
    sleep_parser.add_argument("edf_file", help="EDF鏂囦欢璺緞")
    
    # 鍘嬪姏璇勪及
    stress_parser = subparsers.add_parser("stress", help="鍘嬪姏璇勪及")
    stress_parser.add_argument("hr_data", help="蹇冪巼鏁版嵁锛堥€楀彿鍒嗛殧锛?)
    
    # 鏂囦欢淇℃伅
    file_parser = subparsers.add_parser("file", help="鏂囦欢淇℃伅")
    file_parser.add_argument("file_path", help="鏂囦欢璺緞")
    
    # 鐜妫€鏌?    subparsers.add_parser("env", help="鐜妫€鏌?)
    
    args = parser.parse_args()
    
    skill = SleepRabbitSkill()
    
    if args.version:
        print(f"{skill.name} v{skill.version}")
        print(f"鍘熷垯: 鎵€鏈夊姛鑳介兘鏄湡瀹炵殑锛岀粷涓嶆ā鎷?)
        print(f"妯″紡: {skill.capability.value}")
        return
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == "sleep":
        result = skill._handle_sleep_analyze_real({"edf_file": args.edf_file})
        print(skill.format_output(result))
    elif args.command == "stress":
        result = skill._handle_stress_check_real({"heart_rate_data": args.hr_data})
        print(skill.format_output(result))
    elif args.command == "file":
        result = skill._handle_file_info({"file_path": args.file_path})
        print(skill.format_output(result))
    elif args.command == "env":
        result = skill._handle_env_check({})
        print(skill.format_output(result))


if __name__ == "__main__":
    main()
