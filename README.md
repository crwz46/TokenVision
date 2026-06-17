# TokenVision

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-brightgreen)](LICENSE)

Analyze token holder concentration, detect whales, and assess centralization risk — all from your terminal.

## Features

| Feature | Description |
|---------|-------------|
| 🐋 **Whale Detection** | Top holders & their concentration |
| 📊 **Concentration Metrics** | HHI Index, Gini Coefficient, Top-N % |
| 🚨 **Risk Assessment** | HIGH / MODERATE / LOW centralization |
| 📈 **Charts** | Pie chart, bar chart, Lorenz curve (matplotlib) |
| 🪙 **10+ Tokens** | Built-in data for USDC, UNI, SHIB, PEPE, LINK, etc |

## Quick Start

```bash
pip install -r requirements.txt
python main.py UNI
```

## Usage

```bash
# Analyze any token
python main.py UNI
python main.py SHIB
python main.py PEPE

# Generate charts
python main.py UNI --charts

# List available tokens
python main.py --list
```

## Example Output

```
======================================================================
  🟢 TOKENVISION — UNI
======================================================================

  Token       : Uniswap (UNI)
  Supply      : 1,000,000,000

  ────────────────────────────────────────
  CONCENTRATION
  ────────────────────────────────────────
  Top 1       :  13.56%
  Top 5       :  50.64%
  Top 10      :  72.54%
  HHI         :   0.0761
  Gini        :   0.4069
  Eff. Holders:     13.1

  Risk        : 🟢 LOW CONCENTRATION

  TOP 10:
  Rank  Address                                          Hold     Label
  ───── ──────────────────────────────────────────── ──────── ──────────
     1. 0x0000...3456                               13.56%   🐋 Whale
     2. 0x0000...d811                               13.31%   🐳 Mega Whale
     3. 0x0000...7807                               12.51%   🦈 Shark
  ...
======================================================================
```

## Charts

With `--charts`, generates:

| Chart | Description |
|-------|-------------|
| 🥧 Pie | Top 10 holders vs others |
| 📊 Bar | Top 20 holders comparison |
| 📈 Lorenz | Wealth distribution curve |

## Project Structure

```
TokenVision/
├── main.py
├── tokenvision/
│   ├── __init__.py
│   ├── cli.py
│   ├── analyzer.py     # Core analytics engine
│   └── charts.py       # matplotlib visualization
├── tests/
│   └── test_tokenvision.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Tests

```bash
pytest tests/ -v
```

## Why Recruiters Love This

| Skill | Shown |
|-------|-------|
| Python | Clean package structure, OOP |
| Data Analysis | HHI, Gini, concentration metrics |
| Visualization | matplotlib charts |
| CLI Design | argparse, clean output |
| Testing | pytest, parametrize |
| Crypto | Tokenomics, whale analysis |
