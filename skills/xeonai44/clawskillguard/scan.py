#!/usr/bin/env python3
"""
ClawSkillGuard — OpenClaw Skill Security Scanner
100% local. Zero network calls.
"""

import os
import re
import sys
import json
import hashlib
import argparse
from pathlib import Path
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Optional


class Severity(Enum):
    CLEAN = "clean"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

    def __lt__(self, other):
        order = [Severity.CLEAN, Severity.LOW, Severity.MEDIUM, Severity.HIGH, Severity.CRITICAL]
        return order.index(self) < order.index(other)


SEVERITY_ICONS = {
    Severity.CLEAN: "✅",
    Severity.LOW: "🟢",
    Severity.MEDIUM: "🟡",
    Severity.HIGH: "🟠",
    Severity.CRITICAL: "🔴",
}


@dataclass
class Finding:
    severity: Severity
    category: str
    file: str
    line: Optional[int]
    pattern: str
    description: str
    recommendation: str
    snippet: str = ""


@dataclass
class ScanResult:
    skill_path: str
    skill_name: str
    findings: list = field(default_factory=list)
    files_scanned: int = 0
    errors: list = field(default_factory=list)

    @property
    def max_severity(self) -> Severity:
        if not self.findings:
            return Severity.CLEAN
        return max(f.severity for f in self.findings)

    @property
    def verdict(self) -> str:
        sev = self.max_severity
        if sev == Severity.CRITICAL:
            return "❌ DO NOT INSTALL — Critical threats detected"
        elif sev == Severity.HIGH:
            return "⚠️ REVIEW NEEDED — Suspicious patterns found"
        elif sev == Severity.MEDIUM:
            return "⚠️ REVIEW NEEDED — Some concerns detected"
        elif sev == Severity.LOW:
            return "✅ SAFE TO INSTALL — Minor concerns only"
        return "✅ CLEAN — No threats detected"


# ─── Detection Rules ──────────────────────────────────────────────

# SKILL.md prompt injection patterns
SKILL_INJECTION_PATTERNS = [
    # Hidden instructions
    (r'<span[^>]*style=["\'].*display:\s*none.*["\'].*>', Severity.HIGH, "Hidden HTML content in markdown"),
    (r'\u200b|\u200c|\u200d|\ufeff', Severity.HIGH, "Zero-width characters detected (possible hidden text)"),
    (r'<!--[\s\S]*?-->', Severity.MEDIUM, "HTML comment — may contain hidden instructions"),
    
    # System prompt override attempts
    (r'ignore\s+(all\s+)?(previous|prior|above|system)\s+(instructions?|prompts?|rules?)', Severity.CRITICAL, "Attempt to override system instructions"),
    (r'disregard\s+(all\s+)?(previous|prior|above|system)', Severity.CRITICAL, "Attempt to disregard system prompts"),
    (r'you\s+are\s+now\s+(a\s+)?(different|new|another)', Severity.HIGH, "Attempt to redefine agent identity"),
    (r'forget\s+(everything|all)\s+(you|that)\s+(know|learned)', Severity.HIGH, "Attempt to reset agent context"),
    (r'new\s+(system\s+)?prompt', Severity.CRITICAL, "Attempt to inject new system prompt"),
    (r'<\|im_start\|>|<\|im_end\|>', Severity.CRITICAL, "Chat template injection tokens"),
    
    # Data exfiltration
    (r'(send|post|upload|transmit|exfiltrate|leak)\s+.*(contents?|data|files?|tokens?|keys?|secrets?|credentials?)', Severity.CRITICAL, "Potential data exfiltration instruction"),
    (r'(curl|wget|fetch)\s+.*\$\{|http[s]?://.*\$\{', Severity.CRITICAL, "Dynamic URL construction (potential data exfil)"),
    (r'report\s+.*(to|at)\s+(http|url|endpoint|server|webhook)', Severity.CRITICAL, "Reporting to external endpoint"),
    
    # Credential access prompts
    (r'(read|access|grab|collect|gather|steal)\s+.*(\.env|\.ssh|\.aws|\.config|password|token|secret|credential|api.?key)', Severity.CRITICAL, "Prompt to access credentials"),
    (r'(cat|read|open)\s+.*(~\/|\$\{?HOME)?\/?\.(env|ssh|aws|gnupg|npmrc|pip)', Severity.CRITICAL, "Prompt to read sensitive config files"),
]

