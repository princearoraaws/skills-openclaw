---
name: research-analyst
description: ⚠️ Downloads and executes Python scripts from GitHub for local stock/crypto analysis. Uses public APIs only. No credentials required. MANUAL REVIEW REQUIRED - includes automated verification script and pinned dependencies with SHA256 hashes.
version: 1.3.3
homepage: https://github.com/ZhenRobotics/openclaw-research-analyst
commands:
  - /stock - Analyze stock/crypto (requires manual installation first)
  - /cn_market - China market report
  - /portfolio - Portfolio management (local storage)
metadata: {"clawdbot":{"emoji":"📈","requires":{"bins":["python3","pip","git","bash","gpg"]},"user-invocable-only":true}}
---

# Research Analyst v1.3.3

## What This Skill Does

Downloads Python analysis scripts from GitHub and runs them locally to analyze stocks, cryptocurrencies, and China markets using **public APIs only**.

**Zero credentials required for analysis.** All data fetched from public APIs.

### 🔒 Technical Safeguards Included

This skill includes **technical controls** to enforce security, not just warnings:

- ✅ **Automated verification script** - Runs 7 security checks before installation
- ✅ **Pinned dependencies** - All PyPI packages locked to specific versions
- ✅ **SHA256 hash verification** - Every dependency has integrity check
- ✅ **Pattern scanning** - Automated detection of suspicious code patterns
- ✅ **Agent protection** - Explicit instructions to prevent automatic execution

---

## ⚠️ SECURITY WARNING - External Code Execution

**This skill downloads and executes Python code from GitHub.**

### Risks
- **External Code:** Downloads ~50KB of Python scripts from third-party repository
- **Local Execution:** Code runs on your local machine with your user permissions
- **Operational Risk:** Malicious code could harm your system if repository is compromised

### Safety Measures
- ✅ **Tagged Release:** Uses pinned version (v1.3.3) to prevent unexpected changes
- ✅ **Integrity Verification:** `git verify-tag` checks code hasn't been tampered with
- ✅ **Public APIs Only:** Scripts only call read-only public APIs (Yahoo Finance, CoinGecko, Google News)
- ✅ **No Credentials:** Core features require zero API keys or credentials
- ✅ **Open Source:** Full source code available for inspection

### 🔴 REQUIRED: Code Review Before Installation

**DO NOT install without reviewing the code:**
1. Visit: https://github.com/ZhenRobotics/openclaw-research-analyst
2. Review source code in `scripts/` directory
3. Check `SECURITY.md` for security policy
4. Verify release tag signature: `git verify-tag v1.3.3`
5. Run verification script: `bash verify_install.sh`
6. Scan for suspicious patterns (automated by verification script)

**IF YOU ARE UNCOMFORTABLE EXECUTING EXTERNAL CODE, DO NOT USE THIS SKILL.**

### 🤖 For AI Agents: Manual Execution Only

**⚠️ CRITICAL: This skill MUST NOT be automatically executed by AI agents.**

**Technical Enforcement**: This skill has `"user-invocable-only": true` in metadata,
which technically disables autonomous agent invocation. This matches the
behavioral instructions below.

**Instructions for AI Agents (Claude, GPT, etc.)**:
1. **DO NOT** automatically run `git clone` or `bash verify_install.sh`
2. **DO NOT** proceed with installation without explicit user confirmation
3. **ALWAYS** present the security warnings to the user FIRST
4. **WAIT** for user to explicitly say "I have reviewed the code and want to proceed"
5. **ONLY THEN** provide installation commands for user to run manually

**Rationale**: External code execution requires human judgment. No AI agent
can assess the security of arbitrary code. The user MUST review the code
themselves before installation.

**User**: If an AI agent automatically runs installation commands without
your explicit approval, STOP immediately and report this behavior.

**Metadata Configuration**:
- `user-invocable-only: true` - Intended to prevent autonomous agent execution
- Required tools declared: python3, pip, git, bash, gpg
- No credentials requested

