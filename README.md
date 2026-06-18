# TokenVision

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-brightgreen)](LICENSE)

Analyze token holder concentration, detect whales, and assess centralization risk — from your terminal **or** via REST API.

## Features

| Feature | Description |
|---------|-------------|
| 🐋 **Whale Detection** | Top holders & their concentration |
| 📊 **Concentration Metrics** | HHI Index, Gini Coefficient, Top-N % |
| 🚨 **Risk Assessment** | HIGH / MODERATE / LOW centralization |
| 📈 **Charts** | Pie chart, bar chart, Lorenz curve |
| 🌐 **Live Data** | Fetch real holder data via Etherscan API |
| 🔄 **Compare** | Cross-token comparison table |
| 🚀 **Web API** | FastAPI server with auto-generated docs |

## Quick Start

```bash
pip install -r requirements.txt
python main.py UNI
```

## Usage

### CLI

```bash
# Analyze any token (sample data)
python main.py UNI
python main.py SHIB
python main.py PEPE

# Use live Etherscan data
python main.py UNI --live

# Generate charts
python main.py UNI --charts

# Compare multiple tokens
python main.py --compare UNI SHIB PEPE

# List available tokens
python main.py --list
```

### Web Server

```bash
# Start FastAPI server
python main.py --server

# or via uvicorn directly
uvicorn tokenvision.api:app --reload

# Open http://localhost:8000/docs for interactive API docs
```

**API Endpoints:**

| Endpoint | Description |
|----------|-------------|
| `GET /` | Service info & links |
| `GET /analyze/{symbol}` | Analyze a token (`?live=true&charts=true`) |
| `GET /compare?symbols=UNI,SHIB` | Compare multiple tokens |
| `GET /tokens` | List available tokens |
| `GET /health` | Health check |
| `GET /docs` | Swagger UI |

### Docker

```bash
docker-compose up -d
# → http://localhost:8000
```

Set your Etherscan API key in `.env`:
```env
ETHERSCAN_API_KEY=your_api_key_here
```

### As a Library

```python
from tokenvision import TokenVision

tv = TokenVision(use_live=True)  # use_live requires ETHERSCAN_API_KEY
report = tv.analyze("UNI")
print(report["metrics"]["gini"])
```

## Example CLI Output

```
======================================================================
  🟢 TOKENVISION — UNI  (🔵 SAMPLE)
======================================================================

  Token       : Uniswap (UNI)
  Supply      : 1,000,000,000

  ────────────────────────────────────────
  CONCENTRATION
  ────────────────────────────────────────
  Top 1       :  11.16%
  Top 5       :  51.73%
  Top 10      :  71.07%
  HHI         :   0.0646
  Gini        :   0.6853
  Eff. Holders:     15.5

  Risk        : 🟢 LOW CONCENTRATION

  TOP 10:
  Rank  Address                                          Hold     Label
  ───── ──────────────────────────────────────────── ──────── ──────────
     1. 0x0000...b95e                               11.16%   🐋 Whale
     2. 0x0000...eded                               10.94%     Whale
     3. 0x0000...9a1e                               10.43%  🐳 Mega Whale
     4. 0x0000...3820                               10.05%     Whale
     5. 0x0000...8b26                                9.15%   🦈 Shark
     6. 0x0000...2b4f                                4.95%
     7. 0x0000...9521                                4.72%
     8. 0x0000...407c                                4.04%
     9. 0x0000...aeaf                                2.91%
    10. 0x0000...1f92                                2.73%
======================================================================
  ✅ Well distributed. Low centralization risk.
======================================================================
```

### Comparison

```
  Symbol  Name            Holders  Top 1    Top 5    Top 10       HHI     Gini            Risk
  ─────── ────────────── ──────── ──────── ──────── ──────── ──────── ──────── ────────────────
  UNI     Uniswap              17   11.16%   51.73%   71.07%   0.0646   0.6853   🟢 LOW
  SHIB    Shiba Inu            24   44.20%   88.21%   95.31%   0.2157   0.9204   🔴 HIGH CONC.
  PEPE    Pepe                 19   25.16%   67.98%   82.44%   0.1032   0.6518   🟡 MODERATE
```

## Charts

With `--charts`, generates:

| Chart | Description |
|-------|-------------|
| 🥧 Pie | Top 10 holders vs others |
| 📊 Bar | Top 20 holders comparison |
| 📈 Lorenz | Wealth distribution curve |

Charts are saved as PNG (also supports PDF, SVG programmatically).

## Project Structure

```
TokenVision/
├── main.py
├── tokenvision/
│   ├── __init__.py
│   ├── cli.py              # CLI entry point
│   ├── analyzer.py          # Core analytics engine
│   ├── charts.py            # matplotlib visualization
│   ├── config.py            # Configuration & env vars
│   ├── cache.py             # File-based JSON cache
│   ├── fetcher.py           # Etherscan API integration
│   ├── comparison.py        # Cross-token comparison
│   └── api.py               # FastAPI web service
├── tests/
│   └── test_tokenvision.py  # 20+ tests
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Configuration

Set via environment variables or `.env` file:

| Variable | Default | Description |
|----------|---------|-------------|
| `ETHERSCAN_API_KEY` | — | Etherscan API key for live data |
| `BSCSCAN_API_KEY` | — | BscScan API key |
| `POLYGONSCAN_API_KEY` | — | PolygonScan API key |
| `CACHE_TTL` | `3600` | Cache time-to-live (seconds) |
| `PORT` | `8000` | Web server port |
| `HOST` | `0.0.0.0` | Web server host |

Copy `.env.example` → `.env` and fill in your keys.

## Supported Tokens

USDC, USDT, LINK, UNI, AAVE, MATIC, SHIB, PEPE, WETH, CRO

## Tests

```bash
pytest tests/ -v
```

## Why Recruiters Love This

| Skill | Shown |
|-------|-------|
| Python | Clean package structure, OOP |
| Data Analysis | HHI, Gini, concentration metrics |
| Visualization | matplotlib charts (dark theme) |
| API Design | FastAPI, OpenAPI docs |
| CLI Design | argparse, clean output |
| Web Scraping | Etherscan API integration |
| Caching | TTL-based JSON cache |
| Docker | Containerized web service |
| Testing | pytest, comprehensive coverage |
| Crypto | Tokenomics, whale analysis |

## 🌐 Ecosystem

This project is part of a **5-repo analytics & AI ecosystem** by [crwz46](https://github.com/crwz46):

| Repo | Focus |
|------|-------|
| 🏠 [WallTrack](https://github.com/crwz46/WallTrack) | Multi-chain wallet tracking, gas alerts, flash loans |
| 🔍 [TokenVision](https://github.com/crwz46/TokenVision) | Token holder concentration, HHI/Gini, whale detection |
| 🪂 [AirDropScanner](https://github.com/crwz46/AirDropScanner) | Multi-protocol airdrop eligibility checker |
| 📊 [TradeLens](https://github.com/crwz46/TradeLens) | Market intelligence, risk engine, portfolio tracker |
| 🧠 [DocuMind](https://github.com/crwz46/DocuMind) | RAG-powered Document Q&A with LLMs |

## 📝 License

MIT &mdash; see [LICENSE](LICENSE)

---

*Built by [crwz46](https://github.com/crwz46) &mdash; Data Scientist &amp; AI Engineer*