# Script file malicious patterns
SCRIPT_MALICIOUS_PATTERNS = [
    # Shell/network
    (r'bash\s+-i\s+>&\s*/dev/(tcp|udp)', Severity.CRITICAL, "Reverse shell attempt"),
    (r'nc\s+.*-[el]\s+', Severity.CRITICAL, "Netcat listener (possible backdoor)"),
    (r'ncat\s+.*-[el]\s+', Severity.CRITICAL, "Ncat listener (possible backdoor)"),
    (r'socat\s+.*exec', Severity.CRITICAL, "Socat with exec (possible shell)"),
    (r'python.*socket.*connect', Severity.HIGH, "Python socket connection"),
    (r'os\.system\s*\(', Severity.HIGH, "Direct OS command execution"),
    (r'subprocess\.(call|run|Popen|check_output).*shell\s*=\s*True', Severity.HIGH, "Shell injection risk (shell=True)"),
    
    # Credential theft
    (r'(cat|read|open|load)\s+.*\.env', Severity.CRITICAL, "Reading .env files"),
    (r'(cat|read|open|load)\s+.*\.ssh/', Severity.CRITICAL, "Reading SSH keys"),
    (r'(cat|read|open|load)\s+.*\.(aws|gnupg|npmrc|pip/)', Severity.CRITICAL, "Reading sensitive config"),
    (r'os\.environ', Severity.MEDIUM, "Accessing environment variables"),
    (r'process\.env', Severity.MEDIUM, "Accessing environment variables"),
    (r'(localStorage|sessionStorage|document\.cookie)', Severity.MEDIUM, "Accessing browser storage/cookies"),
    
    # Destructive commands
    (r'rm\s+(-rf?|--recursive)\s+/', Severity.CRITICAL, "Recursive deletion from root"),
    (r'rm\s+(-rf?|--recursive)\s+\$\{?(HOME|PWD|USER)', Severity.CRITICAL, "Recursive deletion of home/pwd"),
    (r'(format|mkfs|wipefs|shred|dd\s+if=)', Severity.CRITICAL, "Disk destruction/formatting"),
    (r'chmod\s+777', Severity.HIGH, "Overly permissive file permissions"),
    (r'chown\s+-R\s+root', Severity.HIGH, "Recursive ownership change to root"),
    
    # Cryptomining
    (r'(xmrig|minerd|cgminer|ethminer|nicehash)', Severity.CRITICAL, "Cryptocurrency miner detected"),
    (r'stratum\+tcp', Severity.CRITICAL, "Mining pool connection"),
    
    # Downloads and execution
    (r'curl\s+.*\|\s*(ba)?sh', Severity.CRITICAL, "Piping download to shell"),
    (r'wget\s+.*\|\s*(ba)?sh', Severity.CRITICAL, "Piping download to shell"),
    (r'curl\s+.*-o\s+.*\s+&&\s+.*(chmod|bash|sh|python|node)', Severity.HIGH, "Download and execute"),
    (r'wget\s+.*-O\s+.*\s+&&\s+.*(chmod|bash|sh|python|node)', Severity.HIGH, "Download and execute"),
    (r'Invoke-WebRequest.*\|\s*(iex|Invoke-Expression)', Severity.CRITICAL, "PowerShell download and execute"),
    (r'Invoke-Expression|IEX\s*\(', Severity.HIGH, "PowerShell dynamic execution"),
    
    # Obfuscation
    (r'base64\s+(-d|--decode)\s*\|', Severity.HIGH, "Base64 decode piped to shell"),
    (r'eval\s*\(', Severity.HIGH, "Dynamic code evaluation (eval)"),
    (r'exec\s*\(', Severity.HIGH, "Dynamic code execution (exec)"),
    (r'Function\s*\(\s*["\']return\s+["\']', Severity.HIGH, "JavaScript Function constructor (obfuscation)"),
    (r'\\x[0-9a-fA-F]{2}\\x[0-9a-fA-F]{2}\\x[0-9a-fA-F]{2}', Severity.HIGH, "Hex-encoded strings (possible obfuscation)"),
    (r'String\.fromCharCode\s*\(', Severity.MEDIUM, "Character code obfuscation"),
    (r'atob\s*\(', Severity.MEDIUM, "Base64 decode (atob)"),
    
    # Privilege escalation
    (r'sudo\s+', Severity.MEDIUM, "Uses sudo"),
    (r'setuid|setgid', Severity.HIGH, "Setuid/setgid operation"),
    (r'chmod\s+[4-7][0-9]{3}', Severity.MEDIUM, "Setuid/setgid permission"),
    
    # Data exfil via HTTP
    (r'(requests|urllib|http\.client|axios|fetch|got|node-fetch).*\.(post|put|patch)\s*\(', Severity.HIGH, "Outbound HTTP POST (potential data exfil)"),
    (r'(curl|wget).*-X\s+POST', Severity.HIGH, "Outbound HTTP POST via CLI"),
    
    # Cron/persistence
    (r'(crontab|systemctl|launchctl)\s+', Severity.HIGH, "System service/cron manipulation"),
    (r'/etc/cron', Severity.HIGH, "Modifying system cron"),
]