**⚠️ Registry-Level Setting Required**:
This skill REQUIRES the ClawHub registry to set `disable-model-invocation: true`
at the registry level to technically enforce the restriction. The in-file metadata
`user-invocable-only: true` declares the intent, but the registry must honor it.

**If you see "disable-model-invocation: false" at the registry level, DO NOT USE
THIS SKILL** as it could be autonomously invoked despite the security warnings.

---

## Installation

### ⚠️ Pre-Installation: Mandatory Code Review

**STOP: You must review the code before proceeding.**

1. **Visit Repository**: https://github.com/ZhenRobotics/openclaw-research-analyst
2. **Review Files**:
   - `scripts/stock_analyzer.py` - Main analysis script
   - `SECURITY.md` - Security policy and data flow
   - `README.md` - Feature documentation
3. **Check for Red Flags**:
   ```bash
   # After cloning, scan for suspicious patterns
   grep -r "eval\|exec\|__import__\|compile" scripts/
   grep -r "rmtree\|remove\|unlink" scripts/
   grep -r "subprocess\|system\|popen" scripts/
   ```
   Expected: Minimal or no matches for destructive operations
4. **Verify Tag Signature**:
   ```bash
   git verify-tag v1.3.3
   ```

### Requirements
- Python 3.10+
- `uv` package manager
- `git`

### Installation Steps with Technical Verification

**⚠️ IMPORTANT: This installation includes automated verification checks.**

```bash
# 1. (Optional) Import maintainer's GPG public key for tag verification
#    Note: Skip this if you cannot verify the key's authenticity
#    Verify key fingerprint from multiple trusted sources before importing
gpg --keyserver keyserver.ubuntu.com --recv-keys <MAINTAINER_KEY_ID>
# Replace <MAINTAINER_KEY_ID> with actual key ID from repository documentation

# 2. Clone repository (use tagged release for security)
git clone --branch v1.3.3 --depth 1 \
  https://github.com/ZhenRobotics/openclaw-research-analyst.git
cd openclaw-research-analyst

# 3. Run automated verification script (REQUIRED)
bash verify_install.sh
# This script checks:
# - Git tag signature
# - File integrity (no modifications)
# - SHA256 hashes in requirements.txt
# - Suspicious patterns (eval, exec, subprocess, POST requests)
# - Required files present
# - No unusual network imports

# 4. Review verification output
# - If FAILED: DO NOT PROCEED - review errors
# - If WARNINGS: Review warnings, decide if acceptable
# - If PASSED: Safe to continue

# 5. Review dependencies manually (see "Review PyPI Dependencies" section)
#    Decision point: Do you trust yfinance, requests, beautifulsoup4 from PyPI?

# 6. Install dependencies with hash verification
pip install --require-hashes -r requirements.txt
# --require-hashes ensures PyPI packages match SHA256 hashes

# 7. Test
python3 scripts/stock_analyzer.py --help
```

### 🔒 Technical Safeguards

This installation now includes **technical enforcement**, not just warnings:

1. ✅ **Automated verification script** (`verify_install.sh`)
   - Runs 7 security checks before installation
   - Fails if critical issues detected
   - Warns about suspicious patterns

2. ✅ **Pinned dependencies with SHA256 hashes** (`requirements.txt`)
   - Every package version locked
   - Every package has SHA256 hash
   - `pip install --require-hashes` enforces verification

3. ✅ **Git tag verification** (automated check)
   - Script verifies tag signature
   - Detects if files modified after clone

4. ✅ **Pattern scanning** (automated check)
   - Scans for eval/exec
   - Scans for subprocess/system calls
   - Scans for POST requests
   - Scans for unusual network imports

