import os
from typing import List, Optional

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .analyzer import TokenVision, TOKEN_DB
from .comparison import Comparison
from .config import Config

app = FastAPI(
    title="TokenVision API",
    description="Token Holder Concentration Analyzer — Detect whales, measure centralization risk",
    version="1.0.0",
    contact={"name": "crwz46"},
    license_info={"name": "MIT"},
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

CHARTS_DIR = "charts"
if os.path.isdir(CHARTS_DIR):
    app.mount("/charts", StaticFiles(directory=CHARTS_DIR), name="charts")


@app.get("/")
async def root():
    return {
        "service": "TokenVision",
        "version": "1.0.0",
        "endpoints": {
            "analyze": "/analyze/{symbol}?live=false&charts=false",
            "compare": "/compare?symbols=UNI,SHIB&live=false",
            "tokens": "/tokens",
            "health": "/health",
            "docs": "/docs",
        },
    }


def _generate_charts(report: dict) -> dict:
    try:
        from .charts import generate
        return generate(report)
    except Exception:
        return {}


@app.get("/analyze/{symbol}")
async def analyze(symbol: str, live: bool = False, charts: bool = False):
    tv = TokenVision(use_live=live)
    try:
        report = tv.analyze(symbol.upper())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if not report.get("metrics"):
        raise HTTPException(status_code=404, detail=f"Token '{symbol.upper()}' not found")

    if charts:
        report["charts"] = _generate_charts(report)

    return report


@app.get("/compare")
async def compare(symbols: str = Query(..., description="Comma-separated symbols"), live: bool = False):
    sym_list = [s.strip().upper() for s in symbols.split(",") if s.strip()]
    if not sym_list:
        raise HTTPException(status_code=400, detail="Provide at least one symbol")
    try:
        reports = Comparison.compare(sym_list, live=live)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"symbols": sym_list, "count": len(reports), "results": reports}


@app.get("/tokens")
async def list_tokens():
    tokens = [{"symbol": sym, "name": info["name"], "supply": info["supply"]} for sym, info in sorted(TOKEN_DB.items())]
    return {"count": len(tokens), "tokens": tokens}


@app.get("/health")
async def health():
    config = Config()
    return {
        "status": "ok",
        "live_data": config.any_api_key(),
        "provider": "etherscan" if config.has_etherscan_key() else "sample",
    }