# Suspicious imports
SUSPICIOUS_IMPORTS = [
    (r'import\s+socket', Severity.MEDIUM, "Network socket access"),
    (r'import\s+subprocess', Severity.MEDIUM, "Process spawning"),
    (r'import\s+os', Severity.LOW, "OS access"),
    (r'from\s+os\s+import\s+system', Severity.HIGH, "Direct OS command execution"),
    (r'import\s+pickle', Severity.MEDIUM, "Pickle deserialization (can execute arbitrary code)"),
    (r'import\s+marshal', Severity.MEDIUM, "Marshal deserialization"),
    (r'import\s+ctypes', Severity.HIGH, "Low-level C access via ctypes"),
    (r'require\s*\(\s*["\']child_process["\']\s*\)', Severity.MEDIUM, "Node.js child process access"),
    (r'require\s*\(\s*["\']fs["\']\s*\)', Severity.LOW, "Node.js filesystem access"),
    (r'require\s*\(\s*["\']net["\']\s*\)', Severity.MEDIUM, "Node.js network access"),
    (r'require\s*\(\s*["\']http["\']\s*\)|require\s*\(\s*["\']https["\']\s*\)', Severity.MEDIUM, "Node.js HTTP client"),
]


def scan_file_patterns(filepath: Path, patterns: list, category: str) -> list:
    """Scan a file against a list of regex patterns."""
    findings = []
    try:
        content = filepath.read_text(errors='replace')
        lines = content.splitlines()
        
        for pattern, severity, description in patterns:
            for line_num, line in enumerate(lines, 1):
                if re.search(pattern, line, re.IGNORECASE):
                    findings.append(Finding(
                        severity=severity,
                        category=category,
                        file=str(filepath),
                        line=line_num,
                        pattern=pattern,
                        description=description,
                        recommendation=f"Review line {line_num}: {line.strip()[:120]}",
                        snippet=line.strip()[:200],
                    ))
    except Exception as e:
        findings.append(Finding(
            severity=Severity.LOW,
            category="scan_error",
            file=str(filepath),
            line=None,
            pattern="",
            description=f"Could not scan file: {e}",
            recommendation="Manual review recommended",
        ))
    return findings


def get_file_hash(filepath: Path) -> str:
    """Get SHA256 hash of a file."""
    try:
        return hashlib.sha256(filepath.read_bytes()).hexdigest()
    except:
        return "unknown"