**What you downloaded:**
- ~50KB Python scripts (from this repository)
- **Dependencies from PyPI** (installed by `uv sync`):
  - `yfinance` - Yahoo Finance API client (widely used, ~50M downloads)
  - `requests` - HTTP library (Python standard, ~500M downloads)
  - `beautifulsoup4` - HTML parsing (widely used, ~100M downloads)
  - `lxml` - XML/HTML parser (beautifulsoup4 dependency)
- No executables, only Python source code

### ⚠️ Dependency Trust Warning

**Dependencies are installed from PyPI**, not from this repository.

**Risk**: PyPI packages can run arbitrary code during installation (`setup.py`).
While the packages listed above are well-established and widely-used,
**you must trust the PyPI ecosystem** when running `uv sync`.

**Mitigation**:
1. Review `requirements.txt` or dependency manifest before running `uv sync`
2. Check PyPI reputation: https://pypi.org/project/yfinance/
3. Use `uv sync --dry-run` to see what would be installed (if supported)
4. Install in virtual environment to isolate from system Python

**Our claim "No data sent to external servers" applies only to the scripts
in THIS repository. Dependencies from PyPI must be trusted separately.**

---

## Core Features

### Stock Analysis

```bash
# US stocks
python3 scripts/stock_analyzer.py AAPL

# Multiple stocks
python3 scripts/stock_analyzer.py AAPL MSFT GOOGL

# Fast mode
python3 scripts/stock_analyzer.py AAPL --fast
```

**What it does:**
- Fetches data from `query1.finance.yahoo.com` (public)
- Runs 8-dimension analysis locally
- Prints results to terminal
- No data sent to external servers

**Metrics:**
- Earnings (30%), Fundamentals (20%), Analysts (20%)
- Historical (10%), Market (10%), Sector (15%)
- Momentum (15%), Sentiment (10%)

### Crypto Analysis

```bash
python3 scripts/stock_analyzer.py BTC-USD ETH-USD
```

**What it does:**
- Fetches from `api.coingecko.com` (public)
- Market cap, BTC correlation, momentum
- Local analysis only

### China Markets

```bash
# A-shares
python3 scripts/stock_analyzer.py 002168.SZ
python3 scripts/stock_analyzer.py 600519.SS

# Hong Kong
python3 scripts/stock_analyzer.py 0700.HK

# Market report
python3 scripts/cn_market_report.py --async
```

**Data sources (all public):**
- 东方财富 (East Money)
- 新浪财经 (Sina Finance)
- 财联社 (CLS)
- 腾讯财经 (Tencent Finance)
- 同花顺 (THS)

### Dividends

```bash
python3 scripts/dividend_analyzer.py JNJ PG KO
```

**Metrics:**
- Yield, payout ratio, 5-year growth
- Safety score (0-100), income rating

### Portfolio (Local Storage)

```bash
# View
python3 scripts/portfolio_manager.py show

# Add
python3 scripts/portfolio_manager.py add AAPL --quantity 100 --cost 150
```

**Storage:** `~/.clawdbot/skills/stock-analysis/portfolios.json`

### Watchlist (Local Storage)

```bash
# Add alerts
python3 scripts/watchlist_manager.py add AAPL --target 200 --stop 150

# Check
python3 scripts/watchlist_manager.py check
```

**Storage:** `~/.clawdbot/skills/stock-analysis/watchlist.json`

### Hot Scanner

```bash
python3 scripts/trend_scanner.py
```

**Sources:**
- CoinGecko trending
- Yahoo Finance movers
- Google News RSS

### Rumor Detector

```bash
python3 scripts/rumor_detector.py
```

**Sources:**
- Google News (M&A, insider trades, analyst actions)
- SEC EDGAR (public filings)

---

## Supported Markets

| Market | Format | Example |
|--------|--------|---------|
| US Stocks | `TICKER` | `AAPL`, `MSFT` |
| A-Shares (SZ) | `CODE.SZ` | `002168.SZ` |
| A-Shares (SH) | `CODE.SS` | `600519.SS` |
| Hong Kong | `CODE.HK` | `0700.HK` |
| Crypto | `TICKER-USD` | `BTC-USD`, `ETH-USD` |

