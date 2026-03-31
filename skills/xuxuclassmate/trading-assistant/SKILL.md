---
name: trading-assistant
description: Technical analysis and trading signal generator for stocks and cryptocurrencies (no auto-trading)
version: 1.5.1
author: OpenClaw Community
license: MIT
category: Finance
tags:
  - trading
  - finance
  - technical-analysis
  - stock-market
  - investment
  - openclaw
metadata:
  openclaw:
    requires:
      env:
        - TWELVE_DATA_API_KEY
        - ALPHA_VANTAGE_API_KEY
      bins:
        - python3
        - pip
    primaryEnv: TWELVE_DATA_API_KEY
    emoji: 📊
    homepage: https://github.com/XuXuClassMate/trading-assistant
---

# 📊 Trading Assistant

**Version**: v1.5.1 | **License**: MIT

A **read-only trading analysis tool** that provides technical indicators, market signals, and position sizing suggestions.  
🚫 This skill does **NOT execute trades**, manage funds, or interact with brokerage accounts.

---

## 🔐 Security & Transparency

To ensure safety and clarity:

- ✅ **No trading execution**: This tool does not place orders or connect to trading accounts  
- ✅ **No fund access**: No wallet, exchange, or brokerage integration  
- ✅ **No data exfiltration**: API keys are used locally only for market data retrieval  
- ✅ **No hidden behavior**: All functionality is fully visible in source code  
- ✅ **No background tasks**: No schedulers, hooks, or real-time trading triggers  

📌 External API usage:
- `TWELVE_DATA_API_KEY` → Market data (price, indicators)
- `ALPHA_VANTAGE_API_KEY` → Market data (backup source)

---

## ✨ Features

- **Technical Indicators**: RSI, MACD, Bollinger Bands, KDJ, CCI, ADX, ATR, OBV, VWAP  
- **Trading Signals**: BUY / SELL / HOLD suggestions with confidence score  
- **Position Sizing**: Risk-based position calculator (manual decision support only)  
- **Support/Resistance**: Key level detection  
- **Multi-Market**: A-shares, US stocks, crypto  

---

## ⚠️ Important Clarification

This tool is strictly:

👉 **Analysis + Decision Support only**

It does NOT:
- Execute trades  
- Connect to exchanges  
- Store or transmit user credentials  
- Perform automated trading  

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