def scan_skill(skill_path: str, min_severity: Severity = Severity.LOW) -> ScanResult:
    """Scan an OpenClaw skill directory."""
    skill_dir = Path(skill_path).resolve()
    skill_name = skill_dir.name
    result = ScanResult(
        skill_path=str(skill_dir),
        skill_name=skill_name,
    )
    
    if not skill_dir.exists():
        result.errors.append(f"Path does not exist: {skill_dir}")
        return result
    
    # Files to skip
    skip_dirs = {'.git', 'node_modules', '__pycache__', '.venv', 'venv', '.env', 'dist', 'build'}
    skip_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.ico', '.woff', '.woff2', '.ttf', '.eot', '.mp3', '.mp4', '.wav', '.zip', '.tar', '.gz', '.pdf', '.doc', '.docx'}
    
    # Scan all files
    for root, dirs, files in os.walk(skill_dir):
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        
        for fname in files:
            filepath = Path(root) / fname
            
            # Skip binary files
            if filepath.suffix.lower() in skip_extensions:
                continue
            
            result.files_scanned += 1
            
            # SKILL.md — prompt injection scan
            if fname.upper() == 'SKILL.md':
                findings = scan_file_patterns(filepath, SKILL_INJECTION_PATTERNS, "prompt_injection")
                result.findings.extend(findings)
            
            # Script files — malicious pattern scan
            script_extensions = {'.py', '.js', '.ts', '.sh', '.bash', '.zsh', '.ps1', '.rb', '.pl', '.php', '.go', '.rs', '.c', '.cpp', '.h', '.hpp'}
            if filepath.suffix.lower() in script_extensions or (fname.startswith('scan') or fname.startswith('install') or fname.startswith('setup') or fname.startswith('run')):
                findings = scan_file_patterns(filepath, SCRIPT_MALICIOUS_PATTERNS, "malicious_code")
                result.findings.extend(findings)
                
                # Also check imports
                import_findings = scan_file_patterns(filepath, SUSPICIOUS_IMPORTS, "suspicious_import")
                result.findings.extend(import_findings)
            
            # Config files
            config_extensions = {'.json', '.yaml', '.yml', '.toml', '.env', '.ini', '.cfg'}
            if filepath.suffix.lower() in config_extensions and fname != 'SKILL.md':
                findings = scan_file_patterns(filepath, SCRIPT_MALICIOUS_PATTERNS, "config_analysis")
                result.findings.extend(findings)
    
    # Filter by minimum severity
    severity_order = [Severity.LOW, Severity.MEDIUM, Severity.HIGH, Severity.CRITICAL]
    min_idx = severity_order.index(min_severity) if min_severity in severity_order else 0
    result.findings = [f for f in result.findings if severity_order.index(f.severity) >= min_idx]
    
    return result


def format_text_report(result: ScanResult) -> str:
    """Format scan results as human-readable text."""
    lines = []
    lines.append(f"{'='*60}")
    lines.append(f"🛡️  ClawGuard Security Scan Report")
    lines.append(f"{'='*60}")
    lines.append(f"")
    lines.append(f"📁 Skill: {result.skill_name}")
    lines.append(f"📂 Path:  {result.skill_path}")
    lines.append(f"📄 Files: {result.files_scanned} scanned")
    lines.append(f"")
    
    if result.errors:
        lines.append(f"⚠️  Errors:")
        for err in result.errors:
            lines.append(f"   • {err}")
        lines.append(f"")
    
    if not result.findings:
        lines.append(f"✅ No security issues detected.")
        lines.append(f"")
        lines.append(f"Verdict: {result.verdict}")
        return "\n".join(lines)
    
    # Group by severity
    by_severity = {}
    for f in result.findings:
        if f.severity not in by_severity:
            by_severity[f.severity] = []
        by_severity[f.severity].append(f)
    
    # Print findings by severity (critical first)
    for sev in [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW]:
        if sev not in by_severity:
            continue
        icon = SEVERITY_ICONS[sev]
        findings = by_severity[sev]
        lines.append(f"{icon} {sev.value.upper()} ({len(findings)} finding{'s' if len(findings) != 1 else ''})")
        lines.append(f"{'-'*40}")
        for f in findings:
            rel_file = f.file.replace(result.skill_path, ".")
            lines.append(f"  📄 {rel_file}:{f.line or '?'}")
            lines.append(f"     {f.description}")
            if f.snippet:
                snippet = f.snippet[:100] + ("..." if len(f.snippet) > 100 else "")
                lines.append(f"     > {snippet}")
            lines.append(f"")
    
    lines.append(f"{'='*60}")
    lines.append(f"Verdict: {result.verdict}")
    lines.append(f"{'='*60}")
    
    return "\n".join(lines)