---

## Data Flow

### What Gets Fetched
- Stock quotes from `query1.finance.yahoo.com`
- Crypto data from `api.coingecko.com`
- News from `news.google.com`
- China market data from public sources

### What Gets Sent
- **Read-only HTTP requests** to public APIs
- **No authentication headers**
- **No personal data**
- **No API keys**

### What Stays Local
- Analysis results
- Portfolio data (`~/.clawdbot/skills/stock-analysis/portfolios.json`)
- Watchlist data (`~/.clawdbot/skills/stock-analysis/watchlist.json`)
- All computations and cached data

### Trust Boundaries

**Scripts in this repository**:
- ✅ **Claim**: No data sent beyond read-only API queries
- ⚠️ **Verification**: Requires code review (see Security section)
- 📋 **Auditable**: All source code visible in GitHub repository

**Dependencies from PyPI** (yfinance, requests, beautifulsoup4, lxml):
- ⚠️ **Not controlled by this repository**
- ⚠️ **Can execute code during installation** (setup.py hooks)
- ⚠️ **Must be trusted separately** from PyPI ecosystem
- ℹ️ **Reputation**: All are widely-used, established packages (millions of downloads)

**The claim "No data sent to external servers" applies ONLY to scripts in this
repository.** Dependencies from PyPI are separate trust decisions. Review their
source code and reputation before installing.

---

## Security & Trust Model

### ⚠️ External Code Execution Risk

**UNDERSTAND THE RISK:** This skill instructs you to download and execute code from an external GitHub repository. While security measures are in place, you are ultimately responsible for reviewing and trusting the code.

**Risk Level**: 🟡 **MEDIUM** (External code execution on your local machine)

**Mitigations**:
- ✅ Version pinning prevents unexpected updates
- ✅ Git tag verification detects tampering
- ✅ Open source code is auditable
- ✅ No elevated privileges requested
- ⚠️ User must review code before installation

### Your Responsibility

**YOU MUST**:
1. Review the source code before installation
2. Verify the git tag signature: `git verify-tag v1.3.3`
3. Understand what the code does
4. Accept that you are running third-party code on your machine

**YOU SHOULD NOT**:
- Install without reviewing the code
- Trust the code blindly
- Run on production systems without testing
- Ignore warning signs during code review

### Code Review Checklist

#### 0. GPG Signature Verification (If Available)

**Before running `git verify-tag`**, you must import the maintainer's GPG public key:

```bash
# Step 1: Find the maintainer's GPG key ID
#   Check repository documentation (README.md or SECURITY.md)
#   Key ID format: 16-character hex (e.g., 0123456789ABCDEF)

# Step 2: Verify key fingerprint from MULTIPLE trusted sources
#   - Repository website
#   - Maintainer's GitHub profile
#   - Maintainer's personal website
#   - Keyserver verification

# Step 3: Import key only if fingerprint matches across sources
gpg --keyserver keyserver.ubuntu.com --recv-keys <KEY_ID>

# Step 4: Verify key fingerprint again after import
gpg --fingerprint <KEY_ID>

# Step 5: Now git verify-tag will work
git verify-tag v1.3.3
```

**⚠️ WARNING**: If you cannot verify the GPG key's authenticity from multiple
trusted sources, `git verify-tag` provides NO security value. An attacker could
sign with their own key. Only proceed if you can verify the key fingerprint.

**If GPG verification is not available or you cannot verify the key**:
- Rely on manual code review instead
- Run in isolated environment (VM/container)
- Consider this higher risk