def format_json_report(result: ScanResult) -> str:
    """Format scan results as JSON."""
    data = {
        "skill_name": result.skill_name,
        "skill_path": result.skill_path,
        "files_scanned": result.files_scanned,
        "max_severity": result.max_severity.value,
        "verdict": result.verdict,
        "finding_count": len(result.findings),
        "findings": [
            {
                "severity": f.severity.value,
                "category": f.category,
                "file": f.file,
                "line": f.line,
                "pattern": f.pattern,
                "description": f.description,
                "snippet": f.snippet,
            }
            for f in result.findings
        ],
        "errors": result.errors,
    }
    return json.dumps(data, indent=2)


def main():
    parser = argparse.ArgumentParser(
        description="ClawGuard — OpenClaw Skill Security Scanner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  scan.py ~/.openclaw/skills/my-skill
  scan.py ~/.openclaw/workspace/skills/clawguard --format json
  scan.py ~/.openclaw/skills/ --severity high
        """,
    )
    parser.add_argument("path", help="Path to skill directory or parent directory to scan")
    parser.add_argument("--format", choices=["text", "json"], default="text", help="Output format")
    parser.add_argument("--severity", choices=["low", "medium", "high", "critical"], default="low",
                        help="Minimum severity to report")
    parser.add_argument("--all", action="store_true", help="Scan all skills in parent directory")
    
    args = parser.parse_args()
    min_severity = Severity(args.severity)
    scan_path = Path(args.path).resolve()
    
    if not scan_path.exists():
        print(f"❌ Path does not exist: {scan_path}", file=sys.stderr)
        sys.exit(1)
    
    # Scan all skills in directory
    if args.all or scan_path.is_dir() and not (scan_path / "SKILL.md").exists():
        skill_dirs = [d for d in scan_path.iterdir() if d.is_dir() and (d / "SKILL.md").exists()]
        if not skill_dirs:
            # Maybe it's a single skill
            if (scan_path / "SKILL.md").exists():
                skill_dirs = [scan_path]
            else:
                print(f"❌ No skills found in: {scan_path}", file=sys.stderr)
                sys.exit(1)
        
        all_results = []
        for skill_dir in sorted(skill_dirs):
            result = scan_skill(str(skill_dir), min_severity)
            all_results.append(result)
            
            if args.format == "text":
                print(format_text_report(result))
                print()
        
        if args.format == "json":
            print(json.dumps([json.loads(format_json_report(r)) for r in all_results], indent=2))
        
        # Summary
        if len(all_results) > 1 and args.format == "text":
            print(f"\n{'='*60}")
            print(f"📊 Summary: {len(all_results)} skills scanned")
            for r in all_results:
                icon = SEVERITY_ICONS[r.max_severity]
                print(f"  {icon} {r.skill_name}: {r.max_severity.value}")
            print(f"{'='*60}")
    
    else:
        # Single skill scan
        result = scan_skill(str(scan_path), min_severity)
        if args.format == "json":
            print(format_json_report(result))
        else:
            print(format_text_report(result))


if __name__ == "__main__":
    main()