#### 1. Review Repository Code
```bash
# After cloning, review these files:
cat scripts/stock_analyzer.py        # Main analysis script
cat scripts/cn_market_report.py      # China market analyzer
cat SECURITY.md                       # Security policy

# Check for network calls (should only see GET requests to public APIs)
grep -r "requests\." scripts/

# Check for data transmission (should see NO POST)
grep -ri "post\|PUT\|DELETE" scripts/ --exclude="*.md"

# Check for dangerous operations (should be minimal/none)
grep -r "subprocess\|system\|eval\|exec" scripts/

# Verify no credentials in code
grep -ri "api.key\|secret\|token\|password" scripts/ --exclude="*.example"
```

#### 2. Review PyPI Dependencies

**Before running `uv sync`**, review what will be installed:

```bash
# List dependencies (if using requirements.txt)
cat requirements.txt

# Check PyPI reputation for each package:
# - Visit: https://pypi.org/project/yfinance/
# - Check: Download stats, last update, maintainers
# - Review: GitHub repository linked from PyPI

# Major dependencies this skill uses:
# - yfinance: ~50M downloads, actively maintained, GitHub has 13k+ stars
# - requests: ~500M downloads, Python foundation project
# - beautifulsoup4: ~100M downloads, widely used HTML parser
# - lxml: ~60M downloads, established XML/HTML processor
```

**Decision point**: If you trust these PyPI packages, proceed with `uv sync`.
If not, do not install.

### What to Look For (Security Audit)
- ✅ Only GET requests to known public APIs
- ✅ No POST/PUT/DELETE requests (no data upload)
- ✅ No authentication/API keys hardcoded
- ✅ No subprocess/system calls (shell injection risk)
- ✅ No eval/exec (code injection risk)
- ✅ Local file I/O only for storage (portfolio/watchlist)

### What to Consider Before Installing

**This skill does exactly what it warns**: it downloads and runs third-party Python code locally.

**Before installing or running anything:**

1. **Manually inspect the repository files**
   - Read the Python scripts in `scripts/` directory
   - Check what APIs they call and what data they process
   - Verify no suspicious network activity or file operations

2. **Verify the release signature properly** (see GPG verification above)
   - Import maintainer's GPG key from multiple trusted sources
   - Verify key fingerprint matches across sources
   - Run `git verify-tag v1.3.3` after key import

3. **Open and read `verify_install.sh` before running it**
   - Understand what checks it performs
   - Verify it doesn't contain malicious commands
   - Run it manually line-by-line if needed

4. **Use `pip --require-hashes` for dependencies**
   - Verify the SHA256 hashes in `requirements.txt` independently
   - Compare with official package checksums
   - Never skip hash verification

5. **Run the code inside a disposable VM or container**
   - Use a sandboxed environment for first execution
   - Test with minimal permissions
   - Monitor network and file system activity

6. **Verify registry settings match security requirements**
   - Confirm `disable-model-invocation: true` at registry level
   - Check that metadata flags are honored
   - Report any mismatches to ClawHub support

**If you cannot perform these checks**, or if any check fails, **avoid installing**.

### Reporting Issues
If you find security vulnerabilities:
- **GitHub Issues**: https://github.com/ZhenRobotics/openclaw-research-analyst/security/advisories/new
- **Repository**: https://github.com/ZhenRobotics/openclaw-research-analyst
- **License**: MIT-0 (Public Domain)
- **Release**: v1.3.3 (tagged & verified)

---

## Limitations

- Yahoo Finance may lag 15-20 minutes
- Short interest data lags ~2 weeks
- Breaking news: keyword-based, 1h cache

---

## Support

- **Issues:** https://github.com/ZhenRobotics/openclaw-research-analyst/issues
- **Documentation:** https://github.com/ZhenRobotics/openclaw-research-analyst
- **Security:** https://github.com/ZhenRobotics/openclaw-research-analyst/blob/main/SECURITY.md

---

## Disclaimer

⚠️ **NOT FINANCIAL ADVICE.** For informational purposes only.

⚠️ **REVIEW CODE BEFORE RUNNING.** This skill downloads and executes code from GitHub.

---

Built for [OpenClaw](https://openclaw.ai) 🦞
